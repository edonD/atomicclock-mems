# SDC Timing Constraints — CSAC Digital Top
# For OpenSTA and OpenROAD consumption.

# ── Clock definitions ───────────────────────────────────────────────
# Note: 6.835 GHz (146 ps period) is the VCO frequency.
# In practice, a prescaler divides this before it hits the digital counter.
# The SDC documents the aspirational spec; STA will show violations
# which are expected until the prescaler is designed.

create_clock -name clk_vco -period 0.146 [get_ports clk_vco]
create_clock -name spi_clk -period 100.0 [get_ports spi_clk]

# ── Clock domain crossing ──────────────────────────────────────────
# These clocks are asynchronous — all paths between them go through
# cdc_bus_sync (toggle-handshake synchronizer).

set_clock_groups -asynchronous \
    -group {clk_vco} \
    -group {spi_clk}

# ── Input delays ────────────────────────────────────────────────────
# ADC inputs: assumed synchronous to clk_vco with generous setup
set_input_delay -clock clk_vco -max 0.100 [get_ports {photo_adc[*] temp_adc[*]}]
set_input_delay -clock clk_vco -min 0.000 [get_ports {photo_adc[*] temp_adc[*]}]

# SPI inputs: relative to spi_clk
set_input_delay -clock spi_clk -max 10.0 [get_ports {spi_mosi spi_cs}]
set_input_delay -clock spi_clk -min 0.0  [get_ports {spi_mosi spi_cs}]

# ── Output delays ───────────────────────────────────────────────────
set_output_delay -clock clk_vco -max 0.050 [get_ports {dac_vco_tune[*] dac_heater_power[*]}]
set_output_delay -clock clk_vco -max 0.050 [get_ports {count_1hz[*] valid_lock status_byte[*]}]
set_output_delay -clock spi_clk -max 10.0  [get_ports spi_miso]

# ── False paths ─────────────────────────────────────────────────────
# Async reset — not a timing path
set_false_path -from [get_ports reset_n]

# ── Design constraints ──────────────────────────────────────────────
set_max_transition 0.5 [current_design]
set_max_fanout 20 [current_design]
