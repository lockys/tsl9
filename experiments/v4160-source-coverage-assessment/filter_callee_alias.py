"""Address-set check for the filter caller and 0x18ba2's stores.

Conditional on the byte actually read by the callee being 0..13 and standard
32-bit arithmetic; a prior aliased store could change that byte, so this is not
an unconditional complete store set. Addresses do not establish mapping,
accepted writes or stable MMIO.
"""
import hashlib
import importlib.util
from pathlib import Path

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('audit',HERE/'filter_callee_registers.py')
audit=importlib.util.module_from_spec(spec); spec.loader.exec_module(audit)
MASK=0xffffffff
FIXED=(0x40006600,0x40006604,0x4000660c,0x40006614,0x4000661c)


EXPECTED_STORES={
    0x18bb8:(14,13,512), 0x18bca:(14,11,540), 0x18be0:(14,11,524),
    0x18bf4:(15,11,576), 0x18c00:(15,14,580), 0x18c18:(15,14,516),
    0x18c30:(15,13,532), 0x18c46:(15,12,1564), 0x18c54:(15,14,1536),
    0x18c6a:(14,11,524), 0x18c7e:(15,11,576), 0x18c9e:(15,14,532),
}


def decode_store(word):
    if word&127!=0x23 or (word>>12)&7!=2: raise ValueError('not sw')
    offset=((word>>25)<<5)|((word>>7)&31)
    if offset&2048: offset-=4096
    return ((word>>15)&31,(word>>20)&31,offset)


def verify_stores(image):
    pc=audit.START; found={}
    while pc<audit.END:
        off=pc-0x8000; h=int.from_bytes(image[off:off+2],'little')
        width=4 if h&3==3 else 2
        if width==4:
            word=int.from_bytes(image[off:off+4],'little')
            if word&127==0x23: found[pc]=decode_store(word)
        pc+=width
    if found!=EXPECTED_STORES: raise ValueError('store inventory mismatch')
    return found


def byte_set(starts,size):
    return {(addr+i)&MASK for addr in starts for i in range(size)}


def writes(index):
    if not 0<=index<14: raise ValueError('index outside caller sequence')
    # Conservative union: mutually exclusive branches are intentionally merged.
    return byte_set((*FIXED,0x40006640+8*index,0x40006644+8*index),4)


def classify(sp):
    sp&=MASK
    source=byte_set(((sp+32)&MASK,),112)
    descriptor=byte_set(((sp+12)&MASK,),20)
    all_stores=set().union(*(writes(i) for i in range(14)))
    return source&all_stores,descriptor&all_stores


def all_indices_stores():
    # Dynamic two adjacent words per byte-valued index fill 2048 bytes.
    return byte_set(FIXED,4) | set(range(0x40006640,0x40006e40))


def classify_all(sp):
    source=byte_set((((sp&MASK)+32)&MASK,),112)
    descriptor=byte_set((((sp&MASK)+12)&MASK,),20)
    potential=all_indices_stores()
    return source&potential,descriptor&potential


def main():
    image=audit.loop.calls.case.dispatch.IMAGE.read_bytes()
    if len(image)!=76800 or hashlib.sha256(image).hexdigest()!=audit.loop.calls.case.dispatch.SHA: raise ValueError('APP identity mismatch')
    audit.scan(image); verify_stores(image)
    # Check store operand extraction without relying on the image-hash check.
    for pc in EXPECTED_STORES:
        off=pc-0x8000; word=int.from_bytes(image[off:off+4],'little')
        for bit in (7,15,20,25):
            bad=bytearray(image); bad[off:off+4]=(word^(1<<bit)).to_bytes(4,'little')
            try: verify_stores(bad)
            except ValueError: continue
            raise ValueError('store operand mutant accepted')
    for i in range(14):
        if len(writes(i))!=28: raise ValueError('unexpected overlapping store words')
    # Independent interval test in a non-wrapping sweep around the peripheral.
    for sp in range(0x40000000,0x40010000):
        actual=classify(sp)
        starts=[*FIXED]+[0x40006640+4*i for i in range(28)]
        expected=[]
        for offset,size in ((32,112),(12,20)):
            expected.append({x for a in starts for x in range(a,a+4) if sp+offset<=x<sp+offset+size})
        if actual!=tuple(expected): raise ValueError('interval comparison failed')
    source,descriptor=classify(0x40006620)
    if 0x40006640 not in source or descriptor: raise ValueError('source overlap witness failed')
    source,descriptor=classify(0x400065f4)
    if 0x40006600 not in descriptor: raise ValueError('descriptor overlap witness failed')
    for sp in (0,0x20000f50,0xffffff80,0xfffffff0,0xffffffff):
        source,descriptor=classify(sp)
        if source or descriptor: raise ValueError('unexpected control overlap')
        if any(classify_all(sp)): raise ValueError('unexpected full-index overlap')
    # Verify all 256 possible loaded indices against the closed-form byte union.
    all_index=all_indices_stores()
    explicit=byte_set(FIXED,4)
    for i in range(256):
        explicit |= byte_set((0x40006640+8*i,0x40006644+8*i),4)
    if explicit!=all_index or len(all_index)!=2068: raise ValueError('all-index union mismatch')
    source,descriptor=classify_all(0x40006e00)
    if 0x40006e20 not in source or not descriptor: raise ValueError('high-index overlap witness failed')
    if any(classify(0x40006e00)): raise ValueError('witness should be outside 0..13 union')
    print('PASS: 12 original store operands, 48 operand mutants, 65536 stack addresses, 14 index unions, two witnesses and five controls')
    print('When the callee actually reads index 0..13, potential writes overlap source at synthetic sp=0x40006620.')
    print('Prior aliased writes can change the index; no unconditional store-set completeness is claimed.')
    print('All 256 actual byte indices yield a 2068-byte conservative union; sp=0x40006e00 adds a high-index witness.')
    print('Address intersection only; no assertion that peripheral memory is ordinary RAM or the witness is reachable.')

if __name__=='__main__': main()
