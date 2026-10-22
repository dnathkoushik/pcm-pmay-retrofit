# Exploring the potential of independent PCM-based free cooling in climate-dominant building structures

## 1. Core Problem Being Solved
The building sector accounts for a massive portion of global energy consumption and greenhouse gas emissions, largely driven by HVAC systems. While passive cooling using Phase Change Materials (PCMs) has been studied, almost all prior research focused on residential or commercial buildings with inherent thermal mass (concrete, bricks). 
This paper targets **low-thermal-mass, climate-dominant enclosures** (e.g., outdoor equipment sheds, sensor stations, battery storage cabinets). Constructed from thin metal or timber, these structures offer zero thermal buffering. Consequently, their indoor temperatures spike severely due to solar irradiation, often trapping heat and remaining significantly hotter than the outdoor ambient air.

## 2. State of the Art & Progress Made
**State of the Art:** Macro-encapsulated PCM ceilings are popular because they exploit downward natural convection and do not interfere with usable space. Historically, they have been used to shave peak cooling loads by up to 30% in standard offices. 
**Progress Made:** This study pioneers the use of an independent, modular PCM panel array in a zero-thermal-mass outdoor shed. The results proved highly effective:
*   Reduced the daily average indoor-outdoor temperature difference by **88.4%**.
*   Lowered the nocturnal temperature difference by **92.1%**.
*   Achieved **sub-ambient indoor cooling**, proving that the PCM panels could successfully drive the internal temperature of a sealed metal shed *below* the outdoor ambient temperature during peak midday periods.

## 3. Tools, Techniques, and Formulas Used
*   **Material Design:** A eutectic binary mixture of organic fatty acids (Capric and Lauric acid) was engineered. Based on local climate analysis in Canberra, the mixture was tuned to a freezing point of $18^\circ\text{C}$ and a melting point of $20^\circ\text{C}$ to balance diurnal charging and discharging.
*   **Characterization:** Differential Scanning Calorimetry (DSC) was used to measure a latent heat of fusion of $115\text{ kJ/kg}$.
*   **Fabrication:** 25 hollow panels were 3D-printed using Acrylonitrile Butadiene Styrene (ABS) with a 2 mm shell thickness. The geometry featured a cuboid base topped with four pyramids.
*   **Experimental Setup:** The panels were installed on the ceiling of a galvanized metal shed. A polyethylene foam layer insulated the top of the panels to enforce an adiabatic boundary, ensuring heat was absorbed exclusively from the indoor air. Type-K thermocouples and data loggers mapped vertical thermal stratification.
*   **Computational Fluid Dynamics (CFD):** Used Ansys Fluent to model individual panel performance. The researchers successfully used an **equivalent constant ambient temperature** as a boundary condition substitution for time-varying temperatures, which maintained phase-change fidelity while cutting computational time by over 50%.