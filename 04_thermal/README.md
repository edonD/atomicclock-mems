# 04_thermal — MEMS Atomic Clock Thermal Oven

> **Status: PASS** — all Wave 2 thermal management criteria satisfied.
> `python evaluator.py` exits 0.

---

## 1. What This Module Does

This module designs the thermal oven that holds the Rb-87 vapor cell at a
stable 85°C across the full military operating range of −40°C to +40°C ambient
(the cell must be heated to 85°C even at the worst-case −40°C cold soak).

Three subsystems are co-designed here:

1. **Pt serpentine heater** — sputtered 200 nm Pt trace on the Si die, etched
   into a compact serpentine geometry.  Resistance 100 Ω; drives ~74 mW steady
   state at worst-case ambient.

2. **Pt100 RTD sensor** — a second Pt trace alongside the heater, read by
   4-wire measurement, provides the temperature feedback signal.  The Callendar-
   Van Dusen model gives 0.381 Ω/°C sensitivity; Johnson noise sets the
   temperature resolution floor at ~13 µ°C rms (10 Hz bandwidth), far below
   the 10 m°C stability requirement.

3. **PID thermal controller** — a first-order plant model (K_plant, τ_plant)
   combined with a discrete-time PID loop, tuned to bring the cell from −40°C
   to within ±0.1°C of setpoint in under 2 minutes, then hold within
   ±21 µ°C (peak-to-peak 42 µ°C) in steady state.

The outputs — heater trace geometry, RTD geometry, and PID gain values (Kp,
Ki, Kd) — go directly into the GDS-II mask and the firmware parameter file.

---

## 2. Analytical Heat Balance

### Governing Equation

At steady state, heater power equals total heat lost to the environment:

```
P_heater = Q_conv + Q_cond + Q_rad
```

Worst-case condition: T_cell = 85°C, T_ambient = −40°C, ΔT = 125°C.

Cell geometry (from module 03_mems_geometry):

```
Cell stack: 3.0 mm × 3.0 mm × 1.6 mm  (Si die + two anodic-bond glass lids)
Surface area:
  Top + bottom:  2 × (3.0×10⁻³)² = 18.0×10⁻⁶ m²
  Four sides:    4 × (3.0×10⁻³) × (1.6×10⁻³) = 19.2×10⁻⁶ m²
  Total:  A_surface = 37.2×10⁻⁶ m²
```

### Natural Convection

```
Q_conv = h_conv × A_surface × ΔT

h_conv = 8 W/m²K  (conservative upper bound for natural convection
                    on a 3 mm cube; published range 5–15 W/m²K)

Q_conv = 8 × 37.2×10⁻⁶ × 125 = 37.20 mW
```

### Conduction (Package Leads to PCB)

Chip-scale MEMS packages lose heat through solder bumps and bond-wire leads
into the PCB.  Published CSAC thermal budgets (Knappe 2005, Lutwak 2004)
estimate this path at ~10 mW for a chip-scale hermetic package:

```
Q_cond ≈ 10 mW
```

### Radiation (Stefan-Boltzmann)

```
Q_rad = ε × σ_SB × A_surface × (T_cell_K⁴ − T_amb_K⁴)

ε      = 0.7   (oxidised/passivated Si surface)
σ_SB   = 5.67×10⁻⁸ W/m²K⁴
T_cell = 358.15 K
T_amb  = 233.15 K

Q_rad = 0.7 × 5.67×10⁻⁸ × 37.2×10⁻⁶ × (358.15⁴ − 233.15⁴)
      = 0.7 × 5.67×10⁻⁸ × 37.2×10⁻⁶ × (1.645×10¹⁰ − 2.952×10⁹)
      = 19.93 mW
```

### Total Heater Power with Design Margin

```
Q_total = 37.20 + 10.00 + 19.93 = 67.13 mW

P_heater = Q_total × 1.10  (10% design margin)
         = 73.84 mW
```

The heater power budget is summarised in the table below:

| Loss path | Power |
|---|---|
| Natural convection | 37.20 mW |
| Conduction (leads/bumps) | 10.00 mW |
| Radiation | 19.93 mW |
| Subtotal | 67.13 mW |
| **Design margin (+10%)** | **→ 73.84 mW total** |

The 73.84 mW result is **26% below the 100 mW budget limit** derived from the
SA65 120 mW total system budget (electronics consume ~46 mW).

---

## 3. Pt Heater Trace Design

### Resistivity of Sputtered Pt Film

A 200 nm sputtered Pt film exhibits ~1.5× bulk resistivity due to grain
boundary scattering (Namba, J. Appl. Phys. 41, 1970):

```
ρ_bulk = 1.06×10⁻⁷ Ω·m  (bulk Pt at 20°C)
ρ_film = 1.59×10⁻⁷ Ω·m  (200 nm sputtered film)
```

### Trace Geometry for R = 100 Ω

Target resistance 100 Ω allows a standard drive/sense circuit.  With a 50 µm
trace width:

```
R = ρ_film × L / (w × h)

→ L = R × w × h / ρ_film
    = 100 × 50×10⁻⁶ × 200×10⁻⁹ / 1.59×10⁻⁷
    = 6.29 mm
```

The 6.29 mm trace is routed as a serpentine in the 2.5×2.5 mm heater zone
surrounding the cavity.  With a 100 µm pitch (50 µm trace + 50 µm gap) there
are 25 available passes of 2.5 mm length each (62.5 mm total available), giving
56 mm of headroom over the required 6.29 mm — the serpentine occupies only a
small fraction of the available area.

| Heater parameter | Value |
|---|---|
| Film thickness | 200 nm (sputtered) |
| Trace width | 50 µm |
| Trace length | 6.29 mm |
| Resistance at 20°C | 100 Ω |
| Film resistivity | 1.59×10⁻⁷ Ω·m |
| Serpentine zone | 2.5×2.5 mm |

---

## 4. Pt100 RTD Model — Callendar-Van Dusen Equation

The RTD uses the identical Pt film and process as the heater trace.  Its
resistance is modelled by the IEC 60751 Callendar-Van Dusen equation:

```
R(T) = R₀ × (1 + A·T + B·T²)

IEC 60751 coefficients:
  A = 3.9083×10⁻³ °C⁻¹
  B = −5.775×10⁻⁷ °C⁻²
  R₀ = 100 Ω  (Pt100 standard)
```

At the 85°C operating point:

```
R(85°C) = 100 × (1 + 3.9083×10⁻³ × 85 + (−5.775×10⁻⁷) × 7225)
         = 100 × (1 + 0.33221 − 0.00417)
         = 132.80 Ω

dR/dT (85°C) = R₀ × (A + 2B × T)
              = 100 × (3.9083×10⁻³ + 2 × (−5.775×10⁻⁷) × 85)
              = 0.3810 Ω/°C
```

### Temperature Resolution

With a 1 mA 4-wire sense current and 10 Hz measurement bandwidth, the Johnson
noise sets the temperature resolution floor:

```
V_noise_rms = sqrt(4 × k_B × T × R × BW)
            = sqrt(4 × 1.381×10⁻²³ × 358.15 × 132.80 × 10)
            = 5.13 nV rms

dT_noise = V_noise / (I_sense × dR/dT)
         = 5.13×10⁻⁹ / (1×10⁻³ × 0.381)
         ≈ 13.5 µ°C rms
```

The 13.5 µ°C resolution is **740× below the 10 m°C stability specification**,
confirming that the RTD physics is not the limiting factor.  Actual stability
is determined by the PID loop dynamics and the thermal time constant.

---

## 5. PID Thermal Control

### Plant Model

The cell temperature responds to heater power as a first-order thermal lag:

```
G(s) = K_plant / (τ_plant · s + 1)

K_plant   = ΔT / P_heater = 125°C / 0.07384 W = 1693 °C/W
τ_plant   = 20 s  (validated against published CSAC startup: 1–5 min range)
```

The 20 s time constant reflects the heater being thermally intimate with the Si
die; the dominant heat path is conduction through Si, not through air.

### PID Gains

Ziegler-Nichols tuning was used as a starting point, then refined iteratively:

| Gain | Value | Units | Physical interpretation |
|---|---|---|---|
| Kp | 3 mW/°C | W/°C | Proportional drive — 3 mW per °C of error |
| Ki | 0.3 mW/(°C·s) | W/(°C·s) | Integrator — eliminates steady-state offset |
| Kd | 5 mW·s/°C | W·s/°C | Derivative — damps overshoot at setpoint entry |

Effective open-loop gain at setpoint: Kp × K_plant = 3×10⁻³ × 1693 = 5.1 (dimensionless).

Heater output is clamped to [0, 150 mW].

### Startup Simulation

Starting from T = −40°C (worst-case cold soak), the PID drives full heater
power (150 mW — above steady-state to heat quickly) until the temperature
approaches setpoint, where the derivative term damps the approach to prevent
overshoot.

![Thermal Startup](plots/thermal_startup.png)

The upper panel shows the cell temperature rising from −40°C to 85°C.  The
lower panel shows heater power: initially at the 150 mW clamp, transitioning
to steady-state (~74 mW) once the setpoint is reached.  The dashed line marks
the startup time of **78.5 s** — the first moment the temperature enters the
±0.1°C band and remains there for 5 s or more.  This satisfies the 120 s
startup requirement with 35% margin.

### Steady-State Stability

Once settled, the PID holds temperature against the RTD noise floor:

![Thermal Stability](plots/thermal_stability.png)

The plot shows the temperature deviation from 85°C over a 60 s steady-state
window (extracted from t = 500–560 s of a 600 s simulation).  The peak-to-peak
deviation is **42 µ°C** (0.042 m°C), well inside the ±10 m°C (±0.01°C)
specification window shown by the orange dashed lines.

---

## 6. Thermal Gradient

A symmetric serpentine heater centred over the cavity produces a nearly uniform
temperature distribution across the die.  The worst-case gradient (centre to
edge, 1-D conduction approximation) is:

```
ΔT_die = P_heater × d / (2 × k_Si × A_cross)

where:
  k_Si   = 148 W/mK  (Si thermal conductivity at 85°C)
  d      = 1.5 mm    (half-width of 3 mm die)
  A_cross = 3.0×10⁻³ × 1.6×10⁻³ = 4.8×10⁻⁶ m²

ΔT_die = 0.07384 × 1.5×10⁻³ / (2 × 148 × 4.8×10⁻⁶)
       = 1.108×10⁻⁴ / 1.421×10⁻³
       = 0.078°C  across 1.5 mm

Gradient = 0.078°C / 1.5 mm = 0.052°C/mm
```

The **0.052°C/mm gradient is 19× below the 1°C/mm Rb thermophoresis threshold**.
Rb migration and condensation onto the cell windows is not a risk with this
heater geometry.

---

## 7. Key Results

| Parameter | Value | Limit | Margin | Status |
|---|---|---|---|---|
| Heater power (−40°C ambient) | **73.84 mW** | < 100 mW | 26% | PASS |
| Steady-state stability (pp) | **42 µ°C** | < 10,000 µ°C (0.01°C) | 238× | PASS |
| Thermal gradient | **0.052°C/mm** | < 1.0°C/mm | 19× | PASS |
| Startup time | **78.5 s** | < 120 s | 35% | PASS |
| RTD resistance at 85°C | **132.80 Ω** | — | — | — |
| RTD sensitivity | **0.381 Ω/°C** | > 0.1 Ω/°C | 3.8× | PASS |
| RTD temperature resolution | **~13 µ°C rms** | < 10,000 µ°C | 740× | — |
| Heater resistance | **100.0 Ω** | — | — | — |
| Heater trace length | **6.29 mm** | — | — | — |

---

## 8. Evaluator Checks

`python evaluator.py` loads `fem_results.py` via `importlib` and grades five
criteria against the SA65 power budget and the CPT frequency stability
requirement.

| # | Key | Criterion | Source | Critical |
|---|---|---|---|---|
| 1 | `heater_power_mw` | ≤ 100 mW | SA65 total budget 120 mW | Yes |
| 2 | `temp_stability_degc` | ≤ 0.01°C | CPT frequency-temperature coefficient | Yes |
| 3 | `thermal_gradient_degc_per_mm` | ≤ 1.0°C/mm | Rb thermophoresis limit | Yes |
| 4 | `startup_time_s` | ≤ 120 s | Defence application startup requirement | No |
| 5 | `rtd_sensitivity_ohm_per_degc` | ≥ 0.1 Ω/°C | Pt TCR detectability | No |

Expected evaluator output:

```
======================================================================
  EVALUATOR: 04_thermal
  Wave 2 — Thermal Management
======================================================================
    PASS  heater_power_mw: 73.8  (max 100, 26% margin)  ✓
    PASS  temp_stability_degc: 4.2e-05  (max 0.01, 100% margin)  ✓
    PASS  thermal_gradient_degc_per_mm: 0.052  (max 1.0, 95% margin)  ✓
    PASS  startup_time_s: 78.5  (max 120, 35% margin)  ✓
======================================================================
  VERDICT:  PASS
  OUTPUTS:  heater_power, RTD specs → process_traveler, mask_layout
======================================================================
```

---

## 9. Downstream Impact

The primary output that propagates to other modules is `temp_stability_degc`:

| Downstream module | What it consumes | Physical link |
|---|---|---|
| `08_allan` | `temp_stability_degc` → thermal frequency noise floor | N₂ pressure-shift temperature coefficient ~1 kHz/°C; 42 µ°C stability → 42 mHz clock noise |
| `mask_layout` | Heater trace geometry (width, length, pitch) → GDS-II layer | Physical deposition mask |
| `process_traveler` | Film thickness 200 nm, annealing conditions | Pt sputter recipe |
| `02_buffer_gas` | Heater power budget → confirms N₂ pressure choice is consistent with 85°C cell temperature | Consistency check |

The temperature stability result of 42 µ°C is the critical number for
Allan deviation modelling.  Via the N₂ pressure-shift coefficient of ~1 kHz/°C,
this translates to a thermal frequency noise contribution of ~42 mHz
(fractional: ~6×10⁻¹² at the 6.8347 GHz clock frequency), which is a
subdominant noise term relative to shot noise and photon-number fluctuations.

---

## 10. Files

| File | Description |
|---|---|
| `fem_results.py` | Analytical thermal model: heat balance, Pt trace, PID simulation, plot generation |
| `evaluator.py` | Grades RESULTS against Wave 2 thermal benchmarks |
| `program.md` | Full physics derivation, Elmer FEM thermal setup guide, known failure modes |
| `plots/thermal_startup.png` | PID startup simulation: temperature and power vs time |
| `plots/thermal_stability.png` | Steady-state temperature deviation (60 s window) |

---

*References: IEC 60751 (Pt100 Callendar-Van Dusen coefficients);
Knappe et al., Appl. Phys. Lett. 85, 1460 (2004) — CSAC thermal budget;
Lutwak et al., PTTI (2004) — SA65 power envelope;
Namba, Jpn. J. Appl. Phys. 9, 1070 (1970) — thin-film Pt resistivity;
MIL-STD-810G Method 501.5 / 502.5 (temperature operating range).*
