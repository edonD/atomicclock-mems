* Phase 2: SKY130 Inductor Characterization
* Extract L, Q, SRF for all three PDK inductors at 6.835 GHz

* === Inductor models ===
.include '/home/ubuntu/.volare/volare/sky130/versions/6d4d11780c40b20ee63cc98e645307a9bf2b2ab8/sky130A/libs.ref/sky130_fd_pr/spice/sky130_fd_pr__ind_03_90.model.spice'
.include '/home/ubuntu/.volare/volare/sky130/versions/6d4d11780c40b20ee63cc98e645307a9bf2b2ab8/sky130A/libs.ref/sky130_fd_pr/spice/sky130_fd_pr__ind_05_125.model.spice'
.include '/home/ubuntu/.volare/volare/sky130/versions/6d4d11780c40b20ee63cc98e645307a9bf2b2ab8/sky130A/libs.ref/sky130_fd_pr/spice/sky130_fd_pr__ind_05_220.model.spice'

* ========================================
* Test circuit for ind_03_90 (0.9 nH)
* ========================================
Vac1 port1a 0 dc 0 ac 1
Xind1 port1a port1b ct1 0 sky130_fd_pr__ind_03_90
Rload1 port1b 0 1e6

* ========================================
* Test circuit for ind_05_125 (1.25 nH)
* ========================================
Vac2 port2a 0 dc 0 ac 1
Xind2 port2a port2b ct2 0 sky130_fd_pr__ind_05_125
Rload2 port2b 0 1e6

* ========================================
* Test circuit for ind_05_220 (2.2 nH)
* ========================================
Vac3 port3a 0 dc 0 ac 1
Xind3 port3a port3b ct3 0 sky130_fd_pr__ind_05_220
Rload3 port3b 0 1e6

.control
ac dec 200 100e6 50e9

* Save impedance data: Z = V/I for each inductor (one-port)
* Z(port) = Vac / I(Vac) = 1/I(Vac) since Vac=1
wrdata /home/ubuntu/atomicclock-mems/09_circuit_design/vco_design/02_ind1_data.dat frequency i(Vac1)
wrdata /home/ubuntu/atomicclock-mems/09_circuit_design/vco_design/02_ind2_data.dat frequency i(Vac2)
wrdata /home/ubuntu/atomicclock-mems/09_circuit_design/vco_design/02_ind3_data.dat frequency i(Vac3)

echo "=== Phase 2 Inductor Characterization Complete ==="
quit
.endc

.end
