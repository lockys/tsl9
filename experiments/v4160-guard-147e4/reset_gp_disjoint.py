"""Decode reset GP and check bounded ingress address disjointness conditionally.

Reset GP value is static, not proof it remains live. No concurrency, address
translation, physical RAM, provider effects or complete control flow modeled.
"""
import hashlib
import importlib.util
from pathlib import Path
HERE=Path(__file__).resolve().parent

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path); obj=importlib.util.module_from_spec(spec); spec.loader.exec_module(obj); return obj
store=load('store',HERE/'ingress_payload_store.py'); composed=load('composed',HERE/'ingress_store_length_alias.py')
MASK=0xffffffff

def signed(x,bits): return x-(1<<bits) if x&(1<<(bits-1)) else x

def reset_gp(code):
    if len(code)!=8: raise ValueError('invalid startup code')
    a=int.from_bytes(code[:4],'little'); b=int.from_bytes(code[4:],'little')
    if (a&127,a>>7&31)!=(0x17,3) or (b&127,b>>7&31,b>>12&7,b>>15&31)!=(0x13,3,0,3): raise ValueError('unexpected startup instructions')
    return (0x186aa+(a&0xfffff000)+signed(b>>20,12))&MASK

def main():
    image=store.entry.IMAGE.read_bytes()
    if len(image)!=76800 or hashlib.sha256(image).hexdigest()!=store.entry.SHA: raise ValueError('firmware identity mismatch')
    code=image[0x186aa-0x8000:0x186b2-0x8000]
    if code!=bytes.fromhex('97c1fe1f93816195') or reset_gp(code)!=0x20004000: raise ValueError('reset GP mismatch')
    gp=reset_gp(code)
    if image[0x8a02-0x8000:0x8a20-0x8000]!=store.EXPECTED or image[0x8a20-0x8000:0x8a2a-0x8000]!=composed.transition.EXPECTED: raise ValueError('ingress bytes mismatch')
    protected={(gp+138+i)&MASK for i in range(2)} | {(gp+142+i)&MASK for i in range(2)} | {0x2000bfb8}
    for index in range(1040):
        for byte in (0,255):
            for initial in (0,1,1040,65535):
                loaded,pc,writes=composed.run(image,gp,index,initial,byte)
                if loaded!=initial or pc!=(0x89a8 if index+1<initial else 0x89dc): raise ValueError('length unexpectedly changed')
                if writes[1][0] in protected or writes[1][0]!=0x2000b9d8+index: raise ValueError('payload overlaps protected location')
    for i in range(8):
        mutated=bytearray(code); mutated[i]^=1
        try: result=reset_gp(mutated)
        except ValueError: continue
        if result==gp: raise ValueError(f'undetected startup mutation {i}')
    print('PASS: reset instructions produce gp=0x20004000; 8320 bounded store/reload cases and 8 mutations')
    print('Payload range [0x2000b9d8,0x2000bde8) is disjoint from gp+138, gp+142 and 0x2000bfb8.')
    print('Conditional on unchanged gp and synthetic successful accesses; no hardware or provider-side-effect claim.')

if __name__=='__main__': main()
