#!/usr/bin/env python3
"""Original-byte TX loop against sequential shared-memory reference over offsets."""
import argparse,hashlib,importlib.util
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def load(name,path):
 s=importlib.util.spec_from_file_location(name,HERE/path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
h=load('header','tx-header-projection.py');machine=load('machine','tx-copy-machine.py')
def main():
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=ROOT);img=(p.parse_args().root/h.entry.BIN).read_bytes();h.entry.need(len(img)==76800 and hashlib.sha256(img).hexdigest()==h.entry.SHA,'identity');h.decode(img[0xace:0xb0a]);code={}
 for addr,hexbytes in machine.m.WINDOWS:
  b=bytes.fromhex(hexbytes);h.entry.need(img[addr-0x8000:addr-0x8000+len(b)]==b,'copy bytes');code.update({addr+i:v for i,v in enumerate(b)})
 cases=0;propagations=0
 for bank in range(2):
  for delta in range(-8,9):
   for command in range(256):
    base,writes,seed=h.project(bank,8,command);src=base+5+delta
    original={base+i:(i*37+command)&255 for i in range(-16,40)}
    for address,width,value in writes:
     for j in range(width):original[address+j]=(value>>(8*j))&255
    actual=original.copy();reference=original.copy();r=[0]*32;r[8]=8;r[9]=src;r[14]=seed;r[15]=base;read_values=[]
    for i in range(8):
     value=reference[src+i];reference[base+5+i]=value;read_values.append(value)
     pc,r,events=machine.execute(code,r,actual);h.entry.need(pc==0x8b0a and events==[('read',src+i,value),('write',base+5+i,value)],'copy events')
    pc,r,events=machine.execute(code,r,actual);h.entry.need(pc==0x8b14 and not events and actual==reference and r[14]==((seed+sum(read_values))&255),'final')
    if delta==-1 and len(set(read_values))==1:propagations+=1
    cases+=1
 h.entry.need(propagations==512,'forward propagation witness')
 print(f'PASS: {cases} original-byte copy traces; {propagations} forward-propagation witnesses')
 print('LIMIT: projected header, synthetic shared memory, successful accesses, no interrupts or hardware; no reachability claim')
if __name__=='__main__':main()
