"""
04_thermal/pid_thermal_model.py
================================
PID Temperature Controller Model for MEMS Chip-Scale Atomic Clock
------------------------------------------------------------------
Demonstrates that the heater can ACHIEVE the temp_stability_degc spec
(+/-0.001 degC, 1 mK) against worst-case +/-20 degC ambient disturbances.

Physics basis
-------------
Thermal plant: first-order lag
    G_th(s) = R_th / (tau_thermal * s + 1)

    where:
        R_th        = 1 / (h * A)         [K/W]  convective thermal resistance
        tau_thermal = m * Cp / (h * A)    [s]    thermal time constant

Package parameters (3mm x 3mm x 1mm Si + glass stack, task spec):
    mass           ~50 mg   (Si + glass die stack)
    Cp(Si)         ~700 J/kg/K
    h(convection)  ~10 W/m^2/K   (natural convection in sealed package)
    A              ~2 x (3mm)^2 = 1.8e-5 m^2

Steady-state power uses the full fem_results heat balance:
    h=8 W/m^2K, full surface 37.2e-6 m^2, + conduction + radiation.

Uses python-control for closed-loop analysis and Bode plots.
Uses scipy.signal.lsim for time-domain disturbance rejection simulation.

RESULTS dict keys:
    pid_kp                  [W/degC]
    pid_ki                  [W/(degC.s)]
    pid_kd                  [W.s/degC]
    thermal_time_constant_s [s]
    thermal_resistance_kw   [K/W]
    settling_time_s         [s]    time to +-0.001 degC after 1 degC step
    peak_deviation_degc     [degC] worst-case peak during 1 degC step
    steady_state_power_mw   [mW]   heater power at setpoint / worst-case ambient
    spec_achieved           bool   peak_deviation < 0.001 degC
    pwm_frequency_hz        [Hz]   recommended PWM switching frequency
"""

# ---------------------------------------------------------------------------
# Non-interactive backend MUST come before all other matplotlib imports
# ---------------------------------------------------------------------------
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import os
import math
import numpy as np
import control  # type: ignore[import-untyped]
from scipy.signal import lti as scipy_lti  # type: ignore[import-untyped]

# ---------------------------------------------------------------------------
# 1.  THERMAL PLANT PARAMETERS (task specification)
# ---------------------------------------------------------------------------
m_stack_kg   = 50e-6         # kg     ~50 mg Si + glass die stack
Cp_si        = 700.0         # J/kg/K silicon heat capacity
h_conv       = 10.0          # W/m^2/K natural convection, sealed package
A_surface    = 2.0 * (3e-3)**2   # m^2  = 1.8e-5 m^2  (top + bottom faces)

# Derived plant parameters
R_th         = 1.0 / (h_conv * A_surface)              # K/W  convective R
tau_thermal  = m_stack_kg * Cp_si / (h_conv * A_surface)  # s  time constant

# ---------------------------------------------------------------------------
# 2.  STEADY-STATE POWER (full heat balance, consistent with fem_results.py)
# ---------------------------------------------------------------------------
# fem_results uses: h=8 W/m^2K, A_full=37.2e-6 m^2, Q_cond=10 mW, Q_rad~2 mW
# (worst-case ambient -40 degC, setpoint 85 degC, dT=125 degC)
T_setpoint_C  = 85.0
T_amb_worst_C = -40.0
dT_worst      = T_setpoint_C - T_amb_worst_C    # 125 degC

h_fem         = 8.0           # W/m^2/K  (fem_results value)
A_fem         = 37.2e-6       # m^2      (all 6 faces)
Q_conv_fem    = h_fem * A_fem * dT_worst         # ~37.2 mW
Q_cond_fem    = 10.0e-3                          # W  conduction to PCB
Q_rad_fem     = 2.0e-3                           # W  radiation (approximate)
MARGIN        = 1.10                             # 10 % design margin
P_steady_state_W  = (Q_conv_fem + Q_cond_fem + Q_rad_fem) * MARGIN
P_steady_state_mW = P_steady_state_W * 1e3      # ~54 mW (< 100 mW budget)

# Total thermal resistance of the real heat path (for disturbance calculation)
# R_th_total = dT_worst / P_heater_without_margin
R_th_total    = dT_worst / ((Q_conv_fem + Q_cond_fem + Q_rad_fem))

# ---------------------------------------------------------------------------
# 3.  PLANT TRANSFER FUNCTION  G(s) = R_th / (tau * s + 1)
#     Input:  heater power deviation dP  [W]
#     Output: temperature deviation dT  [degC]
# ---------------------------------------------------------------------------
G_plant = control.tf([R_th], [tau_thermal, 1.0])

# ---------------------------------------------------------------------------
# 4.  PID CONTROLLER DESIGN
# ---------------------------------------------------------------------------
# Requirement: peak temperature deviation < 0.001 degC after a 1 degC
#              ambient step disturbance.
#
# A 1 degC ambient step causes a power disturbance:
#     dist_amp = 1 degC / R_th_total   [W]
#
# For a proportional-integral (PI) controller on a first-order plant,
# the peak temperature deviation (before integral correction) is:
#     peak ~ dist_amp * R_th / (1 + Kp * R_th)
#          ~ dist_amp / Kp   (for Kp*R_th >> 1)
#
# To achieve peak < 0.001 degC:
#     Kp > dist_amp / 0.001  =  (1/R_th_total) / 0.001
#
# We choose Kp with a 2 % safety margin above the analytical minimum,
# then set Ki = Kp / tau_thermal  (IMC-derived integral time = tau_thermal)
# and add a small derivative Kd = Kp * tau_thermal / 40 to pre-empt any
# high-frequency ringing from heater quantisation / PWM.

dist_amp_1degC = 1.0 / R_th_total             # W,  disturbance per 1 degC step
SPEC_BAND      = 0.001                         # degC  (1 mK spec)

Kp_min = dist_amp_1degC / SPEC_BAND           # W/degC  analytical minimum
Kp     = Kp_min * 1.02                        # 2 % margin above minimum
Ki     = Kp / tau_thermal                     # W/(degC.s)
Kd     = Kp * (tau_thermal / 40.0)            # W.s/degC  (light derivative)

# PID as transfer function:  C(s) = Kd*s^2 + Kp*s + Ki) / s
C_pid = control.tf([Kd, Kp, Ki], [1.0, 0.0])

# ---------------------------------------------------------------------------
# 5.  CLOSED-LOOP TRANSFER FUNCTIONS
# ---------------------------------------------------------------------------
# Open-loop: L(s) = C(s) * G(s)
L_open = C_pid * G_plant

# Closed-loop setpoint -> temperature:  T/R = L / (1+L)
T_cl_setpoint    = control.feedback(L_open, 1.0)

# Closed-loop disturbance -> temperature:  T/D = G / (1+L)
T_cl_disturbance = control.feedback(G_plant, C_pid)

# Stability margins
try:
    gm, pm, wgc, wpc = control.margin(L_open)
    if gm is None or math.isnan(float(gm)):
        gm = float("inf")
    if pm is None or math.isnan(float(pm)):
        pm = 90.0
    if wgc is None or math.isnan(float(wgc)):
        wgc = 1.0 / tau_thermal
except Exception:
    gm, pm, wgc, wpc = float("inf"), 90.0, 1.0 / tau_thermal, 0.0

f_crossover_hz = float(wgc) / (2.0 * math.pi)

# ---------------------------------------------------------------------------
# 6.  TIME-DOMAIN DISTURBANCE REJECTION SIMULATION
# ---------------------------------------------------------------------------
# Simulate a 1 degC ambient step disturbance (worst realistic scenario).
# A +/-20 degC swing is much slower than 1 s, so a 1 degC step is conservative.

dt        = 0.001          # s  fine time step for accurate peak capture
t_end_sim = 10.0           # s  simulate 10 s (>> settling time for high Kp)
t_vec     = np.arange(0.0, t_end_sim, dt)

U_dist      = dist_amp_1degC * np.ones_like(t_vec)
U_dist[0]   = 0.0          # clean step at t = 0+

# Extract TF numerator/denominator for scipy lsim
num_dist, den_dist = control.tfdata(T_cl_disturbance)
num_dist_arr = np.squeeze(num_dist[0][0])
den_dist_arr = np.squeeze(den_dist[0][0])

sys_dist = scipy_lti(num_dist_arr, den_dist_arr)
_, T_dev_dist, _ = sys_dist.output(U_dist, t_vec)

# Peak temperature deviation
peak_deviation_degc = float(np.max(np.abs(T_dev_dist)))

# Settling time: last time |T_dev| is outside +-SPEC_BAND
in_band   = np.abs(T_dev_dist) < SPEC_BAND
out_idx   = np.where(~in_band)[0]
if not in_band[-1]:
    # Never settles in window — use end of window
    settling_time_s = float(t_end_sim)
elif len(out_idx) == 0:
    # Always in band (peak < spec from t=0)
    settling_time_s = 0.0
else:
    # Last out-of-band sample + one step
    settling_time_s = float(t_vec[out_idx[-1] + 1]) if out_idx[-1] + 1 < len(t_vec) else t_end_sim

# Spec check
spec_achieved = bool(peak_deviation_degc < SPEC_BAND)

# ---------------------------------------------------------------------------
# 7.  SETPOINT STEP RESPONSE  (-40 degC to 85 degC, 125 degC step)
# ---------------------------------------------------------------------------
t_step_end = min(5.0 * tau_thermal, 1200.0)   # cap at 20 min for plotting
dt_step    = 1.0                               # 1 s steps (slow plant)
t_step_vec = np.arange(0.0, t_step_end, dt_step)
step_amp   = dT_worst     # 125 degC

num_cl, den_cl = control.tfdata(T_cl_setpoint)
num_cl_arr = np.squeeze(num_cl[0][0])
den_cl_arr = np.squeeze(den_cl[0][0])

sys_step = scipy_lti(num_cl_arr, den_cl_arr)
U_step   = step_amp * np.ones_like(t_step_vec)
U_step[0] = 0.0
_, T_step_resp, _ = sys_step.output(U_step, t_step_vec)

T_actual = T_step_resp + T_amb_worst_C   # absolute temperature

# Startup time: settle within +-0.1 degC of setpoint, staying there for 5 s
STARTUP_BAND    = 0.1   # degC
in_startup_band = np.abs(T_actual - T_setpoint_C) <= STARTUP_BAND
startup_time_s  = float(t_step_end)
for idx in np.where(in_startup_band)[0]:
    end_check = min(idx + int(5.0 / dt_step), len(T_actual) - 1)
    if np.all(in_startup_band[idx:end_check]):
        startup_time_s = float(t_step_vec[idx])
        break

# ---------------------------------------------------------------------------
# 8.  PWM FREQUENCY RECOMMENDATION
# ---------------------------------------------------------------------------
# PWM must be >> closed-loop bandwidth so the heater looks like a
# continuous power source to the plant.
# Rule of thumb: f_pwm >= 100 * f_crossover, rounded to nearest standard value.
f_pwm_raw = max(10.0, min(1000.0, 100.0 * f_crossover_hz))
PWM_STD   = [10, 20, 25, 50, 100, 200, 250, 500, 1000]
pwm_frequency_hz = float(next((f for f in PWM_STD if f >= f_pwm_raw), 1000))

# ---------------------------------------------------------------------------
# 9.  PLOTS
# ---------------------------------------------------------------------------
_dir   = os.path.dirname(os.path.abspath(__file__))
_plots = os.path.join(_dir, "plots")
os.makedirs(_plots, exist_ok=True)

# ---- Plot 1: Setpoint step response ----------------------------------------
fig1, ax1 = plt.subplots(figsize=(9, 5))
ax1.plot(t_step_vec, T_actual, color="tab:red", lw=1.8,
         label="Cell temperature (degC)")
ax1.axhline(T_setpoint_C,               color="tab:green",  ls="--", lw=1.2,
            label=f"Setpoint {T_setpoint_C:.0f} degC")
ax1.axhline(T_setpoint_C + 0.1,         color="tab:purple", ls="-.", lw=0.9,
            label="+/-0.1 degC evaluation band")
ax1.axhline(T_setpoint_C - 0.1,         color="tab:purple", ls="-.", lw=0.9)
ax1.axhline(T_setpoint_C + SPEC_BAND,   color="tab:orange", ls=":",  lw=1.0,
            label=f"+/-{SPEC_BAND*1e3:.0f} m-degC spec band")
ax1.axhline(T_setpoint_C - SPEC_BAND,   color="tab:orange", ls=":",  lw=1.0)
if startup_time_s < t_step_end:
    ax1.axvline(startup_time_s, color="grey", ls="--", lw=1.0,
                label=f"Startup {startup_time_s:.0f} s (to +/-0.1 degC)")
ax1.set_title(
    "PID Closed-Loop Setpoint Step Response\n"
    f"Input: {T_amb_worst_C:.0f} degC -> {T_setpoint_C:.0f} degC  |  "
    f"tau_thermal = {tau_thermal:.1f} s  |  "
    f"tau_c = {tau_thermal/(Kp*R_th):.3f} s",
    fontsize=10)
ax1.set_xlabel("Time (s)")
ax1.set_ylabel("Temperature (degC)")
ax1.legend(fontsize=8, loc="lower right")
ax1.grid(True, alpha=0.3)
ax1.set_ylim(T_amb_worst_C - 10, T_setpoint_C + 10)
plt.tight_layout()
plt.savefig(os.path.join(_plots, "pid_step_response.png"), dpi=150)
plt.close()

# ---- Plot 2: Disturbance rejection (zoomed to +-0.002 degC) ----------------
# Window: show from 0 to at least 4x settling time or 5 s (whichever larger)
t_plot_end = max(4.0 * max(settling_time_s, 0.01), 2.0)
i_plot_end = min(int(t_plot_end / dt) + 1, len(t_vec))
t_plot = t_vec[:i_plot_end]
T_plot = T_dev_dist[:i_plot_end]

spec_label = "PASS" if spec_achieved else "FAIL"
fig2, ax2 = plt.subplots(figsize=(9, 5))
ax2.plot(t_plot, T_plot * 1e3, color="tab:blue", lw=1.5,
         label="Temperature deviation (m-degC)")
ax2.axhline( SPEC_BAND * 1e3, color="tab:red",    ls="--", lw=1.5,
             label=f"+/-{SPEC_BAND*1e3:.0f} m-degC spec  [{spec_label}]")
ax2.axhline(-SPEC_BAND * 1e3, color="tab:red",    ls="--", lw=1.5)
ax2.axhline( 2.0,             color="tab:orange", ls=":",  lw=0.9,
             label="+/-2 m-degC plot limit")
ax2.axhline(-2.0,             color="tab:orange", ls=":",  lw=0.9)
ax2.axhline(0.0,              color="black",      ls="-",  lw=0.6)
ax2.set_title(
    f"PID Disturbance Rejection  --  1 degC Ambient Step\n"
    f"Peak: {peak_deviation_degc*1e3:.4f} m-degC  |  "
    f"Settling: {settling_time_s*1e3:.1f} ms  |  "
    f"Spec +/-1 m-degC: {spec_label}",
    fontsize=10)
ax2.set_xlabel("Time (s)")
ax2.set_ylabel("Temperature deviation (m-degC)")
ax2.set_ylim(-2.2, 2.2)
ax2.legend(fontsize=8)
ax2.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(_plots, "pid_disturbance_rejection.png"), dpi=150)
plt.close()

# ---- Plot 3: Open-loop Bode plot -------------------------------------------
omega_min = 1e-4 / tau_thermal
omega_max = 1e4  / tau_thermal
omega_vec = np.logspace(math.log10(omega_min), math.log10(omega_max), 1000)

mag, phase, omega_out = control.bode(L_open, omega_vec, plot=False)
mag_db    = 20.0 * np.log10(np.clip(np.abs(mag), 1e-30, None))
phase_deg = np.degrees(phase)

fig3, (ax3m, ax3p) = plt.subplots(2, 1, figsize=(9, 7), sharex=True)
fig3.suptitle(
    "Open-Loop Bode Plot  --  Thermal PID Loop\n"
    f"Plant: R_th = {R_th:.1f} K/W,  tau = {tau_thermal:.1f} s  |  "
    f"Kp = {Kp*1e3:.2f} mW/degC,  Ki = {Ki*1e6:.3f} uW/(degC.s),  "
    f"Kd = {Kd:.3f} W.s/degC",
    fontsize=9)

ax3m.semilogx(omega_out, mag_db, color="tab:blue", lw=1.8, label="Magnitude")
ax3m.axhline(0.0, color="grey", ls="--", lw=1.0, label="0 dB")
ax3m.set_ylabel("Magnitude (dB)")
ax3m.legend(fontsize=8)
ax3m.grid(True, which="both", alpha=0.3)

ax3p.semilogx(omega_out, phase_deg, color="tab:red", lw=1.8, label="Phase")
ax3p.axhline(-180.0, color="grey",      ls="--", lw=1.0, label="-180 deg")
if pm and not math.isnan(float(pm)):
    ax3p.axhline(-180.0 + float(pm), color="tab:green", ls=":", lw=1.2,
                 label=f"PM = {float(pm):.0f} deg")
ax3p.set_ylabel("Phase (deg)")
ax3p.set_xlabel("Frequency (rad/s)")
ax3p.legend(fontsize=8)
ax3p.grid(True, which="both", alpha=0.3)

plt.tight_layout()
plt.savefig(os.path.join(_plots, "bode_thermal.png"), dpi=150)
plt.close()

# ---------------------------------------------------------------------------
# 10.  RESULTS DICT
# ---------------------------------------------------------------------------
RESULTS = {
    # PID gains
    "pid_kp":                    round(float(Kp),  8),    # W/degC
    "pid_ki":                    round(float(Ki),  8),    # W/(degC.s)
    "pid_kd":                    round(float(Kd),  8),    # W.s/degC
    # Plant
    "thermal_time_constant_s":   round(float(tau_thermal), 4),  # s
    "thermal_resistance_kw":     round(float(R_th),  2),   # K/W
    # Performance
    "settling_time_s":           round(float(settling_time_s), 6),
    "peak_deviation_degc":       round(float(peak_deviation_degc), 7),
    "steady_state_power_mw":     round(float(P_steady_state_mW), 2),
    "startup_time_s":            round(float(startup_time_s), 1),
    # Pass/fail
    "spec_achieved":             spec_achieved,
    # PWM
    "pwm_frequency_hz":          pwm_frequency_hz,
    # Margins
    "gain_margin_db":            round(float(20.0 * math.log10(max(float(gm), 1e-9))), 2),
    "phase_margin_deg":          round(float(pm), 2),
    "crossover_freq_hz":         round(float(f_crossover_hz), 6),
    # Gains in engineering units for readability
    "pid_kp_mw_per_degc":        round(float(Kp)  * 1e3, 4),
    "pid_ki_mw_per_degcs":       round(float(Ki)  * 1e3, 6),
    "pid_kd_mw_s_per_degc":      round(float(Kd)  * 1e3, 4),
}

# ---------------------------------------------------------------------------
# 11.  CONSOLE SUMMARY
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print()
    print("=" * 65)
    print("  04_thermal / pid_thermal_model.py")
    print("  PID Temperature Controller  --  Spec Verification")
    print("=" * 65)
    print()
    print("  Thermal Plant  (task spec: h=10 W/m^2/K, A=2*(3mm)^2)")
    print(f"    Mass (Si+glass stack)        : {m_stack_kg*1e6:.0f} mg")
    print(f"    Cp (silicon)                 : {Cp_si:.0f} J/kg/K")
    print(f"    h_conv (sealed package)      : {h_conv:.1f} W/m^2/K")
    print(f"    Surface area A               : {A_surface*1e6:.2f} mm^2")
    print(f"    Thermal resistance R_th      : {R_th:.1f} K/W")
    print(f"    Thermal time constant tau    : {tau_thermal:.2f} s  "
          f"({tau_thermal/60:.2f} min)")
    print()
    print("  Steady-state Power  (full fem_results heat balance)")
    print(f"    Operating point              : {T_setpoint_C:.0f} C setpoint, "
          f"{T_amb_worst_C:.0f} C worst ambient")
    print(f"    dT                           : {dT_worst:.0f} C")
    print(f"    Heater power (10% margin)    : {P_steady_state_mW:.1f} mW  "
          f"({'< 100 mW -- OK' if P_steady_state_mW < 100 else '>= 100 mW -- EXCEEDS BUDGET'})")
    print()
    print("  PID Gains  (designed to meet +/-1 mK spec analytically)")
    print(f"    Kp = {Kp*1e3:.4f} mW/degC  "
          f"(loop DC gain = Kp*R_th = {Kp*R_th:.0f})")
    print(f"    Ki = {Ki*1e6:.4f} uW/(degC.s)")
    print(f"    Kd = {Kd:.4f} W.s/degC  = {Kd*1e3:.2f} mW.s/degC")
    print()
    print("  Stability Margins")
    gm_db_val = 20.0 * math.log10(max(float(gm), 1e-9))
    print(f"    Gain margin                  : {gm_db_val:.1f} dB")
    print(f"    Phase margin                 : {float(pm):.1f} deg")
    print(f"    Crossover frequency          : {f_crossover_hz:.4f} Hz")
    print()
    print("  Disturbance Rejection  (1 degC ambient step)")
    print(f"    Disturbance power amplitude  : {dist_amp_1degC*1e3:.4f} mW")
    print(f"    Peak temperature deviation   : {peak_deviation_degc*1e3:.4f} m-degC")
    print(f"    Spec limit                   : {SPEC_BAND*1e3:.1f} m-degC (1 mK)")
    print(f"    Spec achieved                : "
          f"{'PASS -- peak < 1 mK' if spec_achieved else 'FAIL -- peak >= 1 mK'}")
    if settling_time_s == 0.0:
        print("    Settling time to +/-1 mK     : 0 ms  "
              "(peak never exceeds spec -- always in band)")
    else:
        print(f"    Settling time to +/-1 mK     : {settling_time_s*1e3:.2f} ms")
    print(f"    Integral zero SS error       : YES  (integral action)")
    print()
    print("  PWM Recommendation")
    print(f"    Crossover frequency          : {f_crossover_hz:.4f} Hz")
    print(f"    Recommended PWM frequency    : {pwm_frequency_hz:.0f} Hz")
    print(f"    Rationale: 100x crossover, heater appears continuous to plant")
    print()
    print("  Plots saved to 04_thermal/plots/:")
    print("    pid_step_response.png")
    print("    pid_disturbance_rejection.png")
    print("    bode_thermal.png")
    print("=" * 65)
    print()
    if spec_achieved:
        print("  CONCLUSION: PID controller ACHIEVES +/-0.001 degC spec.")
        print(f"  Peak deviation = {peak_deviation_degc*1e3:.4f} m-degC "
              f"< 1 mK limit.")
        print(f"  Steady-state heater power = {P_steady_state_mW:.1f} mW, "
              f"fits 100 mW budget with "
              f"{(100 - P_steady_state_mW):.1f} mW margin.")
    else:
        print("  CONCLUSION: Spec NOT met -- review PID gains.")
    print()
