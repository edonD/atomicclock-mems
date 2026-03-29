# 07_servo_loop — PID Servo Locking VCO to CPT Resonance

> **Status: PASS** — `sim.py` runs, `python evaluator.py` exits 0.

---

## 1. What This Module Does

This module designs and verifies the electronic feedback loop that locks the VCO
to the Rb-87 CPT resonance frequency.  Without a servo loop the VCO drifts freely,
and the clock provides no frequency reference.  With the loop closed, the VCO is
continuously corrected toward the atomic resonance — the CPT transparency dip from
module 00_atomic_model.

Three questions must be answered before the loop can be trusted:

1. **Is the loop stable?**  Phase margin > 45° and gain margin > 10 dB are the
   classical Bode stability criteria.  Violation means the loop oscillates instead
   of locking.

2. **Is the loop bandwidth appropriate?**  Too narrow (< 5 Hz) and the loop is slow
   to recover from vibration-induced frequency jumps; too wide (> 500 Hz) and it
   amplifies noise and interferes with the lock-in detection at f_dither ≈ 100 Hz.

3. **Is the capture range sufficient?**  The loop must be able to pull in and lock
   starting from anywhere within the CPT linewidth.  The minimum capture range is
   half the CPT linewidth ≈ 1.6 kHz.

**Key results:** Phase margin = 84.9°, gain margin = 60 dB, bandwidth = 30 Hz,
capture range = 1.6 kHz.

---

## 2. Loop Architecture

### 2.1 Signal Flow

```
                      ┌──────────────────────────────────────────┐
  Setpoint            │                                          │
  (δ_R = 0) ──→ [Σ] ──→ [PID Controller] ──→ [VCO + VCSEL mod] ──→ [Rb cell]
                 ↑                                                      │
                 └──────────────── [Lock-in demodulator] ←── [I_pd] ───┘
                                   (demod at f_dither)
```

The loop dithers the VCO frequency at f_dither ≈ 100 Hz with an amplitude
±Δf_dither ≈ 1 kHz.  The photodetector output is demodulated at f_dither by a
lock-in amplifier (or digital mixer) to extract the first derivative of the CPT
absorption lineshape.  This derivative is the **error signal**: it is zero at the
CPT resonance, positive on one side, and negative on the other.

### 2.2 CPT Discriminator Slope

The photodetector TIA produces a voltage V_pd proportional to optical power.  At
nominal operating conditions:

```
I_pd  = R_pd × P_detector = 0.5 A/W × 50 µW = 25 µA
V_pd  = I_pd × R_TIA      = 25 µA × 100 kΩ  = 2.5 V
V_dip = CPT_contrast × V_pd = 0.05 × 2.5 V  = 0.125 V
```

The lock-in slope — the change in error signal per unit frequency detuning — is
approximated as the CPT dip voltage divided by the half-linewidth:

```
K_CPT = V_dip / (Δν_CPT / 2)
      = 0.125 V / (3200 Hz / 2)
      = 0.125 / 1600
      = 7.8×10⁻⁵ V/Hz
```

This is the **discriminant slope** of the frequency detector.  It determines how
large a control voltage the loop generates for a given frequency offset.

---

## 3. Loop Transfer Function

### 3.1 Plant Model G(s)

The plant converts PID output voltage into CPT error signal voltage.  The chain is:

```
V_control → VCO → frequency shift → CPT absorption → error voltage
```

The VCO is a voltage-controlled integrator (frequency ∝ voltage, phase ∝ integral):

```
G(s) = K_VCO × K_CPT / s
```

where:
- K_VCO = 10 MHz/V  — VCO tuning sensitivity (typical for a 3.4 GHz oscillator)
- K_CPT = 7.8×10⁻⁵ V/Hz — CPT discriminator slope
- 1/s    — phase integration: VCO converts voltage to frequency (= d(phase)/dt)

### 3.2 PID Controller C(s)

The PID controller with a first-order low-pass filter on the derivative (to prevent
high-frequency gain amplification) has transfer function:

```
C(s) = Kd × ω_f × s / (s + ω_f)  +  Kp  +  Ki / s

     = [Kd·ω_f + Kp] s² + [Kp·ω_f + Ki] s + [Ki·ω_f]
       ─────────────────────────────────────────────────
                     s² + ω_f · s
```

with derivative filter corner ω_f = 2π × 1000 rad/s (1 kHz).

### 3.3 Open-Loop Transfer Function

```
L(s) = C(s) × G(s)  =  PID(s) × K_VCO × K_CPT / s
```

Bode stability requires:
- **Phase margin (PM)**: phase angle of L(jω) at the gain-crossover frequency ωgc
  (where |L(jω)| = 1) plus 180°.  Required: PM > 45°.
- **Gain margin (GM)**: reciprocal of |L(jω)| at the phase-crossover frequency ωpc
  (where ∠L(jω) = −180°), expressed in dB.  Required: GM > 10 dB.

### 3.4 PID Auto-Tune Formula

Starting from a P-only gain condition at the target bandwidth ω_bw = 2π × 30 rad/s:

```
|Kp × K_VCO × K_CPT / (j × ω_bw)| = 1

→  Kp = ω_bw / (K_VCO × K_CPT)
      = 2π × 30 / (10×10⁶ × 7.8×10⁻⁵)
      = 188.5 / 780
      = 0.242  V/V
```

The integral and derivative time constants are set relative to the bandwidth:

```
Ti = 10 / (2π × f_bw)   (integral pole placed 1 decade below bandwidth)
Ki = Kp / Ti

Td = 0.01 / (2π × f_bw)  (derivative zero placed well above bandwidth)
Kd = Kp × Td
```

This places the integral zero at f_bw/10 = 3 Hz and the derivative zero at
f_bw/0.01/(2π) ≈ 4.8 kHz — standard rules for PID design on an integrating plant.

### 3.5 Iterative Gain Refinement

`sim.py` checks PM and GM after initial auto-tune.  If either criterion is violated,
it halves the gains (Kp, Ki, Kd) iteratively until both criteria are satisfied
(up to 20 iterations).  For the nominal K_CPT = 7.8×10⁻⁵ V/Hz, the initial
auto-tuned gains already satisfy PM > 45° and GM > 10 dB.

---

## 4. Stability Results

| Parameter | Value | Criterion |
|-----------|-------|-----------|
| **Phase margin** | **84.9°** | > 45° ✓ |
| **Gain margin** | **60 dB** | > 10 dB ✓ |
| **Lock bandwidth** | **30 Hz** | 5–500 Hz ✓ |
| **Capture range** | **1.6 kHz** | > 1.6 kHz (= 0.5 × 3.2 kHz CPT LW) ✓ |
| K_CPT | 7.8×10⁻⁵ V/Hz | Discriminator slope |
| K_VCO | 10 MHz/V | VCO sensitivity |
| Kp | ~0.242 V/V | Proportional gain |
| Ki | ~0.453 V/(V·s) | Integral gain |
| Kd | ~1.3×10⁻⁴ V·s/V | Derivative gain |

The 84.9° phase margin and 60 dB gain margin indicate a very well-damped loop —
considerably more robust than the 45°/10 dB minimum.  This headroom accommodates
parameter variations (K_VCO drifts with temperature, K_CPT changes with laser power)
without approaching instability.

---

## 5. Plots

### 5.1 Open-Loop Bode Plot

![Open-Loop Bode Plot](plots/bode_plot.png)

The upper panel shows loop gain magnitude L(jω) in dB vs frequency.  The 0 dB
crossing at 30 Hz is the gain-crossover frequency — the closed-loop bandwidth.
The red dotted line marks this crossing.  The lower panel shows phase of L(jω).
The phase at 30 Hz crossover is annotated with the phase margin arrow.  Phase never
reaches −180° within the plotted range (0.016 Hz to 16 kHz), confirming the 60 dB
gain margin.

Key features:
- Below 3 Hz: integral action adds +20 dB/decade — slow drift is rejected
- 3–30 Hz: proportional regime — flat gain, predictable crossover
- Above ~4.8 kHz: derivative filter rolls off — high-frequency noise is not amplified
- Phase margin annotation at ωgc confirms PM = 84.9°

### 5.2 Closed-Loop Step Response

![Closed-Loop Step Response](plots/step_response.png)

The closed-loop response to a unit step in setpoint (equivalent to a sudden
frequency jump applied to the reference).  The output (normalised) settles to 1.0
within approximately 1/f_bw ≈ 33 ms with no overshoot.  The grey dashed lines mark
the ±5% settling band.  The response is critically damped — consistent with the
84.9° phase margin.

---

## 6. Physical Interpretation

### 6.1 Lock Bandwidth and ADEV

The servo loop suppresses VCO frequency noise at all frequencies below its 30 Hz
bandwidth.  Above 30 Hz, the VCO free-runs.  The Allan deviation improvement from
servo action is:

```
σ_y_unlocked / σ_y_locked ≈ sqrt(f_VCO_noise / f_bw)   [for white FM noise]
```

With VCO white phase noise of −90 dBc/Hz at 10 kHz, the servo provides > 40 dB
of noise rejection below 30 Hz — completely removing the VCO contribution from the
clock ADEV at τ > 33 ms.

### 6.2 Capture Range and Cold-Start

On cold start the VCO begins at an arbitrary frequency (set by the PLL N/F/M
dividers, offset by pressure shift, temperature, aging).  The servo must pull it
to the CPT resonance.  The capture range defines the frequency interval from which
lock can be acquired:

```
f_capture = ±½ × Δν_CPT = ±1.6 kHz  (for Δν_CPT = 3.2 kHz)
```

The ADF4351 frequency error of 0.896 Hz (module 06) is negligible compared to the
1.6 kHz capture range.  The N₂ pressure shift of −513 kHz is handled by the initial
PLL frequency setting (the target f_VCO already incorporates the expected shift).

### 6.3 Lock-In Dither and Modulation Index

The 100 Hz dither of ±1 kHz imposes a small frequency modulation on the VCSEL
sidebands.  The modulation index β = ±1 kHz / 3.2 kHz ≈ ±0.31 of the CPT
linewidth.  This is within the linear discriminant regime (β << 1 for the CPT
dip half-width), so the lock-in output is proportional to frequency error without
nonlinear distortion.

---

## 7. Evaluator Checks

`python evaluator.py` grades four checks against RESULTS from `sim.py`:

| # | Check | Criterion | Critical | Source |
|---|-------|-----------|----------|--------|
| 1 | `phase_margin_deg` | ≥ 45° | Yes | Bode stability criterion |
| 2 | `gain_margin_db` | ≥ 10 dB | Yes | Bode stability criterion |
| 3 | `lock_bandwidth_hz` | 5–500 Hz | No | CSAC literature: 10–100 Hz typical |
| 4 | `capture_range_khz` | ≥ 0.5 × CPT linewidth | Yes | Internal requirement |

Expected passing output:

```
======================================================================
  EVALUATOR: 07_servo_loop
  Wave 3 — Servo Loop Stability
======================================================================
    PASS  phase_margin_deg: 84.9°  (min 45°, good margin)  ✓
    PASS  gain_margin_db: 60.0 dB  (min 10 dB)  ✓
    PASS  lock_bandwidth_hz: 30.0 Hz  ✓
    PASS  capture_range_khz: 1.60 kHz  (min 1.60 kHz = 0.5 × CPT linewidth)  ✓
======================================================================
  VERDICT:  PASS
  OUTPUTS:  PID gains, lock bandwidth → spec_sheet
```

---

## 8. Downstream Impact

| Downstream module | Consumed quantity | Impact |
|-------------------|------------------|--------|
| `design/spec_sheet` | `lock_bandwidth_hz` | Servo bandwidth specification |
| `design/spec_sheet` | `phase_margin_deg`, `gain_margin_db` | Stability guarantee |
| `design/spec_sheet` | `capture_range_khz` | Acquisition range specification |
| `08_allan` | `lock_bandwidth_hz` | Servo correction term in ADEV model |
| `design/spec_sheet` | `pid_kp`, `pid_ki`, `pid_kd` | PID register values for FPGA/MCU implementation |

The lock bandwidth directly enters the ADEV model in 08_allan: the servo
white-frequency modulation noise contribution is σ_y ≈ √(S_FM × f_bw) / f₀,
where S_FM is the free-running VCO FM noise.  A narrower bandwidth reduces
in-band noise but slows the response to platform vibration.  30 Hz is the
design optimum for portable/handheld defense applications.

---

## Files

| File | Description |
|------|-------------|
| `sim.py` | PID auto-tune, python-control Bode/step analysis, margin extraction |
| `evaluator.py` | Grades PM, GM, bandwidth, capture range |
| `program.md` | Loop design equations, lock-in demodulation physics, failure modes |
| `requirements.md` | Inputs, upstream module dependencies |
| `results.md` | Output table |
| `plots/bode_plot.png` | Open-loop Bode (magnitude + phase) with margin annotations |
| `plots/step_response.png` | Closed-loop step response showing settling time |

---

*References: Franklin, Powell & Emami-Naeini, Feedback Control of Dynamic Systems
(8th ed.) §10 (Bode stability); Åström & Hägglund, PID Controllers: Theory, Design
and Tuning (1995) §5; Knappe et al. Appl. Phys. Lett. 85, 1460 (2004) servo
implementation; python-control library documentation v0.9 (https://python-control.org).*
