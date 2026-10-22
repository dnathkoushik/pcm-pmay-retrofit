# Literature review: PCM retrofit of the roof and walls of a PMAY house in a warm-humid climate

**Project:** Optimisation of the roof and walls of a Pradhan Mantri Awas Yojana (PMAY) house by retrofitting a phase change material (PCM) layer, for thermal comfort and lower energy use, in Kolkata / Kharagpur (warm-humid, West Bengal).
**Baseline PCM:** n-octadecane (melts at about 28 °C). **Tools:** EnergyPlus (CondFD + `MaterialProperty:PhaseChange`), IMAC-R comfort model, EPI, NSGA-II / NSGA-III in pymoo.
**Prepared:** 22 October 2026.

## How to read this file

- **Verification.** I checked the DOI of every journal or conference source below with the Crossref API (`https://api.crossref.org/works/<DOI>`). Title, authors, year and journal all match. The NIST WebBook DOI is registered with DataCite instead, and resolves correctly. The codes, tariffs and reports have no DOI, so I read them directly at the URL given.
- **Where the numbers come from.** Numbers are taken from the abstract or the full text. Whenever a number came only from a secondary summary (another paper or a repository page), I say so. If I could not check something, it is listed under **Unverified leads** near the end.
- **The five papers you already have** (Abass & Muthulingam 2024; Yang et al. 2023; Yang et al. 2025; Rawal et al. 2022 IMAC-R; Pourshaghaghy & Omidvari 2012) are not summarised again. They are cited where useful and are in `references.bib`.
- **BibTeX keys** are shown in square brackets, e.g. [ArumugamC2024].

---

## A. PCM in roofs and walls in hot-humid, tropical and Indian climates

### A1. Arumugam C. et al. (2024): the paper cited as ref. [49] in Abass & Muthulingam 2024  [ArumugamC2024]
**Citation:** Arumugam, C., Shaik, S., Roy, A., Kontoleon, K.J., Cuce, E., Shaik, A.H., Chakraborty, S., Alwetaishi, M., Cuce, P.M., Gupta, M. (2024). Analysis of the benefits of adopting roof sandwich panels integrated with PCM versus PUR to mitigate energy costs and carbon dioxide emissions. *Journal of Energy Storage*, 77, 109947. DOI: 10.1016/j.est.2023.109947
**Summary:** The authors compared roof sandwich panels made with four sheet materials (acrylic, aluminium, galvanised iron, polycarbonate). Each panel was filled either with polyurethane (PUR) foam or with a form-stable PCM (FS29). They measured the PCM's latent heat themselves. The acrylic panel with PCM did best, giving the largest annual air-conditioning cost savings (7.90 and 8.18 US$/m²/yr), the largest CO₂ reductions (144.15 and 156.44 kg-CO₂/yr) and payback periods of 9 and 8.7 years, for India's composite and warm-humid climates respectively. These figures come from the abstract. The pairing of each number with each climate follows the abstract's order.
**Relevance to this BTP:** This is the exact ref. [49]. It is one of very few studies with Indian warm-humid roof PCM economics, and it is a benchmark for your payback and CO₂ results.

### A2. Reddy, Mudgal & Mallick (2017): multi-layer PCM roofs in Chennai  [Reddy2017]
**Citation:** Reddy, K.S., Mudgal, V., Mallick, T. (2017). Thermal performance analysis of multi-phase change material layer-integrated building roofs for energy efficiency in built-environment. *Energies*, 10(9), 1367. DOI: 10.3390/en10091367 (open access)
**Summary:** This numerical study tested single and double PCM layers in a roof, varying thickness, phase-transition temperature and latent heat, for Chennai (warm-humid). A single PCM layer could not hold a steady indoor temperature *because the PCM did not fully solidify and melt*. Two PCM layers of suitable thickness kept the indoor temperature at about 28 °C through the day. Compared with a roof without PCM, heat gain fell by 17–26% with one layer and by 25–36% with two, depending on the month.
**Relevance to this BTP:** This is the most direct Indian warm-humid evidence that a single-melting-point roof PCM suffers from incomplete solidification. It also points to a possible design variable: a second PCM or a second melting point.

### A3. Bhamare, Rathod & Banerjee (2020): inclined PCM layer in a residential roof  [Bhamare2020]
**Citation:** Bhamare, D.K., Rathod, M.K., Banerjee, J. (2020). Numerical model for evaluating thermal performance of residential building roof integrated with inclined phase change material (PCM) layer. *Journal of Building Engineering*, 28, 101018. DOI: 10.1016/j.jobe.2019.101018
**Summary:** The authors built a 3-D CFD (ANSYS Fluent) model of a residential RCC roof with a PCM layer, including convection in the molten PCM and a combined radiative and convective outdoor boundary. They validated it against published experiments and ran it for Chennai. The PCM roof kept the ceiling temperature in a narrow band and cut peak heat load. Tilting the PCM layer by 2° gave the best time lag, decrement factor, melting and solidification cycle, and daily heat-gain saving.
**Relevance to this BTP:** This is an Indian residential roof PCM study. Its CFD detail (melt convection) is something EnergyPlus CondFD cannot capture, so it is a limitation you should state.

### A4. Arumugam P. & Ramalingam (2024): PCM + insulation + natural ventilation, warm-humid offices  [ArumugamP2024]
**Citation:** Arumugam, P., Ramalingam, V. (2024). Thermal comfort enhancement of office buildings located under warm and humid climate through phase change material and insulation coupled with natural ventilation. *Sustainable Energy Technologies and Assessments*, 63, 103657. DOI: 10.1016/j.seta.2024.103657
**Summary:** Four office models with different PCM and insulation combinations were simulated in DesignBuilder (EnergyPlus engine) for Chennai. The PCM-only roof-and-wall case did *not* give adequate comfort. The cases with insulation kept the mean hourly operative temperature near 26.8 °C and 26.6 °C, even in peak summer. The optimised design used 50 mm insulation plus 30 mm PCM. The authors' discussion (open repository version) notes that extreme summer temperatures stop the PCM from solidifying at night, and that adding insulation helps.
**Relevance to this BTP:** This is a very close match in climate and tool (EnergyPlus-based, warm-humid India, natural ventilation). It warns that a PCM layer alone may not be enough, which supports adding insulation as a design variable.

### A5. Lei, Yang & Yang (2016): PCM envelopes in tropical Singapore  [Lei2016]
**Citation:** Lei, J., Yang, J., Yang, E.-H. (2016). Energy performance of building envelopes integrated with phase change materials for cooling load reduction in tropical Singapore. *Applied Energy*, 162, 207–217. DOI: 10.1016/j.apenergy.2015.10.031
**Summary:** This is an EnergyPlus study of PCM layers in walls and roof for a hot, humid climate with little seasonal change. PCM cut envelope heat gains all year. The optimum phase-change temperature was *the lowest temperature that still allows the full melting–solidification cycle of the whole PCM layer*. PCM on the exterior surface of walls worked better. A wider melting range made the PCM more adaptable but lowered the peak saving. Thicker layers cut more heat gain, while thinner layers were more efficient and more cost-effective. (Summary is from the abstract. I could not access the specific optimum temperatures.)
**Relevance to this BTP:** Its melting-temperature rule is directly usable. It also justifies testing PCM position (outer vs inner) and thickness as optimisation variables.

### A6. Triano-Juárez et al. (2020): PCM roof with and without a reflective coating, warm-humid Mexico  [TrianoJuarez2020]
**Citation:** Triano-Juárez, J., Macias-Melo, E.V., Hernández-Pérez, I., Aguilar-Castro, K.M., Xamán, J. (2020). Thermal behavior of a phase change material in a building roof with and without reflective coating in a warm humid zone. *Journal of Building Engineering*, 32, 101648. DOI: 10.1016/j.jobe.2020.101648
**Summary:** This is a 2-D finite-volume model of a concrete roof with a PCM layer (3 positions, 3 thicknesses, grey vs white surface) for a summer week in warm-humid Mexico. On the grey roof, a 2 cm PCM layer near the interior surface cut the peak interior-surface temperature by 6.4 °C and heat gain by 22.2%. On the white roof, PCM position and thickness made almost no difference. The reflective coating alone cut the peak surface temperature by 14.7–15.4 °C and the cooling load by 58.1–62.7%.
**Relevance to this BTP:** Roof solar absorptance strongly interacts with the roof PCM. A cool roof can make the PCM nearly useless, so either include roof absorptance as a variable or justify keeping it fixed.

---

## B. Incomplete night-time solidification, melting-temperature selection, and night ventilation with PCM

### B1. Arumugam P., Ramalingam & Vellaichamy (2022): review of PCM, insulation and natural/night ventilation  [ArumugamP2022]
**Citation:** Arumugam, P., Ramalingam, V., Vellaichamy, P. (2022). Effective PCM, insulation, natural and/or night ventilation techniques to enhance the thermal performance of buildings located in various climates – A review. *Energy and Buildings*, 258, 111840. DOI: 10.1016/j.enbuild.2022.111840
**Summary:** This review covers how PCM, insulation, natural ventilation and night ventilation (alone and combined) perform in hot-arid, hot-humid, cold-dry and cold-wet regions. It is also ref. [50] in Abass & Muthulingam. I could not read the abstract. A later paper by the same authors (A4) and a secondary summary report the main message: in hot climates night ventilation alone is limited, and combining it with PCM (and insulation) is recommended.
**Relevance to this BTP:** This is the best single review linking PCM with night ventilation by climate. Read it before you fix your ventilation schedules.

### B2. Panchabikesan, Vellaisamy & Ramalingam (2017): passive cooling potential across Indian climates  [Panchabikesan2017]
**Citation:** Panchabikesan, K., Vellaisamy, K., Ramalingam, V. (2017). Passive cooling potential in buildings under various climatic conditions in India. *Renewable and Sustainable Energy Reviews*, 78, 1236–1252. DOI: 10.1016/j.rser.2017.05.030
**Summary:** This review covers evaporative cooling, night radiative cooling and PCM-based free cooling in India, and estimates monthly and yearly passive cooling potential for five cities from weather data. The yearly average potential was highest for hot-dry Jaipur (251 W/m²) and only about half that for warm-humid Chennai (127 W/m²).
**Relevance to this BTP:** It quantifies why night-time "recharging" of a PCM is harder in warm-humid India than in hot-dry India.

### B3. Saffari et al. (2017): simulation-based optimisation of PCM melting temperature  [Saffari2017AE]
**Citation:** Saffari, M., de Gracia, A., Fernández, C., Cabeza, L.F. (2017). Simulation-based optimization of PCM melting temperature to improve the energy performance in buildings. *Applied Energy*, 202, 420–434. DOI: 10.1016/j.apenergy.2017.05.107
**Summary:** The authors coupled EnergyPlus with GenOpt, using a custom enthalpy–temperature (h–T) function, to find the best PCM peak melting temperature for a residential building in many Köppen–Geiger climates. In cooling-dominated climates the best melting temperature was about 26 °C (melting range 24–28 °C). In heating-dominated climates it was about 20 °C. Picking the right melting temperature for each climate gave notable energy savings.
**Relevance to this BTP:** This is the template for treating the melting temperature as a design variable in an EnergyPlus loop. Their roughly 26 °C optimum is close to your n-octadecane baseline (about 28 °C).

### B4. Saxena, Agarwal, Rakshit & Kaushik (2020): PCM suitability for Indian buildings  [Saxena2020JSEE]
**Citation:** Saxena, R., Agarwal, N., Rakshit, D., Kaushik, S.C. (2020). Suitability assessment and experimental characterization of phase change materials for energy conservation in Indian buildings. *Journal of Solar Energy Engineering*, 142(1), 011014. DOI: 10.1115/1.4044568
**Summary:** The authors simulated inner-surface temperatures of PCM-sandwiched walls with five PCMs for composite-climate Delhi. A phase-change range of 34–38 °C suited Delhi's peak summer. Eicosane and OM35 were confirmed suitable by DSC tests. Other PCMs were simulated for other Indian climates. They also note that low-conductivity PCMs act as both storage and insulation.
**Relevance to this BTP:** Indian evidence that the best melting temperature depends strongly on climate, and that hot-dry or composite optima (34–38 °C) are much higher than a warm-humid 28 °C PCM. This supports testing n-eicosane / n-nonadecane as alternatives.

### B5. Arıcı et al. (2020): maximising activation of latent heat in walls  [Arici2020]
**Citation:** Arıcı, M., Bilgin, F., Nižetić, S., Karabay, H. (2020). PCM integrated to external building walls: An optimization study on maximum activation of latent heat. *Applied Thermal Engineering*, 165, 114560. DOI: 10.1016/j.applthermaleng.2019.114560
**Summary:** The authors compared a wall with a real PCM against the same wall with a "phase-stabilised" material (same properties but no latent heat). This isolates how much the latent heat really helps. They optimised PCM location, melting temperature and thickness for three Turkish cities. The monthly optimum melting temperature ranged from 6 to 34 °C and the thickness from 1 to 20 mm. Without optimisation, the PCM can behave like an ordinary sensible material.
**Relevance to this BTP:** The "PCM vs same material without latent heat" comparison is an easy and convincing EnergyPlus check. Use it to show that your savings come from the phase change, not from the extra mass.

### B6. Evola, Marletta & Sicurella (2013): indicators for PCM effectiveness  [Evola2013]
**Citation:** Evola, G., Marletta, L., Sicurella, F. (2013). A methodology for investigating the effectiveness of PCM wallboards for summer thermal comfort in buildings. *Building and Environment*, 59, 517–527. DOI: 10.1016/j.buildenv.2012.09.021
**Summary:** The paper proposes indicators that describe how the PCM itself behaves (frequency of melting, storage efficiency), alongside the intensity and duration of occupant comfort. It applies them to PCM wallboards on partitions of a lightweight office. The approach helps choose the PCM and where to install it for a given climate.
**Relevance to this BTP:** Ready-made metrics for reporting "how often the PCM fully melts / fully solidifies". These are useful outputs alongside IMAC-R comfort hours.

### B7. Prabhakar et al. (2020): PCM + controlled natural (night) ventilation  [Prabhakar2020]
**Citation:** Prabhakar, M., Saffari, M., de Gracia, A., Cabeza, L.F. (2020). Improving the energy efficiency of passive PCM system using controlled natural ventilation. *Energy and Buildings*, 228, 110483. DOI: 10.1016/j.enbuild.2020.110483
**Summary:** This EnergyPlus-based optimisation of PCM melting temperature in an office covered 15 cities, combined with window-based night ventilation strategies. The PCM must be fully charged each cycle to be useful. Night ventilation improved PCM effectiveness in temperate climates from 3.32% to 25.62%, and temperature-controlled ventilation raised it to 40%. In hot-arid climates the PCM alone was ineffective.
**Relevance to this BTP:** Directly supports modelling your free-running / natural-ventilation mode with temperature-controlled night opening, rather than a fixed schedule.

### B8. Ramakrishnan et al. (2017): PCM to reduce heat stress in heatwaves  [Ramakrishnan2017]
**Citation:** Ramakrishnan, S., Wang, X., Sanjayan, J., Wilson, J. (2017). Thermal performance of buildings integrated with phase change materials to reduce heat stress risks during extreme heatwave events. *Applied Energy*, 194, 410–421. DOI: 10.1016/j.apenergy.2016.04.084
**Summary:** The authors simulated a single-storey house in Melbourne without air conditioning, with PCM mats in walls and ceiling, during the 2009 heatwave, using a discomfort index. PCM with a suitable ventilation design shortened the severe-discomfort period by 65%. Night ventilation was needed to recharge the PCM. The melting temperature and amount of PCM were critical.
**Relevance to this BTP:** A good analogue for your "free-running" PMAY case, where the main benefit is fewer overheating hours rather than kWh saved.

### Melting-temperature rules found in the literature

| Rule | Source |
|---|---|
| The melting temperature must lie between the daily maximum and minimum temperature the PCM sees, or it will not cycle every day | Abass & Muthulingam 2024 (Sec. 2) |
| Optimum = the lowest melting temperature that still allows full melting *and* full solidification of the whole layer | Lei et al. 2016 |
| Cooling-dominated climates: peak about 26 °C (range 24–28 °C) for a residential building | Saffari et al. 2017 |
| Composite Delhi, peak summer: 34–38 °C | Saxena et al. 2020 (JSEE) |
| A single roof PCM in Chennai does not fully solidify; two layers or two melting points work better | Reddy et al. 2017 |
| Night ventilation (preferably temperature-controlled) is needed to recharge the PCM | Prabhakar et al. 2020; Ramakrishnan et al. 2017 |
| The optimum shifts month to month (6–34 °C in Turkey); unoptimised PCM acts like plain mass | Arıcı et al. 2020 |

**Your own weather files (my analysis, not a published result).** I counted the days on which the outdoor dry-bulb temperature never dropped below a given value:
- Kolkata TMYx 2011–2025 file: 119 of 365 days stayed at or above 27 °C all night, and 166 days stayed at or above 26 °C. Almost all of these days fall between April and September.
- Kolkata ISHRAE 2014 file: 62 and 121 days.
- Midnapore (near Kharagpur) TMYx: 90 and 150 days.

On these nights, outdoor air alone cannot cool a 28 °C n-octadecane layer below its freezing range. This supports the incomplete-discharge concern. It also shows that the result will depend on which weather file you use.

---

## C. EnergyPlus PCM modelling: verification, settings, hysteresis

### C1. Tabares-Velasco, Christensen & Bianchi (2012): verification and validation of the EnergyPlus PCM model  [TabaresVelasco2012]
**Citation:** Tabares-Velasco, P.C., Christensen, C., Bianchi, M. (2012). Verification and validation of EnergyPlus phase change material model for opaque wall assemblies. *Building and Environment*, 54, 186–196. DOI: 10.1016/j.buildenv.2012.02.019
**Companion report (read in full):** Tabares-Velasco, P.C., Christensen, C., Bianchi, M., Booten, C. (2012). *Verification and Validation of EnergyPlus Conduction Finite Difference and Phase Change Material Models for Opaque Wall Assemblies*. NREL Technical Report NREL/TP-5500-55792, Golden, CO. DOI: 10.2172/1050120  [TabaresVelasco2012NREL]
**Summary:** NREL tested the CondFD and PCM algorithms in three steps, following ASHRAE Standard 140: analytical checks, comparison with other software, and comparison with measurements, at wall level and whole-house level. They found and fixed more than 10 bugs, and the validated model went into EnergyPlus 7.1. The report's guidelines:
- (i) use **time steps of 3 min or less**;
- (ii) PCMs with **strong hysteresis** can cause accuracy problems, because the model uses a single enthalpy curve;
- (iii) the **default node spacing** is fine for monthly and annual results, but for sub-hourly results use about **one-third of the default spacing**, which equals a Space Discretization Constant of about 0.3–0.5.

Preliminary whole-house runs suggested annual savings of up to 20% (Phoenix).
**Relevance to this BTP:** This is the paper to cite for using CondFD + `MaterialProperty:PhaseChange`, and for your time-step and node-spacing choices.

### C2. Goia, Chaudhary & Fantucci (2018): modelling hysteresis in EnergyPlus  [Goia2018]
**Citation:** Goia, F., Chaudhary, G., Fantucci, S. (2018). Modelling and experimental validation of an algorithm for simulation of hysteresis effects in phase change materials for building components. *Energy and Buildings*, 174, 54–67. DOI: 10.1016/j.enbuild.2018.06.001
**Summary:** The authors built a hysteresis algorithm in EnergyPlus through the Energy Management System, using separate heating and cooling enthalpy curves, and compared it with experiments on a PCM layer for opaque walls. It agreed with the measurements better than single-curve methods. However, *all* tested models struggled when the PCM did not completely melt or re-solidify (partial cycles).
**Relevance to this BTP:** Partial cycles are exactly the warm-humid case. You should state this as a modelling limitation and/or run a hysteresis sensitivity case.

### C3. Al-Janabi & Kavgic (2019): sensitivity analysis of the EnergyPlus hysteresis object  [AlJanabiKavgic2019]
**Citation:** Al-Janabi, A., Kavgic, M. (2019). Application and sensitivity analysis of the phase change material hysteresis method in EnergyPlus: A case study. *Applied Thermal Engineering*, 162, 114222. DOI: 10.1016/j.applthermaleng.2019.114222
**Summary:** The authors compared the newer `MaterialProperty:PhaseChangeHysteresis` object (EnergyPlus 8.9) with the older enthalpy–temperature method on a university building. The two methods gave different results, and the difference grew with the intensity and duration of solar gain. The most influential hysteresis inputs were the peak melting and freezing temperatures, latent heat, solid density and thickness. PCM in a suspended ceiling saved 1.9–11.4% heating and 5.5–37.4% cooling energy, and cut discomfort hours by 10–29%.
**Relevance to this BTP:** It tells you which inputs to vary if you run the hysteresis object as a check on your `MaterialProperty:PhaseChange` baseline.

### C4. Saffari et al. (2017): review of whole-building simulation of PCM passive cooling  [Saffari2017RSER]
**Citation:** Saffari, M., de Gracia, A., Ushak, S., Cabeza, L.F. (2017). Passive cooling of buildings with phase change materials using whole-building energy simulation tools: A review. *Renewable and Sustainable Energy Reviews*, 80, 1239–1255. DOI: 10.1016/j.rser.2017.05.139
**Summary:** This review covers how EnergyPlus, TRNSYS and similar tools are used to simulate PCM passive cooling in different envelope parts and climates. PCM has "not always been as energy beneficial as expected"; results depend on climate, melting temperature and occupant behaviour. The authors frame PCM design as a single- or multi-objective optimisation problem, and call for more work on night ventilation with PCM.
**Relevance to this BTP:** It justifies the "simulation + multi-objective optimisation" structure of your project in one citation.

### C5. EnergyPlus documentation (Input Output Reference, v24.1 checked)  [EnergyPlusIORef]
**What it says:**
- CondFD needs **at least 20 time steps per hour**.
- `HeatBalanceSettings:ConductionFiniteDifference` defaults: fully implicit first-order scheme, Space Discretization Constant 3 (lower values give more nodes), relaxation factor 1.0, inside-face convergence criterion 0.002 °C.
- `MaterialProperty:PhaseChange` takes a temperature coefficient for conductivity plus up to 16 temperature–enthalpy pairs. This is a single curve, so no hysteresis.
- `MaterialProperty:PhaseChangeHysteresis` takes separate melting and freezing curves (peak temperatures, curve widths) and separate solid and liquid conductivity, density and specific heat.

**Relevance to this BTP:** These are the settings you will actually type into your IDF. Your EnergyPlus 26.2 documentation should be checked for any changes.

---

## D. Thermophysical properties of paraffins (C16–C20)

### D1. Faden et al. (2019): review of octadecane property data  [Faden2019]
**Citation:** Faden, M., Höhlein, S., Wanner, J., König-Haagen, A., Brüggemann, D. (2019). Review of thermophysical property data of octadecane for phase-change studies. *Materials*, 12(18), 2974. DOI: 10.3390/ma12182974 (open access)
**Summary:** The authors reviewed more than 80 references that measured n-octadecane properties, and fitted temperature-dependent functions with confidence intervals, valid ±40 K around melting. Recommended values:
- mean melting point 301.13 K (28.0 °C);
- latent heat 236.98 kJ/kg;
- solid density 867.9 kg/m³; liquid density ρ = 979.826 − 0.674·T;
- solid conductivity 0.334 W/m·K; liquid conductivity k = 0.246 − 3.121×10⁻⁴·T;
- solid and liquid specific-heat polynomials.

(T is in K.) Solid-phase data scatter much more than liquid-phase data.
**Relevance to this BTP:** This is the best single source for your baseline PCM inputs. Use it for the n-octadecane row of the property table.

### D2. Vélez, Khayet & Ortiz de Zárate (2015): even n-alkanes C16, C18, C20  [Velez2015AE]
**Citation:** Vélez, C., Khayet, M., Ortiz de Zárate, J.M. (2015). Temperature-dependent thermal properties of solid/liquid phase change even-numbered n-alkanes: n-Hexadecane, n-octadecane and n-eicosane. *Applied Energy*, 143, 383–394. DOI: 10.1016/j.apenergy.2015.01.054
**Summary:** They measured conductivity and diffusivity by the transient hot-wire method (258–348 K), and melting and freezing points, latent heat and specific heat by DSC. They also measured liquid density.
- DSC melting onset and latent heat: C16 290.90 K / 235.13 kJ/kg; C18 300.22 K / 243.68 kJ/kg; C20 308.84 K / 247.05 kJ/kg.
- Conductivity drops sharply on melting: the solid-minus-liquid difference is 0.172, 0.182 and 0.263 W/m·K for C16, C18 and C20.
- Liquid density fits: C16 ρ = −0.661T + 966.72; C18 ρ = −0.650T + 971.52; C20 ρ = −0.549T + 945.72 (kg/m³, T in K).

**Relevance to this BTP:** Measured values for three of your five candidate PCMs, all from one consistent method.

### D3. Vélez, Ortiz de Zárate & Khayet (2015): odd n-alkanes C15, C17, C19  [Velez2015IJTS]
**Citation:** Vélez, C., Ortiz de Zárate, J.M., Khayet, M. (2015). Thermal properties of n-pentadecane, n-heptadecane and n-nonadecane in the solid/liquid phase change region. *International Journal of Thermal Sciences*, 94, 139–146. DOI: 10.1016/j.ijthermalsci.2015.03.001
**Summary:** Odd-numbered alkanes show *two* DSC peaks: a solid–solid ("rotator") transition a few kelvin below melting, then melting.
- n-heptadecane: 281.96 K (9.64 kJ/mol), then 294.47 K (39.68 kJ/mol).
- n-nonadecane: 294.97 K (11.20 kJ/mol), then 304.37 K (44.61 kJ/mol).
- Measured conductivity: about 0.20 W/m·K (C17) and 0.21–0.23 W/m·K (C19) in the ordered solid, and 0.143–0.152 W/m·K in the liquid.

**Relevance to this BTP:** The split latent heat in C17 and C19 means their enthalpy curve in EnergyPlus must include the solid–solid step. Otherwise you will over-predict the useful latent heat near the melting point.

### D4. NIST Chemistry WebBook (data source)  [NISTWebBook]
**Citation:** Linstrom, P.J., Mallard, W.G. (eds.). *NIST Chemistry WebBook, NIST Standard Reference Database 69*. National Institute of Standards and Technology. DOI: 10.18434/T4D303 (DataCite). Phase-change pages for the five alkanes, accessed 22 Oct 2026.
**Summary:** NIST gives averaged fusion temperatures, with ± uncertainty, and individual enthalpy-of-fusion measurements with their original references:
- C16: Tfus = 291 ± 1 K, ΔfusH = 51.46 kJ/mol;
- C17: 295.1 ± 0.9 K, 40.17 kJ/mol, plus a solid transition of 10.94 kJ/mol at 284.3 K;
- C18: 301.0 ± 0.7 K, 61.5 kJ/mol;
- C19: 304 ± 3 K, 45.8–47.4 kJ/mol, plus 13.75 kJ/mol at about 296 K;
- C20: 310 ± 1 K, 67.8–69.8 kJ/mol.

The ΔfusH values are those listed from the Domalski & Hearing 1996 compilation, or the range of listed values.
**Relevance to this BTP:** An independent, authoritative check on the melting point and latent heat used for each candidate PCM.

### D5. Sharma et al. (2009): review of thermal energy storage with PCMs  [Sharma2009]
**Citation:** Sharma, A., Tyagi, V.V., Chen, C.R., Buddhi, D. (2009). Review on thermal energy storage with phase change materials and applications. *Renewable and Sustainable Energy Reviews*, 13(2), 318–345. DOI: 10.1016/j.rser.2007.10.005
**Summary:** This widely cited review covers latent-heat storage systems: PCM classes (organic, inorganic, eutectic), property tables, and applications in buildings, solar systems and other fields. It stresses PCMs' high storage density at nearly constant temperature.
**Relevance to this BTP:** It is the standard background citation for PCM classes and for why paraffins are chosen. Note that I could not access its property tables, so the values in the property table below are *not* taken from it.

### D6. Zalba et al. (2003): review of PCM materials, heat transfer and applications  [Zalba2003]
**Citation:** Zalba, B., Marín, J.M., Cabeza, L.F., Mehling, H. (2003). Review on thermal energy storage with phase change: materials, heat transfer analysis and applications. *Applied Thermal Engineering*, 23(3), 251–283. DOI: 10.1016/S1359-4311(02)00192-8
**Summary:** This classic review lists more than 150 materials used as PCMs in research and about 45 commercial PCMs, with their thermophysical properties. It also reviews heat-transfer modelling and applications.
**Relevance to this BTP:** The classic source for PCM property lists. Use it as background, and cite D1–D4 for the actual numbers.

### D7. Cabeza et al. (2011): materials used as PCM in buildings  [Cabeza2011]
**Citation:** Cabeza, L.F., Castell, A., Barreneche, C., de Gracia, A., Fernández, A.I. (2011). Materials used as PCM in thermal energy storage in buildings: A review. *Renewable and Sustainable Energy Reviews*, 15(3), 1675–1695. DOI: 10.1016/j.rser.2010.11.018
**Summary:** This review collects the requirements for PCMs in buildings (thermal, physical, kinetic, chemical, economic), how PCMs are classified, what materials are available, and common problems with solutions (leakage, supercooling, phase segregation, fire, encapsulation).
**Relevance to this BTP:** Use it for the practical side of a retrofit layer: encapsulation, fire safety, and the long-term stability of paraffin.

---

## E. Thermal comfort and overheating in Indian affordable housing; ceiling fans

### E1. Manu et al. (2016): India Model for Adaptive Comfort (IMAC)  [Manu2016]
**Citation:** Manu, S., Shukla, Y., Rawal, R., Thomas, L.E., de Dear, R. (2016). Field studies of thermal comfort across multiple climate zones for the subcontinent: India Model for Adaptive Comfort (IMAC). *Building and Environment*, 98, 55–70. DOI: 10.1016/j.buildenv.2015.12.019
**Summary:** The authors collected 6330 survey responses in 16 office buildings across 5 cities and 3 seasons. Occupants of naturally ventilated Indian offices were more adaptive than the ASHRAE and EN models predict. Neutral temperature in naturally ventilated buildings ranged from 19.6 to 28.5 °C for 30-day running-mean outdoor temperatures of 12.5–31 °C. PMV over-predicted warm sensation in air-conditioned buildings.
**Relevance to this BTP:** IMAC is the office predecessor of IMAC-R (Rawal et al. 2022, which you use). Cite it to explain why an Indian adaptive model is used instead of PMV.

### E2. Indraganti (2010): naturally ventilated apartments in Hyderabad  [Indraganti2010]
**Citation:** Indraganti, M. (2010). Thermal comfort in naturally ventilated apartments in summer: Findings from a field study in Hyderabad, India. *Applied Energy*, 87(3), 866–883. DOI: 10.1016/j.apenergy.2009.08.042
**Summary:** This field study ran for 3 months in summer and monsoon 2008, with more than 100 residents and 3962 data sets. The comfort band (votes between −1 and +1) was 26–32.45 °C, with a neutral temperature of 29.23 °C. This is well above the 23–26 °C in Indian standards at that time. PMV always over-predicted the actual sensation. Residents' use of fans and windows gave enough air movement for sweat evaporation most of the time.
**Relevance to this BTP:** A residential (not office) Indian dataset showing that comfort limits in free-running homes are much higher than PMV suggests. It supports the IMAC-R + fan approach.

### E3. Asrani et al. (2022): PMAY-Urban housing vs the residential energy code  [Asrani2022]
**Citation:** Asrani, S., Rawal, R., Shukla, Y., Graham, P., Bhanushali, P., Desai, A. (2022). Thermally comfortable affordable housing: A study on residential building code in India. *The Journal of Engineering Research [TJER]*, 18(2), 124–136. DOI: 10.53540/tjer.vol18iss2pp124-136. (The issue is dated Feb 2022; Crossref shows a 2025 online date.)
**Summary:** The authors collated the spatial design and wall assemblies of 80 PMAY-Urban EWS projects and analysed 30 in detail against Eco-Niwas Samhita. Walls with lower U-values met the RETV limit. Changing wall assemblies gave 4145–6034 thermally comfortable hours per year and an EPI of 64–68 kWh/m²/yr for the dwelling units.
**Relevance to this BTP:** The only peer-reviewed PMAY-specific simulation study found. It gives benchmark EPI and comfort-hour ranges to compare your base case against.

### E4. Malik et al. (2020): adaptive behaviour in Mumbai low-income housing  [Malik2020]
**Citation:** Malik, J., Bardhan, R., Hong, T., Piette, M.A. (2020). Contextualising adaptive comfort behaviour within low-income housing of Mumbai, India. *Building and Environment*, 177, 106877. DOI: 10.1016/j.buildenv.2020.106877
**Summary:** This longitudinal field study collected 705 responses in two low-income neighbourhoods. A logistic model predicts an 88% probability of ceiling-fan use (and 20% for exhaust fans) at 80% indoor relative humidity. Security, privacy, dust, noise, odour and pests often stopped residents from opening windows.
**Relevance to this BTP:** It supports your "ceiling fan" operating mode. It also warns that night ventilation in EWS housing may be limited in practice, so test a reduced-opening scenario.

### E5. Nutkiewicz, Jain & Bardhan (2018): slum-redevelopment design in Dharavi  [Nutkiewicz2018]
**Citation:** Nutkiewicz, A., Jain, R.K., Bardhan, R. (2018). Energy modeling of urban informal settlement redevelopment: Exploring design parameters for optimal thermal comfort in Dharavi, Mumbai, India. *Applied Energy*, 231, 433–445. DOI: 10.1016/j.apenergy.2018.09.002
**Summary:** The authors simulated 18,900 design scenarios for horizontal and vertical (rehabilitation) building forms, using days within Indian comfort limits as the metric. Copying existing materials in vertical form worsened comfort. There were large differences between ground-floor and top-floor units. Window-to-wall ratio was the most sensitive parameter, and the ventilation rate mattered as much as other design parameters.
**Relevance to this BTP:** Top-floor units (under the roof) are the worst off in Indian low-income housing. This directly motivates a roof PCM retrofit, and it treats comfort as the main outcome.

### E6. Vakil et al. (2025): insulation can hurt naturally ventilated homes  [Vakil2025]
**Citation:** Vakil, G., Vaidya, P., Hollannavar, P.S., Jain, Y., Gupta, A. (2025). Rolling back insulation in naturally ventilated buildings: A case to re-evaluate the residential energy code and its implementation practices in India. In *Proceedings of Building Simulation 2025: 19th Conference of IBPSA*, Vol. 19. DOI: 10.26868/25222708.2025.1619
**Summary:** DesignBuilder simulations of a naturally ventilated residence in a hot-dry climate, compared with measured data, found that insulated walls *increased* discomfort hours by 4% compared with uninsulated walls. High-thermal-mass envelopes improved comfort hours by 3% and 8%. The authors argue that meeting the ENS RETV limit by adding insulation can be counter-productive in free-running homes.
**Relevance to this BTP:** A strong argument for PCM (added thermal mass) instead of insulation in free-running PMAY houses. It also tells you to report free-running comfort, not only RETV and U-value compliance.

### E7. Lipczynska, Schiavon & Graham (2018): ceiling fans in a tropical office  [Lipczynska2018]
**Citation:** Lipczynska, A., Schiavon, S., Graham, L.T. (2018). Thermal comfort and self-reported productivity in an office with ceiling fans in the tropics. *Building and Environment*, 135, 202–212. DOI: 10.1016/j.buildenv.2018.03.013
**Summary:** In a Singapore field study, occupants with ceiling fans felt most comfortable at 26 °C. Raising the set-point from 23 to 26 °C increased thermal acceptability from 59% to 91% and saved 44 kWh/m²/yr of cooling electricity. Up to 27 °C had no negative effect when fans were provided. Self-reported productivity did not fall.
**Relevance to this BTP:** Evidence for an "AC + fan at a raised set-point" mode, and for crediting fans with a comfort benefit in a humid climate.

### E8. ASHRAE 55-2020 elevated-air-speed adjustment, via pythermalcomfort  [ASHRAE55_2020; TartariniSchiavon2020]
**Citation:** ASHRAE (2020). *ANSI/ASHRAE Standard 55-2020: Thermal Environmental Conditions for Human Occupancy.* Atlanta: ASHRAE. And: Tartarini, F., Schiavon, S. (2020). pythermalcomfort: A Python package for thermal comfort research. *SoftwareX*, 12, 100578. DOI: 10.1016/j.softx.2020.100578
**Summary:** pythermalcomfort implements the comfort standards and is validated against the standards' reference tables. Its ASHRAE 55-2020 adaptive model (checked in the source code) uses:
- comfort temperature = 0.31·T_rm + 17.8 °C;
- 80% acceptability band ±3.5 K and 90% band ±2.5 K;
- valid for a running-mean outdoor temperature of 10–33.5 °C;
- an elevated-air-speed "cooling effect" added to the *upper* limit only: +1.2 K at ≥0.6 m/s, +1.8 K at ≥0.9 m/s, +2.2 K at ≥1.2 m/s, applied only when the operative temperature is ≥25 °C.

**Relevance to this BTP:** IMAC-R has its own equations, but this is the standard, citable way to credit a ceiling fan in an adaptive comfort calculation. Since you use Python, you can call the package directly.

---

## F. Multi-objective optimisation of envelopes and PCM

### F1. Deb et al. (2002): NSGA-II  [Deb2002]
**Citation:** Deb, K., Pratap, A., Agarwal, S., Meyarivan, T. (2002). A fast and elitist multiobjective genetic algorithm: NSGA-II. *IEEE Transactions on Evolutionary Computation*, 6(2), 182–197. DOI: 10.1109/4235.996017
**Summary:** NSGA-II introduced fast non-dominated sorting (complexity O(MN²) instead of O(MN³)), a crowding-distance measure that needs no sharing parameter to keep solutions spread out, and elitism. It found better-spread, better-converged Pareto fronts than earlier algorithms on standard test problems.
**Relevance to this BTP:** The algorithm for your 2–3-objective runs (e.g. discomfort hours vs EPI vs cost).

### F2. Deb & Jain (2014): NSGA-III  [DebJain2014]
**Citation:** Deb, K., Jain, H. (2014). An evolutionary many-objective optimization algorithm using reference-point-based nondominated sorting approach, Part I: Solving problems with box constraints. *IEEE Transactions on Evolutionary Computation*, 18(4), 577–601. DOI: 10.1109/TEVC.2013.2281535
**Summary:** NSGA-III replaces crowding distance with a set of well-spread reference points. This keeps the population diverse when there are many objectives (tested with 3 to 15), where NSGA-II's crowding distance stops working well.
**Relevance to this BTP:** Use it when you optimise 4 or more objectives at once (e.g. free-running discomfort, fan-mode discomfort, AC EPI, cost, CO₂).

### F3. Blank & Deb (2020): pymoo  [BlankDeb2020]
**Citation:** Blank, J., Deb, K. (2020). Pymoo: Multi-objective optimization in Python. *IEEE Access*, 8, 89497–89509. DOI: 10.1109/ACCESS.2020.2990567
**Summary:** pymoo is an open-source Python framework with NSGA-II, NSGA-III and other algorithms, plus operators for mixed variables, constraint handling, performance indicators (e.g. hypervolume), visualisation and multi-criteria decision-making tools.
**Relevance to this BTP:** The library you will cite for your optimisation code.

### F4. Bre & Fachinotti (2017): NSGA-II + EnergyPlus for dwellings  [BreFachinotti2017]
**Citation:** Bre, F., Fachinotti, V.D. (2017). A computational multi-objective optimization method to improve energy efficiency and thermal comfort in dwellings. *Energy and Buildings*, 154, 283–294. DOI: 10.1016/j.enbuild.2017.08.002
**Summary:** The authors coupled a Python NSGA-II to EnergyPlus on a computing cluster, with discrete and categorical variables (wall and roof types, orientation, solar absorptance, windows, shading). The case was a house in Argentina with some rooms naturally ventilated and some with natural ventilation plus AC. Results versus the original design: up to 95% better comfort in naturally ventilated rooms and up to 82% better energy performance in air-conditioned rooms. Run time fell from about 12 days to 4.4 hours.
**Relevance to this BTP:** It has the same structure as your problem (free-running comfort and AC energy in one dwelling, EnergyPlus + Python NSGA-II). Use it as a methods template.

### F5. Bre, Caggiano & Koenders (2022): optimising PCM panels with EnergyPlus  [Bre2022]
**Citation:** Bre, F., Caggiano, A., Koenders, E.A.B. (2022). Multiobjective optimization of cement-based panels enhanced with microencapsulated phase change materials for building energy applications. *Energies*, 15(14), 5192. DOI: 10.3390/en15145192 (open access)
**Summary:** The authors built a parametric EnergyPlus model and coupled a multi-objective genetic algorithm to it. The design variables were PCM melting temperature, panel thickness and conductivity; the objectives were annual heating and cooling loads. For Sofia, a thin panel melting at 27 °C was best for cooling, and a thick one at 22 °C was best for heating. Raising panel conductivity increased the cooling-load reduction to 12.4%.
**Relevance to this BTP:** A direct example of optimising melting temperature, thickness and conductivity of a PCM layer with EnergyPlus and a genetic algorithm.

### F6. Saurbayeva, Memon & Kim (2023): sensitivity analysis + multi-objective optimisation of PCM residential buildings  [Saurbayeva2023]
**Citation:** Saurbayeva, A., Memon, S.A., Kim, J. (2023). Integrated multi-stage sensitivity analysis and multi-objective optimization approach for PCM integrated residential buildings in different climate zones. *Energy*, 278, 127973. DOI: 10.1016/j.energy.2023.127973
**Summary:** The authors ranked early-design parameters with three global methods (SRRC, PRCC, Morris) and one local method, then ran a genetic-algorithm Pareto optimisation of energy and cost, followed by multi-criteria decision-making, for arid-climate zones. Parameter rankings differed between methods and between climates. The best solutions cut total energy use by 11.1–34.6% compared with the reference. The abstract also gives payback-related figures of 17.6–48.5 years; check the paper for exactly what these mean. The related thesis lists roof and wall solar absorptance, window U-value, orientation and PCM melting temperature as the most important parameters.
**Relevance to this BTP:** A good model for "screen the variables first, then optimise". This keeps your EnergyPlus run count manageable.

### F7. Kishore et al. (2020): optimising PCM walls in U.S. climates  [Kishore2020]
**Citation:** Kishore, R.A., Bianchi, M.V.A., Booten, C., Vidal, J., Jackson, R. (2020). Optimizing PCM-integrated walls for potential energy savings in U.S. Buildings. *Energy and Buildings*, 226, 110355. DOI: 10.1016/j.enbuild.2020.110355
**Summary:** This NREL numerical study found the best transition temperature and wall location for PCM in five U.S. climate zones. Using PCM "does not always lead to an improvement", and incorrect use can increase energy use. Optimised PCM cut annual wall heat gain by 3.5–47.2%, but changed heat loss by only −2.8% to +8.3%.
**Relevance to this BTP:** It supports optimising PCM location and melting temperature per orientation, and reporting cases where PCM makes things worse.

### F8. Roth et al. (2018): scripting frameworks for EnergyPlus (including eppy)  [Roth2018]
**Citation:** Roth, A., Bull, J., Criswell, S., Ellis, P., Glazer, J., Goldwasser, D., Kruis, N., Parker, A., Philip, S., Reddy, D. (2018). Scripting frameworks for enhancing EnergyPlus modeling productivity. In *Proceedings of SimBuild 2018*, Vol. 8. DOI: 10.26868/25746308.2018.c043
**Summary:** The paper describes four EnergyPlus scripting frameworks: eppy (EnergyPlus IDF objects as Python objects), Modelkit, OpenStudio Measures and CBECC. It explains their architecture and shows typical automated modelling tasks.
**Relevance to this BTP:** A peer-reviewed citation for the Python (eppy-style) EnergyPlus automation behind your pymoo loop. I found no DOI-registered peer-reviewed paper for jEPlus.

---

## G. Indian codes, data, tariffs and costs

### G1. Eco-Niwas Samhita 2018, Part I: Building Envelope (BEE)  [BEE_ENS2018]
**Citation:** Bureau of Energy Efficiency (2018). *Eco-Niwas Samhita 2018 (Energy Conservation Building Code for Residential Buildings), Part I: Building Envelope.* New Delhi: BEE, Ministry of Power. (PDF read directly.)
**What it sets for warm-humid climates (Kolkata is listed as Warm-Humid in Annexure 2):**
- **RETV** (residential envelope transmittance value: net heat gain through walls and windows, *excluding the roof*) ≤ **15 W/m²** (clause 3.4.2). A footnote says BEE plans to tighten this to 12 W/m².
- RETV formula coefficients for Warm-Humid: a = 5.15, b = 1.31, c = 65.21 (Table 3). Orientation factors for latitude < 23.5° N, which covers Kolkata and Kharagpur: N 0.659, NE 0.906, E 1.155, SE 1.125, S 0.966, SW 1.124, W 1.156, NW 0.908 (Annexure 6, Table 9).
- **Roof U-value** ≤ **1.2 W/m²·K** for all climates (clause 3.3.2).
- Openable window-to-floor ratio ≥ **16.66%** for Warm-Humid (Table 1, adapted from NBC 2016).
- Applies to residential buildings on plots ≥ 500 m²; states may lower this threshold (clause 2.4).

**Relevance to this BTP:** The compliance limits for your base-case and retrofit envelopes. Note that RETV excludes the roof and does not capture PCM latent heat, which is itself a point to discuss. An ENS 2024 version exists, but I could not open it (see Unverified leads).

### G2. Bhanware et al. (2019): how the RETV formula was developed  [Bhanware2019]
**Citation:** Bhanware, P.K., Jaboyedoff, P., Maithel, S., Lall, A., Chetia, S., Kapoor, V.P., Rana, S., Mohan, S., Diddi, S., Siddiqui, A.N., Singh, A., Shukla, A. (2019). Development of RETV (Residential Envelope Transmittance Value) formula for cooling dominated climates of India for the proposed Energy Conservation Building Code for Residential Building (ECBC-R). In *Proceedings of Building Simulation 2019: 16th Conference of IBPSA*, Vol. 16, 3976–3983. DOI: 10.26868/25222708.2019.211019
**Summary:** RETV was fitted by multiple linear regression to many energy simulations (floor plans × climates × envelopes). The formula matched the simulated RETV with an average R² of 0.95. It is meant both for compliance and as a quick design-comparison tool.
**Relevance to this BTP:** Explains where the ENS coefficients come from, and that RETV is a steady regression on conduction and solar gain. That is why it cannot "see" a PCM.

### G3. National Building Code of India 2016 (BIS)  [BIS_NBC2016]
**Citation:** Bureau of Indian Standards (2016). *National Building Code of India 2016 (SP 7:2016).* New Delhi: BIS.
**Note:** I only checked it through ENS 2018, which adapts its window-to-floor-ratio table from NBC 2016. Use NBC Part 8 (Building Services) directly if you quote its ventilation or comfort clauses.

### G4. CEA CO₂ Baseline Database, Version 22.0 (August 2026)  [CEA2026v22; CEA2025v21]
**Citation:** Central Electricity Authority (2026). *CO2 Baseline Database for the Indian Power Sector, User Guide, Version 22.0.* New Delhi: CEA, Ministry of Power. (PDF read directly.)
**Numbers:** Weighted average grid emission factor of the integrated Indian grid, including renewables and captive injection, adjusted for cross-border transfers:
- **0.675 tCO₂/MWh for FY 2025-26** (Table S, v22.0), with OM 0.963, BM 0.446, CM 0.705;
- 0.710 for FY 2024-25 (Table S, v21.0, November 2025);
- 0.727 for FY 2023-24 (Table S, v20.0, December 2024).

v22.0 says earlier years were revised retroactively for captive-power data, so use one version consistently.
**Relevance to this BTP:** The CO₂ factor for converting kWh savings to CO₂ savings. 0.675 kg CO₂/kWh is the latest value.

### G5. WBSEDCL domestic tariff, FY 2025-26 (WBERC order of 20.03.2025)  [WBSEDCL2025tariff]
**Citation:** WBSEDCL (2025). *Gist of Tariff Order for the year 2025-26.* (PDF read directly.)
**Numbers (Low and Medium Voltage, *quarterly* consumption slabs, energy charge in paise/kWh):**
- **Domestic (Urban) Rate A(DM-U):** first 102 kWh 504; next 78 kWh 633; next 120 kWh 712; next 300 kWh 752; next 300 kWh 769; above 900 kWh 922. Fixed charge Rs 30/kVA/month.
- Domestic (Rural): 500 / 624 / 689 / 744 / 761 / 922.
- For consumers using up to 300 units, a state subsidy lowers the net Urban rates to 415 / 537 / 638 / 673 / 689 p/kWh (fixed charge Rs 20/kVA/month).
- "Hasir Alo" lifeline consumers (0–75 kWh per quarter) pay a net rate of zero.

**Relevance to this BTP:** For cost savings, use the *marginal* slab of a typical PMAY household. For example, at 300 kWh per quarter the last unit costs Rs 7.12 (Rs 6.38 after subsidy), and the average is about Rs 6.2/kWh (about Rs 5.4 after subsidy) (my calculation from the slabs). Note: most of Kolkata city is supplied by CESC Ltd. (separate tariff, not checked), while Kharagpur is in the WBSEDCL area. I found no 2026-27 tariff gist.

### G6. PMAY-Urban house size  [MoHUA_CLSS]
**Citation:** Ministry of Housing and Urban Affairs. *PMAY (Urban) Credit Linked Subsidy Scheme for EWS/LIG: Operational Guidelines.* (PDF read directly.)
**Numbers:** Carpet area up to **30 m²** for EWS houses and up to 60 m² for LIG houses. A PMAY-U 2.0 FAQ (seen only as a search snippet, not opened) mentions up to 45 m² for the BLC/AHP verticals, with a minimum of 30 m².
**Relevance to this BTP:** It fixes the floor area of your base-case house (EWS, about 30 m² carpet area).

### G7. PCM cost in India
- **OM37 (organic, non-paraffin, commercial PCM): Rs 450/kg (about US$5.4/kg).** In Abass & Muthulingam 2024 this gives a PCM cost of Rs 2430/m² of roof (600 g × 9 void formers), and Rs 3960/m² including aluminium void formers (Rs 170 each), with a 5.7-year payback in Rupnagar. *This is one supplier quote at one time; medium confidence.*
- I could not find a published price for PLUSS savE products or for technical-grade n-octadecane in India (see Unverified leads). Ask a supplier for a quote and run a cost sensitivity, e.g. Rs 300–900/kg.

---

## Further reading (DOI verified on Crossref; content only partly checked)

These are real and relevant, but I could not read enough of each to summarise it with numbers. They are in `references.bib`.
- Pasupathy, A., Velraj, R. (2008). Effect of double layer phase change material in building roof for year round thermal management. *Energy and Buildings*, 40(3), 193–203. DOI: 10.1016/j.enbuild.2007.02.016. (Chennai; early Indian roof-PCM work.)
- Pasupathy, A., Athanasius, L., Velraj, R., Seeniraj, R.V. (2008). Experimental investigation and numerical simulation analysis on the thermal performance of a building roof incorporating phase change material (PCM) for thermal management. *Applied Thermal Engineering*, 28(5–6), 556–565. DOI: 10.1016/j.applthermaleng.2007.04.016
- Kumar, A., Bhanja, D., Biswas, A. (2026). Impact of phase change material placement and thickness on roof thermal inertia in the warm and humid climate of Northeast India. *Journal of Thermal Analysis and Calorimetry*, 151(3), 2453–2468. DOI: 10.1007/s10973-025-15183-8. (Closest climate match to yours, but I could not access the abstract. Read it.)
- Saxena, R., Rakshit, D., Kaushik, S.C. (2020). Experimental assessment of Phase Change Material (PCM) embedded bricks for passive conditioning in buildings. *Renewable Energy*, 149, 587–599. DOI: 10.1016/j.renene.2019.12.081. (Delhi; inner-surface temperature 4–9.5 °C lower and heat transfer 40–60% lower during the day, per the abstract.)
- Solgi, E., Fayaz, R., Kari, B.M. (2016). Cooling load reduction in office buildings of hot-arid climate, combining phase change materials and night purge ventilation. *Renewable Energy*, 85, 725–731. DOI: 10.1016/j.renene.2015.07.028
- Tamer, T., Gürsel Dino, I., Baker, D.K., Meral Akgül, C. (2023). Coupling PCM wallboard utilization with night ventilation: Energy efficiency and overheating risk in office buildings under climate change impact. *Energy and Buildings*, 298, 113482. DOI: 10.1016/j.enbuild.2023.113482
- Al-Saadi, S.N., Zhai, Z. (2013). Modeling phase change materials embedded in building enclosure: A review. *Renewable and Sustainable Energy Reviews*, 21, 659–673. DOI: 10.1016/j.rser.2013.01.024. (Reviews the enthalpy and heat-capacity methods and the PCM models in EnergyPlus, TRNSYS and ESP-r.)
- Al-Saadi, S.N., Zhai, Z. (2015). Systematic evaluation of mathematical methods and numerical schemes for modeling PCM-enhanced building enclosure. *Energy and Buildings*, 92, 374–388. DOI: 10.1016/j.enbuild.2015.01.044
- Nguyen, A.-T., Reiter, S., Rigo, P. (2014). A review on simulation-based optimization methods applied to building performance analysis. *Applied Energy*, 113, 1043–1058. DOI: 10.1016/j.apenergy.2013.08.061
- Schiavon, S., Melikov, A.K. (2008). Energy saving and improved comfort by increased air movement. *Energy and Buildings*, 40(10), 1954–1960. DOI: 10.1016/j.enbuild.2008.05.001. (17–48% simulated cooling-energy savings; fan power above about 20 W can cancel the saving.)
- Indraganti, M., Ooka, R., Rijal, H.B., Brager, G.S. (2014). Adaptive model of thermal comfort for offices in hot and humid climates of India. *Building and Environment*, 74, 39–53. DOI: 10.1016/j.buildenv.2014.01.002
- Mi, X., Liu, R., Cui, H., Memon, S.A., Xing, F., Lo, Y. (2016). Energy and economic analysis of building integrated with PCM in different cities of China. *Applied Energy*, 175, 324–336. DOI: 10.1016/j.apenergy.2016.05.032
- Abilkhassenova, Z., Memon, S.A., Ahmad, A., Saurbayeva, A., Kim, J. (2023). Utilizing the Fanger thermal comfort model to evaluate the thermal, energy, economic, and environmental performance of PCM-integrated buildings in various climate zones worldwide. *Energy and Buildings*, 297, 113479. DOI: 10.1016/j.enbuild.2023.113479
- Mejia-Solis, E., Göransson, T., Palm, B. (2026). Optimizing thermal comfort and life cycle cost in high-altitude rural housing using NSGA-II and EnergyPlus. *Buildings*, 16(11), 2153. DOI: 10.3390/buildings16112153. (NSGA-II + EnergyPlus for low-income housing: discomfort and 10-year life-cycle cost.)
- Himran, S., Suwono, A., Mansoori, G.A. (1994). Characterization of alkanes and paraffin waxes for application as phase change energy storage medium. *Energy Sources*, 16(1), 117–128. DOI: 10.1080/00908319408909065
- Abhat, A. (1983). Low temperature latent heat thermal energy storage: Heat storage materials. *Solar Energy*, 30(4), 313–332. DOI: 10.1016/0038-092X(83)90186-X
- Neeper, D.A. (2000). Thermal dynamics of wallboard with latent heat storage. *Solar Energy*, 68(5), 393–403. DOI: 10.1016/S0038-092X(00)00012-8. (See Unverified leads about the claim usually attributed to it.)

## Unverified leads (do NOT cite these numbers until checked)

1. **Eco-Niwas Samhita 2024 (BEE).** BEE has published a newer residential code ("ENS 2024"), but its PDF would not download. I could not check whether the RETV (15 W/m²) or roof U-value (1.2 W/m²·K) limits changed. Check the BEE website.
2. **Sharma 2009 / Zalba 2003 property tables.** Values often quoted from these reviews for n-octadecane (about 28.2 °C, about 245 kJ/kg, k ≈ 0.148 W/m·K liquid / 0.358 W/m·K solid, ρ ≈ 774 / 814 kg/m³) could not be checked against the original tables (paywalled). I used Faden 2019, Vélez 2015 and NIST instead.
3. **Neeper (2000), Peippo et al. (1991, DOI 10.1016/0378-7788(91)90009-R).** These are often cited for the rule "optimal melting temperature ≈ average room temperature" and for an optimal melting-temperature formula. The DOIs are valid, but I could not read the text to confirm the claims.
4. **Indraganti et al. (2014).** A 2013 conference abstract by the same group reported comfort temperatures of 27.1 °C (Chennai) and 26.0 °C (Hyderabad) in AC mode. These are preliminary and were not checked in the 2014 paper.
5. **PLUSS savE product prices and the FS29 supplier.** No public price list was found. FS29 (used in A1) may be an Indian commercial product, but I did not confirm the supplier.
6. **WBSEDCL 2026-27 tariff and the CESC (Kolkata) tariff.** Not found or not checked. The 2025-26 WBSEDCL gist is the latest I could read.
7. **PMAY-U 2.0 house sizes** (45 m² for BLC/AHP; minimum 30 m²). Seen only in a search snippet of a government FAQ.
8. **jEPlus.** A widely used parametric tool, but I found no DOI-registered peer-reviewed paper for it. Cite eppy / Roth et al. 2018 instead, or the jEPlus website as software.
9. **"A Comparison of Thermal Comfort of Old Indigenous Houses with New Residential Buildings of Kolkata" (ISVS e-journal 11(2), 2024, DOI 10.61275/isvsej-2024-11-02-23).** Crossref has no author list; not read. It may be useful for Kolkata-specific comfort.

---

## Research gap (what this BTP adds)

1. **Climate and building type gap.** Indian PCM-roof studies are mostly for composite or hot-dry sites (Rupnagar: Abass & Muthulingam 2024; Delhi: Saxena et al. 2020), or for Chennai roofs and offices (Reddy et al. 2017; Bhamare et al. 2020; Arumugam & Ramalingam 2024). Only a few cover warm-humid *eastern* India, and none of those studied PMAY/EWS houses (Asrani et al. 2022 studied PMAY walls, but without PCM).
2. **Night discharge is the key unknown in warm-humid climates.** Night-time cooling potential in warm-humid India is about half that of hot-dry India (127 vs 251 W/m²; Panchabikesan et al. 2017). Chennai roof PCMs do not fully solidify (Reddy et al. 2017; Arumugam & Ramalingam 2024). In your Kolkata TMYx file, outdoor air stays at or above 27 °C all night on about 119 days per year. Most optimisation studies choose the melting temperature from energy alone (Saffari et al. 2017; Kishore et al. 2020). Few report *how often the PCM completes its cycle* (Evola et al. 2013; Lei et al. 2016).
3. **Comfort model gap.** PCM studies usually judge comfort with PMV/Fanger (e.g. Abilkhassenova et al. 2023) or generic adaptive limits. None found uses the Indian residential adaptive model IMAC-R (Rawal et al. 2022). Ceiling fans, which most low-income households use (Malik et al. 2020), are rarely combined with PCM in the analysis.
4. **Configuration gap.** Studies tend to put PCM in "the walls" or "the roof" (Lei et al. 2016; Kishore et al. 2020; Triano-Juárez et al. 2020). A side-by-side comparison of roof vs individual N/E/S/W walls vs walls+roof, for a small Indian dwelling under three operating modes (free-running, fan, AC), was not found.
5. **Code gap.** ENS 2018 judges envelopes by RETV (walls only, steady conduction and solar regression; Bhanware et al. 2019) and a roof U-value. Neither captures latent storage, and adding insulation can *worsen* free-running comfort (Vakil et al. 2025). Your study can show how a PCM retrofit performs compared with what ENS compliance alone would predict.
6. **Modelling-uncertainty gap.** EnergyPlus CondFD is validated (Tabares-Velasco et al. 2012), but single-curve models are known to struggle with hysteresis and partial melting cycles (Goia et al. 2018; Al-Janabi & Kavgic 2019). Indian PCM simulation studies rarely report sensitivity to time step, node spacing or hysteresis.
7. **Optimisation gap.** Multi-objective PCM optimisation exists for Europe, the U.S. and Central Asia (Bre et al. 2022; Saurbayeva et al. 2023), and NSGA-II + EnergyPlus exists for dwellings (Bre & Fachinotti 2017). No study was found that applies NSGA-II/NSGA-III to PCM type, melting temperature, thickness and location for Indian affordable housing with comfort, energy, cost and CO₂ objectives.
8. **Economic-context gap.** Indian payback estimates (5.7 years, Abass & Muthulingam 2024; 8.7–9 years, Arumugam C. et al. 2024) are for other building types and use flat electricity prices. EWS households face subsidised slab tariffs (WBSEDCL 2025-26), and the grid is getting cleaner (CEA: 0.727 → 0.675 tCO₂/MWh from FY 2023-24 to FY 2025-26). Both change the payback and CO₂ case for a retrofit.

---

## Paraffin property table (theme D)

All values are for pure n-alkanes. Commercial "technical" grades melt over a wider range and usually have 5–20% lower latent heat. **Source codes:**
- [F] Faden et al. 2019
- [V-AE] Vélez et al. 2015, *Applied Energy*
- [V-IJTS] Vélez et al. 2015, *Int. J. Thermal Sciences*
- [N] NIST WebBook (kJ/mol converted with NIST molar mass)
- [P] PubChem, quoting HSDB / CAMEO (NTP 1992) data; phase not always stated

"≈" means read from a graph or estimated (approximate). "—" means no verified value found.

| Property | n-Hexadecane C16 | n-Heptadecane C17 | **n-Octadecane C18 (baseline)** | n-Nonadecane C19 | n-Eicosane C20 |
|---|---|---|---|---|---|
| Molar mass (g/mol) [N] | 226.44 | 240.47 | 254.49 | 268.52 | 282.55 |
| Melting point (°C) | 17.8 [V-AE onset]; 17.9 ± 1 [N] | 21.3 [V-IJTS onset]; 22.0 ± 0.9 [N] | **28.0 [F mean]**; 27.1 [V-AE onset]; 27.9 ± 0.7 [N] | 31.2 [V-IJTS onset]; ≈31 ± 3 [N] | 35.7 [V-AE onset]; 36.9 ± 1 [N] |
| Latent heat of melting (kJ/kg) | 235 [V-AE]; 227 [N, 51.46 kJ/mol] | 165 [V-IJTS]; 167 [N] | **237 [F]**; 244 [V-AE]; 242 [N, 61.5 kJ/mol] | 166 [V-IJTS]; 171–177 [N] | 247 [V-AE]; 240–247 [N] |
| Solid–solid (rotator) transition | none | 8.8 °C, 40 kJ/kg [V-IJTS]; NIST lists ≈11 °C, 45.5 kJ/kg [N] | none on heating (V-AE saw one only on cooling for C20, not C18) | 21.8 °C, 42 kJ/kg [V-IJTS]; ≈22.8 °C, 51 kJ/kg [N] | on cooling only, 32.3 °C [V-AE] |
| Thermal conductivity, solid (W/m·K) | ≈0.33–0.35 [V-AE Fig. 6] | ≈0.20 (ordered solid, −14 to 0 °C) [V-IJTS] | **0.334 [F]**; ≈0.32–0.36 [V-AE] | 0.21–0.23 (−14 to 10 °C) [V-IJTS] | ≈0.42–0.45 [V-AE Fig. 6] |
| Thermal conductivity, liquid (W/m·K) | ≈0.15 (jump of 0.172 on melting) [V-AE] | 0.146 at 25–35 °C [V-IJTS] | **0.151 at 30 °C; 0.148 at 40 °C [F]** | 0.152 at 33 °C; 0.150 at 45 °C [V-IJTS] | ≈0.15 (jump of 0.263 on melting) [V-AE] |
| Density, solid (kg/m³) | — | — | **868 (wide uncertainty) [F]** | — | — |
| Density, liquid (kg/m³) | 766 at 30 °C [V-AE fit] | ≈778 at 20 °C [P, HSDB; probably sub-cooled liquid] | **775 at 30 °C; 769 at 40 °C [F]**; 774 at 30 °C [V-AE fit] | ≈777 at 32 °C [P, CAMEO/NTP] | 774 at 40 °C [V-AE fit] |
| Specific heat (kJ/kg·K) | polynomial in [V-AE] | polynomial in [V-IJTS] | **solid 1.84 at 20 °C; liquid 2.23 at 30 °C [F]** | polynomial in [V-IJTS] | polynomial in [V-AE] |

**Notes for EnergyPlus input:**
- **Odd alkanes (C17, C19) release part of their latent heat 9–10 K below melting.** Put this step into the enthalpy–temperature pairs, or you will overstate the useful latent heat.
- **Density.** `Material` takes one density. Faden's solid (868) and liquid (≈775) values differ by about 12%. Use the solid value with the full latent heat, or test both, and say which you chose.
- **Conductivity.** Conductivity roughly halves on melting. `MaterialProperty:PhaseChange` only allows a linear temperature coefficient, while the hysteresis object takes separate solid and liquid values.

---

## Key numbers to use in the model

| Item | Value | Source | Confidence |
|---|---|---|---|
| Roof U-value limit (ENS 2018, all climates) | ≤ 1.2 W/m²·K | ENS 2018 cl. 3.3.2 (PDF) | High |
| RETV limit, warm-humid (walls + windows, roof excluded) | ≤ 15 W/m² (BEE target: 12) | ENS 2018 cl. 3.4.2 and footnote 19 | High |
| RETV coefficients, warm-humid | a = 5.15, b = 1.31, c = 65.21 | ENS 2018 Table 3 | High |
| Orientation factors, latitude < 23.5° N | N 0.659, E 1.155, S 0.966, W 1.156 (others in G1) | ENS 2018 Annexure 6 | High |
| Minimum openable window-to-floor ratio, warm-humid | 16.66% | ENS 2018 Table 1 (from NBC 2016) | High |
| Grid CO₂ emission factor (latest) | 0.675 tCO₂/MWh (FY 2025-26) | CEA CO₂ Baseline Database v22.0, Aug 2026, Table S | High |
| Grid CO₂ factor, earlier years (for sensitivity) | 0.710 (FY 2024-25); 0.727 (FY 2023-24) | CEA v21.0, v20.0 | High |
| Electricity tariff, WBSEDCL Domestic Urban, FY 2025-26 | 5.04 / 6.33 / 7.12 / 7.52 / 7.69 / 9.22 Rs/kWh for quarterly slabs 0–102 / 103–180 / 181–300 / 301–600 / 601–900 / >900 kWh; fixed Rs 30/kVA/month | WBSEDCL gist 2025-26 | High (official), but a different tariff applies in CESC-supplied Kolkata |
| Same, net of state subsidy (consumers ≤ 300 units) | 4.15 / 5.37 / 6.38 / 6.73 / 6.89 Rs/kWh | WBSEDCL gist 2025-26 | High |
| Typical marginal rate for an EWS household (about 100 kWh/month) | about Rs 7.1/kWh (Rs 6.4 with subsidy) | my calculation from the slabs | Medium |
| PCM material cost | Rs 450/kg (OM37 organic PCM) | Abass & Muthulingam 2024 | Medium (single quote); run a sensitivity of about Rs 300–900/kg |
| Benchmark retrofit payback (other Indian cases) | 5.7 yr (Rupnagar roof slab); 8.7–9 yr (roof panels, composite / warm-humid) | Abass & Muthulingam 2024; Arumugam C. et al. 2024 | Medium |
| n-octadecane inputs | Tm 28.0 °C; L 237 kJ/kg; ρs 868 / ρl 775 kg/m³; ks 0.334 / kl 0.151 W/m·K; cp,s 1.84 / cp,l 2.23 kJ/kg·K | Faden et al. 2019 | High (liquid), medium (solid) |
| EnergyPlus time step for CondFD + PCM | ≥ 20 per hour (≤ 3 min) | EnergyPlus I/O Reference; Tabares-Velasco et al. 2012 | High |
| CondFD space discretisation | Default 3 is fine for annual results; about 1/3 of default spacing (constant ≈ 0.3–0.5) for hourly detail | NREL/TP-5500-55792 | High |
| Fan credit (ASHRAE 55 adaptive, upper limit only, operative temperature ≥ 25 °C) | +1.2 K at 0.6 m/s; +1.8 K at 0.9 m/s; +2.2 K at 1.2 m/s | ASHRAE 55-2020 via pythermalcomfort | High |
| PMAY-U EWS floor area | carpet area ≤ 30 m² | MoHUA CLSS guidelines | High |
| PMAY benchmark performance | EPI 64–68 kWh/m²/yr; 4145–6034 comfortable hours/yr | Asrani et al. 2022 | Medium (other climates and projects) |
