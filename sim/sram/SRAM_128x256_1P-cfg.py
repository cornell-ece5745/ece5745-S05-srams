#=========================================================================
# OpenRAM Memory Compiler Configuration File
#=========================================================================
# You should really only change the word_size and the num_words
# parameters. Leave the other parameters alone for now. The word_size
# is in units of bits.

word_size = 128
num_words = 256
num_banks = 1
tech_name = "freepdk45"
process_corners = ["TT"]
supply_voltages = [ 1.1 ]
temperatures = [ 25 ]
output_path = "SRAM_128x256_1P_inner"
output_name = "SRAM_128x256_1P_inner"

