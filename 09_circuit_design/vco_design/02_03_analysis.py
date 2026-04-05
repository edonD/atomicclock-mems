#!/usr/bin/env python3
"""Phase 2 & 3: Inductor and Varactor characterization analysis."""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import re, os

OUTDIR = os.path.dirname(os.path.abspath(__file__))

# ===================================================================
# Phase 2: Inductor Analysis
# ===================================================================
def parse_inductor_data(filepath):
    """Parse inductor AC data. Columns: freq freq 0 freq I_real I_imag"""
    data = np.loadtxt(filepath, skiprows=1)
    freq = data[:, 0]
    i_real = data[:, 4]
    i_imag = data[:, 5]
    # Z = V/I = 1/(I_real + j*I_imag) since V=1
    i_complex = i_real + 1j * i_imag
    z = 1.0 / i_complex
    # Z = R + jX; for inductor, X = omega*L, Q = X/R
    omega = 2 * np.pi * freq
    L_eff = np.imag(z) / omega
    Q = np.imag(z) / np.real(z)
    return freq, z, L_eff, Q

inductors = {
    'ind_03_90 (0.9 nH nom)': os.path.join(OUTDIR, '02_ind1_data.dat'),
    'ind_05_125 (1.25 nH nom)': os.path.join(OUTDIR, '02_ind2_data.dat'),
    'ind_05_220 (2.2 nH nom)': os.path.join(OUTDIR, '02_ind3_data.dat'),
}

# Nominal half-inductances from models
nominal_L = {
    'ind_03_90 (0.9 nH nom)': 760.5e-12 * 2,  # 1.521 nH total
    'ind_05_125 (1.25 nH nom)': 2.895e-9 * 2,  # 5.79 nH total
    'ind_05_220 (2.2 nH nom)': 4.96e-9 * 2,    # 9.92 nH total
}

print("="*60)
print("PHASE 2: INDUCTOR CHARACTERIZATION")
print("="*60)

fig2, axes2 = plt.subplots(1, 3, figsize=(16, 5))
fig2.suptitle('SKY130 PDK Inductor Characterization', fontsize=14, fontweight='bold')

colors = ['blue', 'red', 'green']
f_target = 6.835e9

ind_results = {}
for idx, (name, fpath) in enumerate(inductors.items()):
    freq, z, L_eff, Q = parse_inductor_data(fpath)

    # Find SRF (where inductance crosses zero or Q goes negative)
    srf = None
    for i in range(1, len(L_eff)):
        if L_eff[i] < 0 and L_eff[i-1] > 0:
            srf = freq[i]
            break

    # Values at 6.835 GHz
    idx_target = np.argmin(np.abs(freq - f_target))
    L_at_target = L_eff[idx_target]
    Q_at_target = Q[idx_target]

    ind_results[name] = {
        'L': L_at_target, 'Q': Q_at_target, 'SRF': srf,
        'freq': freq, 'L_eff': L_eff, 'Q_full': Q
    }

    print(f"\n{name}:")
    print(f"  Nominal L: {nominal_L[name]*1e9:.3f} nH")
    print(f"  L at 6.835 GHz: {L_at_target*1e9:.3f} nH")
    print(f"  Q at 6.835 GHz: {Q_at_target:.1f}")
    print(f"  SRF: {'%.2f GHz' % (srf/1e9) if srf else 'not found (>50 GHz)'}")
    if srf and srf < f_target:
        print(f"  WARNING: SRF < 6.835 GHz — NOT usable at target frequency!")

# Plot L(f)
for idx, (name, r) in enumerate(ind_results.items()):
    axes2[0].semilogx(r['freq']/1e9, r['L_eff']*1e9, color=colors[idx],
                      label=name.split('(')[0].strip(), linewidth=1.5)
axes2[0].axvline(x=6.835, color='orange', linestyle='--', alpha=0.7)
axes2[0].set_xlabel('Frequency (GHz)')
axes2[0].set_ylabel('L_eff (nH)')
axes2[0].set_title('Effective Inductance')
axes2[0].legend(fontsize=8)
axes2[0].grid(True, alpha=0.3)
axes2[0].set_ylim([-5, 15])

# Plot Q(f)
for idx, (name, r) in enumerate(ind_results.items()):
    axes2[1].semilogx(r['freq']/1e9, r['Q_full'], color=colors[idx],
                      label=name.split('(')[0].strip(), linewidth=1.5)
axes2[1].axvline(x=6.835, color='orange', linestyle='--', alpha=0.7)
axes2[1].set_xlabel('Frequency (GHz)')
axes2[1].set_ylabel('Q factor')
axes2[1].set_title('Quality Factor')
axes2[1].legend(fontsize=8)
axes2[1].grid(True, alpha=0.3)
axes2[1].set_ylim([-20, 30])

# Plot |Z|(f)
for idx, (name, r) in enumerate(ind_results.items()):
    axes2[2].loglog(r['freq']/1e9, np.abs(1.0/(np.loadtxt(inductors[name], skiprows=1)[:, 4] + 1j*np.loadtxt(inductors[name], skiprows=1)[:, 5])),
                    color=colors[idx], label=name.split('(')[0].strip(), linewidth=1.5)
axes2[2].axvline(x=6.835, color='orange', linestyle='--', alpha=0.7)
axes2[2].set_xlabel('Frequency (GHz)')
axes2[2].set_ylabel('|Z| (Ω)')
axes2[2].set_title('Impedance Magnitude')
axes2[2].legend(fontsize=8)
axes2[2].grid(True, which='both', alpha=0.3)

plt.tight_layout()
plt.savefig(os.path.join(OUTDIR, 'inductor_characterization.png'), dpi=150, bbox_inches='tight')
print("\nPlot saved to vco_design/inductor_characterization.png")

# Selection
print(f"\n--- INDUCTOR SELECTION ---")
best = None
for name, r in ind_results.items():
    usable = (r['SRF'] is None or r['SRF'] > f_target) and r['Q'] > 0 and r['L'] > 0
    if usable:
        if best is None or r['Q'] > ind_results[best]['Q']:
            best = name
if best:
    print(f"Selected: {best}")
    print(f"  L = {ind_results[best]['L']*1e9:.3f} nH, Q = {ind_results[best]['Q']:.1f}")
else:
    print("No PDK inductor usable at 6.835 GHz — will need custom model")

# ===================================================================
# Phase 3: Varactor Analysis
# ===================================================================
print(f"\n{'='*60}")
print("PHASE 3: VARACTOR CHARACTERIZATION")
print("="*60)

# Parse VAR_DATA from log
vtune_vals = []
cap_vals = []
with open(os.path.join(OUTDIR, '03_varactor.log'), 'r') as f:
    for line in f:
        m = re.match(r'VAR_DATA: Vtune=([\d.]+) Iac_re=([\d.eE+-]+)', line)
        if m:
            vtune = float(m.group(1))
            iac = float(m.group(2))
            # C = |I| / (2*pi*f) at f=1 GHz, V=1
            cap = abs(iac) / (2 * np.pi * 1e9)
            vtune_vals.append(vtune)
            cap_vals.append(cap)

vtune_vals = np.array(vtune_vals)
cap_vals = np.array(cap_vals)  # in Farads

print(f"Varactor: sky130_fd_pr__cap_var_lvt, w=1, l=0.5")
print(f"  Cmax (Vtune=0V): {cap_vals[0]*1e15:.2f} fF")
print(f"  Cmin (Vtune=1.8V): {cap_vals[-1]*1e15:.2f} fF")
print(f"  Tuning ratio: {cap_vals[0]/cap_vals[-1]:.2f}")
print(f"  ΔC: {(cap_vals[0]-cap_vals[-1])*1e15:.2f} fF")

# For VCO: need to scale varactors
# Using ind_03_90 half-inductor: L_half = 760.5 pH
# f0 = 1/(2*pi*sqrt(L*C)) => C = 1/(4*pi^2*f0^2*L)
L_half = 760.5e-12
C_needed = 1.0 / (4 * np.pi**2 * (6.835e9)**2 * L_half)
print(f"\nFor 6.835 GHz with L_half = {L_half*1e12:.1f} pH:")
print(f"  C_needed per side = {C_needed*1e15:.1f} fF")
print(f"  This includes varactor + parasitic Cds of cross-coupled pair")

# Plot
fig3, (ax3a, ax3b) = plt.subplots(1, 2, figsize=(12, 5))
fig3.suptitle('SKY130 LVT Varactor Characterization', fontsize=14, fontweight='bold')

ax3a.plot(vtune_vals, cap_vals * 1e15, 'b-o', linewidth=2, markersize=5)
ax3a.set_xlabel('Vtune (V)')
ax3a.set_ylabel('Capacitance (fF)')
ax3a.set_title('C(V) Curve — Unit Varactor (w=1, l=0.5)')
ax3a.grid(True, alpha=0.3)

# Frequency sweep at Vtune=0.9V
var_ac = np.loadtxt(os.path.join(OUTDIR, '03_var_ac.dat'), skiprows=1)
freq_var = var_ac[:, 0]
i_var_re = var_ac[:, 4]
i_var_im = var_ac[:, 5]
z_var = 1.0 / (i_var_re + 1j * i_var_im)
c_eff = -1.0 / (2 * np.pi * freq_var * np.imag(z_var))

ax3b.semilogx(freq_var / 1e9, c_eff * 1e15, 'r-', linewidth=2)
ax3b.axvline(x=6.835, color='orange', linestyle='--', alpha=0.7, label='6.835 GHz')
ax3b.set_xlabel('Frequency (GHz)')
ax3b.set_ylabel('C_eff (fF)')
ax3b.set_title('C(f) at Vtune = 0.9V')
ax3b.legend()
ax3b.grid(True, alpha=0.3)
ax3b.set_ylim([0, max(c_eff*1e15)*1.5])

plt.tight_layout()
plt.savefig(os.path.join(OUTDIR, 'varactor_characterization.png'), dpi=150, bbox_inches='tight')
print("Plot saved to vco_design/varactor_characterization.png")
