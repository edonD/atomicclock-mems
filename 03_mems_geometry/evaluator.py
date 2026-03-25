"""
EVALUATOR: 03_mems_geometry
============================
Wave 1 — must PASS before Wave 2 modules 02, 04, 05 run.

Grades FEM results against:
  - Bond strength literature (Wallis & Pomerantz 1969, ~10 MPa)
  - MIL-STD-810 thermal cycling range (-40 to +85°C)
  - CSAC published cell geometry (Knappe et al. NIST 2004)
  - Optical absorption requirements for CPT signal

EXIT 0 = PASS
EXIT 1 = FAIL
"""

import sys
import os

BENCHMARKS = {

    "bond_stress_mpa": {
        "description": "Von Mises stress at anodic bond interface (worst case temperature)",
        "target_max": 3.3,              # MPa — safety factor 3x vs 10 MPa bond strength
        "bond_strength_mpa": 10.0,      # literature: Wallis & Pomerantz 1969
        "safety_factor_min": 3.0,
        "source": "Wallis & Pomerantz (1969), anodic bond strength ~10 MPa",
        "critical": True,
        "note": "Exceeding this = bond cracks under thermal cycling. Wafer run wasted.",
    },

    "safety_factor": {
        "description": "Bond strength / max stress safety factor",
        "target_min": 3.0,
        "source": "Internal design rule (industry standard for MEMS hermetic packages)",
        "critical": True,
    },

    "lowest_resonance_hz": {
        "description": "Lowest mechanical resonance frequency of cell structure",
        "target_min": 2000,             # Hz — must be above vibration environment
        "source": "MIL-STD-810G vibration spectrum (ground vehicle: 20–2000 Hz)",
        "critical": True,
        "note": "Resonance in vibration band = frequency modulation of CPT signal = noise",
    },

    "alpha_L": {
        "description": "Optical absorption product α·L at 85°C",
        "target_min": 0.1,              # too small = weak CPT signal
        "target_max": 3.0,              # too large = opaque cell, no light gets through
        "source": "Knappe et al. NIST (2004), standard CSAC cell design",
        "critical": True,
        "note": "α·L ~ 1 is optimal. <0.1 = no signal. >3 = cell too opaque for CPT.",
    },

    "cavity_depth_mm": {
        "description": "DRIE etch depth (optical path length)",
        "target_min": 0.5,
        "target_max": 1.5,
        "benchmark": "~1.0 mm typical for CSAC cells",
        "source": "Knappe et al. NIST (2004), SA65 cell geometry",
        "critical": False,
    },

    "cavity_diameter_mm": {
        "description": "Cavity diameter",
        "target_min": 1.0,
        "target_max": 2.0,
        "benchmark": "~1.5 mm typical for CSAC cells",
        "source": "Knappe et al. NIST (2004)",
        "critical": False,
    },

    "die_area_mm2": {
        "description": "Total die area (cell + bonding ring + traces)",
        "target_max": 16.0,             # mm² — 4×4 mm maximum for cost reasons
        "source": "Internal cost target — larger dies cost more per wafer",
        "critical": False,
    },
}


def load_results():
    results_path = os.path.join(os.path.dirname(__file__), "results.md")
    sim_path     = os.path.join(os.path.dirname(__file__), "sim.sif")

    # Try to import a Python results file if it exists
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

    if not os.path.exists(sim_path):
        return None, "sim.sif not found — Elmer FEM not set up yet"

    return None, (
        "Elmer FEM has been set up but fem_results.py not found.\n"
        "  After running Elmer, extract results into fem_results.py\n"
        "  as a RESULTS dict (see requirements.md for field names)."
    )


def grade(results):
    passed   = []
    failed   = []
    warnings = []

    # ── Bond stress ──
    b = BENCHMARKS["bond_stress_mpa"]
    val = results.get("bond_stress_mpa")
    if val is None:
        failed.append("bond_stress_mpa: NOT IN RESULTS")
    else:
        sf = b["bond_strength_mpa"] / val
        if val <= b["target_max"]:
            passed.append(
                f"bond_stress_mpa: {val:.2f} MPa  (safety factor {sf:.1f}×)  ✓"
            )
        else:
            failed.append(
                f"bond_stress_mpa: {val:.2f} MPa  EXCEEDS {b['target_max']} MPa  "
                f"(safety factor only {sf:.1f}×, need {b['safety_factor_min']}×) — "
                f"reduce cavity size or increase glass thickness"
            )

    # ── Safety factor ──
    b = BENCHMARKS["safety_factor"]
    val = results.get("safety_factor")
    if val is not None:
        if val >= b["target_min"]:
            passed.append(f"safety_factor: {val:.1f}×  (min {b['target_min']}×)  ✓")
        else:
            failed.append(f"safety_factor: {val:.1f}×  BELOW minimum {b['target_min']}×")

    # ── Mechanical resonance ──
    b = BENCHMARKS["lowest_resonance_hz"]
    val = results.get("lowest_resonance_hz")
    if val is None:
        failed.append("lowest_resonance_hz: NOT IN RESULTS")
    else:
        if val >= b["target_min"]:
            passed.append(f"lowest_resonance_hz: {val:.0f} Hz  (min {b['target_min']} Hz)  ✓")
        elif val >= 500:
            warnings.append(
                f"lowest_resonance_hz: {val:.0f} Hz  in vibration band — "
                f"clock will be sensitive to mechanical vibration"
            )
        else:
            failed.append(
                f"lowest_resonance_hz: {val:.0f} Hz  FAR inside vibration band — "
                f"redesign geometry to stiffen structure"
            )

    # ── Optical absorption ──
    b = BENCHMARKS["alpha_L"]
    val = results.get("alpha_L")
    if val is None:
        failed.append("alpha_L: NOT IN RESULTS")
    else:
        if b["target_min"] <= val <= b["target_max"]:
            if val >= 0.3:
                passed.append(f"alpha_L: {val:.3f}  (range {b['target_min']}–{b['target_max']})  ✓")
            else:
                warnings.append(
                    f"alpha_L: {val:.3f}  MARGINAL — signal may be weak. "
                    f"Consider increasing cavity depth."
                )
        elif val < b["target_min"]:
            failed.append(
                f"alpha_L: {val:.4f}  TOO LOW (min {b['target_min']}) — "
                f"cell too short, no CPT signal. Increase cavity depth."
            )
        else:
            failed.append(
                f"alpha_L: {val:.2f}  TOO HIGH (max {b['target_max']}) — "
                f"cell too dense/long, light cannot penetrate. "
                f"Reduce Rb amount or cavity depth."
            )

    # ── Cavity dimensions ──
    for key in ["cavity_depth_mm", "cavity_diameter_mm"]:
        b = BENCHMARKS[key]
        val = results.get(key)
        if val is not None:
            if b["target_min"] <= val <= b["target_max"]:
                passed.append(f"{key}: {val:.2f} mm  (range {b['target_min']}–{b['target_max']} mm)  ✓")
            else:
                warnings.append(f"{key}: {val:.2f} mm  outside typical range {b['target_min']}–{b['target_max']} mm")

    # ── Die area ──
    b = BENCHMARKS["die_area_mm2"]
    val = results.get("die_area_mm2")
    if val is not None:
        if val <= b["target_max"]:
            passed.append(f"die_area_mm2: {val:.1f} mm²  (max {b['target_max']} mm²)  ✓")
        else:
            warnings.append(f"die_area_mm2: {val:.1f} mm²  exceeds {b['target_max']} mm² — will increase wafer cost")

    return passed, failed, warnings


def report(passed, failed, warnings):
    width = 70
    print()
    print("=" * width)
    print("  EVALUATOR: 03_mems_geometry")
    print("  Wave 1 Gate — MEMS Structural + Optical Validation")
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
        print("  ACTION:   Redesign cell geometry. Do NOT proceed to Wave 2.")
        print("  REASON:   Structural or optical failure would destroy wafer run.")
        print("=" * width)
        return False
    elif warnings:
        print("  VERDICT:  MARGINAL")
        print("  ACTION:   Review warnings. Recommend iterating geometry before Wave 2.")
        print("=" * width)
        return True
    else:
        print("  VERDICT:  PASS")
        print("  ACTION:   Proceed to Wave 2.")
        print("            02_buffer_gas, 04_thermal, 05_optical can now start.")
        print("  OUTPUTS:  cavity_depth, cavity_diameter → mask_layout, process_traveler")
        print("=" * width)
        return True


if __name__ == "__main__":
    results, error = load_results()

    if results is None:
        print(f"\n  [NOT RUN]  {error}")
        print("  Set up Elmer FEM first: see requirements/02_elmer_fem.md")
        sys.exit(2)

    passed, failed, warnings = grade(results)
    ok = report(passed, failed, warnings)
    sys.exit(0 if ok else 1)
