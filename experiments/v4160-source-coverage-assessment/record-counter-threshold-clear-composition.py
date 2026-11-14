#!/usr/bin/env python3
"""Compose post-callback decision, queue-clear and tail on shared memory."""
import argparse,importlib.util
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];MASK=0xffffffff
def load(name,file):
 s=importlib.util.spec_from_file_location(name,HERE/file);x=importlib.util.module_from_spec(s);s.loader.exec_module(x);return x
machine=load('machine','record-counter-107d8-machine.py');queue=load('queue','queue-clear-820c-decoder.py');tail=load('tail','record-counter-clear-tail.py');m=machine.m

def main():
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=ROOT);image=(p.parse_args().root/m.BIN).read_bytes();m.validate(image);queue.validate(image);tail.validate_tail(image)
 code={}
 for pc,h in m.WINDOWS:code.update({pc+i:b for i,b in enumerate(bytes.fromhex(h))})
 m.need(image[0x8814:0x8816]==bytes.fromhex('e9bf'),'return jump');code.update({0x10814:0xe9,0x10815:0xbf});qcode={0x820c+i:b for i,b in enumerate(queue.PROVIDER)}
 cases=0;changed=0;gp=0x20004000;addr=gp+193;counter=0x20005000
 for off in (20,24,28):
  for byte in range(4):
   sp=addr-off-byte
   for saved in range(256):
    for old in range(2,255):
     mem={counter:old}
     for wordoff in (12,20,24,28):
      value=3 if wordoff==12 else 0x55555555
      for i in range(4):mem[sp+wordoff+i]=(value>>(i*8))&255
     mem[addr]=saved
     pc,ev=machine.execute(code,1,old,3,sp=sp,counter=counter,memory=mem)
     m.need(pc==0x107fc and ev[-1]==('store8',counter,0),'threshold branch');before=tail.after_provider(sp,1,mem)
     ret,writes=queue.execute(qcode,0,gp);m.need(ret==0 and writes==[('store8',addr,0)],'provider write')
     mem[addr]=writes[0][2];after=tail.after_provider(sp,1,mem);field={20:'s1',24:'s0',28:'ra'}[off]
     m.need(after[field]==(before[field]&~(255<<(8*byte))),'saved word')
     m.need(after['a0']==1 and after['target']==0x1074c and mem[counter]==0,'tail result')
     changed+=before[field]!=after[field];cases+=1
 print(f'PASS: {cases} decision/provider/tail shared-memory cases; {changed} changed restored word')
 print('LIMIT: fixed projections and restricted decoders, callback already returned, threshold 3, provider normal return and preserved gp/sp/s1; synthetic alias, no hardware or reachability proof')
if __name__=='__main__':main()
