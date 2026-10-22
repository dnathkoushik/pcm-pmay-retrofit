"""EnergyPlus model generator for the West Bengal PMAY-U (BLC) model dwelling unit.

Geometry is taken from the drawing "Model Design of Dwelling Unit for BLC" (Office of the Chief
Engineer, Municipal Engineering Directorate, Govt. of West Bengal). Plan dimensions are used as
centre-line dimensions (mm on the drawing, m here); +x = plan right, +y = plan up. With
orientation = 0 the drawing's "up" points to true North (orientation is a study variable because
the drawing does not give it).

Three thermal zones:
    BED  - bedroom                                   x 0.000-3.025, y 1.325-4.950
    LIV  - multi-purpose room + kitchen + passage    x 3.025-6.400, y 0.000-4.950
    TOI  - WC + bath                                 x 1.900-5.600, y 4.950-6.100
PCM retrofits are applied only to the habitable zones (BED, LIV).

Build a model with build_idf(Case(...)).
"""
from dataclasses import dataclass, field, asdict
from typing import FrozenSet, Optional
import hashlib
import json

H = 2.75          # ceiling height (drawing note 5)
WIN_W, WIN_H, WIN_SILL = 0.90, 0.90, 1.20   # W1 900x900, head at 2.1 m lintel level
DOOR_W, DOOR_H = 0.90, 2.10                 # D1

ZONES = {
    "BED": [(0.000, 1.325), (3.025, 1.325), (3.025, 4.950), (0.000, 4.950)],
    "LIV": [(3.025, 0.000), (6.400, 0.000), (6.400, 4.950), (3.025, 4.950)],
    "TOI": [(1.900, 4.950), (5.600, 4.950), (5.600, 6.100), (1.900, 6.100)],
}
HABITABLE = ("BED", "LIV")

# Wall segments per zone, in counter-clockwise order (viewed from above), so that the
# segment start point is the left end when viewed from outside.
# (zone, p1, p2, boundary) where boundary = "ext" or the adjacent zone name.
SEGMENTS = [
    ("BED", (0.000, 1.325), (3.025, 1.325), "ext"),   # S
    ("BED", (3.025, 1.325), (3.025, 4.950), "LIV"),   # E (partition)
    ("BED", (3.025, 4.950), (1.900, 4.950), "TOI"),   # N (partition)
    ("BED", (1.900, 4.950), (0.000, 4.950), "ext"),   # N
    ("BED", (0.000, 4.950), (0.000, 1.325), "ext"),   # W
    ("LIV", (3.025, 0.000), (6.400, 0.000), "ext"),   # S
    ("LIV", (6.400, 0.000), (6.400, 4.950), "ext"),   # E
    ("LIV", (6.400, 4.950), (5.600, 4.950), "ext"),   # N
    ("LIV", (5.600, 4.950), (3.025, 4.950), "TOI"),   # N (partition)
    ("LIV", (3.025, 4.950), (3.025, 1.325), "BED"),   # W (partition)
    ("LIV", (3.025, 1.325), (3.025, 0.000), "ext"),   # W (entrance, faces verandah)
    ("TOI", (1.900, 4.950), (3.025, 4.950), "BED"),   # S (partition)
    ("TOI", (3.025, 4.950), (5.600, 4.950), "LIV"),   # S (partition)
    ("TOI", (5.600, 4.950), (5.600, 6.100), "ext"),   # E
    ("TOI", (5.600, 6.100), (1.900, 6.100), "ext"),   # N
    ("TOI", (1.900, 6.100), (1.900, 4.950), "ext"),   # W
]

# Openings: (zone, segment p1, kind, centre distance from segment start [m])
OPENINGS = [
    ("BED", (0.000, 1.325), "W1", 1.5125),   # bedroom, south
    ("BED", (0.000, 4.950), "W1", 1.8125),   # bedroom, west
    ("LIV", (3.025, 0.000), "W1", 1.6875),   # multi-purpose room, south
    ("LIV", (6.400, 0.000), "W1", 1.70),     # multi-purpose room, east
    ("LIV", (6.400, 0.000), "W1", 4.20),     # kitchen, east
    ("LIV", (3.025, 1.325), "D1", 0.6625),   # main entrance door, west (verandah)
]
# Toilet block ventilators WO2 (750x750, RCC jali) - modelled as permanent vent openings
JALI_AREA = 3 * 0.75 * 0.75 * 0.5          # 3 openings, ~50 % free area

# ----------------------------------------------------------------------------------------
# Materials  (k W/m-K, rho kg/m3, cp J/kg-K). Values follow ECBC 2017 / NBC tables.
# ----------------------------------------------------------------------------------------
MATERIALS = {
    #  name               rough         k      rho    cp    sol_abs
    "CementPlaster":   ("MediumRough", 0.721, 1762, 840, 0.60),
    "BurntBrick":      ("Rough",       0.811, 1820, 880, 0.70),
    "RCC_M20":         ("MediumRough", 1.580, 2288, 880, 0.70),
    "CementScreed":    ("MediumRough", 0.720, 1648, 920, 0.70),
    "PCC_136":         ("Rough",       1.200, 2200, 880, 0.70),
    "ASFlooring":      ("MediumSmooth",1.300, 2300, 840, 0.60),
    "GypsumBoard":     ("Smooth",      0.160,  800, 1090, 0.50),
    "WoodDoor":        ("MediumSmooth",0.150,  600, 1630, 0.70),
}
THICK = {"plaster_out": 0.015, "plaster_in": 0.012, "brick_ext": 0.250, "brick_part": 0.125,
         "rcc": 0.125, "screed": 0.025, "pcc": 0.075, "dpc": 0.025, "floor": 0.020,
         "gypsum": 0.0125, "door": 0.035}

# ----------------------------------------------------------------------------------------
# PCM library. Pure n-alkane (paraffin) values are typical literature values
# (e.g. Sharma et al. 2009, RSER 13:318) and must be checked against supplier DSC data.
#   tm: peak melting temperature, dt: melting range width, L: latent heat (J/kg)
# ----------------------------------------------------------------------------------------
PCMS = {
    "C17":  {"name": "n-heptadecane", "tm": 22.0, "dt": 2.0, "L": 214e3, "rho": 778, "cp": 2100, "ks": 0.21, "kl": 0.15},
    "C18":  {"name": "n-octadecane",  "tm": 28.2, "dt": 2.0, "L": 244e3, "rho": 800, "cp": 2000, "ks": 0.36, "kl": 0.15},
    "C19":  {"name": "n-nonadecane",  "tm": 32.0, "dt": 2.0, "L": 222e3, "rho": 800, "cp": 2000, "ks": 0.30, "kl": 0.15},
    "C20":  {"name": "n-eicosane",    "tm": 36.6, "dt": 2.0, "L": 247e3, "rho": 800, "cp": 2000, "ks": 0.30, "kl": 0.15},
    "OM37": {"name": "OM37 (Abass & Muthulingam 2024)", "tm": 37.0, "dt": 3.0, "L": 173.9e3, "rho": 880, "cp": 2000, "ks": 0.30, "kl": 0.20},
}


@dataclass(frozen=True)
class Case:
    roof: str = "none"                    # "none" | "top" (above slab, under new screed) | "bottom" (ceiling board)
    walls: FrozenSet[str] = frozenset()   # subset of {"N","E","S","W"}: PCM on inner face of those habitable-zone walls
    thk: float = 0.010                    # PCM layer thickness [m]
    pcm: str = "C18"                      # key in PCMS, or "custom"
    tm: Optional[float] = None            # custom melting temperature (pcm == "custom")
    L: Optional[float] = None             # custom latent heat (pcm == "custom")
    latent: bool = True                   # False = control case: same layer, latent heat removed
    night_vent: bool = False              # windows also open at night (22-06 h)
    mode: str = "FR"                      # "FR" free-running, "FAN" ceiling fans, "AC" air-conditioned
    orientation: float = 0.0              # building north axis [deg]
    ac_setpoint: float = 26.0
    timestep: int = 20
    space_c: float = 3.0                  # CondFD space discretisation constant
    algo: str = "CondFD"                  # "CondFD" or "CTF" (CTF only valid without PCM; verification)
    hourly_pcm_nodes: bool = False        # extra CondFD node outputs (diagnostics)

    def has_pcm(self):
        return self.roof != "none" or len(self.walls) > 0

    def pcm_props(self):
        if self.pcm == "custom":
            base = dict(PCMS["C18"])
            base.update({"name": f"custom Tm={self.tm}", "tm": self.tm, "L": self.L or base["L"]})
        else:
            base = dict(PCMS[self.pcm])
        if not self.latent:
            base["L"] = 0.0
            base["name"] += " (no latent heat)"
        return base

    def key(self):
        d = asdict(self)
        d["walls"] = "".join(sorted(self.walls))
        if not self.has_pcm():          # thickness/PCM irrelevant without PCM
            d.update(thk=0, pcm="-", tm=None, L=None, latent=True)
        return d

    def case_id(self):
        d = self.key()
        w = d["walls"] or "0"
        tag = (f"{'' if self.algo == 'CondFD' else 'CTF_'}{d['mode']}_R{self.roof[0]}_W-{w}_{d['pcm']}{'' if d['latent'] else 'noL'}"
               f"_{int(round(d['thk']*1000))}mm_NV{int(self.night_vent)}_O{int(self.orientation)}")
        if self.pcm == "custom" and self.has_pcm():
            tag += f"_Tm{self.tm:.1f}"
        h = hashlib.md5(json.dumps(d, sort_keys=True, default=str).encode()).hexdigest()[:6]
        return f"{tag}_{h}"


# ----------------------------------------------------------------------------------------
def _seg_facade(p1, p2):
    (x1, y1), (x2, y2) = p1, p2
    if abs(y1 - y2) < 1e-9:
        return "S" if x2 > x1 else "N"
    return "E" if y2 > y1 else "W"


def _obj(obj, *vals):
    return f"{obj},\n    " + ",\n    ".join(str(v) for v in vals) + ";\n"


def _pcm_objects(props, thk):
    """Material + enthalpy curve + variable conductivity for a PCM layer."""
    tm, dt, L, cp = props["tm"], props["dt"], props["L"], props["cp"]
    ts, tl = tm - dt / 2, tm + dt / 2
    tref = -20.0
    pts = [(tref, 0.0), (ts, cp * (ts - tref)), (tl, cp * (tl - tref) + L), (100.0, cp * (100 - tref) + L)]
    name = f"PCM_{thk*1000:.0f}mm"
    out = _obj("Material", name, "Smooth", f"{thk:.4f}", props["ks"], props["rho"], cp, 0.9, 0.6, 0.6)
    vals = [name, 0.0]
    for t, h in pts:
        vals += [f"{t:.2f}", f"{h:.1f}"]
    if L > 0:
        out += _obj("MaterialProperty:PhaseChange", *vals)
    out += _obj("MaterialProperty:VariableThermalConductivity", name,
                f"{ts:.2f}", props["ks"], f"{tl:.2f}", props["kl"])
    return name, out


def _schedules(case: Case):
    """All schedules. Occupancy pattern: family of four (2 adults, 2 children/elders)."""
    s = ""
    s += _obj("ScheduleTypeLimits", "Fraction", 0, 1, "Continuous")
    s += _obj("ScheduleTypeLimits", "AnyNumber")
    s += _obj("ScheduleTypeLimits", "Temperature", -60, 200, "Continuous")
    s += _obj("Schedule:Constant", "AlwaysOn", "Fraction", 1)
    s += _obj("Schedule:Constant", "AlwaysOff", "Fraction", 0)
    # Bedroom: 2 people, sleeping 22-06
    s += _obj("Schedule:Compact", "Occ_BED", "Fraction", "Through: 12/31", "For: AllDays",
              "Until: 06:00", 1.0, "Until: 07:00", 0.5, "Until: 21:00", 0.0, "Until: 22:00", 0.5, "Until: 24:00", 1.0)
    # Multi-purpose room + kitchen: 4 people max; 2 sleep here at night
    s += _obj("Schedule:Compact", "Occ_LIV", "Fraction", "Through: 12/31", "For: AllDays",
              "Until: 06:00", 0.5, "Until: 09:00", 1.0, "Until: 17:00", 0.5, "Until: 22:00", 1.0, "Until: 24:00", 0.5)
    s += _obj("Schedule:Compact", "Act_BED", "AnyNumber", "Through: 12/31", "For: AllDays",
              "Until: 06:00", 72, "Until: 22:00", 108, "Until: 24:00", 72)
    s += _obj("Schedule:Compact", "Act_LIV", "AnyNumber", "Through: 12/31", "For: AllDays",
              "Until: 06:00", 72, "Until: 22:00", 117, "Until: 24:00", 72)
    s += _obj("Schedule:Compact", "Lights", "Fraction", "Through: 12/31", "For: AllDays",
              "Until: 05:00", 0.0, "Until: 07:00", 0.5, "Until: 18:00", 0.0, "Until: 22:00", 1.0, "Until: 24:00", 0.1)
    s += _obj("Schedule:Compact", "TV", "Fraction", "Through: 12/31", "For: AllDays",
              "Until: 18:00", 0.0, "Until: 22:00", 1.0, "Until: 24:00", 0.0)
    s += _obj("Schedule:Compact", "Cooking", "Fraction", "Through: 12/31", "For: AllDays",
              "Until: 07:00", 0.0, "Until: 08:00", 1.0, "Until: 12:00", 0.0, "Until: 13:00", 0.5,
              "Until: 19:00", 0.0, "Until: 20:00", 1.0, "Until: 24:00", 0.0)
    # Comfort-model inputs (Fanger PMV output, used only as a secondary metric)
    s += _obj("Schedule:Constant", "WorkEff", "AnyNumber", 0)
    s += _obj("Schedule:Compact", "Clothing", "AnyNumber", "Through: 2/28", "For: AllDays", "Until: 24:00", 1.0,
              "Through: 11/15", "For: AllDays", "Until: 24:00", 0.5, "Through: 12/31", "For: AllDays", "Until: 24:00", 1.0)
    s += _obj("Schedule:Constant", "AirVel", "AnyNumber", 0.8 if case.mode == "FAN" else 0.1)

    # Ceiling fans (60 W per habitable room) run whenever the room is occupied, 1 Mar - 15 Nov
    for z in HABITABLE:
        s += _obj("Schedule:Compact", f"Fan_{z}", "Fraction",
                  "Through: 2/28", "For: AllDays", "Until: 24:00", 0.0,
                  "Through: 11/15", "For: AllDays", *OCC_ON[z],
                  "Through: 12/31", "For: AllDays", "Until: 24:00", 0.0)

    # Window opening. Day (06-22) always allowed; night only if night_vent.
    night = 1.0 if case.night_vent else 0.0
    day_vent = ["Until: 06:00", night, "Until: 22:00", 1.0, "Until: 24:00", night]
    if case.mode == "AC":
        # AC used 1 Mar - 15 Nov: bedroom while sleeping, living room afternoon + evening.
        # Windows of a room are closed while its AC is available.
        for z in HABITABLE:
            s += _obj("Schedule:Compact", f"ACavail_{z}", "Fraction",
                      "Through: 2/28", "For: AllDays", "Until: 24:00", 0.0,
                      "Through: 11/15", "For: AllDays", *AC_HOURS[z],
                      "Through: 12/31", "For: AllDays", "Until: 24:00", 0.0)
            s += _obj("Schedule:Compact", f"Vent_{z}", "Fraction",
                      "Through: 2/28", "For: AllDays", *day_vent,
                      "Through: 11/15", "For: AllDays", *AC_SEASON_VENT[z](night),
                      "Through: 12/31", "For: AllDays", *day_vent)
        s += _obj("Schedule:Constant", "CoolSP", "Temperature", case.ac_setpoint)
        s += _obj("Schedule:Constant", "TstatType", "AnyNumber", 2)
    else:
        for z in HABITABLE:
            s += _obj("Schedule:Compact", f"Vent_{z}", "Fraction", "Through: 12/31", "For: AllDays", *day_vent)
    return s


# Occupied hours (fans run when the room is occupied)
OCC_ON = {
    "BED": ["Until: 07:00", 1.0, "Until: 21:00", 0.0, "Until: 24:00", 1.0],
    "LIV": ["Until: 24:00", 1.0],
}
# AC availability during the cooling season
AC_HOURS = {
    "BED": ["Until: 07:00", 1.0, "Until: 22:00", 0.0, "Until: 24:00", 1.0],
    "LIV": ["Until: 13:00", 0.0, "Until: 17:00", 1.0, "Until: 19:00", 0.0, "Until: 22:00", 1.0, "Until: 24:00", 0.0],
}
# Window opening during the cooling season in AC mode (closed whenever the AC is available)
AC_SEASON_VENT = {
    "BED": lambda n: ["Until: 07:00", 0.0, "Until: 22:00", 1.0, "Until: 24:00", 0.0],
    "LIV": lambda n: ["Until: 06:00", n, "Until: 13:00", 1.0, "Until: 17:00", 0.0, "Until: 19:00", 1.0,
                      "Until: 22:00", 0.0, "Until: 24:00", n],
}


def build_idf(case: Case, epw_meta: dict) -> str:
    pcm = case.pcm_props()
    out = []
    a = out.append
    a(_obj("Version", "26.2"))
    a(_obj("SimulationControl", "No", "No", "No", "No", "Yes", "No", 1))
    a(_obj("Building", "PMAY_BLC_WestBengal", case.orientation, "Suburbs", 0.04, 0.4, "FullExterior", 50, 6))
    a(_obj("Timestep", case.timestep))
    a(_obj("HeatBalanceAlgorithm", "ConductionFiniteDifference" if case.algo == "CondFD" else "ConductionTransferFunction", 200))
    a(_obj("HeatBalanceSettings:ConductionFiniteDifference", "FullyImplicitFirstOrder", case.space_c, 1.0, 0.002))
    a(_obj("SurfaceConvectionAlgorithm:Inside", "TARP"))
    a(_obj("SurfaceConvectionAlgorithm:Outside", "DOE-2"))
    m = epw_meta
    a(_obj("Site:Location", m["city"], m["lat"], m["lon"], m["tz"], m["elev"]))
    a(_obj("RunPeriod", "Annual", 1, 1, "", 12, 31, "", "", "Yes", "Yes", "No", "Yes", "Yes"))
    a(_obj("GlobalGeometryRules", "UpperLeftCorner", "Counterclockwise", "Relative"))
    g05 = [g for g in m["ground"] if abs(g["depth"] - 0.5) < 0.01][0]["monthly"]
    a(_obj("Site:GroundTemperature:BuildingSurface", *[f"{t:.1f}" for t in g05]))

    # ---- materials & constructions
    mats = {
        "PlasterOut15": ("CementPlaster", THICK["plaster_out"]),
        "PlasterIn12": ("CementPlaster", THICK["plaster_in"]),
        "Brick250": ("BurntBrick", THICK["brick_ext"]),
        "Brick125": ("BurntBrick", THICK["brick_part"]),
        "RCC125": ("RCC_M20", THICK["rcc"]),
        "Screed25": ("CementScreed", THICK["screed"]),
        "PCC75": ("PCC_136", THICK["pcc"]),
        "DPC25": ("PCC_136", THICK["dpc"]),
        "Floor20": ("ASFlooring", THICK["floor"]),
        "Gypsum12": ("GypsumBoard", THICK["gypsum"]),
        "Door35": ("WoodDoor", THICK["door"]),
    }
    for nm, (base, t) in mats.items():
        rough, k, rho, cp, sabs = MATERIALS[base]
        a(_obj("Material", nm, rough, t, k, rho, cp, 0.9, sabs, sabs))
    a(_obj("WindowMaterial:SimpleGlazingSystem", "SingleClear3mm", 5.8, 0.82, 0.88))

    cons = {
        "ExtWall": ["PlasterOut15", "Brick250", "PlasterIn12"],
        "Partition": ["PlasterIn12", "Brick125", "PlasterIn12"],
        "Roof": ["Screed25", "RCC125", "PlasterIn12"],
        "GroundFloor": ["PCC75", "DPC25", "Floor20"],
        "Window": ["SingleClear3mm"],
        "Door": ["Door35"],
    }
    if case.has_pcm():
        pcm_mat, pcm_txt = _pcm_objects(pcm, case.thk)
        a(pcm_txt)
        cons["ExtWall_PCM"] = ["PlasterOut15", "Brick250", "PlasterIn12", pcm_mat, "Gypsum12"]
        cons["Roof_PCMtop"] = ["Screed25", pcm_mat, "Screed25", "RCC125", "PlasterIn12"]
        cons["Roof_PCMbottom"] = ["Screed25", "RCC125", "PlasterIn12", pcm_mat, "Gypsum12"]
    for nm, layers in cons.items():
        a(_obj("Construction", nm, *layers))

    # ---- zones & surfaces
    for z in ZONES:
        a(_obj("Zone", z))
    surf_names = {}
    for i, (z, p1, p2, bnd) in enumerate(SEGMENTS):
        fac = _seg_facade(p1, p2)
        name = f"{z}_Wall_{fac}_{i}"
        surf_names[(z, p1)] = name
    for i, (z, p1, p2, bnd) in enumerate(SEGMENTS):
        fac = _seg_facade(p1, p2)
        name = surf_names[(z, p1)]
        verts = [(p1[0], p1[1], H), (p1[0], p1[1], 0), (p2[0], p2[1], 0), (p2[0], p2[1], H)]
        vtxt = [f"{x:.4f},{y:.4f},{zz:.4f}" for x, y, zz in verts]
        if bnd == "ext":
            con = "ExtWall_PCM" if (z in HABITABLE and fac in case.walls) else "ExtWall"
            a(_obj("BuildingSurface:Detailed", name, "Wall", con, z, "", "Outdoors", "", "SunExposed",
                   "WindExposed", "autocalculate", 4, *vtxt))
        else:
            # paired surface: segment in the other zone with reversed endpoints
            other = surf_names[(bnd, p2)]
            a(_obj("BuildingSurface:Detailed", name, "Wall", "Partition", z, "", "Surface", other, "NoSun",
                   "NoWind", "autocalculate", 4, *vtxt))
    for z, poly in ZONES.items():
        roof_con = "Roof"
        if z in HABITABLE and case.roof == "top":
            roof_con = "Roof_PCMtop"
        elif z in HABITABLE and case.roof == "bottom":
            roof_con = "Roof_PCMbottom"
        rv = [f"{x:.4f},{y:.4f},{H:.4f}" for x, y in poly]                 # CCW from above
        fv = [f"{x:.4f},{y:.4f},0.0000" for x, y in reversed(poly)]       # CCW from below
        a(_obj("BuildingSurface:Detailed", f"{z}_Roof", "Roof", roof_con, z, "", "Outdoors", "", "SunExposed",
               "WindExposed", "autocalculate", 4, *rv))
        a(_obj("BuildingSurface:Detailed", f"{z}_Floor", "Floor", "GroundFloor", z, "", "Ground", "", "NoSun",
               "NoWind", "autocalculate", 4, *fv))
    for j, (z, p1, kind, centre) in enumerate(OPENINGS):
        base = surf_names[(z, p1)]
        if kind == "W1":
            a(_obj("Window", f"{z}_W1_{j}", "Window", base, "", 1, f"{centre - WIN_W/2:.4f}", WIN_SILL, WIN_W, WIN_H))
        else:
            a(_obj("Door", f"{z}_D1_{j}", "Door", base, 1, f"{centre - DOOR_W/2:.4f}", 0, DOOR_W, DOOR_H))

    # ---- internal gains
    a(_schedules(case))
    people = {"BED": 2, "LIV": 4}
    for z in HABITABLE:
        a(_obj("People", f"{z}_People", z, f"Occ_{z}", "People", people[z], "", "", 0.3, "autocalculate",
               f"Act_{z}", "", "No", "EnclosureAveraged", "", "WorkEff", "ClothingInsulationSchedule", "",
               "Clothing", "AirVel", "Fanger"))
        a(_obj("Lights", f"{z}_Lights", z, "Lights", "Watts/Area", "", 3.0, "", 0, 0.4, 0.2, 1, "General"))
        if case.mode == "FAN":
            a(_obj("ElectricEquipment", f"{z}_CeilingFan", z, f"Fan_{z}", "EquipmentLevel", 60, "", "", 0, 0.0, 0, "CeilingFan"))
    a(_obj("ElectricEquipment", "LIV_FridgeMisc", "LIV", "AlwaysOn", "EquipmentLevel", 60, "", "", 0, 0.3, 0, "Plug"))
    a(_obj("ElectricEquipment", "LIV_TV", "LIV", "TV", "EquipmentLevel", 70, "", "", 0, 0.3, 0, "Plug"))
    a(_obj("GasEquipment", "LIV_Cooking", "LIV", "Cooking", "EquipmentLevel", 1000, "", "", 0.1, 0.3, 0.3, "", "Cooking"))

    # ---- air flows
    for z in ZONES:
        a(_obj("ZoneInfiltration:DesignFlowRate", f"{z}_Infiltration", z, "AlwaysOn", "AirChanges/Hour",
               "", "", "", 1.0, 1, 0, 0, 0))
    win_area = {"BED": 2 * WIN_W * WIN_H, "LIV": 3 * WIN_W * WIN_H}
    eff_angle = {"BED": 180, "LIV": 90}
    for z in HABITABLE:
        a(_obj("ZoneVentilation:WindandStackOpenArea", f"{z}_NatVent", z, f"{0.5 * win_area[z]:.3f}",
               f"Vent_{z}", "autocalculate", eff_angle[z], 0.9, "autocalculate",
               22, "", 100, "", 0, "", -100, "", 100, "", 40))
    a(_obj("ZoneVentilation:WindandStackOpenArea", "TOI_Jali", "TOI", f"{JALI_AREA:.3f}", "AlwaysOn",
           "autocalculate", 0, 0.75, "autocalculate", -100, "", 100, "", -100, "", -100, "", 100, "", 40))

    # ---- air conditioning (ideal loads, cooling only)
    if case.mode == "AC":
        for z in HABITABLE:
            a(_obj("ZoneHVAC:EquipmentConnections", z, f"{z}_Equip", f"{z}_Inlets", "", f"{z}_AirNode", f"{z}_ReturnNode"))
            a(_obj("NodeList", f"{z}_Inlets", f"{z}_SupplyNode"))
            a(_obj("ZoneHVAC:EquipmentList", f"{z}_Equip", "SequentialLoad", "ZoneHVAC:IdealLoadsAirSystem",
                   f"{z}_IdealAC", 1, 1, "", ""))
            a(_obj("ZoneHVAC:IdealLoadsAirSystem", f"{z}_IdealAC", f"ACavail_{z}", f"{z}_SupplyNode", "", "",
                   50, 13, 0.0156, 0.0077, "NoLimit", "", "", "NoLimit", "", "", "", "",
                   "ConstantSensibleHeatRatio", 0.7, "None"))
            a(_obj("ZoneControl:Thermostat", f"{z}_Tstat", z, "TstatType", "ThermostatSetpoint:SingleCooling", f"{z}_CoolSP"))
            a(_obj("ThermostatSetpoint:SingleCooling", f"{z}_CoolSP", "CoolSP"))

    # ---- outputs
    a(_obj("Output:SQLite", "SimpleAndTabular"))
    a(_obj("Output:Table:SummaryReports", "AllSummary"))
    a(_obj("OutputControl:Table:Style", "CommaAndHTML"))
    hourly = [
        ("*", "Site Outdoor Air Drybulb Temperature"),
        ("BED", "Zone Operative Temperature"), ("LIV", "Zone Operative Temperature"),
        ("BED", "Zone Mean Air Temperature"), ("LIV", "Zone Mean Air Temperature"),
        ("BED", "Zone Air Relative Humidity"), ("LIV", "Zone Air Relative Humidity"),
        ("BED_People", "Zone Thermal Comfort Fanger Model PMV"), ("LIV_People", "Zone Thermal Comfort Fanger Model PMV"),
        ("BED", "Zone People Occupant Count"), ("LIV", "Zone People Occupant Count"),
        ("BED_Roof", "Surface Inside Face Temperature"), ("LIV_Roof", "Surface Inside Face Temperature"),
        ("BED_Roof", "Surface Outside Face Temperature"),
        ("BED_Roof", "Surface Inside Face Conduction Heat Transfer Rate per Area"),
        ("LIV_Roof", "Surface Inside Face Conduction Heat Transfer Rate per Area"),
    ]
    if case.mode == "AC":
        for z in HABITABLE:
            hourly.append((f"{z}_IdealAC", "Zone Ideal Loads Zone Total Cooling Energy"))
            hourly.append((f"{z}_IdealAC", "Zone Ideal Loads Zone Sensible Cooling Energy"))
    if case.hourly_pcm_nodes:
        for n in range(1, 41):
            hourly.append(("*", f"CondFD Surface Temperature Node {n}"))
    for key, var in hourly:
        a(_obj("Output:Variable", key, var, "Hourly"))
    a(_obj("Output:VariableDictionary", "IDF"))
    return "\n".join(out)


def pcm_areas(case: Case):
    """Net PCM-covered area [m2] per element (habitable zones only), for costing."""
    areas = {"roof": 0.0, "N": 0.0, "E": 0.0, "S": 0.0, "W": 0.0}
    if case.roof != "none":
        for z in HABITABLE:
            xs = [p[0] for p in ZONES[z]]
            ys = [p[1] for p in ZONES[z]]
            areas["roof"] += (max(xs) - min(xs)) * (max(ys) - min(ys))
    for z, p1, p2, bnd in SEGMENTS:
        if bnd != "ext" or z not in HABITABLE:
            continue
        fac = _seg_facade(p1, p2)
        if fac not in case.walls:
            continue
        L = ((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2) ** 0.5
        A = L * H
        for oz, op1, kind, _ in OPENINGS:
            if oz == z and op1 == p1:
                A -= WIN_W * WIN_H if kind == "W1" else DOOR_W * DOOR_H
        areas[fac] += A
    return areas


FLOOR_AREA = sum((max(p[0] for p in poly) - min(p[0] for p in poly)) *
                 (max(p[1] for p in poly) - min(p[1] for p in poly)) for poly in ZONES.values())
HABITABLE_AREA = sum((max(p[0] for p in ZONES[z]) - min(p[0] for p in ZONES[z])) *
                     (max(p[1] for p in ZONES[z]) - min(p[1] for p in ZONES[z])) for z in HABITABLE)


# ----------------------------------------------------------------------------------------
# CondFD node layout (replicates EnergyPlus' rule: dx = sqrt(C * alpha * dt), n = int(L/dx) >= 1)
# ----------------------------------------------------------------------------------------
LAYER_PROPS = {
    "PlasterOut15": ("CementPlaster", THICK["plaster_out"]), "PlasterIn12": ("CementPlaster", THICK["plaster_in"]),
    "Brick250": ("BurntBrick", THICK["brick_ext"]), "Brick125": ("BurntBrick", THICK["brick_part"]),
    "RCC125": ("RCC_M20", THICK["rcc"]), "Screed25": ("CementScreed", THICK["screed"]),
    "Gypsum12": ("GypsumBoard", THICK["gypsum"]),
}
PCM_CONSTRUCTIONS = {
    "roof_top": ["Screed25", "PCM", "Screed25", "RCC125", "PlasterIn12"],
    "roof_bottom": ["Screed25", "RCC125", "PlasterIn12", "PCM", "Gypsum12"],
    "wall": ["PlasterOut15", "Brick250", "PlasterIn12", "PCM", "Gypsum12"],
}


def pcm_node_range(case: Case, element: str):
    """1-based (first, last) CondFD node indices bounding the PCM layer of a construction."""
    dt = 3600.0 / case.timestep
    node = 1
    for lay in PCM_CONSTRUCTIONS[element]:
        if lay == "PCM":
            p = case.pcm_props()
            k, rho, cp, t = p["ks"], p["rho"], p["cp"], case.thk
        else:
            base, t = LAYER_PROPS[lay]
            _, k, rho, cp, _ = MATERIALS[base]
        dx = (case.space_c * k / (rho * cp) * dt) ** 0.5
        n = max(1, int(t / dx))
        if lay == "PCM":
            return node, node + n
        node += n
    raise ValueError(element)
