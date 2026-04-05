#!/usr/bin/env python3
"""Phase 4: VCO transient analysis — frequency, amplitude, startup, power."""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os

OUTDIR = os.path.dirname(os.path.abspath(__file__))

def parse_raw_file(filepath):
    """Parse ngspice ASCII raw file (real-valued transient)."""
    with open(filepath, 'r') as f:
        lines = f.readlines()

    n_vars = 0
    n_points = 0
    var_names = []
    data_start = 0

    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith('No. Variables:'):
            n_vars = int(stripped.split(':')[1].strip())
        elif stripped.startswith('No. Points:'):
            n_points = int(stripped.split(':')[1].strip())
        elif stripped.startswith('Variables:'):
            for j in range(n_vars):
                parts = lines[i + 1 + j].strip().split('\t')
                var_names.append(parts[1] if len(parts) > 1 else parts[0])
        elif stripped == 'Values:':
            data_start = i + 1
            break

    # Parse data: format is "idx  time_val\n\tval1\n\tval2\n..."
    data = np.zeros((n_points, n_vars))
    point = 0
    var = 0

    for i in range(data_start, len(lines)):
        line = lines[i].strip()
        if not line:
            continue
        parts = line.split()
        if len(parts) == 2 and var == 0:
            # "index  time_value"
            data[point, 0] = float(parts[1])
            var = 1
        elif len(parts) == 1:
            data[point, var] = float(parts[0])
            var += 1
            if var >= n_vars:
                var = 0
                point += 1
                if point >= n_points:
                    break

    return var_names, data[:point]

# ===================================================================
# Parse VCO transient data
# ===================================================================
print("Parsing VCO transient data...")
var_names, data = parse_raw_file(os.path.join(OUTDIR, '04_vco_tran.raw'))
print(f"  Variables ({len(var_names)}): {var_names[:5]}... ")
print(f"  Points: {data.shape[0]}")

time = data[:, 0]
outp = data[:, 13]  # v(outp)
outn = data[:, 12]  # v(outn)
vdiff = outp - outn
i_vdd = data[:, 18]  # i(vdd)

# ===================================================================
# Analysis
# ===================================================================
# Steady state: last 5 ns
t_start = 15e-9
mask = time > t_start
vdiff_ss = vdiff[mask]
time_ss = time[mask]
outp_ss = outp[mask]
outn_ss = outn[mask]

amplitude = (np.max(vdiff_ss) - np.min(vdiff_ss)) / 2
single_amp = (np.max(outp_ss) - np.min(outp_ss)) / 2

print(f"\n{'='*60}")
print(f"VCO TRANSIENT ANALYSIS RESULTS")
print(f"{'='*60}")
print(f"V(outp) range: {np.min(outp_ss):.3f} to {np.max(outp_ss):.3f} V")
print(f"V(outn) range: {np.min(outn_ss):.3f} to {np.max(outn_ss):.3f} V")
print(f"Single-ended amplitude: {single_amp*1e3:.1f} mV")
print(f"Differential amplitude: {amplitude*1e3:.1f} mV peak")

oscillating = amplitude > 0.010  # >10 mV

if oscillating:
    # Measure frequency from positive zero crossings of vdiff
    crossings = []
    for i in range(1, len(vdiff_ss)):
        if vdiff_ss[i-1] < 0 and vdiff_ss[i] >= 0:
            t_cross = time_ss[i-1] + (time_ss[i] - time_ss[i-1]) * (-vdiff_ss[i-1]) / (vdiff_ss[i] - vdiff_ss[i-1])
            crossings.append(t_cross)

    if len(crossings) >= 2:
        periods = np.diff(crossings)
        freq_avg = 1.0 / np.mean(periods)
        freq_std = np.std(1.0 / periods)
        print(f"Oscillation frequency: {freq_avg/1e9:.3f} GHz ± {freq_std/1e6:.1f} MHz")
        print(f"Periods measured: {len(periods)}")
    else:
        freq_avg = 0
        print("Not enough zero crossings")

    # Startup time
    # Find when envelope first reaches 50% of steady-state
    dt_avg = np.mean(np.diff(time[:1000]))
    window = max(10, int(0.3e-9 / dt_avg))
    env = np.zeros(len(vdiff))
    for i in range(window, len(vdiff)):
        env[i] = np.max(np.abs(vdiff[max(0,i-window):i+1]))
    startup_mask = env > 0.5 * amplitude
    if np.any(startup_mask):
        startup_time = time[np.argmax(startup_mask)]
    else:
        startup_time = 0
    print(f"Startup time (50% amplitude): {startup_time*1e9:.2f} ns")

    # FFT
    dt = np.mean(np.diff(time_ss))
    N = len(vdiff_ss)
    window_fn = np.hanning(N)
    fft_vals = np.fft.rfft(vdiff_ss * window_fn)
    fft_freq = np.fft.rfftfreq(N, dt)
    fft_mag_raw = np.abs(fft_vals)
    fft_mag = 20 * np.log10(fft_mag_raw / np.max(fft_mag_raw) + 1e-15)

    peak_idx = np.argmax(fft_mag_raw[1:]) + 1
    peak_freq = fft_freq[peak_idx]
    print(f"FFT peak frequency: {peak_freq/1e9:.3f} GHz")

    # Check harmonics
    for h in [2, 3]:
        h_idx = np.argmin(np.abs(fft_freq - h * peak_freq))
        h_level = fft_mag[h_idx]
        print(f"  {h}nd harmonic at {h*peak_freq/1e9:.3f} GHz: {h_level:.1f} dBc")
else:
    freq_avg = 0
    peak_freq = 0
    startup_time = 0
    print("VCO NOT oscillating!")

# Power
i_supply = -np.mean(i_vdd[mask])  # Current flows out of Vdd source (negative)
power = 1.8 * i_supply
print(f"\nSupply current (avg, last 5ns): {i_supply*1e3:.2f} mA")
print(f"Power consumption: {power*1e3:.2f} mW")

# ===================================================================
# Plots
# ===================================================================
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle('SKY130 VCO — Transient Simulation (BSIM4 Real Models)\n'
             f'Frequency: {freq_avg/1e9:.3f} GHz | Amplitude: {amplitude*1e3:.0f} mV | Power: {power*1e3:.1f} mW',
             fontsize=13, fontweight='bold')

# Full transient
ax1 = axes[0, 0]
ax1.plot(time * 1e9, outp, 'b-', linewidth=0.3, alpha=0.8, label='V(outp)')
ax1.plot(time * 1e9, outn, 'r-', linewidth=0.3, alpha=0.8, label='V(outn)')
ax1.set_xlabel('Time (ns)')
ax1.set_ylabel('Voltage (V)')
ax1.set_title('Output Waveforms')
ax1.legend(fontsize=8)
ax1.grid(True, alpha=0.3)

# Zoomed (last 1.5 ns)
ax2 = axes[0, 1]
mask_zoom = time > 18.5e-9
ax2.plot(time[mask_zoom] * 1e9, outp[mask_zoom], 'b-', linewidth=1.2, label='V(outp)')
ax2.plot(time[mask_zoom] * 1e9, outn[mask_zoom], 'r-', linewidth=1.2, label='V(outn)')
ax2.set_xlabel('Time (ns)')
ax2.set_ylabel('Voltage (V)')
ax2.set_title('Steady-State (zoomed)')
ax2.legend(fontsize=8)
ax2.grid(True, alpha=0.3)

# FFT
ax3 = axes[1, 0]
if oscillating:
    ax3.plot(fft_freq / 1e9, fft_mag, 'b-', linewidth=0.8)
    ax3.axvline(x=6.835, color='r', linestyle='--', alpha=0.7, label='6.835 GHz target')
    ax3.axvline(x=peak_freq/1e9, color='green', linestyle=':', linewidth=2,
                label=f'Peak: {peak_freq/1e9:.3f} GHz')
    ax3.set_xlim([0, 25])
    ax3.set_ylim([-80, 5])
    ax3.legend(fontsize=8)
ax3.set_xlabel('Frequency (GHz)')
ax3.set_ylabel('Magnitude (dB)')
ax3.set_title('FFT Spectrum')
ax3.grid(True, alpha=0.3)

# Differential
ax4 = axes[1, 1]
ax4.plot(time * 1e9, vdiff * 1e3, 'purple', linewidth=0.3)
ax4.set_xlabel('Time (ns)')
ax4.set_ylabel('Vdiff (mV)')
ax4.set_title(f'Differential Output')
ax4.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(os.path.join(OUTDIR, 'vco_transient_results.png'), dpi=150, bbox_inches='tight')
print(f"\nPlot saved to vco_design/vco_transient_results.png")

# Save key results for later phases
with open(os.path.join(OUTDIR, '04_results.txt'), 'w') as f:
    f.write(f"oscillating={1 if oscillating else 0}\n")
    f.write(f"freq_hz={freq_avg}\n")
    f.write(f"freq_fft_hz={peak_freq}\n")
    f.write(f"amplitude_v={amplitude}\n")
    f.write(f"power_w={power}\n")
    f.write(f"startup_s={startup_time}\n")
    f.write(f"i_supply_a={i_supply}\n")
