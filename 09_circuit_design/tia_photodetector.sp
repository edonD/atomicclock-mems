* Transimpedance Amplifier (TIA) — Photodetector Readout
* SKY130 CMOS
* Converts photodiode current (pA–nA range) to voltage
* Authors: CSAC team
* Date: 2026-03-29

.title CSAC Photodetector TIA — SKY130

* ─────────────────────────────────────────────────────────────────────────────
* PHOTODIODE + TIA ARCHITECTURE
* ─────────────────────────────────────────────────────────────────────────────
*
* Photodetector signal path:
*   Photodiode (optical cavity) → photocurrent (pA–nA, proportional to absorption)
*   → TIA transimpedance amp (I-to-V converter)
*   → Low-pass filter
*   → PID controller input
*
* When atoms are in dark state (CPT):    photodiode current is LOW
* When atoms absorb (off-resonance):     photodiode current is HIGH
*
* TIA gain is high (~MΩ) so even pA-level currents produce V-level signals

.model nch nmos level=1 kp=20u vto=0.4
.model pch pmos level=1 kp=8u vto=-0.4

* ─────────────────────────────────────────────────────────────────────────────
* SUPPLY & BIAS
* ─────────────────────────────────────────────────────────────────────────────
Vdd  vdd   0  DC 1.8

* ─────────────────────────────────────────────────────────────────────────────
* PHOTODIODE SIMULATION
* ─────────────────────────────────────────────────────────────────────────────

* Integrated on-chip photodiode in SKY130: n-well/p-substrate junction
* Spectral response: 700–1000 nm (covers 780 nm Rb-87 D2 line)
* Typical: ~0.5 A/W responsivity at 780 nm

* Simplified photodiode model:
* Real device has:
* - Reverse-bias capacitance (Cj ~ 10–100 fF for small junction)
* - Leakage current (dark current ~ 10 pA typical)
* - Series resistance (Rj ~ 1 MΩ)

Dphoto  pd_node  0  dphoto
.model dphoto d (is=1e-15 rs=1meg cjo=50f vj=0.7 m=0.5 bv=5 ibv=10u)

* Photocurrent source — represents optical signal
* When CPT dark state: Iph_dark ≈ 0.1 nA (atoms transparent, minimal absorption)
* Off resonance: Iph_bright ≈ 10 nA (atoms absorb, strong photocurrent)
*
* Simulate a CPT resonance scan: sweep frequency slowly, photocurrent shows dip
* For transient simulation, use a switching profile:

Iphoto  0  pd_node  DC 5n  AC 0.0  SIN(5n 2n 100k)  ; 100 kHz modulation, 5±2 nA

* This creates: baseline 5 nA with 2 nA amplitude 100 kHz dither
* When servo locks, dither amplitude → 0

* ─────────────────────────────────────────────────────────────────────────────
* TRANSIMPEDANCE AMPLIFIER (TIA)
* ─────────────────────────────────────────────────────────────────────────────

* Topology: inverting transimpedance amp with capacitive feedback
* High transimpedance gain (Ztrans = −Rf) with noise-optimal bandwidth

* TIA gain resistor: Rf = 1 MΩ (typical for this current range)
* TIA feedback capacitor: Cf = 1 pF (for bandwidth and stability)
* Expected gain: Ztrans = 1 MΩ → 1 nA input = 1 mV output

Rf  pd_node  tia_out  1Meg
Cf  tia_out  tia_inv  1p

* Operational amplifier (TIA core)
* Simplified two-stage opamp:
*   - Input differential pair (Gain stage 1)
*   - Common-source gain stage 2
*   - Compensation capacitor

* Stage 1: Differential pair (inverting input at pd_node, non-inverting at 0.9V ref)
Min   tia_inv   tia_inv   vdd   vdd   pch  w=100u  l=0.18u
Mip   pd_node   tia_inv   vdd   vdd   pch  w=100u  l=0.18u

* Active load (current mirror) for differential pair
Mload  tia_inv  tia_inv  vdd  vdd  pch  w=50u  l=0.18u
Mload2 pd_node  tia_inv  vdd  vdd  pch  w=50u  l=0.18u

* Tail current source
Itail1  vdd  tia_tail  DC 1m
Mtail   tia_tail  bias   0  0  nch  w=100u  l=0.18u

* Reference bias = vdd/2 = 0.9V
Vref   tia_inv   0  DC 0.9

* Stage 2: High-gain common-source amp
Mgain  int_node  tia_inv  vdd  vdd  pch  w=200u  l=0.18u
Mgain_tail int_node bias 0 0 nch w=200u l=0.18u

* Load for gain stage
Rload  vdd  int_node  10k
Ccomp  int_node  tia_out  0.5p   ; Compensation capacitor for stability

* Output buffer (source follower to drive next stage)
Mbuf  tia_out  int_node  vdd  vdd  pch  w=50u  l=0.18u
Ibuf  vdd  tia_out  DC 1m
Rbuf  tia_out  out_final  1k

* ─────────────────────────────────────────────────────────────────────────────
* OUTPUT LOW-PASS FILTER
* ─────────────────────────────────────────────────────────────────────────────

* Servo loop update rate is ~1 kHz (slow closed-loop bandwidth)
* High-frequency noise (>10 kHz) is filtered to reduce noise injection

Rlpf  out_final  servo_in  10k
Clpf  servo_in   0         10n    ; RC filter: tau = 10k × 10n = 100 µs → f_c ≈ 1.6 kHz

* ─────────────────────────────────────────────────────────────────────────────
* SIMULATION
* ─────────────────────────────────────────────────────────────────────────────

.control

* Transient: photocurrent changes, watch TIA output change
tran 0 100u 0 0.1u

plot v(pd_node) v(tia_out) v(servo_in) xlabel 'Time (µs)' ylabel 'Voltage (V)'
plot i(Iphoto) xlabel 'Time (µs)' ylabel 'Photocurrent (A)'

* AC analysis: measure TIA gain and bandwidth
ac dec 50 1 1G

plot vdb(tia_out) vdb(servo_in) xlabel 'Frequency (Hz)' ylabel 'Gain (dB)'
plot vp(tia_out) xlabel 'Frequency (Hz)' ylabel 'Phase (deg)'

quit
.endc

* ─────────────────────────────────────────────────────────────────────────────
* EXPECTED RESULTS
* ─────────────────────────────────────────────────────────────────────────────

* TIA Gain (Ztrans):
*   - DC gain: −Rf = −1 MΩ
*   - 1 nA input → 1 mV output
*   - 0.1 nA input → 0.1 mV output
*   - 10 nA input → 10 mV output
*
* Bandwidth:
*   - Gain-bandwidth product ≈ 1/(2π × Rf × Cf) ≈ 159 MHz
*   - At servo loop frequency (1 kHz), TIA is flat in gain
*   - LPF reduces noise above 1.6 kHz
*
* Noise (not simulated here, but important):
*   - Photodiode shot noise: 2.4 pA/√Hz @ 5 nA bias
*   - Amplifier input-referred noise: ~100 µV/√Hz (thermal noise of diff pair)
*   - Output-referred: noise × Ztrans = 100 µV × 1 MΩ/V = ...significant!
*   - → Need low-noise design (high W/L, optimized bias currents)
*
* Nonlinearity:
*   - For Iphoto 0–20 nA, output stays linear (0–20 mV range)
*   - Beyond 20 nA, rails begin to matter

* Integration notes:
*   1. Rf and Cf set the TIA characteristics
*      - Higher Rf → higher gain but lower bandwidth and higher noise
*      - Typical: Rf = 1–10 MΩ, Cf = 0.5–2 pF
*
*   2. Stability compensation:
*      - Single pole at f_p = 1/(2π Rf Cf) must be dominant
*      - Higher-order poles from opamp stages need to be far away
*      - Monitor phase margin in AC analysis
*
*   3. Power consumption:
*      - Bias currents: ~5 mA total (acceptable for low-power lock)
*      - Future: reduce to sub-mA with gm/ID design
*
*   4. Layout considerations (when you go to GDS):
*      - Photodiode must be placed near TIA input (minimize parasitic inductance)
*      - Rf should be polysilicon (low noise, temperature-stable)
*      - Feedback line (pd_node to Rf to tia_out) must be short/shielded
*      - Use guard rings around sensitive analog circuits

.end
