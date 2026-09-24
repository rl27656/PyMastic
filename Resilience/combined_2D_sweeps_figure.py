"""
Combined figure: the other two 2D sweeps side by side.

Reads AC_base_modulus_2D.csv and AC_base_thickness_2D.csv (run
sensitivity_AC_base_modulus_2D.py and sensitivity_AC_base_thickness_2D.py
first) and lays their governing-distress region maps out side by side
with one shared legend, companion to combined_sensitivity_figure.py
(which covers the five 1D sweeps plus the Mr x AC thickness 2D sweep).
Together the two combined figures cover all three 2D sweeps:
  - Mr x AC thickness       (environmental x structural) -> combined_sensitivity_figure.py
  - AC modulus x base modulus   (structural x structural) -> this figure
  - AC thickness x base thickness (structural x structural) -> this figure

Output
------
Resilience/results/combined_2D_sweeps.png
"""
import os
import csv

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.colors import ListedColormap

RESULTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")

BLUE = "#2a78d6"
AQUA = "#1baf7a"
INK = "#0b0b0b"
SEC_INK = "#52514e"
MUTED = "#898781"
SURFACE = "#fcfcfb"


def read_csv(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def build_grid(rows, xcol, ycol):
    xvals = sorted(set(float(r[xcol]) for r in rows))
    yvals = sorted(set(float(r[ycol]) for r in rows))
    xi = {v: j for j, v in enumerate(xvals)}
    yi = {v: i for i, v in enumerate(yvals)}
    gov = np.zeros((len(yvals), len(xvals)))
    Nf = np.zeros_like(gov)
    Nd = np.zeros_like(gov)
    for r in rows:
        i, j = yi[float(r[ycol])], xi[float(r[xcol])]
        gov[i, j] = 1.0 if r["governing_AI"] == "rutting" else 0.0
        Nf[i, j] = float(r["Nf_AI"])
        Nd[i, j] = float(r["Nd_AI"])
    return np.array(xvals), np.array(yvals), gov, Nf, Nd


def edges_linear(vals):
    d = (vals[1] - vals[0]) / 2
    return np.concatenate([[vals[0] - d], vals[:-1] + d, [vals[-1] + d]])


def edges_log(vals):
    return np.concatenate([[vals[0]], np.sqrt(vals[:-1] * vals[1:]), [vals[-1]]])


PANELS = [
    dict(csv="AC_base_modulus_2D.csv", xcol="E_AC_ksi", ycol="E_BASE_ksi",
         title="AC Modulus x Base Modulus", xlabel="$E_{AC}$ (ksi)", ylabel="$E_{base}$ (ksi)",
         xscale="log", yscale="log", baseline=(500, 30),
         fatigue_label_pos=(1300, 70), rutting_label_pos=(150, 15)),
    dict(csv="AC_base_thickness_2D.csv", xcol="H_AC_in", ycol="H_BASE_in",
         title="AC Thickness x Base Thickness", xlabel="$H_{AC}$ (in)", ylabel="$H_{base}$ (in)",
         xscale="linear", yscale="linear", baseline=(6, 10),
         fatigue_label_pos=(10, 17), rutting_label_pos=(5, 7)),
]

fig, axes = plt.subplots(1, 2, figsize=(11.5, 5.5), dpi=200)
fig.patch.set_facecolor(SURFACE)

gov_cmap = ListedColormap([BLUE, AQUA])

for ax, panel in zip(axes, PANELS):
    rows = read_csv(os.path.join(RESULTS_DIR, panel["csv"]))
    xvals, yvals, gov, Nf, Nd = build_grid(rows, panel["xcol"], panel["ycol"])

    edges_x = edges_log(xvals) if panel["xscale"] == "log" else edges_linear(xvals)
    edges_y = edges_log(yvals) if panel["yscale"] == "log" else edges_linear(yvals)

    ax.set_facecolor(SURFACE)
    ax.pcolormesh(edges_x, edges_y, gov, cmap=gov_cmap, vmin=0, vmax=1, shading="flat")
    ax.contour(xvals, yvals, np.log10(Nf) - np.log10(Nd), levels=[0], colors=INK, linewidths=1.8)
    bx, by = panel["baseline"]
    ax.plot(bx, by, marker="*", markersize=15, markerfacecolor=SURFACE,
            markeredgecolor=INK, markeredgewidth=1.4, linestyle="none", zorder=5)

    fx, fy = panel["fatigue_label_pos"]
    rx, ry = panel["rutting_label_pos"]
    ax.text(fx, fy, "Fatigue-governed", color=INK, fontsize=9, ha="center", va="center")
    ax.text(rx, ry, "Rutting-governed", color=SURFACE, fontsize=9, ha="center", va="center")

    ax.set_xscale(panel["xscale"])
    ax.set_yscale(panel["yscale"])
    ax.set_title(panel["title"], color=INK, fontsize=12, fontweight="bold", pad=10)
    ax.set_xlabel(panel["xlabel"], color=SEC_INK, fontsize=10)
    ax.set_ylabel(panel["ylabel"], color=SEC_INK, fontsize=10)
    ax.tick_params(colors=MUTED, labelsize=8)
    if panel["xscale"] == "log":
        ax.xaxis.set_major_formatter(mticker.ScalarFormatter())
    if panel["yscale"] == "log":
        ax.yaxis.set_major_formatter(mticker.ScalarFormatter())
    for spine in ax.spines.values():
        spine.set_visible(False)

handles = [
    plt.Rectangle((0, 0), 1, 1, facecolor=BLUE, label="Fatigue-governed"),
    plt.Rectangle((0, 0), 1, 1, facecolor=AQUA, label="Rutting-governed"),
    plt.Line2D([0], [0], color=INK, linewidth=1.8, label="$N_f = N_d$ boundary"),
    plt.Line2D([0], [0], marker="*", markersize=11, markerfacecolor=SURFACE,
               markeredgecolor=INK, linestyle="none", label="Baseline design point"),
]
fig.legend(handles=handles, loc="lower center", ncol=4, frameon=False, fontsize=9.5,
           labelcolor=SEC_INK, bbox_to_anchor=(0.5, 0.0))

fig.suptitle("Pavement Design Life — Structural x Structural 2D Sweeps\n"
             "(baseline: 6 in AC / 10 in base, $E_{AC}$=500 ksi, $E_{base}$=30 ksi, $M_r$=10 ksi)",
             color=INK, fontsize=13.5, fontweight="bold", y=0.99)

fig.tight_layout()
fig.subplots_adjust(top=0.80, bottom=0.16, wspace=0.32)
png_path = os.path.join(RESULTS_DIR, "combined_2D_sweeps.png")
fig.savefig(png_path, facecolor=SURFACE)
print(f"Wrote {png_path}")
