#!/usr/bin/env python3
"""
CSAC Chip Cross-Section Diagram
Shows all layers: silicon, CMOS electronics, Pyrex cavity, Rb vapor, N2, optical path

Author: CSAC team
Date: 2026-03-30
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Rectangle, FancyArrowPatch
from pathlib import Path

BASE = Path(__file__).parent

fig, ax = plt.subplots(figsize=(16, 10), dpi=150)
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)
ax.set_aspect('equal')

# ─────────────────────────────────────────────────────────────────────────────
# BACKGROUND
# ─────────────────────────────────────────────────────────────────────────────
ax.add_patch(Rectangle((0, 0), 100, 100, facecolor='#0d1117', edgecolor='none'))

# ─────────────────────────────────────────────────────────────────────────────
# LAYER DESCRIPTIONS (Y-axis = depth from top)
# ─────────────────────────────────────────────────────────────────────────────
# Y=85-100: Pyrex 7740 lid (sealed top)
# Y=70-85:  Rb-87 vapor + N2 buffer gas in sealed cavity (1 mm deep)
# Y=65-70:  Glass frit seal / anodic bond interface
# Y=40-65:  Silicon substrate (post-CMOS thinned to ~200 µm) with cavity etched from back
# Y=20-40:  CMOS metal layers (M1-M4, contact vias)
# Y=15-20:  Polysilicon + gate oxide
# Y=0-15:   Si substrate (bulk + well structure)

# ─────────────────────────────────────────────────────────────────────────────
# 1. TOP PYREX LID
# ─────────────────────────────────────────────────────────────────────────────
pyrex_top = Rectangle((5, 85), 90, 15, facecolor='#4a9eff', edgecolor='#1f6feb', linewidth=2)
ax.add_patch(pyrex_top)
ax.text(50, 92, 'Pyrex 7740 Lid (sealed top)', ha='center', va='center',
        fontsize=11, fontweight='bold', color='white')
ax.text(50, 87.5, 'Optically transparent, thermally matched to Si', ha='center', va='center',
        fontsize=8, color='#c0d9ff', style='italic')

# ─────────────────────────────────────────────────────────────────────────────
# 2. OPTICAL CAVITY & VAPOR
# ─────────────────────────────────────────────────────────────────────────────
# Rb-87 vapor (red glow)
vapor = Rectangle((10, 70), 80, 15, facecolor='#6b1515', edgecolor='#ff6b6b', linewidth=1.5, alpha=0.7)
ax.add_patch(vapor)
ax.text(50, 77.5, 'Rb-87 Atoms + N₂ Buffer Gas (76.6 Torr)', ha='center', va='center',
        fontsize=10, fontweight='bold', color='#ffcccc')
ax.text(50, 72, '≈1 mm³ sealed cavity, ~10¹⁴ atoms/cm³', ha='center', va='center',
        fontsize=8, color='#ff9999')

# Add atom icons
for x in [20, 35, 50, 65, 80]:
    circle = mpatches.Circle((x, 75), 1.2, color='#ff8888', alpha=0.6)
    ax.add_patch(circle)

# ─────────────────────────────────────────────────────────────────────────────
# 3. ANODIC BOND INTERFACE
# ─────────────────────────────────────────────────────────────────────────────
bond_interface = Rectangle((5, 67.5), 90, 2.5, facecolor='#8b4513', edgecolor='#d4a574', linewidth=2, linestyle='--')
ax.add_patch(bond_interface)
ax.text(2, 68.75, 'Anodic Bond\n(350°C, 800V)', ha='right', va='center',
        fontsize=7, color='#d4a574', fontweight='bold')

# ─────────────────────────────────────────────────────────────────────────────
# 4. SILICON SUBSTRATE (with CMOS electronics underneath)
# ─────────────────────────────────────────────────────────────────────────────
si_bulk = Rectangle((5, 15), 90, 52.5, facecolor='#1a3a52', edgecolor='#4a7ba7', linewidth=2)
ax.add_patch(si_bulk)
ax.text(50, 55, 'Silicon Substrate (200 µm thick after thinning)', ha='center', va='center',
        fontsize=10, fontweight='bold', color='#7fb3d5')

# Cavity outline (DRIE etched from back) — empty space inside Si
cavity_void = Rectangle((15, 42), 70, 12, facecolor='#0d1117', edgecolor='#ff6b6b', linewidth=2, linestyle=':')
ax.add_patch(cavity_void)
ax.text(50, 48, 'Cavity Volume\n(etched via DRIE from backside)', ha='center', va='center',
        fontsize=8, color='#ff9999', style='italic')

# ─────────────────────────────────────────────────────────────────────────────
# 5. CMOS ELECTRONICS LAYERS (inside the Si)
# ─────────────────────────────────────────────────────────────────────────────

# Heater resistor (polysilicon, on top of CMOS)
heater_left = Rectangle((8, 35), 8, 6, facecolor='#ff6b35', edgecolor='#ff4500', linewidth=1.5)
ax.add_patch(heater_left)
ax.text(12, 38, 'Heater\n(polySi)', ha='center', va='center', fontsize=7, color='white', fontweight='bold')

heater_right = Rectangle((84, 35), 8, 6, facecolor='#ff6b35', edgecolor='#ff4500', linewidth=1.5)
ax.add_patch(heater_right)
ax.text(88, 38, 'Heater\n(polySi)', ha='center', va='center', fontsize=7, color='white', fontweight='bold')

# Photodiode (n-well/p-substrate junction, center-ish)
pd_box = Rectangle((46, 28), 8, 5, facecolor='#79c0ff', edgecolor='#1f6feb', linewidth=1.5)
ax.add_patch(pd_box)
ax.text(50, 30.5, 'Photo-\ndiode\n(n-well)', ha='center', va='center', fontsize=7, color='white', fontweight='bold')

# VCO (LC-tank with inductors, varactors)
vco_box = Rectangle((15, 20), 12, 7, facecolor='#a371f7', edgecolor='#7928ca', linewidth=1.5)
ax.add_patch(vco_box)
ax.text(21, 23.5, 'VCO\n(LC-tank)\n6.835 GHz', ha='center', va='center', fontsize=7, color='white', fontweight='bold')

# TIA (opamp + feedback resistor)
tia_box = Rectangle((30, 20), 12, 7, facecolor='#79c0ff', edgecolor='#0969da', linewidth=1.5)
ax.add_patch(tia_box)
ax.text(36, 23.5, 'TIA\n(opamp +\nRf = 1MΩ)', ha='center', va='center', fontsize=7, color='white', fontweight='bold')

# Frequency divider (logic gates, counters)
fdiv_box = Rectangle((45, 20), 12, 7, facecolor='#56d364', edgecolor='#238636', linewidth=1.5)
ax.add_patch(fdiv_box)
ax.text(51, 23.5, 'Freq Div\n(÷2³³)\n1 Hz out', ha='center', va='center', fontsize=7, color='white', fontweight='bold')

# PID controller (logic)
pid_box = Rectangle((60, 20), 12, 7, facecolor='#f78166', edgecolor='#da3633', linewidth=1.5)
ax.add_patch(pid_box)
ax.text(66, 23.5, 'PID Loop\n(error,\nintegral)', ha='center', va='center', fontsize=7, color='white', fontweight='bold')

# DAC (resistor ladder or capacitive)
dac_box = Rectangle((75, 20), 12, 7, facecolor='#ffc300', edgecolor='#d0883e', linewidth=1.5)
ax.add_patch(dac_box)
ax.text(81, 23.5, 'DAC\n(10-bit)\nVtune out', ha='center', va='center', fontsize=7, color='white', fontweight='bold')

# ─────────────────────────────────────────────────────────────────────────────
# 6. SUBSTRATE / BULK
# ─────────────────────────────────────────────────────────────────────────────
substrate = Rectangle((5, 0), 90, 15, facecolor='#0a1929', edgecolor='#1f6feb', linewidth=2)
ax.add_patch(substrate)
ax.text(50, 7.5, 'Si Bulk / Well Structure + Bond Pads (periphery)', ha='center', va='center',
        fontsize=9, fontweight='bold', color='#58a6ff')

# Wire bond pads around perimeter
for x in [8, 16, 24, 32, 40, 48, 56, 64, 72, 80, 88]:
    pad = Rectangle((x-1, 2), 2, 4, facecolor='#d0883e', edgecolor='#ff9944', linewidth=1)
    ax.add_patch(pad)

# ─────────────────────────────────────────────────────────────────────────────
# OPTICAL PATH ARROWS
# ─────────────────────────────────────────────────────────────────────────────

# Incoming laser (from external VCSEL or fiber)
arrow_in = FancyArrowPatch((2, 77.5), (10, 77.5), mutation_scale=30, color='#ff4444', linewidth=2.5)
ax.add_patch(arrow_in)
ax.text(1, 82, 'Laser\ninput\n(780 nm)', ha='right', va='center', fontsize=8, color='#ff8888', fontweight='bold')

# Reflected/scattered light back to photodiode
arrow_out = FancyArrowPatch((50, 70), (50, 55), mutation_scale=20, color='#ffdd00', linewidth=2, linestyle='--')
ax.add_patch(arrow_out)
ax.text(55, 62.5, 'CPT\nabsorption\nvar.', ha='left', va='center', fontsize=8, color='#ffdd00', fontweight='bold')

# ─────────────────────────────────────────────────────────────────────────────
# SIGNAL FLOW ANNOTATIONS
# ─────────────────────────────────────────────────────────────────────────────

# Photodiode → TIA
arrow_pd_tia = FancyArrowPatch((54, 30.5), (42, 27), mutation_scale=15, color='#7fb3d5', linewidth=1.5)
ax.add_patch(arrow_pd_tia)

# TIA → PID
arrow_tia_pid = FancyArrowPatch((42, 23.5), (60, 23.5), mutation_scale=15, color='#a371f7', linewidth=1.5)
ax.add_patch(arrow_tia_pid)

# PID → DAC
arrow_pid_dac = FancyArrowPatch((72, 23.5), (75, 23.5), mutation_scale=15, color='#f78166', linewidth=1.5)
ax.add_patch(arrow_pid_dac)

# DAC → VCO
arrow_dac_vco = FancyArrowPatch((81, 21), (27, 22), mutation_scale=15, color='#ffc300', linewidth=1.5, linestyle=':')
ax.add_patch(arrow_dac_vco)
ax.text(55, 20, 'Vtune feedback', ha='center', va='top', fontsize=7, color='#ffc300', style='italic')

# VCO → Laser (external, shown as output)
arrow_vco_out = FancyArrowPatch((21, 20), (3, 77.5), mutation_scale=15, color='#a371f7', linewidth=2, linestyle=':')
ax.add_patch(arrow_vco_out)
ax.text(8, 45, '6.835 GHz\nto EOM\n(external)', ha='right', va='center', fontsize=7, color='#a371f7', fontweight='bold')

# Heater control
arrow_heater = FancyArrowPatch((66, 23.5), (84, 38), mutation_scale=15, color='#ff6b35', linewidth=1.5, linestyle='-')
ax.add_patch(arrow_heater)
ax.text(76, 30, 'Heater\nPWM', ha='center', va='center', fontsize=7, color='#ff6b35', fontweight='bold')

# ─────────────────────────────────────────────────────────────────────────────
# KEY DIMENSIONS
# ─────────────────────────────────────────────────────────────────────────────

# Die size annotation
ax.annotate('', xy=(2, 10), xytext=(2, 80), arrowprops=dict(arrowstyle='<->', color='#58a6ff', lw=2))
ax.text(0.5, 45, '3.0 mm', rotation=90, ha='right', va='center', fontsize=10, color='#58a6ff', fontweight='bold')

ax.annotate('', xy=(5, 10), xytext=(95, 10), arrowprops=dict(arrowstyle='<->', color='#58a6ff', lw=2))
ax.text(50, 9, '3.0 mm', ha='center', va='top', fontsize=10, color='#58a6ff', fontweight='bold')

# ─────────────────────────────────────────────────────────────────────────────
# LEGEND / NOTES
# ─────────────────────────────────────────────────────────────────────────────

legend_y = 2
ax.text(50, legend_y - 2, 'Cross-Section View (not to scale) — Shows internal architecture of 3×3 mm CSAC die',
        ha='center', fontsize=9, color='#8b949e', style='italic', transform=ax.transData)

# Remove axes
ax.set_xticks([])
ax.set_yticks([])
ax.spines['top'].set_visible(False)
ax.spines['bottom'].set_visible(False)
ax.spines['left'].set_visible(False)
ax.spines['right'].set_visible(False)

# Title
ax.text(50, 99, 'CSAC Chip Architecture — Cross-Section', ha='center', fontsize=16, fontweight='bold', color='#e6edf3')
ax.text(50, 97, 'Shows integration of optical cavity, Rb vapor, CMOS electronics, and heater on a single 3×3 mm die',
        ha='center', fontsize=9, color='#8b949e', style='italic')

plt.tight_layout()
outfile = BASE / 'chip_cross_section.png'
fig.savefig(str(outfile), dpi=150, facecolor='#0d1117', edgecolor='none', bbox_inches='tight')
print(f"Cross-section diagram saved: {outfile}")
plt.close()

# ─────────────────────────────────────────────────────────────────────────────
# TOP-DOWN FLOORPLAN
# ─────────────────────────────────────────────────────────────────────────────

fig, ax = plt.subplots(figsize=(14, 14), dpi=150)
ax.set_xlim(0, 3000)
ax.set_ylim(0, 3000)
ax.set_aspect('equal')

# Background
ax.add_patch(Rectangle((0, 0), 3000, 3000, facecolor='#0d1117', edgecolor='none'))

# Die outline
die_outline = Rectangle((0, 0), 3000, 3000, facecolor='none', edgecolor='#58a6ff', linewidth=3)
ax.add_patch(die_outline)

# ─────────────────────────────────────────────────────────────────────────────
# FUNCTIONAL BLOCKS (top-down layout)
# ─────────────────────────────────────────────────────────────────────────────

# Cavity (center) — large, occupies ~40% of die area
cavity = Rectangle((600, 600), 1800, 1800, facecolor='#6b1515', edgecolor='#ff6b6b', linewidth=2, alpha=0.5)
ax.add_patch(cavity)
ax.text(1500, 1500, 'Optical Cavity\n(Rb-87 vapor, N₂)\n1.8 mm × 1.8 mm\nDepth: 1 mm',
        ha='center', va='center', fontsize=12, fontweight='bold', color='#ffcccc')

# Heater traces (on all 4 sides of cavity for uniform heating)
heater_top = Rectangle((600, 2300), 1800, 200, facecolor='#ff6b35', edgecolor='#ff4500', linewidth=2)
ax.add_patch(heater_top)
ax.text(1500, 2400, 'Heater (polySi)', ha='center', va='center', fontsize=9, color='white', fontweight='bold')

heater_bottom = Rectangle((600, 100), 1800, 200, facecolor='#ff6b35', edgecolor='#ff4500', linewidth=2)
ax.add_patch(heater_bottom)
ax.text(1500, 200, 'Heater (polySi)', ha='center', va='center', fontsize=9, color='white', fontweight='bold')

heater_left = Rectangle((100, 600), 200, 1800, facecolor='#ff6b35', edgecolor='#ff4500', linewidth=2)
ax.add_patch(heater_left)
ax.text(200, 1500, 'Heater', ha='center', va='center', fontsize=8, color='white', fontweight='bold', rotation=90)

heater_right = Rectangle((2700, 600), 200, 1800, facecolor='#ff6b35', edgecolor='#ff4500', linewidth=2)
ax.add_patch(heater_right)
ax.text(2800, 1500, 'Heater', ha='center', va='center', fontsize=8, color='white', fontweight='bold', rotation=90)

# Photodiode (near cavity, for sensing)
pd = Rectangle((2500, 2500), 300, 300, facecolor='#79c0ff', edgecolor='#1f6feb', linewidth=2)
ax.add_patch(pd)
ax.text(2650, 2650, 'PD', ha='center', va='center', fontsize=10, color='white', fontweight='bold')

# VCO (high-frequency, sensitive — away from heater)
vco = Rectangle((2300, 1800), 400, 400, facecolor='#a371f7', edgecolor='#7928ca', linewidth=2)
ax.add_patch(vco)
ax.text(2500, 2000, 'VCO\n6.835\nGHz', ha='center', va='center', fontsize=9, color='white', fontweight='bold')

# TIA (near photodiode, minimize trace length)
tia = Rectangle((2100, 2500), 300, 300, facecolor='#79c0ff', edgecolor='#0969da', linewidth=2)
ax.add_patch(tia)
ax.text(2250, 2650, 'TIA', ha='center', va='center', fontsize=9, color='white', fontweight='bold')

# Frequency divider (logic, low-power, can be anywhere)
fdiv = Rectangle((100, 2500), 400, 300, facecolor='#56d364', edgecolor='#238636', linewidth=2)
ax.add_patch(fdiv)
ax.text(300, 2650, 'Freq Div\n÷2³³', ha='center', va='center', fontsize=9, color='white', fontweight='bold')

# PID controller
pid = Rectangle((100, 2050), 400, 300, facecolor='#f78166', edgecolor='#da3633', linewidth=2)
ax.add_patch(pid)
ax.text(300, 2200, 'PID\nController', ha='center', va='center', fontsize=9, color='white', fontweight='bold')

# DAC (drives VCO, keep close)
dac = Rectangle((2000, 1300), 300, 300, facecolor='#ffc300', edgecolor='#d0883e', linewidth=2)
ax.add_patch(dac)
ax.text(2150, 1450, 'DAC\n10-bit', ha='center', va='center', fontsize=9, color='white', fontweight='bold')

# SPI interface (at edge for bonding)
spi = Rectangle((100, 1400), 300, 300, facecolor='#79c0ff', edgecolor='#0969da', linewidth=2)
ax.add_patch(spi)
ax.text(250, 1550, 'SPI\nI/O', ha='center', va='center', fontsize=9, color='white', fontweight='bold')

# Decoupling capacitors (scattered throughout)
for (x, y) in [(400, 1000), (1200, 2700), (2400, 500), (500, 500), (2600, 1200)]:
    cap = Rectangle((x, y), 150, 150, facecolor='#30363d', edgecolor='#484f58', linewidth=1)
    ax.add_patch(cap)
    ax.text(x+75, y+75, 'C', ha='center', va='center', fontsize=7, color='#8b949e')

# Wire bond pads (around periphery)
for x in range(100, 3000, 250):
    # Top
    pad_t = Rectangle((x, 2900), 120, 100, facecolor='#d0883e', edgecolor='#ff9944', linewidth=1)
    ax.add_patch(pad_t)
    # Bottom
    pad_b = Rectangle((x, 0), 120, 100, facecolor='#d0883e', edgecolor='#ff9944', linewidth=1)
    ax.add_patch(pad_b)

for y in range(100, 3000, 250):
    # Left
    pad_l = Rectangle((0, y), 100, 120, facecolor='#d0883e', edgecolor='#ff9944', linewidth=1)
    ax.add_patch(pad_l)
    # Right
    pad_r = Rectangle((2900, y), 100, 120, facecolor='#d0883e', edgecolor='#ff9944', linewidth=1)
    ax.add_patch(pad_r)

# ─────────────────────────────────────────────────────────────────────────────
# SIGNAL ROUTING (schematic)
# ─────────────────────────────────────────────────────────────────────────────

# PD → TIA
ax.plot([2500, 2250], [2500, 2650], 'c--', linewidth=2, alpha=0.6)

# TIA → PID
ax.plot([2100, 500], [2650, 2200], 'm--', linewidth=2, alpha=0.6)

# PID → DAC
ax.plot([500, 2000], [2200, 1450], 'r--', linewidth=2, alpha=0.6)

# DAC → VCO
ax.plot([2150, 2500], [1300, 1800], 'y--', linewidth=2, alpha=0.6)

# VCO → external EOM (laser modulation)
ax.annotate('6.835 GHz\nto EOM', xy=(2500, 1800), xytext=(2800, 1200),
            arrowprops=dict(arrowstyle='->', color='#a371f7', lw=2),
            fontsize=8, color='#a371f7', fontweight='bold')

# Frequency divider output
ax.annotate('1 Hz out', xy=(500, 2500), xytext=(700, 2200),
            arrowprops=dict(arrowstyle='->', color='#56d364', lw=2),
            fontsize=8, color='#56d364', fontweight='bold')

# ─────────────────────────────────────────────────────────────────────────────
# ANNOTATIONS
# ─────────────────────────────────────────────────────────────────────────────

ax.text(1500, 3200, 'Top-Down Floorplan — 3×3 mm Die', ha='center', fontsize=14, fontweight='bold', color='#e6edf3')
ax.text(1500, 3100, 'Shows component placement and signal routing for optimal performance',
        ha='center', fontsize=9, color='#8b949e', style='italic')

# Dimension labels
ax.annotate('', xy=(50, 0), xytext=(50, 3000), arrowprops=dict(arrowstyle='<->', color='#58a6ff', lw=2))
ax.text(0, 1500, '3 mm', rotation=90, ha='right', va='center', fontsize=11, color='#58a6ff', fontweight='bold')

ax.annotate('', xy=(0, 50), xytext=(3000, 50), arrowprops=dict(arrowstyle='<->', color='#58a6ff', lw=2))
ax.text(1500, 10, '3 mm', ha='center', fontsize=11, color='#58a6ff', fontweight='bold')

# Remove axes
ax.set_xticks([])
ax.set_yticks([])
ax.spines['top'].set_visible(False)
ax.spines['bottom'].set_visible(False)
ax.spines['left'].set_visible(False)
ax.spines['right'].set_visible(False)

plt.tight_layout()
outfile = BASE / 'chip_floorplan.png'
fig.savefig(str(outfile), dpi=150, facecolor='#0d1117', edgecolor='none', bbox_inches='tight')
print(f"Floorplan diagram saved: {outfile}")
plt.close()

print("\n[OK] Both diagrams created:")
print("   - chip_cross_section.png")
print("   - chip_floorplan.png")
