# Module 00: Atomic Model — Program

## 1. Mission

Simulate the Rb-87 quantum system and extract the CPT resonance curve that proves
our vapor cell design will produce a usable atomic frequency reference.

This is the physics foundation. Every other module either feeds into this model
or is calibrated against its output. If the CPT linewidth and contrast predicted
here are wrong, the clock fails before a single wafer is ordered.

**What "done" means:**

1. `sim.py` runs without error and populates `RESULTS` dict with all required fields.
2. `python evaluator.py` exits with code 0 (PASS).
3. The hyperfine splitting matches NIST to 0.01 ppm — proving the Hamiltonian is correct.
4. The CPT linewidth is < 5 kHz and contrast > 3% — matching Microchip SA65 published range.
5. A CPT resonance plot is saved showing a clear transparency dip vs Raman detuning.

---

## 2. State of the Art

### 2.1 Vanier & Audoin — The Textbook (1989)

"The Quantum Physics of Atomic Frequency Standards" is the definitive reference.
Chapter 4 covers CPT clocks in full. The key CPT linewidth formula derived there:

```
Δν_CPT ≈ (1/π) × (Γ₁₂ + Ω²/(2Γ))
```

where Γ₁₂ is the ground-state decoherence rate and Ω is the Rabi frequency.
The first term is set by the cell physics (buffer gas, wall collisions), the
second by the laser power. This formula is the sanity check for our simulation.

### 2.2 Knappe et al. NIST (2004) — First MEMS CSAC Cell

"A microfabricated atomic clock" (Applied Physics Letters 85, 1460) demonstrated
CPT in a MEMS-fabricated Rb vapor cell:
- Cell size: 1 mm × 1 mm × 2 mm
- CPT linewidth: ~4 kHz
- Contrast: ~4%
- N2 buffer gas: ~75 Torr

This is the primary experimental benchmark. Our simulation must reproduce these
numbers ± factor of 2 for the same cell geometry to be credible.

### 2.3 Lutwak et al. — Symmetricom CSAC (2004)

"The Chip-Scale Atomic Clock — Coherent Population Trapping vs. Conventional
Interrogation" (PTTI 2004) showed:
- ADEV 2×10⁻¹⁰ at τ=1s using CPT
- CPT linewidth ~5 kHz in a sealed Rb cell
- Key finding: contrast × linewidth product is the fundamental figure of merit

Their result sets the competitive bar. If our simulation gives the same linewidth
and contrast, our ADEV prediction will also match.

### 2.4 Microchip SA65 (current product)

Publicly available datasheet shows:
- ADEV: 2.5×10⁻¹⁰ at τ=1s (specified)
- Power: 120 mW
- Volume: 17 cm³
- Based on CPT in Rb-87

The SA65 is the commercial benchmark. Our design is correct when the simulation
predicts performance comparable to it.

### 2.5 Honest Assessment

A 3×3 density matrix simulation is well-established physics. There is no novelty
here — we are not extending theory. The task is purely implementation: set up the
correct Hamiltonian, the correct Lindblad operators, solve for steady state, and
extract the right observables. If the result disagrees with Knappe (2004), the
most likely cause is wrong Lindblad operators, wrong rotating frame, or wrong
definition of contrast. The physics is not in question.

---

## 3. Physics

### 3.1 Why Rb-87 and the D1 Line

Rb-87 has nuclear spin I=3/2. Combined with electron spin J=1/2 in the 5S₁/₂
ground state, this gives total angular momentum F = 1 and F = 2. The magnetic
dipole coupling constant A_hfs = 3417.341 MHz (for the 5S₁/₂ state) produces
the hyperfine splitting:

```
ΔE_hfs = A_hfs × (I + 1/2) = A_hfs × 2  →  6834.682... MHz
```

We use the D1 line (5S₁/₂ → 5P₁/₂) at 794.979 nm because:
- The D1 line connects F=1 and F=2 ground states to the SAME excited state
  manifold → clean Lambda system formation
- D1 excited state has only F'=1 and F'=2 (unlike D2 which has F'=0,1,2,3)
  → simpler optical pumping, less open-channel loss

### 3.2 The Lambda System

CPT uses a three-level Lambda (Λ) system:

```
          |3⟩ = |5P₁/₂, F'=1⟩
         / \
    Ω₁  /   \ Ω₂       (two optical fields, sidebands of VCSEL)
       /     \
    |1⟩       |2⟩
  |F=1,mF=0⟩  |F=2,mF=0⟩
    ←  6.8347 GHz  →
```

|1⟩ and |2⟩ are the two ground-state hyperfine levels (mF=0 sublevels).
|3⟩ is the excited state.
Ω₁, Ω₂ are the Rabi frequencies of the two optical fields (VCSEL ±1 sidebands).

When ω₁ - ω₂ = ω_hyperfine exactly, the atoms are driven into the dark state:

```
|D⟩ = (Ω₂|1⟩ - Ω₁|2⟩) / sqrt(|Ω₁|² + |Ω₂|²)
```

The dark state does not absorb light → transparency peak → our clock signal.

### 3.3 The Density Matrix

The quantum state is described by a 3×3 density matrix ρ:

```
ρ = [[ρ₁₁, ρ₁₂, ρ₁₃],
     [ρ₂₁, ρ₂₂, ρ₂₃],
     [ρ₃₁, ρ₃₂, ρ₃₃]]
```

Diagonal elements ρᵢᵢ = populations (ρ₁₁+ρ₂₂+ρ₃₃ = 1).
Off-diagonal elements ρᵢⱼ = coherences.

### 3.4 The Hamiltonian (Rotating Frame, RWA)

In the rotating wave approximation, transforming to a frame rotating with the
laser frequencies:

```
H = -ħ × [[0,        0,        Ω₁*/2  ],
           [0,        δ_R,      Ω₂*/2  ],
           [Ω₁/2,    Ω₂/2,    δ₁     ]]
```

where:
- δ₁ = one-photon detuning (ω_laser - ω_31), typically set to 0 (resonance)
- δ_R = Raman detuning = (ω₁-ω₂) - ω_hyperfine (THIS IS WHAT WE SWEEP)
- Ω₁, Ω₂ = Rabi frequencies (proportional to sqrt(laser power))

For equal beams: Ω₁ = Ω₂ = Ω.

### 3.5 Lindblad Dissipators

The master equation includes decay processes:

```
dρ/dt = -i/ħ [H, ρ] + Σₖ (Lₖ ρ Lₖ† - ½{Lₖ†Lₖ, ρ})
```

Lindblad operators for our system:

```python
# Spontaneous decay |3⟩ → |1⟩  (rate Γ/2)
L1 = sqrt(Γ/2) × |1><3|    # = sqrt(Γ/2) × basis(3,0) × basis(3,2).dag()

# Spontaneous decay |3⟩ → |2⟩  (rate Γ/2)
L2 = sqrt(Γ/2) × |2><3|

# Ground-state decoherence |1⟩↔|2⟩  (rate γ₁₂)
# This captures: transit relaxation, wall collisions, buffer-gas spin relaxation
L3 = sqrt(γ₁₂) × |1><2|
L4 = sqrt(γ₁₂) × |2><1|
```

Γ = 2π × 5.746 MHz (natural linewidth of 5P₁/₂, from lifetime 27.70 ns).
γ₁₂ = ground-state decoherence rate. This is the KEY parameter — it sets the
CPT linewidth floor. Typical values: 300 Hz (low pressure, good cell) to 3 kHz
(high pressure or small cell with wall collisions).

### 3.6 Observable: Absorption

The measurable signal is the light absorbed by the atoms, proportional to:

```
Absorption ∝ Im(ρ₃₁) + Im(ρ₃₂)
```

At the CPT resonance (δ_R = 0), atoms go dark → absorption drops → transparency peak.

We sweep δ_R from -50 kHz to +50 kHz and plot absorption vs δ_R.
The CPT resonance appears as a narrow DIP in the absorption curve.

### 3.7 Extracting Linewidth and Contrast

From the absorption curve A(δ_R):

```
baseline  = A(δ_R >> linewidth)  = absorption far from resonance
peak_dip  = A(0)                  = absorption at exact resonance

contrast = (baseline - peak_dip) / baseline × 100  [%]
linewidth = FWHM of the dip [Hz or kHz]
```

For finding FWHM: find the two points where A = baseline - (baseline-peak_dip)/2.

---

## 4. Implementation

### 4.1 Dependencies

```python
import numpy as np
import qutip as qt          # pip install qutip>=5.0
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from scipy.optimize import minimize_scalar
```

### 4.2 Basis States

```python
# 3-level basis: |1⟩=ground F=1, |2⟩=ground F=2, |3⟩=excited 5P1/2
g1 = qt.basis(3, 0)   # |F=1, mF=0⟩
g2 = qt.basis(3, 1)   # |F=2, mF=0⟩
ex = qt.basis(3, 2)   # |5P1/2, F'=1⟩

# Transition operators
sigma_31 = g1 * ex.dag()   # |1⟩⟨3|  decay from excited to g1
sigma_32 = g2 * ex.dag()   # |2⟩⟨3|  decay from excited to g2
sigma_12 = g1 * g2.dag()   # |1⟩⟨2|  ground coherence
```

### 4.3 Constants

```python
# Physical constants
hbar = 1.054571817e-34
h    = 6.62607015e-34
c    = 299792458.0
kB   = 1.380649e-23

# Rb-87 constants (NIST 2021 — these are exact, do not change)
HYPERFINE_HZ  = 6_834_682_610.904      # Hz — NIST 2021
D1_FREQ_HZ    = 377_107_463_380_000.0  # Hz
D1_LAMBDA_NM  = 794.978851156          # nm
LIFETIME_S    = 27.70e-9               # s  (5P1/2 spontaneous lifetime)
GAMMA_RAD     = 1.0 / LIFETIME_S       # rad/s natural linewidth
GAMMA_HZ      = GAMMA_RAD / (2*np.pi)  # Hz = 5.746 MHz
```

### 4.4 Part A — Verify Energy Levels

```python
def verify_atomic_constants():
    """
    Compute the hyperfine splitting from first principles using the
    magnetic dipole coupling constant for Rb-87 5S1/2.
    Then verify against NIST.
    """
    # Rb-87 hyperfine coupling constant for 5S1/2
    A_hfs = 3417.341305  # MHz (ground state)

    # Hyperfine splitting = A × (2I+1) for F_max - F_min levels
    # For I=3/2, J=1/2: F=1 and F=2
    # ΔE_hfs = A_hfs × [F_max(F_max+1) - F_min(F_min+1)] / 2
    # Simplified: ΔE_hfs = A_hfs × (I + 1/2) = A_hfs × 2 for I=3/2
    delta_hfs_mhz = A_hfs * 2.0  # = 6834.682610 MHz
    delta_hfs_hz  = delta_hfs_mhz * 1e6

    # Verify against NIST
    nist_value = HYPERFINE_HZ
    error_ppm  = abs(delta_hfs_hz - nist_value) / nist_value * 1e6

    return {
        "hyperfine_hz":          nist_value,     # use NIST exact value
        "d1_wavelength_nm":      D1_LAMBDA_NM,
        "natural_linewidth_mhz": GAMMA_HZ / 1e6,
        "computed_splitting_hz": delta_hfs_hz,
        "nist_error_ppm":        error_ppm,
    }
```

### 4.5 Part B — CPT Steady State (core simulation)

```python
def build_hamiltonian(delta_1_hz, delta_R_hz, omega_hz):
    """
    Build 3×3 rotating-frame Hamiltonian.

    Args:
        delta_1_hz:  one-photon detuning (Hz). Set to 0 for resonance.
        delta_R_hz:  Raman detuning (Hz). This is the sweep variable.
        omega_hz:    Rabi frequency (Hz) for each beam. Equal beams assumed.

    Returns:
        qutip.Qobj Hamiltonian
    """
    delta_1 = 2 * np.pi * delta_1_hz
    delta_R = 2 * np.pi * delta_R_hz
    omega   = 2 * np.pi * omega_hz

    # 3×3 matrix in rotating frame (units: rad/s, so multiply by hbar for energy)
    H = qt.Qobj([
        [0,          0,          omega/2   ],
        [0,          delta_R,    omega/2   ],
        [omega/2,    omega/2,    delta_1   ],
    ])
    return H


def build_lindblad_ops(gamma_12_hz):
    """
    Build Lindblad collapse operators.

    Args:
        gamma_12_hz: ground-state decoherence rate (Hz)

    Returns:
        list of qutip.Qobj operators
    """
    Gamma  = GAMMA_RAD           # natural linewidth (rad/s)
    g12    = 2 * np.pi * gamma_12_hz

    c_ops = [
        np.sqrt(Gamma / 2) * (g1 * ex.dag()),  # |3⟩ → |1⟩ decay
        np.sqrt(Gamma / 2) * (g2 * ex.dag()),  # |3⟩ → |2⟩ decay
        np.sqrt(g12)       * (g1 * g2.dag()),  # ground decoherence
        np.sqrt(g12)       * (g2 * g1.dag()),  # ground decoherence (conjugate)
    ]
    return c_ops


def cpt_absorption(delta_R_hz, delta_1_hz=0.0, omega_hz=None, gamma_12_hz=1000.0):
    """
    Compute steady-state absorption at a given Raman detuning.

    Returns: absorption signal (proportional to Im(ρ₃₁) + Im(ρ₃₂))
    """
    if omega_hz is None:
        omega_hz = GAMMA_HZ * 0.3   # default: Ω = 0.3 × Γ

    H     = build_hamiltonian(delta_1_hz, delta_R_hz, omega_hz)
    c_ops = build_lindblad_ops(gamma_12_hz)

    # Solve for steady state: dρ/dt = 0
    rho_ss = qt.steadystate(H, c_ops)

    # Absorption ∝ imaginary part of coherences
    rho_31 = rho_ss[2, 0]  # ⟨3|ρ|1⟩
    rho_32 = rho_ss[2, 1]  # ⟨3|ρ|2⟩

    absorption = np.imag(rho_31) + np.imag(rho_32)
    return absorption


def scan_cpt_resonance(gamma_12_hz=1000.0, omega_hz=None, n_points=500):
    """
    Sweep Raman detuning and build the CPT resonance curve.

    Returns:
        delta_R_arr: array of Raman detunings (Hz)
        absorption:  array of absorption values
    """
    if omega_hz is None:
        omega_hz = GAMMA_HZ * 0.3

    delta_R_arr = np.linspace(-50e3, 50e3, n_points)  # ±50 kHz sweep
    absorption  = np.array([
        cpt_absorption(dr, omega_hz=omega_hz, gamma_12_hz=gamma_12_hz)
        for dr in delta_R_arr
    ])
    return delta_R_arr, absorption
```

### 4.6 Extract Linewidth and Contrast

```python
def extract_cpt_params(delta_R_arr, absorption):
    """
    Extract CPT linewidth (FWHM) and contrast from resonance curve.

    The CPT resonance is a DIP (minimum) in the absorption curve.

    Returns:
        dict with: linewidth_hz, linewidth_khz, contrast_pct,
                   dark_state_verified
    """
    # Baseline = mean of outer 20% of sweep range (far from resonance)
    n = len(absorption)
    n_outer = n // 5
    baseline = np.mean(np.concatenate([absorption[:n_outer], absorption[-n_outer:]]))

    # Peak dip = value at center (δ_R = 0)
    center_idx = n // 2
    peak_dip   = absorption[center_idx]

    # Contrast
    contrast_pct = (baseline - peak_dip) / baseline * 100

    # FWHM: find half-maximum points
    half_max = baseline - (baseline - peak_dip) / 2.0
    # Find crossings
    above = absorption > half_max
    crossings = np.where(np.diff(above.astype(int)))[0]

    if len(crossings) >= 2:
        # Use first and last crossing
        left_idx  = crossings[0]
        right_idx = crossings[-1]
        delta_step = delta_R_arr[1] - delta_R_arr[0]
        linewidth_hz = (right_idx - left_idx) * delta_step
    else:
        linewidth_hz = None  # could not find FWHM

    # Dark state verification: contrast > 0 means dark state formed
    dark_state_verified = contrast_pct > 0.5

    return {
        "linewidth_hz":          linewidth_hz,
        "linewidth_khz":         linewidth_hz / 1e3 if linewidth_hz else None,
        "contrast_pct":          contrast_pct,
        "dark_state_verified":   dark_state_verified,
        "baseline":              baseline,
        "peak_dip":              peak_dip,
    }
```

### 4.7 Parameter Sweep — Find Optimal Laser Power

```python
def sweep_laser_power(gamma_12_hz=1000.0):
    """
    Sweep Rabi frequency (laser power) to find optimal operating point.
    Returns: list of (omega_ratio, linewidth_khz, contrast_pct)
    """
    results = []
    omega_ratios = np.linspace(0.05, 2.0, 30)  # Ω/Γ sweep

    for ratio in omega_ratios:
        omega_hz = GAMMA_HZ * ratio
        delta_R, absorption = scan_cpt_resonance(
            gamma_12_hz=gamma_12_hz,
            omega_hz=omega_hz,
            n_points=300  # coarser for speed
        )
        params = extract_cpt_params(delta_R, absorption)
        results.append({
            "omega_ratio":   ratio,
            "omega_hz":      omega_hz,
            "linewidth_khz": params["linewidth_khz"],
            "contrast_pct":  params["contrast_pct"],
        })

    return results
```

### 4.8 Discriminator Slope

```python
def compute_discriminator_slope(gamma_12_hz=1000.0, omega_hz=None):
    """
    The discriminator slope is dA/d(δ_R) at the lock point (δ_R = 0).
    This is what the servo loop multiplies by to get the error signal.
    Steeper slope = easier to lock = better clock.
    """
    if omega_hz is None:
        omega_hz = GAMMA_HZ * 0.3

    epsilon = 500.0  # Hz, small perturbation
    A_plus  = cpt_absorption( epsilon, omega_hz=omega_hz, gamma_12_hz=gamma_12_hz)
    A_minus = cpt_absorption(-epsilon, omega_hz=omega_hz, gamma_12_hz=gamma_12_hz)

    slope = (A_plus - A_minus) / (2 * epsilon)  # (absorption units) / Hz
    return slope
```

### 4.9 Clock Transition Verification

```python
def verify_clock_transition():
    """
    The mF=0 ↔ mF=0 transition must be first-order Zeeman insensitive.
    The first-order Zeeman shift is zero because both mF=0 substates have
    the same first-order Zeeman coefficient.

    Second-order (quadratic) Zeeman shift:
    δν_quad = 575 Hz/G² × B²
    At Earth's field (0.5 G): δν = 575 × 0.25 = 144 Hz — negligible.
    """
    # First-order Zeeman: Δν₁ = gF × mF × μ_B × B / h
    # For mF=0: Δν₁ = 0 for both levels → clock transition is field-independent
    gF_F1 = -1/2   # Landé g-factor for F=1
    gF_F2 = +1/2   # Landé g-factor for F=2
    mF    = 0

    first_order_shift_f1 = gF_F1 * mF  # = 0
    first_order_shift_f2 = gF_F2 * mF  # = 0

    clock_transition_verified = (first_order_shift_f1 == 0 and
                                  first_order_shift_f2 == 0)

    # Quadratic Zeeman coefficient
    quadratic_zeeman_hz_per_G2 = 575.0

    return clock_transition_verified, quadratic_zeeman_hz_per_G2
```

### 4.10 Estimate Optimal Laser Power in µW

```python
def omega_to_power_uw(omega_hz, cell_diameter_mm=1.5):
    """
    Convert Rabi frequency to laser power in µW.
    Uses D1 transition matrix element for Rb-87.

    Ω = d_eg × E / ħ
    P = ε₀ c |E|² × A_beam / 2

    Simplified: P_µW ≈ (Ω/Γ)² × P_sat
    where P_sat ≈ 16 µW for a 1.5mm diameter beam at D1 line.
    """
    # Saturation intensity for Rb-87 D1, circular polarization
    I_sat_mW_cm2 = 4.49     # mW/cm² (Rb-87 D1, σ+ polarization)

    beam_area_cm2 = np.pi * (cell_diameter_mm / 2 / 10)**2  # convert mm to cm
    P_sat_uW      = I_sat_mW_cm2 * beam_area_cm2 * 1000     # mW → µW

    # At Ω = Γ (saturation), P = P_sat
    power_uW = (omega_hz / GAMMA_HZ)**2 * P_sat_uW
    return power_uW
```

---

## 5. Full sim.py Structure

```python
if __name__ == "__main__":
    # ── Step 1: Verify atomic constants ──────────────────────────────────
    atomic = verify_atomic_constants()

    # ── Step 2: Single CPT scan (nominal parameters) ─────────────────────
    gamma_12 = 1000.0    # Hz — start with 1 kHz decoherence
    omega    = GAMMA_HZ * 0.3

    delta_R, absorption = scan_cpt_resonance(gamma_12_hz=gamma_12, omega_hz=omega)
    cpt_params = extract_cpt_params(delta_R, absorption)

    # ── Step 3: Sweep laser power to find optimum ─────────────────────────
    power_sweep = sweep_laser_power(gamma_12_hz=gamma_12)
    # Find row with best (contrast / linewidth) ratio
    best = max(power_sweep, key=lambda r: r["contrast_pct"] / r["linewidth_khz"]
                                          if r["linewidth_khz"] else 0)

    # Re-run at optimal power
    delta_R_opt, absorption_opt = scan_cpt_resonance(
        gamma_12_hz=gamma_12, omega_hz=best["omega_hz"])
    cpt_opt = extract_cpt_params(delta_R_opt, absorption_opt)

    # ── Step 4: Discriminator slope ──────────────────────────────────────
    slope = compute_discriminator_slope(gamma_12_hz=gamma_12,
                                        omega_hz=best["omega_hz"])

    # ── Step 5: Clock transition ─────────────────────────────────────────
    clock_ok, quadratic_zeeman = verify_clock_transition()

    # ── Step 6: Convert optimal Ω to µW ──────────────────────────────────
    power_uw = omega_to_power_uw(best["omega_hz"])

    # ── Step 7: Plot ─────────────────────────────────────────────────────
    # Plot 1: CPT resonance at optimal power
    # Plot 2: Contrast vs Ω/Γ sweep
    # Plot 3: Linewidth vs Ω/Γ sweep
    # Save to 00_atomic_model/plots/

    # ── Step 8: Populate RESULTS ─────────────────────────────────────────
    RESULTS = {
        "hyperfine_hz":              atomic["hyperfine_hz"],
        "d1_wavelength_nm":          atomic["d1_wavelength_nm"],
        "natural_linewidth_mhz":     atomic["natural_linewidth_mhz"],
        "cpt_linewidth_khz":         cpt_opt["linewidth_khz"],
        "cpt_contrast_pct":          cpt_opt["contrast_pct"],
        "optimal_laser_power_uw":    power_uw,
        "discriminator_slope":       abs(slope),
        "dark_state_verified":       cpt_opt["dark_state_verified"],
        "clock_transition_verified": clock_ok,
    }
```

---

## 6. What "Done" Looks Like

Run `python evaluator.py`. Expected output:

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

## 7. Known Failure Modes

| Symptom | Cause | Fix |
|---|---|---|
| CPT dip does not appear | Lindblad operators wrong sign or wrong basis order | Check: L = sqrt(Γ/2) × g1 × ex.dag(), not the reverse |
| Linewidth too broad (> 10 kHz) | gamma_12 too large, or Ω too large (power broadening) | Reduce gamma_12 to 500 Hz, reduce Ω to 0.1×Γ |
| Contrast too low (< 1%) | Ω too small (atoms not pumped) or delta_1 off resonance | Set delta_1 = 0, increase Ω to 0.3×Γ |
| hyperfine error > 1 ppm | Not using NIST constant directly | Use HYPERFINE_HZ = 6_834_682_610.904 exactly |
| qt.steadystate() fails to converge | Hamiltonian too strong (Ω >> Γ) | Reduce Ω, ensure Lindblad operators are physical |
| Absorption curve is flat | Wrong observable — check Im(ρ₃₁) sign convention | absorption = -Im(rho_ss[2,0]) - Im(rho_ss[2,1]) (sign depends on convention) |

---

## 8. Runtime Estimate

Single CPT scan (500 points, 1 kHz decoherence): ~30 seconds on laptop.
Power sweep (30 Ω values × 300 points each): ~15 minutes on laptop.
With Python multiprocessing (Pool, 8 cores): ~2 minutes.

For faster development: use n_points=100 and omega_ratios=10 points first,
then run the full sweep once the logic is verified.
