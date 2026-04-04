// PID Controller — parameterized proportional-integral-derivative servo
// Computes error = adc_in - setpoint, applies PID gains, saturates output.
// Uses proper signed arithmetic throughout.

`timescale 1ns / 1ps

module pid_controller #(
    parameter ADC_WIDTH    = 8,
    parameter DAC_WIDTH    = 10,
    parameter GAIN_WIDTH   = 4,
    parameter signed [GAIN_WIDTH-1:0] KP = 2,
    parameter signed [GAIN_WIDTH-1:0] KD = 3,
    parameter [ADC_WIDTH-1:0] SETPOINT = 50
)(
    input  wire                         clk,
    input  wire                         rst_n,
    input  wire                         ce,
    input  wire [ADC_WIDTH-1:0]         adc_in,
    output reg  [DAC_WIDTH-1:0]         dac_out,
    output wire signed [ADC_WIDTH:0]    error_out
);

    localparam PTERM_W = ADC_WIDTH + GAIN_WIDTH + 1;

    localparam signed [PTERM_W-1:0] DAC_MAX = {{(PTERM_W-DAC_WIDTH){1'b0}}, {DAC_WIDTH{1'b1}}};  // 1023

    // Signed error: adc - setpoint
    wire signed [ADC_WIDTH:0] error = $signed({1'b0, adc_in}) - $signed({1'b0, SETPOINT});
    assign error_out = error;

    // State registers
    reg signed [DAC_WIDTH:0]   integral;
    reg signed [ADC_WIDTH:0]   last_error;

    // Sign-extend error and last_error to PTERM_W for p_term and d_term
    wire signed [PTERM_W-1:0] error_ext      = {{(PTERM_W-ADC_WIDTH-1){error[ADC_WIDTH]}}, error};
    wire signed [PTERM_W-1:0] last_error_ext = {{(PTERM_W-ADC_WIDTH-1){last_error[ADC_WIDTH]}}, last_error};

    // Combinational PID terms
    wire signed [PTERM_W-1:0] p_term = error_ext * KP;
    wire signed [PTERM_W-1:0] d_term = (error_ext - last_error_ext) * KD;

    // Integral update: sign-extend error and integral to DAC_WIDTH+2
    wire signed [DAC_WIDTH+1:0] integral_ext = {{1{integral[DAC_WIDTH]}}, integral};
    wire signed [DAC_WIDTH+1:0] error_i_ext  = {{(DAC_WIDTH+2-ADC_WIDTH-1){error[ADC_WIDTH]}}, error};
    wire signed [DAC_WIDTH+1:0] i_update     = integral_ext + (error_i_ext >>> 2);

    // Saturated integral — compare with width-matched constants
    localparam signed [DAC_WIDTH+1:0] DAC_MAX_I = {{2{1'b0}}, {DAC_WIDTH{1'b1}}};
    localparam signed [DAC_WIDTH+1:0] DAC_MIN_I = {(DAC_WIDTH+2){1'b0}};

    wire signed [DAC_WIDTH:0] i_sat =
        (i_update > DAC_MAX_I) ? DAC_MAX_I[DAC_WIDTH:0] :
        (i_update < DAC_MIN_I) ? DAC_MIN_I[DAC_WIDTH:0] :
        i_update[DAC_WIDTH:0];

    // Combined PID output — extend all terms to PTERM_W
    wire signed [PTERM_W-1:0] i_sat_ext = {{(PTERM_W-DAC_WIDTH-1){i_sat[DAC_WIDTH]}}, i_sat};
    wire signed [PTERM_W-1:0] pid_sum   = p_term + i_sat_ext + d_term;

    // Saturated output
    wire [DAC_WIDTH-1:0] dac_sat =
        pid_sum[PTERM_W-1]  ? {DAC_WIDTH{1'b0}} :         // negative -> 0
        (pid_sum > DAC_MAX) ? DAC_MAX[DAC_WIDTH-1:0] :     // overflow -> max
        pid_sum[DAC_WIDTH-1:0];

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            integral   <= {(DAC_WIDTH+1){1'b0}};
            last_error <= {(ADC_WIDTH+1){1'b0}};
            dac_out    <= {1'b1, {(DAC_WIDTH-1){1'b0}}};  // midpoint
        end else if (ce) begin
            integral   <= i_sat;
            last_error <= error;
            dac_out    <= dac_sat;
        end
    end

endmodule
