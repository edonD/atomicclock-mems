"""
3D Educational Simulation: How a Chip-Scale Atomic Clock (CSAC) Enables GPS-Denied Navigation

Core idea: GPS satellites are just atomic clocks in the sky. Each satellite broadcasts
its time signal. Your receiver compares arrival times from 4+ satellites to triangulate
your position. When GPS is jammed/spoofed/denied, you lose those external clocks.
A CSAC gives you a LOCAL atomic clock so you can keep navigating without GPS.

Time error -> Position error:  1 microsecond of clock drift = ~300 meters of position error
(because signals travel at the speed of light: 3e8 m/s * 1e-6 s = 300 m)
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from matplotlib import cm
from matplotlib.colors import LinearSegmentedColormap
from mpl_toolkits.mplot3d import art3d
import matplotlib.patches as mpatches

# ──────────────────────────────────────────────────────────────────────────────
# CONFIG
# ──────────────────────────────────────────────────────────────────────────────
CELL_WIDTH  = 2.0    # mm
SI_THICK    = 1.0    # mm
CAVITY_FRAC = 0.65
CELL_TEMP   = 85     # deg C
N_ATOMS     = 140
RB_HYPERFINE = 6.834682610  # GHz
C_LIGHT = 299792458  # m/s


def draw_box(ax, origin, size, color, alpha=0.25, edgecolor='k', linewidth=0.5):
    x0, y0, z0 = origin
    dx, dy, dz = size
    faces = [
        [[x0,y0,z0],[x0+dx,y0,z0],[x0+dx,y0+dy,z0],[x0,y0+dy,z0]],
        [[x0,y0,z0+dz],[x0+dx,y0,z0+dz],[x0+dx,y0+dy,z0+dz],[x0,y0+dy,z0+dz]],
        [[x0,y0,z0],[x0+dx,y0,z0],[x0+dx,y0,z0+dz],[x0,y0,z0+dz]],
        [[x0,y0+dy,z0],[x0+dx,y0+dy,z0],[x0+dx,y0+dy,z0+dz],[x0,y0+dy,z0+dz]],
        [[x0,y0,z0],[x0,y0+dy,z0],[x0,y0+dy,z0+dz],[x0,y0,z0+dz]],
        [[x0+dx,y0,z0],[x0+dx,y0+dy,z0],[x0+dx,y0+dy,z0+dz],[x0+dx,y0,z0+dz]],
    ]
    poly = art3d.Poly3DCollection(faces, alpha=alpha, facecolor=color,
                                   edgecolor=edgecolor, linewidth=linewidth)
    ax.add_collection3d(poly)


# ──────────────────────────────────────────────────────────────────────────────
# FIGURE
# ──────────────────────────────────────────────────────────────────────────────
fig = plt.figure(figsize=(22, 28), facecolor='#0a0a1a')
fig.suptitle(
    'HOW A CHIP-SCALE ATOMIC CLOCK REPLACES GPS\n'
    'From Quantum Physics to Battlefield Navigation',
    fontsize=18, fontweight='bold', color='white', y=0.99
)

gs = GridSpec(4, 3, figure=fig, hspace=0.32, wspace=0.30,
              left=0.05, right=0.95, top=0.96, bottom=0.03)


# ======================================================================
# ROW 1, PANEL 1: WHY GPS NEEDS CLOCKS (the fundamental link)
# ======================================================================
ax_why = fig.add_subplot(gs[0, 0], facecolor='#0a0a1a')
ax_why.set_title('1. WHY GPS IS REALLY ABOUT CLOCKS', color='#00ccff',
                 fontsize=12, fontweight='bold')

# Draw Earth, satellites, and timing signals
theta_earth = np.linspace(0, 2*np.pi, 100)
# Earth
ax_why.fill(1.8*np.cos(theta_earth), 1.8*np.sin(theta_earth),
            color='#114488', alpha=0.3)
ax_why.plot(1.8*np.cos(theta_earth), 1.8*np.sin(theta_earth),
            color='#2266aa', linewidth=2)
ax_why.text(0, 0, 'EARTH', ha='center', va='center', fontsize=8,
            color='#4488cc', fontweight='bold')

# Receiver on surface
rx, ry = 1.2, 1.2
ax_why.plot(rx, ry, 's', color='#00ff88', markersize=12, zorder=5)
ax_why.text(rx+0.3, ry+0.1, 'YOU\n(receiver)', fontsize=8, color='#00ff88',
            fontweight='bold')

# Satellites
sat_positions = [(4.0, 3.5), (-3.5, 4.0), (-4.5, -1.5), (3.0, -3.8)]
sat_labels = ['SAT 1\nt=12:00:00.000000001',
              'SAT 2\nt=12:00:00.000000003',
              'SAT 3\nt=12:00:00.000000007',
              'SAT 4\nt=12:00:00.000000002']
for (sx, sy), lab in zip(sat_positions, sat_labels):
    ax_why.plot(sx, sy, '*', color='#FFD700', markersize=15, zorder=5)
    ax_why.text(sx, sy+0.5, lab, ha='center', fontsize=6, color='#FFD700')
    # Signal line
    ax_why.annotate('', xy=(rx, ry), xytext=(sx, sy),
                    arrowprops=dict(arrowstyle='->', color='#ff4444',
                                    lw=1.2, linestyle='--', alpha=0.6))

# Explanation box
ax_why.text(0, -4.8,
    'Each satellite has an ATOMIC CLOCK and\n'
    'broadcasts its exact time. Your receiver\n'
    'measures the ARRIVAL TIME DIFFERENCE\n'
    'between signals. Since signals travel at\n'
    'the speed of light, time delay = distance.\n'
    '4 satellites = 3D position + time sync.',
    ha='center', va='top', fontsize=8, color='white',
    bbox=dict(boxstyle='round,pad=0.5', facecolor='#111133', edgecolor='#444'))

ax_why.set_xlim(-6, 6)
ax_why.set_ylim(-6, 5)
ax_why.axis('off')


# ======================================================================
# ROW 1, PANEL 2: WHAT HAPPENS WHEN GPS IS DENIED
# ======================================================================
ax_denied = fig.add_subplot(gs[0, 1], facecolor='#0a0a1a')
ax_denied.set_title('2. GPS-DENIED: THE PROBLEM', color='#ff4444',
                    fontsize=12, fontweight='bold')

# Earth
ax_denied.fill(1.8*np.cos(theta_earth), 1.8*np.sin(theta_earth),
               color='#441111', alpha=0.3)
ax_denied.plot(1.8*np.cos(theta_earth), 1.8*np.sin(theta_earth),
               color='#662222', linewidth=2)

# Receiver
ax_denied.plot(rx, ry, 's', color='#ff4444', markersize=12, zorder=5)
ax_denied.text(rx+0.3, ry+0.1, 'YOU\n(LOST!)', fontsize=8, color='#ff4444',
               fontweight='bold')

# Jammed satellites
for (sx, sy) in sat_positions:
    ax_denied.plot(sx, sy, '*', color='#666666', markersize=15, zorder=5)
    # Crossed out signal
    mid_x, mid_y = (sx + rx)/2, (sy + ry)/2
    ax_denied.plot([sx, rx], [sy, ry], color='#ff0000', lw=1, alpha=0.3, linestyle='--')
    ax_denied.text(mid_x, mid_y, 'X', fontsize=14, color='#ff0000',
                   ha='center', va='center', fontweight='bold')

# Jammer
ax_denied.plot(0, -2.5, '^', color='#ff0000', markersize=20, zorder=5)
ax_denied.text(0, -3.0, 'JAMMER', ha='center', fontsize=9, color='#ff0000',
               fontweight='bold')
# Jamming waves
for r_jam in [0.8, 1.6, 2.5]:
    jam_theta = np.linspace(0, 2*np.pi, 60)
    ax_denied.plot(r_jam*np.cos(jam_theta), r_jam*np.sin(jam_theta) - 2.5,
                   color='#ff0000', alpha=0.15, linewidth=1)

ax_denied.text(0, -4.8,
    'Enemy JAMS or SPOOFS GPS signals.\n'
    'Without satellite clocks, your quartz\n'
    'oscillator drifts rapidly:\n\n'
    '  Quartz: ~1 us/hour = 300 m/hr error\n'
    '  After 4 hours: ~1.2 km off target!\n\n'
    'Missiles miss. Troops get lost. Drones crash.',
    ha='center', va='top', fontsize=8, color='#ff6666',
    bbox=dict(boxstyle='round,pad=0.5', facecolor='#1a0a0a', edgecolor='#662222'))

ax_denied.set_xlim(-6, 6)
ax_denied.set_ylim(-6, 5)
ax_denied.axis('off')


# ======================================================================
# ROW 1, PANEL 3: THE CSAC SOLUTION
# ======================================================================
ax_sol = fig.add_subplot(gs[0, 2], facecolor='#0a0a1a')
ax_sol.set_title('3. THE SOLUTION: CARRY YOUR OWN ATOMIC CLOCK', color='#00ff88',
                 fontsize=12, fontweight='bold')

# Earth
ax_sol.fill(1.8*np.cos(theta_earth), 1.8*np.sin(theta_earth),
            color='#114422', alpha=0.3)
ax_sol.plot(1.8*np.cos(theta_earth), 1.8*np.sin(theta_earth),
            color='#226644', linewidth=2)

# Receiver with CSAC
ax_sol.plot(rx, ry, 's', color='#00ff88', markersize=12, zorder=5)
ax_sol.text(rx+0.3, ry+0.1, 'YOU\n+ CSAC', fontsize=8, color='#00ff88',
            fontweight='bold')

# CSAC chip on the soldier
csac_rect = plt.Rectangle((rx-0.6, ry-0.9), 1.2, 0.6, fill=True,
                            facecolor='#003322', edgecolor='#00ff88', linewidth=2)
ax_sol.add_patch(csac_rect)
ax_sol.text(rx, ry-0.6, 'CSAC\nChip', ha='center', va='center',
            fontsize=7, color='#00ff88', fontweight='bold')

# Show holdover navigation
waypoints = [(rx, ry), (0, 2.5), (-2, 1), (-3.5, -1)]
for i in range(len(waypoints)-1):
    x1, y1 = waypoints[i]
    x2, y2 = waypoints[i+1]
    ax_sol.annotate('', xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle='->', color='#00ff88',
                                    lw=2.5, alpha=0.7))
    ax_sol.plot(x2, y2, 'o', color='#00ff88', markersize=6, zorder=5)

ax_sol.text(-3.5, -1.6, 'Mission\ncomplete!', ha='center', fontsize=8,
            color='#00ff88', fontweight='bold')

# Still jammed
ax_sol.plot(0, -2.5, '^', color='#ff0000', markersize=15, zorder=5, alpha=0.4)
ax_sol.text(0, -3.0, 'jammer\n(still active)', ha='center', fontsize=7,
            color='#ff4444', alpha=0.5)

ax_sol.text(0, -4.8,
    'A CSAC gives you an ATOMIC CLOCK\n'
    'the size of a postage stamp (~16 cm3).\n'
    'It drifts only ~0.3 us/day vs 1 us/hour\n'
    'for quartz. That means:\n\n'
    '  CSAC: ~100 m error after 8 HOURS\n'
    '  Quartz: ~2.4 km error after 8 hours\n\n'
    'Navigate for hours without GPS!',
    ha='center', va='top', fontsize=8, color='#88ffaa',
    bbox=dict(boxstyle='round,pad=0.5', facecolor='#0a1a0a', edgecolor='#224422'))

ax_sol.set_xlim(-6, 6)
ax_sol.set_ylim(-6, 5)
ax_sol.axis('off')


# ======================================================================
# ROW 2, PANEL 4: 3D EXPLODED VIEW OF THE CSAC CORE
# ======================================================================
ax_chip = fig.add_subplot(gs[1, 0], projection='3d', facecolor='#0a0a1a')
ax_chip.set_title('4. INSIDE THE CSAC CHIP (Exploded View)', color='#ffaa00',
                  fontsize=12, fontweight='bold', pad=12)

gap = 0.55
cx, cy = -CELL_WIDTH/2, -CELL_WIDTH/2
z = 0

layers_info = [
    (0.20, '#ff4444', 'VCSEL Laser (795 nm)\nEmits modulated light', 0.75),
    (0.15, '#cc44ff', 'Quarter-Wave Plate\nMakes light circularly polarized', 0.55),
    (0.30, '#44aaff', 'Bottom Glass Window\nSeals the cell (anodic bond)', 0.35),
    (1.00, '#888888', 'Silicon Body (MEMS etched)\nContains Rb atoms + N2 gas', 0.45),
    (0.30, '#44aaff', 'Top Glass Window\nSeals the cell (anodic bond)', 0.35),
    (0.15, '#44ff44', 'Photodetector\nMeasures transmitted light', 0.75),
]

z_positions = []
for thick, col, label, alpha in layers_info:
    draw_box(ax_chip, (cx, cy, z), (CELL_WIDTH, CELL_WIDTH, thick),
             col, alpha=alpha, edgecolor='white', linewidth=0.7)
    ax_chip.text(cx + CELL_WIDTH + 0.2, cy + CELL_WIDTH/2, z + thick/2,
                 label, fontsize=6.5, color='white', ha='left', va='center')
    z_positions.append(z)
    z += thick + gap

# Laser beam through center
bz = np.linspace(-0.4, z + 0.3, 80)
ax_chip.plot(np.zeros(80), np.zeros(80), bz,
             color='red', alpha=0.5, linewidth=3, linestyle='--')
ax_chip.scatter([0], [0], [-0.4], color='red', s=50, marker='^', zorder=10)
ax_chip.scatter([0], [0], [z+0.3], color='lime', s=50, marker='v', zorder=10)

# Heater traces on silicon
theta_h = np.linspace(0, 4*np.pi, 100)
r_h = 0.25 + 0.15 * theta_h / (4*np.pi)
si_z = z_positions[3]
ax_chip.plot(r_h*np.cos(theta_h), r_h*np.sin(theta_h),
             np.full(100, si_z + 1.01),
             color='#FFD700', linewidth=1.5, alpha=0.8)
ax_chip.text(0.9, 0.9, si_z + 1.05, 'Pt Heater', fontsize=5.5, color='#FFD700')

ax_chip.set_xlim(-2, 4.5)
ax_chip.set_ylim(-2, 2)
ax_chip.set_zlim(-0.5, z + 0.8)
ax_chip.set_xlabel('X (mm)', color='gray', fontsize=6)
ax_chip.set_ylabel('Y (mm)', color='gray', fontsize=6)
ax_chip.set_zlabel('Z (mm)', color='gray', fontsize=6)
ax_chip.tick_params(colors='gray', labelsize=5)
for pane in [ax_chip.xaxis.pane, ax_chip.yaxis.pane, ax_chip.zaxis.pane]:
    pane.fill = False
    pane.set_edgecolor('#333')
ax_chip.view_init(elev=20, azim=-52)


# ======================================================================
# ROW 2, PANEL 5: QUANTUM PHYSICS — CPT ENERGY LEVELS
# ======================================================================
ax_qm = fig.add_subplot(gs[1, 1], facecolor='#0a0a1a')
ax_qm.set_title('5. THE QUANTUM TRICK: Coherent Population Trapping',
                color='#ffaa00', fontsize=11, fontweight='bold')

# Energy levels
e1, e2, e3 = 0.0, 0.6, 3.5

# Ground states
ax_qm.plot([1, 3], [e1, e1], color='#44aaff', linewidth=3.5)
ax_qm.plot([5, 7], [e2, e2], color='#44aaff', linewidth=3.5)
# Excited
ax_qm.plot([2.5, 5.5], [e3, e3], color='#ff8844', linewidth=3.5)

# Labels
ax_qm.text(2, e1-0.4, '|1> = F=1 ground state', ha='center', fontsize=9,
            color='#44aaff', fontweight='bold')
ax_qm.text(6, e2-0.4, '|2> = F=2 ground state', ha='center', fontsize=9,
            color='#44aaff', fontweight='bold')
ax_qm.text(4, e3+0.25, '|3> = Excited state (5P1/2)', ha='center', fontsize=10,
            color='#ff8844', fontweight='bold')

# Laser arrows
ax_qm.annotate('', xy=(3.0, e3-0.08), xytext=(2.0, e1+0.08),
                arrowprops=dict(arrowstyle='->', color='#ff3333', lw=3))
ax_qm.text(1.5, 1.8, 'Laser\nfield 1', fontsize=9, color='#ff5555', fontweight='bold')

ax_qm.annotate('', xy=(5.0, e3-0.08), xytext=(6.0, e2+0.08),
                arrowprops=dict(arrowstyle='->', color='#ff3333', lw=3))
ax_qm.text(6.3, 2.0, 'Laser\nfield 2', fontsize=9, color='#ff5555', fontweight='bold')

# Hyperfine splitting
ax_qm.annotate('', xy=(8.2, e2), xytext=(8.2, e1),
                arrowprops=dict(arrowstyle='<->', color='yellow', lw=2))
ax_qm.text(8.5, 0.3, '6.835\nGHz', ha='left', va='center', fontsize=10,
            color='yellow', fontweight='bold')

# THE KEY INSIGHT - dark state
ax_qm.text(4.0, -1.3,
    'THE KEY INSIGHT:\n'
    'When the two laser fields are separated by\n'
    'EXACTLY 6.835 GHz, the atom enters a quantum\n'
    '"DARK STATE" -- a superposition of |1> and |2>\n'
    'that CANNOT absorb light. The atom becomes\n'
    'transparent! Detect this transparency peak\n'
    'to lock your oscillator to the atomic frequency.',
    ha='center', va='top', fontsize=8.5, color='#00ff88', fontweight='bold',
    bbox=dict(boxstyle='round,pad=0.5', facecolor='#0a1a0a', edgecolor='#00ff88',
              linewidth=1.5))

# Dark state arrow
ax_qm.annotate('DARK\nSTATE', xy=(4.0, 0.3), xytext=(4.0, -0.3),
                ha='center', fontsize=10, color='#00ff88', fontweight='bold',
                arrowprops=dict(arrowstyle='->', color='#00ff88', lw=2))

ax_qm.set_xlim(-0.5, 10)
ax_qm.set_ylim(-3.5, 4.5)
ax_qm.axis('off')


# ======================================================================
# ROW 2, PANEL 6: 3D VAPOR CELL INTERIOR
# ======================================================================
ax_cell = fig.add_subplot(gs[1, 2], projection='3d', facecolor='#0a0a1a')
ax_cell.set_title('6. INSIDE THE VAPOR CELL (Rb Atoms + Laser Beam)',
                  color='#ffaa00', fontsize=11, fontweight='bold', pad=10)

cell_half = CELL_WIDTH * CAVITY_FRAC / 2
draw_box(ax_cell, (-cell_half, -cell_half, 0), (2*cell_half, 2*cell_half, SI_THICK),
         '#4488aa', alpha=0.07, edgecolor='#4488aa', linewidth=0.8)

np.random.seed(42)
ax_ = np.random.uniform(-cell_half*0.88, cell_half*0.88, N_ATOMS)
ay_ = np.random.uniform(-cell_half*0.88, cell_half*0.88, N_ATOMS)
az_ = np.random.uniform(0.04, SI_THICK-0.04, N_ATOMS)

dist = np.sqrt(ax_**2 + ay_**2)
colors_atoms = []
for d in dist:
    if d < 0.15:
        colors_atoms.append('#00ff88')  # dark state (near beam)
    elif d < 0.3:
        colors_atoms.append('#88ff88')  # partially dark
    else:
        colors_atoms.append('#ff4444')  # absorbing

ax_cell.scatter(ax_, ay_, az_, c=colors_atoms, s=22, alpha=0.7, edgecolors='none')

# Laser beam
bz_line = np.linspace(-0.3, SI_THICK+0.3, 60)
ax_cell.plot(np.zeros(60), np.zeros(60), bz_line, color='red', alpha=0.6, linewidth=4)
for zring in [0.0, 0.33, 0.66, 1.0]:
    w = 0.06 + 0.02*zring
    th = np.linspace(0, 2*np.pi, 40)
    ax_cell.plot(w*np.cos(th), w*np.sin(th), np.full(40, zring),
                 color='red', alpha=0.25, linewidth=0.8)

# N2 buffer gas
n2x = np.random.uniform(-cell_half*0.85, cell_half*0.85, 35)
n2y = np.random.uniform(-cell_half*0.85, cell_half*0.85, 35)
n2z = np.random.uniform(0.05, SI_THICK-0.05, 35)
ax_cell.scatter(n2x, n2y, n2z, c='#6666ff', s=6, alpha=0.25, marker='o')

# Legend
ax_cell.scatter([], [], [], c='#00ff88', s=40, label='Rb: dark state (transparent)')
ax_cell.scatter([], [], [], c='#ff4444', s=40, label='Rb: absorbing photons')
ax_cell.scatter([], [], [], c='#6666ff', s=15, label='N2 buffer gas')
ax_cell.plot([], [], [], c='red', lw=3, label='795 nm laser beam')
ax_cell.legend(loc='upper left', fontsize=6.5, facecolor='#1a1a2e', edgecolor='#444',
               labelcolor='white', framealpha=0.9)

ax_cell.set_xlim(-0.9, 0.9)
ax_cell.set_ylim(-0.9, 0.9)
ax_cell.set_zlim(-0.4, 1.4)
ax_cell.set_xlabel('X (mm)', color='gray', fontsize=6)
ax_cell.set_ylabel('Y (mm)', color='gray', fontsize=6)
ax_cell.set_zlabel('Z (mm)', color='gray', fontsize=6)
ax_cell.tick_params(colors='gray', labelsize=5)
for pane in [ax_cell.xaxis.pane, ax_cell.yaxis.pane, ax_cell.zaxis.pane]:
    pane.fill = False
    pane.set_edgecolor('#333')
ax_cell.view_init(elev=20, azim=-40)


# ======================================================================
# ROW 3, PANEL 7: CPT SIGNAL — what the photodetector sees
# ======================================================================
ax_cpt = fig.add_subplot(gs[2, 0], facecolor='#0a0a1a')
ax_cpt.set_title('7. CPT SIGNAL: How You Lock to the Atom',
                 color='#00ccff', fontsize=12, fontweight='bold')

delta = np.linspace(-400, 400, 3000)  # kHz detuning
doppler_w = 200
bg = 1.0 - 0.30 * np.exp(-delta**2 / (2*doppler_w**2))
cpt_w = 2.5
cpt_h = 0.22
signal = bg + cpt_h * np.exp(-delta**2 / (2*cpt_w**2))

ax_cpt.fill_between(delta, 0.6, bg, alpha=0.1, color='#ff4444')
ax_cpt.plot(delta, bg, color='#ff4444', alpha=0.4, linewidth=1, label='Rb absorption dip')
ax_cpt.plot(delta, signal, color='#00ff88', linewidth=2.5, label='CPT transparency peak')
ax_cpt.axvline(0, color='yellow', linestyle=':', alpha=0.5, linewidth=1)

# Zoom inset
axins = ax_cpt.inset_axes([0.60, 0.50, 0.36, 0.42])
axins.set_facecolor('#111133')
mask = np.abs(delta) < 15
axins.plot(delta[mask], signal[mask], color='#00ff88', linewidth=2.5)
axins.fill_between(delta[mask], 0.9, signal[mask], alpha=0.2, color='#00ff88')
axins.axvline(0, color='yellow', linestyle=':', alpha=0.7)
axins.set_title('Zoom: The Peak', fontsize=7, color='white')
axins.tick_params(colors='gray', labelsize=5)
axins.set_xlabel('kHz', fontsize=6, color='gray')
for sp in axins.spines.values():
    sp.set_edgecolor('#444')

# Teaching annotation
ax_cpt.annotate(
    'THIS PEAK is your atomic reference!\n'
    'Width ~3 kHz, contrast ~22%\n'
    'Feedback loop keeps oscillator\n'
    'locked to the peak center.',
    xy=(0, signal[1500]), xytext=(160, 1.08),
    fontsize=8, color='#00ff88', fontweight='bold',
    arrowprops=dict(arrowstyle='->', color='#00ff88', lw=1.5))

ax_cpt.set_xlabel('Detuning from 6.835 GHz (kHz)', color='white', fontsize=9)
ax_cpt.set_ylabel('Transmitted Light (a.u.)', color='white', fontsize=9)
ax_cpt.legend(fontsize=8, facecolor='#1a1a2e', edgecolor='#444',
              labelcolor='white', loc='lower left')
ax_cpt.tick_params(colors='gray')
ax_cpt.set_ylim(0.6, 1.15)
for sp in ax_cpt.spines.values():
    sp.set_edgecolor('#333')


# ======================================================================
# ROW 3, PANEL 8: FEEDBACK LOOP BLOCK DIAGRAM
# ======================================================================
ax_loop = fig.add_subplot(gs[2, 1], facecolor='#0a0a1a')
ax_loop.set_title('8. FEEDBACK LOOP: Locking to the Atom',
                  color='#00ccff', fontsize=12, fontweight='bold')

# Block diagram of the CSAC control loop
blocks = [
    (1.0, 4.0, 'Local\nOscillator\n(3.417 GHz)',  '#ff8844'),
    (1.0, 2.5, 'VCSEL\nLaser\n(795 nm)',           '#ff4444'),
    (4.0, 2.5, 'Rb Vapor\nCell\n(85 C)',            '#4488aa'),
    (7.0, 2.5, 'Photo-\ndetector',                  '#44ff44'),
    (7.0, 4.0, 'Lock-in\nAmplifier',                '#ffaa00'),
    (4.0, 4.0, 'PID\nController',                   '#aa44ff'),
]

for bx, by, txt, col in blocks:
    rect = plt.Rectangle((bx-0.8, by-0.5), 1.6, 1.0, fill=True,
                          facecolor=col, edgecolor='white', linewidth=1.5,
                          alpha=0.3)
    ax_loop.add_patch(rect)
    ax_loop.text(bx, by, txt, ha='center', va='center', fontsize=7.5,
                 color='white', fontweight='bold')

# Arrows connecting blocks
arrows = [
    ((1.0, 3.5), (1.0, 3.0)),     # LO -> VCSEL
    ((1.8, 2.5), (3.2, 2.5)),     # VCSEL -> Cell
    ((4.8, 2.5), (6.2, 2.5)),     # Cell -> PD
    ((7.0, 3.0), (7.0, 3.5)),     # PD -> Lock-in
    ((6.2, 4.0), (4.8, 4.0)),     # Lock-in -> PID
    ((3.2, 4.0), (1.8, 4.0)),     # PID -> LO
]
arrow_labels = ['modulates', '795nm light', 'transmitted\nlight',
                'signal', 'error signal', 'correction']
for (start, end), lab in zip(arrows, arrow_labels):
    ax_loop.annotate('', xy=end, xytext=start,
                     arrowprops=dict(arrowstyle='->', color='white', lw=2))
    mx, my = (start[0]+end[0])/2, (start[1]+end[1])/2
    offset = 0.2 if start[1] == end[1] else 0.35
    ax_loop.text(mx, my+offset, lab, ha='center', fontsize=6, color='#aaaaaa')

# Output
ax_loop.annotate('', xy=(1.0, 5.3), xytext=(1.0, 4.5),
                 arrowprops=dict(arrowstyle='->', color='#00ff88', lw=2.5))
ax_loop.text(1.0, 5.5, 'STABLE OUTPUT\n6.835 GHz\n(your atomic reference!)',
             ha='center', fontsize=9, color='#00ff88', fontweight='bold',
             bbox=dict(boxstyle='round,pad=0.3', facecolor='#0a1a0a', edgecolor='#00ff88'))

ax_loop.text(4.0, 0.8,
    'The loop keeps the oscillator locked to the EXACT\n'
    'Rb atomic transition. If it drifts, atoms absorb\n'
    'more light, photodetector sees a dip, PID corrects.',
    ha='center', fontsize=8, color='#aaaaaa',
    bbox=dict(boxstyle='round,pad=0.4', facecolor='#111133', edgecolor='#444'))

ax_loop.set_xlim(-0.5, 8.5)
ax_loop.set_ylim(0.3, 6.2)
ax_loop.axis('off')


# ======================================================================
# ROW 3, PANEL 9: THERMAL CONTROL 3D
# ======================================================================
ax_therm = fig.add_subplot(gs[2, 2], projection='3d', facecolor='#0a0a1a')
ax_therm.set_title('9. THERMAL CONTROL (Why 85 C Matters)',
                   color='#00ccff', fontsize=11, fontweight='bold', pad=10)

res = 50
xg = np.linspace(-1, 1, res)
yg = np.linspace(-1, 1, res)
X, Y = np.meshgrid(xg, yg)
R = np.sqrt(X**2 + Y**2)
T = CELL_TEMP + 2.0*np.exp(-R**2/0.8) - 1.5*(R/1.0)**2
T += 0.4*np.exp(-((X-0.3)**2+(Y-0.3)**2)/0.3)
T += 0.4*np.exp(-((X+0.3)**2+(Y+0.3)**2)/0.3)

hot_cmap = LinearSegmentedColormap.from_list('hot_c',
    ['#000044', '#0044aa', '#ff4400', '#ffaa00', '#ffffff'], N=256)
surf = ax_therm.plot_surface(X, Y, T, cmap=hot_cmap, alpha=0.85,
                              edgecolor='none', antialiased=True)
fig.colorbar(surf, ax=ax_therm, shrink=0.45, aspect=12, pad=0.08,
             label='T (C)')
ax_therm.contour(X, Y, T, zdir='z', offset=82, cmap=hot_cmap, alpha=0.3, levels=8)

ax_therm.set_zlim(82, 89)
ax_therm.set_xlabel('X (mm)', color='gray', fontsize=6)
ax_therm.set_ylabel('Y (mm)', color='gray', fontsize=6)
ax_therm.set_zlabel('T (C)', color='gray', fontsize=6)
ax_therm.tick_params(colors='gray', labelsize=5)
for pane in [ax_therm.xaxis.pane, ax_therm.yaxis.pane, ax_therm.zaxis.pane]:
    pane.fill = False
    pane.set_edgecolor('#333')
ax_therm.view_init(elev=30, azim=-45)

ax_therm.text2D(0.02, 0.92,
    'Rb atoms must be at ~85 C\n'
    'to have enough vapor pressure.\n'
    'Too cold: no atoms to interrogate.\n'
    'Too hot: collisional broadening.\n'
    'Pt heaters hold +/- 0.1 C.',
    transform=ax_therm.transAxes, fontsize=7, color='#ffaa00',
    bbox=dict(boxstyle='round,pad=0.3', facecolor='#1a1a2e', edgecolor='#444'))


# ======================================================================
# ROW 4, PANEL 10: TIME ERROR -> POSITION ERROR (the money plot)
# ======================================================================
ax_pos = fig.add_subplot(gs[3, 0], facecolor='#0a0a1a')
ax_pos.set_title('10. TIME ERROR = POSITION ERROR', color='#ff4444',
                 fontsize=12, fontweight='bold')

t_hours = np.linspace(0, 24, 500)  # hours after GPS loss

# Clock drift models (time error in microseconds)
# Quartz TCXO: ~1 ppm aging + temperature, roughly 1 us/hr
drift_quartz = 1.0 * t_hours + 0.05 * t_hours**2

# CSAC: ~3e-10/day Allan deviation floor + drift ~1e-11/s
drift_csac = 0.01 * t_hours + 0.0005 * t_hours**2

# OCXO (oven-controlled crystal): intermediate
drift_ocxo = 0.1 * t_hours + 0.005 * t_hours**2

# Convert time error (us) to position error (meters): 1 us = 300 m
pos_quartz = drift_quartz * 300
pos_csac = drift_csac * 300
pos_ocxo = drift_ocxo * 300

ax_pos.semilogy(t_hours, pos_quartz, color='#ff4444', linewidth=2.5,
                label='Quartz (TCXO)')
ax_pos.semilogy(t_hours, pos_ocxo, color='#ffaa00', linewidth=2,
                linestyle='--', label='OCXO')
ax_pos.semilogy(t_hours, pos_csac, color='#00ff88', linewidth=2.5,
                label='CSAC (this chip)')

# Mission requirement lines
ax_pos.axhline(100, color='cyan', alpha=0.3, linestyle='-.')
ax_pos.text(24.3, 100, '100 m\n(tactical\nrequirement)', fontsize=7,
            color='cyan', va='center')
ax_pos.axhline(1000, color='#ff8844', alpha=0.3, linestyle='-.')
ax_pos.text(24.3, 1000, '1 km', fontsize=7, color='#ff8844', va='center')

# GPS loss marker
ax_pos.axvline(0, color='#ff0000', linewidth=2, alpha=0.5)
ax_pos.text(0.3, 50000, 'GPS\nLOST', fontsize=10, color='#ff0000', fontweight='bold')

# Shade the "acceptable" region
ax_pos.fill_between(t_hours, 0.1, 100, alpha=0.05, color='#00ff88')

ax_pos.set_xlabel('Hours After GPS Loss', color='white', fontsize=10)
ax_pos.set_ylabel('Position Error (meters)', color='white', fontsize=10)
ax_pos.set_xlim(0, 25)
ax_pos.set_ylim(0.5, 200000)
ax_pos.legend(fontsize=9, facecolor='#1a1a2e', edgecolor='#444',
              labelcolor='white', loc='upper left')
ax_pos.grid(True, alpha=0.15, color='gray')
ax_pos.tick_params(colors='gray')
for sp in ax_pos.spines.values():
    sp.set_edgecolor('#333')

# Key insight annotation
ax_pos.text(12, 5,
    'Rule: 1 microsecond of clock error\n= 300 meters of position error\n'
    '(speed of light x time)',
    fontsize=9, color='yellow', fontweight='bold', ha='center',
    bbox=dict(boxstyle='round,pad=0.4', facecolor='#1a1a0a', edgecolor='yellow',
              linewidth=1.5))


# ======================================================================
# ROW 4, PANEL 11: ALLAN DEVIATION (clock fingerprint)
# ======================================================================
ax_allan = fig.add_subplot(gs[3, 1], facecolor='#0a0a1a')
ax_allan.set_title('11. CLOCK STABILITY (Allan Deviation)',
                   color='#00ccff', fontsize=12, fontweight='bold')

tau = np.logspace(-1, 6, 300)
adev_csac = 2e-10/np.sqrt(tau) + 5e-12 + 8e-15*tau
adev_rb   = 5e-11/np.sqrt(tau) + 2e-12 + 3e-15*tau
adev_xtal = 1e-9/np.sqrt(tau)  + 1e-10 + 1e-11*np.sqrt(tau)
adev_gps  = np.where(tau < 100, 1e-9/np.sqrt(tau), 1e-12*np.ones_like(tau))

ax_allan.loglog(tau, adev_xtal, color='#ff4444', lw=2, label='TCXO (quartz)')
ax_allan.loglog(tau, adev_csac, color='#00ff88', lw=2.5, label='CSAC')
ax_allan.loglog(tau, adev_rb, color='#ffaa00', lw=2, ls='--', label='Rb oscillator')
ax_allan.loglog(tau, adev_gps, color='cyan', lw=1.5, ls=':', label='GPS-disciplined')

# Holdover
ax_allan.axvspan(3600, 86400, alpha=0.08, color='yellow')
ax_allan.text(10000, 5e-8, 'GPS-denied\nholdover\nperiod', fontsize=8,
              color='yellow', ha='center')

ax_allan.set_xlabel('Averaging Time (seconds)', color='white', fontsize=9)
ax_allan.set_ylabel('Allan Deviation', color='white', fontsize=9)
ax_allan.legend(fontsize=8, facecolor='#1a1a2e', edgecolor='#444',
                labelcolor='white', loc='upper right')
ax_allan.set_xlim(0.1, 1e6)
ax_allan.set_ylim(1e-13, 1e-7)
ax_allan.grid(True, alpha=0.15, color='gray')
ax_allan.tick_params(colors='gray')
for sp in ax_allan.spines.values():
    sp.set_edgecolor('#333')

# Top axis
ax_top = ax_allan.twiny()
ax_top.set_xscale('log')
ax_top.set_xlim(ax_allan.get_xlim())
tl = {1:'1s', 60:'1min', 3600:'1hr', 86400:'1day'}
ax_top.set_xticks(list(tl.keys()))
ax_top.set_xticklabels(list(tl.values()), fontsize=7, color='gray')
ax_top.tick_params(colors='gray')
for sp in ax_top.spines.values():
    sp.set_edgecolor('#333')


# ======================================================================
# ROW 4, PANEL 12: REAL-WORLD SCENARIO — MISSION TIMELINE
# ======================================================================
ax_mission = fig.add_subplot(gs[3, 2], facecolor='#0a0a1a')
ax_mission.set_title('12. MISSION SCENARIO: 8-Hour Patrol Without GPS',
                     color='#00ccff', fontsize=11, fontweight='bold')

# Timeline
events = [
    (0.0,  'GPS lock\nacquired',       '#00ff88', 15),
    (0.5,  'Patrol\nbegins',           '#44aaff', 12),
    (1.0,  'Enter denied\nzone (jammed)', '#ff4444', 14),
    (2.5,  'Checkpoint A\n(CSAC: 8m err)', '#00ff88', 10),
    (4.0,  'Target area\n(CSAC: 15m err)', '#ffaa00', 10),
    (6.0,  'Extraction point\n(CSAC: 25m err)', '#ffaa00', 10),
    (8.0,  'Exit denied zone\nRe-acquire GPS',  '#00ff88', 14),
]

for t, label, col, fs in events:
    ax_mission.plot(t, 0, 'o', color=col, markersize=fs, zorder=5)
    y_off = 0.6 if events.index((t, label, col, fs)) % 2 == 0 else -0.6
    ax_mission.text(t, y_off, label, ha='center', va='center', fontsize=7.5,
                    color=col, fontweight='bold')
    ax_mission.plot([t, t], [0, y_off*0.45], color=col, alpha=0.4, linewidth=1)

# Timeline arrow
ax_mission.annotate('', xy=(8.5, 0), xytext=(-0.3, 0),
                    arrowprops=dict(arrowstyle='->', color='white', lw=2))
ax_mission.text(4.0, -1.7, 'TIME (hours)', ha='center', fontsize=9, color='white')

# GPS denied zone
ax_mission.axvspan(1.0, 8.0, ymin=0.35, ymax=0.65, alpha=0.1, color='red')
ax_mission.text(4.5, 0, 'GPS DENIED ZONE', fontsize=8, color='#ff4444',
                alpha=0.5, ha='center', va='center')

# Comparison table
table_text = (
    'POSITION ERROR AT 8 HOURS:\n'
    '-------------------------------------\n'
    'Quartz TCXO:     ~2,400 m  (LOST)\n'
    'OCXO:                ~240 m  (risky)\n'
    'CSAC (this chip):     ~30 m  (ON TARGET)\n'
    '-------------------------------------\n'
    'Size: ~16 cm3 | Power: ~120 mW\n'
    'Cost target: $250-$1,200 per unit'
)
ax_mission.text(4.0, -3.0, table_text, ha='center', va='top', fontsize=8,
                color='white', fontfamily='monospace',
                bbox=dict(boxstyle='round,pad=0.5', facecolor='#111133',
                          edgecolor='#00ff88', linewidth=1.5))

ax_mission.set_xlim(-0.8, 9.0)
ax_mission.set_ylim(-5.5, 1.5)
ax_mission.axis('off')


# ──────────────────────────────────────────────────────────────────────────────
# BOTTOM: FULL SIGNAL CHAIN
# ──────────────────────────────────────────────────────────────────────────────
fig.text(0.5, 0.008,
    'SIGNAL CHAIN:  VCSEL (795nm, RF modulated at 3.417 GHz)  -->  Quarter-Wave Plate  -->  '
    'MEMS Vapor Cell (Rb-87 + N2 buffer, 85 C)  -->  Photodetector  -->  '
    'Lock-in Amp  -->  PID Controller  -->  Locked 6.835 GHz Output  -->  Timing for Navigation',
    ha='center', va='bottom', fontsize=8.5, color='#aaaaaa',
    bbox=dict(boxstyle='round,pad=0.4', facecolor='#111122', edgecolor='#444'),
    fontfamily='monospace')

plt.savefig('csac_simulation.png', dpi=160, facecolor=fig.get_facecolor(),
            bbox_inches='tight')
plt.show()

print("\nDone! Saved to csac_simulation.png")
print("\n" + "="*70)
print("HOW A CSAC REPLACES GPS -- SUMMARY")
print("="*70)
print("""
1. GPS IS A CLOCK SYSTEM: Satellites broadcast atomic-clock time signals.
   Your receiver computes position from signal arrival-time differences.

2. THE PROBLEM: Jammers/spoofers block GPS. Without satellite clocks,
   your cheap quartz oscillator drifts ~1 us/hour = 300 m/hour of error.

3. THE SOLUTION: A CSAC puts an ATOMIC CLOCK on a chip the size of a
   postage stamp. It uses quantum physics (CPT in Rb-87 vapor) to lock
   a local oscillator to the Rb hyperfine transition at 6.835 GHz.

4. HOW IT WORKS:
   - VCSEL laser (795 nm) is modulated at 3.417 GHz
   - Two sidebands separated by 6.835 GHz interrogate Rb atoms
   - At exact resonance, atoms enter a "dark state" (CPT) and stop absorbing
   - Photodetector sees a transparency peak -> feedback locks the oscillator
   - Result: ~1e-10 stability (vs ~1e-6 for quartz)

5. FOR NAVIGATION: After GPS loss, CSAC maintains microsecond-level timing
   for 8+ hours. This keeps position error under ~30 meters vs ~2.4 km
   for quartz. Soldiers, drones, and missiles can navigate without GPS.

6. THE CHIP: Glass/Silicon/Glass wafer stack (MEMS), anodically bonded,
   with integrated Pt heaters keeping Rb at 85C. Size ~16 cm3, ~120 mW.
""")
