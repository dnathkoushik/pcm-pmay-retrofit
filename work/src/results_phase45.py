"""Figures for verification (PCM cycling), optimisation (Phase 4) and sensitivity (Phase 5).

    python results_phase45.py
"""
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from results_phase3 import RES, ASSETS, INK, MUTED, GRID, PCM_COL, PCM_LAB  # also applies the plot style

OPT = RES / "optimisation"


def fig_cycles():
    c = pd.read_csv(RES / "pcm_cycles.csv")
    locs = [("roof_top", "roof-top"), ("roof_bottom", "ceiling"), ("wall_S", "walls")]
    seasons = [("summer", "Mar–May"), ("monsoon", "Jun–Sep"), ("winter", "Dec–Feb")]
    fig, axes = plt.subplots(1, 3, figsize=(9.2, 3.2), sharey=True)
    w = 0.2
    for ax, (el, lab) in zip(axes, locs):
        for i, pcm in enumerate(("C17", "C18", "C19", "C20")):
            r = c[(c.element == el) & (c.pcm == pcm)]
            if not len(r):
                continue
            vals = [100 * r[f"util_{s}"].iloc[0] for s, _ in seasons]
            ax.bar(np.arange(3) + (i - 1.5) * w, vals, w, color=PCM_COL[pcm], label=PCM_LAB[pcm])
        ax.set_xticks(range(3), [f"{s}\n{d}" for s, d in seasons])
        ax.set_title(lab, loc="left", fontsize=10, color=INK)
        ax.set_ylim(0, 100)
    axes[0].set_ylabel("Latent-heat utilisation (%)\n(mean daily melt-fraction swing)")
    axes[2].legend(fontsize=7.5, loc="upper right")
    fig.suptitle("Does the PCM actually melt and re-solidify? (10 mm layer, free-running)", x=0.01, ha="left",
                 fontsize=11, color=INK)
    fig.tight_layout()
    fig.savefig(ASSETS / "r_cycles.png")
    plt.close(fig)


def fig_opt_validation():
    s = pd.read_csv(OPT / "discrete_summary.csv")
    fig, axes = plt.subplots(1, 3, figsize=(9.2, 3.0), sharey=True)
    tags = [("discomfort_cost", "comfort vs cost"), ("energy_cost", "energy vs cost"),
            ("discomfort_energy_cost", "comfort vs energy vs cost")]
    for ax, (tag, title) in zip(axes, tags):
        for alg, col in (("NSGA-II", "#2f6690"), ("NSGA-III", "#c8553d")):
            sub = s[(s.objectives == tag) & (s.algorithm == alg)]
            for _, r in sub.iterrows():
                h = json.load(open(OPT / f"history_{tag}_{alg}_s{r['seed']}.json"))
                ev, _, hv = zip(*h)
                ax.plot(ev, 100 * np.array(hv), color=col, lw=1, alpha=0.7,
                        label=alg if r["seed"] == sub.seed.min() else None)
        ax.axvline(int(s[s.objectives == tag].space_size.iloc[0]), color=MUTED, ls=":", lw=1)
        ax.set_title(title, loc="left", fontsize=10, color=INK)
        ax.set_xlabel("simulations (lookups) used")
        ax.set_ylim(50, 101)
    axes[0].set_ylabel("Hypervolume reached (% of true front)")
    axes[0].legend(fontsize=8, loc="lower right")
    fig.suptitle("Optimiser check on the discrete space (true Pareto front from 1,130-case brute force; "
                 "dotted = brute-force cost)", x=0.01, ha="left", fontsize=10.5, color=INK)
    fig.tight_layout()
    fig.savefig(ASSETS / "r_opt_validation.png")
    plt.close(fig)


def fig_opt_front(algorithm="NSGA-III"):
    log = pd.DataFrame(json.load(open(OPT / f"extended_{algorithm}_log.json")))
    front = pd.read_csv(OPT / f"extended_{algorithm}_front.csv")
    fig, axes = plt.subplots(1, 2, figsize=(9.2, 3.8))
    kind = np.where(log.roof.eq("none") & log.walls.eq(""), "no PCM", "with PCM")
    for ax, (x, y, xl, yl) in zip(axes, [("cost_krs", "disc80_pct", "Retrofit cost (thousand Rs)", "Discomfort, free-running (%)"),
                                         ("cost_krs", "epi_cool", "Retrofit cost (thousand Rs)", "Cooling EPI with AC (kWh/m²·yr)")]):
        for k, col in (("no PCM", "#2f6690"), ("with PCM", "#e0a12e")):
            sel = kind == k
            ax.scatter(log.loc[sel, x], log.loc[sel, y], s=8, alpha=0.35, color=col, lw=0, label=f"evaluated, {k}")
        fk = np.where(front.roof.eq("none") & front.walls.eq("-"), "#2f6690", "#e0a12e")
        ax.scatter(front[x], front[y], s=34, c=fk, edgecolor=INK, lw=0.7, label="Pareto-optimal", zorder=5)
        ax.set_xlabel(xl)
        ax.set_ylabel(yl)
        ax.set_xscale("symlog", linthresh=10)
    axes[0].legend(fontsize=7.8, loc="upper right")
    fig.suptitle(f"Extended optimisation ({algorithm}): PCM melting point, thickness, placement, "
                 "XPS insulation, cool roof, night ventilation", x=0.01, ha="left", fontsize=10.5, color=INK)
    fig.tight_layout()
    fig.savefig(ASSETS / "r_opt_front.png")
    plt.close(fig)


def fig_sensitivity():
    s = pd.read_csv(RES / "sensitivity.csv")
    fr = s[s["mode"] == "FR"]
    designs = list(dict.fromkeys(fr.design))
    fig, axes = plt.subplots(1, 2, figsize=(9.2, 3.8), sharey=True)
    y = np.arange(len(designs))[::-1]
    for d, yy in zip(designs, y):
        o = fr[(fr.design == d) & (fr.factor == "orientation")]
        axes[0].plot(o.disc80_pct, [yy] * len(o), "-", color=GRID, lw=6, solid_capstyle="round")
        for _, r in o.iterrows():
            axes[0].scatter(r.disc80_pct, yy, s=26, zorder=3, color={"0": INK, "90": "#2f6690", "180": "#c8553d",
                                                                     "270": "#e0a12e"}[str(r.level)])
        k = fr[(fr.design == d) & (fr.factor == "climate")]
        g = fr[(fr.design == d) & (fr.factor == "grid")]
        b = o[o.level.astype(str) == "0"]
        if len(b):
            axes[1].scatter(b.disc80_pct, [yy], s=26, color=INK, zorder=3)
        if len(k):
            axes[1].scatter(k.disc80_pct, [yy], s=30, marker="D", color="#3a7d44", zorder=3)
        if len(g):
            axes[1].scatter(g.disc80_pct, [yy], s=40, marker="|", color="#c8553d", zorder=4)
    for lab, col in (("0° (base)", INK), ("90°", "#2f6690"), ("180°", "#c8553d"), ("270°", "#e0a12e")):
        axes[0].scatter([], [], color=col, s=26, label=lab)
    axes[1].scatter([], [], color=INK, s=26, label="Kolkata, base")
    axes[1].scatter([], [], color="#3a7d44", marker="D", s=30, label="Kharagpur (Midnapore weather)")
    axes[1].scatter([], [], color="#c8553d", marker="|", s=40, label="fine grid (C = 1.0)")
    axes[0].set_yticks(y, designs)
    axes[0].set_xlabel("Discomfort, free-running (%)")
    axes[1].set_xlabel("Discomfort, free-running (%)")
    axes[0].set_title("building orientation", loc="left", fontsize=10, color=INK)
    axes[1].set_title("climate and numerics", loc="left", fontsize=10, color=INK)
    axes[0].legend(fontsize=7.5, loc="lower right")
    axes[1].legend(fontsize=7.5, loc="lower right")
    fig.suptitle("Sensitivity of the key designs", x=0.01, ha="left", fontsize=11, color=INK)
    fig.tight_layout()
    fig.savefig(ASSETS / "r_sensitivity.png")
    plt.close(fig)


if __name__ == "__main__":
    import sys
    which = sys.argv[1:] or ["cycles", "validation", "front", "sensitivity"]
    funcs = {"cycles": fig_cycles, "validation": fig_opt_validation, "front": fig_opt_front, "sensitivity": fig_sensitivity}
    for w in which:
        try:
            funcs[w]()
            print("ok", w)
        except FileNotFoundError as e:
            print("skipped", w, "(missing input:", e.filename, ")")
