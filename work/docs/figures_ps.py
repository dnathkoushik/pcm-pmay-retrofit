"""Figures for the problem-statement document (written to work/docs/assets)."""
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "src"))
from climate import read_epw, running_mean_30d, imacr_band, monthly_summary  # noqa: E402
from model import ZONES, SEGMENTS, OPENINGS, WIN_W, DOOR_W, PCMS  # noqa: E402
from run import WEATHER  # noqa: E402

ASSETS = HERE / "assets"
ASSETS.mkdir(exist_ok=True)

INK = "#1d2733"
MUTED = "#5b6773"
GRID = "#d9dee3"
C_HOT = "#c8553d"
C_COOL = "#2f6690"
C_PCM = "#e0a12e"
C_BAND = "#3a7d44"

plt.rcParams.update({
    "font.family": "Calibri", "font.size": 10, "axes.edgecolor": MUTED, "axes.labelcolor": INK,
    "xtick.color": MUTED, "ytick.color": MUTED, "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6, "axes.axisbelow": True,
    "legend.frameon": False, "savefig.dpi": 220, "savefig.bbox": "tight",
})
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def climate_figure():
    w = read_epw(WEATHER["kolkata"])
    rows = monthly_summary(w)
    t30 = running_mean_30d(w["tdb"])
    mon_day = w["month"].reshape(365, 24)[:, 0].astype(int)
    t30_m = np.array([t30[mon_day == m].mean() for m in range(1, 13)])
    tn, lo, hi = imacr_band(t30_m, 80)
    x = np.arange(12)
    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(9.2, 3.5), gridspec_kw={"width_ratios": [1.65, 1]})
    tmax = [r["tmax"] for r in rows]
    tmin = [r["tmin"] for r in rows]
    tnight = [r["tnight"] for r in rows]
    ax.fill_between(x, lo, hi, color=C_BAND, alpha=0.13, lw=0, label="IMAC-R 80 % comfort band")
    pcm = PCMS["C18"]
    ax.axhspan(pcm["tm"] - pcm["dt"] / 2, pcm["tm"] + pcm["dt"] / 2, color=C_PCM, alpha=0.35, lw=0,
               label="n-octadecane melting range")
    ax.plot(x, tmax, "-o", color=C_HOT, ms=3.5, lw=1.8, label="mean daily maximum")
    ax.plot(x, tnight, "-o", color="#7a4ea3", ms=3.5, lw=1.8, label="mean night (22-06 h)")
    ax.plot(x, tmin, "-o", color=C_COOL, ms=3.5, lw=1.8, label="mean daily minimum")
    ax.set_xticks(x, MONTHS)
    ax.set_ylabel("Outdoor dry-bulb temperature (°C)")
    ax.set_ylim(10, 40)
    ax.legend(loc="lower center", fontsize=8.2, ncol=2)
    ax.set_title("Kolkata: monthly temperatures vs PCM melting range", loc="left", fontsize=10.5, color=INK)
    below26 = [100 * r["frac_nights_min_below_26"] for r in rows]
    bars = ax2.bar(x, below26, color=[C_COOL if v >= 50 else C_HOT for v in below26], width=0.7)
    ax2.set_xticks(x, [m[0] for m in MONTHS])
    ax2.set_ylim(0, 105)
    ax2.set_ylabel("Nights with minimum < 26 °C (%)")
    ax2.set_title("Can a 28 °C PCM re-solidify at night?", loc="left", fontsize=10.5, color=INK)
    for b, v in zip(bars, below26):
        if v < 50:
            ax2.text(b.get_x() + b.get_width() / 2, v + 2, f"{v:.0f}", ha="center", fontsize=7.5, color=C_HOT)
    fig.tight_layout()
    fig.savefig(ASSETS / "climate_kolkata.png")
    plt.close(fig)
    return rows, t30


def plan_figure():
    fig, ax = plt.subplots(figsize=(5.4, 5.0))
    colors = {"BED": "#dbe9f6", "LIV": "#fbe7d0", "TOI": "#e5e5e5"}
    labels = {"BED": "BED\nbedroom\n2.9 x 3.1 m", "LIV": "LIV\nmulti-purpose room\n+ kitchen + passage",
              "TOI": "TOI  (WC + bath)"}
    for z, poly in ZONES.items():
        xs, ys = zip(*poly)
        ax.add_patch(plt.Polygon(poly, closed=True, fc=colors[z], ec=INK, lw=1.6))
        ax.text(np.mean(xs), np.mean(ys), labels[z], ha="center", va="center", fontsize=9, color=INK)
    for z, p1, kind, c in OPENINGS:
        seg = [s for s in SEGMENTS if s[0] == z and s[1] == p1][0]
        (x1, y1), (x2, y2) = seg[1], seg[2]
        L = np.hypot(x2 - x1, y2 - y1)
        ux, uy = (x2 - x1) / L, (y2 - y1) / L
        wdt = WIN_W if kind == "W1" else DOOR_W
        a = (x1 + ux * (c - wdt / 2), y1 + uy * (c - wdt / 2))
        b = (x1 + ux * (c + wdt / 2), y1 + uy * (c + wdt / 2))
        ax.plot([a[0], b[0]], [a[1], b[1]], color=C_COOL if kind == "W1" else "#8b5a2b", lw=5, solid_capstyle="butt")
    for xx in (2.4, 3.4, 4.4):  # WO2 jali openings, north wall of toilet block
        ax.plot([xx - 0.375, xx + 0.375], [6.1, 6.1], color=MUTED, lw=5, solid_capstyle="butt", alpha=0.6)
    ax.annotate("N", xy=(7.15, 6.0), xytext=(7.15, 5.2), ha="center", fontsize=11, color=INK,
                arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.5))
    ax.plot([], [], color=C_COOL, lw=5, label="window W1 (0.9 x 0.9 m)")
    ax.plot([], [], color="#8b5a2b", lw=5, label="entrance door D1")
    ax.plot([], [], color=MUTED, lw=5, alpha=0.6, label="RCC jali ventilator WO2")
    ax.legend(loc="lower left", bbox_to_anchor=(-0.02, -0.2), ncol=3, fontsize=7.8)
    ax.set_xlim(-0.4, 7.6)
    ax.set_ylim(-0.4, 6.6)
    ax.set_aspect("equal")
    ax.set_xlabel("x (m)")
    ax.set_ylabel("y (m)")
    ax.set_title("Simulation model: three thermal zones (plan)", loc="left", fontsize=10.5, color=INK)
    fig.savefig(ASSETS / "model_plan.png")
    plt.close(fig)


def _box(ax, x, y, w, h, text, fc, fs=8.6, bold=False):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.06", fc=fc, ec=INK, lw=0.9))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs, color=INK,
            fontweight="bold" if bold else "normal", wrap=True)


def _arrow(ax, x1, y1, x2, y2):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1), arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.0))


def method_figure():
    fig, ax = plt.subplots(figsize=(9.2, 4.6))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 5)
    ax.axis("off")
    inputs = [("PMAY-U BLC house\n(WB drawing)", 4.15), ("Weather: Kolkata TMYx\n+ Midnapore (Kharagpur)", 3.25),
              ("PCM properties\n(n-alkanes C17-C20)", 2.35), ("Occupancy, ventilation\n& AC schedules", 1.45)]
    for t, y in inputs:
        _box(ax, 0.1, y, 2.0, 0.7, t, "#eef2f6")
        _arrow(ax, 2.1, y + 0.35, 2.55, 2.85)
    _box(ax, 2.55, 2.2, 1.9, 1.3, "EnergyPlus 26.2\nCondFD algorithm\nPCM enthalpy model\n(3 zones, 1 h output)", "#fbe7d0", bold=False)
    _arrow(ax, 4.45, 2.85, 4.85, 2.85)
    _box(ax, 4.85, 3.35, 2.1, 0.95, "Free-running (FR)\n& ceiling fan (FAN):\nIMAC-R discomfort hours", "#e4f1e6")
    _box(ax, 4.85, 2.2, 2.1, 0.95, "Air-conditioned (AC):\ncooling EPI\n(kWh/m²·yr)", "#dbe9f6")
    _box(ax, 4.85, 1.05, 2.1, 0.95, "Cost, payback,\nCO₂ savings,\nPCM melt/freeze use", "#f6efd9")
    _arrow(ax, 4.45, 2.85, 4.85, 3.8)
    _arrow(ax, 4.45, 2.85, 4.85, 1.5)
    _box(ax, 7.4, 2.9, 2.5, 1.4, "Phase 3: full-factorial\nparametric study\n(placement x thickness x\nmelting point x ventilation)", "#ffffff")
    _box(ax, 7.4, 1.15, 2.5, 1.4, "Phase 4: NSGA-II / NSGA-III\n(pymoo) - Pareto front of\ncomfort vs energy vs cost", "#ffffff")
    for y in (3.8, 2.65, 1.5):
        _arrow(ax, 6.95, y, 7.4, 2.9 if y > 2 else 1.85)
    _arrow(ax, 8.65, 2.9, 8.65, 2.55)
    _box(ax, 7.4, 0.15, 2.5, 0.7, "Recommended retrofit\nfor PMAY houses", "#3a7d44", fs=9, bold=True)
    ax.texts[-1].set_color("white")
    _arrow(ax, 8.65, 1.15, 8.65, 0.85)
    _box(ax, 2.55, 0.25, 1.9, 1.3, "Verification:\nCondFD vs CTF,\ngrid & timestep,\nlatent-heat control", "#f2f2f2", fs=8.2)
    _arrow(ax, 3.5, 1.55, 3.5, 2.2)
    fig.savefig(ASSETS / "methodology.png")
    plt.close(fig)


def gantt_figure():
    tasks = [
        ("0  Literature review & scope freeze", "2026-10-20", "2026-11-15", "#5b6773"),
        ("1  Base model (PMAY house, Kolkata)", "2026-10-22", "2026-11-30", "#2f6690"),
        ("   BTP-I report & presentation", "2026-11-10", "2026-11-25", "#9aa5b1"),
        ("2  PCM model & verification", "2026-11-01", "2026-12-31", "#2f6690"),
        ("3  Parametric study (all configurations)", "2026-12-01", "2027-01-31", "#e0a12e"),
        ("4  Multi-objective optimisation (NSGA)", "2027-01-15", "2027-02-28", "#c8553d"),
        ("5  Sensitivity, thesis & BTP-II defence", "2027-03-01", "2027-04-25", "#3a7d44"),
    ]
    import datetime as dt
    d = lambda s: dt.date.fromisoformat(s)
    t0 = d("2026-10-01")
    fig, ax = plt.subplots(figsize=(9.2, 2.9))
    for i, (name, s, e, c) in enumerate(tasks):
        y = len(tasks) - 1 - i
        ax.barh(y, (d(e) - d(s)).days, left=(d(s) - t0).days, color=c, height=0.55)
        ax.text(-3, y, name, ha="right", va="center", fontsize=8.8, color=INK)
    ticks = [d(f"{y}-{m:02d}-01") for y, m in [(2026, 10), (2026, 11), (2026, 12), (2027, 1), (2027, 2), (2027, 3), (2027, 4), (2027, 5)]]
    ax.set_xticks([(t - t0).days for t in ticks], [t.strftime("%b %y") for t in ticks])
    ax.set_yticks([])
    ax.axvline((d("2026-10-22") - t0).days, color=C_HOT, lw=1.2, ls="--")
    ax.text((d("2026-10-22") - t0).days + 2, len(tasks) - 0.45, "today", color=C_HOT, fontsize=8)
    ax.set_xlim(0, (d("2027-05-01") - t0).days)
    ax.spines["left"].set_visible(False)
    ax.grid(axis="y", visible=False)
    fig.savefig(ASSETS / "gantt.png")
    plt.close(fig)


if __name__ == "__main__":
    climate_figure()
    plan_figure()
    method_figure()
    gantt_figure()
    print("figures written to", ASSETS)
