#!/usr/bin/env python3
"""Visualize CSAC digital_top Yosys synthesis results for SKY130."""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import numpy as np

# ── Synthesis data ──────────────────────────────────────────────────────────

cells = {
    'dfrtp_1': 134, 'dfstp_2': 1,
    'and2_0': 8, 'and3_1': 6, 'and4_1': 7, 'or3_1': 5, 'or4_1': 1,
    'nand2_1': 65, 'nand2b_1': 12, 'nand3_1': 15, 'nand3b_1': 2,
    'nand4_1': 11, 'nand4b_1': 1,
    'nor2_1': 42, 'nor2b_1': 6, 'nor3_1': 4, 'nor3b_1': 1,
    'nor4_1': 4, 'nor4b_1': 2,
    'xnor2_1': 85, 'xnor3_1': 10, 'xor2_1': 38, 'xor3_1': 1,
    'a21oi_1': 27, 'a21o_1': 4, 'a211oi_1': 2, 'a22o_1': 11, 'a22oi_1': 20,
    'a222oi_1': 10, 'a31o_1': 1, 'a31oi_1': 13,
    'o21ai_0': 27, 'o21a_1': 1, 'o211ai_1': 9, 'o221ai_1': 1,
    'o22a_1': 1, 'o31ai_1': 3, 'o41ai_1': 1,
    'mux2_1': 15, 'mux2i_1': 1,
    'clkinv_1': 7, 'lpflow_isobufsrc_1': 30, 'lpflow_inputiso1p_1': 5,
    'maj3_1': 23,
}

categories = {
    'Flip-Flops\n(registers)': ['dfrtp_1', 'dfstp_2'],
    'XOR/XNOR\n(arithmetic)': ['xnor2_1', 'xnor3_1', 'xor2_1', 'xor3_1'],
    'NAND': ['nand2_1', 'nand2b_1', 'nand3_1', 'nand3b_1', 'nand4_1', 'nand4b_1'],
    'NOR': ['nor2_1', 'nor2b_1', 'nor3_1', 'nor3b_1', 'nor4_1', 'nor4b_1'],
    'AOI/OAI\n(complex)': ['a21oi_1', 'a21o_1', 'a211oi_1', 'a22o_1', 'a22oi_1',
                           'a222oi_1', 'a31o_1', 'a31oi_1', 'o21ai_0', 'o21a_1',
                           'o211ai_1', 'o221ai_1', 'o22a_1', 'o31ai_1', 'o41ai_1'],
    'AND/OR': ['and2_0', 'and3_1', 'and4_1', 'or3_1', 'or4_1'],
    'MUX': ['mux2_1', 'mux2i_1'],
    'Buffers &\nInverters': ['clkinv_1', 'lpflow_isobufsrc_1', 'lpflow_inputiso1p_1'],
    'Majority\n(carry logic)': ['maj3_1'],
}

cat_counts = {cat: sum(cells.get(k, 0) for k in keys) for cat, keys in categories.items()}

# ── Create figure ───────────────────────────────────────────────────────────

fig = plt.figure(figsize=(18, 11), facecolor='#0d1117')
mono = 'monospace'

fig.text(0.5, 0.96, 'CSAC Digital Top \u2014 SKY130 Synthesis Results',
         ha='center', va='top', fontsize=22, fontweight='bold', color='#58a6ff', fontfamily=mono)
fig.text(0.5, 0.93, 'Yosys \u2192 sky130_fd_sc_hd  |  673 cells  |  7,176 um2  |  135 flip-flops',
         ha='center', va='top', fontsize=13, color='#8b949e', fontfamily=mono)

# ── Panel 1: Block diagram ─────────────────────────────────────────────────

ax1 = fig.add_axes([0.03, 0.42, 0.45, 0.48])
ax1.set_xlim(0, 10); ax1.set_ylim(0, 10)
ax1.set_facecolor('#161b22'); ax1.set_xticks([]); ax1.set_yticks([])
for s in ax1.spines.values(): s.set_color('#30363d')

ax1.text(5, 9.6, 'Chip Architecture', ha='center', fontsize=14,
         fontweight='bold', color='#c9d1d9', fontfamily=mono)

bs = dict(boxstyle='round,pad=0.3', linewidth=1.5)

def block(ax, xy, wh, title, sub, fc, ec):
    ax.add_patch(FancyBboxPatch(xy, wh[0], wh[1], **bs, facecolor=fc, edgecolor=ec))
    cx = xy[0] + wh[0]/2
    ax.text(cx, xy[1] + wh[1]*0.7, title, ha='center', va='center',
            fontsize=9, fontweight='bold', color=ec, fontfamily=mono)
    if sub:
        lines = sub if isinstance(sub, list) else [sub]
        for i, line in enumerate(lines):
            ax.text(cx, xy[1] + wh[1]*0.35 - i*0.4, line, ha='center', va='center',
                    fontsize=7, color='#8b949e', fontfamily=mono)

block(ax1, (0.3, 7.0), (3.0, 1.5), '33-bit Counter', '6.835 GHz / 2^33', '#1a3a5c', '#58a6ff')
block(ax1, (4.0, 7.0), (2.5, 1.5), 'Clock Enable', 'Edge Detect', '#1a3a2c', '#3fb950')
block(ax1, (7.2, 7.0), (2.5, 1.5), '1 Hz Output', 'count_1hz[31:0]', '#1a3a2c', '#3fb950')
block(ax1, (0.3, 4.5), (3.5, 2.0), 'PID Controller', ['Kp=2 Ki=1 Kd=3', '-> dac_vco_tune[9:0]'], '#3b1a3a', '#bc8cff')
block(ax1, (4.3, 4.5), (2.5, 2.0), 'Lock Detect', ['err < 10 for', '8 consecutive'], '#3a2a1a', '#d29922')
block(ax1, (7.2, 4.8), (2.5, 1.5), 'Status Byte', 'lock|hb|diag', '#3a2a1a', '#d29922')
block(ax1, (0.3, 2.0), (3.5, 2.0), 'Thermal Ctrl', ['Setpoint: 350', '-> dac_heater[7:0]'], '#3a1a1a', '#f85149')
block(ax1, (4.3, 2.0), (2.5, 2.0), 'SPI Slave', ['9 registers', '41 cells'], '#1a2a3a', '#79c0ff')

ax1.text(0.15, 0.8, 'INPUTS:', color='#58a6ff', fontsize=8, fontweight='bold', fontfamily=mono)
ax1.text(0.15, 0.3, 'clk_vco  photo_adc[7:0]  temp_adc[9:0]  spi_{clk,mosi,cs}  reset_n',
         color='#8b949e', fontsize=7, fontfamily=mono)

arr = dict(arrowstyle='->', color='#484f58', lw=1.5)
ax1.annotate('', xy=(4.0, 7.75), xytext=(3.3, 7.75), arrowprops=arr)
ax1.annotate('', xy=(7.2, 7.75), xytext=(6.5, 7.75), arrowprops=arr)
ax1.annotate('', xy=(2.05, 6.5), xytext=(2.05, 7.0), arrowprops=dict(arrowstyle='->', color='#3fb950', lw=1.2))
ax1.annotate('', xy=(5.55, 6.5), xytext=(5.55, 7.0), arrowprops=dict(arrowstyle='->', color='#3fb950', lw=1.2))
ax1.text(3.0, 6.7, 'ce_servo', color='#3fb950', fontsize=7, fontfamily=mono)

# ── Panel 2: Cell distribution bar chart ────────────────────────────────────

ax2 = fig.add_axes([0.55, 0.42, 0.42, 0.48])
ax2.set_facecolor('#161b22')
for s in ax2.spines.values(): s.set_color('#30363d')

colors = ['#58a6ff', '#bc8cff', '#f85149', '#d29922', '#3fb950',
          '#79c0ff', '#ff7b72', '#ffa657', '#a5d6ff']

cat_names = list(cat_counts.keys())
cat_values = list(cat_counts.values())
idx = np.argsort(cat_values)[::-1]
cat_names = [cat_names[i] for i in idx]
cat_values = [cat_values[i] for i in idx]

bars = ax2.barh(range(len(cat_names)), cat_values,
                color=[colors[i % len(colors)] for i in range(len(cat_names))],
                alpha=0.85, edgecolor='#30363d', height=0.7)
ax2.set_yticks(range(len(cat_names)))
ax2.set_yticklabels(cat_names, fontsize=9, color='#c9d1d9', fontfamily=mono)
ax2.invert_yaxis()
ax2.set_xlabel('Number of Cells', color='#8b949e', fontsize=10, fontfamily=mono)
ax2.tick_params(axis='x', colors='#8b949e')
ax2.set_title('Cell Distribution by Function', color='#c9d1d9', fontsize=14,
              fontweight='bold', fontfamily=mono, pad=10)

for bar, val in zip(bars, cat_values):
    ax2.text(bar.get_width() + 2, bar.get_y() + bar.get_height()/2,
             str(val), va='center', color='#8b949e', fontsize=10, fontfamily=mono)
ax2.set_xlim(0, max(cat_values) * 1.15)

# ── Panel 3: Key metrics boxes ─────────────────────────────────────────────

ax3 = fig.add_axes([0.03, 0.03, 0.94, 0.32])
ax3.set_xlim(0, 10); ax3.set_ylim(0, 4)
ax3.set_facecolor('#161b22'); ax3.set_xticks([]); ax3.set_yticks([])
for s in ax3.spines.values(): s.set_color('#30363d')

metrics = [
    ('673', 'Total\nCells', '#58a6ff'),
    ('135', 'Flip-\nFlops', '#bc8cff'),
    ('7,176', 'Area\n(um2)', '#3fb950'),
    ('0.08%', 'of 3x3mm\nDie Used', '#d29922'),
    ('2', 'Clock\nDomains', '#f85149'),
    ('130nm', 'SKY130\nProcess', '#79c0ff'),
]

for i, (val, label, color) in enumerate(metrics):
    x = 0.4 + i * 1.6
    ax3.add_patch(FancyBboxPatch((x, 0.5), 1.35, 3.0, boxstyle='round,pad=0.2',
                                 facecolor='#0d1117', edgecolor=color, linewidth=2))
    ax3.text(x + 0.675, 2.7, val, ha='center', va='center',
             fontsize=16, fontweight='bold', color=color, fontfamily=mono)
    ax3.text(x + 0.675, 1.3, label, ha='center', va='center',
             fontsize=10, color='#8b949e', fontfamily=mono)

plt.savefig('/home/ubuntu/atomicclock-mems/09_circuit_design/digital_top_synth.png',
            dpi=150, bbox_inches='tight', facecolor='#0d1117')
print("Saved: digital_top_synth.png")
