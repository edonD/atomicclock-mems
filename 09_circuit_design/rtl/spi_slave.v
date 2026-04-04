// SPI Slave — 8-bit shift register with synchronous reset
// CPOL=0, CPHA=0: data sampled on rising sclk edge.
// cs_n checked synchronously (no async loads).

`timescale 1ns / 1ps

module spi_slave #(
    parameter DATA_WIDTH = 8
)(
    input  wire                    sclk,
    input  wire                    rst_n,
    input  wire                    mosi,
    output wire                    miso,
    input  wire                    cs_n,
    input  wire [DATA_WIDTH-1:0]   tx_data,
    output wire [DATA_WIDTH-1:0]   rx_data,
    output wire                    rx_valid,
    output wire                    byte_done
);

    // verilator lint_off UNUSEDSIGNAL
    reg [DATA_WIDTH-1:0] rx_shift;
    // verilator lint_on UNUSEDSIGNAL
    reg [DATA_WIDTH-1:0] tx_shift;
    reg [$clog2(DATA_WIDTH)-1:0] bit_count;

    wire active = ~cs_n;

    always @(posedge sclk or negedge rst_n) begin
        if (!rst_n) begin
            rx_shift  <= {DATA_WIDTH{1'b0}};
            tx_shift  <= {DATA_WIDTH{1'b0}};
            bit_count <= {$clog2(DATA_WIDTH){1'b0}};
        end else begin
            if (!active) begin
                // Idle: preload TX, reset counter
                bit_count <= {$clog2(DATA_WIDTH){1'b0}};
                tx_shift  <= tx_data;
                rx_shift  <= {DATA_WIDTH{1'b0}};
            end else begin
                // Shift
                rx_shift  <= {rx_shift[DATA_WIDTH-2:0], mosi};
                bit_count <= bit_count + {{($clog2(DATA_WIDTH)-1){1'b0}}, 1'b1};
                if (bit_count == {$clog2(DATA_WIDTH){1'b1}}) begin
                    // Byte boundary: reload TX for next byte
                    tx_shift <= tx_data;
                end else begin
                    tx_shift <= {tx_shift[DATA_WIDTH-2:0], 1'b0};
                end
            end
        end
    end

    assign miso     = tx_shift[DATA_WIDTH-1];
    // Combinational: include current MOSI so complete byte is available
    // in the same cycle as rx_valid (avoids 1-cycle stale address bug)
    assign rx_data  = {rx_shift[DATA_WIDTH-2:0], mosi};
    assign rx_valid = active & (bit_count == {$clog2(DATA_WIDTH){1'b1}});
    assign byte_done = rx_valid;

endmodule
