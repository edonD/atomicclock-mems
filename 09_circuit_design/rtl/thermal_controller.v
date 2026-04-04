// Thermal Controller — proportional heater control
// Computes error = setpoint - temp_adc, applies proportional gain (shift),
// saturates output to DAC range.

`timescale 1ns / 1ps

module thermal_controller #(
    parameter ADC_WIDTH = 10,
    parameter DAC_WIDTH = 8,
    parameter [ADC_WIDTH-1:0] SETPOINT = 350,
    parameter SHIFT = 2      // proportional gain = 1/(2^SHIFT)
)(
    input  wire                    clk,
    input  wire                    rst_n,
    input  wire                    ce,
    input  wire [ADC_WIDTH-1:0]    temp_adc,
    output reg  [DAC_WIDTH-1:0]    heater_pwm
);

    localparam signed [ADC_WIDTH+1:0] DAC_MAX_EXT = {{(ADC_WIDTH+2-DAC_WIDTH){1'b0}}, {DAC_WIDTH{1'b1}}};

    // Signed error: setpoint - measured
    wire signed [ADC_WIDTH+1:0] temp_error =
        $signed({2'b0, SETPOINT}) - $signed({2'b0, temp_adc});

    // Proportional output with arithmetic shift
    wire signed [ADC_WIDTH+1:0] heater_raw = temp_error >>> SHIFT;

    // Saturate
    wire [DAC_WIDTH-1:0] heater_sat =
        heater_raw[ADC_WIDTH+1]         ? {DAC_WIDTH{1'b0}} :       // negative → 0
        (heater_raw > DAC_MAX_EXT)      ? {DAC_WIDTH{1'b1}} :       // overflow → max
        heater_raw[DAC_WIDTH-1:0];

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n)
            heater_pwm <= {DAC_WIDTH{1'b0}};
        else if (ce)
            heater_pwm <= heater_sat;
    end

endmodule
