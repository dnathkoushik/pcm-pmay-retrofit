"""Phase 5 - sensitivity of the key designs.

  orientation : 0 / 90 / 180 / 270 deg (the drawing does not give the orientation)
  climate     : Kolkata vs Midnapore (WMO 428030, ~10 km from Kharagpur)
  numerics    : CondFD grid constant 1.8 (study default) vs 1.0 (converged)
  PCM data    : n-octadecane properties from Faden et al. 2019 (L 237 kJ/kg, rho ~822, k 0.334/0.151)

    python sensitivity.py [--extra-json designs.json]
Writes results/sensitivity.csv.
"""
import argparse
import csv
import json
from dataclasses import replace

from model import Case, PCMS
from run import run_many, ROOT

OUT = ROOT / "results"

KEY_DESIGNS = {
    "baseline": Case(),
    "PCM C18 roof-top 10 mm": Case(roof="top", pcm="C18", thk=0.010),
    "PCM C19 roof-top 10 mm": Case(roof="top", pcm="C19", thk=0.010),
    "PCM C19 roof-top 20 mm": Case(roof="top", pcm="C19", thk=0.020),
    "XPS 25 mm": Case(roof_ins_mm=25),
    "XPS 25 mm + cool roof": Case(roof_ins_mm=25, cool_roof=True),
    "PCM C19 10 mm + XPS 25 mm": Case(roof="top", pcm="C19", thk=0.010, roof_ins_mm=25),
}


def design_cases(extra=None):
    designs = dict(KEY_DESIGNS)
    if extra:
        designs.update(extra)
    jobs = []   # (design, factor, level, weather, case)
    for name, c in designs.items():
        for mode in ("FR", "AC"):
            base = replace(c, mode=mode)
            for o in (0.0, 90.0, 180.0, 270.0):
                jobs.append((name, "orientation", f"{int(o)}", "kolkata", replace(base, orientation=o)))
            jobs.append((name, "climate", "Midnapore (Kharagpur)", "midnapore", base))
            jobs.append((name, "grid", "C=1.0", "kolkata", replace(base, space_c=1.0)))
            if c.has_pcm() and c.pcm == "C18":
                jobs.append((name, "pcm_data", "Faden 2019", "kolkata", replace(base, pcm="custom", tm=28.0, L=237e3)))
            jobs.append((name, "night_vent", "on", "kolkata", replace(base, night_vent=True)))
    return jobs


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--extra-json", default=None, help="JSON {name: Case kwargs} of extra designs (e.g. optimum)")
    ap.add_argument("--workers", type=int, default=11)
    a = ap.parse_args()
    extra = None
    if a.extra_json:
        raw = json.load(open(a.extra_json))
        extra = {k: Case(**{**v, "walls": frozenset(v.get("walls", ""))}) for k, v in raw.items()}
    jobs = design_cases(extra)
    by_weather = {}
    for j in jobs:
        by_weather.setdefault(j[3], []).append(j[4])
    res = {}
    for w, cases in by_weather.items():
        print(f"== {w}: {len(set(cases))} cases", flush=True)
        for r in run_many(list(dict.fromkeys(cases)), weather=w, workers=a.workers):
            res[r["case_id"]] = r
    rows = []
    for name, factor, level, w, c in jobs:
        cid = c.case_id() + ("" if w == "kolkata" else f"_{w}")
        r = res.get(cid, {})
        if "error" in r or not r:
            print("missing/error", cid, r.get("error", "")[:300])
            continue
        rows.append({"design": name, "mode": c.mode, "factor": factor, "level": level, "disc80_pct": r["disc80_pct"],
                     "hot80_h": r["hot80_h"], "cold80_h": r["cold80_h"], "Top_max": r["Top_max"],
                     "epi_cool": r.get("epi_cool", ""), "cost_rs": r["pcm_cost_rs"]})
    with open(OUT / "sensitivity.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {len(rows)} rows to results/sensitivity.csv")
