"""Synthetic ordered fill/copy projection, conditional on reference providers.

Not an ISA emulator. No claim that an overlapping source is reachable or safe.
"""
from pathlib import Path
import hashlib
ROOT=Path(__file__).resolve().parents[2]
BIN=ROOT/'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
DIGEST='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'


def sequential(memory,dst,src,n):
    if not dst or not src or not 0<=n<=112: raise ValueError('unsupported inputs')
    for i in range(112): memory[dst+i]=0
    for i in range(n): memory[dst+i]=memory[src+i]
    return bytes(memory[dst:dst+112])


def expected(source,n,offset):
    # Fill first destroys the source bytes that overlap the 112-byte workspace.
    after_fill=bytes(0 if 0<=offset+i<112 else source[i] for i in range(n))
    out=bytearray(112)
    for i in range(n):
        # Forward copy may overwrite the next source byte before it is read.
        src_relative=offset+i
        out[i]=out[src_relative] if 0<=src_relative<i else after_fill[i]
    return bytes(out)


def main():
    raw=BIN.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=DIGEST: raise ValueError('APP hash mismatch')
    count=0
    for pc,n in ((0x19d08,94),(0x19d68,106)):
        source=raw[pc-0x8000:pc-0x8000+n]
        for offset in range(-224,225):
            dst=512; src=dst+offset
            m=bytearray([0xa5]*1200); m[src:src+n]=source
            result=sequential(m,dst,src,n)
            if result!=expected(source,n,offset): raise ValueError(f'mismatch {pc:#x} {offset}')
            if offset>=112 or offset+n<=0:
                if result!=source+bytes(112-n): raise ValueError('disjoint case')
            count+=1
        # Entire source inside workspace: fill destroys it before copy.
        m=bytearray([0xa5]*1200); m[512:512+n]=source
        if sequential(m,512,512,n)!=bytes(112): raise ValueError('same-address witness')
        # Source one byte before workspace: first byte can propagate forward.
        m=bytearray([0xa5]*1200); m[511:511+n]=source
        if sequential(m,512,511,n)!=bytes([source[0]])*n+bytes(112-n): raise ValueError('forward alias witness')
    print(f'PASS: {count} synthetic offsets across two original data slices; disjoint and two alias witnesses')
    print('Conditional forward byte-copy semantics only; no candidate CPU, installed provider or hardware execution.')
if __name__=='__main__': main()
