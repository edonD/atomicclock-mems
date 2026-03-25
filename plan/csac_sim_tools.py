"""
SIMULATION-FIRST BUILD PLAN: CSAC Vapor Cell Core
Every step simulated before touching hardware.
Each block lists the EXACT software tool, what you simulate, and what you learn.

10 simulation blocks, each validatable on a laptop/workstation.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from matplotlib.patches import FancyBboxPatch

fig = plt.figure(figsize=(24, 72), facecolor='#0a0a1a')

gs = GridSpec(12, 1, figure=fig, hspace=0.05,
              left=0.03, right=0.97, top=0.993, bottom=0.002)

fig.text(0.5, 0.998,
    'SIMULATE BEFORE YOU BUILD: Complete CSAC Simulation Roadmap',
    ha='center', fontsize=22, fontweight='bold', color='white')
fig.text(0.5, 0.9955,
    'Every physics layer simulated on your computer  |  Exact tools  |  What you learn before spending EUR 1',
    ha='center', fontsize=12, color='#00ff88')


def sim_block(gs_slot, num, title, color, tool_name, tool_type, tool_cost,
              what_you_simulate, what_you_learn, input_params, output_you_get,
              python_alternative, validation_check, time_estimate):
    ax = fig.add_subplot(gs_slot, facecolor='#0d0d20')
    for sp in ax.spines.values():
        sp.set_edgecolor(color)
        sp.set_linewidth(2)
    ax.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)

    # ── Header ──
    ax.add_patch(FancyBboxPatch((0.003, 0.82), 0.994, 0.175,
                 boxstyle="round,pad=0.008", facecolor=color, alpha=0.12,
                 edgecolor='none', transform=ax.transAxes))

    ax.text(0.01, 0.96, f'SIM {num}', fontsize=15, fontweight='bold',
            color='#0d0d20', transform=ax.transAxes,
            bbox=dict(boxstyle='round,pad=0.3', facecolor=color, edgecolor='none'))
    ax.text(0.09, 0.96, title, fontsize=15, fontweight='bold', color=color,
            transform=ax.transAxes)
    ax.text(0.70, 0.96, f'Time: {time_estimate}', fontsize=11, color='white',
            transform=ax.transAxes)

    # ── Tool Box ──
    ax.add_patch(FancyBboxPatch((0.01, 0.60), 0.32, 0.22,
                 boxstyle="round,pad=0.01", facecolor='#111144', edgecolor=color,
                 linewidth=1.5, transform=ax.transAxes))
    ax.text(0.03, 0.80, 'PRIMARY TOOL:', fontsize=10, color=color,
            fontweight='bold', transform=ax.transAxes)
    ax.text(0.03, 0.755, tool_name, fontsize=13, color='white',
            fontweight='bold', transform=ax.transAxes)
    ax.text(0.03, 0.70, f'Type: {tool_type}', fontsize=9, color='#888888',
            transform=ax.transAxes)
    ax.text(0.03, 0.67, f'Cost: {tool_cost}', fontsize=9, color='#FFD700',
            transform=ax.transAxes)
    ax.text(0.03, 0.63, f'Python alt: {python_alternative}', fontsize=8,
            color='#44aaff', transform=ax.transAxes)

    # ── What you simulate ──
    ax.text(0.35, 0.80, 'WHAT YOU SIMULATE:', fontsize=10, color='#ffaa00',
            fontweight='bold', transform=ax.transAxes)
    ax.text(0.35, 0.75, what_you_simulate, fontsize=9, color='white',
            transform=ax.transAxes, va='top')

    # ── What you learn ──
    ax.text(0.70, 0.80, 'WHAT YOU LEARN:', fontsize=10, color='#00ff88',
            fontweight='bold', transform=ax.transAxes)
    ax.text(0.70, 0.75, what_you_learn, fontsize=9, color='#00ff88',
            transform=ax.transAxes, va='top')

    # ── Input parameters ──
    ax.text(0.01, 0.55, 'INPUT PARAMETERS:', fontsize=9, color='#ff8844',
            fontweight='bold', transform=ax.transAxes)
    ax.text(0.01, 0.50, input_params, fontsize=8.5, color='#ccaa88',
            transform=ax.transAxes, va='top', fontfamily='monospace')

    # ── Output ──
    ax.text(0.55, 0.55, 'OUTPUT YOU GET:', fontsize=9, color='#44aaff',
            fontweight='bold', transform=ax.transAxes)
    ax.text(0.55, 0.50, output_you_get, fontsize=8.5, color='#88aacc',
            transform=ax.transAxes, va='top', fontfamily='monospace')

    # ── Validation ──
    ax.text(0.01, 0.12, 'VALIDATION CHECK:', fontsize=9, color='#FFD700',
            fontweight='bold', transform=ax.transAxes)
    ax.text(0.01, 0.07, validation_check, fontsize=9, color='#FFD700',
            transform=ax.transAxes, va='top')

    # Arrow to next
    ax.annotate('', xy=(0.5, 0.005), xytext=(0.5, 0.04),
                xycoords='axes fraction', textcoords='axes fraction',
                arrowprops=dict(arrowstyle='->', color='white', lw=2))
    return ax


# ═══════════════════════════════════════════════════════════════
# OVERVIEW PANEL
# ═══════════════════════════════════════════════════════════════
ax0 = fig.add_subplot(gs[0], facecolor='#0d0d20')
for sp in ax0.spines.values():
    sp.set_edgecolor('#00ccff')
    sp.set_linewidth(2)
ax0.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)

ax0.text(0.50, 0.90, 'THE SIMULATION STACK: 10 Layers, Bottom to Top',
         ha='center', fontsize=16, fontweight='bold', color='#00ccff',
         transform=ax0.transAxes)

stack = [
    ('SIM 1', 'Rb-87 Atomic Structure', 'QuTiP / Python', '#ff8844'),
    ('SIM 2', 'CPT Dark State & Resonance', 'QuTiP / Python', '#ff4444'),
    ('SIM 3', 'VCSEL Sideband Spectrum', 'Python + SciPy', '#cc44ff'),
    ('SIM 4', 'Buffer Gas & Line Shape', 'Python + SciPy', '#44aaff'),
    ('SIM 5', 'Vapor Cell Geometry (MEMS)', 'COMSOL / FreeCAD + Elmer', '#888888'),
    ('SIM 6', 'Thermal Management', 'COMSOL / OpenFOAM', '#FFD700'),
    ('SIM 7', 'Optical Beam Propagation', 'Lumerical / Python (ABCD)', '#ff4444'),
    ('SIM 8', 'Feedback Control Loop', 'MATLAB Simulink / Python', '#aa44ff'),
    ('SIM 9', 'Allan Deviation & Clock Perf', 'Python + Allantools', '#00ff88'),
    ('SIM 10', 'Full System Integration', 'Python (all combined)', '#00ccff'),
]

for i, (sim_id, name, tool, col) in enumerate(stack):
    y = 0.08 + i * 0.075
    ax0.add_patch(FancyBboxPatch((0.10, y), 0.80, 0.06,
                  boxstyle="round,pad=0.005", facecolor=col, edgecolor='white',
                  linewidth=1, alpha=0.25, transform=ax0.transAxes))
    ax0.text(0.12, y + 0.03, sim_id, fontsize=9, color=col, fontweight='bold',
             va='center', transform=ax0.transAxes)
    ax0.text(0.20, y + 0.03, name, fontsize=10, color='white', fontweight='bold',
             va='center', transform=ax0.transAxes)
    ax0.text(0.65, y + 0.03, tool, fontsize=9, color='#888888',
             va='center', transform=ax0.transAxes)
    if i < len(stack) - 1:
        ax0.annotate('', xy=(0.50, y + 0.065), xytext=(0.50, y + 0.06),
                     xycoords='axes fraction', textcoords='axes fraction',
                     arrowprops=dict(arrowstyle='->', color='white', lw=1, alpha=0.4))


# ═══════════════════════════════════════════════════════════════
# SIM 1: ATOMIC STRUCTURE
# ═══════════════════════════════════════════════════════════════
sim_block(gs[1], 1,
    'Rb-87 Atomic Structure & Energy Levels',
    '#ff8844',
    'QuTiP (Python)', 'Open-source quantum simulation', 'FREE',
    'Build the Rb-87 energy level structure:\n'
    '- Ground state: 5S1/2, F=1 (3 substates) and F=2 (5 substates)\n'
    '- Excited state: 5P1/2, F\'=1 and F\'=2\n'
    '- Hyperfine splitting: 6.834682611 GHz\n'
    '- Zeeman sublevels in magnetic field\n'
    '- Transition dipole matrix elements\n'
    '- Selection rules for sigma+, sigma-, pi polarization',
    'Whether your chosen mF=0 to mF=0\n'
    'transition is field-independent\n'
    '(first-order Zeeman cancellation).\n'
    'This confirms the "clock transition"\n'
    'is the right one to use.\n'
    'Also: absorption cross-sections\n'
    'at 795 nm for cell design.',
    'Rb-87 nuclear spin: I = 3/2\n'
    'Electron spin:      J = 1/2 (ground), 1/2 (5P1/2)\n'
    'Hyperfine constant:  A_hfs = 3417.341 MHz (5S1/2)\n'
    'D1 wavelength:       794.979 nm\n'
    'D1 natural linewidth: Gamma = 2*pi * 5.75 MHz\n'
    'Lande g-factor:      gF(F=1) = -1/2, gF(F=2) = +1/2',
    'Energy level diagram (validated against NIST ASD)\n'
    'Transition strengths: d_ij matrix\n'
    'Zeeman shift vs B-field plot\n'
    'Clock transition identification:\n'
    '  |F=1,mF=0> <-> |F=2,mF=0>\n'
    '  Quadratic Zeeman: 575 Hz/G^2',
    'QuTiP (qutip.org) -- pip install qutip',
    'Compare your calculated hyperfine splitting to NIST value: 6,834,682,610.904 Hz.\n'
    'If your simulation matches to 9 digits, your atomic model is correct.',
    '1-2 days')


# ═══════════════════════════════════════════════════════════════
# SIM 2: CPT DARK STATE
# ═══════════════════════════════════════════════════════════════
sim_block(gs[2], 2,
    'CPT Dark State & Resonance Signal',
    '#ff4444',
    'QuTiP + custom Python', 'Open-source + custom code', 'FREE',
    'Solve the 3-level Lambda system density matrix:\n'
    '- Build 3x3 Hamiltonian (rotating frame, RWA)\n'
    '- Add Lindblad dissipators: spontaneous decay (Gamma),\n'
    '  ground-state decoherence (gamma_12), transit relaxation\n'
    '- Solve for steady state: d(rho)/dt = 0\n'
    '- Extract absorption: Im(rho_13) vs Raman detuning\n'
    '- Sweep parameters: laser power, detuning, decoherence\n'
    '- Verify dark state |D> = (Omega_2|1> - Omega_1|2>)/N',
    'The CPT signal you EXPECT to see:\n'
    '- Linewidth (target <5 kHz)\n'
    '- Contrast (target >3%)\n'
    '- Optimal laser power\n'
    '- Sensitivity to decoherence rate\n'
    'THIS IS THE CORE PREDICTION.\n'
    'If the sim says contrast is too low,\n'
    'redesign before fabrication.',
    'Omega_1, Omega_2: Rabi frequencies (set by laser power)\n'
    'Gamma:       5.75 MHz (D1 natural linewidth)\n'
    'gamma_12:    0.3-3 kHz (ground decoherence, depends on\n'
    '             buffer gas, cell size, wall coatings)\n'
    'delta_1:     one-photon detuning (scan -500 to +500 MHz)\n'
    'delta_R:     Raman detuning (scan -50 to +50 kHz)',
    'CPT resonance curve: transmission vs delta_R\n'
    'Contrast vs laser power (optimum curve)\n'
    'Linewidth vs gamma_12 (decoherence scan)\n'
    'Dark state population vs parameters\n'
    'Discriminator slope: dSignal/dFrequency\n'
    'Expected short-term stability estimate',
    'QuTiP mesolve() or steadystate() -- all in Python',
    'Compare your CPT linewidth and contrast to published CSAC data:\n'
    'Microchip SA65: ~3-5 kHz linewidth, 3-8% contrast.\n'
    'If your simulation is within 2x of these, your model is valid.',
    '3-5 days')


# ═══════════════════════════════════════════════════════════════
# SIM 3: VCSEL SIDEBAND
# ═══════════════════════════════════════════════════════════════
sim_block(gs[3], 3,
    'VCSEL Modulation & Sideband Spectrum',
    '#cc44ff',
    'Python + SciPy', 'Pure Python', 'FREE',
    'Model the VCSEL current modulation and resulting optical spectrum:\n'
    '- E(t) = E0 * exp(i*w_c*t + i*beta*sin(w_m*t))\n'
    '- Jacobi-Anger expansion: sum of Bessel functions J_n(beta)\n'
    '- Sweep modulation index beta from 0 to 3\n'
    '- Calculate power in each sideband: |J_n(beta)|^2\n'
    '- Find optimal beta that maximizes J_1 (CPT sidebands)\n'
    '- Include AM (intensity modulation) alongside FM\n'
    '- Model the actual VCSEL: P(I) and lambda(I) curves',
    'Optimal modulation index beta\n'
    '(typically beta ~ 1.5-2.0)\n'
    'Power distribution across sidebands\n'
    'Residual carrier suppression needed\n'
    'AM index and its effect on CPT signal\n'
    'RF power needed at 3.417 GHz',
    'VCSEL wavelength:     794.979 nm\n'
    'Modulation frequency: f_m = 3,417,341,305.452 Hz\n'
    'Modulation index:     beta = 0 to 3 (sweep)\n'
    'VCSEL tuning coeff:   ~0.3 nm/mA (FM), ~0.5 mW/mA (AM)\n'
    'Bias current:         ~2-4 mA (typical)\n'
    'RF modulation power:  ~0 to +10 dBm',
    'Sideband power spectrum: |J_n(beta)|^2 for n=-5..+5\n'
    'Optimal beta for max J_1 * J_{-1} product\n'
    'Carrier-to-sideband power ratio\n'
    'Total optical power budget\n'
    'Residual AM index (alpha_AM)',
    'scipy.special.jv() for Bessel functions, numpy for FFT',
    'Bessel function J_1(1.84) = 0.582 (maximum of J_1).\n'
    'Optimal beta is near 1.84 for maximizing first sideband.\n'
    'Verify: J_0(1.84) = 0.327, J_1(1.84) = 0.582, J_2(1.84) = 0.310.',
    '1-2 days')


# ═══════════════════════════════════════════════════════════════
# SIM 4: BUFFER GAS
# ═══════════════════════════════════════════════════════════════
sim_block(gs[4], 4,
    'Buffer Gas Physics & Line Shape Optimization',
    '#44aaff',
    'Python + SciPy + published data', 'Pure Python', 'FREE',
    'Model the N2 buffer gas effects on CPT resonance:\n'
    '- Dicke narrowing: transit-time linewidth vs pressure\n'
    '- Pressure broadening: gamma_pressure = k * P_N2\n'
    '- Pressure shift: delta_shift = s * P_N2 (shifts center freq)\n'
    '- Optimal pressure: minimize total linewidth\n'
    '- Temperature dependence of all parameters\n'
    '- Rb vapor density vs temperature (Antoine equation)\n'
    '- Rb-N2 collision cross-sections from literature\n'
    '- Diffusion coefficient: D = D0 * (T/T0)^1.5 * (P0/P)',
    'OPTIMAL N2 PRESSURE (Torr)\n'
    'for your specific cell geometry.\n'
    'This tells you exactly how much\n'
    'N2 to put in during filling.\n'
    'Also: expected pressure shift\n'
    '(need to know for locking)\n'
    'and temperature coefficient.',
    'Cell diameter:    d = 1-2 mm (your cavity size)\n'
    'Cell length:      L = 1 mm (cavity depth)\n'
    'Temperature:      T = 85 C (358 K)\n'
    'Rb mass:          87 u\n'
    'N2 mass:          28 u\n'
    'Rb-N2 broadening: k = 10.8 kHz/Torr (from literature)\n'
    'Rb-N2 shift:      s = -6.7 kHz/Torr (from literature)\n'
    'Rb diffusion in N2: D0 = 0.15 cm^2/s at 1 atm, 300K',
    'Optimal N2 pressure: P_opt (typically 30-75 Torr)\n'
    'CPT linewidth at P_opt (kHz)\n'
    'Pressure shift at P_opt (kHz)\n'
    'Temperature coefficient of shift (Hz/C)\n'
    'Rb number density at 85C: ~2e17 m^-3\n'
    'Absorption length: alpha * L product',
    'All Python. Use published Rb-N2 collisional data from Vanier & Audoin textbook.',
    'Published optimal pressure for ~1mm CSAC cells: 30-75 Torr N2.\n'
    'Your simulation should land in this range.\n'
    'Pressure shift: ~200-500 kHz total (compensated by tuning modulation freq).',
    '2-3 days')


# ═══════════════════════════════════════════════════════════════
# SIM 5: MEMS GEOMETRY
# ═══════════════════════════════════════════════════════════════
sim_block(gs[5], 5,
    'Vapor Cell Geometry & MEMS Structure',
    '#888888',
    'COMSOL Multiphysics (or Elmer FEM + FreeCAD)', 'FEM simulation',
    'COMSOL: EUR 3-5k/yr academic | Elmer: FREE',
    'Design the physical MEMS cell geometry:\n'
    '- Draw 3D model: glass-Si-glass stack\n'
    '- Cavity dimensions: diameter, depth, wall thickness\n'
    '- Stress analysis of anodic bond interface\n'
    '- Thermal expansion mismatch: Si vs borosilicate glass\n'
    '  (CTE: Si=2.6, Borofloat33=3.25 ppm/K)\n'
    '- Mechanical resonance frequencies (avoid vibration modes)\n'
    '- DRIE etch profile simulation (sidewall angle)\n'
    '- Optical path: window thickness effect on beam',
    'Cell dimensions that survive\n'
    'thermal cycling (-40 to +80C)\n'
    'without cracking the bond.\n'
    'Optimal cavity depth for your\n'
    'target absorption (alpha*L).\n'
    'Mask layout dimensions for GDS-II.',
    'Materials:\n'
    '  Si:    E=170 GPa, nu=0.28, CTE=2.6 ppm/K\n'
    '  Glass: E=63 GPa, nu=0.20, CTE=3.25 ppm/K\n'
    '  Pt:    E=168 GPa, nu=0.38, rho=21450 kg/m3\n'
    'Geometry:\n'
    '  Cavity diameter: 1.0-2.0 mm (parameter sweep)\n'
    '  Cavity depth:    0.5-1.5 mm (parameter sweep)\n'
    '  Glass thickness: 0.3-0.5 mm\n'
    '  Si thickness:    0.5-1.5 mm',
    'Optimized cavity dimensions (mm)\n'
    'Stress map at bond interface (MPa)\n'
    'Max stress at thermal cycling extremes\n'
    'Safety factor vs bond strength (~10 MPa)\n'
    'Resonance frequencies (Hz) -- avoid excitation\n'
    'GDS-II compatible mask layout',
    'FreeCAD (free) + Elmer FEM (free) for structural analysis.\n'
    'Or: KLayout (free, open-source) for mask design only.',
    'Bond interface stress at -40C should be < 3 MPa (safety factor 3x).\n'
    'Cavity depth of ~1mm is standard for CSAC cells.\n'
    'Published CSAC cells: 1-2mm diameter, 0.5-1.5mm deep.',
    '1-2 weeks')


# ═══════════════════════════════════════════════════════════════
# SIM 6: THERMAL
# ═══════════════════════════════════════════════════════════════
sim_block(gs[6], 6,
    'Thermal Management & Heater Design',
    '#FFD700',
    'COMSOL (or OpenFOAM / Elmer + Python)', 'FEM thermal simulation',
    'COMSOL: EUR 3-5k/yr | OpenFOAM/Elmer: FREE',
    'Simulate the complete thermal system:\n'
    '- Pt heater trace layout: serpentine, dual-zone\n'
    '- Steady-state temperature distribution at 85C\n'
    '- Gradient across cavity (target < 0.1C)\n'
    '- Power consumption: P_heater at different T_ambient\n'
    '- Transient response: startup time, PID settling\n'
    '- Vacuum insulation model: radiation + conduction\n'
    '  through suspension beams\n'
    '- External temperature shock: -40C to +80C step response',
    'Heater trace design (geometry)\n'
    'Power budget: mW to maintain 85C\n'
    'in vacuum at each T_ambient.\n'
    'Thermal time constant (for PID tuning).\n'
    'Temperature uniformity across cavity.\n'
    'Worst-case gradient location.',
    'Pt resistivity:    rho = 1.06e-7 ohm*m\n'
    'Pt film thickness: 200 nm\n'
    'Pt trace width:    10-50 um\n'
    'Pt TCR:            alpha = 3.9e-3 /K\n'
    'Vacuum pressure:   0.01 mbar (molecular flow)\n'
    'Suspension beam:   Si, 50um wide, 500um long, 50um thick\n'
    'Stefan-Boltzmann:  sigma = 5.67e-8 W/m^2/K^4\n'
    'Emissivity Si/glass: ~0.4-0.7',
    'Temperature map (3D, steady-state)\n'
    'Power vs T_ambient curve (mW vs C)\n'
    'Startup transient: T(t) curve\n'
    'PID response to -20C shock\n'
    'Heater resistance at 85C (Ohms)\n'
    'Optimal trace width and spacing',
    'Python + scipy.integrate for transient ODE.\n'
    'OpenFOAM for full 3D thermal FEM (free).\n'
    'Or: simple lumped-parameter model in Python.',
    'Heater power at T_amb=25C should be ~50-70 mW in vacuum.\n'
    'Without vacuum: ~1-2 W (10x more). This validates vacuum packaging need.\n'
    'Published CSAC: 55 mW heater, <120 mW total system.',
    '1-2 weeks')


# ═══════════════════════════════════════════════════════════════
# SIM 7: OPTICS
# ═══════════════════════════════════════════════════════════════
sim_block(gs[7], 7,
    'Optical Beam Propagation Through Cell',
    '#ff4444',
    'Python (ABCD matrix) or Lumerical FDTD', 'Gaussian optics / wave optics',
    'Python: FREE | Lumerical: EUR 5-15k/yr',
    'Model the laser beam path through the MEMS stack:\n'
    '- VCSEL beam profile: divergence angle, waist size\n'
    '- Propagation through QWP, bottom glass, cavity, top glass\n'
    '- Gaussian beam ABCD matrix at each interface\n'
    '- Beam diameter at cavity center (must fill cavity)\n'
    '- Reflections at each glass-air and glass-Si interface\n'
    '- Anti-reflection coating design (optional)\n'
    '- Etalon effects from parallel glass surfaces\n'
    '- Photodetector collection efficiency',
    'Whether your VCSEL beam fills the\n'
    'cavity properly (not too wide, not\n'
    'too narrow). Optimal VCSEL-to-cell\n'
    'distance. Etalon fringes that could\n'
    'corrupt the CPT signal. Total\n'
    'optical power budget: laser -> detector.',
    'VCSEL beam divergence:  ~15 deg half-angle\n'
    'VCSEL beam waist:       ~3 um at facet\n'
    'VCSEL wavelength:       795 nm\n'
    'VCSEL power:            ~1-2 mW\n'
    'Glass refractive index: n = 1.47 (Borofloat 33)\n'
    'Si refractive index:    n = 3.42 (but cavity is air)\n'
    'Glass thickness:        0.3-0.5 mm\n'
    'Cavity length:          1 mm',
    'Beam diameter at cavity center (um)\n'
    'Total transmission: VCSEL to detector (%)\n'
    'Etalon fringe period (MHz) and contrast\n'
    'Optimal VCSEL-to-cell spacing (mm)\n'
    'Photodetector signal level (uW)\n'
    'Beam profile at detector plane',
    'Python ABCD Gaussian beam propagation (10 lines of code).\n'
    'RayTransferMatrix from sympy.physics.optics, or just numpy.',
    'Photodetector should receive ~10-100 uW with ~1 mW VCSEL.\n'
    'Beam diameter in cavity: ~0.3-1.0 mm (should fill most of cavity).\n'
    'Etalon fringes should be >10x wider than CPT linewidth (otherwise problem).',
    '2-3 days')


# ═══════════════════════════════════════════════════════════════
# SIM 8: CONTROL LOOP
# ═══════════════════════════════════════════════════════════════
sim_block(gs[8], 8,
    'Feedback Control Loop (Frequency Lock)',
    '#aa44ff',
    'Python + scipy (or MATLAB Simulink)', 'Control systems simulation',
    'Python: FREE | Simulink: EUR 2-4k/yr',
    'Simulate the complete frequency lock loop:\n'
    '- Local oscillator (LO) at 3.417 GHz: model phase noise\n'
    '- Frequency modulation (dithering) across CPT peak\n'
    '- Lock-in detection: demodulate at dither frequency\n'
    '- Error signal extraction: S-curve (discriminator)\n'
    '- PID controller: P, I, D gains -> correction voltage\n'
    '- Closed-loop response: lock acquisition, settling time\n'
    '- Disturbance rejection: temperature step, vibration\n'
    '- Loop bandwidth optimization (fast enough but not noisy)',
    'PID gains that give stable lock.\n'
    'Loop bandwidth (Hz).\n'
    'Lock acquisition time (ms).\n'
    'Sensitivity to temperature and\n'
    'vibration disturbances.\n'
    'Whether the loop can recover\n'
    'from a momentary unlock.',
    'CPT peak: from SIM 2 output (contrast, linewidth)\n'
    'LO phase noise: -80 dBc/Hz at 1 kHz offset (typical)\n'
    'Dither frequency: 1-10 kHz\n'
    'Dither depth: 100-500 Hz\n'
    'Loop filter bandwidth: 10-100 Hz\n'
    'PID gains: Kp, Ki, Kd (swept to optimize)\n'
    'Temperature disturbance: 1C step',
    'Lock-in error signal (S-curve)\n'
    'Closed-loop frequency stability (Hz)\n'
    'PID gains: Kp, Ki, Kd (optimized)\n'
    'Lock acquisition transient\n'
    'Bode plot: open-loop gain + phase margin\n'
    'Step response to 1C temperature change',
    'Python control library: pip install control (or python-control).\n'
    'scipy.signal for Bode plots, step response.',
    'Loop bandwidth ~10-50 Hz is typical for CSAC.\n'
    'Phase margin > 45 degrees for stability.\n'
    'Lock acquisition < 1 second.',
    '3-5 days')


# ═══════════════════════════════════════════════════════════════
# SIM 9: ALLAN DEVIATION
# ═══════════════════════════════════════════════════════════════
sim_block(gs[9], 9,
    'Allan Deviation & Clock Performance Prediction',
    '#00ff88',
    'Python + Allantools', 'Open-source clock analysis', 'FREE (pip install allantools)',
    'Predict your clock\'s stability from the simulated parameters:\n'
    '- Short-term: shot-noise limited ADEV = (dv/v0) * 1/(SNR*sqrt(tau))\n'
    '- Medium-term: flicker floor from temperature sensitivity\n'
    '- Long-term: drift from cell aging (He permeation model)\n'
    '- Generate synthetic clock noise time series\n'
    '- Compute Allan deviation from simulated data\n'
    '- Compare to published CSAC specs\n'
    '- Sensitivity analysis: which parameter matters most?',
    'Your PREDICTED clock stability.\n'
    'Before building anything, you\'ll know:\n'
    '- Expected ADEV at 1s, 100s, 1 day\n'
    '- Which parameter limits performance\n'
    '- Whether your design meets the\n'
    '  ~1e-10 CSAC target\n'
    '- What to improve if it does not.',
    'From SIM 2: CPT linewidth (kHz), contrast (%)\n'
    'From SIM 3: optical power at detector (uW)\n'
    'From SIM 6: temperature stability (C)\n'
    'From SIM 4: temp coefficient of freq (Hz/C)\n'
    'He leak rate model: Q = 1e-13 cc*atm/s\n'
    'Cell volume: V = 1e-3 cc\n'
    'Pressure shift coefficient: -6.7 kHz/Torr',
    'Allan deviation plot: sigma_y(tau) from 0.1s to 1 day\n'
    'Noise breakdown: white FM + flicker + drift\n'
    'Parameter sensitivity: d(ADEV)/d(parameter)\n'
    'Predicted holdover performance:\n'
    '  time error after 1h, 8h, 24h\n'
    'Position error equivalent (x 300m/us)',
    'pip install allantools. Also: pip install colorednoise for noise generation.',
    'Target: ADEV < 3e-10 at tau=1s, < 1e-11 at tau=1000s.\n'
    'Published Microchip SA65: 2.5e-10 at 1s.\n'
    'If your prediction is within 3x of this, design is viable.',
    '2-4 days')


# ═══════════════════════════════════════════════════════════════
# SIM 10: FULL SYSTEM
# ═══════════════════════════════════════════════════════════════
sim_block(gs[10], 10,
    'Full System Integration Simulation',
    '#00ccff',
    'Python (combining all SIMs)', 'Custom integration', 'FREE',
    'Connect ALL simulations into one end-to-end model:\n'
    '- VCSEL -> sidebands (SIM 3) -> through optics (SIM 7)\n'
    '  -> into Rb vapor (SIM 2+4) at temperature from (SIM 6)\n'
    '  -> CPT signal -> lock loop (SIM 8) -> clock output\n'
    '  -> Allan deviation (SIM 9)\n'
    '- Run Monte Carlo: vary all parameters within tolerances\n'
    '- Find the DESIGN SPACE: which combinations work?\n'
    '- Identify the CRITICAL PARAMETER (one that matters most)\n'
    '- Generate a SPEC SHEET for your vapor cell core\n'
    '- Create the GO/NO-GO decision: is this worth building?',
    'FINAL ANSWER: Is this design viable?\n'
    'Predicted performance spec sheet.\n'
    'Critical parameter identified.\n'
    'Tolerance analysis: how much can\n'
    'each parameter vary before failure?\n'
    'Monte Carlo yield estimate.\n'
    'Decision: GO to fabrication or REDESIGN.',
    'ALL parameters from SIMs 1-9 combined.\n'
    'Add manufacturing tolerances:\n'
    '  Cavity depth: +/- 5%\n'
    '  N2 pressure:  +/- 20%\n'
    '  Rb amount:    +/- 50%\n'
    '  Glass thickness: +/- 10%\n'
    '  Pt resistance: +/- 10%\n'
    '  Bonding temp:  +/- 10C\n'
    'Run 1000+ Monte Carlo iterations.',
    'System-level performance prediction\n'
    'Yield estimate: % of cells that work\n'
    'Sensitivity ranking: which parameter\n'
    '  matters most (Pareto chart)\n'
    'GO/NO-GO recommendation\n'
    'Complete design document for fab',
    'All Python. No commercial tools needed for integration.',
    'If >50% of Monte Carlo runs meet ADEV < 5e-10 at 1s,\n'
    'the design is worth fabricating. If <20%, redesign.\n'
    'The critical parameter is almost always: gamma_12 (ground-state decoherence)\n'
    'which depends on cell cleanliness (contamination).',
    '1-2 weeks')


# ═══════════════════════════════════════════════════════════════
# SUMMARY
# ═══════════════════════════════════════════════════════════════
ax_sum = fig.add_subplot(gs[11], facecolor='#0d0d20')
for sp in ax_sum.spines.values():
    sp.set_edgecolor('#00ff88')
    sp.set_linewidth(2)
ax_sum.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)

ax_sum.text(0.50, 0.90, 'TOOL SUMMARY: Everything You Need to Install',
            ha='center', fontsize=16, fontweight='bold', color='#00ff88',
            transform=ax_sum.transAxes)

tools_summary = (
    'FREE TOOLS (install today):\n'
    '  pip install qutip numpy scipy matplotlib allantools colorednoise sympy\n'
    '  KLayout (klayout.de) -- FREE open-source mask/GDS-II editor\n'
    '  FreeCAD (freecad.org) -- FREE 3D CAD for cell geometry\n'
    '  Elmer FEM (elmerfem.org) -- FREE open-source FEM solver (thermal + structural)\n'
    '  OpenFOAM (openfoam.org) -- FREE CFD/thermal simulation\n'
    '  Python control library: pip install control\n'
    '  Jupyter Notebook: pip install jupyterlab\n\n'
    'COMMERCIAL TOOLS (if budget allows):\n'
    '  COMSOL Multiphysics -- EUR 3-5k/yr academic license (SIM 5, 6)\n'
    '    Modules needed: Heat Transfer, Structural Mechanics, AC/DC\n'
    '    STRONGLY recommended for thermal + stress simulation\n'
    '  MATLAB + Simulink -- EUR 2-4k/yr (SIM 8, optional -- Python works)\n'
    '  Lumerical FDTD -- EUR 5-15k/yr (SIM 7, optional -- ABCD in Python works)\n\n'
    'MINIMUM VIABLE SETUP (EUR 0):\n'
    '  Python + QuTiP + SciPy + Allantools + KLayout + FreeCAD + Elmer = EVERYTHING\n'
    '  You can do ALL 10 simulations with only free/open-source tools.\n'
    '  COMSOL is nice-to-have but not required for proof of concept.\n\n'
    'TIMELINE:  6-10 weeks for all 10 simulations\n'
    'COST:      EUR 0 (free tools) to EUR 5k (with COMSOL)\n'
    'OUTPUT:    Complete design document, spec sheet, GO/NO-GO decision\n'
    '           BEFORE spending any money on fabrication.'
)

ax_sum.text(0.50, 0.50, tools_summary, ha='center', va='center', fontsize=11,
            color='white', fontfamily='monospace', transform=ax_sum.transAxes,
            bbox=dict(boxstyle='round,pad=0.6', facecolor='#111133',
                      edgecolor='#00ff88', linewidth=2))


plt.savefig('csac_sim_tools.png', dpi=110, facecolor=fig.get_facecolor(),
            bbox_inches='tight')
plt.show()
print("Saved to csac_sim_tools.png")
