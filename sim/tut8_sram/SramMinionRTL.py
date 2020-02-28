#=========================================================================
# Choose PyMTL or Verilog version
# =========================================================================
# Set this variable to 'pymtl' if you are using PyMTL for your RTL design
# or set this variable to 'verilog' if you are using Verilog for your RTL
# design.

rtl_language = 'pymtl'

#-------------------------------------------------------------------------
# Do not edit below this line
#-------------------------------------------------------------------------

# This is the PyMTL wrapper for the corresponding Verilog RTL model.

from pymtl3 import *
from pymtl3.stdlib.ifcs import MinionIfcRTL
from pymtl3.passes.backends.verilog import \
    VerilogPlaceholderConfigs, TranslationConfigs

# See if the course staff want to force testing a specific RTL language
# for their own testing.

import sys
if hasattr( sys, '_called_from_test' ):
  if sys._pymtl_rtl_override:
    rtl_language = sys._pymtl_rtl_override

# Import the appropriate version based on the rtl_language variable

if rtl_language == 'pymtl':
  from .SramMinionPRTL import SramMinionPRTL as _cls
else:
  raise Exception("Invalid RTL language!")

class SramMinionRTL( _cls ):
  def construct( s ):
    super().construct()
    # The translated Verilog must be xRTL.v instead of xPRTL.v
    s.config_verilog_translate = TranslationConfigs(
      translate=False,
      explicit_module_name = 'SramMinionRTL',
    )

