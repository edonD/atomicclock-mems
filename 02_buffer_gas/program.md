# Module 02: Buffer Gas — Program

## 1. Mission

Find the exact N2 fill pressure that minimizes CPT linewidth for our specific
cavity geometry. This single number goes directly into the process traveler
as the Rb fill step specification. If this pressure is wrong by ±20 Torr,
the linewidth degrades and the clock misses its ADEV target.

**What "done" means:**

1. `sim.py` runs and populates RESULTS.
2. `python evaluator.py` exits 0.
3. Optimal N2 pressure in range 20–100 Torr.
4. CPT linewidth at optimal pressure < 5 kHz.
5. Rb vapor density at 85°C within 50% of Antoine equation prediction.

---

## 2. Physics

### 2.1 Why Buffer Gas Is Used

Without buffer gas, Rb atoms cross the ~1.5mm cell in time:
```
t_transit = d / v_thermal = 1.5e-3 / 270 ≈ 5.6 µs
```

This gives a transit-time CPT linewidth of:
```
γ_transit = 1 / (π × t_transit) ≈ 57 kHz
```

57 kHz linewidth → ADEV of ~5×10⁻⁹. Ten times worse than our target.

Buffer gas (N2 at 30–75 Torr) makes atoms undergo many collisions before
crossing the cell — Dicke narrowing. The effective transit time becomes
the diffusion time across the cell, which is much longer.

### 2.2 The Competing Effects

Buffer gas adds two effects that trade off:

**Dicke narrowing (good):** reduces transit-time linewidth:
```
γ_Dicke = γ_transit² / (γ_transit + γ_pressure)
```

**Pressure broadening (bad):** N2 collisions dephase the CPT coherence:
```
γ_pressure = k_broad × P_N2        k_broad = 10.8 kHz/Torr  (Rb-N2, Vanier & Audoin)
```

**Total CPT linewidth:**
```
γ_total(P) = γ_Dicke(P) + γ_ground + γ_laser_power_broadening

where γ_ground = γ₁₂ from 00_atomic_model (wall collisions, residual)
```

The optimal pressure P_opt minimizes γ_total(P).

### 2.3 Pressure Shift

N2 collisions also shift the clock frequency:
```
δ_shift(Hz) = k_shift × P_N2        k_shift = -6.7 kHz/Torr  (Rb-N2)
```

At P_opt = 50 Torr: δ_shift = -335 kHz. This is large but compensated by
tuning the modulation frequency f_mod away from HYPERFINE_HZ/2 by 335 kHz.
The servo loop locks to the actual resonance — the shift is absorbed
automatically. But we must know it precisely so the PLL covers the range.

### 2.4 Rb Vapor Density (Antoine Equation)

```
log₁₀(P_Rb_Pa) = 9.863 - 4529.6 / T      [T in Kelvin, valid 312–961 K liquid Rb]
```

At T = 358 K (85°C):
```
P_Rb = 10^(9.863 - 4529.6/358) = 10^(9.863 - 12.65) = 10^(-2.79) = 1.6×10⁻³ bar ≈ 1.6 mbar
P_Rb_Pa = 160 Pa
n_Rb = P_Rb / (kB × T) = 160 / (1.38e-23 × 358) = 3.2×10²² m⁻³
```

Wait — let me recheck. Steck's Rb-87 data (2021) gives vapor pressure at 85°C.
Use Steck coefficients for accuracy:
```
log₁₀(P_Torr) = 7.0464 - 4040 / T     [T in Kelvin, solid Rb, valid < 312 K]
log₁₀(P_Torr) = 7.5175 - 4132 / T     [T in Kelvin, liquid Rb, 312 K to 961 K]
```

At T = 358 K (liquid phase since T > 312 K):
```
log₁₀(P_Torr) = 7.5175 - 4132/358 = 7.5175 - 11.542 = -4.025
P_Torr = 10^(-4.025) = 9.4×10⁻⁵ Torr
P_Pa   = 9.4×10⁻⁵ × 133.3 = 0.0126 Pa
n_Rb   = 0.0126 / (1.38e-23 × 358) = 2.55×10¹⁸ m⁻³
```

This is approximately 2.5×10¹⁸ m⁻³ — lower than the coarser Antoine estimate.
Use the Steck coefficients for the simulation. Both implementations are provided
below; use the one that matches published data.

---

## 3. Implementation

```python
import numpy as np
from scipy.optimize import minimize_scalar

# Published collision parameters (Vanier & Audoin, Table 2)
K_BROAD_KHZ_TORR = 10.8    # pressure broadening coefficient
K_SHIFT_KHZ_TORR = -6.7    # pressure shift coefficient

# Constants
kB = 1.380649e-23
M_RB = 87 * 1.66053906660e-27  # kg


def rb_vapor_density(T_celsius):
    """Rb number density from Steck (2021) vapor pressure."""
    T_K = T_celsius + 273.15

    if T_K < 312.0:  # solid phase
        log10_P_Torr = 7.0464 - 4040.0 / T_K
    else:            # liquid phase
        log10_P_Torr = 7.5175 - 4132.0 / T_K

    P_Torr = 10 ** log10_P_Torr
    P_Pa   = P_Torr * 133.322  # 1 Torr = 133.322 Pa
    n_Rb   = P_Pa / (kB * T_K)
    return n_Rb


def thermal_velocity(T_celsius):
    """Mean thermal velocity of Rb atoms."""
    T_K = T_celsius + 273.15
    return np.sqrt(8 * kB * T_K / (np.pi * M_RB))


def transit_time_linewidth(cavity_diameter_mm, T_celsius=85.0):
    """Transit-time CPT linewidth (Hz) without buffer gas."""
    d = cavity_diameter_mm * 1e-3
    v = thermal_velocity(T_celsius)
    t_transit = d / v
    return 1.0 / (np.pi * t_transit)


def dicke_narrowing(gamma_transit_hz, gamma_pressure_hz):
    """
    Dicke narrowing: effective linewidth with buffer gas.
    When gamma_pressure >> gamma_transit, Dicke limit reached.
    """
    return gamma_transit_hz**2 / (gamma_transit_hz + gamma_pressure_hz)


def total_cpt_linewidth(P_N2_Torr, cavity_diameter_mm,
                         gamma_12_hz=300.0, T_celsius=85.0):
    """
    Total CPT linewidth at a given N2 pressure.

    Args:
        P_N2_Torr:          N2 buffer gas pressure
        cavity_diameter_mm: from 03_mems_geometry/results.md
        gamma_12_hz:        residual ground decoherence (wall collisions, etc.)
        T_celsius:          cell operating temperature

    Returns:
        total_linewidth_hz, components dict
    """
    gamma_transit  = transit_time_linewidth(cavity_diameter_mm, T_celsius)
    gamma_pressure = K_BROAD_KHZ_TORR * P_N2_Torr * 1e3  # convert kHz to Hz
    gamma_Dicke    = dicke_narrowing(gamma_transit, gamma_pressure)

    total = gamma_Dicke + gamma_12_hz + gamma_pressure

    return total, {
        "gamma_transit_hz":  gamma_transit,
        "gamma_pressure_hz": gamma_pressure,
        "gamma_Dicke_hz":    gamma_Dicke,
        "gamma_12_hz":       gamma_12_hz,
        "total_hz":          total,
    }


def find_optimal_pressure(cavity_diameter_mm, gamma_12_hz=300.0):
    """Find N2 pressure that minimizes total CPT linewidth."""
    def objective(P):
        lw, _ = total_cpt_linewidth(P, cavity_diameter_mm, gamma_12_hz)
        return lw

    result = minimize_scalar(objective, bounds=(1.0, 200.0), method='bounded')
    return result.x, result.fun


def pressure_shift(P_N2_Torr):
    """Clock frequency shift due to N2 buffer gas (Hz)."""
    return K_SHIFT_KHZ_TORR * P_N2_Torr * 1e3  # kHz → Hz


def temperature_coefficient(P_N2_Torr, dT=1.0):
    """Temperature coefficient of pressure shift (Hz/°C)."""
    shift_T1 = pressure_shift(P_N2_Torr)
    # At T+dT, N2 pressure changes slightly due to ideal gas law
    # P(T+dT) ≈ P(T) × (T+dT)/T
    T_K = 85.0 + 273.15
    P_at_T_plus_dT = P_N2_Torr * (T_K + dT) / T_K
    shift_T2 = pressure_shift(P_at_T_plus_dT)
    return (shift_T2 - shift_T1) / dT


# ── MAIN ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Load cavity diameter from 03_mems_geometry results
    # (or use default for now)
    try:
        import sys, os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "03_mems_geometry"))
        from fem_results import RESULTS as GEO
        cavity_diameter_mm = GEO["cavity_diameter_mm"]
        cavity_depth_mm    = GEO["cavity_depth_mm"]
    except Exception:
        cavity_diameter_mm = 1.5   # default from literature
        cavity_depth_mm    = 1.0

    P_opt, lw_opt = find_optimal_pressure(cavity_diameter_mm)
    n_Rb          = rb_vapor_density(85.0)
    shift_at_Popt = pressure_shift(P_opt)
    tc            = temperature_coefficient(P_opt)

    RESULTS = {
        "optimal_n2_pressure_torr":          P_opt,
        "cpt_linewidth_at_popt_khz":         lw_opt / 1e3,
        "rb_density_m3":                     n_Rb,
        "pressure_shift_khz":                shift_at_Popt / 1e3,
        "temp_coefficient_hz_per_degc":      tc,
        "broadening_coefficient_khz_torr":   K_BROAD_KHZ_TORR,
        "shift_coefficient_khz_torr":        K_SHIFT_KHZ_TORR,
    }
```

---

## 4. Known Failure Modes

| Symptom | Cause | Fix |
|---|---|---|
| P_opt > 150 Torr | Cavity too large → transit-time too low to benefit from Dicke | Check cavity_diameter_mm input |
| P_opt < 5 Torr | gamma_12 too high — pressure broadening kicks in before Dicke | Normal for wall-collision-dominated cells — this is valid |
| Linewidth at P_opt > 10 kHz | Wrong broadening coefficient — check units (kHz/Torr not Hz/Torr) | Multiply K_BROAD by 1e3 |
| Rb density off by 100× | Using Antoine equation instead of Steck — different coefficient set | Use Steck 2021 log₁₀ coefficients |
