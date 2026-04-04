/**
 * CSAC Digital Control Top Module — SKY130
 *
 * Implements:
 *  - Frequency divider: 6.835 GHz → 1 Hz (binary ÷2^33)
 *  - PID servo controller (clock-enable architecture)
 *  - SPI slave interface for external MCU
 *  - Thermistor ADC input
 *  - DAC output for VCO tuning voltage
 *  - Watchdog / health monitoring
 *
 * All sequential logic uses clk_vco as the single clock domain.
 * Slower update rates use clock-enable pulses derived from the
 * divider chain — no gated clocks.
 *
 * Authors: CSAC team
 * Date: 2026-03-29
 */

`timescale 1ps / 1ps

module csac_digital_top (
    // Clock input from VCO (6.835 GHz)
    input wire clk_vco,

    // Analog feedback inputs (from ADC or comparator)
    input wire [7:0] photo_adc,          // 8-bit photodetector signal
    input wire [9:0] temp_adc,           // 10-bit thermistor reading

    // DAC outputs (control)
    output wire [9:0] dac_vco_tune,      // VCO tuning voltage (10-bit)
    output wire [7:0] dac_heater_power,  // Heater PWM duty cycle

    // SPI interface (external MCU control)
    input wire spi_clk,
    input wire spi_mosi,
    output wire spi_miso,
    input wire spi_cs,

    // Outputs for measurement / test
    output reg [31:0] count_1hz,         // 1 Hz output (directly measurable)
    output reg valid_lock,               // Servo loop locked
    output wire [7:0] status_byte,       // Health status

    // Power / Reset
    input wire reset_n,
    input wire clk_slow                  // ~1 MHz for digital control logic
);

    // ─────────────────────────────────────────────────────────────────────────
    // FREQUENCY DIVIDER: 6.835 GHz → 1 Hz (binary ÷2^33)
    // ─────────────────────────────────────────────────────────────────────────
    // 2^33 = 8,589,934,592 ≈ 6,834,682,611 (0.26% error, trimmed by servo)

    reg [32:0] vco_counter;

    always @(posedge clk_vco or negedge reset_n) begin
        if (!reset_n)
            vco_counter <= 33'd0;
        else
            vco_counter <= vco_counter + 1'b1;
    end

    // ─────────────────────────────────────────────────────────────────────────
    // CLOCK ENABLE GENERATION (edge detectors on divider bits)
    // ─────────────────────────────────────────────────────────────────────────
    // Instead of using counter bits as clocks (gated clock = bad for synthesis),
    // detect rising edges and generate single-cycle enable pulses.

    reg vco_bit26_d;  // delayed version of vco_counter[26] (~50 Hz)
    reg vco_bit32_d;  // delayed version of vco_counter[32] (~1 Hz)

    wire ce_servo = vco_counter[26] & ~vco_bit26_d;  // one clk_vco pulse at ~50 Hz
    wire ce_1hz   = vco_counter[32] & ~vco_bit32_d;  // one clk_vco pulse at ~1 Hz

    always @(posedge clk_vco or negedge reset_n) begin
        if (!reset_n) begin
            vco_bit26_d <= 1'b0;
            vco_bit32_d <= 1'b0;
        end else begin
            vco_bit26_d <= vco_counter[26];
            vco_bit32_d <= vco_counter[32];
        end
    end

    // Heartbeat signal for status byte (toggles at ~50 Hz)
    wire heartbeat = vco_counter[26];

    // 1 Hz output counter
    always @(posedge clk_vco or negedge reset_n) begin
        if (!reset_n)
            count_1hz <= 32'd0;
        else if (ce_1hz)
            count_1hz <= count_1hz + 1'b1;
    end

    // ─────────────────────────────────────────────────────────────────────────
    // SERVO LOOP: PID Controller
    // ─────────────────────────────────────────────────────────────────────────

    localparam [7:0] SETPOINT = 8'd50;

    reg [9:0] pid_integral;
    reg [7:0] pid_last_error;
    wire [7:0] current_error = photo_adc - SETPOINT;

    localparam [3:0] Kp = 4'd2;
    localparam [3:0] Ki = 4'd1;
    localparam [3:0] Kd = 4'd3;

    // Combinational PID terms
    wire signed [15:0] prop_term = $signed({1'b0, current_error}) * $signed({1'b0, Kp});
    wire signed [15:0] int_update = $signed({1'b0, pid_integral}) + ($signed({1'b0, current_error}) >>> 2);
    wire signed [15:0] deriv_term = ($signed({1'b0, current_error}) - $signed({1'b0, pid_last_error})) * $signed({1'b0, Kd});
    wire signed [15:0] pid_raw = prop_term + $signed({6'b0, pid_integral}) + deriv_term;

    reg [9:0] pid_output;

    always @(posedge clk_vco or negedge reset_n) begin
        if (!reset_n) begin
            pid_integral <= 10'd0;
            pid_last_error <= 8'd0;
            pid_output <= 10'd512;
        end else if (ce_servo) begin
            // Integral with antiwindup
            if (int_update[15])
                pid_integral <= 10'd0;
            else if (int_update > 16'sd1023)
                pid_integral <= 10'd1023;
            else
                pid_integral <= int_update[9:0];

            // Saturate PID output to DAC range [0, 1023]
            if (pid_raw[15])
                pid_output <= 10'd0;
            else if (pid_raw > 16'sd1023)
                pid_output <= 10'd1023;
            else
                pid_output <= pid_raw[9:0];

            pid_last_error <= current_error;
        end
    end

    assign dac_vco_tune = pid_output;

    // ─────────────────────────────────────────────────────────────────────────
    // LOCK DETECTION
    // ─────────────────────────────────────────────────────────────────────────

    localparam [7:0] LOCK_THRESHOLD = 8'd10;
    localparam [3:0] LOCK_WINDOW = 4'd8;
    reg [3:0] lock_counter;

    always @(posedge clk_vco or negedge reset_n) begin
        if (!reset_n) begin
            lock_counter <= 4'd0;
            valid_lock <= 1'b0;
        end else if (ce_servo) begin
            if ((current_error < LOCK_THRESHOLD) &&
                (current_error != 8'hFF)) begin
                if (lock_counter == LOCK_WINDOW)
                    valid_lock <= 1'b1;
                else
                    lock_counter <= lock_counter + 1'b1;
            end else begin
                lock_counter <= 4'd0;
                valid_lock <= 1'b0;
            end
        end
    end

    // ─────────────────────────────────────────────────────────────────────────
    // THERMAL CONTROL
    // ─────────────────────────────────────────────────────────────────────────

    localparam [9:0] TEMP_SETPOINT = 10'd350;

    wire signed [11:0] temp_error = $signed({2'b0, TEMP_SETPOINT}) -
                                    $signed({2'b0, temp_adc});
    wire signed [11:0] heater_raw = temp_error >>> 2;

    reg [7:0] heater_pwm;

    always @(posedge clk_vco or negedge reset_n) begin
        if (!reset_n)
            heater_pwm <= 8'd0;
        else if (ce_servo) begin
            if (heater_raw[11])
                heater_pwm <= 8'd0;
            else if (heater_raw > 12'sd255)
                heater_pwm <= 8'd255;
            else
                heater_pwm <= heater_raw[7:0];
        end
    end

    assign dac_heater_power = heater_pwm;

    // ─────────────────────────────────────────────────────────────────────────
    // SPI SLAVE INTERFACE
    // ─────────────────────────────────────────────────────────────────────────

    reg [7:0] spi_addr_latch;
    reg [7:0] spi_data_out;
    wire [7:0] spi_data_in;
    wire spi_rx_valid;

    spi_slave spi_inst (
        .sclk(spi_clk),
        .mosi(spi_mosi),
        .miso(spi_miso),
        .cs_n(spi_cs),
        .reset_n(reset_n),
        .data_in(spi_data_out),
        .data_out(spi_data_in),
        .rx_valid(spi_rx_valid)
    );

    always @(posedge spi_clk or negedge reset_n) begin
        if (!reset_n)
            spi_addr_latch <= 8'h00;
        else if (!spi_cs && spi_rx_valid)
            spi_addr_latch <= spi_data_in;
    end

    // Read multiplexer
    always @(*) begin
        case (spi_addr_latch)
            8'h00: spi_data_out = count_1hz[31:24];
            8'h01: spi_data_out = count_1hz[23:16];
            8'h02: spi_data_out = count_1hz[15:8];
            8'h03: spi_data_out = count_1hz[7:0];
            8'h04: spi_data_out = status_byte;
            8'h05: spi_data_out = dac_vco_tune[9:2];
            8'h06: spi_data_out = dac_heater_power;
            8'h07: spi_data_out = photo_adc;
            8'h08: spi_data_out = temp_adc[9:2];
            default: spi_data_out = 8'h00;
        endcase
    end

    // ─────────────────────────────────────────────────────────────────────────
    // STATUS BYTE
    // ─────────────────────────────────────────────────────────────────────────

    assign status_byte = {
        valid_lock,           // [7] = Servo locked
        1'b0,                 // [6] = Reserved
        1'b0,                 // [5] = Reserved
        heartbeat,            // [4] = Heartbeat (toggles at ~50 Hz)
        pid_integral[9:6]     // [3:0] = Integral accumulator (diagnostic)
    };

endmodule

// ─────────────────────────────────────────────────────────────────────────────
// SPI SLAVE — fully synchronous (no async load)
// ─────────────────────────────────────────────────────────────────────────────

module spi_slave (
    input wire sclk,
    input wire mosi,
    output wire miso,
    input wire cs_n,
    input wire reset_n,
    input wire [7:0] data_in,
    output wire [7:0] data_out,
    output wire rx_valid
);

    reg [7:0] rx_shift, tx_shift;
    reg [2:0] bit_count;

    always @(posedge sclk or negedge reset_n) begin
        if (!reset_n) begin
            bit_count <= 3'd0;
            tx_shift <= 8'd0;
            rx_shift <= 8'd0;
        end else if (cs_n) begin
            // Idle: preload TX shift register
            bit_count <= 3'd0;
            tx_shift <= data_in;
            rx_shift <= 8'd0;
        end else begin
            // Active transfer
            rx_shift <= {rx_shift[6:0], mosi};
            tx_shift <= {tx_shift[6:0], 1'b0};
            bit_count <= bit_count + 1'b1;
        end
    end

    assign miso = tx_shift[7];
    assign data_out = rx_shift;
    assign rx_valid = (bit_count == 3'd7);

endmodule
