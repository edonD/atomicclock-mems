# 06_rf_synthesis — ADF4351 Fractional-N PLL Synthesis

> **Status: PASS** — `sim.py` runs, `python evaluator.py` exits 0.

---

## 1. What This Module Does

The MEMS atomic clock needs a microwave oscillator locked to exactly half the
Rb-87 hyperfine frequency:

```
f_VCO = f_hfs / 2 = 6,834,682,610.904 Hz / 2 = 3,417,341,305.452 Hz
```

This frequency modulates the VCSEL so that its optical sidebands are separated by
exactly f_hfs, driving both legs of the CPT Λ transition simultaneously.

This module proves that the ADF4351 fractional-N PLL synthesizer IC can generate
that frequency from a standard 10 MHz TCXO reference with:

1. **< 1 Hz frequency error** — residual offset corrected by the servo loop
2. **Tuning range covering the N₂ pressure shift** (≈ −513 kHz from 02_buffer_gas)
3. **Phase noise contribution to ADEV** well below the 5×10⁻¹⁰ clock target

**Key results:** N=341, F=798, M=1087, frequency error = 0.896 Hz,
ADEV from VCO = 9.25×10⁻¹⁵ at τ=1s (10,807× below the clock target).

---

## 2. PLL Frequency Synthesis

### 2.1 Fractional-N Architecture

The ADF4351 (Analog Devices) is a 35 MHz–4.4 GHz PLL with a fractional-N divider.
The output frequency is:

```
f_VCO = (N + F/M) × f_ref / R

where:
  f_ref  = 10,000,000 Hz   (10 MHz TCXO reference)
  R      = 1               (reference divider — bypassed)
  N      = integer part of f_VCO / f_ref   (23 ≤ N ≤ 65535)
  F/M    = fractional part                 (0 ≤ F < M, 2 ≤ M ≤ 4095)
```

### 2.2 Divider Search Algorithm

The ratio f_VCO / f_ref = 341.7341305452 decomposes as:

```
N    = int(341.7341305452) = 341
frac = 341.7341305452 − 341 = 0.7341305452
```

For each modulus M from 2 to 4095, `sim.py` computes:

```python
F = round(frac × M)
f_actual = (N + F/M) × f_ref
error    = |f_actual − f_target|
```

The best M minimises the error.  The achievable frequency resolution is:

```
δf = f_ref / M = 10 MHz / M
```

At M = 1087:  δf = 10,000,000 / 1087 = 9,199.6 Hz per step.
The fractional algorithm effectively interpolates between adjacent integer steps,
so the achievable granularity within one M-step is ~9.2 kHz — but the exhaustive
search finds the specific F that lands within 0.896 Hz of the target.

### 2.3 Chosen Settings

| Parameter | Value | Constraint |
|-----------|-------|-----------|
| Integer divider N | **341** | 23–65535 ADF4351 limit |
| Fractional numerator F | **798** | 0 ≤ F < M |
| Modulus M | **1087** | 2–4095 ADF4351 limit |
| Actual f_VCO | 3,417,341,306.348 Hz | — |
| **Frequency error** | **0.896 Hz** | < 1 Hz ✓ |
| Freq step (f_ref/M) | 9,199.6 Hz | — |

The 0.896 Hz static offset is corrected in real time by the servo loop (module 07),
which pulls the VCO onto the CPT resonance to sub-Hz precision.

### 2.4 Alternative: 100 MHz Reference

Multiplying the TCXO to 100 MHz before the PLL input uses ADF4351 with N=34, F=377,
M=2174, giving a nearly identical 0.90 Hz error.  The direct 10 MHz path is preferred
(one fewer component, lower phase noise added by the multiplier).

---

## 3. Phase Noise to ADEV Conversion

### 3.1 Phase Noise Spectral Density

VCO phase noise is specified as S_φ(f) in dBc/Hz at a given offset frequency f.
The fractional frequency noise spectral density is:

```
S_y(f) = S_φ(f) / f_VCO²
```

For white phase noise (flat S_φ = S₀):

```
σ_y(τ) = sqrt(S₀) / (f_VCO × τ)
```

This gives ADEV ∝ τ⁻¹ — the characteristic slope of phase-noise-limited clocks
on a log-log ADEV plot.

### 3.2 Full ADEV Integral

For arbitrary S_φ(f), the Allan variance is:

```
σ_y²(τ) = 2 × ∫₀^∞  S_y(f) × [sin(π f τ) / (π f τ)]²  df
```

The (sin/x)² kernel is the transfer function of the ADEV estimator; it suppresses
noise at frequencies above 1/(2τ).

### 3.3 Servo-Bandwidth Correction

The CPT servo loop (module 07, bandwidth ≈ 30 Hz) actively suppresses VCO frequency
noise below its bandwidth.  Outside the servo bandwidth, the free-running VCO phase
noise is the dominant contribution:

```
σ_y_servo(τ) ≈ sqrt(S₀ × f_servo_bw) / (f_VCO × τ)
```

At −90 dBc/Hz (S₀ = 10⁻⁹ rad²/Hz) and f_VCO = 3.4174 GHz with τ = 1 s:

```
σ_y(1s) = sqrt(10⁻⁹) / (3.4174×10⁹ × 1)
         = 3.162×10⁻⁵ / 3.4174×10⁹
         = 9.25×10⁻¹⁵
```

The clock target is 5×10⁻¹⁰.  The VCO margin is 5×10⁻¹⁰ / 9.25×10⁻¹⁵ = **54,054×**.
VCO phase noise is completely non-limiting.

---

## 4. Tuning Range Requirement

### 4.1 N₂ Pressure Shift

Buffer gas N₂ shifts the Rb hyperfine frequency by approximately
−6700 Hz/Torr (from 02_buffer_gas).  At the nominal 76.6 Torr:

```
Δf_hfs ≈ −6700 Hz/Torr × 76.6 Torr = −513,220 Hz ≈ −513 kHz
```

The VCO frequency must be pre-shifted by Δf_hfs/2 ≈ −256 kHz from the free-space
value to compensate.  The servo handles the fine correction, but the VCO tuning
range must cover the full shift plus margin.

### 4.2 Required Tuning Range

`sim.py` applies a 3× safety margin:

```
f_tuning = |Δf_pressure| × 3 = 513 kHz × 3 = 1,539 kHz
```

The ADF4351 VCO has tuning sensitivity K_VCO ≈ 10 MHz/V.  The required tuning
voltage swing:

```
V_tuning = f_tuning / K_VCO = 1,539,000 Hz / 10,000,000 Hz/V = 154 mV
```

A standard 12-bit DAC at 3.3 V supply provides ~0.8 mV resolution — more than
adequate.  No special high-voltage varactor tuning is required.

---

## 5. Plots

### 5.1 PLL Frequency Error vs Modulus M

![PLL Frequency Error vs M](plots/pll_frequency_error.png)

The main line shows the frequency synthesis error (log scale) for every ADF4351
modulus M from 2 to 4095.  The error varies non-monotonically because different M
values happen to produce better rational approximations to the fractional part
0.7341305452.  The red dot marks the optimal M=1087 (0.896 Hz error); the green
triangle marks M=4095 (a common default).  Orange bars mark reference checkpoints
at M = 100, 500, 1000, 2000, 4095 to show the landscape.  The dashed red line is
the 1 Hz pass/fail threshold.

### 5.2 VCO ADEV vs Averaging Time

![Phase Noise ADEV](plots/phase_noise_adev.png)

Two ADEV curves are plotted on logarithmic axes:

- **Blue solid** — free-running VCO white phase noise
  σ_y ∝ τ⁻¹ from S_φ = −90 dBc/Hz at 10 kHz offset
- **Orange dashed** — servo-limited VCO contribution
  (noise below 30 Hz servo bandwidth is suppressed)
- **Crimson dash-dot** — clock target ADEV = 5×10⁻¹⁰ (horizontal line)
- **Blue dot** — VCO ADEV at τ=1s = 9.25×10⁻¹⁵

The green shading indicates the region where the VCO noise is safely below the
clock target.  The VCO is non-limiting at all averaging times from 1 s to 10,000 s.

---

## 6. Evaluator Checks

`python evaluator.py` runs seven check groups against `RESULTS`:

| # | Check | Criterion | Source |
|---|-------|-----------|--------|
| 1 | All required keys present | 10 keys | — |
| 2 | `pll_N` valid ADF4351 integer | 23–65535 | ADF4351 datasheet |
| 3 | `pll_F` valid (0 ≤ F < M) | Integer | ADF4351 datasheet |
| 4 | `pll_M` valid (2–4095) | Integer | ADF4351 datasheet |
| 5 | `frequency_error_hz` < 1 Hz | < 1.0 Hz | Program §2.1 |
| 6 | `tuning_range_hz` ≥ 2× pressure shift | ≥ 2× \|Δf_pressure\| | Program §2.3 |
| 7 | `adev_from_vco_1s` < 1×10⁻¹⁰ | < 1e-10 | Phase noise budget |

Expected passing output:

```
==============================================================
06_rf_synthesis — Evaluator
==============================================================

--- Required keys ---
  [PASS]  All 10 required keys present

--- PLL divider validity ---
  [PASS]  pll_N type is int: int
  [PASS]  pll_F type is int: int
  [PASS]  pll_M type is int: int
  [PASS]  pll_N in ADF4351 range: 341  (allowed 23..65535)
  [PASS]  pll_F valid (0 <= F < M): 798  (M=1087)
  [PASS]  pll_M valid (2 <= M <= 4095): 1087

--- Frequency synthesis ---
  [PASS]  f_actual close to f_target: 3417341306.3480 Hz
  [PASS]  Frequency error < 1 Hz: 0.8960 Hz  (threshold = 1.0 Hz)
  [PASS]  achievable_freq_step_hz is positive: 9199.632 Hz

--- Tuning range ---
  [PASS]  Tuning range >= 2× pressure shift: 1539.3 kHz  (need >= 1026.2 kHz)
  [PASS]  Tuning range > 0: 1539300 Hz

--- VCO phase noise & ADEV ---
  [PASS]  vco_phase_noise_dbc == -90.0 dBc/Hz: -90.0 dBc/Hz
  [PASS]  ADEV from VCO at tau=1s < 1e-10: 9.252e-15  (threshold = 1e-10)
          VCO ADEV margin vs target: 10807×

--- Recommended chip ---
  [PASS]  recommended_chip non-empty string: 'ADF4351 (Analog Devices, ~$15, 35 MHz-4.4 GHz)'

--- Plot files ---
  [PASS]  plots/pll_frequency_error.png exists: found
  [PASS]  plots/phase_noise_adev.png exists: found

==============================================================
  RESULT: PASS  (0 failures)

  PLL: N=341, F=798, M=1087
  Frequency error : 0.8960 Hz
  ADEV (VCO, 1s)  : 9.25e-15  (10807× below limit)
  Tuning range    : 1539.3 kHz
  Chip            : ADF4351 (Analog Devices, ~$15, 35 MHz-4.4 GHz)
==============================================================
```

---

## 7. Downstream Impact

| Downstream module | Consumed quantity | Impact |
|-------------------|------------------|--------|
| `07_servo_loop` | `frequency_error_hz` — initial VCO offset | Sets servo pull-in requirement |
| `07_servo_loop` | `tuning_range_hz` — confirms VCO range | Informs K_VCO parameter |
| `08_allan` | `adev_from_vco_1s` — VCO noise floor | One term in total ADEV budget |
| `design/spec_sheet` | PLL chip, N/F/M settings | BOM and hardware specification |

The VCO ADEV of 9.25×10⁻¹⁵ contributes negligibly to the clock ADEV budget
(target 5×10⁻¹⁰): VCO noise is > 50,000× below the target and can be ignored
in the 08_allan noise model.  The dominant ADEV terms are the CPT photon shot noise
and the ground-state decoherence from 00_atomic_model.

---

## Files

| File | Description |
|------|-------------|
| `sim.py` | ADF4351 divider search, phase-noise ADEV calculation, M-sweep plots |
| `evaluator.py` | Grades frequency error, tuning range, ADEV, divider validity |
| `program.md` | Physics derivation, fractional-N architecture, failure modes |
| `requirements.md` | Inputs, upstream dependencies, ADF4351 hardware limits |
| `results.md` | Output table (PASS) |
| `plots/pll_frequency_error.png` | Frequency error vs ADF4351 modulus M |
| `plots/phase_noise_adev.png` | VCO ADEV contribution vs averaging time |

---

*References: Analog Devices ADF4351 datasheet Rev. C (2013); Riley, W.J., NIST
Technical Note 1337 — Handbook of Frequency Stability Analysis (2008) §3.2;
Walls & Vig, "Fundamental Limits on the Frequency Instabilities of Crystal Oscillators,"
IEEE Trans. UFFC 42, 576 (1995); Knappe et al. Appl. Phys. Lett. 85, 1460 (2004).*
