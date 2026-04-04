#!/usr/bin/env python3
"""Generate a professional CSAC chip architecture diagram."""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np

# ─── Figure setup ───────────────────────────────────────────────────
fig, ax = plt.subplots(1, 1, figsize=(22, 16), dpi=180)
ax.set_xlim(0, 22)
ax.set_ylim(0, 16)
ax.set_aspect('equal')
ax.axis('off')
fig.patch.set_facecolor('#0d1117')

# ─── Color palette ──────────────────────────────────────────────────
CLK_VCO_COLOR = '#1f6feb'     # Blue — clk_vco domain
SPI_CLK_COLOR = '#f0883e'     # Orange — spi_clk domain
ANALOG_COLOR  = '#8b949e'     # Gray — analog blocks
CDC_COLOR     = '#da3633'     # Red — CDC crossing
CHIP_BG       = '#161b22'     # Dark background for chip
BLOCK_TEXT    = '#e6edf3'     # Light text
TITLE_COLOR   = '#58a6ff'     # Bright blue titles
BORDER_COLOR  = '#30363d'     # Subtle border
PIN_COLOR     = '#7ee787'     # Green — pins
DONE_COLOR    = '#238636'     # Green badge
RISK_COLOR    = '#da3633'     # Red badge
PENDING_COLOR = '#f0883e'     # Orange badge

# ─── Chip boundary ──────────────────────────────────────────────────
chip = FancyBboxPatch((0.5, 0.5), 21, 15, boxstyle="round,pad=0.15",
                       facecolor=CHIP_BG, edgecolor='#58a6ff', linewidth=2.5)
ax.add_patch(chip)

ax.text(11, 15.7, 'CSAC Readout IC — SKY130 130nm CMOS', fontsize=18,
        ha='center', va='center', color=TITLE_COLOR, fontweight='bold',
        fontfamily='monospace')
ax.text(11, 15.25, 'Chip-Scale Atomic Clock Digital Control Subsystem',
        fontsize=10, ha='center', va='center', color='#8b949e',
        fontfamily='monospace')

# ─── Helper functions ───────────────────────────────────────────────
def draw_block(x, y, w, h, label, sublabel, color, status='done', cells=None):
    """Draw a rounded block with label, sublabel, status badge, and cell count."""
    blk = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.08",
                          facecolor=color, edgecolor='#e6edf3', linewidth=1.2, alpha=0.85)
    ax.add_patch(blk)
    ax.text(x + w/2, y + h*0.65, label, fontsize=10, ha='center', va='center',
            color=BLOCK_TEXT, fontweight='bold', fontfamily='monospace')
    ax.text(x + w/2, y + h*0.35, sublabel, fontsize=7, ha='center', va='center',
            color='#c9d1d9', fontfamily='monospace')
    # Status badge
    sc = {'done': (DONE_COLOR, 'DONE'), 'pending': (PENDING_COLOR, 'PEND'),
          'risk': (RISK_COLOR, 'RISK')}
    bc, bt = sc.get(status, (DONE_COLOR, 'DONE'))
    badge = FancyBboxPatch((x + w - 0.65, y + h - 0.32), 0.6, 0.25,
                            boxstyle="round,pad=0.03", facecolor=bc, edgecolor='none')
    ax.add_patch(badge)
    ax.text(x + w - 0.35, y + h - 0.20, bt, fontsize=5, ha='center', va='center',
            color='white', fontweight='bold', fontfamily='monospace')
    if cells:
        ax.text(x + 0.15, y + 0.1, cells, fontsize=5.5, ha='left', va='bottom',
                color='#7ee787', fontfamily='monospace')

def draw_arrow(x1, y1, x2, y2, color='#e6edf3', width=None, style='->', label=''):
    """Draw a signal flow arrow with optional bus width label."""
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle=style, color=color, lw=1.5))
    if label:
        mx, my = (x1+x2)/2, (y1+y2)/2
        ax.text(mx, my+0.15, label, fontsize=6, ha='center', va='bottom',
                color=color, fontfamily='monospace',
                bbox=dict(boxstyle='round,pad=0.1', facecolor=CHIP_BG, edgecolor='none'))

def draw_pin(x, y, label, side='left'):
    """Draw a pin indicator on the chip boundary."""
    if side == 'left':
        ax.plot([0.5, x], [y, y], color=PIN_COLOR, lw=1.5, ls='--', alpha=0.6)
        ax.text(0.3, y, label, fontsize=6, ha='right', va='center',
                color=PIN_COLOR, fontfamily='monospace', fontweight='bold')
        ax.plot(0.5, y, 'o', color=PIN_COLOR, markersize=5)
    elif side == 'right':
        ax.plot([x, 21.5], [y, y], color=PIN_COLOR, lw=1.5, ls='--', alpha=0.6)
        ax.text(21.7, y, label, fontsize=6, ha='left', va='center',
                color=PIN_COLOR, fontfamily='monospace', fontweight='bold')
        ax.plot(21.5, y, 'o', color=PIN_COLOR, markersize=5)
    elif side == 'top':
        ax.plot([x, x], [y, 15.5], color=PIN_COLOR, lw=1.5, ls='--', alpha=0.6)
        ax.text(x, 15.65, label, fontsize=6, ha='center', va='bottom',
                color=PIN_COLOR, fontfamily='monospace', fontweight='bold')
        ax.plot(x, 15.5, 'o', color=PIN_COLOR, markersize=5)
    elif side == 'bottom':
        ax.plot([x, x], [0.5, y], color=PIN_COLOR, lw=1.5, ls='--', alpha=0.6)
        ax.text(x, 0.25, label, fontsize=6, ha='center', va='top',
                color=PIN_COLOR, fontfamily='monospace', fontweight='bold')
        ax.plot(x, 0.5, 'o', color=PIN_COLOR, markersize=5)

# ═══════════════════════════════════════════════════════════════════
# ANALOG BLOCKS (left side — external to digital, shown as context)
# ═══════════════════════════════════════════════════════════════════

# VCO
draw_block(1.0, 11.5, 3.0, 2.0, 'VCO', '6.835 GHz VCXO\nΔf ±100 ppm',
           ANALOG_COLOR, status='pending')

# TIA + Photodetector ADC
draw_block(1.0, 8.5, 3.0, 2.0, 'TIA + ADC', 'Photodetector\n8-bit flash ADC',
           ANALOG_COLOR, status='pending')

# Temperature ADC
draw_block(1.0, 5.5, 3.0, 2.0, 'TEMP ADC', 'NTC Thermistor\n10-bit SAR ADC',
           ANALOG_COLOR, status='pending')

# VCO Tune DAC
draw_block(1.0, 2.5, 3.0, 2.0, 'VCO DAC', 'Tune Voltage\n10-bit R-2R DAC',
           ANALOG_COLOR, status='pending')

# Heater DAC
draw_block(1.0, 0.8, 3.0, 1.2, 'HEATER DAC', '8-bit PWM DAC',
           ANALOG_COLOR, status='pending')

# ═══════════════════════════════════════════════════════════════════
# DIGITAL BLOCKS — clk_vco domain (center)
# ═══════════════════════════════════════════════════════════════════

# Clock domain label
ax.text(9.5, 14.7, '◆ clk_vco domain (6.835 GHz)', fontsize=9,
        ha='center', va='center', color=CLK_VCO_COLOR, fontweight='bold',
        fontfamily='monospace')

# Reset Sync (VCO)
draw_block(5.0, 13.0, 2.5, 1.3, 'RESET SYNC', '2-FF sync\nasync→sync',
           CLK_VCO_COLOR, cells='10 cells')

# Frequency Divider
draw_block(5.0, 10.5, 4.0, 2.0, 'FREQ DIVIDER', '33-bit counter\nce_servo / ce_1hz',
           CLK_VCO_COLOR, cells='95 cells')
draw_arrow(4.0, 12.5, 5.0, 11.5, CLK_VCO_COLOR, label='clk_vco')

# PID Controller
draw_block(5.0, 7.5, 4.0, 2.2, 'PID CTRL', 'P+I+D loop\nKp=2, Ki=1, Kd=3\n10-bit DAC output',
           CLK_VCO_COLOR, cells='380 cells')
draw_arrow(4.0, 9.5, 5.0, 8.6, CLK_VCO_COLOR, label='photo[7:0]')

# Lock Detector
draw_block(5.0, 5.0, 4.0, 1.8, 'LOCK DET', 'Window comparator\nthresh=10, window=8',
           CLK_VCO_COLOR, cells='45 cells')
draw_arrow(7.0, 7.5, 7.0, 6.8, CLK_VCO_COLOR, label='error[8:0]')

# Thermal Controller
draw_block(5.0, 2.5, 4.0, 1.8, 'THERMAL CTRL', 'Bang-bang + shift\nsetpoint=350',
           CLK_VCO_COLOR, cells='52 cells')
draw_arrow(4.0, 6.5, 5.0, 3.4, CLK_VCO_COLOR, label='temp[9:0]')

# 1 Hz Counter
draw_block(10.0, 10.5, 2.5, 2.0, 'COUNT 1Hz', '32-bit counter\nce_1hz gated',
           CLK_VCO_COLOR, cells='128 cells')
draw_arrow(9.0, 11.5, 10.0, 11.5, CLK_VCO_COLOR, label='ce_1hz')

# Status byte
draw_block(10.0, 7.5, 2.5, 2.0, 'STATUS', '{lock, 0, 0,\nheart, int[3:0]}',
           CLK_VCO_COLOR, cells='8 cells')
draw_arrow(7.0, 5.0, 10.5, 7.5, CLK_VCO_COLOR, label='locked')

# Signal flows from analog to digital
draw_arrow(4.0, 9.5, 5.0, 8.6, CLK_VCO_COLOR)

# DAC outputs back to analog
draw_arrow(5.0, 8.2, 4.0, 3.5, '#7ee787', label='dac_vco[9:0]')
draw_arrow(5.0, 3.0, 4.0, 1.4, '#7ee787', label='heater[7:0]')

# ═══════════════════════════════════════════════════════════════════
# CDC CROSSING (center-right)
# ═════════════════════════════════════════════════════���═════════════

# CDC Bus Sync
draw_block(13.5, 7.5, 2.5, 4.5, 'CDC BUS\nSYNC', 'toggle-handshake\n76-bit bus\nclk_vco → spi_clk\n2-stage sync',
           CDC_COLOR, cells='160 cells')

# CDC arrows
draw_arrow(12.5, 11.5, 13.5, 11.0, CDC_COLOR, label='76b')
draw_arrow(12.5, 8.6, 13.5, 9.0, CDC_COLOR)

# Dashed line for domain boundary
for yy in np.arange(0.8, 15.0, 0.3):
    ax.plot([13.0, 13.0], [yy, yy+0.15], color=CDC_COLOR, lw=1.0, alpha=0.4)
ax.text(13.0, 14.7, '║ CDC', fontsize=8, ha='center', va='center',
        color=CDC_COLOR, fontweight='bold', fontfamily='monospace')

# ═══════════════════════════════════════════════════════════════════
# SPI DOMAIN (right side)
# ═══════════════════════════════════════════════════════════════════

ax.text(18.5, 14.7, '◆ spi_clk domain (~10 MHz)', fontsize=9,
        ha='center', va='center', color=SPI_CLK_COLOR, fontweight='bold',
        fontfamily='monospace')

# SPI Slave
draw_block(17.0, 10.5, 3.5, 2.0, 'SPI SLAVE', '8-bit shift reg\nCPOL=0 CPHA=0\ntx_shift reload fix',
           SPI_CLK_COLOR, cells='30 cells')

# SPI Regmap
draw_block(17.0, 7.5, 3.5, 2.2, 'SPI REGMAP', 'Addr decode + mux\n9 registers\ncomb. addr bypass',
           SPI_CLK_COLOR, cells='49 cells')

# Arrows between SPI blocks
draw_arrow(16.0, 9.75, 17.0, 9.75, SPI_CLK_COLOR, label='76b sync')
draw_arrow(18.75, 10.5, 18.75, 9.7, SPI_CLK_COLOR, label='rx[7:0]')
draw_arrow(18.0, 9.7, 18.0, 10.5, SPI_CLK_COLOR, label='tx[7:0]')

# ═══════════════════════════════════════════════════════════════════
# PINS / PORTS
# ═══════════════════════════════════════════════════════════════════

draw_pin(1.0, 12.5, 'clk_vco', 'top')
draw_pin(19.5, 14.5, 'spi_clk', 'top')
draw_pin(4.0, 14.5, 'reset_n', 'top')

draw_pin(1.0, 9.5, 'photo_adc[7:0]', 'left')
draw_pin(1.0, 6.5, 'temp_adc[9:0]', 'left')

draw_pin(20.5, 11.5, 'spi_miso', 'right')
draw_pin(20.5, 11.0, 'spi_mosi', 'right')
draw_pin(20.5, 10.5, 'spi_cs_n', 'right')

draw_pin(4.0, 3.5, 'dac_vco[9:0]', 'bottom')
draw_pin(7.0, 1.4, 'heater[7:0]', 'bottom')
draw_pin(10.5, 0.8, 'count_1hz[31:0]', 'bottom')
draw_pin(14.0, 0.8, 'valid_lock', 'bottom')
draw_pin(17.0, 0.8, 'status[7:0]', 'bottom')

# ═══════════════════════════════════════════════════════════════════
# SYNTHESIS METRICS TABLE
# ═══════════════════════════════════════════════════════════════════

table_x, table_y = 14.0, 1.5
ax.text(table_x + 2.5, table_y + 3.3, 'Multi-Corner Synthesis (SKY130 HD)',
        fontsize=10, ha='center', va='center', color=TITLE_COLOR,
        fontweight='bold', fontfamily='monospace')

# Table background
table_bg = FancyBboxPatch((table_x, table_y), 5.0, 3.0,
                           boxstyle="round,pad=0.1",
                           facecolor='#21262d', edgecolor='#30363d', linewidth=1)
ax.add_patch(table_bg)

headers = ['Corner', 'Cond.', 'Cells', 'Area (μm²)']
rows = [
    ['TT', '25°C / 1.80V', '957', '12,220'],
    ['SS', '100°C / 1.60V', '957', '12,220'],
    ['FF', '-40°C / 1.95V', '957', '12,220'],
]

for i, h in enumerate(headers):
    ax.text(table_x + 0.3 + i*1.25, table_y + 2.55, h, fontsize=7,
            ha='center', va='center', color=TITLE_COLOR, fontweight='bold',
            fontfamily='monospace')

# Header line
ax.plot([table_x + 0.1, table_x + 4.9], [table_y + 2.35, table_y + 2.35],
        color='#30363d', lw=1)

for r, row in enumerate(rows):
    for c, val in enumerate(row):
        color = '#7ee787' if c >= 2 else '#c9d1d9'
        ax.text(table_x + 0.3 + c*1.25, table_y + 1.85 - r*0.55, val,
                fontsize=7, ha='center', va='center', color=color,
                fontfamily='monospace')

# Unmapped cells note
ax.text(table_x + 2.5, table_y + 0.15, '✓ Zero unmapped cells — all corners',
        fontsize=6.5, ha='center', va='center', color=DONE_COLOR,
        fontfamily='monospace', fontweight='bold')

# ═══════════════════════════════════════════════════════════════════
# LEGEND
# ═══════════════════════════════════════════════════════════════════

legend_x, legend_y = 0.8, 14.5
legend_items = [
    (CLK_VCO_COLOR, 'clk_vco (6.835 GHz)'),
    (SPI_CLK_COLOR, 'spi_clk (~10 MHz)'),
    (CDC_COLOR, 'CDC crossing'),
    (ANALOG_COLOR, 'Analog (external)'),
]
for i, (color, label) in enumerate(legend_items):
    ax.add_patch(FancyBboxPatch((legend_x + i*2.8, legend_y), 0.25, 0.18,
                                 boxstyle="round,pad=0.02", facecolor=color, edgecolor='none'))
    ax.text(legend_x + 0.35 + i*2.8, legend_y + 0.09, label, fontsize=6.5,
            ha='left', va='center', color='#c9d1d9', fontfamily='monospace')

# ═══════════════════════════════════════════════════════════════════
# VERIFICATION STATUS
# ═══════════════════════════════════════════════════════════════════

vx, vy = 5.5, 1.0
ax.text(vx, vy + 0.6, 'Verification:', fontsize=8, ha='left', va='center',
        color=TITLE_COLOR, fontweight='bold', fontfamily='monospace')
checks = ['Lint: CLEAN (verilator -Wall)', 'RTL sim: 11/11 PASS',
          'Gate sim: 11/11 PASS (TT)', 'Synth: 3 corners clean']
for i, c in enumerate(checks):
    ax.text(vx + 0.3 + i*2.5, vy + 0.1, f'✓ {c}', fontsize=6,
            ha='left', va='center', color=DONE_COLOR, fontfamily='monospace')

# ─── Save ───────────────────────────────────────────────────────────
plt.tight_layout(pad=0.5)
fig.savefig('csac_chip_professional.png', dpi=180, facecolor=fig.get_facecolor(),
            bbox_inches='tight', pad_inches=0.3)
print("Saved: reports/csac_chip_professional.png")
