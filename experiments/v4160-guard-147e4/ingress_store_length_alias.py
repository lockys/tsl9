"""Compose original ingress payload store and length reload over shared bytes.

Single-thread synthetic memory, successful operations, no provider effects;
not proof that arbitrary gp/index states occur on a device.
"""
import hashlib
import importlib.util
from pathlib import Path
HERE=Path(__file__).resolve().parent

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path); obj=importlib.util.module_from_spec(spec); spec.loader.exec_module(obj); return obj
store=load('store',HERE/'ingress_payload_store.py'); transition=load('transition',HERE/'ingress_payload_transition.py')
MASK=0xffffffff; BUFFER=0x2000b9d8


def run(image,gp,index,initial_length,byte):
    mem={}; length_address=(gp+142)&MASK
    mem[length_address]=initial_length&255; mem[(length_address+1)&MASK]=initial_length>>8
    store_code=image[0x8a02-0x8000:0x8a20-0x8000]; transition_code=image[0x8a20-0x8000:0x8a2a-0x8000]
    pc,writes,_=store.run(store_code,gp,index,byte)
    if pc!=0x8a20 or len(writes)!=2: raise ValueError('store path not taken')
    for address,width,value in writes:
        for i in range(width): mem[(address+i)&MASK]=(value>>(8*i))&255
    if length_address not in mem or (length_address+1)&MASK not in mem: raise ValueError('length missing')
    loaded=mem[length_address] | mem[(length_address+1)&MASK]<<8
    next_index=(index+1)&65535
    pc,reads,_=transition.run(transition_code,gp,next_index,loaded)
    if reads!=[length_address]: raise ValueError('read address mismatch')
    return loaded,pc,writes


def main():
    image=store.entry.IMAGE.read_bytes()
    if len(image)!=76800 or hashlib.sha256(image).hexdigest()!=store.entry.SHA: raise ValueError('firmware identity mismatch')
    if image[0x8a02-0x8000:0x8a20-0x8000]!=store.EXPECTED or image[0x8a20-0x8000:0x8a2a-0x8000]!=transition.EXPECTED: raise ValueError('original bytes mismatch')
    alias_gp=BUFFER-142
    for byte in range(256):
        loaded,pc,writes=run(image,alias_gp,0,2,byte)
        if (loaded,pc)!=(byte,0x89a8 if byte>1 else 0x89dc) or writes!=[(alias_gp+138,2,1),(BUFFER,1,byte)]: raise ValueError('low-byte overlap mismatch')
        loaded,pc,_=run(image,0x20004000,0,2,byte)
        if (loaded,pc)!=(2,0x89a8): raise ValueError('disjoint control mismatch')
    # A 0x0002 length becomes zero if the payload byte aliases its low byte.
    if run(image,alias_gp,0,2,0)[:2]!=(0,0x89dc): raise ValueError('alias witness mismatch')
    print('PASS: 256 low-byte overlaps and 256 disjoint controls; length 2 becomes 0 and changes 0x89a8 -> 0x89dc')
    print('Conditional synthetic gp; fixed reset-derived gp control is not a live device measurement.')

if __name__=='__main__': main()
