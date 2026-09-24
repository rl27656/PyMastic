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
- `sensitivity_base_thickness.py` — sweeps granular base thickness (4-20 in)
  with AC thickness, all moduli, and load held fixed. Writes
  `results/base_thickness_sensitivity.csv` and `.png`.
- `sensitivity_AC_modulus.py` — sweeps AC modulus (100-2000 ksi, a
  temperature-driven seasonal range) with all thicknesses and the other
  moduli held fixed. Writes `results/AC_modulus_sensitivity.csv` and `.png`.
- `sensitivity_base_modulus.py` — sweeps granular base modulus (10-100 ksi)
  with all thicknesses, AC modulus, and subgrade Mr held fixed. Writes
  `results/base_modulus_sensitivity.csv` and `.png`.
- `combined_sensitivity_figure.py` — reads all five sweeps' CSVs (run them
  first) and lays them out as a 5-panel comparison with a shared legend
  and a marked fatigue/rutting crossover per panel. Writes
  `results/combined_sensitivity.png`.
- `sensitivity_AC_base_modulus_2D.py` — sweeps E_AC and E_base together on
  a 40x40 log-spaced grid (1600 PyMastic evaluations, ~12s), with
  thicknesses and subgrade Mr held fixed. Writes
  `results/AC_base_modulus_2D.csv` (long format) and `.png` (a 2-panel
  governing-distress region map + design-life heatmap, both with the
  Nf=Nd boundary curve and the baseline point (500, 30 ksi) marked).

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
- **Base thickness sweep:** the same pattern again — thin base (<~11-12 in)
  is rutting-governed, thicker base is fatigue-governed, crossing over
  around H_base ~ 11-12 in. Unlike the AC sweep, fatigue life is nearly
  flat here (base thickness barely changes eps_t at the bottom of AC),
  so the crossover is driven almost entirely by rutting life falling as
  the base thins — worth noting in the write-up as a distinct mechanism
  from the AC-thickness crossover.
- **AC modulus sweep:** a second seasonal/environmental variable (AC
  stiffens in cold weather, softens in heat), alongside subgrade Mr. Soft
  AC (E_AC <~ 850-1000 ksi, e.g. hot weather) is rutting-governed; stiff AC
  (e.g. cold weather) is fatigue-governed, crossing over around
  E_AC ~ 850-1000 ksi. Note this is the one sweep where the varied
  parameter also appears directly inside the fatigue transfer function
  itself (both models include an E_AC^-exponent term) in addition to
  changing the LEA strains — so the fatigue-life curve responds to E_AC
  through two combined mechanisms, unlike the other three sweeps.
- **Base modulus sweep:** the crossover **direction reverses** here
  compared to the other four sweeps — low base modulus (E_base <~ 20 ksi,
  a weak/undercompacted base) is **fatigue**-governed, and high base
  modulus (a strong/well-compacted base) is **rutting**-governed, crossing
  over around E_base ~ 18-20 ksi. That's because eps_t (bottom-of-AC
  tensile strain, which drives fatigue life via a steeper strain exponent)
  falls off faster with increasing base modulus than eps_c (top-of-
  subgrade compressive strain, which drives rutting life) does — so
  fatigue life overtakes rutting life as the base stiffens, the opposite
  of what happens in the other four sweeps. Also note eps_c is *not*
  monotonic in E_base here (it rises slightly from E_base=10 to ~20 ksi
  before falling) — a real layered-elastic effect from the base/subgrade
  modulus ratio, not a numerical artifact (visible as the small dip in the
  green curve early in `base_modulus_sensitivity.png`).

All five natural sweep variables (subgrade Mr, AC thickness, base
thickness, AC modulus, base modulus) are now covered.
- **AC x base modulus 2D sweep:** combining the two modulus sweeps into a
  grid shows the full $N_f=N_d$ boundary as a curve rather than a single
  crossover point. It's nearly vertical (governance is dominated by
  E_AC), with a slight leftward bend at low E_base consistent with the
  1D base-modulus sweep's crossover (~18-20 ksi at E_AC=500). The
  baseline case (E_AC=500, E_base=30) sits just inside the
  rutting-governed region, close to the boundary — consistent with the
  baseline structure result throughout this README.

## Numerical stability note (PyMastic)

PyMastic's Hankel-integral series can overflow (`exp()` -> NaN) at high
`iteration` values once total pavement thickness gets large relative to the
load radius `a`. In `sensitivity_AC_thickness.py` this appeared starting
around a total depth of 18 in at `iteration=40` (the value used in
`sensitivity_subgrade_Mr.py`, safe there because total depth is fixed at
16 in). Convergence for these single-point-at-load-center cases is reached
well before that — `iteration=5` matches `iteration=40`'s result to 8+
significant figures and stays finite across the full thickness sweep.
`sensitivity_base_thickness.py` reaches 26 in total depth, well past that
threshold, so it uses `iteration=5` too. If you extend these sweeps to
larger structures, re-check for this and back off `iteration` (or watch
for the library's own "singular matrix, PINV was used instead" warning)
rather than assuming a higher iteration count is always more accurate.

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
