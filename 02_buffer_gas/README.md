# 02_buffer_gas — N₂ Buffer Gas Optimization

> **Status: FAIL (formula bug)** — optimal pressure hits lower bound (1.0 Torr); evaluator expects 20–100 Torr.
> Root cause documented below. Fix required in `sim.py` Dicke-narrowing model.

---

## 1. What This Module Does

This module finds the single most important number in the process traveler: the N₂ fill pressure for the Rb vapor cell.
Buffer gas pressure controls the balance between **Dicke narrowing** (good — slows atoms down, narrows CPT linewidth) and **pressure broadening** (bad — N₂ collisions dephase the CPT coherence).
Get this number wrong by ±20 Torr and the clock misses its ADEV target before a single die is tested.
The output, `optimal_n2_pressure_torr`, goes directly into the wafer-bonding fill recipe.

---

## 2. Physics — Competing Effects of Buffer Gas

Without N₂, Rb atoms cross a 1.5 mm cell in ~5 µs → transit-time CPT linewidth ≈ **63 kHz**. At that linewidth, Allan deviation would be ~5×10⁻⁹ — ten times worse than the SA65 target.

Buffer gas adds two opposing effects:

| Effect | Direction | Formula |
|---|---|---|
| **Dicke narrowing** — diffusion-limited transit | Narrows ∝ 1/P | γ_diff(P) = 63 375 / P  Hz |
| **Pressure broadening** — N₂ dephases CPT coherence | Broadens ∝ P | γ_pressure = 10.8 · P  Hz |

The total CPT linewidth has a **clear minimum** where these balance — at approximately 75 Torr for a 1.5 mm cell.

![Dicke narrowing vs pressure broadening competition](plots/dicke_narrowing_physics.png)

The plot shows:
- **Blue dashed** — free-flight transit linewidth (63 kHz, no buffer gas)
- **Red** — Dicke-narrowed diffusion linewidth γ_diff ∝ 1/P (decreasing)
- **Green** — pressure broadening γ_pressure ∝ P (increasing)
- **Black bold** — total CPT linewidth (clear minimum near 75 Torr, ≈ 2 kHz)
- **Shaded bands** — Dicke-dominated (left) vs pressure-dominated (right) regimes

The optimal pressure for a **1.5 mm cell** is ~**75 Torr**, consistent with Knappe et al. (NIST, 2004) who used 75 Torr N₂ and achieved 4 kHz CPT linewidth.

---

## 3. Rb Vapor Density vs Temperature

The cell must be heated to 85 °C to produce sufficient Rb vapor for optical absorption.

![Rb vapor pressure and number density vs temperature](plots/rb_vapor_pressure.png)

Key values using **Steck (2021)** coefficients for liquid Rb (T > 39 °C):

```
log₁₀(P_Torr) = 7.5175 − 4132 / T_K
```

| Temperature | Vapor Pressure | Number Density |
|---|---|---|
| 25 °C (room) | ~5×10⁻⁷ Torr | ~1.6×10¹⁶ m⁻³ |
| 60 °C | ~2×10⁻⁵ Torr | ~5×10¹⁷ m⁻³ |
| **85 °C (operating)** | **~9.4×10⁻⁵ Torr** | **~2.55×10¹⁸ m⁻³** |
| 100 °C | ~3×10⁻⁴ Torr | ~7×10¹⁸ m⁻³ |

Too cold → insufficient absorption → no CPT signal. Too hot → cell opaque → self-absorption. 85 °C is the published optimum for MEMS CSAC cells.

---

## 4. Pressure Shift of the Clock Frequency

N₂ collisions shift the Rb hyperfine frequency by `δf = −6.7 kHz/Torr × P`.
At P_opt = 75 Torr: **δf ≈ −503 kHz** — large but fully compensated by tuning f_mod.

![Clock frequency pressure shift](plots/pressure_shift.png)

The temperature sensitivity via ideal gas law (ΔP/P = ΔT/T) gives ~1.77 Hz/°C at 75 Torr — sets the thermal stability requirement for module 04.

---

## 5. Linewidth Budget at Optimal Pressure

At P_opt ≈ 75 Torr, the CPT linewidth breaks down as:

![Linewidth contribution budget](plots/linewidth_budget_pie.png)

| Contribution | Value | Source |
|---|---|---|
| Dicke-narrowed diffusion | ~845 Hz | γ_diff = 63 375 / 75 |
| Pressure broadening | ~810 Hz | 10.8 Hz/Torr × 75 |
| Wall-collision residual | ~300 Hz | γ₁₂ baseline |
| **Total** | **~2.0 kHz** | within 5 kHz target |

---

## 6. Current Evaluator Results — FAIL

```
======================================================================
  EVALUATOR: 02_buffer_gas
======================================================================
    PASS  broadening_coeff: 10.80 kHz/Torr  ✓
    PASS  rb_density_m3: 2.58e+18 m⁻³  ✓
    PASS  pressure_shift_khz: -6.7 kHz  ✓
    FAIL  optimal_n2_pressure_torr: 1.0 Torr  (expected 20–100 Torr)
    FAIL  cpt_linewidth_at_popt: 64.54 kHz  (expected < 5 kHz)
======================================================================
  VERDICT:  FAIL
```

### Root Cause

`sim.py` uses `gamma_Dicke = gamma_transit² / (gamma_transit + gamma_pressure)`. Setting d(total)/dP = 0 analytically gives **P = 0 as the only critical point** — the function is monotonically increasing for P > 0. The optimizer hits the lower bound.

### Fix

Replace with the diffusion-coefficient model where γ_diff ∝ 1/P:

```python
D0_m2_per_s = 1.9e-5   # Rb-in-N2 diffusion coeff at 760 Torr
P0_torr     = 760.0

def dicke_narrowed_linewidth(P_N2_Torr, cavity_diameter_mm):
    d = cavity_diameter_mm * 1e-3
    D = D0_m2_per_s * P0_torr / P_N2_Torr  # D ∝ 1/P
    return (np.pi**2 * D) / d**2            # Hz, decreases with P

# P_opt = sqrt(63375 / 10.8) ≈ 76.6 Torr  ✓
```

---

## 7. Key Outputs → Downstream

| Output | Expected value | Feeds into |
|---|---|---|
| `optimal_n2_pressure_torr` | ~75 Torr | Process traveler — cell fill recipe |
| `cpt_linewidth_at_popt_khz` | ~2.0 kHz | `08_allan` — ADEV estimate |
| `pressure_shift_khz` | ~−503 kHz | `06_rf_synthesis` — PLL tuning range |
| `temp_coefficient_hz_per_degc` | ~1.77 Hz/°C | `04_thermal` — temperature stability spec |
| `rb_density_m3` | ~2.55×10¹⁸ m⁻³ | `05_optical` — optical depth |
