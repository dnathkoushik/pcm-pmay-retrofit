"""Phase 2 - model verification.

1. CondFD vs CTF heat-balance algorithms for the baseline house (should agree closely).
2. Grid / timestep sensitivity of a PCM case (space discretisation constant, timesteps per hour).
3. Latent-heat control: PCM layer vs identical layer without latent heat.
4. PCM melt/freeze (charge/discharge) statistics for each PCM location and melting point.
Writes results/verification.csv and results/pcm_cycles.csv.
"""
import csv
from pathlib import Path

from model import Case
from run import run_many, load_series, epw_data, ROOT
from analysis import pcm_layer_temperature, cycle_stats

OUT = ROOT / "results"
OUT.mkdir(exist_ok=True)
NESW = frozenset("NESW")

verification = {
    "base_CondFD": Case(),
    "base_CTF": Case(algo="CTF"),
    "roofTop20_C3_ts20": Case(roof="top", thk=0.020, space_c=3.0, timestep=20, hourly_pcm_nodes=True),
    "roofTop20_C1_ts20": Case(roof="top", thk=0.020, space_c=1.0, timestep=20, hourly_pcm_nodes=True),
    "roofTop20_C1_ts30": Case(roof="top", thk=0.020, space_c=1.0, timestep=30, hourly_pcm_nodes=True),
    "roofTop20_C05_ts20": Case(roof="top", thk=0.020, space_c=0.5, timestep=20, hourly_pcm_nodes=True),
    "roofTop10_latent": Case(roof="top", thk=0.010, space_c=1.0, hourly_pcm_nodes=True),
    "roofTop10_noLatent": Case(roof="top", thk=0.010, space_c=1.0, latent=False),
    "roofBot10_latent": Case(roof="bottom", thk=0.010, space_c=1.0, hourly_pcm_nodes=True),
    "roofBot10_noLatent": Case(roof="bottom", thk=0.010, space_c=1.0, latent=False),
    "walls10_latent": Case(walls=NESW, thk=0.010, space_c=1.0, hourly_pcm_nodes=True),
    "walls10_noLatent": Case(walls=NESW, thk=0.010, space_c=1.0, latent=False),
}
# melt/freeze behaviour for each location x melting point (10 mm)
cycles = {}
for pcm in ("C17", "C18", "C19", "C20"):
    cycles[f"roofTop_{pcm}"] = (Case(roof="top", pcm=pcm, thk=0.010, space_c=1.0, hourly_pcm_nodes=True), "roof_top")
    cycles[f"roofBot_{pcm}"] = (Case(roof="bottom", pcm=pcm, thk=0.010, space_c=1.0, hourly_pcm_nodes=True), "roof_bottom")
    cycles[f"walls_{pcm}"] = (Case(walls=NESW, pcm=pcm, thk=0.010, space_c=1.0, hourly_pcm_nodes=True), "wall_S")

if __name__ == "__main__":
    allcases = list(verification.values()) + [c for c, _ in cycles.values()]
    uniq = list(dict.fromkeys(allcases))
    print(f"running {len(uniq)} verification cases")
    res = {r.get("case_id"): r for r in run_many(uniq, keep=True)}
    for r in res.values():
        if "error" in r:
            print("ERROR", r["case_id"], r["error"][:1500])

    cols = ["label", "case_id", "runtime_s", "disc80_pct", "disc90_pct", "hot80_h", "cold80_h", "ddh_hot",
            "Top_max", "BED_ceiling_T_max", "BED_roof_gain_kwh_m2", "BED_roof_flux_max", "n_warnings"]
    with open(OUT / "verification.csv", "w", newline="") as f:
        wr = csv.writer(f)
        wr.writerow(cols)
        for lab, c in verification.items():
            r = res[c.case_id()]
            wr.writerow([lab] + [r.get(k) if not isinstance(r.get(k), float) else round(r[k], 3) for k in cols[1:]])
            print(f"{lab:22s} disc80 {r['disc80_pct']:6.2f}  disc90 {r['disc90_pct']:6.2f}  hot80 {r['hot80_h']:4d}  "
                  f"Tmax {r['Top_max']:5.2f}  ceilTmax {r['BED_ceiling_T_max']:5.2f}  roofgain {r['BED_roof_gain_kwh_m2']:6.1f}  "
                  f"rt {r['runtime_s']:5.1f}s")

    w = epw_data("kolkata")
    rows = []
    for lab, (c, el) in cycles.items():
        s = load_series(c)
        st = cycle_stats(pcm_layer_temperature(s, c, el), c, w["month"])
        r = res[c.case_id()]
        st.update({"label": lab, "pcm": c.pcm, "element": el, "disc80_pct": r["disc80_pct"], "hot80_h": r["hot80_h"],
                   "cold80_h": r["cold80_h"], "Top_max": r["Top_max"]})
        rows.append(st)
        print(f"{lab:14s} util_yr {st['util_year']:.2f} | summer util {st['util_summer']:.2f} full {st['full_frac_summer']:.2f} "
              f"neverSolid {st['never_solid_frac_summer']:.2f} | monsoon util {st['util_monsoon']:.2f} "
              f"neverSolid {st['never_solid_frac_monsoon']:.2f} | winter util {st['util_winter']:.2f} "
              f"neverLiquid {st['never_liquid_frac_winter']:.2f} | disc80 {r['disc80_pct']:.2f}")
    keys = list(rows[0].keys())
    with open(OUT / "pcm_cycles.csv", "w", newline="") as f:
        wr = csv.DictWriter(f, fieldnames=keys)
        wr.writeheader()
        wr.writerows(rows)
