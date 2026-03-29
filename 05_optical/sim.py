"""
SIM: 05_optical
Wave 2 — Optical Path Simulation

Simulates Gaussian beam propagation from VCSEL through the MEMS atomic clock
optical stack (glass window -> Rb cell -> glass window -> gap -> photodetector),
computes Beer-Lambert absorption with N2 pressure broadening, window Fresnel
losses, and shot-noise-limited SNR.
"""

import numpy as np
import os
import sys

# ── Load geometry from 03_mems_geometry if available ─────────────────────────
try:
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "03_mems_geometry"))
    from fem_results import RESULTS as GEO  # type: ignore
    cavity_diameter_mm  = GEO["cavity_diameter_mm"]
    cavity_depth_mm     = GEO["cavity_depth_mm"]
    glass_thickness_mm  = GEO["glass_thickness_mm"]
    alpha_L_base        = GEO.get("alpha_L", 0.22)
except Exception:
    cavity_diameter_mm  = 1.5   # mm  (Knappe NIST 2004)
    cavity_depth_mm     = 1.0   # mm
    glass_thickness_mm  = 0.3   # mm
    alpha_L_base        = 0.22  # Beer-Lambert α·L at 85°C, 1 mm cavity (module 03)

# ── Load N2 pressure from 02_buffer_gas ──────────────────────────────────────
try:
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "02_buffer_gas"))
    import sim as _bg  # type: ignore
    P_N2_Torr = _bg.RESULTS.get("optimal_n2_pressure_torr", 75.0)
except Exception:
    P_N2_Torr = 75.0   # Torr  default

# ── Physical constants ────────────────────────────────────────────────────────
LAMBDA_M    = 794.979e-9   # m  Rb D1 line
E_CHARGE    = 1.602e-19    # C
GAMMA_NAT   = 2 * np.pi * 5.746e6   # rad/s  natural linewidth

# Optical pressure broadening coefficient for Rb D1 by N2
# Published range: 10–20 MHz/Torr; use midpoint 15 MHz/Torr
K_OPT_MHZ_TORR = 15.0     # MHz/Torr

# ── VCSEL & detector parameters ───────────────────────────────────────────────
W0_M            = 4e-6     # m  VCSEL emitter waist
INPUT_POWER_UW  = 200.0    # µW
N_GLASS         = 1.47     # Borosilicate refractive index
FRESNEL_LOSS    = 0.04     # per glass-air surface (normal incidence, n=1.47)
N_SURFACES      = 4        # 2 windows × 2 surfaces each
R_PD            = 0.5      # A/W  Si photodiode responsivity at 795 nm
BW_HZ           = 100.0    # Hz  lock-in detection bandwidth
GAP_M           = 0.5e-3   # m   gap from top window to photodetector


# ═══════════════════════════════════════════════════════════════════════════════
# 1. Gaussian Beam Propagation
# ═══════════════════════════════════════════════════════════════════════════════

def gaussian_beam_propagation():
    """
    Propagate a Gaussian beam (waist w0 at VCSEL facet) through the optical
    stack.  Each glass window is replaced by its equivalent free-space length
    z_eff = t / n.  The cell interior and detector gap are true free-space
    segments.

    Returns a dict with beam radii at key planes and a (z, w) trace for plotting.
    """
    w0   = W0_M
    lam  = LAMBDA_M
    z_R  = np.pi * w0**2 / lam      # Rayleigh range

    # Segment optical-path lengths (m)
    z_win   = (glass_thickness_mm * 1e-3) / N_GLASS   # one glass window
    z_cell  = cavity_depth_mm * 1e-3                   # Rb cell (free space)
    z_gap   = GAP_M

    # Cumulative z positions (optical equivalent distances from VCSEL waist)
    z_bottom_win_in  = 0.0
    z_bottom_win_out = z_win
    z_cell_in        = z_bottom_win_out
    z_cell_out       = z_cell_in + z_cell
    z_top_win_in     = z_cell_out
    z_top_win_out    = z_top_win_in + z_win
    z_detector       = z_top_win_out + z_gap
    z_total          = z_detector

    def w_at(z):
        return w0 * np.sqrt(1.0 + (z / z_R)**2)

    # Beam diameters at key planes
    w_cell_entrance  = w_at(z_cell_in)
    w_cell_exit      = w_at(z_cell_out)
    w_detector       = w_at(z_total)

    # Clipping check: full beam diameter (2w) < 90% of cavity diameter
    no_clipping = (2.0 * w_cell_exit * 1e3) < (0.9 * cavity_diameter_mm)

    # Fine-grained trace for plotting (physical z in metres)
    # Map back: physical z = z_eff × n inside glass, z = z_eff in free space.
    # For the plot we use physical distance from VCSEL face.
    phys_bottom_win = glass_thickness_mm * 1e-3
    phys_cell       = phys_bottom_win + cavity_depth_mm * 1e-3
    phys_top_win    = phys_cell + glass_thickness_mm * 1e-3
    phys_detector   = phys_top_win + GAP_M

    # Build trace: propagate each physical segment using its effective z
    # optical-equivalent z accumulates for w(z), physical z is for the x-axis
    n_pts      = 500
    phys_z_arr = np.linspace(0.0, phys_detector, n_pts)
    opt_z_arr  = np.zeros(n_pts)
    for i, pz in enumerate(phys_z_arr):
        if pz <= phys_bottom_win:
            # inside bottom glass window
            opt_z_arr[i] = pz / N_GLASS
        elif pz <= phys_cell:
            # inside Rb cell (free space)
            opt_z_arr[i] = z_bottom_win_out + (pz - phys_bottom_win)
        elif pz <= phys_top_win:
            # inside top glass window
            opt_z_arr[i] = z_top_win_in + (pz - phys_cell) / N_GLASS
        else:
            # gap to photodetector
            opt_z_arr[i] = z_top_win_out + (pz - phys_top_win)

    w_trace = w0 * np.sqrt(1.0 + (opt_z_arr / z_R)**2)

    return {
        "w0_um":                         w0 * 1e6,
        "rayleigh_range_mm":             z_R * 1e3,
        "z_total_mm":                    z_total * 1e3,
        "w_at_cell_entrance_um":         w_cell_entrance * 1e6,
        "w_at_cell_exit_um":             w_cell_exit * 1e6,
        "w_at_detector_um":              w_detector * 1e6,
        "beam_diameter_at_cell_exit_mm": 2.0 * w_cell_exit * 1e3,
        "no_clipping":                   bool(no_clipping),
        # Boundary positions for plotting (physical, mm)
        "boundaries_mm": {
            "vcsel":            0.0,
            "bottom_win_out":   phys_bottom_win * 1e3,
            "cell_exit":        phys_cell * 1e3,
            "top_win_out":      phys_top_win * 1e3,
            "detector":         phys_detector * 1e3,
        },
        # Arrays for plotting
        "plot_z_mm":  phys_z_arr * 1e3,
        "plot_w_um":  w_trace * 1e6,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# 2. Optical Absorption with N2 Pressure Broadening
# ═══════════════════════════════════════════════════════════════════════════════

def compute_absorption(P_N2):
    """
    Compute effective α·L with N2 optical pressure broadening.

    Γ_total = Γ_nat + 2π × k_opt_MHz/Torr × P_N2_Torr × 1e6 rad/s
    α_L_eff = α_L_base × (Γ_nat / Γ_total)

    Returns alpha_L_effective and component linewidths.
    """
    gamma_nat      = GAMMA_NAT
    gamma_pressure = 2.0 * np.pi * K_OPT_MHZ_TORR * P_N2 * 1e6   # rad/s
    gamma_total    = gamma_nat + gamma_pressure

    alpha_L_eff    = alpha_L_base * (gamma_nat / gamma_total)

    return {
        "alpha_L_base":              alpha_L_base,
        "alpha_L_effective":         alpha_L_eff,
        "gamma_nat_mhz":             gamma_nat / (2 * np.pi * 1e6),
        "gamma_pressure_mhz":        gamma_pressure / (2 * np.pi * 1e6),
        "gamma_total_mhz":           gamma_total / (2 * np.pi * 1e6),
        "broadening_factor":         gamma_total / gamma_nat,
        "absorption_pct":            (1.0 - np.exp(-alpha_L_eff)) * 100.0,
        "absorption_pct_no_buffer":  (1.0 - np.exp(-alpha_L_base)) * 100.0,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# 3. Power Budget
# ═══════════════════════════════════════════════════════════════════════════════

def compute_power_budget(alpha_L_eff):
    """
    Compute optical power at each stage:
      VCSEL → bottom window → cell absorption → top window → detector

    Window loss: Fresnel reflection at each glass-air interface.
      T_surface = 1 − 0.04 = 0.96   (normal incidence, n=1.47)
      4 surfaces total → T_windows = 0.96^4
    """
    T_surface  = 1.0 - FRESNEL_LOSS                # per surface
    T_windows  = T_surface ** N_SURFACES            # all 4 surfaces
    T_cell     = np.exp(-alpha_L_eff)               # Beer-Lambert

    P_vcsel          = INPUT_POWER_UW
    P_after_win_in   = P_vcsel   * (T_surface ** 2)   # 2 surfaces, bottom window
    P_after_cell     = P_after_win_in * T_cell
    P_after_win_out  = P_after_cell  * (T_surface ** 2)   # 2 surfaces, top window
    P_detector       = P_after_win_out                    # no further loss in gap

    return {
        "P_vcsel_uw":           P_vcsel,
        "P_after_win_in_uw":    P_after_win_in,
        "P_after_cell_uw":      P_after_cell,
        "P_after_win_out_uw":   P_after_win_out,
        "P_detector_uw":        P_detector,
        "window_transmission_pct": T_windows * 100.0,
        "cell_transmission_pct":   T_cell    * 100.0,
        "total_transmission_pct":  (P_detector / P_vcsel) * 100.0,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# 4. Shot-Noise SNR
# ═══════════════════════════════════════════════════════════════════════════════

def compute_snr(P_detector_uw):
    """
    Shot-noise limited SNR.

    I_pd  = R_pd × P_detector              [A]
    σ_shot= sqrt(2 × e × I_pd × BW)       [A / sqrt(Hz)]
    SNR   = I_pd / σ_shot = sqrt(I_pd / (2 × e × BW))
    """
    I_pd = R_PD * P_detector_uw * 1e-6    # A  (P in µW → W)
    snr  = np.sqrt(I_pd / (2.0 * E_CHARGE * BW_HZ))

    return {
        "photodiode_current_ua": I_pd * 1e6,
        "snr":                   snr,
        "shot_noise_floor_pa":   np.sqrt(2.0 * E_CHARGE * I_pd * BW_HZ) * 1e12,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# 5. Run all computations
# ═══════════════════════════════════════════════════════════════════════════════

_beam   = gaussian_beam_propagation()
_absorb = compute_absorption(P_N2_Torr)
_power  = compute_power_budget(_absorb["alpha_L_effective"])
_snr    = compute_snr(_power["P_detector_uw"])

RESULTS = {
    # Beam geometry
    "beam_diameter_at_cell_exit_mm": _beam["beam_diameter_at_cell_exit_mm"],
    "no_clipping":                   _beam["no_clipping"],
    "rayleigh_range_mm":             _beam["rayleigh_range_mm"],
    "beam_waist_at_detector_um":     _beam["w_at_detector_um"],

    # Absorption
    "alpha_L_base":                  _absorb["alpha_L_base"],
    "alpha_L_effective":             _absorb["alpha_L_effective"],
    "absorption_pct":                _absorb["absorption_pct"],
    "pressure_broadening_factor":    _absorb["broadening_factor"],

    # Power budget
    "optical_power_at_detector_uw":  _power["P_detector_uw"],
    "window_transmission_pct":       _power["window_transmission_pct"],
    "cell_transmission_pct":         _power["cell_transmission_pct"],
    "total_transmission_pct":        _power["total_transmission_pct"],

    # SNR
    "snr":                           _snr["snr"],
    "photodiode_current_ua":         _snr["photodiode_current_ua"],

    # Inputs used
    "P_N2_Torr":                     P_N2_Torr,
    "input_power_uw":                INPUT_POWER_UW,
    "cavity_diameter_mm":            cavity_diameter_mm,
    "cavity_depth_mm":               cavity_depth_mm,
}


# ═══════════════════════════════════════════════════════════════════════════════
# 6. Generate plots
# ═══════════════════════════════════════════════════════════════════════════════

def _make_plots():
    """Generate beam_propagation.png and power_budget.png into plots/."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import matplotlib.patches as mpatches
    except ImportError:
        print("  [WARN] matplotlib not available — skipping plots")
        return

    plots_dir = os.path.join(os.path.dirname(__file__), "plots")
    os.makedirs(plots_dir, exist_ok=True)

    bnd = _beam["boundaries_mm"]

    # ── Plot 1: beam propagation ──────────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(9, 4))

    z  = _beam["plot_z_mm"]
    w  = _beam["plot_w_um"]
    ax.plot(z,  w, color="#1f77b4", lw=2, label="Beam radius w(z)")
    ax.plot(z, -w, color="#1f77b4", lw=2)
    ax.fill_between(z, -w, w, alpha=0.15, color="#1f77b4")

    # Cavity diameter limit
    half_cav = (cavity_diameter_mm * 1e3) / 2.0   # µm
    ax.axhline( half_cav, color="red",   lw=1.2, ls="--", label=f"Cavity wall (±{cavity_diameter_mm/2:.2f} mm)")
    ax.axhline(-half_cav, color="red",   lw=1.2, ls="--")
    ax.axhline( 0.9 * half_cav, color="orange", lw=1.0, ls=":",
                label="90% no-clip limit")
    ax.axhline(-0.9 * half_cav, color="orange", lw=1.0, ls=":")

    # Region shading for optical elements
    ax.axvspan(0,                        bnd["bottom_win_out"], alpha=0.10, color="green",  label="Bottom glass")
    ax.axvspan(bnd["bottom_win_out"],    bnd["cell_exit"],      alpha=0.10, color="violet", label="Rb cell")
    ax.axvspan(bnd["cell_exit"],         bnd["top_win_out"],    alpha=0.10, color="green",  label="Top glass")
    ax.axvspan(bnd["top_win_out"],       bnd["detector"],       alpha=0.10, color="gray",   label="Gap")

    # Boundary lines
    for label, xval in [
        ("Bottom\nwindow", bnd["bottom_win_out"]),
        ("Cell\nexit",     bnd["cell_exit"]),
        ("Top\nwindow",    bnd["top_win_out"]),
        ("Detector",       bnd["detector"]),
    ]:
        ax.axvline(xval, color="gray", lw=0.8, ls=":")
        ax.text(xval, ax.get_ylim()[1] * 0.5 if ax.get_ylim()[1] > 0 else 1,
                label, ha="center", va="bottom", fontsize=7, color="gray")

    ax.set_xlabel("Physical distance from VCSEL (mm)")
    ax.set_ylabel("Beam radius w(z) (µm)")
    ax.set_title(
        f"Gaussian Beam Propagation — VCSEL to Photodetector\n"
        f"w₀ = {W0_M*1e6:.0f} µm,  z_R = {_beam['rayleigh_range_mm']:.2f} mm,  "
        f"P_N2 = {P_N2_Torr:.1f} Torr,  "
        f"w(exit) = {_beam['w_at_cell_exit_um']:.1f} µm  "
        f"({'OK' if _beam['no_clipping'] else 'CLIP!'})"
    )
    ax.legend(fontsize=7, loc="upper left", ncol=2)
    ax.set_ylim(-half_cav * 1.15, half_cav * 1.15)
    fig.tight_layout()
    fig.savefig(os.path.join(plots_dir, "beam_propagation.png"), dpi=150)
    plt.close(fig)

    # ── Plot 2: power budget waterfall ────────────────────────────────────────
    stages = [
        "VCSEL\noutput",
        "After bottom\nwindow",
        "After Rb\ncell",
        "Detector\n(after top window)",
    ]
    powers = [
        _power["P_vcsel_uw"],
        _power["P_after_win_in_uw"],
        _power["P_after_cell_uw"],
        _power["P_detector_uw"],
    ]
    colors = ["#2ca02c", "#ff7f0e", "#d62728", "#1f77b4"]

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(stages, powers, color=colors, edgecolor="black", linewidth=0.7,
                  width=0.55, zorder=3)

    # Annotate bars
    for bar, pwr in zip(bars, powers):
        ax.text(bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 1.5,
                f"{pwr:.1f} µW",
                ha="center", va="bottom", fontsize=9, fontweight="bold")

    # Loss annotations between bars
    loss_labels = [
        f"−{(powers[0] - powers[1]):.1f} µW\nFresnel (2 surfs)",
        f"−{(powers[1] - powers[2]):.1f} µW\nAbsorption {_absorb['absorption_pct']:.1f}%",
        f"−{(powers[2] - powers[3]):.1f} µW\nFresnel (2 surfs)",
    ]
    for i in range(len(loss_labels)):
        xmid = (i + i + 1) / 2.0 + 0.5   # midpoint between bar i and i+1
        ymid = (powers[i] + powers[i + 1]) / 2.0
        ax.annotate(loss_labels[i],
                    xy=(xmid, ymid), xytext=(xmid, ymid + 8),
                    ha="center", fontsize=7, color="gray",
                    arrowprops=dict(arrowstyle="-", color="lightgray"))

    # Reference line at 10 µW (minimum useful power from program.md)
    ax.axhline(10, color="red", lw=1.2, ls="--", zorder=2, label="Min. useful (10 µW)")
    ax.legend(fontsize=8)

    ax.set_ylabel("Optical Power (µW)")
    ax.set_title(
        f"Optical Power Budget\n"
        f"Window T = {_power['window_transmission_pct']:.1f}%,  "
        f"Cell T = {_power['cell_transmission_pct']:.1f}%  "
        f"(α·L_eff = {_absorb['alpha_L_effective']:.4f} at {P_N2_Torr:.0f} Torr N2),  "
        f"I_pd = {_snr['photodiode_current_ua']:.1f} µA,  SNR = {_snr['snr']:.0f}"
    )
    ax.set_ylim(0, max(powers) * 1.25)
    ax.grid(axis="y", linestyle=":", alpha=0.5, zorder=1)
    fig.tight_layout()
    fig.savefig(os.path.join(plots_dir, "power_budget.png"), dpi=150)
    plt.close(fig)

    print("  [plots] Saved beam_propagation.png and power_budget.png -> plots/")


_make_plots()


# ═══════════════════════════════════════════════════════════════════════════════
# CLI summary
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print()
    print("=" * 60)
    print("  05_optical — Simulation Results")
    print("=" * 60)
    print(f"  VCSEL input power        : {INPUT_POWER_UW:.0f} µW")
    print(f"  N2 buffer pressure       : {P_N2_Torr:.1f} Torr")
    print(f"  Rayleigh range           : {_beam['rayleigh_range_mm']:.3f} mm")
    print(f"  Beam diam at cell exit   : {_beam['beam_diameter_at_cell_exit_mm']:.3f} mm")
    print(f"  No clipping              : {_beam['no_clipping']}")
    print(f"  alpha_L (base)           : {_absorb['alpha_L_base']:.4f}")
    print(f"  alpha_L (effective)      : {_absorb['alpha_L_effective']:.4f}")
    print(f"  Pressure broadening      : {_absorb['broadening_factor']:.0f}x  "
          f"(Gamma_total = {_absorb['gamma_total_mhz']:.0f} MHz)")
    print(f"  Absorption               : {_absorb['absorption_pct']:.2f} %")
    print(f"  Window transmission      : {_power['window_transmission_pct']:.2f} %")
    print(f"  Power at detector        : {_power['P_detector_uw']:.2f} µW")
    print(f"  Photodiode current       : {_snr['photodiode_current_ua']:.2f} µA")
    print(f"  Shot-noise SNR           : {_snr['snr']:.0f}")
    print("=" * 60)
