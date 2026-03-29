"""
EVALUATOR: 05_optical
Wave 2

Grades the optical path simulation against:
  - Beam clipping requirement  (beam must fit through cavity)
  - Optical power at detector  > 10 µW
  - Shot-noise SNR             > 100
  - Absorption                 within sensible bounds

EXIT 0 = PASS
EXIT 1 = FAIL
EXIT 2 = NOT RUN / ERROR
"""

import sys
import os

BENCHMARKS = {
    "no_clipping": {
        "description": "Gaussian beam fits through cavity without clipping",
        "required":    True,
        "critical":    True,
    },
    "optical_power_at_detector_uw": {
        "description": "Optical power reaching the photodetector",
        "target_min":  10.0,        # µW — enough for shot-noise limited detection
        "target_warn": 50.0,        # µW — comfortable margin
        "source":      "program.md §1 'done' criteria",
        "critical":    True,
    },
    "snr": {
        "description": "Shot-noise limited SNR (feeds ADEV in 08_allan)",
        "target_min":  100.0,
        "target_warn": 1000.0,
        "source":      "program.md §1 'done' criteria",
        "critical":    True,
    },
    "absorption_pct": {
        "description": "Absorption in Rb cell (Beer-Lambert)",
        "target_min":  0.5,         # % — sanity check: some absorption must happen
        "target_max":  90.0,        # % — cell cannot be opaque
        "source":      "program.md §2.2 (α·L ~ 0.22 → ~20% absorption without buffer gas)",
        "critical":    False,
    },
    "window_transmission_pct": {
        "description": "Combined transmission through all 4 glass-air surfaces",
        "target_min":  80.0,        # %
        "source":      "4 × Fresnel 4% reflection → 0.96^4 = 84.9%",
        "critical":    False,
    },
    "beam_diameter_at_cell_exit_mm": {
        "description": "Full beam diameter (2w) at cell exit plane",
        "target_max":  0.9 * 1.5,   # mm  — default 90% of 1.5 mm cavity
        "source":      "program.md no-clipping condition",
        "critical":    True,
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
        spec.loader.exec_module(module)          # type: ignore[union-attr]
        if not hasattr(module, "RESULTS") or not module.RESULTS:
            return None, "sim.py RESULTS dict is empty — not implemented yet"
        return module.RESULTS, None
    except Exception as e:
        return None, f"sim.py error: {e}"


def grade(results):
    passed   = []
    failed   = []
    warnings = []

    # Retrieve cavity diameter used by sim (may differ from default)
    cav_diam = results.get("cavity_diameter_mm", 1.5)

    # ── No-clipping ──────────────────────────────────────────────────────────
    no_clip = results.get("no_clipping")
    bd_mm   = results.get("beam_diameter_at_cell_exit_mm")
    if no_clip is None:
        failed.append("no_clipping: NOT IN RESULTS")
    elif not no_clip:
        failed.append(
            f"no_clipping: FAIL  beam diameter {bd_mm:.3f} mm >= 90% of "
            f"cavity {cav_diam:.2f} mm = {0.9*cav_diam:.3f} mm  — "
            "add collimating microlens or increase cavity diameter"
        )
    else:
        passed.append(
            f"no_clipping: PASS  beam diameter {bd_mm:.3f} mm < "
            f"{0.9*cav_diam:.3f} mm (90% of {cav_diam:.2f} mm cavity)"
        )

    # ── Optical power at detector ─────────────────────────────────────────────
    b   = BENCHMARKS["optical_power_at_detector_uw"]
    val = results.get("optical_power_at_detector_uw")
    if val is None:
        failed.append("optical_power_at_detector_uw: NOT IN RESULTS")
    elif val < b["target_min"]:
        failed.append(
            f"optical_power_at_detector_uw: {val:.2f} µW  BELOW minimum "
            f"{b['target_min']} µW — increase VCSEL power or reduce cavity absorption"
        )
    elif val < b["target_warn"]:
        passed.append(f"optical_power_at_detector_uw: {val:.2f} µW  (min {b['target_min']} µW)  PASS")
        warnings.append(f"optical_power_at_detector_uw: {val:.2f} µW  marginal — comfortable margin is > {b['target_warn']} µW")
    else:
        passed.append(f"optical_power_at_detector_uw: {val:.2f} µW  (min {b['target_min']} µW)  PASS")

    # ── SNR ──────────────────────────────────────────────────────────────────
    b   = BENCHMARKS["snr"]
    val = results.get("snr")
    if val is None:
        failed.append("snr: NOT IN RESULTS")
    elif val < b["target_min"]:
        failed.append(
            f"snr: {val:.0f}  BELOW minimum {b['target_min']}  — "
            "insufficient for ADEV target"
        )
    elif val < b["target_warn"]:
        passed.append(f"snr: {val:.0f}  (min {b['target_min']})  PASS")
        warnings.append(f"snr: {val:.0f}  marginal — comfortable margin is > {b['target_warn']}")
    else:
        passed.append(f"snr: {val:.0f}  (min {b['target_min']})  PASS")

    # ── Absorption ────────────────────────────────────────────────────────────
    b   = BENCHMARKS["absorption_pct"]
    val = results.get("absorption_pct")
    if val is not None:
        if b["target_min"] <= val <= b["target_max"]:
            passed.append(f"absorption_pct: {val:.2f}%  (range {b['target_min']}–{b['target_max']}%)  PASS")
        elif val < b["target_min"]:
            warnings.append(
                f"absorption_pct: {val:.2f}%  very low — CPT signal may be weak. "
                "Check Rb vapor density / cavity depth."
            )
        else:
            failed.append(
                f"absorption_pct: {val:.2f}%  TOO HIGH (max {b['target_max']}%) — "
                "cell is nearly opaque"
            )

    # ── Window transmission ───────────────────────────────────────────────────
    b   = BENCHMARKS["window_transmission_pct"]
    val = results.get("window_transmission_pct")
    if val is not None:
        expected = (1 - 0.04) ** 4 * 100
        if val >= b["target_min"]:
            passed.append(
                f"window_transmission_pct: {val:.2f}%  "
                f"(expected ~{expected:.1f}% for n=1.47 glass)  PASS"
            )
        else:
            warnings.append(f"window_transmission_pct: {val:.2f}%  unexpectedly low — check coating model")

    # ── Photodiode current (informational) ────────────────────────────────────
    i_ua = results.get("photodiode_current_ua")
    if i_ua is not None:
        passed.append(f"photodiode_current_ua: {i_ua:.2f} µA  (informational)")

    return passed, failed, warnings


def report(results, passed, failed, warnings):
    width = 70
    print()
    print("=" * width)
    print("  EVALUATOR: 05_optical")
    print("  Wave 2 — Optical Path & SNR Validation")
    print("=" * width)

    # Print key numbers for quick scan
    pd_uw  = results.get("optical_power_at_detector_uw", "?")
    snr    = results.get("snr", "?")
    bd_mm  = results.get("beam_diameter_at_cell_exit_mm", "?")
    clip   = results.get("no_clipping", "?")
    abs_p  = results.get("absorption_pct", "?")
    win_t  = results.get("window_transmission_pct", "?")
    i_ua   = results.get("photodiode_current_ua", "?")
    p_n2   = results.get("P_N2_Torr", "?")

    print(f"\n  Key Results (P_N2 = {p_n2:.1f} Torr):")
    print(f"    Beam diam at cell exit : {bd_mm:.3f} mm   no_clipping = {clip}")
    print(f"    Absorption             : {abs_p:.2f} %")
    print(f"    Window transmission    : {win_t:.2f} %")
    print(f"    Power at detector      : {pd_uw:.2f} µW")
    print(f"    Photodiode current     : {i_ua:.2f} µA")
    print(f"    Shot-noise SNR         : {snr:.0f}")

    if passed:
        print(f"\n  PASSED ({len(passed)})")
        for p in passed:
            print(f"    PASS  {p}")

    if warnings:
        print(f"\n  WARNINGS ({len(warnings)})")
        for w in warnings:
            print(f"    WARN  {w}")

    if failed:
        print(f"\n  FAILED ({len(failed)})")
        for f in failed:
            print(f"    FAIL  {f}")

    print()
    print("=" * width)
    if failed:
        print("  VERDICT:  FAIL")
        print("  ACTION:   Fix optical path — SNR or power target not met.")
        print("=" * width)
        return False
    elif warnings:
        print("  VERDICT:  MARGINAL PASS")
        print("  ACTION:   Review warnings. Proceed to 08_allan with caution.")
        print("=" * width)
        return True
    else:
        print("  VERDICT:  PASS")
        print("  ACTION:   Proceed to 08_allan.")
        print(f"  NOTE:     SNR = {snr:.0f} feeds directly into ADEV formula.")
        print("=" * width)
        return True


if __name__ == "__main__":
    results, error = load_results()
    if results is None:
        print(f"\n  [NOT RUN]  {error}")
        sys.exit(2)

    passed, failed, warnings = grade(results)
    ok = report(results, passed, failed, warnings)
    sys.exit(0 if ok else 1)
