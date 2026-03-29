"""
SIM: 06_rf_synthesis
RF synthesis simulation for MEMS atomic clock.

Simulates ADF4351 fractional-N PLL synthesizing 3.4173 GHz from a 10 MHz
TCXO reference, computes VCO phase noise contribution to ADEV, and checks
tuning range against the N2 pressure shift from 02_buffer_gas.
"""

import os
import sys
import math
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ---------------------------------------------------------------------------
# Physical constants
# ---------------------------------------------------------------------------
HYPERFINE_HZ    = 6_834_682_610.904     # Hz  Rb-87 ground-state hyperfine
F_REF_HZ        = 10_000_000.0          # Hz  10 MHz TCXO reference
F_TARGET_HZ     = HYPERFINE_HZ / 2      # Hz  = 3_417_341_305.452

# ADF4351 hardware limits
ADF4351_M_MAX   = 4095                  # max modulus M (denominator)
ADF4351_N_MIN   = 23
ADF4351_N_MAX   = 65535

# VCO parameters
VCO_PHASE_NOISE_DBC  = -90.0            # dBc/Hz at 10 kHz offset (typical 3.4 GHz VCO)
K_VCO_HZ_PER_V       = 10e6            # Hz/V  VCO tuning sensitivity
F_SERVO_BW_HZ        = 30.0            # Hz    CPT servo loop bandwidth

# ADEV target
ADEV_TARGET_1S  = 5e-10                # clock ADEV target at tau=1s

# ---------------------------------------------------------------------------
# Load pressure shift from 02_buffer_gas
# ---------------------------------------------------------------------------
try:
    _bg_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             "..", "02_buffer_gas")
    sys.path.insert(0, _bg_path)
    import sim as _bg
    pressure_shift_hz = float(_bg.RESULTS["pressure_shift_khz"]) * 1e3
    _bg_source = "02_buffer_gas/sim.py"
except Exception as _e:
    pressure_shift_hz = -513_000.0      # default: 76.6 Torr × 6700 Hz/Torr
    _bg_source = f"default (buffer gas load failed: {_e})"

# ---------------------------------------------------------------------------
# PLL fractional-N synthesis  (ADF4351)
# f_VCO = (N + F/M) * f_ref,   0 <= F < M
# ---------------------------------------------------------------------------

def find_pll_settings(f_target=F_TARGET_HZ, f_ref=F_REF_HZ, M_max=ADF4351_M_MAX):
    """
    Search all M from 2 to M_max, compute best (N, F, M) that minimises
    |f_actual - f_target|.

    Returns dict with keys: N, F, M, f_actual_hz, error_hz
    """
    ratio = f_target / f_ref
    N     = int(ratio)
    frac  = ratio - N

    best_error = math.inf
    best       = {}

    for M in range(2, M_max + 1):
        F = round(frac * M)
        if F >= M:
            F = M - 1
        if F < 0:
            F = 0
        f_actual = (N + F / M) * f_ref
        error    = abs(f_actual - f_target)
        if error < best_error:
            best_error = error
            best = {
                "N":          N,
                "F":          F,
                "M":          M,
                "f_actual_hz": f_actual,
                "error_hz":   error,
            }

    return best


def find_pll_settings_100mhz(f_target=F_TARGET_HZ, M_max=ADF4351_M_MAX):
    """
    Alternative: use a 100 MHz reference (10 MHz TCXO × 10 OCXO multiplier).
    Searches M from 2 to M_max.
    """
    return find_pll_settings(f_target=f_target, f_ref=100_000_000.0, M_max=M_max)


# ---------------------------------------------------------------------------
# VCO phase noise → ADEV contribution
# ---------------------------------------------------------------------------

def vco_adev(s_phi_dbc, f_vco, tau):
    """
    Estimate ADEV from white VCO phase noise floor.

    For white phase noise (flat S_phi):
        sigma_y(tau) = sqrt(S_phi_linear) / (f_vco * tau)

    Parameters
    ----------
    s_phi_dbc : float
        Phase noise floor in dBc/Hz.
    f_vco : float
        VCO frequency in Hz.
    tau : float or array
        Averaging time in seconds.

    Returns
    -------
    float or ndarray  ADEV value(s).
    """
    S_phi_linear = 10.0 ** (s_phi_dbc / 10.0)
    return np.sqrt(S_phi_linear) / (f_vco * np.asarray(tau, dtype=float))


def vco_adev_with_servo(s_phi_dbc, f_vco, tau, f_servo_bw=F_SERVO_BW_HZ):
    """
    More accurate estimate: integrate VCO noise only outside servo bandwidth.

    ADEV_vco ≈ sqrt(S_phi_linear * f_servo_bw) / (f_vco * tau)
    """
    S_phi_linear = 10.0 ** (s_phi_dbc / 10.0)
    return np.sqrt(S_phi_linear * f_servo_bw) / (f_vco * np.asarray(tau, dtype=float))


# ---------------------------------------------------------------------------
# Tuning range
# ---------------------------------------------------------------------------

def required_tuning_range(pressure_shift_hz, margin=3.0):
    """VCO tuning range needed to cover pressure shift with margin."""
    return abs(pressure_shift_hz) * margin


# ---------------------------------------------------------------------------
# Run calculations
# ---------------------------------------------------------------------------

# --- 10 MHz reference (primary) ---
pll_10mhz = find_pll_settings(f_ref=F_REF_HZ)

# --- 100 MHz reference (alternative) ---
pll_100mhz = find_pll_settings_100mhz()

# Choose option with lower frequency error
if pll_10mhz["error_hz"] <= pll_100mhz["error_hz"]:
    pll_best     = pll_10mhz
    chosen_f_ref = F_REF_HZ
    chosen_label = "10 MHz TCXO (direct)"
else:
    pll_best     = pll_100mhz
    chosen_f_ref = 100_000_000.0
    chosen_label = "100 MHz (10 MHz × 10 multiplier)"

# ADEV at tau = 1 s
adev_1s = float(vco_adev(VCO_PHASE_NOISE_DBC, F_TARGET_HZ, 1.0))

# Tuning range
tuning_range_hz = required_tuning_range(pressure_shift_hz)

# Required tuning voltage
req_tuning_voltage_v = tuning_range_hz / K_VCO_HZ_PER_V

# Achievable frequency step at chosen M
achievable_freq_step_hz = chosen_f_ref / pll_best["M"]

# ---------------------------------------------------------------------------
# Build M-sweep data for plot (sample M values from 100 to 4095)
# ---------------------------------------------------------------------------
_ratio = F_TARGET_HZ / F_REF_HZ
_N     = int(_ratio)
_frac  = _ratio - _N

# Compute frequency error for every M from 2 to 4095
m_values   = np.arange(2, ADF4351_M_MAX + 1)
f_errors   = np.empty(len(m_values))
for _i, _m in enumerate(m_values):
    _F = round(_frac * _m)
    if _F >= _m:
        _F = _m - 1
    f_errors[_i] = abs(((_N + _F / _m) * F_REF_HZ) - F_TARGET_HZ)

# ---------------------------------------------------------------------------
# Plots
# ---------------------------------------------------------------------------
_plot_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "plots")
os.makedirs(_plot_dir, exist_ok=True)

# ---- Plot 1: Frequency error vs M ----------------------------------------
_fig1, _ax1 = plt.subplots(figsize=(10, 5))

# Thin grey line for every M (too dense to plot individually — use line)
_ax1.semilogy(m_values, f_errors, color="steelblue", linewidth=0.6,
              alpha=0.7, label="Frequency error vs M")

# Mark best M
_ax1.semilogy(pll_best["M"], pll_best["error_hz"],
              "ro", markersize=8,
              label=f"Best M={pll_best['M']}: {pll_best['error_hz']:.3f} Hz")

# Mark M=4095
_f_err_4095 = f_errors[ADF4351_M_MAX - 2]   # index = M-2
_ax1.semilogy(ADF4351_M_MAX, _f_err_4095,
              "g^", markersize=8,
              label=f"M=4095: {_f_err_4095:.1f} Hz")

# Mark M=100, 500, 1000, 2000 as reference bars
_bar_ms = [100, 500, 1000, 2000, 4095]
_bar_errs = [f_errors[m - 2] for m in _bar_ms]
_ax1.bar(_bar_ms, _bar_errs, width=60, color="orange", alpha=0.5,
         label="Selected M checkpoints", zorder=3)

_ax1.axhline(1.0, color="red", linestyle="--", linewidth=1.2,
             label="1 Hz threshold")
_ax1.set_xlabel("Modulus M", fontsize=12)
_ax1.set_ylabel("Frequency error (Hz)", fontsize=12)
_ax1.set_title("ADF4351 PLL Frequency Error vs Modulus M\n"
               f"f_ref=10 MHz, f_target={F_TARGET_HZ/1e9:.9f} GHz", fontsize=12)
_ax1.legend(fontsize=9)
_ax1.grid(True, which="both", alpha=0.3)
_ax1.set_xlim(0, ADF4351_M_MAX + 50)
_fig1.tight_layout()
_fig1.savefig(os.path.join(_plot_dir, "pll_frequency_error.png"), dpi=150)
plt.close(_fig1)

# ---- Plot 2: ADEV from VCO vs tau ----------------------------------------
_tau_arr = np.logspace(0, 4, 300)   # 1 s to 10000 s

_adev_white  = vco_adev(VCO_PHASE_NOISE_DBC, F_TARGET_HZ, _tau_arr)
_adev_servo  = vco_adev_with_servo(VCO_PHASE_NOISE_DBC, F_TARGET_HZ,
                                    _tau_arr, F_SERVO_BW_HZ)
_adev_target = np.full_like(_tau_arr, ADEV_TARGET_1S)

_fig2, _ax2 = plt.subplots(figsize=(9, 6))
_ax2.loglog(_tau_arr, _adev_white,
            color="royalblue", linewidth=2,
            label=r"VCO ADEV (white phase noise, $\sigma_y \propto \tau^{-1}$)")
_ax2.loglog(_tau_arr, _adev_servo,
            color="darkorange", linewidth=2, linestyle="--",
            label=f"VCO ADEV (servo BW={F_SERVO_BW_HZ:.0f} Hz limit)")
_ax2.loglog(_tau_arr, _adev_target,
            color="crimson", linewidth=1.5, linestyle="-.",
            label=f"Clock target ADEV = {ADEV_TARGET_1S:.0e}")

# Mark tau = 1s point
_ax2.plot(1.0, adev_1s, "bo", markersize=9,
          label=f"VCO ADEV at τ=1s = {adev_1s:.2e}")

# Shade region where VCO is safely below target
_ax2.fill_between(_tau_arr, _adev_white, _adev_target,
                  where=(_adev_white < _adev_target),
                  alpha=0.12, color="green", label="VCO safely below target")

_ax2.set_xlabel("Averaging time τ (s)", fontsize=12)
_ax2.set_ylabel("Allan Deviation σ_y(τ)", fontsize=12)
_ax2.set_title(
    f"VCO Phase Noise → ADEV Contribution\n"
    f"S_φ = {VCO_PHASE_NOISE_DBC:.0f} dBc/Hz @ 10 kHz offset, f_VCO = {F_TARGET_HZ/1e9:.4f} GHz",
    fontsize=12,
)
_ax2.legend(fontsize=9)
_ax2.grid(True, which="both", alpha=0.3)
_ax2.set_xlim(1, 10000)
_fig2.tight_layout()
_fig2.savefig(os.path.join(_plot_dir, "phase_noise_adev.png"), dpi=150)
plt.close(_fig2)

# ---------------------------------------------------------------------------
# RESULTS
# ---------------------------------------------------------------------------
RESULTS = {
    # PLL divider settings (best M from 2..4095 with 10 MHz ref)
    "pll_N":                    int(pll_best["N"]),
    "pll_F":                    int(pll_best["F"]),
    "pll_M":                    int(pll_best["M"]),

    # Frequency synthesis quality
    "f_actual_hz":              float(pll_best["f_actual_hz"]),
    "frequency_error_hz":       float(pll_best["error_hz"]),
    "achievable_freq_step_hz":  float(achievable_freq_step_hz),

    # Tuning range to cover N2 pressure shift (3× margin)
    "tuning_range_hz":          float(tuning_range_hz),
    "pressure_shift_hz":        float(pressure_shift_hz),
    "required_tuning_voltage_v": float(req_tuning_voltage_v),

    # VCO phase noise
    "vco_phase_noise_dbc":      float(VCO_PHASE_NOISE_DBC),
    "adev_from_vco_1s":         float(adev_1s),

    # Chip recommendation
    "recommended_chip":         "ADF4351 (Analog Devices, ~$15, 35 MHz-4.4 GHz)",

    # Metadata
    "f_ref_hz":                 float(chosen_f_ref),
    "f_target_hz":              float(F_TARGET_HZ),
    "pll_reference":            chosen_label,
    "pressure_shift_source":    _bg_source,
}

# ---------------------------------------------------------------------------
# Console summary
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("=" * 60)
    print("06_rf_synthesis — ADF4351 PLL Synthesis Results")
    print("=" * 60)
    print(f"Target frequency    : {F_TARGET_HZ:.3f} Hz")
    print(f"Reference           : {chosen_label}")
    print(f"Pressure shift src  : {_bg_source}")
    print()
    print(f"PLL settings        : N={pll_best['N']}, F={pll_best['F']}, M={pll_best['M']}")
    print(f"Actual frequency    : {pll_best['f_actual_hz']:.4f} Hz")
    print(f"Frequency error     : {pll_best['error_hz']:.4f} Hz")
    print(f"Freq step (f_ref/M) : {achievable_freq_step_hz:.2f} Hz")
    print()
    print(f"Alternative (100MHz ref): N={pll_100mhz['N']}, F={pll_100mhz['F']}, "
          f"M={pll_100mhz['M']}, error={pll_100mhz['error_hz']:.2f} Hz")
    print(f"Chosen option       : {chosen_label} (lower error)")
    print()
    print(f"Pressure shift      : {pressure_shift_hz/1e3:.2f} kHz")
    print(f"Tuning range (3x)   : {tuning_range_hz/1e3:.2f} kHz")
    print(f"Required voltage    : {req_tuning_voltage_v*1e3:.1f} mV  (K_VCO=10 MHz/V)")
    print()
    print(f"VCO phase noise     : {VCO_PHASE_NOISE_DBC:.0f} dBc/Hz @ 10 kHz")
    print(f"ADEV from VCO (1s)  : {adev_1s:.3e}  (target < 1e-10)")
    print(f"Margin vs target    : {ADEV_TARGET_1S / adev_1s:.0f}x")
    print()
    print(f"Recommended chip    : {RESULTS['recommended_chip']}")
    print()
    print("Plots saved to plots/")
    print("  pll_frequency_error.png")
    print("  phase_noise_adev.png")
