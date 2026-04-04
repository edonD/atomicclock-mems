// Lock Detector — declares lock when |error| < threshold for N consecutive samples

`timescale 1ns / 1ps

module lock_detector #(
    parameter ERROR_WIDTH  = 9,        // signed error width (from PID)
    parameter THRESH_WIDTH = 8,
    parameter [THRESH_WIDTH-1:0] THRESHOLD = 10,
    parameter WINDOW_BITS  = 4,
    parameter [WINDOW_BITS-1:0] WINDOW = 8
)(
    input  wire                             clk,
    input  wire                             rst_n,
    input  wire                             ce,
    input  wire signed [ERROR_WIDTH-1:0]    error,
    output reg                              locked
);

    // Absolute value of error
    wire [ERROR_WIDTH-2:0] abs_error =
        error[ERROR_WIDTH-1] ? (~error[ERROR_WIDTH-2:0] + 1'b1) : error[ERROR_WIDTH-2:0];

    wire error_small = (abs_error < {{(ERROR_WIDTH-1-THRESH_WIDTH){1'b0}}, THRESHOLD});

    reg [WINDOW_BITS-1:0] counter;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            counter <= {WINDOW_BITS{1'b0}};
            locked  <= 1'b0;
        end else if (ce) begin
            if (error_small) begin
                if (counter == WINDOW)
                    locked <= 1'b1;
                else
                    counter <= counter + {{(WINDOW_BITS-1){1'b0}}, 1'b1};
            end else begin
                counter <= {WINDOW_BITS{1'b0}};
                locked  <= 1'b0;
            end
        end
    end

endmodule
