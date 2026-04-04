// 2-FF Synchronizer — single-bit clock domain crossing
// Standard double-flop for metastability resolution.

`timescale 1ns / 1ps

module cdc_sync2 #(
    parameter STAGES    = 2,
    parameter RESET_VAL = 1'b0
)(
    input  wire clk_dst,
    input  wire rst_n,
    input  wire din,
    output wire dout
);

    reg [STAGES-1:0] sync_chain;

    always @(posedge clk_dst or negedge rst_n) begin
        if (!rst_n)
            sync_chain <= {STAGES{RESET_VAL}};
        else
            sync_chain <= {sync_chain[STAGES-2:0], din};
    end

    assign dout = sync_chain[STAGES-1];

endmodule
