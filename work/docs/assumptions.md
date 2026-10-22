# Modelling assumptions

The values below are used in `work/src/model.py` and `work/src/run.py`. Items marked **(assumed)** are engineering judgements that should be confirmed or tested in a sensitivity analysis.

## Building (West Bengal PMAY-U BLC model design)

| Item | Value | Source |
|---|---|---|
| Plan dimensions | Centre-line dimensions from the drawing; 3 zones (BED 3.025 × 3.625 m, LIV 3.375 × 4.95 m, TOI 3.7 × 1.15 m) | WB MED drawing |
| Ceiling height | 2.75 m | drawing note 5 |
| External wall | 15 mm cement plaster + 250 mm burnt brick + 12 mm plaster | drawing (250 mm main wall) |
| Partition | 12 + 125 mm brick + 12 mm plaster | drawing (125 mm partition) |
| Roof | 25 mm cement screed + **125 mm** RCC M20 + 12 mm plaster | RCC M20 from drawing; thickness **(assumed)** |
| Ground floor | 75 mm PCC + 25 mm DPC + 20 mm flooring; ground temperatures from the EPW at 0.5 m depth | drawing foundation detail |
| Windows | 5 × W1 900 × 900 mm, sill 1.2 m, single clear glass (U 5.8, SHGC 0.82). The drawing specifies Z-batten (timber) shutters; glazing is **(assumed)**, as is common in built houses | drawing schedule |
| Toilet ventilators | 3 × WO2 750 × 750 mm with RCC jali, modelled as a permanent 50 % free-area opening **(assumed)** | drawing |
| Orientation | Drawing "up" = North **(assumed)**; tested as a sensitivity | — |
| Material properties | Brick k 0.811, ρ 1820, cp 880; RCC k 1.58, ρ 2288, cp 880; plaster k 0.721, ρ 1762, cp 840; screed k 0.72, ρ 1648, cp 920 | ECBC 2017 / NBC tables |
| Solar absorptance | Roof screed 0.70, wall plaster 0.60; cool-roof coating 0.25 **(assumed)** | — |

## Occupancy and operation (family of four)

| Item | Value |
|---|---|
| Bedroom | 2 people, occupied 21–07 h (sleeping 72 W/person) |
| Living + kitchen | 4 people 06–09 h and 17–22 h, 2 people otherwise (117 W/person awake) |
| Lights | 3 W/m², 05–07 h (50 %) and 18–22 h |
| Equipment | fridge + misc 60 W continuous, TV 70 W 18–22 h, LPG cooking 1 kW 07–08, 12–13 (50 %), 19–20 h |
| Infiltration | 1.0 ACH **(assumed)**, leaky timber shutters |
| Natural ventilation | Window opening area 50 % of window area. Open 06–22 h when T<sub>in</sub> > T<sub>out</sub> and T<sub>in</sub> > 22 °C; night ventilation (22–06 h) is a design variable. Toilet jalis are always open |
| Ceiling fans (FAN mode) | 60 W per habitable room while occupied, 1 Mar–15 Nov; comfort credit +1.2 °C on the IMAC-R upper limit (ASHRAE 55 elevated air speed, 0.6 m/s) |
| AC (AC mode) | Ideal-loads cooling, 26 °C set-point, SHR 0.7; bedroom 22–07 h, living room 13–17 h and 19–22 h, 1 Mar–15 Nov; windows closed while AC is available; COP 3.3 **(assumed)** |

## PCM

| PCM | T<sub>m</sub> (°C) | Latent heat (kJ/kg) | ρ (kg/m³) | k solid/liquid (W/m·K) |
|---|---|---|---|---|
| n-heptadecane (C17) | 22.0 | 214 | 778 | 0.21 / 0.15 |
| n-octadecane (C18), baseline | 28.2 | 244 | 800 | 0.36 / 0.15 |
| n-nonadecane (C19) | 32.0 | 222 | 800 | 0.30 / 0.15 |
| n-eicosane (C20) | 36.6 | 247 | 800 | 0.30 / 0.15 |
| OM37 (reference only) | 37.0 | 173.9 | 880 | 0.30 / 0.20 |

- These are typical literature values for pure paraffins (e.g. Sharma et al. 2009) and should be checked against supplier DSC data.
- The melting range is 2 K wide (linear enthalpy rise). cp is 2000 J/kg·K (2100 for C17). There is no hysteresis.
- The encapsulation shell is not modelled; the PCM is an effective continuous layer.
- **Retrofit build-ups:**
  - roof top: new 25 mm screed over PCM over the existing roof;
  - ceiling: PCM + 12.5 mm gypsum board under the slab;
  - walls: PCM + 12.5 mm gypsum board on the inner face.
- PCM is applied only to the habitable rooms (BED, LIV).

## Numerics

- **Algorithm:** EnergyPlus 26.2, CondFD (fully implicit). EnergyPlus enforces at least 20 time steps per hour with CondFD.
- **Grid:** space discretisation constant 1.8 for the parametric study, which is within about 0.1 percentage points of the converged result at 1.0 or 0.5. The final cases are re-run at 1.0.
- **Algorithm check:** for the baseline, CondFD and CTF agree within 0.02 percentage points of discomfort and 1 % of roof heat gain.

## Economics

| Item | Value |
|---|---|
| PCM price | Rs 450/kg (OM37 price reported by Abass & Muthulingam 2024) |
| Encapsulation, finish and labour | Rs 700/m² roof top, Rs 600/m² ceiling or wall **(assumed)** |
| Cool-roof coating | Rs 150/m² **(assumed)** |
| XPS insulation | Rs 14/m² per mm + Rs 700/m² screed and labour **(assumed)** |
| Electricity tariff | Rs 7/kWh **(assumed)**, marginal domestic slab |
| Grid emission factor | 0.72 kgCO₂/kWh (CEA, approximate) |
