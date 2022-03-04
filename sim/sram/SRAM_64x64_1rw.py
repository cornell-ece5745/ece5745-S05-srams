#=========================================================================
# 64 bits x 64 words SRAM model
#=========================================================================

from .BaseSRAM1rw import BaseSRAM1rw

class SRAM_64x64_1rw( BaseSRAM1rw ):

  # Make sure widths match the .v

  def construct( s ):
    super().construct( 64, 64 )
