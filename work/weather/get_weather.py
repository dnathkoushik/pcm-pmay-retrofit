"""Download the weather files used in this project from climate.onebuilding.org.

    python work/weather/get_weather.py

Kolkata (Netaji Subhas Chandra Bose Intl. Airport, WMO 428090) TMYx 2011-2025 is the main file;
Midnapore (WMO 428030, ~10 km from Kharagpur) is used as the Kharagpur proxy.
"""
import io
import urllib.request
import zipfile
from pathlib import Path

BASE = "https://climate.onebuilding.org/WMO_Region_2_Asia/IND_India/WB_West_Bengal/"
FILES = [
    "IND_WB_Kolkata-Bose.Intl.AP.428090_TMYx.2011-2025",
    "IND_WB_Midnapore.428030_TMYx.2011-2025",
]

here = Path(__file__).resolve().parent
for name in FILES:
    dest = here / name
    if (dest / f"{name}.epw").exists():
        print("already present:", name)
        continue
    print("downloading", name)
    data = urllib.request.urlopen(BASE + name + ".zip", timeout=120).read()
    dest.mkdir(exist_ok=True)
    zipfile.ZipFile(io.BytesIO(data)).extractall(dest)
print("done")
