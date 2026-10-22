"""Run EnergyPlus cases and compute comfort / energy / cost metrics.

Usage from Python:
    from run import run_case, run_many
    m = run_case(Case(roof="top", pcm="C18"))
"""
import json
import os
import shutil
import sqlite3
import subprocess
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import numpy as np

from climate import read_epw, running_mean_30d, imacr_band
from model import Case, build_idf, pcm_areas, FLOOR_AREA, HABITABLE, PCMS

ROOT = Path(__file__).resolve().parents[1]            # .../work
EPLUS = ROOT / "tools" / "EnergyPlus-26.2.0" / "energyplus.exe"
WEATHER = {
    "kolkata": ROOT / "weather" / "IND_WB_Kolkata-Bose.Intl.AP.428090_TMYx.2011-2025" / "IND_WB_Kolkata-Bose.Intl.AP.428090_TMYx.2011-2025.epw",
    "midnapore": ROOT / "weather" / "IND_WB_Midnapore.428030_TMYx.2011-2025" / "IND_WB_Midnapore.428030_TMYx.2011-2025.epw",
}
RUNS = ROOT / "runs"

# ---- economic & comfort assumptions (see docs/assumptions.md) --------------------------
AC_COP = 3.3                 # seasonal COP of a 3-star inverter split AC at Kolkata conditions
FAN_W = 60.0                 # ceiling fan power per habitable room
FAN_COMFORT_CREDIT = 1.2     # degC added to the IMAC-R upper limit with ceiling fans (ASHRAE 55, 0.6 m/s)
TARIFF = 7.0                 # Rs/kWh, marginal domestic tariff (assumed)
EMISSION_FACTOR = 0.72       # kgCO2/kWh, Indian grid (CEA, approximate)
PCM_PRICE = 450.0            # Rs/kg (OM37 price reported by Abass & Muthulingam 2024)
ENCAP_COST = {"roof_top": 700.0, "roof_bottom": 600.0, "wall": 600.0}   # Rs/m2 encapsulation + finish + labour (assumed)

SEASONS = {"winter": (12, 1, 2), "summer": (3, 4, 5), "monsoon": (6, 7, 8, 9), "postmonsoon": (10, 11)}

_epw_cache = {}


def epw_data(weather):
    if weather not in _epw_cache:
        w = read_epw(WEATHER[weather])
        t30 = running_mean_30d(w["tdb"])
        w["t30_hourly"] = np.repeat(t30, 24)
        _epw_cache[weather] = w
    return _epw_cache[weather]


def pcm_cost(case: Case):
    """Investment cost in Rs for the PCM retrofit."""
    if not case.has_pcm():
        return 0.0, 0.0
    areas = pcm_areas(case)
    rho = case.pcm_props()["rho"]
    a_total = sum(areas.values())
    mass = a_total * case.thk * rho
    encap = (areas["roof"] * (ENCAP_COST["roof_top"] if case.roof == "top" else ENCAP_COST["roof_bottom"])
             + sum(areas[f] for f in "NESW") * ENCAP_COST["wall"])
    return mass * PCM_PRICE + encap, mass


# ---------------------------------------------------------------------------------------
def read_sql(sql_path):
    con = sqlite3.connect(sql_path)
    q = """SELECT rdd.KeyValue, rdd.Name, rd.Value
           FROM ReportData rd
           JOIN ReportDataDictionary rdd ON rd.ReportDataDictionaryIndex = rdd.ReportDataDictionaryIndex
           JOIN Time t ON rd.TimeIndex = t.TimeIndex
           JOIN EnvironmentPeriods e ON t.EnvironmentPeriodIndex = e.EnvironmentPeriodIndex
           WHERE (t.WarmupFlag = 0 OR t.WarmupFlag IS NULL) AND e.EnvironmentType = 3
           ORDER BY rdd.ReportDataDictionaryIndex, t.TimeIndex"""
    series = {}
    for key, name, val in con.execute(q):
        series.setdefault((key.upper(), name), []).append(val)
    con.close()
    return {k: np.array(v) for k, v in series.items()}


def comfort_metrics(series, case: Case, w):
    t30 = w["t30_hourly"]
    tn, lo80, hi80 = imacr_band(t30, 80)
    _, lo90, hi90 = imacr_band(t30, 90)
    if case.mode == "FAN":
        hi80 = hi80 + FAN_COMFORT_CREDIT
        hi90 = hi90 + FAN_COMFORT_CREDIT
    month = w["month"].astype(int)
    out = {}
    tot = {"occ": 0, "hot80": 0, "cold80": 0, "hot90": 0, "cold90": 0, "ddh_hot": 0.0, "ddh_cold": 0.0}
    seas = {s: {"occ": 0, "out80": 0, "hot80": 0, "cold80": 0} for s in SEASONS}
    tmax = []
    for z in HABITABLE:
        top = series[(z, "Zone Operative Temperature")]
        occ = series[(z, "Zone People Occupant Count")] > 0
        if case.mode == "AC":
            # comfort is assessed only when the room is free-running (AC hours are comfortable by design)
            pass
        hot80 = occ & (top > hi80)
        cold80 = occ & (top < lo80)
        tot["occ"] += occ.sum()
        tot["hot80"] += hot80.sum()
        tot["cold80"] += cold80.sum()
        tot["hot90"] += (occ & (top > hi90)).sum()
        tot["cold90"] += (occ & (top < lo90)).sum()
        tot["ddh_hot"] += np.clip(top - hi80, 0, None)[occ].sum()
        tot["ddh_cold"] += np.clip(lo80 - top, 0, None)[occ].sum()
        for s, months in SEASONS.items():
            sel = np.isin(month, months)
            seas[s]["occ"] += (occ & sel).sum()
            seas[s]["hot80"] += (hot80 & sel).sum()
            seas[s]["cold80"] += (cold80 & sel).sum()
            seas[s]["out80"] += ((hot80 | cold80) & sel).sum()
        out[f"{z}_Top_max"] = float(top.max())
        out[f"{z}_Top_mean_summer"] = float(top[np.isin(month, SEASONS["summer"])].mean())
        d = top.reshape(365, 24)
        out[f"{z}_swing_summer"] = float((d.max(1) - d.min(1))[np.isin(month.reshape(365, 24)[:, 0], SEASONS["summer"])].mean())
        tmax.append(top.max())
    occ_h = max(tot["occ"], 1)
    out.update({
        "occ_hours": int(tot["occ"]),
        "disc80_h": int(tot["hot80"] + tot["cold80"]),
        "disc80_pct": 100.0 * (tot["hot80"] + tot["cold80"]) / occ_h,
        "hot80_h": int(tot["hot80"]), "cold80_h": int(tot["cold80"]),
        "disc90_pct": 100.0 * (tot["hot90"] + tot["cold90"]) / occ_h,
        "ddh_hot": float(tot["ddh_hot"]), "ddh_cold": float(tot["ddh_cold"]),
        "Top_max": float(max(tmax)),
    })
    for s in SEASONS:
        o = max(seas[s]["occ"], 1)
        out[f"disc80_pct_{s}"] = 100.0 * seas[s]["out80"] / o
        out[f"hot80_pct_{s}"] = 100.0 * seas[s]["hot80"] / o
        out[f"cold80_pct_{s}"] = 100.0 * seas[s]["cold80"] / o
    return out


def energy_metrics(series, case: Case, w):
    out = {}
    month = w["month"].astype(int)
    if case.mode == "AC":
        q = np.zeros(8760)
        for z in HABITABLE:
            q += series[(f"{z}_IDEALAC", "Zone Ideal Loads Zone Total Cooling Energy")] / 3.6e6   # J -> kWh
        elec = q / AC_COP
        out["cool_load_kwh"] = float(q.sum())
        out["ac_elec_kwh"] = float(elec.sum())
        out["epi_cool"] = float(elec.sum() / FLOOR_AREA)
        out["ac_peak_kw"] = float(q.max())
        for s, months in SEASONS.items():
            out[f"ac_elec_kwh_{s}"] = float(elec[np.isin(month, months)].sum())
    if case.mode == "FAN":
        # BED fan 21-07 h, LIV fan 24 h, 1 Mar - 15 Nov (260 days)
        out["fan_elec_kwh"] = FAN_W * (10 + 24) * 260 / 1000
        out["epi_fan"] = out["fan_elec_kwh"] / FLOOR_AREA
    # roof heat gain into the habitable rooms (positive = into zone)
    for z in HABITABLE:
        k = (f"{z}_ROOF", "Surface Inside Face Conduction Heat Transfer Rate per Area")
        if k in series:
            f = series[k]
            out[f"{z}_roof_flux_max"] = float(f.max())
            out[f"{z}_roof_gain_kwh_m2"] = float(f[f > 0].sum() / 1000)
        k = (f"{z}_ROOF", "Surface Inside Face Temperature")
        if k in series:
            out[f"{z}_ceiling_T_max"] = float(series[k].max())
    return out


def run_case(case: Case, weather="kolkata", keep=False, force=False, tag=None):
    cid = case.case_id() + ("" if weather == "kolkata" else f"_{weather}")
    d = RUNS / cid
    mfile = d / "metrics.json"
    if mfile.exists() and not force:
        return json.loads(mfile.read_text())
    if d.exists():
        shutil.rmtree(d, ignore_errors=True)
    d.mkdir(parents=True)
    w = epw_data(weather)
    (d / "in.idf").write_text(build_idf(case, w["meta"]))
    t0 = time.time()
    r = subprocess.run([str(EPLUS), "-w", str(WEATHER[weather]), "-d", str(d), str(d / "in.idf")],
                       capture_output=True, text=True)
    runtime = time.time() - t0
    err = (d / "eplusout.err").read_text(errors="ignore") if (d / "eplusout.err").exists() else ""
    if r.returncode != 0 or "EnergyPlus Completed Successfully" not in err:
        raise RuntimeError(f"EnergyPlus failed for {cid}:\n{r.stdout[-2000:]}\n{err[-4000:]}")
    series = read_sql(d / "eplusout.sql")
    cost, mass = pcm_cost(case)
    m = {"case_id": cid, "weather": weather, "runtime_s": round(runtime, 1),
         "n_warnings": err.count("** Warning **"), "n_severe": err.count("** Severe  **")}
    m.update(case.key())
    m.update({"pcm_cost_rs": cost, "pcm_mass_kg": mass})
    m.update(comfort_metrics(series, case, w))
    m.update(energy_metrics(series, case, w))
    if keep:
        np.savez_compressed(d / "hourly.npz", **{f"{k[0]}|{k[1]}": v for k, v in series.items()})
        for f in d.iterdir():
            if f.name not in ("in.idf", "eplusout.err", "hourly.npz", "eplusout.rdd", "eplusout.eio", "eplustbl.htm"):
                f.unlink()
    else:
        for f in d.iterdir():
            if f.name not in ("eplusout.err",):
                f.unlink()
    mfile.write_text(json.dumps(m, indent=1, default=float))
    return m


def _worker(args):
    case, weather, keep = args
    try:
        return run_case(case, weather, keep)
    except Exception as e:  # keep the batch going; record the failure
        return {"case_id": case.case_id(), "error": str(e)[:3000]}


def run_many(cases, weather="kolkata", workers=None, keep=False, progress=True):
    workers = workers or max(1, (os.cpu_count() or 2) - 2)
    results = []
    t0 = time.time()
    with ProcessPoolExecutor(max_workers=workers) as ex:
        futs = [ex.submit(_worker, (c, weather, keep)) for c in cases]
        for i, f in enumerate(as_completed(futs), 1):
            results.append(f.result())
            if progress and (i % 25 == 0 or i == len(futs)):
                el = time.time() - t0
                print(f"  {i}/{len(futs)} done, {el/60:.1f} min elapsed, ETA {el/i*(len(futs)-i)/60:.1f} min", flush=True)
    return results


def load_series(case: Case, weather="kolkata"):
    cid = case.case_id() + ("" if weather == "kolkata" else f"_{weather}")
    z = np.load(RUNS / cid / "hourly.npz")
    return {tuple(k.split("|", 1)): z[k] for k in z.files}
