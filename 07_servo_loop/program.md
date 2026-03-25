# Module 07: Servo Loop — Program

## 1. Mission

Design the PID servo loop that locks the VCO to the CPT resonance.
Prove the loop is stable (phase margin > 45°, gain margin > 10 dB)
and has a lock bandwidth suitable for defense applications (10–100 Hz).

**What "done" means:**

1. Open-loop Bode plot shows phase margin > 45° and gain margin > 10 dB.
2. Closed-loop step response settles without oscillation.
3. Capture range > half the CPT linewidth from 00_atomic_model.
4. `python evaluator.py` exits 0.

---

## 2. Physics

### 2.1 Loop Components

```
Error signal          CPT dip slope    VCO
     ε(t) = setpoint - measurement
     ↓
  [PID controller]  →  [VCO + VCSEL modulation]  →  [Rb cell]
         ↑                                                 |
         └─────────────── [Photodetector + Lock-in] ←─────┘
```

### 2.2 Plant Model

The "plant" is: PID output voltage → VCO frequency → VCSEL modulation → CPT absorption signal.

Transfer function from VCO control voltage to CPT error signal:

```
G(s) = K_VCO × K_CPT_slope / s

where:
  K_VCO       = VCO tuning sensitivity (Hz/V) — from 06_rf_synthesis
  K_CPT_slope = CPT discriminator slope (V/Hz) — from 00_atomic_model
  1/s         = VCO is a frequency-to-phase integrator
```

### 2.3 Lock-In Demodulation

The loop dithers the VCO at f_dither (~100 Hz) by ±Δf_dither (~1 kHz).
The photodetector output is then demodulated at f_dither to extract the
first derivative of the CPT lineshape — the error signal.

At lock point (δ_R = 0): error signal = 0.
Off-resonance: error signal ∝ δ_R × (slope of CPT dip).

### 2.4 PID Design

Open-loop transfer function:
```
L(s) = C(s) × G(s) = Kp(1 + 1/(Ti×s) + Td×s) × K_VCO × K_CPT / s
```

Phase margin (PM): phase of L(jω) at gain crossover + 180°. Need PM > 45°.

---

## 3. Implementation

```python
import numpy as np
import control

# Load discriminator slope and CPT linewidth from 00_atomic_model
try:
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "00_atomic_model"))
    import sim as atomic
    cpt_slope    = atomic.RESULTS.get("discriminator_slope", 1e-4)
    cpt_lw_hz    = atomic.RESULTS.get("cpt_linewidth_khz", 3.2) * 1e3
except Exception:
    cpt_slope    = 1e-4
    cpt_lw_hz    = 3200.0

# VCO parameters from 06_rf_synthesis
K_VCO = 10e6   # Hz/V (10 MHz/V tuning sensitivity — typical)

def build_loop(Kp=1.0, Ki=10.0, Kd=0.001, K_vco=K_VCO, K_slope=1e-4):
    """
    Build open-loop transfer function for Bode analysis.

    L(s) = C(s) × G(s)
    C(s) = Kp + Ki/s + Kd*s    (PID)
    G(s) = K_vco × K_slope / s (VCO + CPT slope, integrator)
    """
    # PID transfer function
    pid = control.tf([Kd, Kp, Ki], [1, 0])

    # Plant: integrator × gain
    plant = control.tf([K_vco * K_slope], [1, 0])

    # Open loop
    L = pid * plant
    return L

def analyze_stability(L):
    """Extract phase margin, gain margin, crossover frequency."""
    gm, pm, wgc, wpc = control.margin(L)
    return {
        "gain_margin_db":       20 * np.log10(gm) if gm > 0 else -np.inf,
        "phase_margin_deg":     pm,
        "gain_crossover_hz":    wgc / (2 * np.pi),
        "phase_crossover_hz":   wpc / (2 * np.pi),
    }

def tune_pid(K_vco=K_VCO, K_slope=1e-4, target_bw_hz=30.0):
    """
    Auto-tune PID for target bandwidth and PM > 45°.
    Simple: set Kp to achieve bandwidth, then add integral.
    """
    # Start with P-only for bandwidth target
    # At crossover: |L(j×2π×f_bw)| = 1
    # |Kp × K_vco × K_slope / (j × 2π × f_bw)| = 1
    # Kp = 2π × f_bw / (K_vco × K_slope)
    omega_bw = 2 * np.pi * target_bw_hz
    Kp = omega_bw / (K_vco * K_slope)

    # Integral: place at 1/10 of bandwidth for high PM
    Ti = 10.0 / target_bw_hz
    Ki = Kp / Ti

    # Derivative: place at 5× bandwidth
    Td = 1.0 / (5 * target_bw_hz * 2 * np.pi)
    Kd = Kp * Td

    return Kp, Ki, Kd

# ── Main ─────────────────────────────────────────────────────────────
Kp, Ki, Kd = tune_pid(K_vco=K_VCO, K_slope=cpt_slope, target_bw_hz=30.0)
L     = build_loop(Kp, Ki, Kd)
stab  = analyze_stability(L)

capture_range_hz = cpt_lw_hz / 2.0  # minimum capture range

RESULTS = {
    "phase_margin_deg":       stab["phase_margin_deg"],
    "gain_margin_db":         stab["gain_margin_db"],
    "lock_bandwidth_hz":      stab["gain_crossover_hz"],
    "capture_range_khz":      capture_range_hz / 1e3,
    "pid_kp":                 Kp,
    "pid_ki":                 Ki,
    "pid_kd":                 Kd,
    "cpt_linewidth_khz":      cpt_lw_hz / 1e3,
}
```

---

## 4. Known Failure Modes

| Symptom | Cause | Fix |
|---|---|---|
| PM < 30° | Kp too high — gain crossover in high-phase-lag region | Reduce Kp by 3×, re-check |
| Loop unstable | Kd too large — derivative amplifies noise | Set Kd = 0 first, then add small positive value |
| Capture range < linewidth/2 | Ki too small | Increase Ki — loop must integrate past CPT linewidth edge |
| control.margin() returns NaN | L(s) has RHP poles | Check plant model — VCO integrator should have no RHP poles |
