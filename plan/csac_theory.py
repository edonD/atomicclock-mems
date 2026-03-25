"""
THE THEORY BEHIND THE CHIP-SCALE ATOMIC CLOCK
==============================================

This simulation walks through ALL the physics layers, from fundamental
quantum mechanics to the final clock output, showing the math at each step.

Layer 1: ATOMIC STRUCTURE  -- Why Rb-87? Hyperfine splitting from nuclear spin.
Layer 2: LIGHT-ATOM INTERACTION -- Rabi oscillations, dressed states.
Layer 3: THE LAMBDA SYSTEM -- Three-level quantum mechanics.
Layer 4: COHERENT POPULATION TRAPPING -- The dark state (the core invention).
Layer 5: DENSITY MATRIX DYNAMICS -- Solving the master equation for CPT.
Layer 6: LASER PHYSICS -- VCSEL modulation, sideband generation.
Layer 7: BUFFER GAS PHYSICS -- Dicke narrowing, why N2 matters.
Layer 8: ALLAN DEVIATION THEORY -- How atomic stability beats crystal.
Layer 9: FROM FREQUENCY TO TIME -- Counting cycles = measuring time.
Layer 10: ANODIC BONDING -- How the MEMS cell is sealed (materials science).
Layer 11: HERMETIC LIFETIME -- Leak rate physics, Arrhenius aging.
Layer 12: THE FULL EQUATION CHAIN -- From Schrodinger to nanoseconds.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Arc
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.patheffects as pe

# ──────────────────────────────────────────────────────────────────
# CONSTANTS
# ──────────────────────────────────────────────────────────────────
hbar = 1.054571817e-34   # J*s
h    = 6.62607015e-34    # J*s
kB   = 1.380649e-23      # J/K
c    = 299792458          # m/s
e_charge = 1.602176634e-19
mu_B = 9.2740100783e-24  # Bohr magneton J/T
mu_N = 5.0507837461e-27  # nuclear magneton J/T
a0   = 5.29177210903e-11 # Bohr radius m

# Rb-87 specific
RB87_HYPERFINE = 6.834682610904e9   # Hz  (ground state splitting)
RB87_D1_FREQ   = 377.107463380e12   # Hz  (D1 line, 795 nm)
RB87_D1_LAMBDA = 794.978851156e-9   # m
RB87_NUCLEAR_SPIN = 3/2             # I = 3/2
RB87_LIFETIME_5P = 27.70e-9         # s   (5P1/2 radiative lifetime)
RB87_GAMMA = 1 / RB87_LIFETIME_5P   # natural linewidth rate
RB87_GAMMA_NAT = RB87_GAMMA / (2*np.pi)  # Hz


# ──────────────────────────────────────────────────────────────────
# FIGURE
# ──────────────────────────────────────────────────────────────────
fig = plt.figure(figsize=(24, 36), facecolor='#0a0a1a')
fig.suptitle(
    'THE THEORY BEHIND THE CHIP-SCALE ATOMIC CLOCK\n'
    'From the Schrodinger Equation to Nanosecond Timing',
    fontsize=18, fontweight='bold', color='white', y=0.997
)

gs = GridSpec(5, 3, figure=fig, hspace=0.30, wspace=0.30,
              left=0.06, right=0.94, top=0.97, bottom=0.02)


# ======================================================================
# PANEL 1: ATOMIC STRUCTURE -- Why Rb-87 has a hyperfine splitting
# ======================================================================
ax1 = fig.add_subplot(gs[0, 0], facecolor='#0a0a1a')
ax1.set_title('1. ATOMIC STRUCTURE: Why Rb-87?', color='#ff8844',
              fontsize=13, fontweight='bold')

# The key idea: nuclear spin I couples with electron spin J
# For Rb-87:  I = 3/2,  J = 1/2 (ground state 5S1/2)
# F = |I-J| to I+J  =>  F = 1 and F = 2
# The splitting comes from the magnetic dipole interaction
# between the nuclear magnetic moment and the electron's field

# Draw the energy level diagram with full quantum numbers
levels = [
    # (y, label, color, x_range)
    (0.0,  '5S1/2, F=1, (2F+1)=3 substates', '#44aaff', (0.5, 3.5)),
    (0.8,  '5S1/2, F=2, (2F+1)=5 substates', '#44aaff', (0.5, 3.5)),
    (6.0,  '5P1/2, F\'=1', '#ff8844', (1.0, 3.0)),
    (6.5,  '5P1/2, F\'=2', '#ff8844', (1.0, 3.0)),
    (8.5,  '5P3/2 (D2 line, 780 nm)', '#ff4444', (1.5, 2.5)),
]

for y, lab, col, (x0, x1) in levels:
    ax1.plot([x0, x1], [y, y], color=col, linewidth=3)
    ax1.text(x1 + 0.2, y, lab, fontsize=7.5, color=col, va='center')

# Hyperfine splitting annotation
ax1.annotate('', xy=(0.2, 0.8), xytext=(0.2, 0.0),
             arrowprops=dict(arrowstyle='<->', color='yellow', lw=2))
ax1.text(-0.8, 0.4,
    'HYPERFINE\nSPLITTING\n\n6,834,682,610.904 Hz\n\n'
    'Origin:\nH_hfs = A * I . J\n\n'
    'A = magnetic dipole\n    coupling constant\n'
    'I = nuclear spin (3/2)\n'
    'J = electron spin (1/2)\n\n'
    'F=2: I and J parallel\n'
    'F=1: I and J antiparallel',
    fontsize=7, color='yellow', va='center',
    bbox=dict(boxstyle='round,pad=0.4', facecolor='#1a1a0a', edgecolor='yellow'))

# D1 transition
ax1.annotate('', xy=(2.0, 6.0), xytext=(2.0, 0.8),
             arrowprops=dict(arrowstyle='->', color='red', lw=2, linestyle='--'))
ax1.text(2.3, 3.5, 'D1 line\n795 nm\n377 THz', fontsize=8, color='red')

# Why Rb-87?
ax1.text(4.5, -1.5,
    'WHY Rb-87?\n'
    '1. Large hyperfine splitting (6.835 GHz)\n'
    '    -> accessible with microwave electronics\n'
    '2. D1 line at 795 nm -> cheap VCSELs exist\n'
    '3. High vapor pressure at 85C -> works in tiny cells\n'
    '4. Odd nucleon count (I=3/2) -> hyperfine structure',
    fontsize=7.5, color='white',
    bbox=dict(boxstyle='round,pad=0.4', facecolor='#111133', edgecolor='#444'))

ax1.set_xlim(-2, 9)
ax1.set_ylim(-2.5, 9.5)
ax1.axis('off')


# ======================================================================
# PANEL 2: LIGHT-ATOM INTERACTION -- Rabi Oscillations
# ======================================================================
ax2 = fig.add_subplot(gs[0, 1], facecolor='#0a0a1a')
ax2.set_title('2. LIGHT-ATOM INTERACTION: Rabi Oscillations', color='#ff8844',
              fontsize=13, fontweight='bold')

# Two-level atom in a resonant laser field
# |psi(t)> = c_g(t)|g> + c_e(t)|e>
# Probability of being in excited state:
# P_e(t) = sin^2(Omega_R * t / 2)  (at resonance)
# where Omega_R = d * E0 / hbar  is the Rabi frequency

t_rabi = np.linspace(0, 5, 1000)  # in units of 2*pi/Omega_R
Omega_R = 2 * np.pi  # Rabi frequency (normalized)

# On resonance
P_e_resonant = np.sin(Omega_R * t_rabi / 2)**2

# Off resonance (detuning delta)
for delta_frac, col, alpha, label in [(0, '#00ff88', 1.0, 'On resonance (delta=0)'),
                                       (1.0, '#ffaa00', 0.7, 'delta = Omega_R'),
                                       (2.0, '#ff4444', 0.5, 'delta = 2*Omega_R')]:
    Omega_eff = np.sqrt(Omega_R**2 + (delta_frac * Omega_R)**2)
    P_e = (Omega_R / Omega_eff)**2 * np.sin(Omega_eff * t_rabi / 2)**2
    ax2.plot(t_rabi, P_e, color=col, linewidth=2, alpha=alpha, label=label)

ax2.set_xlabel('Time (units of 2pi / Omega_R)', color='white', fontsize=9)
ax2.set_ylabel('Excited State Population P_e', color='white', fontsize=9)
ax2.legend(fontsize=7.5, facecolor='#1a1a2e', edgecolor='#444', labelcolor='white')
ax2.grid(True, alpha=0.1, color='gray')
ax2.tick_params(colors='gray')
for sp in ax2.spines.values():
    sp.set_edgecolor('#333')

# Theory box
ax2.text(2.5, 1.05,
    'Schrodinger Equation for 2-level atom:\n'
    'i*hbar * d|psi>/dt = H|psi>\n\n'
    'H = H_atom + H_interaction\n'
    'H_int = -d . E(t)   (dipole coupling)\n\n'
    'Rabi frequency: Omega_R = d*E0/hbar\n'
    'P_excited = (Omega_R/Omega_eff)^2 * sin^2(Omega_eff*t/2)\n'
    'Omega_eff = sqrt(Omega_R^2 + delta^2)',
    fontsize=6.5, color='#aaaaaa', va='top',
    bbox=dict(boxstyle='round,pad=0.3', facecolor='#111133', edgecolor='#444'),
    transform=ax2.transData)


# ======================================================================
# PANEL 3: THE LAMBDA SYSTEM -- Three-level quantum mechanics
# ======================================================================
ax3 = fig.add_subplot(gs[0, 2], facecolor='#0a0a1a')
ax3.set_title('3. THE LAMBDA SYSTEM (3-Level QM)', color='#ff8844',
              fontsize=13, fontweight='bold')

# Lambda system: |1>, |2> (ground), |3> (excited)
# Two laser fields: Omega_1 (|1> <-> |3>) and Omega_2 (|2> <-> |3>)

e1, e2, e3 = 0.0, 0.7, 4.5

# States
ax3.plot([1, 3], [e1, e1], color='#44aaff', linewidth=3)
ax3.plot([5, 7], [e2, e2], color='#44aaff', linewidth=3)
ax3.plot([2.5, 5.5], [e3, e3], color='#ff8844', linewidth=3)

ax3.text(2.0, e1-0.4, '|1> = |F=1, mF=0>', ha='center', fontsize=9, color='#44aaff')
ax3.text(6.0, e2-0.4, '|2> = |F=2, mF=0>', ha='center', fontsize=9, color='#44aaff')
ax3.text(4.0, e3+0.3, '|3> = |F\'=1 or F\'=2>', ha='center', fontsize=9, color='#ff8844')

# Coupling arrows
ax3.annotate('', xy=(3.0, e3-0.1), xytext=(2.0, e1+0.1),
             arrowprops=dict(arrowstyle='->', color='red', lw=3))
ax3.text(1.5, 2.3, 'Omega_1\n(probe)', fontsize=10, color='red', fontweight='bold')

ax3.annotate('', xy=(5.0, e3-0.1), xytext=(6.0, e2+0.1),
             arrowprops=dict(arrowstyle='->', color='#ff6666', lw=3))
ax3.text(6.5, 2.5, 'Omega_2\n(coupling)', fontsize=10, color='#ff6666', fontweight='bold')

# Decay (wavy line approximated)
t_wave = np.linspace(0, 1, 50)
ax3.plot(3.8 + 0.15*np.sin(20*t_wave), e3 - 0.3 - t_wave*2.5,
         color='#888888', linewidth=1, alpha=0.5)
ax3.text(4.2, 2.5, 'Gamma\n(spont.\ndecay)', fontsize=7, color='#888888')

# Hamiltonian
ax3.text(4.0, -1.5,
    'Hamiltonian (rotating frame, RWA):\n\n'
    '        | 0        0       Omega_1/2 |\n'
    'H = -hbar| 0      -delta_R   Omega_2/2 |\n'
    '        | Omega_1/2  Omega_2/2  -delta_1  |\n\n'
    'delta_1 = one-photon detuning (laser - atom)\n'
    'delta_R = two-photon (Raman) detuning\n'
    '        = (omega_1 - omega_2) - omega_HFS\n\n'
    'CPT happens when delta_R = 0 (exact Raman resonance)',
    ha='center', va='top', fontsize=7, color='white', fontfamily='monospace',
    bbox=dict(boxstyle='round,pad=0.5', facecolor='#111133', edgecolor='#ff8844'))

ax3.set_xlim(-0.5, 9)
ax3.set_ylim(-4.5, 5.5)
ax3.axis('off')


# ======================================================================
# PANEL 4: CPT -- THE DARK STATE (the core invention)
# ======================================================================
ax4 = fig.add_subplot(gs[1, 0], facecolor='#0a0a1a')
ax4.set_title('4. COHERENT POPULATION TRAPPING (The Key)', color='#00ff88',
              fontsize=13, fontweight='bold')

# The dark state: |D> = (Omega_2|1> - Omega_1|2>) / sqrt(Omega_1^2 + Omega_2^2)
# This state has ZERO overlap with |3> -- it cannot absorb light!

# Show absorption vs Raman detuning
delta_R = np.linspace(-50, 50, 2000)  # kHz

# Broad absorption background (Doppler + power broadened)
Gamma_D = 20  # kHz effective Doppler width
absorption_bg = 0.8 * (1 - np.exp(-delta_R**2 / (2*Gamma_D**2)) * 0.3)

# Narrow CPT dip in absorption (= transparency window)
Gamma_CPT = 1.5  # kHz (CPT linewidth)
CPT_contrast = 0.6
cpt_dip = CPT_contrast * np.exp(-delta_R**2 / (2*Gamma_CPT**2))

absorption = absorption_bg - cpt_dip
transmission = 1 - absorption

ax4.plot(delta_R, absorption, color='#ff4444', linewidth=2, label='Absorption')
ax4.plot(delta_R, transmission, color='#00ff88', linewidth=2.5, label='Transmission (CPT)')
ax4.fill_between(delta_R, 0, cpt_dip * 0.5, alpha=0.15, color='#00ff88')

ax4.axvline(0, color='yellow', linestyle=':', alpha=0.4)

# Zoom inset
axins4 = ax4.inset_axes([0.60, 0.55, 0.37, 0.40])
axins4.set_facecolor('#111133')
mask4 = np.abs(delta_R) < 8
axins4.plot(delta_R[mask4], transmission[mask4], color='#00ff88', linewidth=2.5)
axins4.axvline(0, color='yellow', linestyle=':', alpha=0.5)
axins4.set_title('The CPT Window', fontsize=7, color='white')
axins4.tick_params(colors='gray', labelsize=5)
for sp in axins4.spines.values():
    sp.set_edgecolor('#444')

# THE KEY EQUATIONS
ax4.text(25, 0.95,
    'THE DARK STATE:\n\n'
    '|D> = (Omega_2|1> - Omega_1|2>)\n'
    '      / sqrt(Omega_1^2+Omega_2^2)\n\n'
    'Property: <3|H|D> = 0\n'
    '-> atom CANNOT absorb light!\n'
    '-> trapped in dark superposition\n\n'
    'CPT linewidth:\n'
    'Gamma_CPT ~ Gamma_rel + (Omega1*Omega2)^2\n'
    '            / (Gamma * Gamma_opt)\n\n'
    'Gamma_rel = ground-state\n'
    '  decoherence rate (~1 kHz in\n'
    '  buffer gas cell)',
    fontsize=7, color='#00ff88', va='top',
    bbox=dict(boxstyle='round,pad=0.4', facecolor='#0a1a0a', edgecolor='#00ff88'))

ax4.set_xlabel('Two-Photon (Raman) Detuning delta_R (kHz)', color='white', fontsize=9)
ax4.set_ylabel('Signal (a.u.)', color='white', fontsize=9)
ax4.legend(fontsize=8, facecolor='#1a1a2e', edgecolor='#444', labelcolor='white')
ax4.tick_params(colors='gray')
ax4.grid(True, alpha=0.1, color='gray')
for sp in ax4.spines.values():
    sp.set_edgecolor('#333')


# ======================================================================
# PANEL 5: DENSITY MATRIX -- Solving the master equation
# ======================================================================
ax5 = fig.add_subplot(gs[1, 1], facecolor='#0a0a1a')
ax5.set_title('5. DENSITY MATRIX: The Full Quantum Solution', color='#00ff88',
              fontsize=13, fontweight='bold')

# Solve the 3-level Lambda system density matrix equations
# d(rho)/dt = -i/hbar [H, rho] + L[rho]  (Lindblad master equation)
#
# For steady state, set d(rho)/dt = 0 and solve.
# Key observable: Im(rho_13) proportional to absorption of field 1

# Simplified steady-state solution for absorption
# Im(rho_13) ~ Omega_1 * Gamma/2 / [(delta_1)^2 + (Gamma/2)^2 + |Omega_c|^2/(gamma_12 - i*delta_R)]
# This shows the CPT dip when delta_R -> 0

delta_R_fine = np.linspace(-30, 30, 1000)

Omega_1 = 1.0   # probe Rabi frequency (normalized)
Omega_2 = 1.0   # coupling Rabi frequency
Gamma = 10.0     # excited state decay rate (arb units)
gamma_12 = 0.3   # ground-state decoherence rate
delta_1 = 0.0    # one-photon detuning = 0 (on D1 resonance)

# Absorption: Im(rho_13)
# Using the analytical formula for Lambda CPT
denom_base = (Gamma/2)**2 + delta_1**2
coupling_term = Omega_2**2 / (gamma_12 + 1j*delta_R_fine)
absorption_rho = Omega_1 * (Gamma/2) / np.abs(denom_base + coupling_term)

# Plot populations
ax5.plot(delta_R_fine, absorption_rho / absorption_rho.max(),
         color='#ff8844', linewidth=2.5, label='Absorption ~ Im(rho_13)')
ax5.fill_between(delta_R_fine, 0, absorption_rho / absorption_rho.max(),
                 alpha=0.15, color='#ff8844')

# Show the dark state population
# rho_DD ~ 1 - absorption (roughly)
dark_pop = 1 - absorption_rho / absorption_rho.max()
ax5.plot(delta_R_fine, dark_pop, color='#00ff88', linewidth=2,
         linestyle='--', label='Dark state population rho_DD')

ax5.set_xlabel('Raman Detuning delta_R (arb. units)', color='white', fontsize=9)
ax5.set_ylabel('Normalized Signal', color='white', fontsize=9)
ax5.legend(fontsize=7.5, facecolor='#1a1a2e', edgecolor='#444', labelcolor='white')
ax5.tick_params(colors='gray')
ax5.grid(True, alpha=0.1, color='gray')
for sp in ax5.spines.values():
    sp.set_edgecolor('#333')

# Master equation
ax5.text(15, 0.95,
    'Lindblad Master Equation:\n\n'
    'd(rho)/dt = -(i/hbar)[H,rho]\n'
    '            + SUM_k (L_k rho L_k+\n'
    '              - 1/2{L_k+ L_k, rho})\n\n'
    'L_k = collapse operators\n'
    '    = sqrt(Gamma)|g><e| (spont. decay)\n\n'
    'Steady state: d(rho)/dt = 0\n'
    '-> solve 9 coupled equations\n'
    '-> extract Im(rho_13) = absorption',
    fontsize=6.5, color='#aaaaaa', va='top',
    bbox=dict(boxstyle='round,pad=0.4', facecolor='#111133', edgecolor='#444'))


# ======================================================================
# PANEL 6: VCSEL MODULATION -- Sideband Generation
# ======================================================================
ax6 = fig.add_subplot(gs[1, 2], facecolor='#0a0a1a')
ax6.set_title('6. LASER PHYSICS: VCSEL Sideband Generation', color='#00ff88',
              fontsize=13, fontweight='bold')

# The VCSEL is current-modulated at f_mod = 3.417 GHz
# This creates FM sidebands: E(t) = E0 * exp(i*omega_c*t + i*beta*sin(omega_m*t))
# Jacobi-Anger expansion: E(t) = E0 * SUM_n J_n(beta) * exp(i*(omega_c + n*omega_m)*t)
# For CPT, we use n=+1 and n=-1 sidebands separated by 2*f_mod = 6.834 GHz

# Frequency spectrum
f_mod = 3.417  # GHz
f_carrier = 377107.463  # GHz (D1 line)
beta = 1.8  # modulation index (typical for CSAC)

# Bessel function amplitudes
from scipy.special import jv as bessel_j

n_sidebands = 5
orders = np.arange(-n_sidebands, n_sidebands + 1)
amplitudes = np.array([bessel_j(n, beta) for n in orders])
freqs = orders * f_mod  # GHz offset from carrier

# Plot spectrum
markerline, stemlines, baseline = ax6.stem(freqs, np.abs(amplitudes)**2,
                                            linefmt='-', markerfmt='o', basefmt=' ')
plt.setp(stemlines, color='#ff4444', linewidth=2, alpha=0.7)
plt.setp(markerline, color='#ff4444', markersize=8)

# Highlight the two CPT sidebands
ax6.plot(-f_mod, np.abs(bessel_j(-1, beta))**2, 'o', color='#00ff88',
         markersize=14, zorder=10)
ax6.plot(+f_mod, np.abs(bessel_j(+1, beta))**2, 'o', color='#00ff88',
         markersize=14, zorder=10)

ax6.annotate('1st order\nsideband\n(omega_1)',
             xy=(-f_mod, np.abs(bessel_j(-1, beta))**2),
             xytext=(-f_mod - 4, 0.25),
             fontsize=8, color='#00ff88', fontweight='bold',
             arrowprops=dict(arrowstyle='->', color='#00ff88', lw=1.5))
ax6.annotate('1st order\nsideband\n(omega_2)',
             xy=(+f_mod, np.abs(bessel_j(+1, beta))**2),
             xytext=(+f_mod + 2, 0.25),
             fontsize=8, color='#00ff88', fontweight='bold',
             arrowprops=dict(arrowstyle='->', color='#00ff88', lw=1.5))

# Separation annotation
ax6.annotate('', xy=(f_mod, 0.38), xytext=(-f_mod, 0.38),
             arrowprops=dict(arrowstyle='<->', color='yellow', lw=2))
ax6.text(0, 0.40, '2 * f_mod = 6.835 GHz\n= Rb-87 hyperfine splitting!',
         ha='center', fontsize=9, color='yellow', fontweight='bold')

ax6.set_xlabel('Frequency Offset from Carrier (GHz)', color='white', fontsize=9)
ax6.set_ylabel('Relative Power |J_n(beta)|^2', color='white', fontsize=9)
ax6.tick_params(colors='gray')
ax6.grid(True, alpha=0.1, color='gray')
for sp in ax6.spines.values():
    sp.set_edgecolor('#333')

# Theory box
ax6.text(0, -0.08,
    'E(t) = E0 * exp(i*w_c*t + i*beta*sin(w_m*t))\n'
    '     = E0 * SUM_n J_n(beta) * exp(i*(w_c + n*w_m)*t)\n\n'
    'J_n = Bessel function of 1st kind\n'
    f'Modulation index beta = {beta} (optimized for max J_1)',
    ha='center', fontsize=7, color='#aaaaaa', va='top',
    bbox=dict(boxstyle='round,pad=0.3', facecolor='#111133', edgecolor='#444'))


# ======================================================================
# PANEL 7: BUFFER GAS PHYSICS -- Dicke Narrowing
# ======================================================================
ax7 = fig.add_subplot(gs[2, 0], facecolor='#0a0a1a')
ax7.set_title('7. BUFFER GAS: Why N2 is Inside the Cell', color='#44aaff',
              fontsize=13, fontweight='bold')

# Without buffer gas: atoms fly across beam in ~microseconds -> transit-time broadening
# With buffer gas (N2): atoms undergo random walk -> Dicke narrowing
# The effective linewidth narrows because atoms spend more time in the beam

# Transit time broadening vs buffer gas pressure
P_buffer = np.linspace(0, 150, 300)  # Torr

# Transit-time linewidth (no buffer gas): Gamma_tt = v_th / beam_diameter
v_thermal = np.sqrt(2 * kB * (85+273) / (87 * 1.66e-27))  # Rb at 85C
beam_diam = 0.5e-3  # 0.5 mm beam in MEMS cell
Gamma_tt_0 = v_thermal / (np.pi * beam_diam)  # Hz

# With buffer gas: mean free path decreases, effective transit time increases
# Gamma_tt(P) ~ Gamma_tt_0 * P0 / P  (Dicke narrowing regime)
P0 = 10  # Torr reference
Gamma_tt = Gamma_tt_0 * P0 / (P_buffer + 0.1)  # avoid div by zero

# But buffer gas also causes pressure broadening: Gamma_pressure = k * P
k_pressure = 500  # Hz/Torr for N2 on Rb
Gamma_pressure = k_pressure * P_buffer

# Total CPT linewidth
Gamma_total = Gamma_tt + Gamma_pressure
# There's an optimum!
opt_idx = np.argmin(Gamma_total)
P_opt = P_buffer[opt_idx]

ax7.semilogy(P_buffer, Gamma_tt / 1e3, color='#ff4444', linewidth=2,
             label='Transit-time broadening', linestyle='--')
ax7.semilogy(P_buffer, Gamma_pressure / 1e3, color='#44aaff', linewidth=2,
             label='Pressure broadening (N2)', linestyle='--')
ax7.semilogy(P_buffer, Gamma_total / 1e3, color='#00ff88', linewidth=3,
             label='TOTAL linewidth')

# Mark optimum
ax7.plot(P_opt, Gamma_total[opt_idx]/1e3, 'o', color='yellow', markersize=12, zorder=5)
ax7.annotate(f'OPTIMUM\nP = {P_opt:.0f} Torr\nGamma = {Gamma_total[opt_idx]/1e3:.1f} kHz',
             xy=(P_opt, Gamma_total[opt_idx]/1e3),
             xytext=(P_opt + 40, Gamma_total[opt_idx]/1e3 * 5),
             fontsize=9, color='yellow', fontweight='bold',
             arrowprops=dict(arrowstyle='->', color='yellow', lw=1.5))

ax7.set_xlabel('N2 Buffer Gas Pressure (Torr)', color='white', fontsize=10)
ax7.set_ylabel('CPT Linewidth (kHz)', color='white', fontsize=10)
ax7.legend(fontsize=8, facecolor='#1a1a2e', edgecolor='#444', labelcolor='white')
ax7.tick_params(colors='gray')
ax7.grid(True, alpha=0.15, color='gray')
for sp in ax7.spines.values():
    sp.set_edgecolor('#333')

# Physics box
ax7.text(100, 300,
    'DICKE NARROWING:\n'
    'Buffer gas confines Rb atoms\n'
    'via random walk (diffusion).\n'
    'Effective interaction time\n'
    'increases -> narrower line.\n\n'
    'But too much gas -> pressure\n'
    'broadening dominates.\n'
    'Optimal: ~30-75 Torr N2.',
    fontsize=7.5, color='#44aaff',
    bbox=dict(boxstyle='round,pad=0.3', facecolor='#0a0a2e', edgecolor='#44aaff'))


# ======================================================================
# PANEL 8: BLOCH SPHERE -- Visualization of the Dark State
# ======================================================================
ax8 = fig.add_subplot(gs[2, 1], projection='3d', facecolor='#0a0a1a')
ax8.set_title('8. BLOCH SPHERE: Dark State Geometry', color='#44aaff',
              fontsize=12, fontweight='bold', pad=12)

# The ground-state coherence lives on a Bloch sphere spanned by |1> and |2>
# Dark state |D> is a specific point on this sphere
# Bright state |B> is the orthogonal point
# CPT = pumping ALL population into |D>

# Draw Bloch sphere
u = np.linspace(0, 2*np.pi, 60)
v = np.linspace(0, np.pi, 40)
x_sphere = np.outer(np.cos(u), np.sin(v))
y_sphere = np.outer(np.sin(u), np.sin(v))
z_sphere = np.outer(np.ones(np.size(u)), np.cos(v))
ax8.plot_surface(x_sphere, y_sphere, z_sphere, alpha=0.05,
                  color='#4488aa', edgecolor='#4488aa', linewidth=0.1)

# Axes
for direction, label, col in [([1.3,0,0], '|1>', '#44aaff'),
                                ([0,1.3,0], 'coherence', '#aaaaaa'),
                                ([0,0,1.3], '|2>', '#44aaff')]:
    ax8.plot([0, direction[0]], [0, direction[1]], [0, direction[2]],
             color=col, linewidth=1.5, alpha=0.5)
    ax8.text(direction[0]*1.15, direction[1]*1.15, direction[2]*1.15,
             label, fontsize=8, color=col)

# Dark state vector (depends on Omega_1/Omega_2 ratio)
# For equal Rabi frequencies: |D> = (|1> - |2>)/sqrt(2) -> equator, 225 degrees
theta_D = np.pi / 2  # equator
phi_D = 5 * np.pi / 4  # 225 degrees
D_x = np.sin(theta_D) * np.cos(phi_D)
D_y = np.sin(theta_D) * np.sin(phi_D)
D_z = np.cos(theta_D)
ax8.quiver(0, 0, 0, D_x, D_y, D_z, color='#00ff88', linewidth=3,
           arrow_length_ratio=0.15)
ax8.text(D_x*1.2, D_y*1.2, D_z+0.15, '|D> DARK\nSTATE', fontsize=9,
         color='#00ff88', fontweight='bold')

# Bright state (orthogonal)
B_x = np.sin(theta_D) * np.cos(phi_D + np.pi)
B_y = np.sin(theta_D) * np.sin(phi_D + np.pi)
B_z = 0
ax8.quiver(0, 0, 0, B_x, B_y, B_z, color='#ff4444', linewidth=2,
           arrow_length_ratio=0.15, alpha=0.7)
ax8.text(B_x*1.2, B_y*1.2, 0.15, '|B> BRIGHT\n(absorbs)', fontsize=8,
         color='#ff4444')

# Show pumping trajectory (spiral toward dark state)
t_spiral = np.linspace(0, 3*np.pi, 100)
r_spiral = 1.0
theta_spiral = np.pi/2
phi_spiral = np.pi/4 + t_spiral * 0.4
z_tilt = 0.3 * np.exp(-t_spiral / 3)
ax8.plot(r_spiral * np.cos(phi_spiral),
         r_spiral * np.sin(phi_spiral),
         z_tilt,
         color='yellow', linewidth=1.5, alpha=0.5, linestyle=':')
ax8.text(0.8, 0.8, 0.4, 'Optical\npumping\ntrajectory', fontsize=6, color='yellow')

ax8.set_xlim(-1.3, 1.3)
ax8.set_ylim(-1.3, 1.3)
ax8.set_zlim(-1.3, 1.3)
ax8.tick_params(colors='gray', labelsize=5)
for pane in [ax8.xaxis.pane, ax8.yaxis.pane, ax8.zaxis.pane]:
    pane.fill = False
    pane.set_edgecolor('#222')
ax8.view_init(elev=20, azim=-45)


# ======================================================================
# PANEL 9: ALLAN DEVIATION THEORY
# ======================================================================
ax9 = fig.add_subplot(gs[2, 2], facecolor='#0a0a1a')
ax9.set_title('9. ALLAN DEVIATION: The Math of Clock Stability', color='#44aaff',
              fontsize=13, fontweight='bold')

tau = np.logspace(-1, 6, 400)

# Three noise types that dominate CSAC stability:
# 1. White frequency noise: sigma_y(tau) = sigma_0 / sqrt(tau)
# 2. Flicker frequency noise: sigma_y(tau) = const
# 3. Random walk (drift): sigma_y(tau) = sigma_d * sqrt(tau)

sigma_0 = 2e-10   # white FM coefficient
sigma_f = 5e-12    # flicker floor
sigma_d = 8e-15    # drift coefficient

adev_white = sigma_0 / np.sqrt(tau)
adev_flicker = sigma_f * np.ones_like(tau)
adev_drift = sigma_d * np.sqrt(tau)
adev_total = np.sqrt(adev_white**2 + adev_flicker**2 + adev_drift**2)

ax9.loglog(tau, adev_white, color='#44aaff', lw=1.5, ls='--', alpha=0.6,
           label='White FM: sigma_0/sqrt(tau)')
ax9.loglog(tau, adev_flicker, color='#ffaa00', lw=1.5, ls=':', alpha=0.6,
           label='Flicker floor: const')
ax9.loglog(tau, adev_drift, color='#ff4444', lw=1.5, ls='-.', alpha=0.6,
           label='Drift: sigma_d*sqrt(tau)')
ax9.loglog(tau, adev_total, color='#00ff88', lw=3, label='TOTAL ADEV')

ax9.set_xlabel('Averaging Time tau (s)', color='white', fontsize=10)
ax9.set_ylabel('Allan Deviation sigma_y(tau)', color='white', fontsize=10)
ax9.legend(fontsize=7.5, facecolor='#1a1a2e', edgecolor='#444', labelcolor='white',
           loc='upper right')
ax9.set_xlim(0.1, 1e6)
ax9.set_ylim(1e-13, 1e-7)
ax9.grid(True, alpha=0.15, color='gray')
ax9.tick_params(colors='gray')
for sp in ax9.spines.values():
    sp.set_edgecolor('#333')

# Theory box
ax9.text(0.3, 5e-8,
    'Allan Variance:\n'
    'sigma_y^2(tau) = <(y_k+1 - y_k)^2> / 2\n\n'
    'y_k = fractional frequency\n'
    '    = (f - f_0) / f_0\n'
    '    averaged over interval tau\n\n'
    'For CSAC:\n'
    '  Short-term: photon shot noise\n'
    '    -> sigma_0 ~ 2e-10\n'
    '  Medium-term: flicker (1/f)\n'
    '    -> 5e-12 floor\n'
    '  Long-term: cell aging/drift\n'
    '    -> sigma_d ~ 8e-15',
    fontsize=7, color='#aaaaaa',
    bbox=dict(boxstyle='round,pad=0.3', facecolor='#111133', edgecolor='#444'))


# ======================================================================
# PANEL 10: FROM FREQUENCY TO TIME -- Counting cycles
# ======================================================================
ax10 = fig.add_subplot(gs[3, 0], facecolor='#0a0a1a')
ax10.set_title('10. FROM FREQUENCY TO TIME: Counting Cycles', color='#ffaa00',
               fontsize=13, fontweight='bold')

# Show the fundamental principle: time = counting oscillation cycles
# 1 second = exactly 6,834,682,610.904 cycles of Rb-87 hyperfine transition

t_osc = np.linspace(0, 4, 1000)  # nanoseconds

# Rb oscillation (6.835 GHz)
f_rb = 6.835  # GHz
signal_rb = np.sin(2 * np.pi * f_rb * t_osc)
ax10.plot(t_osc, signal_rb + 3, color='#00ff88', linewidth=1.5)
ax10.text(-0.3, 3, 'Rb-87\n6.835 GHz', fontsize=8, color='#00ff88',
          fontweight='bold', ha='right')

# Quartz oscillation (10 MHz for comparison)
f_xtal = 0.01  # GHz
signal_xtal = np.sin(2 * np.pi * f_xtal * t_osc)
ax10.plot(t_osc, signal_xtal + 1, color='#ff4444', linewidth=1.5)
ax10.text(-0.3, 1, 'Quartz\n10 MHz', fontsize=8, color='#ff4444',
          fontweight='bold', ha='right')

# Divider output (1 PPS)
ax10.plot([0, 0.5, 0.5, 3.5, 3.5, 4], [-1, -1, -0.3, -0.3, -1, -1],
          color='#ffaa00', linewidth=2)
ax10.text(-0.3, -0.65, '1 PPS\noutput', fontsize=8, color='#ffaa00',
          fontweight='bold', ha='right')

# Annotations
ax10.text(2, 4.5,
    'ATOMIC CLOCK = FREQUENCY COUNTER\n\n'
    'Step 1: Lock oscillator to atom (6,834,682,610.904 Hz)\n'
    'Step 2: Count exactly this many cycles = 1 SECOND\n'
    'Step 3: Output 1 pulse per second (1 PPS)\n\n'
    'WHY ATOMS ARE BETTER THAN CRYSTALS:\n'
    'Every Rb-87 atom in the universe oscillates at\n'
    'EXACTLY the same frequency (set by quantum mechanics).\n'
    'Crystal oscillators depend on shape, temperature,\n'
    'aging -- no two are identical.',
    ha='center', va='top', fontsize=8, color='white',
    bbox=dict(boxstyle='round,pad=0.5', facecolor='#111133', edgecolor='#ffaa00'))

ax10.set_xlim(-1.5, 4.5)
ax10.set_ylim(-2, 5.2)
ax10.axis('off')


# ======================================================================
# PANEL 11: ANODIC BONDING -- How the cell is sealed
# ======================================================================
ax11 = fig.add_subplot(gs[3, 1], facecolor='#0a0a1a')
ax11.set_title('11. ANODIC BONDING: Sealing the Cell', color='#ffaa00',
               fontsize=13, fontweight='bold')

# Draw the anodic bonding process
# Glass (borosilicate, contains Na+) + Silicon
# Apply voltage (~400V) at ~350C
# Na+ ions drift away from interface -> depletion layer
# Electrostatic force pulls glass to Si -> forms Si-O bond

# Before bonding
ax11.text(4, 9, 'THE BONDING PROCESS', ha='center', fontsize=10,
          color='white', fontweight='bold')

# Step 1: Stack
draw_y = 7.5
ax11.add_patch(FancyBboxPatch((1, draw_y), 6, 0.6, boxstyle="round,pad=0.02",
               facecolor='#4488cc', edgecolor='white', alpha=0.4))
ax11.text(4, draw_y+0.3, 'Glass (borosilicate, has Na+ ions)', ha='center',
          fontsize=7.5, color='white')
ax11.add_patch(FancyBboxPatch((1, draw_y-0.8), 6, 0.6, boxstyle="round,pad=0.02",
               facecolor='#888888', edgecolor='white', alpha=0.4))
ax11.text(4, draw_y-0.5, 'Silicon', ha='center', fontsize=7.5, color='white')
ax11.text(0.3, draw_y-0.1, 'Step 1:\nStack', fontsize=7, color='#aaaaaa', ha='right')

# Step 2: Heat + Voltage
draw_y2 = 5.5
ax11.add_patch(FancyBboxPatch((1, draw_y2), 6, 0.6, boxstyle="round,pad=0.02",
               facecolor='#4488cc', edgecolor='white', alpha=0.4))
ax11.add_patch(FancyBboxPatch((1, draw_y2-0.7), 6, 0.6, boxstyle="round,pad=0.02",
               facecolor='#888888', edgecolor='white', alpha=0.4))

# Voltage source
ax11.annotate('', xy=(4, draw_y2+0.7), xytext=(4, draw_y2+1.3),
              arrowprops=dict(arrowstyle='->', color='#FFD700', lw=2))
ax11.text(4, draw_y2+1.5, '- (cathode, 400V)', ha='center', fontsize=7, color='#FFD700')
ax11.annotate('', xy=(4, draw_y2-0.8), xytext=(4, draw_y2-1.4),
              arrowprops=dict(arrowstyle='->', color='#ff4444', lw=2))
ax11.text(4, draw_y2-1.6, '+ (anode, ground)', ha='center', fontsize=7, color='#ff4444')

# Na+ ions moving
for nx in [2, 3, 4, 5, 6]:
    ax11.annotate('Na+', xy=(nx, draw_y2+0.55), xytext=(nx, draw_y2+0.2),
                  fontsize=5, color='yellow',
                  arrowprops=dict(arrowstyle='->', color='yellow', lw=0.8))

ax11.text(0.3, draw_y2, 'Step 2:\n350 C\n+400V', fontsize=7, color='#aaaaaa', ha='right')

# Step 3: Bond formed
draw_y3 = 2.5
ax11.add_patch(FancyBboxPatch((1, draw_y3), 6, 1.0, boxstyle="round,pad=0.02",
               facecolor='#558866', edgecolor='#00ff88', linewidth=2, alpha=0.4))
ax11.text(4, draw_y3+0.5, 'HERMETIC BOND\nGlass-Si-O covalent bond\n(survives decades)',
          ha='center', fontsize=8, color='#00ff88', fontweight='bold')
ax11.text(0.3, draw_y3+0.5, 'Step 3:\nBonded!', fontsize=7, color='#aaaaaa', ha='right')

# Explanation
ax11.text(4, 0.5,
    'CHEMISTRY:\n'
    'Heat mobilizes Na+ in glass.\n'
    'Voltage drives Na+ away from interface.\n'
    'Depletion zone creates huge E-field.\n'
    'E-field pulls glass to Si at atomic level.\n'
    'O from glass bonds with Si -> Si-O-Si bridge.\n\n'
    'RESULT: Hermetic seal lasting decades.\n'
    'Leak rate < 1e-12 atm*cc/s (helium)',
    ha='center', va='top', fontsize=8, color='white',
    bbox=dict(boxstyle='round,pad=0.5', facecolor='#111133', edgecolor='#444'))

ax11.set_xlim(-0.5, 8.5)
ax11.set_ylim(-0.5, 10)
ax11.axis('off')


# ======================================================================
# PANEL 12: HERMETIC LIFETIME -- Leak rate physics
# ======================================================================
ax12 = fig.add_subplot(gs[3, 2], facecolor='#0a0a1a')
ax12.set_title('12. CELL LIFETIME: Leak Rate & Aging', color='#ffaa00',
               fontsize=13, fontweight='bold')

# Helium permeation through glass is the main leak mechanism
# Permeation rate: Q = K * A * (P_ext - P_int) / d
# K = permeability (Arrhenius: K = K0 * exp(-Ea/kT))
# For borosilicate glass, He permeation ~ 1e-12 to 1e-10 cc/s at RT

t_years = np.linspace(0, 30, 500)

# Model: internal pressure change from He permeation
# delta_P = Q * t / V_cell
V_cell = 1e-3  # cc (1 mm^3 MEMS cell volume)
Q_leak = np.array([1e-14, 1e-13, 1e-12])  # cc*atm/s (good, typical, bad)
labels_leak = ['Excellent bond (1e-14)', 'Typical bond (1e-13)', 'Poor bond (1e-12)']
colors_leak = ['#00ff88', '#ffaa00', '#ff4444']

for Q, lab, col in zip(Q_leak, labels_leak, colors_leak):
    delta_P = Q * t_years * 365.25 * 86400 / V_cell  # atm
    # Frequency shift from pressure change: ~500 Hz/Torr * 760 Torr/atm
    freq_shift = delta_P * 500 * 760  # Hz
    frac_shift = freq_shift / RB87_HYPERFINE
    ax12.semilogy(t_years, frac_shift, color=col, linewidth=2, label=lab)

# Spec line
ax12.axhline(1e-10, color='white', linestyle=':', alpha=0.3)
ax12.text(30.5, 1e-10, 'CSAC spec\n(1e-10)', fontsize=7, color='white', va='center')
ax12.axhline(1e-11, color='cyan', linestyle=':', alpha=0.3)
ax12.text(30.5, 1e-11, 'Target\n(1e-11)', fontsize=7, color='cyan', va='center')

ax12.set_xlabel('Time (years)', color='white', fontsize=10)
ax12.set_ylabel('Fractional Frequency Drift', color='white', fontsize=10)
ax12.legend(fontsize=7.5, facecolor='#1a1a2e', edgecolor='#444', labelcolor='white')
ax12.tick_params(colors='gray')
ax12.set_xlim(0, 32)
ax12.grid(True, alpha=0.15, color='gray')
for sp in ax12.spines.values():
    sp.set_edgecolor('#333')

# Arrhenius box
ax12.text(15, 5e-8,
    'LEAK RATE PHYSICS:\n'
    'K(T) = K0 * exp(-Ea / kB*T)\n\n'
    'Ea ~ 0.25 eV for He in glass\n'
    'Higher T -> faster leak\n'
    '(accelerated aging test uses this)\n\n'
    'Anti-permeation coating (Al2O3)\n'
    'reduces K by 100-1000x',
    fontsize=7.5, color='#aaaaaa',
    bbox=dict(boxstyle='round,pad=0.3', facecolor='#111133', edgecolor='#444'))


# ======================================================================
# ROW 5: THE COMPLETE EQUATION CHAIN + Q FACTOR + SENSITIVITY
# ======================================================================

# PANEL 13: Q-FACTOR -- Why atomic resonance beats quartz
ax13 = fig.add_subplot(gs[4, 0], facecolor='#0a0a1a')
ax13.set_title('13. Q-FACTOR: Why Atoms Beat Crystals', color='#00ccff',
               fontsize=13, fontweight='bold')

# Q = f_0 / delta_f  (center frequency / linewidth)
# Higher Q = sharper discriminator = better clock

oscillators = [
    ('Quartz\n(TCXO)', 10e6, 1, '#ff4444'),           # 10 MHz, 1 Hz linewidth
    ('Quartz\n(OCXO)', 10e6, 0.01, '#ff8844'),        # 10 MHz, 10 mHz
    ('Rb CSAC\n(CPT)', 6.835e9, 3e3, '#00ff88'),      # 6.835 GHz, 3 kHz CPT
    ('Rb cell\n(optical)', 377e12, 6e6, '#44aaff'),    # 377 THz, 6 MHz (Doppler)
    ('Cs fountain\n(SI def)', 9.192e9, 1, '#ffaa00'),  # 9.192 GHz, 1 Hz
]

names = [o[0] for o in oscillators]
Qs = [o[1]/o[2] for o in oscillators]
colors_q = [o[3] for o in oscillators]

y_pos = np.arange(len(names))
bars = ax13.barh(y_pos, Qs, color=colors_q, alpha=0.6, edgecolor='white', linewidth=0.8)
ax13.set_yticks(y_pos)
ax13.set_yticklabels(names, fontsize=9, color='white')
ax13.set_xscale('log')
ax13.set_xlabel('Quality Factor Q = f0 / delta_f', color='white', fontsize=10)
ax13.tick_params(colors='gray')
ax13.grid(True, alpha=0.1, color='gray', axis='x')
for sp in ax13.spines.values():
    sp.set_edgecolor('#333')

# Label each bar
for i, (name, f0, df, col) in enumerate(oscillators):
    Q = f0/df
    ax13.text(Q * 1.5, i, f'Q = {Q:.0e}\nf0={f0:.0e} Hz\ndf={df:.0e} Hz',
              fontsize=6.5, color='white', va='center')

ax13.text(1e4, -1,
    'Higher Q = sharper resonance = better frequency discriminator.\n'
    'CSAC CPT: Q ~ 2e6 (modest, but 6.835 GHz center freq compensates).\n'
    'Short-term stability ~ 1/Q * 1/sqrt(tau) -> fundamental limit.',
    fontsize=7.5, color='#aaaaaa',
    bbox=dict(boxstyle='round,pad=0.3', facecolor='#111133', edgecolor='#444'))


# PANEL 14: SENSITIVITY FORMULA
ax14 = fig.add_subplot(gs[4, 1], facecolor='#0a0a1a')
ax14.set_title('14. FUNDAMENTAL STABILITY LIMIT', color='#00ccff',
               fontsize=13, fontweight='bold')

# The shot-noise limited stability for CPT:
# sigma_y(tau) = (delta_nu / nu_0) * (1 / SNR) * (1 / sqrt(tau))
# where SNR = sqrt(eta * R * A_CPT^2 / (2 * e * delta_nu))

# Plot stability vs key parameters
tau_plot = np.logspace(-1, 5, 200)

# Baseline
delta_nu_cpt = 3e3  # 3 kHz CPT linewidth
nu_0 = RB87_HYPERFINE
contrast_cpt = 0.05  # 5% contrast
R_photocurrent = 1e-6  # 1 uA photocurrent -> shot noise

# Shot-noise limited ADEV
# sigma_y = (1/Q) * (1/SNR) * 1/sqrt(tau)
Q_cpt = nu_0 / delta_nu_cpt
SNR_1s = contrast_cpt * np.sqrt(R_photocurrent / (2 * e_charge * delta_nu_cpt))
sigma_shot = 1 / (Q_cpt * SNR_1s * np.sqrt(tau_plot))

# With flicker + drift
sigma_total = np.sqrt(sigma_shot**2 + (5e-12)**2 + (8e-15 * np.sqrt(tau_plot))**2)

ax14.loglog(tau_plot, sigma_shot, color='#44aaff', lw=2, ls='--',
            label='Shot-noise limit')
ax14.loglog(tau_plot, sigma_total, color='#00ff88', lw=3, label='Realistic total')

# Improve contrast
sigma_better = 1 / (Q_cpt * SNR_1s * 3 * np.sqrt(tau_plot))
sigma_better_total = np.sqrt(sigma_better**2 + (3e-12)**2 + (5e-15*np.sqrt(tau_plot))**2)
ax14.loglog(tau_plot, sigma_better_total, color='#ffaa00', lw=2, ls=':',
            label='Improved vapor cell (3x contrast)')

ax14.set_xlabel('Averaging Time tau (s)', color='white', fontsize=10)
ax14.set_ylabel('Allan Deviation', color='white', fontsize=10)
ax14.legend(fontsize=7.5, facecolor='#1a1a2e', edgecolor='#444', labelcolor='white')
ax14.set_xlim(0.1, 1e5)
ax14.set_ylim(1e-13, 1e-8)
ax14.grid(True, alpha=0.15, color='gray')
ax14.tick_params(colors='gray')
for sp in ax14.spines.values():
    sp.set_edgecolor('#333')

# The master formula
ax14.text(1, 3e-9,
    'MASTER FORMULA:\n\n'
    'sigma_y(tau) = (delta_nu / nu_0)\n'
    '             * (1 / SNR_1s)\n'
    '             * (1 / sqrt(tau))\n\n'
    'To improve:\n'
    '  1. Narrow CPT line (better buffer gas)\n'
    '  2. Higher contrast (better cell, coatings)\n'
    '  3. Lower noise (better photodetector)\n'
    '  4. Higher Q (use optical transition?)',
    fontsize=7.5, color='#00ff88',
    bbox=dict(boxstyle='round,pad=0.4', facecolor='#0a1a0a', edgecolor='#00ff88'))


# PANEL 15: THE FULL CHAIN -- Schrodinger to Nanoseconds
ax15 = fig.add_subplot(gs[4, 2], facecolor='#0a0a1a')
ax15.set_title('15. THE FULL CHAIN: Theory to Clock', color='#00ccff',
               fontsize=13, fontweight='bold')

chain = [
    ('QUANTUM\nMECHANICS', 'Schrodinger equation\n-> energy levels of Rb-87\n-> hyperfine splitting', '#ff8844'),
    ('ATOMIC\nPHYSICS', 'Nuclear spin (I=3/2) couples\nwith electron spin (J=1/2)\n-> F=1,2 ground states', '#ff4444'),
    ('QUANTUM\nOPTICS', 'Lambda system + 2 laser fields\n-> coherent population trapping\n-> DARK STATE', '#00ff88'),
    ('LASER\nPHYSICS', 'VCSEL current modulation\n-> Bessel sidebands\n-> 2 fields from 1 laser', '#aa44ff'),
    ('STATISTICAL\nMECHANICS', 'Rb vapor pressure (85C)\n+ N2 buffer gas (Dicke)\n-> optimal signal', '#44aaff'),
    ('MATERIALS\nSCIENCE', 'Anodic bonding (Si-O-Si)\n+ anti-permeation coating\n-> hermetic MEMS cell', '#FFD700'),
    ('CONTROL\nTHEORY', 'PID thermal control (+/- 0.1C)\n+ frequency lock loop\n-> stable output', '#ff8844'),
    ('SIGNAL\nPROCESSING', 'Lock-in detection of CPT peak\n-> error signal -> correction\n-> Allan deviation ~2e-10', '#ffaa00'),
    ('TIMING\nOUTPUT', '6,834,682,610.904 Hz\n-> count cycles -> 1 PPS\n-> nanosecond navigation', '#00ff88'),
]

y_start = 8.5
for i, (title, desc, col) in enumerate(chain):
    y = y_start - i * 0.95
    # Box
    rect = FancyBboxPatch((0.3, y - 0.35), 1.8, 0.7, boxstyle="round,pad=0.05",
                           facecolor=col, edgecolor='white', linewidth=1.2, alpha=0.3)
    ax15.add_patch(rect)
    ax15.text(1.2, y, title, ha='center', va='center', fontsize=7,
              color='white', fontweight='bold')
    ax15.text(2.4, y, desc, ha='left', va='center', fontsize=6.5, color=col)
    # Arrow to next
    if i < len(chain) - 1:
        ax15.annotate('', xy=(1.2, y - 0.4), xytext=(1.2, y - 0.6),
                      arrowprops=dict(arrowstyle='->', color='white', lw=1.5))

ax15.set_xlim(-0.2, 8)
ax15.set_ylim(-0.5, 9.5)
ax15.axis('off')


# ──────────────────────────────────────────────────────────────────
# BOTTOM TEXT
# ──────────────────────────────────────────────────────────────────
fig.text(0.5, 0.005,
    'THEORY CHAIN:  Schrodinger Eq -> Rb-87 hyperfine (6.835 GHz) -> Lambda system -> '
    'CPT dark state |D> = (Omega_2|1> - Omega_1|2>)/N -> '
    'VCSEL sidebands (Bessel) -> Buffer gas (Dicke) -> PID thermal -> '
    'Lock-in detection -> Allan deviation 2e-10/sqrt(tau) -> Nanosecond timing',
    ha='center', va='bottom', fontsize=7.5, color='#888888',
    bbox=dict(boxstyle='round,pad=0.4', facecolor='#111122', edgecolor='#333'),
    fontfamily='monospace')


plt.savefig('csac_theory.png', dpi=150, facecolor=fig.get_facecolor(),
            bbox_inches='tight')
plt.show()
print("Saved to csac_theory.png")
