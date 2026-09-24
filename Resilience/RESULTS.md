# Results

Draft results-section text for the flexible pavement resilience paper, generated
from the analysis implemented in this directory. Section numbering (4.x) is a
placeholder — renumber to match the manuscript (follows on from `METHODS.md`'s
3.x numbering). All figures referenced are archived under `results/`; the
numbers below are reproducible directly from the corresponding CSV files.

## 4.1 Baseline Response

Under the baseline structure (6 in AC / 10 in granular base over a 10 ksi
subgrade; Section 3.3) and the standard single-wheel load (Section 3.2), the
layered elastic analysis gives a tensile strain of ε_t = 258.6 µε at the bottom
of the AC layer and a compressive strain of ε_c = 562.3 µε at the top of the
subgrade. Applying the transfer functions (Section 3.5) gives *N_f* (Asphalt
Institute) = 6.92×10⁵, *N_d* = 4.85×10⁵, and *N_f* (MEPDG) = 1.32×10⁴
repetitions. Rutting governs at the baseline (*N_d* < *N_f*), with a design
life of 4.85×10⁵ ESALs. As expected given their independent calibration
(Section 3.5), the MEPDG fatigue estimate is roughly 50× lower than the
Asphalt Institute estimate; this offset is consistent across every condition
tested (Sections 4.2–4.3) and is treated throughout as a modeling-uncertainty
result rather than a discrepancy to be resolved.

## 4.2 One-Factor-at-a-Time Sensitivity

Table 1 summarizes the fatigue/rutting crossover and the range of design-life
variation for each of the five OFAT sweeps (baseline held at all other
variables; Section 3.6).

**Table 1.** Fatigue/rutting crossover and design-life sensitivity by variable.

| Variable | Range tested | Crossover | *N_d* fold-change | *N_f* fold-change (AI) |
|---|---|---|---|---|
| Subgrade *Mr* | 4–25 ksi | 12.0 ksi | ×60.9 | ×1.8 |
| AC thickness | 3–12 in | 7.3 in | ×1364.4 | ×96.7 |
| Base thickness | 4–20 in | 11.4 in | ×81.8 | ×1.9 |
| AC modulus | 100–2000 ksi | 865 ksi | ×142.4 | ×15.4 |
| Base modulus | 10–100 ksi | 18.0 ksi | ×4.0 | ×15.9 |

In four of the five sweeps, *N_d* is markedly more sensitive to the swept
variable than *N_f* — increasing subgrade *Mr*, AC thickness, base thickness,
or AC modulus all raise the rutting life far faster than the fatigue life, so
each of these sweeps runs from rutting-governed (low end) to fatigue-governed
(high end) as the parameter increases. AC thickness is the most influential
single variable tested, producing more than three orders of magnitude of
variation in *N_d* over the 3–12 in range.

The base modulus sweep is the exception: *N_f* is more sensitive to base
modulus than *N_d* is (×15.9 vs. ×4.0), so the crossover **direction
reverses** relative to the other four sweeps — a weak base (*E_base* ≲ 18 ksi)
is fatigue-governed, and a strong base is rutting-governed. This is consistent
with the tensile strain at the bottom of AC falling off faster with base
stiffening than the subgrade compressive strain does. The base modulus sweep
also produced a non-monotonic ε_c response (a local rise from *E_base* = 10 to
≈20 ksi before falling), a genuine layered-elastic effect rather than a
numerical artifact.

## 4.3 Two-Factor (2D) Sensitivity

**Subgrade *Mr* × AC thickness.** Of the 1,600 grid points sampled, 1,078
(67.4%) were fatigue-governed and 522 (32.6%) rutting-governed. The
*N_f = N_d* boundary is a monotonically decreasing curve in (*H_AC*, *Mr*)
space, directly quantifying how much AC thickness compensates for seasonal
subgrade softening: the boundary crosses *H_AC* ≈ 7.3 in at *Mr* ≈ 10 ksi
(consistent with the 1D AC-thickness crossover, Table 1), *H_AC* ≈ 4.7 in at
*Mr* ≈ 15 ksi, and *H_AC* ≈ 3.2 in at *Mr* ≈ 20 ksi. At *Mr* ≈ 5 ksi, no
crossover occurs within the tested range (*H_AC* ≤ 12 in) — the structure
remains rutting-governed regardless of AC thickness, indicating that AC
thickness alone cannot fully compensate for subgrade softening of this
severity at this base/load combination.

**AC modulus × base modulus.** 1,036 points (64.8%) were rutting-governed and
564 (35.3%) fatigue-governed. The boundary is steep and dominated by *E_AC*:
at *E_base* = 10 ksi the crossover occurs at *E_AC* ≈ 170 ksi; at
*E_base* ≈ 31 ksi (near baseline) at *E_AC* ≈ 867 ksi, closely matching the 1D
AC-modulus crossover (865 ksi, Table 1); at *E_base* = 100 ksi at
*E_AC* ≈ 1182 ksi. Base modulus shifts the boundary by roughly a factor of 7
in *E_AC* across its full tested range, confirming AC modulus as the dominant
variable of the pair while base modulus still measurably modulates the
governance boundary.

**AC thickness × base thickness.** 578 points (36.1%) were rutting-governed
and 1,022 (63.9%) fatigue-governed. The boundary is close to linear: at
*H_AC* = 3 in the crossover occurs at *H_base* ≈ 15.0 in (total structural
thickness ≈ 17.95 in); at *H_AC* = 6 in at *H_base* ≈ 11.4 in (total
≈ 17.4 in, matching the 1D base-thickness crossover of 11.4 in, Table 1); at
*H_AC* = 12 in at *H_base* ≈ 4.6 in (total ≈ 16.6 in). The modest decline in
total crossover thickness as more of it is allocated to AC is consistent with
AC being the stiffer, more load-spreading-effective layer per inch.

## 4.4 Cross-Sweep Synthesis

Two results recur across the analysis and are worth foregrounding for the
discussion. First, the baseline structure sits close to the fatigue/rutting
boundary in every sweep that includes AC or base thickness (crossovers at
7.3 in vs. a baseline of 6 in AC; 11.4 in vs. a baseline of 10 in base), and
rutting-governed but near the boundary in the two modulus-based sweeps — this
is a structure operating near its fatigue/rutting balance point rather than
deep in either regime, which is what makes it a sensitive reference case for
a resilience study. Second, base modulus is the only one of the five OFAT
variables whose crossover runs in the opposite direction from the rest
(Section 4.2); this asymmetry, together with the near-vertical
AC-modulus-dominated boundary in the joint modulus sweep (Section 4.3),
suggests AC properties are the primary lever governing which distress mode
controls design life in this structure, with base and subgrade properties
acting as secondary, sometimes counteracting, influences.
