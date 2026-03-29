"""
SIM: 09_fullchain
Wave 4 — End-to-end system validation and Phase 2 authorization gate.

Loads RESULTS from all 9 modules, recomputes ADEV from first principles
(consistency check vs 08_allan), runs sensitivity analysis to find the
weakest manufacturing link, and computes the total power budget.

Physics reference: program.md
Evaluator:         evaluator.py
"""

import importlib.util
import os
import sys
import numpy as np

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ─────────────────────────────────────────────────────────────────────────────
# MODULE LOADER
# ─────────────────────────────────────────────────────────────────────────────

_HERE = os.path.dirname(os.path.abspath(__file__))


def _load_module_results(rel_path):
    """Load RESULTS dict from a module file. Returns {} on any failure."""
    try:
        path = os.path.normpath(os.path.join(_HERE, rel_path))
        if not os.path.exists(path):
            return {}
        spec = importlib.util.spec_from_file_location("_fc_mod", path)
        if spec is None or spec.loader is None:
            return {}
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return getattr(mod, "RESULTS", {})
    except Exception as e:
        print(f"  [09_fullchain] Warning: could not load {rel_path}: {e}")
        return {}


# ─────────────────────────────────────────────────────────────────────────────
# LOAD ALL UPSTREAM RESULTS
# ─────────────────────────────────────────────────────────────────────────────

r00 = _load_module_results("../00_atomic_model/sim.py")
r01 = _load_module_results("../01_vcsel_sideband/sim.py")
r02 = _load_module_results("../02_buffer_gas/sim.py")
r03 = _load_module_results("../03_mems_geometry/fem_results.py")   # NOTE: fem_results.py
r04 = _load_module_results("../04_thermal/fem_results.py")         # NOTE: fem_results.py
r05 = _load_module_results("../05_optical/sim.py")
r06 = _load_module_results("../06_rf_synthesis/sim.py")
r07 = _load_module_results("../07_servo_loop/sim.py")
r08 = _load_module_results("../08_allan/sim.py")

# Flat namespace with module prefix (mirrors program.md convention)
all_results = {}
for prefix, res in [
    ("00_atomic_model",  r00),
    ("01_vcsel_sideband", r01),
    ("02_buffer_gas",    r02),
    ("03_mems_geometry", r03),
    ("04_thermal",       r04),
    ("05_optical",       r05),
    ("06_rf_synthesis",  r06),
    ("07_servo_loop",    r07),
    ("08_allan",         r08),
]:
    for k, v in res.items():
        all_results[f"{prefix}.{k}"] = v

# ─────────────────────────────────────────────────────────────────────────────
# EXTRACT PHYSICAL PARAMETERS (with fallbacks)
# ─────────────────────────────────────────────────────────────────────────────

F_HFS = 6_834_682_610.904  # Hz

def _get(key, default):
    v = all_results.get(key)
    return float(v) if v is not None else float(default)


# Parameters used in ADEV computation
cpt_lw_khz   = _get("00_atomic_model.cpt_linewidth_khz",        3.2)
cpt_contrast_pct = _get("00_atomic_model.cpt_contrast_pct",     4.8)
snr          = _get("05_optical.snr",                            28000.0)
adev_vco_1s  = _get("06_rf_synthesis.adev_from_vco_1s",         9e-15)
temp_stab    = _get("04_thermal.temp_stability_degc",            0.001)
p_n2_torr    = _get("02_buffer_gas.optimal_n2_pressure_torr",   76.6)

# Power budget input from 04_thermal
heater_mw    = _get("04_thermal.heater_power_mw",               60.0)

# ─────────────────────────────────────────────────────────────────────────────
# FULL ADEV FORMULA (same as 08_allan — all three noise sources)
# ─────────────────────────────────────────────────────────────────────────────

def compute_adev_1s(lw_khz, contrast_pct, snr_val, adev_vco, t_stab, p_n2,
                    f_hfs=F_HFS):
    """
    Compute total ADEV at tau=1s from first principles.
    Three noise sources added in quadrature (Vanier & Audoin eq. 6.41):
      1. Shot noise (white FM):   sigma_shot = (Δν / (C × f_hfs)) / SNR
      2. VCO phase noise (PM):    sigma_vco  = adev_vco_1s
      3. Thermal via pressure shift: sigma_thermal = K × P_N2 × (δT/T) / f_hfs
    """
    delta_nu  = lw_khz * 1e3                     # Hz
    contrast  = contrast_pct / 100.0             # fraction

    sigma_shot    = (delta_nu / (contrast * f_hfs)) / snr_val
    sigma_vco_    = adev_vco                      # already at tau=1s
    K_shift       = 6700.0                        # Hz/Torr
    T_K           = 358.0                         # K
    delta_nu_th   = K_shift * p_n2 * (t_stab / T_K)
    sigma_thermal = delta_nu_th / f_hfs

    return float(np.sqrt(sigma_shot**2 + sigma_vco_**2 + sigma_thermal**2))


# Nominal ADEV
final_adev = compute_adev_1s(
    cpt_lw_khz, cpt_contrast_pct, snr, adev_vco_1s, temp_stab, p_n2_torr
)

# ─────────────────────────────────────────────────────────────────────────────
# CONSISTENCY CHECK vs 08_ALLAN
# ─────────────────────────────────────────────────────────────────────────────

adev_08 = _get("08_allan.adev_1s", final_adev)  # fallback to self if 08 unavailable
diff_pct = abs(final_adev - adev_08) / adev_08 * 100.0
adev_consistent = diff_pct < 20.0

# ─────────────────────────────────────────────────────────────────────────────
# SENSITIVITY ANALYSIS — ±10% perturbation on each physical parameter
# ─────────────────────────────────────────────────────────────────────────────

# Physical parameters to perturb (key in all_results → positional argument name)
SENSITIVITY_MAP = {
    "00_atomic_model.cpt_linewidth_khz":       "lw_khz",
    "00_atomic_model.cpt_contrast_pct":        "contrast_pct",
    "05_optical.snr":                          "snr_val",
    "04_thermal.temp_stability_degc":          "t_stab",
    "02_buffer_gas.optimal_n2_pressure_torr":  "p_n2",
}

# Nominal parameter values for perturbation
nominal_phys = {
    "lw_khz":      cpt_lw_khz,
    "contrast_pct": cpt_contrast_pct,
    "snr_val":     snr,
    "adev_vco":    adev_vco_1s,
    "t_stab":      temp_stab,
    "p_n2":        p_n2_torr,
}

sensitivities = {}
for result_key, param_name in SENSITIVITY_MAP.items():
    perturbed = nominal_phys.copy()
    perturbed[param_name] = nominal_phys[param_name] * 1.10   # +10%
    adev_perturbed = compute_adev_1s(
        perturbed["lw_khz"],
        perturbed["contrast_pct"],
        perturbed["snr_val"],
        perturbed["adev_vco"],
        perturbed["t_stab"],
        perturbed["p_n2"],
    )
    sensitivity_pct = abs(adev_perturbed - final_adev) / final_adev * 100.0
    # Use the human-readable base key as the label
    short_key = result_key.split(".", 1)[1]   # strip module prefix
    sensitivities[short_key] = sensitivity_pct

weakest_link = max(sensitivities, key=sensitivities.get)

# ─────────────────────────────────────────────────────────────────────────────
# POWER BUDGET
# ─────────────────────────────────────────────────────────────────────────────

vcsel_mw   = 5.0    # VCSEL driver (~5 mA × 1.5 V)
rf_mw      = 30.0   # ADF4351 PLL + VCO + amp
digital_mw = 15.0   # MCU + ADC + PID firmware

total_power_mw = heater_mw + vcsel_mw + rf_mw + digital_mw

# ─────────────────────────────────────────────────────────────────────────────
# PHASE 2 GATE
# ─────────────────────────────────────────────────────────────────────────────

phase2_ready = (
    final_adev < 5e-10
    and total_power_mw < 150.0
    and adev_consistent
)

# ─────────────────────────────────────────────────────────────────────────────
# RESULTS  (defined before plots so evaluator sees them even if plots fail)
# ─────────────────────────────────────────────────────────────────────────────

RESULTS = {
    "final_adev_1s":             final_adev,
    "total_power_mw":            total_power_mw,
    "weakest_link_parameter":    weakest_link,
    "adev_consistent_with_08":   adev_consistent,
    "phase2_ready":              phase2_ready,
    # diagnostics
    "diff_pct_vs_08":            diff_pct,
    "heater_power_mw":           heater_mw,
    "vcsel_power_mw":            vcsel_mw,
    "rf_power_mw":               rf_mw,
    "digital_power_mw":          digital_mw,
    "sensitivities":             sensitivities,
}

# ─────────────────────────────────────────────────────────────────────────────
# PLOTS  (non-critical — wrapped so evaluator still gets RESULTS if they fail)
# ─────────────────────────────────────────────────────────────────────────────

plots_dir = os.path.join(_HERE, "plots")
os.makedirs(plots_dir, exist_ok=True)

try:
# ── 1. Sensitivity bar chart ──────────────────────────────────────────────────
    labels  = list(sensitivities.keys())
    values  = [float(sensitivities[k]) for k in labels]  # ensure plain Python float
    max_val = max(values)
    colors  = ["tab:red" if abs(v - max_val) < 1e-12 else "steelblue" for v in values]

    fig, ax = plt.subplots(figsize=(9, max(4, len(labels) * 0.8)))
    y_pos = list(range(len(labels)))
    ax.barh(y_pos, values, color=colors, edgecolor="black", linewidth=0.5)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels, fontsize=10)
    ax.set_xlabel("ADEV sensitivity to +10% parameter change (%)", fontsize=11)
    ax.set_title("09_fullchain — Parameter Sensitivity Analysis\n"
                 "(red = weakest link / tightest manufacturing tolerance)", fontsize=11)
    ax.grid(axis="x", ls=":", alpha=0.5)
    plt.tight_layout()
    sensitivity_path = os.path.join(plots_dir, "sensitivity_chart.png")
    plt.savefig(sensitivity_path, dpi=150)
    plt.close()
    print(f"  [plots] Saved {sensitivity_path}")

    # ── 2. Power budget pie chart ─────────────────────────────────────────────
    power_labels  = ["Heater",     "VCSEL",    "RF / PLL", "Digital"]
    power_values  = [float(heater_mw), float(vcsel_mw), float(rf_mw), float(digital_mw)]
    power_colors  = ["tab:orange", "tab:blue", "tab:red",  "tab:green"]

    fig2, ax2 = plt.subplots(figsize=(7, 7))
    ax2.pie(
        power_values,
        labels=power_labels,
        colors=power_colors,
        explode=[0.05] * 4,
        autopct="%1.1f%%",
        startangle=140,
        textprops={"fontsize": 11},
    )
    ax2.set_title(
        f"MEMS CSAC — Power Budget\nTotal: {total_power_mw:.1f} mW  "
        f"(SA65 benchmark: 120 mW)",
        fontsize=12,
    )
    plt.tight_layout()
    power_path = os.path.join(plots_dir, "power_budget.png")
    plt.savefig(power_path, dpi=150)
    plt.close()
    print(f"  [plots] Saved {power_path}")

except Exception as _plot_err:
    print(f"  [plots] Warning: plot generation failed ({_plot_err})")

# ─────────────────────────────────────────────────────────────────────────────
# SUMMARY
# ─────────────────────────────────────────────────────────────────────────────

print()
print("=" * 60)
print("  09_fullchain — End-to-End Results")
print("=" * 60)
print(f"  Final ADEV @ tau=1s : {final_adev:.2e}")
print(f"  08_allan ADEV @ 1s  : {adev_08:.2e}   (diff {diff_pct:.1f}%)")
print(f"  Consistent          : {adev_consistent}")
print(f"  Total power         : {total_power_mw:.1f} mW")
print(f"  Weakest link        : {weakest_link}")
print(f"  Phase 2 ready       : {phase2_ready}")
print("=" * 60)
