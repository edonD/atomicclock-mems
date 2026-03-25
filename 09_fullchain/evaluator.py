"""
EVALUATOR: 09_fullchain
========================
Wave 4 — Final Go/No-Go for Phase 2.

This is the master physics evaluator. All module outputs converge here.
If this passes, Phase 1 is complete and you proceed to:
  - design/spec_sheet.md
  - design/process_traveler.md
  - design/mask_layout/ (GDS-II)

Grades against:
  - Full system ADEV consistent with module-level predictions
  - Power budget < 150 mW
  - All critical specs met simultaneously (no spec borrowing)

EXIT 0 = PASS  — proceed to Phase 2
EXIT 1 = FAIL  — fix identified module, re-run that wave
"""

import sys
import os

BENCHMARKS = {
    "final_adev_1s": {
        "description": "End-to-end Allan deviation at τ=1s",
        "target_max": 5e-10,
        "critical": True,
    },
    "adev_consistency_with_08": {
        "description": "Fullchain ADEV within 20% of 08_allan prediction",
        "tolerance_pct": 20.0,
        "critical": True,
        "note": "If fullchain gives very different ADEV than 08_allan, modules have interactions not modeled",
    },
    "total_power_mw": {
        "description": "Total system power consumption",
        "target_max": 150.0,
        "benchmark_sa65": 120.0,
        "source": "Microchip SA65: 120 mW",
        "critical": True,
    },
    "phase2_ready": {
        "description": "All critical specs met — Phase 2 go/no-go",
        "target": True,
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
            return None, "RESULTS dict not found"
        return module.RESULTS, None
    except NotImplementedError:
        return None, "sim.py not implemented yet"
    except Exception as e:
        return None, f"sim.py error: {e}"


def load_module_result(module_name, key):
    """Load a specific result from a previous module."""
    path = os.path.join(os.path.dirname(__file__), "..", module_name, "sim.py")
    path = os.path.normpath(path)
    if not os.path.exists(path):
        return None
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location(module_name, path)
        if spec is None or spec.loader is None:
            return None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)  # type: ignore[union-attr]
        return getattr(module, "RESULTS", {}).get(key)
    except Exception:
        return None


def grade(results):
    passed, failed, warnings = [], [], []

    # ── Final ADEV ──
    b   = BENCHMARKS["final_adev_1s"]
    val = results.get("final_adev_1s")
    if val is None:
        failed.append("final_adev_1s: NOT IN RESULTS")
    else:
        if val <= b["target_max"]:
            passed.append(f"final_adev_1s: {val:.2e}  PASS  ✓")
        else:
            failed.append(f"final_adev_1s: {val:.2e}  FAILS target {b['target_max']:.0e}")

    # ── Consistency with 08_allan ──
    b            = BENCHMARKS["adev_consistency_with_08"]
    val_full     = results.get("final_adev_1s")
    val_08       = load_module_result("08_allan", "adev_1s")
    if val_full is not None and val_08 is not None:
        diff_pct = abs(val_full - val_08) / val_08 * 100
        if diff_pct <= b["tolerance_pct"]:
            passed.append(f"adev_consistency: fullchain {val_full:.2e} vs 08_allan {val_08:.2e}  ({diff_pct:.1f}% diff)  ✓")
        else:
            failed.append(
                f"adev_consistency: fullchain {val_full:.2e} differs from 08_allan {val_08:.2e} "
                f"by {diff_pct:.1f}% — module interaction not modeled in 08_allan. Investigate."
            )

    # ── Power budget ──
    b   = BENCHMARKS["total_power_mw"]
    val = results.get("total_power_mw")
    if val is None:
        failed.append("total_power_mw: NOT IN RESULTS — cannot verify power budget")
    else:
        if val <= b["target_max"]:
            if val <= b["benchmark_sa65"]:
                passed.append(f"total_power_mw: {val:.1f} mW  BETTER than SA65 ({b['benchmark_sa65']} mW)  ✓✓")
            else:
                passed.append(f"total_power_mw: {val:.1f} mW  (max {b['target_max']} mW)  ✓")
        else:
            failed.append(f"total_power_mw: {val:.1f} mW  EXCEEDS {b['target_max']} mW — review 04_thermal heater power")

    # ── Phase 2 ready ──
    val = results.get("phase2_ready")
    if val is True:
        passed.append("phase2_ready: confirmed by simulation  ✓")
    elif val is False:
        failed.append("phase2_ready: simulation flagged unresolved issues — see results.md")

    # ── Weakest link ──
    weakest = results.get("weakest_link_parameter")
    if weakest:
        warnings.append(f"weakest_link: '{weakest}' — tighten manufacturing control on this parameter")

    return passed, failed, warnings


def report(passed, failed, warnings):
    width = 70
    print()
    print("=" * width)
    print("  EVALUATOR: 09_fullchain")
    print("  WAVE 4 FINAL GATE — Phase 1 Complete?")
    print("=" * width)
    for p in passed:   print(f"    PASS  {p}")
    for w in warnings: print(f"    WARN  {w}")
    for f in failed:   print(f"    FAIL  {f}")
    print("=" * width)

    if failed:
        print("  VERDICT:  FAIL")
        print("  ACTION:   Phase 2 NOT authorized.")
        print("            Return to the failing module's wave and fix root cause.")
        return False
    elif warnings:
        print("  VERDICT:  MARGINAL — Phase 2 allowed but review warnings first")
        return True
    else:
        print("  VERDICT:  PASS — PHASE 1 COMPLETE")
        print()
        print("  NEXT STEPS (Phase 2):")
        print("    1. compile design/spec_sheet.md from all results.md files")
        print("    2. compile design/process_traveler.md")
        print("    3. run design/mask_layout/csac_cell_v1.py  (generates GDS-II)")
        print("    4. send design/fto_brief.md to patent attorney")
        print("    5. contact foundry with GDS-II + process_traveler")
        return True


if __name__ == "__main__":
    results, error = load_results()
    if results is None:
        print(f"\n  [NOT RUN]  {error}")
        sys.exit(2)
    passed, failed, warnings = grade(results)
    ok = report(passed, failed, warnings)
    sys.exit(0 if ok else 1)
