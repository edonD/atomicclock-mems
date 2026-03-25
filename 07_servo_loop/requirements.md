# 07_servo_loop — Requirements

**WAVE 3 | Tool: python-control | Depends on: 00_atomic_model + 05_optical + 06_rf_synthesis**

---

## Questions This Simulation Must Answer

1. Is the PID servo loop stable? What are the phase and gain margins?
2. What lock bandwidth is achievable? (determines how fast the clock recovers from perturbations)
3. What is the capture range? (how far off-resonance the loop can lock from)
4. Does frequency modulation dither cause measurable bias in the locked frequency?

---

## Inputs Required

| Parameter | Source |
|---|---|
| CPT discriminator slope (dI/df) | 00_atomic_model/results.md |
| Photodetector noise floor | 05_optical/results.md |
| VCO tuning sensitivity (Hz/V) | 06_rf_synthesis/results.md |
| VCO phase noise spectrum | 06_rf_synthesis/results.md |

---

## What to Simulate

- Model the full feedback loop in the Laplace domain
- Plant: VCO (integrator) + CPT resonance (dispersive lineshape)
- Sensor: photodetector + transimpedance amp + lock-in demodulator
- Controller: PID (tune gains)
- Open-loop Bode plot: extract phase margin and gain margin
- Closed-loop step response: verify no oscillation
- Noise analysis: compute frequency noise floor from photon shot noise + VCO noise

---

## Output to Extract into results.md

```
Phase margin          : _____ degrees   must be > 45°
Gain margin           : _____ dB        must be > 10 dB
Lock bandwidth        : _____ Hz        expected 10-100 Hz
Capture range         : _____ kHz       must be > CPT linewidth / 2
PID Kp                : _____
PID Ki                : _____
PID Kd                : _____
Frequency noise floor : _____ Hz/√Hz
```
