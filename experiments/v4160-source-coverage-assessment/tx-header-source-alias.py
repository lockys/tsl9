#!/usr/bin/env python3
"""Synthetic shared-memory witness: TX header writes precede payload reads."""
import argparse,hashlib,importlib.util
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];M=0xffffffff
def load(name,path):
 s=importlib.util.spec_from_file_location(name,HERE/path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
h=load('header','tx-header-projection.py')
def put(mem,a,width,value):
 for i in range(width):mem[(a+i)&M]=(value>>(8*i))&255
def run(bank,command,alias):
 base,writes,checksum=h.project(bank,5,command);src=base if alias else (base+128)&M
 mem={(src+i)&M:0xee for i in range(5)}
 for a,w,v in writes:put(mem,a,w,v)
 actual=bytes(mem[(src+i)&M] for i in range(5))
 return actual,(checksum+sum(actual))&255

def main():
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=ROOT);img=(p.parse_args().root/h.entry.BIN).read_bytes()
 h.entry.need(len(img)==76800 and hashlib.sha256(img).hexdigest()==h.entry.SHA,'identity');h.decode(img[0xace:0xb0a])
 # Only header writes and subsequent source-read values are projected here;
 # the copy loop itself is not executed by this script.
 for bank in range(2):
  for command in range(256):
   data,checksum=run(bank,command,True);control,c2=run(bank,command,False)
   expected=bytes((0x55,0x7f,command,0,5));h.entry.need(data==expected and control==bytes([0xee]*5),'shared memory order')
   h.entry.need(checksum==((5+command+sum(expected))&255) and c2==((5+command+5*0xee)&255),'sum')
 print('PASS: 512 header/source alias and 512 disjoint control cases')
 print('LIMIT: projected header and later reads, not continuous CPU/copy execution; synthetic source pointers; no provider or hardware reachability proof')
if __name__=='__main__':main()
