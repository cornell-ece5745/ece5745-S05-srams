//========================================================================
// SRAM RTL with custom low-level interface
//========================================================================
// This is the SRAM RTL model with our own low-level interface. It
// contains an instance of either a SRAM generated by OpenRAM memory
// compiler or a This is the SRAM RTL model with our own low-level
// interfacegeneric SRAM RTL model (SramGenericPRTL).
//
// The interface of this module are prefixed by port0_, meaning all reads
// and writes happen through the only port. Multiported SRAMs have ports
// prefixed by port1_, port2_, etc.
//
// The following list describes each port of this module.
//
//  Port Name     Direction  Description
//  ----------------------------------------------------------------------
//  port0_val     I          port enable (1 = enabled)
//  port0_type    I          transaction type, 0 = read, 1 = write
//  port0_idx     I          index of the SRAM
//  port0_wdata   I          write data
//  port0_rdata   O          read data output
//

`ifndef SRAM_SRAM_VRTL
`define SRAM_SRAM_VRTL

`include "sram/SramGenericVRTL.v"
`include "sram/SRAM_32x256_1rw.v"
`include "sram/SRAM_64x64_1rw.v"
`include "sram/SRAM_128x256_1rw.v"

// ''' TUTORIAL TASK '''''''''''''''''''''''''''''''''''''''''''''''''''''
// Include new SRAM configuration RTL model
// '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''\/

module sram_SramVRTL
#(
  parameter p_data_nbits  = 32,
  parameter p_num_entries = 256,

  // Local constants not meant to be set from outside the module
  parameter c_addr_nbits  = $clog2(p_num_entries),
  parameter c_data_nbytes = (p_data_nbits+7)/8 // $ceil(p_data_nbits/8)
)(
  input  logic                      clk,
  input  logic                      reset,
  input  logic                      port0_val,
  input  logic                      port0_type,
  input  logic [c_addr_nbits-1:0]   port0_idx,
  input  logic [p_data_nbits-1:0]   port0_wdata,
  output logic [p_data_nbits-1:0]   port0_rdata
);

  logic                     clk0;
  logic                     web0;
  logic                     csb0;
  logic [c_addr_nbits-1:0]  addr0;
  logic [p_data_nbits-1:0]  din0;
  logic [p_data_nbits-1:0]  dout0;

  assign clk0  = clk;
  assign web0  = ~port0_type;
  assign csb0  = ~port0_val;
  assign addr0 = port0_idx;
  assign din0  = port0_wdata;

  assign port0_rdata = dout0;

  generate
    if      ( p_data_nbits == 32  && p_num_entries == 256 ) SRAM_32x256_1rw  sram (.*);
    else if ( p_data_nbits == 64  && p_num_entries == 64  ) SRAM_64x64_1rw   sram (.*);
    else if ( p_data_nbits == 128 && p_num_entries == 256 ) SRAM_128x256_1rw sram (.*);

    else
      sram_SramGenericVRTL#(p_data_nbits,p_num_entries) sram (.*);

  endgenerate

endmodule

`endif /* SRAM_SRAM_VRTL */

