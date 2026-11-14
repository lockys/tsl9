#!/usr/bin/env python3
"""TX tail call boundary; synthetic byte memory and successful loads assumed."""
import argparse,hashlib,importlib.util
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];M=0xffffffff
s=importlib.util.spec_from_file_location('entry',HERE/'tx-entry-length-guard.py');entry=importlib.util.module_from_spec(s);s.loader.exec_module(entry)
RAW=bytes.fromhex('938741093e966244b707040003a307050345060005610283')
def verify(b):entry.need(b==RAW,'tail window')
def rd(mem,addr,width):return sum(mem.get((addr+i)&M,0)<<(i*8) for i in range(width))
def project(mem,gp,shifted_a2,sp,ra):
    # 0x8b40 restores s0 first; pointer and selector are then read in this order.
    restored_s0=rd(mem,(sp+24)&M,4);target=rd(mem,0x40050,4);selector_addr=(gp+148+shifted_a2)&M;selector=rd(mem,selector_addr,1)
    return (target&~1,selector,1,(sp+32)&M,ra,restored_s0,selector_addr)
def main():
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=ROOT);image=(p.parse_args().root/entry.BIN).read_bytes()
    entry.need(len(image)==76800 and hashlib.sha256(image).hexdigest()==entry.SHA,'identity');raw=image[0xb3a:0xb52];verify(raw)
    for i in range(len(raw)):
        v=bytearray(raw);v[i]^=1
        try:verify(v)
        except ValueError:continue
        raise ValueError('mutation accepted')
    for selector in range(256):
        for low in range(256):
            mem={0x40050:low,0x40051:0x12,0x40052:0x34,0x40053:0x56,0x20004094:selector}
            t,a0,a1,sp,ra,s0,addr=project(mem,0x20004000,0,0xfffffffc,0x12345679)
            entry.need((t,a0,a1,sp,ra,s0,addr)==((0x56341200|low)&~1,selector,1,28,0x12345679,0,0x20004094),'projection')
    # Shared memory: the selector itself may be a byte of the loaded target.
    for low in range(256):
        mem={0x40050:low};t,a0,*_=project(mem,0x40050-148,0,0,3)
        entry.need(a0==low and t==(low&~1),'target/selector alias')
    print(f'PASS: 65536 tail projections, 256 target/selector alias cases, {len(raw)} mutated bytes rejected')
    print('LIMIT: fixed encoding projection; assumes successful loads and little-endian synthetic memory, no hardware or provider behavior')
if __name__=='__main__':main()
