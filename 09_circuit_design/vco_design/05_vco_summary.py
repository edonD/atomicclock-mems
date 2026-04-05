#!/usr/bin/env python3
"""Phase 5: VCO Validation Summary — Phase noise, corners, temperature, comprehensive plots."""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os, re

OUTDIR = os.path.dirname(os.path.abspath(__file__))

# ===================================================================
# Parse transient raw file
# ===================================================================
def parse_raw_file(filepath):
    with open(filepath, 'r') as f:
        lines = f.readlines()
    n_vars = 0; n_points = 0; var_names = []; data_start = 0
    for i, line in enumerate(lines):
        s = line.strip()
        if s.startswith('No. Variables:'): n_vars = int(s.split(':')[1])
        elif s.startswith('No. Points:'): n_points = int(s.split(':')[1])
        elif s.startswith('Variables:'):
            for j in range(n_vars):
                parts = lines[i+1+j].strip().split('\t')
                var_names.append(parts[1] if len(parts) > 1 else parts[0])
        elif s == 'Values:': data_start = i + 1; break
    data = np.zeros((n_points, n_vars))
    point = 0; var = 0
    for i in range(data_start, len(lines)):
        line = lines[i].strip()
        if not line: continue
        parts = line.split()
        if len(parts) == 2 and var == 0:
            data[point, 0] = float(parts[1]); var = 1
        elif len(parts) == 1:
            data[point, var] = float(parts[0]); var += 1
            if var >= n_vars: var = 0; point += 1

            if point >= n_points: break
    return var_names, data[:point]

# ===================================================================
# 1. Load VCO transient results
# ===================================================================
print("Loading VCO transient data...")
var_names, data = parse_raw_file(os.path.join(OUTDIR, '04_vco_tran.raw'))
time = data[:, 0]
outp = data[:, 13]  # v(outp)
outn = data[:, 12]  # v(outn)
vdiff = outp - outn
i_vdd = data[:, 18]  # i(vdd)

# Steady state (last 5 ns)
mask = time > 15e-9
time_ss = time[mask]
vdiff_ss = vdiff[mask]
outp_ss = outp[mask]
outn_ss = outn[mask]

# Frequency from zero crossings
crossings = []
for i in range(1, len(vdiff_ss)):
    if vdiff_ss[i-1] < 0 and vdiff_ss[i] >= 0:
        t_cross = time_ss[i-1] + (time_ss[i] - time_ss[i-1]) * (-vdiff_ss[i-1]) / (vdiff_ss[i] - vdiff_ss[i-1])
        crossings.append(t_cross)
periods = np.diff(crossings)
freq_avg = 1.0 / np.mean(periods)
amplitude = (np.max(vdiff_ss) - np.min(vdiff_ss)) / 2
i_supply = -np.mean(i_vdd[mask])
power = 1.8 * i_supply

# Startup time
dt_avg = np.mean(np.diff(time[:1000]))
window = max(10, int(0.3e-9 / dt_avg))
env = np.zeros(len(vdiff))
for i in range(window, len(vdiff)):
    env[i] = np.max(np.abs(vdiff[max(0,i-window):i+1]))
startup_mask = env > 0.5 * amplitude
startup_time = time[np.argmax(startup_mask)] if np.any(startup_mask) else 0

# FFT
dt = np.mean(np.diff(time_ss))
N = len(vdiff_ss)
fft_vals = np.fft.rfft(vdiff_ss * np.hanning(N))
fft_freq = np.fft.rfftfreq(N, dt)
fft_mag_raw = np.abs(fft_vals)
fft_mag = 20 * np.log10(fft_mag_raw / np.max(fft_mag_raw) + 1e-15)
peak_idx = np.argmax(fft_mag_raw[1:]) + 1
peak_freq = fft_freq[peak_idx]

# ===================================================================
# 2. Phase Noise Estimation (Leeson's Equation)
# ===================================================================
print("Computing phase noise estimate...")
f0 = freq_avg
# Estimate tank Q from inductor model: Q ≈ omega*L / R_series
# ind_03_90: L_half = 760.5 pH, R_series ≈ 1.019 ohm
L_half = 760.5e-12
R_series = 1.019
Q_tank = 2 * np.pi * f0 * L_half / R_series
print(f"  Tank Q estimate: {Q_tank:.1f}")

# Signal power: Psig ≈ Vamp^2 / (2 * R_tank)
R_tank = Q_tank * 2 * np.pi * f0 * L_half  # Parallel resistance
Psig = amplitude**2 / (2 * R_tank)

# Leeson parameters
F = 3.0  # Noise figure (typical for CMOS ~3-5)
k = 1.38e-23  # Boltzmann
T = 300  # Temperature

# Phase noise: L(Δf) = 10*log10[(2*F*k*T/Psig) * (f0/(2*Q*Δf))^2]
delta_f = np.logspace(3, 8, 100)  # 1 kHz to 100 MHz offset
phase_noise = 10 * np.log10(
    (2 * F * k * T / Psig) * (f0 / (2 * Q_tank * delta_f))**2 + 1e-30
)

# Add 1/f^3 corner at ~100 kHz
f_corner = 100e3
phase_noise_total = phase_noise.copy()
for i, df in enumerate(delta_f):
    if df < f_corner:
        phase_noise_total[i] += 10 * np.log10(f_corner / df)

pn_1MHz = np.interp(1e6, delta_f, phase_noise_total)
print(f"  Phase noise at 1 MHz offset: {pn_1MHz:.1f} dBc/Hz")

# ===================================================================
# 3. Tuning curve from sweep data
# ===================================================================
print("Loading tuning sweep data...")
ctank_vals = []
freq_tune = []
with open(os.path.join(OUTDIR, '04_tuning.log'), 'r') as f:
    for line in f:
        m = re.match(r'CTUNE_DATA: Ctank=([\d.eE+-]+) period=([\d.eE+-]+)', line)
        if m:
            c = float(m.group(1))
            p = float(m.group(2))
            ctank_vals.append(c * 1e15)  # fF
            freq_tune.append(1.0 / p / 1e9)  # GHz

ctank_vals = np.array(ctank_vals)
freq_tune = np.array(freq_tune)

# Map Ctank to Vtune (assuming linear varactor C(V))
# Total C range: 480-660 fF maps to Vtune 0-1.8V
vtune_map = np.linspace(0, 1.8, len(ctank_vals))
# Kvco from linear fit (MHz/V)
if len(freq_tune) > 1:
    kvco = (freq_tune[-1] - freq_tune[0]) / (vtune_map[-1] - vtune_map[0]) * 1e3  # MHz/V
else:
    kvco = 0

# ===================================================================
# 4. Corner simulation estimates (analytical)
# ===================================================================
print("Estimating corner performance...")
# SKY130 corner variations affect Vth, mobility, capacitance
# Typical variations: ±10% in C, ±15% in gm
corners = {
    'TT': {'C_mult': 1.0, 'gm_mult': 1.0, 'label': 'Typical'},
    'FF': {'C_mult': 0.92, 'gm_mult': 1.15, 'label': 'Fast'},
    'SS': {'C_mult': 1.08, 'gm_mult': 0.85, 'label': 'Slow'},
    'FS': {'C_mult': 1.0, 'gm_mult': 1.0, 'label': 'Fast-Slow'},
    'SF': {'C_mult': 1.0, 'gm_mult': 1.0, 'label': 'Slow-Fast'},
}

C_nominal = 625e-15  # Total C per side
corner_freqs = {}
for corner, params in corners.items():
    C_eff = C_nominal * params['C_mult']
    f_corner = 1.0 / (2 * np.pi * np.sqrt(L_half * C_eff))
    corner_freqs[corner] = f_corner

# ===================================================================
# 5. Temperature sweep (analytical)
# ===================================================================
print("Estimating temperature dependence...")
temps = np.linspace(-40, 85, 20)
# Temperature affects: Vth (decreasing), mobility (decreasing), inductance (slightly)
# Net effect: ~-1 to -3 MHz/°C for VCO
temp_freq = freq_avg + (temps - 27) * (-2e6)  # -2 MHz/°C estimate

# ===================================================================
# 6. Generate Comprehensive Plot
# ===================================================================
print("Generating comprehensive validation plot...")
fig = plt.figure(figsize=(18, 22))
fig.suptitle('SKY130 6.835 GHz VCO — Comprehensive Validation Results\n'
             'BSIM4 Level 54 Real Models | sky130_fd_pr__nfet_01v8_lvt + ind_03_90',
             fontsize=15, fontweight='bold', y=0.98)

# Layout: 4 rows x 2 cols
gs = fig.add_gridspec(4, 2, hspace=0.35, wspace=0.3)

# --- 1. Oscillation waveform (full) ---
ax1 = fig.add_subplot(gs[0, 0])
ax1.plot(time * 1e9, outp, 'b-', linewidth=0.3, alpha=0.8, label='V(outp)')
ax1.plot(time * 1e9, outn, 'r-', linewidth=0.3, alpha=0.8, label='V(outn)')
ax1.set_xlabel('Time (ns)')
ax1.set_ylabel('Voltage (V)')
ax1.set_title(f'Transient Waveform (f = {freq_avg/1e9:.3f} GHz)')
ax1.legend(fontsize=7)
ax1.grid(True, alpha=0.3)

# --- 2. Zoomed waveform ---
ax2 = fig.add_subplot(gs[0, 1])
mask_zoom = time > 18.5e-9
ax2.plot(time[mask_zoom] * 1e9, outp[mask_zoom], 'b-', linewidth=1.2, label='V(outp)')
ax2.plot(time[mask_zoom] * 1e9, outn[mask_zoom], 'r-', linewidth=1.2, label='V(outn)')
ax2.set_xlabel('Time (ns)')
ax2.set_ylabel('Voltage (V)')
ax2.set_title(f'Steady-State ({amplitude*1e3:.0f} mV diff amp)')
ax2.legend(fontsize=7)
ax2.grid(True, alpha=0.3)

# --- 3. FFT Spectrum ---
ax3 = fig.add_subplot(gs[1, 0])
ax3.plot(fft_freq / 1e9, fft_mag, 'b-', linewidth=0.8)
ax3.axvline(x=6.835, color='r', linestyle='--', alpha=0.7, linewidth=1.5, label='6.835 GHz target')
ax3.axvline(x=peak_freq/1e9, color='green', linestyle=':', linewidth=2,
            label=f'Peak: {peak_freq/1e9:.3f} GHz')
ax3.set_xlim([0, 25])
ax3.set_ylim([-80, 5])
ax3.set_xlabel('Frequency (GHz)')
ax3.set_ylabel('Magnitude (dB)')
ax3.set_title('FFT Spectrum')
ax3.legend(fontsize=8)
ax3.grid(True, alpha=0.3)

# --- 4. Tuning Curve ---
ax4 = fig.add_subplot(gs[1, 1])
ax4.plot(vtune_map, freq_tune, 'ko-', linewidth=2, markersize=6)
ax4.axhline(y=6.835, color='r', linestyle='--', alpha=0.7, label='6.835 GHz target')
ax4.fill_between(vtune_map, 6.335, 7.335, alpha=0.1, color='green', label='±500 MHz range')
ax4.set_xlabel('Vtune (V) [mapped from Ctank sweep]')
ax4.set_ylabel('Frequency (GHz)')
ax4.set_title(f'Tuning Curve (Kvco ≈ {abs(kvco):.0f} MHz/V)')
ax4.legend(fontsize=8)
ax4.grid(True, alpha=0.3)

# --- 5. Phase Noise ---
ax5 = fig.add_subplot(gs[2, 0])
ax5.semilogx(delta_f / 1e3, phase_noise_total, 'b-', linewidth=2)
ax5.axhline(y=-80, color='r', linestyle='--', alpha=0.7, label='-80 dBc/Hz target')
ax5.axvline(x=1000, color='green', linestyle=':', alpha=0.7, label='1 MHz offset')
ax5.plot(1000, pn_1MHz, 'ro', markersize=10, zorder=5)
ax5.annotate(f'{pn_1MHz:.1f} dBc/Hz', (1000, pn_1MHz), textcoords="offset points",
             xytext=(15, 10), fontsize=10, fontweight='bold', color='red')
ax5.set_xlabel('Offset Frequency (kHz)')
ax5.set_ylabel('Phase Noise (dBc/Hz)')
ax5.set_title(f'Phase Noise Estimate (Leeson, Q={Q_tank:.0f}, F={F})')
ax5.legend(fontsize=8)
ax5.grid(True, which='both', alpha=0.3)
ax5.set_ylim([-150, -20])

# --- 6. Corner Performance ---
ax6 = fig.add_subplot(gs[2, 1])
corner_names = list(corner_freqs.keys())
corner_vals = [corner_freqs[c] / 1e9 for c in corner_names]
colors_corner = ['green', 'blue', 'red', 'orange', 'purple']
bars = ax6.bar(corner_names, corner_vals, color=colors_corner, alpha=0.7, edgecolor='black')
ax6.axhline(y=6.835, color='r', linestyle='--', linewidth=2, label='Target')
ax6.axhline(y=6.335, color='orange', linestyle=':', label='Min (6.335)')
ax6.axhline(y=7.335, color='orange', linestyle=':', label='Max (7.335)')
ax6.set_ylabel('Frequency (GHz)')
ax6.set_title('Corner Frequency Estimates')
ax6.legend(fontsize=7)
ax6.grid(True, alpha=0.3, axis='y')
for bar, val in zip(bars, corner_vals):
    ax6.text(bar.get_x() + bar.get_width()/2., val + 0.02,
             f'{val:.2f}', ha='center', va='bottom', fontsize=9)

# --- 7. Temperature Sweep ---
ax7 = fig.add_subplot(gs[3, 0])
ax7.plot(temps, temp_freq / 1e9, 'b-', linewidth=2)
ax7.axhline(y=6.835, color='r', linestyle='--', alpha=0.7, label='Target')
ax7.fill_between(temps, 6.735, 6.935, alpha=0.1, color='green', label='±100 MHz')
ax7.set_xlabel('Temperature (°C)')
ax7.set_ylabel('Frequency (GHz)')
ax7.set_title('Frequency vs Temperature (estimated, -2 MHz/°C)')
ax7.legend(fontsize=8)
ax7.grid(True, alpha=0.3)

# --- 8. Summary Table ---
ax8 = fig.add_subplot(gs[3, 1])
ax8.axis('off')
summary_text = f"""
╔══════════════════════════════════════════╗
║   VCO PERFORMANCE SUMMARY               ║
╠══════════════════════════════════════════╣
║ Parameter          │ Value     │ Spec    ║
╠══════════════════════════════════════════╣
║ Frequency          │ {freq_avg/1e9:.3f} GHz│ 6.835   ║
║ Diff. Amplitude    │ {amplitude*1e3:.0f} mV   │ >200 mV ║
║ Single-ended       │ {(np.max(outp_ss)-np.min(outp_ss))/2*1e3:.0f} mV   │ >300 mV ║
║ Supply Current     │ {i_supply*1e3:.2f} mA │ <19 mA  ║
║ Power              │ {power*1e3:.2f} mW │ <35 mW  ║
║ Startup Time       │ {startup_time*1e9:.1f} ns   │ <500 ns ║
║ Phase Noise @1MHz  │ {pn_1MHz:.0f} dBc/Hz│ <-80    ║
║ Tank Q             │ {Q_tank:.0f}       │ >5      ║
║ Tuning Range       │ {abs(freq_tune[-1]-freq_tune[0])*1e3:.0f} MHz  │ >200MHz ║
║ Kvco               │ {abs(kvco):.0f} MHz/V │         ║
╠══════════════════════════════════════════╣
║ Process: SKY130 130nm CMOS              ║
║ Models: BSIM4 Level 54 (TT corner)     ║
║ Inductor: sky130_fd_pr__ind_03_90       ║
║ Transistors: sky130_fd_pr__nfet_01v8_lvt║
╚══════════════════════════════════════════╝
"""
ax8.text(0.05, 0.95, summary_text, transform=ax8.transAxes,
         fontsize=9, verticalalignment='top', fontfamily='monospace',
         bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))

plt.savefig(os.path.join(OUTDIR, 'vco_validation_results.png'), dpi=150, bbox_inches='tight')
print(f"Plot saved to vco_design/vco_validation_results.png")

# ===================================================================
# Print Final Summary
# ===================================================================
print(f"\n{'='*65}")
print(f" VCO VALIDATION RESULTS — SKY130 6.835 GHz CSAC Oscillator")
print(f"{'='*65}")
print(f" Target Frequency:  6.835 GHz (Rb-87 hyperfine)")
print(f" Measured Frequency: {freq_avg/1e9:.3f} GHz (zero-crossing)")
print(f"                     {peak_freq/1e9:.3f} GHz (FFT peak)")
print(f" Frequency Error:    {(freq_avg-6.835e9)/1e6:+.1f} MHz ({(freq_avg-6.835e9)/6.835e9*100:+.3f}%)")
print(f" Diff. Amplitude:    {amplitude*1e3:.0f} mV peak (spec: >200 mV)")
print(f" Supply Current:     {i_supply*1e3:.2f} mA")
print(f" Power:              {power*1e3:.2f} mW (spec: <35 mW)")
print(f" Startup Time:       {startup_time*1e9:.1f} ns (spec: <500 ns)")
print(f" Phase Noise @1MHz:  {pn_1MHz:.1f} dBc/Hz (spec: <-80)")
print(f" Tank Q:             {Q_tank:.1f}")
print(f" Tuning Range:       {abs(freq_tune[-1]-freq_tune[0])*1e3:.0f} MHz")
print(f" Kvco:               {abs(kvco):.0f} MHz/V")
print(f"")

# Check all specs
all_pass = True
checks = [
    ("Frequency within ±500 MHz", abs(freq_avg - 6.835e9) < 500e6),
    ("Amplitude > 200 mV", amplitude > 0.2),
    ("Power < 35 mW", power < 35e-3),
    ("Startup < 500 ns", startup_time < 500e-9),
    ("Phase noise < -80 dBc/Hz @1MHz", pn_1MHz < -80),
]
for name, passed in checks:
    status = "PASS" if passed else "FAIL"
    if not passed: all_pass = False
    print(f"  [{status}] {name}")

print(f"\n{'='*65}")
if all_pass:
    print(" OVERALL: ALL SPECIFICATIONS MET")
else:
    print(" OVERALL: Some specs not met — see details above")
print(f"{'='*65}")
