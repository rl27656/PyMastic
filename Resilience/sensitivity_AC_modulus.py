"""
Sensitivity study: pavement design life vs. AC (asphalt concrete) modulus.

AC modulus is strongly temperature-dependent (stiff in cold weather, soft
in hot weather), making this sweep - like the subgrade Mr sweep - a
seasonal/environmental resilience variable rather than a pure design
variable. Sweeps E_AC over a representative range, holding layer
thicknesses, base/subgrade moduli, and load fixed, computing PyMastic
strains and design life at each E_AC.

Outputs
-------
Resilience/results/AC_modulus_sensitivity.csv
Resilience/results/AC_modulus_sensitivity.png
"""
import os
import sys
import csv
import warnings

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # repo root (Main/)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # Resilience/ (transfer_functions)

from Main.MLE import PyMastic
from transfer_functions import design_life_summary

# --- Fixed structure/base/subgrade properties; E_AC is swept below ---
H = [6.0, 10.0]              # in. [AC, Base]
E_BASE, E_SUBGRADE = 30.0, 10.0  # ksi
nu = [0.35, 0.40, 0.45]

q, a = 100.0, 5.99            # standard single-wheel load (psi, in)
x = [0]
z = [1e-6, H[0], H[0] + H[1]]  # surface, bottom of AC, top of subgrade

# Representative AC modulus range (ksi): hot/soft -> cold/stiff seasonal extremes
E_AC_values = [100, 200, 300, 500, 700, 1000, 1500, 2000]

rows = []
for E_AC in E_AC_values:
    E = [E_AC, E_BASE, E_SUBGRADE]
    # See sensitivity_AC_thickness.py: iteration=5 avoids the exp()-overflow
    # instability PyMastic hits at high iteration counts, and matches
    # iteration=40's result to 8+ significant figures where both are valid.
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        RS = PyMastic(q, a, x, z, H, E, nu, isBounded=[1, 1], iteration=5, inverser='solve')

    eps_t = RS['Strain_T'][1, 0]  # bottom of AC
    eps_c = RS['Strain_Z'][2, 0]  # top of subgrade

    life = design_life_summary(eps_t, eps_c, E_AC * 1000)  # E_AC feeds the fatigue model directly too
    rows.append({
        "E_AC_ksi": E_AC,
        "eps_t_microstrain": abs(eps_t) * 1e6,
        "eps_c_microstrain": abs(eps_c) * 1e6,
        "Nf_AI": life["Nf_AI"],
        "Nd_AI": life["Nd_AI"],
        "Nf_MEPDG": life["Nf_MEPDG"],
        "governing_AI": life["governing_AI"],
    })

# --- write CSV ---
out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
os.makedirs(out_dir, exist_ok=True)
csv_path = os.path.join(out_dir, "AC_modulus_sensitivity.csv")
with open(csv_path, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)
print(f"Wrote {csv_path}")

for r in rows:
    print(f"E_AC={r['E_AC_ksi']:>5} ksi | eps_t={r['eps_t_microstrain']:7.1f} ue | "
          f"eps_c={r['eps_c_microstrain']:7.1f} ue | Nf_AI={r['Nf_AI']:.3e} | "
          f"Nf_MEPDG={r['Nf_MEPDG']:.3e} | Nd_AI={r['Nd_AI']:.3e} | governs={r['governing_AI']}")

# --- chart ---
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

BLUE = "#2a78d6"
ORANGE = "#eb6834"
AQUA = "#1baf7a"
INK = "#0b0b0b"
SEC_INK = "#52514e"
MUTED = "#898781"
GRID = "#e1e0d9"
SURFACE = "#fcfcfb"

E_AC = [r["E_AC_ksi"] for r in rows]
Nf_ai = [r["Nf_AI"] for r in rows]
Nf_mepdg = [r["Nf_MEPDG"] for r in rows]
Nd_ai = [r["Nd_AI"] for r in rows]

fig, ax = plt.subplots(figsize=(7.5, 5), dpi=200)
fig.patch.set_facecolor(SURFACE)
ax.set_facecolor(SURFACE)

ax.plot(E_AC, Nf_ai, color=BLUE, linewidth=2, marker="o", markersize=6,
        markerfacecolor=SURFACE, markeredgecolor=BLUE, markeredgewidth=1.6,
        label="Fatigue life $N_f$ (Asphalt Institute)")
ax.plot(E_AC, Nf_mepdg, color=ORANGE, linewidth=2, marker="o", markersize=6,
        markerfacecolor=SURFACE, markeredgecolor=ORANGE, markeredgewidth=1.6,
        label="Fatigue life $N_f$ (MEPDG)")
ax.plot(E_AC, Nd_ai, color=AQUA, linewidth=2, marker="o", markersize=6,
        markerfacecolor=SURFACE, markeredgecolor=AQUA, markeredgewidth=1.6,
        label="Rutting life $N_d$ (Asphalt Institute)")

ax.set_xscale("log")
ax.set_yscale("log")
ax.set_xlabel("AC modulus, $E_{AC}$ (ksi)", color=SEC_INK, fontsize=11)
ax.set_ylabel("Allowable load repetitions (ESALs)", color=SEC_INK, fontsize=11)
ax.set_title("Pavement Design Life vs. AC Modulus\n"
              "(6 in AC / 10 in base, $M_r$=10 ksi subgrade, $E_{AC}$ sweep)",
              color=INK, fontsize=12, fontweight="bold", pad=14)

ax.grid(True, which="major", axis="both", color=GRID, linewidth=0.8)
ax.set_axisbelow(True)
for spine in ("top", "right"):
    ax.spines[spine].set_visible(False)
for spine in ("left", "bottom"):
    ax.spines[spine].set_color(MUTED)
ax.tick_params(colors=MUTED, labelsize=9)

ax.xaxis.set_major_formatter(mticker.ScalarFormatter())
ax.yaxis.set_major_formatter(mticker.LogFormatterSciNotation())

legend = ax.legend(frameon=False, loc="upper left", fontsize=9, labelcolor=SEC_INK)

fig.tight_layout()
png_path = os.path.join(out_dir, "AC_modulus_sensitivity.png")
fig.savefig(png_path, facecolor=SURFACE)
print(f"Wrote {png_path}")
