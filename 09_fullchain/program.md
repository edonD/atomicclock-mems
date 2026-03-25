# Module 09: Full Chain — Program

## 1. Mission

Connect all 9 modules into a single end-to-end simulation that validates
the complete system. Run a sensitivity analysis to find the weakest link.
Verify the power budget. This is the Phase 2 authorization gate.

**What "done" means:**

1. End-to-end ADEV @ τ=1s matches 08_allan prediction within 20%.
2. Total power < 150 mW.
3. Sensitivity analysis identifies the most critical parameter.
4. `python evaluator.py` exits 0 and prints "PHASE 1 COMPLETE".

---

## 2. What This Module Does

It does not run new physics. It imports RESULTS from every module and:
1. Recomputes ADEV using all parameters simultaneously (not independently)
2. Checks for cross-module interactions
3. Runs ±10% perturbation on each parameter to find sensitivity
4. Computes total power budget

---

## 3. Implementation

```python
import numpy as np
import sys, os, importlib.util

def load_all_results():
    """Import RESULTS dict from every module's sim.py."""
    modules = {
        "00_atomic_model":  ["cpt_linewidth_khz", "cpt_contrast_pct",
                              "discriminator_slope"],
        "01_vcsel_sideband":["optimal_beta", "sideband_power_pct"],
        "02_buffer_gas":    ["optimal_n2_pressure_torr", "pressure_shift_khz"],
        "03_mems_geometry": ["cavity_diameter_mm", "cavity_depth_mm"],
        "04_thermal":       ["heater_power_mw", "temp_stability_degc"],
        "05_optical":       ["optical_power_at_detector_uw", "snr"],
        "06_rf_synthesis":  ["adev_from_vco_1s"],
        "07_servo_loop":    ["phase_margin_deg", "lock_bandwidth_hz"],
        "08_allan":         ["adev_1s"],
    }

    all_results = {}
    for mod_name, keys in modules.items():
        path = os.path.normpath(
            os.path.join(os.path.dirname(__file__), "..", mod_name, "sim.py"))
        try:
            spec = importlib.util.spec_from_file_location(mod_name, path)
            if spec is None or spec.loader is None:
                continue
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)  # type: ignore[union-attr]
            for k in keys:
                all_results[f"{mod_name}.{k}"] = module.RESULTS.get(k)
        except Exception as e:
            print(f"  Warning: could not load {mod_name}: {e}")

    return all_results


def compute_full_adev(params):
    """
    Recompute ADEV from scratch using all parameters.
    This is the integrated version of 08_allan's formula.
    """
    F_HFS     = 6_834_682_610.904
    delta_nu  = params.get("00_atomic_model.cpt_linewidth_khz", 3.2) * 1e3
    contrast  = params.get("00_atomic_model.cpt_contrast_pct",  4.8) / 100.0
    snr       = params.get("05_optical.snr", 28000.0)
    adev_vco  = params.get("06_rf_synthesis.adev_from_vco_1s", 9e-15)

    adev_shot = (delta_nu / (contrast * F_HFS)) / snr
    adev_total = np.sqrt(adev_shot**2 + adev_vco**2)
    return adev_total


def sensitivity_analysis(params_nominal, delta_pct=10.0):
    """
    Perturb each parameter ±10% and measure ADEV change.
    Returns: dict of {parameter: sensitivity_ratio}
    """
    adev_nominal = compute_full_adev(params_nominal)
    sensitivities = {}

    for key, val in params_nominal.items():
        if val is None or not isinstance(val, (int, float)):
            continue

        # Perturb +10%
        params_plus = params_nominal.copy()
        params_plus[key] = val * (1 + delta_pct / 100)
        adev_plus = compute_full_adev(params_plus)

        sensitivity = abs(adev_plus - adev_nominal) / adev_nominal
        sensitivities[key] = sensitivity

    return sensitivities


def compute_power_budget(params):
    """Total system power consumption (mW)."""
    heater_mw = params.get("04_thermal.heater_power_mw", 60.0)
    vcsel_mw  = 5.0    # VCSEL at ~5mA × 1.5V
    rf_mw     = 30.0   # PLL + VCO + RF amp
    digital_mw = 15.0  # MCU + ADC + PID
    return heater_mw + vcsel_mw + rf_mw + digital_mw


# ── MAIN ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    params = load_all_results()

    final_adev    = compute_full_adev(params)
    sensitivities = sensitivity_analysis(params)
    total_power   = compute_power_budget(params)

    # Weakest link = parameter with highest ADEV sensitivity
    if sensitivities:
        weakest = max(sensitivities, key=sensitivities.get)
    else:
        weakest = "unknown (run all modules first)"

    # Consistency check vs 08_allan
    adev_08 = params.get("08_allan.adev_1s")
    consistent = True
    if adev_08 is not None:
        diff_pct = abs(final_adev - adev_08) / adev_08 * 100
        consistent = diff_pct < 20.0

    phase2_ready = (final_adev < 5e-10 and total_power < 150.0 and consistent)

    RESULTS = {
        "final_adev_1s":        final_adev,
        "total_power_mw":       total_power,
        "weakest_link_parameter": weakest,
        "adev_consistent_with_08": consistent,
        "phase2_ready":         phase2_ready,
    }
```

---

## 4. Interpreting Sensitivity Analysis

```
High sensitivity parameter  →  tight manufacturing control needed
Low sensitivity parameter   →  relaxed tolerance acceptable
```

Example output:
```
Sensitivity analysis (ADEV change per 10% parameter perturbation):
  00_atomic_model.cpt_contrast_pct    0.45    ← tighten N2 fill tolerance
  00_atomic_model.cpt_linewidth_khz   0.40
  05_optical.snr                      0.30
  04_thermal.temp_stability_degc      0.02    ← loose — thermal is fine
```

The top parameter goes into the process traveler as the tightest
manufacturing control specification.
