// SPI Master Bus-Functional Model
// Task-based SPI master for testbench use.
// Drives sclk, mosi, cs_n and captures miso.

module spi_master_bfm #(
    parameter CLK_HALF_PERIOD = 50  // spi_clk half-period in time units
)(
    output reg        sclk,
    output reg        mosi,
    input  wire       miso,
    output reg        cs_n
);

    reg [7:0] captured_byte;

    initial begin
        sclk = 1'b0;
        mosi = 1'b0;
        cs_n = 1'b1;
    end

    // Transfer one byte: send tx_byte, receive rx_byte
    task spi_xfer;
        input  [7:0] tx_byte;
        output [7:0] rx_byte;
        integer i;
        begin
            rx_byte = 8'd0;
            for (i = 7; i >= 0; i = i - 1) begin
                mosi = tx_byte[i];
                #(CLK_HALF_PERIOD);
                sclk = 1'b1;           // rising edge: slave samples mosi
                rx_byte = {rx_byte[6:0], miso};
                #(CLK_HALF_PERIOD);
                sclk = 1'b0;           // falling edge
            end
        end
    endtask

    // Write address byte, then read data byte back
    task spi_read_reg;
        input  [7:0] addr;
        output [7:0] data;
        reg [7:0] dummy;
        begin
            cs_n = 1'b0;
            #(CLK_HALF_PERIOD * 2);
            spi_xfer(addr, dummy);     // send address
            spi_xfer(8'h00, data);     // clock out data
            #(CLK_HALF_PERIOD * 2);
            cs_n = 1'b1;
            #(CLK_HALF_PERIOD * 4);    // inter-transaction gap
        end
    endtask

endmodule
