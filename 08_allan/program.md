# Module 08: Allan Deviation — Program

## 1. Mission

Predict the Allan deviation of the clock from first principles, combining
all noise sources from upstream modules. This is the clock performance number
that determines whether the design is fundable and manufacturable.

If this module fails (ADEV > 5×10⁻¹⁰ at τ=1s), the design does not meet spec
and the root cause must be found before proceeding. Return to the failing module.

**What "done" means:**

1. ADEV @ τ=1s < 5×10⁻¹⁰ (design target).
2. ADEV @ τ=1s within 2× of Microchip SA65 (2.5×10⁻¹⁰).
3. Dominant noise at τ=1s is photon shot noise (not VCO, not thermal).
4. `python evaluator.py` exits 0.

---

## 2. Physics

### 2.1 The Fundamental CSAC Stability Formula

Short-term Allan deviation (white FM noise):
```
σ_y(τ) = (1 / (2π × f_hfs)) × (Δν_CPT / C) × (1 / SNR) × (1 / √τ)
```

where:
- f_hfs  = 6,834,682,610.904 Hz (hyperfine reference frequency)
- Δν_CPT = CPT linewidth (Hz) — from 00_atomic_model
- C       = CPT contrast (dimensionless fraction) — from 00_atomic_model
- SNR     = signal-to-noise ratio at photodetector — from 05_optical
- τ       = averaging time (s)

This formula is the key result. Physically: the clock precision is proportional
to how sharply we can locate the center of the CPT dip (Δν_CPT/C) relative to
the noise floor (1/SNR).

### 2.2 Shot Noise Contribution (dominant at short τ)

```
SNR_shot = sqrt(I_pd / (2 × e × BW))

ADEV_shot(τ) = (Δν_CPT / (C × f_hfs)) × sqrt(2 × e × BW / I_pd) × (1/√τ)
```

### 2.3 VCO Phase Noise Contribution

```
ADEV_VCO(τ) = sqrt(S_φ(f_servo) / f_VCO²) × (1/τ)
```

For white phase noise outside the servo bandwidth.

### 2.4 Thermal Noise Contribution

Temperature fluctuation δT causes frequency shift through N2 pressure:
```
ADEV_thermal(τ) = (δν_T / f_hfs) × (1/√τ)

δν_T = K_shift × δP_N2 = K_shift × P_N2 × (δT / T)
```

For PID stability δT = 0.01°C:
```
δν_T = 6700 × 50 × (0.01 / 358) = 9.4 Hz — negligible
```

---

## 3. Implementation

```python
import numpy as np

# ── Load results from all upstream modules ────────────────────────────
def load(module_name, key, default):
    try:
        import sys, os, importlib.util
        path = os.path.join(os.path.dirname(__file__), "..", module_name, "sim.py")
        spec = importlib.util.spec_from_file_location(module_name, os.path.normpath(path))
        if spec is None or spec.loader is None: return default
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)  # type: ignore[union-attr]
        return mod.RESULTS.get(key, default)
    except Exception:
        return default

F_HFS        = 6_834_682_610.904
cpt_lw_hz    = load("00_atomic_model", "cpt_linewidth_khz", 3.2) * 1e3
cpt_contrast = load("00_atomic_model", "cpt_contrast_pct",  4.8) / 100.0
snr          = load("05_optical",      "snr",               28000.0)
adev_vco     = load("06_rf_synthesis", "adev_from_vco_1s",  9e-15)
servo_bw_hz  = load("07_servo_loop",   "lock_bandwidth_hz", 30.0)


def adev_shot_noise(tau_arr, delta_nu, contrast, snr_val, f_hfs=F_HFS):
    """Allan deviation from photon shot noise (white FM, slope τ^-0.5)."""
    sigma_1s = (delta_nu / (contrast * f_hfs)) / snr_val
    return sigma_1s / np.sqrt(tau_arr)


def adev_vco_noise(tau_arr, adev_vco_1s):
    """Allan deviation from VCO phase noise (white PM, slope τ^-1)."""
    return adev_vco_1s / tau_arr


def adev_thermal(tau_arr, temp_stability_degc=0.01, P_N2_Torr=50.0,
                  T_K=358.0, f_hfs=F_HFS):
    """Allan deviation from thermal fluctuations."""
    k_shift_hz_per_torr = 6700.0
    delta_nu_thermal = k_shift_hz_per_torr * P_N2_Torr * (temp_stability_degc / T_K)
    sigma_thermal = delta_nu_thermal / f_hfs / np.sqrt(tau_arr)
    return sigma_thermal


def total_adev(tau_arr):
    """Combined ADEV from all noise sources (add in quadrature)."""
    shot    = adev_shot_noise(tau_arr, cpt_lw_hz, cpt_contrast, snr)
    vco     = adev_vco_noise(tau_arr, adev_vco)
    thermal = adev_thermal(tau_arr)
    return np.sqrt(shot**2 + vco**2 + thermal**2), shot, vco, thermal


# ── Compute at key averaging times ───────────────────────────────────
tau_points = np.array([1.0, 10.0, 100.0, 3600.0])
adev_total, adev_s, adev_v, adev_t = total_adev(tau_points)

# Identify dominant noise at τ=1s
sources_1s = {"shot_noise": adev_s[0], "vco_noise": adev_v[0], "thermal": adev_t[0]}
dominant   = max(sources_1s, key=sources_1s.get)

RESULTS = {
    "adev_1s":            adev_total[0],
    "adev_10s":           adev_total[1],
    "adev_100s":          adev_total[2],
    "adev_1hr":           adev_total[3],
    "flicker_floor":      adev_total[-1],
    "dominant_noise_1s":  dominant,
    "adev_shot_1s":       adev_s[0],
    "adev_vco_1s":        adev_v[0],
    "adev_thermal_1s":    adev_t[0],
}
```

---

## 4. What the Result Tells You

```
If ADEV_shot >> ADEV_vco and ADEV_thermal:  → design is optimal (shot-noise limited)
If ADEV_vco dominates:                       → fix 06_rf_synthesis phase noise
If ADEV_thermal dominates:                   → fix 04_thermal PID stability
If ADEV_shot too high:                       → improve CPT contrast or SNR (00, 05)
```

---

## 5. Known Failure Modes

| Symptom | Cause | Fix |
|---|---|---|
| ADEV > 1e-9 at 1s | CPT linewidth too broad OR contrast too low | Return to 00_atomic_model, increase N2 pressure, reduce decoherence |
| ADEV dominated by VCO | Wrong VCO phase noise spec used | Use -90 dBc/Hz for Crystek CVCO55, not a noisy VCO |
| ADEV flat (not τ^-0.5) | Flicker noise floor reached too fast | Indicates systematic bias — check lock-in demodulation in 07 |
