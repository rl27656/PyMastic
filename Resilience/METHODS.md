# Methods

Draft methods-section text for the flexible pavement resilience paper, generated
from the analysis implemented in this directory. Section numbering (3.x) is a
placeholder — renumber to match the manuscript. Verify all citation years below
against your own bibliography before submitting.

## 3.1 Mechanistic Framework

Pavement structural response was computed using multilayer elastic theory
(Burmister, 1943), implemented in the open-source Python package PyMastic
(Nakhaei, 2020), which solves the axisymmetric layered elastic boundary-value
problem via a Hankel integral transform evaluated as a truncated Bessel-function
series. PyMastic has been validated by its developer against the established
multilayer elastic solvers WESLEA and KENPAVE. All layer interfaces were modeled
as fully bonded (continuous stress and displacement across interfaces).

## 3.2 Loading Configuration

A single circular wheel load was applied at the pavement surface, with tire
contact pressure *q* = 100 psi and contact radius *a* = 5.99 in, corresponding to
a resultant wheel load *P* = *qπa²* ≈ 11,275 lbf. These load parameters follow the
values conventionally used in multilayer elastic analysis benchmark problems
(e.g., Huang, 2004). All responses were evaluated at the load center (*r* = 0),
the critical radial position for a single symmetric circular load.

## 3.3 Baseline Pavement Structure

A three-layer flexible pavement section was used as the reference case for all
sensitivity analyses:

| Layer | Thickness (in) | Modulus (ksi) | Poisson's ratio |
|---|---|---|---|
| Asphalt concrete (AC) | 6.0 | 500 | 0.35 |
| Granular base | 10.0 | 30 | 0.40 |
| Subgrade (semi-infinite) | — | 10 (*Mr*) | 0.45 |

The subgrade modulus is treated throughout as the subgrade resilient modulus, *Mr*.

## 3.4 Critical Response Locations

Two critical responses were extracted from each layered elastic solution:

- **εt** — the horizontal tensile strain at the bottom of the AC layer
  (*z* = *H_AC*), the strain governing bottom-up fatigue cracking;
- **εc** — the vertical compressive strain at the top of the subgrade
  (*z* = *H_AC* + *H_base*), the strain governing subgrade rutting (permanent
  deformation).

PyMastic reports strain using a compression-positive sign convention; strain
magnitudes were used in all transfer-function calculations.

## 3.5 Distress Transfer Functions

Critical strains were converted to allowable load repetitions (design life)
using established mechanistic-empirical transfer functions.

**Fatigue cracking** — Asphalt Institute (1981):

*N_f* = 0.0796 · ε_t^(−3.291) · E₁^(−0.854)

where *E₁* is the AC modulus (psi).

**Fatigue cracking** — MEPDG / NCHRP 1-37A (2004), reported in parallel for
comparison:

*N_f* = 0.00432 · *k₁* · *C* · ε_t^(−3.9492) · E₁^(−1.281)

*C* = 10^*M*, *M* = 4.84·(*V_be*/(*V_a*+*V_be*) − 0.69)

with air voids *V_a* = 7% and effective binder content *V_be* = 11% (typical
dense-graded HMA defaults, not a project-specific mix design) and calibration
coefficient *k₁* = 1.0 (uncalibrated national value).

**Rutting (subgrade permanent deformation)** — Asphalt Institute (1981):

*N_d* = 1.365×10⁻⁹ · ε_c^(−4.477)

For each condition, the governing distress mode was taken as whichever of *N_f*
(Asphalt Institute) or *N_d* produced the lower allowable repetitions, and
design life was defined as *min(N_f, N_d)*. The MEPDG fatigue estimate was
computed and reported alongside but was not combined with the Asphalt Institute
rutting model into a governance decision, since the two families of transfer
functions are calibrated independently and are not directly comparable in
absolute magnitude.

*Limitation:* The MEPDG's full rutting procedure requires an incremental, time-
and temperature-dependent simulation and has no closed-form strain-based
equivalent; consequently no MEPDG rutting model is included, and rutting
governance throughout is based solely on the Asphalt Institute model.

## 3.6 Sensitivity Analysis Design

Two complementary sweep strategies were used, all varying parameters around the
baseline structure (Section 3.3):

**One-factor-at-a-time (OFAT) sweeps** — five parameters were varied
individually, holding all others at baseline:

| Variable | Range | Interpretation |
|---|---|---|
| Subgrade *Mr* | 4–25 ksi | seasonal (spring-thaw softening to dry/frozen stiffening) |
| AC thickness | 3–12 in | structural design |
| Base thickness | 4–20 in | structural design |
| AC modulus | 100–2000 ksi | seasonal (temperature-driven stiffness) |
| Base modulus | 10–100 ksi | structural/material quality |

**Two-factor (2D) sweeps** — three parameter pairs were varied jointly on 40×40
grids (linear spacing for thickness/*Mr* pairs, logarithmic spacing for modulus
pairs), with the remaining parameters held at baseline: subgrade *Mr* × AC
thickness (crossing an environmental variable with a structural one), AC
modulus × base modulus, and AC thickness × base thickness (the latter two
crossing pairs of structural variables).

At every sampled condition, PyMastic was re-solved for the resulting strains,
and *N_f* and *N_d* were recomputed via Section 3.5. Where consecutive samples
changed governing distress, the fatigue/rutting crossover was located by linear
interpolation of log₁₀(*N_f*) − log₁₀(*N_d*) between the bracketing points (a
scalar crossover value for 1D sweeps; a boundary curve, obtained by the same
zero-level interpolation applied across the 2D grid, for 2D sweeps).

## 3.7 Numerical Implementation and Verification

PyMastic's Hankel-integral summation is controlled by an `iteration` parameter
setting the number of Bessel-zero-based quadrature points. At high iteration
counts, the summation's exponential terms were found to overflow (producing
non-finite results) once total pavement thickness became large relative to the
load radius *a* — observed starting near 18 in of total depth at the library's
example-default `iteration` = 40. Convergence was verified to occur well before
that point: results computed at `iteration` = 5 matched `iteration` = 40 to at
least 8 significant figures within the stable range, and remained numerically
finite across the full range of layer thicknesses studied here (up to 32 in
total depth). `iteration` = 5 was therefore used throughout without loss of
accuracy.

## 3.8 Software and Reproducibility

All analysis was implemented in Python (NumPy, SciPy, Matplotlib) built on the
open-source PyMastic solver. All sweep scripts, tabulated results (CSV), and
figures are archived at `rl27656/PyMastic` under `Resilience/`, allowing every
result in this section to be regenerated directly.
