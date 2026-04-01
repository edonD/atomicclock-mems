"""
CSAC-1 LCC-20 Package Design Drawings
Generates: lcc20_package.png, cross_section.png, package_summary.md
"""

import os
import math

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.patches as mpatches
import matplotlib.lines as mlines
import numpy as np

# Output directory: same folder as this script
OUT_DIR = os.path.dirname(os.path.abspath(__file__))

BG = "#050812"
PANEL = "#0b1321"
TEXT = "#e8effb"
MUTED = "#93a6c3"
ACCENT = "#62d5ff"
THERMAL = "#ffbd62"
OUTLINE = "#21334d"
CERAMIC = "#8c7e69"
CERAMIC_EDGE = "#5d5448"
DIE_FILL = "#20334d"
DIE_EDGE = "#62d5ff"
CAVITY_FILL = "#5b284f"
CAVITY_EDGE = "#c19be5"
PAD_FILL = "#8d7557"
PAD_EDGE = "#d2af78"
BOND = "#ffbd62"

# ── helpers ──────────────────────────────────────────────────────────────────

def save(fig, name):
    path = os.path.join(OUT_DIR, name)
    fig.savefig(path, dpi=150, bbox_inches='tight', facecolor=fig.get_facecolor())
    print(f"Saved: {path}")
    plt.close(fig)


# ═══════════════════════════════════════════════════════════════════════════════
# 1.  LCC-20 TOP-DOWN FOOTPRINT
# ═══════════════════════════════════════════════════════════════════════════════

def draw_lcc20():
    fig, ax = plt.subplots(figsize=(10, 10))
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(PANEL)
    ax.set_aspect('equal')

    PKG  = 7.0          # package body mm
    PAD_W  = 0.8        # pad width mm
    PAD_D  = 0.6        # pad depth (into body) mm
    PITCH  = 1.2        # pad pitch mm
    NPADS  = 5          # pads per side  (5×4 = 20 total)
    DIE    = 3.0
    DIE_AT = 3.2        # die attach area

    # package outline centred at origin
    half = PKG / 2
    pkg_rect = patches.Rectangle((-half, -half), PKG, PKG,
                                  linewidth=2, edgecolor=CERAMIC_EDGE,
                                  facecolor=CERAMIC, zorder=2)
    ax.add_patch(pkg_rect)

    # ── castellated pads ──────────────────────────────────────────────────────
    # pads are numbered 1-20 CCW starting from pin 1 (top-left corner going down left side)
    # side order: LEFT (pins 1-5, bottom→top), BOTTOM (6-10, left→right),
    #             RIGHT (11-15, bottom→top), TOP (16-20, right→left)
    # We'll label them per convention: 1=top-left going CW
    # Standard LCC-20: pin 1 top-left, go CW → left side, bottom side, right side, top side

    pad_color   = PAD_FILL
    pad_border  = PAD_EDGE

    # compute pad centre positions (5 per side, pitch 1.2 mm, centred on each side)
    def side_centres(n, pitch, side_len):
        total = (n - 1) * pitch
        start = -total / 2
        return [start + i * pitch for i in range(n)]

    centres = side_centres(NPADS, PITCH, PKG)   # offsets along the side

    pad_rects = {}   # pad_number → (cx, cy)  for bond-wire endpoints

    # LEFT side  — pins 1-5, x = -half, offset along y, pads protrude LEFT
    for i, yc in enumerate(centres):
        pin = i + 1
        rect = patches.Rectangle((-half - PAD_D, yc - PAD_W / 2),
                                  PAD_D, PAD_W,
                                  linewidth=1, edgecolor=pad_border,
                                  facecolor=pad_color, zorder=3)
        ax.add_patch(rect)
        pad_rects[pin] = (-half - PAD_D / 2, yc)

    # BOTTOM side — pins 6-10, y = -half, offset along x, pads protrude DOWN
    for i, xc in enumerate(centres):
        pin = i + 6
        rect = patches.Rectangle((xc - PAD_W / 2, -half - PAD_D),
                                  PAD_W, PAD_D,
                                  linewidth=1, edgecolor=pad_border,
                                  facecolor=pad_color, zorder=3)
        ax.add_patch(rect)
        pad_rects[pin] = (xc, -half - PAD_D / 2)

    # RIGHT side — pins 11-15, x = +half, offset along y, pads protrude RIGHT
    for i, yc in enumerate(centres):
        pin = i + 11
        rect = patches.Rectangle((half, yc - PAD_W / 2),
                                  PAD_D, PAD_W,
                                  linewidth=1, edgecolor=pad_border,
                                  facecolor=pad_color, zorder=3)
        ax.add_patch(rect)
        pad_rects[pin] = (half + PAD_D / 2, yc)

    # TOP side — pins 16-20, y = +half, offset along x (reversed), pads protrude UP
    for i, xc in enumerate(reversed(centres)):
        pin = i + 16
        rect = patches.Rectangle((xc - PAD_W / 2, half),
                                  PAD_W, PAD_D,
                                  linewidth=1, edgecolor=pad_border,
                                  facecolor=pad_color, zorder=3)
        ax.add_patch(rect)
        pad_rects[pin] = (xc, half + PAD_D / 2)

    # ── die attach area (dashed) ──────────────────────────────────────────────
    da_half = DIE_AT / 2
    die_attach = patches.Rectangle((-da_half, -da_half), DIE_AT, DIE_AT,
                                    linewidth=1.2, edgecolor='#5c6f8a',
                                    facecolor='none', linestyle='--', zorder=4)
    ax.add_patch(die_attach)

    # ── die outline (solid blue) ──────────────────────────────────────────────
    die_half = DIE / 2
    die_rect = patches.Rectangle((-die_half, -die_half), DIE, DIE,
                                  linewidth=2, edgecolor=DIE_EDGE,
                                  facecolor=DIE_FILL, zorder=5)
    ax.add_patch(die_rect)

    # ── cavity window (yellow circle) ─────────────────────────────────────────
    cav = patches.Circle((0, 0), 0.75, linewidth=1.5,
                          edgecolor=CAVITY_EDGE, facecolor=CAVITY_FILL, zorder=6)
    ax.add_patch(cav)
    ax.text(0, 0, 'cavity', ha='center', va='center',
            fontsize=7, color='#f2d9ff', zorder=7, style='italic')

    # ── 8 die bond pads along bottom edge of die ─────────────────────────────
    # bottom edge: y = -die_half, 8 pads evenly spaced
    NBOND = 8
    bond_xs = np.linspace(-die_half + 0.15, die_half - 0.15, NBOND)
    bond_y_die = -die_half   # on die
    DIE_PAD_SIZE = 0.18

    bond_pad_names = ['VCC', 'GND', 'HTR+', 'HTR-', 'RTD+', 'RTD-', 'CLK', 'DATA']

    for i, bx in enumerate(bond_xs):
        bpad = patches.Rectangle((bx - DIE_PAD_SIZE / 2, bond_y_die - DIE_PAD_SIZE / 2),
                                  DIE_PAD_SIZE, DIE_PAD_SIZE,
                                  linewidth=0.8, edgecolor=PAD_EDGE,
                                  facecolor=THERMAL, zorder=7)
        ax.add_patch(bpad)

    # ── pad label assignment ──────────────────────────────────────────────────
    # Bottom side pads 6-10, central 4 used → pins 7,8,9,10 get VCC…DATA
    # We assign 8 signals to the 8 bottom pads (all 5 bottom + 3 closest on left/right)
    # Simplified: pads 6-10 on bottom (5 pads) and pads 5, 1, 15 on left/right
    # Actual assignment:
    #   bottom pads 6-10 (5): VCC, GND, HTR+, HTR-, RTD+
    #   right-side pad 11: RTD-
    #   right-side pad 12: CLK
    #   right-side pad 13: DATA
    # Remaining 12 pads = NC

    signal_map = {
        6:  'VCC',
        7:  'GND',
        8:  'HTR+',
        9:  'HTR-',
        10: 'RTD+',
        11: 'RTD-',
        12: 'CLK',
        13: 'DATA',
    }

    # ── pad labels ────────────────────────────────────────────────────────────
    label_offset = 0.55   # mm beyond pad centre outward

    for pin in range(1, 21):
        cx, cy = pad_rects[pin]
        label  = signal_map.get(pin, 'NC')
        color  = THERMAL if label != 'NC' else MUTED
        fsize  = 6.5 if label != 'NC' else 5.5

        # direction outward from package centre
        if pin <= 5:      # left
            tx, ty = cx - label_offset, cy
            ha, va = 'right', 'center'
        elif pin <= 10:   # bottom
            tx, ty = cx, cy - label_offset
            ha, va = 'center', 'top'
        elif pin <= 15:   # right
            tx, ty = cx + label_offset, cy
            ha, va = 'left', 'center'
        else:             # top
            tx, ty = cx, cy + label_offset
            ha, va = 'center', 'bottom'

        ax.text(tx, ty, f'{pin}\n{label}', ha=ha, va=va,
                fontsize=fsize, color=color, zorder=8,
                fontweight='bold' if label != 'NC' else 'normal')

    # ── bond wire arcs ─────────────────────────────────────────────────────────
    # 8 die pads (bond_xs, bond_y_die) → package pads for pins 6-13
    pkg_signal_pins = [6, 7, 8, 9, 10, 11, 12, 13]

    for i, pin in enumerate(pkg_signal_pins):
        x0, y0 = bond_xs[i], bond_y_die
        x1, y1 = pad_rects[pin]

        # arc midpoint bulge
        mx, my = (x0 + x1) / 2, (y0 + y1) / 2
        dx, dy = x1 - x0, y1 - y0
        length = math.hypot(dx, dy)
        # normal direction (for bulge)
        nx, ny = -dy / length, dx / length
        bulge = 0.3
        cpx, cpy = mx + nx * bulge, my + ny * bulge

        # draw quadratic Bezier as polyline
        t_vals = np.linspace(0, 1, 40)
        bx_arr = (1 - t_vals)**2 * x0 + 2 * (1 - t_vals) * t_vals * cpx + t_vals**2 * x1
        by_arr = (1 - t_vals)**2 * y0 + 2 * (1 - t_vals) * t_vals * cpy + t_vals**2 * y1

        ax.plot(bx_arr, by_arr, color=BOND, linewidth=1.2,
                zorder=6, alpha=0.85)

    # ── pin 1 marker ─────────────────────────────────────────────────────────
    # triangle at top-left corner of package
    tri_x = -half + 0.2
    tri_y =  half - 0.2
    triangle = mpatches.Polygon([[tri_x, tri_y],
                             [tri_x + 0.35, tri_y],
                             [tri_x, tri_y - 0.35]],
                            closed=True, facecolor=THERMAL,
                            edgecolor='#8f5e1e', zorder=9)
    ax.add_patch(triangle)
    ax.text(tri_x + 0.55, tri_y - 0.05, 'Pin 1', fontsize=7,
            color=THERMAL, va='center', zorder=9, fontweight='bold')

    # ── scale bar ─────────────────────────────────────────────────────────────
    sb_x0, sb_y = -half + 0.2, -half - 1.7
    ax.plot([sb_x0, sb_x0 + 1.0], [sb_y, sb_y], color=TEXT, linewidth=2, zorder=9)
    ax.plot([sb_x0, sb_x0],       [sb_y - 0.1, sb_y + 0.1], color=TEXT, linewidth=2)
    ax.plot([sb_x0 + 1.0, sb_x0 + 1.0], [sb_y - 0.1, sb_y + 0.1], color=TEXT, linewidth=2)
    ax.text(sb_x0 + 0.5, sb_y - 0.25, '1 mm', ha='center', va='top',
            fontsize=8, zorder=9, color=TEXT)

    # ── dimension annotations ─────────────────────────────────────────────────
    # package width
    ax.annotate('', xy=(half, -half - 1.1), xytext=(-half, -half - 1.1),
                arrowprops=dict(arrowstyle='<->', color=ACCENT, lw=1.2))
    ax.text(0, -half - 1.25, '7.0 mm', ha='center', va='top',
            fontsize=8, color=ACCENT)

    # die width
    ax.annotate('', xy=(die_half, die_half + 0.5), xytext=(-die_half, die_half + 0.5),
                arrowprops=dict(arrowstyle='<->', color=ACCENT, lw=1.0))
    ax.text(0, die_half + 0.62, '3.0 mm die', ha='center', va='bottom',
            fontsize=7.5, color=ACCENT)

    # ── legend ────────────────────────────────────────────────────────────────
    legend_items = [
        patches.Patch(facecolor=DIE_FILL, edgecolor=DIE_EDGE, label='Si Die (3.0×3.0 mm)'),
        patches.Patch(facecolor=CAVITY_FILL, edgecolor=CAVITY_EDGE, label='Cs vapour cavity (ø1.5 mm)'),
        patches.Patch(facecolor=CERAMIC, edgecolor=CERAMIC_EDGE, label='LCC-20 ceramic body'),
        patches.Patch(facecolor=pad_color,  edgecolor=pad_border, label='Castellated pad'),
        mlines.Line2D([], [], color=BOND, linewidth=1.5, label='Bond wire'),
    ]
    ax.legend(handles=legend_items, loc='upper right',
              fontsize=7, framealpha=0.9, edgecolor=OUTLINE,
              facecolor=PANEL, labelcolor=TEXT)

    # ── axes ──────────────────────────────────────────────────────────────────
    margin = 2.4
    ax.set_xlim(-half - margin, half + margin)
    ax.set_ylim(-half - margin, half + margin)
    ax.set_xlabel('mm', fontsize=9, color=MUTED)
    ax.set_ylabel('mm', fontsize=9, color=MUTED)
    ax.set_title('CSAC-1  LCC-20 Package - Top View', fontsize=13, fontweight='bold', pad=12, color=TEXT)
    ax.text(0, half + 1.15, 'Concept package sheet with the same palette as the architecture graphics.',
            ha='center', va='bottom', fontsize=8, color=MUTED)
    ax.grid(True, linestyle=':', linewidth=0.5, color='#1d2b42', zorder=0)
    ax.tick_params(labelsize=8, colors=MUTED)

    fig.tight_layout()
    save(fig, 'lcc20_package.png')


# ═══════════════════════════════════════════════════════════════════════════════
# 2.  CROSS-SECTION VIEW
# ═══════════════════════════════════════════════════════════════════════════════

def draw_cross_section():
    fig, ax = plt.subplots(figsize=(12, 6))
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(PANEL)
    ax.set_aspect('equal')

    # ── layer stack (bottom → top) ────────────────────────────────────────────
    # Each entry: (label, colour, thickness_mm, hatch)
    W = 9.0   # drawing width (mm)
    X0 = 0.0  # left edge

    layers = [
        ('PCB Substrate\n(FR-4 / AlN)',      '#6d737c', 1.50, None),
        ('Solder Paste\n(SAC305)',           '#8b9099', 0.15, '//'),
        ('LCC Ceramic Body\n(Al2O3)',        CERAMIC, 1.50, None),
        ('Die Attach Epoxy\n(low outgas)',   '#71452a', 0.10, None),
        ('Si Die\n(3x3 mm)',                 DIE_FILL, 0.50, None),
        ('Ar/N2 Fill\n(cavity atmosphere)',  '#3e2346', 0.60, None),
        ('Glass Lid / Window\n(borosilicate)', '#6ed4ff', 0.30, '\\\\'),
        ('Metal Lid\n(Kovar hermetic seal)', '#505965', 0.30, '..'),
    ]

    y_cur = 0.0
    layer_centres = []

    for label, color, thick, hatch in layers:
        rect = patches.FancyBboxPatch((X0, y_cur), W, thick,
                                       boxstyle='square,pad=0',
                                       linewidth=1.0, edgecolor=OUTLINE,
                                       facecolor=color, hatch=hatch,
                                       zorder=3)
        ax.add_patch(rect)
        layer_centres.append(y_cur + thick / 2)
        y_cur += thick

    total_height = y_cur

    # ── cavity (white rectangle inside Si die layer + Ar fill) ────────────────
    # cavity spans: die_attach top + die + Ar fill layers  → visually inside die+fill
    # die layer starts at y=1.5+0.15+1.5+0.1 = 3.25
    die_y = sum(t for _, _, t, _ in layers[:4])   # bottom of Si die
    cav_w = 1.5
    cav_h = layers[4][2] + layers[5][2]           # die + Ar fill
    cav_x = X0 + (W - cav_w) / 2
    cav_rect = patches.Rectangle((cav_x, die_y), cav_w, cav_h,
                                   linewidth=1.2, edgecolor=CAVITY_EDGE,
                                   facecolor=CAVITY_FILL, zorder=4)
    ax.add_patch(cav_rect)
    ax.text(cav_x + cav_w / 2, die_y + cav_h / 2,
            'Cs vapour\ncavity', ha='center', va='center',
            fontsize=7, color='#f2d9ff', zorder=5, style='italic')

    # ── layer labels (right side) ─────────────────────────────────────────────
    label_x = X0 + W + 0.2
    y_cur2 = 0.0
    for (label, color, thick, _), yc in zip(layers, layer_centres):
        ax.text(label_x, yc, label,
                ha='left', va='center', fontsize=7.5,
                color=TEXT, zorder=6,
                bbox=dict(boxstyle='round,pad=0.15', facecolor=color,
                           edgecolor=OUTLINE, alpha=0.9, linewidth=0.7))
        # leader line
        ax.plot([X0 + W, label_x - 0.05], [yc, yc],
                color=MUTED, linewidth=0.6, linestyle=':', zorder=5)
        y_cur2 += thick

    # ── dimension arrows (left side) ─────────────────────────────────────────
    arrow_x = -1.6

    def dim_arrow(y_bot, y_top, label, x=arrow_x, color=TEXT):
        ax.annotate('', xy=(x, y_top), xytext=(x, y_bot),
                    arrowprops=dict(arrowstyle='<->', color=color,
                                   lw=1.1, mutation_scale=8))
        ax.text(x - 0.12, (y_bot + y_top) / 2, label,
                ha='right', va='center', fontsize=7, color=color,
                rotation=90)

    # total height
    dim_arrow(0, total_height, f'Total\n{total_height:.2f} mm', x=-1.0, color=TEXT)

    # die height
    die_top = die_y + layers[4][2]
    dim_arrow(die_y, die_top, f'Die\n{layers[4][2]:.2f} mm', x=-1.9, color=ACCENT)

    # cavity depth
    dim_arrow(die_y, die_y + cav_h, f'Cavity\n{cav_h:.2f} mm', x=-2.7, color=THERMAL)

    # ── material / thickness callouts on layers ───────────────────────────────
    y_cur3 = 0.0
    for label, color, thick, _ in layers:
        ax.text(X0 + W / 2, y_cur3 + thick / 2,
                f'{thick*1000:.0f} µm',
                ha='center', va='center', fontsize=6.5,
                color=TEXT, zorder=6, alpha=0.72,
                fontweight='bold')
        y_cur3 += thick

    # ── axes ──────────────────────────────────────────────────────────────────
    ax.set_xlim(-3.2, X0 + W + 4.5)
    ax.set_ylim(-0.4, total_height + 0.5)
    ax.set_xlabel('Width (mm)', fontsize=9, color=MUTED)
    ax.set_ylabel('Height (mm)', fontsize=9, color=MUTED)
    ax.set_title('CSAC-1 Package Cross-Section', fontsize=13,
                 fontweight='bold', pad=12, color=TEXT)
    ax.text(0.02, 0.98, 'CONCEPT PACKAGE STACK', transform=ax.transAxes,
            ha='left', va='top', fontsize=8, color=TEXT,
            bbox=dict(boxstyle='round,pad=0.25,rounding_size=0.18',
                      facecolor=PANEL, edgecolor=ACCENT, linewidth=1.0))
    ax.tick_params(labelsize=8, colors=MUTED)

    # x-ticks only at package edges
    ax.set_xticks([X0, X0 + W])
    ax.set_xticklabels(['0', f'{W} mm'])

    fig.tight_layout()
    save(fig, 'cross_section.png')


# ═══════════════════════════════════════════════════════════════════════════════
# 3.  PACKAGE SUMMARY MARKDOWN
# ═══════════════════════════════════════════════════════════════════════════════

def write_summary():
    md = """\
# CSAC-1 Package Design Summary

## Package Specification

| Parameter | Value |
|-----------|-------|
| Package type | LCC-20 (Leadless Chip Carrier, 20 pads) |
| Body dimensions | 7.0 mm × 7.0 mm × 4.35 mm (H) |
| Die cavity | 3.5 mm × 3.5 mm × 1.1 mm deep |
| Pad pitch | 1.2 mm |
| Pad size | 0.8 mm × 0.6 mm (W × D) |
| Pads per side | 5 (4 sides) |
| Die size | 3.0 mm × 3.0 mm × 0.5 mm |
| Cavity window | Ø 1.5 mm borosilicate glass |
| Cavity atmosphere | Ar/N₂ (inert, <1 ppm O₂/H₂O) |
| Hermetic seal | Metal lid, seam-weld or solder-seal |
| Thermal resistance junction-to-case | θ_jc ≈ 15 °C/W |
| Thermal resistance junction-to-ambient | θ_ja ≈ 45 °C/W |
| Operating temperature | −40 °C to +85 °C |
| Storage temperature | −55 °C to +125 °C |
| Package material | 96% Al₂O₃ multilayer ceramic |
| Lid material | Kovar (Fe-Ni-Co), gold-plated |
| Marking | `CSAC-1 / YYXX` (YY = year, XX = lot) |

---

## Pin Assignment (LCC-20, CCW from Pin 1)

| Pin | Signal | Description |
|-----|--------|-------------|
| 1   | NC     | No connect (left side, pin 1 marker) |
| 2   | NC     | No connect |
| 3   | NC     | No connect |
| 4   | NC     | No connect |
| 5   | NC     | No connect |
| 6   | VCC    | +3.3 V supply |
| 7   | GND    | Ground |
| 8   | HTR+   | Heater positive drive |
| 9   | HTR−   | Heater negative / return |
| 10  | RTD+   | RTD sense positive |
| 11  | RTD−   | RTD sense negative |
| 12  | CLK    | SPI clock input |
| 13  | DATA   | SPI data (MOSI/MISO) |
| 14  | NC     | No connect |
| 15  | NC     | No connect |
| 16  | NC     | No connect |
| 17  | NC     | No connect |
| 18  | NC     | No connect |
| 19  | NC     | No connect |
| 20  | NC     | No connect |

> **Note:** NC pads should be left floating on the PCB (do not connect to GND plane —
> prevents thermal shorts from affecting heater control accuracy).

---

## Layer Stack (bottom to top)

| Layer | Material | Thickness |
|-------|----------|-----------|
| PCB substrate | FR-4 or AlN (preferred for thermal) | 1.50 mm |
| Solder paste | SAC305 (Sn-Ag-Cu lead-free) | 0.15 mm |
| LCC ceramic body | Al₂O₃ multilayer | 1.50 mm |
| Die attach epoxy | Low-outgassing Ag-filled epoxy (≤50 ppm TML) | 0.10 mm |
| Si die | CSAC physics/ASIC die | 0.50 mm |
| Cavity atmosphere | Ar/N₂ fill | 0.60 mm |
| Glass window | Borosilicate, AR-coated (795 nm) | 0.30 mm |
| Metal lid | Kovar hermetic seal lid | 0.30 mm |
| **Total** | | **4.35 mm** |

---

## Key Assembly Notes

### Die Attach
- Use **low-outgassing silver-filled epoxy** (e.g., Loctite Ablestik 8175 or equivalent).
- TML (Total Mass Loss) spec: **≤ 50 ppm** at 125 °C / 24 h per ASTM E595.
- CVCM (Collected Volatile Condensable Material): **≤ 10 ppm**.
- Cure: 150 °C / 60 min in N₂ atmosphere (prevent oxidation of Ag filler).
- Die attach fillet: ≤ 50 µm climb on die sidewall.

### Cavity Seal / Lid Atmosphere
- Purge cavity with **Ar/N₂ (99.999%)** immediately before seam-welding.
- Residual O₂: **< 100 ppm**; H₂O: **< 50 ppm** (dew point ≤ −60 °C).
- Perform lid seal in glove-box or vacuum chamber with controlled backfill.
- Seal integrity: fine-leak test per MIL-STD-883 Method 1014 (He leak rate < 5×10⁻⁹ atm·cc/s).

### Reflow Profile (PCB Assembly)
| Phase | Temperature | Duration |
|-------|-------------|----------|
| Preheat | 25 → 150 °C | 60–90 s |
| Soak | 150–180 °C | 60–120 s |
| Reflow peak | 245–260 °C | ≤ 30 s above 217 °C |
| Cool-down | 260 → 25 °C | ≥ 2 °C/s |
- Max package body temperature: **260 °C** (do not exceed — glass window AR coating risk).
- Use **no-clean flux** (halide-free); aqueous wash not recommended (hermetic risk).

### Handling
- ESD class: HBM 2000 V (Class 2).
- Moisture sensitivity: MSL-1 (unlimited floor life at ≤ 30 °C/85% RH) — hermetic package.
- Storage: dry-pack not required; recommend sealed bag with desiccant for long-term (>12 mo).

### PCB Footprint Recommendation
- Land pattern: IPC-7351 LCC20 (7.0 × 7.0 mm body), pad 0.8 × 0.6 mm, pitch 1.2 mm.
- Courtyard: 9.0 × 9.0 mm minimum.
- Thermal relief: **avoid** on HTR± and RTD± pads — use solid fill for accurate RTD readings.

---

## Marking

Top-side laser mark (white):

```
CSAC-1
YYXX
```

- `YY` = 2-digit year (e.g., `26` for 2026)
- `XX` = 2-digit lot code (00–99)

Pin 1 indicator: bevelled corner + silkscreen dot on PCB.
"""

    path = os.path.join(OUT_DIR, 'package_summary.md')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(md)
    print(f"Saved: {path}")


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    print("Generating CSAC-1 package design files …")
    draw_lcc20()
    draw_cross_section()
    write_summary()
    print("Done.")
