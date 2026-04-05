#!/usr/bin/env python3
"""Generate professional VCO schematic PNG."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import os

OUTDIR = os.path.dirname(os.path.abspath(__file__))

fig, ax = plt.subplots(1, 1, figsize=(14, 10))
ax.set_xlim(0, 14)
ax.set_ylim(0, 10)
ax.set_aspect('equal')
ax.axis('off')

# Title
ax.text(7, 9.7, 'SKY130 6.835 GHz LC-VCO Schematic', fontsize=16, fontweight='bold',
        ha='center', va='center', fontfamily='sans-serif')
ax.text(7, 9.3, 'NMOS Cross-Coupled | BSIM4 Level 54 | ind_03_90 Tank', fontsize=10,
        ha='center', va='center', color='gray')

# VDD rail
ax.plot([3, 11], [8.5, 8.5], 'r-', linewidth=2)
ax.text(11.2, 8.5, 'VDD = 1.8V', fontsize=10, color='red', va='center')

# GND rail
ax.plot([3, 11], [0.5, 0.5], 'k-', linewidth=2)
ax.text(11.2, 0.5, 'GND', fontsize=10, va='center')

# Inductor (center-tapped)
# Left half
cx, cy = 7, 7.5
for i in range(4):
    theta = np.linspace(0, np.pi, 20) if i % 2 == 0 else np.linspace(np.pi, 0, 20)
    r = 0.2
    x = cx - 1.5 + i * 0.3 + r * np.cos(theta)
    y = cy + r * np.sin(theta)

# Simplified inductor representation
ax.annotate('', xy=(5, 8), xytext=(5, 7),
            arrowprops=dict(arrowstyle='-', connectionstyle='arc3,rad=0.3', lw=2, color='blue'))
ax.annotate('', xy=(5.3, 7), xytext=(5.3, 8),
            arrowprops=dict(arrowstyle='-', connectionstyle='arc3,rad=0.3', lw=2, color='blue'))
ax.annotate('', xy=(5.6, 8), xytext=(5.6, 7),
            arrowprops=dict(arrowstyle='-', connectionstyle='arc3,rad=0.3', lw=2, color='blue'))

ax.annotate('', xy=(8.4, 8), xytext=(8.4, 7),
            arrowprops=dict(arrowstyle='-', connectionstyle='arc3,rad=-0.3', lw=2, color='blue'))
ax.annotate('', xy=(8.7, 7), xytext=(8.7, 8),
            arrowprops=dict(arrowstyle='-', connectionstyle='arc3,rad=-0.3', lw=2, color='blue'))
ax.annotate('', xy=(9, 8), xytext=(9, 7),
            arrowprops=dict(arrowstyle='-', connectionstyle='arc3,rad=-0.3', lw=2, color='blue'))

# Inductor body rectangle
ind_rect = patches.FancyBboxPatch((4.5, 6.8), 5, 1.4, boxstyle="round,pad=0.1",
                                   facecolor='lightyellow', edgecolor='blue', linewidth=2)
ax.add_patch(ind_rect)
ax.text(7, 7.5, 'sky130_fd_pr__ind_03_90\nL_half = 760.5 pH\nSRF = 16.5 GHz',
        fontsize=8, ha='center', va='center', fontweight='bold')

# Center tap to VDD
ax.plot([7, 7], [8.2, 8.5], 'b-', linewidth=1.5)
ax.plot(7, 8.2, 'bo', markersize=4)
ax.text(7.2, 8.35, 'ct', fontsize=8, color='blue')

# Left output node (outp)
ax.plot([4.5, 4.5], [7.5, 5.5], 'k-', linewidth=1.5)
ax.plot(4.5, 7.5, 'ko', markersize=5)
ax.text(3.8, 7.5, 'outp', fontsize=10, fontweight='bold', color='darkgreen', va='center')

# Right output node (outn)
ax.plot([9.5, 9.5], [7.5, 5.5], 'k-', linewidth=1.5)
ax.plot(9.5, 7.5, 'ko', markersize=5)
ax.text(9.8, 7.5, 'outn', fontsize=10, fontweight='bold', color='darkgreen', va='center')

# Tank capacitors (left)
cap_rect_l = patches.FancyBboxPatch((3.3, 6.2), 1, 0.6, boxstyle="round,pad=0.05",
                                     facecolor='lightcyan', edgecolor='teal', linewidth=1.5)
ax.add_patch(cap_rect_l)
ax.text(3.8, 6.5, 'C=565fF', fontsize=7, ha='center', va='center')
ax.plot([4.5, 4.3], [6.5, 6.5], 'k-', linewidth=1)
ax.plot([3.3, 3.3], [6.5, 0.5], 'k-', linewidth=1, linestyle=':')

# Tank capacitors (right)
cap_rect_r = patches.FancyBboxPatch((9.7, 6.2), 1, 0.6, boxstyle="round,pad=0.05",
                                     facecolor='lightcyan', edgecolor='teal', linewidth=1.5)
ax.add_patch(cap_rect_r)
ax.text(10.2, 6.5, 'C=565fF', fontsize=7, ha='center', va='center')
ax.plot([9.5, 9.7], [6.5, 6.5], 'k-', linewidth=1)
ax.plot([10.7, 10.7], [6.5, 0.5], 'k-', linewidth=1, linestyle=':')

# Varactors
var_l = patches.FancyBboxPatch((3.3, 5.2), 1, 0.5, boxstyle="round,pad=0.05",
                                facecolor='lightyellow', edgecolor='orange', linewidth=1.5)
ax.add_patch(var_l)
ax.text(3.8, 5.45, 'Cv=60fF', fontsize=7, ha='center', va='center')
ax.plot([4.5, 4.3], [5.45, 5.45], 'k-', linewidth=1)

var_r = patches.FancyBboxPatch((9.7, 5.2), 1, 0.5, boxstyle="round,pad=0.05",
                                facecolor='lightyellow', edgecolor='orange', linewidth=1.5)
ax.add_patch(var_r)
ax.text(10.2, 5.45, 'Cv=60fF', fontsize=7, ha='center', va='center')
ax.plot([9.5, 9.7], [5.45, 5.45], 'k-', linewidth=1)

# Vtune connection
ax.plot([3.3, 2.5, 2.5], [5.45, 5.45, 5.45], 'orange', linewidth=1.5)
ax.plot([10.7, 11.5, 11.5], [5.45, 5.45, 5.45], 'orange', linewidth=1.5)
ax.text(1.5, 5.45, 'Vtune', fontsize=10, color='orange', fontweight='bold', va='center')

# Cross-coupled NMOS pair
# M1 (left)
m1_rect = patches.FancyBboxPatch((4, 3.8), 1.5, 1.2, boxstyle="round,pad=0.1",
                                  facecolor='lightgreen', edgecolor='darkgreen', linewidth=2)
ax.add_patch(m1_rect)
ax.text(4.75, 4.4, 'M1 (LVT)\nW=8µm×10\nL=150nm', fontsize=7, ha='center', va='center')

# M2 (right)
m2_rect = patches.FancyBboxPatch((8.5, 3.8), 1.5, 1.2, boxstyle="round,pad=0.1",
                                  facecolor='lightgreen', edgecolor='darkgreen', linewidth=2)
ax.add_patch(m2_rect)
ax.text(9.25, 4.4, 'M2 (LVT)\nW=8µm×10\nL=150nm', fontsize=7, ha='center', va='center')

# Drain connections
ax.plot([4.5, 4.5], [5.5, 5.0], 'k-', linewidth=1.5)
ax.plot([9.5, 9.5], [5.5, 5.0], 'k-', linewidth=1.5)

# Cross-coupling (gate connections)
# M1 gate from outn
ax.plot([4.0, 3.5, 3.5, 9.5], [4.4, 4.4, 3.3, 3.3], 'darkred', linewidth=1.5, linestyle='--')
ax.plot([9.5, 9.5], [3.3, 3.8], 'darkred', linewidth=1)
ax.annotate('', xy=(4.0, 4.4), xytext=(3.5, 4.4),
            arrowprops=dict(arrowstyle='->', color='darkred', lw=1.5))

# M2 gate from outp
ax.plot([10, 10.5, 10.5, 4.5], [4.4, 4.4, 3.0, 3.0], 'darkblue', linewidth=1.5, linestyle='--')
ax.plot([4.5, 4.5], [3.0, 3.8], 'darkblue', linewidth=1)
ax.annotate('', xy=(10, 4.4), xytext=(10.5, 4.4),
            arrowprops=dict(arrowstyle='->', color='darkblue', lw=1.5))

ax.text(6, 3.15, 'Cross-coupled', fontsize=8, ha='center', color='purple', fontstyle='italic')

# Source connections to tail
ax.plot([4.75, 4.75, 7, 9.25, 9.25], [3.8, 2.5, 2.5, 2.5, 3.8], 'k-', linewidth=1.5)
ax.plot(7, 2.5, 'ko', markersize=5)
ax.text(7.3, 2.7, 'tail', fontsize=9, va='center')

# Tail current source
tail_rect = patches.FancyBboxPatch((6, 1.0), 2, 1.0, boxstyle="round,pad=0.1",
                                    facecolor='mistyrose', edgecolor='brown', linewidth=2)
ax.add_patch(tail_rect)
ax.text(7, 1.5, 'Mtail (LVT)\nW=8µm×20\nVb=0.9V', fontsize=7, ha='center', va='center')

ax.plot([7, 7], [2.5, 2.0], 'k-', linewidth=1.5)
ax.plot([7, 7], [1.0, 0.5], 'k-', linewidth=1.5)

# Bias voltage
ax.plot([6, 5.5], [1.5, 1.5], 'brown', linewidth=1.5)
ax.text(4.5, 1.5, 'Vbias\n0.9V', fontsize=8, ha='center', va='center', color='brown')

# Performance annotations
perf_box = patches.FancyBboxPatch((0.3, 0.3), 3, 2.5, boxstyle="round,pad=0.15",
                                   facecolor='white', edgecolor='navy', linewidth=1.5)
ax.add_patch(perf_box)
ax.text(1.8, 2.5, 'Performance', fontsize=9, fontweight='bold', ha='center', color='navy')
ax.text(0.5, 2.1, f'f₀ = 6.834 GHz', fontsize=8)
ax.text(0.5, 1.7, f'Vamp = 1.04 V diff', fontsize=8)
ax.text(0.5, 1.3, f'P = 1.57 mW', fontsize=8)
ax.text(0.5, 0.9, f'PN = -123 dBc/Hz @1MHz', fontsize=8)
ax.text(0.5, 0.5, f'Startup < 1 ns', fontsize=8)

import numpy as np  # needed for earlier plotting

plt.savefig(os.path.join(OUTDIR, 'vco_schematic.png'), dpi=150, bbox_inches='tight',
            facecolor='white', edgecolor='none')
print("Schematic saved to vco_design/vco_schematic.png")
