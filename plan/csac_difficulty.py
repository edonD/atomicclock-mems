"""
BUILD DIFFICULTY ANALYSIS: MEMS Vapor-Cell CSAC Core

Honest, brutal assessment of what it takes to actually build this thing.
Based on the PDF's own risk tables, budget ranges, and public research citations.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from matplotlib.patches import FancyBboxPatch
from matplotlib.colors import LinearSegmentedColormap

fig = plt.figure(figsize=(22, 52), facecolor='#0a0a1a')

gs = GridSpec(9, 1, figure=fig, hspace=0.10,
              left=0.04, right=0.96, top=0.988, bottom=0.004)

fig.text(0.5, 0.995,
    'HOW HARD IS IT TO BUILD A CSAC?  --  Honest Difficulty Analysis',
    ha='center', fontsize=22, fontweight='bold', color='white')
fig.text(0.5, 0.992,
    'What you need, what can go wrong, how much it costs, and where the bodies are buried',
    ha='center', fontsize=12, color='#888888', style='italic')


def panel(gs_slot, title, color):
    ax = fig.add_subplot(gs_slot, facecolor='#0d0d20')
    for sp in ax.spines.values():
        sp.set_edgecolor(color)
        sp.set_linewidth(2)
    ax.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)
    ax.text(0.01, 0.97, title, transform=ax.transAxes,
            fontsize=15, fontweight='bold', color=color, va='top')
    return ax


# ════════════════════════════════════════════════════════════════
# 1. OVERALL VERDICT
# ════════════════════════════════════════════════════════════════
ax1 = panel(gs[0], 'THE BOTTOM LINE', '#ff4444')

ax1.text(0.50, 0.78,
    'OVERALL DIFFICULTY:   8.5 / 10   --   VERY HARD',
    ha='center', fontsize=18, color='#ff4444', fontweight='bold',
    transform=ax1.transAxes,
    bbox=dict(boxstyle='round,pad=0.5', facecolor='#1a0a0a', edgecolor='#ff4444', linewidth=2))

ax1.text(0.50, 0.42,
    'This is NOT a weekend project, a startup hackathon, or a software problem.\n'
    'You are building a quantum physics instrument using semiconductor fabrication.\n\n'
    'The PDF itself says the MVP budget is $250k-$500k (low) to $2.5M-$6M (high).\n'
    'Timeline: 12-18 months to first working prototype, 24-36 months to a differentiating product.\n'
    'The document explicitly flags hermeticity, filling, and contamination as UNSOLVED at production scale.\n\n'
    'BUT -- the PDF also argues this is EASIER than most defense MEMS bets because:\n'
    '  - You\'re building a COMPONENT (vapor cell core), not a full clock module\n'
    '  - Recent research (2024-2025) has de-risked the hardest sub-problems\n'
    '  - You don\'t need to own the entire clock stack, just the physics package\n'
    '  - NIST, DARPA, and labs have published enough to build on',
    ha='center', va='center', fontsize=11, color='white',
    transform=ax1.transAxes,
    bbox=dict(boxstyle='round,pad=0.6', facecolor='#111133', edgecolor='#444'))

# Difficulty meter
meter_x = np.linspace(0.10, 0.90, 100)
meter_colors = plt.cm.RdYlGn_r(np.linspace(0, 1, 100))
for i in range(99):
    ax1.plot([meter_x[i], meter_x[i+1]], [0.12, 0.12], color=meter_colors[i],
             linewidth=12, transform=ax1.transAxes, solid_capstyle='butt')
# Needle at 8.5/10
needle_pos = 0.10 + 0.80 * (8.5/10)
ax1.plot(needle_pos, 0.12, 'v', color='white', markersize=18, transform=ax1.transAxes)
ax1.text(0.10, 0.07, 'Easy', fontsize=8, color='#00ff88', transform=ax1.transAxes)
ax1.text(0.88, 0.07, 'Extreme', fontsize=8, color='#ff4444', transform=ax1.transAxes, ha='right')


# ════════════════════════════════════════════════════════════════
# 2. DIFFICULTY BREAKDOWN BY SUBSYSTEM
# ════════════════════════════════════════════════════════════════
ax2 = panel(gs[1], 'DIFFICULTY BREAKDOWN: What\'s hard and what\'s not', '#ffaa00')

subsystems = [
    ('MEMS vapor cell fabrication\n(Si etch, glass bonding, cavity formation)',
     9.0, '#ff2222',
     'Requires cleanroom + MEMS foundry access. Anodic bonding at 350C/400V.\n'
     'Sub-mm cavity etching with tight tolerances. This is the hardest part.'),

    ('Alkali filling (Rb + N2 buffer gas)\n(get atoms inside, then seal)',
     9.5, '#ff0000',
     'THE SINGLE HARDEST STEP. 2025 research explicitly calls this "difficult".\n'
     'Photolysis of RbN3 or pill dispensing. Contamination kills performance.\n'
     'Quantity control, hermeticity, and bake-out protocols are still being refined.'),

    ('Pt heater/sensor deposition\n(thin-film platinum on Si)',
     5.0, '#ffaa00',
     'Standard MEMS metallization. Sputter or e-beam deposit ~200nm Pt.\n'
     'Pattern with photolithography. Dual-zone design adds complexity but is doable.'),

    ('Anti-permeation coating (Al2O3)\n(prevent He leak through glass)',
     6.5, '#ff8844',
     'ALD (atomic layer deposition) of Al2O3. Equipment is expensive but\n'
     'the process is well-understood. Key to long cell lifetime.'),

    ('Anodic bonding (seal the cell)\n(glass-to-silicon hermetic bond)',
     7.5, '#ff6633',
     'Need specialized bonder ($200k-$500k). Process is known but yield\n'
     'is THE critical metric. Bad bonds = leaking cells = dead clocks.\n'
     'PDF flags this as a core COGS driver.'),

    ('VCSEL laser (buy, don\'t build)\n(795nm, single-mode)',
     2.0, '#44ff44',
     'Buy off the shelf. Multiple suppliers (Vixar, Philips, II-VI).\n'
     'This is a commodity component. ~$10-50 per unit.'),

    ('Optics (quarter-wave plate)\n(polarization control)',
     3.0, '#88ff44',
     'Buy or have fabricated. Micro-optic QWP is a known part.\n'
     'Alignment during packaging adds some complexity.'),

    ('Photodetector\n(detect transmitted light)',
     2.0, '#44ff44',
     'Standard Si photodiode. Commodity. <$5 per unit.'),

    ('Electronics (LO, PID, lock-in)\n(3.417 GHz oscillator + control)',
     5.5, '#ffaa00',
     'RF modulation at 3.4 GHz needs careful PCB design. PID and lock-in\n'
     'are standard but tuning for CPT signal requires atomic physics expertise.'),

    ('Packaging (vacuum + LCC ceramic)\n(hermetic package for the whole stack)',
     7.0, '#ff8833',
     'Vacuum packaging (~0.01 mbar) with getter material. Needs specialized\n'
     'assembly. Getter activation, outgassing control, lid seal yield.'),

    ('Test & characterization\n(spectroscopy, drift, thermal cycling)',
     6.0, '#ff8844',
     'Need atomic spectroscopy setup ($50k-$200k). Accelerated aging tests\n'
     'take months. PDF explicitly says test time is a "hidden COGS" driver.'),

    ('Defense qualification\n(MIL-STD environmental testing)',
     7.0, '#ff8833',
     'Thermal cycling, vibration, shock, humidity. Months of testing.\n'
     'PDF emphasizes DSB requires "realistic environment testing".'),
]

y_start = 0.89
for i, (name, diff, col, desc) in enumerate(subsystems):
    y = y_start - i * 0.074
    # Difficulty bar
    bar_width = diff / 10 * 0.22
    ax2.add_patch(FancyBboxPatch((0.01, y - 0.02), bar_width, 0.04,
                  boxstyle="round,pad=0.003", facecolor=col, edgecolor='none',
                  alpha=0.6, transform=ax2.transAxes))
    ax2.text(bar_width + 0.02, y, f'{diff}/10', fontsize=9, color=col,
             fontweight='bold', va='center', transform=ax2.transAxes)
    # Name
    ax2.text(0.28, y + 0.01, name, fontsize=8.5, color='white', fontweight='bold',
             va='top', transform=ax2.transAxes)
    # Description
    ax2.text(0.55, y, desc, fontsize=7.5, color='#aaaaaa',
             va='center', transform=ax2.transAxes)


# ════════════════════════════════════════════════════════════════
# 3. WHAT YOU NEED (facilities, equipment, people)
# ════════════════════════════════════════════════════════════════
ax3 = panel(gs[2], 'WHAT YOU ACTUALLY NEED TO BUILD THIS', '#44aaff')

categories = [
    ('FACILITIES', '#ff4444', [
        ('MEMS cleanroom (Class 100-1000)', '$2M-$20M to build, or $500-$2k/day to rent'),
        ('Anodic bonding station', '$200k-$500k (Suss, EVG)'),
        ('Atomic spectroscopy lab', '$50k-$200k (laser + optics + detectors)'),
        ('Vacuum bakeout oven', '$20k-$50k'),
        ('Environmental test chamber', '$30k-$100k (thermal cycling, vibration)'),
    ]),
    ('EQUIPMENT', '#ffaa00', [
        ('DRIE etcher (deep reactive ion etch)', '$500k-$2M, or use foundry'),
        ('Sputter / e-beam evaporator (Pt deposition)', '$200k-$500k, or use foundry'),
        ('ALD system (Al2O3 coating)', '$300k-$800k, or use foundry'),
        ('Photolithography aligner', '$100k-$500k, or use foundry'),
        ('Wire bonder / die bonder', '$50k-$200k'),
        ('Helium leak detector', '$15k-$40k'),
        ('RF signal generator (3.4 GHz)', '$5k-$30k'),
        ('Time-interval counter', '$10k-$50k'),
    ]),
    ('PEOPLE (minimum viable team)', '#00ff88', [
        ('MEMS process engineer', 'Cleanroom fab experience. HARDEST to hire.'),
        ('Atomic physicist / spectroscopist', 'CPT/EIT expertise. Usually PhD-level.'),
        ('RF/analog electronics engineer', '3.4 GHz oscillator + PID loop design.'),
        ('Packaging / reliability engineer', 'Vacuum packaging, hermeticity testing.'),
        ('Part-time: defense/export compliance', 'ITAR/EAR, if US-based.'),
    ]),
]

y = 0.90
for cat_name, cat_color, items in categories:
    ax3.text(0.02, y, cat_name, fontsize=12, color=cat_color, fontweight='bold',
             transform=ax3.transAxes)
    y -= 0.035
    for item_name, item_desc in items:
        ax3.text(0.05, y, '>', fontsize=10, color=cat_color, transform=ax3.transAxes)
        ax3.text(0.07, y, item_name, fontsize=9, color='white', fontweight='bold',
                 transform=ax3.transAxes)
        ax3.text(0.48, y, item_desc, fontsize=8.5, color='#888888',
                 transform=ax3.transAxes)
        y -= 0.032
    y -= 0.015

ax3.text(0.50, 0.03,
    'SHORTCUT: Use a MEMS foundry (MEMSCAP, STMicro, Silex, etc.) for fabrication.\n'
    'You design the cell + process recipe, they run the wafers. Cuts capital needs by 80%.\n'
    'The PDF recommends this approach: "start with bonding flows consistent with known anodic bonding approaches".',
    ha='center', fontsize=10, color='#00ff88',
    transform=ax3.transAxes,
    bbox=dict(boxstyle='round,pad=0.4', facecolor='#0a1a0a', edgecolor='#00ff88'))


# ════════════════════════════════════════════════════════════════
# 4. COST BREAKDOWN
# ════════════════════════════════════════════════════════════════
ax4 = panel(gs[3], 'COST BREAKDOWN (from the PDF + real-world estimates)', '#FFD700')

# Budget tiers from the PDF
tiers = [
    ('LOW\n$250k-$500k', '#ffaa00', [
        '1 wafer fabrication run (foundry)',
        'Bench spectroscopy setup',
        'Packaging experiments (small batch)',
        'Early drift characterization',
        '4-6 person-months of effort',
    ], 'Gets you: proof that YOUR cell design works.\nDoesn\'t get you: yield data, aging data, or a product.'),

    ('MEDIUM\n$750k-$1.8M', '#ff8844', [
        '2-3 fabrication iterations',
        '20-50 evaluation units built',
        'Accelerated aging campaign (months)',
        'At least one partner pilot',
        'Reference integration demo',
        '12-18 person-months of effort',
    ], 'Gets you: a real component with test data.\nCustomers can evaluate it. You know your yield and drift.'),

    ('HIGH\n$2.5M-$6M', '#ff4444', [
        'Pilot production line readiness',
        'Expanded environmental validation',
        'Supply-chain hardening',
        'Multi-partner pilots',
        'Defense qualification started',
        '30+ person-months of effort',
    ], 'Gets you: a product you can sell.\nQualified, tested, with a supply chain and customers.'),
]

for i, (tier_name, col, items, summary) in enumerate(tiers):
    x_start = 0.03 + i * 0.33
    ax4.text(x_start + 0.14, 0.88, tier_name, ha='center', fontsize=13, color=col,
             fontweight='bold', transform=ax4.transAxes)
    y_item = 0.77
    for item in items:
        ax4.text(x_start + 0.02, y_item, '> ' + item, fontsize=8.5, color='white',
                 transform=ax4.transAxes)
        y_item -= 0.055
    ax4.text(x_start + 0.14, 0.18, summary, ha='center', fontsize=8.5, color=col,
             transform=ax4.transAxes,
             bbox=dict(boxstyle='round,pad=0.3', facecolor='#111133', edgecolor=col, alpha=0.8))

# Dividers
for x_div in [0.335, 0.665]:
    ax4.plot([x_div, x_div], [0.1, 0.95], color='#333333', linewidth=1,
             linestyle='-', transform=ax4.transAxes)

ax4.text(0.50, 0.05,
    'Note from PDF: "wafer bonding yield and hermeticity screening" and "test and accelerated aging time"\n'
    'are HIDDEN COGS that most people underestimate. Budget 30% extra for things going wrong.',
    ha='center', fontsize=9, color='#ff8844', style='italic', transform=ax4.transAxes)


# ════════════════════════════════════════════════════════════════
# 5. THE TOP 5 WAYS THIS FAILS
# ════════════════════════════════════════════════════════════════
ax5 = panel(gs[4], 'THE TOP 5 WAYS THIS PROJECT FAILS', '#ff4444')

failures = [
    ('1. YOUR CELLS LEAK',
     'Probability: HIGH (this is the #1 killer)',
     'Anodic bonding yield is everything. A single pinhole = helium permeates in\n'
     '= buffer gas pressure changes = frequency drifts = dead clock.\n'
     'The 2025 hermeticity study exists BECAUSE this is a known unsolved problem.\n'
     'Your first 2-3 bonding runs will probably have >50% leak rate.',
     '#ff2222'),

    ('2. CONTAMINATION DURING FILLING',
     'Probability: HIGH',
     'Getting Rb atoms + N2 into a sub-mm cavity without contaminating the\n'
     'cell walls is incredibly hard. Residual gases (O2, H2O) from outgassing\n'
     'react with Rb and destroy the CPT signal. The PDF explicitly flags\n'
     '"coatings/getters/bake/clean protocols" as the primary mitigation.',
     '#ff4444'),

    ('3. DRIFT IS WORSE THAN EXPECTED',
     'Probability: MEDIUM-HIGH',
     'Even a "working" cell can have unpredictable long-term drift from:\n'
     '  - Slow outgassing from cell walls\n'
     '  - Rb reacting with glass surfaces\n'
     '  - Buffer gas pressure creeping\n'
     'You won\'t know your drift for MONTHS (accelerated aging needed).\n'
     'The PDF says this "makes life-cycle cost unpredictable".',
     '#ff6644'),

    ('4. YOU CAN\'T FIND THE PEOPLE',
     'Probability: MEDIUM',
     'You need someone who knows MEMS fab AND atomic physics AND can do RF\n'
     'electronics. This person barely exists. The Venn diagram of "cleanroom\n'
     'experience" + "CPT spectroscopy" + "willing to work at a startup" is tiny.\n'
     'University labs are your best recruiting ground, but they move slowly.',
     '#ff8844'),

    ('5. PATENTS BLOCK YOU',
     'Probability: MEDIUM',
     'The PDF warns about TWO patent clusters: vapor-cell manufacturing\n'
     'process claims (anodic bonding variations) and laminated cell structures.\n'
     'A 2024 granted patent covers specific bonding design choices.\n'
     'You MUST do FTO (freedom-to-operate) screening early or risk being\n'
     'designed into a corner you can\'t ship from.',
     '#ffaa44'),
]

y = 0.88
for title, prob, desc, col in failures:
    ax5.text(0.02, y, title, fontsize=12, color=col, fontweight='bold',
             transform=ax5.transAxes)
    ax5.text(0.02, y - 0.025, prob, fontsize=9, color=col, style='italic',
             transform=ax5.transAxes)
    ax5.text(0.02, y - 0.05, desc, fontsize=8.5, color='#aaaaaa',
             transform=ax5.transAxes, va='top')
    y -= 0.19


# ════════════════════════════════════════════════════════════════
# 6. TIMELINE (realistic)
# ════════════════════════════════════════════════════════════════
ax6 = panel(gs[5], 'REALISTIC TIMELINE (from the PDF\'s own Gantt chart)', '#00ccff')

# Gantt chart based on PDF's timeline
phases = [
    ('Requirements + partner interviews', 0, 1.0, '#44aaff'),
    ('Foundry/MPW design + first fab run', 1, 3.0, '#ff8844'),
    ('Wafer bonding + packaging iteration 1', 2, 2.0, '#ff4444'),
    ('Alkali filling + bakeout development', 2.5, 3.0, '#ff2222'),
    ('Spectroscopy + thermal control demo', 4, 1.5, '#ffaa00'),
    ('Reference design integration', 5, 3.0, '#aa44ff'),
    ('Accelerated aging + drift model v1', 5.5, 4.0, '#ff8844'),
    ('Pilot evaluation units (20-50)', 7, 2.5, '#00ff88'),
    ('Partner LOI / pilot decision gate', 9, 0.5, '#FFD700'),
    ('Scale + qualification plan', 9.5, 0.7, '#FFD700'),
]

y_gantt = 0.85
for name, start_month, duration, col in phases:
    x_start = 0.08 + start_month / 12 * 0.70
    x_width = duration / 12 * 0.70
    ax6.add_patch(FancyBboxPatch((x_start, y_gantt - 0.015), x_width, 0.04,
                  boxstyle="round,pad=0.003", facecolor=col, edgecolor='white',
                  linewidth=0.8, alpha=0.6, transform=ax6.transAxes))
    ax6.text(x_start + x_width + 0.01, y_gantt + 0.005, name,
             fontsize=8, color='white', va='center', transform=ax6.transAxes)
    y_gantt -= 0.065

# Month markers
for m in range(0, 13, 3):
    x_m = 0.08 + m / 12 * 0.70
    ax6.plot([x_m, x_m], [0.15, 0.90], color='#333333', linewidth=0.5,
             linestyle=':', transform=ax6.transAxes)
    ax6.text(x_m, 0.13, f'Month {m}', fontsize=7, color='#888888',
             ha='center', transform=ax6.transAxes)

# Decision gates
for m, label, col in [(5, 'GATE A\nPhysics works?', '#ffaa00'),
                        (9, 'GATE B\nBuyer interest?', '#00ff88')]:
    x_g = 0.08 + m / 12 * 0.70
    ax6.plot([x_g, x_g], [0.15, 0.90], color=col, linewidth=2,
             alpha=0.5, transform=ax6.transAxes)
    ax6.text(x_g, 0.10, label, fontsize=8, color=col, ha='center',
             fontweight='bold', transform=ax6.transAxes)

ax6.text(0.50, 0.03,
    'PDF: "Achievable with staged risk: prototype early with reference integration, then iterate on packaging and drift."',
    ha='center', fontsize=9.5, color='#00ccff', style='italic', transform=ax6.transAxes)


# ════════════════════════════════════════════════════════════════
# 7. BUY vs BUILD DECISION
# ════════════════════════════════════════════════════════════════
ax7 = panel(gs[6], 'BUY vs BUILD: Should you even attempt this?', '#aa44ff')

options = [
    ('BUY A CSAC MODULE\n(e.g., Microchip SA65)', '#44aaff',
     0.03, [
         ('Cost', '$2,712 per unit (5k qty)'),
         ('Time to deploy', 'Weeks (order and integrate)'),
         ('Difficulty', '2/10 (integration only)'),
         ('Performance', 'Known: <120mW, <17cc, ~1e-10 ADEV'),
         ('Differentiation', 'ZERO (same part your competitor buys)'),
         ('Supply risk', 'Single source (Microchip). They can raise prices,\ndiscontinue, or restrict exports.'),
         ('IP ownership', 'None. You own nothing.'),
     ]),
    ('BUILD THE VAPOR CELL CORE\n(what the PDF recommends)', '#00ff88',
     0.36, [
         ('Cost', '$250k-$6M development. $180-$650 per unit at scale.'),
         ('Time to deploy', '12-18 months to prototype. 24-36 months to product.'),
         ('Difficulty', '8.5/10'),
         ('Performance', 'Unknown until you build it. Could be better OR worse.'),
         ('Differentiation', 'HIGH. Your own vapor cell = your own performance.\nCustomers pay for drift predictability + ruggedness.'),
         ('Supply risk', 'YOU control it. Sovereign supply chain if needed.\nEU/UK defense explicitly want this (PDF cites EU factsheet).'),
         ('IP ownership', 'Full. Process know-how + potential patents.'),
     ]),
    ('PARTNER WITH A LAB\n(license university research)', '#ffaa00',
     0.69, [
         ('Cost', '$50k-$300k licensing + your own packaging effort.'),
         ('Time to deploy', '6-12 months to working cell (with their recipe).'),
         ('Difficulty', '5-6/10 (de-risked recipe, but you still package it)'),
         ('Performance', 'Proven in lab. Unproven in YOUR packaging.'),
         ('Differentiation', 'MEDIUM. Shared IP. Others can license too.'),
         ('Supply risk', 'Depends on lab relationship. Export/jurisdiction issues.'),
         ('IP ownership', 'Shared or licensed. Constraints depend on terms.'),
     ]),
]

for opt_name, col, x_start, items in options:
    ax7.text(x_start + 0.14, 0.90, opt_name, ha='center', fontsize=11, color=col,
             fontweight='bold', transform=ax7.transAxes)
    y_item = 0.80
    for item_name, item_val in items:
        ax7.text(x_start + 0.01, y_item, item_name + ':', fontsize=8, color=col,
                 fontweight='bold', transform=ax7.transAxes)
        ax7.text(x_start + 0.01, y_item - 0.03, item_val, fontsize=8, color='#aaaaaa',
                 transform=ax7.transAxes)
        y_item -= 0.075

# Dividers
for x_div in [0.34, 0.67]:
    ax7.plot([x_div, x_div], [0.05, 0.95], color='#333333', linewidth=1,
             linestyle='-', transform=ax7.transAxes)

ax7.text(0.50, 0.03,
    'PDF\'s recommendation: BUILD the core, BUY everything else (VCSEL, optics, detector).\n'
    'Position as a "component supplier" to timing integrators, not a full-module competitor to Microchip.',
    ha='center', fontsize=10, color='#aa44ff', fontweight='bold',
    transform=ax7.transAxes,
    bbox=dict(boxstyle='round,pad=0.3', facecolor='#111133', edgecolor='#aa44ff'))


# ════════════════════════════════════════════════════════════════
# 8. SKILLS GAP REALITY CHECK
# ════════════════════════════════════════════════════════════════
ax8 = panel(gs[7], 'SKILLS GAP: The knowledge you need (and probably don\'t have)', '#ff8844')

skills = [
    ('MEMS fabrication\n(Si etching, lithography, bonding)', 9, '#ff4444',
     'PhD or 5+ years in MEMS foundry. Knows DRIE recipes, bonding parameters,\n'
     'wafer handling. You CANNOT learn this from YouTube. Need hands-on cleanroom time.'),
    ('Atomic / quantum physics\n(CPT, spectroscopy, Rb vapor)', 8, '#ff6644',
     'PhD in atomic physics or quantum optics. Understands dark states, density\n'
     'matrices, buffer gas physics. Very few people outside universities have this.'),
    ('Vacuum / packaging engineering\n(hermetic sealing, getters, outgassing)', 7, '#ff8844',
     'Industrial experience with vacuum electronics or MEMS packaging. Knows\n'
     'leak testing (He), getter activation, clean assembly. Aerospace/space background helps.'),
    ('RF electronics design\n(3.4 GHz oscillator, frequency synthesis)', 6, '#ffaa00',
     'RF PCB design at 3-4 GHz. Phase noise optimization. PLL/frequency synthesis.\n'
     'More available than MEMS/physics people, but still specialized.'),
    ('Control systems\n(PID thermal, frequency lock loops)', 5, '#ffcc00',
     'Standard control engineering + some analog electronics. Most EE grads can\n'
     'learn this. The thermal PID is straightforward; the frequency lock needs care.'),
    ('Defense procurement / ITAR\n(export controls, qualification)', 4, '#88ff44',
     'Can be hired as consultant. Needed if selling to US/UK/EU defense.\n'
     'PDF warns about export control constraints on customer set and demos.'),
    ('Optics (basic alignment, polarization)', 3, '#44ff44',
     'Quarter-wave plate alignment, beam shaping. Lab optics skills.\n'
     'Most physics undergrads can do this. Not a bottleneck.'),
]

y_sk = 0.88
for skill_name, difficulty, col, desc in skills:
    # Skill bar
    bar_w = difficulty / 10 * 0.20
    ax8.add_patch(FancyBboxPatch((0.01, y_sk - 0.015), bar_w, 0.035,
                  boxstyle="round,pad=0.003", facecolor=col, edgecolor='none',
                  alpha=0.6, transform=ax8.transAxes))
    ax8.text(bar_w + 0.02, y_sk + 0.002, f'{difficulty}/10', fontsize=9, color=col,
             fontweight='bold', va='center', transform=ax8.transAxes)
    ax8.text(0.26, y_sk + 0.008, skill_name, fontsize=9, color='white', fontweight='bold',
             va='top', transform=ax8.transAxes)
    ax8.text(0.48, y_sk + 0.002, desc, fontsize=7.5, color='#888888',
             va='center', transform=ax8.transAxes)
    y_sk -= 0.115

ax8.text(0.50, 0.06,
    'REALITY: You need at minimum 2-3 people who overlap MEMS + atomic physics + packaging.\n'
    'These people mostly exist at NIST, DARPA-funded labs, or Microchip\'s clock division.\n'
    'The PDF suggests partnering with national labs / universities as a source of IP and talent.',
    ha='center', fontsize=9.5, color='#ff8844',
    transform=ax8.transAxes,
    bbox=dict(boxstyle='round,pad=0.3', facecolor='#1a0a0a', edgecolor='#ff8844'))


# ════════════════════════════════════════════════════════════════
# 9. FINAL VERDICT
# ════════════════════════════════════════════════════════════════
ax9 = panel(gs[8], 'FINAL VERDICT', '#00ff88')

ax9.text(0.50, 0.75,
    'IS IT POSSIBLE?     YES.  The physics is proven. 95,000+ CSACs already sold.\n\n'
    'IS IT EASY?            NO.  This is elite-level hardware engineering.\n\n'
    'IS IT WORTH IT?     DEPENDS on your goal:',
    ha='center', fontsize=13, color='white', fontweight='bold',
    transform=ax9.transAxes)

verdicts = [
    ('If you want to USE a CSAC:', 'Just buy one. $2,700 from Microchip. Done in a week.', '#44aaff'),
    ('If you want to IMPROVE the core:', 'Partner with a university. $100k-$300k. 6-12 months.', '#ffaa00'),
    ('If you want to OWN the technology:', 'Build it. $500k-$2M. 18+ months. Hire from NIST/DARPA labs.', '#ff8844'),
    ('If you want a DEFENSE BUSINESS:', 'Full build + qualify. $2M-$6M. 24-36 months. But the market pays $1k+/unit.', '#ff4444'),
]

y_v = 0.52
for label, answer, col in verdicts:
    ax9.text(0.08, y_v, label, fontsize=11, color=col, fontweight='bold',
             transform=ax9.transAxes)
    ax9.text(0.45, y_v, answer, fontsize=11, color='white',
             transform=ax9.transAxes)
    y_v -= 0.08

ax9.text(0.50, 0.12,
    'The PDF\'s own recommendation: build the VAPOR CELL CORE only (not the full module).\n'
    'Sell it as a qualified subassembly to timing integrators like Microchip, Teledyne, or AccuBeat.\n'
    'This is the NARROWEST, CHEAPEST path that still builds defensible IP and captures value.\n'
    'Start at $250k, prove the physics, then raise to $2M+ when you have data.',
    ha='center', fontsize=11, color='#00ff88', fontweight='bold',
    transform=ax9.transAxes,
    bbox=dict(boxstyle='round,pad=0.6', facecolor='#0a1a0a', edgecolor='#00ff88', linewidth=2))


plt.savefig('csac_difficulty.png', dpi=130, facecolor=fig.get_facecolor(),
            bbox_inches='tight')
plt.show()
print("Saved to csac_difficulty.png")
