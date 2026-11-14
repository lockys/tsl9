"""Bounded bit-dependence of filter packed data under stable synthetic inputs.

Maps each of the 896 source bits through the caller event decoder and the
selected original-byte callee decoder. No provider or hardware is executed.
"""
import importlib.util
from pathlib import Path
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('compose',HERE/'filter_original_data_composition.py')
compose=importlib.util.module_from_spec(spec); spec.loader.exec_module(compose)
loop=compose.loop; machine=compose.compose.machine


def project(image,buffer):
    if len(buffer)!=112: raise ValueError('expected 112 bytes')
    sp=0x20001000; mem={sp+32+i:b for i,b in enumerate(buffer)}; output=[]
    for i in range(14):
        loop.step(image,mem,sp,sp+32+8*i,i,1,1)
        fields=tuple(mem[sp+12+2*j]|mem[sp+13+2*j]<<8 for j in range(4))
        events,_=machine.run(image,i,fields,(0,)*7)
        output.extend((events[3][1],events[4][1]))
    return output


def main():
    image=loop.calls.case.dispatch.IMAGE.read_bytes(); machine.projection.route.flow.flow(image)
    base=project(image,bytes(112)); visible=0; invisible=0; suffix={94:0,106:0}; basis={}
    for byte in range(112):
        for bit in range(8):
            modified=bytearray(112); modified[byte]=1<<bit
            words=project(image,modified)
            changed=[(i,a^b) for i,(a,b) in enumerate(zip(words,base)) if a!=b]
            # Halfword order maps f0,f1,f2,f3 into output pair f1|f3<<16,
            # then f0|f2<<16. High input byte bits 3..7 are shifted out.
            field=(byte//2)%4; slot=2*(byte//8)+(0 if field in (1,3) else 1)
            output_bit=(8*(byte%2)+bit+5)+(16 if field>=2 else 0)
            observable=(byte%2==0 or bit<3)
            expected=[(slot,1<<output_bit)] if observable else []
            if changed!=expected: raise ValueError(f'dependency mismatch byte={byte} bit={bit}')
            if observable:
                key=(slot,output_bit)
                if key in basis: raise ValueError('two source bits map to same output bit')
                basis[key]=(byte,bit)
                visible+=1
                for length in suffix:
                    if byte>=length: suffix[length]+=1
            else: invisible+=1
    if (visible,invisible,suffix)!=(616,280,{94:99,106:33}): raise ValueError('unexpected counts')
    # On this bounded instruction path the constituent operations on source
    # data are shifts, masks and nonoverlapping ORs, so this is a linear map.
    # Check arbitrary buffers against the single-bit map as a regression test.
    import random
    rng=random.Random(0x4160)
    for _ in range(256):
        sample=bytes(rng.getrandbits(8) for _ in range(112)); want=[0]*28
        for (slot,output_bit),(byte,bit) in basis.items():
            want[slot]|=((sample[byte]>>bit)&1)<<output_bit
        if project(image,sample)!=want: raise ValueError('superposition mismatch')
    print(f'PASS: 896 input-bit probes; {visible} distinct output bits, {invisible} discarded; 256 superposition cases')
    print('Conditional bit-map rank=616; each pair of equal outputs shares the same 616 observable input bits.')
    print(f'Unknown suffix observable bits: 94-byte prefix={suffix[94]}, 106-byte prefix={suffix[106]}')
    print('Conditional output possibilities with fixed prefix and unconstrained suffix: 2^99 / 2^33.')
    print('Bounded synthetic decoder projection; no installed provider or hardware demonstrated.')
if __name__=='__main__': main()
