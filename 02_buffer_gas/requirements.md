# 02_buffer_gas — Requirements

**WAVE 2 | Tool: Python + SciPy | Depends on: 00_atomic_model + 03_mems_geometry**

---

## Questions This Simulation Must Answer

1. What N2 pressure minimizes total CPT linewidth for our specific cavity geometry?
2. What is the pressure shift of the clock frequency at the optimal N2 pressure?
3. How does the pressure shift vary with temperature? (temperature coefficient)
4. What Rb vapor density is achievable at 85°C operating temperature?
5. Is the Rb number density sufficient for good absorption at our cell depth?

---

## Inputs Required

| Parameter | Source | Value |
|---|---|---|
| Cavity depth | 03_mems_geometry/results.md | _____ mm |
| Cavity diameter | 03_mems_geometry/results.md | _____ mm |
| CPT linewidth at zero pressure | 00_atomic_model/results.md | _____ kHz |
| Operating temperature | Fixed | 85°C = 358 K |

---

## Physics to Model

### Transit-time broadening (pressure-independent)
```
γ_transit = v_thermal / d_cavity
v_thermal = sqrt(8 kB T / π m_Rb)    where m_Rb = 87 u
```

### Pressure broadening (linear in N2 pressure)
```
γ_pressure = k_broad × P_N2
k_broad = 10.8 kHz/Torr    (Rb-N2, from Vanier & Audoin)
```

### Pressure shift (linear in N2 pressure)
```
δ_shift = k_shift × P_N2
k_shift = -6.7 kHz/Torr    (Rb-N2, from Vanier & Audoin)
```

### Dicke narrowing (buffer gas suppresses transit broadening)
```
γ_Dicke = γ_transit²  /  (γ_transit + γ_pressure)
```
N2 buffer gas traps atoms in the cell → reduces transit-time broadening.
This is WHY buffer gas is used. Without it, atoms fly across the cell in ~1 µs
and the CPT linewidth would be ~1 MHz instead of ~1 kHz.

### Rb vapor density (Antoine equation)
```
log₁₀(P_Rb_Pa) = A - B/T
A = 9.863, B = 4529.6    (for T in K, liquid Rb range)
n_Rb = P_Rb / (kB × T)
```

### Optimal N2 pressure
Sweep P_N2 from 0 to 200 Torr. Find minimum of γ_total(P_N2).

---

## Output to Extract into results.md

```
Optimal N2 pressure          : _____ Torr  expected 30-75 Torr
CPT linewidth at P_opt       : _____ kHz   must be < 5 kHz
Pressure shift at P_opt      : _____ kHz   (will be compensated by tuning f_mod)
Temp coefficient of shift    : _____ kHz/°C
Rb vapor density at 85°C     : _____ m⁻³   expected ~2×10¹⁷ m⁻³
Transit time at P=0          : _____ µs
```
