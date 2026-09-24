"""
2D sensitivity study: pavement design life over AC modulus x base modulus.

Sweeps E_AC and E_base together on a grid (instead of one at a time),
holding layer thicknesses and subgrade Mr fixed, computing PyMastic
strains and design life at every combination. This is the natural next
step after the two separate 1D sweeps (sensitivity_AC_modulus.py,
sensitivity_base_modulus.py): it shows the full fatigue/rutting
governance boundary as a curve in (E_AC, E_base) space, rather than at
a single fixed value of the other modulus.

Outputs
-------
Resilience/results/AC_base_modulus_2D.csv   (long format, one row per grid point)
Resilience/results/AC_base_modulus_2D.png   (2-panel: governance map + design-life heatmap)
"""
import os
import sys
import csv
import warnings

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # repo root (Main/)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # Resilience/ (transfer_functions)

from Main.MLE import PyMastic
from transfer_functions import design_life_summary

# --- Fixed structure/subgrade properties; E_AC and E_BASE are swept below ---
H = [6.0, 10.0]        # in. [AC, Base]
E_SUBGRADE = 10.0      # ksi
nu = [0.35, 0.40, 0.45]

q, a = 100.0, 5.99      # standard single-wheel load (psi, in)
x = [0]
z = [1e-6, H[0], H[0] + H[1]]  # surface, bottom of AC, top of subgrade

# Grid ranges (log-spaced, matching the 1D sweeps' endpoints)
N = 40
E_AC_grid = np.logspace(np.log10(100), np.log10(2000), N)     # ksi
E_BASE_grid = np.logspace(np.log10(10), np.log10(100), N)     # ksi

rows = []
Nf_grid = np.zeros((N, N))   # [i=E_BASE index, j=E_AC index]
Nd_grid = np.zeros((N, N))
life_grid = np.zeros((N, N))
gov_grid = np.zeros((N, N))  # 0 = fatigue-governed, 1 = rutting-governed

for i, E_BASE in enumerate(E_BASE_grid):
    for j, E_AC in enumerate(E_AC_grid):
        E = [E_AC, E_BASE, E_SUBGRADE]
        # See sensitivity_AC_thickness.py: iteration=5 avoids the exp()-overflow
        # instability PyMastic hits at high iteration counts, and matches
        # iteration=40's result to 8+ significant figures where both are valid.
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            RS = PyMastic(q, a, x, z, H, E, nu, isBounded=[1, 1], iteration=5, inverser='solve')

        eps_t = RS['Strain_T'][1, 0]
        eps_c = RS['Strain_Z'][2, 0]
        life = design_life_summary(eps_t, eps_c, E_AC * 1000)

        Nf_grid[i, j] = life["Nf_AI"]
        Nd_grid[i, j] = life["Nd_AI"]
        life_grid[i, j] = life["design_life_AI"]
        gov_grid[i, j] = 1.0 if life["governing_AI"] == "rutting" else 0.0

        rows.append({
            "E_AC_ksi": E_AC,
            "E_BASE_ksi": E_BASE,
            "eps_t_microstrain": abs(eps_t) * 1e6,
            "eps_c_microstrain": abs(eps_c) * 1e6,
            "Nf_AI": life["Nf_AI"],
            "Nd_AI": life["Nd_AI"],
            "Nf_MEPDG": life["Nf_MEPDG"],
            "governing_AI": life["governing_AI"],
        })

out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
os.makedirs(out_dir, exist_ok=True)
csv_path = os.path.join(out_dir, "AC_base_modulus_2D.csv")
with open(csv_path, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)
print(f"Wrote {csv_path} ({len(rows)} grid points)")

n_rutting = int(gov_grid.sum())
print(f"Rutting-governed: {n_rutting}/{N*N} grid points | Fatigue-governed: {N*N - n_rutting}/{N*N}")

# --- chart ---
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.colors import LinearSegmentedColormap, ListedColormap

BLUE = "#2a78d6"
AQUA = "#1baf7a"
INK = "#0b0b0b"
SEC_INK = "#52514e"
MUTED = "#898781"
GRID = "#e1e0d9"
SURFACE = "#fcfcfb"

# Sequential blue ramp (light -> dark), per dataviz palette
SEQ_BLUE_STOPS = ["#cde2fb", "#b7d3f6", "#9ec5f4", "#86b6ef", "#6da7ec", "#5598e7",
                  "#3987e5", "#2a78d6", "#256abf", "#1c5cab", "#184f95", "#104281", "#0d366b"]
seq_cmap = LinearSegmentedColormap.from_list("blue_seq", SEQ_BLUE_STOPS)

AC_edges = np.concatenate([[E_AC_grid[0]], np.sqrt(E_AC_grid[:-1] * E_AC_grid[1:]), [E_AC_grid[-1]]])
BASE_edges = np.concatenate([[E_BASE_grid[0]], np.sqrt(E_BASE_grid[:-1] * E_BASE_grid[1:]), [E_BASE_grid[-1]]])

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5.5), dpi=200)
fig.patch.set_facecolor(SURFACE)

# --- Panel 1: governing-distress region map ---
ax1.set_facecolor(SURFACE)
gov_cmap = ListedColormap([BLUE, AQUA])
ax1.pcolormesh(AC_edges, BASE_edges, gov_grid, cmap=gov_cmap, vmin=0, vmax=1, shading="flat")
CS = ax1.contour(E_AC_grid, E_BASE_grid, np.log10(Nf_grid) - np.log10(Nd_grid),
                  levels=[0], colors=INK, linewidths=1.8)
ax1.set_xscale("log")
ax1.set_yscale("log")
ax1.set_xlabel("AC modulus, $E_{AC}$ (ksi)", color=SEC_INK, fontsize=10)
ax1.set_ylabel("Base modulus, $E_{base}$ (ksi)", color=SEC_INK, fontsize=10)
ax1.set_title("Governing Distress", color=INK, fontsize=12, fontweight="bold", pad=10)
ax1.tick_params(colors=MUTED, labelsize=8)
ax1.xaxis.set_major_formatter(mticker.ScalarFormatter())
ax1.yaxis.set_major_formatter(mticker.ScalarFormatter())
for spine in ax1.spines.values():
    spine.set_visible(False)

ax1.plot(500, 30, marker="*", markersize=16, markerfacecolor=SURFACE,
         markeredgecolor=INK, markeredgewidth=1.4, linestyle="none", zorder=5)

legend_handles = [
    plt.Rectangle((0, 0), 1, 1, facecolor=BLUE, label="Fatigue-governed"),
    plt.Rectangle((0, 0), 1, 1, facecolor=AQUA, label="Rutting-governed"),
    plt.Line2D([0], [0], color=INK, linewidth=1.8, label="$N_f = N_d$ boundary"),
    plt.Line2D([0], [0], marker="*", markersize=12, markerfacecolor=SURFACE,
               markeredgecolor=INK, linestyle="none", label="Baseline (500, 30 ksi)"),
]
ax1.legend(handles=legend_handles, loc="lower right", frameon=False, fontsize=8, labelcolor=SEC_INK)

# --- Panel 2: design-life heatmap ---
ax2.set_facecolor(SURFACE)
mesh = ax2.pcolormesh(AC_edges, BASE_edges, np.log10(life_grid), cmap=seq_cmap, shading="flat")
ax2.contour(E_AC_grid, E_BASE_grid, np.log10(Nf_grid) - np.log10(Nd_grid),
            levels=[0], colors=INK, linewidths=1.8, linestyles="dashed")
ax2.plot(500, 30, marker="*", markersize=16, markerfacecolor=SURFACE,
         markeredgecolor=INK, markeredgewidth=1.4, linestyle="none", zorder=5)
ax2.set_xscale("log")
ax2.set_yscale("log")
ax2.set_xlabel("AC modulus, $E_{AC}$ (ksi)", color=SEC_INK, fontsize=10)
ax2.set_ylabel("Base modulus, $E_{base}$ (ksi)", color=SEC_INK, fontsize=10)
ax2.set_title("Design Life (governing, ESALs)", color=INK, fontsize=12, fontweight="bold", pad=10)
ax2.tick_params(colors=MUTED, labelsize=8)
ax2.xaxis.set_major_formatter(mticker.ScalarFormatter())
ax2.yaxis.set_major_formatter(mticker.ScalarFormatter())
for spine in ax2.spines.values():
    spine.set_visible(False)

cbar = fig.colorbar(mesh, ax=ax2, pad=0.02)
cbar.set_label("log$_{10}$(design life)", color=SEC_INK, fontsize=9)
cbar.ax.tick_params(colors=MUTED, labelsize=8)
cbar.outline.set_visible(False)

fig.suptitle("Pavement Design Life — AC Modulus x Base Modulus (2D sweep)\n"
             "(6 in AC / 10 in base, $M_r$=10 ksi subgrade)",
             color=INK, fontsize=13, fontweight="bold", y=0.99)

fig.tight_layout()
fig.subplots_adjust(top=0.82, wspace=0.32)
png_path = os.path.join(out_dir, "AC_base_modulus_2D.png")
fig.savefig(png_path, facecolor=SURFACE)
print(f"Wrote {png_path}")
