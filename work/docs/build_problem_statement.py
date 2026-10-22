"""Build BTP_Problem_Statement.pdf (in the project root).

    .venv/Scripts/python.exe work/docs/build_problem_statement.py
"""
import csv
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "src"))

from reportlab.platypus import Spacer, PageBreak, KeepTogether  # noqa: E402
from pdfkit import P, bullets, numbered, figure, table, callout, make_doc, S, TEXT_W  # noqa: E402
from climate import read_epw, monthly_summary  # noqa: E402
from run import WEATHER  # noqa: E402

ASSETS = HERE / "assets"
OUT = ROOT / "BTP_Problem_Statement.pdf"

# ---- numbers quoted in the text come from the data, not typed by hand -------------------
rows = monthly_summary(read_epw(WEATHER["kolkata"]))
hot_months = [r for r in rows if r["month"] in (4, 5, 6, 7, 8, 9)]
night_mean = sum(r["tnight"] for r in hot_months) / len(hot_months)
above26 = [100 * (1 - r["frac_nights_min_below_26"]) for r in hot_months]
winter_night = sum(r["tnight"] for r in rows if r["month"] in (12, 1, 2)) / 3

base = None
vfile = HERE.parent / "results" / "verification.csv"
if vfile.exists():
    for r in csv.DictReader(open(vfile)):
        if r["label"] == "base_CondFD":
            base = {k: float(v) for k, v in r.items() if k not in ("label", "case_id")}

story = []
A = story.append

A(P("B.TECH PROJECT · PROBLEM STATEMENT", "kicker"))
A(P("Optimising Phase Change Material (PCM) Retrofits on the Roof and Walls of PMAY Houses "
    "for Thermal Comfort and Energy Savings in a Warm-Humid Climate", "title"))
A(P("Indian Institute of Technology Kharagpur · Study location: Kolkata / Kharagpur, West Bengal "
    "(warm-humid climate) · Version 1.0, 22 October 2026", "meta"))

# 1 ----------------------------------------------------------------------------------------
A(P("1. Background and motivation", "h1"))
A(P("Space cooling is the fastest-growing use of energy in Indian buildings. It already accounts for about 38 % "
    "of building-sector energy use and is projected to reach 50 % by 2027 [1]. India experiences roughly 28 % of "
    "the world's population-weighted cooling degree-days, yet fewer than 7 % of homes own a room air conditioner "
    "[2]. As incomes rise this gap will close quickly, with large consequences for peak electricity demand and "
    "emissions. Every passive measure that keeps homes comfortable without air conditioning, or reduces how hard "
    "an air conditioner must work, therefore matters at national scale."))
A(P("Pradhan Mantri Awas Yojana – Urban (PMAY-U) is delivering millions of small, permanent houses to "
    "economically weaker households. The West Bengal model design for <i>Beneficiary-Led Construction</i> (BLC), "
    "shown in Fig. 1, is typical: a 25.8 m² carpet-area unit with 250 mm burnt-brick walls and an exposed, "
    "uninsulated reinforced-cement-concrete (RCC) roof slab [12]. In a warm-humid climate such a roof absorbs "
    "intense solar radiation through the day and keeps radiating that heat into the rooms well into the night. The "
    "occupants, who mostly cannot afford air conditioning, bear the consequences."))
A(P("Phase change materials (PCMs) store a large amount of heat at an almost constant temperature while they melt, "
    "and give it back when they solidify. Placed in the building envelope, a PCM layer can absorb part of the "
    "daytime heat flow, delaying and flattening indoor temperature peaks. In Rupnagar (Punjab), an RCC roof slab "
    "with macro-encapsulated PCM cut the heat flux into the room by 60.6 % and the thermal load by 49.8 %, with a "
    "simple payback of 5.7 years [1]. Independent PCM ceiling panels have even held a lightweight enclosure below "
    "the outdoor temperature [3, 4]. Because a PCM layer can be added to an existing house (on top of the roof "
    "slab, as a ceiling board, or as an inner wall lining) without rebuilding it, PCM is a candidate "
    "<i>retrofit</i> for the large stock of PMAY houses already built."))
A(figure(ASSETS / "pmay_blc_drawing.jpg", 112,
         "Fig. 1. Reference building: PMAY-U model design of a dwelling unit for BLC, Municipal Engineering "
         "Directorate, Government of West Bengal [12]. Floor area 25.77 m², built-up area 32.58 m²."))

# 2 ----------------------------------------------------------------------------------------
A(P("2. Why this is not straightforward", "h1"))
A(P("A PCM only helps if it completes a melt–freeze cycle every day: it must melt while absorbing daytime "
    "heat and then <i>re-solidify at night</i> to be ready for the next day. Fig. 2 shows why this is the central "
    f"difficulty in Kolkata. From April to September the mean night-time temperature is {night_mean:.1f} °C, "
    f"and on {min(above26):.0f}–{max(above26):.0f} % of nights the outdoor minimum stays above 26 °C. "
    "n-Octadecane, the PCM proposed for this project, melts at about 28 °C, so it may stay partly molten for "
    "weeks and stop working exactly when it is needed. The opposite problem appears in winter "
    f"(December–February, mean night temperature {winter_night:.1f} °C), when a 28 °C PCM placed "
    "indoors may hardly melt at all. On the outer face of a sun-baked roof, temperatures far above 50 °C "
    "change the picture again."))
A(P("The best PCM, its melting temperature, thickness and position therefore depend on the climate, the "
    "orientation of each surface and on how the house is operated (windows, ceiling fans, air conditioning). "
    "These choices must also be balanced against cost for a house built on a very small budget. Finally, comfort "
    "has to be judged with the right yardstick. The India Model for Adaptive Comfort – Residential (IMAC-R), "
    "derived from year-long surveys in Indian homes including Kolkata, shows that the PMV model under-predicts how "
    "much warmth Indian occupants accept [2]. IMAC-R is therefore the appropriate measure for naturally "
    "ventilated PMAY houses."))
A(figure(ASSETS / "climate_kolkata.png", 170,
         "Fig. 2. Left: Kolkata monthly mean maximum, night-time (22–06 h) and minimum outdoor temperature "
         "(TMYx 2011–2025 [13]) against the melting range of n-octadecane and the IMAC-R 80 % comfort band. "
         "Right: share of nights on which the outdoor minimum falls below 26 °C, i.e. when a 28 °C PCM "
         "could fully re-solidify by exchanging heat with outdoor air."))

# 3 ----------------------------------------------------------------------------------------
A(P("3. Problem statement", "h1"))
A(callout(
    "To identify, through verified building-energy simulation and multi-objective optimisation, the PCM retrofit "
    "(choice of PCM and its melting temperature, layer thickness, and location on the roof and walls) that gives "
    "the best trade-off between <b>occupant thermal comfort</b> (IMAC-R), <b>cooling energy use</b> (Energy "
    "Performance Index) and <b>investment cost</b> for the West Bengal PMAY-U BLC dwelling in the warm-humid "
    "climate of Kolkata/Kharagpur, under passive (free-running), ceiling-fan-assisted and air-conditioned operation.",
    "Problem statement"))
A(Spacer(1, 6))
A(P("Research gaps addressed", "h2"))
A(P("The gaps below come from the papers reviewed so far; the ongoing literature review will refine them."))
story.extend(bullets([
    "<b>Climate and building type.</b> Experimental PCM-roof work in India has concentrated on hot, dry or composite "
    "climates and on small test units [1]. Whole-house assessments of low-cost dwellings in the warm-humid east of "
    "India are scarce.",
    "<b>Thermal mass.</b> Much recent PCM-panel research targets lightweight, low-mass enclosures [3, 4]. Brick-and-RCC "
    "houses already store heat, so the added benefit of PCM there is less certain.",
    "<b>Night-time discharge.</b> Incomplete re-solidification in climates with warm nights, and how it should drive "
    "melting-temperature selection, is seldom quantified for Indian houses.",
    "<b>Comfort yardstick.</b> PCM benefits are usually reported as temperature reductions, PMV or energy savings. "
    "India's residential adaptive model (IMAC-R) [2] is seldom used to judge them.",
    "<b>Joint optimisation.</b> Placement (roof vs. individual walls), operating mode and cost have not been "
    "optimised together for affordable housing.",
]))

# 4 ----------------------------------------------------------------------------------------
A(P("4. Aim and objectives", "h1"))
A(P("<b>Aim:</b> to recommend a practical, cost-effective PCM retrofit for PMAY houses in warm-humid West Bengal."))
story.extend(numbered([
    "Build and verify an EnergyPlus model of the PMAY BLC house in Kolkata, and establish its baseline comfort and "
    "energy performance.",
    "Model PCM layers on the roof (top of slab or ceiling underside) and on each wall, with n-octadecane as the "
    "baseline PCM and n-alkanes melting between 22 °C and 37 °C as alternatives. Verify the PCM model "
    "(grid and time-step independence, and a control case without latent heat).",
    "Quantify, for passive, fan and air-conditioned operation, the effect of each configuration on IMAC-R "
    "discomfort hours, peak temperatures and cooling energy, separately for summer, monsoon and winter.",
    "Quantify how often the PCM actually completes its melt–freeze cycle, and identify suitable melting "
    "temperatures for the warm-humid climate.",
    "Find Pareto-optimal retrofits for comfort, energy and cost with NSGA-II/NSGA-III, and compute payback and "
    "CO₂ savings.",
    "Translate the results into retrofit guidelines for PMAY houses.",
]))

# 5 ----------------------------------------------------------------------------------------
A(P("5. Scope and study design", "h1"))
A(P("5.1 Reference building and simulation model", "h2"))
spec = [
    ["Item", "Value / assumption"],
    ["Location & climate", "Kolkata (22.65° N, 88.45° E), warm-humid climate zone (NBC 2016 [7]). "
                           "Kharagpur checked with Midnapore weather (WMO 428030, ~10 km away)."],
    ["Weather data", "TMYx 2011–2025 typical-year files from climate.onebuilding.org [13]"],
    ["Geometry", "Bedroom (BED), multi-purpose room + kitchen + passage (LIV), WC + bath (TOI); 2.75 m ceiling; "
                 "31.9 m² modelled floor area (Fig. 3)"],
    ["Walls", "15 mm cement plaster + 250 mm burnt brick + 12 mm plaster (U ≈ 2.0 W/m²K); "
              "125 mm brick partitions"],
    ["Roof", "25 mm cement screed + 125 mm M20 RCC slab + 12 mm plaster (U ≈ 3.4 W/m²K); "
             "slab thickness assumed (not on drawing)"],
    ["Openings", "5 windows W1 (0.9 × 0.9 m, single clear glass), entrance door, 3 jali ventilators to "
                 "the toilet block"],
    ["Occupancy", "Family of four; bedroom used 21–07 h, living room all day; lights 3 W/m², fridge, "
                  "TV, LPG cooking (1 kW, 2.5 h/day)"],
    ["Ventilation", "Windows open 06–22 h when the room is warmer than outdoors and warmer than the day's IMAC-R "
                    "90 % lower comfort limit; night ventilation is a study variable; infiltration 1 ACH"],
    ["Orientation", "Not given on the drawing: plan-up = North as the base case, with rotation as a sensitivity "
                    "check"],
]
A(table(spec, [38, TEXT_W / 2.835 - 38]))
A(Spacer(1, 6))
A(figure(ASSETS / "model_plan.png", 70,
         "Fig. 3. Plan of the simulation model derived from Fig. 1 (centre-line dimensions). PCM retrofits are "
         "applied only to the habitable rooms (BED, LIV)."))

A(P("5.2 Configurations (from the proposed layout of work)", "h2"))
conf = [
    ["Group", "Configuration", "How it is modelled"],
    ["Passive", "PCM on roof", "PCM layer on top of the slab under a new 25 mm screed, <i>or</i> as a ceiling lining "
                               "(PCM + 12.5 mm gypsum board)"],
    ["Passive", "PCM on walls", "Inner-face PCM lining on the North, East, South, West or all walls of the "
                                "habitable rooms (16 combinations)"],
    ["Passive", "Walls + roof", "Any wall combination together with either roof position"],
    ["Mixed", "Ceiling fan", "Every passive configuration with a 60 W ceiling fan per room. The IMAC-R upper limit is "
                             "raised by 1.2 °C for elevated air speed (ASHRAE 55 [6])"],
    ["Mixed", "Air conditioning", "Every passive configuration with a split AC (26 °C set-point, COP 3.3) in the "
                                  "bedroom at night and in the living room in the afternoon and evening "
                                  "(1 Mar–15 Nov)"],
]
A(table(conf, [22, 30, TEXT_W / 2.835 - 52]))
A(Spacer(1, 6))
A(P("5.3 Design variables", "h2"))
dv = [
    ["Variable", "Levels in the parametric study", "In optimisation"],
    ["Roof PCM position", "none / top of slab / ceiling underside", "categorical"],
    ["Wall PCM", "any subset of N, E, S, W (16)", "4 binary"],
    ["PCM (melting point)", "n-heptadecane 22 °C, <b>n-octadecane 28 °C</b> (baseline), n-nonadecane "
                            "32 °C, n-eicosane 36.6 °C [8]", "continuous 20–38 °C"],
    ["Layer thickness", "5, 10, 20 mm", "continuous 3–30 mm"],
    ["Night ventilation", "windows closed / open at night", "binary"],
    ["Orientation", "0° (base); 90°, 180°, 270° as sensitivity", "fixed"],
]
A(table(dv, [36, 92, TEXT_W / 2.835 - 128]))

# 6 ----------------------------------------------------------------------------------------
A(P("6. Methodology", "h1"))
A(figure(ASSETS / "methodology.png", 170, "Fig. 4. Methodology and work-flow."))
story.extend(bullets([
    "<b>Simulation engine:</b> EnergyPlus 26.2 [9] with the Conduction Finite Difference (CondFD) algorithm, which "
    "represents the PCM by its enthalpy–temperature curve and temperature-dependent conductivity. A 3-minute "
    "time step is used, and every case (including the no-PCM baseline) uses the same algorithm so comparisons are "
    "fair.",
    "<b>Model generation and automation:</b> the model is written by a Python script (geometry from the drawing, "
    "constructions, schedules), so thousands of variants can be generated and run in parallel without manual "
    "editing.",
    "<b>Verification:</b> CondFD against the standard conduction-transfer-function solver for the baseline; "
    "sensitivity to the grid and time step; a control case with the same layer but no latent heat, to separate the "
    "PCM effect from the extra layer's resistance and mass; and checks on the PCM melt–freeze state [14]. No "
    "measured data exist yet for this house, so short-term indoor temperature logging in a real PMAY house near "
    "Kharagpur is proposed for validation.",
    "<b>Optimisation:</b> NSGA-II [10] and NSGA-III [11] (pymoo). Optimisation is first run on the discrete "
    "parametric space, where the true Pareto front is known from brute force, to check that the optimiser finds "
    "it. It is then run on an extended continuous space (melting point, thickness).",
]))

A(P("Performance indicators", "h2"))
kpi = [
    ["Indicator", "Definition"],
    ["Discomfort hours", "Occupied hours with indoor operative temperature outside the IMAC-R 80 % band: "
                         "T<sub>n</sub> = 0.42·T<sub>out,30DRM</sub> + 17.6 °C, band ±3.6 °C "
                         "(±2.15 °C for 90 %) [2]"],
    ["Discomfort degree-hours", "Sum of the temperature excess above (or below) the band over occupied hours"],
    ["Peak temperature & swing", "Maximum operative temperature; mean daily indoor swing in summer"],
    ["Cooling EPI", "Annual AC electricity per m² of floor area (kWh/m²·yr)"],
    ["Seasonal performance", "Winter (Dec–Feb), summer (Mar–May), monsoon (Jun–Sep), "
                             "post-monsoon (Oct–Nov)"],
    ["PCM utilisation", "Share of days with a full melt–freeze cycle; mean daily swing of melt fraction"],
    ["Cost, payback, CO₂", "PCM at Rs 450/kg [1] + encapsulation and finish; payback = cost / (annual kWh "
                                "saved × tariff); CO₂ = kWh saved × grid emission factor "
                                "(≈ 0.72 kg/kWh)"],
]
A(table(kpi, [42, TEXT_W / 2.835 - 42]))

# 7 ----------------------------------------------------------------------------------------
if base:
    A(P("7. First result: the un-retrofitted house", "h1"))
    A(P(f"The baseline model (no PCM, free-running, windows open by day) already shows the problem. Indoor operative "
        f"temperature peaks at {base['Top_max']:.1f} °C, the ceiling surface reaches "
        f"{base['BED_ceiling_T_max']:.0f} °C, and about {base['BED_roof_gain_kwh_m2']:.0f} kWh of heat per m² "
        f"of roof enters the bedroom each year. {base['disc80_pct']:.1f} % of occupied hours fall outside the IMAC-R "
        f"80 % band ({base['disc90_pct']:.0f} % outside the stricter 90 % band). Hot discomfort is concentrated in "
        "pre-monsoon afternoons, and cold discomfort in winter nights."))

# 8 ----------------------------------------------------------------------------------------
A(P(("8" if base else "7") + ". Expected outcomes and deliverables", "h1"))
story.extend(bullets([
    "A verified, scriptable EnergyPlus model of the PMAY BLC house, and a ranked comparison of all roof and wall "
    "PCM configurations for passive, fan and AC operation.",
    "Evidence on whether n-octadecane suits Kolkata, and which melting temperature works best for each location "
    "(roof top, ceiling, walls), including summer vs. winter behaviour.",
    "Pareto fronts of comfort vs. energy vs. cost, a recommended retrofit with its payback and CO₂ savings, "
    "and simple design guidelines.",
    "A reproducible code repository (GitHub), the BTP-I and BTP-II reports, and (if results permit) a conference "
    "or journal manuscript.",
]))
A(KeepTogether([P(("9" if base else "8") + ". Work plan", "h1"),
                figure(ASSETS / "gantt.png", 170, "Fig. 5. Work plan for BTP-I (autumn 2026) and BTP-II (spring 2027).")]))
A(P("Key assumptions and limitations", "h2"))
story.extend(bullets([
    "PCM properties are typical literature values for pure n-alkanes [8], and the encapsulation shell is not modelled "
    "explicitly. Both will be checked against supplier data.",
    "Costs, tariff and AC efficiency are indicative and will be varied in a sensitivity analysis.",
    "A single typical-year weather file is used. Future-climate files may be added if time permits.",
    "The model is verified numerically. Validation against measured indoor temperatures is planned but depends on "
    "access to an occupied PMAY house.",
]))

# References ----------------------------------------------------------------------------------
A(P("References", "h1"))
refs = [
    "P.J. Abass, S. Muthulingam, Comprehensive assessment of PCM integrated roof for passive building design: a study "
    "in energo-economics, <i>Energy and Buildings</i> 317 (2024) 114387. doi:10.1016/j.enbuild.2024.114387",
    "R. Rawal, Y. Shukla, V. Vardhan, S. Asrani, M. Schweiker, R. de Dear, et al., Adaptive thermal comfort model "
    "based on field studies in five climate zones across India, <i>Building and Environment</i> 219 (2022) 109187. "
    "doi:10.1016/j.buildenv.2022.109187",
    "S. Yang, Y. Zhang, X. Zhai, J.F. Torres, Y. Lu, Y. Zhao, B. Chalermsinsuwan, X. Wang, Exploring the potential "
    "of independent PCM-based free cooling in climate-dominant building structures, <i>Thermal Science and "
    "Engineering Progress</i> 63 (2025) 103732. doi:10.1016/j.tsep.2025.103732",
    "S. Yang, Y. Zhang, Y. Zhao, J.F. Torres, X. Wang, PCM-based ceiling panels for passive cooling in buildings: a "
    "CFD modelling, <i>Energy and Buildings</i> 285 (2023) 112898. doi:10.1016/j.enbuild.2023.112898",
    "A. Pourshaghaghy, M. Omidvari, Examination of thermal comfort in a hospital using PMV–PPD model, "
    "<i>Applied Ergonomics</i> 43 (2012) 1089–1095. doi:10.1016/j.apergo.2012.03.010",
    "ANSI/ASHRAE Standard 55-2020, Thermal Environmental Conditions for Human Occupancy, ASHRAE, Atlanta, 2020.",
    "Bureau of Indian Standards, National Building Code of India 2016, Part 11: Approach to Sustainability.",
    "A. Sharma, V.V. Tyagi, C.R. Chen, D. Buddhi, Review on thermal energy storage with phase change materials and "
    "applications, <i>Renewable and Sustainable Energy Reviews</i> 13 (2009) 318–345. "
    "doi:10.1016/j.rser.2007.10.005",
    "EnergyPlus Version 26.2 Engineering Reference and Input Output Reference, U.S. Department of Energy, 2026.",
    "K. Deb, A. Pratap, S. Agarwal, T. Meyarivan, A fast and elitist multiobjective genetic algorithm: NSGA-II, "
    "<i>IEEE Transactions on Evolutionary Computation</i> 6 (2002) 182–197. doi:10.1109/4235.996017",
    "K. Deb, H. Jain, An evolutionary many-objective optimization algorithm using reference-point-based "
    "nondominated sorting approach, part I, <i>IEEE Transactions on Evolutionary Computation</i> 18 (2014) "
    "577–601. doi:10.1109/TEVC.2013.2281535",
    "Office of the Chief Engineer, Municipal Engineering Directorate, Govt. of West Bengal, PMAY (Housing for All "
    "– Urban): Model design of dwelling unit for BLC (drawing), Urban Development & Municipal Affairs Dept.",
    "Climate.OneBuilding.Org, TMYx 2011–2025 weather files for Kolkata (WMO 428090) and Midnapore (WMO 428030), "
    "accessed October 2026.",
    "P.C. Tabares-Velasco, C. Christensen, M. Bianchi, Verification and validation of EnergyPlus phase change "
    "material model for opaque wall assemblies, <i>Building and Environment</i> 54 (2012) 186–196. "
    "doi:10.1016/j.buildenv.2012.02.019",
]
for i, r in enumerate(refs, 1):
    A(P(f"[{i}]&nbsp;&nbsp;{r}", "ref"))

doc, on_page = make_doc(OUT, "BTP Problem Statement - PCM retrofits for PMAY houses",
                        "BTP · PCM retrofit of PMAY houses · Problem statement")
doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
print("written", OUT)
