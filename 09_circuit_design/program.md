# CSAC Digital Design — Professional Build Program

## Overview
Complete the professional digital IC design flow for the CSAC readout IC.
All work targets the SKY130 130nm CMOS open-source PDK.

## Working Directory
`/home/ubuntu/atomicclock-mems/09_circuit_design`

## Task List

### Phase 1: Fix SPI Slave Bug
- [ ] Fix `rtl/spi_slave.v`: tx_shift must reload from tx_data at byte boundaries (when bit_count wraps), not only when cs_n is high. Currently the second SPI byte always reads stale tx_data because tx_shift is only preloaded during idle.
- [ ] Verify fix doesn't break lint: `make lint` must pass with zero warnings

### Phase 2: Pass All RTL Tests
- [ ] Run `make sim_rtl` — all 11 tests must PASS
- [ ] Fix any remaining test failures by debugging with VCD waveforms if needed
- [ ] Tests cover: reset, PID convergence, PID integral accumulation, lock detection, lock drop, thermal heat/cool, 1Hz counter, SPI status read, SPI photo_adc readback via CDC

### Phase 3: Multi-Corner Synthesis
- [ ] Run `make synth_tt` — typical corner (25C, 1.80V)
- [ ] Run `make synth_ss` — slow-slow corner (100C, 1.60V)
- [ ] Run `make synth_ff` — fast-fast corner (-40C, 1.95V)
- [ ] All three must produce zero unmapped cells
- [ ] Record cell counts and area for each corner in `reports/`

### Phase 4: Gate-Level Simulation
- [ ] Run `make sim_gate` — post-synthesis functional simulation using TT netlist + SKY130 cell Verilog models
- [ ] All 11 tests must PASS at gate level
- [ ] Fix any gate-level-only failures (timing, initialization, X-propagation)

### Phase 5: Professional Circuit Visualization
- [ ] Generate a comprehensive, professional-quality PNG showing the full chip architecture with:
  - All analog blocks (VCO, TIA, ADCs, DACs) with their specs
  - All digital blocks (divider, PID, lock, thermal, SPI) with cell counts
  - CDC crossings shown explicitly
  - Signal flow arrows with bus widths
  - Clock domains color-coded
  - Design status per block (done/pending/risk)
  - Synthesis metrics per corner (TT/SS/FF cell count + area)
  - Pin/port map around the chip boundary
- [ ] Save as `reports/csac_chip_professional.png`

### Phase 6: Commit & Push
- [ ] Stage all new/modified files under `09_circuit_design/`
- [ ] Commit with descriptive message
- [ ] Push to remote

## Constraints
- All RTL must be Verilog-2001 (no SystemVerilog)
- Verilator lint must be clean (`--lint-only -Wall`, zero warnings)
- iverilog for simulation (`-g2005`)
- Yosys 0.33 for synthesis
- SKY130 PDK at `/home/ubuntu/.volare/volare/sky130/versions/6d4d11780c40b20ee63cc98e645307a9bf2b2ab8/sky130A/`
- Liberty files: `libs.ref/sky130_fd_sc_hd/lib/sky130_fd_sc_hd__{tt_025C_1v80,ss_100C_1v60,ff_n40C_1v95}.lib`
- Gate-level sim cell models: `libs.ref/sky130_fd_sc_hd/verilog/{primitives.v,sky130_fd_sc_hd.v}`

## Success Criteria
- `make all` completes end-to-end: lint → sim_rtl (11/11 PASS) → synth_all (3 corners) → sim_gate (11/11 PASS)
- Professional chip PNG generated
- Everything committed and pushed to GitHub
