* Phase 4b: VCO Tuning Range sweep

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

.include '/home/ubuntu/.volare/volare/sky130/versions/6d4d11780c40b20ee63cc98e645307a9bf2b2ab8/sky130A/libs.ref/sky130_fd_pr/spice/sky130_fd_pr__nfet_01v8_lvt__tt.corner.spice'
.include '/home/ubuntu/.volare/volare/sky130/versions/6d4d11780c40b20ee63cc98e645307a9bf2b2ab8/sky130A/libs.ref/sky130_fd_pr/spice/sky130_fd_pr__ind_03_90.model.spice'

Vdd vdd 0 dc 1.8
Vtune vtune_node 0 dc 0.9

Xind outp outn vdd 0 sky130_fd_pr__ind_03_90

Ctank_p outp 0 565e-15
Ctank_n outn 0 565e-15
Cvar_p outp vtune_node 60e-15
Cvar_n outn vtune_node 60e-15

XM1 outp outn tail 0 sky130_fd_pr__nfet_01v8_lvt w=8e-6 l=150e-9 nf=1 mult=10 ad=2.32e-12 as=2.32e-12 pd=16.58e-6 ps=16.58e-6 sa=0.28e-6 sb=0.28e-6 sd=0.28e-6
XM2 outn outp tail 0 sky130_fd_pr__nfet_01v8_lvt w=8e-6 l=150e-9 nf=1 mult=10 ad=2.32e-12 as=2.32e-12 pd=16.58e-6 ps=16.58e-6 sa=0.28e-6 sb=0.28e-6 sd=0.28e-6

Vbias vbias 0 dc 0.9
XMtail tail vbias 0 0 sky130_fd_pr__nfet_01v8_lvt w=8e-6 l=150e-9 nf=1 mult=20 ad=2.32e-12 as=2.32e-12 pd=16.58e-6 ps=16.58e-6 sa=0.28e-6 sb=0.28e-6 sd=0.28e-6

.ic v(outp)=1.4 v(outn)=0.6 v(tail)=0.4

.control
* Sweep tank capacitance to map tuning range
foreach cval 480e-15 510e-15 540e-15 565e-15 590e-15 620e-15 660e-15
  alter ctank_p = $cval
  alter ctank_n = $cval
  tran 0.5p 10n uic
  meas tran period_val trig v(outp) val=1.55 rise=5 targ v(outp) val=1.55 rise=15
  echo "CTUNE_DATA: Ctank=$cval period=$&period_val"
  destroy all
end

echo "=== Phase 4b Tuning Complete ==="
quit
.endc

.end
