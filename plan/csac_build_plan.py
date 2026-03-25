"""
BLOCK-BY-BLOCK BUILD PLAN: MEMS Vapor-Cell CSAC Core

Based on patent analysis: CSAC has clear FTO. Gyroscope is patent-blocked.
This is the step-by-step plan to build the vapor cell core component.
Organized as 12 blocks, each with: what to do, how long, cost, risk, and go/no-go gate.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

fig = plt.figure(figsize=(22, 58), facecolor='#0a0a1a')

gs = GridSpec(14, 1, figure=fig, hspace=0.06,
              left=0.03, right=0.97, top=0.99, bottom=0.003)

fig.text(0.5, 0.997,
    'BLOCK-BY-BLOCK BUILD PLAN: MEMS Vapor-Cell CSAC Core',
    ha='center', fontsize=20, fontweight='bold', color='white')
fig.text(0.5, 0.9945,
    'Patent-clear path  |  12 blocks  |  $250k-$500k Phase 1  |  12-18 months to working prototype',
    ha='center', fontsize=11, color='#00ff88')


def block_panel(gs_slot, block_num, title, duration, cost, difficulty, color,
                what_to_do, deliverable, risk, gate, tools_needed):
    ax = fig.add_subplot(gs_slot, facecolor='#0d0d20')
    for sp in ax.spines.values():
        sp.set_edgecolor(color)
        sp.set_linewidth(2)
    ax.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)

    # Header bar
    ax.add_patch(FancyBboxPatch((0.005, 0.75), 0.99, 0.24,
                 boxstyle="round,pad=0.01", facecolor=color, alpha=0.15,
                 edgecolor='none', transform=ax.transAxes))

    # Block number
    ax.text(0.01, 0.92, f'BLOCK {block_num}', fontsize=14, fontweight='bold',
            color='#0d0d20', transform=ax.transAxes,
            bbox=dict(boxstyle='round,pad=0.3', facecolor=color, edgecolor='none'))
    ax.text(0.12, 0.92, title, fontsize=14, fontweight='bold', color=color,
            transform=ax.transAxes)

    # Metrics
    ax.text(0.62, 0.92, f'Duration: {duration}', fontsize=10, color='white',
            transform=ax.transAxes)
    ax.text(0.62, 0.84, f'Cost: {cost}', fontsize=10, color='#FFD700',
            transform=ax.transAxes)
    ax.text(0.82, 0.92, f'Difficulty: {difficulty}/10', fontsize=10, color=color,
            transform=ax.transAxes)

    # Difficulty bar
    bar_w = difficulty / 10 * 0.15
    ax.add_patch(FancyBboxPatch((0.82, 0.84), bar_w, 0.04,
                 boxstyle="round,pad=0.003", facecolor=color, edgecolor='none',
                 alpha=0.6, transform=ax.transAxes))

    # What to do
    ax.text(0.01, 0.76, 'WHAT TO DO:', fontsize=9, color=color,
            fontweight='bold', transform=ax.transAxes)
    ax.text(0.01, 0.70, what_to_do, fontsize=9, color='white',
            transform=ax.transAxes, va='top')

    # Deliverable
    ax.text(0.55, 0.76, 'DELIVERABLE:', fontsize=9, color='#00ff88',
            fontweight='bold', transform=ax.transAxes)
    ax.text(0.55, 0.70, deliverable, fontsize=9, color='#00ff88',
            transform=ax.transAxes, va='top')

    # Risk
    ax.text(0.01, 0.30, 'RISK:', fontsize=9, color='#ff4444',
            fontweight='bold', transform=ax.transAxes)
    ax.text(0.06, 0.30, risk, fontsize=8.5, color='#ff8888',
            transform=ax.transAxes, va='top')

    # Tools needed
    ax.text(0.01, 0.12, 'TOOLS/ACCESS:', fontsize=9, color='#44aaff',
            fontweight='bold', transform=ax.transAxes)
    ax.text(0.13, 0.12, tools_needed, fontsize=8.5, color='#88aacc',
            transform=ax.transAxes, va='top')

    # Gate
    ax.text(0.55, 0.30, 'GO/NO-GO GATE:', fontsize=9, color='#FFD700',
            fontweight='bold', transform=ax.transAxes)
    ax.text(0.55, 0.22, gate, fontsize=9, color='#FFD700',
            transform=ax.transAxes, va='top')

    # Arrow to next
    ax.annotate('', xy=(0.5, 0.01), xytext=(0.5, 0.06),
                xycoords='axes fraction', textcoords='axes fraction',
                arrowprops=dict(arrowstyle='->', color='white', lw=2))
    return ax


# ─── IP HEADER ───
ax_ip = fig.add_subplot(gs[0], facecolor='#0d0d20')
for sp in ax_ip.spines.values():
    sp.set_edgecolor('#00ff88')
    sp.set_linewidth(2)
ax_ip.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)

ax_ip.text(0.50, 0.85, 'WHY BUILD THE CSAC (NOT THE GYROSCOPE)?  --  PATENT ANALYSIS RESULT',
           ha='center', fontsize=14, fontweight='bold', color='#00ff88', transform=ax_ip.transAxes)

ax_ip.text(0.02, 0.65,
    'SiC BAW GYROSCOPE:  Georgia Tech/Ayazi owns ~50 patents. US 12,407,322 (granted 2025, expires 2039)\n'
    'specifically claims 4H-SiC resonators on phononic crystal substrates. You CANNOT build a competitive\n'
    'SiC gyroscope without a license from Georgia Tech. The fundamental BAW patent expires Feb 2027, but\n'
    'the SiC-specific claims block the high-performance path until 2039.',
    fontsize=10, color='#ff4444', transform=ax_ip.transAxes,
    bbox=dict(boxstyle='round,pad=0.3', facecolor='#1a0a0a', edgecolor='#ff4444'))

ax_ip.text(0.02, 0.22,
    'CSAC VAPOR CELL CORE:  Foundational CSAC patent (Sarnoff) is ABANDONED. All cited patents are narrow\n'
    'and avoidable (NIST = all-glass only, QVIL = tabbed arrays only, AccuBeat = anti-spoof apparatus only).\n'
    'Honeywell dual-chamber patent avoidable with single-chamber design. TI filling patent avoidable with\n'
    'alternative alkali dispensing. Multiple documented design-around paths for EVERY claim cluster.\n'
    'CLEAR FREEDOM TO OPERATE.',
    fontsize=10, color='#00ff88', transform=ax_ip.transAxes,
    bbox=dict(boxstyle='round,pad=0.3', facecolor='#0a1a0a', edgecolor='#00ff88'))


# ─── BLOCK 1 ───
block_panel(gs[1], 1,
    'FTO Screening + Cell Architecture Design',
    '4 weeks', '$5k-$15k', 3, '#44aaff',
    'Hire a patent attorney for a focused FTO search on YOUR specific cell design.\n'
    'Choose: single-chamber glass-Si-glass (avoids Honeywell dual-chamber claims).\n'
    'Choose filling method: wax micro-packet or direct Rb pipetting in glove box\n'
    '(avoids TI azide-capillary patent). Choose bonding: standard anodic OR indium\n'
    'thermocompression (avoids any anodic-bonding-specific claims).\n'
    'Design the mask set: cavity geometry, heater traces, RTD sensor layout.',
    'Cell architecture document\n'
    'Mask layout (GDS-II)\n'
    'FTO opinion letter\n'
    'Foundry selection shortlist',
    'Patent attorney finds a blocking claim you missed.\n'
    'Mitigation: design flexibility at this stage is maximum.',
    'FTO opinion says GO.\n'
    'If any blocking patent found,\n'
    'redesign before spending money.',
    'Patent attorney, KLayout/L-Edit CAD, literature access')


# ─── BLOCK 2 ───
block_panel(gs[2], 2,
    'Foundry Selection + First Wafer Run',
    '6-8 weeks', '$30k-$70k', 5, '#ff8844',
    'Contact MEMS foundries: MEMSCAP (US/FR), Silex (SE), STMicro (FR/IT),\n'
    'or university fabs (e.g., EPFL CMi, TU Delft). Send your GDS-II masks.\n'
    'Process: (a) DRIE etch Si wafer to create cavities (~1mm deep),\n'
    '(b) sputter Pt thin-film for heaters + RTD sensor, (c) pattern with photolithography,\n'
    '(d) deposit Al2O3 anti-permeation coating via ALD.\n'
    'Order borosilicate glass wafers (Schott Borofloat 33 or similar).\n'
    'This is a multi-project wafer (MPW) run -- share cost with other users.',
    'Processed Si wafers (10-25 dies)\n'
    'Patterned Pt heaters/sensors\n'
    'Al2O3 coated cavity walls\n'
    'Glass wafers ready for bonding',
    'Foundry turnaround time can slip 2-4 weeks.\n'
    'DRIE depth uniformity across wafer may vary.\n'
    'Mitigation: order 2x more dies than you need.',
    'Wafers received and inspected.\n'
    'Cavity depth within +/- 5%.\n'
    'Pt traces electrically continuous.',
    'MEMS foundry access, profilometer, multimeter')


# ─── BLOCK 3 ───
block_panel(gs[3], 3,
    'Anodic Bonding: Seal Bottom Glass to Silicon',
    '3-4 weeks', '$10k-$25k', 7, '#ff4444',
    'Bond the first (bottom) glass wafer to the silicon wafer using anodic bonding:\n'
    '  - Clean both wafers (RCA clean or piranha etch)\n'
    '  - Align glass wafer to Si wafer on bonding chuck\n'
    '  - Heat to 350-400 C, apply 400-800V DC\n'
    '  - Na+ ions drift, depletion layer forms, Si-O covalent bond forms\n'
    '  - Cool down, inspect bond quality\n'
    'Use helium leak detector to test hermeticity of bonded wafer pair.\n'
    'Target: leak rate < 1e-10 atm*cc/s.\n'
    'If using indium bonding alternative: deposit In, align, press at 180 C.',
    'Bonded Si-glass wafer pairs\n'
    'Hermeticity test results\n'
    'Bond yield percentage\n'
    '(target: >70% good dies)',
    'THIS IS THE FIRST CRITICAL STEP.\n'
    'Bad bonds = leaking cells = dead project.\n'
    'First run may have <50% yield. Normal.\n'
    'Mitigation: iterate bonding parameters (T, V, time).',
    'All dies pass He leak test.\n'
    'If <50% yield, iterate parameters\n'
    'before proceeding.\n'
    'DO NOT SKIP THIS GATE.',
    'Anodic bonder (Suss SB6/8, or EVG), He leak detector, clean bench')


# ─── BLOCK 4 ───
block_panel(gs[4], 4,
    'Alkali Filling: Get Rb + N2 Into the Cavity',
    '4-6 weeks', '$15k-$30k', 9, '#ff0000',
    'THE HARDEST STEP IN THE ENTIRE PROJECT.\n'
    'Option A -- Direct dispensing (patent-safe, simpler):\n'
    '  1. Work inside nitrogen-purged glove box (O2 < 1 ppm, H2O < 1 ppm)\n'
    '  2. Place micro-droplet of Rb metal into each cavity using micropipette\n'
    '  3. Backfill chamber with N2 buffer gas at target pressure (30-75 Torr)\n'
    '  4. Immediately proceed to top glass bonding (Block 5)\n'
    'Option B -- Rb azide photolysis (established, but check TI patent):\n'
    '  1. Deposit RbN3 into cavity\n'
    '  2. Seal cell, then UV-decompose RbN3 -> Rb + N2\n'
    '  3. Advantage: N2 generated in-situ at controlled amount\n'
    'CRITICAL: Any contamination (O2, H2O) will react with Rb and kill the signal.',
    'Filled cavities with Rb metal visible\n'
    'N2 pressure at target (measured\n'
    'via absorption spectroscopy later)\n'
    'No visible oxidation of Rb',
    'Contamination is the #1 killer.\n'
    'Rb amount too little = weak signal.\n'
    'Rb amount too much = opaque cell.\n'
    'N2 pressure wrong = wrong linewidth.\n'
    'Mitigation: fill 20+ cavities, test all.',
    'Visual inspection shows clean Rb\n'
    'metal in cavities.\n'
    'No white/grey oxide films visible.\n'
    'Proceed to sealing IMMEDIATELY.',
    'N2 glove box ($15k-$30k), Rb metal ampule ($200), micropipette, UV lamp')


# ─── BLOCK 5 ───
block_panel(gs[5], 5,
    'Top Glass Bonding: Seal the Cell',
    '2-3 weeks', '$10k-$20k', 8, '#ff2222',
    'Bond the top glass wafer to seal the Rb + N2 inside the silicon cavity.\n'
    'This MUST happen inside the glove box or controlled atmosphere:\n'
    '  - Align top glass wafer on filled Si wafer\n'
    '  - Perform anodic bonding at 350C / 400V (or In bonding at 180C)\n'
    '  - The cell is now hermetically sealed\n'
    'After bonding, dice the wafer into individual cell dies.\n'
    'Each die is one vapor cell (~2mm x 2mm x 2mm).\n'
    'Test hermeticity of EACH die with He leak detector.',
    'Individual sealed vapor cell dies\n'
    'He leak test results per die\n'
    'Yield count: good cells / total cells',
    'Bonding at elevated T can cause Rb to redistribute.\n'
    'Rb may condense on glass windows = optically blocked.\n'
    'Mitigation: control temperature gradient during bonding\n'
    'so Rb stays in cavity body, not on windows.',
    'He leak rate < 1e-10 for each die.\n'
    'At least 10 good cells from this\n'
    'batch to proceed to testing.\n'
    'If <10 good cells: re-run Block 3-5.',
    'Anodic bonder (in glove box or loadlock), dicing saw, He leak detector')


# ─── BLOCK 6 ───
block_panel(gs[6], 6,
    'First Light: Bench Spectroscopy Test',
    '3-4 weeks', '$20k-$40k', 6, '#ffaa00',
    'THIS IS WHERE YOU FIND OUT IF YOUR CELL WORKS.\n'
    'Set up a bench-top CPT spectroscopy rig:\n'
    '  1. Mount one sealed cell die on a temperature-controlled stage\n'
    '  2. Heat to 85C using external heater (not on-chip yet)\n'
    '  3. Shine a 795nm VCSEL laser through the cell\n'
    '  4. Modulate VCSEL at 3.417 GHz\n'
    '  5. Scan modulation frequency and look for CPT transparency peak\n'
    '  6. Measure: peak contrast, linewidth, signal-to-noise ratio\n'
    'If you see a CPT peak: YOUR CELL WORKS. Celebrate.\n'
    'If no peak: diagnose (Rb contaminated? N2 pressure wrong? Cell leaking?).',
    'CPT spectroscopy data\n'
    'Peak contrast (target: >3%)\n'
    'Linewidth (target: <5 kHz)\n'
    'PROOF YOUR CELL WORKS',
    'No CPT peak = Rb is contaminated or absent.\n'
    'Peak is there but broad = N2 pressure is wrong.\n'
    'Peak is there but weak = not enough Rb atoms.\n'
    'Mitigation: this is why you made 10+ cells.',
    'CPT peak observed with\n'
    'contrast > 3% and\n'
    'linewidth < 10 kHz.\n'
    'THIS IS THE #1 GO/NO-GO GATE.',
    'VCSEL (795nm), RF signal generator (3.4 GHz), photodetector, lock-in amp, temp controller')


# ─── BLOCK 7 ───
block_panel(gs[7], 7,
    'On-Chip Thermal Control: Test the Pt Heaters',
    '2-3 weeks', '$5k-$10k', 4, '#44aaff',
    'Now test the integrated Pt heaters and RTD sensor on your working cells:\n'
    '  1. Wire-bond to the Pt heater pads and RTD pads\n'
    '  2. Measure RTD resistance vs temperature (calibrate)\n'
    '  3. Apply current to heaters, verify cell reaches 85C\n'
    '  4. Implement PID controller (Arduino/FPGA is fine for prototype)\n'
    '  5. Demonstrate stable 85C +/- 0.1C control\n'
    '  6. Repeat CPT spectroscopy using ON-CHIP heating\n'
    '  7. Compare signal quality: external heater vs on-chip heater',
    'PID thermal control working\n'
    'RTD calibration curve\n'
    'Heater power consumption (mW)\n'
    'CPT signal with on-chip heating',
    'Pt traces may have breaks (open circuit) from bonding.\n'
    'Heater power may be insufficient to reach 85C.\n'
    'Mitigation: have backup cells, check traces before filling.',
    '85C reached with <100mW heater\n'
    'power. PID holds +/- 0.1C.\n'
    'CPT signal comparable to\n'
    'external-heater result.',
    'Wire bonder, SMU (source-measure unit), Arduino/FPGA, PID code')


# ─── BLOCK 8 ───
block_panel(gs[8], 8,
    'Frequency Lock Loop: Lock to the Atom',
    '4-6 weeks', '$10k-$20k', 6, '#ffaa00',
    'Build the electronics that lock a local oscillator to the CPT peak:\n'
    '  1. 3.417 GHz voltage-controlled oscillator (VCO) -- COTS part\n'
    '  2. Frequency modulation to dither across CPT peak\n'
    '  3. Lock-in amplifier (analog or digital) to extract error signal\n'
    '  4. PID controller to feed correction back to VCO\n'
    '  5. Verify lock: oscillator stays on CPT peak for hours\n'
    '  6. Measure short-term Allan deviation (1s, 10s, 100s)\n'
    'Target: ADEV < 5e-10 at 1 second averaging time.\n'
    'This is your CLOCK. If it locks, you have an atomic clock.',
    'Locked oscillator output (6.835 GHz)\n'
    'Allan deviation measurements\n'
    'Lock stability over 1+ hours\n'
    'YOU HAVE A WORKING CLOCK',
    'RF design at 3.4 GHz is tricky (PCB parasitics).\n'
    'Lock may oscillate or lose lock.\n'
    'Mitigation: start with commercial lock-in amp,\n'
    'then miniaturize to custom PCB.',
    'ADEV < 5e-10 at tau = 1s.\n'
    'Lock holds for >1 hour without\n'
    'manual intervention.\n'
    'THIS IS THE SECOND MAJOR GATE.',
    'VCO (3.4 GHz), lock-in amplifier, frequency counter, stable RF source')


# ─── BLOCK 9 ───
block_panel(gs[9], 9,
    'Vacuum Packaging: The Final Housing',
    '4-6 weeks', '$15k-$30k', 7, '#ff8844',
    'Package the working cell + optics + VCSEL + detector into a hermetic\n'
    'vacuum module:\n'
    '  1. Choose LCC (leadless chip carrier) ceramic package\n'
    '  2. Mount VCSEL on bottom of package\n'
    '  3. Mount quarter-wave plate above VCSEL\n'
    '  4. Mount vapor cell above QWP\n'
    '  5. Mount photodetector above cell\n'
    '  6. Wire-bond all electrical connections\n'
    '  7. Activate getter material (absorbs residual gas)\n'
    '  8. Seal lid in vacuum (<0.01 mbar)\n'
    'The vacuum insulation reduces heater power from >1W to ~50mW.',
    'Sealed CSAC physics package\n'
    'in LCC ceramic housing\n'
    'Vacuum level verified\n'
    'Heater power measured (<100mW)',
    'Getter activation may outgas onto Rb cell.\n'
    'Alignment of VCSEL-cell-detector stack is critical.\n'
    'Mitigation: use alignment jig, test optical path before sealing.',
    'Sealed package maintains vacuum.\n'
    'CPT signal visible through package.\n'
    'Heater power < 100 mW at 85C.',
    'LCC packages, getter material, vacuum sealing station, alignment jig')


# ─── BLOCK 10 ───
block_panel(gs[10], 10,
    'Accelerated Aging: Prove It Lasts',
    '8-12 weeks', '$10k-$20k', 5, '#44aaff',
    'Run your packaged CSAC units at elevated temperature (95-105C) to\n'
    'accelerate aging and predict long-term drift:\n'
    '  1. Place 5-10 units in thermal chamber at 95C\n'
    '  2. Measure frequency drift daily for 2-3 months\n'
    '  3. Use Arrhenius model to extrapolate room-temperature lifetime\n'
    '  4. Characterize drift rate (target: <1e-10 per month)\n'
    '  5. Build drift model: drift(t, T) = f(time, temperature)\n'
    '  6. This data is your "evidence package" for customers\n'
    'Simultaneously: thermal cycle 5 units (-40C to +80C, 100 cycles)\n'
    'to verify survivability.',
    'Drift model with data\n'
    'Thermal cycling pass/fail\n'
    'Projected lifetime estimate\n'
    'Customer-ready test report',
    'Drift may be worse than expected.\n'
    'Some cells may fail during cycling.\n'
    'Mitigation: this is why you test 10 units,\n'
    'not 1. Statistical confidence needs N > 5.',
    'Drift rate < 1e-10/month.\n'
    'At least 80% survive thermal cycling.\n'
    'Lifetime projection > 5 years.',
    'Thermal chamber, frequency counter (long-term stable), data logger')


# ─── BLOCK 11 ───
block_panel(gs[11], 11,
    'Reference Integration Demo',
    '4-6 weeks', '$10k-$20k', 4, '#00ff88',
    'Build a demo that shows your CSAC core working in a real scenario:\n'
    '  "Assured timing through GNSS outage" (from the PDF):\n'
    '  1. Set up a bench GPS receiver disciplined to your CSAC\n'
    '  2. Run normally with GPS for 1 hour (sync and calibrate)\n'
    '  3. DISCONNECT GPS (simulate jamming)\n'
    '  4. Show time error growth: CSAC holdover vs quartz-only holdover\n'
    '  5. Log and display on dashboard\n'
    '  6. Use DARPA ROCkN public framing: "nanoseconds of time error\n'
    '     = meters of position error" (safe, non-classified messaging)\n'
    'This demo is what you show to defense buyers and timing integrators.',
    'Working holdover demo\n'
    'Dashboard showing CSAC\n'
    'vs quartz drift in real time\n'
    'Video/screenshots for pitch deck',
    'Low risk at this stage -- it is a demo of\n'
    'already-working hardware.\n'
    'Make sure the quartz baseline is fair\n'
    '(use a real TCXO, not a terrible crystal).',
    'Demo shows CSAC holdover\n'
    'significantly better than TCXO\n'
    'after 1+ hour of GPS denial.',
    'GPS receiver, TCXO module, laptop with dashboard software, video camera')


# ─── BLOCK 12 ───
block_panel(gs[12], 12,
    'Customer Discovery + Eval Unit Shipment',
    '6-8 weeks', '$5k-$15k', 3, '#00ff88',
    'Take your demo + test data to potential buyers:\n'
    '  1. Timing-module vendors (they integrate your cell into their clock)\n'
    '  2. RF/comm subsystem primes (need assured timing)\n'
    '  3. Military labs (evaluate for specific platforms)\n'
    '  4. Ship 5-10 evaluation units with test data package\n'
    '  5. Collect feedback: what specs matter? what needs improving?\n'
    '  6. Get LOIs (Letters of Intent) contingent on drift/robustness data\n'
    'PDF recommends: approach via DIU (Defense Innovation Unit) for rapid\n'
    'procurement. Other Transaction awards can lead to production contracts.',
    'Eval units shipped (5-10)\n'
    'Customer feedback collected\n'
    'At least 1 LOI received\n'
    'Decision: iterate or scale?',
    'Customers may want specs you cannot hit yet.\n'
    'Export controls may limit who you can sell to.\n'
    'Mitigation: start with non-classified applications.\n'
    'Get ITAR/EAR guidance before first customer contact.',
    'At least 1 customer willing to\n'
    'pay for next iteration or sign LOI.\n'
    'If no interest: pivot or stop.',
    'Eval unit packaging, test data reports, CRM, travel budget')


# ─── SUMMARY FOOTER ───
ax_summary = fig.add_subplot(gs[13], facecolor='#0d0d20')
for sp in ax_summary.spines.values():
    sp.set_edgecolor('#00ff88')
    sp.set_linewidth(2)
ax_summary.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)

ax_summary.text(0.50, 0.85, 'TOTAL BUILD SUMMARY', ha='center', fontsize=16,
                fontweight='bold', color='#00ff88', transform=ax_summary.transAxes)

summary = (
    'TOTAL TIMELINE:  12-18 months  (Blocks 1-12)\n'
    'TOTAL BUDGET:    $145k-$315k  for Phase 1 (proof of physics)\n'
    '                 $250k-$500k  including iteration + aging tests\n\n'
    'CRITICAL PATH:   Block 3 (bonding) -> Block 4 (filling) -> Block 5 (sealing) -> Block 6 (first light)\n'
    '                 If first light fails, iterate Blocks 3-5 before proceeding.\n\n'
    'TEAM NEEDED:     1 MEMS engineer  |  1 atomic physicist  |  1 RF/electronics engineer\n'
    '                 (Part-time: patent attorney, defense compliance consultant)\n\n'
    'KEY GATES:       Gate A (Block 6): Do you see a CPT peak?  YES -> continue.  NO -> iterate.\n'
    '                 Gate B (Block 8): Does the oscillator lock?  YES -> you have a clock.  NO -> fix electronics.\n'
    '                 Gate C (Block 12): Does anyone want to buy it?  YES -> scale.  NO -> pivot.\n\n'
    'PATENT STATUS:   CLEAR.  Foundational CSAC patent abandoned. All process patents have design-arounds.\n'
    '                 Build single-chamber glass-Si-glass cell with direct Rb dispensing + anodic or In bonding.'
)

ax_summary.text(0.50, 0.50, summary, ha='center', va='center', fontsize=11,
                color='white', fontfamily='monospace', transform=ax_summary.transAxes,
                bbox=dict(boxstyle='round,pad=0.5', facecolor='#111133',
                          edgecolor='#00ff88', linewidth=2))


plt.savefig('csac_build_plan.png', dpi=120, facecolor=fig.get_facecolor(),
            bbox_inches='tight')
plt.show()
print("Saved to csac_build_plan.png")
