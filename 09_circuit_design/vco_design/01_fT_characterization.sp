* Phase 1: SKY130 RF NFET LVT fT Characterization
* Uses REAL BSIM4 (Level 54) models from SKY130 PDK

* === Global parameters needed by SKY130 models ===
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

* --- DUT: NFET LVT, W=5u, L=0.15u, nf=4 ---
* Vgs has ac=1 for AC small-signal stimulus
Vgs gate 0 dc 0.9 ac 1
Vds drain 0 dc 0.9

XDUT drain gate 0 0 sky130_fd_pr__nfet_01v8_lvt w=5e-6 l=150e-9 nf=4 ad=2.8e-12 as=2.8e-12 pd=12.12e-6 ps=12.12e-6 sa=0.28e-6 sb=0.28e-6 sd=0.28e-6

.control
set wr_vecnames

* ==========================================
* 1) DC sweep: Id vs Vgs
* ==========================================
dc Vgs 0.0 1.8 0.01
wrdata /home/ubuntu/atomicclock-mems/09_circuit_design/vco_design/01_dc_sweep.dat v(gate) v(drain) i(Vds)

destroy all

* ==========================================
* 2) AC at Vgs=0.9V: full h21 vs freq
* ==========================================
alter Vgs dc = 0.9
ac dec 50 1e6 200e9
wrdata /home/ubuntu/atomicclock-mems/09_circuit_design/vco_design/01_ac_0p9.dat frequency i(Vds) i(Vgs)
destroy all

* 3) AC at Vgs=0.6V
alter Vgs dc = 0.6
ac dec 50 1e6 200e9
wrdata /home/ubuntu/atomicclock-mems/09_circuit_design/vco_design/01_ac_0p6.dat frequency i(Vds) i(Vgs)
destroy all

* 4) AC at Vgs=1.2V
alter Vgs dc = 1.2
ac dec 50 1e6 200e9
wrdata /home/ubuntu/atomicclock-mems/09_circuit_design/vco_design/01_ac_1p2.dat frequency i(Vds) i(Vgs)
destroy all

* 5) AC at Vgs=1.5V
alter Vgs dc = 1.5
ac dec 50 1e6 200e9
wrdata /home/ubuntu/atomicclock-mems/09_circuit_design/vco_design/01_ac_1p5.dat frequency i(Vds) i(Vgs)

echo "=== Phase 1 Complete ==="
quit
.endc

.end
