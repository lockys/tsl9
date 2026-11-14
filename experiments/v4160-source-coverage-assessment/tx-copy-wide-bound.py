#!/usr/bin/env python3
"""Universal gate bound when then-live u32 length exceeds 65535."""
import argparse,hashlib,importlib.util
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
s=importlib.util.spec_from_file_location('machine',HERE/'tx-copy-machine.py');machine=importlib.util.module_from_spec(s);s.loader.exec_module(machine);m=machine.m

def main():
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=ROOT);root=p.parse_args().root
    raw=(root/m.BIN).read_bytes();m.need(len(raw)==76800 and hashlib.sha256(raw).hexdigest()==m.SHA,'identity');code={}
    for addr,h in m.WINDOWS:
        b=bytes.fromhex(h);m.need(raw[addr-0x8000:addr-0x8000+len(b)]==b,'instruction bytes');code.update({addr+i:v for i,v in enumerate(b)})
    # For every u32 index its low halfword is <=65535. Any larger u32
    # length therefore selects the copy edge. Addition wraps modulo 2^32.
    for low in range(65536):
        for length in (65536,0x10001,0x7fffffff,0xffffffff):
            m.need(low<length,'gate bound')
            idx=0xffff0000|low;r=[0]*32;r[8]=length;r[9]=0x1234;r[11]=idx;r[14]=255;r[15]=0x2000
            addr=(r[9]+idx)&m.MASK;pc,out,events=machine.execute(code,r,{addr:17})
            m.need(pc==0x8b0a and out[11]==(idx+1)&m.MASK and len(events)==2,'decoded wide gate')
    print('PASS: 262144 decoded cases, all 65536 low indices and four wide lengths; modulo index wrap')
    print('LIMIT: mathematical gate property plus finite synthetic cases; requires unchanged live s0, successful accesses and no asynchronous events; no claim of real reachability or infinite execution')
if __name__=='__main__':main()
