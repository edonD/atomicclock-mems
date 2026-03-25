"""
EVALUATOR: 04_thermal
======================
Wave 2 — Thermal management validation.

Grades against:
  - SA65 power budget: 120 mW total (heater should be < 100 mW)
  - MIL-STD-810 operating range: -40°C to +85°C ambient
  - Rb condensation limit: thermal gradient < 1°C/mm
  - PID stability: temperature variation < ±0.01°C

EXIT 0 = PASS
EXIT 1 = FAIL
"""

import sys
import os

BENCHMARKS = {
    "heater_power_mw": {
        "description": "Heater power at worst-case ambient (-40°C)",
        "target_max": 100.0,
        "source": "SA65 total budget 120 mW — heater must leave room for electronics",
        "critical": True,
    },
    "temp_stability_degc": {
        "description": "Temperature variation around 85°C setpoint (PID controlled)",
        "target_max": 0.01,
        "source": "CPT frequency-temperature coefficient requirement",
        "critical": True,
        "note": "1°C change → ~1 kHz clock frequency shift via N2 pressure-shift TC",
    },
    "thermal_gradient_degc_per_mm": {
        "description": "Temperature gradient across vapor cell",
        "target_max": 1.0,
        "source": "Rb thermophoresis threshold — condensation on cooler window",
        "critical": True,
        "note": "Gradient causes Rb to migrate to cold window = cell death",
    },
    "startup_time_s": {
        "description": "Time to reach 85°C from -40°C ambient",
        "target_max": 120.0,            # seconds — 2 minutes max
        "source": "Defense application startup requirement",
        "critical": False,
    },
    "rtd_sensitivity_ohm_per_degc": {
        "description": "RTD resistance sensitivity dR/dT",
        "target_min": 0.1,              # Ω/°C — must be detectable
        "source": "Pt TCR = 3850 ppm/°C, R₀ dependent",
        "critical": False,
    },
}


def load_results():
    py_results = os.path.join(os.path.dirname(__file__), "fem_results.py")
    if os.path.exists(py_results):
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location("fem_results", py_results)
            if spec is None or spec.loader is None:
                return None, "could not load fem_results.py"
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)  # type: ignore[union-attr]
            if hasattr(module, "RESULTS"):
                return module.RESULTS, None
        except Exception as e:
            return None, f"fem_results.py error: {e}"
    return None, "Elmer FEM not run yet — see requirements/02_elmer_fem.md"


def grade(results):
    passed, failed, warnings = [], [], []

    checks = [
        ("heater_power_mw",              "max", BENCHMARKS["heater_power_mw"]),
        ("temp_stability_degc",          "max", BENCHMARKS["temp_stability_degc"]),
        ("thermal_gradient_degc_per_mm", "max", BENCHMARKS["thermal_gradient_degc_per_mm"]),
        ("startup_time_s",               "max", BENCHMARKS["startup_time_s"]),
    ]

    for key, check_type, b in checks:
        val = results.get(key)
        if val is None:
            if b["critical"]:
                failed.append(f"{key}: NOT IN RESULTS")
            else:
                warnings.append(f"{key}: not reported")
            continue

        if check_type == "max":
            lim = b["target_max"]
            if val <= lim:
                margin = (lim - val) / lim * 100
                if margin > 20:
                    passed.append(f"{key}: {val:.3g}  (max {lim}, {margin:.0f}% margin)  ✓")
                else:
                    warnings.append(f"{key}: {val:.3g}  MARGINAL — only {margin:.0f}% below limit")
            else:
                msg = f"{key}: {val:.3g}  EXCEEDS {lim}"
                note = b.get("note", "")
                if note:
                    msg += f" — {note}"
                if b["critical"]:
                    failed.append(msg)
                else:
                    warnings.append(msg)

    return passed, failed, warnings


def report(passed, failed, warnings):
    width = 70
    print()
    print("=" * width)
    print("  EVALUATOR: 04_thermal")
    print("  Wave 2 — Thermal Management")
    print("=" * width)
    for p in passed:   print(f"    PASS  {p}")
    for w in warnings: print(f"    WARN  {w}")
    for f in failed:   print(f"    FAIL  {f}")
    print("=" * width)
    if failed:
        print("  VERDICT:  FAIL — thermal design inadequate")
        return False
    elif warnings:
        print("  VERDICT:  MARGINAL")
        return True
    else:
        print("  VERDICT:  PASS")
        print("  OUTPUTS:  heater_power, RTD specs → process_traveler, mask_layout")
        return True


if __name__ == "__main__":
    results, error = load_results()
    if results is None:
        print(f"\n  [NOT RUN]  {error}")
        sys.exit(2)
    passed, failed, warnings = grade(results)
    ok = report(passed, failed, warnings)
    sys.exit(0 if ok else 1)
