// Frequency Divider — binary counter with clock-enable outputs
// Divides clk by 2^DIV_WIDTH. Generates single-cycle enable pulses
// at configurable bit positions for servo and 1 Hz update rates.

`timescale 1ns / 1ps

module freq_divider #(
    parameter DIV_WIDTH = 33,
    parameter SERVO_BIT = 26,   // ce_servo from this counter bit
    parameter ONEHZ_BIT = 32    // ce_1hz from this counter bit
)(
    input  wire                   clk,
    input  wire                   rst_n,
    output wire [DIV_WIDTH-1:0]   count,
    output wire                   ce_servo,
    output wire                   ce_1hz,
    output wire                   heartbeat
);

    // Main counter
    reg [DIV_WIDTH-1:0] counter;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n)
            counter <= {DIV_WIDTH{1'b0}};
        else
            counter <= counter + {{(DIV_WIDTH-1){1'b0}}, 1'b1};
    end

    assign count = counter;

    // Edge detectors for clock enables
    reg servo_bit_d, onehz_bit_d;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            servo_bit_d <= 1'b0;
            onehz_bit_d <= 1'b0;
        end else begin
            servo_bit_d <= counter[SERVO_BIT];
            onehz_bit_d <= counter[ONEHZ_BIT];
        end
    end

    assign ce_servo  = counter[SERVO_BIT] & ~servo_bit_d;
    assign ce_1hz    = counter[ONEHZ_BIT] & ~onehz_bit_d;
    assign heartbeat = counter[SERVO_BIT];

endmodule
