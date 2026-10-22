"""Post-processing helpers: PCM charge/discharge (melt/freeze) statistics."""
import numpy as np

from model import Case, pcm_node_range, SEGMENTS, _seg_facade
from run import SEASONS

# Representative surfaces for each PCM location
REP_SURFACE = {"roof_top": "BED_ROOF", "roof_bottom": "BED_ROOF"}
for _i, (_z, _p1, _p2, _b) in enumerate(SEGMENTS):
    if _b == "ext" and _z in ("BED", "LIV"):
        REP_SURFACE.setdefault(f"wall_{_seg_facade(_p1, _p2)}", f"{_z}_WALL_{_seg_facade(_p1, _p2)}_{_i}".upper())


def pcm_layer_temperature(series, case: Case, element: str):
    """Mean temperature of the PCM layer (average of the nodes bounding it), hourly."""
    surf = REP_SURFACE[element]
    kind = "roof_top" if element == "roof_top" else "roof_bottom" if element == "roof_bottom" else "wall"
    a, b = pcm_node_range(case, kind)
    nodes = [series[(surf, f"CondFD Surface Temperature Node {n}")] for n in range(a, b + 1)]
    return np.mean(nodes, axis=0)


def cycle_stats(t_layer, case: Case, month):
    """Daily melt/freeze classification of a PCM layer.

    full     : layer passes below the solidus AND above the liquidus on the same day
    liquid   : stays above the solidus all day (never re-solidifies)
    solid    : stays below the liquidus all day (never fully melts)
    utilisation: mean daily swing of melt fraction (0 = latent heat unused, 1 = fully cycled)
    """
    p = case.pcm_props()
    ts, tl = p["tm"] - p["dt"] / 2, p["tm"] + p["dt"] / 2
    d = t_layer.reshape(365, 24)
    dmax, dmin = d.max(1), d.min(1)
    fl_max = np.clip((dmax - ts) / (tl - ts), 0, 1)
    fl_min = np.clip((dmin - ts) / (tl - ts), 0, 1)
    util = fl_max - fl_min
    full = (dmin < ts) & (dmax > tl)
    stuck_liquid = dmin >= ts
    stuck_solid = dmax <= tl
    m = month.reshape(365, 24)[:, 0]
    out = {"util_year": float(util.mean()), "full_days": int(full.sum()),
           "never_solid_days": int(stuck_liquid.sum()), "never_liquid_days": int(stuck_solid.sum())}
    for s, months in SEASONS.items():
        sel = np.isin(m, months)
        out[f"util_{s}"] = float(util[sel].mean())
        out[f"full_frac_{s}"] = float(full[sel].mean())
        out[f"never_solid_frac_{s}"] = float(stuck_liquid[sel].mean())
        out[f"never_liquid_frac_{s}"] = float(stuck_solid[sel].mean())
    return out
