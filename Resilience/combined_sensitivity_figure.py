"""
Combined 5-panel figure comparing all sensitivity sweeps.

Reads the CSVs already written by sensitivity_subgrade_Mr.py,
sensitivity_AC_thickness.py, sensitivity_base_thickness.py,
sensitivity_AC_modulus.py, and sensitivity_base_modulus.py (run those
first) and lays them out on one figure with a shared legend, so the
fatigue/rutting crossover behavior can be compared side by side across
all five variables.

Output
------
Resilience/results/combined_sensitivity.png
"""
import os
import csv
import math

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

RESULTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")

BLUE = "#2a78d6"
ORANGE = "#eb6834"
AQUA = "#1baf7a"
INK = "#0b0b0b"
SEC_INK = "#52514e"
MUTED = "#898781"
GRID = "#e1e0d9"
SURFACE = "#fcfcfb"

# (csv filename, x column, panel title, x label, x scale)
PANELS = [
    ("subgrade_Mr_sensitivity.csv", "Mr_ksi", "Subgrade $M_r$",
     "$M_r$ (ksi)", "linear"),
    ("AC_thickness_sensitivity.csv", "H_AC_in", "AC Thickness",
     "$H_{AC}$ (in)", "linear"),
    ("base_thickness_sensitivity.csv", "H_BASE_in", "Base Thickness",
     "$H_{base}$ (in)", "linear"),
    ("AC_modulus_sensitivity.csv", "E_AC_ksi", "AC Modulus",
     "$E_{AC}$ (ksi)", "log"),
    ("base_modulus_sensitivity.csv", "E_BASE_ksi", "Base Modulus",
     "$E_{base}$ (ksi)", "log"),
]


def read_csv(path):
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        return [row for row in reader]


def find_crossover(x, nf, nd):
    """Linear-interpolate the x value where log(Nf) - log(Nd) changes sign."""
    diff = [math.log10(a) - math.log10(b) for a, b in zip(nf, nd)]
    for i in range(len(diff) - 1):
        if diff[i] == 0:
            return x[i]
        if (diff[i] < 0) != (diff[i + 1] < 0):
            frac = diff[i] / (diff[i] - diff[i + 1])
            return x[i] + frac * (x[i + 1] - x[i])
    return None


fig, axes = plt.subplots(2, 3, figsize=(15, 9), dpi=200)
fig.patch.set_facecolor(SURFACE)
axes_flat = axes.flatten()

for ax, (fname, xcol, title, xlabel, xscale) in zip(axes_flat, PANELS):
    rows = read_csv(os.path.join(RESULTS_DIR, fname))
    x = [float(r[xcol]) for r in rows]
    Nf_ai = [float(r["Nf_AI"]) for r in rows]
    Nf_mepdg = [float(r["Nf_MEPDG"]) for r in rows]
    Nd_ai = [float(r["Nd_AI"]) for r in rows]

    ax.set_facecolor(SURFACE)
    ax.plot(x, Nf_ai, color=BLUE, linewidth=2, marker="o", markersize=5,
            markerfacecolor=SURFACE, markeredgecolor=BLUE, markeredgewidth=1.4)
    ax.plot(x, Nf_mepdg, color=ORANGE, linewidth=2, marker="o", markersize=5,
            markerfacecolor=SURFACE, markeredgecolor=ORANGE, markeredgewidth=1.4)
    ax.plot(x, Nd_ai, color=AQUA, linewidth=2, marker="o", markersize=5,
            markerfacecolor=SURFACE, markeredgecolor=AQUA, markeredgewidth=1.4)

    xover = find_crossover(x, Nf_ai, Nd_ai)
    if xover is not None:
        ax.axvline(xover, color=MUTED, linewidth=1.2, linestyle=(0, (4, 3)))

    ax.set_xscale(xscale)
    ax.set_yscale("log")
    ax.set_title(title, color=INK, fontsize=12, fontweight="bold", pad=10)
    ax.set_xlabel(xlabel, color=SEC_INK, fontsize=10)

    ax.grid(True, which="major", axis="both", color=GRID, linewidth=0.7)
    ax.set_axisbelow(True)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    for spine in ("left", "bottom"):
        ax.spines[spine].set_color(MUTED)
    ax.tick_params(colors=MUTED, labelsize=8)
    ax.yaxis.set_major_formatter(mticker.LogFormatterSciNotation())
    if xscale == "log":
        ax.xaxis.set_major_formatter(mticker.ScalarFormatter())

    # annotate crossover value now that ylim is finalized
    if xover is not None:
        ymin, ymax = ax.get_ylim()
        ylabel_pos = ymin * (ymax / ymin) ** 0.06
        ax.text(xover, ylabel_pos, f"  {xover:.1f}", color=MUTED, fontsize=8,
                va="bottom", ha="left")

# shared y-axis label on left-column panels
axes[0, 0].set_ylabel("Allowable load repetitions (ESALs)", color=SEC_INK, fontsize=10)
axes[1, 0].set_ylabel("Allowable load repetitions (ESALs)", color=SEC_INK, fontsize=10)

# 6th cell: legend + summary
legend_ax = axes_flat[5]
legend_ax.axis("off")
legend_ax.set_facecolor(SURFACE)

handles = [
    plt.Line2D([0], [0], color=BLUE, linewidth=2, marker="o", markersize=6,
               markerfacecolor=SURFACE, markeredgecolor=BLUE,
               label="Fatigue life $N_f$ (Asphalt Institute)"),
    plt.Line2D([0], [0], color=ORANGE, linewidth=2, marker="o", markersize=6,
               markerfacecolor=SURFACE, markeredgecolor=ORANGE,
               label="Fatigue life $N_f$ (MEPDG)"),
    plt.Line2D([0], [0], color=AQUA, linewidth=2, marker="o", markersize=6,
               markerfacecolor=SURFACE, markeredgecolor=AQUA,
               label="Rutting life $N_d$ (Asphalt Institute)"),
    plt.Line2D([0], [0], color=MUTED, linewidth=1.2, linestyle=(0, (4, 3)),
               label="Fatigue/rutting crossover ($N_f$=$N_d$, AI)"),
]
legend_ax.legend(handles=handles, loc="center", frameon=False, fontsize=10,
                  labelcolor=SEC_INK, title="Series", title_fontsize=11)

fig.suptitle("Flexible Pavement Design Life Sensitivity — Five-Variable Comparison\n"
             "(baseline: 6 in AC / 10 in base, $E_{AC}$=500 ksi, $E_{base}$=30 ksi, $M_r$=10 ksi)",
             color=INK, fontsize=14, fontweight="bold", y=0.98)

fig.tight_layout()
fig.subplots_adjust(top=0.84, hspace=0.35, wspace=0.28)
png_path = os.path.join(RESULTS_DIR, "combined_sensitivity.png")
fig.savefig(png_path, facecolor=SURFACE)
print(f"Wrote {png_path}")
