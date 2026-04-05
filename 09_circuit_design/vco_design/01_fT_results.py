#!/usr/bin/env python3
"""Phase 1: Parse ngspice fT characterization data and generate plots."""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import re
import os

OUTDIR = os.path.dirname(os.path.abspath(__file__))

# ===================================================================
# 1) Parse DC operating point data from log
# ===================================================================
vgs_dc = []
id_dc = []
with open(os.path.join(OUTDIR, '../vco_design/01_dc.log') if not os.path.exists(os.path.join(OUTDIR, '01_dc.log')) else os.path.join(OUTDIR, '01_dc.log'), 'r') as f:
    for line in f:
        m = re.match(r'OP_DATA: Vgs=([\d.]+) Id=([\d.eE+-]+)', line)
        if m:
            vgs_dc.append(float(m.group(1)))
            id_dc.append(float(m.group(2)))

vgs_dc = np.array(vgs_dc)
id_dc = np.array(id_dc)
# Compute gm = dId/dVgs
gm_dc = np.gradient(id_dc, vgs_dc)

# ===================================================================
# 2) Parse AC data to extract fT at multiple bias points
# ===================================================================
def parse_ac_file(filepath):
    """Parse ngspice wrdata AC file.
    Format: freq freq 0 freq id_real id_imag freq ig_real ig_imag
    """
    data = np.loadtxt(filepath, skiprows=1)
    freq = data[:, 0]
    id_real = data[:, 4]
    id_imag = data[:, 5]
    ig_real = data[:, 7]
    ig_imag = data[:, 8]

    id_mag = np.sqrt(id_real**2 + id_imag**2)
    ig_mag = np.sqrt(ig_real**2 + ig_imag**2)

    # h21 = |Id/Ig|
    h21 = id_mag / np.maximum(ig_mag, 1e-30)
    h21_db = 20 * np.log10(np.maximum(h21, 1e-10))

    return freq, h21, h21_db

# AC files at different bias points
ac_files = {
    0.6: os.path.join(OUTDIR, '01_ac_0p6.dat'),
    0.9: os.path.join(OUTDIR, '01_ac_0p9.dat'),
    1.2: os.path.join(OUTDIR, '01_ac_1p2.dat'),
    1.5: os.path.join(OUTDIR, '01_ac_1p5.dat'),
}

# Extract fT for each bias
ft_values = {}
gm_from_ac = {}
for vgs, fpath in ac_files.items():
    if os.path.exists(fpath):
        freq, h21, h21_db = parse_ac_file(fpath)
        # Find fT: where h21_db crosses 0 dB
        # Use interpolation
        for i in range(len(h21_db) - 1):
            if h21_db[i] > 0 and h21_db[i+1] <= 0:
                # Linear interpolation
                f1, f2 = freq[i], freq[i+1]
                d1, d2 = h21_db[i], h21_db[i+1]
                ft = f1 + (f2 - f1) * (0 - d1) / (d2 - d1)
                ft_values[vgs] = ft
                break

        # gm from low-frequency |h21| * omega * Cgg ≈ from |id_ac| at low freq
        data = np.loadtxt(fpath, skiprows=1)
        id_real_lf = data[0, 4]  # real part at lowest freq
        gm_from_ac[vgs] = abs(id_real_lf)  # gm ≈ |id/vgs| at low freq (vgs_ac = 1)

# ===================================================================
# 3) Generate Plots
# ===================================================================
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle('SKY130 RF NFET LVT (W=5µm, L=150nm, nf=4) — fT Characterization\nReal BSIM4 Models', fontsize=14, fontweight='bold')

# Plot 1: Id vs Vgs (log scale)
ax1 = axes[0, 0]
ax1.semilogy(vgs_dc, id_dc, 'b-', linewidth=2)
ax1.set_xlabel('Vgs (V)')
ax1.set_ylabel('Id (A)')
ax1.set_title('Drain Current vs Gate Voltage')
ax1.grid(True, which='both', alpha=0.3)
ax1.set_ylim([1e-10, 1e-2])

# Plot 2: gm vs Vgs
ax2 = axes[0, 1]
ax2.plot(vgs_dc, gm_dc * 1e3, 'r-', linewidth=2)
ax2.set_xlabel('Vgs (V)')
ax2.set_ylabel('gm (mS)')
ax2.set_title('Transconductance vs Gate Voltage')
ax2.grid(True, alpha=0.3)

# Plot 3: |h21| vs frequency at Vgs=0.9V
ax3 = axes[1, 0]
colors = ['blue', 'green', 'red', 'purple']
for idx, (vgs, fpath) in enumerate(sorted(ac_files.items())):
    if os.path.exists(fpath):
        freq, h21, h21_db = parse_ac_file(fpath)
        ft_str = f" (fT={ft_values.get(vgs, 0)/1e9:.1f} GHz)" if vgs in ft_values else ""
        ax3.semilogx(freq / 1e9, h21_db, color=colors[idx], linewidth=1.5,
                     label=f'Vgs={vgs}V{ft_str}')

ax3.axhline(y=0, color='k', linestyle='--', alpha=0.5, label='0 dB (fT)')
ax3.axvline(x=6.835, color='orange', linestyle='--', alpha=0.7, label='6.835 GHz target')
ax3.set_xlabel('Frequency (GHz)')
ax3.set_ylabel('|h21| (dB)')
ax3.set_title('Current Gain |h21| vs Frequency')
ax3.legend(fontsize=8)
ax3.grid(True, which='both', alpha=0.3)
ax3.set_xlim([0.001, 200])

# Plot 4: fT vs Vgs summary + decision gate
ax4 = axes[1, 1]
ft_vgs = sorted(ft_values.keys())
ft_vals_ghz = [ft_values[v] / 1e9 for v in ft_vgs]
ax4.plot(ft_vgs, ft_vals_ghz, 'ko-', linewidth=2, markersize=8)
ax4.axhline(y=20, color='r', linestyle='--', alpha=0.7, label='fT > 20 GHz threshold')
ax4.axhline(y=6.835, color='orange', linestyle='--', alpha=0.7, label='6.835 GHz target')
ax4.set_xlabel('Vgs (V)')
ax4.set_ylabel('fT (GHz)')
ax4.set_title('Unity Current Gain Frequency vs Bias')
ax4.legend(fontsize=9)
ax4.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(os.path.join(OUTDIR, 'fT_characterization.png'), dpi=150, bbox_inches='tight')
print("Plot saved to vco_design/fT_characterization.png")

# ===================================================================
# 4) Print Summary and Decision Gate
# ===================================================================
print("\n" + "="*60)
print("PHASE 1 RESULTS: SKY130 RF NFET LVT fT Characterization")
print("="*60)
print(f"Device: sky130_fd_pr__nfet_01v8_lvt, W=5µm, L=150nm, nf=4")
print(f"Model: BSIM4 Level 54, TT corner")
print(f"\nDC Operating Points:")
for v, i in zip(vgs_dc, id_dc):
    if v in [0.5, 0.7, 0.9, 1.0, 1.2, 1.5]:
        print(f"  Vgs={v:.1f}V: Id={i*1e3:.4f} mA")

print(f"\nTransconductance:")
for v, g in zip(vgs_dc, gm_dc):
    if v in [0.7, 0.9, 1.0, 1.2, 1.5]:
        print(f"  Vgs={v:.1f}V: gm={g*1e3:.2f} mS")

print(f"\nfT (Unity Current Gain Frequency):")
for vgs in sorted(ft_values.keys()):
    ft = ft_values[vgs]
    print(f"  Vgs={vgs:.1f}V: fT = {ft/1e9:.1f} GHz")

max_ft = max(ft_values.values()) if ft_values else 0
print(f"\n  Peak fT = {max_ft/1e9:.1f} GHz")

print(f"\n{'='*60}")
print("DECISION GATE:")
if max_ft > 20e9:
    print(f"  fT = {max_ft/1e9:.1f} GHz > 20 GHz")
    print(f"  PASS: 6.835 GHz VCO is FEASIBLE on SKY130")
    print(f"  fT/f0 ratio = {max_ft/6.835e9:.1f}x (need >3x)")
    if max_ft / 6.835e9 > 3:
        print(f"  Excellent margin for direct VCO design")
    else:
        print(f"  Tight margin — consider prescaler as backup")
else:
    print(f"  fT = {max_ft/1e9:.1f} GHz < 20 GHz")
    print(f"  FAIL: Must use prescaler architecture (Phase 6)")
print("="*60)
