#=========================================================================
# SRAM PyMTL wrapper
#=========================================================================

from pymtl3 import *
from pymtl3.passes.backends.verilog import *

class Sram( VerilogPlaceholder, Component ):

  def construct( s, data_nbits=32, num_entries=256, mask_size=0 ):

    addr_width = clog2( num_entries )       # address width
    nbytes     = int( data_nbits + 7 ) // 8 # $ceil(num_bits/8)

    # Interface

    s.port0_val   = InPort ()
    s.port0_type  = InPort ()
    s.port0_idx   = InPort ( addr_width )
    s.port0_wdata = InPort ( data_nbits   )
    s.port0_rdata = OutPort( data_nbits   )

    # if mask_size > 0:
    #   s.port0_wben = InPort( mk_bits(mask_size) )

    # Verilog import setup

    from os import path
    s.set_metadata( VerilogPlaceholderPass.src_file, path.dirname(__file__) + '/Sram.v' )
    s.set_metadata( VerilogPlaceholderPass.top_module, 'Sram' )
    s.set_metadata( VerilogPlaceholderPass.params, {
      'p_data_nbits'  : data_nbits,
      'p_num_entries' : num_entries,
    })

