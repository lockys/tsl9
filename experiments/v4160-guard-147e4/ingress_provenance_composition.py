"""Conditional connection: selected LBU byte, length formation, route.

Block boundaries are reconstructed; successful accesses and no concurrent
register changes are assumptions, not a complete CPU or hardware execution.
"""
import hashlib
import importlib.util
from pathlib import Path
HERE=Path(__file__).resolve().parent

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module
prov=load('prov',HERE/'ingress_a5_provenance.py')
init=load('init',HERE/'ingress_length_initialize.py')
route=load('route',HERE/'ingress_length_route.py')

def main():
    image=prov.gate.entry.IMAGE.read_bytes()
    if len(image)!=76800 or hashlib.sha256(image).hexdigest()!=prov.gate.entry.SHA: raise ValueError('firmware identity mismatch')
    blocks={pc:image[pc-0x8000:pc-0x8000+len(expected)] for pc,expected in prov.EXPECTED.items()}
    a=image[0x89cc-0x8000:0x89da-0x8000]; b=image[0x89da-0x8000:0x89f6-0x8000]
    if blocks!=prov.EXPECTED or a!=init.EXPECTED or b!=route.EXPECTED: raise ValueError('original bytes mismatch')
    gp=0x20004000
    for byte in range(256):
        pc,a5,reads,_=prov.run(blocks,4,(1,2,3,4),byte,0x20001000)
        if pc!=0x89cc or a5!=byte or reads!=[0x20001000]: raise ValueError('selector did not preserve byte')
        for loaded in (0,1,255,256,1040,1041,32768,65535):
            memory={}; init.put(memory,0x1000,2,loaded)
            value,_=init.run(a,gp,0x1000,a5,memory)
            events,_,_=route.run(b,gp,value)
            if value!=(loaded|byte) or init.get(memory,gp+142,2)!=value: raise ValueError('full/stored mismatch')
            expected=6 if value==0 else (5 if value<=1040 else 0)
            if events!=[(gp+156,1,expected)]: raise ValueError('state mismatch')
    for loaded in range(65536):
        for byte in range(256):
            value=loaded|byte
            if value>65535 or (value&0xffff)!=value: raise ValueError('range invariant failed')
    print('PASS: 2048 segmented byte-decoder cases, 16777216 exhaustive arithmetic pairs')
    print('Conditionally on this selector path, a5 is 8-bit so full a4 equals the stored halfword.')
    print('The prior high-a5 witness is not reachable through this local chain; other paths remain unknown.')

if __name__=='__main__': main()
