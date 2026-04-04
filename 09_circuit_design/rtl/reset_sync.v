// Reset Synchronizer — async assert, sync deassert
// Ensures clean reset release aligned to destination clock.

`timescale 1ns / 1ps

module reset_sync #(
    parameter STAGES = 2
)(
    input  wire clk,
    input  wire rst_async_n,
    output wire rst_sync_n
);

    reg [STAGES-1:0] sync_chain;

    always @(posedge clk or negedge rst_async_n) begin
        if (!rst_async_n)
            sync_chain <= {STAGES{1'b0}};
        else
            sync_chain <= {sync_chain[STAGES-2:0], 1'b1};
    end

    assign rst_sync_n = sync_chain[STAGES-1];

endmodule
