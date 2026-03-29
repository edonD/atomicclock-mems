"""
csac_cell_v1.py
===============
GDS-II mask layout generator for the CSAC MEMS vapor cell chip.

Die: 3×3 mm Silicon
Technology: Borosilicate glass / Si anodic bond stack
Process: DRIE cavity etch, Pt sputtered heater + RTD, anodic bonding

Layer map
---------
  1  CAVITY      DRIE etch boundary
  2  PT_HEATER   Platinum serpentine heater trace
  3  PT_RTD      Platinum RTD meander
  4  BOND_RING   Anodic bonding frame
  5  DICING      Dicing lane outline
  6  OPTICAL_WIN Optical window (glass lid area)
 10  LABELS      Text annotations / pad labels

Usage
-----
  python csac_cell_v1.py

Outputs
-------
  csac_cell_v1.gds   — GDSII binary, send to foundry
  csac_cell_v1.svg   — SVG colour preview (open in browser or Inkscape)
  csac_cell_v1_preview.png — PNG raster via matplotlib
"""

import os
import sys
import math
import numpy as np

import gdstk
import matplotlib
matplotlib.use("Agg")          # headless rendering
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.collections import PatchCollection

# ---------------------------------------------------------------------------
# SCRIPT DIRECTORY — all outputs land here
# ---------------------------------------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
GDS_OUT    = os.path.join(SCRIPT_DIR, "csac_cell_v1.gds")
SVG_OUT    = os.path.join(SCRIPT_DIR, "csac_cell_v1.svg")
PNG_OUT    = os.path.join(SCRIPT_DIR, "csac_cell_v1_preview.png")

# ---------------------------------------------------------------------------
# LAYER CONSTANTS
# ---------------------------------------------------------------------------
L_CAVITY      = 1
L_PT_HEATER   = 2
L_PT_RTD      = 3
L_BOND_RING   = 4
L_DICING      = 5
L_OPTICAL_WIN = 6
L_LABELS      = 10

DT = 0   # datatype for all shapes

# ---------------------------------------------------------------------------
# DESIGN PARAMETERS  (all in micrometres)
# ---------------------------------------------------------------------------
DIE_W = 3000.0
DIE_H = 3000.0

# Circular DRIE cavity
CAVITY_CX   = 1500.0
CAVITY_CY   = 1500.0
CAVITY_R    = 750.0      # diameter 1500 um

# Anodic bond ring
BOND_OUTER_MARGIN = 100.0    # from die edge inward to outer edge of ring
BOND_RING_WIDTH   = 250.0    # ring width

# Dicing lane
DICING_WIDTH = 100.0

# Optical window (glass lid)
OPT_W = 1800.0
OPT_H = 1800.0
OPT_CX = 1500.0
OPT_CY = 1500.0

# Platinum heater (serpentine, lower-left quadrant)
HTR_CX       = 600.0     # serpentine block centre
HTR_CY       = 600.0
HTR_AREA_W   = 600.0     # bounding box of serpentine block
HTR_AREA_H   = 600.0
HTR_N_LINES  = 8         # number of parallel lines
HTR_TRACE_W  = 50.0      # trace width um
HTR_TRACE_T  = 0.0002    # 200 nm thickness (informational only)

# Platinum RTD (meander, upper-right quadrant)
RTD_CX       = 2400.0
RTD_CY       = 2400.0
RTD_AREA_W   = 300.0
RTD_AREA_H   = 300.0
RTD_N_LINES  = 10        # enough meander lines for ~1 mm length
RTD_TRACE_W  = 20.0

# Electrical pads
PAD_W       = 150.0
PAD_H       = 150.0
PAD_Y_CTR   = 150.0      # pad centre y
PAD_X_CTRS  = [200, 550, 900, 1250, 1600, 1950, 2300, 2650]
PAD_LABELS  = ["VCC", "GND", "HTR+", "HTR-", "RTD+", "RTD-", "SPI_CLK", "SPI_DATA"]


# ---------------------------------------------------------------------------
# HELPER: build a serpentine trace as a list of gdstk.Polygon rectangles
# ---------------------------------------------------------------------------
def serpentine_rects(cx, cy, area_w, area_h, n_lines, trace_w, layer, datatype=0):
    """
    Build a serpentine (boustrophedon) pattern centred at (cx, cy).

    The pattern has `n_lines` parallel horizontal runs connected by
    U-bends at alternating left/right ends.  Each run is a long thin
    rectangle; the connecting bends are small square end-caps.

    Returns a flat list of gdstk.Polygon objects.
    """
    polys = []

    # Available height divided equally among n_lines runs + gaps
    # pitch = area_h / n_lines
    pitch  = area_h / n_lines
    run_h  = trace_w                 # height of each horizontal strip
    run_w  = area_w                  # full width each run spans

    # Bend half-width (the U-turn connector at each end)
    bend_w = trace_w                 # same width as the trace

    x0 = cx - area_w / 2.0
    y0 = cy - area_h / 2.0

    for i in range(n_lines):
        # Centre y of this line
        yc = y0 + (i + 0.5) * pitch

        # Horizontal run
        r = gdstk.rectangle(
            (x0, yc - trace_w / 2),
            (x0 + run_w, yc + trace_w / 2),
            layer=layer, datatype=datatype
        )
        polys.append(r)

        # End-cap bend connecting to next line (except after last line)
        if i < n_lines - 1:
            yc_next = y0 + (i + 1 + 0.5) * pitch
            if i % 2 == 0:
                # right-side bend
                bx = x0 + run_w - trace_w / 2
            else:
                # left-side bend
                bx = x0 + trace_w / 2

            # The bend connects (yc) to (yc_next) at x = bx
            b = gdstk.rectangle(
                (bx - trace_w / 2, yc - trace_w / 2),
                (bx + trace_w / 2, yc_next + trace_w / 2),
                layer=layer, datatype=datatype
            )
            polys.append(b)

    return polys


# ---------------------------------------------------------------------------
# HELPER: bond ring as two overlapping rectangles (outer frame, inner hole)
# gdstk supports boolean ops; alternatively use a polygon outline.
# We just use a rectangle border (4 edge strips).
# ---------------------------------------------------------------------------
def bond_ring_polys(die_w, die_h, outer_margin, ring_width, layer, datatype=0):
    """
    Return four rectangles forming a closed rectangular frame.
    Outer edge of ring: outer_margin from die edge.
    Inner edge of ring: outer_margin + ring_width from die edge.
    """
    om = outer_margin
    rw = ring_width
    polys = []

    # Bottom strip
    polys.append(gdstk.rectangle(
        (om, om), (die_w - om, om + rw),
        layer=layer, datatype=datatype))
    # Top strip
    polys.append(gdstk.rectangle(
        (om, die_h - om - rw), (die_w - om, die_h - om),
        layer=layer, datatype=datatype))
    # Left strip
    polys.append(gdstk.rectangle(
        (om, om + rw), (om + rw, die_h - om - rw),
        layer=layer, datatype=datatype))
    # Right strip
    polys.append(gdstk.rectangle(
        (die_w - om - rw, om + rw), (die_w - om, die_h - om - rw),
        layer=layer, datatype=datatype))

    return polys


# ---------------------------------------------------------------------------
# HELPER: dicing lane (four strips around perimeter)
# ---------------------------------------------------------------------------
def dicing_lane_polys(die_w, die_h, lane_w, layer, datatype=0):
    polys = []
    polys.append(gdstk.rectangle((0, 0),          (die_w, lane_w),          layer=layer, datatype=datatype))   # bottom
    polys.append(gdstk.rectangle((0, die_h - lane_w), (die_w, die_h),       layer=layer, datatype=datatype))   # top
    polys.append(gdstk.rectangle((0, lane_w),      (lane_w, die_h - lane_w), layer=layer, datatype=datatype))  # left
    polys.append(gdstk.rectangle((die_w - lane_w, lane_w), (die_w, die_h - lane_w), layer=layer, datatype=datatype))  # right
    return polys


# ---------------------------------------------------------------------------
# BUILD LIBRARY
# ---------------------------------------------------------------------------
print("=" * 60)
print(f"gdstk version : {gdstk.__version__}")
print(f"Output GDS    : {GDS_OUT}")
print("=" * 60)

lib  = gdstk.Library(name="CSAC_CELL_V1", unit=1e-6, precision=1e-9)
cell = lib.new_cell("CSAC_V1")

shape_counts = {}

def add(layer_name, layer_id, shapes):
    """Add shapes to cell and tally."""
    if isinstance(shapes, (gdstk.Polygon,)):
        shapes = [shapes]
    for s in shapes:
        cell.add(s)
    shape_counts[layer_name] = shape_counts.get(layer_name, 0) + len(shapes)


# --- Layer 5: DICING lane (draw first so it appears at the bottom) ---------
add("DICING", L_DICING,
    dicing_lane_polys(DIE_W, DIE_H, DICING_WIDTH, L_DICING, DT))

# --- Layer 4: BOND RING -----------------------------------------------------
add("BOND_RING", L_BOND_RING,
    bond_ring_polys(DIE_W, DIE_H, BOND_OUTER_MARGIN, BOND_RING_WIDTH, L_BOND_RING, DT))

# --- Layer 6: OPTICAL WINDOW ------------------------------------------------
opt_rect = gdstk.rectangle(
    (OPT_CX - OPT_W / 2, OPT_CY - OPT_H / 2),
    (OPT_CX + OPT_W / 2, OPT_CY + OPT_H / 2),
    layer=L_OPTICAL_WIN, datatype=DT)
add("OPTICAL_WIN", L_OPTICAL_WIN, [opt_rect])

# --- Layer 1: CAVITY --------------------------------------------------------
cavity = gdstk.ellipse(
    (CAVITY_CX, CAVITY_CY),
    CAVITY_R,
    tolerance=0.5,       # ≈ 0.5 um tolerance → smooth circle
    layer=L_CAVITY, datatype=DT)
add("CAVITY", L_CAVITY, [cavity])

# --- Layer 2: PT_HEATER (serpentine, lower-left) ----------------------------
heater_polys = serpentine_rects(
    HTR_CX, HTR_CY, HTR_AREA_W, HTR_AREA_H,
    HTR_N_LINES, HTR_TRACE_W, L_PT_HEATER, DT)
add("PT_HEATER", L_PT_HEATER, heater_polys)

# Heater bond pads (two 150×150 um pads at the ends of the serpentine)
htr_pad_y   = HTR_CY - HTR_AREA_H / 2 - 50
htr_pad_xL  = HTR_CX - HTR_AREA_W / 2
htr_pad_xR  = HTR_CX + HTR_AREA_W / 2 - PAD_W
for px in [htr_pad_xL, htr_pad_xR]:
    cell.add(gdstk.rectangle(
        (px, htr_pad_y), (px + PAD_W, htr_pad_y + PAD_H),
        layer=L_PT_HEATER, datatype=DT))
shape_counts["PT_HEATER"] = shape_counts.get("PT_HEATER", 0) + 2

# --- Layer 3: PT_RTD (meander, upper-right) ---------------------------------
rtd_polys = serpentine_rects(
    RTD_CX, RTD_CY, RTD_AREA_W, RTD_AREA_H,
    RTD_N_LINES, RTD_TRACE_W, L_PT_RTD, DT)
add("PT_RTD", L_PT_RTD, rtd_polys)

# RTD bond pads
rtd_pad_y  = RTD_CY + RTD_AREA_H / 2 + 20
rtd_pad_xL = RTD_CX - RTD_AREA_W / 2
rtd_pad_xR = RTD_CX + RTD_AREA_W / 2 - PAD_W
for px in [rtd_pad_xL, rtd_pad_xR]:
    cell.add(gdstk.rectangle(
        (px, rtd_pad_y), (px + PAD_W, rtd_pad_y + PAD_H),
        layer=L_PT_RTD, datatype=DT))
shape_counts["PT_RTD"] = shape_counts.get("PT_RTD", 0) + 2

# --- Layer 10 / pads: ELECTRICAL PADS + LABELS ------------------------------
for xc, lbl in zip(PAD_X_CTRS, PAD_LABELS):
    # Pad rectangle on L_LABELS layer (also visible as a metal shape)
    cell.add(gdstk.rectangle(
        (xc - PAD_W / 2, PAD_Y_CTR - PAD_H / 2),
        (xc + PAD_W / 2, PAD_Y_CTR + PAD_H / 2),
        layer=L_LABELS, datatype=DT))

    # Polygonal text label above pad
    txt = gdstk.text(
        lbl,
        size=60,
        position=(xc - PAD_W / 2, PAD_Y_CTR + PAD_H / 2 + 10),
        layer=L_LABELS, datatype=DT)
    for p in txt:
        cell.add(p)

shape_counts["LABELS"] = len(PAD_X_CTRS)

# Die outline (informational — layer 0)
cell.add(gdstk.rectangle((0, 0), (DIE_W, DIE_H), layer=0, datatype=DT))

# Chip title label (centre)
title_txt = gdstk.text("CSAC_V1  3x3mm", size=80,
                        position=(DIE_W / 2 - 600, DIE_H - 180),
                        layer=L_LABELS, datatype=DT)
for p in title_txt:
    cell.add(p)

# Cavity depth annotation
depth_txt = gdstk.text("CAVITY 1000um DRIE", size=50,
                        position=(CAVITY_CX - 450, CAVITY_CY - 50),
                        layer=L_LABELS, datatype=DT)
for p in depth_txt:
    cell.add(p)

# ---------------------------------------------------------------------------
# WRITE GDS
# ---------------------------------------------------------------------------
lib.write_gds(GDS_OUT)

gds_size = os.path.getsize(GDS_OUT)
bbox = cell.bounding_box()

print("\n--- Layer shape counts ---")
for name, cnt in sorted(shape_counts.items()):
    print(f"  {name:15s}: {cnt} polygon(s)")

print(f"\nCell bounding box : {bbox}")
print(f"GDS file size     : {gds_size:,} bytes  ({gds_size/1024:.1f} kB)")
print(f"GDS written to    : {GDS_OUT}")

# ---------------------------------------------------------------------------
# SVG PREVIEW (gdstk built-in)
# ---------------------------------------------------------------------------
LAYER_COLORS = {
    (0,  0): {"fill": "none",    "stroke": "#888888", "stroke-width": "2"},
    (L_CAVITY,      DT): {"fill": "#3399ff", "stroke": "#1155cc", "stroke-width": "1", "opacity": "0.55"},
    (L_PT_HEATER,   DT): {"fill": "#ff3333", "stroke": "#aa0000", "stroke-width": "1", "opacity": "0.75"},
    (L_PT_RTD,      DT): {"fill": "#ff8800", "stroke": "#cc5500", "stroke-width": "1", "opacity": "0.75"},
    (L_BOND_RING,   DT): {"fill": "#33cc55", "stroke": "#117733", "stroke-width": "1", "opacity": "0.60"},
    (L_DICING,      DT): {"fill": "none",    "stroke": "#666666", "stroke-width": "3", "stroke-dasharray": "40,20"},
    (L_OPTICAL_WIN, DT): {"fill": "#ffee44", "stroke": "#aa9900", "stroke-width": "1", "opacity": "0.35"},
    (L_LABELS,      DT): {"fill": "#ffffff", "stroke": "none",    "opacity": "0.85"},
}

cell.write_svg(
    SVG_OUT,
    scaling=0.12,          # 3000 um × 0.12 = 360 px wide
    background="#1a1a2e",
    shape_style=LAYER_COLORS,
    pad="3%",
)
print(f"SVG preview       : {SVG_OUT}")

# ---------------------------------------------------------------------------
# PNG PREVIEW via matplotlib
# ---------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(8, 8), facecolor="#1a1a2e")
ax.set_facecolor("#1a1a2e")
ax.set_aspect("equal")
ax.set_xlim(-50, DIE_W + 50)
ax.set_ylim(-50, DIE_H + 50)
ax.set_title("CSAC_V1 — Mask Layout Preview", color="white", fontsize=13, pad=10)
ax.tick_params(colors="white")
for spine in ax.spines.values():
    spine.set_edgecolor("#555555")

# Colour map for matplotlib rendering
MPL_COLORS = {
    0:            ("#888888", "none",    0.5,  1.5),   # die outline
    L_CAVITY:     ("#3399ff", "#3399ff", 0.50, 0.8),
    L_PT_HEATER:  ("#ff3333", "#ff3333", 0.75, 0.8),
    L_PT_RTD:     ("#ff8800", "#ff8800", 0.75, 0.8),
    L_BOND_RING:  ("#33cc55", "#33cc55", 0.55, 0.8),
    L_DICING:     ("#666666", "none",    1.0,  1.5),
    L_OPTICAL_WIN:("#ffee44", "#ffee44", 0.30, 0.5),
    L_LABELS:     ("#ffffff", "#ffffff", 0.85, 0.0),
}

# Collect all polygons from cell, render by layer
polys_by_layer: dict[int, list] = {}
for poly in cell.polygons:
    lay = poly.layer
    polys_by_layer.setdefault(lay, []).append(poly)

render_order = [L_OPTICAL_WIN, L_BOND_RING, L_DICING, L_CAVITY,
                L_PT_HEATER, L_PT_RTD, L_LABELS, 0]

for lay in render_order:
    if lay not in polys_by_layer:
        continue
    ec, fc, alpha, lw = MPL_COLORS.get(lay, ("#aaaaaa", "#aaaaaa", 0.5, 0.5))
    for poly in polys_by_layer[lay]:
        pts = poly.points
        patch = plt.Polygon(pts, closed=True,
                            facecolor=fc if fc != "none" else "none",
                            edgecolor=ec,
                            linewidth=lw,
                            alpha=alpha)
        ax.add_patch(patch)

# Legend
legend_entries = [
    mpatches.Patch(color="#3399ff", alpha=0.6, label="L1 CAVITY (DRIE)"),
    mpatches.Patch(color="#ff3333", alpha=0.8, label="L2 PT_HEATER"),
    mpatches.Patch(color="#ff8800", alpha=0.8, label="L3 PT_RTD"),
    mpatches.Patch(color="#33cc55", alpha=0.65, label="L4 BOND_RING"),
    mpatches.Patch(color="#666666", alpha=0.7, label="L5 DICING"),
    mpatches.Patch(color="#ffee44", alpha=0.45, label="L6 OPTICAL_WIN"),
    mpatches.Patch(color="#ffffff", alpha=0.85, label="L10 LABELS/PADS"),
]
ax.legend(handles=legend_entries, loc="upper right",
          facecolor="#333355", edgecolor="#888888",
          labelcolor="white", fontsize=8, framealpha=0.85)

# Dimension annotations
ax.annotate("", xy=(DIE_W, -35), xytext=(0, -35),
            arrowprops=dict(arrowstyle="<->", color="white", lw=1.2))
ax.text(DIE_W / 2, -42, "3000 um", ha="center", va="top", color="white", fontsize=8)

ax.annotate("", xy=(DIE_W + 35, DIE_H), xytext=(DIE_W + 35, 0),
            arrowprops=dict(arrowstyle="<->", color="white", lw=1.2))
ax.text(DIE_W + 40, DIE_H / 2, "3000 um", ha="left", va="center",
        color="white", fontsize=8, rotation=90)

plt.tight_layout()
plt.savefig(PNG_OUT, dpi=200, facecolor=fig.get_facecolor())
plt.close()
print(f"PNG preview       : {PNG_OUT}")

# ---------------------------------------------------------------------------
# FINAL SUMMARY
# ---------------------------------------------------------------------------
print("\n========================================")
print("  CSAC_CELL_V1  GDS generation complete")
print("========================================")
print(f"  Die            : {DIE_W:.0f} x {DIE_H:.0f} um")
print(f"  Cavity         : dia {CAVITY_R*2:.0f} um @ ({CAVITY_CX:.0f}, {CAVITY_CY:.0f}) um")
print(f"  Cavity depth   : 1000 um (DRIE, encoded in process traveler)")
print(f"  Heater area    : {HTR_AREA_W:.0f}x{HTR_AREA_H:.0f} um, {HTR_N_LINES} runs x {HTR_TRACE_W:.0f} um wide")
print(f"  RTD area       : {RTD_AREA_W:.0f}x{RTD_AREA_H:.0f} um, {RTD_N_LINES} runs x {RTD_TRACE_W:.0f} um wide")
print(f"  Bond ring      : {BOND_RING_WIDTH:.0f} um wide, {BOND_OUTER_MARGIN:.0f} um from edge")
print(f"  Dicing lane    : {DICING_WIDTH:.0f} um")
print(f"  Pads           : {len(PAD_X_CTRS)} x {PAD_W:.0f}x{PAD_H:.0f} um")
print(f"  GDS size       : {gds_size/1024:.1f} kB")
print("========================================")
print("  To inspect in KLayout:")
print(f"    klayout {GDS_OUT}")
print("========================================")
