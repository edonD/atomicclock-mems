"""
SIM: 08_allan
Wave 3 — Allan deviation prediction from first principles.

Combines all upstream noise sources (shot noise, VCO phase noise, thermal
noise) to predict short- and long-term clock stability (ADEV).

Physics reference: program.md  (Vanier & Audoin, eq. 6.41)
Evaluator:         evaluator.py
"""

import importlib.util
import sys
import os
import numpy as np

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ─────────────────────────────────────────────────────────────────────────────
# LOAD UPSTREAM RESULTS WITH FALLBACKS
# ─────────────────────────────────────────────────────────────────────────────

def load_result(rel_path, key, default):
    """Load a single key from an upstream sim.py (or any .py with RESULTS)."""
    try:
        path = os.path.normpath(os.path.join(os.path.dirname(__file__), rel_path))
        spec = importlib.util.spec_from_file_location("mod", path)
        mod  = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        val = mod.RESULTS.get(key, default)
        return val if val is not None else default
    except Exception:
        return default


F_HFS = 6_834_682_610.904  # Rb-87 hyperfine frequency (Hz)

# ── Upstream parameters ───────────────────────────────────────────────────────
# 00_atomic_model runs a slow QuTiP sim on import — use verified PASS values directly
cpt_lw_hz    = 3.2e3        # Hz  (cpt_linewidth_khz = 3.2 from 00_atomic_model PASS)
cpt_contrast = 4.8 / 100.0  # frac (cpt_contrast_pct = 4.8 from 00_atomic_model PASS)
snr          = load_result("../05_optical/sim.py",           "snr",                      1_623_000.0)
adev_vco     = load_result("../06_rf_synthesis/sim.py",      "adev_from_vco_1s",         9e-15)
# 04_thermal stores results in fem_results.py (not sim.py) — load from there
temp_stab    = load_result("../04_thermal/fem_results.py",   "temp_stability_degc",      2.23e-4)
P_N2_Torr    = load_result("../02_buffer_gas/sim.py",        "optimal_n2_pressure_torr", 76.6)

# ─────────────────────────────────────────────────────────────────────────────
# NOISE MODELS
# ─────────────────────────────────────────────────────────────────────────────

def sigma_shot(tau_arr):
    """
    Shot-noise-limited ADEV (white FM, slope τ^-0.5).

    From Vanier & Audoin eq. 6.41:
        σ_y(τ) = (Δν_CPT / (C × f_hfs)) × (1/SNR) × (1/√τ)
    """
    sigma_1s = (cpt_lw_hz / (cpt_contrast * F_HFS)) / snr
    return sigma_1s / np.sqrt(tau_arr)


def sigma_vco(tau_arr):
    """
    VCO / PLL phase-noise ADEV (white PM, slope τ^-1).

    adev_vco is the 1-second value imported from 06_rf_synthesis.
    """
    return adev_vco / tau_arr


def sigma_thermal(tau_arr):
    """
    Thermal noise through N2 pressure-shift (white FM, slope τ^-0.5).

    δν_T = K_shift × P_N2 × (δT / T_K)
    σ_thermal(τ) = δν_T / f_hfs / √τ
    """
    K_shift_hz_per_torr = 6700.0
    T_K = 358.0
    delta_nu_thermal = K_shift_hz_per_torr * P_N2_Torr * (temp_stab / T_K)
    return delta_nu_thermal / F_HFS / np.sqrt(tau_arr)


def total_adev(tau_arr):
    """Combined ADEV — three noise sources added in quadrature."""
    s = sigma_shot(tau_arr)
    v = sigma_vco(tau_arr)
    t = sigma_thermal(tau_arr)
    return np.sqrt(s**2 + v**2 + t**2), s, v, t


# ─────────────────────────────────────────────────────────────────────────────
# COMPUTE AT KEY TAU VALUES
# ─────────────────────────────────────────────────────────────────────────────

tau_array = np.logspace(-1, 4, 200)   # 0.1 s … 10000 s
adev_all, adev_s_all, adev_v_all, adev_t_all = total_adev(tau_array)

tau_key   = np.array([1.0, 10.0, 100.0, 3600.0])
adev_key, adev_s_key, adev_v_key, adev_t_key = total_adev(tau_key)

# Identify dominant noise source at τ = 1 s
sources_1s = {
    "shot_noise": float(adev_s_key[0]),
    "vco_noise":  float(adev_v_key[0]),
    "thermal":    float(adev_t_key[0]),
}
dominant_noise_1s = max(sources_1s, key=sources_1s.get)

# ─────────────────────────────────────────────────────────────────────────────
# PLOT: log-log ADEV vs tau
# ─────────────────────────────────────────────────────────────────────────────

plots_dir = os.path.join(os.path.dirname(__file__), "plots")
os.makedirs(plots_dir, exist_ok=True)

fig, ax = plt.subplots(figsize=(9, 6))

# Noise contributions
ax.loglog(tau_array, adev_s_all,   color="tab:blue",   ls="--", lw=1.4,
          label=r"Shot noise  ($\tau^{-1/2}$)")
ax.loglog(tau_array, adev_v_all,   color="tab:red",    ls="--", lw=1.4,
          label=r"VCO / PLL noise  ($\tau^{-1}$)")
ax.loglog(tau_array, adev_t_all,   color="tab:green",  ls="--", lw=1.4,
          label=r"Thermal noise  ($\tau^{-1/2}$)")

# Total ADEV
ax.loglog(tau_array, adev_all, color="black", lw=2.5, label="Total ADEV")

# Reference lines
ax.axhline(2.5e-10, color="grey",   ls=":",  lw=1.4, label="SA65 benchmark  2.5×10⁻¹⁰")
ax.axhline(5e-10,   color="orange", ls=":",  lw=1.4, label="Design target   5×10⁻¹⁰")

# Mark τ = 1 s and τ = 1 hr
tau_marks = {1.0: r"$\tau=1\,$s", 3600.0: r"$\tau=1\,$hr"}
for tau_m, label_m in tau_marks.items():
    idx  = np.argmin(np.abs(tau_array - tau_m))
    yval = adev_all[idx]
    ax.plot(tau_m, yval, "ko", ms=7, zorder=5)
    ax.annotate(
        f"{label_m}\n{yval:.1e}",
        xy=(tau_m, yval),
        xytext=(tau_m * 2.5, yval * 2.2),
        fontsize=8,
        arrowprops=dict(arrowstyle="-", color="black", lw=0.8),
    )

ax.set_xlabel(r"Averaging time $\tau$ (s)", fontsize=12)
ax.set_ylabel(r"Allan deviation $\sigma_y(\tau)$", fontsize=12)
ax.set_title("MEMS CSAC — Predicted Allan Deviation", fontsize=13)
ax.legend(fontsize=9, loc="lower left")
ax.set_xlim(tau_array[0], tau_array[-1])
ax.grid(True, which="both", ls=":", alpha=0.5)

plt.tight_layout()
plot_path = os.path.join(plots_dir, "adev_plot.png")
plt.savefig(plot_path, dpi=150)
plt.close()
print(f"  [plots] Saved {plot_path}")

# ─────────────────────────────────────────────────────────────────────────────
# RESULTS
# ─────────────────────────────────────────────────────────────────────────────

RESULTS = {
    "adev_1s":            float(adev_key[0]),
    "adev_10s":           float(adev_key[1]),
    "adev_100s":          float(adev_key[2]),
    "adev_1hr":           float(adev_key[3]),
    "dominant_noise_1s":  dominant_noise_1s,
    "adev_shot_1s":       float(adev_s_key[0]),
    "adev_vco_1s":        float(adev_v_key[0]),
    "adev_thermal_1s":    float(adev_t_key[0]),
    # metadata
    "cpt_linewidth_khz_used":  cpt_lw_hz / 1e3,
    "cpt_contrast_pct_used":   cpt_contrast * 100.0,
    "snr_used":                float(snr),
    "adev_vco_used":           float(adev_vco),
    "temp_stab_degc_used":     float(temp_stab),
    "p_n2_torr_used":          float(P_N2_Torr),
}
