"""Weather-file utilities: read an EPW, compute running means and the IMAC-R comfort band.

IMAC-R (Rawal et al. 2022, Building and Environment 219, 109187), Fig. 15(b):
    T_neutral = 0.42 * T_out,30DRM + 17.60   [degC]
    90 % acceptability: T_neutral +/- 2.15 degC
    80 % acceptability: T_neutral +/- 3.60 degC
    applicable for 5.5 <= T_out,30DRM <= 33 degC, naturally ventilated / mixed-mode homes.
T_out,30DRM is the simple (unweighted) 30-day running mean of daily mean outdoor temperature.
"""
import csv
import numpy as np

EPW_COLS = {"month": 1, "day": 2, "hour": 3, "tdb": 6, "tdp": 7, "rh": 8,
            "ghi": 13, "dni": 14, "dhi": 15, "wdir": 20, "wspd": 21}

IMACR_SLOPE, IMACR_INTERCEPT = 0.42, 17.60
IMACR_BAND = {80: 3.60, 90: 2.15}


def read_epw(path):
    """Return dict of numpy arrays (8760 values each) plus header metadata."""
    with open(path, newline="", encoding="latin-1") as f:
        rows = list(csv.reader(f))
    header = rows[:8]
    data = rows[8:]
    out = {k: np.array([float(r[i]) for r in data]) for k, i in EPW_COLS.items()}
    loc = header[0]
    out["meta"] = {"city": loc[1], "state": loc[2], "country": loc[3], "source": loc[4],
                   "wmo": loc[5], "lat": float(loc[6]), "lon": float(loc[7]),
                   "tz": float(loc[8]), "elev": float(loc[9])}
    # ground temperatures (EPW header line 4): depth blocks of 16 fields
    g = header[3]
    n = int(g[1])
    grounds = []
    for k in range(n):
        blk = g[2 + 16 * k: 2 + 16 * (k + 1)]
        grounds.append({"depth": float(blk[0]), "monthly": [float(x) for x in blk[4:16]]})
    out["meta"]["ground"] = grounds
    return out


def daily_mean(t_hourly):
    return t_hourly.reshape(365, 24).mean(axis=1)


def running_mean_30d(t_hourly):
    """30-day running mean of the *previous* 30 daily means (wraps around the year,
    which is the usual practice for a typical-year weather file)."""
    dm = daily_mean(t_hourly)
    ext = np.concatenate([dm[-30:], dm])
    return np.array([ext[d:d + 30].mean() for d in range(365)])


def imacr_band(t30, acceptability=80):
    tn = IMACR_SLOPE * np.asarray(t30) + IMACR_INTERCEPT
    b = IMACR_BAND[acceptability]
    return tn, tn - b, tn + b


def monthly_summary(w):
    """Monthly mean of daily max / mean / min dry-bulb, RH, and night (22-06 h) mean."""
    t = w["tdb"].reshape(365, 24)
    months = w["month"].reshape(365, 24)[:, 0].astype(int)
    hours = np.arange(24)
    night = (hours >= 22) | (hours < 6)
    rows = []
    for m in range(1, 13):
        sel = months == m
        td = t[sel]
        rows.append({
            "month": m,
            "tmax": td.max(axis=1).mean(),
            "tmean": td.mean(),
            "tmin": td.min(axis=1).mean(),
            "tnight": td[:, night].mean(),
            "rh": w["rh"].reshape(365, 24)[sel].mean(),
            "ghi_kwh_day": w["ghi"].reshape(365, 24)[sel].sum(axis=1).mean() / 1000,
            "frac_nights_min_below_26": (td.min(axis=1) < 26).mean(),
            "frac_nights_min_below_28": (td.min(axis=1) < 28).mean(),
        })
    return rows


if __name__ == "__main__":
    import sys
    for p in sys.argv[1:]:
        w = read_epw(p)
        m = w["meta"]
        print(f"\n== {m['city']} ({m['wmo']}) lat {m['lat']} lon {m['lon']} src {m['source']}")
        print(f"annual mean {w['tdb'].mean():.1f}  max {w['tdb'].max():.1f}  min {w['tdb'].min():.1f}  "
              f"RH {w['rh'].mean():.0f}%")
        t30 = running_mean_30d(w["tdb"])
        print(f"30DRM range {t30.min():.1f} - {t30.max():.1f}")
        print("mon  Tmax  Tmean Tmin  Tnight RH   GHI   min<26 min<28")
        for r in monthly_summary(w):
            print(f"{r['month']:>3} {r['tmax']:5.1f} {r['tmean']:5.1f} {r['tmin']:5.1f} {r['tnight']:6.1f} "
                  f"{r['rh']:4.0f} {r['ghi_kwh_day']:5.2f} {r['frac_nights_min_below_26']:6.2f} "
                  f"{r['frac_nights_min_below_28']:6.2f}")
        print("ground temps:", [(g["depth"], [round(x, 1) for x in g["monthly"]]) for g in m["ground"]])
        hrs = w["tdb"]
        print(f"hours > 35C: {(hrs > 35).sum()}, hours > 30C: {(hrs > 30).sum()}, hours < 15C: {(hrs < 15).sum()}")
