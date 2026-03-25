# Module 04: Thermal Management — Program

## 1. Mission

Design the Pt heater and RTD geometry that holds the cell at 85°C ± 0.01°C
across ambient temperatures -40°C to +40°C, with total heater power < 100 mW
and thermal gradient < 1°C/mm across the cell.

The output is: Pt heater trace geometry (width, length, serpentine pitch)
that goes into the GDS-II mask, plus PID gain values for the firmware.

**What "done" means:**

1. Elmer FEM steady-state: temperature at cell center = 85°C at ambient -40°C.
2. Thermal gradient across cell < 1°C/mm.
3. Heater power < 100 mW.
4. Python PID model shows ±0.01°C stability with realistic RTD noise.
5. `python evaluator.py` exits 0.

---

## 2. Physics

### 2.1 Heat Balance

```
P_heater = P_loss_conduction + P_loss_convection + P_loss_radiation

P_loss_conduction = keff × A × ΔT / L     (through substrate to PCB)
P_loss_convection = h × A_surface × ΔT   (to surrounding air)
P_loss_radiation  = ε × σ × A × (T_hot⁴ - T_amb⁴)
```

At 85°C with ΔT = 125°C (ambient -40°C):
- Convection dominates for small cells in ambient air
- h ≈ 10 W/m²K (natural convection, small geometry)
- Cell surface area ≈ 6 × (2mm)² = 24 mm² = 24×10⁻⁶ m²
- P_convection ≈ 10 × 24e-6 × 125 = 30 mW

This rough estimate tells us 30–80 mW is needed. FEM gives the exact value
with actual geometry and boundary conditions.

### 2.2 Pt RTD Physics

Platinum resistance temperature detector (RTD) uses:
```
R(T) = R₀ × (1 + A × T + B × T²)
```

Callendar-Van Dusen coefficients for Pt:
- A = 3.9083 × 10⁻³ °C⁻¹
- B = -5.775 × 10⁻⁷ °C⁻²

Simplified for our range (0–100°C):
```
R(T) ≈ R₀ × (1 + 3850×10⁻⁶ × (T - 0))    [TCR = 3850 ppm/°C]
```

For R₀ = 100 Ω (Pt100 standard):
```
R(85°C) = 100 × (1 + 3850e-6 × 85) = 100 × 1.3273 = 132.73 Ω
dR/dT = 100 × 3850e-6 = 0.385 Ω/°C
```

To detect ΔT = 0.01°C: ΔR = 0.00385 Ω. Requires 4-wire measurement.

### 2.3 PID Thermal Control Model

Plant transfer function (cell temperature vs heater power):
```
G(s) = K / (τs + 1)

where:
  K = steady-state gain (°C/W) = 1/h_eff
  τ = thermal time constant = m × Cp / h_eff × A
```

Approximate for 2×2×2mm cell:
- Mass m ≈ ρ × V = 2330 × (2e-3)³ = 18.6 µg → tiny
- Thermal time constant τ ≈ 1–20 seconds (depends on packaging)

PID controller:
```
C(s) = Kp × (1 + 1/(Ti×s) + Td×s)
```

Ziegler-Nichols starting point, then tune for ±0.01°C.

---

## 3. Implementation

### 3.1 Elmer FEM Thermal (sim_thermal.sif)

```
Solver 1
  Equation = Heat Equation
  Procedure = "HeatSolve" "HeatSolver"
  Variable = Temperature
  Steady State Convergence Tolerance = 1.0e-6
End

! Heat source on Pt heater body
Body Force 1
  Name = "HeaterPower"
  Heat Source = 5.0e7   ! W/m³ — adjust to match target temperature
                         ! For 50mW in 1µm × 50µm × 10mm trace:
                         ! V = 1e-6 × 50e-6 × 10e-3 = 5e-13 m³
                         ! Q = P/V = 50e-3 / 5e-13 = 1e11 W/m³
End

Boundary Condition 1
  Name = "AmbientConvection"
  Heat Transfer Coefficient = 10.0   ! W/m²K — natural convection
  External Temperature = -40.0       ! °C worst case ambient
End
```

### 3.2 Heater Trace Design

Pt heater as serpentine trace:
```
R_heater = ρ_Pt × L_trace / (w × h)

where:
  ρ_Pt = 1/9.43e6 Ω·m = 1.06×10⁻⁷ Ω·m  (electrical resistivity)
  h    = 200 nm = 200e-9 m  (sputtered thickness)
  w    = trace width (design variable)
  L    = trace length (design variable)
```

For R = 100 Ω, w = 50 µm:
```
L = R × w × h / ρ_Pt = 100 × 50e-6 × 200e-9 / 1.06e-7 = 9.4 mm
```

This fits as a serpentine in a 2×2 mm die. Use 5 passes of 1.5mm length each.

### 3.3 Python PID Simulation

```python
import numpy as np
from scipy.signal import lti, step

def simulate_pid_thermal(K_plant, tau_plant, Kp, Ki, Kd,
                          T_setpoint=85.0, T_start=-40.0, t_end=120.0):
    """
    Simulate PID temperature control.
    Returns: time array, temperature array, power array
    """
    dt = 0.1  # seconds
    t  = np.arange(0, t_end, dt)
    T  = np.zeros_like(t)
    P  = np.zeros_like(t)
    T[0] = T_start

    integral   = 0.0
    prev_error = 0.0

    for i in range(1, len(t)):
        error     = T_setpoint - T[i-1]
        integral += error * dt
        derivative = (error - prev_error) / dt

        # PID output = heater power (W)
        P[i] = Kp * error + Ki * integral + Kd * derivative
        P[i] = max(0.0, min(P[i], 0.150))  # clamp 0–150 mW

        # Plant: first-order thermal model
        dT = (K_plant * P[i] - (T[i-1] - T_start)) / tau_plant
        T[i] = T[i-1] + dT * dt

        prev_error = error

    return t, T, P

# Extract temperature stability at steady state
def temp_stability(T_array, t_settle=60.0, dt=0.1):
    i_start = int(t_settle / dt)
    T_ss    = T_array[i_start:]
    return np.max(T_ss) - np.min(T_ss)


RESULTS = {
    "heater_power_mw":                None,   # from FEM
    "temp_stability_degc":            None,   # from PID sim
    "thermal_gradient_degc_per_mm":   None,   # from FEM
    "startup_time_s":                 None,   # time to reach 85°C-0.1°C
    "heater_resistance_ohm":          None,   # from trace design
    "rtd_resistance_at_85c_ohm":      None,   # from Callendar-Van Dusen
    "rtd_sensitivity_ohm_per_degc":   None,
    "pid_kp":                         None,
    "pid_ki":                         None,
    "pid_kd":                         None,
}
```

---

## 4. Known Failure Modes

| Symptom | Cause | Fix |
|---|---|---|
| Gradient > 2°C/mm | Heater not symmetric around cavity | Wrap heater as ring around cavity, not linear trace |
| Power > 150 mW | Convection coefficient too high (forced air?) | Check h value — natural convection h≈5–15 W/m²K |
| PID oscillates | Kp too high, tau underestimated | Reduce Kp by 2×, measure tau from step response |
| Startup > 5 min | tau too large — cell not thermally isolated | Add Si undercut trenches for thermal isolation |
