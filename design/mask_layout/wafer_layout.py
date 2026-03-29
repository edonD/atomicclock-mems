"""
wafer_layout.py — CSAC Wafer Layout Generator
Tiles csac_cell_v1.gds onto a 100 mm wafer with 150 µm dicing lanes.
Outputs: wafer_layout.gds, wafer_layout_preview.png
"""

import math
import numpy as np
import gdstk
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).parent
INPUT_GDS  = SCRIPT_DIR / "csac_cell_v1.gds"
OUTPUT_GDS = SCRIPT_DIR / "wafer_layout.gds"
OUTPUT_PNG = SCRIPT_DIR / "wafer_layout_preview.png"

# ── Wafer / die parameters (all in µm) ─────────────────────────────────────
WAFER_RADIUS   = 50_000          # 100 mm diameter
WAFER_CX       = 50_000          # wafer centre X
WAFER_CY       = 50_000          # wafer centre Y
FLAT_Y         = 2_500           # flat chord y-coordinate (from bottom of wafer box)
EDGE_EXCLUSION = 1_000           # keep dice 1 mm inside wafer edge

DIE_W   = 3_000                  # die width  µm
DIE_H   = 3_000                  # die height µm
LANE_W  = 150                    # dicing lane width µm
PITCH   = DIE_W + LANE_W         # = 3150 µm

GRID_ORIGIN_X = 500              # grid start X
GRID_ORIGIN_Y = 500              # grid start Y

WAFER_LAYER = 20                 # GDS layer for wafer outline
DIE_LAYER   = 0                  # die cell layer (already in cell)
N_CIRCLE_SEG = 360               # polygon segments for circle approximation

# ── Helper: point inside wafer (circle with flat) ──────────────────────────
def inside_wafer(x, y, r=WAFER_RADIUS - EDGE_EXCLUSION,
                 cx=WAFER_CX, cy=WAFER_CY, flat_y=FLAT_Y):
    """Return True if (x,y) is inside the wafer keep-in zone."""
    if (x - cx)**2 + (y - cy)**2 > r**2:
        return False
    if y < flat_y:
        return False
    return True

def die_fits(x0, y0):
    """All four corners of die at (x0,y0) must be inside wafer zone."""
    return (inside_wafer(x0,       y0      ) and
            inside_wafer(x0+DIE_W, y0      ) and
            inside_wafer(x0,       y0+DIE_H) and
            inside_wafer(x0+DIE_W, y0+DIE_H))

# ── Build wafer outline polygon (circle with flat) ─────────────────────────
def wafer_polygon(cx, cy, r, flat_y, n_seg=N_CIRCLE_SEG):
    """
    Approximate a circle with a flat (orientation flat at the bottom).
    The flat is a horizontal chord at y = flat_y.
    """
    pts = []
    for i in range(n_seg):
        theta = 2 * math.pi * i / n_seg
        px = cx + r * math.cos(theta)
        py = cy + r * math.sin(theta)
        if py < flat_y:
            py = flat_y          # clip to flat
        pts.append((px, py))
    # Remove consecutive duplicates on the flat
    clean = [pts[0]]
    for p in pts[1:]:
        if p != clean[-1]:
            clean.append(p)
    return clean

# ── 1. Read source GDS ─────────────────────────────────────────────────────
print(f"Reading {INPUT_GDS} …")
src_lib   = gdstk.read_gds(str(INPUT_GDS))
top_cells = src_lib.top_level()
assert top_cells, "No top-level cell found in source GDS"
unit_cell = top_cells[0]
print(f"  Unit cell: '{unit_cell.name}'")

# ── 2. Build output library ────────────────────────────────────────────────
lib = gdstk.Library(name="CSAC_WAFER", unit=1e-6, precision=1e-9)

# Copy unit cell into new library (including all dependencies)
# gdstk doesn't have a merge utility, so we add all cells from src_lib
cell_map = {}
for cell in src_lib.cells:
    lib.add(cell)
    cell_map[cell.name] = cell

unit_cell_ref = cell_map[unit_cell.name]

# ── 3. Create wafer top cell ───────────────────────────────────────────────
wafer_cell = lib.new_cell("WAFER_100MM_CSAC")

# Wafer outline polygon on layer 20
outline_pts = wafer_polygon(WAFER_CX, WAFER_CY, WAFER_RADIUS, FLAT_Y)
wafer_poly  = gdstk.Polygon(outline_pts, layer=WAFER_LAYER, datatype=0)
wafer_cell.add(wafer_poly)

# ── 4. Tile dice ───────────────────────────────────────────────────────────
die_positions = []   # list of (x0, y0) lower-left corners

# Grid spans: need enough rows/cols to cover the wafer
n_cols = int((2 * WAFER_RADIUS) / PITCH) + 2
n_rows = int((2 * WAFER_RADIUS) / PITCH) + 2

for row in range(n_rows):
    y0 = GRID_ORIGIN_Y + row * PITCH
    if y0 > WAFER_CY + WAFER_RADIUS:
        break
    for col in range(n_cols):
        x0 = GRID_ORIGIN_X + col * PITCH
        if x0 > WAFER_CX + WAFER_RADIUS:
            break
        if die_fits(x0, y0):
            die_positions.append((x0, y0))
            ref = gdstk.Reference(unit_cell_ref, origin=(x0, y0))
            wafer_cell.add(ref)

n_dice      = len(die_positions)
die_area    = DIE_W * DIE_H                          # µm²
wafer_area  = math.pi * WAFER_RADIUS**2              # µm²
fill_pct    = 100.0 * n_dice * die_area / wafer_area

print(f"\n-- Placement summary --")
print(f"  Die size          : {DIE_W} x {DIE_H} um")
print(f"  Die pitch         : {PITCH} um")
print(f"  Dicing lane width : {LANE_W} um")
print(f"  Edge exclusion    : {EDGE_EXCLUSION} um")
print(f"  Dice placed       : {n_dice}")
print(f"  Fill factor       : {fill_pct:.2f}%")
print(f"  Die positions (first 5): {die_positions[:5]}")

# ── 5. Write GDS ───────────────────────────────────────────────────────────
lib.write_gds(str(OUTPUT_GDS))
print(f"\nGDS written -> {OUTPUT_GDS}")

# ── 6. Preview PNG ─────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(10, 10), dpi=150)
ax.set_aspect("equal")

# Convert µm → mm for display
def um2mm(v):
    return np.asarray(v) / 1000.0

# Wafer circle (gray filled)
theta_arr = np.linspace(0, 2 * math.pi, 1000)
wx = WAFER_CX + WAFER_RADIUS * np.cos(theta_arr)
wy = WAFER_CY + WAFER_RADIUS * np.sin(theta_arr)
# Apply flat clipping
wy = np.where(wy < FLAT_Y, FLAT_Y, wy)
ax.fill(um2mm(wx), um2mm(wy), color="#d0d0d0", zorder=1)
ax.plot(um2mm(wx), um2mm(wy), color="#888888", linewidth=0.8, zorder=2)

# Edge exclusion circle (dashed, for reference)
ex = WAFER_CX + (WAFER_RADIUS - EDGE_EXCLUSION) * np.cos(theta_arr)
ey = WAFER_CY + (WAFER_RADIUS - EDGE_EXCLUSION) * np.sin(theta_arr)
ey = np.where(ey < FLAT_Y, FLAT_Y, ey)
ax.plot(um2mm(ex), um2mm(ey), color="#aaaaaa", linewidth=0.5,
        linestyle="--", zorder=3, label="Edge exclusion")

# Dice rectangles
die_color  = "#4682B4"   # steel blue
die_edge   = "#1a1a1a"

for (x0, y0) in die_positions:
    rect = mpatches.Rectangle(
        (float(um2mm(x0)), float(um2mm(y0))),
        DIE_W / 1000.0,
        DIE_H / 1000.0,
        linewidth=0.3,
        edgecolor=die_edge,
        facecolor=die_color,
        zorder=4,
    )
    ax.add_patch(rect)

# Labels / title
yield_area = fill_pct
ax.set_title(
    f"CSAC Wafer Layout — 100 mm wafer, {n_dice} dice, {yield_area:.1f}% fill",
    fontsize=11, fontweight="bold", pad=10
)
ax.set_xlabel("X (mm)", fontsize=9)
ax.set_ylabel("Y (mm)", fontsize=9)

# Die count annotation
ax.text(
    float(um2mm(WAFER_CX)), float(um2mm(WAFER_CY + WAFER_RADIUS * 0.75)),
    f"{n_dice} dice",
    ha="center", va="center", fontsize=13, fontweight="bold",
    color="white",
    bbox=dict(boxstyle="round,pad=0.3", fc="#4682B4", ec="none", alpha=0.85),
    zorder=6,
)

# Scale bar: 10 mm
sb_x0   = um2mm(WAFER_CX + WAFER_RADIUS * 0.45)
sb_y0   = um2mm(FLAT_Y + 800)
sb_len  = 10.0   # mm
ax.plot([sb_x0, sb_x0 + sb_len], [sb_y0, sb_y0],
        color="black", linewidth=2, zorder=7)
ax.plot([sb_x0, sb_x0],         [sb_y0 - 0.3, sb_y0 + 0.3],
        color="black", linewidth=1.5, zorder=7)
ax.plot([sb_x0 + sb_len, sb_x0 + sb_len], [sb_y0 - 0.3, sb_y0 + 0.3],
        color="black", linewidth=1.5, zorder=7)
ax.text(float(sb_x0 + sb_len / 2), float(sb_y0 + 0.7),
        "10 mm", ha="center", va="bottom", fontsize=8, zorder=7)

# Axis limits with a bit of padding
pad_mm = 3
ax.set_xlim(float(um2mm(WAFER_CX - WAFER_RADIUS)) - pad_mm,
            float(um2mm(WAFER_CX + WAFER_RADIUS)) + pad_mm)
ax.set_ylim(float(um2mm(FLAT_Y)) - pad_mm,
            float(um2mm(WAFER_CY + WAFER_RADIUS)) + pad_mm)

ax.legend(loc="lower left", fontsize=7, framealpha=0.7)
ax.grid(True, linewidth=0.3, alpha=0.4)

plt.tight_layout()
fig.savefig(str(OUTPUT_PNG), dpi=150)
plt.close(fig)
print(f"Preview PNG written -> {OUTPUT_PNG}")
