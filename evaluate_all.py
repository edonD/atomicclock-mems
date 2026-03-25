"""
MASTER EVALUATOR — CSAC MEMS
==============================
Runs all module evaluators in wave order.
Stops at any wave that fails — does not evaluate downstream modules.

Usage:
    python evaluate_all.py           # run all waves
    python evaluate_all.py --wave 1  # run only Wave 1
    python evaluate_all.py --wave 2  # run only Wave 2

EXIT 0 = all evaluated waves PASS
EXIT 1 = at least one FAIL found
EXIT 2 = modules not run yet (sim.py not implemented)
"""

import sys
import os
import subprocess
import argparse

ROOT = os.path.dirname(os.path.abspath(__file__))

# ─────────────────────────────────────────────────────────────────────────────
# WAVE DEFINITIONS
# ─────────────────────────────────────────────────────────────────────────────

WAVES = {
    1: {
        "name": "Wave 1 — Foundation (parallel, no dependencies)",
        "modules": [
            ("00_atomic_model",  "evaluator.py", "QuTiP CPT physics"),
            ("03_mems_geometry", "evaluator.py", "Elmer FEM structural"),
        ],
        "gate": "Both must PASS before Wave 2 can run",
    },
    2: {
        "name": "Wave 2 — Module physics (parallel, after Wave 1)",
        "modules": [
            ("01_vcsel_sideband", "evaluator.py", "VCSEL sideband spectrum"),
            ("02_buffer_gas",     "evaluator.py", "N2 buffer gas optimization"),
            ("04_thermal",        "evaluator.py", "Thermal management FEM"),
            ("05_optical",        "evaluator.py", "Optical beam propagation"),
            ("06_rf_synthesis",   "evaluator.py", "RF PLL synthesis"),
        ],
        "gate": "All must PASS before Wave 3 can run",
    },
    3: {
        "name": "Wave 3 — System integration (after Wave 2)",
        "modules": [
            ("07_servo_loop", "evaluator.py", "Servo loop stability"),
            ("08_allan",      "evaluator.py", "Allan deviation — PERFORMANCE GATE"),
        ],
        "gate": "Both must PASS before Wave 4 can run",
    },
    4: {
        "name": "Wave 4 — Full system (after Wave 3)",
        "modules": [
            ("09_fullchain", "evaluator.py", "End-to-end integration — PHASE 2 GATE"),
        ],
        "gate": "Must PASS to authorize Phase 2 (design package + foundry submission)",
    },
}


# ─────────────────────────────────────────────────────────────────────────────
# RUN ONE EVALUATOR
# ─────────────────────────────────────────────────────────────────────────────

def run_evaluator(module_dir, evaluator_file):
    """Run a single evaluator subprocess. Returns (exit_code, stdout)."""
    evaluator_path = os.path.join(ROOT, module_dir, evaluator_file)

    if not os.path.exists(evaluator_path):
        return -1, f"evaluator.py not found in {module_dir}/"

    result = subprocess.run(
        [sys.executable, evaluator_path],
        capture_output=True,
        text=True
    )
    output = result.stdout + result.stderr
    return result.returncode, output


# ─────────────────────────────────────────────────────────────────────────────
# RUN ONE WAVE
# ─────────────────────────────────────────────────────────────────────────────

def run_wave(wave_num):
    """Run all evaluators in a wave. Returns True if wave passes."""
    wave = WAVES[wave_num]
    width = 72

    print()
    print("█" * width)
    print(f"  {wave['name']}")
    print("█" * width)

    wave_passed   = True
    wave_notrun   = False
    module_results = {}

    for module_dir, evaluator_file, description in wave["modules"]:
        print(f"\n  Running: {module_dir}  ({description})")
        print("  " + "─" * 60)

        exit_code, output = run_evaluator(module_dir, evaluator_file)

        # Print evaluator output indented
        for line in output.splitlines():
            print("  " + line)

        if exit_code == 0:
            module_results[module_dir] = "PASS"
        elif exit_code == 2:
            module_results[module_dir] = "NOT RUN"
            wave_notrun = True
        else:
            module_results[module_dir] = "FAIL"
            wave_passed = False

    # Wave summary
    print()
    print("─" * width)
    print(f"  WAVE {wave_num} SUMMARY")
    print("─" * width)
    for mod, verdict in module_results.items():
        icon = "✓" if verdict == "PASS" else ("?" if verdict == "NOT RUN" else "✗")
        print(f"    {icon} {mod:<30}  {verdict}")
    print()

    if wave_notrun:
        print(f"  WAVE {wave_num}: INCOMPLETE — some simulations not run yet")
        print(f"  Run sim.py files first, then re-run evaluate_all.py")
    elif wave_passed:
        print(f"  WAVE {wave_num}: PASS ✓  Gate: {wave['gate']}")
    else:
        print(f"  WAVE {wave_num}: FAIL ✗")
        print(f"  BLOCKED: subsequent waves will not run.")
        print(f"  FIX:     Return to failing module, correct simulation, re-run.")

    print("─" * width)
    return wave_passed and not wave_notrun


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="CSAC MEMS Master Evaluator")
    parser.add_argument("--wave", type=int, choices=[1, 2, 3, 4], default=None,
                        help="Run only this wave number")
    args = parser.parse_args()

    width = 72
    print()
    print("=" * width)
    print("  CSAC MEMS — MASTER EVALUATOR")
    print("  Chip-Scale Atomic Clock | Rb-87 CPT | Defense Timing")
    print("  Benchmark: Microchip SA65  ADEV = 2.5×10⁻¹⁰ @ 1s  |  120 mW")
    print("=" * width)

    if args.wave is not None:
        # Run single wave
        run_wave(args.wave)
        return

    # Run all waves in order, stop if a wave fails
    overall_passed = True
    for wave_num in [1, 2, 3, 4]:
        passed = run_wave(wave_num)
        if not passed:
            overall_passed = False
            print()
            print("=" * width)
            print(f"  STOPPED at Wave {wave_num}.")
            print(f"  Waves {wave_num+1}+ not evaluated (depend on Wave {wave_num} passing).")
            print("=" * width)
            break

    if overall_passed:
        print()
        print("=" * width)
        print("  ALL WAVES PASS — PHASE 1 COMPLETE")
        print()
        print("  PHASE 2 AUTHORIZED:")
        print("    design/spec_sheet.md       ← compile from all results.md")
        print("    design/process_traveler.md ← step-by-step fab instructions")
        print("    design/mask_layout/        ← run csac_cell_v1.py → GDS-II")
        print("    design/fto_brief.md        ← send to patent attorney")
        print()
        print("  FOUNDRY CONTACT:")
        print("    MEMSCAP:         info@memscap.com")
        print("    EPFL CMi:        cmi@epfl.ch")
        print("    CMC Microsystems: mems@cmc.ca")
        print("=" * width)

    sys.exit(0 if overall_passed else 1)


if __name__ == "__main__":
    main()
