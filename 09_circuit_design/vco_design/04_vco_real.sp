* Phase 4: Cross-Coupled LC VCO with Real SKY130 Models
* Target: 6.835 GHz (Rb-87 hyperfine frequency)
* Uses REAL BSIM4 Level 54 models — NOT Level 1

* ============================================================
* Global parameters for SKY130 models
* ============================================================
.param mc_mm_switch = 0
.param sky130_fd_pr__nfet_01v8_lvt__toxe_slope = 3.443e-03
.param sky130_fd_pr__nfet_01v8_lvt__toxe_slope1 = 2.443e-03
.param sky130_fd_pr__nfet_01v8_lvt__vth0_slope = 5.456e-03
.param sky130_fd_pr__nfet_01v8_lvt__vth0_slope1 = 5.456e-03
.param sky130_fd_pr__nfet_01v8_lvt__vth0_slope2 = 7.456e-03
.param sky130_fd_pr__nfet_01v8_lvt__voff_slope = 0.0
.param sky130_fd_pr__nfet_01v8_lvt__nfactor_slope = 0.0
.param sky130_fd_pr__nfet_01v8_lvt__lint_slope = 0.0
.param sky130_fd_pr__nfet_01v8_lvt__wint_slope = 0.0
.param sky130_fd_pr__nfet_01v8_lvt__wlod_diff = 0.0
.param sky130_fd_pr__nfet_01v8_lvt__kvth0_diff = 0.0
.param sky130_fd_pr__nfet_01v8_lvt__lkvth0_diff = 0.0
.param sky130_fd_pr__nfet_01v8_lvt__wkvth0_diff = 0.0
.param sky130_fd_pr__nfet_01v8_lvt__ku0_diff = 0.0
.param sky130_fd_pr__nfet_01v8_lvt__lku0_diff = 0.0
.param sky130_fd_pr__nfet_01v8_lvt__wku0_diff = 0.0
.param sky130_fd_pr__nfet_01v8_lvt__kvsat_diff = 0.0

* ============================================================
* Include real SKY130 PDK models
* ============================================================
.include '/home/ubuntu/.volare/volare/sky130/versions/6d4d11780c40b20ee63cc98e645307a9bf2b2ab8/sky130A/libs.ref/sky130_fd_pr/spice/sky130_fd_pr__nfet_01v8_lvt__tt.corner.spice'
.include '/home/ubuntu/.volare/volare/sky130/versions/6d4d11780c40b20ee63cc98e645307a9bf2b2ab8/sky130A/libs.ref/sky130_fd_pr/spice/sky130_fd_pr__ind_03_90.model.spice'

* ============================================================
* Design Parameters
* ============================================================
* Using W=8µm (safely in 7-100µm model bin) with mult for scaling
* Cross-coupled pair: need gm > 2/Rtank ≈ 6 mS per side
* W=8µm at Vgs≈0.9V: gm/W ≈ 90µS/µm → gm ≈ 0.72 mS per instance
* Use mult=10 → gm ≈ 7.2 mS per side (sufficient)
*
* Tank: ind_03_90, L_half=760.5 pH
* Ctank chosen to resonate near 6.835 GHz

.param VTUNE = 0.9

* ============================================================
* POWER SUPPLY
* ============================================================
Vdd vdd 0 dc 1.8
Vtune vtune_node 0 dc VTUNE

* ============================================================
* TANK INDUCTOR (center-tapped)
* ind_03_90: L_half = 760.5 pH each side, series R ~1 ohm
* a → outp, b → outn, ct → vdd, sub → gnd
* ============================================================
Xind outp outn vdd 0 sky130_fd_pr__ind_03_90

* ============================================================
* TANK CAPACITORS
* Target f = 6.835 GHz → Ctotal_per_side ≈ 713 fF
* Subtract parasitic C from inductor (~50 fF) and MOSFETs (~100 fF)
* Fixed caps: ~500 fF per side
* Varactor caps: ~60 fF per side (variable)
* ============================================================
Ctank_p outp 0 565e-15
Ctank_n outn 0 565e-15

* Varactor (ideal voltage-dependent) for tuning
Cvar_p outp vtune_node 60e-15
Cvar_n outn vtune_node 60e-15

* ============================================================
* CROSS-COUPLED NMOS PAIR (LVT for best fT)
* W=8µm, L=150nm, nf=1, mult=10 → Wtotal=80µm per side
* ============================================================
XM1 outp outn tail 0 sky130_fd_pr__nfet_01v8_lvt w=8e-6 l=150e-9 nf=1 mult=10 ad=2.32e-12 as=2.32e-12 pd=16.58e-6 ps=16.58e-6 sa=0.28e-6 sb=0.28e-6 sd=0.28e-6
XM2 outn outp tail 0 sky130_fd_pr__nfet_01v8_lvt w=8e-6 l=150e-9 nf=1 mult=10 ad=2.32e-12 as=2.32e-12 pd=16.58e-6 ps=16.58e-6 sa=0.28e-6 sb=0.28e-6 sd=0.28e-6

* ============================================================
* TAIL CURRENT SOURCE
* W=8µm, L=500nm (longer L for better current source output R)
* mult=5 → Wtotal=40µm, biased for ~4 mA
* ============================================================
* Tail: Vbias=0.9V, W=8µm L=150nm mult=20 for ~4-8 mA
Vbias vbias 0 dc 0.9
XMtail tail vbias 0 0 sky130_fd_pr__nfet_01v8_lvt w=8e-6 l=150e-9 nf=1 mult=20 ad=2.32e-12 as=2.32e-12 pd=16.58e-6 ps=16.58e-6 sa=0.28e-6 sb=0.28e-6 sd=0.28e-6

* ============================================================
* INITIAL CONDITIONS (kick-start oscillation)
* ============================================================
.ic v(outp)=1.4 v(outn)=0.6 v(tail)=0.4

* ============================================================
* SIMULATION: 20 ns transient with 0.5 ps timestep
* ============================================================
.control
tran 0.5p 20n uic

set filetype=ascii
set wr_singlescale
write /home/ubuntu/atomicclock-mems/09_circuit_design/vco_design/04_vco_tran.raw

echo "=== Phase 4 VCO Transient Complete ==="
quit
.endc

.end
