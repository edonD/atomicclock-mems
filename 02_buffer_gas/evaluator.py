"""
EVALUATOR: 02_buffer_gas
=========================
Wave 2

Grades against:
  - Published Rb-N2 collision data (Vanier & Audoin textbook)
  - Standard CSAC published N2 pressure range
  - Rb vapor density from Antoine equation (thermodynamic identity)

EXIT 0 = PASS
EXIT 1 = FAIL
"""

import sys
import os

BENCHMARKS = {

    "optimal_n2_pressure_torr": {
        "description": "N2 buffer gas pressure that minimizes CPT linewidth",
        "target_min": 20.0,
        "target_max": 100.0,
        "benchmark": "30–75 Torr for ~1mm cells",
        "source": "Knappe et al. NIST (2004), Vanier & Audoin textbook",
        "critical": True,
        "note": "Outside this range = either Dicke narrowing fails or pressure broadening dominates",
    },

    "cpt_linewidth_at_popt_khz": {
        "description": "CPT linewidth at optimal N2 pressure",
        "target_max": 5.0,             # kHz
        "source": "Microchip SA65: 3–5 kHz",
        "critical": True,
    },

    "rb_density_m3": {
        "description": "Rb vapor number density at 85°C",
        "target_min": 5e16,            # m⁻³
        "target_max": 1e19,            # m⁻³
        "benchmark": "~2×10¹⁷ m⁻³ at 85°C",
        "source": "Antoine equation for Rb (Steck, Rb-87 D line data)",
        "critical": True,
        "note": "Too low = no absorption. Too high = cell opaque, atoms self-absorb.",
    },

    "pressure_shift_khz": {
        "description": "Clock frequency shift due to N2 pressure at P_opt",
        "target_max_abs": 1000.0,      # kHz — large shifts are compensated but must be known
        "source": "k_shift = -6.7 kHz/Torr (Vanier & Audoin)",
        "critical": False,
        "note": "This shift is compensated by tuning f_mod. Must be known precisely.",
    },

    "broadening_coefficient_khz_torr": {
        "description": "Pressure broadening coefficient k_broad (Rb-N2)",
        "target": 10.8,
        "tolerance_pct": 10.0,
        "source": "Vanier & Audoin (1989), Table 2",
        "critical": True,
        "note": "If your simulation uses wrong k_broad, N2 pressure target is wrong.",
    },

    "shift_coefficient_khz_torr": {
        "description": "Pressure shift coefficient k_shift (Rb-N2)",
        "target": -6.7,
        "tolerance_pct": 10.0,
        "source": "Vanier & Audoin (1989), Table 2",
        "critical": False,
    },
}


def load_results():
    sim_path = os.path.join(os.path.dirname(__file__), "sim.py")
    if not os.path.exists(sim_path):
        return None, "sim.py not found"
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("sim", sim_path)
        if spec is None or spec.loader is None:
            return None, "could not load sim.py"
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)  # type: ignore[union-attr]
        if not hasattr(module, "RESULTS"):
            return None, "sim.py did not define RESULTS dict"
        return module.RESULTS, None
    except NotImplementedError:
        return None, "sim.py not implemented yet"
    except Exception as e:
        return None, f"sim.py error: {e}"


def grade(results):
    passed, failed, warnings = [], [], []

    # ── Broadening coefficient (validates model inputs) ──
    b   = BENCHMARKS["broadening_coefficient_khz_torr"]
    val = results.get("broadening_coefficient_khz_torr")
    if val is None:
        warnings.append("broadening_coefficient_khz_torr: NOT IN RESULTS — cannot validate model inputs")
    else:
        err_pct = abs(val - b["target"]) / abs(b["target"]) * 100
        if err_pct <= b["tolerance_pct"]:
            passed.append(f"broadening_coeff: {val:.2f} kHz/Torr  (target {b['target']}, error {err_pct:.1f}%)  ✓")
        else:
            failed.append(
                f"broadening_coeff: {val:.2f} kHz/Torr  ERROR {err_pct:.1f}% vs published {b['target']} — "
                f"check Vanier & Audoin data, wrong coefficient invalidates pressure calculation"
            )

    # ── Optimal N2 pressure ──
    b   = BENCHMARKS["optimal_n2_pressure_torr"]
    val = results.get("optimal_n2_pressure_torr")
    if val is None:
        failed.append("optimal_n2_pressure_torr: NOT IN RESULTS — cannot define fill recipe")
    else:
        if b["target_min"] <= val <= b["target_max"]:
            passed.append(f"optimal_n2_pressure_torr: {val:.1f} Torr  (range {b['target_min']}–{b['target_max']} Torr)  ✓")
        else:
            failed.append(
                f"optimal_n2_pressure_torr: {val:.1f} Torr  OUTSIDE range {b['target_min']}–{b['target_max']} Torr — "
                f"check cell geometry inputs from 03_mems_geometry"
            )

    # ── CPT linewidth at optimal pressure ──
    b   = BENCHMARKS["cpt_linewidth_at_popt_khz"]
    val = results.get("cpt_linewidth_at_popt_khz")
    if val is None:
        failed.append("cpt_linewidth_at_popt_khz: NOT IN RESULTS")
    else:
        if val <= b["target_max"]:
            passed.append(f"cpt_linewidth_at_popt: {val:.2f} kHz  (max {b['target_max']} kHz)  ✓")
        else:
            failed.append(f"cpt_linewidth_at_popt: {val:.2f} kHz  EXCEEDS {b['target_max']} kHz — cell too large or pressure wrong")

    # ── Rb vapor density ──
    b   = BENCHMARKS["rb_density_m3"]
    val = results.get("rb_density_m3")
    if val is None:
        failed.append("rb_density_m3: NOT IN RESULTS")
    else:
        if b["target_min"] <= val <= b["target_max"]:
            passed.append(f"rb_density_m3: {val:.2e} m⁻³  ✓")
        elif val < b["target_min"]:
            failed.append(f"rb_density_m3: {val:.2e} m⁻³  TOO LOW — insufficient absorption, increase cell temperature")
        else:
            warnings.append(f"rb_density_m3: {val:.2e} m⁻³  HIGH — check Antoine equation parameters")

    # ── Pressure shift ──
    b   = BENCHMARKS["pressure_shift_khz"]
    val = results.get("pressure_shift_khz")
    if val is not None:
        if abs(val) <= b["target_max_abs"]:
            passed.append(f"pressure_shift_khz: {val:.1f} kHz  (compensatable by f_mod tuning)  ✓")
        else:
            warnings.append(f"pressure_shift_khz: {val:.1f} kHz  large — verify tuning range in 06_rf_synthesis covers this")

    return passed, failed, warnings


def report(passed, failed, warnings):
    width = 70
    print()
    print("=" * width)
    print("  EVALUATOR: 02_buffer_gas")
    print("  Wave 2 — Buffer Gas Optimization")
    print("=" * width)
    for p in passed:   print(f"    PASS  {p}")
    for w in warnings: print(f"    WARN  {w}")
    for f in failed:   print(f"    FAIL  {f}")
    print("=" * width)
    if failed:
        print("  VERDICT:  FAIL — N2 pressure recipe cannot be defined")
        return False
    elif warnings:
        print("  VERDICT:  MARGINAL — review warnings before committing to fill recipe")
        return True
    else:
        print("  VERDICT:  PASS")
        print("  OUTPUTS:  optimal_n2_pressure → process_traveler (fill step)")
        return True


if __name__ == "__main__":
    results, error = load_results()
    if results is None:
        print(f"\n  [NOT RUN]  {error}")
        sys.exit(2)
    passed, failed, warnings = grade(results)
    ok = report(passed, failed, warnings)
    sys.exit(0 if ok else 1)
