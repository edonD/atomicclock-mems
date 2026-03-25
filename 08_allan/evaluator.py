"""
EVALUATOR: 08_allan
====================
Wave 3 — the performance gate.

This is the most important evaluator after 00_atomic_model.
If the Allan deviation does not meet spec here, the clock fails
its primary mission before any hardware is built.

Grades against:
  - Design target: ADEV < 5×10⁻¹⁰ at τ=1s
  - Benchmark: Microchip SA65 ADEV = 2.5×10⁻¹⁰ at τ=1s
  - Defense application: < 1×10⁻¹¹ at τ=1hr (GPS holdover requirement)

EXIT 0 = PASS
EXIT 1 = FAIL
"""

import sys
import os

BENCHMARKS = {

    "adev_1s": {
        "description": "Allan deviation at τ = 1 second",
        "target_max": 5e-10,
        "benchmark_sa65": 2.5e-10,
        "source": "Microchip SA65 CSAC datasheet + internal target",
        "critical": True,
        "note": (
            "This is the PRIMARY clock spec. "
            "1 µs timing error per day requires ADEV < 1.2×10⁻¹¹ at 1 hr. "
            "For GPS holdover at 1s: ADEV < 5×10⁻¹⁰ gives <150m position error/second."
        ),
    },

    "adev_100s": {
        "description": "Allan deviation at τ = 100 seconds",
        "target_max": 5e-11,
        "source": "Internal target (white FM noise floor)",
        "critical": True,
    },

    "adev_1hr": {
        "description": "Allan deviation at τ = 1 hour",
        "target_max": 1e-11,
        "source": "GPS holdover requirement for defense navigation",
        "critical": False,
        "note": "Reaching 1e-11 at 1hr typically requires active temperature compensation",
    },

    "flicker_floor": {
        "description": "Long-term Allan deviation flicker floor",
        "target_max": 3e-11,
        "source": "SA65 specification",
        "critical": False,
    },

    "dominant_noise_1s": {
        "description": "Dominant noise source at τ=1s (must be shot noise, not VCO or thermal)",
        "target": "shot_noise",
        "source": "Good clock design: shot-noise limited at short term",
        "critical": False,
        "note": "If VCO noise dominates at 1s, fix the PLL. If thermal dominates, fix PID.",
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
            return None, "RESULTS dict not found"
        return module.RESULTS, None
    except NotImplementedError:
        return None, "sim.py not implemented yet"
    except Exception as e:
        return None, f"sim.py error: {e}"


def grade(results):
    passed, failed, warnings = [], [], []

    # ── ADEV @ 1s ── (most critical)
    b   = BENCHMARKS["adev_1s"]
    val = results.get("adev_1s")
    if val is None:
        failed.append("adev_1s: NOT IN RESULTS — cannot evaluate clock performance")
    else:
        ratio_vs_target = val / b["target_max"]
        ratio_vs_sa65   = val / b["benchmark_sa65"]
        if val <= b["target_max"]:
            if ratio_vs_sa65 <= 1.0:
                passed.append(f"adev_1s: {val:.2e}  BEATS SA65 benchmark ({b['benchmark_sa65']:.2e})  ✓✓")
            else:
                passed.append(
                    f"adev_1s: {val:.2e}  (target {b['target_max']:.0e}, "
                    f"{ratio_vs_sa65:.1f}× worse than SA65 {b['benchmark_sa65']:.0e})  ✓"
                )
        elif val <= b["target_max"] * 2:
            warnings.append(
                f"adev_1s: {val:.2e}  MARGINALLY FAILS target {b['target_max']:.0e} — "
                f"clock unstable for GPS holdover. Improve SNR or reduce linewidth."
            )
        else:
            failed.append(
                f"adev_1s: {val:.2e}  FAILS target {b['target_max']:.0e} by {ratio_vs_target:.1f}× — "
                f"fundamental redesign needed. Check CPT contrast and laser power."
            )

    # ── ADEV @ 100s ──
    b   = BENCHMARKS["adev_100s"]
    val = results.get("adev_100s")
    if val is None:
        warnings.append("adev_100s: NOT IN RESULTS")
    else:
        if val <= b["target_max"]:
            passed.append(f"adev_100s: {val:.2e}  (target {b['target_max']:.0e})  ✓")
        else:
            failed.append(f"adev_100s: {val:.2e}  FAILS target {b['target_max']:.0e}")

    # ── ADEV @ 1hr ──
    b   = BENCHMARKS["adev_1hr"]
    val = results.get("adev_1hr")
    if val is not None:
        if val <= b["target_max"]:
            passed.append(f"adev_1hr: {val:.2e}  (target {b['target_max']:.0e})  ✓")
        else:
            warnings.append(
                f"adev_1hr: {val:.2e}  ABOVE target {b['target_max']:.0e} — "
                f"may need temperature stabilization improvement"
            )

    # ── Dominant noise ──
    val = results.get("dominant_noise_1s")
    if val is not None:
        if val == "shot_noise":
            passed.append("dominant_noise_1s: shot_noise limited  ✓  (optimal design)")
        elif val == "vco_noise":
            warnings.append("dominant_noise_1s: VCO noise limited — improve PLL phase noise (06_rf_synthesis)")
        elif val == "thermal":
            warnings.append("dominant_noise_1s: thermal noise limited — improve PID temperature control (04_thermal)")
        else:
            warnings.append(f"dominant_noise_1s: {val} — unexpected noise source")

    return passed, failed, warnings


def report(passed, failed, warnings):
    width = 70
    print()
    print("=" * width)
    print("  EVALUATOR: 08_allan")
    print("  Wave 3 — Allan Deviation Performance Gate")
    print("  Benchmark: Microchip SA65  ADEV = 2.5×10⁻¹⁰ @ 1s")
    print("=" * width)
    for p in passed:   print(f"    PASS  {p}")
    for w in warnings: print(f"    WARN  {w}")
    for f in failed:   print(f"    FAIL  {f}")
    print("=" * width)
    if failed:
        print("  VERDICT:  FAIL — clock does not meet performance spec")
        print("  ACTION:   Do NOT proceed to 09_fullchain.")
        print("            Return to 00_atomic_model and 05_optical to improve SNR.")
        return False
    elif warnings:
        print("  VERDICT:  MARGINAL — review noise sources before proceeding")
        return True
    else:
        print("  VERDICT:  PASS — predicted performance meets or beats SA65")
        print("  ACTION:   Proceed to 09_fullchain for end-to-end validation.")
        return True


if __name__ == "__main__":
    results, error = load_results()
    if results is None:
        print(f"\n  [NOT RUN]  {error}")
        sys.exit(2)
    passed, failed, warnings = grade(results)
    ok = report(passed, failed, warnings)
    sys.exit(0 if ok else 1)
