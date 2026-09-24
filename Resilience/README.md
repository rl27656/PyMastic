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
- `sensitivity_AC_thickness.py` — sweeps AC surface thickness (3-12 in) with
  base thickness, all moduli, and load held fixed. Writes
  `results/AC_thickness_sensitivity.csv` and `.png`.

## Key findings (baseline structure: 6 in AC / 10 in base, Mr=10 ksi)

- **Subgrade Mr sweep:** design life is rutting-governed at low subgrade Mr
  (soft, e.g. spring thaw) and fatigue-governed at high Mr (stiff, e.g.
  dry/frozen conditions), crossing over around Mr ~ 12 ksi. This crossover
  is the kind of seasonal-resilience result the transfer functions are
  meant to surface.
- **AC thickness sweep:** the same crossover appears from the structural
  side — thin AC (<~7-8 in) is rutting-governed, thicker AC is
  fatigue-governed, crossing over around H_AC ~ 7-8 in for this base/
  subgrade combination.

Sweep other structural variables (base thickness, AC modulus) the same way
to build out the rest of the sensitivity analysis.

## Numerical stability note (PyMastic)

PyMastic's Hankel-integral series can overflow (`exp()` -> NaN) at high
`iteration` values once total pavement thickness gets large relative to the
load radius `a`. In `sensitivity_AC_thickness.py` this appeared starting
around a total depth of 18 in at `iteration=40` (the value used in
`sensitivity_subgrade_Mr.py`, safe there because total depth is fixed at
16 in). Convergence for these single-point-at-load-center cases is reached
well before that — `iteration=5` matches `iteration=40`'s result to 8+
significant figures and stays finite across the full thickness sweep. If
you extend these sweeps to larger structures, re-check for this and back
off `iteration` (or watch for the library's own "singular matrix, PINV was
used instead" warning) rather than assuming a higher iteration count is
always more accurate.

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
