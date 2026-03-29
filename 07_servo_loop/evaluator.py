"""
EVALUATOR: 07_servo_loop
=========================
Wave 3

Grades against:
  - Control theory stability requirements (phase/gain margin)
  - Published CSAC servo loop parameters
  - Lock bandwidth targets for defense applications

EXIT 0 = PASS
EXIT 1 = FAIL
"""

import sys
import os

BENCHMARKS = {
    "phase_margin_deg": {
        "description": "Open-loop phase margin",
        "target_min": 45.0,
        "source": "Control engineering standard (Bode stability criterion)",
        "critical": True,
        "note": "<45° = marginally stable, oscillates under perturbation. <0° = unstable.",
    },
    "gain_margin_db": {
        "description": "Open-loop gain margin",
        "target_min": 10.0,
        "source": "Control engineering standard",
        "critical": True,
    },
    "lock_bandwidth_hz": {
        "description": "Closed-loop servo bandwidth",
        "target_min": 5.0,
        "target_max": 500.0,
        "source": "CSAC literature: 10–100 Hz typical",
        "critical": False,
        "note": "Too narrow = slow to lock, sensitive to vibration. Too wide = amplifies noise.",
    },
    "capture_range_khz": {
        "description": "Frequency range over which loop will lock",
        "target_min_x_linewidth": 0.5,     # must be > 0.5 × CPT linewidth
        "source": "Internal requirement",
        "critical": True,
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

    # ── Phase margin ──
    b   = BENCHMARKS["phase_margin_deg"]
    val = results.get("phase_margin_deg")
    if val is None:
        failed.append("phase_margin_deg: NOT IN RESULTS")
    else:
        if val >= b["target_min"] + 15:
            passed.append(f"phase_margin_deg: {val:.1f}°  (min {b['target_min']}°, good margin)  ✓")
        elif val >= b["target_min"]:
            warnings.append(f"phase_margin_deg: {val:.1f}°  MARGINAL — only {val - b['target_min']:.1f}° above limit")
        else:
            failed.append(f"phase_margin_deg: {val:.1f}°  BELOW {b['target_min']}° — loop will oscillate, reduce PID gains")

    # ── Gain margin ──
    b   = BENCHMARKS["gain_margin_db"]
    val = results.get("gain_margin_db")
    if val is None:
        failed.append("gain_margin_db: NOT IN RESULTS")
    else:
        if val >= b["target_min"]:
            passed.append(f"gain_margin_db: {val:.1f} dB  (min {b['target_min']} dB)  ✓")
        else:
            failed.append(f"gain_margin_db: {val:.1f} dB  BELOW {b['target_min']} dB — reduce loop gain")

    # ── Lock bandwidth ──
    b   = BENCHMARKS["lock_bandwidth_hz"]
    val = results.get("lock_bandwidth_hz")
    if val is not None:
        if b["target_min"] <= val <= b["target_max"]:
            passed.append(f"lock_bandwidth_hz: {val:.1f} Hz  ✓")
        else:
            warnings.append(f"lock_bandwidth_hz: {val:.1f} Hz  outside typical range {b['target_min']}–{b['target_max']} Hz")

    # ── Capture range ──
    b   = BENCHMARKS["capture_range_khz"]
    val = results.get("capture_range_khz")
    cpt_lw = results.get("cpt_linewidth_khz", 5.0)  # default 5 kHz if not provided
    if val is None:
        warnings.append("capture_range_khz: NOT IN RESULTS")
    else:
        min_required = cpt_lw * b["target_min_x_linewidth"]
        if val >= min_required:
            passed.append(f"capture_range_khz: {val:.2f} kHz  (min {min_required:.2f} kHz = 0.5 × CPT linewidth)  ✓")
        else:
            failed.append(f"capture_range_khz: {val:.2f} kHz  TOO SMALL — clock may fail to lock from cold start")

    return passed, failed, warnings


def report(passed, failed, warnings):
    width = 70
    print()
    print("=" * width)
    print("  EVALUATOR: 07_servo_loop")
    print("  Wave 3 — Servo Loop Stability")
    print("=" * width)
    for p in passed:   print(f"    PASS  {p}")
    for w in warnings: print(f"    WARN  {w}")
    for f in failed:   print(f"    FAIL  {f}")
    print("=" * width)
    if failed:
        print("  VERDICT:  FAIL — servo loop unstable or insufficient capture range")
        return False
    elif warnings:
        print("  VERDICT:  MARGINAL")
        return True
    else:
        print("  VERDICT:  PASS")
        print("  OUTPUTS:  PID gains, lock bandwidth → spec_sheet")
        return True


if __name__ == "__main__":
    # Ensure UTF-8 output on Windows so Unicode check-marks print cleanly
    if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf-8-sig"):
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

    results, error = load_results()
    if results is None:
        print(f"\n  [NOT RUN]  {error}")
        sys.exit(2)
    passed, failed, warnings = grade(results)
    ok = report(passed, failed, warnings)
    sys.exit(0 if ok else 1)
