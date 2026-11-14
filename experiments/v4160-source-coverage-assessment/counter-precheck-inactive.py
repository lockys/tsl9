#!/usr/bin/env python3
"""Sufficient no-call return-zero conditions for APP 0x82d2, not reachability."""
import argparse,hashlib
from itertools import product
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
BIN='firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
SHA='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
def need(v,msg):
    if not v:raise ValueError(msg)
def project(memory):
    trace=[]
    for index in range(2):
        pos=index*4
        h=int.from_bytes(memory[pos+2:pos+4],'little');trace.append((pos+2,2))
        if h==0xfffe:continue
        kind=memory[pos+5];trace.append((pos+5,1))
        if kind!=2:continue
        active=memory[pos+4];trace.append((pos+4,1))
        if active!=0:return None,trace
    return 0,trace
def main():
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=ROOT);image=(p.parse_args().root/BIN).read_bytes()
    need(len(image)==76800 and hashlib.sha256(image).hexdigest()==SHA,'APP identity')
    windows=((0x82ee,'0149014a974a0020938a2a4af919094bA14b'),(0x8308,'13142900569483572400638cf904834754006318fb048347440093f7f70fb1c3'),(0x836a,'63000902f25062545285'),(0x838a,'0549b5bf'))
    for pc,h in windows:
        raw=bytes.fromhex(h);need(image[pc-0x8000:pc-0x8000+len(raw)]==raw,f'instruction mismatch {pc:x}')
    # s5 = 0x82f2 + 0x20004000 + 1186.
    base=(0x82f2+0x20004000+1186)&0xffffffff;need(base==0x2000c794,'table base')
    count=0
    for h0,h1,k0,k1,a0,a1 in product((0,0xfffe,0xffff),(0,0xfffe,0xffff),(0,2,255),(0,2,255),(0,1,255),(0,1,255)):
        m=bytearray(10);m[2:4]=h0.to_bytes(2,'little');m[6:8]=h1.to_bytes(2,'little');m[5]=k0;m[9]=k1;m[4]=a0;m[8]=a1
        result,events=project(m)
        qualify=lambda h,k,a:h!=0xfffe and k==2 and a!=0
        need((result==0)==(not qualify(h0,k0,a0) and not qualify(h1,k1,a1)),'gate')
        if result==0:need(all(off in (2,4,5,6,8,9) for off,_ in events),'reads')
        count+=1
    print(f'PASS: {count} synthetic two-entry states; if neither entry qualifies, 0x82d2 projection returns zero without the copy/callee branch')
    print('LIMIT: fixed-encoding projection, no interrupts or traps, successful stable reads; qualifying path, initial state, hardware and reachability unverified')
if __name__=='__main__':main()
