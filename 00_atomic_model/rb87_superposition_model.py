"""
RB-87 ATOMIC SUPERPOSITION MODEL
=================================
Visualizes quantum spin states, superposition, and frequency response
when exposed to 6.8 GHz microwave radiation (hyperfine transition region).

Shows:
- Rb-87 nuclear and electronic spin configurations
- Energy level diagram with hyperfine splitting
- Bloch sphere representation of superposition states
- Rabi oscillations (time evolution under microwave)
- Frequency response curves (narrow resonance dip at 6.834 GHz)
- Population dynamics in superposition
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle
from mpl_toolkits.mplot3d import Axes3D
import os

# ═══════════════════════════════════════════════════════════════════════════════
# RB-87 CONSTANTS
# ═══════════════════════════════════════════════════════════════════════════════

# Nuclear and electronic structure
I_nuclear = 5/2           # Rb-87 nuclear spin
S_electron = 1/2          # Electron spin
L_orbital = 0             # Ground state is S-state (L=0)

# Hyperfine levels: F = I ± S
F1 = I_nuclear - S_electron  # F=2
F2 = I_nuclear + S_electron  # F=3

# Hyperfine transition frequency (used in Rb atomic clocks)
HYPERFINE_FREQ_HZ = 6_834_682_610.904  # 6.834... GHz
HYPERFINE_FREQ_MHZ = HYPERFINE_FREQ_HZ / 1e6

# Test frequency range: ±30 MHz around hyperfine
TEST_OFFSET_MHZ = 30

# Quantum mechanics constants
hbar = 1.054571817e-34
h = 6.62607015e-34
c = 299792458.0
kB = 1.380649e-23

# Natural linewidth (from spontaneous emission)
LIFETIME = 27.7e-9  # seconds for 5P₁/₂ excited state
GAMMA = 1.0 / LIFETIME
LINEWIDTH_HZ = GAMMA / (2 * np.pi)
LINEWIDTH_MHZ = LINEWIDTH_HZ / 1e6

# ═══════════════════════════════════════════════════════════════════════════════
# 1. ATOMIC STRUCTURE & SPINS
# ═══════════════════════════════════════════════════════════════════════════════

def get_rb87_structure():
    """Return physical constants describing Rb-87"""
    return {
        "element": "Rubidium-87",
        "mass_number": 87,
        "nuclear_spin_I": I_nuclear,
        "electron_spin_S": S_electron,
        "ground_state": "5S₁/₂",
        "excited_state": "5P₁/₂",
        "hyperfine_levels": {
            f"F={int(F1)}": {"F": F1, "m_F_values": np.arange(-F1, F1+1)},
            f"F={int(F2)}": {"F": F2, "m_F_values": np.arange(-F2, F2+1)},
        },
        "hyperfine_frequency_ghz": HYPERFINE_FREQ_HZ / 1e9,
        "natural_linewidth_khz": LINEWIDTH_MHZ,
    }


def visualize_spin_configuration():
    """Create diagram showing nuclear I, electronic S, and resulting F"""
    fig, axes = plt.subplots(1, 3, figsize=(14, 4))

    # Left: Nuclear spin I = 5/2
    ax = axes[0]
    ax.set_xlim(-4, 4)
    ax.set_ylim(-4, 4)
    ax.axis('off')
    ax.set_aspect('equal')

    # Draw nucleus
    nucleus = Circle((0, 0), 0.8, color='red', alpha=0.7)
    ax.add_patch(nucleus)
    ax.text(0, 0, "I=5/2\n(nucleus)", ha='center', va='center', fontsize=10, weight='bold', color='white')

    # Draw m_I levels (6 values: -5/2, -3/2, -1/2, 1/2, 3/2, 5/2)
    m_I_values = np.arange(-5, 6, 2) / 2
    for i, m_I in enumerate(m_I_values):
        y = 2 * np.sin(2*np.pi*i/len(m_I_values))
        ax.arrow(-3, y, 0.5, 0, head_width=0.3, head_length=0.2, fc='darkred', ec='darkred')
        ax.text(-2.2, y+0.4, f"m_I={m_I:+.1f}", fontsize=9)
    ax.set_title("Nuclear Spin I = 5/2", fontsize=12, weight='bold')

    # Middle: Electronic spin S = 1/2
    ax = axes[1]
    ax.set_xlim(-4, 4)
    ax.set_ylim(-4, 4)
    ax.axis('off')
    ax.set_aspect('equal')

    # Draw electron
    electron = Circle((0, 0), 0.8, color='blue', alpha=0.7)
    ax.add_patch(electron)
    ax.text(0, 0, "S=1/2\n(electron)", ha='center', va='center', fontsize=10, weight='bold', color='white')

    # Draw m_S levels
    m_S_values = [-1/2, 1/2]
    for i, m_S in enumerate(m_S_values):
        y = 2 - i*4
        ax.arrow(-3, y, 0.5, 0, head_width=0.3, head_length=0.2, fc='darkblue', ec='darkblue')
        ax.text(-2.2, y+0.4, f"m_S={m_S:+.1f}", fontsize=9)
    ax.set_title("Electron Spin S = 1/2", fontsize=12, weight='bold')

    # Right: Total angular momentum F
    ax = axes[2]
    ax.set_xlim(-4, 4)
    ax.set_ylim(-4, 4)
    ax.axis('off')
    ax.set_aspect('equal')

    # Draw hyperfine levels
    ax.text(0, 3, "F = I + S", ha='center', fontsize=11, weight='bold')

    # F=3 (upper level)
    f3_rect = Rectangle((-2.5, 1.5), 5, 0.6, color='purple', alpha=0.7)
    ax.add_patch(f3_rect)
    ax.text(0, 1.8, f"F=3  (m_F = -3 to +3, 7 states)", ha='center', fontsize=10, weight='bold', color='white')
    ax.text(0, 0.8, "ΔE = 3×A/2", ha='center', fontsize=9)

    # F=2 (lower level)
    f2_rect = Rectangle((-2.5, -0.8), 5, 0.6, color='orange', alpha=0.7)
    ax.add_patch(f2_rect)
    ax.text(0, -0.5, f"F=2  (m_F = -2 to +2, 5 states)", ha='center', fontsize=10, weight='bold', color='white')
    ax.text(0, -1.5, "ΔE = -A", ha='center', fontsize=9)

    # Draw hyperfine splitting arrow
    ax.arrow(-3, -1.5, 0, 2.5, head_width=0.2, head_length=0.3, fc='green', ec='green', linewidth=2)
    ax.text(-2.2, 0.5, f"6.834 GHz", fontsize=10, weight='bold', color='green', rotation=90)

    ax.set_title("Hyperfine Structure\n(F = I ⊕ S)", fontsize=12, weight='bold')

    plt.tight_layout()
    return fig


# ═══════════════════════════════════════════════════════════════════════════════
# 2. BLOCH SPHERE: SUPERPOSITION STATES
# ═══════════════════════════════════════════════════════════════════════════════

def bloch_vector(theta, phi):
    """
    Generate Bloch vector components from spherical angles.
    |ψ⟩ = cos(θ/2)|0⟩ + e^(iφ) sin(θ/2)|1⟩

    where |0⟩ = ground state (F=2), |1⟩ = other state (F=3)
    """
    x = np.sin(theta) * np.cos(phi)
    y = np.sin(theta) * np.sin(phi)
    z = np.cos(theta)
    return np.array([x, y, z])


def visualize_bloch_sphere():
    """3D Bloch sphere showing quantum superposition states"""
    fig = plt.figure(figsize=(14, 5))

    # ─────────────────────────────────────────────────────────────────────────
    # LEFT: Bloch sphere with key superposition states
    # ─────────────────────────────────────────────────────────────────────────
    ax1 = fig.add_subplot(121, projection='3d')

    # Draw Bloch sphere (transparent)
    u = np.linspace(0, 2*np.pi, 50)
    v = np.linspace(0, np.pi, 50)
    x_sphere = np.outer(np.cos(u), np.sin(v))
    y_sphere = np.outer(np.sin(u), np.sin(v))
    z_sphere = np.outer(np.ones(np.size(u)), np.cos(v))
    ax1.plot_surface(x_sphere, y_sphere, z_sphere, alpha=0.1, color='cyan')

    # Axes
    ax1.quiver(0, 0, 0, 1.2, 0, 0, color='r', arrow_length_ratio=0.1, linewidth=2, label='X')
    ax1.quiver(0, 0, 0, 0, 1.2, 0, color='g', arrow_length_ratio=0.1, linewidth=2, label='Y')
    ax1.quiver(0, 0, 0, 0, 0, 1.2, color='b', arrow_length_ratio=0.1, linewidth=2, label='Z')

    # Key quantum states
    states = {
        "|0⟩ (F=2)": (np.pi, 0),           # South pole
        "|1⟩ (F=3)": (0, 0),               # North pole
        "|+⟩ (superposition)": (np.pi/2, 0),    # Equator
        "|-⟩ (superposition)": (np.pi/2, np.pi), # Opposite equator
        "|↻⟩ (circular +)": (np.pi/2, np.pi/2), # Circular +
        "|↺⟩ (circular -)": (np.pi/2, -np.pi/2), # Circular -
    }

    colors = {'|0⟩ (F=2)': 'orange', '|1⟩ (F=3)': 'purple',
              '|+⟩ (superposition)': 'red', '|-⟩ (superposition)': 'blue',
              '|↻⟩ (circular +)': 'green', '|↺⟩ (circular -)': 'magenta'}

    for state_label, (theta, phi) in states.items():
        vec = bloch_vector(theta, phi)
        ax1.quiver(0, 0, 0, vec[0], vec[1], vec[2],
                  color=colors[state_label], arrow_length_ratio=0.1, linewidth=2.5)
        # Position label
        label_pos = vec * 1.3
        ax1.text(label_pos[0], label_pos[1], label_pos[2], state_label, fontsize=9, weight='bold')

    ax1.set_xlabel('X (Re coherence)')
    ax1.set_ylabel('Y (Im coherence)')
    ax1.set_zlabel('Z (Population diff)')
    ax1.set_xlim((-1.5, 1.5))
    ax1.set_ylim((-1.5, 1.5))
    ax1.set_zlim((-1.5, 1.5))
    ax1.set_title("Bloch Sphere: Quantum Superposition States\n(F=2 to F=3 transition)",
                  fontsize=11, weight='bold')

    # ─────────────────────────────────────────────────────────────────────────
    # RIGHT: Time evolution under microwave field (Rabi oscillations)
    # ─────────────────────────────────────────────────────────────────────────
    ax2 = fig.add_subplot(122)

    # Parameters for Rabi oscillations
    rabi_freq_hz = 50e3  # 50 kHz Rabi frequency
    rabi_freq = 2 * np.pi * rabi_freq_hz
    t = np.linspace(0, 50e-6, 1000)  # 50 microseconds

    # Populations under resonant driving (on-resonance at 6.834 GHz)
    # P_excited = sin²(Ω_rabi * t / 2)
    # P_ground = cos²(Ω_rabi * t / 2)
    pop_excited = np.sin(rabi_freq * t / 2)**2
    pop_ground = np.cos(rabi_freq * t / 2)**2

    ax2.plot(t*1e6, pop_excited, 'purple', linewidth=2.5, label='F=3 (excited)')
    ax2.plot(t*1e6, pop_ground, 'orange', linewidth=2.5, label='F=2 (ground)')
    ax2.fill_between(t*1e6, pop_excited, alpha=0.2, color='purple')
    ax2.fill_between(t*1e6, pop_ground, alpha=0.2, color='orange')

    # Mark π/2 and π pulses
    t_pi2 = np.pi / (2 * rabi_freq)  # π/2 pulse time
    t_pi = np.pi / rabi_freq  # π pulse time

    ax2.axvline(t_pi2*1e6, color='green', linestyle='--', linewidth=1.5, alpha=0.7, label='π/2 pulse')
    ax2.axvline(t_pi*1e6, color='red', linestyle='--', linewidth=1.5, alpha=0.7, label='π pulse')
    ax2.text(t_pi2*1e6, 0.95, 'π/2', ha='center', fontsize=9, weight='bold', color='green')
    ax2.text(t_pi*1e6, 0.95, 'π', ha='center', fontsize=9, weight='bold', color='red')

    ax2.set_xlabel('Time (μs)', fontsize=11)
    ax2.set_ylabel('Population', fontsize=11)
    ax2.set_title(f"Rabi Oscillations at 6.834 GHz\n(Ω_Rabi = 50 kHz)", fontsize=11, weight='bold')
    ax2.legend(loc='right', fontsize=10)
    ax2.grid(True, alpha=0.3)
    ax2.set_ylim((0, 1.05))

    plt.tight_layout()
    return fig


# ═══════════════════════════════════════════════════════════════════════════════
# 3. FREQUENCY RESPONSE: 6.8 GHz REGION
# ═══════════════════════════════════════════════════════════════════════════════

def frequency_response_lorentzian(freq_hz, center_hz, linewidth_hz):
    """
    Lorentzian lineshape for optical/RF transition.
    I(ν) ∝ 1 / (1 + 4(ν - ν₀)² / Γ²)
    """
    delta = freq_hz - center_hz
    return linewidth_hz / (2 * np.pi * ((delta)**2 + (linewidth_hz/(2*np.pi))**2))


def visualize_frequency_response():
    """Show resonance response at 6.834 GHz and ±30 MHz offsets"""
    fig, axes = plt.subplots(2, 2, figsize=(14, 9))

    # ─────────────────────────────────────────────────────────────────────────
    # TOP LEFT: Narrow resonance (high resolution)
    # ─────────────────────────────────────────────────────────────────────────
    ax = axes[0, 0]
    freq_offset_hz = np.linspace(-200e3, 200e3, 800)  # ±200 kHz
    freq_hz = HYPERFINE_FREQ_HZ + freq_offset_hz
    response = frequency_response_lorentzian(freq_hz, HYPERFINE_FREQ_HZ, LINEWIDTH_HZ)

    ax.plot(freq_offset_hz/1e3, response, 'b-', linewidth=2.5)
    ax.fill_between(freq_offset_hz/1e3, response, alpha=0.3, color='blue')
    ax.axvline(0, color='r', linestyle='--', linewidth=2, alpha=0.7, label='6.834 GHz')
    ax.set_xlabel('Frequency Offset (kHz)', fontsize=11)
    ax.set_ylabel('Response (normalized)', fontsize=11)
    ax.set_title(f"Narrow Resonance at 6.834 GHz\n(Natural Linewidth = {LINEWIDTH_MHZ:.2f} MHz)",
                fontsize=11, weight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=10)

    # ─────────────────────────────────────────────────────────────────────────
    # TOP RIGHT: Wider view (±30 MHz)
    # ─────────────────────────────────────────────────────────────────────────
    ax = axes[0, 1]
    freq_offset_hz = np.linspace(-30e6, 30e6, 1000)
    freq_hz = HYPERFINE_FREQ_HZ + freq_offset_hz
    response = frequency_response_lorentzian(freq_hz, HYPERFINE_FREQ_HZ, LINEWIDTH_HZ)

    ax.plot(freq_offset_hz/1e6, response, 'b-', linewidth=2)
    ax.fill_between(freq_offset_hz/1e6, response, alpha=0.2, color='blue')
    ax.axvline(0, color='r', linestyle='--', linewidth=2, alpha=0.7, label='6.834 GHz')
    ax.set_xlabel('Frequency Offset (MHz)', fontsize=11)
    ax.set_ylabel('Response (normalized)', fontsize=11)
    ax.set_title("Hyperfine Transition (Wide View ±30 MHz)", fontsize=11, weight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=10)
    ax.set_yscale('log')

    # ─────────────────────────────────────────────────────────────────────────
    # BOTTOM LEFT: CPT dark state resonance (very narrow)
    # ─────────────────────────────────────────────────────────────────────────
    ax = axes[1, 0]
    freq_offset_hz = np.linspace(-50e3, 50e3, 1000)  # ±50 kHz
    freq_hz = HYPERFINE_FREQ_HZ + freq_offset_hz
    response = frequency_response_lorentzian(freq_hz, HYPERFINE_FREQ_HZ, LINEWIDTH_HZ*0.05)  # CPT narrows linewidth

    ax.plot(freq_offset_hz/1e3, response, 'g-', linewidth=2.5)
    ax.fill_between(freq_offset_hz/1e3, response, alpha=0.3, color='green')
    ax.axvline(0, color='r', linestyle='--', linewidth=2, alpha=0.7, label='6.834 GHz')
    ax.set_xlabel('Frequency Offset (kHz)', fontsize=11)
    ax.set_ylabel('Response (normalized)', fontsize=11)
    ax.set_title(f"CPT Dark State (Narrowed Linewidth ~100 Hz)\nUsed in atomic clocks",
                fontsize=11, weight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=10)

    # ─────────────────────────────────────────────────────────────────────────
    # BOTTOM RIGHT: Discriminator signal (error signal for servo)
    # ─────────────────────────────────────────────────────────────────────────
    ax = axes[1, 1]
    freq_offset_hz = np.linspace(-100e3, 100e3, 800)
    freq_hz_plus = HYPERFINE_FREQ_HZ + freq_offset_hz + 5e3   # +5 kHz sideband
    freq_hz_minus = HYPERFINE_FREQ_HZ + freq_offset_hz - 5e3  # -5 kHz sideband

    response_plus = frequency_response_lorentzian(freq_hz_plus, HYPERFINE_FREQ_HZ, LINEWIDTH_HZ*0.05)
    response_minus = frequency_response_lorentzian(freq_hz_minus, HYPERFINE_FREQ_HZ, LINEWIDTH_HZ*0.05)
    discriminator = response_minus - response_plus  # Error signal

    ax.plot(freq_offset_hz/1e3, discriminator, 'r-', linewidth=2.5)
    ax.fill_between(freq_offset_hz/1e3, discriminator, alpha=0.2, color='red')
    ax.axhline(0, color='k', linestyle='-', linewidth=0.8, alpha=0.5)
    ax.axvline(0, color='g', linestyle='--', linewidth=2, alpha=0.7, label='Lock point')
    ax.set_xlabel('Frequency Offset (kHz)', fontsize=11)
    ax.set_ylabel('Discriminator Signal (arb.)', fontsize=11)
    ax.set_title("Frequency Discriminator (Error Signal)\nUsed for servo feedback lock",
                fontsize=11, weight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=10)

    plt.tight_layout()
    return fig


# ═══════════════════════════════════════════════════════════════════════════════
# 4. QUANTUM STATE EVOLUTION
# ═══════════════════════════════════════════════════════════════════════════════

def visualize_superposition_evolution():
    """Show how a quantum superposition evolves over time"""
    fig, axes = plt.subplots(2, 2, figsize=(14, 9))

    # Parameters
    freq_hyperfine = HYPERFINE_FREQ_HZ
    dt = 1e-12  # 1 picosecond time step
    t = np.arange(0, 200e-9, dt)  # 200 nanoseconds

    # ─────────────────────────────────────────────────────────────────────────
    # Case 1: Initial state |+⟩ = (|F=2⟩ + |F=3⟩)/√2
    # ─────────────────────────────────────────────────────────────────────────
    ax = axes[0, 0]

    # Phase evolution from hyperfine oscillation
    phase_f2 = np.zeros_like(t)
    phase_f3 = 2 * np.pi * freq_hyperfine * t

    # Coherence oscillation
    coherence = 0.5 * np.exp(1j * (phase_f3 - phase_f2))

    ax.plot(t*1e9, np.abs(coherence), 'b-', linewidth=2, label='|⟨F=3|ψ(t)⟩|')
    ax.plot(t*1e9, np.real(coherence), 'r--', linewidth=1.5, label='Re[coherence]')
    ax.plot(t*1e9, np.imag(coherence), 'g--', linewidth=1.5, label='Im[coherence]')
    ax.set_xlabel('Time (ns)', fontsize=11)
    ax.set_ylabel('Amplitude', fontsize=11)
    ax.set_title("Superposition State |+⟩ = (|F=2⟩ + |F=3⟩)/√2\nCoherence oscillates at 6.834 GHz",
                fontsize=11, weight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)

    # ─────────────────────────────────────────────────────────────────────────
    # Case 2: Decoherence due to environment (decay of coherence)
    # ─────────────────────────────────────────────────────────────────────────
    ax = axes[0, 1]

    # Decoherence timescale τ_c (e.g., 100 ns)
    tau_c = 100e-9

    coherence_decay = 0.5 * np.exp(1j * (phase_f3 - phase_f2)) * np.exp(-t / tau_c)

    ax.plot(t*1e9, np.abs(coherence_decay), 'purple', linewidth=2.5, label='|coherence|')
    ax.plot(t*1e9, np.exp(-t/tau_c), 'k--', linewidth=2, label=f'Envelope (τ_c = 100 ns)')
    ax.set_xlabel('Time (ns)', fontsize=11)
    ax.set_ylabel('Amplitude', fontsize=11)
    ax.set_title("Decoherence: Loss of Superposition\n(From random phase kicks, collisions)",
                fontsize=11, weight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)

    # ─────────────────────────────────────────────────────────────────────────
    # Case 3: Population dynamics under resonant MW (π pulse sequence)
    # ─────────────────────────────────────────────────────────────────────────
    ax = axes[1, 0]

    rabi_freq = 2 * np.pi * 100e3  # 100 kHz Rabi

    # π/2 pulse: creates superposition
    # π pulse: flips populations
    # π/2 pulse: analyzes superposition

    # Time windows
    t_pi2 = np.pi / (2 * rabi_freq)
    t_pi = np.pi / rabi_freq

    pop_f2 = np.ones_like(t)
    pop_f3 = np.zeros_like(t)

    # First π/2 pulse (0 to t_pi2)
    mask1 = t < t_pi2
    pop_f2[mask1] = np.cos(rabi_freq * t[mask1] / 2)**2
    pop_f3[mask1] = np.sin(rabi_freq * t[mask1] / 2)**2

    # Drift period (t_pi2 to 3*t_pi2) - populations stay constant
    mask2 = (t >= t_pi2) & (t < 3*t_pi2)
    pop_f2[mask2] = 0.5
    pop_f3[mask2] = 0.5

    # Second π/2 pulse (3*t_pi2 to 2*t_pi)
    mask3 = (t >= 3*t_pi2) & (t < 2*t_pi)
    t_rel = t[mask3] - 3*t_pi2
    pop_f2[mask3] = np.sin(rabi_freq * t_rel / 2)**2
    pop_f3[mask3] = np.cos(rabi_freq * t_rel / 2)**2

    ax.plot(t*1e6, pop_f2, 'orange', linewidth=2.5, label='F=2 population')
    ax.plot(t*1e6, pop_f3, 'purple', linewidth=2.5, label='F=3 population')
    ax.axvline(t_pi2*1e6, color='green', linestyle=':', alpha=0.5)
    ax.axvline(3*t_pi2*1e6, color='green', linestyle=':', alpha=0.5)
    ax.text(t_pi2*1e6, 0.05, 'π/2', fontsize=9, ha='center')
    ax.text(3*t_pi2*1e6, 0.05, 'π/2', fontsize=9, ha='center')
    ax.set_xlabel('Time (μs)', fontsize=11)
    ax.set_ylabel('Population', fontsize=11)
    ax.set_title("Pulse Sequence: π/2 – Drift – π/2\n(Creates and analyzes superposition)",
                fontsize=11, weight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    ax.set_ylim([-0.1, 1.1])

    # ─────────────────────────────────────────────────────────────────────────
    # Case 4: Ramsey fringe visibility vs decoherence
    # ─────────────────────────────────────────────────────────────────────────
    ax = axes[1, 1]

    # Vary drift time T between pulses
    T_drift = np.linspace(0, 500e-9, 50)
    visibility = np.zeros_like(T_drift)

    # Visibility = (P_max - P_min) / (P_max + P_min)
    # P_max/min depends on coherence phase and decoherence
    tau_c_ramsey = 200e-9

    for i, T in enumerate(T_drift):
        # Coherence after drift (with decoherence)
        coherence_amplitude = np.exp(-T / tau_c_ramsey)
        # Fringe visibility is proportional to coherence
        visibility[i] = np.cos(2 * np.pi * freq_hyperfine * T) * coherence_amplitude

    ax.plot(T_drift*1e9, np.abs(visibility), 'darkblue', linewidth=2.5, marker='o', markersize=4)
    ax.fill_between(T_drift*1e9, 0, np.abs(visibility), alpha=0.2, color='blue')
    ax.set_xlabel('Ramsey Drift Time T (ns)', fontsize=11)
    ax.set_ylabel('Fringe Visibility', fontsize=11)
    ax.set_title(f"Ramsey Fringes: Loss of Fringe Visibility\n(Decoherence time τ_c = 200 ns)",
                fontsize=11, weight='bold')
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    return fig


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN EXECUTION
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    os.makedirs("plots", exist_ok=True)

    print("=" * 80)
    print("RB-87 ATOMIC SUPERPOSITION MODEL — 6.834 GHz HYPERFINE TRANSITION")
    print("=" * 80)

    # Get Rb-87 structure
    rb87 = get_rb87_structure()
    print("\n1. RB-87 ATOMIC STRUCTURE")
    print("-" * 80)
    print(f"   Element: {rb87['element']}")
    print(f"   Nuclear Spin I = {rb87['nuclear_spin_I']}")
    print(f"   Electron Spin S = {rb87['electron_spin_S']}")
    print(f"   Ground State: 5S_1/2")
    print(f"   Hyperfine Frequency: {rb87['hyperfine_frequency_ghz']:.9f} GHz")
    print(f"   Natural Linewidth: {LINEWIDTH_MHZ:.3f} MHz ({LINEWIDTH_HZ:.1f} Hz)")
    print(f"   Hyperfine Levels:")
    for label, data in rb87['hyperfine_levels'].items():
        print(f"      {label}: {len(data['m_F_values'])} magnetic sublevels (m_F = {data['m_F_values'][0]:.1f} to {data['m_F_values'][-1]:.1f})")

    # Generate visualizations
    print("\n2. GENERATING VISUALIZATIONS...")
    print("-" * 80)

    print("   > Spin configuration diagram...")
    fig1 = visualize_spin_configuration()
    fig1.savefig("plots/01_spin_configuration.png", dpi=150, bbox_inches='tight')
    plt.close(fig1)

    print("   > Bloch sphere and Rabi oscillations...")
    fig2 = visualize_bloch_sphere()
    fig2.savefig("plots/02_bloch_sphere_rabi.png", dpi=150, bbox_inches='tight')
    plt.close(fig2)

    print("   > Frequency response (6.834 GHz region)...")
    fig3 = visualize_frequency_response()
    fig3.savefig("plots/03_frequency_response.png", dpi=150, bbox_inches='tight')
    plt.close(fig3)

    print("   > Superposition evolution and decoherence...")
    fig4 = visualize_superposition_evolution()
    fig4.savefig("plots/04_superposition_evolution.png", dpi=150, bbox_inches='tight')
    plt.close(fig4)

    print("\n* All plots saved to plots/")
    print("\nGenerated files:")
    print("   01_spin_configuration.png  — Nuclear I, electron S, hyperfine F")
    print("   02_bloch_sphere_rabi.png   — Quantum states and Rabi oscillations")
    print("   03_frequency_response.png  — 6.834 GHz resonance responses")
    print("   04_superposition_evolution.png — Quantum coherence and decoherence")
    print("\n" + "=" * 80)
