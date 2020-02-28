#=========================================================================
# FooPRTL_test
#=========================================================================

from __future__ import print_function

import pytest
import random

from pymtl3             import *
from pymtl3.stdlib.test import mk_test_case_table, run_sim, config_model
from pymtl3.stdlib.test import TestSrcCL, TestSinkCL
from pymtl3.stdlib.ifcs import mk_mem_msg, MemMsgType

from tut8_sram.SramMinionRTL import SramMinionRTL

MemReqType, MemRespType = mk_mem_msg( 8, 32, 64 )

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------

class TestHarness( Component ):

  def construct( s, dut ):

    # Instantiate models

    s.src  = TestSrcCL( MemReqType )
    s.sram = dut
    s.sink = TestSinkCL( MemRespType )

    # Connect

    s.src.send  //= s.sram.minion.req
    s.sink.recv //= s.sram.minion.resp

  def done( s ):
    return s.src.done() and s.sink.done()

  def line_trace( s ):
    return f"{s.src.line_trace()} > ({s.sram.line_trace()}) > {s.sink.line_trace()}"

#-------------------------------------------------------------------------
# make messages
#-------------------------------------------------------------------------

def req( type_, opaque, addr, len, data ):
  if   type_ == 'rd': type_ = MemMsgType.READ
  elif type_ == 'wr': type_ = MemMsgType.WRITE

  return MemReqType( type_, opaque, addr, len, data)

def resp( type_, opaque, len, data ):
  if   type_ == 'rd': type_ = MemMsgType.READ
  elif type_ == 'wr': type_ = MemMsgType.WRITE

  return MemRespType( type_, opaque, b2(0), len, data )

#----------------------------------------------------------------------
# Test Case: directed
#----------------------------------------------------------------------

def basic_single_msgs():
  return [
    #    type  opq  addr   len data                        type  opq len data
    req( 'wr', 0x0, 0x0000, 0, 0xdeadbeefcafe0123 ), resp( 'wr', 0x0, 0, 0                  ),
    req( 'rd', 0x1, 0x0000, 0, 0                  ), resp( 'rd', 0x1, 0, 0xdeadbeefcafe0123 ),
  ]

def basic_multiple_msgs():
  return [
    #    type  opq  addr   len data                        type  opq len data
    req( 'wr', 0x0, 0x0000, 0, 0xdeadbeefcafe0123 ), resp( 'wr', 0x0, 0, 0                  ),
    req( 'rd', 0x1, 0x0000, 0, 0                  ), resp( 'rd', 0x1, 0, 0xdeadbeefcafe0123 ),
    req( 'wr', 0x2, 0x0008, 0, 0x0a0b0c0d0e0f0102 ), resp( 'wr', 0x2, 0, 0                  ),
    req( 'rd', 0x3, 0x0008, 0, 0                  ), resp( 'rd', 0x3, 0, 0x0a0b0c0d0e0f0102 ),
    req( 'wr', 0x4, 0x01f8, 0, 0x4213421342134213 ), resp( 'wr', 0x4, 0, 0                  ),
    req( 'rd', 0x5, 0x01f8, 0, 0                  ), resp( 'rd', 0x5, 0, 0x4213421342134213 ),
  ]

#----------------------------------------------------------------------
# Test Case: random
#----------------------------------------------------------------------

def random_msgs():

  base_addr = 0

  rgen = random.Random()
  rgen.seed(0xa4e28cc2)

  vmem = [ rgen.randint(0,0xffffffffffffffff) for _ in range(64) ]
  msgs = []

  # Force this to be 64 because there are 64 entries in the SRAM
  for i in range(64):
    msgs.extend([
      req( 'wr', i, base_addr+8*i, 0, vmem[i] ), resp( 'wr', i, 0, 0 ),
    ])

  for i in range(64):
    idx = rgen.randint(0,63)

    if rgen.randint(0,1):

      correct_data = vmem[idx]
      msgs.extend([
        req( 'rd', i, base_addr+8*idx, 0, 0 ), resp( 'rd', i, 0, correct_data ),
      ])

    else:

      new_data = rgen.randint(0,0xffffffffffffffff)
      vmem[idx] = new_data
      msgs.extend([
        req( 'wr', i, base_addr+8*idx, 0, new_data ), resp( 'wr', i, 0, 0 ),
      ])

  return msgs

#-------------------------------------------------------------------------
# Test Case: all constant values
#-------------------------------------------------------------------------

def allN_msgs( num ):

  base_addr = 0

  rgen = random.Random()
  rgen.seed(0xa4e28cc2)

  msgs = []

  # Force this to be 64 because there are 64 entries in the SRAM
  for i in range(64):
    msgs.extend([
      req( 'wr', i, base_addr+4*i, 0, num ), resp( 'wr', i, 0, 0 ),
    ])

  for i in range(150):
    idx = rgen.randint(0,63)

    if rgen.randint(0,1):
      correct_data = num
      msgs.extend([
        req( 'rd', i, base_addr+4*idx, 0, 0 ), resp( 'rd', i, 0, num ),
      ])
    else:
      msgs.extend([
        req( 'wr', i, base_addr+4*idx, 0, num ), resp( 'wr', i, 0, 0 ),
      ])

  return msgs

#-------------------------------------------------------------------------
# Test table for generic test
#-------------------------------------------------------------------------

test_case_table = mk_test_case_table([
  (                       "msg_func             src sink"),
  [ "basic_single_msgs",   basic_single_msgs,   0,  0    ],
  [ "basic_multiple_msgs", basic_multiple_msgs, 0,  0    ],
  [ "random",              random_msgs,         0,  0    ],
  [ "random_0_3",          random_msgs,         0,  3    ],
  [ "random_3_0",          random_msgs,         3,  0    ],
  [ "random_3_5",          random_msgs,         3,  5    ],
])

#-------------------------------------------------------------------------
# Test table for generic test
#-------------------------------------------------------------------------

@pytest.mark.parametrize( **test_case_table )
def test( test_params, dump_vcd, test_verilog ):

  # instantiate test harness

  top = TestHarness( SramMinionRTL() )

  # configure the src/sink messages

  msgs = test_params.msg_func()

  top.set_param("top.src.construct",
    msgs=msgs[::2],
    initial_delay=test_params.src,
    interval_delay=test_params.src )

  top.set_param("top.sink.construct",
    msgs=msgs[1::2],
    initial_delay=test_params.sink,
    interval_delay=test_params.sink )

  # elaborate, configure, and run the simulation

  top.elaborate()

  config_model( top, dump_vcd, test_verilog, ['sram'] )

  run_sim( top )

