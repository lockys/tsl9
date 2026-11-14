#!/usr/bin/env python3
"""Conditional stack alias bound for the 0x10bae caller's counter pointer."""
import argparse,importlib.util
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];MASK=0xffffffff
def load(name,file):
 s=importlib.util.spec_from_file_location(name,HERE/file);x=importlib.util.module_from_spec(s);s.loader.exec_module(x);return x
entry=load('entry','record-counter-entry-107c6.py');m=entry.m
WINDOWS=((0x186aa,bytes.fromhex('97c1fe1f938161951781ff1f1301e194')),(0x10bae,bytes.fromhex('97060000938606af05468d45138521146ff09fc0')))
def validate_windows(data):
 for pc,expected in WINDOWS:m.need(data[pc-0x8000:pc-0x8000+len(expected)]==expected,f'window {pc:x}')

def main():
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=ROOT);data=(p.parse_args().root/m.BIN).read_bytes();entry.validate(data)
 def read(pc,n):return data[pc-0x8000:pc-0x8000+n]
 validate_windows(data)
 # Reset AUIPC/ADDI results, conditional on execution and preservation.
 def auadd(pc,b):
  au=int.from_bytes(b[:4],'little');ad=int.from_bytes(b[4:8],'little');imm=ad>>20;imm=imm-4096 if imm&2048 else imm;return (pc+(au&0xfffff000)+imm)&MASK
 gp=auadd(0x186aa,read(0x186aa,8));reset=auadd(0x186b2,read(0x186b2,8));m.need((gp,reset)==(0x20004000,0x20010000),'reset values')
 caller=int.from_bytes(read(0x10bba,4),'little');m.need((caller&0xfffff)==0x18513 and caller>>20==0x142,'caller addi operands')
 counter=(gp+(caller>>20))&MASK
 sps={ (counter+20-i)&MASK for i in range(4)};aligned=sorted(x for x in sps if x%4==0 and x<=reset);m.need(len(aligned)==1,'aligned witness');closest=reset-max(aligned)
 for depth in range(0,closest,4):
  sp=reset-depth;m.need(counter not in {(sp-20+i)&MASK for i in range(4)},'unexpected overlap')
 sp=reset-closest;mem={counter:99};entry.enter(sp,1,2,3,counter,3,1,0x1069e,0,mem)
 m.need(mem[counter]==0,'actual alias store')
 print(f'PASS: counter 0x{counter:08x}; aligned alias entry SP 0x{sp:08x}; reset-SP depth {closest} bytes; all smaller aligned depths excluded')
 print('LIMIT: assumes reset gp/SP remain applicable and depth is nonnegative; no actual stack bound, alignment guarantee, reachability, callback or hardware proof')
if __name__=='__main__':main()
