# PCM-based ceiling panels for passive cooling in buildings: A CFD modelling

## 1. Core Problem Being Solved
While macro-encapsulating PCMs prevents leakage and chemical interaction with building materials, it creates a severe thermal bottleneck: organic PCMs have inherently **low thermal conductivity**. This restricts heat transfer, causing the PCM core to remain solid and useless even while the surface melts. Furthermore, traditional PCM applications are static (embedded in plaster or concrete), making them difficult to retrofit or adjust for seasonal cooling capacity. 

## 2. State of the Art & Progress Made
**State of the Art:** Prior literature established that increasing the surface-area-to-volume ratio of an encapsulated PCM boosts its melting rate. However, exhaustive geometric optimization of 3D macro-capsules for ceiling applications was lacking.
**Progress Made:** This study decoupled the PCM from the building structure by designing flexible, modular, ceiling-suspended panels. Through rigorous CFD modeling and physical validation, the researchers established critical geometric design rules:
*   **Shape Matters:** Multi-pyramidal panels outperformed tetrahedral panels, yielding a **20.8% higher average melting rate** due to a thinner thermal boundary layer around the protrusions.
*   **Volume Penalty:** Increasing a panel's volume (from 250 mL to 750 mL) drastically dropped the normalized melting rate by up to 46.4%. Large volumes insulate themselves; PCMs must be distributed into multiple smaller panels.
*   **Suspension Gap:** Hanging the panels at least 5 cm below the ceiling exposes the base to natural convection, increasing the melting rate by over 30%.

## 3. Tools, Techniques, and Formulas Used
*   **Material:** A ternary eutectic mixture of capric, lauric, and oleic acids, achieving a specific melting temperature of $13^\circ\text{C}$. Properties were verified using a TEMPOS thermal conductivity analyzer.
*   **CFD Solver (Ansys Fluent):** Modeled 3D conjugate heat transfer (natural convection + solid conduction).
*   **Enthalpy-Porosity Method:** Used to model the phase change without tracking a sharp solid/liquid interface. The mushy zone is treated as a porous medium where liquid fraction $\gamma$ is:
    $$\gamma = \begin{cases} 0 & \text{when } T < T_{solidus} \\ \frac{T - T_{solidus}}{T_{liquidus} - T_{solidus}} & \text{when } T_{solidus} < T < T_{liquidus} \\ 1 & \text{when } T > T_{liquidus} \end{cases}$$
*   **Boussinesq Approximation:** Modeled buoyancy-driven airflow and liquid PCM convection:
    $$\rho = \rho_{ref}[1 - \beta(T - T_{ref})]$$
*   **Realizable k-$\epsilon$ Model:** Used to resolve the turbulence of the natural convection plume in the ambient air.
*   **Momentum Sink Source Term ($S_{i}$):** Added to the Navier-Stokes equations to rapidly force velocity to zero as the PCM solidifies:
    $$S_{i} = \frac{(1 - \gamma)^2}{(\gamma^3 + \epsilon)} A_{mush} u_i$$