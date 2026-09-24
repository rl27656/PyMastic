# Resilience

Mechanistic-empirical design-life analysis built on PyMastic's layered
elastic response, for a flexible pavement resilience study.

## Contents

- `transfer_functions.py` — strain-to-life transfer functions:
  - `fatigue_life_ai` / `rutting_life_ai`: Asphalt Institute (1981) models
  - `fatigue_life_mepdg`: MEPDG / NCHRP 1-37A (2004) bottom-up fatigue model
  - `design_life_summary`: runs all of the above and reports the governing
    (lowest) Asphalt Institute life
- `sensitivity_subgrade_Mr.py` — sweeps subgrade resilient modulus (Mr) over
  a representative seasonal range (4-25 ksi) with the AC/base structure held
  fixed, computing PyMastic strains and design life at each Mr. Writes
  `results/subgrade_Mr_sensitivity.csv` and `.png`.

## Key finding (current structure: 6 in AC / 10 in base)

Design life is rutting-governed at low subgrade Mr (soft, e.g. spring
thaw) and fatigue-governed at high Mr (stiff, e.g. dry/frozen conditions),
crossing over around Mr ~ 12 ksi. This crossover is the kind of
seasonal-resilience result the transfer functions are meant to surface —
sweep other structural variables (layer thickness, AC modulus) the same
way to build out the rest of the sensitivity analysis.

## Caveats

- The MEPDG fatigue model requires mix-design inputs (air voids `Va`,
  effective binder content `Vbe`) that are not outputs of the layered
  elastic analysis; `sensitivity_subgrade_Mr.py` uses typical dense-graded
  HMA defaults (Va=7%, Vbe=11%, k1=1.0) — replace with your actual mix
  design before reporting results.
- Asphalt Institute and MEPDG fatigue life values are **not directly
  comparable in absolute magnitude** — they come from different
  calibration datasets and are typically used with their own shift/
  calibration factors, not against each other. Treat cross-model
  agreement/disagreement as a modeling-uncertainty result, not an error.
- The MEPDG's actual rutting procedure is a full incremental,
  time-and-temperature-dependent calculation (not a closed-form
  Nd equation); only the Asphalt Institute closed-form rutting model is
  implemented here.
