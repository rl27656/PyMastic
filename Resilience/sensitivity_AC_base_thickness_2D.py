"""
2D sensitivity study: pavement design life over AC thickness x base thickness.

Sweeps H_AC and H_base together on a grid (instead of one at a time),
holding all layer moduli and subgrade Mr fixed, computing PyMastic
strains and design life at every combination. Companion to
sensitivity_AC_base_modulus_2D.py: shows the full fatigue/rutting
governance boundary as a curve in (H_AC, H_base) space, generalizing
sensitivity_AC_thickness.py and sensitivity_base_thickness.py.

Outputs
-------
Resilience/results/AC_base_thickness_2D.csv   (long format, one row per grid point)
Resilience/results/AC_base_thickness_2D.png   (2-panel: governance map + design-life heatmap)
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

# --- Fixed moduli/subgrade properties; H_AC and H_BASE are swept below ---
E_AC, E_BASE, E_SUBGRADE = 500.0, 30.0, 10.0  # ksi
nu = [0.35, 0.40, 0.45]

q, a = 100.0, 5.99      # standard single-wheel load (psi, in)
x = [0]

# Grid ranges (linear, matching the 1D sweeps' endpoints)
# Verified stable at iteration=5 up to 32in total depth (the max reached here).
N = 40
H_AC_grid = np.linspace(3, 12, N)     # in
H_BASE_grid = np.linspace(4, 20, N)   # in

rows = []
Nf_grid = np.zeros((N, N))   # [i=H_BASE index, j=H_AC index]
Nd_grid = np.zeros((N, N))
life_grid = np.zeros((N, N))
gov_grid = np.zeros((N, N))  # 0 = fatigue-governed, 1 = rutting-governed

for i, H_BASE in enumerate(H_BASE_grid):
    for j, H_AC in enumerate(H_AC_grid):
        H = [H_AC, H_BASE]
        E = [E_AC, E_BASE, E_SUBGRADE]
        z = [1e-6, H_AC, H_AC + H_BASE]
        # See sensitivity_AC_thickness.py: iteration=5 avoids the exp()-overflow
        # instability PyMastic hits at high iteration counts, and matches
        # iteration=40's result to 8+ significant figures where both are valid.
        # Verified finite here across the full grid corners (up to 32in total depth).
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
            "H_AC_in": H_AC,
            "H_BASE_in": H_BASE,
            "eps_t_microstrain": abs(eps_t) * 1e6,
            "eps_c_microstrain": abs(eps_c) * 1e6,
            "Nf_AI": life["Nf_AI"],
            "Nd_AI": life["Nd_AI"],
            "Nf_MEPDG": life["Nf_MEPDG"],
            "governing_AI": life["governing_AI"],
        })

out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
os.makedirs(out_dir, exist_ok=True)
csv_path = os.path.join(out_dir, "AC_base_thickness_2D.csv")
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
from matplotlib.colors import LinearSegmentedColormap, ListedColormap

BLUE = "#2a78d6"
AQUA = "#1baf7a"
INK = "#0b0b0b"
SEC_INK = "#52514e"
MUTED = "#898781"
SURFACE = "#fcfcfb"

# Sequential blue ramp (light -> dark), per dataviz palette
SEQ_BLUE_STOPS = ["#cde2fb", "#b7d3f6", "#9ec5f4", "#86b6ef", "#6da7ec", "#5598e7",
                  "#3987e5", "#2a78d6", "#256abf", "#1c5cab", "#184f95", "#104281", "#0d366b"]
seq_cmap = LinearSegmentedColormap.from_list("blue_seq", SEQ_BLUE_STOPS)

# linear grid -> uniform half-step edges
dAC = (H_AC_grid[1] - H_AC_grid[0]) / 2
dBASE = (H_BASE_grid[1] - H_BASE_grid[0]) / 2
AC_edges = np.concatenate([[H_AC_grid[0] - dAC], H_AC_grid[:-1] + dAC, [H_AC_grid[-1] + dAC]])
BASE_edges = np.concatenate([[H_BASE_grid[0] - dBASE], H_BASE_grid[:-1] + dBASE, [H_BASE_grid[-1] + dBASE]])

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5.5), dpi=200)
fig.patch.set_facecolor(SURFACE)

# --- Panel 1: governing-distress region map ---
ax1.set_facecolor(SURFACE)
gov_cmap = ListedColormap([BLUE, AQUA])
ax1.pcolormesh(AC_edges, BASE_edges, gov_grid, cmap=gov_cmap, vmin=0, vmax=1, shading="flat")
ax1.contour(H_AC_grid, H_BASE_grid, np.log10(Nf_grid) - np.log10(Nd_grid),
            levels=[0], colors=INK, linewidths=1.8)
ax1.plot(6, 10, marker="*", markersize=16, markerfacecolor=SURFACE,
         markeredgecolor=INK, markeredgewidth=1.4, linestyle="none", zorder=5)
ax1.set_xlabel("AC thickness, $H_{AC}$ (in)", color=SEC_INK, fontsize=10)
ax1.set_ylabel("Base thickness, $H_{base}$ (in)", color=SEC_INK, fontsize=10)
ax1.set_title("Governing Distress", color=INK, fontsize=12, fontweight="bold", pad=10)
ax1.tick_params(colors=MUTED, labelsize=8)
for spine in ax1.spines.values():
    spine.set_visible(False)

legend_handles = [
    plt.Rectangle((0, 0), 1, 1, facecolor=BLUE, label="Fatigue-governed"),
    plt.Rectangle((0, 0), 1, 1, facecolor=AQUA, label="Rutting-governed"),
    plt.Line2D([0], [0], color=INK, linewidth=1.8, label="$N_f = N_d$ boundary"),
    plt.Line2D([0], [0], marker="*", markersize=12, markerfacecolor=SURFACE,
               markeredgecolor=INK, linestyle="none", label="Baseline (6, 10 in)"),
]
ax1.legend(handles=legend_handles, loc="upper right", frameon=True, facecolor=SURFACE,
           edgecolor="none", framealpha=0.9, fontsize=8, labelcolor=SEC_INK)

# --- Panel 2: design-life heatmap ---
ax2.set_facecolor(SURFACE)
mesh = ax2.pcolormesh(AC_edges, BASE_edges, np.log10(life_grid), cmap=seq_cmap, shading="flat")
ax2.contour(H_AC_grid, H_BASE_grid, np.log10(Nf_grid) - np.log10(Nd_grid),
            levels=[0], colors=INK, linewidths=1.8, linestyles="dashed")
ax2.plot(6, 10, marker="*", markersize=16, markerfacecolor=SURFACE,
         markeredgecolor=INK, markeredgewidth=1.4, linestyle="none", zorder=5)
ax2.set_xlabel("AC thickness, $H_{AC}$ (in)", color=SEC_INK, fontsize=10)
ax2.set_ylabel("Base thickness, $H_{base}$ (in)", color=SEC_INK, fontsize=10)
ax2.set_title("Design Life (governing, ESALs)", color=INK, fontsize=12, fontweight="bold", pad=10)
ax2.tick_params(colors=MUTED, labelsize=8)
for spine in ax2.spines.values():
    spine.set_visible(False)

cbar = fig.colorbar(mesh, ax=ax2, pad=0.02)
cbar.set_label("log$_{10}$(design life)", color=SEC_INK, fontsize=9)
cbar.ax.tick_params(colors=MUTED, labelsize=8)
cbar.outline.set_visible(False)

fig.suptitle("Pavement Design Life — AC Thickness x Base Thickness (2D sweep)\n"
             "($E_{AC}$=500 ksi, $E_{base}$=30 ksi, $M_r$=10 ksi subgrade)",
             color=INK, fontsize=13, fontweight="bold", y=0.99)

fig.tight_layout()
fig.subplots_adjust(top=0.82, wspace=0.32)
png_path = os.path.join(out_dir, "AC_base_thickness_2D.png")
fig.savefig(png_path, facecolor=SURFACE)
print(f"Wrote {png_path}")
