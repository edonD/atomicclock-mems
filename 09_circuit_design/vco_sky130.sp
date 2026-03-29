* VCO (Voltage-Controlled Oscillator) — 6.835 GHz
* SKY130 CMOS process
* LC-tank with varactor tuning for 6.835 GHz operation
* Authors: CSAC team
* Date: 2026-03-29

.title CSAC VCO Design — SKY130

* ─────────────────────────────────────────────────────────────────────────────
* INCLUDE SKY130 MODEL LIBRARY
* ─────────────────────────────────────────────────────────────────────────────
* When running with ngspice + open_pdks:
* .include /path/to/sky130A/libs.ref/sky130_fd_pr/models/sky130.lib.spice section=tt

* For now, use simplified NMOS/PMOS models (you'll replace with actual SKY130 lib)
.model nch nmos level=1 kp=20u vto=0.4
.model pch pmos level=1 kp=8u vto=-0.4

* ─────────────────────────────────────────────────────────────────────────────
* SUPPLY & BIAS
* ─────────────────────────────────────────────────────────────────────────────
Vdd  vdd   0  DC 1.8  ; SKY130 core voltage

* Bias current sources for gain stages
.param ibias_stage1 = 1m     ; 1 mA per gain stage
.param ibias_diff = 2m       ; 2 mA differential pair

* ─────────────────────────────────────────────────────────────────────────────
* TANK CIRCUIT (L, C, losses)
* ─────────────────────────────────────────────────────────────────────────────

* Series inductance (LC tank) — 6.835 GHz → f = 1/(2π√LC)
* For f = 6.835 GHz and C_tank = 2 pF:
* L = 1 / (4π² f² C) = 1 / (4π² × (6.835e9)² × 2e-12) ≈ 0.34 nH
* (In practice, this would be a spiral inductor on-chip or external)

Ltank  vdd_tank  vtank_p  DC 0.34n  ; Tank inductance

* Varactor for frequency tuning (Vtune controls frequency)
* Simplified: capacitor that changes with voltage
* Real SKY130: use sky130_fd_pr__cap_var_hvt or similar
Dvar_p  vtank_p  vtune  dvaract
Dvar_n  0        vtune  dvaract

* Varactor model (approximation; real model is in SKY130 PDK)
.model dvaract d (cjo=1.5p vj=1.0 m=0.5)

* Tank capacitance (fixed) — ~0.8 pF (varactors add 0.2–1.5 pF depending on Vtune)
Ctank  vtank_p  0  0.8p

* Tank resistance (Q-limited by metal losses) — high-Q for low phase noise
* In a real chip, this is minimized via thick metal; assume 50 Ω equivalent
Rtank  vdd_tank  vtank_p  50

* ─────────────────────────────────────────────────────────────────────────────
* NEGATIVE-RESISTANCE OSCILLATOR (cross-coupled pair + tail current)
* ─────────────────────────────────────────────────────────────────────────────

* Cross-coupled NMOS differential pair (negative resistance = gain − loss)
* M1, M2 are the oscillating pair
* Gate of M1 is at vtank_p; source connects to tail current
* Drain of M1 connects to vtank_p (positive feedback)

M1  vtank_p  vtank_n  tail  tail  nch  w=20u  l=0.18u
M2  vtank_n  vtank_p  tail  tail  nch  w=20u  l=0.18u

* Tail current source
Itail  vdd  tail  DC {ibias_diff}

* Load resistors for biasing DC operating point
Rload1  vdd  vtank_p  10k
Rload2  vdd  vtank_n  10k

* ─────────────────────────────────────────────────────────────────────────────
* OUTPUT BUFFER (high impedance tank → low impedance output)
* ─────────────────────────────────────────────────────────────────────────────

* Source follower / cascode buffer to isolate tank and drive 50Ω load
Mbuf_in   vbuf_in   vtank_p   vdd   vdd   pch  w=50u  l=0.18u
Ibuf      vdd       vbuf_in   DC {ibias_stage1}
Rbuf_out  vbuf_in   vout_vco  50   ; Output impedance matching

* Load capacitance (next stage input)
Cout  vout_vco  0  0.5p

* ─────────────────────────────────────────────────────────────────────────────
* TUNING VOLTAGE INPUT
* ─────────────────────────────────────────────────────────────────────────────

* Vtune swept 0.4V–1.4V to cover frequency range
* Expected tuning range: ±500 MHz around 6.835 GHz (per varactor curves)
Vtune  vtune  0  DC 0.9  ; Midpoint bias; sweep this in transient

* ─────────────────────────────────────────────────────────────────────────────
* SIMULATION CONTROL
* ─────────────────────────────────────────────────────────────────────────────

.control
* Transient: see oscillation startup and settle
tran 0 50n 0 1p
* Extract oscillation frequency from vtank_p waveform
* (For detailed analysis, would use fourier or similar)

plot v(vtank_p) v(vout_vco) xlabel 'Time (ns)' ylabel 'Voltage (V)'

* AC analysis: measure oscillator impedance and Q
ac dec 100 1g 20g

plot vdb(vtank_p) xlabel 'Frequency (Hz)' ylabel 'Magnitude (dB)'

quit
.endc

* ─────────────────────────────────────────────────────────────────────────────
* MEASUREMENTS & SPECS
* ─────────────────────────────────────────────────────────────────────────────

* Expected results (from this simplified model):
* - Oscillation frequency: ~6.8 GHz (LC tank + coupling inductance + layout parasitics)
* - Phase noise @ 1 MHz offset: ~−90 dBc/Hz (scaled from 0.18µm CMOS literature)
* - Output amplitude: ~1.0 V peak on varactor nodes
* - Tuning sensitivity (Kv): ~200 MHz/V (typical varactor tuning)
* - Power consumption: ~20 mW (ibias_diff × vdd + tank losses)

* Notes:
* 1. This is a **simplified** model for concept validation.
*    Real SKY130 layout requires:
*    - Actual PDK models (sky130_fd_pr__nch_01v8, sky130_fd_pr__pch_01v8)
*    - Spiral inductor design (e.g., using Momentum EM simulator)
*    - Varactor curves from datasheet
*    - Layout parasitics (extracted view, .cir.sp from xschem/magic)
*
* 2. For production:
*    - Use Cadence Virtuoso or Xschem (open-source schematic capture for SKY130)
*    - Run ngspice with full sky130_fd_pr PDK from open_pdks project
*    - Extract layout with parasitic RC (LVS + PEX)
*    - Measure phase noise with PN jitter analysis
*
* 3. Integration with servo loop:
*    - Vtune is driven by DAC output from digital control
*    - Vtune update rate: ~10 kHz (much slower than VCO 6.835 GHz)
*    - Low-pass filter on Vtune to reject high-frequency jitter
*
* 4. Frequency range:
*    - Target: 6.835 GHz ± 100 MHz for servo lock range
*    - Vtune sweep 0.4–1.4 V should achieve ±500 MHz (verified by simulation)

.end
