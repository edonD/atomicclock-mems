// CSAC Digital Top — Project Parameters
// All design constants in one place. Override via module parameters.

`ifndef CSAC_PKG_V
`define CSAC_PKG_V

// Frequency divider
`define CSAC_DIV_WIDTH       33
`define CSAC_SERVO_BIT       26   // ~50 Hz enable from 6.835 GHz
`define CSAC_ONEHZ_BIT       32   // ~1 Hz enable

// PID controller
`define CSAC_PID_KP          4'sd2
`define CSAC_PID_KI          4'sd1
`define CSAC_PID_KD          4'sd3
`define CSAC_PID_SETPOINT    8'd50
`define CSAC_PID_ADC_W       8
`define CSAC_PID_DAC_W       10

// Lock detector
`define CSAC_LOCK_THRESH     8'd10
`define CSAC_LOCK_WINDOW     4'd8

// Thermal controller
`define CSAC_TEMP_SETPOINT   10'd350
`define CSAC_TEMP_ADC_W      10
`define CSAC_TEMP_DAC_W      8
`define CSAC_TEMP_SHIFT      2

// SPI
`define CSAC_SPI_DATA_W      8

// CDC
`define CSAC_CDC_STAGES      2

`endif
