* Phase 3: SKY130 Varactor (cap_var_lvt) Characterization
* Extract C(V) curve, Cmin, Cmax, tuning ratio

* === Global parameters for varactor model ===
.param mc_mm_switch = 0
* Varactor corner params (TT defaults)
.param cnwvc_tox = 41.6503
.param cnwvc_cdepmult = 1.0
.param cnwvc_cintmult = 1.0
.param cnwvc_vt1 = 0.3333
.param cnwvc_vt2 = 0.2380952
.param cnwvc_vtr = 0.16
.param cnwvc_dwc = 0.0
.param cnwvc_dlc = 0.0
.param cnwvc_dld = 0.0
* Resistance params
.param rp1 = 520
.param rcp1 = 100
.param rcn = 80
.param rnw = 680

.include '/home/ubuntu/.volare/volare/sky130/versions/6d4d11780c40b20ee63cc98e645307a9bf2b2ab8/sky130A/libs.ref/sky130_fd_pr/spice/sky130_fd_pr__cap_var_lvt.model.spice'

* Varactor test: AC analysis at each Vtune bias
* Varactor pins: c0 c1 b (gate, source, bulk)
* Use w=1 l=0.5 (default) — 1 unit varactor
Vac vtop 0 dc 0 ac 1
Xvar1 vtop vbot 0 sky130_fd_pr__cap_var_lvt w=1 l=0.5
Vbot vbot 0 dc 0.9

.control
* Sweep Vtune (vbot) and measure capacitance via AC
* C = Im(I(Vac)) / (2*pi*f) at a reference frequency

foreach vtune 0.0 0.1 0.2 0.3 0.4 0.5 0.6 0.7 0.8 0.9 1.0 1.1 1.2 1.3 1.4 1.5 1.6 1.7 1.8
  alter Vbot dc = $vtune
  ac lin 1 1e9 1e9
  echo "VAR_DATA: Vtune=$vtune Iac_re=$&i(Vac)[0] Iac_im=$&i(Vac)[1]"
  destroy all
end

* Also do a frequency sweep at Vtune=0.9V for impedance curve
alter Vbot dc = 0.9
ac dec 100 100e6 20e9
wrdata /home/ubuntu/atomicclock-mems/09_circuit_design/vco_design/03_var_ac.dat frequency i(Vac)

echo "=== Phase 3 Varactor Characterization Complete ==="
quit
.endc

.end
