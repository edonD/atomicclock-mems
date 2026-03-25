"""
HOW A CSAC WORKS -- THE SIMPLE VERSION

One connected story told in 8 steps, like a comic book.
Each panel builds on the previous one. No isolated theory dumps.

The story: You need to build the world's tiniest, most accurate metronome.
How do you do it? You use atoms, because every atom is an identical copy.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle
from matplotlib.colors import LinearSegmentedColormap

fig = plt.figure(figsize=(20, 48), facecolor='#0a0a1a')

gs = GridSpec(8, 1, figure=fig, hspace=0.12,
              left=0.04, right=0.96, top=0.985, bottom=0.005)

# Global title
fig.text(0.5, 0.993,
    'HOW A CHIP-SCALE ATOMIC CLOCK ACTUALLY WORKS',
    ha='center', fontsize=22, fontweight='bold', color='white')
fig.text(0.5, 0.989,
    'One connected story, from the basic idea to the final clock',
    ha='center', fontsize=13, color='#888888', style='italic')


def make_panel(gs_slot, step_num, title, color_accent):
    """Create a panel with consistent styling."""
    ax = fig.add_subplot(gs_slot, facecolor='#0d0d20')
    # Border
    for sp in ax.spines.values():
        sp.set_edgecolor(color_accent)
        sp.set_linewidth(2)
    ax.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)
    # Step number badge
    ax.text(0.01, 0.97, f'STEP {step_num}', transform=ax.transAxes,
            fontsize=14, fontweight='bold', color='#0d0d20', va='top',
            bbox=dict(boxstyle='round,pad=0.3', facecolor=color_accent, edgecolor='none'))
    ax.text(0.10, 0.97, title, transform=ax.transAxes,
            fontsize=16, fontweight='bold', color=color_accent, va='top')
    return ax


# ════════════════════════════════════════════════════════════════════
# STEP 1: THE PROBLEM — What is a clock, really?
# ════════════════════════════════════════════════════════════════════
ax1 = make_panel(gs[0], 1, 'What is a clock? Something that ticks at a known rate.', '#ffaa00')

# Left side: pendulum analogy
# Pendulum
t_pend = np.linspace(0, 4*np.pi, 300)
pend_x = 0.15 + 0.06 * np.sin(t_pend)
pend_y = 0.75 - 0.15 * np.abs(np.cos(t_pend))
ax1.plot(pend_x, pend_y, color='#ffaa00', linewidth=2, transform=ax1.transAxes)
ax1.plot([0.15, 0.15], [0.90, 0.75], color='#888888', linewidth=1, transform=ax1.transAxes)
ax1.plot(pend_x[-1], pend_y[-1], 'o', color='#ffaa00', markersize=10, transform=ax1.transAxes)

# Quartz crystal
t_q = np.linspace(0, 8*np.pi, 300)
q_signal = 0.50 + 0.04 * np.sin(t_q)
q_x = np.linspace(0.30, 0.55, 300)
ax1.plot(q_x, q_signal, color='#ff4444', linewidth=2, transform=ax1.transAxes)
ax1.text(0.42, 0.58, 'Quartz crystal\nvibrates 32,768x / sec', ha='center',
         fontsize=10, color='#ff4444', transform=ax1.transAxes)

# Atom
t_a = np.linspace(0, 30*np.pi, 300)
a_signal = 0.50 + 0.04 * np.sin(t_a)
a_x = np.linspace(0.62, 0.87, 300)
ax1.plot(a_x, a_signal, color='#00ff88', linewidth=2, transform=ax1.transAxes)
ax1.text(0.75, 0.58, 'Rb atom oscillates\n6,834,682,611x / sec', ha='center',
         fontsize=10, color='#00ff88', transform=ax1.transAxes)

# THE KEY INSIGHT (big text)
ax1.text(0.50, 0.28,
    'EVERY clock works the same way:\n'
    'find something that repeats  -->  count the repetitions  -->  that\'s time.\n\n'
    'Pendulum: gravity pulls it back and forth. Count swings.\n'
    'Quartz: electric field makes crystal vibrate. Count vibrations.\n'
    'Atom: electrons oscillate between energy levels. Count oscillations.\n\n'
    'THE BIG QUESTION: Why are atoms better?',
    ha='center', va='center', fontsize=12, color='white',
    transform=ax1.transAxes,
    bbox=dict(boxstyle='round,pad=0.6', facecolor='#111133', edgecolor='#ffaa00', linewidth=1.5))

# Arrow to next
ax1.annotate('', xy=(0.5, 0.02), xytext=(0.5, 0.08),
             xycoords='axes fraction', textcoords='axes fraction',
             arrowprops=dict(arrowstyle='->', color='white', lw=3))


# ════════════════════════════════════════════════════════════════════
# STEP 2: WHY ATOMS — Every copy is identical
# ════════════════════════════════════════════════════════════════════
ax2 = make_panel(gs[1], 2, 'Why atoms? Because EVERY Rb-87 atom is an identical copy.', '#00ff88')

# Left: show identical atoms
for i in range(5):
    cx = 0.08 + i * 0.07
    circle = Circle((cx, 0.72), 0.02, transform=ax2.transAxes,
                     facecolor='#00ff88', edgecolor='white', linewidth=1.5, alpha=0.7)
    ax2.add_patch(circle)
    ax2.text(cx, 0.72, 'Rb', ha='center', va='center', fontsize=7,
             color='white', fontweight='bold', transform=ax2.transAxes)

ax2.text(0.22, 0.64, 'ALL oscillate at EXACTLY\n6,834,682,610.904 Hz', ha='center',
         fontsize=10, color='#00ff88', fontweight='bold', transform=ax2.transAxes)

# Right: show different quartz crystals
shapes = ['s', 'D', 'p', '^', 'o']
sizes = [12, 10, 14, 11, 9]
for i, (s, sz) in enumerate(zip(shapes, sizes)):
    cx = 0.58 + i * 0.07
    ax2.plot(cx, 0.72, s, color='#ff4444', markersize=sz, transform=ax2.transAxes)

ax2.text(0.76, 0.64, 'Each crystal is DIFFERENT\n(shape, defects, temperature)', ha='center',
         fontsize=10, color='#ff4444', transform=ax2.transAxes)

# The analogy
ax2.text(0.50, 0.42,
    'ANALOGY:  Imagine you need a perfect ruler.\n\n'
    'Option A: Carve one from wood.  --> Every piece of wood is different. Temperature\n'
    '          warps it. It ages. Two rulers will never match exactly.\n\n'
    'Option B: Use the wavelength of light.  --> Physics guarantees every photon of the\n'
    '          same type has EXACTLY the same wavelength. Unchanging. Universal.\n\n'
    'Atoms are option B. Quantum mechanics sets the oscillation frequency.\n'
    'No manufacturing tolerance. No aging. No two atoms disagree.',
    ha='center', va='center', fontsize=11, color='white',
    transform=ax2.transAxes,
    bbox=dict(boxstyle='round,pad=0.6', facecolor='#111133', edgecolor='#00ff88', linewidth=1.5))

# Energy levels (simple)
ax2.plot([0.15, 0.35], [0.14, 0.14], color='#44aaff', linewidth=3, transform=ax2.transAxes)
ax2.plot([0.15, 0.35], [0.22, 0.22], color='#44aaff', linewidth=3, transform=ax2.transAxes)
ax2.text(0.37, 0.14, 'Energy level 1 (low)', fontsize=9, color='#44aaff',
         va='center', transform=ax2.transAxes)
ax2.text(0.37, 0.22, 'Energy level 2 (slightly higher)', fontsize=9, color='#44aaff',
         va='center', transform=ax2.transAxes)
ax2.annotate('', xy=(0.12, 0.22), xytext=(0.12, 0.14),
             xycoords='axes fraction', textcoords='axes fraction',
             arrowprops=dict(arrowstyle='<->', color='yellow', lw=2))
ax2.text(0.06, 0.18, 'Gap =\n6.835\nGHz', ha='center', fontsize=8, color='yellow',
         fontweight='bold', transform=ax2.transAxes)
ax2.text(0.75, 0.14,
    'The gap between these two levels\n'
    'is set by quantum mechanics.\n'
    'It is the SAME for every Rb-87\n'
    'atom in the universe. That gap\n'
    'IS your clock frequency.',
    ha='center', va='center', fontsize=10, color='yellow',
    transform=ax2.transAxes,
    bbox=dict(boxstyle='round,pad=0.4', facecolor='#1a1a0a', edgecolor='yellow'))

ax2.annotate('', xy=(0.5, 0.02), xytext=(0.5, 0.06),
             xycoords='axes fraction', textcoords='axes fraction',
             arrowprops=dict(arrowstyle='->', color='white', lw=3))


# ════════════════════════════════════════════════════════════════════
# STEP 3: THE TRICK — How do you "listen" to an atom's frequency?
# ════════════════════════════════════════════════════════════════════
ax3 = make_panel(gs[2], 3, 'The trick: shine a laser and watch what happens.', '#ff8844')

# Scene 1: laser OFF resonance -> atom absorbs
ax3.text(0.25, 0.85, 'WHEN LASER IS WRONG FREQUENCY:', ha='center',
         fontsize=11, color='#ff4444', fontweight='bold', transform=ax3.transAxes)

# Laser
ax3.annotate('', xy=(0.25, 0.68), xytext=(0.08, 0.68),
             xycoords='axes fraction', textcoords='axes fraction',
             arrowprops=dict(arrowstyle='->', color='red', lw=4))
ax3.text(0.04, 0.72, 'LASER', fontsize=9, color='red', fontweight='bold',
         transform=ax3.transAxes)

# Atom (absorbing)
circle_abs = Circle((0.30, 0.68), 0.03, transform=ax3.transAxes,
                     facecolor='#ff4444', edgecolor='white', linewidth=2, alpha=0.8)
ax3.add_patch(circle_abs)
ax3.text(0.30, 0.68, 'Rb', ha='center', va='center', fontsize=8,
         color='white', fontweight='bold', transform=ax3.transAxes)

# Dim light after
ax3.annotate('', xy=(0.45, 0.68), xytext=(0.36, 0.68),
             xycoords='axes fraction', textcoords='axes fraction',
             arrowprops=dict(arrowstyle='->', color='#661111', lw=2, linestyle='--'))
ax3.text(0.46, 0.68, 'DIM\n(absorbed)', fontsize=9, color='#ff4444',
         va='center', transform=ax3.transAxes)


# Scene 2: laser AT EXACT resonance -> atom becomes transparent (CPT)
ax3.text(0.75, 0.85, 'WHEN LASER IS EXACTLY RIGHT:', ha='center',
         fontsize=11, color='#00ff88', fontweight='bold', transform=ax3.transAxes)

ax3.annotate('', xy=(0.75, 0.68), xytext=(0.58, 0.68),
             xycoords='axes fraction', textcoords='axes fraction',
             arrowprops=dict(arrowstyle='->', color='red', lw=4))
ax3.text(0.54, 0.72, 'LASER', fontsize=9, color='red', fontweight='bold',
         transform=ax3.transAxes)

# Atom (transparent / dark state)
circle_dark = Circle((0.80, 0.68), 0.03, transform=ax3.transAxes,
                      facecolor='none', edgecolor='#00ff88', linewidth=2, linestyle='--')
ax3.add_patch(circle_dark)
ax3.text(0.80, 0.68, 'Rb', ha='center', va='center', fontsize=8,
         color='#00ff88', fontweight='bold', transform=ax3.transAxes)

# Bright light after
ax3.annotate('', xy=(0.95, 0.68), xytext=(0.86, 0.68),
             xycoords='axes fraction', textcoords='axes fraction',
             arrowprops=dict(arrowstyle='->', color='red', lw=4))
ax3.text(0.96, 0.68, 'BRIGHT!\n(passed\nthrough)', fontsize=9, color='#00ff88',
         va='center', transform=ax3.transAxes)

# The CPT signal plot (simple version)
delta = np.linspace(-100, 100, 1000)
brightness = 0.4 + 0.15 * np.exp(-delta**2 / (2*50**2))  # broad dip inverted
brightness += 0.35 * np.exp(-delta**2 / (2*2**2))  # sharp CPT peak
ax3.plot(0.10 + delta/250 * 0.35 + 0.35, brightness * 0.38 + 0.12,
         color='#00ff88', linewidth=3, transform=ax3.transAxes)
ax3.axvline(x=0.45, ymin=0.08, ymax=0.46, color='yellow', linestyle=':',
            alpha=0.5, linewidth=1)

ax3.text(0.45, 0.52, 'detector brightness', ha='center', fontsize=8,
         color='#888888', transform=ax3.transAxes)
ax3.text(0.45, 0.08, 'laser frequency (scanning)', ha='center', fontsize=8,
         color='#888888', transform=ax3.transAxes)
ax3.text(0.45, 0.48, 'SHARP PEAK = the atom\n"ringing" at its natural frequency',
         ha='center', fontsize=10, color='yellow', fontweight='bold',
         transform=ax3.transAxes)

# Right side explanation
ax3.text(0.78, 0.35,
    'This is called CPT:\n'
    'Coherent Population\n'
    'Trapping.\n\n'
    'When the laser matches\n'
    'the atom\'s frequency\n'
    'EXACTLY, the atom enters\n'
    'a quantum "dark state"\n'
    'and becomes TRANSPARENT.\n\n'
    'It\'s like a tuning fork:\n'
    'the atom only "rings"\n'
    'at one exact note.',
    ha='center', va='center', fontsize=10, color='#ff8844',
    transform=ax3.transAxes,
    bbox=dict(boxstyle='round,pad=0.5', facecolor='#1a0a0a', edgecolor='#ff8844', linewidth=1.5))

ax3.annotate('', xy=(0.5, 0.01), xytext=(0.5, 0.05),
             xycoords='axes fraction', textcoords='axes fraction',
             arrowprops=dict(arrowstyle='->', color='white', lw=3))


# ════════════════════════════════════════════════════════════════════
# STEP 4: THE FEEDBACK LOOP — Lock to the peak
# ════════════════════════════════════════════════════════════════════
ax4 = make_panel(gs[3], 4, 'Lock to the peak: if you drift, correct yourself.', '#aa44ff')

# Simple feedback story
ax4.text(0.50, 0.82,
    'Now you have a sharp peak that marks the EXACT atomic frequency.\n'
    'Your job: keep your oscillator parked on top of that peak. How?',
    ha='center', fontsize=12, color='white', transform=ax4.transAxes)

# Three scenarios side by side
scenarios = [
    (0.18, 'TOO LOW', '#ff4444',
     'Your oscillator is below\nthe atomic frequency.\n\nDetector sees: dim light.\n\nAction: nudge frequency UP.'),
    (0.50, 'JUST RIGHT', '#00ff88',
     'Your oscillator matches\nthe atom exactly.\n\nDetector sees: bright light!\n\nAction: do nothing (perfect).'),
    (0.82, 'TOO HIGH', '#ffaa00',
     'Your oscillator is above\nthe atomic frequency.\n\nDetector sees: dim light.\n\nAction: nudge frequency DOWN.'),
]

for cx, label, col, desc in scenarios:
    # Mini CPT curve
    d = np.linspace(-1, 1, 200)
    peak = np.exp(-d**2 / (2*0.03**2))
    ax4.plot(cx + d*0.12, 0.55 + peak*0.12, color='#00ff88', linewidth=2,
             transform=ax4.transAxes, alpha=0.5)
    # Marker showing "where you are"
    if label == 'TOO LOW':
        mx = cx - 0.06
    elif label == 'TOO HIGH':
        mx = cx + 0.06
    else:
        mx = cx
    my_val = np.exp(-(mx-cx)**2 / (2*(0.12*np.sqrt(0.03))**2))
    ax4.plot(mx, 0.55 + my_val * 0.12, 'v', color=col, markersize=14,
             transform=ax4.transAxes, zorder=5)
    ax4.text(cx, 0.72, label, ha='center', fontsize=11, color=col,
             fontweight='bold', transform=ax4.transAxes)
    ax4.text(cx, 0.35, desc, ha='center', fontsize=9, color=col,
             transform=ax4.transAxes, va='top',
             bbox=dict(boxstyle='round,pad=0.4', facecolor='#111133', edgecolor=col, alpha=0.8))

# The loop summary
ax4.text(0.50, 0.10,
    'THIS IS THE FEEDBACK LOOP:   Measure brightness  -->  Compare to peak  '
    '-->  Calculate error  -->  Correct oscillator  -->  Repeat 1000x per second\n\n'
    'Result: your oscillator stays locked to the atom\'s frequency with incredible precision.\n'
    'This is the same idea as cruise control in a car: measure speed, compare to target, adjust gas pedal.',
    ha='center', va='center', fontsize=11, color='white',
    transform=ax4.transAxes,
    bbox=dict(boxstyle='round,pad=0.5', facecolor='#111133', edgecolor='#aa44ff', linewidth=1.5))

ax4.annotate('', xy=(0.5, 0.01), xytext=(0.5, 0.04),
             xycoords='axes fraction', textcoords='axes fraction',
             arrowprops=dict(arrowstyle='->', color='white', lw=3))


# ════════════════════════════════════════════════════════════════════
# STEP 5: THE CLEVER TRICK — Two frequencies from one laser
# ════════════════════════════════════════════════════════════════════
ax5 = make_panel(gs[4], 5, 'The clever trick: get two frequencies from one laser.', '#44aaff')

ax5.text(0.50, 0.83,
    'PROBLEM: The atom needs TWO light frequencies separated by 6.835 GHz to create the dark state.\n'
    'But a tiny chip can only fit ONE laser. Solution: modulate it.',
    ha='center', fontsize=11, color='white', transform=ax5.transAxes)

# Show modulation concept
t_mod = np.linspace(0, 6, 500)

# Unmodulated laser
carrier = np.sin(2 * np.pi * 8 * t_mod)
ax5.plot(0.05 + t_mod/6 * 0.28, 0.67 + carrier * 0.04, color='red', linewidth=1.5,
         transform=ax5.transAxes, alpha=0.7)
ax5.text(0.19, 0.74, 'Plain laser\n(one frequency)', ha='center', fontsize=9,
         color='red', transform=ax5.transAxes)

# Arrow
ax5.annotate('  modulate\n  at 3.417 GHz', xy=(0.38, 0.67), xytext=(0.34, 0.67),
             xycoords='axes fraction', textcoords='axes fraction',
             fontsize=9, color='#ffaa00', fontweight='bold',
             arrowprops=dict(arrowstyle='->', color='#ffaa00', lw=2))

# Modulated laser (beat pattern)
mod_signal = np.sin(2*np.pi*8*t_mod) * (1 + 0.5*np.sin(2*np.pi*2*t_mod))
ax5.plot(0.42 + t_mod/6 * 0.28, 0.67 + mod_signal * 0.04, color='#ff8844', linewidth=1.5,
         transform=ax5.transAxes)
ax5.text(0.56, 0.74, 'Modulated laser\n(multiple frequencies)', ha='center', fontsize=9,
         color='#ff8844', transform=ax5.transAxes)

# Equals sign
ax5.text(0.73, 0.67, '=', fontsize=20, color='white', fontweight='bold',
         ha='center', va='center', transform=ax5.transAxes)

# Frequency spectrum (the sidebands)
freqs = [-2, -1, 0, 1, 2]
amps = [0.05, 0.35, 0.20, 0.35, 0.05]  # Bessel-like
colors_sb = ['#444444', '#00ff88', '#ff4444', '#00ff88', '#444444']
for f, a, col in zip(freqs, amps, colors_sb):
    x_pos = 0.85 + f * 0.03
    ax5.plot([x_pos, x_pos], [0.60, 0.60 + a * 0.2], color=col, linewidth=4,
             transform=ax5.transAxes, solid_capstyle='round')
    ax5.plot(x_pos, 0.60 + a * 0.2, 'o', color=col, markersize=6,
             transform=ax5.transAxes)

# Label the important ones
ax5.annotate('', xy=(0.88, 0.55), xytext=(0.82, 0.55),
             xycoords='axes fraction', textcoords='axes fraction',
             arrowprops=dict(arrowstyle='<->', color='yellow', lw=2))
ax5.text(0.85, 0.52, '6.835 GHz apart!', ha='center', fontsize=9,
         color='yellow', fontweight='bold', transform=ax5.transAxes)

# Simple explanation
ax5.text(0.50, 0.30,
    'GUITAR STRING ANALOGY:\n\n'
    'Pluck a guitar string and you get the fundamental note PLUS harmonics (overtones).\n'
    'Same idea: wobble the laser\'s power at 3.417 GHz and you create "sidebands" --\n'
    'new frequencies above and below the original.\n\n'
    'The two green sidebands are separated by 2 x 3.417 = 6.835 GHz.\n'
    'That EXACTLY matches the Rb atom\'s energy gap!\n\n'
    'So one tiny laser, modulated by one cheap oscillator, creates\n'
    'the exact pair of frequencies needed to talk to the atom.',
    ha='center', va='center', fontsize=11, color='white',
    transform=ax5.transAxes,
    bbox=dict(boxstyle='round,pad=0.6', facecolor='#111133', edgecolor='#44aaff', linewidth=1.5))

ax5.annotate('', xy=(0.5, 0.01), xytext=(0.5, 0.05),
             xycoords='axes fraction', textcoords='axes fraction',
             arrowprops=dict(arrowstyle='->', color='white', lw=3))


# ════════════════════════════════════════════════════════════════════
# STEP 6: THE DARK STATE — Why atoms become transparent
# ════════════════════════════════════════════════════════════════════
ax6 = make_panel(gs[5], 6, 'The dark state: why the atom becomes transparent.', '#00ff88')

ax6.text(0.50, 0.84,
    'This is the quantum magic at the heart of the whole device.',
    ha='center', fontsize=12, color='#888888', style='italic', transform=ax6.transAxes)

# Swing analogy (two pushers, one swing)
# Left side: out of sync pushers -> swing moves
ax6.text(0.25, 0.76, 'TWO PUSHERS, ONE SWING', ha='center', fontsize=11,
         color='white', fontweight='bold', transform=ax6.transAxes)

# Out of sync
ax6.text(0.12, 0.68, 'Out of sync:', fontsize=10, color='#ff4444',
         fontweight='bold', transform=ax6.transAxes)
# Pushers
ax6.plot(0.07, 0.58, 'o', color='#ff4444', markersize=15, transform=ax6.transAxes)
ax6.text(0.07, 0.53, 'Push\nRIGHT', fontsize=7, color='#ff4444', ha='center',
         transform=ax6.transAxes)
ax6.plot(0.22, 0.58, 'o', color='#ff8844', markersize=15, transform=ax6.transAxes)
ax6.text(0.22, 0.53, 'Push\nRIGHT', fontsize=7, color='#ff8844', ha='center',
         transform=ax6.transAxes)
# Swing moving
swing_t = np.linspace(0, 2*np.pi, 50)
ax6.plot(0.145 + 0.03*np.sin(swing_t), 0.58 + 0.015*np.cos(swing_t),
         color='#ffaa00', linewidth=2, transform=ax6.transAxes)
ax6.text(0.14, 0.63, 'SWINGING', fontsize=8, color='#ffaa00', fontweight='bold',
         ha='center', transform=ax6.transAxes)

# In sync but opposite
ax6.text(0.33, 0.68, 'Perfectly opposing:', fontsize=10, color='#00ff88',
         fontweight='bold', transform=ax6.transAxes)
ax6.plot(0.33, 0.58, 'o', color='#00ff88', markersize=15, transform=ax6.transAxes)
ax6.text(0.33, 0.53, 'Push\nRIGHT', fontsize=7, color='#00ff88', ha='center',
         transform=ax6.transAxes)
ax6.plot(0.48, 0.58, 'o', color='#88ffaa', markersize=15, transform=ax6.transAxes)
ax6.text(0.48, 0.53, 'Push\nLEFT', fontsize=7, color='#88ffaa', ha='center',
         transform=ax6.transAxes)
# Swing still
ax6.plot(0.405, 0.58, 's', color='#00ff88', markersize=12, transform=ax6.transAxes)
ax6.text(0.405, 0.63, 'STILL!', fontsize=9, color='#00ff88', fontweight='bold',
         ha='center', transform=ax6.transAxes)

# The atom explanation
ax6.text(0.50, 0.38,
    'THE ATOM VERSION:\n\n'
    'The atom has 3 energy levels arranged in a "V" shape (called Lambda):\n'
    '  - Level 1 (ground, low)         Two laser fields push the atom\n'
    '  - Level 2 (ground, slightly higher)   between these levels.\n'
    '  - Level 3 (excited, way up top)\n\n'
    'When the two laser fields are at EXACTLY the right frequencies,\n'
    'they push the atom in PERFECTLY OPPOSING ways -- like the two pushers.\n\n'
    'The atom gets trapped in a superposition of level 1 and level 2 where\n'
    'the two pushes CANCEL OUT. It literally CANNOT absorb any light.\n'
    'This is the "dark state". The atom becomes invisible to the laser.\n\n'
    'The detector sees maximum brightness = you found the exact frequency!',
    ha='center', va='center', fontsize=10.5, color='white',
    transform=ax6.transAxes,
    bbox=dict(boxstyle='round,pad=0.6', facecolor='#0a1a0a', edgecolor='#00ff88', linewidth=2))

# Math footnote (small, optional)
ax6.text(0.50, 0.06,
    'Math:  |Dark> = ( Omega_2 * |1> - Omega_1 * |2> ) / N       '
    'Property: <Excited| H |Dark> = 0  (cannot absorb)',
    ha='center', fontsize=9, color='#555555', style='italic', transform=ax6.transAxes)

ax6.annotate('', xy=(0.5, 0.01), xytext=(0.5, 0.04),
             xycoords='axes fraction', textcoords='axes fraction',
             arrowprops=dict(arrowstyle='->', color='white', lw=3))


# ════════════════════════════════════════════════════════════════════
# STEP 7: THE PHYSICAL CHIP — Putting it all together
# ════════════════════════════════════════════════════════════════════
ax7 = make_panel(gs[6], 7, 'The physical chip: stack of layers on a 2mm die.', '#FFD700')

ax7.text(0.50, 0.83,
    'Now package all of this into a chip the size of a grain of rice:',
    ha='center', fontsize=12, color='white', transform=ax7.transAxes)

# Vertical stack diagram (left side, simple rectangles)
layers_stack = [
    (0.82, 0.08, '#44ff44', 'PHOTODETECTOR',
     'Measures brightness. When light is brightest = atom is transparent = you\'re on frequency.'),
    (0.72, 0.08, '#44aaff', 'GLASS (top seal)',
     'Borosilicate glass, anodically bonded to silicon. Seals the Rb atoms inside for decades.'),
    (0.52, 0.18, '#666666', 'SILICON BODY (the cell)',
     'MEMS-etched cavity filled with Rb-87 atoms + N2 gas. Heated to 85C by platinum traces.\n'
     'N2 buffer gas slows atoms down so they spend more time in the laser beam = sharper signal.'),
    (0.42, 0.08, '#44aaff', 'GLASS (bottom seal)',
     'Same bonding. Together with top glass, creates hermetic chamber.'),
    (0.32, 0.06, '#cc44ff', 'QUARTER-WAVE PLATE',
     'Converts laser light from straight polarization to circular. Needed for the dark state to work.'),
    (0.20, 0.08, '#ff4444', 'VCSEL LASER (795 nm)',
     'Tiny semiconductor laser. Modulated at 3.417 GHz to create the two sideband frequencies.'),
]

for y, h, col, name, desc in layers_stack:
    rect = FancyBboxPatch((0.06, y), 0.20, h, boxstyle="round,pad=0.005",
                           facecolor=col, edgecolor='white', linewidth=1.5,
                           alpha=0.5, transform=ax7.transAxes)
    ax7.add_patch(rect)
    ax7.text(0.16, y + h/2, name, ha='center', va='center', fontsize=7.5,
             color='white', fontweight='bold', transform=ax7.transAxes)
    # Description to the right
    ax7.text(0.30, y + h/2, desc, va='center', fontsize=8.5, color=col,
             transform=ax7.transAxes)

# Laser beam arrow
ax7.annotate('', xy=(0.16, 0.82), xytext=(0.16, 0.28),
             xycoords='axes fraction', textcoords='axes fraction',
             arrowprops=dict(arrowstyle='->', color='red', lw=3, linestyle='--', alpha=0.4))

# Scale reference
ax7.text(0.16, 0.14, 'Total height: ~2mm\nTotal width: ~2mm\nEntire thing smaller\nthan a pencil eraser',
         ha='center', fontsize=9, color='#FFD700', fontweight='bold',
         transform=ax7.transAxes,
         bbox=dict(boxstyle='round,pad=0.3', facecolor='#1a1a0a', edgecolor='#FFD700'))

ax7.annotate('', xy=(0.5, 0.01), xytext=(0.5, 0.04),
             xycoords='axes fraction', textcoords='axes fraction',
             arrowprops=dict(arrowstyle='->', color='white', lw=3))


# ════════════════════════════════════════════════════════════════════
# STEP 8: THE PAYOFF — Time -> Position
# ════════════════════════════════════════════════════════════════════
ax8 = make_panel(gs[7], 8, 'The payoff: microseconds of time = meters of position.', '#00ccff')

ax8.text(0.50, 0.84,
    'All of the physics above exists for ONE reason: to keep time accurately when GPS is gone.',
    ha='center', fontsize=12, color='white', transform=ax8.transAxes)

# The key equation
ax8.text(0.50, 0.73,
    'THE KEY EQUATION:     position error  =  time error  x  speed of light\n\n'
    '1 microsecond of clock error   =   300 meters of position error',
    ha='center', fontsize=14, color='yellow', fontweight='bold',
    transform=ax8.transAxes,
    bbox=dict(boxstyle='round,pad=0.5', facecolor='#1a1a0a', edgecolor='yellow', linewidth=2))

# Comparison over time (simple bar chart style)
hours = [1, 2, 4, 8, 12, 24]
err_quartz = [300, 660, 1440, 3200, 5400, 12000]  # meters
err_csac   = [3, 7, 16, 35, 55, 120]               # meters

y_positions = np.arange(len(hours))
bar_height = 0.35

ax8_inner = fig.add_axes([0.08, 0.025, 0.84, 0.075])  # manual placement for chart
ax8_inner.set_facecolor('#0d0d20')

bars_q = ax8_inner.barh(y_positions + bar_height/2, err_quartz, bar_height,
                         color='#ff4444', alpha=0.7, edgecolor='white', linewidth=0.5,
                         label='Quartz crystal')
bars_c = ax8_inner.barh(y_positions - bar_height/2, err_csac, bar_height,
                         color='#00ff88', alpha=0.7, edgecolor='white', linewidth=0.5,
                         label='CSAC (this chip)')

ax8_inner.set_yticks(y_positions)
ax8_inner.set_yticklabels([f'{h}h' for h in hours], color='white', fontsize=9)
ax8_inner.set_xlabel('Position Error (meters) after GPS loss', color='white', fontsize=10)
ax8_inner.set_xscale('log')
ax8_inner.legend(fontsize=9, facecolor='#1a1a2e', edgecolor='#444', labelcolor='white',
                 loc='lower right')
ax8_inner.tick_params(colors='gray')
ax8_inner.grid(True, alpha=0.1, color='gray', axis='x')
for sp in ax8_inner.spines.values():
    sp.set_edgecolor('#333')

# Labels on bars
for i, (q, c) in enumerate(zip(err_quartz, err_csac)):
    ax8_inner.text(q * 1.2, i + bar_height/2, f'{q:,}m', va='center',
                   fontsize=7.5, color='#ff4444')
    ax8_inner.text(c * 1.5, i - bar_height/2, f'{c}m', va='center',
                   fontsize=7.5, color='#00ff88')

# Summary in the main panel
ax8.text(0.50, 0.40,
    'THE COMPLETE CHAIN:\n\n'
    '  Quantum mechanics  -->  Rb-87 atom has a fixed energy gap (6.835 GHz)\n'
    '             |\n'
    '  Laser physics  -->  One modulated VCSEL creates two frequencies that match it\n'
    '             |\n'
    '  CPT dark state  -->  Atom becomes transparent at EXACT resonance = sharp peak\n'
    '             |\n'
    '  Feedback loop  -->  Lock your oscillator to that peak = atomic-grade frequency\n'
    '             |\n'
    '  Count cycles  -->  6,834,682,611 oscillations = 1 second (to nanosecond accuracy)\n'
    '             |\n'
    '  Navigation  -->  Accurate time = accurate position, even without GPS satellites\n\n\n'
    'ALL OF THIS FITS ON A 2mm CHIP USING 120 MILLIWATTS OF POWER.',
    ha='center', va='center', fontsize=11, color='white', fontfamily='monospace',
    transform=ax8.transAxes,
    bbox=dict(boxstyle='round,pad=0.6', facecolor='#111133', edgecolor='#00ccff', linewidth=2))


# ──────────────────────────────────────────────────────────────────
plt.savefig('csac_simple.png', dpi=140, facecolor=fig.get_facecolor(),
            bbox_inches='tight')
plt.show()
print("Saved to csac_simple.png")
