# Module 06: RF Synthesis — Program

## 1. Mission

Verify that a standard fractional-N PLL (ADF4351) can synthesize the exact
modulation frequency 3.417341305 GHz from a 10 MHz TCXO reference, with
sufficient frequency resolution to compensate the N2 pressure shift and
with phase noise low enough not to limit the clock ADEV.

**What "done" means:**

1. `sim.py` runs and populates RESULTS.
2. PLL divider ratio achieves < 1 Hz frequency error.
3. Tuning range covers N2 pressure shift from 02_buffer_gas.
4. VCO phase noise contribution to ADEV < 1×10⁻¹⁰ at τ=1s.
5. `python evaluator.py` exits 0.

---

## 2. Physics

### 2.1 PLL Frequency Synthesis

A fractional-N PLL:
```
f_VCO = (N + F/M) × f_ref / R

where:
  f_ref = 10.000000 MHz (TCXO)
  R     = reference divider
  N     = integer divider
  F/M   = fractional part (0 ≤ F < M)
```

Target: f_VCO = 3,417,341,305.452 Hz

Using ADF4351 (Analog Devices): f_ref = 10 MHz, R=1:
```
N + F/M = 3,417,341,305.452 / 10,000,000 = 341.7341305452
N = 341
F/M = 0.7341305452
```

With M = 4095 (ADF4351 max):
```
F = round(0.7341305452 × 4095) = 3007
Actual f = (341 + 3007/4095) × 10e6 = 3,417,341,318.73 Hz
Error = 13.3 Hz
```

With M=65535 (some other PLL chips) or using reference multiplication:
achievable resolution → sub-Hz. For our purposes, 13 Hz is fine because
the servo loop locks to the CPT resonance and corrects this offset.

### 2.2 VCO Phase Noise → ADEV Contribution

VCO phase noise S_φ(f) [dBc/Hz] converts to fractional frequency noise:
```
S_y(f) = S_φ(f) / f_VCO²
```

Contribution to ADEV at averaging time τ:
```
σ_y²(τ) = 2 × ∫₀^∞ S_y(f) × (sin(π f τ) / (π f τ))² df
```

For white phase noise floor S_φ = S₀ [flat]:
```
σ_y(τ) ≈ sqrt(S₀) / (f_VCO × τ)
```

Typical VCO at 3.4 GHz: S_φ = -90 dBc/Hz at 10 kHz offset.
```
σ_y(τ=1s) ≈ sqrt(10^(-9)) / 3.4e9 = 3.16e-5 / 3.4e9 = 9.3e-15
```

This is 50× better than our ADEV target of 5×10⁻¹⁰ → VCO noise is NOT limiting.

### 2.3 Tuning Range Requirement

The VCO must cover:
- Pressure shift from 02_buffer_gas (e.g., -335 kHz at 50 Torr N2)
- Temperature drift across operating range
- Initial frequency error from TCXO aging

Total required tuning range: ±500 kHz around f_VCO nominal.
Standard VCO tuning sensitivity: ~10–50 MHz/V → ±500 kHz needs only ±10–50 mV tuning voltage. No problem.

---

## 3. Implementation

```python
import numpy as np

# Constants
F_REF_HZ     = 10_000_000.0           # Hz (10 MHz TCXO)
F_TARGET_HZ  = 3_417_341_305.452      # Hz (half Rb hyperfine)

# ADF4351 parameters
ADF4351_N_MIN = 23
ADF4351_N_MAX = 65535
ADF4351_M_MAX = 4095     # modulus M (denominator)
ADF4351_R_MIN = 1

def find_pll_settings(f_target=F_TARGET_HZ, f_ref=F_REF_HZ, M_max=4095):
    """Find optimal N, F, M for PLL to hit f_target."""
    best_error = np.inf
    best = {}

    ratio = f_target / f_ref
    N     = int(ratio)
    frac  = ratio - N

    for M in range(M_max, M_max // 2, -1):   # try from max M downward
        F = round(frac * M)
        if F >= M:
            F = M - 1
        f_actual = (N + F / M) * f_ref
        error    = abs(f_actual - f_target)
        if error < best_error:
            best_error = error
            best = {"N": N, "F": F, "M": M,
                    "f_actual_hz": f_actual,
                    "error_hz": error}

    return best

def vco_phase_noise_to_adev(s_phi_dbc_at_10khz, f_vco=F_TARGET_HZ, tau=1.0):
    """Estimate ADEV contribution from VCO phase noise."""
    S_phi_linear = 10 ** (s_phi_dbc_at_10khz / 10)
    S_y_10khz    = S_phi_linear / f_vco**2
    # Assume white phase noise floor for conservative estimate
    adev = np.sqrt(S_y_10khz) / (f_vco * tau)
    return adev

def required_tuning_range(pressure_shift_khz):
    """VCO tuning range needed to cover pressure shift + margin."""
    return abs(pressure_shift_khz) * 1e3 * 3.0  # 3× margin in Hz

# ── Load pressure shift from 02_buffer_gas ───────────────────────────
try:
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "02_buffer_gas"))
    import sim as bg
    pressure_shift_hz = bg.RESULTS.get("pressure_shift_khz", -335.0) * 1e3
except Exception:
    pressure_shift_hz = -335_000.0   # default: 335 kHz shift at 50 Torr N2

pll     = find_pll_settings()
adev_vco = vco_phase_noise_to_adev(-90.0)  # typical VCO: -90 dBc/Hz @ 10kHz
tuning_range_hz = required_tuning_range(abs(pressure_shift_hz) / 1e3)

RESULTS = {
    "pll_N":                      pll["N"],
    "pll_F":                      pll["F"],
    "pll_M":                      pll["M"],
    "f_actual_hz":                pll["f_actual_hz"],
    "frequency_error_hz":         pll["error_hz"],
    "achievable_freq_step_hz":    F_REF_HZ / pll["M"],
    "tuning_range_hz":            tuning_range_hz,
    "vco_phase_noise_dbc":        -90.0,
    "adev_from_vco_1s":           adev_vco,
    "recommended_chip":           "ADF4351 (Analog Devices, $15)",
}
```

---

## 4. Known Failure Modes

| Symptom | Cause | Fix |
|---|---|---|
| Frequency error > 1 kHz | M too small | Use ADF5356 (M up to 16M) or multiply f_ref to 100 MHz first |
| ADEV from VCO > 1e-10 | VCO phase noise too high | Use lower-noise VCO (Crystek CVCO55, -100 dBc/Hz) |
| Tuning range insufficient | Pressure shift larger than expected | Check 02_buffer_gas results — verify K_shift coefficient |
