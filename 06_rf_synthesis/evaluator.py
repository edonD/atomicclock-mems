"""
EVALUATOR: 06_rf_synthesis
Wave 2

Grades the RF synthesis simulation against the specification in requirements.md.

Pass criteria (all must hold):
  1. RESULTS dict is populated with all required keys.
  2. Frequency error < 1 Hz  (PLL resolution adequate).
  3. Tuning range covers pressure shift with at least 2× margin.
  4. VCO ADEV at tau=1s < 1e-10  (phase noise not limiting).
  5. pll_N, pll_F, pll_M are integers with valid ADF4351 ranges.
  6. recommended_chip is a non-empty string.

EXIT 0 = PASS
EXIT 1 = FAIL
"""
import sys
import os

REQUIRED_KEYS = [
    "pll_N",
    "pll_F",
    "pll_M",
    "f_actual_hz",
    "frequency_error_hz",
    "achievable_freq_step_hz",
    "tuning_range_hz",
    "vco_phase_noise_dbc",
    "adev_from_vco_1s",
    "recommended_chip",
]

# Thresholds from requirements.md / program.md
MAX_FREQ_ERROR_HZ       = 1.0           # Hz  — must be < 1 Hz
ADEV_VCO_MAX_1S         = 1e-10         # —    must be < 1e-10 at tau=1s
ADF4351_N_MIN           = 23
ADF4351_N_MAX           = 65535
ADF4351_M_MAX           = 4095
F_TARGET_HZ             = 3_417_341_305.452


def load_results():
    sim_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sim.py")
    if not os.path.exists(sim_path):
        return None, "sim.py not found"
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("sim", sim_path)
        if spec is None or spec.loader is None:
            return None, "could not load sim.py"
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)  # type: ignore[union-attr]
        if not hasattr(module, "RESULTS") or not module.RESULTS:
            return None, "sim.py RESULTS dict is empty — not implemented yet"
        return module.RESULTS, None
    except Exception as e:
        return None, f"sim.py error: {e}"


def check(label, value, condition, detail=""):
    symbol = "PASS" if condition else "FAIL"
    suffix = f"  ({detail})" if detail else ""
    print(f"  [{symbol}]  {label}: {value}{suffix}")
    return condition


if __name__ == "__main__":
    results, error = load_results()

    if results is None:
        print(f"  [NOT RUN]  {error}")
        sys.exit(2)

    print()
    print("=" * 62)
    print("06_rf_synthesis — Evaluator")
    print("=" * 62)

    failures = 0

    # ------------------------------------------------------------------
    # 1. Required keys present
    # ------------------------------------------------------------------
    print("\n--- Required keys ---")
    missing = [k for k in REQUIRED_KEYS if k not in results]
    if missing:
        print(f"  [FAIL]  Missing keys: {missing}")
        failures += len(missing)
    else:
        print(f"  [PASS]  All {len(REQUIRED_KEYS)} required keys present")

    if missing:
        # Cannot proceed with numeric checks if keys are absent
        print(f"\n  TOTAL FAILURES: {failures}")
        sys.exit(1)

    # ------------------------------------------------------------------
    # 2. PLL integer types and valid ADF4351 ranges
    # ------------------------------------------------------------------
    print("\n--- PLL divider validity ---")
    N = results["pll_N"]
    F = results["pll_F"]
    M = results["pll_M"]

    if not check("pll_N type is int", type(N).__name__,
                 isinstance(N, int)):
        failures += 1
    if not check("pll_F type is int", type(F).__name__,
                 isinstance(F, int)):
        failures += 1
    if not check("pll_M type is int", type(M).__name__,
                 isinstance(M, int)):
        failures += 1

    if not check("pll_N in ADF4351 range",
                 f"{N}",
                 ADF4351_N_MIN <= N <= ADF4351_N_MAX,
                 f"allowed {ADF4351_N_MIN}..{ADF4351_N_MAX}"):
        failures += 1
    if not check("pll_F valid (0 <= F < M)",
                 f"{F}",
                 0 <= F < M,
                 f"M={M}"):
        failures += 1
    if not check("pll_M valid (2 <= M <= 4095)",
                 f"{M}",
                 2 <= M <= ADF4351_M_MAX):
        failures += 1

    # ------------------------------------------------------------------
    # 3. Frequency synthesis — error < 1 Hz
    # ------------------------------------------------------------------
    print("\n--- Frequency synthesis ---")
    freq_error = results["frequency_error_hz"]
    f_actual   = results["f_actual_hz"]

    if not check("f_actual close to f_target",
                 f"{f_actual:.4f} Hz",
                 abs(f_actual - F_TARGET_HZ - freq_error) < 1e-3,
                 "consistency: |f_actual - f_target| == frequency_error_hz"):
        failures += 1

    if not check("Frequency error < 1 Hz",
                 f"{freq_error:.4f} Hz",
                 freq_error < MAX_FREQ_ERROR_HZ,
                 f"threshold = {MAX_FREQ_ERROR_HZ} Hz"):
        failures += 1

    step = results["achievable_freq_step_hz"]
    if not check("achievable_freq_step_hz is positive",
                 f"{step:.3f} Hz",
                 step > 0):
        failures += 1

    # ------------------------------------------------------------------
    # 4. Tuning range covers pressure shift (at least 2× margin)
    # ------------------------------------------------------------------
    print("\n--- Tuning range ---")
    tuning_range = results["tuning_range_hz"]
    pressure_hz  = results.get("pressure_shift_hz", None)

    if pressure_hz is not None:
        min_tuning = abs(pressure_hz) * 2.0      # 2× minimum margin
        if not check("Tuning range >= 2× pressure shift",
                     f"{tuning_range/1e3:.2f} kHz",
                     tuning_range >= min_tuning,
                     f"need >= {min_tuning/1e3:.2f} kHz"):
            failures += 1
    else:
        # pressure_shift_hz not in RESULTS — soft check only
        if not check("Tuning range > 0",
                     f"{tuning_range:.0f} Hz",
                     tuning_range > 0):
            failures += 1

    if not check("Tuning range > 0",
                 f"{tuning_range:.0f} Hz",
                 tuning_range > 0):
        failures += 1

    # ------------------------------------------------------------------
    # 5. VCO phase noise / ADEV
    # ------------------------------------------------------------------
    print("\n--- VCO phase noise & ADEV ---")
    s_phi = results["vco_phase_noise_dbc"]
    if not check("vco_phase_noise_dbc == -90.0 dBc/Hz",
                 f"{s_phi:.1f} dBc/Hz",
                 s_phi == -90.0):
        failures += 1

    adev_1s = results["adev_from_vco_1s"]
    if not check("ADEV from VCO at tau=1s < 1e-10",
                 f"{adev_1s:.3e}",
                 adev_1s < ADEV_VCO_MAX_1S,
                 f"threshold = {ADEV_VCO_MAX_1S:.0e}"):
        failures += 1

    margin = ADEV_VCO_MAX_1S / adev_1s if adev_1s > 0 else float("inf")
    print(f"          VCO ADEV margin vs target: {margin:.0f}×")

    # ------------------------------------------------------------------
    # 6. recommended_chip is a non-empty string
    # ------------------------------------------------------------------
    print("\n--- Recommended chip ---")
    chip = results["recommended_chip"]
    if not check("recommended_chip non-empty string",
                 repr(chip),
                 isinstance(chip, str) and len(chip) > 0):
        failures += 1

    # ------------------------------------------------------------------
    # 7. Plots saved
    # ------------------------------------------------------------------
    print("\n--- Plot files ---")
    _plot_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "plots")
    for _fname in ("pll_frequency_error.png", "phase_noise_adev.png"):
        _fpath = os.path.join(_plot_dir, _fname)
        if not check(f"plots/{_fname} exists",
                     "found" if os.path.exists(_fpath) else "missing",
                     os.path.exists(_fpath)):
            failures += 1

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------
    print()
    print("=" * 62)
    if failures == 0:
        print(f"  RESULT: PASS  (0 failures)")
        print()
        print(f"  PLL: N={N}, F={F}, M={M}")
        print(f"  Frequency error : {freq_error:.4f} Hz")
        print(f"  ADEV (VCO, 1s)  : {adev_1s:.3e}  ({margin:.0f}× below limit)")
        print(f"  Tuning range    : {tuning_range/1e3:.1f} kHz")
        print(f"  Chip            : {chip}")
        print("=" * 62)
        sys.exit(0)
    else:
        print(f"  RESULT: FAIL  ({failures} failure(s))")
        print("=" * 62)
        sys.exit(1)
