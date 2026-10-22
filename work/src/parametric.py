"""Phase 3 - full-factorial parametric study.

Design (Kolkata TMYx, orientation 0):
  roof PCM position  : none / top / bottom                       (3)
  wall PCM           : every subset of N, E, S, W                (16)
  PCM                : C17 22 C, C18 28 C, C19 32 C, C20 36.6 C  (4)
  thickness          : 5, 10, 20 mm                              (3)
  night ventilation  : off / on                                  (2)
  -> 47 PCM placements x 24 + 2 baselines = 1130 cases per mode, for FR and AC.
FAN mode: all placements with C18 and C19 at 10 mm (+ baselines).
Benchmarks (FR, FAN, AC): cool roof, 25/50 mm XPS roof insulation, PCM + cool roof.

    python parametric.py [all|bench|fan|FR|AC] [--workers N]
Results: results/parametric_<mode>.csv (one row per case).
"""
import argparse
import csv
import itertools
import json

from model import Case
from run import run_many, ROOT, RUNS

OUT = ROOT / "results"
WALL_SETS = [frozenset(c) for r in range(5) for c in itertools.combinations("NESW", r)]
PCMS = ("C17", "C18", "C19", "C20")
THKS = (0.005, 0.010, 0.020)


def factorial(mode):
    cases = [Case(mode=mode, night_vent=nv) for nv in (False, True)]
    for roof, walls, pcm, thk, nv in itertools.product(("none", "top", "bottom"), WALL_SETS, PCMS, THKS, (False, True)):
        if roof == "none" and not walls:
            continue
        cases.append(Case(roof=roof, walls=walls, pcm=pcm, thk=thk, night_vent=nv, mode=mode))
    return cases


def fan_subset():
    cases = [Case(mode="FAN", night_vent=nv) for nv in (False, True)]
    for roof, walls, pcm, nv in itertools.product(("none", "top", "bottom"), WALL_SETS, ("C18", "C19"), (False, True)):
        if roof == "none" and not walls:
            continue
        cases.append(Case(roof=roof, walls=walls, pcm=pcm, thk=0.010, night_vent=nv, mode="FAN"))
    return cases


def benchmarks():
    cases = []
    for mode, nv in itertools.product(("FR", "FAN", "AC"), (False, True)):
        cases += [Case(mode=mode, night_vent=nv),
                  Case(mode=mode, night_vent=nv, cool_roof=True),
                  Case(mode=mode, night_vent=nv, roof_ins_mm=25),
                  Case(mode=mode, night_vent=nv, roof_ins_mm=50),
                  Case(mode=mode, night_vent=nv, roof_ins_mm=25, cool_roof=True),
                  Case(mode=mode, night_vent=nv, roof="top", pcm="C18", thk=0.010, cool_roof=True),
                  Case(mode=mode, night_vent=nv, roof="top", pcm="C19", thk=0.010, cool_roof=True),
                  Case(mode=mode, night_vent=nv, roof="top", pcm="C18", thk=0.010, roof_ins_mm=25),
                  Case(mode=mode, night_vent=nv, roof="top", pcm="C19", thk=0.010, roof_ins_mm=25)]
    return cases


def collect(cases, path):
    rows = []
    for c in cases:
        f = RUNS / c.case_id() / "metrics.json"
        if f.exists():
            rows.append(json.loads(f.read_text()))
    if not rows:
        return 0
    keys = []
    for r in rows:
        for k in r:
            if k not in keys:
                keys.append(k)
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        w.writerows(rows)
    return len(rows)


SETS = {"bench": benchmarks, "fan": fan_subset, "FR": lambda: factorial("FR"), "AC": lambda: factorial("AC")}

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("which", nargs="?", default="all")
    ap.add_argument("--workers", type=int, default=11)
    ap.add_argument("--collect-only", action="store_true")
    a = ap.parse_args()
    order = ["bench", "FR", "AC", "fan"] if a.which == "all" else [a.which]
    for name in order:
        cases = list(dict.fromkeys(SETS[name]()))
        if not a.collect_only:
            print(f"== {name}: {len(cases)} cases", flush=True)
            res = run_many(cases, workers=a.workers)
            errs = [r for r in res if "error" in r]
            print(f"   {len(errs)} errors", flush=True)
            for e in errs[:3]:
                print(e["case_id"], e["error"][:800], flush=True)
        n = collect(cases, OUT / f"parametric_{name}.csv")
        print(f"   collected {n} rows -> results/parametric_{name}.csv", flush=True)
