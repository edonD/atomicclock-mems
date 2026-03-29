"""
geometry_sweep.py — MEMS cell geometry parameter space exploration
===================================================================
Analytical computation — Elmer FEM not available.
Shows bond stress vs alpha_L for the cavity diameter / depth design space,
highlighting which geometries satisfy all three constraints simultaneously:
  1. bond_stress < 3.3 MPa  (safety factor > 3x vs 10 MPa bond strength)
  2. alpha_L in [0.1, 3.0]  (sufficient but not opaque)
  3. resonance > 2000 Hz    (above MIL-STD-810G vibration band)

Selected design point: dia=1.5mm, depth=1.0mm (star marker).

Output: plots/geometry_sweep.png
"""

import math
import os
import sys

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    import numpy as np
    HAS_MPL = True
except ImportError:
    HAS_MPL = False
    print("WARNING: matplotlib not available -- printing table only, no plot written.")

# ---------------------------------------------------------------------------
# Physics models (same as fem_results.py — kept self-contained)
# ---------------------------------------------------------------------------

# Material constants
E_GLASS  = 63.0e9;  NU_GLASS = 0.20;  CTE_GLASS = 3.25e-6
E_SI     = 170.0e9; NU_SI    = 0.28;  CTE_SI    = 2.60e-6; RHO_SI = 2330.0
k_B      = 1.380649e-23
BOND_STRENGTH_MPA = 10.0

# Geometry constants
H_SI      = 1.0e-3        # Si wafer thickness [m]
H_GLASS   = 0.3e-3        # glass wafer thickness [m]
DIE_SIDE  = 3.0e-3        # die side [m]
P_N2_TORR = 75.0          # buffer gas pressure [Torr]
T_OP_C    = 85.0          # operating temp [degC]


def bond_stress_mpa(h_glass=H_GLASS, h_Si=H_SI, d_alpha=None, dT=125.0, Kt=1.5):
    """
    Modified Stoney formula (Freund & Suresh 2003).
    Returns max bond stress in MPa at cavity corner.
    Note: stress is independent of cavity geometry in this analytical model --
    it depends only on layer thicknesses and material properties.
    """
    if d_alpha is None:
        d_alpha = CTE_GLASS - CTE_SI   # 0.65e-6 /K
    sigma = (
        (E_GLASS / (1.0 - NU_GLASS))
        * (d_alpha * dT)
        * (h_glass * E_SI / (h_glass * E_GLASS + h_Si * E_SI))
    )
    return sigma * Kt / 1e6


def resonance_hz(a=DIE_SIDE, h_Si=H_SI):
    """
    Kirchhoff plate lowest-mode frequency [Hz].
    Conservative lower bound (treats full die as free plate, no glass constraint).
    """
    return (
        (math.pi * h_Si) / (2.0 * a**2)
        * math.sqrt(E_SI / (12.0 * RHO_SI * (1.0 - NU_SI**2)))
    )


def alpha_L(depth_mm, T_C=T_OP_C):
    """
    Beer-Lambert absorption product at temperature T_C [degC].
    Uses Antoine equation (Steck 2001) for Rb vapor pressure and
    N2 pressure broadening of Rb D1 (Rotondaro & Perram 1997, ~18 MHz/Torr).
    """
    T_K = T_C + 273.15
    P_Torr = 10.0 ** (7.5175 - 4132.0 / T_K)
    n_Rb   = P_Torr * 133.322 / (k_B * T_K)
    sigma_D1  = 1.1e-13                      # peak D1 cross-section [m^2]
    gamma_nat = 2.0 * math.pi * 5.746e6      # natural linewidth [rad/s]
    gamma_N2  = 2.0 * math.pi * 18.0e6 * P_N2_TORR  # N2 optical broadening [rad/s]
    sigma_eff = sigma_D1 * gamma_nat / (gamma_nat + gamma_N2)
    L = depth_mm * 1e-3
    return n_Rb * sigma_eff * L


# ---------------------------------------------------------------------------
# Parameter sweep
# ---------------------------------------------------------------------------
CAVITY_DIAMETERS = [1.0, 1.25, 1.5, 2.0]      # mm
CAVITY_DEPTHS    = [0.5, 0.75, 1.0, 1.5]       # mm

# Stress is the same for all geometries (only depends on layer thicknesses)
stress_mpa = bond_stress_mpa()
f1_hz      = resonance_hz()

print("=" * 78)
print("  geometry_sweep.py -- Analytical MEMS geometry parameter space")
print("=" * 78)
print()
print(f"  Bond stress (all geometries, h_glass=0.3mm, h_Si=1.0mm):")
print(f"    sigma_max = {stress_mpa:.4f} MPa  (Kt=1.5, dT=125 K)")
print(f"    safety_factor = {BOND_STRENGTH_MPA/stress_mpa:.2f}x")
print()
print(f"  Resonance frequency (all geometries, 3x3mm die):")
print(f"    f1 = {f1_hz:.0f} Hz")
print()
print("  Geometry sweep (bond_stress < 3.3 MPa AND alpha_L in [0.1, 3.0]):")
print()
print(f"  {'dia_mm':>7}  {'dep_mm':>7}  {'bond_MPa':>10}  {'sf':>5}  {'alpha_L':>9}  {'res_Hz':>10}  {'OK':>4}")
print("  " + "-" * 62)

all_data = []
for dia in CAVITY_DIAMETERS:
    for dep in CAVITY_DEPTHS:
        aL    = alpha_L(dep)
        sf    = BOND_STRENGTH_MPA / stress_mpa
        ok_stress  = stress_mpa < 3.3
        ok_optical = 0.1 <= aL <= 3.0
        ok_res     = f1_hz > 2000
        ok = ok_stress and ok_optical and ok_res
        all_data.append((dia, dep, stress_mpa, sf, aL, f1_hz, ok))
        flag = "PASS" if ok else "----"
        print(f"  {dia:7.2f}  {dep:7.2f}  {stress_mpa:10.4f}  {sf:5.2f}  {aL:9.4f}  {f1_hz:10.0f}  {flag:>4}")

print()
print("  Selected: dia=1.5mm, depth=1.0mm")
print("    - Central diameter; avoids Si wall stress concentrations from oversizing")
print("    - Depth 1.0mm: alpha_L=1.2, well within [0.1, 3.0], close to optimal ~1")
print("    - Bond stress 2.59 MPa < 3.3 MPa, safety factor 3.86x > 3x")
print("    - Resonance 448 kHz >> 2000 Hz vibration band")
print()

# ---------------------------------------------------------------------------
# Plot: bond stress vs alpha_L for different depths, marker per diameter
# ---------------------------------------------------------------------------
if not HAS_MPL:
    print("No plot written (matplotlib unavailable).")
    sys.exit(0)

os.makedirs("plots", exist_ok=True)

fig, axes = plt.subplots(1, 2, figsize=(13, 5))

# --- Left: scatter plot alpha_L vs bond_stress, coloured by depth ---
ax = axes[0]

depth_colors = {0.5: "#2196F3", 0.75: "#4CAF50", 1.0: "#FF9800", 1.5: "#E91E63"}
dia_markers  = {1.0: "o", 1.25: "s", 1.5: "^", 2.0: "D"}

for dia, dep, sm, sf, aL, f1, ok in all_data:
    ax.scatter(
        aL, sm,
        c=depth_colors[dep],
        marker=dia_markers[dia],
        s=100,
        edgecolors="black",
        linewidths=0.6,
        zorder=3,
    )
    ax.annotate(
        f"d={dep}",
        (aL, sm),
        textcoords="offset points",
        xytext=(5, 4),
        fontsize=7,
        color="gray",
    )

# Feasible region shading
ax.axhspan(0, 3.3, alpha=0.08, color="green", label="bond stress OK (<3.3 MPa)")
ax.axvspan(0.1, 3.0, alpha=0.08, color="blue", label="alpha_L OK (0.1-3.0)")

# Limit lines
ax.axhline(3.3, color="red", lw=1.2, ls="--", label="bond limit 3.3 MPa")
ax.axvline(0.1, color="navy", lw=1.0, ls=":", label="alpha_L min 0.1")
ax.axvline(3.0, color="navy", lw=1.0, ls=":", label="alpha_L max 3.0")

# Selected design point
sel_aL = alpha_L(1.0)
ax.scatter(
    sel_aL, stress_mpa,
    marker="*",
    s=350,
    c="gold",
    edgecolors="black",
    linewidths=1.2,
    zorder=5,
    label="Selected (dia=1.5, dep=1.0)",
)

# Legend for depth (colour) and diameter (marker)
depth_patches = [
    mpatches.Patch(color=c, label=f"depth={d} mm")
    for d, c in depth_colors.items()
]
dia_handles = [
    plt.Line2D([0], [0], marker=m, color="gray", linestyle="None",
               markersize=8, label=f"dia={d} mm")
    for d, m in dia_markers.items()
]
first_legend = ax.legend(
    handles=depth_patches + dia_handles,
    fontsize=7,
    loc="upper left",
    title="Geometry",
    title_fontsize=7,
)
ax.add_artist(first_legend)

ax.set_xlabel("alpha*L  (optical absorption product)", fontsize=10)
ax.set_ylabel("Bond stress [MPa]", fontsize=10)
ax.set_title("Bond Stress vs Optical Absorption\n(parameter sweep, all geometries)", fontsize=10)
ax.set_xlim(0, 4.2)
ax.set_ylim(0, 5.0)
ax.grid(True, alpha=0.3)

# Annotate feasible zone
ax.text(0.7, 0.5, "FEASIBLE\nZONE",
        fontsize=9, color="green", alpha=0.7, style="italic",
        ha="center", transform=ax.transAxes)

# --- Right: alpha_L vs cavity depth for each diameter (lines), with constraint bands ---
ax2 = axes[1]
depths_fine = np.linspace(0.3, 2.0, 200)

dia_line_colors = {1.0: "#2196F3", 1.25: "#4CAF50", 1.5: "#FF5722", 2.0: "#9C27B0"}
for dia in CAVITY_DIAMETERS:
    aLs = [alpha_L(d) for d in depths_fine]
    ax2.plot(depths_fine, aLs, color=dia_line_colors[dia],
             lw=2, label=f"dia = {dia} mm")
    # Note: alpha_L is independent of diameter in this model (optical path = depth only)
    # Lines overlap; the different diameters are shown for completeness
    break   # alpha_L depends only on depth, not diameter -- plot once

# All diameters give the same curve; show sweep points
for dep in CAVITY_DEPTHS:
    for dia in CAVITY_DIAMETERS:
        aL_val = alpha_L(dep)
        ax2.scatter(dep, aL_val,
                    color=dia_line_colors.get(dia, "gray"),
                    marker=dia_markers[dia], s=80,
                    edgecolors="black", linewidths=0.6, zorder=4)

ax2.axhspan(0.1, 3.0, alpha=0.10, color="green", label="target range [0.1, 3.0]")
ax2.axhline(0.1, color="navy", lw=1.2, ls="--", label="min alpha_L = 0.1")
ax2.axhline(3.0, color="red",  lw=1.2, ls="--", label="max alpha_L = 3.0")
ax2.axvline(1.0, color="gold", lw=2.0, ls="-",  label="selected depth 1.0 mm", alpha=0.8)

ax2.scatter(1.0, alpha_L(1.0), marker="*", s=350, c="gold",
            edgecolors="black", linewidths=1.2, zorder=5, label="Selected design")

ax2.set_xlabel("Cavity depth [mm]", fontsize=10)
ax2.set_ylabel("alpha*L  (optical absorption product)", fontsize=10)
ax2.set_title("alpha*L vs Cavity Depth\n(T = 85 degC, 75 Torr N2 buffer gas)", fontsize=10)
ax2.legend(fontsize=8, loc="upper left")
ax2.grid(True, alpha=0.3)

# Show depth sweep markers legend
dia_handles2 = [
    plt.Line2D([0], [0], marker=m, color="gray", linestyle="None",
               markersize=8, label=f"dia={d} mm")
    for d, m in dia_markers.items()
]
ax2.legend(
    handles=[
        mpatches.Patch(color="green", alpha=0.4, label="target range [0.1, 3.0]"),
        plt.Line2D([0], [0], color="navy", ls="--", lw=1.5, label="alpha_L min = 0.1"),
        plt.Line2D([0], [0], color="red", ls="--", lw=1.5, label="alpha_L max = 3.0"),
        plt.Line2D([0], [0], color="gold", lw=2.0, label="selected depth 1.0 mm"),
        plt.Line2D([0], [0], marker="*", color="gold", markersize=12,
                   linestyle="None", label="Selected point"),
    ] + dia_handles2,
    fontsize=7,
    loc="upper left",
)

fig.suptitle(
    "MEMS Atomic Clock Cell: Geometry Parameter Sweep\n"
    "Si 3x3x1.0mm + Borofloat 33 0.3mm top+bottom | Bond temp 350 degC | dT_op = 125 K",
    fontsize=10,
)
fig.tight_layout(rect=[0, 0, 1, 0.93])

outpath = os.path.join("plots", "geometry_sweep.png")
fig.savefig(outpath, dpi=150, bbox_inches="tight")
print(f"  Plot saved to: {outpath}")
plt.close(fig)
