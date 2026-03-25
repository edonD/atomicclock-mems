# 01_vcsel_sideband — Requirements

**WAVE 2 | Tool: Python + SciPy | Depends on: 00_atomic_model**

---

## Questions This Simulation Must Answer

1. What modulation index β gives maximum power in the ±1 sidebands?
2. What RF drive power (dBm) is needed at the 3.4173 GHz modulation port?
3. How much power remains in the carrier at optimal β? (residual carrier degrades CPT)
4. What is the AM modulation index alongside the FM — and does it hurt CPT contrast?
5. Does the sideband spacing exactly match the Rb-87 hyperfine splitting?

---

## Inputs Required

| Parameter | Source | Value |
|---|---|---|
| Modulation frequency | Fixed (Rb-87 physics) | f_m = 3,417,341,305.452 Hz |
| Sideband spacing | = 2 × f_m | = 6,834,682,610.904 Hz |
| VCSEL wavelength | Fixed (Rb D1 line) | 794.979 nm |
| Hyperfine splitting confirmed | 00_atomic_model/results.md | — |

---

## What to Simulate

VCSEL optical field under current modulation:

```
E(t) = E₀ · exp(i·ω_c·t + i·β·sin(ω_m·t))
```

Jacobi-Anger expansion into sidebands:
```
E(t) = E₀ · Σ_n  J_n(β) · exp(i·(ω_c + n·ω_m)·t)
```

Power in each sideband: `P_n = |J_n(β)|² · P_total`

- Sweep β from 0 to 4
- Find β that maximizes `J₋₁(β) · J₁(β)` (both CPT sidebands)
- Verify mathematical optimum: J₁ peaks at β ≈ 1.84, J₁(1.84) = 0.582
- Model AM alongside FM: VCSEL has both intensity and frequency modulation
- Compute total efficiency: fraction of power in useful ±1 sidebands

---

## Output to Extract into results.md

```
Optimal modulation index β   : _____      expected ~1.84
Power in +1 sideband at β_opt: _____ %    expected ~33.9%
Power in -1 sideband at β_opt: _____ %    expected ~33.9%
Carrier power at β_opt       : _____ %    expected ~10.7%
RF drive power needed        : _____ dBm
AM modulation index          : _____
Sideband spacing             : _____ GHz  must = 6.8347 GHz
```

---

## Validation Check

J₁(1.84) = 0.582 (mathematical fact — if your Bessel calculation gives something
different, your SciPy call is wrong).

J₀(1.84) = 0.327, J₁(1.84) = 0.582, J₂(1.84) = 0.310 — verify all three.
