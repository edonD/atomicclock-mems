* Phase 1b: DC operating point at multiple Vgs values

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

vgs gate 0 dc 0.9
vds drain 0 dc 0.9
vsrc source 0 dc 0

XDUT drain gate source 0 sky130_fd_pr__nfet_01v8_lvt w=5e-6 l=150e-9 nf=4 ad=2.8e-12 as=2.8e-12 pd=12.12e-6 ps=12.12e-6 sa=0.28e-6 sb=0.28e-6 sd=0.28e-6

.control
* Operating point sweep
foreach vg_val 0.0 0.1 0.2 0.3 0.4 0.5 0.6 0.7 0.8 0.9 1.0 1.1 1.2 1.3 1.4 1.5 1.6 1.7 1.8
  alter vgs dc = $vg_val
  op
  echo "OP_DATA: Vgs=$vg_val Id=$&i(vsrc)"
  destroy all
end

quit
.endc

.end
