"""
gen_plots.py — 01_vcsel_sideband
=================================
Generates publication-quality visualisation plots for the VCSEL sideband
modulation module of the MEMS atomic clock.

Outputs (saved to plots/):
  bessel_functions.png
  sideband_spectrum.png
  modulation_efficiency.png
  rf_power_sensitivity.png

Usage:
    python gen_plots.py
"""

import os
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.patches import FancyArrowPatch
from scipy.special import jv

# ── Import sim results ─────────────────────────────────────────────────────
sys.path.insert(0, os.path.dirname(__file__))
from sim import RESULTS, F_MOD_HZ, compute_rf_power_dbm

PLOTS_DIR = os.path.join(os.path.dirname(__file__), "plots")
os.makedirs(PLOTS_DIR, exist_ok=True)

# ── Pull values from RESULTS ───────────────────────────────────────────────
beta_opt        = RESULTS["optimal_beta"]          # 1.8409
j1_opt          = RESULTS["j1_at_optimal"]         # 0.5819
j0_opt          = RESULTS["j0_at_optimal"]         # 0.3162
sb_pwr          = RESULTS["sideband_power_pct"]    # 67.71 %
spacing_ghz     = RESULTS["sideband_spacing_ghz"]  # 6.834682611 GHz
rf_dbm          = RESULTS["rf_drive_power_dbm"]    # ~6.0 dBm
f_mod_ghz       = F_MOD_HZ / 1e9                   # 3.4173 GHz

carrier_pct     = jv(0, beta_opt)**2 * 100         # ~10.0 %
pm1_pct         = (jv(1, beta_opt)**2 + jv(-1, beta_opt)**2) * 100  # ~67.7 %
pm2_pct         = (jv(2, beta_opt)**2 + jv(-2, beta_opt)**2) * 100  # ~19.97 %

# ── Global style ───────────────────────────────────────────────────────────
matplotlib.style.use("seaborn-v0_8-whitegrid")

PALETTE = {
    "blue":   "#1f77b4",
    "red":    "#d62728",
    "green":  "#2ca02c",
    "purple": "#9467bd",
    "orange": "#ff7f0e",
    "grey":   "#7f7f7f",
    "cyan":   "#17becf",
}

DPI        = 150
FIGSIZE_W  = (9, 5.5)
FIGSIZE_SQ = (7, 6)


# ══════════════════════════════════════════════════════════════════════════════
# 1. BESSEL FUNCTIONS
# ══════════════════════════════════════════════════════════════════════════════
def plot_bessel_functions():
    beta = np.linspace(0, 6, 1200)
    j0   = jv(0, beta)
    j1   = jv(1, beta)
    j2   = jv(2, beta)
    j3   = jv(3, beta)

    # Find exact J1 maximum for annotation
    idx_max  = np.argmax(j1)
    beta_max = beta[idx_max]
    j1_max   = j1[idx_max]

    fig, ax = plt.subplots(figsize=FIGSIZE_W)

    ax.plot(beta, j0, color=PALETTE["blue"],   lw=2.2, label=r"$J_0(\beta)$")
    ax.plot(beta, j1, color=PALETTE["red"],    lw=2.2, label=r"$J_1(\beta)$")
    ax.plot(beta, j2, color=PALETTE["green"],  lw=2.2, label=r"$J_2(\beta)$")
    ax.plot(beta, j3, color=PALETTE["purple"], lw=2.2, label=r"$J_3(\beta)$")

    # Vertical dashed line at optimal beta
    ax.axvline(beta_opt, color=PALETTE["orange"], lw=1.6, ls="--",
               label=fr"$\beta_{{opt}} = {beta_opt:.4f}$")

    # Horizontal dashed line at J1 max
    ax.axhline(j1_max, color=PALETTE["red"], lw=1.2, ls=":", alpha=0.65,
               label=fr"$J_{{1,\max}} = {j1_max:.4f}$")

    # Star at J1 maximum
    ax.plot(beta_max, j1_max, marker="*", ms=14, color=PALETTE["red"],
            zorder=6, label=None)

    # Arrow annotation for beta_opt
    ax.annotate(
        fr"$\beta_{{opt}} = {beta_opt:.4f}$" + "\n" + fr"$J_1 = {j1_max:.4f}$",
        xy=(beta_opt, j1_max),
        xytext=(beta_opt + 0.55, j1_max + 0.10),
        fontsize=9.5,
        color=PALETTE["orange"],
        arrowprops=dict(
            arrowstyle="->",
            color=PALETTE["orange"],
            lw=1.4,
            connectionstyle="arc3,rad=-0.25",
        ),
        bbox=dict(boxstyle="round,pad=0.3", fc="white", ec=PALETTE["orange"],
                  alpha=0.85, lw=0.8),
    )

    # Zero line
    ax.axhline(0, color="black", lw=0.7, ls="-", alpha=0.35)

    ax.set_xlim(0, 6)
    ax.set_ylim(-0.45, 0.82)
    ax.set_xlabel(r"Modulation index $\beta$", fontsize=12)
    ax.set_ylabel(r"$J_n(\beta)$", fontsize=12)
    ax.set_title("Bessel Functions — VCSEL Sideband Amplitudes", fontsize=13, fontweight="bold")
    ax.legend(loc="upper right", fontsize=9.5, framealpha=0.9)
    ax.xaxis.set_minor_locator(ticker.MultipleLocator(0.25))
    ax.yaxis.set_minor_locator(ticker.MultipleLocator(0.05))

    # Shade the useful ±1 sideband region of J1
    ax.fill_between(beta, 0, j1, where=(j1 > 0),
                    color=PALETTE["red"], alpha=0.06)

    fig.tight_layout()
    path = os.path.join(PLOTS_DIR, "bessel_functions.png")
    fig.savefig(path, dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {path}")


# ══════════════════════════════════════════════════════════════════════════════
# 2. SIDEBAND SPECTRUM
# ══════════════════════════════════════════════════════════════════════════════
def plot_sideband_spectrum():
    orders = np.arange(-5, 6)
    powers = np.array([jv(n, beta_opt)**2 * 100 for n in orders])

    # Colours: ±1 = bright red, n=0 = orange, rest = grey
    bar_colors = []
    for n in orders:
        if abs(n) == 1:
            bar_colors.append(PALETTE["red"])
        elif n == 0:
            bar_colors.append(PALETTE["orange"])
        else:
            bar_colors.append(PALETTE["grey"])

    fig, ax = plt.subplots(figsize=FIGSIZE_W)

    bars = ax.bar(orders, powers, color=bar_colors, width=0.65,
                  edgecolor="white", linewidth=0.6, zorder=3)

    # Annotate ±1 bars
    for n, p in zip(orders, powers):
        if abs(n) == 1:
            ax.text(n, p + 0.6, f"{p:.1f}%",
                    ha="center", va="bottom", fontsize=10,
                    fontweight="bold", color=PALETTE["red"])
        elif n == 0:
            ax.text(n, p + 0.6, f"{p:.1f}%",
                    ha="center", va="bottom", fontsize=9.5,
                    color=PALETTE["orange"])
        elif abs(n) == 2:
            ax.text(n, p + 0.6, f"{p:.1f}%",
                    ha="center", va="bottom", fontsize=8.5,
                    color=PALETTE["grey"])

    # Total CPT-useful annotation box
    total_cpt = powers[orders == 1][0] + powers[orders == -1][0]
    ax.annotate(
        f"Total CPT-useful power\n(±1 sidebands combined)\n"
        f"{total_cpt:.1f}%",
        xy=(0, 0), xytext=(2.4, 28),
        fontsize=9.5,
        bbox=dict(boxstyle="round,pad=0.5", fc="#fff3cd", ec=PALETTE["orange"],
                  alpha=0.95, lw=1.2),
        arrowprops=None,
    )
    # Arrows from annotation to ±1 bars
    ax.annotate("", xy=(-1, powers[orders == -1][0] + 0.5),
                xytext=(2.0, 27.5),
                arrowprops=dict(arrowstyle="->", color=PALETTE["red"],
                                lw=1.3, connectionstyle="arc3,rad=0.25"))
    ax.annotate("", xy=(1, powers[orders == 1][0] + 0.5),
                xytext=(3.0, 27.5),
                arrowprops=dict(arrowstyle="->", color=PALETTE["red"],
                                lw=1.3, connectionstyle="arc3,rad=-0.25"))

    # ── Secondary x-axis: frequency offset in GHz ─────────────────────────
    ax2 = ax.twiny()
    ax2.set_xlim(ax.get_xlim())
    sec_ticks  = orders
    sec_labels = [f"{n * f_mod_ghz:.2f}" for n in sec_ticks]
    ax2.set_xticks(sec_ticks)
    ax2.set_xticklabels(sec_labels, fontsize=7.5, rotation=30, ha="left")
    ax2.set_xlabel("Frequency offset from carrier (GHz)", fontsize=10, labelpad=4)

    ax.set_xlabel("Sideband order  $n$", fontsize=12)
    ax.set_ylabel("Power fraction (%)", fontsize=12)
    ax.set_title(fr"Sideband Power Distribution at $\beta = {beta_opt:.2f}$",
                 fontsize=13, fontweight="bold")
    ax.set_xticks(orders)
    ax.set_xlim(-5.7, 5.7)
    ax.set_ylim(0, 43)
    ax.yaxis.set_minor_locator(ticker.MultipleLocator(2))

    # Legend patches
    from matplotlib.patches import Patch
    legend_els = [
        Patch(facecolor=PALETTE["red"],    label=f"±1 sidebands — CPT signal ({pm1_pct:.1f}%)"),
        Patch(facecolor=PALETTE["orange"], label=f"Carrier n=0 ({carrier_pct:.1f}%)"),
        Patch(facecolor=PALETTE["grey"],   label=f"Higher sidebands (|n|≥2, {100-pm1_pct-carrier_pct:.1f}%)"),
    ]
    ax.legend(handles=legend_els, loc="upper left", fontsize=9, framealpha=0.9)

    fig.tight_layout()
    path = os.path.join(PLOTS_DIR, "sideband_spectrum.png")
    fig.savefig(path, dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {path}")


# ══════════════════════════════════════════════════════════════════════════════
# 3. MODULATION EFFICIENCY
# ══════════════════════════════════════════════════════════════════════════════
def plot_modulation_efficiency():
    beta = np.linspace(0.01, 4.0, 1000)

    # Total power fractions vs beta
    p_pm1  = (jv(1, beta)**2  + jv(-1, beta)**2)  * 100   # ±1 combined
    p_car  = jv(0, beta)**2 * 100                          # carrier
    p_pm2  = (jv(2, beta)**2  + jv(-2, beta)**2)  * 100   # ±2 combined

    # Values at optimal beta for annotations
    p_pm1_opt = (jv(1, beta_opt)**2 + jv(-1, beta_opt)**2) * 100
    p_car_opt  = jv(0, beta_opt)**2 * 100
    p_pm2_opt  = (jv(2, beta_opt)**2 + jv(-2, beta_opt)**2) * 100

    fig, ax = plt.subplots(figsize=FIGSIZE_W)

    ax.plot(beta, p_pm1, color=PALETTE["red"],   lw=2.4,
            label=r"$2|J_1(\beta)|^2$ — total ±1 power (CPT signal)")
    ax.plot(beta, p_car, color=PALETTE["blue"],  lw=2.4,
            label=r"$|J_0(\beta)|^2$ — carrier")
    ax.plot(beta, p_pm2, color=PALETTE["green"], lw=2.0, ls="--",
            label=r"$2|J_2(\beta)|^2$ — total ±2 power (waste)")

    # Vertical line at optimal beta
    ax.axvline(beta_opt, color=PALETTE["orange"], lw=1.8, ls="--",
               label=fr"$\beta_{{opt}} = {beta_opt:.4f}$", zorder=4)

    # Horizontal line at peak ±1 power
    ax.axhline(p_pm1_opt, color=PALETTE["red"], lw=1.2, ls=":",
               alpha=0.6)

    # Shaded region under the ±1 curve at optimum
    ax.fill_between(beta, 0, p_pm1, where=(beta <= beta_opt + 0.01) & (beta >= beta_opt - 0.01),
                    color=PALETTE["orange"], alpha=0.3)

    # Annotation: peak efficiency
    ax.annotate(
        fr"Peak ±1 power: {p_pm1_opt:.1f}%"
        "\n"
        fr"Carrier suppressed to {p_car_opt:.1f}%",
        xy=(beta_opt, p_pm1_opt),
        xytext=(beta_opt + 0.45, p_pm1_opt - 12),
        fontsize=9.5,
        color="#333333",
        arrowprops=dict(arrowstyle="->", color=PALETTE["orange"], lw=1.4,
                        connectionstyle="arc3,rad=0.2"),
        bbox=dict(boxstyle="round,pad=0.4", fc="white", ec=PALETTE["orange"],
                  alpha=0.90, lw=0.9),
    )

    # Annotation: carrier power at optimum
    ax.annotate(
        fr"$J_0(\beta_{{opt}}) = {j0_opt:.4f}$" + "\n" + fr"Carrier = {p_car_opt:.1f}%",
        xy=(beta_opt, p_car_opt),
        xytext=(beta_opt + 0.45, p_car_opt + 8),
        fontsize=9,
        color=PALETTE["blue"],
        arrowprops=dict(arrowstyle="->", color=PALETTE["blue"], lw=1.3,
                        connectionstyle="arc3,rad=-0.2"),
        bbox=dict(boxstyle="round,pad=0.35", fc="white", ec=PALETTE["blue"],
                  alpha=0.88, lw=0.8),
    )

    ax.set_xlim(0, 4)
    ax.set_ylim(0, 80)
    ax.set_xlabel(r"Modulation index $\beta$", fontsize=12)
    ax.set_ylabel("Power fraction (%)", fontsize=12)
    ax.set_title("CPT Power Efficiency vs Modulation Index", fontsize=13, fontweight="bold")
    ax.legend(loc="upper right", fontsize=9.5, framealpha=0.9)
    ax.xaxis.set_minor_locator(ticker.MultipleLocator(0.1))
    ax.yaxis.set_minor_locator(ticker.MultipleLocator(5))

    # Add horizontal grid lines for key percentages
    for pct, lbl in [(60, "60% requirement"), (p_pm1_opt, "")]:
        ax.axhline(pct, color="black", lw=0.7, ls=":", alpha=0.4)
        if lbl:
            ax.text(3.98, pct + 0.8, lbl, ha="right", va="bottom",
                    fontsize=8, color="black", alpha=0.6)

    fig.tight_layout()
    path = os.path.join(PLOTS_DIR, "modulation_efficiency.png")
    fig.savefig(path, dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {path}")


# ══════════════════════════════════════════════════════════════════════════════
# 4. RF POWER SENSITIVITY
# ══════════════════════════════════════════════════════════════════════════════
def plot_rf_power_sensitivity():
    sens_mhz_ma = np.linspace(100, 1000, 500)  # MHz/mA

    # Beta values to show
    betas_plot = [1.0, 1.5, beta_opt, 2.0]
    labels      = [
        r"$\beta = 1.0$",
        r"$\beta = 1.5$",
        fr"$\beta = {beta_opt:.4f}$ (optimal)",
        r"$\beta = 2.0$",
    ]
    colors_plot = [PALETTE["grey"], PALETTE["blue"], PALETTE["red"], PALETTE["purple"]]
    lws         = [1.6, 1.8, 2.6, 1.8]
    lss         = ["--", "--", "-", "--"]

    fig, ax = plt.subplots(figsize=FIGSIZE_W)

    # Feasible region shading: −5 to +15 dBm
    ax.axhspan(-5, 15, facecolor=PALETTE["green"], alpha=0.10, zorder=0,
               label="Feasible RF range (−5 to +15 dBm)")
    ax.axhline(-5,  color=PALETTE["green"], lw=1.0, ls=":", alpha=0.7)
    ax.axhline(15,  color=PALETTE["green"], lw=1.0, ls=":", alpha=0.7)
    ax.text(105, 15.4, "+15 dBm limit", fontsize=7.5, color=PALETTE["green"], va="bottom")
    ax.text(105, -5.8, "−5 dBm limit",  fontsize=7.5, color=PALETTE["green"], va="top")

    for beta_v, lbl, col, lw, ls in zip(betas_plot, labels, colors_plot, lws, lss):
        rf = np.array([compute_rf_power_dbm(beta_v, s) for s in sens_mhz_ma])
        ax.plot(sens_mhz_ma, rf, color=col, lw=lw, ls=ls, label=lbl, zorder=3)

    # Nominal design point: 500 MHz/mA, beta_opt
    nom_sens = 500.0
    nom_rf   = compute_rf_power_dbm(beta_opt, nom_sens)
    ax.plot(nom_sens, nom_rf, "o", ms=11, color=PALETTE["red"],
            markeredgecolor="white", markeredgewidth=1.5, zorder=6,
            label=f"Nominal design point\n({nom_sens:.0f} MHz/mA → {nom_rf:.1f} dBm)")
    ax.annotate(
        f"Design point\n{nom_sens:.0f} MHz/mA\n{nom_rf:.1f} dBm",
        xy=(nom_sens, nom_rf),
        xytext=(nom_sens + 90, nom_rf + 3.5),
        fontsize=9,
        color=PALETTE["red"],
        arrowprops=dict(arrowstyle="->", color=PALETTE["red"], lw=1.4,
                        connectionstyle="arc3,rad=-0.15"),
        bbox=dict(boxstyle="round,pad=0.35", fc="white", ec=PALETTE["red"],
                  alpha=0.90, lw=0.9),
    )

    ax.set_xlim(100, 1000)
    ax.set_ylim(-20, 30)
    ax.set_xlabel("VCSEL FM sensitivity (MHz/mA)", fontsize=12)
    ax.set_ylabel("Required RF drive power (dBm)", fontsize=12)
    ax.set_title("RF Drive Power vs VCSEL Sensitivity", fontsize=13, fontweight="bold")
    ax.legend(loc="upper right", fontsize=8.5, framealpha=0.9)
    ax.xaxis.set_minor_locator(ticker.MultipleLocator(50))
    ax.yaxis.set_minor_locator(ticker.MultipleLocator(2))

    fig.tight_layout()
    path = os.path.join(PLOTS_DIR, "rf_power_sensitivity.png")
    fig.savefig(path, dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {path}")


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("Generating plots for 01_vcsel_sideband …")
    print()
    print(f"  beta_opt           = {beta_opt:.6f}")
    print(f"  J1(beta_opt)       = {j1_opt:.6f}")
    print(f"  J0(beta_opt)       = {j0_opt:.6f}")
    print(f"  CPT sideband power = {sb_pwr:.2f}%")
    print(f"  Sideband spacing   = {spacing_ghz:.9f} GHz")
    print(f"  RF drive power     = {rf_dbm:.2f} dBm")
    print()

    plot_bessel_functions()
    plot_sideband_spectrum()
    plot_modulation_efficiency()
    plot_rf_power_sensitivity()

    print()
    print("All plots saved to plots/")
