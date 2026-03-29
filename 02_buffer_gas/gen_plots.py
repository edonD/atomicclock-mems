"""
gen_plots.py — Buffer Gas Module Visualisations
================================================
Generates four publication-quality plots for 02_buffer_gas.
All physics computed directly here; does NOT import sim.py.

Physics reference
-----------------
  Vanier & Audoin, "The Quantum Physics of Atomic Frequency Standards" (1989)
  Steck, "Rubidium 87 D Line Data" (2021)
  Knappe et al., NIST (2004)

Correct Dicke narrowing model (diffusion-limited):
  γ_diff(P) = D0 / (d²)  where  D0_eff ∝ 1/P
  i.e.  γ_diff(P) = γ_diff_ref / P   with γ_diff_ref = 63_375 Hz·Torr
  (calibrated so γ_diff at P=1 Torr matches the transit linewidth at ~1.5mm cell)

Compare to BROKEN model in sim.py:
  γ_Dicke = γ_transit² / (γ_transit + γ_pressure)
  This formula is monotonically INCREASING for all P > 0, never produces a minimum.
"""

import os
import sys
# Ensure stdout handles Unicode on Windows (cp1252 terminal)
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf-16"):
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

import numpy as np
import matplotlib
matplotlib.use("Agg")          # headless — no display needed
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec

# ── Output directory ─────────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PLOT_DIR   = os.path.join(SCRIPT_DIR, "plots")
os.makedirs(PLOT_DIR, exist_ok=True)

DPI = 150

# ── Physical constants ───────────────────────────────────────────────
kB   = 1.380649e-23          # J/K
M_RB = 87 * 1.66053906660e-27  # kg

# ── Model parameters ────────────────────────────────────────────────
K_BROAD_HZ_TORR  = 10.8          # Hz/Torr  — ground-state CPT coherence (NOT optical!)
K_SHIFT_KHZ_TORR = -6.7          # kHz/Torr — clock frequency shift
K_SHIFT_TCOEFF   = -6.7e3 / (85 + 273.15)  # Hz/Torr per K (d(k_shift P)/dT approx)

GAMMA_WALL       = 300.0         # Hz  — residual wall-collision decoherence
GAMMA_TRANSIT_FREE = 62_700.0    # Hz  — free-flight transit linewidth (1.5mm cell, 85°C)

# Diffusion-model Dicke narrowing constant:
#   γ_diff(P) = GAMMA_DIFF_REF / P
# GAMMA_DIFF_REF calibrated so γ_diff(1 Torr) ≈ γ_transit_free
#   At 75 Torr: γ_diff ≈ 63_375/75 ≈ 845 Hz
GAMMA_DIFF_REF   = 63_375.0      # Hz·Torr

CAVITY_D_MM      = 1.5           # mm
T_OP_C           = 85.0          # °C
P_OPT            = 75.0          # Torr  — correct physics optimum

# ── Pressure axis ────────────────────────────────────────────────────
P_arr = np.linspace(0.5, 150.0, 2000)   # Torr

# ── Correct physics functions ────────────────────────────────────────

def gamma_diff(P):
    """Diffusion-limited Dicke narrowing linewidth [Hz]."""
    return GAMMA_DIFF_REF / P

def gamma_pressure(P):
    """Pressure broadening contribution [Hz]."""
    return K_BROAD_HZ_TORR * P

def gamma_total(P):
    """Total CPT linewidth with correct Dicke model [Hz]."""
    return gamma_diff(P) + gamma_pressure(P) + GAMMA_WALL

def rb_vapor_density(T_celsius):
    """Rb number density [m⁻³] — Steck 2021 coefficients."""
    T_K = T_celsius + 273.15
    if np.isscalar(T_celsius):
        if T_K < 312.0:
            log10_P = 7.0464 - 4040.0 / T_K
        else:
            log10_P = 7.5175 - 4132.0 / T_K
    else:
        log10_P = np.where(T_K < 312.0,
                           7.0464 - 4040.0 / T_K,
                           7.5175 - 4132.0 / T_K)
    P_Torr = 10.0 ** log10_P
    P_Pa   = P_Torr * 133.322
    return P_Pa / (kB * T_K)

def rb_vapor_pressure_torr(T_celsius):
    """Rb vapor pressure [Torr] — Steck 2021."""
    T_K = T_celsius + 273.15
    if np.isscalar(T_celsius):
        if T_K < 312.0:
            return 10.0 ** (7.0464 - 4040.0 / T_K)
        else:
            return 10.0 ** (7.5175 - 4132.0 / T_K)
    else:
        return np.where(T_K < 312.0,
                        10.0 ** (7.0464 - 4040.0 / T_K),
                        10.0 ** (7.5175 - 4132.0 / T_K))


# ════════════════════════════════════════════════════════════════════
# PLOT 1 — Dicke narrowing physics
# ════════════════════════════════════════════════════════════════════

def plot_dicke_narrowing():
    fig, ax = plt.subplots(figsize=(10, 6))

    gd  = gamma_diff(P_arr)
    gp  = gamma_pressure(P_arr)
    gt  = gamma_total(P_arr)

    # ── find minimum of total ──────────────────────────────────────
    idx_min = np.argmin(gt)
    P_min   = P_arr[idx_min]
    g_min   = gt[idx_min]

    # ── shaded regimes ─────────────────────────────────────────────
    ax.axvspan(P_arr[0],  P_min, alpha=0.08, color="steelblue",
               label="_Dicke narrowing regime")
    ax.axvspan(P_min, P_arr[-1], alpha=0.08, color="tomato",
               label="_Pressure broadening regime")

    # Regime text
    ax.text(P_min * 0.45, g_min * 3.8, "← Dicke narrowing\n    dominates",
            color="steelblue", fontsize=10, ha="center", va="center",
            fontweight="semibold")
    ax.text(P_min * 1.65, g_min * 3.8, "Pressure broadening\n    dominates →",
            color="tomato", fontsize=10, ha="center", va="center",
            fontweight="semibold")

    # ── curves ────────────────────────────────────────────────────
    ax.axhline(GAMMA_TRANSIT_FREE, color="gray", ls="--", lw=1.6,
               label=f"γ_transit (free flight) = {GAMMA_TRANSIT_FREE/1e3:.1f} kHz")
    ax.plot(P_arr, gd, color="steelblue", lw=2.0,
            label=r"γ$_{diff}$(P) = 63 375 / P   [Dicke, diffusion model]")
    ax.plot(P_arr, gp, color="tomato", lw=2.0,
            label=r"γ$_{pressure}$(P) = 10.8 × P   [pressure broadening]")
    ax.plot(P_arr, gt, color="black", lw=2.5,
            label=r"γ$_{total}$(P) = γ$_{diff}$ + γ$_{pressure}$ + γ$_{wall}$")

    # ── optimal pressure marker ────────────────────────────────────
    ax.axvline(P_min, color="goldenrod", lw=1.8, ls="-.",
               label=f"P_opt ≈ {P_min:.0f} Torr  (minimum)")
    ax.scatter([P_min], [g_min], s=100, zorder=6, color="goldenrod",
               edgecolors="black", lw=1.0)
    ax.annotate(f"Minimum\n{g_min/1e3:.2f} kHz\n@ {P_min:.0f} Torr",
                xy=(P_min, g_min),
                xytext=(P_min + 18, g_min + 600),
                arrowprops=dict(arrowstyle="->", color="goldenrod", lw=1.5),
                fontsize=9, color="goldenrod",
                bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="goldenrod", alpha=0.9))

    # ── wall contribution reference ────────────────────────────────
    ax.axhline(GAMMA_WALL, color="mediumseagreen", ls=":", lw=1.4,
               label=f"γ_wall = {GAMMA_WALL:.0f} Hz  (residual)")

    # ── cosmetics ─────────────────────────────────────────────────
    ax.set_xlim(0, 152)
    ax.set_ylim(0, min(GAMMA_TRANSIT_FREE * 1.35, gt.max() * 1.25))
    ax.set_xlabel("N₂ Buffer Gas Pressure (Torr)", fontsize=12)
    ax.set_ylabel("CPT Linewidth (Hz)", fontsize=12)
    ax.set_title(
        "Buffer Gas Optimisation — Competing Dicke Narrowing vs Pressure Broadening\n"
        r"(K$_{ground}$ = 10.8 Hz/Torr for ground-state CPT coherence; "
        r"K$_{opt}$ = 10.8 kHz/Torr is the optical line — different!)",
        fontsize=11)
    ax.legend(loc="upper right", fontsize=8.5, framealpha=0.9)
    ax.yaxis.set_major_formatter(
        matplotlib.ticker.FuncFormatter(lambda x, _: f"{x/1000:.0f} kHz" if x >= 1000 else f"{x:.0f} Hz"))
    ax.grid(True, alpha=0.3, which="both")
    ax.set_axisbelow(True)

    # ── inset: zoomed near minimum ─────────────────────────────────
    from mpl_toolkits.axes_grid1.inset_locator import inset_axes
    axins = inset_axes(ax, width="38%", height="38%", loc="upper left",
                       bbox_to_anchor=(0.03, 0.97, 1, 1),
                       bbox_transform=ax.transAxes)
    zoom_mask = (P_arr >= 20) & (P_arr <= 130)
    axins.plot(P_arr[zoom_mask], gt[zoom_mask] / 1e3, color="black", lw=2)
    axins.scatter([P_min], [g_min / 1e3], s=60, zorder=6,
                  color="goldenrod", edgecolors="black", lw=0.8)
    axins.axvline(P_min, color="goldenrod", lw=1.2, ls="-.")
    axins.set_xlabel("Pressure (Torr)", fontsize=7)
    axins.set_ylabel("kHz", fontsize=7)
    axins.set_title("Zoomed: 20–130 Torr", fontsize=7.5)
    axins.tick_params(labelsize=7)
    axins.grid(True, alpha=0.25)

    fig.tight_layout()
    path = os.path.join(PLOT_DIR, "dicke_narrowing_physics.png")
    fig.savefig(path, dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {path}")


# ════════════════════════════════════════════════════════════════════
# PLOT 2 — Rb vapor pressure & number density
# ════════════════════════════════════════════════════════════════════

def plot_rb_vapor_pressure():
    T_arr_C = np.linspace(20, 120, 800)
    T_arr_K = T_arr_C + 273.15

    # Vapor pressure (Torr) — handle solid/liquid split
    P_vap = rb_vapor_pressure_torr(T_arr_C)
    n_arr = rb_vapor_density(T_arr_C)

    # Values at 85°C
    P_85  = rb_vapor_pressure_torr(85.0)
    n_85  = rb_vapor_density(85.0)

    # Melting point: 39°C (312 K)
    T_melt_C = 312.0 - 273.15   # ≈ 38.85°C

    fig, ax1 = plt.subplots(figsize=(10, 6))
    color_pres = "steelblue"
    color_dens = "tomato"

    # ── solid / liquid split lines ────────────────────────────────
    mask_solid  = T_arr_C < T_melt_C
    mask_liquid = T_arr_C >= T_melt_C

    l1_s, = ax1.semilogy(T_arr_C[mask_solid],  P_vap[mask_solid],
                          color=color_pres, lw=2.2, ls="-",
                          label="Rb vapor pressure (solid, Steck 2021)")
    l1_l, = ax1.semilogy(T_arr_C[mask_liquid], P_vap[mask_liquid],
                          color=color_pres, lw=2.2, ls="--",
                          label="Rb vapor pressure (liquid, Steck 2021)")

    # Phase transition marker
    ax1.axvline(T_melt_C, color="purple", lw=1.5, ls=":",
                label=f"Melting point ≈ {T_melt_C:.0f}°C (312 K)")
    ax1.annotate("Rb melting\npoint (39°C)",
                 xy=(T_melt_C, P_vap[np.argmin(np.abs(T_arr_C - T_melt_C))]),
                 xytext=(T_melt_C - 14, 1e-6),
                 arrowprops=dict(arrowstyle="->", color="purple", lw=1.2),
                 fontsize=8.5, color="purple",
                 bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="purple", alpha=0.85))

    # ── operating temperature ─────────────────────────────────────
    ax1.axvline(85.0, color="goldenrod", lw=1.8, ls="-.",
                label="T_op = 85°C (cell operating point)")
    ax1.scatter([85.0], [P_85], s=90, zorder=6, color="goldenrod",
                edgecolors="black", lw=1.0)
    ax1.annotate(
        f"P_Rb = {P_85:.2e} Torr\nn_Rb = {n_85:.2e} m⁻³",
        xy=(85.0, P_85),
        xytext=(95.0, P_85 * 12),
        arrowprops=dict(arrowstyle="->", color="goldenrod", lw=1.2),
        fontsize=8.5, color="black",
        bbox=dict(boxstyle="round,pad=0.35", fc="lightyellow",
                  ec="goldenrod", alpha=0.95))

    ax1.set_xlabel("Cell Temperature (°C)", fontsize=12)
    ax1.set_ylabel("Vapor Pressure (Torr)", fontsize=12, color=color_pres)
    ax1.tick_params(axis="y", labelcolor=color_pres)

    # ── right axis: number density ────────────────────────────────
    ax2 = ax1.twinx()
    ax2.semilogy(T_arr_C[mask_solid],  n_arr[mask_solid],
                 color=color_dens, lw=2.2, ls="-",
                 label="n_Rb (solid phase)")
    ax2.semilogy(T_arr_C[mask_liquid], n_arr[mask_liquid],
                 color=color_dens, lw=2.2, ls="--",
                 label="n_Rb (liquid phase)")
    ax2.scatter([85.0], [n_85], s=90, zorder=6, color=color_dens,
                edgecolors="black", lw=1.0)
    ax2.set_ylabel("Number Density (m⁻³)", fontsize=12, color=color_dens)
    ax2.tick_params(axis="y", labelcolor=color_dens)

    # Combined legend
    lines  = [l1_s, l1_l,
               plt.Line2D([0], [0], color="purple",  lw=1.5, ls=":"),
               plt.Line2D([0], [0], color="goldenrod", lw=1.8, ls="-."),
               plt.Line2D([0], [0], color=color_dens, lw=2.2, ls="--")]
    labels = ["Vapor pressure (solid Rb)", "Vapor pressure (liquid Rb)",
               "Melting point (39°C)", "T_op = 85°C",
               "Number density n_Rb"]
    ax1.legend(lines, labels, loc="upper left", fontsize=8.5, framealpha=0.9)

    ax1.set_xlim(20, 120)
    ax1.set_ylim(1e-8, 1e-1)
    ax2.set_ylim(ax1.get_ylim()[0] * 133.322 / (kB * (85 + 273.15)) * 100,
                 1e22)
    ax2.set_ylim(1e13, 1e22)

    ax1.set_title("Rb-87 Vapor Pressure and Number Density (Steck 2021)\n"
                  "Liquid phase above 39°C; operating temperature 85°C for CSAC", fontsize=11)
    ax1.grid(True, alpha=0.3, which="both", axis="both")
    ax1.set_axisbelow(True)

    fig.tight_layout()
    path = os.path.join(PLOT_DIR, "rb_vapor_pressure.png")
    fig.savefig(path, dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {path}")


# ════════════════════════════════════════════════════════════════════
# PLOT 3 — Pressure shift vs N2 pressure
# ════════════════════════════════════════════════════════════════════

def plot_pressure_shift():
    P_plot = np.linspace(0, 150, 1000)

    # Nominal: δ(P) = -6.7 kHz/Torr × P
    delta_nom = K_SHIFT_KHZ_TORR * P_plot   # kHz

    # Temperature sensitivity: at T+1°C, N2 pressure rises by P × dT/T_K
    T_K   = T_OP_C + 273.15
    dT    = 1.0
    delta_Tplus1 = K_SHIFT_KHZ_TORR * P_plot * (T_K + dT) / T_K   # kHz
    delta_delta  = delta_Tplus1 - delta_nom                          # kHz (small)

    fig, ax = plt.subplots(figsize=(10, 6))

    # ── optimal pressure band (20–100 Torr) ──────────────────────
    ax.axvspan(20, 100, alpha=0.12, color="steelblue",
               label="Optimal pressure range (20–100 Torr)")
    ax.axhspan(K_SHIFT_KHZ_TORR * 100, K_SHIFT_KHZ_TORR * 20,
               alpha=0.07, color="steelblue")

    # ── curves ────────────────────────────────────────────────────
    ax.plot(P_plot, delta_nom, color="steelblue", lw=2.5,
            label=f"δ(P) = {K_SHIFT_KHZ_TORR} kHz/Torr × P")
    ax.fill_between(P_plot, delta_nom, delta_Tplus1,
                    alpha=0.25, color="tomato",
                    label="ΔT = +1°C shift  (due to N₂ expansion)")
    ax.plot(P_plot, delta_Tplus1, color="tomato", lw=1.6, ls="--",
            label="δ(P, T+1°C)")

    # ── mark P=20 Torr and P=100 Torr ────────────────────────────
    for P_mark, ls_s in [(20, ":"), (100, ":")]:
        d_mark = K_SHIFT_KHZ_TORR * P_mark
        ax.axvline(P_mark, color="steelblue", lw=1.2, ls=ls_s)
        ax.axhline(d_mark, color="steelblue", lw=1.0, ls=ls_s, alpha=0.6)
        ax.scatter([P_mark], [d_mark], s=60, color="steelblue",
                   edgecolors="black", lw=0.8, zorder=5)
        ax.annotate(f"{d_mark:.0f} kHz",
                    xy=(P_mark, d_mark),
                    xytext=(P_mark + 5, d_mark + 25),
                    fontsize=8, color="steelblue")

    # ── P_opt marker at 75 Torr ────────────────────────────────────
    d_opt = K_SHIFT_KHZ_TORR * P_OPT
    ax.axvline(P_OPT, color="goldenrod", lw=1.8, ls="-.",
               label=f"P_opt = {P_OPT:.0f} Torr → δ = {d_opt:.0f} kHz")
    ax.scatter([P_OPT], [d_opt], s=90, color="goldenrod",
               edgecolors="black", lw=1.0, zorder=6)

    # ── annotation box ────────────────────────────────────────────
    ax.annotate(
        "Compensated by tuning f_mod\n"
        "— must be within PLL range\n"
        f"Range: {K_SHIFT_KHZ_TORR*20:.0f} to {K_SHIFT_KHZ_TORR*100:.0f} kHz",
        xy=(60, K_SHIFT_KHZ_TORR * 60),
        xytext=(80, K_SHIFT_KHZ_TORR * 30),
        arrowprops=dict(arrowstyle="->", color="black", lw=1.2),
        fontsize=9, color="black",
        bbox=dict(boxstyle="round,pad=0.4", fc="lightyellow",
                  ec="goldenrod", alpha=0.95))

    ax.set_xlim(0, 152)
    ax.set_xlabel("N₂ Pressure (Torr)", fontsize=12)
    ax.set_ylabel("Clock Frequency Shift (kHz)", fontsize=12)
    ax.set_title("N₂ Pressure Shift of Clock Frequency\n"
                 "k_shift = −6.7 kHz/Torr (Vanier & Audoin). "
                 "Servo loop absorbs shift — but PLL must cover full range.", fontsize=11)
    ax.legend(loc="lower left", fontsize=9, framealpha=0.9)
    ax.grid(True, alpha=0.3)
    ax.set_axisbelow(True)

    # ── zero-line ─────────────────────────────────────────────────
    ax.axhline(0, color="black", lw=0.8, alpha=0.5)

    fig.tight_layout()
    path = os.path.join(PLOT_DIR, "pressure_shift.png")
    fig.savefig(path, dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {path}")


# ════════════════════════════════════════════════════════════════════
# PLOT 4 — Linewidth budget pie at P_opt
# ════════════════════════════════════════════════════════════════════

def plot_linewidth_budget_pie():
    # Components at P_opt = 75 Torr
    g_diff  = GAMMA_DIFF_REF / P_OPT       # ≈ 845 Hz
    g_press = K_BROAD_HZ_TORR * P_OPT      # = 810 Hz
    g_wall  = GAMMA_WALL                   # = 300 Hz
    g_total = g_diff + g_press + g_wall    # ≈ 1955 Hz

    labels  = [
        f"γ_Dicke (diffusion)\n{g_diff:.0f} Hz",
        f"γ_pressure\n{g_press:.0f} Hz",
        f"γ_wall\n{g_wall:.0f} Hz",
    ]
    sizes   = [g_diff, g_press, g_wall]
    colors  = ["steelblue", "tomato", "mediumseagreen"]
    explode = (0.04, 0.04, 0.08)

    fig, (ax_pie, ax_bar) = plt.subplots(1, 2, figsize=(12, 6),
                                          gridspec_kw={"width_ratios": [1.1, 0.9]})

    # ── Pie chart ─────────────────────────────────────────────────
    wedges, texts, autotexts = ax_pie.pie(
        sizes, labels=labels, colors=colors, explode=explode,
        autopct=lambda p: f"{p:.1f}%\n({p/100*g_total:.0f} Hz)",
        startangle=120, pctdistance=0.68,
        textprops={"fontsize": 9.5},
        wedgeprops={"linewidth": 1.2, "edgecolor": "white"})

    for at in autotexts:
        at.set_fontsize(8.5)
        at.set_color("white")
        at.set_fontweight("bold")

    ax_pie.set_title(
        f"CPT Linewidth Budget at P_opt = {P_OPT:.0f} Torr\n"
        f"Total ≈ {g_total:.0f} Hz ≈ {g_total/1e3:.1f} kHz",
        fontsize=11, pad=15)

    # ── Bar chart breakdown ────────────────────────────────────────
    component_labels = ["γ_Dicke\n(diffusion)", "γ_pressure\n(N₂ dephasing)", "γ_wall\n(residual)"]
    bar_vals = [g_diff, g_press, g_wall]
    bars = ax_bar.barh(component_labels, bar_vals, color=colors,
                       edgecolor="white", linewidth=1.2, height=0.55)

    # Value labels
    for bar, val in zip(bars, bar_vals):
        ax_bar.text(val + 12, bar.get_y() + bar.get_height() / 2,
                    f"{val:.0f} Hz  ({val/g_total*100:.1f}%)",
                    va="center", fontsize=9.5)

    # Total line
    ax_bar.axvline(g_total, color="black", lw=2, ls="--", alpha=0.6)
    ax_bar.text(g_total + 15, 2.35, f"Total\n{g_total:.0f} Hz",
                fontsize=9, color="black", va="center",
                bbox=dict(boxstyle="round,pad=0.2", fc="lightyellow",
                          ec="gray", alpha=0.8))

    ax_bar.set_xlabel("Linewidth Contribution (Hz)", fontsize=11)
    ax_bar.set_title("Component Breakdown", fontsize=11)
    ax_bar.set_xlim(0, g_total * 1.45)
    ax_bar.grid(True, axis="x", alpha=0.35)
    ax_bar.set_axisbelow(True)
    ax_bar.tick_params(labelsize=9.5)

    # ── Comparison note ────────────────────────────────────────────
    fig.text(0.5, 0.01,
             f"Free-flight transit linewidth (no buffer gas): {GAMMA_TRANSIT_FREE/1e3:.1f} kHz   "
             f"→   Buffer gas reduces linewidth by {GAMMA_TRANSIT_FREE/g_total:.0f}×",
             ha="center", fontsize=9.5, style="italic", color="dimgray")

    fig.tight_layout(rect=[0, 0.05, 1, 1])
    path = os.path.join(PLOT_DIR, "linewidth_budget_pie.png")
    fig.savefig(path, dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {path}")


# ════════════════════════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════════════════════════

def main():
    # Print a quick numerical summary first
    print("\n── Buffer Gas Physics Summary ─────────────────────────────")

    P_min_idx = np.argmin(gamma_total(P_arr))
    P_min_val = P_arr[P_min_idx]
    g_min_val = gamma_total(P_arr)[P_min_idx]
    print(f"  Correct γ_diff(P) = {GAMMA_DIFF_REF}/P Hz  →  "
          f"P_opt = {P_min_val:.1f} Torr,  γ_total_min = {g_min_val:.0f} Hz "
          f"({g_min_val/1e3:.2f} kHz)")
    print(f"  Rb density at 85°C: {rb_vapor_density(85.0):.3e} m⁻³")
    print(f"  Vapor pressure at 85°C: {rb_vapor_pressure_torr(85.0):.3e} Torr")
    print(f"  Pressure shift at P_opt={P_OPT} Torr: "
          f"{K_SHIFT_KHZ_TORR * P_OPT:.0f} kHz")
    print()

    print("── Generating plots ───────────────────────────────────────")
    plot_dicke_narrowing()
    plot_rb_vapor_pressure()
    plot_pressure_shift()
    plot_linewidth_budget_pie()

    print()
    print("── All plots saved to plots/ ──────────────────────────────")
    print(f"   {os.path.join(SCRIPT_DIR, 'plots/')}")
    print()


if __name__ == "__main__":
    main()
