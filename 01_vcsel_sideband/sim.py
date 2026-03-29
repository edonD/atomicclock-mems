"""
SIM: 01_vcsel_sideband
Wave — see requirements.md
"""

import sys
import io

# Ensure stdout uses UTF-8 on Windows (evaluator output contains ✓)
if hasattr(sys.stdout, 'buffer') and sys.stdout.encoding.lower().replace('-', '') not in ('utf8',):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from scipy.special import jv
import numpy as np

# Constants from 00_atomic_model
HYPERFINE_HZ  = 6_834_682_610.904
F_MOD_HZ      = HYPERFINE_HZ / 2  # = 3,417,341,305.452 Hz


def compute_sideband_spectrum(beta, n_max=5):
    """
    Compute power fraction in each sideband for a given modulation index.

    Returns: dict {n: power_fraction} for n in [-n_max, +n_max]
    """
    return {n: jv(n, beta)**2 for n in range(-n_max, n_max+1)}


def find_optimal_beta():
    """
    Sweep β from 0 to 4 and find the value that maximizes |J₁(β)|².
    """
    betas = np.linspace(0.01, 4.0, 4000)
    j1_vals = jv(1, betas)
    # Maximise J1 (first sideband power)
    idx_opt = np.argmax(np.abs(j1_vals))
    return betas[idx_opt], j1_vals[idx_opt]


def compute_rf_power_dbm(beta, vcsel_fm_sensitivity_mhz_per_ma=500.0,
                          vcsel_impedance_ohm=50.0):
    """
    Estimate RF drive power needed to achieve modulation index β.

    The VCSEL FM sensitivity is typically 200–500 MHz/mA for a 795nm VCSEL.
    Required current amplitude: i_rf = (β × f_m) / sensitivity
    RF power: P = i_rf² × Z / 2
    """
    f_m_hz = F_MOD_HZ
    sensitivity_hz_per_a = vcsel_fm_sensitivity_mhz_per_ma * 1e6 / 1e-3

    # Current amplitude to achieve modulation depth β
    i_amplitude_a = beta * f_m_hz / sensitivity_hz_per_a
    power_w = 0.5 * i_amplitude_a**2 * vcsel_impedance_ohm
    power_dbm = 10 * np.log10(power_w * 1000)
    return power_dbm


# ── RESULTS ──────────────────────────────────────────────────────────
beta_opt, j1_opt = find_optimal_beta()
spectrum_opt = compute_sideband_spectrum(beta_opt)
sideband_power_pct = (spectrum_opt[1] + spectrum_opt[-1]) * 100

RESULTS = {
    "optimal_beta":             beta_opt,
    "j1_at_optimal":            abs(jv(1, beta_opt)),
    "j0_at_optimal":            abs(jv(0, beta_opt)),
    "sideband_power_pct":       sideband_power_pct,
    "sideband_spacing_ghz":     2 * F_MOD_HZ / 1e9,
    "rf_drive_power_dbm":       compute_rf_power_dbm(beta_opt),
}
