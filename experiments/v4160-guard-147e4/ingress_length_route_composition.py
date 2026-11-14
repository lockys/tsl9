"""Compose length initialization with its state route at a register boundary."""
import hashlib
import importlib.util
from pathlib import Path
HERE=Path(__file__).resolve().parent

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module
init=load('init',HERE/'ingress_length_initialize.py')
route=load('route',HERE/'ingress_length_route.py')

def main():
    image=init.gate.entry.IMAGE.read_bytes()
    if len(image)!=76800 or hashlib.sha256(image).hexdigest()!=init.gate.entry.SHA: raise ValueError('firmware identity mismatch')
    a=image[0x89cc-0x8000:0x89da-0x8000]; b=image[0x89da-0x8000:0x89f6-0x8000]
    if a!=init.EXPECTED or b!=route.EXPECTED: raise ValueError('original bytes mismatch')
    gp=0x20004000
    for loaded in range(65536):
        for a5 in (0,0x10000):
            memory={}; init.put(memory,0x1000,2,loaded)
            value,events=init.run(a,gp,0x1000,a5,memory)
            route_events,_,_=route.run(b,gp,value)
            expected=6 if value==0 else (5 if value<=1040 else 0)
            if route_events!=[(gp+156,1,expected)] or init.get(memory,gp+142,2)!=(value&0xffff): raise ValueError('composition mismatch')
    memory={}; init.put(memory,0x1000,2,0)
    value,_=init.run(a,gp,0x1000,0x10000,memory)
    events,_,_=route.run(b,gp,value)
    if value!=0x10000 or init.get(memory,gp+142,2)!=0 or events!=[(gp+156,1,0)]: raise ValueError('high-bit witness mismatch')
    print('PASS: 131072 segmented initialization/route cases')
    print('Synthetic a5=0x10000, loaded=0 stores length 0 yet routes state 0 (full a4=65536).')
    print('Assumes successful stable accesses; neither caller reachability nor hardware established.')

if __name__=='__main__': main()
