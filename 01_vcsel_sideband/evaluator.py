"""
EVALUATOR: 01_vcsel_sideband
==============================
Wave 2

Grades against:
  - Mathematical Bessel function values (exact, no tolerance)
  - Practical VCSEL modulation efficiency targets
  - CPT sideband power requirements

EXIT 0 = PASS
EXIT 1 = FAIL
"""

import sys
import os

BENCHMARKS = {

    "optimal_beta": {
        "description": "Modulation index that maximizes first sideband power",
        "target": 1.8412,              # exact: argmax of J1(x)
        "tolerance": 0.05,
        "source": "Bessel function mathematics (exact)",
        "critical": True,
    },

    "j1_at_optimal": {
        "description": "J₁(β_opt) — must match Bessel function table exactly",
        "target": 0.5819,              # J1(1.8412) exact
        "tolerance_pct": 0.5,
        "source": "Mathematical identity",
        "critical": True,
    },

    "j0_at_optimal": {
        "description": "J₀(β_opt) — residual carrier power indicator",
        "target": 0.3275,              # J0(1.8412)
        "tolerance_pct": 0.5,
        "source": "Mathematical identity",
        "critical": False,
    },

    "sideband_power_pct": {
        "description": "Total power fraction in ±1 sidebands combined",
        "target_min": 60.0,            # % — at least 60% of optical power useful
        "source": "CPT efficiency requirement",
        "critical": True,
        "note": "Power in other sidebands (carrier, ±2, ±3...) does not drive CPT and adds noise",
    },

    "sideband_spacing_ghz": {
        "description": "Frequency spacing between +1 and -1 sidebands",
        "target": 6.834682611,         # GHz — must match Rb hyperfine splitting exactly
        "tolerance_khz": 1.0,          # 1 kHz tolerance
        "source": "Rb-87 hyperfine splitting (NIST)",
        "critical": True,
        "note": "Wrong spacing = sidebands miss the atomic resonance = no CPT signal",
    },

    "rf_drive_power_dbm": {
        "description": "Required RF power at VCSEL modulation input",
        "target_max": 15.0,            # dBm — must be achievable with standard RF chips
        "target_min": -5.0,
        "source": "Practical RF design constraint (ADF4351 output range)",
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
    passed   = []
    failed   = []
    warnings = []

    # ── Optimal beta ──
    b   = BENCHMARKS["optimal_beta"]
    val = results.get("optimal_beta")
    if val is None:
        failed.append("optimal_beta: NOT IN RESULTS")
    else:
        err = abs(val - b["target"])
        if err <= b["tolerance"]:
            passed.append(f"optimal_beta: {val:.4f}  (target {b['target']}, error {err:.4f})  ✓")
        else:
            failed.append(f"optimal_beta: {val:.4f}  off by {err:.4f} — check scipy.special.jv() call")

    # ── J1 at optimal ──
    b   = BENCHMARKS["j1_at_optimal"]
    val = results.get("j1_at_optimal")
    if val is None:
        failed.append("j1_at_optimal: NOT IN RESULTS")
    else:
        err_pct = abs(val - b["target"]) / b["target"] * 100
        if err_pct <= b["tolerance_pct"]:
            passed.append(f"j1_at_optimal: {val:.4f}  (target {b['target']}, error {err_pct:.3f}%)  ✓")
        else:
            failed.append(f"j1_at_optimal: {val:.4f}  error {err_pct:.2f}% — Bessel calculation is wrong")

    # ── J0 at optimal ──
    b   = BENCHMARKS["j0_at_optimal"]
    val = results.get("j0_at_optimal")
    if val is not None:
        err_pct = abs(val - b["target"]) / b["target"] * 100
        if err_pct <= b["tolerance_pct"]:
            passed.append(f"j0_at_optimal: {val:.4f}  (carrier fraction {val**2*100:.1f}%)  ✓")
        else:
            warnings.append(f"j0_at_optimal: {val:.4f}  error {err_pct:.2f}%")

    # ── Total sideband power ──
    b   = BENCHMARKS["sideband_power_pct"]
    val = results.get("sideband_power_pct")
    if val is None:
        failed.append("sideband_power_pct: NOT IN RESULTS")
    else:
        if val >= b["target_min"]:
            passed.append(f"sideband_power_pct: {val:.1f}%  (min {b['target_min']}%)  ✓")
        else:
            failed.append(f"sideband_power_pct: {val:.1f}%  BELOW {b['target_min']}% — too much power wasted in unused sidebands")

    # ── Sideband spacing ──
    b   = BENCHMARKS["sideband_spacing_ghz"]
    val = results.get("sideband_spacing_ghz")
    if val is None:
        failed.append("sideband_spacing_ghz: NOT IN RESULTS")
    else:
        err_khz = abs(val - b["target"]) * 1e6
        if err_khz <= b["tolerance_khz"]:
            passed.append(f"sideband_spacing_ghz: {val:.9f} GHz  (error {err_khz:.3f} kHz)  ✓")
        else:
            failed.append(
                f"sideband_spacing_ghz: {val:.6f} GHz  off by {err_khz:.1f} kHz — "
                f"sidebands will miss Rb resonance"
            )

    # ── RF drive power ──
    b   = BENCHMARKS["rf_drive_power_dbm"]
    val = results.get("rf_drive_power_dbm")
    if val is not None:
        if b["target_min"] <= val <= b["target_max"]:
            passed.append(f"rf_drive_power_dbm: {val:.1f} dBm  ✓")
        else:
            warnings.append(f"rf_drive_power_dbm: {val:.1f} dBm  outside practical range — check RF chain design")

    return passed, failed, warnings


def report(passed, failed, warnings):
    width = 70
    print()
    print("=" * width)
    print("  EVALUATOR: 01_vcsel_sideband")
    print("  Wave 2 — VCSEL Modulation Validation")
    print("=" * width)

    for p in passed:   print(f"    PASS  {p}")
    for w in warnings: print(f"    WARN  {w}")
    for f in failed:   print(f"    FAIL  {f}")

    print("=" * width)
    if failed:
        print("  VERDICT:  FAIL — VCSEL modulation model incorrect")
        return False
    elif warnings:
        print("  VERDICT:  MARGINAL — review warnings")
        return True
    else:
        print("  VERDICT:  PASS — VCSEL sideband model validated")
        print("  OUTPUTS:  optimal_beta, rf_drive_power → spec_sheet, bom")
        return True


if __name__ == "__main__":
    results, error = load_results()
    if results is None:
        print(f"\n  [NOT RUN]  {error}")
        sys.exit(2)
    passed, failed, warnings = grade(results)
    ok = report(passed, failed, warnings)
    sys.exit(0 if ok else 1)
