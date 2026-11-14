#!/usr/bin/env python3
"""Synthetic clear-then-callback composition; does not assert reachability.

Starts with three 3 bytes after b0fc initialization. Models only a chosen
0x820c call then an injected 0xb0d0 call, with the same gp and no interference.
"""
import argparse,importlib.util
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];MASK=0xffffffff
def load(name,file):
 s=importlib.util.spec_from_file_location(name,HERE/file);x=importlib.util.module_from_spec(s);s.loader.exec_module(x);return x
m=load('m','record-counter-107d8.py');queue=load('queue','queue-clear-820c-decoder.py');cb=load('cb','callback-b0d0-decoder.py')
def main():
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=ROOT);image=(p.parse_args().root/m.BIN).read_bytes();m.validate(image);queue.validate(image);cb.validate_local(image);code={0x820c+i:b for i,b in enumerate(queue.PROVIDER)};count=0
 for gp in (0x20004000,0xffffff3e,0xffffffff):
  for index in (0,1,2,3,0xffffffff):
   for flag in range(256):
    memory={(gp+193+i)&MASK:3 for i in range(3)};ret,events=queue.execute(code,index,gp)
    for op,addr,value in events:m.need(op=='store8','clear operation');memory[addr]=value
    before=[memory[(gp+193+i)&MASK] for i in range(3)];result,after,cb_events=cb.execute(gp,flag,before)
    expected=[(1 if flag&1 else 0) if i==index and index<=2 else 3 for i in range(3)]
    m.need(ret==index and [after[(gp+193+i)&MASK] for i in range(3)]==expected,'composition mismatch')
    m.need(result==((flag^1) if flag&1 else 0),'callback result')
    m.need(len([e for e in cb_events if e[0]=='write8'])==(1 if flag&1 and index<=2 else 0),'write count');count+=1
 print('PASS:',count,'synthetic clear/index/flag/gp cases')
 print('LIMIT: selected clear and callback order are injected, initial bytes and no interference assumed; not reachability or hardware proof')
if __name__=='__main__':main()
