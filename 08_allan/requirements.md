# 08_allan — Requirements

**WAVE 3 | Tool: Python + allantools | Depends on: 00_atomic_model + 05_optical + 07_servo_loop**

---

## Questions This Simulation Must Answer

1. What is the predicted Allan deviation at τ = 1s, 10s, 100s, 1hr?
2. Is ADEV < 5×10⁻¹⁰ at τ = 1s achievable with our design?
3. What is the dominant noise source at each averaging time?
4. What flicker floor does the design reach at long averaging times?

---

## Inputs Required

| Parameter | Source |
|---|---|
| CPT linewidth | 00_atomic_model/results.md |
| CPT contrast | 00_atomic_model/results.md |
| Optical power at detector | 05_optical/results.md |
| Photodetector noise | 05_optical/results.md |
| Servo bandwidth | 07_servo_loop/results.md |
| VCO phase noise | 06_rf_synthesis/results.md |

---

## What to Simulate

Short-term ADEV dominated by photon shot noise:
```
σ_y(τ) ≈ (1 / (2π × f_hfs)) × (Δν_CPT / C) × (1 / SNR) × (1/√τ)

where:
  f_hfs    = 6.8347 GHz    (hyperfine frequency)
  Δν_CPT   = CPT linewidth (Hz)
  C        = CPT contrast
  SNR      = signal-to-noise ratio at photodetector
```

Noise contributions to model:
- Photon shot noise: S_shot = 2eI_pd
- Johnson noise in TIA resistor
- VCO phase noise (from 06_rf_synthesis)
- Thermal noise (from 04_thermal → temperature fluctuations)

---

## Output to Extract into results.md

```
ADEV @ τ=1s    : _____    must be < 5×10⁻¹⁰
ADEV @ τ=10s   : _____
ADEV @ τ=100s  : _____
ADEV @ τ=1hr   : _____    target < 1×10⁻¹¹
Flicker floor  : _____
Dominant noise @ 1s  : shot noise / VCO / thermal
```
