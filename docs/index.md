
ECE 5745 Section 5: SRAM Generators
==========================================================================

 - Author: Christopher Batten, Jack Brzozowski
 - Date: March 3, 2021

**Table of Contents**

 - Introduction
 - OpenRAM Memory Generator
 - Using SRAMs in RTL Models
 - Manual ASIC Flow with SRAM Macros

Introduction
--------------------------------------------------------------------------

In this section, we will be learning about SRAM generators. Small
memories can be easily synthesized using flip-flop or latch standard
cells, but synthesizing large memories can significantly impact the area,
energy, and timing of the overall design. ASIC designers often use SRAM
generators to "generate" arrays of memory bitcells and the corresponding
peripheral circuitry (e.g., address decoders, bitline drivers, sense
amps) which are combined into what is called an "SRAM macro". These SRAM
generators are parameterized to enable generating a wide range of SRAM
macros with different numbers of rows, columns, and column muxes, as well
as optional support for partial writes, built-in self-test, and error
correction. Similar to a standard-cell library, an SRAM generator must
generate not just layout but also all of the necessary views to capture
logical functionality, timing, geometry, and power usage. These views can
then by used by the ASIC tools to produce a complete design which
includes a mix of both standard cells and SRAM macros. We will first see
how to use the open-source OpenRAM memory generator to generate various
views of an SRAM macro. Then we will see how to use SRAMs in our RTL
designs. Finally, we will put the these two pieces together to combine
synthesizable RTL with SRAM macros and push the composition through the
ASIC toolflow.

The first step is to access `ecelinux`. You can use VS Code for working
at the command line, but you will also need to a remote access option
that supports Linux applications with a GUI such as X2Go, MobaXterm, or
Mac Terminal with XQuartz. Once you are at the `ecelinux` prompt, source
the setup script, clone this repository from GitHub, and define an
environment variable to keep track of the top directory for the project.

**NOTE: You need to use the `--2022` command line option with the setup
script since the code in this repo has not been updated to work with the
2023 environment.**

    % source setup-ece5745.sh --2022
    % mkdir -p $HOME/ece5745
    % cd $HOME/ece5745
    % git clone git@github.com:cornell-ece5745/ece5745-S05-srams sec5
    % cd sec5
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
should name your file `SRAM_32x128_1rw-cfg.py` and it should be located in
the directory shown below.

    % mkdir -p $TOPDIR/asic/openram-mc
    % cd $TOPDIR/asic/openram-mc
    % cat SRAM_32x128_1rw-cfg.py
    num_rw_ports    = 1
    num_r_ports     = 0
    num_w_ports     = 0

    word_size       = 32
    num_words       = 128
    num_banks       = 1
    words_per_row   = 4

    tech_name       = "freepdk45"
    process_corners = ["TT"]
    supply_voltages = [1.1]
    temperatures    = [25]

    route_supplies  = True
    check_lvsdrc    = False

    output_path     = "SRAM_32x128_1rw"
    output_name     = "SRAM_32x128_1rw"
    instance_name   = "SRAM_32x128_1rw"

In this example, we are generating a single-ported SRAM which has 32 rows
and 128 bits per row for a total capacity of 4096 bits or 512B. This size
is probably near the cross-over point where you might transition from
using synthesized memories to SRAM macros. OpenRAM will take this
configuration file as input and generate many different views of the SRAM
macro including: schematics (`.sp`), layout (`.gds`), a Verilog
behavioral model (`.v`), abstract logical, timing, power view (`.lib`),
and a physical view (`.lef`). These views can then be used by the ASIC
tools.

You can use the following command to run the OpenRAM memory generator.

    % cd $TOPDIR/asic/openram-mc
    % openram -v SRAM_32x128_1rw-cfg.py

It will take about 6-7 minutes to generate the SRAM macro. You can see
the resulting views here:

    % cd $TOPDIR/asic/openram-mc/SRAM_32x128_1rw
    % ls -1
    SRAM_32x128_1rw.gds
    SRAM_32x128_1rw.lef
    SRAM_32x128_1rw.sp
    SRAM_32x128_1rw_TT_1p1V_25C.lib
    SRAM_32x128_1rw.v

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

    % cd $TOPDIR/asic/openram-mc/SRAM_32x128_1rw
    % less SRAM_32x128_1rw.v

You can take a look at the generated transistor-level netlist like this:

    % cd $TOPDIR/asic/openram-mc/SRAM_32x128_1rw
    % less -p " cell_1rw " SRAM_32x128_1rw.sp

Now let's use Klayout look at the actual layout produced by the OpenRAM
memory generator.

    % cd $TOPDIR/asic/openram-mc/SRAM_32x128_1rw
    % klayout -l $ECE5745_STDCELLS/klayout.lyp SRAM_32x128_1rw.gds

In Klayout, you can show/hide layers by double clicking on them on the
right panel. You can show more of the hierarchy by selecting _Display >
Increment Hierarchy_ from the menu.

Take a quick look at the `.lib` file and the `.lef` file for the SRAM
macro.

    % cd $TOPDIR/asic/openram-mc/SRAM_32x128_1rw
    % less SRAM_32x128_1rw_TT_1p1V_25C.lib
    % less SRAM_32x128_1rw.lef

Using SRAMs in RTL Models
--------------------------------------------------------------------------

Now that we understand how an SRAM generator works, let's see how to
actually use an SRAM in your RTL models. We have create a behavioral SRAM
model in the `sim/sram` subdirectory.

    % cd $TOPDIR/sim/sram
    % ls
    ...
    SramGeneric.v
    Sram.v

The SRAM model is parameterized by the number of words and the bits per
word, and has the following pin-level interface:

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
Verilog version (we will provide you a similar PyMTL version for you to
use):

    % cd $TOPDIR/sim/tut8_sram
    % more SramMinion.v
    `include "sram/Sram.v"
    ...
    sram_Sram#(32,128) sram
    (
      .clk         (clk),
      .reset       (reset),
      .port0_idx   (sram_addr_M0),
      .port0_type  (sram_wen_M0),
      .port0_val   (sram_en_M0),
      .port0_wdata (memreq_msg_data_M0),
      .port0_rdata (sram_read_data_M1)
    );

To use an SRAM in a Verilog model, simply include `sram/Sram.v`,
instantiate the SRAM, and set the number of words and number of bits per
word. We can run a test on the SRAM minion wrapper like this:

```
 % mkdir -p $TOPDIR/sim/build
 % cd $TOPDIR/sim/build
 % pytest ../tut8_sram/test/SramMinion_test.py -k random_0_3 -s
  1r                           > (  (). ) > .
  2r                           > (  (). ) > .
  3:                           > (  (). ) > .
  4: wr:00:00000000:0:55fceed9 > (wr(). ) > .
  5: wr:01:00000004:0:5bec8a7b > (wr()# ) > #
  6: #                         > (# ()# ) > #
  7: #                         > (# ()wr) > wr:00:0:0:
  8: #                         > (# ()# ) > #
  9: #                         > (# ()# ) > #
 10: #                         > (# ()# ) > #
 11: #                         > (# ()wr) > wr:01:0:0:
 12: wr:02:00000008:0:b1aa20f1 > (wr(). ) > .
 13: wr:03:0000000c:0:a5b6b6bb > (wr()# ) > #
 14: #                         > (# ()# ) > #
 15: #                         > (# ()wr) > wr:02:0:0:
```

The first write transaction takes a single cycle to go through the SRAM
minion wrapper, but then the response interface is not ready on cycles
5-6. The second write transaction is still accepted by the SRAM minion
wrapper and they will end up in the bypass queue, but the later
transactions are stalled because the request interface is not ready. No
transactions are lost.

The SRAM module is parameterized to enable initial design space
exploration, but just because we choose a specific SRAM configuration
does not mean the files we need to create the corresponding SRAM macro
exist yet. Once we have finalized the SRAM size, we need to go through a
five step process.

**Step 1: See if SRAM configuration already exists**

The first step is to see if your desired SRAM configuration already
exists. You can do this by looking at the names of the `-cfg.py` files in
the `sim/sram` subdirectory.

    % cd $TOPDIR/sim/sram
    % ls *-cfg.py
    SRAM_128x256_1rw-cfg.py
    SRAM_32x256_1rw-cfg.py

This means there are two SRAM configurations already available. One SRAM
has 256 words each with 128 bits and the other SRAM has 256 words each
with 32 bits. If the SRAM configuration you need already exists then you
are done and can skip the remaining steps.

**Step 2: Create SRAM configuration file**

The next step is to create a new SRAM configuration file. You must use a
very specific naming scheme. An SRAM with `N` words and `M` bits per word
must be named `SRAM_MxN_1rw-cfg.py` (i.e., `SRAM_32x128_1rw-cfg.py`). We
already created this configuration file earlier in the section so we can
just move it here.

    % cd $TOPDIR/sim/sram
    % mv $TOPDIR/asic/openram-mc/SRAM_32x128_1rw-cfg.py .
    % cat SRAM_32x128_1rw-cfg.py

**Step 3: Create an SRAM configuration RTL model**

The next step is to create an SRAM configuration RTL model. This new RTL
model should have the same name as the configuration file without `-cfg`
and it should use a `.v` filename extension. We have provided a generic
SRAM RTL model to make it easier to implement the SRAM configuration RTL
model. The generic Verilog SRAM RTL model is in `SramGeneric.v`. Go ahead
and create an SRAM configuration RTL model for the 32x128 configuration
that we used in the SRAM val/rdy wrapper. The file should be named
`SRAM_32x128_1rw.v`.

Here is what this model should look like if you are using Verilog:

```verilog
`ifndef SRAM_32x128_1rw
`define SRAM_32x128_1rw

`include "sram/SramGeneric.v"

`ifndef SYNTHESIS

module SRAM_32x128_1rw
(
  input  logic        clk0,
  input  logic        web0,
  input  logic        csb0,
  input  logic [7:0]  addr0,
  input  logic [31:0] din0,
  output logic [31:0] dout0
);

  sram_SramGeneric
  #(
    .p_data_nbits  (32),
    .p_num_entries (128)
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

`endif /* SRAM_32x128_1rw */
```

Notice how this is simply a wrapper around `SramGeneric` instantiated
with the desired number of words and bits per word.

**Step 4: Use new SRAM configuration RTL model in top-level SRAM model**

The final step is to modify the top-level SRAM model to select the proper
SRAM configuration RTL model. You need to modify `Sram.v` like this:

```verilog
// Add this at the top of the file
`include "sram/SRAM_32x128_1rw.v"
...
  generate
    if      ( p_data_nbits == 32  && p_num_entries == 256 ) SRAM_32x256_1rw  sram (.*);
    else if ( p_data_nbits == 64  && p_num_entries == 64  ) SRAM_64x64_1rw   sram (.*);
    else if ( p_data_nbits == 128 && p_num_entries == 256 ) SRAM_128x256_1rw sram (.*);
    else if ( p_data_nbits == 32  && p_num_entries == 128 ) SRAM_32x128_1rw  sram (.*);
    else
      sram_SramGeneric#(p_data_nbits,p_num_entries) sram (.*);
  endgenerate
```

One might ask what is the point of going through all of the trouble of
creating an SRAM configuration RTL model that is for a specific size if
we already have a generic SRAM RTL model. The key reason is that the ASIC
tools will use the _name_ of the SRAM to figure out where to swap in the
SRAM macro. So we need a explicit module name for every different SRAM
configuration to enable using SRAM macros in the ASIC tools.

**Step 5: Test new SRAM configuration**

The final step is to test the new configuration and verify everything
works. We have a simple directed test in `Sram_test.py` ready for you
to use.

```python
def test_direct_32x128( cmdline_opts ):
  run_test_vector_sim( Sram(32, 128), [ header_str,
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
    [ 1,  1,  0x1f, 0x0a0a0a0a, '?'        ],
    [ 1,  0,  0x1f, 0x00000000, '?'        ],
    [ 0,  0,  0x00, 0x00000000, 0x0a0a0a0a ],

    [ 1,  1,  0x1e, 0x0b0b0b0b, '?'        ], # streaming reads
    [ 1,  0,  0x1e, 0x00000000, '?'        ],
    [ 1,  0,  0x1f, 0x00000000, 0x0b0b0b0b ],
    [ 1,  0,  0x01, 0x00000000, 0x0a0a0a0a ],
    [ 1,  0,  0x00, 0x00000000, 0xcafecafe ],
    [ 0,  0,  0x00, 0x00000000, 0xdeadbeef ],

    [ 1,  1,  0x1d, 0x0c0c0c0c, '?'        ], # streaming writes/reads
    [ 1,  0,  0x1d, 0x00000000, '?'        ],
    [ 1,  1,  0x1c, 0x0d0d0d0d, 0x0c0c0c0c ],
    [ 1,  0,  0x1c, 0x00000000, '?'        ],
    [ 1,  1,  0x1b, 0x0e0e0e0e, 0x0d0d0d0d ],
    [ 1,  0,  0x1b, 0x00000000, '?'        ],
    [ 0,  0,  0x00, 0x00000000, 0x0e0e0e0e ],
  ], cmdline_opts )
```

This directed test writes a value to a specific word and then reads that
word to verify the value was written correctly. We test writing the first
word, the last word, and then some streaming reads and writes. We can run
the directed test like this:

    % cd $TOPDIR/sim/build
    % pytest ../sram/test/Sram_test.py -k test_direct_32x128

We have included a helper function that simplifies random testing. You
can run the random test like this:

    % cd $TOPDIR/sim/build
    % pytest ../sram/test/Sram_test.py -k test_random[32-128] -s

And of course we should run all of the tests to ensure we haven't broken
anything when adding this new configuration.

    % cd $TOPDIR/sim/build
    % pytest ../sram

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
    SramMinion__pickled.v

The next step is to run the OpenRAM memory generator to generate the SRAM
macro corresponding to the desired 32x128 configuration, but we already
did this earlier in the discussion section. We want to move the key
generated files to make them easier to use by the ASIC tools.

    % cd $TOPDIR/asic/openram-mc/SRAM_32x128_1rw
    % mv *.gds *.lib *.lef ..

We need to convert the `.lib` file into a `.db` file using the Synopsys
Library Compiler (LC) tool.

    % cd $TOPDIR/asic/openram-mc
    % cp SRAM_32x128_1rw_TT_1p1V_25C.lib SRAM_32x128_1rw.lib
    % lc_shell
    lc_shell> read_lib SRAM_32x128_1rw.lib
    lc_shell> write_lib SRAM_32x128_1rw_TT_1p1V_25C_lib \
      -format db -output SRAM_32x128_1rw.db
    lc_shell> exit

Check that the `.db` file now exists.

    % cd $TOPDIR/asic/openram-mc
    % ls
    ...
    SRAM_32x128_1rw.db

Now we can use Synopsys DC to synthesize the logic which goes around the
SRAM macro.

    % mkdir -p $TOPDIR/asic/synopsys-dc
    % cd $TOPDIR/asic/synopsys-dc
    % dc_shell-xg-t

    dc_shell> set_app_var target_library "$env(ECE5745_STDCELLS)/stdcells.db ../openram-mc/SRAM_32x128_1rw.db"
    dc_shell> set_app_var link_library   "* $env(ECE5745_STDCELLS)/stdcells.db ../openram-mc/SRAM_32x128_1rw.db"
    dc_shell> analyze -format sverilog ../../sim/build/SramMinion__pickled.v
    dc_shell> elaborate SramMinion
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

    % cd $TOPDIR/asic/synopsys-dc
    % less -p SRAM post-synth.v

Now we can use Cadence Innovus to place the SRAM macro and the standard
cells, and then automatically route everything together. We will be
running Cadence Innovus in a separate directory to keep the files
separate from the other tools.

    % mkdir -p $TOPDIR/asic/cadence-innovus
    % cd $TOPDIR/asic/cadence-innovus

As in the Synopsys/Cadence ASIC tool tutorial, we need to create two
files before starting Cadence Innovus. Use Geany or your favorite text
editor to create a file named `constraints.sdc`in
`$TOPDIR/asic/cadence-innovus` with the following content:

```
 create_clock clk -name ideal_clock -period 1.0
```

Now use Geany or your favorite text editor to create a file named
`setup-timing.tcl` in `$TOPDIR/asic/cadence-innovus` with the
following content:

```
 create_rc_corner -name typical \
    -cap_table "$env(ECE5745_STDCELLS)/rtk-typical.captable" \
    -T 25

 create_library_set -name libs_typical \
    -timing [list "$env(ECE5745_STDCELLS)/stdcells.lib" "../openram-mc/SRAM_32x128_1rw.lib"]

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

    % cd $TOPDIR/asic/cadence-innovus
    % innovus -64
    innovus> set init_mmmc_file "setup-timing.tcl"
    innovus> set init_verilog   "../synopsys-dc/post-synth.v"
    innovus> set init_top_cell  "SramMinion"
    innovus> set init_lef_file  "$env(ECE5745_STDCELLS)/rtk-tech.lef \
                                 $env(ECE5745_STDCELLS)/stdcells.lef \
                                 ../openram-mc/SRAM_32x128_1rw.lef"
    innovus> set init_gnd_net   "VSS"
    innovus> set init_pwr_net   "VDD"
    innovus> init_design
    innovus> floorPlan -r 0.60 0.65 4.0 4.0 4.0 4.0
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

    innovus> place_design
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
                      ../openram-mc/SRAM_32x128_1rw.gds" \
              -mapFile "$env(ECE5745_STDCELLS)/rtk-stream-out.map"
    innovus> exit

Then we can use Klayout to take a look.

    % cd $TOPDIR/asic/cadence-innovus
    % klayout -l $ECE5745_STDCELLS/klayout.lyp post-par.gds
