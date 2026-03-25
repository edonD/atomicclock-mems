# 00_atomic_model — Requirements

**WAVE 1 | Tool: QuTiP (Python) | No dependencies**

---

## Questions This Simulation Must Answer

1. What is the expected CPT linewidth for our cell geometry?
2. What is the expected CPT contrast (transparency depth)?
3. What is the optimal laser power per beam?
4. Is the mF=0 ↔ mF=0 clock transition truly first-order field-independent?
5. What is the discriminator slope (dSignal/dFrequency) at the lock point?

These five numbers directly determine whether the clock can reach ADEV < 5×10⁻¹⁰.
If the CPT linewidth is too broad or contrast too low, the clock fails before
any hardware is built.

---

## Inputs Required

All constants are fixed physics — no external module dependencies.

| Parameter | Value | Source |
|---|---|---|
| Rb-87 hyperfine splitting | 6,834,682,610.904 Hz | NIST 2021 |
| D1 transition frequency | 377,107,463,380,000 Hz | NIST ASD |
| D1 wavelength | 794.978851156 nm | NIST ASD |
| Natural linewidth Γ | 2π × 5.746 MHz | NIST (5P1/2 lifetime = 27.70 ns) |
| Nuclear spin | I = 3/2 | Fixed for Rb-87 |
| Lande g-factor F=1 | gF = -1/2 | Standard |
| Lande g-factor F=2 | gF = +1/2 | Standard |

---

## What to Simulate

### Part A: Energy Level Structure
- Build the Rb-87 Hamiltonian: hyperfine coupling H_hfs = A·I·J
- Compute F=1 and F=2 ground state manifolds (8 total substates)
- Compute 5P1/2 excited state manifolds
- Verify: splitting between F=1 mF=0 and F=2 mF=0 = 6,834,682,610.904 Hz
- Plot: energy level diagram with all quantum numbers

### Part B: Lambda System and CPT
- Reduce to 3-level Lambda system: |1⟩=|F=1,mF=0⟩, |2⟩=|F=2,mF=0⟩, |3⟩=|5P1/2,F'=1⟩
- Build density matrix ρ (3×3)
- Hamiltonian in rotating frame (RWA):
  H = -ħ[δ₁σ₃₃ + δ_R σ₂₂ - Ω₁/2 σ₃₁ - Ω₂/2 σ₃₂ + h.c.]
- Lindblad dissipators:
  - Spontaneous decay: Γ from |3⟩ to |1⟩ and |2⟩
  - Ground decoherence: γ₁₂ (transit + wall collisions, ~0.3-3 kHz)
- Solve steady-state: dρ/dt = 0
- Extract absorption: Im(ρ₃₁) as function of Raman detuning δ_R
- Sweep δ_R from -50 kHz to +50 kHz
- Sweep laser power: Ω from 0.1Γ to 2Γ

---

## Output to Extract into results.md

```
CPT linewidth FWHM         : _____ kHz
CPT contrast               : _____ %
Optimal Rabi frequency Ω   : _____ × Γ
Optimal laser power/beam   : _____ µW
Discriminator slope        : _____ (a.u./Hz)
Dark state verified        : YES / NO
Clock transition verified  : YES / NO
```

---

## Evaluation Gate

Run `python evaluator.py` after simulation completes.
Must achieve PASS before proceeding to Wave 2.
