#!/usr/bin/env python3
"""Generate all synthesis & architecture plots for CSAC digital_top."""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle
import matplotlib.patches as mpatches
import numpy as np

mono = 'monospace'
BG = '#0d1117'
PANEL = '#161b22'
BORDER = '#30363d'
TEXT = '#c9d1d9'
DIM = '#8b949e'

def style_ax(ax, title=None):
    ax.set_facecolor(PANEL)
    for s in ax.spines.values(): s.set_color(BORDER)
    if title:
        ax.set_title(title, color=TEXT, fontsize=14, fontweight='bold', fontfamily=mono, pad=12)

# ═══════════════════════════════════════════════════════════════════════════
# PLOT 1: Full chip schematic / block diagram
# ═══════════════════════════════════════════════════════════════════════════

fig1, ax = plt.subplots(1, 1, figsize=(20, 14), facecolor=BG)
ax.set_xlim(0, 20); ax.set_ylim(0, 14)
ax.set_facecolor(PANEL); ax.set_xticks([]); ax.set_yticks([])
for s in ax.spines.values(): s.set_color(BORDER)

fig1.text(0.5, 0.97, 'CSAC Readout IC — Full Chip Block Diagram', ha='center',
          fontsize=20, fontweight='bold', color='#58a6ff', fontfamily=mono)
fig1.text(0.5, 0.945, 'SKY130 CMOS  |  3x3 mm die  |  Mixed-Signal Architecture', ha='center',
          fontsize=12, color=DIM, fontfamily=mono)

bs = dict(boxstyle='round,pad=0.3', linewidth=2)

def chip_block(ax, x, y, w, h, title, sub, ec, status='designed'):
    fc = '#1a1a2e' if status == 'designed' else '#2a1a1a'
    ax.add_patch(FancyBboxPatch((x, y), w, h, **bs, facecolor=fc, edgecolor=ec))
    ax.text(x+w/2, y+h*0.65, title, ha='center', va='center', fontsize=11,
            fontweight='bold', color=ec, fontfamily=mono)
    if isinstance(sub, list):
        for i, s in enumerate(sub):
            ax.text(x+w/2, y+h*0.35-i*0.35, s, ha='center', va='center',
                    fontsize=8, color=DIM, fontfamily=mono)
    else:
        ax.text(x+w/2, y+h*0.3, sub, ha='center', va='center',
                fontsize=8, color=DIM, fontfamily=mono)
    if status == 'not_designed':
        ax.text(x+w-0.2, y+0.15, 'NOT YET', ha='right', fontsize=6,
                color='#f85149', fontweight='bold', fontfamily=mono)

# External components (top)
ax.add_patch(FancyBboxPatch((0.3, 12.0), 4.0, 1.5, boxstyle='round,pad=0.3',
             linewidth=2, facecolor='#0d2818', edgecolor='#238636', linestyle='--'))
ax.text(2.3, 12.95, 'VCSEL + Lens', ha='center', fontsize=11, fontweight='bold',
        color='#238636', fontfamily=mono)
ax.text(2.3, 12.4, '795 nm  |  EXTERNAL', ha='center', fontsize=8, color=DIM, fontfamily=mono)

ax.add_patch(FancyBboxPatch((5.0, 12.0), 4.5, 1.5, boxstyle='round,pad=0.3',
             linewidth=2, facecolor='#0d2818', edgecolor='#238636', linestyle='--'))
ax.text(7.25, 12.95, 'Rb-87 MEMS Cell', ha='center', fontsize=11, fontweight='bold',
        color='#238636', fontfamily=mono)
ax.text(7.25, 12.4, '3x3x1.1mm  |  GDS done', ha='center', fontsize=8, color=DIM, fontfamily=mono)

ax.add_patch(FancyBboxPatch((10.2, 12.0), 4.0, 1.5, boxstyle='round,pad=0.3',
             linewidth=2, facecolor='#0d2818', edgecolor='#238636', linestyle='--'))
ax.text(12.2, 12.95, 'Photodetector', ha='center', fontsize=11, fontweight='bold',
        color='#238636', fontfamily=mono)
ax.text(12.2, 12.4, 'InGaAs PD  |  EXTERNAL', ha='center', fontsize=8, color=DIM, fontfamily=mono)

# Chip boundary
ax.add_patch(FancyBboxPatch((0.3, 0.3), 19.4, 11.2, boxstyle='round,pad=0.2',
             linewidth=3, facecolor='none', edgecolor='#58a6ff', linestyle='-'))
ax.text(10, 11.25, '< - - - -  SKY130 CMOS DIE (3 x 3 mm)  - - - - >',
        ha='center', fontsize=10, color='#58a6ff', fontfamily=mono)

# Analog blocks
chip_block(ax, 0.8, 8.5, 3.5, 2.2, 'VCO', ['6.835 GHz LC-tank', 'SPICE netlist exists'], '#f85149', 'designed')
chip_block(ax, 5.0, 8.5, 3.5, 2.2, 'TIA', ['1 MOhm gain', 'SPICE netlist exists'], '#f85149', 'designed')

chip_block(ax, 9.2, 8.5, 2.8, 2.2, '8-bit ADC', ['photo signal', ''], '#ff7b72', 'not_designed')
chip_block(ax, 12.5, 8.5, 2.8, 2.2, '10-bit ADC', ['temp sensor', ''], '#ff7b72', 'not_designed')
chip_block(ax, 15.8, 8.5, 3.5, 2.2, '10-bit DAC', ['VCO tune voltage', ''], '#ff7b72', 'not_designed')

# Digital block (center, highlighted)
ax.add_patch(FancyBboxPatch((0.8, 2.8), 18.5, 5.2, boxstyle='round,pad=0.3',
             linewidth=2.5, facecolor='#0d1a2e', edgecolor='#3fb950'))
ax.text(10, 7.7, 'DIGITAL BLOCK  (673 cells  |  7,176 um2  |  SYNTHESIZED)', ha='center',
        fontsize=12, fontweight='bold', color='#3fb950', fontfamily=mono)

# Digital sub-blocks
chip_block(ax, 1.3, 5.0, 3.2, 2.2, '33-bit Divider', ['6.835 GHz -> 1 Hz', '33 FFs + carry'], '#58a6ff', 'designed')
chip_block(ax, 4.9, 5.0, 3.2, 2.2, 'Clock Enable', ['Edge detectors', 'ce_servo, ce_1hz'], '#58a6ff', 'designed')
chip_block(ax, 8.5, 5.0, 3.2, 2.2, 'PID Controller', ['Kp=2 Ki=1 Kd=3', 'Servo loop core'], '#bc8cff', 'designed')
chip_block(ax, 12.1, 5.0, 3.2, 2.2, 'Lock Detect', ['Threshold: 10', 'Window: 8'], '#d29922', 'designed')
chip_block(ax, 15.7, 5.0, 3.2, 2.2, 'Thermal Ctrl', ['Setpoint: 350', 'Heater PWM'], '#f85149', 'designed')

chip_block(ax, 1.3, 3.0, 3.2, 1.6, 'SPI Slave', '9 registers  |  41 cells', '#79c0ff', 'designed')
chip_block(ax, 4.9, 3.0, 3.2, 1.6, 'Status Byte', 'lock|heartbeat|diag', '#d29922', 'designed')
chip_block(ax, 8.5, 3.0, 3.2, 1.6, '1 Hz Counter', 'count_1hz[31:0]', '#3fb950', 'designed')

# 8-bit DAC for heater
chip_block(ax, 15.8, 1.5, 3.5, 1.0, '8-bit DAC', 'heater power', '#ff7b72', 'not_designed')

# I/O pads
ax.add_patch(FancyBboxPatch((12.1, 0.5), 7.0, 1.5, boxstyle='round,pad=0.2',
             linewidth=1.5, facecolor='#1a1a2e', edgecolor=DIM))
ax.text(15.6, 1.5, 'I/O PAD RING', ha='center', fontsize=10, fontweight='bold',
        color=DIM, fontfamily=mono)
ax.text(15.6, 1.0, 'SPI  |  1Hz OUT  |  VDD/VSS  |  TEST', ha='center',
        fontsize=8, color=DIM, fontfamily=mono)

# Legend
legend_items = [
    mpatches.Patch(facecolor='#1a1a2e', edgecolor='#3fb950', label='Designed + Synthesized'),
    mpatches.Patch(facecolor='#1a1a2e', edgecolor='#f85149', label='SPICE exists, not validated'),
    mpatches.Patch(facecolor='#2a1a1a', edgecolor='#ff7b72', label='Not yet designed'),
    mpatches.Patch(facecolor='#0d2818', edgecolor='#238636', label='External / MEMS'),
]
ax.legend(handles=legend_items, loc='lower left', fontsize=9, facecolor=PANEL,
          edgecolor=BORDER, labelcolor=TEXT, prop={'family': mono})

fig1.savefig('/home/ubuntu/atomicclock-mems/09_circuit_design/chip_block_diagram.png',
             dpi=150, bbox_inches='tight', facecolor=BG)
print("Saved: chip_block_diagram.png")

# ═══════════════════════════════════════════════════════════════════════════
# PLOT 2: Digital block detailed schematic (signal flow)
# ═══════════════════════════════════════════════════════════════════════════

fig2, ax = plt.subplots(1, 1, figsize=(18, 10), facecolor=BG)
ax.set_xlim(0, 18); ax.set_ylim(0, 10)
ax.set_facecolor(PANEL); ax.set_xticks([]); ax.set_yticks([])
for s in ax.spines.values(): s.set_color(BORDER)

fig2.text(0.5, 0.97, 'Digital Block — Signal Flow Schematic', ha='center',
          fontsize=18, fontweight='bold', color='#58a6ff', fontfamily=mono)

# Input ports (left side)
inputs = [
    ('clk_vco', 9.0, '#58a6ff'),
    ('photo_adc[7:0]', 7.0, '#bc8cff'),
    ('temp_adc[9:0]', 5.0, '#f85149'),
    ('spi_clk', 3.0, '#79c0ff'),
    ('spi_mosi', 2.3, '#79c0ff'),
    ('spi_cs', 1.6, '#79c0ff'),
    ('reset_n', 0.8, '#d29922'),
]

for name, y, color in inputs:
    ax.annotate('', xy=(2.5, y), xytext=(0.5, y),
                arrowprops=dict(arrowstyle='->', color=color, lw=1.5))
    ax.text(0.3, y, name, ha='right', va='center', fontsize=8, color=color, fontfamily=mono,
            bbox=dict(boxstyle='round,pad=0.15', facecolor='#0d1117', edgecolor=color, lw=0.8))

# Processing blocks (center)
def flow_block(ax, x, y, w, h, title, sub, ec):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.2',
                 linewidth=2, facecolor='#0d1a2e', edgecolor=ec))
    ax.text(x+w/2, y+h*0.65, title, ha='center', va='center', fontsize=10,
            fontweight='bold', color=ec, fontfamily=mono)
    ax.text(x+w/2, y+h*0.25, sub, ha='center', va='center', fontsize=7,
            color=DIM, fontfamily=mono)

# Clock domain
flow_block(ax, 2.5, 8.2, 3.0, 1.5, 'VCO Counter', '33 bits @ 6.835 GHz', '#58a6ff')
flow_block(ax, 6.0, 8.2, 3.0, 1.5, 'Edge Detect', 'bit[26], bit[32]', '#3fb950')

# Data path
flow_block(ax, 2.5, 6.0, 2.5, 1.5, 'Error Calc', 'photo - setpoint', '#bc8cff')
flow_block(ax, 5.5, 6.0, 2.5, 1.5, 'PID Math', 'P + I + D terms', '#bc8cff')
flow_block(ax, 8.5, 6.0, 2.5, 1.5, 'Saturate', '[0, 1023]', '#bc8cff')

# Thermal
flow_block(ax, 2.5, 4.0, 2.5, 1.5, 'Temp Error', 'setpoint - adc', '#f85149')
flow_block(ax, 5.5, 4.0, 2.5, 1.5, 'Proportional', 'error >>> 2', '#f85149')
flow_block(ax, 8.5, 4.0, 2.5, 1.5, 'Saturate', '[0, 255]', '#f85149')

# Lock
flow_block(ax, 11.5, 6.0, 2.5, 1.5, 'Lock Check', 'err < threshold?', '#d29922')
flow_block(ax, 14.5, 6.5, 2.5, 1.0, 'Counter', '8 consecutive', '#d29922')

# SPI
flow_block(ax, 2.5, 1.5, 3.0, 1.5, 'SPI Shift', 'RX/TX 8-bit', '#79c0ff')
flow_block(ax, 6.0, 1.5, 3.0, 1.5, 'Addr Decode', '9 register map', '#79c0ff')
flow_block(ax, 9.5, 1.5, 3.0, 1.5, 'Read Mux', '8:1 output select', '#79c0ff')

# Output ports (right side)
outputs = [
    ('1 Hz count[31:0]', 9.0, '#3fb950'),
    ('dac_vco_tune[9:0]', 7.0, '#bc8cff'),
    ('valid_lock', 6.5, '#d29922'),
    ('dac_heater[7:0]', 5.0, '#f85149'),
    ('status_byte[7:0]', 3.5, '#d29922'),
    ('spi_miso', 2.0, '#79c0ff'),
]

for name, y, color in outputs:
    ax.annotate('', xy=(17.5, y), xytext=(15.5, y),
                arrowprops=dict(arrowstyle='->', color=color, lw=1.5))
    ax.text(17.7, y, name, ha='left', va='center', fontsize=8, color=color, fontfamily=mono,
            bbox=dict(boxstyle='round,pad=0.15', facecolor='#0d1117', edgecolor=color, lw=0.8))

# Arrows between blocks
arr = dict(arrowstyle='->', lw=1.2)
ax.annotate('', xy=(6.0, 8.95), xytext=(5.5, 8.95), arrowprops={**arr, 'color': '#58a6ff'})
ax.annotate('', xy=(5.5, 6.75), xytext=(5.0, 6.75), arrowprops={**arr, 'color': '#bc8cff'})
ax.annotate('', xy=(8.5, 6.75), xytext=(8.0, 6.75), arrowprops={**arr, 'color': '#bc8cff'})
ax.annotate('', xy=(5.5, 4.75), xytext=(5.0, 4.75), arrowprops={**arr, 'color': '#f85149'})
ax.annotate('', xy=(8.5, 4.75), xytext=(8.0, 4.75), arrowprops={**arr, 'color': '#f85149'})
ax.annotate('', xy=(11.5, 6.75), xytext=(11.0, 6.75), arrowprops={**arr, 'color': '#bc8cff'})
ax.annotate('', xy=(14.5, 7.0), xytext=(14.0, 7.0), arrowprops={**arr, 'color': '#d29922'})
ax.annotate('', xy=(6.0, 2.25), xytext=(5.5, 2.25), arrowprops={**arr, 'color': '#79c0ff'})
ax.annotate('', xy=(9.5, 2.25), xytext=(9.0, 2.25), arrowprops={**arr, 'color': '#79c0ff'})

# ce_servo annotation
ax.annotate('ce_servo\nce_1hz', xy=(7.5, 8.2), xytext=(7.5, 7.7),
            fontsize=7, color='#3fb950', fontfamily=mono, ha='center',
            arrowprops=dict(arrowstyle='->', color='#3fb950', lw=1, ls='--'))

fig2.savefig('/home/ubuntu/atomicclock-mems/09_circuit_design/digital_signal_flow.png',
             dpi=150, bbox_inches='tight', facecolor=BG)
print("Saved: digital_signal_flow.png")

# ═══════════════════════════════════════════════════════════════════════════
# PLOT 3: Synthesis cell pie chart + FF breakdown
# ═══════════════════════════════════════════════════════════════════════════

fig3, (ax_pie, ax_ff) = plt.subplots(1, 2, figsize=(16, 8), facecolor=BG)

# Pie chart
categories = {
    'Flip-Flops': 135,
    'XOR/XNOR': 134,
    'AOI/OAI': 131,
    'NAND': 106,
    'NOR': 59,
    'Buffers': 42,
    'AND/OR': 27,
    'Majority': 23,
    'MUX': 16,
}

style_ax(ax_pie, 'Cell Type Distribution (673 total)')
colors_pie = ['#58a6ff', '#bc8cff', '#f85149', '#d29922', '#3fb950',
              '#79c0ff', '#ff7b72', '#ffa657', '#a5d6ff']

wedges, texts, autotexts = ax_pie.pie(
    categories.values(), labels=categories.keys(), autopct='%1.0f%%',
    colors=colors_pie, textprops={'fontsize': 9, 'color': TEXT, 'fontfamily': mono},
    pctdistance=0.8, startangle=90
)
for t in autotexts:
    t.set_fontsize(8)
    t.set_color('#0d1117')
    t.set_fontweight('bold')

# FF breakdown by function
style_ax(ax_ff, 'Flip-Flop Allocation (135 total)')
ff_blocks = {
    'VCO Counter\n(33-bit)': 33,
    '1 Hz Counter\n(32-bit)': 32,
    'PID Regs\n(int+err+out)': 28,
    'SPI\n(shift+addr)': 19,
    'Heater\n(PWM reg)': 8,
    'Lock Det\n(counter)': 5,
    'Clk Enable\n(edge det)': 2,
    'Other': 8,
}

ff_colors = ['#58a6ff', '#3fb950', '#bc8cff', '#79c0ff', '#f85149',
             '#d29922', '#ffa657', DIM]

bars = ax_ff.barh(range(len(ff_blocks)), list(ff_blocks.values()),
                  color=ff_colors, alpha=0.85, edgecolor=BORDER, height=0.65)
ax_ff.set_yticks(range(len(ff_blocks)))
ax_ff.set_yticklabels(ff_blocks.keys(), fontsize=9, color=TEXT, fontfamily=mono)
ax_ff.invert_yaxis()
ax_ff.set_xlabel('Number of Flip-Flops', color=DIM, fontsize=10, fontfamily=mono)
ax_ff.tick_params(axis='x', colors=DIM)

for bar, val in zip(bars, ff_blocks.values()):
    ax_ff.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2,
               str(val), va='center', color=DIM, fontsize=10, fontfamily=mono)
ax_ff.set_xlim(0, 40)

fig3.savefig('/home/ubuntu/atomicclock-mems/09_circuit_design/synth_cell_breakdown.png',
             dpi=150, bbox_inches='tight', facecolor=BG)
print("Saved: synth_cell_breakdown.png")

# ═══════════════════════════════════════════════════════════════════════════
# PLOT 4: Design status / progress tracker
# ═══════════════════════════════════════════════════════════════════════════

fig4, ax = plt.subplots(1, 1, figsize=(16, 9), facecolor=BG)
ax.set_xlim(0, 16); ax.set_ylim(0, 12)
ax.set_facecolor(PANEL); ax.set_xticks([]); ax.set_yticks([])
for s in ax.spines.values(): s.set_color(BORDER)

fig4.text(0.5, 0.97, 'CSAC Chip Design — Progress Tracker', ha='center',
          fontsize=18, fontweight='bold', color='#58a6ff', fontfamily=mono)

# Flow stages
stages = [
    ('Physics\nSimulation', 'COMPLETE', '#3fb950', '10 modules\nAll PASS'),
    ('RTL\nDesign', 'COMPLETE', '#3fb950', 'Verilog\n267 lines'),
    ('Synthesis\n(Yosys)', 'COMPLETE', '#3fb950', '673 cells\n7176 um2'),
    ('Place & Route\n(OpenROAD)', 'NEXT', '#d29922', 'Automated\nP&R flow'),
    ('Analog\nValidation', 'BLOCKED', '#f85149', 'VCO + TIA\nSPICE sim'),
    ('Layout\n(Magic)', 'PENDING', '#8b949e', 'Analog\ncustom'),
    ('DRC/LVS', 'PENDING', '#8b949e', 'Clean\nchecks'),
    ('Tapeout', 'PENDING', '#8b949e', 'GDS-II\nfinal'),
]

for i, (name, status, color, detail) in enumerate(stages):
    x = 0.5 + i * 1.9
    y = 8.0

    # Status box
    ax.add_patch(FancyBboxPatch((x, y), 1.7, 3.0, boxstyle='round,pad=0.2',
                 linewidth=2, facecolor='#0d1117', edgecolor=color))

    ax.text(x+0.85, y+2.5, name, ha='center', va='center', fontsize=9,
            fontweight='bold', color=color, fontfamily=mono)

    # Status badge
    badge_colors = {'COMPLETE': '#238636', 'NEXT': '#9e6a03', 'BLOCKED': '#da3633', 'PENDING': '#484f58'}
    ax.add_patch(FancyBboxPatch((x+0.1, y+1.2), 1.5, 0.5, boxstyle='round,pad=0.1',
                 facecolor=badge_colors[status], edgecolor='none'))
    ax.text(x+0.85, y+1.45, status, ha='center', va='center', fontsize=8,
            fontweight='bold', color='white', fontfamily=mono)

    ax.text(x+0.85, y+0.5, detail, ha='center', va='center', fontsize=7,
            color=DIM, fontfamily=mono)

    # Arrow to next
    if i < len(stages) - 1:
        ax.annotate('', xy=(x+2.0, y+1.5), xytext=(x+1.7, y+1.5),
                    arrowprops=dict(arrowstyle='->', color='#484f58', lw=1.5))

# Key decisions box
ax.add_patch(FancyBboxPatch((0.5, 1.0), 15.0, 5.5, boxstyle='round,pad=0.3',
             linewidth=1.5, facecolor='#0d1117', edgecolor=BORDER))
ax.text(8.0, 6.0, 'Critical Path & Key Decisions', ha='center', fontsize=13,
        fontweight='bold', color=TEXT, fontfamily=mono)

decisions = [
    ('1.', 'VCO feasibility on SKY130', 'Can 6.835 GHz oscillate on 130nm fT~60GHz process?', '#f85149'),
    ('2.', 'Missing analog blocks', 'ADCs (8-bit, 10-bit) and DACs (10-bit, 8-bit) not designed', '#ff7b72'),
    ('3.', 'Post-layout parasitics', 'Inductor Q, routing caps could kill VCO performance', '#d29922'),
    ('4.', 'Go/No-Go: on-chip vs off-chip VCO', 'May need external SiGe VCO if SKY130 fails', '#d29922'),
]

for i, (num, title, desc, color) in enumerate(decisions):
    y = 4.8 - i * 1.2
    ax.text(1.2, y, num, fontsize=11, fontweight='bold', color=color, fontfamily=mono)
    ax.text(1.8, y, title, fontsize=10, fontweight='bold', color=color, fontfamily=mono)
    ax.text(1.8, y-0.4, desc, fontsize=8, color=DIM, fontfamily=mono)

fig4.savefig('/home/ubuntu/atomicclock-mems/09_circuit_design/design_progress.png',
             dpi=150, bbox_inches='tight', facecolor=BG)
print("Saved: design_progress.png")

print("\nAll 4 plots generated successfully.")
