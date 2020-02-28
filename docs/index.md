
ECE 5745 Section 4: SRAM Generators
==========================================================================

 - Author: Christopher Batten
 - Date: February 28, 2020

**Table of Contents**

 - Introduction
 - OpenRAM Memory Generator
 - Using SRAMs in RTL Models
 - Manual ASIC Flow with SRAM Macros

Introduction
--------------------------------------------------------------------------

Small memories can be easily synthesized using flip-flop or latch
standard cells, but synthesizing large memories can significantly impact
the area, energy, and timing of the overall design. ASIC designers often
use SRAM generators to "generate" arrays of memory bitcells and the
corresponding peripheral circuitry (e.g., address decoders, bitline
drivers, sense amps) which are combined into what is called an "SRAM
macro". These SRAM generators are parameterized to enable generating a
wide range of SRAM macros with different numbers of rows, columns, and
column muxes, as well as optional support for partial writes, built-in
self-test, and error correction. Similar to a standard-cell library, an
SRAM generator must generate not just layout but also all of the
necessary views to capture logical functionality, timing, geometry, and
power usage. These views can then by used by the ASIC tools to produce a
complete design which includes a mix of both standard cells and SRAM
macros.

In this section, we will first see how to use the open-source OpenRAM
memory generator to generate various views of an SRAM macro. Then we will
see how to use SRAMs in our RTL designs. Finally, we will put the these
two pieces together to combine synthesizable RTL with SRAM macros and
push the composition through the ASIC toolflow.

The first step is to start MobaXterm. From the _Start_ menu, choose
_MobaXterm Educational Edition > MobaXterm Educational Edition_. Then
double click on _ecelinux.ece.cornell.edu_ under _Saved sessions_ in
MobaXterm. Log in using your NetID and password. Click _Yes_ when asked
if you want to save your password. This will make it easier to open
multiple terminals if you need to.

Once you are at the `ecelinux` prompt, source the setup script, clone
this repository from GitHub, and define an environment variable to keep
track of the top directory for the project.

    % source setup-ece5745.sh
    % mkdir $HOME/ece5745
    % cd $HOME/ece5745
    % git clone https://github.com/cornell-ece5745/ece5745-S04-srams
    % cd ece5745-S04-srams
    % TOPDIR=$PWD

OpenRAM Memory Generator
--------------------------------------------------------------------------

Just as with standard-cell libraries, acquiring real SRAM generators is a
complex and potentially expensive process. It requires gaining access to
a specific fabrication technology, negotiating with a company which makes
the SRAM generator, and usually signing multiple non-disclosure
agreements. The OpenRAM memory generator is based on the same "fake" 45nm
technology that we are using for the Nangate standard-cell library. The
"fake" technology is representative enough to provide reasonable area,
energy, and timing estimates for our purposes. Let's take a look at how
to use the OpenRAM memory generator to generate various views of an SRAM
macro.

An SRAM generator takes as input a configuration file which specifies the
various parameters for the desired SRAM macro. Create a configuration
file with the following content using your favorite text editor. You
should name your file `SRAM_32x32_1P-cfg.py` and it should be located in
the directory shown below.

    % mkdir -p $TOPDIR/asic-manual/openram-mc
    % cd $TOPDIR/asic-manual/openram-mc
    % more SRAM_32x32_1P-cfg.py
    word_size = 32
    num_words = 32
    num_banks = 1
    tech_name = "freepdk45"
    process_corners = ["TT"]
    supply_voltages = [ 1.1 ]
    temperatures = [ 25 ]
    output_path = "SRAM_32x32_1P_inner"
    output_name = "SRAM_32x32_1P_inner"

In this example, we are generating a single-ported SRAM which has 64 rows
and 64 bits per row for a total capacity of 4096 bits or 512B. This size
is probably near the cross-over point where you might transition from
using synthesized memories to SRAM macros. OpenRAM will take this
configuration file as input and generate many different views of the SRAM
macro including: schematics (`.sp`), layout (`.gds`), a Verilog
behavioral model (`.v`), abstract logical, timing, power view (`.lib`),
and a physical view (`.lef`). These views can then be used by the ASIC
tools.

You can use the following command to run the OpenRAM memory generator.

    % cd $TOPDIR/asic-manual/openram-mc
    % openram -v SRAM_32x32_1P-cfg.py

It will take a few minutes to generate the SRAM macro. You can see the
resulting views here:

    % cd $TOPDIR/asic-manual/openram-mc/SRAM_32x32_1P_inner
    % ls -1
    SRAM_32x32_1P_inner.gds
    SRAM_32x32_1P_inner.lef
    SRAM_32x32_1P_inner.sp
    SRAM_32x32_1P_inner_TT_1p1V_25C.lib
    SRAM_32x32_1P_inner.v


You can find more information about the OpenRAM memory generator in this
recent research paper:

 - M. Guthaus et. al, "OpenRAM: An Open-Source Memory Compiler", Int'l
   Conf. on Computer-Aided Design (ICCAD), Nov. 2016.
   (https://doi.org/10.1145/2966986.2980098)

The following excerpt from the paper illustrates the microarchitecture
used in the single-port SRAM macro.

![](assets/fig/openram-sram-uarch.png)

The functionality of the pins are as follows:

 - `clk`: clock
 - `WEb`: write enable (active low)
 - `OEb`: output enable (active low)
 - `CSb`: whole SRAM enable (active low)
 - `ADDR`: address
 - `DATA`: read/write data

Notice that there is a single address, and a single read/write data bus.
This SRAM macro has a single read/write port and only supports executing
a single transaction at a time. The following excerpt from the paper
shows the timing diagram for a read and write transaction.

![](assets/fig/openram-sram-timing.png)

Prof. Batten will explain this timing diagram in more detail, especially
the important distinction between a _synchronous_ read SRAM and a
_combinational_ read register file. Take a few minutes to look at the
behavioral verilog. See if you can see how this models a synchronous read
SRAM.

    % cd $TOPDIR/asic-manual/openram-mc/SRAM_32x32_1P_inner
    % less SRAM_32x32_1P_inner.v

You can take a look at the generated transistor-level netlist like this:

    % cd $TOPDIR/asic-manual/openram-mc/SRAM_32x32_1P_inner
    % less -p " cell_6t " SRAM_32x32_1P_inner.sp

Now let's use Klayout look at the actual layout produced by the OpenRAM
memory generator.

    % cd $TOPDIR/asic-manual/openram-mc/SRAM_32x32_1P_inner
    % klayout -l $ECE5745_STDCELLS/klayout.lyp SRAM_32x32_1P_inner.gds

In Klayout, you can show/hide layers by double clicking on them on the
right panel. You can show more of the hierarchy by selecting _Display >
Increment Hierarchy_ from the menu.

Take a quick look at the `.lib` file and the `.lef` file for the SRAM
macro.

    % cd $TOPDIR/asic-manual/openram-mc/SRAM_32x32_1P_inner
    % less SRAM_32x32_1P_inner*.lib
    % less SRAM_32x32_1P_inner.lef

**To Do On Your Own:** Copy the configuration file and change it to
generate an SRAM which has 64 words and 32 bits per word. Name the
configuration `SRAM_64x32_1P_inner`. Take a look at the generated
layout.

Using SRAMs in RTL Models
--------------------------------------------------------------------------

Now that we understand how an SRAM generator works, let's see how to
actually use an SRAM in your RTL models. We have create a behavioral SRAM
model in the `sim/sram` subdirectory.

    % cd $TOPDIR/sim/sram
    % ls
    ...
    SramPRTL.py
    SramVRTL.v
    SramRTL.py

There is both a PyMTL and Verilog version. Both are parameterized by the
number of words and the bits per word, and both have the same pin-level
interface:

 - `port0_val`: port enable
 - `port0_type`: transaction type (0 = read, 1 = write)
 - `port0_idx`: which row to read/write
 - `port0_wdata`: write data
 - `port0_rdata`: read data

SRAMs use a latency _sensitive_ interface meaning a user must carefully
manage the timing for correct operation (i.e., set the read address and
then exactly one cycle later use the read data). In addition, the SRAM
cannot be "stalled". To illustrate how to use SRAM macros, we will create
a latency _insensitive_ minion wrapper around an SRAM which enables
writing and reading the SRAM using our standard memory messages. The
following figure illustrates our approach to implementing this wrapper:

![](assets/fig/sram-valrdy-wrapper-uarch2.png)

Here is a pipeline diagram that illustrates how this works.

```
 cycle : 0  1  2  3  4  5  6  7  8
 msg a : M0 Mx
 msg b :    M0 Mx
 msg c :       M0 M1 M2 M2 M2
 msg d :          M0 M1 q  q  M2     # msg c is in skid buffer
 msg e :             M0 M0 M0 M0 Mx

 cycle M0 M1 [q ] M2
    0: a
    1: b  a       a  # a flows through bypass queue
    2: c  b       b  # b flows through bypass queue
    3: d  c          # M2 is stalled, c will need to go into bypq
    4: e  d    c     #
    5: e      dc     # d skids behind c into the bypq
    6: e       d  c  # c is dequeued from bypq
    7: e          d  # d is dequeued from bypq
    8:    e       e  # e flows through bypass queue
```

Take a closer look at the SRAM minion wrapper we provide you. Here is the
PyMTL version (we will provide you a similar Verilog version for you to
use):

    % cd $TOPDIR/sim/tut8_sram
    % more SramMinionPRTL.py
    from sram import SramRTL
    ...
    s.sram = SramRTL( num_bits, num_words )

To use an SRAM in a PyMTL model, simply import `SramRTL`, instantiate the
SRAM, and set the number of words and number of bits per word. We can run
a test on the SRAM minion wrapper like this:

```
 % mkdir -p $TOPDIR/sim/build
 % cd $TOPDIR/sim/build
 % py.test ../tut8_sram/test/SramMinionRTL_test.py -k test_generic[random_0_3] -s
  1r .                                   > ( ) > #
  2: .                                   > ( ) > #
  3: (wr:00:00000000:0:b1aa20f1ac2c79ec) > ( ) >
  4: (wr:01:00000008:0:eadb7347037714f4) > (*) > (wr:00:0:0:                )
  5: (wr:02:00000010:0:f956c79b184e3089) > (*) > #
  6: (wr:03:00000018:0:af99be5f98bb9cf5) > (*) > #
  7: #                                   > ( ) > #
  8: #                                   > ( ) > (wr:01:0:0:                )
  9: #                                   > ( ) > #
 10: #                                   > ( ) > #
 11: #                                   > ( ) > #
 12: #                                   > ( ) > (wr:02:0:0:                )
 13: #                                   > ( ) > #
```

The first write transaction takes a single cycle to go through the SRAM
minion wrapper, but then the response interface is not ready on cycles
5-7. The second and third write transactions are still accepted by the
SRAM minion wrapper and they will end up in the bypass queue, but the
later transactions are stalled because the request interface is not
ready. No transactions are lost.

The SRAM module is parameterized to enable initial design space
exploration, but just because we choose a specific SRAM configuration
does not mean the files we need to create the corresponding SRAM macro
exist yet. Once we have finalized the SRAM size, we need to go through a
five step process.

**Step 1: See if SRAM configuration already exists**

The first step is to see if your desired SRAM configuration already
exists. You can do this by looking at the names of the `-cfg.py` files in
the `sim/sram` subdirectory.

    % cd $TOPDIR/sram
    % ls *-cfg.py
    SRAM_128x256_1P-cfg.py
    SRAM_32x256_1P-cfg.py

This means there are two SRAM configurations already available. One SRAM
has 256 words each with 128 bits and the other SRAM has 256 words each
with 32 bits. If the SRAM configuration you need already exists then you
are done and can skip the remaining steps.

**Step 2: Create SRAM configuration file**

The next step is to create a new SRAM configuration file. You must use a
very specific naming scheme. An SRAM with `N` words and `M` bits per word
must be named `SRAM_MxN_1P-cfg.py`. Create a configuration file named
`SRAM_64x64_1P-cfg.py` that we can use in the SRAM minion wrapper. The
configuration file should contain the following contents:

    % cd $TOPDIR/sram
    % more SRAM_64x64_1P.cfg
    word_size = 64
    num_words = 64
    num_banks = 1
    tech_name = "freepdk45"
    process_corners = ["TT"]
    supply_voltages = [ 1.1 ]
    temperatures = [ 25 ]
    output_path = "SRAM_64x64_1P_inner"
    output_name = "SRAM_64x64_1P_inner"

**Step 3: Create an SRAM configuration RTL model**

The next step is to create an SRAM configuration RTL model. This new RTL
model should have the same name as the configuration file except a PyMTL
RTL model should use a `.py` filename extension and a Verilog RTL model
should use a `.v` filename extension. We have provided a generic SRAM RTL
model to make it easier to implement the SRAM configuration RTL model.
The generic PyMTL SRAM RTL model is in `SramGenericPRTL.py` and student's
will also have a generic Verilog SRAM RTL model they can use. Go ahead
and create an SRAM configuration RTL model for the 64x64 configuration
that we used in the SRAM minion wrapper.

Here is what this model should look like if you are using PyMTL:

```python
from pymtl3                         import *
from pymtl3.passes.backends.verilog import TranslationConfigs
from .SramGenericPRTL               import SramGenericPRTL

class SRAM_64x64_1P( Component ):

  # Make sure widths match the .v

  def construct( s ):

    # clock (in PyMTL simulation it uses implict .clk port when
    # translated to Verilog, actual clock ports should be CE1

    s.CE1  = InPort ()          # clk
    s.WEB1 = InPort ()          # bar( write en )
    s.OEB1 = InPort ()          # bar( out en )
    s.CSB1 = InPort ()          # bar( whole SRAM en )
    s.A1   = InPort ( Bits6  )  # address
    s.I1   = InPort ( Bits64 )  # write data
    s.O1   = OutPort( Bits64 )  # read data

    # instantiate a generic sram inside

    s.sram_generic = SramGenericPRTL( 64, 64 )(
      CE1  = s.CE1,
      WEB1 = s.WEB1,
      OEB1 = s.OEB1,
      CSB1 = s.CSB1,
      A1   = s.A1,
      I1   = s.I1,
      O1   = s.O1
    )

    s.config_verilog_translate = TranslationConfigs(
      translate    = False,
      no_synthesis = True,
    )
```

Notice how this is simply a wrapper around `SramGenericPRTL` instantiated
with the desired number of words and bits per word.

**Step 4: Use new SRAM configuration RTL model in top-level SRAM model**

The final step is to modify the top-level SRAM model to select the proper
SRAM configuration RTL model. If you are using PyMTL, you will need to
modify `SramPRTL.py` like this:

```python
# Add this at the top of the file
from .SRAM_64x64_1P   import SRAM_64x64_1P

...

    if   data_nbits == 32 and num_entries == 256:
      s.sram = SRAM_32x256_1P()
    elif data_nbits == 128 and num_entries == 256:
      s.sram = SRAM_128x256_1P()

    # Add the following to choose new SRAM configuration RTL model
    elif data_nbits == 64 and num_entries == 64:
      s.sram = SRAM_64x64_1P()

    else:
      s.sram = SramGenericPRTL( num_bits, num_words )
```

One might ask what is the point of going through all of the trouble of
creating an SRAM configuration RTL model that is for a specific size if
we already have a generic SRAM RTL model. The key reason is that the ASIC
tools will use the _name_ of the SRAM to figure out where to swap in the
SRAM macro. So we need a explicit module name for every different SRAM
configuration to enable using SRAM macros in the ASIC tools.

**Step 5: Test new SRAM configuration**

The final step is to test the new configuration and verify everything
works. We start by adding a simple directed test to the `SramRTL_test.py`
test script. Here is an example:

```python
def test_direct_64x64( dump_vcd, test_verilog ):
  dut = SramRTL(64, 64)
  config_model( dut, dump_vcd, test_verilog )
  run_test_vector_sim( dut, [ header_str,
    # val type idx  wdata   rdata

    [ 1,  1,  0x00, 0x00000000, '?'        ], # one at a time
    [ 1,  0,  0x00, 0x00000000, '?'        ],
    [ 0,  0,  0x00, 0x00000000, 0x00000000 ],
    [ 1,  1,  0x00, 0xdeadbeef, '?'        ],
    [ 1,  0,  0x00, 0x00000000, '?'        ],
    [ 0,  0,  0x00, 0x00000000, 0xdeadbeef ],
    [ 1,  1,  0x01, 0xcafecafe, '?'        ],
    [ 1,  0,  0x01, 0x00000000, '?'        ],
    [ 0,  0,  0x00, 0x00000000, 0xcafecafe ],
    [ 1,  1,  0x2f, 0x0a0a0a0a, '?'        ],
    [ 1,  0,  0x2f, 0x00000000, '?'        ],
    [ 0,  0,  0x00, 0x00000000, 0x0a0a0a0a ],

    [ 1,  1,  0x2e, 0x0b0b0b0b, '?'        ], # streaming reads
    [ 1,  0,  0x2e, 0x00000000, '?'        ],
    [ 1,  0,  0x2f, 0x00000000, 0x0b0b0b0b ],
    [ 1,  0,  0x01, 0x00000000, 0x0a0a0a0a ],
    [ 1,  0,  0x00, 0x00000000, 0xcafecafe ],
    [ 0,  0,  0x00, 0x00000000, 0xdeadbeef ],

    [ 1,  1,  0x2d, 0x0c0c0c0c, '?'        ], # streaming writes/reads
    [ 1,  0,  0x2d, 0x00000000, '?'        ],
    [ 1,  1,  0x2c, 0x0d0d0d0d, 0x0c0c0c0c ],
    [ 1,  0,  0x2c, 0x00000000, '?'        ],
    [ 1,  1,  0x2b, 0x0e0e0e0e, 0x0d0d0d0d ],
    [ 1,  0,  0x2b, 0x00000000, '?'        ],
    [ 0,  0,  0x00, 0x00000000, 0x0e0e0e0e ],
  ] )
```

This directed test writes a value to a specific word and then reads that
word to verify the value was written correctly. We test writing the first
word, the last word, and then some streaming reads and writes. We can run
the directed test like this:

    % cd $TOPDIR/sim/build
    % py.test ../sram/test/SramRTL_test.py -k test_direct_64x64

We have included a helper function that simplifies random testing. All
you need to do is add the configuration to the `sram_configs` variable in
the test script:

```
 sram_configs = [ (16, 32), (32, 256), (128, 256), (64,64) ]
```

Then you can run the random test like this:

    % cd $TOPDIR/sim/build
    % py.test ../sram/test/SramRTL_test.py -k test_random[64-64]

And of course we should run all of the tests to ensure we haven't broken
anything when adding this new configuration.

    % cd $TOPDIR/sim/build
    % py.test ../sram

Manual ASIC Flow with SRAM Macros
--------------------------------------------------------------------------

Now that we have added the desired SRAM configuration, we can use the
ASIC tools to generate layout for the SRAM minion wrapper. In this
section, we will go through the steps manually, but we will also provide
you a way to do these steps automatically.

The first step is to run a simulator to generate the Verilog for pushing
through the flow.

    % cd $TOPDIR/sim/build
    % ../tut8_sram/sram-sim --impl rtl --input random --translate --dump-vcd
    % ls
    ...
    SramMinionRTL.v

The next step is to run the OpenRAM memory generator to generate the SRAM
macro corresponding to the desired 64x64 configuration.

    % cd $TOPDIR/asic-manual/openram-mc
    % openram -v ../../sim/sram/SRAM_64x64_1P-cfg.py
    % cd SRAM_64x64_1P_inner
    % mv *.gds *.lib *.lef ..

We need to convert the `.lib` file into a `.db` file using the Synopsys
Library Compiler (LC) tool.

    % cd $TOPDIR/asic-manual/openram-mc
    % cp SRAM_64x64_1P_inner_TT_1p1V_25C.lib SRAM_64x64_1P_inner.lib
    % lc_shell
    lc_shell> read_lib SRAM_64x64_1P_inner.lib
    lc_shell> write_lib SRAM_64x64_1P_inner_TT_1p1V_25C_lib \
      -format db -output SRAM_64x64_1P_inner.db
    lc_shell> exit

Check that the `.db` file now exists.

    % cd $TOPDIR/asic-manual/openram-mc
    % ls
    ...
    SRAM_64x64_1P_inner.db

Now we can use Synopsys DC to synthesize the logic which goes around the
SRAM macro. There is one wrinkle. OpenRAM generates SRAMs with a
bi-directional data bus, but our SRAM RTL modeling assumes we are using
two uni-directional data buses (an input bus for read data and an output
bus for write data). We need to use a wrapper which uses tri-state
buffers to convert the bi-directional data bus to a uni-directional bus.
We have provided this wrapper for you, so all you need to do is
concatentate it with the Verilog RTL we want to push through the flow.

    % mkdir -p $TOPDIR/asic-manual/synopsys-dc
    % cd $TOPDIR/asic-manual/synopsys-dc
    % cat ../../sram_wrapper.v ../../sim/build/SramMinionRTL.v > SramMinionRTL_concat.v

Now we are ready to synthesize this concatenated Verilog RTL.

    % cd $TOPDIR/asic-manual/synopsys-dc
    % dc_shell-xg-t

    dc_shell> set_app_var target_library "$env(ECE5745_STDCELLS)/stdcells.db ../openram-mc/SRAM_64x64_1P_inner.db"
    dc_shell> set_app_var link_library   "* $env(ECE5745_STDCELLS)/stdcells.db ../openram-mc/SRAM_64x64_1P_inner.db"
    dc_shell> analyze -format sverilog SramMinionRTL_concat.v
    dc_shell> elaborate SramMinionRTL
    dc_shell> check_design
    dc_shell> create_clock clk -name ideal_clock1 -period 1.5
    dc_shell> compile
    dc_shell> write -format verilog -hierarchy -output post-synth.v
    dc_shell> exit

We are basically using the same steps we used in the Synopsys/Cadence
ASIC tool tutorial. Notice how we must point Synopsys DC to the `.db`
file generated by the OpenRAM memory generator so Synopsys DC knows the
abstract logical, timing, power view of the SRAM.

If you look for the SRAM module in the synthesized gate-level netlist,
you will see that it is referenced but not declared. This is what we
expect since we are not synthesizing the memory but instead using an SRAM
macro.

    % cd $TOPDIR/asic-manual/synopsys-dc
    % less -p SRAM post-synth.v

Now we can use Cadence Innovus to place the SRAM macro and the standard
cells, and then automatically route everything together. We will be
running Cadence Innovus in a separate directory to keep the files
separate from the other tools.

    % mkdir -p $TOPDIR/asic-manual/cadence-innovus
    % cd $TOPDIR/asic-manual/cadence-innovus

As in the Synopsys/Cadence ASIC tool tutorial, we need to create two
files before starting Cadence Innovus. Use Geany or your favorite text
editor to create a file named `constraints.sdc`in
`$TOPDIR/asic-manual/cadence-innovus` with the following content:

```
 create_clock clk -name ideal_clock -period 1.5
```

Now use Geany or your favorite text editor to create a file named
`setup-timing.tcl` in `$TOPDIR/asic-manual/cadence-innovus` with the
following content:

```
 create_rc_corner -name typical \
    -cap_table "$env(ECE5745_STDCELLS)/rtk-typical.captable" \
    -T 25

 create_library_set -name libs_typical \
    -timing [list "$env(ECE5745_STDCELLS)/stdcells.lib" "../openram-mc/SRAM_64x64_1P_inner.lib"]

 create_delay_corner -name delay_default \
    -early_library_set libs_typical \
    -late_library_set libs_typical \
    -rc_corner typical

 create_constraint_mode -name constraints_default \
    -sdc_files [list constraints.sdc]

 create_analysis_view -name analysis_default \
    -constraint_mode constraints_default \
    -delay_corner delay_default

 set_analysis_view \
    -setup [list analysis_default] \
    -hold [list analysis_default]
```

This is very similar to the steps we used in the Synopsys/Cadence ASIC
tool tutorial, except that we have to include the `.lib` file generated
by the OpenRAM memory generator. Now let's start Cadence Innovus, load in
the design, and complete the power routing just as in the
Synopsys/Cadence ASIC tool tutorial.

    % cd $TOPDIR/asic-manual/cadence-innovus
    % innovus -64
    innovus> set init_mmmc_file "setup-timing.tcl"
    innovus> set init_verilog   "../synopsys-dc/post-synth.v"
    innovus> set init_top_cell  "SramMinionRTL"
    innovus> set init_lef_file  "$env(ECE5745_STDCELLS)/rtk-tech.lef \
                                 $env(ECE5745_STDCELLS)/stdcells.lef \
                                 ../openram-mc/SRAM_64x64_1P_inner.lef"
    innovus> set init_gnd_net   "VSS"
    innovus> set init_pwr_net   "VDD"
    innovus> init_design
    innovus> floorPlan -r 1.0 0.70 4.0 4.0 4.0 4.0
    innovus> globalNetConnect VDD -type pgpin -pin VDD -inst * -verbose
    innovus> globalNetConnect VSS -type pgpin -pin VSS -inst * -verbose
    innovus> sroute -nets {VDD VSS}

    innovus> addRing -nets {VDD VSS} -width 0.6 -spacing 0.5 \
              -layer [list top 7 bottom 7 left 6 right 6]

    innovus> addStripe -nets {VSS VDD} -layer 6 -direction vertical \
              -width 0.4 -spacing 0.5 -set_to_set_distance 5 -start 0.5

    innovus> addStripe -nets {VSS VDD} -layer 7 -direction horizontal \
              -width 0.4 -spacing 0.5 -set_to_set_distance 5 -start 0.5

We can now do a simple placement and routing of the standard cells _and_
the SRAM macro in the floorplan, and then we can finalize the clock and
signal routing and add filler cells.

    innovus> placeDesign
    innovus> ccopt_design
    innovus> routeDesign
    innovus> setFillerMode -corePrefix FILL -core "FILLCELL_X4 FILLCELL_X2 FILLCELL_X1"
    innovus> addFiller

Try looking at a timing report to learn more about the dealy through the
SRAM.

    innovus> report_timing

Let's finish up by generating the real layout as a `.gds` file.

    innovus> streamOut post-par.gds \
              -merge "$env(ECE5745_STDCELLS)/stdcells.gds \
                      ../openram-mc/SRAM_64x64_1P_inner.gds" \
              -mapFile "$env(ECE5745_STDCELLS)/rtk-stream-out.map"

Then we can use Klayout to take a look.

    % cd $TOPDIR/asic-manual/cadence-innovus
    % klayout -l $ECE5745_STDCELLS/klayout.lyp post-par.gds

