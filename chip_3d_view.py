"""
CSAC MEMS — 3D Chip Visualization
===================================
Run: python chip_3d_view.py
Output: chip_3d_view.png

Shows the complete chip stack with exploded 3D view, cross-section,
size comparison, and full specifications.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.patheffects as pe
from matplotlib.gridspec import GridSpec
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle, Circle
from matplotlib.lines import Line2D
import warnings
warnings.filterwarnings('ignore')

# ─────────────────────────────────────────────────────────────────────────────
# CHIP DIMENSIONS (from Phase 1 simulation targets)
# ─────────────────────────────────────────────────────────────────────────────

# Physical layer dimensions (mm)
PKG_W, PKG_D, PKG_H   = 8.0, 8.0, 5.0    # Ceramic LCC package
CELL_W                 = 3.0               # Vapor cell die lateral
GLASS_T                = 0.3               # Borofloat 33 window thickness
SI_T                   = 1.0               # Silicon wafer thickness
CAV_D                  = 1.5               # Cavity diameter
CAV_H                  = 1.0              # Cavity depth
VCSEL_W                = 1.0               # VCSEL die
VCSEL_T                = 0.3
QWP_W                  = 3.0               # Quarter-wave plate
QWP_T                  = 0.5
PD_W                   = 1.5               # Photodetector
PD_T                   = 0.3
PT_TRACE_W             = 0.05              # Pt heater trace width

# ─────────────────────────────────────────────────────────────────────────────
# COLOR PALETTE
# ─────────────────────────────────────────────────────────────────────────────
BG          = '#050510'
GLASS_C     = '#00c8ff'
SI_C        = '#1c2333'
SI_TOP_C    = '#252d42'
RB_C        = '#9933ff'
VCSEL_C     = '#ff3300'
VCSEL_GW    = '#ff8800'
QWP_C       = '#f0e8c0'
PD_C        = '#003388'
PT_C        = '#ffd700'
PKG_C       = '#b8a898'
PKG_DARK    = '#8a7a6a'
BEAM_C      = '#00ff88'
LABEL_C     = '#e0e8ff'
DIM_C       = '#ffcc44'
ACCENT      = '#00ccff'

# ─────────────────────────────────────────────────────────────────────────────
# HELPER: Draw a 3D box as Poly3DCollection
# ─────────────────────────────────────────────────────────────────────────────

def box_faces(x0, y0, z0, dx, dy, dz):
    """Return 6 faces of a box as list of 4-vertex polygons."""
    x1, y1, z1 = x0+dx, y0+dy, z0+dz
    return [
        [[x0,y0,z0],[x1,y0,z0],[x1,y1,z0],[x0,y1,z0]],   # bottom
        [[x0,y0,z1],[x1,y0,z1],[x1,y1,z1],[x0,y1,z1]],   # top
        [[x0,y0,z0],[x1,y0,z0],[x1,y0,z1],[x0,y0,z1]],   # front
        [[x0,y1,z0],[x1,y1,z0],[x1,y1,z1],[x0,y1,z1]],   # back
        [[x0,y0,z0],[x0,y1,z0],[x0,y1,z1],[x0,y0,z1]],   # left
        [[x1,y0,z0],[x1,y1,z0],[x1,y1,z1],[x1,y0,z1]],   # right
    ]

def draw_box(ax, x0, y0, z0, dx, dy, dz, color, alpha=0.35,
             edgecolor='#ffffff', lw=0.4, zorder=1):
    faces = box_faces(x0, y0, z0, dx, dy, dz)
    poly = Poly3DCollection(faces, alpha=alpha, facecolor=color,
                             edgecolor=edgecolor, linewidth=lw, zorder=zorder)
    ax.add_collection3d(poly)

def draw_cylinder_top(ax, cx, cy, z, radius, color, alpha=0.5, n=64):
    """Draw a filled circle (top face of cylinder) at height z."""
    theta = np.linspace(0, 2*np.pi, n)
    xs = cx + radius * np.cos(theta)
    ys = cy + radius * np.sin(theta)
    zs = np.full(n, z)
    verts = [list(zip(xs, ys, zs))]
    poly = Poly3DCollection(verts, alpha=alpha, facecolor=color,
                             edgecolor=color, linewidth=0.3)
    ax.add_collection3d(poly)

def draw_cylinder_wall(ax, cx, cy, z0, z1, radius, color, alpha=0.3, n=32):
    """Draw cylinder side wall."""
    theta = np.linspace(0, 2*np.pi, n)
    for i in range(n-1):
        t0, t1 = theta[i], theta[i+1]
        verts = [[
            [cx+radius*np.cos(t0), cy+radius*np.sin(t0), z0],
            [cx+radius*np.cos(t1), cy+radius*np.sin(t1), z0],
            [cx+radius*np.cos(t1), cy+radius*np.sin(t1), z1],
            [cx+radius*np.cos(t0), cy+radius*np.sin(t0), z1],
        ]]
        poly = Poly3DCollection(verts, alpha=alpha, facecolor=color,
                                 edgecolor='none', linewidth=0)
        ax.add_collection3d(poly)


# ─────────────────────────────────────────────────────────────────────────────
# FIGURE SETUP
# ─────────────────────────────────────────────────────────────────────────────

fig = plt.figure(figsize=(26, 18), facecolor=BG)

gs = GridSpec(3, 3, figure=fig,
              left=0.02, right=0.98, top=0.93, bottom=0.04,
              hspace=0.35, wspace=0.25,
              height_ratios=[0.08, 1.0, 0.55],
              width_ratios=[1.3, 0.85, 0.85])

# ── Title ─────────────────────────────────────────────────────────────────────
ax_title = fig.add_subplot(gs[0, :])
ax_title.set_facecolor(BG)
ax_title.axis('off')

ax_title.text(0.5, 0.65,
    'CSAC MEMS  —  CHIP-SCALE ATOMIC CLOCK',
    ha='center', va='center', fontsize=28, fontweight='bold', color='white',
    transform=ax_title.transAxes,
    path_effects=[pe.withStroke(linewidth=6, foreground='#0033aa')])

ax_title.text(0.5, 0.05,
    'Rb-87  •  CPT Architecture  •  MEMS Vapor Cell  •  Defense-Grade Timing  •  ADEV < 5×10⁻¹⁰ @ 1s',
    ha='center', va='center', fontsize=12, color='#88aadd',
    transform=ax_title.transAxes)

# gradient line under title
x_line = np.linspace(0.02, 0.98, 300)
colors_line = plt.cm.cool(np.linspace(0, 1, 300))
for i in range(len(x_line)-1):
    ax_title.plot([x_line[i], x_line[i+1]], [-0.25, -0.25],
                   color=colors_line[i], linewidth=2.5,
                   transform=ax_title.transAxes, clip_on=False)


# ─────────────────────────────────────────────────────────────────────────────
# PANEL 1: 3D EXPLODED VIEW
# ─────────────────────────────────────────────────────────────────────────────

ax3d = fig.add_subplot(gs[1, 0], projection='3d', facecolor=BG)
ax3d.set_facecolor(BG)

# Exploded layer z positions (bottom to top, separated for clarity)
GAP = 2.2   # mm gap between layers in exploded view

# Center everything at x=0, y=0
CX = 0.0
CY = 0.0
HW = CELL_W / 2   # half-width = 1.5mm

z_vcsel      = 0.0
z_spacer     = z_vcsel  + VCSEL_T    + GAP
z_qwp        = z_spacer + 0.5        + GAP
z_glass_bot  = z_qwp    + QWP_T      + GAP
z_si         = z_glass_bot + GLASS_T + GAP
z_glass_top  = z_si     + SI_T       + GAP
z_pd         = z_glass_top + GLASS_T + GAP

# ── Ceramic package bottom (reference frame) ──────────────────────────────────
draw_box(ax3d, CX-4, CY-4, -1.2, 8, 8, 0.8, PKG_C,
         alpha=0.55, edgecolor=PKG_DARK, lw=1.0)

# Package walls (4 sides, open top)
for wx0, wy0, wdx, wdy in [
    (-4, -4, 8, 0.6), (-4, 3.4, 8, 0.6),   # front/back
    (-4, -4, 0.6, 8), (3.4, -4, 0.6, 8),   # left/right
]:
    draw_box(ax3d, CX+wx0, CY+wy0, -1.2, wdx, wdy, 5.5,
             PKG_C, alpha=0.18, edgecolor=PKG_DARK, lw=0.5)

# ── Bond pads on package (gold circles) ───────────────────────────────────────
pad_positions = [(-3.2, -3.2), (-3.2, 3.2), (3.2, -3.2), (3.2, 3.2),
                  (-3.2, 0), (3.2, 0), (0, -3.2), (0, 3.2)]
for px, py in pad_positions:
    theta = np.linspace(0, 2*np.pi, 20)
    rx = 0.25 * np.cos(theta) + CX + px
    ry = 0.25 * np.sin(theta) + CY + py
    rz = np.full(20, -0.42)
    verts = [list(zip(rx, ry, rz))]
    poly = Poly3DCollection(verts, alpha=0.9, facecolor=PT_C,
                             edgecolor='#aa8800', linewidth=0.5)
    ax3d.add_collection3d(poly)

# ── VCSEL (795nm laser) ────────────────────────────────────────────────────────
vw = VCSEL_W / 2
draw_box(ax3d, CX-vw, CY-vw, z_vcsel, VCSEL_W, VCSEL_W, VCSEL_T,
         VCSEL_C, alpha=0.90, edgecolor='#ff6600', lw=1.2, zorder=5)

# VCSEL emission glow (small bright circle on top)
draw_cylinder_top(ax3d, CX, CY, z_vcsel+VCSEL_T+0.01, 0.2, VCSEL_GW, alpha=0.95)

# ── Laser beam (light path upward) ────────────────────────────────────────────
beam_z = np.linspace(z_vcsel+VCSEL_T, z_pd-0.1, 100)
beam_r = 0.08
for bz in beam_z[::4]:
    frac = (bz - z_vcsel) / (z_pd - z_vcsel)
    alpha_beam = 0.6 * np.exp(-3 * abs(frac - 0.5)**2) + 0.15
    col = plt.cm.spring(frac * 0.7)
    ax3d.plot([CX], [CY], [bz], 'o', markersize=2.5, color=BEAM_C,
              alpha=alpha_beam, zorder=10)

# Beam as line
ax3d.plot([CX, CX], [CY, CY], [z_vcsel+VCSEL_T, z_pd],
          color=BEAM_C, linewidth=1.5, alpha=0.35, zorder=10, linestyle='--')

# ── Spacer / optical mount ─────────────────────────────────────────────────────
sw = 1.25
draw_box(ax3d, CX-sw, CY-sw, z_spacer, 2*sw, 2*sw, 0.5,
         '#1a1a2e', alpha=0.7, edgecolor='#333355', lw=0.5)
# aperture hole in spacer
draw_cylinder_top(ax3d, CX, CY, z_spacer+0.5, 0.35, BG, alpha=1.0)
draw_cylinder_top(ax3d, CX, CY, z_spacer,     0.35, BG, alpha=1.0)

# ── Quarter-Wave Plate ─────────────────────────────────────────────────────────
qw = QWP_W / 2
draw_box(ax3d, CX-qw, CY-qw, z_qwp, QWP_W, QWP_W, QWP_T,
         QWP_C, alpha=0.45, edgecolor='#d4c890', lw=0.8)
# crystal texture lines on QWP top face
for xi in np.linspace(CX-qw+0.2, CX+qw-0.2, 8):
    ax3d.plot([xi, xi], [CY-qw, CY+qw], [z_qwp+QWP_T]*2,
              color='#c8b870', linewidth=0.4, alpha=0.5)

# ── Bottom Glass (Borofloat 33) ────────────────────────────────────────────────
draw_box(ax3d, CX-HW, CY-HW, z_glass_bot, CELL_W, CELL_W, GLASS_T,
         GLASS_C, alpha=0.30, edgecolor='#00eeff', lw=1.0)

# ── Silicon Wafer (with cavity) ────────────────────────────────────────────────
draw_box(ax3d, CX-HW, CY-HW, z_si, CELL_W, CELL_W, SI_T,
         SI_C, alpha=0.85, edgecolor='#3344aa', lw=0.8)

# Pt heater traces on Si top surface (serpentine gold lines)
z_pt = z_si + SI_T + 0.02
trace_xs = np.linspace(CX-1.1, CX+1.1, 200)
trace_ys = np.zeros(200)
serpentine_period = 0.35
for i, tx in enumerate(trace_xs):
    seg = int(tx / serpentine_period) % 2
    trace_ys[i] = CY + 0.9*np.sin(tx/serpentine_period * np.pi) * 0.5
ax3d.plot(trace_xs, trace_ys, np.full(200, z_pt),
          color=PT_C, linewidth=1.8, alpha=0.85, zorder=15)

# RTD meander on opposite side of Si
rtd_x = np.linspace(CX-0.8, CX+0.8, 100)
rtd_y = CY - 0.7 + 0.3 * np.sin(rtd_x * 8)
ax3d.plot(rtd_x, rtd_y, np.full(100, z_pt),
          color='#ff9900', linewidth=1.5, alpha=0.7, zorder=15)

# Rb vapor cavity (glowing purple cylinder inside Si)
cav_r = CAV_D / 2
draw_cylinder_wall(ax3d, CX, CY, z_si, z_si+CAV_H, cav_r,
                   RB_C, alpha=0.25)
draw_cylinder_top(ax3d, CX, CY, z_si, cav_r, RB_C, alpha=0.40)
draw_cylinder_top(ax3d, CX, CY, z_si+CAV_H, cav_r, RB_C, alpha=0.40)

# Rb atoms scatter glow inside cavity
rng = np.random.default_rng(42)
n_atoms = 80
for _ in range(n_atoms):
    r  = cav_r * 0.85 * np.sqrt(rng.uniform())
    th = rng.uniform(0, 2*np.pi)
    ax = CX + r * np.cos(th)
    ay = CY + r * np.sin(th)
    az = z_si + rng.uniform(0.05, CAV_H - 0.05)
    sz = rng.uniform(8, 30)
    alpha = rng.uniform(0.2, 0.6)
    ax3d.scatter([ax], [ay], [az], s=sz, c=[[0.6, 0.1, 1.0, alpha]], zorder=20)

# ── Top Glass ─────────────────────────────────────────────────────────────────
draw_box(ax3d, CX-HW, CY-HW, z_glass_top, CELL_W, CELL_W, GLASS_T,
         GLASS_C, alpha=0.30, edgecolor='#00eeff', lw=1.0)

# ── Photodetector ─────────────────────────────────────────────────────────────
pw = PD_W / 2
draw_box(ax3d, CX-pw, CY-pw, z_pd, PD_W, PD_W, PD_T,
         PD_C, alpha=0.90, edgecolor='#0055ff', lw=1.0, zorder=5)
# active area
draw_cylinder_top(ax3d, CX, CY, z_pd+PD_T, 0.45, '#2266ff', alpha=0.8)

# ── Labels with leader lines ──────────────────────────────────────────────────
label_data = [
    (CX+2.8, CY+0.5, z_vcsel+0.15,      'VCSEL  795nm',       VCSEL_C,   14),
    (CX+2.5, CY-0.5, z_spacer+0.25,     'Optical Spacer',     '#888888', 11),
    (CX+2.8, CY+0.8, z_qwp+0.25,        'λ/4 Wave Plate',     QWP_C,     13),
    (CX+2.8, CY+0.2, z_glass_bot+0.15,  'Borofloat Glass',    GLASS_C,   12),
    (CX+2.8, CY-0.8, z_si+0.5,          'Si + Rb Cavity',     '#7788ff', 13),
    (CX+2.8, CY+0.5, z_glass_top+0.15,  'Borofloat Glass',    GLASS_C,   12),
    (CX+2.8, CY-0.3, z_pd+0.15,         'Photodetector',      '#4488ff', 14),
    (CX-3.0, CY-2.0, z_si+0.5,          'Pt Heater\n+ RTD',   PT_C,      12),
    (CX-2.0, CY-1.0, z_si+0.3,          'Rb-87 Vapor\n+ N₂',  RB_C,      12),
]

for lx, ly, lz, text, col, fs in label_data:
    # dot at layer
    ax3d.scatter([CX], [CY], [lz], s=3, c=[col], alpha=0.4)
    ax3d.text(lx, ly, lz, text, fontsize=fs, color=col, fontweight='bold',
              ha='left', va='center',
              path_effects=[pe.withStroke(linewidth=2.5, foreground=BG)])

# ── Dimension arrows ──────────────────────────────────────────────────────────
# Cell width: 3mm arrow on bottom glass layer
for zd, label in [(z_glass_bot, '3.0mm'), (z_si, '3.0mm')]:
    ax3d.plot([CX-HW, CX+HW], [CY-HW-0.5, CY-HW-0.5], [zd]*2,
              color=DIM_C, linewidth=1.2, alpha=0.7)
    ax3d.text(CX, CY-HW-0.9, zd,
              label, fontsize=9, color=DIM_C, ha='center',
              path_effects=[pe.withStroke(linewidth=2, foreground=BG)])

# Cavity diameter annotation
ax3d.plot([CX-cav_r, CX+cav_r], [CY, CY], [z_si+0.02]*2,
          color=RB_C, linewidth=1.5, alpha=0.8)
ax3d.text(CX, CY+0.3, z_si-0.1, 'ø1.5mm', fontsize=9, color=RB_C,
          ha='center',
          path_effects=[pe.withStroke(linewidth=2, foreground=BG)])

# ── Axis styling ──────────────────────────────────────────────────────────────
ax3d.set_xlabel('X (mm)', color='#556688', fontsize=9, labelpad=-5)
ax3d.set_ylabel('Y (mm)', color='#556688', fontsize=9, labelpad=-5)
ax3d.set_zlabel('Z (mm, exploded)', color='#556688', fontsize=9, labelpad=-5)

ax3d.tick_params(colors='#334466', labelsize=7)
ax3d.xaxis.pane.fill = False
ax3d.yaxis.pane.fill = False
ax3d.zaxis.pane.fill = False
ax3d.xaxis.pane.set_edgecolor('#1a2040')
ax3d.yaxis.pane.set_edgecolor('#1a2040')
ax3d.zaxis.pane.set_edgecolor('#1a2040')
ax3d.grid(True, color='#1a2040', linewidth=0.5, alpha=0.5)

ax3d.set_xlim(-4, 5)
ax3d.set_ylim(-4, 4)
ax3d.set_zlim(-1.5, z_pd + 3)
ax3d.view_init(elev=22, azim=-48)

ax3d.set_title('EXPLODED 3D VIEW — All Layers', color=ACCENT, fontsize=13,
               fontweight='bold', pad=8)

# ─────────────────────────────────────────────────────────────────────────────
# PANEL 2: CROSS-SECTION (actual scale)
# ─────────────────────────────────────────────────────────────────────────────

ax_xsec = fig.add_subplot(gs[1, 1], facecolor=BG)
ax_xsec.set_facecolor(BG)
ax_xsec.set_aspect('equal')
ax_xsec.axis('off')

ax_xsec.set_title('CROSS-SECTION  (actual scale)', color=ACCENT,
                   fontsize=13, fontweight='bold', pad=6)

# Draw layers as rectangles (actual proportions, scaled ×30 for visibility)
SCALE = 30
cx = 0.5
W  = CELL_W * SCALE   # 90 units wide (in mm*30 space)
# centered: left = cx - W/2, right = cx + W/2
# But we use axes coords 0-1, so:
# W_frac = CELL_W * SCALE / 200  (assuming 200 unit axis width)
AX_W = 200

def draw_layer_xsec(ax, y_mm, h_mm, color, alpha, label, label_color,
                     w_mm=CELL_W, scale=SCALE, ax_w=AX_W):
    x0  = (ax_w/2 - w_mm*scale/2) / ax_w
    wf  = w_mm * scale / ax_w
    yf  = y_mm / ax_w
    hf  = h_mm * scale / ax_w  # use scale
    rect = FancyBboxPatch((x0, yf), wf, hf,
                           boxstyle='square,pad=0.001',
                           facecolor=color, edgecolor='white',
                           linewidth=0.8, alpha=alpha,
                           transform=ax.transAxes)
    ax.add_patch(rect)
    if label:
        ax.text(x0 + wf + 0.03, yf + hf/2, label, fontsize=9,
                color=label_color, va='center', ha='left',
                transform=ax.transAxes, fontweight='bold',
                path_effects=[pe.withStroke(linewidth=2, foreground=BG)])

# Y positions accumulate upward
y0 = 0.04
gap_s = 0.002

layers_xsec = [
    (VCSEL_T,   VCSEL_C,  0.9,  'VCSEL  1×1×0.3mm',    VCSEL_C,  VCSEL_W),
    (0.5,       '#1a1a2e',0.8,  'Spacer  2.5×2.5×0.5mm','#666688', 2.5),
    (QWP_T,     QWP_C,    0.6,  'λ/4 Plate  3×3×0.5mm', QWP_C,    CELL_W),
    (GLASS_T,   GLASS_C,  0.5,  'Glass (Borofloat33)  3×3×0.3mm', GLASS_C, CELL_W),
    (SI_T,      SI_C,     0.85, 'Silicon  3×3×1.0mm',  '#7788ff', CELL_W),
    (GLASS_T,   GLASS_C,  0.5,  'Glass (Borofloat33)  3×3×0.3mm', GLASS_C, CELL_W),
    (PD_T,      PD_C,     0.9,  'Photodetector  1.5×1.5×0.3mm', '#4488ff', PD_W),
]

y_cur = y0
for h, col, alph, lab, lcol, w in layers_xsec:
    draw_layer_xsec(ax_xsec, y_cur*AX_W/SCALE, h,
                    col, alph, lab, lcol, w_mm=w)
    y_cur += h * SCALE / AX_W + gap_s

# Rb cavity inside Si layer
si_idx = 3   # 0-indexed layer
si_y = y0 + sum(l[0]*SCALE/AX_W + gap_s for l in layers_xsec[:3]) + gap_s
cav_h = CAV_H * SCALE / AX_W
cav_w = CAV_D * SCALE / AX_W

ax_xsec.add_patch(FancyBboxPatch(
    (0.5 - cav_w/2, si_y), cav_w, cav_h,
    boxstyle='square,pad=0',
    facecolor=RB_C, edgecolor='#cc44ff',
    linewidth=1.5, alpha=0.5,
    transform=ax_xsec.transAxes))

ax_xsec.text(0.5, si_y + cav_h/2, 'Rb+N₂', fontsize=9,
             ha='center', va='center', color='white', fontweight='bold',
             transform=ax_xsec.transAxes,
             path_effects=[pe.withStroke(linewidth=2, foreground=BG)])

# Light beam through the stack
beam_top    = y_cur + 0.01
beam_bottom = y0 + layers_xsec[0][0]*SCALE/AX_W + gap_s
ax_xsec.annotate('', xy=(0.5, beam_top), xytext=(0.5, y0+0.005),
                  xycoords='axes fraction', textcoords='axes fraction',
                  arrowprops=dict(arrowstyle='->', color=BEAM_C,
                                  lw=2.5, connectionstyle='arc3,rad=0.0'))
ax_xsec.text(0.5+0.10, (beam_top+y0)/2, '795nm\nlaser\nbeam',
             fontsize=9, color=BEAM_C, ha='left', va='center',
             transform=ax_xsec.transAxes, style='italic',
             path_effects=[pe.withStroke(linewidth=2, foreground=BG)])

# Dimension: total height
total_h_mm = VCSEL_T + 0.5 + QWP_T + GLASS_T + SI_T + GLASS_T + PD_T
ax_xsec.annotate('', xy=(0.08, y_cur), xytext=(0.08, y0),
                  xycoords='axes fraction', textcoords='axes fraction',
                  arrowprops=dict(arrowstyle='<->', color=DIM_C, lw=1.8))
ax_xsec.text(0.03, (y_cur + y0) / 2,
             f'{total_h_mm:.1f}mm\ntotal', fontsize=9, color=DIM_C,
             ha='center', va='center', transform=ax_xsec.transAxes,
             path_effects=[pe.withStroke(linewidth=2, foreground=BG)])

# Dimension: cell width
w_frac = CELL_W * SCALE / AX_W
ax_xsec.annotate('', xy=(0.5+w_frac/2, y0-0.025),
                  xytext=(0.5-w_frac/2, y0-0.025),
                  xycoords='axes fraction', textcoords='axes fraction',
                  arrowprops=dict(arrowstyle='<->', color=DIM_C, lw=1.8))
ax_xsec.text(0.5, y0-0.04, '3.0mm', fontsize=9, color=DIM_C,
             ha='center', va='top', transform=ax_xsec.transAxes,
             path_effects=[pe.withStroke(linewidth=2, foreground=BG)])

ax_xsec.set_xlim(0, 1)
ax_xsec.set_ylim(-0.08, 0.75)

# ─────────────────────────────────────────────────────────────────────────────
# PANEL 3: CHIP SPECIFICATIONS
# ─────────────────────────────────────────────────────────────────────────────

ax_spec = fig.add_subplot(gs[1, 2], facecolor=BG)
ax_spec.set_facecolor(BG)
ax_spec.axis('off')
ax_spec.set_title('CHIP SPECIFICATIONS', color=ACCENT,
                   fontsize=13, fontweight='bold', pad=6)

specs = [
    ('DIMENSIONS', None, '#00ccff'),
    ('  Cell die',            '3.0 × 3.0 × 1.6 mm',    'white'),
    ('  Optical stack',       '3.0 × 3.0 × 3.9 mm',    'white'),
    ('  LCC package',         '8.0 × 8.0 × 5.0 mm',    '#ffcc44'),
    ('  Cavity diameter',     'ø 1.5 mm',               'white'),
    ('  Cavity depth',        '1.0 mm',                 'white'),
    ('', None, None),
    ('PHYSICS', None, '#00ccff'),
    ('  Atomic species',      'Rb-87',                  'white'),
    ('  Transition',          'D1 line  794.979 nm',    '#ff8800'),
    ('  Hyperfine reference', '6,834,682,610.904 Hz',   '#ff8800'),
    ('  Modulation freq',     '3,417,341,305 Hz',       'white'),
    ('  Buffer gas',          'N₂  30–75 Torr',         '#88aaff'),
    ('  Cell temperature',    '85°C  ± 0.01°C',         'white'),
    ('', None, None),
    ('PERFORMANCE', None, '#00ccff'),
    ('  ADEV @ τ=1s',         '< 5×10⁻¹⁰',             '#00ff88'),
    ('  ADEV @ τ=1hr',        '< 1×10⁻¹¹',             '#00ff88'),
    ('  CPT linewidth',       '< 5 kHz',                'white'),
    ('  CPT contrast',        '> 3%',                   'white'),
    ('  Power (total)',        '< 150 mW',               'white'),
    ('  Heater power',        '< 100 mW',               'white'),
    ('', None, None),
    ('BENCHMARK vs SA65', None, '#00ccff'),
    ('  Volume reduction',    '~15×  (0.32 vs 5 cm³)',  '#ffcc44'),
    ('  ADEV target',         'comparable to SA65',     '#ffcc44'),
    ('  Architecture',        'MEMS CPT (patent clear)', '#00ff88'),
]

y_s = 0.97
for label, value, col in specs:
    if col is None:
        y_s -= 0.022
        continue
    if value is None:
        ax_spec.text(0.02, y_s, label, fontsize=10, fontweight='bold',
                     color=col, transform=ax_spec.transAxes, va='top',
                     path_effects=[pe.withStroke(linewidth=2.5, foreground=BG)])
        ax_spec.axhline(y=y_s - 0.012, xmin=0.02, xmax=0.98,
                         color=col, linewidth=0.6, alpha=0.4)
        y_s -= 0.042
    else:
        ax_spec.text(0.04, y_s, label, fontsize=9.5, color='#aabbcc',
                     transform=ax_spec.transAxes, va='top')
        ax_spec.text(0.54, y_s, value, fontsize=9.5, color=col,
                     transform=ax_spec.transAxes, va='top', fontweight='bold',
                     path_effects=[pe.withStroke(linewidth=2, foreground=BG)])
        y_s -= 0.038


# ─────────────────────────────────────────────────────────────────────────────
# PANEL 4: SIZE COMPARISON
# ─────────────────────────────────────────────────────────────────────────────

ax_size = fig.add_subplot(gs[2, 0], facecolor=BG)
ax_size.set_facecolor(BG)
ax_size.set_xlim(0, 120)
ax_size.set_ylim(0, 60)
ax_size.axis('off')
ax_size.set_title('SIZE COMPARISON  (top view, actual scale)',
                   color=ACCENT, fontsize=13, fontweight='bold', pad=4)

# Scale: 1mm = 2.2 pixels in axes units
CSCALE = 2.2

def draw_comp_rect(ax, cx, cy, w, h, col, alpha, label, sub):
    rect = FancyBboxPatch((cx - w/2, cy - h/2), w, h,
                           boxstyle='round,pad=0.5',
                           facecolor=col, edgecolor='white',
                           linewidth=1.0, alpha=alpha)
    ax.add_patch(rect)
    ax.text(cx, cy+1, label, ha='center', va='center', fontsize=9.5,
            color='white', fontweight='bold',
            path_effects=[pe.withStroke(linewidth=2, foreground=BG)])
    ax.text(cx, cy-2, sub, ha='center', va='center', fontsize=8,
            color='#aabbcc',
            path_effects=[pe.withStroke(linewidth=2, foreground=BG)])

# Euro coin (ø 23.25mm) for scale
coin_r = 23.25 * CSCALE / 2
ax_size.add_patch(Circle((17, 30), coin_r, facecolor='#c8a020',
                           edgecolor='#ffe060', linewidth=1.5, alpha=0.7))
ax_size.text(17, 30, '€', ha='center', va='center',
             fontsize=22, color='#ffe060', alpha=0.8, fontweight='bold')
ax_size.text(17, 30-coin_r-2.5, '€ coin  ø23mm', ha='center',
             fontsize=8, color='#c8a020')

# SA65 (35.6 × 36.4mm)
sa65_w = 35.6 * CSCALE
sa65_h = 36.4 * CSCALE
draw_comp_rect(ax_size, 70, 30, sa65_w, sa65_h,
               '#443322', 0.7, 'Microchip SA65', '35.6×36.4×11.4mm\n17 cm³')

# Our chip package (8 × 8mm)
pkg_w = PKG_W * CSCALE
pkg_h = PKG_D * CSCALE
draw_comp_rect(ax_size, 70, 30, pkg_w, pkg_h,
               '#003366', 0.85, 'OUR CHIP\n(package)', '8×8×5mm\n0.32 cm³')

# Our cell die (3 × 3mm) — shown inside package position
die_w = 3.0 * CSCALE
die_h = 3.0 * CSCALE
rect_die = FancyBboxPatch((70 - die_w/2, 30 - die_h/2), die_w, die_h,
                            boxstyle='round,pad=0.2',
                            facecolor=RB_C, edgecolor='#cc66ff',
                            linewidth=1.5, alpha=0.7)
ax_size.add_patch(rect_die)
ax_size.text(70, 30, 'CELL\n3×3mm', ha='center', va='center',
             fontsize=7.5, color='white', fontweight='bold')

# Volume comparison bar
ax_size.text(104, 52, 'VOLUME', ha='center', fontsize=9, color=DIM_C, fontweight='bold')
ax_size.add_patch(FancyBboxPatch((95, 5), 18, 42,
                                  boxstyle='round,pad=0.5',
                                  facecolor='#220033', edgecolor='#443366',
                                  linewidth=0.8, alpha=0.5))
# SA65 bar (17 cm³) vs ours (0.32 cm³) — log scale visual
sa_bar_h = 42 * 0.90
our_bar_h = 42 * (np.log(0.32+1)/np.log(18)) * 0.9
ax_size.add_patch(FancyBboxPatch((97, 7), 5, sa_bar_h,
                                  facecolor='#664422', edgecolor='#996633',
                                  linewidth=1, alpha=0.8))
ax_size.text(99.5, 7 + sa_bar_h/2, '17\ncm³', ha='center', va='center',
             fontsize=7, color='#ffcc44')
ax_size.add_patch(FancyBboxPatch((104, 7), 5, our_bar_h,
                                  facecolor='#003388', edgecolor='#0055ff',
                                  linewidth=1, alpha=0.8))
ax_size.text(106.5, 7 + our_bar_h/2, '0.32\ncm³', ha='center', va='center',
             fontsize=7, color='#44aaff')
ax_size.text(99.5, 5.5, 'SA65', ha='center', fontsize=7, color='#996633')
ax_size.text(106.5, 5.5, 'OURS', ha='center', fontsize=7, color='#0055ff')
ax_size.text(104, 3.5, '15× smaller', ha='center', fontsize=8,
             color='#00ff88', fontweight='bold')


# ─────────────────────────────────────────────────────────────────────────────
# PANEL 5: SIGNAL FLOW BLOCK DIAGRAM
# ─────────────────────────────────────────────────────────────────────────────

ax_flow = fig.add_subplot(gs[2, 1:], facecolor=BG)
ax_flow.set_facecolor(BG)
ax_flow.set_xlim(0, 100)
ax_flow.set_ylim(0, 40)
ax_flow.axis('off')
ax_flow.set_title('SIGNAL FLOW — How the Clock Works',
                   color=ACCENT, fontsize=13, fontweight='bold', pad=4)

blocks = [
    (8,  20, '10MHz\nTCXO\nReference',     '#223344', '#4488aa'),
    (24, 20, 'PLL\nSynthesizer\n3.4173GHz', '#223344', '#4488aa'),
    (40, 20, 'VCSEL\n795nm\n÷ sidebands',   '#441100', '#ff5500'),
    (56, 20, 'Rb-87\nVapor Cell\nCPT',      '#220033', '#9933ff'),
    (72, 20, 'Photo-\ndetector\n+ TIA',      '#001133', '#3366ff'),
    (88, 20, 'Lock-in\nPID\nServo',          '#002200', '#00cc44'),
]

for bx, by, label, fc, ec in blocks:
    ax_flow.add_patch(FancyBboxPatch((bx-7, by-8), 14, 16,
                                      boxstyle='round,pad=1',
                                      facecolor=fc, edgecolor=ec,
                                      linewidth=2.0, alpha=0.85))
    ax_flow.text(bx, by, label, ha='center', va='center', fontsize=8,
                  color='white', fontweight='bold')

# Arrows forward
for i in range(len(blocks)-1):
    x0 = blocks[i][0] + 7
    x1 = blocks[i+1][0] - 7
    y  = blocks[i][1]
    ax_flow.annotate('', xy=(x1, y), xytext=(x0, y),
                      arrowprops=dict(arrowstyle='->', color=BEAM_C,
                                      lw=2.0, mutation_scale=14))

# Feedback arrow (servo → PLL)
ax_flow.annotate('', xy=(24, 12), xytext=(88, 12),
                  arrowprops=dict(arrowstyle='->', color='#ffcc00',
                                  lw=2.0, mutation_scale=14,
                                  connectionstyle='arc3,rad=0.0'))
ax_flow.text(56, 9.5, 'Frequency correction feedback',
             ha='center', fontsize=8, color='#ffcc00', style='italic')

# Output
ax_flow.add_patch(FancyBboxPatch((84, 32), 16, 8,
                                  boxstyle='round,pad=1',
                                  facecolor='#003300', edgecolor='#00ff44',
                                  linewidth=2.0, alpha=0.9))
ax_flow.text(92, 36, '10 MHz OUT\n÷ output', ha='center', va='center',
             fontsize=8, color='#00ff88', fontweight='bold')

ax_flow.annotate('', xy=(84, 36), xytext=(80, 20),
                  arrowprops=dict(arrowstyle='->', color='#00ff44', lw=1.5))

# ─────────────────────────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────────────────────────

fig.text(0.5, 0.01,
    'CSAC MEMS  •  Rb-87 CPT Atomic Clock  •  Glass–Si–Glass MEMS Stack  '
    '•  Anodic Bonding  •  CPT Servo Lock  '
    '•  ADEV < 5×10⁻¹⁰ @ 1s  •  8×8×5mm Package',
    ha='center', fontsize=9, color='#445566', style='italic')

# ─────────────────────────────────────────────────────────────────────────────
# SAVE
# ─────────────────────────────────────────────────────────────────────────────

plt.savefig('chip_3d_view.png', dpi=160, bbox_inches='tight',
            facecolor=BG, edgecolor='none')
print("Saved: chip_3d_view.png")
plt.show()
