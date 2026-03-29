"""
gen_plots.py — Illustrative / theory plots for 00_atomic_model
==============================================================
Generates four publication-quality figures from the analytical physics
described in program.md.  Does NOT require QuTiP or sim.py to be
implemented.  All curves come from closed-form expressions.

Output: plots/
    energy_levels.png
    cpt_lineshape_theory.png
    density_matrix_structure.png
    laser_power_sweep_theory.png
"""

import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.patches as FancyArrow
from matplotlib.patches import FancyArrowPatch, Rectangle
from matplotlib.lines import Line2D
import matplotlib.gridspec as gridspec

os.makedirs("plots", exist_ok=True)

# ── Colour palette ────────────────────────────────────────────────────────────
C_BLUE   = "#1f4e79"
C_RED    = "#c00000"
C_GREEN  = "#375623"
C_PURPLE = "#7030a0"
C_ORANGE = "#c55a11"
C_GOLD   = "#bf8f00"
C_LIGHT  = "#bdd7ee"
C_GREY   = "#595959"
C_BG     = "#f8f9fa"

plt.rcParams.update({
    "font.family":      "DejaVu Sans",
    "font.size":        11,
    "axes.titlesize":   13,
    "axes.labelsize":   12,
    "legend.fontsize":  10,
    "xtick.labelsize":  10,
    "ytick.labelsize":  10,
    "figure.facecolor": "white",
    "axes.facecolor":   "white",
    "axes.edgecolor":   "#333333",
    "axes.linewidth":   1.2,
    "grid.color":       "#dddddd",
    "grid.linewidth":   0.8,
    "lines.linewidth":  2.0,
})

# ─────────────────────────────────────────────────────────────────────────────
# PLOT 1 — Rb-87 Energy Level Diagram (Λ system)
# ─────────────────────────────────────────────────────────────────────────────

def plot_energy_levels():
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.set_xlim(0, 10)
    ax.set_ylim(-0.5, 10)
    ax.axis("off")
    fig.patch.set_facecolor("white")

    # ── Level geometry ────────────────────────────────────────────────────────
    # Ground state 5S₁/₂
    y_gs_centre = 1.5
    hfs_gap     = 0.9          # visual gap representing 6.8347 GHz
    y_F1  = y_gs_centre - hfs_gap / 2   # F=1  lower
    y_F2  = y_gs_centre + hfs_gap / 2   # F=2  upper

    # Excited state 5P₁/₂  (D1 line)
    y_ex_centre = 7.5
    excited_gap = 0.35
    y_Fp1 = y_ex_centre - excited_gap / 2   # F'=1  lower
    y_Fp2 = y_ex_centre + excited_gap / 2   # F'=2  upper

    x_left  = 2.0
    x_right = 8.0
    x_mid   = (x_left + x_right) / 2

    lw_main  = 3.0
    lw_fine  = 2.0
    lw_arrow = 2.4

    # ── Draw levels ───────────────────────────────────────────────────────────
    def draw_level(y, x0, x1, color, lw, label, label_side="right", offset=0.15):
        ax.plot([x0, x1], [y, y], color=color, lw=lw, solid_capstyle="round", zorder=3)
        if label:
            if label_side == "right":
                ax.text(x1 + 0.15, y + offset, label, fontsize=10.5,
                        color=color, va="center", ha="left")
            else:
                ax.text(x0 - 0.15, y + offset, label, fontsize=10.5,
                        color=color, va="center", ha="right")

    # Ground F=1
    draw_level(y_F1, x_left, x_mid - 0.3, C_BLUE, lw_main,
               r"$|1\rangle = |5S_{1/2}, F=1, m_F=0\rangle$", offset=0.0)
    # Ground F=2
    draw_level(y_F2, x_left, x_mid - 0.3, C_BLUE, lw_main,
               r"$|2\rangle = |5S_{1/2}, F=2, m_F=0\rangle$", offset=0.0)
    # Excited F'=1
    draw_level(y_Fp1, x_mid + 0.3, x_right, C_RED, lw_fine,
               r"$F'=1$", label_side="right", offset=0.0)
    # Excited F'=2
    draw_level(y_Fp2, x_mid + 0.3, x_right, C_RED, lw_fine,
               r"$F'=2$", label_side="right", offset=0.0)

    # ── State manifold brackets / labels ─────────────────────────────────────
    bx = 1.4
    ax.annotate("", xy=(bx, y_F2 + 0.1), xytext=(bx, y_F1 - 0.1),
                arrowprops=dict(arrowstyle="<->", color=C_BLUE, lw=1.5))
    ax.text(bx - 0.12, y_gs_centre, "6.8347 GHz\nhyperfine", fontsize=9,
            color=C_BLUE, ha="right", va="center", linespacing=1.4)

    ax.text(x_mid - 0.35, y_F1 - 0.55, r"$5S_{1/2}$ ground state",
            fontsize=11, color=C_BLUE, ha="center", style="italic",
            weight="bold")

    bx2 = x_right + 0.9
    ax.annotate("", xy=(bx2, y_Fp2 + 0.08), xytext=(bx2, y_Fp1 - 0.08),
                arrowprops=dict(arrowstyle="<->", color=C_RED, lw=1.5))
    ax.text(bx2 + 0.12, y_ex_centre, "~815 MHz", fontsize=9,
            color=C_RED, ha="left", va="center")

    ax.text(x_mid + 0.35, y_ex_centre + 0.65, r"$5P_{1/2}$ excited state",
            fontsize=11, color=C_RED, ha="center", style="italic",
            weight="bold")

    # ── D1 line label (vertical) ──────────────────────────────────────────────
    y_arrow_top = y_Fp1
    y_arrow_bot = y_F2
    ax.annotate("", xy=(x_mid + 0.0, y_arrow_top - 0.05),
                xytext=(x_mid + 0.0, y_arrow_bot + 0.05),
                arrowprops=dict(arrowstyle="<->", color=C_GREY, lw=1.2,
                                linestyle="dashed"))
    ax.text(x_mid + 0.22, (y_arrow_top + y_arrow_bot) / 2,
            "D1 line\n794.979 nm\n377.107 THz",
            fontsize=8.5, color=C_GREY, ha="left", va="center", linespacing=1.5)

    # ── Lambda arrows (Ω₁ and Ω₂) ────────────────────────────────────────────
    arrow_kw = dict(arrowstyle="-|>", lw=lw_arrow,
                    mutation_scale=18, zorder=5)

    x_omega1_bot = x_left + 0.6
    x_omega2_bot = x_left + 1.8
    x_apex       = x_mid - 0.05

    # Ω₁: from F=1 → excited F'=1
    ax.annotate("", xy=(x_apex, y_Fp1 - 0.05),
                xytext=(x_omega1_bot, y_F1 + 0.05),
                arrowprops=dict(**arrow_kw, color=C_PURPLE))
    # Ω₂: from F=2 → excited F'=1
    ax.annotate("", xy=(x_apex + 0.18, y_Fp1 - 0.05),
                xytext=(x_omega2_bot, y_F2 + 0.05),
                arrowprops=dict(**arrow_kw, color=C_GREEN))

    # Labels on arrows
    ax.text(x_omega1_bot - 0.35, (y_F1 + y_Fp1) / 2 + 0.2,
            r"$\Omega_1$", fontsize=13, color=C_PURPLE, ha="center",
            fontstyle="italic", weight="bold")
    ax.text(x_omega2_bot + 0.35, (y_F2 + y_Fp1) / 2 + 0.1,
            r"$\Omega_2$", fontsize=13, color=C_GREEN, ha="center",
            fontstyle="italic", weight="bold")

    # ── Dark state label with box ─────────────────────────────────────────────
    xd = x_left + 1.2
    yd = y_gs_centre - 0.08
    ax.annotate(
        r"$|D\rangle = \frac{\Omega_2\,|1\rangle - \Omega_1\,|2\rangle}"
        r"{\sqrt{|\Omega_1|^2+|\Omega_2|^2}}$",
        xy=(xd, yd), xytext=(xd - 0.5, yd - 1.3),
        fontsize=10, color="white", ha="center",
        arrowprops=dict(arrowstyle="->", color=C_GOLD, lw=1.5),
        bbox=dict(boxstyle="round,pad=0.4", facecolor=C_GOLD,
                  edgecolor=C_GOLD, alpha=0.92)
    )

    # ── "CPT dark state — no absorption" annotation ──────────────────────────
    ax.text(5.0, 0.1, "CPT Dark State  |D⟩  —  atoms do not absorb light",
            fontsize=10, color=C_GOLD, ha="center",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="#fff9e6",
                      edgecolor=C_GOLD, alpha=0.9))

    # ── Λ system label ────────────────────────────────────────────────────────
    ax.text(5.0, 9.6,
            "Rb-87 Three-Level Λ System  (D1 line, 794.979 nm)",
            fontsize=13, ha="center", color=C_BLUE, weight="bold")
    ax.text(5.0, 9.15,
            r"Ground-state coherence $\rho_{12}$ drives CPT dark state at "
            r"$\omega_1 - \omega_2 = \omega_{\rm hfs}$",
            fontsize=10, ha="center", color=C_GREY)

    # ── Legend ────────────────────────────────────────────────────────────────
    legend_elements = [
        Line2D([0], [0], color=C_BLUE,   lw=3,   label=r"$5S_{1/2}$ ground state levels"),
        Line2D([0], [0], color=C_RED,    lw=2,   label=r"$5P_{1/2}$ excited state levels"),
        Line2D([0], [0], color=C_PURPLE, lw=2.5, label=r"$\Omega_1$ optical field (F=1 → F′=1)"),
        Line2D([0], [0], color=C_GREEN,  lw=2.5, label=r"$\Omega_2$ optical field (F=2 → F′=1)"),
    ]
    ax.legend(handles=legend_elements, loc="upper right",
              framealpha=0.92, edgecolor="#aaaaaa", fontsize=9.5)

    plt.tight_layout()
    fig.savefig("plots/energy_levels.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("  [saved]  plots/energy_levels.png")


# ─────────────────────────────────────────────────────────────────────────────
# PLOT 2 — Theoretical CPT lineshape
# ─────────────────────────────────────────────────────────────────────────────

def lorentzian_cpt(delta_R_khz, gamma_cpt_khz, contrast):
    """
    A(δ_R) = A_bg × (1 - C / (1 + (2·δ_R / Γ_CPT)²))
    Returns normalised absorption (A_bg = 1).
    """
    return 1.0 - contrast / (1.0 + (2.0 * delta_R_khz / gamma_cpt_khz) ** 2)


def plot_cpt_lineshape():
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.set_facecolor(C_BG)

    delta_R = np.linspace(-50, 50, 4000)   # kHz

    cases = [
        # (gamma_12_hz, gamma_cpt_khz, contrast, color, label)
        (300,  0.60, 0.085, C_BLUE,   r"$\gamma_{12}$ = 300 Hz  (narrow, high contrast)"),
        (1000, 2.00, 0.055, C_PURPLE, r"$\gamma_{12}$ = 1000 Hz  (medium)"),
        (3000, 6.00, 0.025, C_RED,    r"$\gamma_{12}$ = 3000 Hz  (broad, low contrast)"),
    ]

    for gamma_12, gamma_cpt, C_val, color, label in cases:
        A = lorentzian_cpt(delta_R, gamma_cpt, C_val)
        ax.plot(delta_R, A, color=color, lw=2.5, label=label)

    # ── Detailed annotations for the medium curve ─────────────────────────────
    g_ann   = 2.00
    C_ann   = 0.055
    A_curve = lorentzian_cpt(delta_R, g_ann, C_ann)

    baseline  = 1.0
    peak_dip  = lorentzian_cpt(0, g_ann, C_ann)
    half_max  = baseline - (baseline - peak_dip) / 2.0
    half_idx  = np.where(np.diff((A_curve < half_max).astype(int)))[0]

    if len(half_idx) >= 2:
        xl = delta_R[half_idx[0]]
        xr = delta_R[half_idx[-1] + 1]
        # FWHM bracket
        ax.annotate("", xy=(xr, half_max), xytext=(xl, half_max),
                    arrowprops=dict(arrowstyle="<->", color=C_PURPLE, lw=1.8))
        ax.text(0, half_max + 0.008, f"FWHM ≈ {g_ann:.1f} kHz",
                ha="center", va="bottom", fontsize=9.5, color=C_PURPLE)

    # Contrast arrow
    ax.annotate("", xy=(18, peak_dip), xytext=(18, baseline),
                arrowprops=dict(arrowstyle="<->", color=C_GREEN, lw=1.8))
    ax.text(19.5, (baseline + peak_dip) / 2,
            f"Contrast\n≈ {C_ann*100:.1f}%",
            fontsize=9, color=C_GREEN, va="center", ha="left")

    # Baseline dotted line
    ax.axhline(1.0, color=C_GREY, lw=1.0, linestyle="--", alpha=0.6, label="Baseline (far from resonance)")

    # Transparency dip label
    ax.axvline(0, color=C_GREY, lw=0.8, linestyle=":", alpha=0.5)
    ax.text(0, 0.862, r" $\delta_R = 0$" + "\nCPT resonance",
            ha="center", va="top", fontsize=9, color=C_GREY,
            bbox=dict(boxstyle="round,pad=0.25", facecolor="white",
                      edgecolor=C_GREY, alpha=0.85))

    # Trade-off annotation
    ax.text(-48, 0.872,
            "Linewidth ↑ with $\\gamma_{12}$ (broader)\nContrast ↓ with $\\gamma_{12}$ (shallower dip)",
            fontsize=9, color=C_GREY,
            bbox=dict(boxstyle="round,pad=0.35", facecolor="#fff5f5",
                      edgecolor=C_RED, alpha=0.9))

    ax.set_xlabel(r"Raman detuning  $\delta_R$  (kHz)", fontsize=12)
    ax.set_ylabel("Normalised absorption  A(δ_R)", fontsize=12)
    ax.set_title("Theoretical CPT Resonance — Transparency Dip vs Raman Detuning\n"
                 r"Lorentzian model:  $A(\delta_R) = A_{\rm bg}\left(1 - "
                 r"\dfrac{C}{1+(2\delta_R/\Gamma_{\rm CPT})^2}\right)$",
                 fontsize=12)
    ax.set_xlim(-50, 50)
    ax.set_ylim(0.84, 1.05)
    ax.legend(loc="upper right", framealpha=0.92, edgecolor="#aaaaaa")
    ax.grid(True, alpha=0.5)

    # Target box
    ax.text(32, 0.852,
            "Targets:\nLinewidth < 5 kHz\nContrast  > 3%",
            fontsize=9.5, color=C_GREEN, va="bottom",
            bbox=dict(boxstyle="round,pad=0.4", facecolor="#f0fff0",
                      edgecolor=C_GREEN, alpha=0.9))

    plt.tight_layout()
    fig.savefig("plots/cpt_lineshape_theory.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("  [saved]  plots/cpt_lineshape_theory.png")


# ─────────────────────────────────────────────────────────────────────────────
# PLOT 3 — Density matrix structure (3×3 grid + Lindblad diagram)
# ─────────────────────────────────────────────────────────────────────────────

def plot_density_matrix():
    fig = plt.figure(figsize=(14, 6))
    gs  = gridspec.GridSpec(1, 2, width_ratios=[1.1, 1], wspace=0.08)

    # ── Left panel: 3×3 grid ─────────────────────────────────────────────────
    ax_dm = fig.add_subplot(gs[0])
    ax_dm.set_xlim(-0.2, 3.2)
    ax_dm.set_ylim(-0.2, 3.2)
    ax_dm.set_aspect("equal")
    ax_dm.axis("off")
    ax_dm.set_facecolor("white")

    labels = [
        [r"$\rho_{11}$", r"$\rho_{12}$", r"$\rho_{13}$"],
        [r"$\rho_{21}$", r"$\rho_{22}$", r"$\rho_{23}$"],
        [r"$\rho_{31}$", r"$\rho_{32}$", r"$\rho_{33}$"],
    ]
    sublabels = [
        ["pop. F=1",    "gnd coherence",  "opt. coh."],
        ["gnd coh.*",   "pop. F=2",       "opt. coh."],
        ["opt. coh.*",  "opt. coh.*",     "pop. excited"],
    ]

    def elem_color(i, j):
        if i == j:
            return C_ORANGE       # populations
        if (i, j) in [(0, 1), (1, 0)]:
            return C_PURPLE       # ground-state coherence — CPT key
        return C_BLUE             # optical coherences

    def elem_alpha(i, j):
        if (i, j) in [(0, 1), (1, 0)]:
            return 0.90
        if i == j:
            return 0.75
        return 0.55

    cell = 1.0
    pad  = 0.04
    for i in range(3):
        for j in range(3):
            yi = 2 - i   # flip so row 0 is at top
            xj = j
            c  = elem_color(i, j)
            a  = elem_alpha(i, j)
            rect = Rectangle((xj + pad, yi + pad),
                              cell - 2*pad, cell - 2*pad,
                              facecolor=c, alpha=a,
                              edgecolor="white", linewidth=2.5,
                              zorder=2)
            ax_dm.add_patch(rect)
            ax_dm.text(xj + cell/2, yi + cell * 0.62, labels[i][j],
                       ha="center", va="center", fontsize=14,
                       color="white", weight="bold", zorder=3)
            ax_dm.text(xj + cell/2, yi + cell * 0.30, sublabels[i][j],
                       ha="center", va="center", fontsize=7.5,
                       color="white", alpha=0.95, zorder=3)

    # Special border for ρ₁₂ (CPT key element)
    rect_key = Rectangle((0 + pad, 1 + pad),
                          cell - 2*pad, cell - 2*pad,
                          facecolor="none", edgecolor=C_GOLD,
                          linewidth=3.5, linestyle="-", zorder=4)
    ax_dm.add_patch(rect_key)
    ax_dm.text(0 + cell/2, 1 + cell + 0.15,
               "← CPT key element", fontsize=8.5, color=C_GOLD,
               ha="center", va="bottom", weight="bold")

    # Row/col labels
    state_labels = [r"$\langle 1|$", r"$\langle 2|$", r"$\langle 3|$"]
    ket_labels   = [r"$|1\rangle$", r"$|2\rangle$", r"$|3\rangle$"]
    for k in range(3):
        ax_dm.text(-0.12, 2.5 - k, state_labels[k], ha="right", va="center",
                   fontsize=12, color=C_GREY, weight="bold")
        ax_dm.text(0.5 + k, 3.12, ket_labels[k], ha="center", va="bottom",
                   fontsize=12, color=C_GREY, weight="bold")

    ax_dm.text(1.5, -0.14,
               r"$\rho = \sum_{ij} \rho_{ij}\,|i\rangle\langle j|$, "
               r"$\,\mathrm{Tr}(\rho)=1$",
               ha="center", va="top", fontsize=10, color=C_GREY)

    # Legend for colours
    leg_items = [
        mpatches.Patch(color=C_ORANGE, alpha=0.85, label="Populations (diagonal)"),
        mpatches.Patch(color=C_PURPLE, alpha=0.90, label=r"Ground-state coherence $\rho_{12}$ — CPT signal"),
        mpatches.Patch(color=C_BLUE,   alpha=0.65, label="Optical coherences"),
    ]
    ax_dm.legend(handles=leg_items, loc="lower center", bbox_to_anchor=(1.5, -0.19),
                 ncol=3, fontsize=8.5, framealpha=0.92, edgecolor="#aaaaaa")

    ax_dm.set_title("3×3 Density Matrix  $\\rho$", fontsize=13, pad=12,
                    color=C_BLUE, weight="bold")

    # ── Right panel: Lindblad diagram ────────────────────────────────────────
    ax_lb = fig.add_subplot(gs[1])
    ax_lb.set_xlim(0, 8)
    ax_lb.set_ylim(0, 9)
    ax_lb.axis("off")
    ax_lb.set_facecolor("white")

    # Three levels
    yl1 = 1.8   # |1⟩
    yl2 = 3.0   # |2⟩
    yl3 = 7.0   # |3⟩
    xl_l = 1.5
    xl_r = 4.5

    for y, lbl, col in [(yl1, r"$|1\rangle$  F=1", C_BLUE),
                         (yl2, r"$|2\rangle$  F=2", C_BLUE),
                         (yl3, r"$|3\rangle$  5P$_{1/2}$", C_RED)]:
        ax_lb.plot([xl_l, xl_r], [y, y], color=col, lw=3, solid_capstyle="round")
        ax_lb.text(xl_r + 0.15, y, lbl, va="center", fontsize=10, color=col)

    arw = dict(arrowstyle="-|>", mutation_scale=14, lw=1.8)

    # L1: |3⟩ → |1⟩
    ax_lb.annotate("", xy=(xl_l + 0.4, yl1 + 0.08),
                   xytext=(xl_l + 0.4, yl3 - 0.08),
                   arrowprops=dict(**arw, color=C_ORANGE))
    ax_lb.text(xl_l + 0.05, (yl1 + yl3)/2,
               r"$L_1 = \sqrt{\Gamma/2}\,|1\rangle\langle3|$" + "\n" + r"$\Gamma = 2\pi\times 5.746$ MHz",
               fontsize=8, color=C_ORANGE, ha="right", va="center", linespacing=1.5)

    # L2: |3⟩ → |2⟩
    ax_lb.annotate("", xy=(xl_r - 0.4, yl2 + 0.08),
                   xytext=(xl_r - 0.4, yl3 - 0.08),
                   arrowprops=dict(**arw, color=C_RED))
    ax_lb.text(xl_r + 2.2, (yl2 + yl3)/2,
               r"$L_2 = \sqrt{\Gamma/2}\,|2\rangle\langle3|$" + "\n" + "spontaneous decay",
               fontsize=8, color=C_RED, ha="right", va="center", linespacing=1.5)

    # L3 + L4: ground decoherence ↔
    ax_lb.annotate("", xy=(xl_l + 1.4, yl2 - 0.08),
                   xytext=(xl_l + 1.4, yl1 + 0.08),
                   arrowprops=dict(**arw, color=C_PURPLE))
    ax_lb.annotate("", xy=(xl_l + 1.8, yl1 + 0.08),
                   xytext=(xl_l + 1.8, yl2 - 0.08),
                   arrowprops=dict(**arw, color=C_PURPLE))
    ax_lb.text(3.0, (yl1 + yl2)/2 + 0.05,
               r"$L_{3,4} = \sqrt{\gamma_{12}}\,|1\rangle\langle2|,\,|2\rangle\langle1|$"
               + "\n" + r"transit / wall / buffer-gas  $\gamma_{12}$: 300–3000 Hz",
               fontsize=8, color=C_PURPLE, ha="left", va="center", linespacing=1.5)

    ax_lb.set_title("Lindblad Collapse Operators", fontsize=13, pad=12,
                    color=C_BLUE, weight="bold")
    ax_lb.text(4.0, 0.3,
               r"Master eq.:  $\dot{\rho} = -(i/\hbar)[H,\rho]"
               r" + \sum_k (L_k\rho L_k^\dagger - \frac{1}{2}L_k^\dagger L_k\rho"
               r" - \frac{1}{2}\rho L_k^\dagger L_k)$",
               ha="center", va="bottom", fontsize=8.5, color=C_GREY)

    plt.suptitle("Rb-87 CPT — Density Matrix Model", fontsize=14,
                 color=C_BLUE, weight="bold", y=1.01)
    plt.tight_layout()
    fig.savefig("plots/density_matrix_structure.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("  [saved]  plots/density_matrix_structure.png")


# ─────────────────────────────────────────────────────────────────────────────
# PLOT 4 — Laser power sweep (Vanier formula)
# ─────────────────────────────────────────────────────────────────────────────

def plot_laser_power_sweep():
    """
    Vanier formula:  Δν ≈ (1/π)(γ₁₂ + Ω²/(2Γ))
    Contrast model:  C ≈ C₀ / (1 + (Ω/Ω_sat)²)

    Γ        = 5.746 MHz (natural linewidth)
    γ₁₂      = 1000 Hz  (nominal ground decoherence)
    C₀       = 0.08     (low-power contrast limit)
    Ω_sat    = 0.35 Γ   (saturation Rabi frequency)
    """
    Gamma_MHz = 5.746        # MHz
    Gamma     = Gamma_MHz    # units: MHz for Ω as well
    gamma_12  = 1000e-6      # MHz  (= 1 kHz)

    omega_ratio = np.linspace(0.01, 2.0, 800)   # Ω/Γ
    Omega_MHz   = omega_ratio * Gamma            # Ω in MHz

    # ── Vanier linewidth (kHz) ────────────────────────────────────────────────
    lw_kHz = (1.0 / np.pi) * (gamma_12 * 1e6 + (Omega_MHz ** 2 / (2 * Gamma)) * 1e6) / 1e3
    # NOTE: full formula in Hz → convert to kHz

    C0       = 0.085
    Omega_sat = 0.35
    contrast = C0 / (1.0 + (omega_ratio / Omega_sat) ** 2) * 100   # %

    # Figure of merit: contrast / linewidth (want to maximise)
    fom = contrast / lw_kHz

    # Find optimal point (peak of FOM, excluding very small Ω where lw is at floor)
    opt_idx = np.argmax(fom[5:]) + 5
    opt_ratio   = omega_ratio[opt_idx]
    opt_lw      = lw_kHz[opt_idx]
    opt_contrast = contrast[opt_idx]

    fig, ax1 = plt.subplots(figsize=(12, 6))
    ax1.set_facecolor(C_BG)
    ax2 = ax1.twinx()

    # ── Linewidth curve ───────────────────────────────────────────────────────
    l1, = ax1.plot(omega_ratio, lw_kHz, color=C_BLUE, lw=2.5,
                   label="CPT linewidth  Δν (kHz)")
    ax1.axhline(5.0, color=C_BLUE, lw=1.2, linestyle="--", alpha=0.55,
                label="Linewidth limit  5 kHz")

    # ── Contrast curve ────────────────────────────────────────────────────────
    l2, = ax2.plot(omega_ratio, contrast, color=C_RED, lw=2.5,
                   label="CPT contrast  C (%)")
    ax2.axhline(3.0, color=C_RED, lw=1.2, linestyle="--", alpha=0.55,
                label="Contrast floor  3%")

    # ── Figure of merit (scaled to fit) ──────────────────────────────────────
    fom_scaled = fom / fom.max() * 6.0   # scale to fit on linewidth axis
    l3, = ax1.plot(omega_ratio, fom_scaled, color=C_GREEN, lw=2.0,
                   linestyle="-.", label="FOM  C/Δν (scaled)")

    # ── Optimal point ─────────────────────────────────────────────────────────
    ax1.axvline(opt_ratio, color=C_GOLD, lw=2.0, linestyle=":", alpha=0.85)
    ax1.scatter([opt_ratio], [opt_lw], color=C_GOLD, s=90, zorder=6)
    ax2.scatter([opt_ratio], [opt_contrast], color=C_GOLD, s=90, zorder=6,
                marker="D")
    ax1.text(opt_ratio + 0.04, opt_lw + 0.3,
             f"Optimal  Ω/Γ ≈ {opt_ratio:.2f}\n"
             f"Δν ≈ {opt_lw:.2f} kHz\n"
             f"C ≈ {opt_contrast:.1f}%",
             fontsize=9, color=C_GOLD,
             bbox=dict(boxstyle="round,pad=0.35", facecolor="#fffde7",
                       edgecolor=C_GOLD, alpha=0.92))

    # ── Power broadening regime label ─────────────────────────────────────────
    ax1.text(1.4, 9.5, "Power-broadening\nregime  Ω > Γ/√2",
             fontsize=9, color=C_GREY, ha="center",
             bbox=dict(boxstyle="round,pad=0.3", facecolor="white",
                       edgecolor=C_GREY, alpha=0.85))
    ax1.annotate("", xy=(1.1, 8.8), xytext=(1.25, 9.3),
                 arrowprops=dict(arrowstyle="->", color=C_GREY, lw=1.3))

    # ── Vanier formula annotation ─────────────────────────────────────────────
    ax1.text(0.05, 10.8,
             r"Vanier (1989):  $\Delta\nu \approx \frac{1}{\pi}"
             r"\!\left(\gamma_{12} + \frac{\Omega^2}{2\Gamma}\right)$",
             fontsize=10, color=C_BLUE,
             bbox=dict(boxstyle="round,pad=0.4", facecolor="#e8f4fd",
                       edgecolor=C_BLUE, alpha=0.9))

    # ── Axes ──────────────────────────────────────────────────────────────────
    ax1.set_xlabel(r"Rabi frequency ratio  $\Omega / \Gamma$", fontsize=12)
    ax1.set_ylabel("CPT linewidth  Δν  (kHz)", fontsize=12, color=C_BLUE)
    ax2.set_ylabel("CPT contrast  C  (%)", fontsize=12, color=C_RED)
    ax1.tick_params(axis="y", labelcolor=C_BLUE)
    ax2.tick_params(axis="y", labelcolor=C_RED)
    ax1.set_xlim(0, 2.0)
    ax1.set_ylim(0, 13)
    ax2.set_ylim(0, 10)
    ax1.grid(True, alpha=0.45)
    ax1.set_title(
        "Laser Power Optimisation — CPT Linewidth vs Contrast Trade-off\n"
        r"$\gamma_{12} = 1000$ Hz,  $\Gamma = 2\pi \times 5.746$ MHz",
        fontsize=12)

    lines  = [l1, l2, l3,
              Line2D([0], [0], color=C_BLUE, lw=1.2, linestyle="--"),
              Line2D([0], [0], color=C_RED,  lw=1.2, linestyle="--"),
              Line2D([0], [0], color=C_GOLD, lw=2.0, linestyle=":",
                     marker="o", markersize=6)]
    llabels = ["Linewidth Δν (kHz)", "Contrast C (%)", "FOM = C/Δν (scaled)",
               "Linewidth limit 5 kHz", "Contrast floor 3%", "Optimal operating point"]
    ax1.legend(lines, llabels, loc="upper right",
               framealpha=0.92, edgecolor="#aaaaaa", fontsize=9)

    plt.tight_layout()
    fig.savefig("plots/laser_power_sweep_theory.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("  [saved]  plots/laser_power_sweep_theory.png")


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("\nGenerating 00_atomic_model theory plots …\n")
    print("1/4  energy_levels.png")
    plot_energy_levels()

    print("2/4  cpt_lineshape_theory.png")
    plot_cpt_lineshape()

    print("3/4  density_matrix_structure.png")
    plot_density_matrix()

    print("4/4  laser_power_sweep_theory.png")
    plot_laser_power_sweep()

    print("\nAll plots saved to plots/\n")
