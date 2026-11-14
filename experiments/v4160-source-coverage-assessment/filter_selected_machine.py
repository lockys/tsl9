"""Bounded RV32I/C decoder for the selected filter path, not a general emulator."""
import importlib.util
from pathlib import Path
import random

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('projection',HERE/'filter_selected_events.py')
projection=importlib.util.module_from_spec(spec); spec.loader.exec_module(projection)
MASK=0xffffffff

def sx(v,b): return v-(1<<b) if v&(1<<(b-1)) else v

def run(image,index,fields,reads):
    descriptor=0x20001000
    mem={}
    for offset,v in enumerate(fields):
        mem[descriptor+2*offset]=v&255; mem[descriptor+2*offset+1]=v>>8
    for offset,v in ((8,0),(9,0),(10,index),(11,1),(12,0),(13,0),(14,0),(15,0),(16,1),(17,0),(18,0),(19,0)): mem[descriptor+offset]=v
    x=[0]*32; x[10]=descriptor; x[1]=0x1234; pc=0x18ba2; events=[]; rpos=0
    read_addresses=(0x40006600,0x4000661c,0x4000660c,0x40006604,0x40006614,0x4000661c,0x40006600)
    for _ in range(100):
        h=int.from_bytes(image[pc-0x8000:pc-0x8000+2],'little')
        if h&3==3:
            w=int.from_bytes(image[pc-0x8000:pc-0x8000+4],'little'); op=w&127; rd=w>>7&31; f=w>>12&7; a=w>>15&31; b=w>>20&31; nextpc=pc+4
            if op==0x37: x[rd]=w&0xfffff000
            elif op==0x13 and f in (0,4,6):
                imm=sx(w>>20,12); x[rd]=((x[a]+imm) if f==0 else (x[a]^imm) if f==4 else (x[a]|imm))&MASK
            elif op==0x33 and w>>25==0 and f in (1,6): x[rd]=((x[a]<<(x[b]&31)) if f==1 else x[a]|x[b])&MASK
            elif op==3 and f in (2,4,5):
                addr=(x[a]+sx(w>>20,12))&MASK; size={2:4,4:1,5:2}[f]
                if addr>=0x40000000:
                    if size!=4 or rpos>=len(reads) or rpos>=len(read_addresses) or addr!=read_addresses[rpos]: raise ValueError('unexpected MMIO read')
                    x[rd]=reads[rpos]; rpos+=1
                else: x[rd]=sum(mem[addr+i]<<(8*i) for i in range(size))
            elif op==0x23 and f==2:
                imm=sx(((w>>25)<<5)|rd,12); events.append(((x[a]+imm)&MASK,x[b]))
            elif op==0x63 and f==1:
                imm=((w>>31&1)<<12|(w>>7&1)<<11|(w>>25&63)<<5|(w>>8&15)<<1)
                if x[a]!=x[b]: nextpc=pc+sx(imm,13)
            else: raise ValueError(f'unsupported {w:08x} at {pc:x}')
        else:
            q=h&3; f=h>>13; rd=h>>7&31; nextpc=pc+2
            if h==0x8082:
                if rpos!=7: raise ValueError('wrong number of MMIO reads')
                return tuple(events),pc
            elif q==1 and f==2 and rd: x[rd]=sx((h>>2&31)|(h>>12&1)<<5,6)&MASK
            elif q==2 and f==0 and rd and not(h>>12&1): x[rd]=(x[rd]<<(h>>2&31))&MASK
            elif q==2 and f==4 and (h>>12&1) and rd and (h>>2&31): x[rd]=(x[rd]+x[h>>2&31])&MASK
            elif q==1 and f==4:
                dest=8+(h>>7&7); sub=h>>10&3
                if sub==2: x[dest]&=sx((h>>2&31)|(h>>12&1)<<5,6)&MASK
                elif sub==3 and not(h>>12&1):
                    other=8+(h>>2&7); kind=h>>5&3
                    if kind==2: x[dest]|=x[other]
                    elif kind==3: x[dest]&=x[other]
                    else: raise ValueError('unsupported compressed arithmetic')
                else: raise ValueError('unsupported compressed ALU')
            elif q==0 and f==2:
                dest=8+(h>>2&7); base=8+(h>>7&7); off=((h>>10&7)<<3)|((h>>6&1)<<2)|((h>>5&1)<<6)
                addr=(x[base]+off)&MASK; x[dest]=sum(mem[addr+i]<<(8*i) for i in range(4))
            elif q==1 and f in (6,7):
                reg=8+(h>>7&7); imm=((h>>12&1)<<8|(h>>10&3)<<3|(h>>5&3)<<6|(h>>3&3)<<1|(h>>2&1)<<5)
                if (x[reg]==0)==(f==6): nextpc=pc+sx(imm,9)
            elif q==1 and f==5:
                imm=((h>>12&1)<<11|(h>>11&1)<<4|(h>>9&3)<<8|(h>>8&1)<<10|(h>>7&1)<<6|(h>>6&1)<<7|(h>>3&7)<<1|(h>>2&1)<<5); nextpc=pc+sx(imm,12)
            else: raise ValueError(f'unsupported {h:04x} at {pc:x}')
        x[0]=0; pc=nextpc
    raise ValueError('instruction limit')

def main():
    image=projection.route.A.audit.loop.calls.case.dispatch.IMAGE.read_bytes(); projection.route.flow.flow(image)
    rng=random.Random(0x1804160); checks=0
    for index in range(14):
        for _ in range(1024):
            fields=tuple(rng.randrange(65536) for _ in range(4)); reads=tuple(rng.getrandbits(32) for _ in range(7))
            actual,pc=run(image,index,fields,reads)
            if pc!=0x18c58 or actual!=projection.project7(index,fields,reads): raise ValueError('differential mismatch')
            checks+=1
    fields=(1,2,3,4); reads=(0,1,2,3,4,5,6); expected=projection.project7(3,fields,reads)
    for pc in (0x18bb8,0x18bca,0x18be0,0x18bf4,0x18c00,0x18c18,0x18c30,0x18c46,0x18c54):
        bad=bytearray(image); bad[pc-0x8000]^=1
        try: actual,_=run(bad,3,fields,reads)
        except (ValueError,KeyError): continue
        if actual==expected: raise ValueError(f'mutation at {pc:x} not detected')
    # Mutating a load address is rejected even if two supplied read values are equal.
    for pc in (0x18baa,0x18bbc,0x18bd4,0x18c8a,0x18c2a,0x18c40,0x18c4e):
        bad=bytearray(image); bad[pc-0x8000+2]^=0x10
        try: run(bad,3,fields,(0,)*7)
        except (ValueError,KeyError): continue
        raise ValueError(f'load-address mutation at {pc:x} not rejected')
    # Distinct reads prevent accidental read-after-write assumptions; these
    # semantic mutants must disagree with decoded stores on a selected case.
    fields=(0x11,0x22,0x33,0x44); reads=(0x100,0x200,0x300,0x400,0x500,0x600,0x701)
    expected,_=run(image,3,fields,reads)
    mutants=[]
    v=list(expected); v[3]=(v[3][0],fields[1]<<16|fields[3]); mutants.append(v)
    v=list(expected); v[7]=(v[7][0],v[1][1]|(1<<3)); mutants.append(v)
    v=list(expected); v[8]=(v[8][0],v[0][1]&~1); mutants.append(v)
    for mutant in mutants:
        if tuple(mutant)==expected: raise ValueError('semantic mutant survived')
    print(f'PASS: {checks} decoder comparisons; 9 store, 7 load and 3 semantic mutants rejected')
    print('Seven synthetic MMIO reads supplied independently; no hardware or exceptions modeled.')
if __name__=='__main__': main()
