//========================================================================
// 64 bits x 64 words SRAM
//========================================================================

`ifndef SRAM_64x64_1rw
`define SRAM_64x64_1rw

`include "sram/SramGenericVRTL.v"

`ifndef SYNTHESIS

module SRAM_64x64_1rw
(
  input  logic        clk0,
  input  logic        web0,
  input  logic        csb0,
  input  logic [5:0]  addr0,
  input  logic [63:0] din0,
  output logic [63:0] dout0
);

  sram_SramGenericVRTL
  #(
    .p_data_nbits  (64),
    .p_num_entries (64)
  )
  sram_generic
  (
    .clk0  (clk0),
    .addr0 (addr0),
    .web0  (web0),
    .csb0  (csb0),
    .din0  (din0),
    .dout0 (dout0)
  );

endmodule

`endif /* SYNTHESIS */

`endif /* SRAM_64x64_1rw */

