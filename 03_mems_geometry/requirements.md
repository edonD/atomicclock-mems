# 03_mems_geometry — Requirements

**WAVE 1 | Tool: Elmer FEM + FreeCAD | No dependencies**

---

## Questions This Simulation Must Answer

1. What cavity diameter and depth gives sufficient optical absorption (α·L > 0.1)?
2. Does the glass-Si-glass stack survive thermal cycling (-40°C to +85°C) without cracking?
3. What is the stress at the anodic bond interface at extreme temperatures?
4. Are there mechanical resonance modes in the 20 Hz – 2 kHz vibration band (must avoid)?
5. What die size is needed including bonding ring and heater traces?

---

## Inputs Required

All material properties are fixed. No module dependencies.

| Parameter | Value | Source |
|---|---|---|
| Si Young's modulus | 170 GPa | Standard |
| Si Poisson ratio | 0.28 | Standard |
| Si CTE | 2.6 ppm/K | Standard |
| Borofloat 33 Young's modulus | 63 GPa | Schott datasheet |
| Borofloat 33 Poisson ratio | 0.20 | Schott datasheet |
| Borofloat 33 CTE | 3.25 ppm/K | Schott datasheet |
| Anodic bond strength | ~10 MPa | Literature (Wallis & Pomerantz 1969) |
| Safety factor target | 3× | Internal design rule |
| Allowable bond stress | 3.3 MPa | = 10 MPa / 3 |
| Temperature range | -40°C to +85°C | MIL-STD-810 defense requirement |

---

## Geometry to Model (FreeCAD + Elmer)

```
  ┌─────────────────────────────────────────┐
  │  Top glass (Borofloat 33)   0.3 mm      │  ← optical window
  ├─────────────────────────────────────────┤  ← anodic bond (top)
  │  Si wafer with etched cavity   1.0 mm   │
  │         ┌───────────┐                   │
  │         │  Rb + N2  │  ← DRIE cavity    │
  │         │           │                   │
  │         └───────────┘                   │
  ├─────────────────────────────────────────┤  ← anodic bond (bottom)
  │  Bottom glass (Borofloat 33)   0.3 mm   │  ← optical window
  └─────────────────────────────────────────┘
```

Parameter sweep:
- Cavity diameter: 1.0 mm to 2.0 mm (step 0.25 mm)
- Cavity depth:    0.5 mm to 1.5 mm (step 0.25 mm)
- Glass thickness: 0.3 mm to 0.5 mm (step 0.1 mm)

---

## What to Simulate

### Analysis A: Thermal stress (Elmer, LinearElasticity solver)
- Apply ΔT = +65°C (room temp 20°C → cell operating at 85°C)
- Apply ΔT = -60°C (room temp 20°C → cold soak at -40°C)
- Extract: von Mises stress at bond interface (MPa)
- Extract: max principal stress in glass windows (MPa)
- Extract: deformation (µm)

### Analysis B: Modal analysis (Elmer, EigenAnalysis)
- Find first 10 resonance frequencies
- Must have no modes in 20 Hz – 2000 Hz band
- (Vibration in this band excites cell motion → frequency noise)

### Analysis C: Optical path (geometric)
- Compute absorption: α·L = n_Rb · σ_D1 · L_cavity
- n_Rb at 85°C from Antoine equation
- σ_D1 = absorption cross section at 795 nm
- Target: α·L > 0.1 (sufficient signal)
- Target: α·L < 3.0 (cell not completely opaque)

---

## Output to Extract into results.md

```
Cavity diameter (optimal)    : _____ mm
Cavity depth (optimal)       : _____ mm
Glass thickness              : _____ mm
Bond interface stress (85°C) : _____ MPa   must be < 3.3 MPa
Bond interface stress (-40°C): _____ MPa   must be < 3.3 MPa
Safety factor (worst case)   : _____       must be > 3.0
Lowest resonance frequency   : _____ Hz    must be > 2000 Hz
Alpha*L (absorption product) : _____       must be 0.1 to 3.0
Die size (total)             : _____ × _____ mm
```

---

## Evaluation Gate

Run `python evaluator.py` after FEM analysis completes.
Must achieve PASS before proceeding to Wave 2 (02, 04, 05 all depend on this).
