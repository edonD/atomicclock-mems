"""
CSAC Thermal Control Simulation: How 85 C Gets Maintained

The Rb atoms need to be at ~85C to have enough vapor pressure for the CPT
interrogation to work. Too cold = not enough atoms = weak signal. Too hot =
collisional broadening = blurry signal. The window is roughly +/- 0.1C.

This simulation shows ALL the layers of the thermal management system:

1. WHY 85C? -- Rb vapor pressure curve (exponential with temperature)
2. THE HEATERS -- Thin-film Pt resistive heaters deposited on the Si body
3. THE SENSOR -- Pt RTD (resistance temperature detector) on the same die
4. THE PID LOOP -- Closed-loop feedback: sensor -> PID -> heater drive
5. THERMAL STRUCTURE -- Vacuum packaging + low-conductivity Si = insulation
6. REAL-TIME RESPONSE -- How the system reacts to external temperature shocks
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import FancyArrowPatch, Rectangle, FancyBboxPatch
from mpl_toolkits.mplot3d import art3d
import matplotlib.patheffects as pe

# ──────────────────────────────────────────────────────────────────────
# FIGURE
# ──────────────────────────────────────────────────────────────────────
fig = plt.figure(figsize=(22, 30), facecolor='#0a0a1a')
fig.suptitle(
    'HOW THE CSAC MAINTAINS EXACTLY 85 C\n'
    'Thermal Control: From Quantum Need to PID Feedback Loop',
    fontsize=18, fontweight='bold', color='white', y=0.995
)

gs = GridSpec(4, 3, figure=fig, hspace=0.30, wspace=0.28,
              left=0.06, right=0.94, top=0.96, bottom=0.03)


# ======================================================================
# PANEL 1: WHY 85C? -- Rb Vapor Pressure Curve
# ======================================================================
ax1 = fig.add_subplot(gs[0, 0], facecolor='#0a0a1a')
ax1.set_title('1. WHY EXACTLY 85 C?', color='#ff8844',
              fontsize=13, fontweight='bold')

# Rubidium vapor pressure (Clausius-Clapeyron approximation)
# log10(P_torr) = A - B/T  for Rb (Antoine equation approximation)
# A ~ 4.312, B ~ 4040 for Rb metal
T_celsius = np.linspace(20, 150, 500)
T_kelvin = T_celsius + 273.15
log10_P = 4.312 - 4040.0 / T_kelvin
P_torr = 10**log10_P
# Rb number density from ideal gas: n = P / (kB * T)
kB = 1.38e-23
P_pascal = P_torr * 133.322
n_density = P_pascal / (kB * T_kelvin)  # atoms/m^3

ax1.semilogy(T_celsius, n_density, color='#ff8844', linewidth=3)

# Mark the operating point
T_op = 85
T_op_K = T_op + 273.15
n_op = (10**(4.312 - 4040.0/T_op_K) * 133.322) / (kB * T_op_K)
ax1.plot(T_op, n_op, 'o', color='#00ff88', markersize=14, zorder=5)
ax1.axvline(T_op, color='#00ff88', linestyle='--', alpha=0.5)

# Operating window
ax1.axvspan(83, 87, alpha=0.15, color='#00ff88')
ax1.text(85, n_op * 5, 'OPERATING\nWINDOW\n83-87 C', ha='center',
         fontsize=9, color='#00ff88', fontweight='bold')

# Too cold region
ax1.axvspan(20, 50, alpha=0.08, color='#4444ff')
ax1.text(35, 1e16, 'TOO COLD\nNot enough\nRb atoms\n= weak signal', ha='center',
         fontsize=8, color='#6666ff')

# Too hot region
ax1.axvspan(120, 150, alpha=0.08, color='#ff4444')
ax1.text(135, 1e19, 'TOO HOT\nCollisional\nbroadening\n= blurry signal', ha='center',
         fontsize=8, color='#ff4444')

# The key number
ax1.annotate(
    f'At 85 C:\nn = {n_op:.1e} atoms/m3\n'
    'Enough atoms to absorb,\nnot so many they collide.',
    xy=(T_op, n_op), xytext=(110, n_op/50),
    fontsize=9, color='white',
    arrowprops=dict(arrowstyle='->', color='white', lw=1.5),
    bbox=dict(boxstyle='round,pad=0.4', facecolor='#1a1a2e', edgecolor='#ff8844'))

ax1.set_xlabel('Temperature (C)', color='white', fontsize=10)
ax1.set_ylabel('Rb Number Density (atoms/m3)', color='white', fontsize=10)
ax1.set_xlim(20, 150)
ax1.grid(True, alpha=0.15, color='gray')
ax1.tick_params(colors='gray')
for sp in ax1.spines.values():
    sp.set_edgecolor('#333')


# ======================================================================
# PANEL 2: CPT SIGNAL QUALITY vs TEMPERATURE
# ======================================================================
ax2 = fig.add_subplot(gs[0, 1], facecolor='#0a0a1a')
ax2.set_title('2. SIGNAL QUALITY vs TEMPERATURE', color='#ff8844',
              fontsize=13, fontweight='bold')

T_sweep = np.linspace(40, 130, 300)

# CPT contrast: rises with vapor density, then drops from broadening
# Model: contrast ~ n * exp(-n/n_optimal) (absorption then broadening)
T_sweep_K = T_sweep + 273.15
n_sweep = (10**(4.312 - 4040.0/T_sweep_K) * 133.322) / (kB * T_sweep_K)
n_opt = n_op  # optimal at 85C
contrast = (n_sweep / n_opt) * np.exp(-(n_sweep / n_opt - 1)**2 / 0.5)
contrast = contrast / contrast.max() * 25  # normalize to ~25% max

# CPT linewidth: broadens with density + power broadening
linewidth = 2.0 + 0.5 * (n_sweep / n_opt) + 0.02 * (T_sweep - 85)**2 / 100

# Figure of merit: contrast / linewidth (what you actually optimize)
fom = contrast / linewidth
fom = fom / fom.max() * 100  # normalize to percentage

ax2b = ax2.twinx()

ax2.plot(T_sweep, contrast, color='#00ff88', linewidth=2.5, label='CPT Contrast (%)')
ax2.plot(T_sweep, linewidth, color='#ff4444', linewidth=2, linestyle='--',
         label='CPT Linewidth (kHz)')
ax2b.plot(T_sweep, fom, color='#ffaa00', linewidth=2.5, linestyle='-',
          label='Figure of Merit', alpha=0.8)

# Mark optimum
fom_max_idx = np.argmax(fom)
T_fom_max = T_sweep[fom_max_idx]
ax2.axvline(T_fom_max, color='yellow', linestyle=':', alpha=0.5)
ax2.text(T_fom_max + 2, 22, f'OPTIMUM\n~{T_fom_max:.0f} C', fontsize=9,
         color='yellow', fontweight='bold')

ax2.axvspan(83, 87, alpha=0.12, color='#00ff88')

ax2.set_xlabel('Cell Temperature (C)', color='white', fontsize=10)
ax2.set_ylabel('Contrast (%) / Linewidth (kHz)', color='#00ff88', fontsize=9)
ax2b.set_ylabel('Figure of Merit (%)', color='#ffaa00', fontsize=9)
ax2.legend(fontsize=8, loc='upper left', facecolor='#1a1a2e', edgecolor='#444',
           labelcolor='white')
ax2b.legend(fontsize=8, loc='upper right', facecolor='#1a1a2e', edgecolor='#444',
            labelcolor='white')
ax2.tick_params(colors='gray')
ax2b.tick_params(colors='gray')
ax2.grid(True, alpha=0.1, color='gray')
for sp in ax2.spines.values():
    sp.set_edgecolor('#333')
for sp in ax2b.spines.values():
    sp.set_edgecolor('#333')


# ======================================================================
# PANEL 3: WHAT HAPPENS WITH +/- 1C ERROR
# ======================================================================
ax3 = fig.add_subplot(gs[0, 2], facecolor='#0a0a1a')
ax3.set_title('3. WHAT IF TEMPERATURE DRIFTS?', color='#ff8844',
              fontsize=13, fontweight='bold')

# Frequency shift vs temperature (temperature coefficient)
# Typical CSAC: ~1e-10 / C  (the "temperature sensitivity")
dT = np.linspace(-5, 5, 300)  # C deviation from setpoint
# Quadratic + linear model for frequency shift
freq_shift = -2e-10 * dT + 5e-11 * dT**2  # fractional frequency shift

# Position error per hour due to this frequency shift
# df/f * speed_of_light * 3600 seconds
pos_err_per_hour = np.abs(freq_shift) * 3e8 * 3600  # meters

ax3_twin = ax3.twinx()
ax3.plot(dT, freq_shift * 1e9, color='#44aaff', linewidth=2.5,
         label='Frequency shift (ppb)')
ax3_twin.plot(dT, pos_err_per_hour, color='#ff4444', linewidth=2.5, linestyle='--',
              label='Position error/hour (m)')

# Mark the good zone
ax3.axvspan(-0.1, 0.1, alpha=0.2, color='#00ff88')
ax3.text(0, 0.15, '+/- 0.1 C\ncontrol', ha='center', fontsize=9,
         color='#00ff88', fontweight='bold',
         bbox=dict(boxstyle='round,pad=0.2', facecolor='#0a1a0a', edgecolor='#00ff88'))

# Bad zones
ax3.annotate('+1 C drift =\n~72 m/hr extra error!',
             xy=(1, -2e-10*1*1e9 + 5e-11*1e9),
             xytext=(2.5, 0.4),
             fontsize=8, color='#ff4444', fontweight='bold',
             arrowprops=dict(arrowstyle='->', color='#ff4444', lw=1.5))

ax3.axhline(0, color='gray', alpha=0.3)
ax3.axvline(0, color='gray', alpha=0.3)
ax3.set_xlabel('Temperature Deviation from 85 C (C)', color='white', fontsize=10)
ax3.set_ylabel('Frequency Shift (ppb)', color='#44aaff', fontsize=10)
ax3_twin.set_ylabel('Extra Position Error/Hour (m)', color='#ff4444', fontsize=10)
ax3.legend(fontsize=8, loc='upper left', facecolor='#1a1a2e', edgecolor='#444',
           labelcolor='white')
ax3_twin.legend(fontsize=8, loc='upper right', facecolor='#1a1a2e', edgecolor='#444',
                labelcolor='white')
ax3.tick_params(colors='gray')
ax3_twin.tick_params(colors='gray')
ax3.grid(True, alpha=0.1, color='gray')
for sp in ax3.spines.values():
    sp.set_edgecolor('#333')
for sp in ax3_twin.spines.values():
    sp.set_edgecolor('#333')


# ======================================================================
# PANEL 4: PHYSICAL STRUCTURE -- Cross-section of thermal insulation
# ======================================================================
ax4 = fig.add_subplot(gs[1, 0], facecolor='#0a0a1a')
ax4.set_title('4. THERMAL INSULATION STRUCTURE (Cross-Section)',
              color='#00ccff', fontsize=12, fontweight='bold')

# Draw the layered cross-section
def draw_rect(ax, x, y, w, h, color, label, alpha=0.4, text_color='white'):
    rect = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02",
                           facecolor=color, edgecolor='white', linewidth=1.2,
                           alpha=alpha)
    ax.add_patch(rect)
    ax.text(x + w/2, y + h/2, label, ha='center', va='center',
            fontsize=8, color=text_color, fontweight='bold')

# Outer vacuum package
draw_rect(ax4, 0.5, 0.2, 9.0, 8.5, '#222244', '', alpha=0.2)
ax4.text(5.0, 8.5, 'VACUUM PACKAGE (LCC ceramic)', ha='center',
         fontsize=9, color='#6666aa', fontweight='bold')

# Vacuum gap (the main insulator)
draw_rect(ax4, 1.0, 0.8, 8.0, 7.2, '#000011', '', alpha=0.3)
ax4.text(5.0, 7.7, 'VACUUM GAP (~0.01 mbar)', ha='center',
         fontsize=9, color='#4444aa')
ax4.text(5.0, 7.2, 'Main thermal insulator!\nVacuum = almost zero conduction',
         ha='center', fontsize=7.5, color='#6666aa', style='italic')

# Suspension beams (low thermal conductance)
for y_beam in [2.5, 5.5]:
    ax4.plot([1.0, 2.5], [y_beam, y_beam], color='#888888', linewidth=3)
    ax4.plot([7.5, 9.0], [y_beam, y_beam], color='#888888', linewidth=3)
ax4.text(1.2, 6.0, 'Thin Si\nsuspension\nbeams', fontsize=6.5, color='#aaaaaa')

# The MEMS cell stack (center)
# Top glass
draw_rect(ax4, 2.5, 5.8, 5.0, 0.6, '#4488cc', 'Top Glass (borosilicate)', alpha=0.5)
# Silicon body with heaters
draw_rect(ax4, 2.5, 3.5, 5.0, 2.3, '#666666', '', alpha=0.5)
ax4.text(5.0, 4.6, 'SILICON BODY', ha='center', fontsize=9, color='white', fontweight='bold')

# Vapor cavity inside Si
draw_rect(ax4, 3.2, 3.8, 3.6, 1.5, '#002244', 'Rb VAPOR\n+ N2 gas\n(85 C)', alpha=0.6, text_color='#00ff88')

# Pt heater traces (on top of Si body)
for hx in [2.7, 3.5, 4.3, 5.1, 5.9, 6.7]:
    ax4.plot([hx, hx], [5.75, 5.85], color='#FFD700', linewidth=3, solid_capstyle='round')
ax4.text(7.8, 5.55, 'Pt HEATERS\n(thin film,\n~200 nm)', fontsize=7,
         color='#FFD700', fontweight='bold',
         bbox=dict(boxstyle='round,pad=0.2', facecolor='#1a1a0a', edgecolor='#FFD700'))
ax4.annotate('', xy=(7.0, 5.8), xytext=(7.7, 5.6),
             arrowprops=dict(arrowstyle='->', color='#FFD700', lw=1.5))

# Pt RTD temperature sensor
ax4.plot([3.0, 3.3, 3.6, 3.9, 4.2], [3.55, 3.65, 3.55, 3.65, 3.55],
         color='#ff8844', linewidth=2.5)
ax4.text(2.3, 3.3, 'Pt RTD\nSENSOR', fontsize=7, color='#ff8844', fontweight='bold',
         bbox=dict(boxstyle='round,pad=0.2', facecolor='#1a0a0a', edgecolor='#ff8844'))

# Bottom glass
draw_rect(ax4, 2.5, 2.9, 5.0, 0.6, '#4488cc', 'Bottom Glass (borosilicate)', alpha=0.5)

# Anti-permeation coating
ax4.plot([2.5, 7.5], [3.5, 3.5], color='#ff44ff', linewidth=1.5, linestyle=':')
ax4.text(8.0, 3.5, 'Anti-permeation\ncoating (Al2O3)', fontsize=6.5,
         color='#ff44ff', ha='left', va='center')

# VCSEL below
draw_rect(ax4, 3.8, 1.5, 2.4, 0.8, '#ff4444', 'VCSEL LASER', alpha=0.5)
# Photodetector above
draw_rect(ax4, 3.8, 6.6, 2.4, 0.6, '#44ff44', 'PHOTODETECTOR', alpha=0.5)

# Laser beam
ax4.annotate('', xy=(5.0, 6.6), xytext=(5.0, 2.3),
             arrowprops=dict(arrowstyle='->', color='red', lw=2, linestyle='--', alpha=0.5))

# Heat flow arrows (showing insulation)
for y_arr in [1.0, 4.5, 7.5]:
    ax4.annotate('', xy=(0.7, y_arr), xytext=(0.2, y_arr),
                 arrowprops=dict(arrowstyle='->', color='#ff4444', lw=1.5, alpha=0.4))
ax4.text(-0.3, 4.5, 'External\nheat\n(blocked!)', fontsize=7, color='#ff4444',
         rotation=90, ha='center', va='center')

ax4.set_xlim(-0.8, 10)
ax4.set_ylim(0, 9.2)
ax4.axis('off')


# ======================================================================
# PANEL 5: THE Pt HEATER -- How it generates heat
# ======================================================================
ax5 = fig.add_subplot(gs[1, 1], facecolor='#0a0a1a')
ax5.set_title('5. PLATINUM THIN-FILM HEATER', color='#00ccff',
              fontsize=13, fontweight='bold')

# Draw the serpentine heater pattern
ax5.text(5.0, 9.5, 'Top view of Si body with Pt heater traces',
         ha='center', fontsize=9, color='#aaaaaa', style='italic')

# Silicon die outline
si_rect = FancyBboxPatch((1, 1), 8, 8, boxstyle="round,pad=0.1",
                          facecolor='#333333', edgecolor='#666666',
                          linewidth=2, alpha=0.4)
ax5.add_patch(si_rect)
ax5.text(5.0, 0.5, 'Silicon die (~2 x 2 mm)', ha='center',
         fontsize=8, color='#888888')

# Vapor cell cavity (center, dashed)
cavity = plt.Circle((5, 5), 2.0, fill=False, edgecolor='#44aaff',
                     linewidth=1.5, linestyle='--')
ax5.add_patch(cavity)
ax5.text(5.0, 5.0, 'Rb Vapor\nCavity', ha='center', fontsize=9,
         color='#44aaff', alpha=0.6)

# Serpentine heater pattern (dual zone)
# Zone 1: inner heater (fine control)
x_serp1 = []
y_serp1 = []
y_pos = 3.0
direction = 1
for i in range(8):
    x_start = 2.5 if direction == 1 else 4.5
    x_end = 4.5 if direction == 1 else 2.5
    x_serp1.extend([x_start, x_end])
    y_serp1.extend([y_pos, y_pos])
    if i < 7:
        y_pos += 0.5
        x_serp1.append(x_end)
        y_serp1.append(y_pos)
    direction *= -1
ax5.plot(x_serp1, y_serp1, color='#FFD700', linewidth=2.5, alpha=0.9)
ax5.text(2.0, 4.0, 'HEATER\nZONE 1\n(inner)', fontsize=7,
         color='#FFD700', fontweight='bold', rotation=90, ha='center', va='center')

# Zone 2: outer heater (guard ring)
x_serp2 = []
y_serp2 = []
y_pos = 2.0
direction = 1
for i in range(10):
    x_start = 5.5 if direction == 1 else 7.5
    x_end = 7.5 if direction == 1 else 5.5
    x_serp2.extend([x_start, x_end])
    y_serp2.extend([y_pos, y_pos])
    if i < 9:
        y_pos += 0.6
        x_serp2.append(x_end)
        y_serp2.append(y_pos)
    direction *= -1
ax5.plot(x_serp2, y_serp2, color='#ff8844', linewidth=2, alpha=0.7)
ax5.text(8.2, 5.0, 'HEATER\nZONE 2\n(outer/\nguard)', fontsize=7,
         color='#ff8844', fontweight='bold', ha='center', va='center')

# Temperature sensor (RTD)
rtd_x = [3.5, 3.7, 3.5, 3.7, 3.5, 3.7, 3.5]
rtd_y = [6.0, 6.0, 6.3, 6.3, 6.6, 6.6, 6.9]
ax5.plot(rtd_x, rtd_y, color='#00ff88', linewidth=3)
ax5.text(3.6, 7.2, 'Pt RTD SENSOR', fontsize=8, color='#00ff88',
         fontweight='bold', ha='center')

# Bond pads
for px, py, label in [(1.3, 1.3, 'H1+'), (1.3, 8.7, 'H1-'),
                       (8.7, 1.3, 'H2+'), (8.7, 8.7, 'H2-'),
                       (1.3, 5.0, 'RTD+'), (8.7, 5.0, 'RTD-')]:
    ax5.plot(px, py, 's', color='white', markersize=8)
    ax5.text(px, py - 0.4, label, ha='center', fontsize=6, color='white')

# Explanation
ax5.text(5.0, -0.8,
    'How it works: Current through Pt trace -> resistive heating (P = I2R)\n'
    'Pt chosen because: linear R vs T, stable, MEMS-compatible deposition\n'
    'Dual zone: inner heater for cavity, outer "guard" to reduce gradients',
    ha='center', fontsize=8, color='#aaaaaa',
    bbox=dict(boxstyle='round,pad=0.4', facecolor='#111133', edgecolor='#444'))

ax5.set_xlim(-0.5, 10.5)
ax5.set_ylim(-1.5, 10)
ax5.set_aspect('equal')
ax5.axis('off')


# ======================================================================
# PANEL 6: THE PID CONTROL LOOP -- Block Diagram
# ======================================================================
ax6 = fig.add_subplot(gs[1, 2], facecolor='#0a0a1a')
ax6.set_title('6. PID FEEDBACK LOOP (The Brain)', color='#00ccff',
              fontsize=13, fontweight='bold')

# Block diagram
blocks = [
    (2.0, 7.0, 2.0, 1.0, 'SETPOINT\n85.000 C', '#00ff88'),
    (2.0, 5.0, 2.0, 1.0, 'ERROR\nSUMMER\ne = Tset - Tmeas', '#ffaa00'),
    (5.5, 5.0, 2.5, 1.0, 'PID\nCONTROLLER', '#aa44ff'),
    (5.5, 3.0, 2.5, 1.0, 'PWM\nDRIVER', '#ff8844'),
    (5.5, 1.0, 2.5, 1.0, 'Pt HEATER\n(I2R heating)', '#FFD700'),
    (2.0, 1.0, 2.0, 1.0, 'Rb VAPOR\nCELL', '#44aaff'),
    (2.0, 3.0, 2.0, 1.0, 'Pt RTD\nSENSOR\n(measures T)', '#ff8844'),
]

for bx, by, bw, bh, txt, col in blocks:
    rect = FancyBboxPatch((bx - bw/2, by - bh/2), bw, bh,
                           boxstyle="round,pad=0.1", facecolor=col,
                           edgecolor='white', linewidth=1.5, alpha=0.35)
    ax6.add_patch(rect)
    ax6.text(bx, by, txt, ha='center', va='center', fontsize=7.5,
             color='white', fontweight='bold')

# Arrows
arrow_list = [
    ((2.0, 6.5), (2.0, 5.5), 'Tset'),
    ((3.0, 5.0), (4.25, 5.0), 'error'),
    ((6.75, 4.5), (6.75, 3.5), 'duty\ncycle'),
    ((6.75, 2.5), (6.75, 1.5), 'current'),
    ((4.25, 1.0), (3.0, 1.0), 'HEAT'),
    ((2.0, 1.5), (2.0, 2.5), 'T'),
    ((2.0, 3.5), (2.0, 4.5), 'Tmeas'),
]
for (x1,y1), (x2,y2), lab in arrow_list:
    ax6.annotate('', xy=(x2,y2), xytext=(x1,y1),
                 arrowprops=dict(arrowstyle='->', color='white', lw=2))
    mx, my = (x1+x2)/2, (y1+y2)/2
    if x1 == x2:  # vertical
        ax6.text(mx + 0.5, my, lab, fontsize=6.5, color='#aaaaaa', va='center')
    else:  # horizontal
        ax6.text(mx, my + 0.25, lab, fontsize=6.5, color='#aaaaaa', ha='center')

# PID explanation
ax6.text(8.5, 5.0,
    'P = Proportional\n  (react to current error)\n\n'
    'I = Integral\n  (eliminate steady-state\n   offset over time)\n\n'
    'D = Derivative\n  (damp oscillations,\n   anticipate changes)',
    fontsize=7.5, color='#aa88ff', va='center',
    bbox=dict(boxstyle='round,pad=0.4', facecolor='#1a1a2e', edgecolor='#aa44ff'))

# Disturbance
ax6.annotate('External\ntemp change\n(disturbance!)', xy=(0.5, 1.0),
             xytext=(-0.5, -0.5), fontsize=8, color='#ff4444', fontweight='bold',
             arrowprops=dict(arrowstyle='->', color='#ff4444', lw=2))

ax6.set_xlim(-1.5, 11)
ax6.set_ylim(-1.2, 8.0)
ax6.axis('off')


# ======================================================================
# PANEL 7: PID STEP RESPONSE -- Simulation of startup
# ======================================================================
ax7 = fig.add_subplot(gs[2, 0], facecolor='#0a0a1a')
ax7.set_title('7. STARTUP: Heating from 25 C to 85 C', color='#ffaa00',
              fontsize=12, fontweight='bold')

# Simulate PID control of thermal mass heating up
dt = 0.01  # seconds
t_end = 15.0  # seconds
t_sim = np.arange(0, t_end, dt)

# Thermal model parameters
C_thermal = 0.005   # J/K (thermal capacitance of MEMS cell -- very small!)
R_thermal = 500.0   # K/W (thermal resistance to ambient -- high due to vacuum)
T_ambient = 25.0    # C
T_setpoint = 85.0   # C
P_max = 0.120       # W (max heater power, ~120 mW total)

# PID gains (tuned for this system)
Kp = 0.008
Ki = 0.003
Kd = 0.001

T_cell = np.zeros(len(t_sim))
P_heater = np.zeros(len(t_sim))
T_cell[0] = T_ambient

integral_err = 0
prev_err = T_setpoint - T_ambient

for i in range(1, len(t_sim)):
    err = T_setpoint - T_cell[i-1]
    integral_err += err * dt
    d_err = (err - prev_err) / dt

    # PID output (heater power as fraction of max)
    u = Kp * err + Ki * integral_err + Kd * d_err
    u = np.clip(u, 0, 1)  # 0 to 100% duty cycle
    P_heat = u * P_max

    # Heat loss to ambient through thermal resistance
    P_loss = (T_cell[i-1] - T_ambient) / R_thermal

    # Temperature update: dT/dt = (P_heat - P_loss) / C_thermal
    dT = (P_heat - P_loss) / C_thermal * dt
    T_cell[i] = T_cell[i-1] + dT
    P_heater[i] = P_heat * 1000  # mW

    prev_err = err

ax7.plot(t_sim, T_cell, color='#ff8844', linewidth=2.5, label='Cell Temperature')
ax7.axhline(T_setpoint, color='#00ff88', linestyle='--', alpha=0.7, label='Setpoint (85 C)')
ax7.axhline(T_ambient, color='#44aaff', linestyle=':', alpha=0.5, label='Ambient (25 C)')

# Power on secondary axis
ax7b = ax7.twinx()
ax7b.plot(t_sim, P_heater, color='#FFD700', linewidth=1.5, alpha=0.5, label='Heater Power (mW)')
ax7b.fill_between(t_sim, 0, P_heater, alpha=0.1, color='#FFD700')

# Settle time
settled_mask = np.abs(T_cell - T_setpoint) < 0.1
if np.any(settled_mask):
    settle_idx = np.argmax(settled_mask)
    settle_time = t_sim[settle_idx]
    ax7.axvline(settle_time, color='#00ff88', alpha=0.3, linewidth=1)
    ax7.text(settle_time + 0.3, 50, f'Settled!\n{settle_time:.1f} s\n+/- 0.1 C',
             fontsize=9, color='#00ff88', fontweight='bold')

ax7.set_xlabel('Time (seconds)', color='white', fontsize=10)
ax7.set_ylabel('Temperature (C)', color='#ff8844', fontsize=10)
ax7b.set_ylabel('Heater Power (mW)', color='#FFD700', fontsize=10)
ax7.legend(fontsize=8, loc='center right', facecolor='#1a1a2e', edgecolor='#444',
           labelcolor='white')
ax7.tick_params(colors='gray')
ax7b.tick_params(colors='gray')
ax7.grid(True, alpha=0.1, color='gray')
for sp in ax7.spines.values():
    sp.set_edgecolor('#333')
for sp in ax7b.spines.values():
    sp.set_edgecolor('#333')


# ======================================================================
# PANEL 8: DISTURBANCE REJECTION -- External temp shock
# ======================================================================
ax8 = fig.add_subplot(gs[2, 1], facecolor='#0a0a1a')
ax8.set_title('8. DISTURBANCE REJECTION: -20 C Cold Shock', color='#ffaa00',
              fontsize=12, fontweight='bold')

# Start at steady state, then external temp drops suddenly
t_end2 = 30.0
t_sim2 = np.arange(0, t_end2, dt)
T_cell2 = np.zeros(len(t_sim2))
P_heater2 = np.zeros(len(t_sim2))
T_ext2 = np.zeros(len(t_sim2))
T_cell2[0] = T_setpoint
integral_err2 = (T_setpoint - T_ambient) / (Ki * P_max) * C_thermal * 0.1  # pre-loaded

prev_err2 = 0

for i in range(1, len(t_sim2)):
    # External temperature: drops from 25 to 5 C at t=5s
    if t_sim2[i] < 5:
        T_ext2[i] = 25.0
    elif t_sim2[i] < 6:
        T_ext2[i] = 25.0 - 20.0 * (t_sim2[i] - 5.0)  # ramp down
    else:
        T_ext2[i] = 5.0

    err = T_setpoint - T_cell2[i-1]
    integral_err2 += err * dt
    integral_err2 = np.clip(integral_err2, -50, 50)
    d_err = (err - prev_err2) / dt

    u = Kp * err + Ki * integral_err2 + Kd * d_err
    u = np.clip(u, 0, 1)
    P_heat = u * P_max

    P_loss = (T_cell2[i-1] - T_ext2[i]) / R_thermal
    dT = (P_heat - P_loss) / C_thermal * dt
    T_cell2[i] = T_cell2[i-1] + dT
    P_heater2[i] = P_heat * 1000
    prev_err2 = err

ax8.plot(t_sim2, T_cell2, color='#ff8844', linewidth=2.5, label='Cell Temperature')
ax8.plot(t_sim2, T_ext2, color='#44aaff', linewidth=1.5, linestyle=':', label='External Temp')
ax8.axhline(T_setpoint, color='#00ff88', linestyle='--', alpha=0.5)

# Zoom inset showing the dip
axins2 = ax8.inset_axes([0.55, 0.10, 0.42, 0.42])
axins2.set_facecolor('#111133')
mask2 = (t_sim2 > 4) & (t_sim2 < 15)
axins2.plot(t_sim2[mask2], T_cell2[mask2], color='#ff8844', linewidth=2)
axins2.axhline(T_setpoint, color='#00ff88', linestyle='--', alpha=0.7)
axins2.axhline(T_setpoint - 0.1, color='white', linestyle=':', alpha=0.3)
axins2.axhline(T_setpoint + 0.1, color='white', linestyle=':', alpha=0.3)
axins2.set_title('Zoom: Recovery Detail', fontsize=7, color='white')
axins2.tick_params(colors='gray', labelsize=5)
for sp in axins2.spines.values():
    sp.set_edgecolor('#444')

# Shock marker
ax8.annotate('COLD SHOCK!\nExternal: 25 C -> 5 C',
             xy=(5.5, T_ext2[int(5.5/dt)]), xytext=(8, 35),
             fontsize=9, color='#ff4444', fontweight='bold',
             arrowprops=dict(arrowstyle='->', color='#ff4444', lw=2))

# Recovery annotation
dip = T_cell2.min()
ax8.text(15, 70, f'Max dip: {T_setpoint - dip:.2f} C\n'
         f'The vacuum insulation +\nPID feedback absorb\nthe shock!',
         fontsize=8, color='#00ff88',
         bbox=dict(boxstyle='round,pad=0.3', facecolor='#0a1a0a', edgecolor='#00ff88'))

ax8.set_xlabel('Time (seconds)', color='white', fontsize=10)
ax8.set_ylabel('Temperature (C)', color='white', fontsize=10)
ax8.legend(fontsize=8, loc='lower left', facecolor='#1a1a2e', edgecolor='#444',
           labelcolor='white')
ax8.tick_params(colors='gray')
ax8.grid(True, alpha=0.1, color='gray')
for sp in ax8.spines.values():
    sp.set_edgecolor('#333')


# ======================================================================
# PANEL 9: STEADY-STATE POWER BUDGET
# ======================================================================
ax9 = fig.add_subplot(gs[2, 2], facecolor='#0a0a1a')
ax9.set_title('9. POWER BUDGET: Where the mW Go', color='#ffaa00',
              fontsize=13, fontweight='bold')

# Typical CSAC power budget (~120 mW total)
components = ['Heater\n(maintain 85C)', 'VCSEL\nLaser', 'Electronics\n(PID, LO, etc.)',
              'Photodetector', 'Modulator\nDriver']
powers = [55, 15, 35, 5, 10]  # mW
colors_pie = ['#FFD700', '#ff4444', '#aa44ff', '#44ff44', '#ff8844']
explode = [0.1, 0, 0, 0, 0]  # explode the heater slice

wedges, texts, autotexts = ax9.pie(
    powers, labels=components, colors=colors_pie, explode=explode,
    autopct='%1.0f%%', startangle=90, textprops={'fontsize': 8, 'color': 'white'},
    pctdistance=0.75, labeldistance=1.15
)
for at in autotexts:
    at.set_fontsize(9)
    at.set_fontweight('bold')
    at.set_color('white')

ax9.text(0, -1.6,
    'The HEATER is the biggest power consumer!\n'
    '~55 mW just to keep 85 C in vacuum package.\n'
    'Total CSAC: ~120 mW (tiny for atomic clock).\n'
    'Vacuum insulation is key -- without it,\n'
    'heater would need >1 W.',
    ha='center', fontsize=9, color='#FFD700',
    bbox=dict(boxstyle='round,pad=0.4', facecolor='#1a1a0a', edgecolor='#FFD700'))


# ======================================================================
# PANEL 10: 3D THERMAL GRADIENT ACROSS THE CELL
# ======================================================================
ax10 = fig.add_subplot(gs[3, 0], projection='3d', facecolor='#0a0a1a')
ax10.set_title('10. 3D TEMPERATURE GRADIENT (Dual-Zone Heater)',
               color='#00ccff', fontsize=11, fontweight='bold', pad=12)

res = 60
xg = np.linspace(-1, 1, res)
yg = np.linspace(-1, 1, res)
X, Y = np.meshgrid(xg, yg)
R = np.sqrt(X**2 + Y**2)

# Dual-zone heater: inner zone (fine) + outer zone (guard)
T_inner = 2.5 * np.exp(-R**2 / 0.3)  # inner heater focused on cavity
T_outer = 1.0 * np.exp(-(R - 0.7)**2 / 0.2)  # outer guard ring
T_profile = T_ambient + (T_setpoint - T_ambient) + T_inner + T_outer
# Slight gradient from imperfect compensation
T_profile += 0.3 * X * Y  # asymmetry

hot_cmap = LinearSegmentedColormap.from_list('hot_c2',
    ['#000066', '#0044aa', '#ff4400', '#ffaa00', '#ffffff'], N=256)

surf = ax10.plot_surface(X, Y, T_profile, cmap=hot_cmap, alpha=0.85,
                          edgecolor='none', antialiased=True)
fig.colorbar(surf, ax=ax10, shrink=0.4, aspect=12, pad=0.08, label='T (C)')

ax10.set_xlabel('X (mm)', color='gray', fontsize=6)
ax10.set_ylabel('Y (mm)', color='gray', fontsize=6)
ax10.set_zlabel('T (C)', color='gray', fontsize=6)
ax10.set_zlim(83, 90)
ax10.tick_params(colors='gray', labelsize=5)
for pane in [ax10.xaxis.pane, ax10.yaxis.pane, ax10.zaxis.pane]:
    pane.fill = False
    pane.set_edgecolor('#333')
ax10.view_init(elev=25, azim=-50)

ax10.text2D(0.02, 0.88,
    'Inner heater: sharp peak at cavity\n'
    'Outer guard: flattens gradients\n'
    'Goal: <0.1 C variation across cavity',
    transform=ax10.transAxes, fontsize=7, color='#ffaa00',
    bbox=dict(boxstyle='round,pad=0.3', facecolor='#1a1a2e', edgecolor='#444'))


# ======================================================================
# PANEL 11: Pt RTD SENSOR CALIBRATION
# ======================================================================
ax11 = fig.add_subplot(gs[3, 1], facecolor='#0a0a1a')
ax11.set_title('11. HOW THE SENSOR READS TEMPERATURE',
               color='#00ccff', fontsize=12, fontweight='bold')

# Pt RTD: R(T) = R0 * (1 + alpha*T + beta*T^2)
R0 = 1000  # Ohms at 0C (typical Pt1000)
alpha_pt = 3.908e-3  # 1/C
beta_pt = -5.775e-7  # 1/C^2
T_range = np.linspace(-40, 150, 400)
R_pt = R0 * (1 + alpha_pt * T_range + beta_pt * T_range**2)

ax11.plot(T_range, R_pt, color='#ff8844', linewidth=2.5)

# Mark the operating point
R_at_85 = R0 * (1 + alpha_pt * 85 + beta_pt * 85**2)
ax11.plot(85, R_at_85, 'o', color='#00ff88', markersize=12, zorder=5)
ax11.annotate(f'At 85 C:\nR = {R_at_85:.1f} ohm\n\nMeasure R -> know T\nto +/- 0.01 C precision',
              xy=(85, R_at_85), xytext=(100, 1100),
              fontsize=9, color='#00ff88',
              arrowprops=dict(arrowstyle='->', color='#00ff88', lw=1.5),
              bbox=dict(boxstyle='round,pad=0.3', facecolor='#0a1a0a', edgecolor='#00ff88'))

ax11.axvspan(83, 87, alpha=0.12, color='#00ff88')

ax11.text(0, 1400,
    'Platinum RTD: Resistance\n'
    'increases linearly with T.\n'
    'R(T) = R0*(1 + aT + bT2)\n'
    'Extremely stable + repeatable.\n'
    'Same Pt used for heater!',
    fontsize=8, color='#aaaaaa',
    bbox=dict(boxstyle='round,pad=0.4', facecolor='#111133', edgecolor='#444'))

ax11.set_xlabel('Temperature (C)', color='white', fontsize=10)
ax11.set_ylabel('Resistance (Ohm)', color='white', fontsize=10)
ax11.grid(True, alpha=0.15, color='gray')
ax11.tick_params(colors='gray')
for sp in ax11.spines.values():
    sp.set_edgecolor('#333')


# ======================================================================
# PANEL 12: SUMMARY -- The full thermal story
# ======================================================================
ax12 = fig.add_subplot(gs[3, 2], facecolor='#0a0a1a')
ax12.set_title('12. THE COMPLETE THERMAL STORY', color='#00ccff',
               fontsize=13, fontweight='bold')

summary_text = """
WHY 85 C?
Rb needs enough vapor pressure to
absorb light, but not so much that
collisions blur the atomic signal.
85 C is the sweet spot.

HOW IS HEAT GENERATED?
Thin-film Pt heaters (~200 nm thick)
deposited directly on the Si body.
Current flows through serpentine
traces: P = I2R = ~55 mW.

HOW IS HEAT KEPT IN?
The entire MEMS cell sits inside
a VACUUM PACKAGE. Vacuum kills
conduction + convection. Only
radiation leaks out. Thin Si
suspension beams minimize
conduction to the package walls.

HOW IS TEMPERATURE MEASURED?
A Pt RTD (resistance temperature
detector) on the same die.
R increases linearly with T.
Precision: +/- 0.01 C.

HOW IS IT CONTROLLED?
PID feedback loop running at ~kHz:
1. RTD measures T
2. Compare to 85.000 C setpoint
3. PID computes heater duty cycle
4. PWM drives heater current
5. Repeat 1000x per second

DUAL-ZONE DESIGN:
Inner heater: fine control at cavity
Outer guard: equalizes gradients
Result: <0.1 C uniformity across
the Rb vapor cavity.
"""

ax12.text(0.05, 0.95, summary_text, transform=ax12.transAxes,
          fontsize=8.5, color='white', fontfamily='monospace',
          verticalalignment='top',
          bbox=dict(boxstyle='round,pad=0.5', facecolor='#111133',
                    edgecolor='#00ccff', linewidth=1.5))
ax12.axis('off')


# ──────────────────────────────────────────────────────────────────────
# SAVE
# ──────────────────────────────────────────────────────────────────────
plt.savefig('csac_thermal_simulation.png', dpi=160, facecolor=fig.get_facecolor(),
            bbox_inches='tight')
plt.show()

print("\nSaved to csac_thermal_simulation.png")
