# Module 01: VCSEL Sideband — Program

## 1. Mission

Find the exact modulation index β and RF drive power that places maximum optical
power in the ±1 sidebands spaced at exactly the Rb-87 hyperfine frequency.

This is the lightest simulation in the project — pure Bessel function math.
It runs in seconds. The value it produces (β ≈ 1.84) goes into the BOM as
the VCSEL driver spec and into the RF chain design.

**What "done" means:**

1. `sim.py` runs and populates RESULTS with all fields.
2. `python evaluator.py` exits 0.
3. β within 0.05 of 1.8412 (mathematical optimum).
4. J₁(β) matches Bessel table to 0.5%.
5. Sideband spacing matches Rb hyperfine to < 1 kHz.

---

## 2. Physics

### 2.1 VCSEL Modulation

A VCSEL modulated at RF frequency f_m = 3.417341305 GHz produces an optical
field with phase modulation:

```
E(t) = E₀ × exp(i × ω_c × t + i × β × sin(ω_m × t))
```

Jacobi-Anger expansion into sidebands:
```
E(t) = E₀ × Σₙ  Jₙ(β) × exp(i × (ω_c + n × ω_m) × t)
```

Power in sideband n: Pₙ = |Jₙ(β)|² × P_total

The CPT needs the +1 and -1 sidebands. Their separation = 2 × f_m = 6.8347 GHz
= Rb-87 hyperfine splitting. The ±1 sideband power product is:

```
P_CPT ∝ |J₁(β)|² × |J₋₁(β)|² = J₁(β)⁴   (since J₋₁ = -J₁ for real β)
```

This is maximized when J₁(β) is at its peak, at β ≈ 1.8412.

### 2.2 Key Bessel Values (mathematical identities — must reproduce exactly)

```
J₀(1.8412) = 0.3275    (residual carrier power ∝ 10.7%)
J₁(1.8412) = 0.5819    (each CPT sideband power ∝ 33.9%)
J₂(1.8412) = 0.3061    (unused 2nd sideband power ∝ 9.4%)
```

Total power in ±1 sidebands at β_opt: 2 × 33.9% = 67.8%.

---

## 3. Implementation

```python
from scipy.special import jv
import numpy as np

# Constants from 00_atomic_model
HYPERFINE_HZ  = 6_834_682_610.904
F_MOD_HZ      = HYPERFINE_HZ / 2  # = 3,417,341,305.452 Hz

def compute_sideband_spectrum(beta, n_max=5):
    """
    Compute power fraction in each sideband for a given modulation index.

    Returns: dict {n: power_fraction} for n in [-n_max, +n_max]
    """
    return {n: jv(n, beta)**2 for n in range(-n_max, n_max+1)}

def find_optimal_beta():
    """
    Sweep β from 0 to 4 and find the value that maximizes |J₁(β)|².
    """
    betas = np.linspace(0.01, 4.0, 4000)
    j1_vals = jv(1, betas)
    # Maximise J1 (first sideband power)
    idx_opt = np.argmax(np.abs(j1_vals))
    return betas[idx_opt], j1_vals[idx_opt]

def compute_rf_power_dbm(beta, vcsel_fm_sensitivity_mhz_per_ma=500.0,
                          vcsel_impedance_ohm=50.0):
    """
    Estimate RF drive power needed to achieve modulation index β.

    The VCSEL FM sensitivity is typically 200–500 MHz/mA for a 795nm VCSEL.
    Required current amplitude: i_rf = (β × f_m) / sensitivity
    RF power: P = i_rf² × Z / 2
    """
    f_m_hz = F_MOD_HZ
    sensitivity_hz_per_a = vcsel_fm_sensitivity_mhz_per_ma * 1e6 / 1e-3

    # Current amplitude to achieve modulation depth β
    i_amplitude_a = beta * f_m_hz / sensitivity_hz_per_a
    power_w = 0.5 * i_amplitude_a**2 * vcsel_impedance_ohm
    power_dbm = 10 * np.log10(power_w * 1000)
    return power_dbm

# ── RESULTS ──────────────────────────────────────────────────────────
beta_opt, j1_opt = find_optimal_beta()
spectrum_opt = compute_sideband_spectrum(beta_opt)
sideband_power_pct = (spectrum_opt[1] + spectrum_opt[-1]) * 100

RESULTS = {
    "optimal_beta":             beta_opt,
    "j1_at_optimal":            abs(jv(1, beta_opt)),
    "j0_at_optimal":            abs(jv(0, beta_opt)),
    "sideband_power_pct":       sideband_power_pct,
    "sideband_spacing_ghz":     2 * F_MOD_HZ / 1e9,
    "rf_drive_power_dbm":       compute_rf_power_dbm(beta_opt),
}
```

---

## 4. Known Failure Modes

| Symptom | Cause | Fix |
|---|---|---|
| β ≠ 1.84 | Wrong sweep range or step | Check argmax on abs(J1), not J1 squared |
| J₁ value off by >1% | Wrong scipy call | Use `scipy.special.jv(1, beta)` not `jn(1, beta)` |
| Sideband spacing wrong | Used wrong hyperfine constant | Import HYPERFINE_HZ from 00_atomic_model |
