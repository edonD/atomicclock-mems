# CSAC Digital Top — Professional Build Flow
# Usage:
#   make lint        Verilator lint (--lint-only -Wall)
#   make sim_rtl     RTL simulation (iverilog + vvp)
#   make synth_tt    Yosys synthesis, typical corner
#   make synth_ss    Yosys synthesis, slow-slow corner
#   make synth_ff    Yosys synthesis, fast-fast corner
#   make synth_all   All three corners
#   make sim_gate    Gate-level simulation (TT netlist)
#   make all         Full flow: lint → sim_rtl → synth_all → sim_gate
#   make clean       Remove generated files

.PHONY: all lint sim_rtl synth_tt synth_ss synth_ff synth_all sim_gate clean

RTL_DIR  := rtl
TB_DIR   := tb
SYN_DIR  := syn
SIM_DIR  := sim
RPT_DIR  := reports
BUILD    := sim/build

RTL_SRC  := $(RTL_DIR)/csac_pkg.v \
            $(RTL_DIR)/reset_sync.v \
            $(RTL_DIR)/cdc_sync2.v \
            $(RTL_DIR)/cdc_bus_sync.v \
            $(RTL_DIR)/freq_divider.v \
            $(RTL_DIR)/pid_controller.v \
            $(RTL_DIR)/lock_detector.v \
            $(RTL_DIR)/thermal_controller.v \
            $(RTL_DIR)/spi_slave.v \
            $(RTL_DIR)/spi_regmap.v \
            $(RTL_DIR)/csac_digital_top.v

# ── Full flow ───────────────────────────────────────────────────────
all: lint sim_rtl synth_all sim_gate
	@echo ""
	@echo "========================================"
	@echo "  FULL FLOW COMPLETE"
	@echo "========================================"

# ── Lint ────────────────────────────────────────────────────────────
lint:
	@echo "=== LINT (verilator) ==="
	verilator --lint-only -Wall --top-module csac_digital_top \
		-I$(RTL_DIR) $(RTL_SRC) \
		2>&1 | tee $(RPT_DIR)/lint.log
	@echo "Lint complete."

# ── RTL Simulation ──────────────────────────────────────────────────
$(BUILD):
	mkdir -p $(BUILD)

sim_rtl: $(BUILD)
	@echo "=== RTL SIMULATION ==="
	cd $(SIM_DIR) && iverilog -g2005 -o build/tb_top.vvp -f rtl_sim.f
	cd $(SIM_DIR) && vvp build/tb_top.vvp | tee ../$(RPT_DIR)/sim_rtl.log
	@echo "RTL simulation complete."

# ── Synthesis ───────────────────────────────────────────────────────
synth_tt:
	@echo "=== SYNTHESIS: TT corner ==="
	cd $(SYN_DIR) && yosys -s synth_tt.ys 2>&1 | tee ../$(RPT_DIR)/synth_tt_full.log
	@echo "TT synthesis complete."

synth_ss:
	@echo "=== SYNTHESIS: SS corner ==="
	cd $(SYN_DIR) && yosys -s synth_ss.ys 2>&1 | tee ../$(RPT_DIR)/synth_ss_full.log
	@echo "SS synthesis complete."

synth_ff:
	@echo "=== SYNTHESIS: FF corner ==="
	cd $(SYN_DIR) && yosys -s synth_ff.ys 2>&1 | tee ../$(RPT_DIR)/synth_ff_full.log
	@echo "FF synthesis complete."

synth_all: synth_tt synth_ss synth_ff
	@echo ""
	@echo "=== All 3 corners synthesized ==="
	@grep "Chip area" $(RPT_DIR)/synth_tt_full.log $(RPT_DIR)/synth_ss_full.log $(RPT_DIR)/synth_ff_full.log 2>/dev/null || true

# ── Gate-Level Synthesis (test parameters for fast sim) ──────────────
synth_gate:
	@echo "=== SYNTHESIS: Gate-sim netlist (test params) ==="
	cd $(SYN_DIR) && yosys -s synth_gate.ys 2>&1 | tee ../$(RPT_DIR)/synth_gate_full.log
	@echo "Gate synthesis complete."

# ── Gate-Level Simulation ───────────────────────────────────────────
sim_gate: $(BUILD) synth_gate
	@echo "=== GATE-LEVEL SIMULATION ==="
	cd $(SIM_DIR) && iverilog -g2005 -o build/tb_gate.vvp -f gate_sim.f
	cd $(SIM_DIR) && vvp build/tb_gate.vvp | tee ../$(RPT_DIR)/sim_gate.log
	@echo "Gate-level simulation complete."

# ── Clean ───────────────────────────────────────────────────────────
clean:
	rm -rf $(BUILD)
	rm -f $(RPT_DIR)/*.log $(RPT_DIR)/*.v $(RPT_DIR)/*.json
	rm -f $(SIM_DIR)/*.vcd
	@echo "Clean complete."
