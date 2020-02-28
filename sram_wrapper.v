//-----------------------------------------------------------------------------
// SRAM
//-----------------------------------------------------------------------------
module SRAM_64x64_1P
(
  input wire           clk,
  input wire           reset,
  input wire           CE1,
  input wire           OEB1,
  input wire           CSB1,
  input wire  [   5:0] A1,
  input wire  [  63:0] I1,
  input wire           WEB1,
  output reg  [  63:0] O1
);
  parameter DATA_WIDTH = 64 ;
  parameter ADDR_WIDTH = 6 ;
  // Internal wires
  reg [DATA_WIDTH-1:0] DATA;
  // Internal regs
  reg                  valid;
  always_ff @(posedge CE1) begin
    valid <= (~CSB1 & ~WEB1);
  end
  always_comb begin
    // Tri-State
    DATA = 'bz;
    // DATA bus
    if (valid) begin
      DATA = I1;
    end
  end
  // Assigns
  assign O1 = DATA;
  // Actual RAM
  SRAM_64x64_1P_inner sram ( .DATA(DATA),
                             .ADDR(A1  ),
                             .CSb (CSB1),
                             .WEb (WEB1),
                             .OEb (OEB1),
                             .clk (CE1 )
                           );
endmodule // SRAM_64x64_1P

