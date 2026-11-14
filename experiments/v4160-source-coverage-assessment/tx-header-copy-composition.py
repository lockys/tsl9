#!/usr/bin/env python3
"""Header projection + original-byte copy loop on shared synthetic memory."""
import argparse,hashlib,importlib.util
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];MASK=0xffffffff
def load(name,path):
 s=importlib.util.spec_from_file_location(name,HERE/path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
h=load('header','tx-header-projection.py');machine=load('machine','tx-copy-machine.py');store=load('store','tx-checksum-store.py')
def put(mem,a,width,val):
 for i in range(width):mem[(a+i)&MASK]=(val>>(8*i))&255
def main():
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=ROOT);img=(p.parse_args().root/h.entry.BIN).read_bytes();h.entry.need(len(img)==76800 and hashlib.sha256(img).hexdigest()==h.entry.SHA,'identity');h.decode(img[0xace:0xb0a]);store.decode(img[0xb14:0xb1a])
 code={}
 for addr,hexbytes in machine.m.WINDOWS:
  b=bytes.fromhex(hexbytes);h.entry.need(img[addr-0x8000:addr-0x8000+len(b)]==b,'copy bytes');code.update({addr+i:v for i,v in enumerate(b)})
 for bank in range(2):
  for command in range(256):
   for alias in (False,True):
    base,writes,seed=h.project(bank,5,command);src=base if alias else base+128
    mem={src+i:0xee for i in range(5)}
    for address,width,value in writes:put(mem,address,width,value)
    expected=bytes((0x55,0x7f,command,0,5)) if alias else bytes([0xee]*5)
    r=[0]*32;r[8]=5;r[9]=src;r[14]=seed;r[15]=base;reads=[]
    for i in range(5):
     pc,r,events=machine.execute(code,r,mem);h.entry.need(pc==0x8b0a and len(events)==2,'iteration');reads.append(events[0][2])
    pc,r,events=machine.execute(code,r,mem);h.entry.need(pc==0x8b14 and not events,'exit')
    address,width,value=store.project(base,5,r[14]);put(mem,address,width,value)
    h.entry.need(bytes(reads)==expected and bytes(mem[base+5+i] for i in range(5))==expected,'payload')
    h.entry.need(value==((seed+sum(expected))&255),'checksum')
 print('PASS: 1024 shared-memory header/decoded-copy/checksum compositions')
 print('LIMIT: header and checksum are fixed-encoding projections; copy uses limited byte interpreter; synthetic aliases, successful accesses, no concurrency or hardware')
if __name__=='__main__':main()
