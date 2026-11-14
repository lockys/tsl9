"""Compose APP high/low length byte and checksum projections via shared bytes.

Assumes stable gp, s1=gp+165, s11=gp+142, successful accesses, no concurrent
changes, and control reaches each fragment in order; not continuous execution.
"""
import hashlib
import importlib.util
from pathlib import Path
HERE=Path(__file__).resolve().parent

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
high=load('high',HERE/'ingress_length_high.py')
init=load('init',HERE/'ingress_length_initialize.py')
route=load('route',HERE/'ingress_length_route.py')
MASK=0xffffffff

def main():
    image=init.gate.entry.IMAGE.read_bytes()
    if len(image)!=76800 or hashlib.sha256(image).hexdigest()!=init.gate.entry.SHA: raise ValueError('APP identity mismatch')
    read=lambda mapping:{pc:image[pc-0x8000:pc-0x8000+len(raw)] for pc,raw in mapping.items()}
    hc=read(high.EXPECTED); common=read(high.third.EXPECTED)
    ic=image[0x89cc-0x8000:0x89da-0x8000]; rc=image[0x89da-0x8000:0x89f6-0x8000]
    if ic!=init.EXPECTED or rc!=route.EXPECTED: raise ValueError('length instructions mismatch')
    gp=0x20004000; checksum_addr=gp+165; length_addr=gp+142; state_addr=gp+156
    def check(length,command):
        upper=length>>8; lower=length&255
        memory={}; init.put(memory,checksum_addr,1,command); init.put(memory,gp+138,2,0x8765)
        pc,events=high.run(hc,common,gp,checksum_addr,upper,init.get(memory,checksum_addr,1))
        if pc!=0x897e: raise ValueError('high path mismatch')
        for event in events:
            if event[0]=='write': init.put(memory,event[1],event[2],event[3])
        value,events=init.run(ic,gp,length_addr,lower,memory)
        if value!=length or init.get(memory,length_addr,2)!=length or init.get(memory,gp+138,2)!=0: raise ValueError('length mismatch')
        events,_,_=route.run(rc,gp,value)
        for address,size,data in events: init.put(memory,address,size,data)
        # Continuation at 0x89a8 uses low byte as a5 and checksum as observed after prior writes.
        loaded=init.get(memory,checksum_addr,1); init.put(memory,checksum_addr,1,(loaded+lower)&255)
        expected_state=6 if length==0 else (5 if length<=1040 else 0)
        if init.get(memory,state_addr,1)!=expected_state: raise ValueError('state mismatch')
        if init.get(memory,checksum_addr,1)!=(command+upper+lower)&255: raise ValueError('checksum mismatch')
    for length in range(65536): check(length,(length*17+3)&255)
    for upper in (0,4,255):
        for lower in range(256):
            for command in range(256): check((upper<<8)|lower,command)
    print('PASS: 65536 lengths plus 196608 independent command/low-byte cases')
    print('Length 0 -> state 6; 1..1040 -> state 5; 1041..65535 -> state 0.')
    print('Checksum low byte = command+high+low mod 256 under stable disjoint addresses.')
    print('Only stitched successful-access projections; no full packet or hardware claim.')
if __name__=='__main__': main()
