"""
EVALUATOR: 00_atomic_model
==========================
Wave 1 — must PASS before any Wave 2 module runs.

Grades simulation results against:
  - NIST Rb-87 spectroscopic constants (physics correctness)
  - Microchip SA65 CSAC published performance (product benchmark)
  - Theoretical CPT dark state conditions (internal consistency)

EXIT 0 = PASS  — proceed to Wave 2
EXIT 1 = FAIL  — fix simulation, do not proceed
"""

import sys
import os

# ─────────────────────────────────────────────────────────────────────────────
# BENCHMARKS
# These are the numbers the simulation MUST reproduce or beat.
# They come from published sources — not internal targets.
# ─────────────────────────────────────────────────────────────────────────────

BENCHMARKS = {

    # Physics correctness — must match NIST to prove the model is right
    "hyperfine_hz": {
        "description": "Rb-87 ground state hyperfine splitting",
        "target": 6_834_682_610.904,
        "tolerance_ppm": 0.01,          # 0.01 ppm = 68 Hz tolerance
        "source": "NIST 2021 Rb-87 constants",
        "critical": True,               # FAIL if this is wrong — model is broken
    },

    "d1_wavelength_nm": {
        "description": "D1 transition wavelength",
        "target": 794.978851156,
        "tolerance_pm": 1.0,            # 1 pm tolerance
        "source": "NIST ASD",
        "critical": True,
    },

    "natural_linewidth_mhz": {
        "description": "5P1/2 natural linewidth Γ/2π",
        "target": 5.746,
        "tolerance_pct": 1.0,           # 1% tolerance
        "source": "NIST (lifetime 27.70 ns)",
        "critical": True,
    },

    # CPT performance — must beat or match commercial product
    "cpt_linewidth_khz": {
        "description": "CPT resonance FWHM linewidth",
        "target_max": 5.0,              # must be BELOW this
        "benchmark": "3–5 kHz",
        "source": "Microchip SA65 CSAC datasheet",
        "critical": True,
        "note": "Broader linewidth = worse clock stability. 5 kHz is the ceiling.",
    },

    "cpt_contrast_pct": {
        "description": "CPT transparency contrast (signal depth)",
        "target_min": 3.0,              # must be ABOVE this
        "benchmark": "3–8%",
        "source": "Microchip SA65 CSAC datasheet",
        "critical": True,
        "note": "Lower contrast = worse SNR = worse ADEV. 3% is the floor.",
    },

    "dark_state_verified": {
        "description": "Dark state |D⟩ forms: population trapped in non-absorbing superposition",
        "target": True,
        "source": "CPT theory (Arimondo 1996)",
        "critical": True,
    },

    "clock_transition_verified": {
        "description": "mF=0 ↔ mF=0 transition is first-order Zeeman insensitive",
        "target": True,
        "source": "Rb-87 quantum mechanics",
        "critical": True,
    },

    # Performance margins — not critical but tracked
    "discriminator_slope_relative": {
        "description": "Discriminator slope sufficient for servo lock",
        "target_min": 0.5,              # relative units — must be positive and non-trivial
        "source": "Internal design requirement",
        "critical": False,
    },

    "optimal_laser_power_uw": {
        "description": "Optimal power per beam at CPT peak",
        "target_min": 10,               # µW — must be achievable with VCSEL
        "target_max": 500,              # µW — must not saturate
        "source": "VCSEL practical range",
        "critical": False,
    },
}

# ─────────────────────────────────────────────────────────────────────────────
# LOAD RESULTS
# sim.py writes results to a dict called RESULTS at module level.
# ─────────────────────────────────────────────────────────────────────────────

def load_results():
    """Import sim.py and extract RESULTS dict."""
    sim_path = os.path.join(os.path.dirname(__file__), "sim.py")

    if not os.path.exists(sim_path):
        return None, "sim.py not found"

    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("sim", sim_path)
        if spec is None or spec.loader is None:
            return None, "could not load sim.py spec"
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)  # type: ignore[union-attr]

        if not hasattr(module, "RESULTS"):
            return None, "sim.py ran but did not define RESULTS dict"

        return module.RESULTS, None

    except NotImplementedError:
        return None, "sim.py exists but is not implemented yet (NotImplementedError)"
    except Exception as e:
        return None, f"sim.py crashed: {e}"


# ─────────────────────────────────────────────────────────────────────────────
# GRADER
# ─────────────────────────────────────────────────────────────────────────────

def grade(results):
    passed   = []
    failed   = []
    warnings = []

    # ── Hyperfine splitting ──
    b = BENCHMARKS["hyperfine_hz"]
    val = results.get("hyperfine_hz")
    if val is None:
        failed.append(f"hyperfine_hz: NOT IN RESULTS")
    else:
        error_ppm = abs(val - b["target"]) / b["target"] * 1e6
        if error_ppm <= b["tolerance_ppm"]:
            passed.append(f"hyperfine_hz: {val:.3f} Hz  (error {error_ppm:.4f} ppm)  ✓")
        else:
            failed.append(
                f"hyperfine_hz: {val:.3f} Hz  (error {error_ppm:.4f} ppm, "
                f"limit {b['tolerance_ppm']} ppm) — model is wrong, check Hamiltonian"
            )

    # ── D1 wavelength ──
    b = BENCHMARKS["d1_wavelength_nm"]
    val = results.get("d1_wavelength_nm")
    if val is None:
        failed.append("d1_wavelength_nm: NOT IN RESULTS")
    else:
        error_pm = abs(val - b["target"]) * 1000
        if error_pm <= b["tolerance_pm"]:
            passed.append(f"d1_wavelength_nm: {val:.6f} nm  (error {error_pm:.3f} pm)  ✓")
        else:
            failed.append(f"d1_wavelength_nm: {val:.6f} nm  (error {error_pm:.3f} pm, limit {b['tolerance_pm']} pm)")

    # ── Natural linewidth ──
    b = BENCHMARKS["natural_linewidth_mhz"]
    val = results.get("natural_linewidth_mhz")
    if val is None:
        warnings.append("natural_linewidth_mhz: NOT IN RESULTS")
    else:
        error_pct = abs(val - b["target"]) / b["target"] * 100
        if error_pct <= b["tolerance_pct"]:
            passed.append(f"natural_linewidth_mhz: {val:.4f} MHz  (error {error_pct:.3f}%)  ✓")
        else:
            failed.append(f"natural_linewidth_mhz: {val:.4f} MHz  (error {error_pct:.2f}%, limit {b['tolerance_pct']}%)")

    # ── CPT linewidth ──
    b = BENCHMARKS["cpt_linewidth_khz"]
    val = results.get("cpt_linewidth_khz")
    if val is None:
        failed.append("cpt_linewidth_khz: NOT IN RESULTS")
    else:
        if val <= b["target_max"]:
            margin = b["target_max"] - val
            if margin > 1.0:
                passed.append(f"cpt_linewidth_khz: {val:.2f} kHz  (limit {b['target_max']} kHz, margin {margin:.2f} kHz)  ✓")
            else:
                warnings.append(f"cpt_linewidth_khz: {val:.2f} kHz  MARGINAL — only {margin:.2f} kHz below limit")
        else:
            failed.append(
                f"cpt_linewidth_khz: {val:.2f} kHz  EXCEEDS limit {b['target_max']} kHz — "
                f"increase N2 pressure or reduce cell size. Benchmark: {b['benchmark']}"
            )

    # ── CPT contrast ──
    b = BENCHMARKS["cpt_contrast_pct"]
    val = results.get("cpt_contrast_pct")
    if val is None:
        failed.append("cpt_contrast_pct: NOT IN RESULTS")
    else:
        if val >= b["target_min"]:
            margin = val - b["target_min"]
            if margin > 1.0:
                passed.append(f"cpt_contrast_pct: {val:.2f}%  (min {b['target_min']}%, margin {margin:.2f}%)  ✓")
            else:
                warnings.append(f"cpt_contrast_pct: {val:.2f}%  MARGINAL — only {margin:.2f}% above floor")
        else:
            failed.append(
                f"cpt_contrast_pct: {val:.2f}%  BELOW floor {b['target_min']}% — "
                f"increase laser power or reduce decoherence. Benchmark: {b['benchmark']}"
            )

    # ── Dark state ──
    val = results.get("dark_state_verified")
    if val is True:
        passed.append("dark_state_verified: dark state confirmed  ✓")
    elif val is False:
        failed.append("dark_state_verified: FAILED — dark state not forming, check Lambda system setup")
    else:
        warnings.append("dark_state_verified: NOT IN RESULTS")

    # ── Clock transition ──
    val = results.get("clock_transition_verified")
    if val is True:
        passed.append("clock_transition_verified: mF=0↔mF=0 transition confirmed field-independent  ✓")
    elif val is False:
        failed.append("clock_transition_verified: FAILED — wrong transition selected")
    else:
        warnings.append("clock_transition_verified: NOT IN RESULTS")

    # ── Laser power ──
    b = BENCHMARKS["optimal_laser_power_uw"]
    val = results.get("optimal_laser_power_uw")
    if val is not None:
        if b["target_min"] <= val <= b["target_max"]:
            passed.append(f"optimal_laser_power_uw: {val:.1f} µW  (range {b['target_min']}–{b['target_max']} µW)  ✓")
        else:
            warnings.append(f"optimal_laser_power_uw: {val:.1f} µW  outside practical VCSEL range {b['target_min']}–{b['target_max']} µW")

    return passed, failed, warnings


# ─────────────────────────────────────────────────────────────────────────────
# REPORT
# ─────────────────────────────────────────────────────────────────────────────

def report(passed, failed, warnings):
    width = 70
    print()
    print("=" * width)
    print("  EVALUATOR: 00_atomic_model")
    print("  Wave 1 Gate — CPT Physics Validation")
    print("=" * width)

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
        print("  ACTION:   Fix simulation. Do NOT proceed to Wave 2.")
        print("  REASON:   Critical physics parameters outside acceptable range.")
        print("            A clock built on this model will not meet specs.")
        print("=" * width)
        return False
    elif warnings:
        print("  VERDICT:  MARGINAL")
        print("  ACTION:   Review warnings. Proceeding is allowed but risky.")
        print("            Low-margin parameters will amplify errors downstream.")
        print("=" * width)
        return True
    else:
        print("  VERDICT:  PASS")
        print("  ACTION:   Proceed to Wave 2.")
        print("            01_vcsel_sideband, 02_buffer_gas, 06_rf_synthesis")
        print("            can now start (all depend on this module).")
        print("=" * width)
        return True


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("\nLoading sim.py results...")
    results, error = load_results()

    if results is None:
        print(f"\n  [NOT RUN]  {error}")
        print("  Run sim.py first:  python 00_atomic_model/sim.py")
        print("  Then re-run:       python 00_atomic_model/evaluator.py")
        sys.exit(2)

    passed, failed, warnings = grade(results)
    ok = report(passed, failed, warnings)
    sys.exit(0 if ok else 1)
