#=========================================================================
# SramMinion PyMTL wrapper
#=========================================================================

from pymtl3                         import *
from pymtl3.stdlib                  import stream
from pymtl3.passes.backends.verilog import *
from pymtl3.stdlib.mem              import mk_mem_msg, MemMsgType

class SramMinion( VerilogPlaceholder, Component ):

  def construct( s ):

    # If translated into Verilog, we use the explicit name

    s.set_metadata( VerilogTranslationPass.explicit_module_name, 'SramMinion' )

    # Default memory message has 8 bits opaque field and 32 bits address

    MemReqType, MemRespType = mk_mem_msg( 8, 32, 32 )

    # Interface

    s.minion = stream.ifcs.MinionIfcRTL( MemReqType, MemRespType )

