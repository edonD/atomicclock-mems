# Module 03: MEMS Geometry — Program

## 1. Mission

Find the cavity dimensions (diameter, depth, wall thickness) that simultaneously:
1. Survive thermal cycling -40°C to +85°C without cracking the anodic bond
2. Provide sufficient optical absorption for CPT (α·L > 0.1)
3. Have no mechanical resonances in the 20–2000 Hz vibration band
4. Fit in a die small enough to be cost-effective (< 4×4 mm)

This module runs in Elmer FEM for structural and thermal stress analysis.
The output is not a graph — it is exact numbers in mm that go directly
into the GDS-II mask and the process traveler.

**What "done" means:**

1. `fem_results.py` defines RESULTS dict with all required geometry fields.
2. `python evaluator.py` exits with code 0 (PASS).
3. Bond interface stress < 3.3 MPa at -40°C (safety factor > 3× vs 10 MPa bond strength).
4. α·L absorption product in range 0.1–3.0 at 85°C.
5. No mechanical resonance below 2000 Hz.

---

## 2. State of the Art

### 2.1 Knappe et al. NIST 2004 — Reference Cell Geometry

"A microfabricated atomic clock" (APL 85, 1460) established the standard:
- Cavity: 1 mm × 1 mm × 2 mm (diameter × diameter × depth)
- Glass thickness: 0.5 mm Pyrex
- Si thickness: 1.5 mm total (with 1mm deep cavity)
- Process: DRIE etch + anodic bonding to Pyrex

Their cell survived thermal cycling and showed CPT signal. This is our baseline.
We target a similar geometry but with Borofloat 33 (better CTE match to Si than Pyrex).

### 2.2 Lutwak et al. (Symmetricom, 2007)

Their production CSAC cell (later SA65):
- Cell volume: ~1.5 mm³ internal
- External cell size: ~2×2×2 mm
- Anodic bond: 400°C, 800V, Pyrex to Si

Key finding: thermal gradient across the cell must be < 1°C/mm to prevent
Rb thermophoresis (Rb migrates to cold spot → condenses on window → cell death).

### 2.3 Borofloat 33 vs Pyrex 7740

Both are suitable for anodic bonding to Si. Borofloat 33 is preferred because:
- CTE: Borofloat 3.25 ppm/K vs Pyrex 3.25 ppm/K (identical — both are good)
- Transmission: both > 92% at 795 nm
- Availability: Borofloat available in 0.3 mm thickness from Schott

Si CTE = 2.6 ppm/K, glass CTE = 3.25 ppm/K → mismatch = 0.65 ppm/K.
Over ΔT = 125°C (-40 to +85°C): differential strain ε = 0.65×10⁻⁶ × 125 = 81 ppm.
This strain concentrates at the bond interface and must be below fracture stress.

### 2.4 Honest Assessment

The geometry is simple: a silicon wafer with a DRIE-etched cylindrical cavity,
bonded between two glass wafers. The FEM model is a standard thermal-mechanical
analysis. There are no exotic geometries. The challenge is not the FEM simulation
itself but setting up the mesh correctly and interpreting the results at the bond
interface (stress concentrators at cavity corners).

---

## 3. Physics

### 3.1 Thermal Expansion Mismatch

When the bonded stack is cooled from bonding temperature (350°C) to -40°C,
ΔT = -390°C. The Si contracts less than the glass:

```
Δε = (CTE_glass - CTE_Si) × ΔT = (3.25 - 2.6)×10⁻⁶ × 390 = 253 µm/m
```

This differential strain creates biaxial stress at the bond interface:

```
σ_biaxial ≈ E_eff × Δε / (1 - ν)
```

For thin-film approximation:
```
E_eff = (E_Si × h_Si + E_glass × h_glass) / (h_Si + h_glass)
```

The critical location is the corner of the cavity, where stress concentrates.
FEM resolves the actual stress field — the above is only a sanity check.

### 3.2 Optical Absorption (Beer-Lambert)

At cell operating temperature 85°C = 358 K, Rb vapor density from Antoine equation:

```
log₁₀(P_Rb_Pa) = 9.863 - 4529.6 / T        [T in Kelvin, liquid Rb phase]
P_Rb_Pa = 10^(9.863 - 4529.6/358) = 2.72 Pa

n_Rb = P_Rb / (k_B × T) = 2.72 / (1.38e-23 × 358) = 5.5×10²⁰ m⁻³
```

Absorption cross-section on D1 line:
```
σ_D1 = λ² / (8π × τ_sp) × (2J'+1)/(2J+1) × 1/Δν_D
```

Simplified for our purpose:
```
σ_D1 ≈ 1.1×10⁻¹³ m²   (peak, σ+ polarization, D1 line, Rb-87)
```

Absorption product:
```
α × L = n_Rb × σ_D1 × L_cavity
```

For L = 1 mm = 0.001 m:
```
α × L = 5.5×10²⁰ × 1.1×10⁻¹³ × 0.001 = 0.061
```

This is marginal (target > 0.1). With buffer gas, pressure broadening reduces σ_D1
by the ratio (Γ_nat / Γ_broadened), so the effective α·L is lower. We need L > 1mm
or σ+ polarization optimization. The FEM sweep over cavity depth will find the
minimum depth needed.

### 3.3 Mechanical Resonances

For a rectangular plate of dimensions a×b×h, fundamental resonance:
```
f₁ = (π/2) × sqrt(E × h² / (12 × ρ × (1-ν²))) × (1/a² + 1/b²)
```

For our ~2mm Si cavity structure (rough estimate):
```
f₁ ≈ (π/2) × sqrt(170e9 × (0.001)² / (12 × 2330 × 0.92)) × (1/0.002² + 1/0.002²)
   ≈ 85 kHz
```

This is well above 2000 Hz — we expect to pass this criterion. FEM confirms
the exact value including the cavity void and glass layers.

---

## 4. Implementation

### 4.1 FreeCAD Geometry

Create the glass-Si-glass stack in FreeCAD FEM workbench:

```
Bodies to create:
1. Si_body:      Box 3mm × 3mm × 1.0mm, then cut cylindrical cavity
                 Cavity: Cylinder, diameter 1.5mm, height 1.0mm, centered
2. Glass_bottom: Box 3mm × 3mm × 0.3mm (below Si)
3. Glass_top:    Box 3mm × 3mm × 0.3mm (above Si)

Bonding interfaces:
  Glass_bottom top face → Si bottom face (contact constraint)
  Glass_top bottom face → Si top face (contact constraint)
```

Export to mesh (.unv format) via FreeCAD FEM workbench.

### 4.2 Elmer FEM — Structural Analysis (sim.sif)

```
Header
  CHECK KEYWORDS Warn
  Mesh DB "." "mesh"
End

Simulation
  Max Output Level = 5
  Coordinate System = Cartesian
  Simulation Type = Steady state
  Steady State Max Iterations = 1
  Output Intervals = 1
End

Constants
  Gravity(4) = 0 -1 0 9.82
End

! ── MATERIAL 1: Silicon ──────────────────────────────────────────────
Material 1
  Name = "Silicon"
  Youngs Modulus = 170.0e9
  Poisson Ratio = 0.28
  Density = 2330.0
  Heat Conductivity = 148.0
  Heat Capacity = 700.0
  ! CTE for thermal stress
  Heat Expansion Coefficient = 2.6e-6
End

! ── MATERIAL 2: Borofloat 33 ─────────────────────────────────────────
Material 2
  Name = "Borofloat33"
  Youngs Modulus = 63.0e9
  Poisson Ratio = 0.20
  Density = 2230.0
  Heat Conductivity = 1.2
  Heat Capacity = 830.0
  Heat Expansion Coefficient = 3.25e-6
End

! ── SOLVER: Linear Elasticity ─────────────────────────────────────────
Solver 1
  Equation = Linear elasticity
  Procedure = "StressSolve" "StressSolver"
  Variable = -dofs 3 Displacement
  Linear System Solver = Direct
  Linear System Direct Method = MUMPS
  Steady State Convergence Tolerance = 1.0e-5
End

! ── EQUATION ─────────────────────────────────────────────────────────
Equation 1
  Active Solvers(1) = 1
End

! ── BODY FORCES: Temperature load ────────────────────────────────────
! Temperature change: from bonding temp 350°C to -40°C = ΔT = -390°C
Body Force 1
  Name = "ThermalStress"
  ! Reference temperature = bonding temperature
  Temperature = -40.0   ! current temperature
End

! ── BOUNDARY CONDITIONS ───────────────────────────────────────────────
! Fix bottom face of glass_bottom to prevent rigid body motion
Boundary Condition 1
  Name = "Fixed_Bottom"
  Target Boundaries(1) = 1   ! bottom face of glass_bottom
  Displacement 1 = 0.0
  Displacement 2 = 0.0
  Displacement 3 = 0.0
End
```

Run: `elmersolver sim.sif`

### 4.3 Extract Results from Elmer

After running, open results in ParaView:
1. Load `.pvtu` output file
2. Apply "Calculator" filter: von Mises stress
   - Formula: `sqrt(0.5*((Stress_xx-Stress_yy)^2 + (Stress_yy-Stress_zz)^2 + (Stress_zz-Stress_xx)^2 + 6*(Stress_xy^2+Stress_yz^2+Stress_xz^2)))`
3. Use "Threshold" filter to isolate bond interface region
4. Find maximum von Mises stress at bond interface

Write extracted value into `fem_results.py`:

```python
# fem_results.py — fill after Elmer run
RESULTS = {
    "cavity_diameter_mm":             1.5,    # from FreeCAD model
    "cavity_depth_mm":                1.0,    # from FreeCAD model
    "glass_thickness_mm":             0.3,    # from FreeCAD model
    "bond_stress_mpa":                2.1,    # from ParaView von Mises extraction
    "safety_factor":                  4.8,    # = 10.0 / 2.1
    "lowest_resonance_hz":            87000,  # from modal analysis
    "alpha_L":                        0.22,   # computed from Antoine + geometry
    "die_area_mm2":                   9.0,    # 3mm × 3mm
}
```

### 4.4 Parameter Sweep Strategy

Run the following geometry combinations (coarse mesh, ~5 min each):

```python
sweep = {
    "cavity_diameter_mm": [1.0, 1.25, 1.5, 2.0],
    "cavity_depth_mm":    [0.5, 0.75, 1.0, 1.5],
    "glass_thickness_mm": [0.3, 0.4, 0.5],
}
# = 48 combinations
```

For each, compute:
1. Bond stress (from Elmer structural FEM)
2. α·L (from Antoine equation, pure math — no FEM needed)
3. Estimate resonance frequency (analytical formula for quick screening)

Select candidates where:
- bond_stress < 3.3 MPa AND
- alpha_L in [0.1, 3.0]

Then run fine-mesh FEM on 4–6 candidates only.

### 4.5 Optical Absorption — Python Computation (no FEM needed)

```python
import numpy as np

def compute_alpha_L(cavity_depth_mm, T_celsius=85.0):
    """
    Beer-Lambert absorption product at operating temperature.
    """
    T_K = T_celsius + 273.15

    # Rb vapor pressure from Antoine equation (liquid phase, Steck 2001)
    log10_P = 9.863 - 4529.6 / T_K
    P_rb_Pa = 10 ** log10_P

    # Rb number density
    kB    = 1.380649e-23
    n_Rb  = P_rb_Pa / (kB * T_K)

    # D1 absorption cross section (peak, σ+ polarization)
    sigma_D1 = 1.1e-13  # m²

    # Cavity depth in meters
    L = cavity_depth_mm * 1e-3

    alpha_L = n_Rb * sigma_D1 * L
    return alpha_L, n_Rb
```

---

## 5. What "Done" Looks Like

```
======================================================================
  EVALUATOR: 03_mems_geometry
  Wave 1 Gate — MEMS Structural + Optical Validation
======================================================================

  PASSED (6)
    PASS  bond_stress_mpa: 2.1 MPa  (safety factor 4.8×)  ✓
    PASS  safety_factor: 4.8×  (min 3.0×)  ✓
    PASS  lowest_resonance_hz: 87000 Hz  (min 2000 Hz)  ✓
    PASS  alpha_L: 0.22  (range 0.1–3.0)  ✓
    PASS  cavity_depth_mm: 1.0 mm  ✓
    PASS  cavity_diameter_mm: 1.5 mm  ✓

======================================================================
  VERDICT:  PASS
  ACTION:   Proceed to Wave 2.
======================================================================
```

---

## 6. Known Failure Modes

| Symptom | Cause | Fix |
|---|---|---|
| Bond stress > 5 MPa | Cavity too large, walls too thin | Reduce diameter or increase glass thickness |
| α·L < 0.05 | Cavity too shallow or cold | Increase depth to 1.5 mm |
| α·L > 5 | Cavity too deep at high Rb density | Reduce depth or reduce operating temperature |
| Resonance < 500 Hz | Si layer too thin relative to area | Increase Si thickness or reduce cavity diameter |
| Elmer solver diverges | Mesh too coarse at cavity corners | Refine mesh at corner edges (element size < 0.05mm) |
| Bond stress much higher at corners | Normal — stress concentrators | Add 0.1mm corner radius fillet to cavity in FreeCAD |

---

## 7. Runtime Estimate

Per Elmer run (coarse mesh 50k elements): 3–5 min on laptop, 30 sec on 16-core cloud.
Coarse sweep (48 geometries): 4 hrs laptop overnight, 25 min on c5.4xlarge ($0.30).
Fine mesh on winners (6 geometries × 30 min each): 3 hrs laptop.
