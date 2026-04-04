// Gate-level simulation file list
// Uses synthesized netlist + SKY130 cell models

+define+GATE_SIM
+define+FUNCTIONAL
+define+UNIT_DELAY=#1

// SKY130 cell models
+incdir+/home/ubuntu/.volare/volare/sky130/versions/6d4d11780c40b20ee63cc98e645307a9bf2b2ab8/sky130A/libs.ref/sky130_fd_sc_hd/verilog
/home/ubuntu/.volare/volare/sky130/versions/6d4d11780c40b20ee63cc98e645307a9bf2b2ab8/sky130A/libs.ref/sky130_fd_sc_hd/verilog/primitives.v
/home/ubuntu/.volare/volare/sky130/versions/6d4d11780c40b20ee63cc98e645307a9bf2b2ab8/sky130A/libs.ref/sky130_fd_sc_hd/verilog/sky130_fd_sc_hd.v

// Synthesized netlist (test parameters for fast simulation)
../reports/csac_digital_top_gate.v

// Testbench
../tb/spi_master_bfm.v
../tb/tb_csac_digital_top.v
