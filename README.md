# CSAC MEMS — Chip-Scale Atomic Clock
## Microfabricated Rb-87 Vapor Cell | CPT Architecture | Defense-Grade Timing

---

## What This Is

A MEMS chip-scale atomic clock (CSAC) based on Coherent Population Trapping (CPT)
in a microfabricated Rb-87 vapor cell. The physics: a modulated VCSEL creates two
coherent optical sidebands that drive a 3-level Lambda system in Rb-87 atoms. When
modulation frequency = half the hyperfine splitting (3.417341305 GHz), atoms go dark.
Lock an oscillator to that dark resonance = atomic frequency reference.

**Target performance:**
- Allan deviation @ 1s  :  < 5×10⁻¹⁰
- Allan deviation @ 1hr :  < 1×10⁻¹¹
- Power consumption     :  < 150 mW
- Cell footprint        :  ~2×2×2 mm
- Reference benchmark   :  Microchip SA65 CSAC

---

## The Evaluator Is the Design

Every simulation module contains an `evaluator.py`. This is not optional and not
a formality. The evaluator grades simulation results against published benchmarks
from real products (Microchip SA65, NIST ASD, Vanier & Audoin textbook). If the
evaluator fails, you do not proceed. The strength of the design equals the toughness
of the evaluation.

**Grading system used in every evaluator:**

```
PASS      — within target, margin confirmed, proceed
MARGINAL  — within target but no margin, flag for review
FAIL      — outside target, stop, do not proceed to next wave
```

Run the master evaluator at any time to see overall project status:
```
python evaluate_all.py
```

---

## Folder Structure

```
atomicclock-mems/
│
├── README.md                        ← this file
├── evaluate_all.py                  ← master evaluator: runs all waves in order
│
├── requirements/                    ← SOFTWARE INSTALLATION
│   ├── README.md                    ← start here: what to install and why
│   ├── 01_python.md                 ← Python packages (pip install)
│   ├── 02_elmer_fem.md              ← Elmer FEM + FreeCAD (free FEM solver)
│   └── 03_klayout_gdstk.md          ← KLayout + gdstk (mask layout)
│
├── ── WAVE 1 ── (run in parallel, no dependencies) ──────────────────────────
│
├── 00_atomic_model/                 ← [WAVE 1] FOUNDATION
│   ├── requirements.md              ← questions to answer, inputs needed
│   ├── sim.py                       ← QuTiP: Rb-87 levels + CPT density matrix
│   ├── evaluator.py                 ← grades against NIST + SA65 benchmarks
│   └── results.md                   ← extracted numbers (filled after sim runs)
│
├── 03_mems_geometry/                ← [WAVE 1] MEMS STRUCTURE (FEM)
│   ├── requirements.md
│   ├── sim.sif                      ← Elmer FEM input file (structural + thermal)
│   ├── geometry.FCStd               ← FreeCAD geometry file
│   ├── evaluator.py                 ← grades stress, dimensions, resonances
│   └── results.md
│
├── ── WAVE 2 ── (after Wave 1, run in parallel) ─────────────────────────────
│
├── 01_vcsel_sideband/               ← [WAVE 2] needs: 00
│   ├── requirements.md
│   ├── sim.py                       ← SciPy Bessel: VCSEL modulation spectrum
│   ├── evaluator.py                 ← grades beta, sideband power, RF drive
│   └── results.md
│
├── 02_buffer_gas/                   ← [WAVE 2] needs: 00 + 03
│   ├── requirements.md
│   ├── sim.py                       ← N2 broadening, optimal pressure
│   ├── evaluator.py                 ← grades N2 pressure, linewidth, shift
│   └── results.md
│
├── 04_thermal/                      ← [WAVE 2] needs: 03 (FEM)
│   ├── requirements.md
│   ├── sim.sif                      ← Elmer FEM thermal analysis
│   ├── evaluator.py                 ← grades heater power, stability, RTD
│   └── results.md
│
├── 05_optical/                      ← [WAVE 2] needs: 03
│   ├── requirements.md
│   ├── sim.py                       ← ABCD beam propagation + absorption
│   ├── evaluator.py                 ← grades absorption, beam clipping, SNR
│   └── results.md
│
├── 06_rf_synthesis/                 ← [WAVE 2] needs: 00
│   ├── requirements.md
│   ├── sim.py                       ← PLL model, VCO tuning, phase noise
│   ├── evaluator.py                 ← grades lock range, phase noise, resolution
│   └── results.md
│
├── ── WAVE 3 ── (after Wave 2) ──────────────────────────────────────────────
│
├── 07_servo_loop/                   ← [WAVE 3] needs: 00 + 05 + 06
│   ├── requirements.md
│   ├── sim.py                       ← python-control: PID + lock-in model
│   ├── evaluator.py                 ← grades phase margin, gain margin, bandwidth
│   └── results.md
│
├── 08_allan/                        ← [WAVE 3] needs: 00 + 05 + 07
│   ├── requirements.md
│   ├── sim.py                       ← allantools: Allan deviation prediction
│   ├── evaluator.py                 ← grades ADEV vs SA65 benchmark
│   └── results.md
│
├── ── WAVE 4 ── (after Wave 3) ──────────────────────────────────────────────
│
├── 09_fullchain/                    ← [WAVE 4] needs: everything
│   ├── requirements.md
│   ├── sim.py                       ← end-to-end integrated simulation
│   ├── evaluator.py                 ← final go/no-go: all specs must pass
│   └── results.md
│
├── ── PHASE 2: DESIGN OUTPUTS ───────────────────────────────────────────────
│
└── design/                          ← compiled from all results.md files
    ├── spec_sheet.md                ← performance spec (for investors + foundry)
    ├── process_traveler.md          ← step-by-step fab instructions (for foundry)
    ├── bom.md                       ← bill of materials (for purchasing)
    ├── fto_brief.md                 ← patent FTO summary (for attorney)
    └── mask_layout/                 ← GDS-II chip layout files
        ├── README.md
        ├── csac_cell_v1.py          ← gdstk Python script (generates GDS-II)
        ├── csac_cell_v1.gds         ← output GDS-II file (send to foundry)
        └── screenshots/             ← layout images for documentation
```

---

## Execution Order

```
STEP 1 — Install software
    → read requirements/README.md
    → follow requirements/01_python.md + 02_elmer_fem.md + 03_klayout_gdstk.md

STEP 2 — Wave 1 (parallel)
    → python 00_atomic_model/sim.py
    → elmer 03_mems_geometry/sim.sif          (run Elmer FEM)
    → python 00_atomic_model/evaluator.py
    → python 03_mems_geometry/evaluator.py
    → BOTH must PASS before Wave 2

STEP 3 — Wave 2 (parallel, after Wave 1 passes)
    → python 01_vcsel_sideband/sim.py
    → python 02_buffer_gas/sim.py
    → elmer 04_thermal/sim.sif
    → python 05_optical/sim.py
    → python 06_rf_synthesis/sim.py
    → run all evaluators
    → ALL must PASS before Wave 3

STEP 4 — Wave 3 (after Wave 2 passes)
    → python 07_servo_loop/sim.py
    → python 08_allan/sim.py
    → run evaluators

STEP 5 — Wave 4 (after Wave 3 passes)
    → python 09_fullchain/sim.py
    → python 09_fullchain/evaluator.py
    → PASS here = proceed to Phase 2

STEP 6 — Phase 2: Design Package
    → compile design/spec_sheet.md from all results.md
    → compile design/process_traveler.md
    → run design/mask_layout/csac_cell_v1.py  (generates GDS-II)
    → compile design/bom.md
    → send design/fto_brief.md to patent attorney
```

Or run everything automatically:
```
python evaluate_all.py
```

---

## Benchmark Reference

All evaluators grade against these published references:

| Source | Used for |
|---|---|
| NIST ASD (Rb-87 spectroscopy) | Atomic constants, wavelengths |
| Microchip SA65 CSAC datasheet | CPT linewidth, contrast, ADEV, power |
| Vanier & Audoin (textbook) | Buffer gas collision data |
| Knappe et al. (NIST, 2004) | MEMS cell geometry validation |
| IEEE UFFC (CPT CSAC papers) | Servo loop, Allan deviation |

---

## Dependencies Between Modules

```
00_atomic_model ──────────────────────────────────┐
    └──→ 01_vcsel_sideband                         │
    └──→ 06_rf_synthesis                           │
    └──→ 07_servo_loop (partial)                   │
    └──→ 08_allan                                  │
                                                   │
03_mems_geometry ─────────────────────────────────┤
    └──→ 02_buffer_gas                             │
    └──→ 04_thermal                                │
    └──→ 05_optical ──────────────────────────────┤
                                                   │
        07_servo_loop ← (00 + 05 + 06) ───────────┤
        08_allan      ← (00 + 05 + 07) ───────────┤
                                                   │
        09_fullchain  ← (everything) ─────────────┘
```

---

## What Phase 1 Produces (inputs to Phase 2)

| Module | Number extracted | Goes into |
|---|---|---|
| 00_atomic_model | CPT linewidth (kHz), contrast (%), laser power (µW) | spec_sheet, process_traveler |
| 01_vcsel_sideband | Modulation index β, RF drive power (dBm) | spec_sheet, bom |
| 02_buffer_gas | N2 fill pressure (Torr) | process_traveler |
| 03_mems_geometry | Cavity diameter (mm), depth (mm), wall thickness (mm) | mask_layout, process_traveler |
| 04_thermal | Heater resistance (Ω), PID gains, power (mW) | mask_layout, process_traveler, spec_sheet |
| 05_optical | Beam diameter (mm), window thickness (mm), absorption depth | mask_layout, process_traveler |
| 06_rf_synthesis | VCO tuning range (MHz), PLL divider, phase noise (dBc/Hz) | spec_sheet, bom |
| 07_servo_loop | PID coefficients, lock bandwidth (Hz) | spec_sheet |
| 08_allan | Predicted ADEV @ 1s, 100s, 1hr | spec_sheet |
| 09_fullchain | Go/No-Go: full system meets all specs | everything |
