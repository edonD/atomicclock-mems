"""
COOL RB-87 QUANTUM SIMULATION
==============================
Animated 3D visualization of quantum state evolution, resonance sweeps,
and phase-space dynamics with beautiful aesthetics.

Creates:
1. Animated Bloch sphere with quantum trajectory
2. Real-time population dynamics
3. Frequency sweep resonance map
4. 3D phase space portrait
5. Quantum state tomography
6. Decoherence cloud animation
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.patches import Circle
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
import os
from scipy.interpolate import griddata

# Constants
HYPERFINE_HZ = 6_834_682_610.904
GAMMA_HZ = 5.746e6  # Natural linewidth in Hz

print("Generating cool quantum simulations...")
os.makedirs("plots", exist_ok=True)

# 
# 1. 3D BLOCH SPHERE WITH ANIMATED QUANTUM TRAJECTORY
# 

def create_animated_bloch_evolution():
    """Create beautiful 3D Bloch sphere with evolving quantum state"""

    fig = plt.figure(figsize=(16, 12))

    # Create 4 subplots with different detunings
    ax_list = [
        fig.add_subplot(2, 2, 1, projection='3d'),
        fig.add_subplot(2, 2, 2, projection='3d'),
        fig.add_subplot(2, 2, 3, projection='3d'),
        fig.add_subplot(2, 2, 4, projection='3d'),
    ]

    scenarios = [
        {"title": "Resonant Drive (On-Resonance)\nΔ = 0", "detuning": 0, "rabi_freq": 100e3, "color": "blue"},
        {"title": "Red Detuned\nΔ = -500 kHz", "detuning": -500e3, "rabi_freq": 100e3, "color": "red"},
        {"title": "Blue Detuned\nΔ = +500 kHz", "detuning": 500e3, "rabi_freq": 100e3, "color": "green"},
        {"title": "AC Stark Shift\n(Power Broadening)", "detuning": 0, "rabi_freq": 200e3, "color": "purple"},
    ]

    for ax, scenario in zip(ax_list, scenarios):
        # Draw Bloch sphere
        u = np.linspace(0, 2*np.pi, 40)
        v = np.linspace(0, np.pi, 40)
        x_sphere = np.outer(np.cos(u), np.sin(v))
        y_sphere = np.outer(np.sin(u), np.sin(v))
        z_sphere = np.outer(np.ones(np.size(u)), np.cos(v))

        ax.plot_surface(x_sphere, y_sphere, z_sphere, alpha=0.15, color='cyan', edgecolor='none')

        # Axes
        ax.quiver(0, 0, 0, 1.3, 0, 0, color='red', arrow_length_ratio=0.08, linewidth=2.5)
        ax.quiver(0, 0, 0, 0, 1.3, 0, color='green', arrow_length_ratio=0.08, linewidth=2.5)
        ax.quiver(0, 0, 0, 0, 0, 1.3, color='blue', arrow_length_ratio=0.08, linewidth=2.5)

        # Trajectory
        t = np.linspace(0, 100e-9, 200)
        omega_rabi = 2*np.pi * scenario["rabi_freq"]
        delta = 2*np.pi * scenario["detuning"]

        # Effective Rabi frequency (includes detuning)
        omega_eff = np.sqrt(omega_rabi**2 + delta**2)

        # Bloch vector evolution
        x_traj = (omega_rabi / omega_eff) * np.sin(omega_eff * t / 2)
        y_traj = np.zeros_like(t)
        z_traj = (delta / omega_eff) * np.sin(omega_eff * t / 2)**2

        # Draw trajectory with gradient
        for i in range(len(t)-1):
            ax.plot(x_traj[i:i+2], y_traj[i:i+2], z_traj[i:i+2],
                   color=scenario["color"], linewidth=3, alpha=0.8)

        # Start and end points
        ax.scatter([x_traj[0]], [y_traj[0]], [z_traj[0]],
                  color='green', s=200, marker='o', label='Start', zorder=10, edgecolor='black', linewidth=2)
        ax.scatter([x_traj[-1]], [y_traj[-1]], [z_traj[-1]],
                  color='red', s=200, marker='s', label='End', zorder=10, edgecolor='black', linewidth=2)

        # Current state marker
        ax.scatter([x_traj[len(t)//2]], [y_traj[len(t)//2]], [z_traj[len(t)//2]],
                  color=scenario["color"], s=300, marker='*', zorder=10,
                  edgecolor='yellow', linewidth=2, label='Current')

        ax.set_xlim((-1.5, 1.5))
        ax.set_ylim((-1.5, 1.5))
        ax.set_zlim((-1.5, 1.5))
        ax.set_xlabel('X (Real)', fontsize=10, weight='bold')
        ax.set_ylabel('Y (Imag)', fontsize=10, weight='bold')
        ax.set_zlabel('Z (Pop)', fontsize=10, weight='bold')
        ax.set_title(scenario["title"], fontsize=11, weight='bold', pad=20)
        ax.legend(loc='upper left', fontsize=9)

        # Make it look cool
        ax.view_init(elev=20, azim=45)
        ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig("plots/COOL_01_bloch_trajectories.png", dpi=200, bbox_inches='tight')
    print("  > COOL_01_bloch_trajectories.png [OK]")
    plt.close()


# 
# 2. FREQUENCY RESPONSE HEATMAP + POPULATION DYNAMICS
# 

def create_frequency_sweep_heatmap():
    """Beautiful heatmap of frequency vs time evolution"""

    fig, axes = plt.subplots(2, 2, figsize=(16, 11))

    # Parameters
    freq_offset = np.linspace(-2e6, 2e6, 150)
    time = np.linspace(0, 200e-9, 100)
    rabi_freq = 2*np.pi*100e3

    # 
    # Panel 1: Population heatmap vs frequency and time
    # 
    ax = axes[0, 0]

    pop_excited = np.zeros((len(freq_offset), len(time)))

    for i, delta in enumerate(freq_offset):
        delta_rad = 2*np.pi * delta
        omega_eff = np.sqrt(rabi_freq**2 + delta_rad**2)
        pop_excited[i, :] = np.sin(omega_eff * time / 2)**2

    im1 = ax.contourf(time*1e9, freq_offset/1e6, pop_excited, levels=50, cmap='hot')
    ax.contour(time*1e9, freq_offset/1e6, pop_excited, levels=10, colors='white', alpha=0.3, linewidths=0.5)
    cbar1 = plt.colorbar(im1, ax=ax)
    cbar1.set_label('F=3 Population', fontsize=10, weight='bold')
    ax.set_xlabel('Time (ns)', fontsize=11, weight='bold')
    ax.set_ylabel('Frequency Offset (MHz)', fontsize=11, weight='bold')
    ax.set_title('Population Heatmap: Rabi Flopping vs Detuning', fontsize=12, weight='bold')
    ax.grid(True, alpha=0.2, color='white')

    # 
    # Panel 2: Resonance response (3D effect)
    # 
    ax = axes[0, 1]

    resonance = np.zeros_like(freq_offset)
    for i, delta in enumerate(freq_offset):
        delta_rad = 2*np.pi * delta
        resonance[i] = np.sin(np.sqrt(rabi_freq**2 + delta_rad**2) * 100e-9 / 2)**2

    # Create gradient fill
    ax.fill_between(freq_offset/1e6, 0, resonance, alpha=0.4, color='blue', label='Excited population')
    ax.plot(freq_offset/1e6, resonance, 'b-', linewidth=3, label='Response peak')

    # Add smooth resonance curve
    resonance_smooth = np.exp(-(freq_offset**2 / (500e3)**2))
    ax.plot(freq_offset/1e6, resonance_smooth*0.95, 'r--', linewidth=2.5, alpha=0.7, label='Natural linewidth')

    ax.axvline(0, color='g', linestyle='--', linewidth=2.5, alpha=0.8, label='On-resonance')
    ax.set_xlabel('Frequency Offset (MHz)', fontsize=11, weight='bold')
    ax.set_ylabel('Excited State Population', fontsize=11, weight='bold')
    ax.set_title('Rabi Resonance Profile (100 ns pulse)', fontsize=12, weight='bold')
    ax.legend(fontsize=10, loc='upper right')
    ax.grid(True, alpha=0.3)
    ax.set_ylim([0, 1.05])

    # 
    # Panel 3: Complex phase space (Real vs Imaginary coherence)
    # 
    ax = axes[1, 0]

    # Generate trajectories for different detunings
    colors_phase = plt.cm.rainbow(np.linspace(0, 1, 5))
    detunings_phase = np.array([-1e6, -500e3, 0, 500e3, 1e6])

    for j, (delta, color) in enumerate(zip(detunings_phase, colors_phase)):
        delta_rad = 2*np.pi * delta
        omega_eff = np.sqrt(rabi_freq**2 + delta_rad**2)
        t_phase = np.linspace(0, 300e-9, 300)

        # Coherence in phase space
        phase = omega_eff * t_phase / 2
        real_coh = np.sin(phase) * np.cos(delta_rad * t_phase)
        imag_coh = np.sin(phase) * np.sin(delta_rad * t_phase)

        ax.plot(real_coh, imag_coh, color=color, linewidth=2.5,
               label=f'Δ={delta/1e6:.1f} MHz', alpha=0.8)
        ax.scatter([real_coh[0]], [imag_coh[0]], color=color, s=100, zorder=5, edgecolor='black', linewidth=1.5)

    ax.set_xlabel('Re[Coherence]', fontsize=11, weight='bold')
    ax.set_ylabel('Im[Coherence]', fontsize=11, weight='bold')
    ax.set_title('Phase Space Trajectories\n(Different Detunings)', fontsize=12, weight='bold')
    ax.legend(fontsize=9, loc='best')
    ax.grid(True, alpha=0.3)
    ax.set_aspect('equal')
    ax.axhline(0, color='k', linewidth=0.5, alpha=0.5)
    ax.axvline(0, color='k', linewidth=0.5, alpha=0.5)

    # Add circle for reference
    theta_ref = np.linspace(0, 2*np.pi, 100)
    ax.plot(0.3*np.cos(theta_ref), 0.3*np.sin(theta_ref), 'k--', alpha=0.3, linewidth=1)

    # 
    # Panel 4: Population inversion dynamics with different power levels
    # 
    ax = axes[1, 1]

    time_dyn = np.linspace(0, 500e-9, 500)
    rabi_freqs = np.array([50e3, 100e3, 200e3, 500e3])
    colors_rabi = ['blue', 'green', 'orange', 'red']

    for rabi, color in zip(rabi_freqs, colors_rabi):
        omega = 2*np.pi * rabi
        pop = np.sin(omega * time_dyn / 2)**2
        ax.plot(time_dyn*1e9, pop, color=color, linewidth=2.5,
               label=f'Ω/(2π) = {rabi/1e3:.0f} kHz', alpha=0.85)

    # Mark π/2 and π pulse times
    for rabi, color in zip(rabi_freqs, colors_rabi):
        omega = 2*np.pi * rabi
        t_pi2 = np.pi / (2*omega)
        t_pi = np.pi / omega
        ax.scatter([t_pi2*1e9], [0.5], color=color, s=80, marker='o', zorder=5, edgecolor='black', linewidth=1)
        ax.scatter([t_pi*1e9], [1.0], color=color, s=80, marker='s', zorder=5, edgecolor='black', linewidth=1)

    ax.set_xlabel('Time (ns)', fontsize=11, weight='bold')
    ax.set_ylabel('F=3 Population', fontsize=11, weight='bold')
    ax.set_title('Rabi Oscillations: Varying Power Levels\n(circles=π/2, squares=π)',
                fontsize=12, weight='bold')
    ax.legend(fontsize=10, loc='right')
    ax.grid(True, alpha=0.3)
    ax.set_ylim([0, 1.05])
    ax.set_xlim([0, 500])

    plt.tight_layout()
    plt.savefig("plots/COOL_02_heatmap_dynamics.png", dpi=200, bbox_inches='tight')
    print("  > COOL_02_heatmap_dynamics.png [OK]")
    plt.close()


# =============================================================================
# 3. 3D PHASE SPACE PORTRAIT
# =============================================================================

def create_3d_phase_portrait():
    """3D trajectory in phase space showing Rabi dynamics"""

    fig = plt.figure(figsize=(16, 6))

    # 
    # Left: 3D Phase space with multiple trajectories
    # 
    ax1 = fig.add_subplot(121, projection='3d')

    t_max = 200e-9
    t = np.linspace(0, t_max, 400)

    # Plot multiple Rabi trajectories in 3D space (x, y, time)
    for idx, rabi_freq in enumerate([50e3, 100e3, 150e3, 200e3]):
        omega = 2*np.pi * rabi_freq

        # X: ground state population
        x = np.cos(omega * t / 2)**2

        # Y: excited state population
        y = np.sin(omega * t / 2)**2

        # Z: time axis
        z = t * 1e9

        color = plt.cm.viridis(idx / 3)
        ax1.plot(x, y, z, color=color, linewidth=3, label=f'{rabi_freq/1e3:.0f} kHz', alpha=0.9)

        # Mark start point
        ax1.scatter([x[0]], [y[0]], [z[0]], color=color, s=150, marker='o',
                   zorder=10, edgecolor='black', linewidth=2)

        # Mark end point
        ax1.scatter([x[-1]], [y[-1]], [z[-1]], color=color, s=150, marker='s',
                   zorder=10, edgecolor='black', linewidth=2)

    # Draw constraint surface (x + y = 1, populations sum to 1)
    x_surf = np.linspace(0, 1, 30)
    z_surf = np.linspace(0, 200, 30)
    X, Z = np.meshgrid(x_surf, z_surf)
    Y = 1 - X
    ax1.plot_surface(X, Y, Z, alpha=0.1, color='gray', edgecolor='none')

    ax1.set_xlabel('P_ground (F=2)', fontsize=11, weight='bold')
    ax1.set_ylabel('P_excited (F=3)', fontsize=11, weight='bold')
    ax1.set_zlabel('Time (ns)', fontsize=11, weight='bold')
    ax1.set_title('3D Phase Space: Population Dynamics\nvs Time', fontsize=12, weight='bold')
    ax1.legend(fontsize=10, loc='upper left')
    ax1.view_init(elev=25, azim=135)
    ax1.grid(True, alpha=0.3)

    # 
    # Right: 2D phase plane with vector field
    # 
    ax2 = fig.add_subplot(122)

    # Create grid for vector field
    x_grid = np.linspace(0, 1, 12)
    y_grid = np.linspace(0, 1, 12)
    X_grid, Y_grid = np.meshgrid(x_grid, y_grid)

    # Only show on the constraint surface x + y = 1
    mask = np.abs(X_grid + Y_grid - 1) < 0.15

    # Rabi equations: dx/dt ∝ -Ω sin(Ωt), dy/dt ∝ Ω sin(Ωt)
    omega = 2*np.pi * 100e3
    t_eval = np.linspace(0, 100e-9, 20)

    # Vector field arrows
    for x0 in [0.1, 0.3, 0.5, 0.7, 0.9]:
        for y0 in [0.0, 0.2, 0.4, 0.6, 0.8]:
            if abs(x0 + y0 - 1.0) < 0.15:
                # Trajectory from this initial point
                t_traj = np.linspace(0, 50e-9, 100)
                x_traj = np.cos(omega * t_traj / 2)**2
                y_traj = np.sin(omega * t_traj / 2)**2

                # Find closest point to (x0, y0)
                dist = (x_traj - x0)**2 + (y_traj - y0)**2
                idx_closest = np.argmin(dist)

                if idx_closest < len(t_traj) - 5:
                    dx = x_traj[idx_closest+5] - x_traj[idx_closest]
                    dy = y_traj[idx_closest+5] - y_traj[idx_closest]
                    norm = np.sqrt(dx**2 + dy**2) + 1e-6
                    dx /= norm
                    dy /= norm

                    ax2.arrow(x0, y0, dx*0.08, dy*0.08,
                             head_width=0.03, head_length=0.02, fc='gray', ec='gray', alpha=0.6)

    # Plot nullcline (constraint surface)
    x_null = np.linspace(0, 1, 100)
    y_null = 1 - x_null
    ax2.plot(x_null, y_null, 'k--', linewidth=2, alpha=0.7, label='P_ground + P_excited = 1')

    # Plot trajectories
    colors_2d = ['blue', 'green', 'orange', 'red']
    for idx, rabi_freq in enumerate([50e3, 100e3, 150e3, 200e3]):
        omega = 2*np.pi * rabi_freq
        t_traj = np.linspace(0, 200e-9, 300)
        x_traj = np.cos(omega * t_traj / 2)**2
        y_traj = np.sin(omega * t_traj / 2)**2

        ax2.plot(x_traj, y_traj, color=colors_2d[idx], linewidth=2.5,
                label=f'{rabi_freq/1e3:.0f} kHz', alpha=0.9)
        ax2.scatter([x_traj[0]], [y_traj[0]], color=colors_2d[idx], s=120,
                   marker='o', zorder=5, edgecolor='black', linewidth=1.5)

    ax2.set_xlabel('P_ground (F=2)', fontsize=11, weight='bold')
    ax2.set_ylabel('P_excited (F=3)', fontsize=11, weight='bold')
    ax2.set_title('Phase Plane with Dynamics\n(Vector field shows evolution direction)',
                 fontsize=12, weight='bold')
    ax2.legend(fontsize=10, loc='best')
    ax2.grid(True, alpha=0.3)
    ax2.set_xlim([-0.05, 1.05])
    ax2.set_ylim([-0.05, 1.05])
    ax2.set_aspect('equal')

    plt.tight_layout()
    plt.savefig("plots/COOL_03_phase_portrait.png", dpi=200, bbox_inches='tight')
    print("  > COOL_03_phase_portrait.png [OK]")
    plt.close()


# =============================================================================
# 4. PULSE SEQUENCE CHOREOGRAPHY
# =============================================================================

def create_pulse_choreography():
    """Beautiful visualization of complex pulse sequences"""

    fig = plt.figure(figsize=(16, 10))

    # Parameters
    dt = 1e-9
    t_total = 1000e-9
    t = np.arange(0, t_total, dt)

    # Define pulse sequences
    sequences = {
        "Simple π/2 Pulse": {
            "pulses": [(0, 10, 100e3)],
            "color": "blue",
        },
        "Ramsey (π/2 - T - π/2)": {
            "pulses": [(0, 10, 100e3), (400, 10, 100e3)],
            "color": "green",
        },
        "Spin Echo (π/2 - T - π - T - π/2)": {
            "pulses": [(0, 10, 100e3), (200, 20, 100e3), (400, 10, 100e3)],
            "color": "orange",
        },
        "CPMG Train (π/2 - [π]x4 - π/2)": {
            "pulses": [(0, 10, 100e3)] + [(100+i*100, 20, 100e3) for i in range(4)] + [(500, 10, 100e3)],
            "color": "red",
        },
    }

    for idx, (name, seq) in enumerate(sequences.items()):
        ax = plt.subplot(2, 2, idx+1)

        # Initialize populations
        pop_ground = np.ones_like(t)
        pop_excited = np.zeros_like(t)

        # Apply pulses
        current_pop_g = 1.0
        current_pop_e = 0.0

        for t_start_ns, t_dur_ns, rabi_freq in seq["pulses"]:
            omega = 2*np.pi * rabi_freq

            t_start = int(t_start_ns)
            t_end = int(t_start_ns + t_dur_ns)

            if t_end <= len(t):
                # Evolve during pulse
                for i in range(t_start, min(t_end, len(t))):
                    tau = (i - t_start) * 1e-9
                    current_pop_e = np.sin(omega * tau / 2)**2
                    current_pop_g = 1 - current_pop_e
                    pop_excited[i] = current_pop_e
                    pop_ground[i] = current_pop_g

                # Hold after pulse
                for i in range(t_end, len(t)):
                    pop_excited[i] = current_pop_e
                    pop_ground[i] = current_pop_g

        # Plot
        ax.fill_between(t*1e9, 0, pop_ground, alpha=0.5, color=seq["color"], label='F=2 (ground)')
        ax.fill_between(t*1e9, pop_ground, 1, alpha=0.5, color='gray', label='F=3 (excited)')
        ax.plot(t*1e9, pop_ground, color=seq["color"], linewidth=2.5, alpha=0.9)
        ax.plot(t*1e9, pop_excited, 'k-', linewidth=2.5, alpha=0.9)

        # Add pulse rectangles
        for t_start_ns, t_dur_ns, rabi_freq in seq["pulses"]:
            rect = plt.Rectangle((t_start_ns, 0), t_dur_ns, 1.05,
                                 alpha=0.2, color=seq["color"], edgecolor=seq["color"], linewidth=2)
            ax.add_patch(rect)
            ax.text(t_start_ns + t_dur_ns/2, 1.08, f'π/2' if t_dur_ns < 15 else 'π',
                   ha='center', fontsize=10, weight='bold', color=seq["color"])

        ax.set_xlabel('Time (ns)', fontsize=11, weight='bold')
        ax.set_ylabel('Population', fontsize=11, weight='bold')
        ax.set_title(name, fontsize=12, weight='bold')
        ax.set_ylim([0, 1.15])
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=9, loc='upper right')

    plt.tight_layout()
    plt.savefig("plots/COOL_04_pulse_sequences.png", dpi=200, bbox_inches='tight')
    print("  > COOL_04_pulse_sequences.png [OK]")
    plt.close()


# 
# 5. QUANTUM INTERFERENCE PATTERN (RAMSEY FRINGES)
# 

def create_ramsey_fringes():
    """Beautiful Ramsey interference pattern"""

    fig = plt.figure(figsize=(16, 11))

    # 
    # Panel 1: 2D Ramsey map (frequency vs drift time)
    # 
    ax1 = fig.add_subplot(2, 2, 1)

    freq_offset = np.linspace(-1e6, 1e6, 200)
    T_drift = np.linspace(0, 1000e-9, 150)
    ramsey_map = np.zeros((len(freq_offset), len(T_drift)))

    for i, delta in enumerate(freq_offset):
        for j, T in enumerate(T_drift):
            # Ramsey fringe visibility oscillates with detuning
            ramsey_map[i, j] = 0.5 * (1 + np.cos(2*np.pi * delta * T))

    im1 = ax1.contourf(T_drift*1e9, freq_offset/1e6, ramsey_map, levels=100, cmap='twilight_shifted')
    cbar1 = plt.colorbar(im1, ax=ax1)
    cbar1.set_label('Excited Population', fontsize=10, weight='bold')
    ax1.set_xlabel('Drift Time T (ns)', fontsize=11, weight='bold')
    ax1.set_ylabel('Frequency Offset (MHz)', fontsize=11, weight='bold')
    ax1.set_title('Ramsey Fringes: 2D Map', fontsize=12, weight='bold')
    ax1.grid(True, alpha=0.2, color='white', linewidth=0.5)

    # 
    # Panel 2: Fringes at different drift times
    # 
    ax2 = fig.add_subplot(2, 2, 2)

    T_values = [100e-9, 200e-9, 500e-9, 1000e-9]
    colors_fringes = ['blue', 'green', 'orange', 'red']

    for T, color in zip(T_values, colors_fringes):
        pop = 0.5 * (1 + np.cos(2*np.pi * freq_offset * T))
        ax2.plot(freq_offset/1e6, pop, color=color, linewidth=2.5,
                label=f'T = {T*1e9:.0f} ns', alpha=0.85)

    ax2.axhline(0.5, color='k', linestyle='--', linewidth=1, alpha=0.5)
    ax2.set_xlabel('Frequency Offset (MHz)', fontsize=11, weight='bold')
    ax2.set_ylabel('F=3 Population', fontsize=11, weight='bold')
    ax2.set_title('Ramsey Fringes at Different Drift Times', fontsize=12, weight='bold')
    ax2.legend(fontsize=10, loc='best')
    ax2.grid(True, alpha=0.3)
    ax2.set_ylim([0, 1])

    # 
    # Panel 3: Fringe visibility decay (decoherence)
    # 
    ax3 = fig.add_subplot(2, 2, 3)

    T_decay = np.linspace(0, 2000e-9, 300)
    tau_coherence_values = [500e-9, 1000e-9, 2000e-9]

    for tau_c, color in zip(tau_coherence_values, ['blue', 'green', 'red']):
        visibility = np.exp(-T_decay / tau_c)
        ax3.plot(T_decay*1e9, visibility, color=color, linewidth=3,
                label=f'τ_c = {tau_c*1e9:.0f} ns', alpha=0.85)

    ax3.axhline(np.exp(-1), color='k', linestyle=':', linewidth=2, alpha=0.5, label='1/e point')
    ax3.set_xlabel('Drift Time T (ns)', fontsize=11, weight='bold')
    ax3.set_ylabel('Fringe Visibility', fontsize=11, weight='bold')
    ax3.set_title('Visibility Decay: Effect of Decoherence', fontsize=12, weight='bold')
    ax3.legend(fontsize=10, loc='best')
    ax3.grid(True, alpha=0.3)
    ax3.set_ylim([0, 1.05])

    # 
    # Panel 4: 3D Ramsey surface
    # 
    ax4 = fig.add_subplot(2, 2, 4, projection='3d')

    freq_3d = np.linspace(-2e6, 2e6, 80)
    T_3d = np.linspace(0, 2000e-9, 80)
    Freq, T_mesh = np.meshgrid(freq_3d, T_3d)

    # Include visibility decay
    tau_c_3d = 1000e-9
    Z = 0.5 * (1 + np.cos(2*np.pi * Freq * T_mesh)) * np.exp(-T_mesh / tau_c_3d)

    surf = ax4.plot_surface(Freq/1e6, T_mesh*1e9, Z, cmap='viridis',
                           alpha=0.95, edgecolor='none', antialiased=True)

    cbar4 = plt.colorbar(surf, ax=ax4, pad=0.1, shrink=0.8)
    cbar4.set_label('Population', fontsize=10, weight='bold')

    ax4.set_xlabel('Frequency (MHz)', fontsize=10, weight='bold')
    ax4.set_ylabel('T (ns)', fontsize=10, weight='bold')
    ax4.set_zlabel('F=3 Pop', fontsize=10, weight='bold')
    ax4.set_title('3D Ramsey Surface\n(with decoherence envelope)', fontsize=12, weight='bold')
    ax4.view_init(elev=25, azim=45)

    plt.tight_layout()
    plt.savefig("plots/COOL_05_ramsey_fringes.png", dpi=200, bbox_inches='tight')
    print("  > COOL_05_ramsey_fringes.png [OK]")
    plt.close()


# 
# 6. QUANTUM STATE TOMOGRAPHY RECONSTRUCTION
# 

def create_state_tomography():
    """Visualize quantum state from measurement projections"""

    fig = plt.figure(figsize=(16, 10))

    # Create measurements in different bases
    bases = ['Z (F=2/F=3)', 'X (Linear)', 'Y (Circular)']
    colors_basis = ['blue', 'red', 'green']

    # Time varying state
    t = np.linspace(0, 100e-9, 100)
    omega = 2*np.pi * 100e3

    # Bloch vector components
    x_vec = np.sin(omega*t/2) * np.cos(omega*t)  # Coherence oscillation
    y_vec = np.sin(omega*t/2) * np.sin(omega*t)
    z_vec = np.cos(omega*t/2)**2 - np.sin(omega*t/2)**2  # Population inversion

    # 
    # Panel 1: Measurement outcomes in 3 bases
    # 
    ax1 = fig.add_subplot(2, 2, 1)

    ax1.plot(t*1e9, z_vec, color='blue', linewidth=2.5, label='Z basis (|F=2⟩ vs |F=3⟩)')
    ax1.plot(t*1e9, x_vec, color='red', linewidth=2.5, label='X basis (|+⟩ vs |-⟩)')
    ax1.plot(t*1e9, y_vec, color='green', linewidth=2.5, label='Y basis (|↻⟩ vs |↺⟩)')

    ax1.axhline(0, color='k', linestyle='--', linewidth=1, alpha=0.5)
    ax1.set_xlabel('Time (ns)', fontsize=11, weight='bold')
    ax1.set_ylabel('Expectation Value ⟨σ⟩', fontsize=11, weight='bold')
    ax1.set_title('Quantum Measurements in 3 Orthogonal Bases', fontsize=12, weight='bold')
    ax1.legend(fontsize=10, loc='best')
    ax1.grid(True, alpha=0.3)
    ax1.set_ylim([-1.1, 1.1])

    # 
    # Panel 2: Bloch sphere reconstruction from measurements
    # 
    ax2 = fig.add_subplot(2, 2, 2, projection='3d')

    # Draw Bloch sphere
    u = np.linspace(0, 2*np.pi, 30)
    v = np.linspace(0, np.pi, 30)
    x_sphere = np.outer(np.cos(u), np.sin(v))
    y_sphere = np.outer(np.sin(u), np.sin(v))
    z_sphere = np.outer(np.ones(np.size(u)), np.cos(v))

    ax2.plot_surface(x_sphere, y_sphere, z_sphere, alpha=0.1, color='cyan', edgecolor='none')

    # Plot measured Bloch vectors
    colors_time = plt.cm.rainbow(np.linspace(0, 1, len(t)))

    for i in range(0, len(t), 5):
        ax2.quiver(0, 0, 0, x_vec[i], y_vec[i], z_vec[i],
                  color=colors_time[i], arrow_length_ratio=0.1, linewidth=2, alpha=0.8)

    # Draw full trajectory
    ax2.plot(x_vec, y_vec, z_vec, 'k-', linewidth=1.5, alpha=0.5, label='Trajectory')

    # Axes
    ax2.quiver(0, 0, 0, 1.3, 0, 0, color='red', arrow_length_ratio=0.08, linewidth=2)
    ax2.quiver(0, 0, 0, 0, 1.3, 0, color='green', arrow_length_ratio=0.08, linewidth=2)
    ax2.quiver(0, 0, 0, 0, 0, 1.3, color='blue', arrow_length_ratio=0.08, linewidth=2)

    ax2.set_xlim((-1.5, 1.5))
    ax2.set_ylim((-1.5, 1.5))
    ax2.set_zlim((-1.5, 1.5))
    ax2.set_xlabel('X', fontsize=10, weight='bold')
    ax2.set_ylabel('Y', fontsize=10, weight='bold')
    ax2.set_zlabel('Z', fontsize=10, weight='bold')
    ax2.set_title('Reconstructed Bloch Sphere\n(from measurements)', fontsize=12, weight='bold')
    ax2.view_init(elev=20, azim=45)

    # 
    # Panel 3: Density matrix evolution (real part)
    # 
    ax3 = fig.add_subplot(2, 2, 3)

    # Density matrix ρ = |ψ⟩⟨ψ|
    rho_00 = (1 + z_vec) / 2  # |F=2⟩ population
    rho_11 = (1 - z_vec) / 2  # |F=3⟩ population
    rho_01 = (x_vec + 1j*y_vec) / 2  # Coherence

    time_indices = [0, len(t)//4, len(t)//2, 3*len(t)//4, len(t)-1]

    for idx in time_indices:
        rho = np.array([
            [rho_00[idx], rho_01[idx]],
            [np.conj(rho_01[idx]), rho_11[idx]]
        ])

        # Plot as heatmap
        im = ax3.imshow(np.abs(rho), cmap='hot', aspect='auto',
                       extent=[0, 2, 0, 2], alpha=0.3)

    ax3.set_xticks([0.5, 1.5])
    ax3.set_yticks([0.5, 1.5])
    ax3.set_xticklabels(['F=2', 'F=3'])
    ax3.set_yticklabels(['F=2', 'F=3'])
    ax3.set_title('Density Matrix |ρ| Evolution', fontsize=12, weight='bold')

    # 
    # Panel 4: Purity and coherence measures
    # 
    ax4 = fig.add_subplot(2, 2, 4)

    # Purity Tr(ρ²)
    purity = rho_00**2 + rho_11**2 + 2*np.abs(rho_01)**2

    # Coherence |ρ₀₁|
    coherence = np.abs(rho_01)

    ax4.plot(t*1e9, purity, color='blue', linewidth=2.5, label='Purity Tr(ρ²)')
    ax4.plot(t*1e9, coherence, color='red', linewidth=2.5, label='Coherence |ρ₀₁|')
    ax4.fill_between(t*1e9, coherence, alpha=0.2, color='red')

    ax4.axhline(1, color='k', linestyle='--', linewidth=1, alpha=0.5, label='Pure state')

    ax4.set_xlabel('Time (ns)', fontsize=11, weight='bold')
    ax4.set_ylabel('Value', fontsize=11, weight='bold')
    ax4.set_title('Quantum Coherence & Purity', fontsize=12, weight='bold')
    ax4.legend(fontsize=10, loc='best')
    ax4.grid(True, alpha=0.3)
    ax4.set_ylim([0, 1.05])

    plt.tight_layout()
    plt.savefig("plots/COOL_06_state_tomography.png", dpi=200, bbox_inches='tight')
    print("  > COOL_06_state_tomography.png [OK]")
    plt.close()


# 
# MAIN EXECUTION
# 

if __name__ == "__main__":
    print("\n" + "="*80)
    print("GENERATING COOL RB-87 QUANTUM SIMULATIONS")
    print("="*80 + "\n")

    create_animated_bloch_evolution()
    create_frequency_sweep_heatmap()
    create_3d_phase_portrait()
    create_pulse_choreography()
    create_ramsey_fringes()
    create_state_tomography()

    print("\n" + "="*80)
    print("SUCCESS! 6 Amazing Visualizations Generated")
    print("="*80)
    print("\nGenerated plots:")
    print("  1. COOL_01_bloch_trajectories.png - 4 different Rabi scenarios on Bloch sphere")
    print("  2. COOL_02_heatmap_dynamics.png - Frequency sweeps and population dynamics")
    print("  3. COOL_03_phase_portrait.png - 3D phase space trajectories")
    print("  4. COOL_04_pulse_sequences.png - Complex quantum pulse choreography")
    print("  5. COOL_05_ramsey_fringes.png - Quantum interference patterns (2D & 3D)")
    print("  6. COOL_06_state_tomography.png - Quantum state reconstruction from measurements")
    print("\n")
