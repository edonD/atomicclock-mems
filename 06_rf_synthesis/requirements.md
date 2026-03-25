# 06_rf_synthesis — Requirements

**WAVE 2 | Tool: Python | Depends on: 00_atomic_model**

---

## Questions This Simulation Must Answer

1. Can a PLL synthesize 3.4173 GHz from a 10 MHz reference with sufficient resolution?
2. What phase noise does the VCO contribute to the clock signal at τ=1s?
3. What VCO tuning range is needed to compensate the N2 pressure shift (from 02_buffer_gas)?
4. What divider ratio is needed and is it achievable with standard PLL chips?

---

## Inputs Required

| Parameter | Source |
|---|---|
| Modulation frequency | Fixed: 3,417,341,305.452 Hz |
| Pressure shift (total) | 02_buffer_gas/results.md |
| Reference oscillator | Fixed: 10 MHz TCXO |

---

## What to Simulate

PLL architecture:
```
f_vco = N × f_ref / R
f_vco = 3,417,341,305 Hz
f_ref = 10,000,000 Hz
→ N/R = 341.7341305
→ Use fractional-N PLL: e.g. ADF4351 (35 MHz to 4.4 GHz)
```

VCO phase noise contribution to ADEV:
```
S_y(f) = S_φ(f) / f_0²
ADEV from VCO = sqrt(2 × integral(S_y(f) × |H(f)|² df))
```

Tuning range requirement:
```
Must cover: hyperfine_splitting ± pressure_shift ± temperature_drift
= 3.4173 GHz ± ~500 kHz minimum
```

---

## Output to Extract into results.md

```
PLL divider ratio N/R       : _____
Achievable frequency step   : _____ Hz     must be < 1 Hz
Tuning range (VCO)          : _____ MHz    must cover pressure shift
VCO phase noise @ 10kHz off : _____ dBc/Hz  target < -90 dBc/Hz
ADEV contribution from VCO  : _____        must be < 1×10⁻¹⁰ at τ=1s
Recommended PLL chip        : _____        (e.g. ADF4351, ADF5356)
```
