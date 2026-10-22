"""Phase 4 - multi-objective optimisation with NSGA-II / NSGA-III (pymoo).

Objectives (all minimised):
  f1  discomfort  : % of occupied hours outside the IMAC-R 80 % band, free-running house
  f2  energy      : cooling EPI of the air-conditioned house, kWh/m2.yr
  f3  cost        : retrofit investment, Rs

Stage B ("discrete")  - the design space of the parametric study; objectives are looked up from the
                        full-factorial results, so the true Pareto front is known and we can measure
                        how well (and how quickly) NSGA-II / NSGA-III find it.
Stage C ("extended")  - continuous melting point (20-38 C) and thickness (3-30 mm), plus cool-roof
                        coating and XPS roof insulation (0-50 mm) as competing / complementary measures;
                        every evaluation runs EnergyPlus twice (FR + AC).

    python optimize.py discrete            # stage B, needs results/parametric_FR.csv and _AC.csv
    python optimize.py extended [--gens N --pop N]
"""
import argparse
import csv
import json
import time

import numpy as np
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.algorithms.moo.nsga3 import NSGA3
from pymoo.core.problem import Problem
from pymoo.operators.crossover.sbx import SBX
from pymoo.operators.mutation.pm import PM
from pymoo.operators.repair.rounding import RoundingRepair
from pymoo.operators.sampling.rnd import IntegerRandomSampling, FloatRandomSampling
from pymoo.optimize import minimize
from pymoo.util.ref_dirs import get_reference_directions
from pymoo.util.nds.non_dominated_sorting import NonDominatedSorting
from pymoo.indicators.igd import IGD
from pymoo.indicators.hv import HV

from model import Case
from run import run_many, ROOT, pcm_cost

OUT = ROOT / "results" / "optimisation"
OUT.mkdir(parents=True, exist_ok=True)

ROOFS = ("none", "top", "bottom")
PCMS = ("C17", "C18", "C19", "C20")
THKS = (0.005, 0.010, 0.020)


# --------------------------------------------------------------------------------------- stage B
def load_table(mode):
    rows = list(csv.DictReader(open(ROOT / "results" / f"parametric_{mode}.csv")))
    tab = {}
    for r in rows:
        key = (r["roof"], r["walls"], r["pcm"], round(float(r["thk"]), 3), r["night_vent"] == "True")
        tab[key] = r
    return tab


def decode_discrete(x):
    """x = [roof(0-2), N, E, S, W, pcm(0-3), thk(0-2), nv(0-1)] -> lookup key."""
    roof = ROOFS[int(x[0])]
    walls = "".join(sorted(f for f, b in zip("NESW", x[1:5]) if int(b)))
    nv = bool(int(x[7]))
    if roof == "none" and not walls:
        return ("none", "", "-", 0.0, nv)
    return (roof, walls, PCMS[int(x[5])], THKS[int(x[6])], nv)


class DiscreteProblem(Problem):
    def __init__(self, fr, ac, objectives):
        super().__init__(n_var=8, n_obj=len(objectives), xl=[0, 0, 0, 0, 0, 0, 0, 0],
                         xu=[2, 1, 1, 1, 1, 3, 2, 1], vtype=int)
        self.fr, self.ac, self.objectives = fr, ac, objectives
        self.seen = set()

    def objective_values(self, key):
        fr, ac = self.fr[key], self.ac[key]
        vals = {"discomfort": float(fr["disc80_pct"]), "energy": float(ac["epi_cool"]),
                "cost": float(fr["pcm_cost_rs"]) / 1000.0}
        return [vals[o] for o in self.objectives]

    def _evaluate(self, X, out, *args, **kwargs):
        F = []
        for x in X:
            key = decode_discrete(x)
            self.seen.add(key)
            F.append(self.objective_values(key))
        out["F"] = np.array(F)


def true_front(problem):
    keys = list(problem.fr.keys())
    F = np.array([problem.objective_values(k) for k in keys])
    nd = NonDominatedSorting().do(F, only_non_dominated_front=True)
    return F[nd], [keys[i] for i in nd]


def run_discrete(seeds=(1, 2, 3, 4, 5), pop=40, gens=40):
    fr, ac = load_table("FR"), load_table("AC")
    summary = []
    for objectives in (["discomfort", "cost"], ["energy", "cost"], ["discomfort", "energy", "cost"]):
        tag = "_".join(objectives)
        probe = DiscreteProblem(fr, ac, objectives)
        PF, pf_keys = true_front(probe)
        ideal, nadir = PF.min(0), PF.max(0)
        scale = lambda F: (F - ideal) / np.where(nadir > ideal, nadir - ideal, 1)
        igd = IGD(scale(PF))
        hv = HV(ref_point=np.full(len(objectives), 1.1))
        hv_true = hv(scale(PF))
        algos = {"NSGA-II": lambda: NSGA2(pop_size=pop, sampling=IntegerRandomSampling(),
                                          crossover=SBX(prob=0.9, eta=15, vtype=float, repair=RoundingRepair()),
                                          mutation=PM(eta=20, vtype=float, repair=RoundingRepair()),
                                          eliminate_duplicates=True)}
        if len(objectives) == 3:
            ref = get_reference_directions("das-dennis", 3, n_partitions=8)
            algos["NSGA-III"] = lambda: NSGA3(ref_dirs=ref, pop_size=max(pop, len(ref)), sampling=IntegerRandomSampling(),
                                              crossover=SBX(prob=0.9, eta=15, vtype=float, repair=RoundingRepair()),
                                              mutation=PM(eta=20, vtype=float, repair=RoundingRepair()),
                                              eliminate_duplicates=True)
        for aname, make in algos.items():
            for seed in seeds:
                prob = DiscreteProblem(fr, ac, objectives)
                res = minimize(prob, make(), ("n_gen", gens), seed=seed, verbose=False, save_history=True)
                hist = []
                for h in res.history:
                    Fh = h.opt.get("F")
                    hist.append((h.evaluator.n_eval, float(igd(scale(Fh))), float(hv(scale(Fh)) / hv_true)))
                found = {decode_discrete(x) for x in res.X}
                hit = len(found & set(pf_keys)) / len(pf_keys)
                summary.append({"objectives": tag, "algorithm": aname, "seed": seed, "n_eval": res.algorithm.evaluator.n_eval,
                                "unique_designs": len(prob.seen), "space_size": len(fr), "true_front_size": len(pf_keys),
                                "front_points_found_pct": round(100 * hit, 1), "igd": round(hist[-1][1], 4),
                                "hv_ratio": round(hist[-1][2], 4)})
                with open(OUT / f"history_{tag}_{aname}_s{seed}.json", "w") as f:
                    json.dump(hist, f)
                print(summary[-1], flush=True)
        with open(OUT / f"true_front_{tag}.csv", "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["roof", "walls", "pcm", "thk", "night_vent"] + objectives)
            for k, row in zip(pf_keys, PF):
                w.writerow(list(k) + [round(v, 4) for v in row])
    with open(OUT / "discrete_summary.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(summary[0].keys()))
        w.writeheader()
        w.writerows(summary)


# --------------------------------------------------------------------------------------- stage C
EXT_XL = [0, 0, 0, 0, 0, 20.0, 3.0, 0, 0, 0.0]
EXT_XU = [2, 1, 1, 1, 1, 38.0, 30.0, 1, 1, 50.0]
L_GENERIC = 230e3       # J/kg, typical of C17-C20 paraffins


def decode_extended(x):
    """x = [roof, N, E, S, W, Tm(C), thk(mm), nv, cool, XPS(mm)] -> (FR case, AC case)."""
    roof = ROOFS[int(round(x[0]))]
    walls = frozenset(f for f, b in zip("NESW", x[1:5]) if round(b))
    tm = round(float(x[5]) * 2) / 2            # 0.5 C resolution
    thk = round(float(x[6])) / 1000            # 1 mm resolution
    nv, cool = bool(round(x[7])), bool(round(x[8]))
    ins = int(5 * round(float(x[9]) / 5))     # XPS roof insulation, 5 mm steps (0 = none)
    if roof == "none" and not walls:
        base = dict(night_vent=nv, cool_roof=cool, roof_ins_mm=ins)
    else:
        base = dict(roof=roof, walls=walls, pcm="custom", tm=tm, L=L_GENERIC, thk=thk, night_vent=nv, cool_roof=cool,
                    roof_ins_mm=ins)
    return Case(mode="FR", **base), Case(mode="AC", **base)


class ExtendedProblem(Problem):
    def __init__(self, workers):
        super().__init__(n_var=10, n_obj=3, xl=EXT_XL, xu=EXT_XU)
        self.workers = workers
        self.log = []

    def _evaluate(self, X, out, *args, **kwargs):
        pairs = [decode_extended(x) for x in X]
        cases = list(dict.fromkeys([c for p in pairs for c in p]))
        res = {r["case_id"]: r for r in run_many(cases, workers=self.workers, progress=False)}
        F = []
        for fr, ac in pairs:
            rf, ra = res[fr.case_id()], res[ac.case_id()]
            if "error" in rf or "error" in ra:
                F.append([1e3, 1e3, 1e4])
                continue
            f = [rf["disc80_pct"], ra["epi_cool"], rf["pcm_cost_rs"] / 1000.0]
            F.append(f)
            self.log.append({"fr": fr.case_id(), "ac": ac.case_id(), "roof": fr.roof, "walls": "".join(sorted(fr.walls)),
                             "tm": fr.tm, "thk_mm": round(fr.thk * 1000), "night_vent": fr.night_vent,
                             "cool_roof": fr.cool_roof, "xps_mm": fr.roof_ins_mm, "disc80_pct": f[0], "epi_cool": f[1], "cost_krs": f[2],
                             "hot80_h": rf["hot80_h"], "cold80_h": rf["cold80_h"]})
        out["F"] = np.array(F)


def run_extended(pop=24, gens=20, workers=11, algorithm="NSGA-III", seed=7):
    prob = ExtendedProblem(workers)
    if algorithm == "NSGA-III":
        ref = get_reference_directions("das-dennis", 3, n_partitions=5)    # 21 directions
        algo = NSGA3(ref_dirs=ref, pop_size=max(pop, len(ref)), sampling=FloatRandomSampling(),
                     crossover=SBX(prob=0.9, eta=15), mutation=PM(eta=20), eliminate_duplicates=True)
    else:
        algo = NSGA2(pop_size=pop, sampling=FloatRandomSampling(), crossover=SBX(prob=0.9, eta=15),
                     mutation=PM(eta=20), eliminate_duplicates=True)
    t0 = time.time()

    def cb(alg):
        print(f"  gen {alg.n_gen}: {alg.evaluator.n_eval} evals, {len(prob.log)} logged, "
              f"{(time.time() - t0) / 60:.1f} min", flush=True)
        with open(OUT / f"extended_{algorithm}_log.json", "w") as f:
            json.dump(prob.log, f)

    res = minimize(prob, algo, ("n_gen", gens), seed=seed, verbose=False, callback=cb)
    rows = []
    for x, f in zip(res.X, res.F):
        fr, _ = decode_extended(x)
        rows.append({"roof": fr.roof, "walls": "".join(sorted(fr.walls)) or "-",
                     "tm": fr.tm if fr.has_pcm() else None, "thk_mm": round(fr.thk * 1000) if fr.has_pcm() else 0,
                     "night_vent": fr.night_vent, "cool_roof": fr.cool_roof, "xps_mm": fr.roof_ins_mm,
                     "disc80_pct": round(f[0], 3), "epi_cool": round(f[1], 3), "cost_krs": round(f[2], 2)})
    rows.sort(key=lambda r: r["cost_krs"])
    with open(OUT / f"extended_{algorithm}_front.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    with open(OUT / f"extended_{algorithm}_log.json", "w") as f:
        json.dump(prob.log, f)
    print(f"done: {len(rows)} Pareto designs, {(time.time() - t0) / 60:.1f} min")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("stage", choices=["discrete", "extended"])
    ap.add_argument("--pop", type=int, default=None)
    ap.add_argument("--gens", type=int, default=None)
    ap.add_argument("--workers", type=int, default=11)
    ap.add_argument("--algorithm", default="NSGA-III")
    a = ap.parse_args()
    if a.stage == "discrete":
        run_discrete(pop=a.pop or 40, gens=a.gens or 40)
    else:
        run_extended(pop=a.pop or 24, gens=a.gens or 20, workers=a.workers, algorithm=a.algorithm)
