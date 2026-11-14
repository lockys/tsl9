#!/usr/bin/env python3
"""Synchronous synthetic b0fc post-registration -> b0d0 composition.

Invocation is injected after b0fc's second call, not inferred from firmware.
Assumes same gp and successful accesses, no intervening stores, interrupts,
alias or unknown callee modifications. Not a hardware execution.
"""
import argparse,importlib.util
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];MASK=0xffffffff
def load(name,file):
 s=importlib.util.spec_from_file_location(name,HERE/file);x=importlib.util.module_from_spec(s);s.loader.exec_module(x);return x
m=load('m','record-counter-107d8.py');caller=load('caller','callback-provider-b0fc-decoder.py');callback=load('callback','callback-b0d0-decoder.py')
def main():
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=ROOT);image=(p.parse_args().root/m.BIN).read_bytes();m.validate(image);caller.model.validate_local(image);callback.validate_local(image)
 for ret in range(256):
  for flag in range(256):
   gp=0x20004000;base=gp+192
   mem,_=caller.execute(ret,base,0x43c4e);before=[mem[base+i] for i in range(1,4)]
   out,after,events=callback.execute(gp,flag,before)
   m.need(before==[3,3,3] and [after[(base+i)&MASK] for i in range(1,4)]==before,'unexpected counter change')
   m.need(mem[base]==ret and out==((flag^1) if flag&1 else 0),'return')
   m.need(len(events)==(3 if flag&1 else 0) and all(e[0]=='read8' for e in events),'read/write events')
 print('PASS: 65536 post-init/injected-callback cases; [3,3,3] unchanged')
 print('LIMIT: injected invocation and no-interference assumptions; callback may execute during registration or later after other changes')
if __name__=='__main__':main()
