# 00_atomic_model — Rb-87 CPT Physics

> **Status: NOT IMPLEMENTED** — `sim.py` stubs pending QuTiP density matrix simulation

---

## 1. What This Module Does

This module is the physics foundation of the entire MEMS atomic clock project.
It simulates the Rb-87 three-level quantum system using a master equation (Lindblad
formalism) and extracts the Coherent Population Trapping (CPT) resonance curve that
proves the vapor cell design can produce a usable atomic frequency reference.
Every downstream module — VCSEL sideband design, buffer gas pressure, RF synthesis,
servo loop, and Allan deviation estimate — is calibrated against the numbers this
module produces.
If the CPT linewidth and contrast predicted here are wrong, the clock fails before
a single wafer is ordered.

The key outputs are the CPT linewidth (target < 5 kHz) and CPT contrast (target > 3%),
matched against the Microchip SA65 CSAC commercial benchmark and the landmark
Knappe et al. (NIST, 2004) first MEMS atomic clock demonstration.

---

## 2. Physics — the Λ System and the CPT Dark State

### Why Rb-87 and the D1 Line

Rb-87 has nuclear spin I = 3/2.  Combined with electron spin J = 1/2 in the 5S₁/₂
ground state, this gives total angular momentum F = 1 and F = 2.  The magnetic
dipole coupling constant A_hfs = 3417.341 MHz produces the hyperfine splitting:

```
ΔE_hfs = A_hfs × 2  →  6834.682... MHz  (≡ 6,834,682,610.904 Hz NIST 2021)
```

The D1 line (5S₁/₂ → 5P₁/₂, 794.979 nm) is used because it naturally forms a clean
Λ system: both F = 1 and F = 2 ground states couple to the same excited-state manifold
(F′ = 1, F′ = 2), with simpler optical pumping than the D2 line.

### The Three-Level Λ System

```
               |3⟩  =  |5P₁/₂, F′=1⟩
              /    \
         Ω₁ /      \ Ω₂         ← two sidebands of the VCSEL
            /        \
         |1⟩          |2⟩
    |F=1, mF=0⟩   |F=2, mF=0⟩
         ←   6.8347 GHz   →
```

When the VCSEL sideband difference frequency exactly equals the hyperfine splitting
(ω₁ − ω₂ = ω_hfs), the atoms are coherently driven into a **dark state**:

```
|D⟩ = (Ω₂|1⟩ − Ω₁|2⟩) / √(|Ω₁|² + |Ω₂|²)
```

The dark state does not absorb light — this is the CPT transparency dip, and it is
the clock signal.

![Rb-87 Energy Level Diagram](plots/energy_levels.png)

The diagram shows the full level structure with the two Rabi frequencies Ω₁ and Ω₂
driving the Λ transitions, the 6.8347 GHz hyperfine splitting, and the dark state
expression.  The ground-state coherence ρ₁₂ (highlighted in gold) is the quantum
element responsible for CPT.

---

## 3. The Density Matrix Model

### Three States

| Index | State | Physical meaning |
|-------|-------|-----------------|
| \|1⟩ | \|5S₁/₂, F=1, mF=0⟩ | Lower clock state |
| \|2⟩ | \|5S₁/₂, F=2, mF=0⟩ | Upper clock state |
| \|3⟩ | \|5P₁/₂, F′=1⟩ | Excited state (radiates) |

The full quantum state is the 3×3 density matrix ρ.  Diagonal elements ρᵢᵢ are
populations; off-diagonal elements ρᵢⱼ are coherences.  The element ρ₁₂ is the
**ground-state coherence** — it is built up by the two optical fields and is the
direct source of the CPT dark state.  Optical coherences ρ₁₃ and ρ₂₃ couple the
ground states to the excited state and carry the absorption observable.

### Hamiltonian (Rotating Frame, RWA)

In the rotating wave approximation, transforming to a frame co-rotating with the
laser frequencies, the Hamiltonian becomes:

```
H = −ħ × [[  0,      0,      Ω*/2  ],
           [  0,      δ_R,    Ω*/2  ],
           [  Ω/2,    Ω/2,    δ₁    ]]
```

where δ₁ is the one-photon detuning (set to 0 at resonance) and **δ_R is the Raman
detuning** — the quantity swept to trace the CPT resonance curve.

### Lindblad Operators

Four collapse operators capture the dissipative physics:

| Operator | Rate | Process |
|----------|------|---------|
| L₁ = √(Γ/2) \|1⟩⟨3\| | Γ/2π = 5.746 MHz | Spontaneous decay \|3⟩ → \|1⟩ |
| L₂ = √(Γ/2) \|2⟩⟨3\| | Γ/2π = 5.746 MHz | Spontaneous decay \|3⟩ → \|2⟩ |
| L₃ = √γ₁₂ \|1⟩⟨2\|   | γ₁₂ = 300–3000 Hz | Ground decoherence (transit + wall) |
| L₄ = √γ₁₂ \|2⟩⟨1\|   | γ₁₂ = 300–3000 Hz | Ground decoherence (conjugate) |

The parameter γ₁₂ — the ground-state decoherence rate — is the single most important
cell-physics number: it sets the CPT linewidth floor and is controlled by N₂ buffer
gas pressure and cell geometry.

![Density Matrix Structure and Lindblad Operators](plots/density_matrix_structure.png)

The left panel shows the 3×3 matrix coloured by element type: populations (orange),
the key CPT ground-state coherence ρ₁₂ (purple, gold border), and optical coherences
(blue).  The right panel maps each Lindblad operator onto the level diagram.

---

## 4. Expected Simulation Results — CPT Resonance Curve

### Absorption Observable

The measured signal is proportional to:

```
Absorption  ∝  Im(ρ₃₁) + Im(ρ₃₂)
```

Sweeping the Raman detuning δ_R from −50 kHz to +50 kHz produces a broad Lorentzian
absorption background with a narrow **transparency dip** at δ_R = 0.  The dip is the
CPT resonance.

### Lineshape Model

```
A(δ_R)  =  A_bg × ( 1 − C / (1 + (2δ_R / Γ_CPT)²) )
```

where C is the contrast and Γ_CPT is the FWHM.

![CPT Resonance Lineshape — Theory](plots/cpt_lineshape_theory.png)

The three curves show how the CPT resonance depends on γ₁₂:

| γ₁₂ | Linewidth (FWHM) | Contrast | Comment |
|-----|-----------------|---------|---------|
| 300 Hz  | ~0.6 kHz | ~8.5% | Low-pressure, excellent cell |
| 1000 Hz | ~2.0 kHz | ~5.5% | Nominal MEMS cell (Knappe 2004 regime) |
| 3000 Hz | ~6.0 kHz | ~2.5% | High-pressure or small cell — fails spec |

### Targets (from evaluator.py)

| Parameter | Target | Source |
|-----------|--------|--------|
| CPT linewidth FWHM | **< 5 kHz** | Microchip SA65 datasheet |
| CPT contrast | **> 3%** | Microchip SA65 datasheet |
| Hyperfine splitting | 6,834,682,610.904 Hz ± 0.01 ppm | NIST 2021 |
| D1 wavelength | 794.978851156 nm ± 1 pm | NIST ASD |
| Natural linewidth | 5.746 MHz ± 1% | NIST (27.70 ns lifetime) |

---

## 5. Laser Power Optimisation

### The Vanier Formula

From Vanier & Audoin (1989) — the foundational CPT linewidth formula:

```
Δν_CPT ≈ (1/π) × ( γ₁₂  +  Ω² / (2Γ) )
```

- The first term **γ₁₂** is set by cell physics (buffer gas, geometry) — fixed for
  a given design.
- The second term **Ω²/(2Γ)** is power broadening — it grows as Ω/Γ increases and
  is the dominant effect above Ω ≈ 0.3 Γ.

### The Trade-off

Higher laser power (larger Ω) improves SNR (more contrast C) but also broadens the
resonance linewidth via power broadening.  The figure of merit is C / Δν — maximised
at an intermediate Rabi frequency.

![Laser Power Sweep — Theory](plots/laser_power_sweep_theory.png)

Key features of the plot:

- **Blue curve** — CPT linewidth rises quadratically with Ω/Γ (power broadening)
- **Red curve** — Contrast falls as laser power saturates the transition
- **Green dashed** — Figure of merit C/Δν peaks near Ω/Γ ≈ 0.30–0.40
- **Gold marker** — Optimal operating point: linewidth ≈ 2 kHz, contrast ≈ 5%,
  corresponding to ~16–25 µW per beam for a 1.5 mm diameter cell

The dashed horizontal lines mark the spec limits (5 kHz linewidth ceiling,
3% contrast floor).

---

## 6. Evaluator Targets

`python evaluator.py` grades `RESULTS` from `sim.py` against seven checks:

| # | Check | Criterion | Source |
|---|-------|-----------|--------|
| 1 | `hyperfine_hz` | = 6,834,682,610.904 Hz ± 0.01 ppm (68 Hz) | NIST 2021 |
| 2 | `d1_wavelength_nm` | = 794.978851156 nm ± 1 pm | NIST ASD |
| 3 | `natural_linewidth_mhz` | = 5.746 MHz ± 1% | NIST (5P₁/₂ lifetime) |
| 4 | `cpt_linewidth_khz` | ≤ 5.0 kHz | Microchip SA65 CSAC |
| 5 | `cpt_contrast_pct` | ≥ 3.0% | Microchip SA65 CSAC |
| 6 | `dark_state_verified` | True | CPT theory (Arimondo 1996) |
| 7 | `clock_transition_verified` | True — mF=0 ↔ mF=0 first-order Zeeman free | Rb-87 QM |

Checks 1–7 are all **critical** (any FAIL blocks Wave 2).  Additional non-critical
checks verify that the optimal laser power (10–500 µW) is achievable with a VCSEL.

Expected passing output:

```
======================================================================
  EVALUATOR: 00_atomic_model
  Wave 1 Gate — CPT Physics Validation
======================================================================

  PASSED (7)
    PASS  hyperfine_hz: 6834682610.904 Hz  (error 0.0000 ppm)  ✓
    PASS  d1_wavelength_nm: 794.978851 nm  (error 0.000 pm)  ✓
    PASS  natural_linewidth_mhz: 5.7460 MHz  (error 0.000%)  ✓
    PASS  cpt_linewidth_khz: 3.2 kHz  (limit 5.0 kHz, margin 1.8 kHz)  ✓
    PASS  cpt_contrast_pct: 4.8%  (min 3.0%, margin 1.8%)  ✓
    PASS  dark_state_verified: dark state confirmed  ✓
    PASS  clock_transition_verified: mF=0↔mF=0 confirmed  ✓

======================================================================
  VERDICT:  PASS
  ACTION:   Proceed to Wave 2.
======================================================================
```

---

## 7. What is Needed to Implement

`sim.py` currently raises `NotImplementedError` on all entry points.
Four steps are required:

- **Install QuTiP** — `pip install qutip>=5.0` (also needs numpy, scipy, matplotlib).
  QuTiP provides `qt.steadystate(H, c_ops)` which is the numerical solver for
  `dρ/dt = 0`.

- **Build the Hamiltonian** — Assemble the 3×3 rotating-frame Hamiltonian from
  `build_hamiltonian(delta_1_hz, delta_R_hz, omega_hz)`.  The Hamiltonian must use
  the NIST constants exactly; do not approximate the hyperfine splitting.

- **Solve steady state** — Call `qt.steadystate(H, c_ops)` for each δ_R point in
  the ±50 kHz sweep.  Extract absorption as `Im(ρ₃₁) + Im(ρ₃₂)` (check sign
  convention — the CPT dip must be a downward feature).

- **Extract linewidth and contrast** — Use `extract_cpt_params()` to find the FWHM
  via half-maximum crossings and the contrast via `(baseline − dip) / baseline × 100`.
  Then sweep Rabi frequency with `sweep_laser_power()` to find the optimal Ω/Γ ratio.

Runtime estimate: ~30 s per CPT scan at 500 points; ~15 minutes for the full power
sweep (30 Ω values × 300 points each).  Use Python `multiprocessing.Pool` to
parallelise across Ω values for a ~8× speedup.

See `program.md` §7 for a complete failure-mode table (wrong Lindblad sign, flat
absorption curve, non-convergent steadystate solver, etc.).

---

## 8. Downstream Impact

This module is a **Wave 1 gate** — all Wave 2 modules depend on it.

| Downstream module | What it consumes |
|-------------------|-----------------|
| `01_vcsel_sideband` | Hyperfine frequency 6,834,682,610.904 Hz — sets EOM/modulation target |
| `02_buffer_gas` | CPT linewidth sensitivity to γ₁₂ — sets N₂ pressure target |
| `06_rf_synthesis` | Modulation frequency = hyperfine/2 = 3.417 GHz |
| `07_servo_loop` | Discriminator slope dA/dδ_R at δ_R = 0 — sets servo gain |
| `08_allan` | Linewidth + contrast → ADEV estimate via σ_y ≈ Δν/(πC√(S/N·τ)) |
| `design/spec_sheet` | All CPT performance numbers for the system specification |

A 50% error in CPT linewidth here propagates directly to a 50% error in the ADEV
prediction in module 08.  The physics is well-established; getting this right is
purely an implementation task.

---

## Files

| File | Description |
|------|-------------|
| `sim.py` | QuTiP density matrix simulation — **NOT IMPLEMENTED** |
| `evaluator.py` | Grades RESULTS against NIST + SA65 benchmarks |
| `gen_plots.py` | Generates theory/illustrative plots from analytical physics |
| `program.md` | Full physics derivation, implementation guide, failure modes |
| `requirements.md` | Inputs, constants, simulation scope |
| `results.md` | Output table — populated after sim.py runs |
| `plots/` | Generated figures (energy levels, lineshape, density matrix, power sweep) |

---

*References: Vanier & Audoin (1989) §4; Knappe et al. Appl. Phys. Lett. 85, 1460 (2004);
Lutwak et al. PTTI (2004); NIST ASD Rb-87 spectroscopic constants (2021).*
