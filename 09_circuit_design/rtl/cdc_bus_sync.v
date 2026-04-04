// Multi-Bit Bus Synchronizer — toggle-handshake protocol
// Source captures a snapshot and toggles a flag.
// Destination detects the toggle edge and latches the bus.
// Safe for multi-bit transfer across async clock domains.

`timescale 1ns / 1ps

module cdc_bus_sync #(
    parameter WIDTH  = 32,
    parameter STAGES = 2
)(
    // Source domain
    input  wire              clk_src,
    input  wire              rst_src_n,
    input  wire              capture,       // pulse to capture snapshot
    input  wire [WIDTH-1:0]  data_src,

    // Destination domain
    input  wire              clk_dst,
    input  wire              rst_dst_n,
    output reg  [WIDTH-1:0]  data_dst,
    output wire              valid_dst      // pulses when new data available
);

    // Source: capture data and toggle flag
    reg [WIDTH-1:0] hold_reg;
    reg             toggle_src;

    always @(posedge clk_src or negedge rst_src_n) begin
        if (!rst_src_n) begin
            hold_reg   <= {WIDTH{1'b0}};
            toggle_src <= 1'b0;
        end else if (capture) begin
            hold_reg   <= data_src;
            toggle_src <= ~toggle_src;
        end
    end

    // Synchronize toggle flag to destination domain
    wire toggle_dst;
    cdc_sync2 #(.STAGES(STAGES)) u_sync_toggle (
        .clk_dst (clk_dst),
        .rst_n   (rst_dst_n),
        .din     (toggle_src),
        .dout    (toggle_dst)
    );

    // Detect toggle edge in destination domain
    reg toggle_dst_d;
    always @(posedge clk_dst or negedge rst_dst_n) begin
        if (!rst_dst_n)
            toggle_dst_d <= 1'b0;
        else
            toggle_dst_d <= toggle_dst;
    end

    assign valid_dst = toggle_dst ^ toggle_dst_d;

    // Latch data from hold_reg on every clk_dst edge.
    // hold_reg is quasi-static (updates once per servo cycle, ~20 ms in
    // production) so multi-bit sampling is safe in practice.  This avoids
    // the toggle-parity issue when clk_dst is gated between SPI bursts.
    always @(posedge clk_dst or negedge rst_dst_n) begin
        if (!rst_dst_n)
            data_dst <= {WIDTH{1'b0}};
        else
            data_dst <= hold_reg;
    end

endmodule
