// CSAC Digital Control Top — SKY130
// Structural top-level: instantiates all sub-modules with proper CDC.
//
// Clock domains:
//   clk_vco  (6.835 GHz) — divider, PID, lock, thermal, 1 Hz counter
//   spi_clk  (~10 MHz)   — SPI slave, register map
//
// CDC crossings:
//   clk_vco → spi_clk: 76-bit bus via toggle-handshake synchronizer
//   async   → both:     reset_n via reset_sync per domain

`timescale 1ns / 1ps

module csac_digital_top #(
    // Frequency divider
    parameter DIV_WIDTH  = 33,
    parameter SERVO_BIT  = 26,
    parameter ONEHZ_BIT  = 32,
    // PID
    parameter PID_ADC_W  = 8,
    parameter PID_DAC_W  = 10,
    parameter PID_GAIN_W = 4,
    parameter signed [3:0] PID_KP = 4'sd2,
    parameter signed [3:0] PID_KD = 4'sd3,
    parameter [7:0] PID_SETPOINT = 8'd50,
    // Lock detector
    parameter [7:0] LOCK_THRESH = 8'd10,
    parameter [3:0] LOCK_WINDOW = 4'd8,
    // Thermal
    parameter [9:0] TEMP_SETPOINT = 10'd350,
    parameter       TEMP_SHIFT    = 2,
    // CDC
    parameter CDC_STAGES = 2
)(
    // Clock & reset
    input  wire        clk_vco,
    input  wire        spi_clk,
    input  wire        reset_n,

    // ADC inputs (synchronous to clk_vco)
    input  wire [7:0]  photo_adc,
    input  wire [9:0]  temp_adc,

    // DAC outputs
    output wire [9:0]  dac_vco_tune,
    output wire [7:0]  dac_heater_power,

    // SPI interface
    input  wire        spi_mosi,
    output wire        spi_miso,
    input  wire        spi_cs,

    // Outputs
    output reg  [31:0] count_1hz,
    output wire        valid_lock,
    output wire [7:0]  status_byte
);

    // ──────────────────────────────────────────────────────────────────
    // Reset synchronizers
    // ──────────────────────────────────────────────────────────────────

    wire rst_vco_n;

    reset_sync #(.STAGES(CDC_STAGES)) u_rst_vco (
        .clk         (clk_vco),
        .rst_async_n (reset_n),
        .rst_sync_n  (rst_vco_n)
    );

    // SPI domain uses reset_n directly: spi_clk is non-free-running
    // (only toggles during SPI transactions), so a sync deassert would
    // stall until the first transaction and corrupt bit_count alignment.
    wire rst_spi_n = reset_n;

    // ──────────────────────────────────────────────────────────────────
    // Frequency divider
    // ──────────────────────────────────────────────────────────────────

    wire ce_servo, ce_1hz, heartbeat;

    freq_divider #(
        .DIV_WIDTH (DIV_WIDTH),
        .SERVO_BIT (SERVO_BIT),
        .ONEHZ_BIT (ONEHZ_BIT)
    ) u_divider (
        .clk       (clk_vco),
        .rst_n     (rst_vco_n),
        /* verilator lint_off PINCONNECTEMPTY */
        .count     (),
        /* verilator lint_on PINCONNECTEMPTY */
        .ce_servo  (ce_servo),
        .ce_1hz    (ce_1hz),
        .heartbeat (heartbeat)
    );

    // 1 Hz output counter
    always @(posedge clk_vco or negedge rst_vco_n) begin
        if (!rst_vco_n)
            count_1hz <= 32'd0;
        else if (ce_1hz)
            count_1hz <= count_1hz + 1'b1;
    end

    // ──────────────────────────────────────────────────────────────────
    // PID controller
    // ──────────────────────────────────────────────────────────────────

    wire signed [PID_ADC_W:0] pid_error;

    pid_controller #(
        .ADC_WIDTH  (PID_ADC_W),
        .DAC_WIDTH  (PID_DAC_W),
        .GAIN_WIDTH (PID_GAIN_W),
        .KP         (PID_KP),
        .KD         (PID_KD),
        .SETPOINT   (PID_SETPOINT)
    ) u_pid (
        .clk       (clk_vco),
        .rst_n     (rst_vco_n),
        .ce        (ce_servo),
        .adc_in    (photo_adc),
        .dac_out   (dac_vco_tune),
        .error_out (pid_error)
    );

    // ──────────────────────────────────────────────────────────────────
    // Lock detector
    // ──────────────────────────────────────────────────────────────────

    lock_detector #(
        .ERROR_WIDTH  (PID_ADC_W + 1),
        .THRESH_WIDTH (8),
        .THRESHOLD    (LOCK_THRESH),
        .WINDOW_BITS  (4),
        .WINDOW       (LOCK_WINDOW)
    ) u_lock (
        .clk    (clk_vco),
        .rst_n  (rst_vco_n),
        .ce     (ce_servo),
        .error  (pid_error),
        .locked (valid_lock)
    );

    // ──────────────────────────────────────────────────────────────────
    // Thermal controller
    // ──────────────────────────────────────────────────────────────────

    thermal_controller #(
        .ADC_WIDTH (10),
        .DAC_WIDTH (8),
        .SETPOINT  (TEMP_SETPOINT),
        .SHIFT     (TEMP_SHIFT)
    ) u_thermal (
        .clk        (clk_vco),
        .rst_n      (rst_vco_n),
        .ce         (ce_servo),
        .temp_adc   (temp_adc),
        .heater_pwm (dac_heater_power)
    );

    // ──────────────────────────────────────────────────────────────────
    // Status byte
    // ──────────────────────────────────────────────────────────────────

    // Internal PID integral access (for diagnostics, MSBs only)
    wire [3:0] pid_integral_diag = u_pid.integral[9:6];

    assign status_byte = {
        valid_lock,              // [7] Servo locked
        1'b0,                    // [6] Reserved
        1'b0,                    // [5] Reserved
        heartbeat,               // [4] Heartbeat (~50 Hz toggle)
        pid_integral_diag        // [3:0] Integral accumulator MSBs
    };

    // ──────────────────────────────────────────────────────────────────
    // CDC: clk_vco → spi_clk domain
    // ──────────────────────────────────────────────────────────────────

    // Pack all vco-domain signals for bus synchronizer
    // Total: 32 + 8 + 10 + 8 + 8 + 10 = 76 bits
    localparam CDC_BUS_W = 76;

    wire [CDC_BUS_W-1:0] cdc_src_bus = {
        count_1hz,          // [75:44] 32 bits
        status_byte,        // [43:36] 8 bits
        dac_vco_tune,       // [35:26] 10 bits
        dac_heater_power,   // [25:18] 8 bits
        photo_adc,          // [17:10] 8 bits
        temp_adc            // [9:0]   10 bits
    };

    wire [CDC_BUS_W-1:0] cdc_dst_bus;

    cdc_bus_sync #(
        .WIDTH  (CDC_BUS_W),
        .STAGES (CDC_STAGES)
    ) u_cdc_to_spi (
        .clk_src   (clk_vco),
        .rst_src_n (rst_vco_n),
        .capture   (ce_servo),
        .data_src  (cdc_src_bus),
        .clk_dst   (spi_clk),
        .rst_dst_n (rst_spi_n),
        .data_dst  (cdc_dst_bus),
        /* verilator lint_off PINCONNECTEMPTY */
        .valid_dst ()
        /* verilator lint_on PINCONNECTEMPTY */
    );

    // Unpack synchronized bus
    wire [31:0] count_1hz_s      = cdc_dst_bus[75:44];
    wire [7:0]  status_byte_s    = cdc_dst_bus[43:36];
    wire [9:0]  dac_vco_tune_s   = cdc_dst_bus[35:26];
    wire [7:0]  dac_heater_s     = cdc_dst_bus[25:18];
    wire [7:0]  photo_adc_s      = cdc_dst_bus[17:10];
    wire [9:0]  temp_adc_s       = cdc_dst_bus[9:0];

    // ──────────────────────────────────────────────────────────────────
    // SPI slave + register map (spi_clk domain)
    // ──────────────────────────────────────────────────────────────────

    wire [7:0] spi_rx_data;
    wire [7:0] spi_tx_data;
    wire       spi_rx_valid;

    spi_slave #(
        .DATA_WIDTH (8)
    ) u_spi (
        .sclk      (spi_clk),
        .rst_n     (rst_spi_n),
        .mosi      (spi_mosi),
        .miso      (spi_miso),
        .cs_n      (spi_cs),
        .tx_data   (spi_tx_data),
        .rx_data   (spi_rx_data),
        .rx_valid  (spi_rx_valid),
        /* verilator lint_off PINCONNECTEMPTY */
        .byte_done ()
        /* verilator lint_on PINCONNECTEMPTY */
    );

    spi_regmap u_regmap (
        .sclk            (spi_clk),
        .rst_n           (rst_spi_n),
        .cs_n            (spi_cs),
        .rx_valid        (spi_rx_valid),
        .rx_data         (spi_rx_data),
        .tx_data         (spi_tx_data),
        .count_1hz_s     (count_1hz_s),
        .status_byte_s   (status_byte_s),
        .dac_vco_tune_s  (dac_vco_tune_s),
        .dac_heater_s    (dac_heater_s),
        .photo_adc_s     (photo_adc_s),
        .temp_adc_s      (temp_adc_s)
    );

endmodule
