# Module 05: Optical — Program

## 1. Mission

Verify the VCSEL beam passes cleanly through the cell without clipping,
compute the optical power at the photodetector, and calculate the SNR
that feeds directly into the Allan deviation estimate in 08_allan.

**What "done" means:**

1. `sim.py` runs and populates RESULTS.
2. Beam diameter at cell exit < cavity diameter.
3. Optical power at detector > 10 µW (enough for shot-noise limited detection).
4. SNR > 100 (shot-noise limited).
5. `python evaluator.py` exits 0.

---

## 2. Physics

### 2.1 ABCD Beam Propagation

A Gaussian beam propagating through a sequence of optical elements:

```
[r'  ]   [A B] [r ]
[r/R'] = [C D] [1/R]
```

For free space propagation (length L):
```
M = [[1, L], [0, 1]]
```

For glass window (refractive index n, thickness t):
```
M = [[1, t/n], [0, 1]]
```

Gaussian beam waist evolution:
```
w(z) = w₀ × sqrt(1 + (z/z_R)²)       z_R = π × w₀² / λ (Rayleigh range)
```

For VCSEL divergence half-angle θ:
```
w₀ = λ / (π × tan(θ)) ≈ λ / (π × θ)    [for small θ]
```

Typical VCSEL 795nm: θ ≈ 7–10° half-angle, w₀ ≈ 3–5 µm at facet.
After propagation through the cell (~1mm glass + 1mm Rb + 1mm glass):
the beam expands significantly unless collimated.

For our MEMS design (no separate collimating lens — VCSEL directly below cell):
```
z_total ≈ 2.6 mm (0.3mm glass + 1mm Si cavity + 0.3mm glass + ~1mm gap)
w(z_total) = w₀ × sqrt(1 + (z_total/z_R)²)
```

For w₀ = 4µm, λ = 795nm, z_R = π×(4e-6)²/795e-9 = 63µm:
```
w(2.6mm) = 4e-6 × sqrt(1 + (2.6e-3/63e-6)²) ≈ 4e-6 × 41 = 164µm = 0.164mm
```

Cavity diameter 1.5mm >> 0.164mm → no clipping problem. Good.

### 2.2 Absorption

Beer-Lambert through the cell:
```
I_out = I_in × exp(-α × L_Rb)
```

With buffer gas, the D1 line is pressure-broadened → lower peak absorption:
```
α_broadened = α_peak × (Γ_nat / Γ_total)
```

where Γ_total = Γ_nat + 2π × γ_pressure (from 02_buffer_gas).

At α·L ≈ 0.22 (from 03_mems_geometry): transmission ≈ exp(-0.22) = 80%.
So 20% of light is absorbed. The CPT dip reduces absorption further at resonance.

### 2.3 Shot-Noise SNR

```
I_pd = R_pd × P_optical      (photodiode current)
        R_pd ≈ 0.5 A/W at 795nm (typical Si photodiode)

Shot noise: σ_shot = sqrt(2 × e × I_pd × BW)

SNR = I_pd / σ_shot = sqrt(I_pd / (2 × e × BW))
    = sqrt(R_pd × P_optical / (2 × e × BW))
```

For P = 50 µW, R_pd = 0.5 A/W, BW = 100 Hz:
```
I_pd = 25 µA
SNR = sqrt(25e-6 / (2 × 1.6e-19 × 100)) = sqrt(7.8×10⁸) = 28000
```

High SNR → shot-noise limited → good. This SNR feeds into ADEV formula in 08_allan.

---

## 3. Implementation

```python
import numpy as np

# Load from other modules
try:
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "03_mems_geometry"))
    from fem_results import RESULTS as GEO
    cavity_diameter_mm = GEO["cavity_diameter_mm"]
    cavity_depth_mm    = GEO["cavity_depth_mm"]
    glass_thickness_mm = GEO["glass_thickness_mm"]
except Exception:
    cavity_diameter_mm = 1.5
    cavity_depth_mm    = 1.0
    glass_thickness_mm = 0.3

try:
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "02_buffer_gas"))
    import sim as bg
    gamma_pressure_hz = bg.RESULTS.get("cpt_linewidth_at_popt_khz", 3.2) * 1e3
except Exception:
    gamma_pressure_hz = 3200.0

# Physical constants
lambda_m = 794.979e-9    # m
e_charge = 1.602e-19     # C
GAMMA_HZ = 5.746e6       # Hz natural linewidth

def vcsel_beam_at_detector(vcsel_divergence_deg=8.0, vcsel_w0_um=4.0,
                            input_power_uw=200.0):
    """ABCD propagation from VCSEL to photodetector."""
    lambda_ = lambda_m
    w0      = vcsel_w0_um * 1e-6
    z_R     = np.pi * w0**2 / lambda_

    # Propagation distances
    z_glass_bottom = glass_thickness_mm * 1e-3 / 1.47   # optical path in glass (n≈1.47)
    z_rb_cell      = cavity_depth_mm    * 1e-3           # free space in Rb cell
    z_glass_top    = glass_thickness_mm * 1e-3 / 1.47
    z_gap          = 0.5e-3                              # gap to photodetector

    z_total = z_glass_bottom + z_rb_cell + z_glass_top + z_gap

    # Beam size at detector
    w_out = w0 * np.sqrt(1 + (z_total / z_R)**2)

    # Check clipping
    no_clip = (2 * w_out * 1e3) < (cavity_diameter_mm * 0.9)   # beam < 90% of cavity

    return {
        "beam_diameter_at_detector_mm": 2 * w_out * 1e3,
        "no_clipping": no_clip,
        "rayleigh_range_mm": z_R * 1e3,
    }

def compute_optical_power_at_detector(input_power_uw, alpha_L):
    """Beer-Lambert transmission through the cell."""
    # Window reflections (4% per surface × 4 surfaces)
    window_loss = (1 - 0.04)**4
    # Beer-Lambert absorption
    transmission = np.exp(-alpha_L) * window_loss
    return input_power_uw * transmission

def compute_snr(power_uw, bandwidth_hz=100.0):
    """Shot-noise limited SNR."""
    R_pd   = 0.5         # A/W quantum efficiency
    I_pd   = R_pd * power_uw * 1e-6
    SNR    = np.sqrt(I_pd / (2 * e_charge * bandwidth_hz))
    return SNR, I_pd

# ── Run all computations ──────────────────────────────────────────────
alpha_L    = 0.22    # from 03_mems_geometry (or compute inline)
input_uw   = 200.0   # µW VCSEL output

beam  = vcsel_beam_at_detector()
P_det = compute_optical_power_at_detector(input_uw, alpha_L)
snr, I_pd = compute_snr(P_det)

RESULTS = {
    "beam_diameter_at_cell_exit_mm":  beam["beam_diameter_at_detector_mm"],
    "no_clipping":                    beam["no_clipping"],
    "optical_power_at_detector_uw":   P_det,
    "snr":                            snr,
    "photodiode_current_ua":          I_pd * 1e6,
    "window_transmission_pct":        (1-0.04)**4 * 100,
    "absorption_pct":                 (1 - np.exp(-alpha_L)) * 100,
}
```

---

## 4. Known Failure Modes

| Symptom | Cause | Fix |
|---|---|---|
| Beam clips cavity | VCSEL divergence too large | Add collimating microlens or increase cavity diameter |
| Power at detector < 5 µW | Cell too absorbing (α·L too high) | Reduce cavity depth in 03_mems_geometry |
| SNR < 50 | Too little input power | Increase VCSEL drive current — check max from datasheet |
