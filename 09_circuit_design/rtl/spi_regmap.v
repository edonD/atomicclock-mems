// SPI Register Map — address decode and read multiplexer
// Operates in spi_clk domain. Reads from CDC-synchronized data.
//
// Register map:
//   0x00-0x03: count_1hz[31:0]  (4 bytes, MSB first)  [R]
//   0x04:      status_byte                              [R]
//   0x05:      dac_vco_tune[9:2]                        [R]
//   0x06:      dac_heater_power                         [R]
//   0x07:      photo_adc                                [R]
//   0x08:      temp_adc[9:2]                            [R]

`timescale 1ns / 1ps

module spi_regmap (
    input  wire        sclk,
    input  wire        rst_n,
    input  wire        cs_n,
    input  wire        rx_valid,
    input  wire [7:0]  rx_data,
    output reg  [7:0]  tx_data,

    // Synchronized register inputs (already in sclk domain)
    input  wire [31:0] count_1hz_s,
    input  wire [7:0]  status_byte_s,
    // verilator lint_off UNUSEDSIGNAL
    input  wire [9:0]  dac_vco_tune_s,   // only [9:2] read via 8-bit SPI
    // verilator lint_on UNUSEDSIGNAL
    input  wire [7:0]  dac_heater_s,
    input  wire [7:0]  photo_adc_s,
    // verilator lint_off UNUSEDSIGNAL
    input  wire [9:0]  temp_adc_s         // only [9:2] read via 8-bit SPI
    // verilator lint_on UNUSEDSIGNAL
);

    reg [7:0] addr_latch;

    // Latch address on first valid byte when selected
    always @(posedge sclk or negedge rst_n) begin
        if (!rst_n)
            addr_latch <= 8'h00;
        else if (!cs_n && rx_valid)
            addr_latch <= rx_data;
    end

    // Combinational bypass: use rx_data directly when new address arrives,
    // so tx_data is valid in the same cycle for SPI tx_shift reload
    wire [7:0] read_addr = (!cs_n && rx_valid) ? rx_data : addr_latch;

    // Read multiplexer (active combinationally for next SPI byte)
    always @(*) begin
        case (read_addr)
            8'h00:   tx_data = count_1hz_s[31:24];
            8'h01:   tx_data = count_1hz_s[23:16];
            8'h02:   tx_data = count_1hz_s[15:8];
            8'h03:   tx_data = count_1hz_s[7:0];
            8'h04:   tx_data = status_byte_s;
            8'h05:   tx_data = dac_vco_tune_s[9:2];
            8'h06:   tx_data = dac_heater_s;
            8'h07:   tx_data = photo_adc_s;
            8'h08:   tx_data = temp_adc_s[9:2];
            default: tx_data = 8'h00;
        endcase
    end

endmodule
