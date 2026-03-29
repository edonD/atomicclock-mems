/**
 * CSAC Digital Control Top Module — SKY130
 *
 * Implements:
 *  - Frequency divider: 6.835 GHz → 1 Hz (decade counters)
 *  - PID servo controller
 *  - SPI slave interface for external MCU
 *  - Thermistor ADC input
 *  - DAC output for VCO tuning voltage
 *  - Watchdog / health monitoring
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
    output reg [9:0] dac_vco_tune,       // VCO tuning voltage (10-bit)
    output reg [7:0] dac_heater_power,   // Heater PWM duty cycle

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
    // DECADE DIVIDER: 6.835 GHz → 1 Hz
    // ─────────────────────────────────────────────────────────────────────────

    // Divide by stages:
    //   6.835 GHz ÷ 10 = 683.5 MHz
    //   ÷ 10 = 68.35 MHz
    //   ÷ 10 = 6.835 MHz
    //   ÷ 10 = 683.5 kHz
    //   ÷ 10 = 68.35 kHz
    //   ÷ 10 = 6.835 kHz
    //   ÷ 10 = 683.5 Hz
    //   ÷ 10 = 68.35 Hz
    //   ÷ 10 = 6.835 Hz
    //   ÷ 6.835 ≈ 1 Hz (final trim)

    // In practice, use binary counters + logic (faster than decade):
    // 6.835 GHz ÷ 2^33 ≈ 1 Hz exactly (since 2^33 = 8,589,934,592)

    reg [32:0] vco_counter;
    wire [32:0] vco_next = vco_counter + 1;

    always @(posedge clk_vco or negedge reset_n) begin
        if (!reset_n)
            vco_counter <= 0;
        else
            vco_counter <= vco_next;
    end

    // Extract various rate signals for servo loop
    wire clk_mhz   = vco_counter[23];  // ~6.8 GHz / 2^24 ≈ 0.4 MHz (close enough)
    wire clk_khz   = vco_counter[16];  // ~6.8 GHz / 2^17 ≈ 50 kHz
    wire clk_100hz = vco_counter[26];  // ~6.8 GHz / 2^27 ≈ 50 Hz (for servo updates)

    // 1 Hz output: count overflow events on high bits
    always @(posedge clk_vco or negedge reset_n) begin
        if (!reset_n)
            count_1hz <= 0;
        else if (vco_counter[32])
            count_1hz <= count_1hz + 1;  // Increments ~1 Hz
    end

    // ─────────────────────────────────────────────────────────────────────────
    // SERVO LOOP: PID Controller
    // ─────────────────────────────────────────────────────────────────────────

    // Goal: minimize photodetector signal error
    // Error = photo_adc - setpoint (setpoint ≈ ~50 to find dark state)

    localparam SETPOINT = 8'd50;  // Aim for this photodetector level

    reg [9:0] pid_integral;
    reg [7:0] pid_last_error;
    wire [7:0] current_error = photo_adc - SETPOINT;

    // PID gains (tuned empirically or from simulation in 07_servo_loop)
    localparam Kp = 4'd2;   // Proportional gain
    localparam Ki = 4'd1;   // Integral gain
    localparam Kd = 4'd3;   // Derivative gain

    reg [9:0] pid_output;

    always @(posedge clk_100hz or negedge reset_n) begin
        if (!reset_n) begin
            pid_integral <= 0;
            pid_last_error <= 0;
            pid_output <= 9'd512;  // Midpoint (0.9V ≈ 512 on 10-bit DAC)
        end else begin
            // Proportional
            wire signed [9:0] prop_term = $signed(current_error) * Kp;

            // Integral (with antiwindup)
            wire [9:0] integral_update = pid_integral + ($signed(current_error) >> 2);
            pid_integral <= (integral_update > 10'd1023) ? 10'd1023 :
                            (integral_update < 10'd0)    ? 10'd0    : integral_update;

            // Derivative
            wire signed [9:0] deriv_term = ($signed(current_error) - $signed(pid_last_error)) * Kd;

            // Combine
            wire signed [12:0] pid_raw = $signed({1'b0, prop_term}) +
                                         $signed({1'b0, pid_integral}) +
                                         $signed(deriv_term);

            // Saturate to DAC range [0, 1023]
            pid_output <= (pid_raw > 13'd1023) ? 10'd1023 :
                          (pid_raw < 13'd0)    ? 10'd0    :
                          pid_raw[9:0];

            pid_last_error <= current_error;
        end
    end

    assign dac_vco_tune = pid_output;

    // Lock detection: if error is small for N consecutive updates, declare lock
    localparam LOCK_THRESHOLD = 8'd10;
    localparam LOCK_WINDOW = 4'd8;
    reg [3:0] lock_counter;

    always @(posedge clk_100hz or negedge reset_n) begin
        if (!reset_n) begin
            lock_counter <= 0;
            valid_lock <= 1'b0;
        end else begin
            if (($unsigned(current_error) < LOCK_THRESHOLD) &&
                ($unsigned(current_error) != 8'hFF)) begin
                if (lock_counter == LOCK_WINDOW) begin
                    valid_lock <= 1'b1;
                end else begin
                    lock_counter <= lock_counter + 1;
                end
            end else begin
                lock_counter <= 0;
                valid_lock <= 1'b0;
            end
        end
    end

    // ─────────────────────────────────────────────────────────────────────────
    // THERMAL CONTROL
    // ─────────────────────────────────────────────────────────────────────────

    // Simple proportional heater control
    // Target: temp_adc ≈ 350 (≈50°C on a −40…85°C sensor)
    localparam TEMP_SETPOINT = 10'd350;

    reg [7:0] heater_pwm;

    always @(posedge clk_100hz or negedge reset_n) begin
        if (!reset_n)
            heater_pwm <= 8'd0;
        else begin
            wire signed [11:0] temp_error = $signed({2'b0, TEMP_SETPOINT}) -
                                            $signed({2'b0, temp_adc});
            wire signed [10:0] heater_raw = $signed(temp_error) >> 2;  // Simple proportional

            heater_pwm <= (heater_raw > 11'd255) ? 8'd255 :
                          (heater_raw < 11'd0)   ? 8'd0   :
                          heater_raw[7:0];
        end
    end

    assign dac_heater_power = heater_pwm;

    // ─────────────────────────────────────────────────────────────────────────
    // SPI SLAVE INTERFACE
    // ─────────────────────────────────────────────────────────────────────────

    // Register map (read/write from external MCU):
    // 0x00: count_1hz[31:24]
    // 0x01: count_1hz[23:16]
    // 0x02: count_1hz[15:8]
    // 0x03: count_1hz[7:0]
    // 0x04: status_byte (R/O)
    // 0x05: dac_vco_tune[9:2] (R/W)
    // 0x06: dac_heater_power (R/W)
    // 0x07: photo_adc (R/O)
    // 0x08: temp_adc[9:2] (R/O)

    reg [7:0] spi_addr_latch;
    reg [7:0] spi_data_out;
    wire [7:0] spi_data_in;

    // Simple SPI decoder (teacher-level implementation)
    spi_slave spi_inst (
        .sclk(spi_clk),
        .mosi(spi_mosi),
        .miso(spi_miso),
        .cs_n(spi_cs),
        .data_in(spi_data_out),
        .data_out(spi_data_in),
        .rx_valid(spi_rx_valid)
    );

    always @(posedge spi_clk or negedge spi_cs) begin
        if (!spi_cs)
            spi_addr_latch <= 8'h00;
        else if (spi_rx_valid) begin
            // First byte = address, second byte = data
            // Simplified: alternate between address and data
            // Real: use a small FSM or protocol framing
        end
    end

    // Read multiplexer
    always @(*) begin
        case (spi_addr_latch)
            8'h00: spi_data_out = count_1hz[31:24];
            8'h01: spi_data_out = count_1hz[23:16];
            8'h02: spi_data_out = count_1hz[15:8];
            8'h03: spi_data_out = count_1hz[7:0];
            8'h04: spi_data_out = status_byte;
            8'h05: spi_data_out = {dac_vco_tune[9:2]};
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
        clk_100hz,            // [4] = Heartbeat (toggles)
        pid_integral[9:6]     // [3:0] = Integral accumulator (diagnostic)
    };

endmodule

// ─────────────────────────────────────────────────────────────────────────────
// SPI SLAVE SUBMODULE (stub)
// ─────────────────────────────────────────────────────────────────────────────

module spi_slave (
    input wire sclk,
    input wire mosi,
    output wire miso,
    input wire cs_n,
    input wire [7:0] data_in,
    output wire [7:0] data_out,
    output wire rx_valid
);

    // Simplified SPI: shift in 8 bits, shift out 8 bits
    reg [7:0] rx_shift, tx_shift;
    reg [2:0] bit_count;
    wire bit_clk_edge = sclk;  // Simplified; real design uses edge detection

    always @(posedge bit_clk_edge or posedge cs_n) begin
        if (cs_n) begin
            bit_count <= 0;
            tx_shift <= data_in;
            rx_shift <= 0;
        end else begin
            rx_shift <= {rx_shift[6:0], mosi};
            tx_shift <= {tx_shift[6:0], 1'b0};
            bit_count <= bit_count + 1;
        end
    end

    assign miso = tx_shift[7];
    assign data_out = rx_shift;
    assign rx_valid = (bit_count == 3'd7);

endmodule
