"""Phase 3 - analysis of the parametric study: summary tables + figures.

    python results_phase3.py
Reads results/parametric_{FR,AC,fan,bench}.csv, writes results/phase3_*.csv and docs/assets/r_*.png.
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from run import ROOT, TARIFF, EMISSION_FACTOR
from pymoo.util.nds.non_dominated_sorting import NonDominatedSorting

RES = ROOT / "results"
ASSETS = ROOT / "docs" / "assets"
INK, MUTED, GRID = "#1d2733", "#5b6773", "#d9dee3"
PCM_COL = {"C17": "#2f6690", "C18": "#e0a12e", "C19": "#c8553d", "C20": "#7a4ea3"}
PCM_LAB = {"C17": "C17 (22 °C)", "C18": "C18 (28 °C)", "C19": "C19 (32 °C)", "C20": "C20 (36.6 °C)"}
ROOF_LAB = {"none": "no roof PCM", "top": "roof: top of slab", "bottom": "roof: ceiling underside"}
plt.rcParams.update({
    "font.family": "Calibri", "font.size": 10, "axes.edgecolor": MUTED, "axes.labelcolor": INK,
    "xtick.color": MUTED, "ytick.color": MUTED, "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6, "axes.axisbelow": True,
    "legend.frameon": False, "savefig.dpi": 220, "savefig.bbox": "tight",
})
WALL_ORDER = ["", "N", "E", "S", "W", "EN", "NS", "NW", "ES", "EW", "SW", "ENS", "ENW", "NSW", "ESW", "ENSW"]


def load(name):
    df = pd.read_csv(RES / f"parametric_{name}.csv", keep_default_na=False)
    df["walls"] = df["walls"].astype(str)
    df["thk_mm"] = (df["thk"].astype(float) * 1000).round().astype(int)
    df["night_vent"] = df["night_vent"].astype(str) == "True"
    return df


def merged():
    fr, ac = load("FR"), load("AC")
    k = ["roof", "walls", "pcm", "thk_mm", "night_vent"]
    m = fr.merge(ac[k + ["epi_cool", "ac_elec_kwh", "ac_elec_kwh_summer", "ac_elec_kwh_monsoon",
                         "ac_elec_kwh_postmonsoon", "ac_elec_kwh_winter", "cool_load_kwh"]], on=k, how="inner")
    for nv in (False, True):
        b = m[(m.roof == "none") & (m.walls == "") & (m.night_vent == nv)].iloc[0]
        sel = m.night_vent == nv
        m.loc[sel, "d_disc80"] = b["disc80_pct"] - m.loc[sel, "disc80_pct"]
        m.loc[sel, "d_hot80_h"] = b["hot80_h"] - m.loc[sel, "hot80_h"]
        m.loc[sel, "kwh_saved"] = b["ac_elec_kwh"] - m.loc[sel, "ac_elec_kwh"]
    m["epi_saving_pct"] = 100 * m["kwh_saved"] / (m["kwh_saved"] + m["ac_elec_kwh"])
    m["rs_saved_yr"] = m["kwh_saved"] * TARIFF
    m["payback_yr"] = np.where(m["rs_saved_yr"] > 0, m["pcm_cost_rs"] / m["rs_saved_yr"], np.inf)
    m["co2_saved_kg_yr"] = m["kwh_saved"] * EMISSION_FACTOR
    m["label"] = m.apply(label, axis=1)
    return m


def label(r):
    if r["roof"] == "none" and r["walls"] == "":
        return "baseline (no PCM)"
    parts = []
    if r["roof"] != "none":
        parts.append({"top": "roof-top", "bottom": "ceiling"}[r["roof"]])
    if r["walls"]:
        parts.append("walls " + r["walls"])
    return f"{' + '.join(parts)}, {r['pcm']} {r['thk_mm']} mm"


# ------------------------------------------------------------------------------------------
def fig_placement(m):
    fig, axes = plt.subplots(1, 2, figsize=(9.2, 5.2))
    sub = m[(m.pcm.isin(["C18", "-"])) & (m.thk_mm.isin([10, 0])) & (~m.night_vent)]
    for ax, col, title, cmap in [(axes[0], "disc80_pct", "Free-running: % hours outside IMAC-R 80 %", "YlOrRd"),
                                 (axes[1], "epi_cool", "AC: cooling EPI (kWh/m²·yr)", "YlGnBu")]:
        Z = np.full((16, 3), np.nan)
        for i, w in enumerate(WALL_ORDER):
            for j, roof in enumerate(("none", "top", "bottom")):
                r = sub[(sub.walls == w) & (sub.roof == roof)]
                if len(r):
                    Z[i, j] = r[col].iloc[0]
        im = ax.imshow(Z, cmap=cmap, aspect="auto")
        for i in range(16):
            for j in range(3):
                if not np.isnan(Z[i, j]):
                    ax.text(j, i, f"{Z[i, j]:.1f}", ha="center", va="center", fontsize=8,
                            color="white" if (Z[i, j] - np.nanmin(Z)) / (np.nanmax(Z) - np.nanmin(Z)) > 0.6 else INK)
        ax.set_xticks(range(3), ["none", "top of slab", "ceiling"])
        ax.set_yticks(range(16), [w or "none" for w in WALL_ORDER])
        ax.set_xlabel("roof PCM")
        ax.set_ylabel("walls with PCM")
        ax.set_title(title, loc="left", fontsize=10, color=INK)
        ax.grid(False)
    fig.suptitle("Where to put the PCM (n-octadecane, 10 mm, windows closed at night)", x=0.01, ha="left",
                 fontsize=11, color=INK)
    fig.tight_layout()
    fig.savefig(ASSETS / "r_placement.png")
    plt.close(fig)


def fig_melting(m, util=None):
    locs = [("roof-top", (m.roof == "top") & (m.walls == "")), ("ceiling", (m.roof == "bottom") & (m.walls == "")),
            ("all walls", (m.roof == "none") & (m.walls == "ENSW"))]
    fig, axes = plt.subplots(1, 2, figsize=(9.2, 3.4))
    w = 0.2
    for k, (metric, ax, ylab) in enumerate([("d_disc80", axes[0], "Reduction in discomfort (percentage points)"),
                                            ("epi_saving_pct", axes[1], "Cooling-energy saving (%)")]):
        for i, pcm in enumerate(("C17", "C18", "C19", "C20")):
            vals = []
            for _, sel in locs:
                r = m[sel & (m.pcm == pcm) & (m.thk_mm == 10) & (~m.night_vent)]
                vals.append(r[metric].iloc[0] if len(r) else np.nan)
            ax.bar(np.arange(3) + (i - 1.5) * w, vals, w, color=PCM_COL[pcm], label=PCM_LAB[pcm])
        ax.set_xticks(range(3), [l for l, _ in locs])
        ax.set_ylabel(ylab)
        ax.axhline(0, color=MUTED, lw=0.8)
    axes[0].legend(fontsize=8, ncol=2, loc="upper right")
    axes[0].set_title("Comfort (free-running)", loc="left", fontsize=10, color=INK)
    axes[1].set_title("Energy (air-conditioned)", loc="left", fontsize=10, color=INK)
    fig.suptitle("Effect of melting temperature, 10 mm PCM, windows closed at night", x=0.01, ha="left",
                 fontsize=11, color=INK)
    fig.tight_layout()
    fig.savefig(ASSETS / "r_melting.png")
    plt.close(fig)


def fig_seasons(m):
    picks = [("baseline", (m.roof == "none") & (m.walls == "")),
             ("roof-top C18", (m.roof == "top") & (m.walls == "") & (m.pcm == "C18")),
             ("roof-top C19", (m.roof == "top") & (m.walls == "") & (m.pcm == "C19")),
             ("roof-top C20", (m.roof == "top") & (m.walls == "") & (m.pcm == "C20")),
             ("ceiling C18", (m.roof == "bottom") & (m.walls == "") & (m.pcm == "C18")),
             ("all walls C18", (m.roof == "none") & (m.walls == "ENSW") & (m.pcm == "C18"))]
    seasons = [("summer", "Mar–May"), ("monsoon", "Jun–Sep"), ("postmonsoon", "Oct–Nov"), ("winter", "Dec–Feb")]
    fig, axes = plt.subplots(1, 2, figsize=(9.2, 3.5), sharey=True)
    for ax, nv in zip(axes, (False, True)):
        w = 0.13
        for i, (lab, sel) in enumerate(picks):
            r = m[sel & ((m.thk_mm == 10) | (m.thk_mm == 0)) & (m.night_vent == nv)].iloc[0]
            hot = [r[f"hot80_pct_{s}"] for s, _ in seasons]
            cold = [r[f"cold80_pct_{s}"] for s, _ in seasons]
            x = np.arange(4) + (i - 2.5) * w
            col = plt.cm.viridis(i / (len(picks) - 1)) if i else "#9aa5b1"
            ax.bar(x, hot, w, color=col, label=lab)
            ax.bar(x, cold, w, bottom=hot, color=col, alpha=0.45, hatch="///", edgecolor="white", lw=0)
        ax.set_xticks(range(4), [f"{s}\n{d}" for s, d in seasons])
        ax.set_title("windows closed at night" if not nv else "night ventilation", loc="left", fontsize=10, color=INK)
    axes[0].set_ylabel("% of occupied hours outside IMAC-R 80 %\n(solid = too hot, hatched = too cold)")
    axes[1].legend(fontsize=7.8, loc="upper right")
    fig.suptitle("Summer vs winter: seasonal discomfort, 10 mm PCM (free-running)", x=0.01, ha="left", fontsize=11, color=INK)
    fig.tight_layout()
    fig.savefig(ASSETS / "r_seasons.png")
    plt.close(fig)


def fig_tradeoff(m):
    fig, axes = plt.subplots(1, 2, figsize=(9.2, 3.8))
    for ax, nv in zip(axes, (False, True)):
        d = m[m.night_vent == nv]
        sc = ax.scatter(d["disc80_pct"], d["epi_cool"], c=d["pcm_cost_rs"] / 1e5, cmap="viridis", s=9, alpha=0.75, lw=0)
        F = d[["disc80_pct", "epi_cool", "pcm_cost_rs"]].to_numpy()
        nd = NonDominatedSorting().do(F[:, :2], only_non_dominated_front=True)
        pf = d.iloc[nd].sort_values("disc80_pct")
        ax.plot(pf["disc80_pct"], pf["epi_cool"], "-", color="#c8553d", lw=1.4, label="comfort–energy Pareto front")
        b = d[(d.roof == "none") & (d.walls == "")].iloc[0]
        ax.scatter([b["disc80_pct"]], [b["epi_cool"]], marker="*", s=160, color="black", label="baseline", zorder=5)
        ax.set_xlabel("Discomfort, free-running (% hours outside IMAC-R 80 %)")
        ax.set_title("windows closed at night" if not nv else "night ventilation", loc="left", fontsize=10, color=INK)
        ax.legend(fontsize=8, loc="upper left")
    axes[0].set_ylabel("Cooling EPI with AC (kWh/m²·yr)")
    cb = fig.colorbar(sc, ax=axes, shrink=0.85, pad=0.02)
    cb.set_label("Retrofit cost (lakh Rs)")
    fig.suptitle("All 1,130 designs: comfort vs energy vs cost", x=0.01, ha="left", fontsize=11, color=INK)
    fig.savefig(ASSETS / "r_tradeoff.png")
    plt.close(fig)


def fig_cost(m):
    fig, ax = plt.subplots(figsize=(9.2, 3.6))
    for roof, mk in (("top", "o"), ("bottom", "s")):
        for pcm in ("C17", "C18", "C19", "C20"):
            d = m[(m.roof == roof) & (m.walls == "") & (m.pcm == pcm) & (~m.night_vent)].sort_values("thk_mm")
            ax.plot(d["pcm_cost_rs"] / 1e3, d["kwh_saved"], marker=mk, color=PCM_COL[pcm], lw=1.2, ms=5,
                    ls="-" if roof == "top" else "--", label=f"{'roof-top' if roof == 'top' else 'ceiling'} {pcm}")
            for _, r in d.iterrows():
                ax.annotate(f"{r['thk_mm']}", (r["pcm_cost_rs"] / 1e3, r["kwh_saved"]), fontsize=6.5, color=MUTED,
                            xytext=(3, 3), textcoords="offset points")
    xs = np.linspace(1, ax.get_xlim()[1], 50)
    for yrs in (10, 25, 50):
        ax.plot(xs, xs * 1e3 / (TARIFF * yrs), color=GRID, lw=1, ls=":")
        ax.text(xs[-1], xs[-1] * 1e3 / (TARIFF * yrs), f" {yrs}-yr payback", fontsize=7.5, color=MUTED, va="center")
    ax.set_xlabel("Retrofit cost (thousand Rs)  —  labels: PCM thickness in mm")
    ax.set_ylabel("AC electricity saved (kWh/yr)")
    ax.legend(fontsize=7.5, ncol=4, loc="upper left")
    ax.set_title("Cost-effectiveness of roof PCM (windows closed at night)", loc="left", fontsize=11, color=INK)
    fig.savefig(ASSETS / "r_cost.png")
    plt.close(fig)


def fig_bench():
    b = pd.read_csv(RES / "parametric_bench.csv", keep_default_na=False)
    b["night_vent"] = b["night_vent"].astype(str) == "True"
    def name(r):
        parts = []
        if r["roof"] == "top":
            parts.append(f"PCM {r['pcm']} 10 mm")
        if str(r.get("roof_ins_mm", "0")) not in ("0", "", "0.0"):
            parts.append(f"XPS {int(float(r['roof_ins_mm']))} mm")
        if str(r.get("cool_roof", "False")) == "True":
            parts.append("cool roof")
        return " + ".join(parts) or "baseline"
    b["name"] = b.apply(name, axis=1)
    fr = b[(b["mode"] == "FR") & (~b.night_vent)].set_index("name")
    ac = b[(b["mode"] == "AC") & (~b.night_vent)].set_index("name")
    order = ["baseline", "cool roof", "XPS 25 mm", "XPS 50 mm", "PCM C18 10 mm + cool roof", "PCM C19 10 mm + cool roof",
             "PCM C18 10 mm + XPS 25 mm", "PCM C19 10 mm + XPS 25 mm"]
    order = [o for o in order if o in fr.index]
    fig, axes = plt.subplots(1, 3, figsize=(9.2, 3.4), sharey=True)
    y = np.arange(len(order))[::-1]
    for ax, (col, src, lab) in zip(axes, [("disc80_pct", fr, "% hours outside IMAC-R 80 %"),
                                          ("epi_cool", ac, "cooling EPI (kWh/m²·yr)"),
                                          ("pcm_cost_rs", fr, "cost (thousand Rs)")]):
        v = [src.loc[o, col] / (1e3 if col == "pcm_cost_rs" else 1) for o in order]
        ax.barh(y, v, color=["#9aa5b1"] + ["#2f6690"] * 3 + ["#e0a12e"] * (len(order) - 4))
        for yy, vv in zip(y, v):
            ax.text(vv, yy, f" {vv:.1f}", va="center", fontsize=8, color=INK)
        ax.set_xlabel(lab)
        ax.grid(axis="y", visible=False)
    axes[0].set_yticks(y, order)
    fig.suptitle("Benchmarks: PCM vs cheap conventional roof measures (windows closed at night)", x=0.01, ha="left",
                 fontsize=11, color=INK)
    fig.tight_layout()
    fig.savefig(ASSETS / "r_bench.png")
    plt.close(fig)
    return b


def tables(m):
    cols = ["label", "night_vent", "disc80_pct", "d_disc80", "hot80_h", "cold80_h", "Top_max", "epi_cool", "epi_saving_pct",
            "kwh_saved", "pcm_cost_rs", "payback_yr", "co2_saved_kg_yr"]
    m.sort_values("disc80_pct")[cols].head(25).to_csv(RES / "phase3_best_comfort.csv", index=False, float_format="%.3f")
    m.sort_values("epi_cool")[cols].head(25).to_csv(RES / "phase3_best_energy.csv", index=False, float_format="%.3f")
    pb = m[np.isfinite(m.payback_yr) & (m.kwh_saved > 0)].sort_values("payback_yr")
    pb[cols].head(25).to_csv(RES / "phase3_best_payback.csv", index=False, float_format="%.3f")
    m.to_csv(RES / "phase3_merged.csv", index=False, float_format="%.4f")


if __name__ == "__main__":
    m = merged()
    tables(m)
    fig_placement(m)
    fig_melting(m)
    fig_seasons(m)
    fig_tradeoff(m)
    fig_cost(m)
    if (RES / "parametric_bench.csv").exists():
        fig_bench()
    print("phase 3 figures and tables written")
