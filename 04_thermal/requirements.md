# 04_thermal — Requirements

**WAVE 2 | Tool: Elmer FEM (thermal) | Depends on: 03_mems_geometry**

---

## Questions This Simulation Must Answer

1. What heater power (mW) is needed to hold cell at 85°C in ambient -40°C?
2. What are the Pt heater trace dimensions (width, length, resistance) needed?
3. Can the PID loop hold temperature to ±0.01°C? What are the PID gains?
4. Where are the thermal gradients across the cell? (gradients cause Rb condensation)
5. What is the thermal time constant (startup time to reach operating temperature)?

---

## Inputs Required

| Parameter | Source |
|---|---|
| Cell geometry (all dimensions) | 03_mems_geometry/results.md |
| Ambient temperature range | Fixed: -40°C to +40°C |
| Target cell temperature | Fixed: 85°C |

---

## What to Simulate (Elmer FEM — Heat Equation)

- Import geometry from 03_mems_geometry FreeCAD file
- Apply: resistive heat source on Pt heater traces
- Boundary conditions: convective cooling on outer surfaces (h = 5-20 W/m²K)
- Solve: steady-state temperature distribution
- Extract: temperature at cell center, windows, and heater
- Solve: transient startup from -40°C to 85°C
- Extract: time constant τ_thermal

Pt RTD design:
- Resistance at 25°C: R₀ = target (design parameter)
- TCR = 3850 ppm/°C → R(T) = R₀ × (1 + 3850×10⁻⁶ × (T - 25))
- Sensitivity: dR/dT = R₀ × 3850×10⁻⁶ Ω/°C

PID model (Python):
- Plant: thermal time constant from FEM
- Sensor: RTD resistance → temperature
- Controller: PID
- Simulate: step response, stability, steady-state error

---

## Output to Extract into results.md

```
Heater power (worst case, -40°C ambient) : _____ mW    must be < 100 mW
Pt heater trace width                     : _____ µm
Pt heater trace length                    : _____ mm
Heater resistance                         : _____ Ω
RTD resistance at 85°C                    : _____ Ω
Temperature stability (PID)               : _____ °C   must be < ±0.01°C
Thermal time constant                     : _____ s
Max thermal gradient across cell          : _____ °C/mm  must be < 1°C/mm
PID Kp, Ki, Kd                            : _____
```

---

## Key Constraint

Max thermal gradient across cell < 1°C/mm. A gradient causes Rb to migrate
(thermophoresis) and condense on the cooler window — permanently blocking the
optical path. This is one of the main causes of cell death in field deployment.
