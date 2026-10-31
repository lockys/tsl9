"""Compare three permitted data windows across saved local candidate runtimes."""
import hashlib
from pathlib import Path

root = Path(__file__).resolve().parents[2]
folder = root / 'firmware-downloads/legacy-options-2026-10-20/BINs'
base = 0x8000
excluded = ((0x14056,0x14c8a),(0x1a69c,0x1a6a0))
reference = folder / 'ID-2966-V4.1.60-decoded.bin'
definitions = (
    ('sequence',0x1a638,48,'234dd45cce8b151ef80ba9455735ac58f2757372e0fca8633569995e542330cf'),
    ('counter',0x1ab48,8,'f39e341bab92c73ab8a2f7c9afcc543cd2f982d599ca715de8ed738d67912dd8'),
    ('mode',0x1a078,96,'e0ef3eab0eff857afab57a4247176bfbbe8b03a712108637178d3a300810db8f'),
    ('sequence_code',0x12020,0x8a,'1225b6a684484e6c5a3fc6b38f57214729a7e3d6029095e66784c9bb31841e82'),
    ('counter_code',0xa114,0x58,'b750b488b310fb5ef9094907b983be0392d8ae1c3506b600bfd9afdaf92661c9'),
    ('mode_code',0xcedc,0xbc,'e6dd2498940c6d477836f3411ad6e381fc9a485d0eb5d54f300f1c7809e9f27f'),
)
def read_window(f, address, size):
    if address<base or any(address<hi and address+size>lo for lo,hi in excluded):
        raise SystemExit('Refusing excluded or invalid window')
    f.seek(address-base)
    result=f.read(size)
    if len(result)!=size:
        raise SystemExit('Short input')
    return result
patterns={}
with reference.open('rb') as f:
    for name,address,size,expected in definitions:
        data=read_window(f,address,size)
        if hashlib.sha256(data).hexdigest()!=expected:
            raise SystemExit('Reference window changed')
        patterns[name]=data
cases=(
 ('2389','4.0.49',76800,0x1a2fc,0x1a7f4,0x19d3c),
 ('2410','4.0.50',76800,0x1a31c,0x1a814,0x19d5c),
 ('2527','4.1.00',76800,0x1a30c,0x1a804,0x19d4c),
 ('2581','4.1.00',76800,0x1a2d0,0x1a7c8,0x19d10),
 ('2590','4.1.00',76800,0x1a30c,0x1a804,0x19d4c),
 ('2601','4.1.00',76800,0x1a4d4,0x1a9cc,0x19f14),
 ('2603','4.1.01',76800,0x1a470,0x1a968,0x19eb0),
 ('2613','4.1.01',76800,0x1a518,0x1aa10,0x19f58),
 ('2816','4.1.01',76800,0x1a56c,0x1aa64,0x19fac),
 ('2833','4.1.01',76800,0x1a4b4,0x1a9b0,0x19ef4),
 ('2841','4.1.10',76800,0x1a504,0x1aa00,0x19f44),
 ('2869','4.1.20',76800,0x1a5b0,0x1aac0,0x19ff0),
 ('2873','4.1.20',77824,0x1a664,0x1ab74,0x1a0a4),
 ('2914','4.1.20',77824,0x1a6ac,0x1abbc,0x1a0ec),
 ('2946','4.1.30',76800,0x1a658,0x1ab68,0x1a098),
 ('2958','4.1.40',76800,0x1a600,0x1ab10,0x1a040),
 ('2963','4.1.50',76800,0x1a638,0x1ab48,0x1a078),
 ('2966','4.1.60',76800,0x1a638,0x1ab48,0x1a078),
)
for ident,version,length,seq,counter,mode in cases:
    path=folder / ('ID-'+ident+'-V'+version+'-decoded.bin')
    if path.stat().st_size!=length:
        raise SystemExit('Candidate size changed: '+ident)
    matches={name:[] for name in ('sequence','counter','mode')}
    with path.open('rb') as f:
        for lo,hi in ((base,0x14056),(0x14c8a,0x1a69c),(0x1a6a0,base+length)):
            data=read_window(f,lo,hi-lo)
            for name in matches:
                offset=0
                while True:
                    pos=data.find(patterns[name],offset)
                    if pos<0:
                        break
                    matches[name].append(lo+pos)
                    offset=pos+1
        if ident=='2963':
            for name,address,size,_ in definitions[3:]:
                if read_window(f,address,size)!=patterns[name]:
                    raise SystemExit('V4.1.50 instruction window changed')
    if matches!={'sequence':[seq],'counter':[counter],'mode':[mode]}:
        raise SystemExit('Candidate matches changed: '+ident)
with reference.open('rb') as f:
    consumers=(
        ('sequence',read_window(f,0x1202e,0x32),0xc17,0xc0c13),
        ('counter',read_window(f,0xa146,0x1e),0x797,0x78793),
        ('mode',read_window(f,0xcf46,0x1c),0x797,0x78793),
    )
totals={name:0 for name,_,_,_ in consumers}
for ident,version,length,seq,counter,mode in cases:
    path=folder / ('ID-'+ident+'-V'+version+'-decoded.bin')
    targets={'sequence':seq,'counter':counter,'mode':mode}
    hits={name:[] for name,_,_,_ in consumers}
    with path.open('rb') as f:
        for lo,hi in ((base,0x14056),(0x14c8a,0x1a69c),(0x1a6a0,base+length)):
            data=read_window(f,lo,hi-lo)
            for name,pattern,auipc_low,addi_low in consumers:
                offset=0
                while True:
                    pos=data.find(pattern[:8],offset)
                    if pos<0:
                        break
                    offset=pos+1
                    if pos+len(pattern)>len(data) or data[pos+16:pos+len(pattern)]!=pattern[16:]:
                        continue
                    auipc=int.from_bytes(data[pos+8:pos+12],'little')
                    addi=int.from_bytes(data[pos+12:pos+16],'little')
                    if auipc&0xfff!=auipc_low or addi&0xfffff!=addi_low:
                        continue
                    imm=addi>>20
                    imm-=4096 if imm&2048 else 0
                    target=(lo+pos+8+(auipc&0xfffff000)+imm)&0xffffffff
                    if target==targets[name]:
                        hits[name].append(lo+pos)
    for name in hits:
        if len(hits[name])>1:
            raise SystemExit('Multiple consumer candidates: '+ident+' '+name)
        totals[name]+=len(hits[name])
if totals!={'sequence':15,'counter':10,'mode':18}:
    raise SystemExit('Cross-version consumer candidate counts changed')
counter_pattern=next(pattern for name,pattern,_,_ in consumers if name=='counter')
for number,(ident,version,length,_,target,_) in enumerate(cases):
    path=folder / ('ID-'+ident+'-V'+version+'-decoded.bin')
    hits=[]
    with path.open('rb') as f:
        for lo,hi in ((base,0x14056),(0x14c8a,0x1a69c),(0x1a6a0,base+length)):
            data=read_window(f,lo,hi-lo)
            offset=0
            while True:
                position=data.find(counter_pattern[4:8],offset)
                if position<0:
                    break
                offset=position+1
                pos=position-4
                if pos<0 or pos+len(counter_pattern)>len(data) or data[pos+16:pos+len(counter_pattern)]!=counter_pattern[16:]:
                    continue
                load=int.from_bytes(data[pos:pos+4],'little')
                auipc=int.from_bytes(data[pos+8:pos+12],'little')
                addi=int.from_bytes(data[pos+12:pos+16],'little')
                if load&0xfffff!=int.from_bytes(counter_pattern[:4],'little')&0xfffff or auipc&0xfff!=0x797 or addi&0xfffff!=0x78793:
                    continue
                imm=addi>>20
                imm-=4096 if imm&2048 else 0
                address=(lo+pos+8+(auipc&0xfffff000)+imm)&0xffffffff
                if address==target:
                    displacement=load>>20
                    displacement-=4096 if displacement&2048 else 0
                    hits.append(displacement)
    expected=184 if number<8 else 176
    if hits!=[expected]:
        raise SystemExit('Cross-version counter GP displacement changed: '+ident)
sequence_pattern=next(pattern for name,pattern,_,_ in consumers if name=='sequence')
different_offsets={'2601':340,'2603':336,'2613':340}
for ident,version,length,target,_,_ in cases:
    path=folder / ('ID-'+ident+'-V'+version+'-decoded.bin')
    hits=[]
    with path.open('rb') as f:
        for lo,hi in ((base,0x14056),(0x14c8a,0x1a69c),(0x1a6a0,base+length)):
            data=read_window(f,lo,hi-lo)
            offset=0
            while True:
                position=data.find(sequence_pattern[4:8],offset)
                if position<0:
                    break
                offset=position+1
                pos=position-4
                if pos<0 or pos+len(sequence_pattern)>len(data) or data[pos+16:pos+len(sequence_pattern)]!=sequence_pattern[16:]:
                    continue
                pointer=int.from_bytes(data[pos:pos+4],'little')
                auipc=int.from_bytes(data[pos+8:pos+12],'little')
                addi=int.from_bytes(data[pos+12:pos+16],'little')
                if pointer&0xfffff!=int.from_bytes(sequence_pattern[:4],'little')&0xfffff or auipc&0xfff!=0xc17 or addi&0xfffff!=0xc0c13:
                    continue
                imm=addi>>20
                imm-=4096 if imm&2048 else 0
                address=(lo+pos+8+(auipc&0xfffff000)+imm)&0xffffffff
                if address==target:
                    displacement=pointer>>20
                    displacement-=4096 if displacement&2048 else 0
                    hits.append((lo+pos,displacement))
    if len(hits)!=1 or hits[0][1]!=different_offsets.get(ident,332):
        raise SystemExit('Cross-version sequence GP displacement changed: '+ident)
    with path.open('rb') as f:
        if read_window(f,hits[0][0]+0x32,0x3a)!=patterns['sequence_code'][0x40:0x7a]:
            raise SystemExit('Cross-version sequence match normalization changed: '+ident)
        if read_window(f,hits[0][0]+0x6e,8)!=patterns['sequence_code'][0x7c:0x84]:
            raise SystemExit('Cross-version sequence mismatch reset changed: '+ident)
entries=(0x1842c,0x1844a,0x1843c,0x183fe,0x1843a,0x1859a,
         0x18536,0x185e0,0x18634,0x1857c,0x185ca,0x18624,
         0x186d8,0x18720,0x186ca,0x18672,0x186ac,0x186aa)
for (ident,version,_,_,_,_),entry in zip(cases,entries):
    path=folder / ('ID-'+ident+'-V'+version+'-decoded.bin')
    with path.open('rb') as f:
        word=int.from_bytes(read_window(f,base,4),'little')
        initialization=read_window(f,entry,16)
    if word&0xfff!=0x6f:
        raise SystemExit('Unexpected reset JAL: '+ident)
    imm=((word>>31)<<20)|(((word>>12)&255)<<12)|(((word>>20)&1)<<11)|(((word>>21)&1023)<<1)
    imm-=1<<21 if imm&(1<<20) else 0
    if (base+imm)&0xffffffff!=entry:
        raise SystemExit('Unexpected reset target: '+ident)
    for offset,auipc_low,addi_low,expected in ((0,0x197,0x18193,0x20004000),(8,0x117,0x10113,0x20010000)):
        auipc=int.from_bytes(initialization[offset:offset+4],'little')
        addi=int.from_bytes(initialization[offset+4:offset+8],'little')
        if auipc&0xfff!=auipc_low or addi&0xfffff!=addi_low:
            raise SystemExit('Unexpected reset register initialization: '+ident)
        immediate=addi>>20
        immediate-=4096 if immediate&2048 else 0
        value=(entry+offset+(auipc&0xfffff000)+immediate)&0xffffffff
        if value!=expected:
            raise SystemExit('Unexpected GP or SP value: '+ident)
ends=(0xc950,0xc950,0xc950,0xc950,0xc950,0xc958,
      0xc954,0xc958,0xc950,0xc94c,0xc950,0xc954,
      0xc954,0xc954,0xc954,0xc954,0xc958,0xc958)
for number,((ident,version,_,_,_,_),entry,end_offset) in enumerate(zip(cases,entries,ends)):
    path=folder / ('ID-'+ident+'-V'+version+'-decoded.bin')
    with path.open('rb') as f:
        data=read_window(f,entry+0x34,0x1a)
    start_inst=int.from_bytes(data[:4],'little')
    upper=int.from_bytes(data[4:8],'little')
    lower=int.from_bytes(data[8:12],'little')
    if start_inst&0xfffff!=0x18513 or upper&0xfff!=0x597 or lower&0xfffff!=0x58593:
        raise SystemExit('Unexpected zero-range setup: '+ident)
    displacement=start_inst>>20
    displacement-=4096 if displacement&2048 else 0
    immediate=lower>>20
    immediate-=4096 if immediate&2048 else 0
    start=0x20004000+displacement
    end=(entry+0x38+(upper&0xfffff000)+immediate)&0xffffffff
    if displacement!=(136 if number<8 else 128) or end!=0x20000000+end_offset:
        raise SystemExit('Unexpected zero-range bounds: '+ident)
    if data[12:]!=bytes.fromhex('6377b500232005001105e36db5fe'):
        raise SystemExit('Unexpected zero-loop instruction bytes: '+ident)
    counter=0x20004000+(184 if number<8 else 176)
    sequence=0x20004000+different_offsets.get(ident,332)
    if start%4 or end%4 or not (start<=counter<end and start<=sequence and sequence+4<=end):
        raise SystemExit('State bytes not contained in reset zero range: '+ident)
    if end-0x2000c000 not in range(2380,2393):
        raise SystemExit('Unexpected excess beyond 48 KiB example: '+ident)
needle=bytes.fromhex('85078d8b')
for number,(ident,version,length,_,_,_) in enumerate(cases):
    path=folder / ('ID-'+ident+'-V'+version+'-decoded.bin')
    displacement=184 if number<8 else 176
    hits=[]
    direct=[]
    sequence_direct=[]
    sequence_start=different_offsets.get(ident,332)
    with path.open('rb') as f:
        for lo,hi in ((base,0x14056),(0x14c8a,0x1a69c),(0x1a6a0,base+length)):
            data=read_window(f,lo,hi-lo)
            for pc in range(0,len(data)-3,2):
                word=int.from_bytes(data[pc:pc+4],'little')
                kind=(word>>12)&7
                if word&127!=0x23 or (word>>15)&31!=3 or kind>2:
                    continue
                imm=((word>>25)<<5)|((word>>7)&31)
                imm-=4096 if imm&2048 else 0
                if imm<=displacement<imm+(1<<kind):
                    direct.append((lo+pc,imm,1<<kind))
                if imm<sequence_start+4 and imm+(1<<kind)>sequence_start:
                    sequence_direct.append((lo+pc,imm,1<<kind))
            offset=0
            while True:
                pos=data.find(needle,offset)
                if pos<0:
                    break
                offset=pos+1
                if pos<4 or pos+10>len(data):
                    continue
                load=int.from_bytes(data[pos-4:pos],'little')
                if load&0xfffff!=0x1c783 or load>>20!=displacement:
                    continue
                for skip in (0,2):
                    if skip and data[pos+4:pos+6]!=bytes.fromhex('2244'):
                        continue
                    store=int.from_bytes(data[pos+4+skip:pos+8+skip],'little')
                    immediate=((store>>25)<<5)|((store>>7)&31)
                    if (store&127==0x23 and (store>>12)&7==0 and
                        (store>>15)&31==3 and (store>>20)&31==15 and
                        immediate==displacement):
                        hits.append((lo+pos-4,skip))
    if len(hits)!=2 or sorted(skip for _,skip in hits)!=[0,2]:
        raise SystemExit('Cross-version masked counter stores changed: '+ident)
    if direct!=sorted((pc+8+skip,displacement,1) for pc,skip in hits):
        raise SystemExit('Additional direct standard GP-relative counter store candidate: '+ident)
    if sequence_direct:
        raise SystemExit('Direct standard GP-relative sequence store candidate: '+ident)
with reference.open('rb') as f:
    clear_pattern=read_window(f,0xa37c,18)
if clear_pattern!=bytes.fromhex('b707040003a38704154681451385c10a0283'):
    raise SystemExit('Reference counter-clear call changed')
for number,(ident,version,length,_,_,_) in enumerate(cases):
    path=folder / ('ID-'+ident+'-V'+version+'-decoded.bin')
    expected=(184 if number<8 else 176)-4
    hits=[]
    with path.open('rb') as f:
        for lo,hi in ((base,0x14056),(0x14c8a,0x1a69c),(0x1a6a0,base+length)):
            data=read_window(f,lo,hi-lo)
            offset=0
            while True:
                pos=data.find(clear_pattern[:12],offset)
                if pos<0:
                    break
                offset=pos+1
                if pos+18>len(data) or data[pos+16:pos+18]!=clear_pattern[16:18]:
                    continue
                addi=int.from_bytes(data[pos+12:pos+16],'little')
                if addi&0xfffff==0x18513 and addi>>20==expected:
                    hits.append(lo+pos)
    if len(hits)!=1:
        raise SystemExit('Candidate counter clear call changed: '+ident)
setter_pcs=(0xced8,0xcee2,0xcefc,0xceba,0xceba,0xcfb0,0xcf4c,0xcf8a,0xcfde,
            0xcf86,0xcfce,0xcfd6,0xd078,0xd078,0xd02a,0xd02a,0xd05c,0xd05c)
mode_anchors=(0xcdc2,0xcdcc,0xcde6,0xcda4,0xcda4,0xce9a,0xce36,0xce74,0xcec8,
              0xce70,0xceb8,0xcec0,0xcf62,0xcf62,0xcf14,0xcf14,0xcf46,0xcf46)
states=(0xbf34,0xbf34,0xbf34,0xbf34,0xbf34,0xbf3c,0xbf38,0xbf3c,0xbf34,
        0xbf30,0xbf34,0xbf34,0xbf34,0xbf34,0xbf34,0xbf34,0xbf38,0xbf38)
with reference.open('rb') as f:
    setter=read_window(f,0xd05c,0x20)
if hashlib.sha256(setter).hexdigest()!='7aeb37e5fa35b5285db6506c1cb8a34b1774f2ed427169e29dd2405aaafa5259':
    raise SystemExit('Reference mode setter changed')
mode_pattern=next(pattern for name,pattern,_,_ in consumers if name=='mode')
def pcrel_target(pc, data, auipc_low, second_low):
    a=int.from_bytes(data[:4],'little')
    b=int.from_bytes(data[4:8],'little')
    if a&0xfff!=auipc_low or b&0xfffff!=second_low:
        raise SystemExit('Unexpected PC-relative instruction pair')
    immediate=b>>20
    immediate-=4096 if immediate&2048 else 0
    return (pc+(a&0xfffff000)+immediate)&0xffffffff
for (ident,version,_,_,_,mode),setter_pc,anchor,state_offset in zip(cases,setter_pcs,mode_anchors,states):
    path=folder / ('ID-'+ident+'-V'+version+'-decoded.bin')
    state=0x20000000+state_offset
    with path.open('rb') as f:
        block=read_window(f,setter_pc,0x20)
        table=read_window(f,anchor,len(mode_pattern))
        enable=read_window(f,anchor-0x6a,8)
        selector=read_window(f,anchor-0x60,8)
        mode_load=read_window(f,anchor-0x40,8)
    if block[8:]!=setter[8:] or pcrel_target(setter_pc,block,0x797,0x78793)!=state:
        raise SystemExit('Mode setter changed: '+ident)
    if (table[:8]!=mode_pattern[:8] or table[16:]!=mode_pattern[16:] or
        pcrel_target(anchor+8,table[8:16],0x797,0x78793)!=mode):
        raise SystemExit('Mode table lookup changed: '+ident)
    for pc,data,first,second,expected in ((anchor-0x6a,enable,0x797,0x7c783,state),
                                         (anchor-0x60,selector,0x717,0x74703,state+2),
                                         (anchor-0x40,mode_load,0x717,0x74703,state+1)):
        if pcrel_target(pc,data,first,second)!=expected:
            raise SystemExit('Mode state read address changed: '+ident)
# These are encoded-transfer candidates, not an instruction-boundary or reachability proof.
expected_transfers = (
 (0xa144,0xabb6,0xd3ee,0xe092,0xe590), (0xa144,0xabb6,0xd3f8,0xe09c,0xe59a),
 (0xa188,0xabd0,0xd412,0xe0b6,0xe5b4), (0xa148,0xab90,0xd3d0,0xe074,0xe572),
 (0xa148,0xab90,0xd3d0,0xe074,0xe572), (0xa142,0xab8c,0xd4ca,0xe16e,0xe66c),
 (0xa142,0xab8c,0xd466,0xe10a,0xe608), (0xa142,0xab8c,0xd4a4,0xe148,0xe646),
 (0xa15a,0xaba4,0xd4f8,0xe19c,0xe69a), (0xa178,0xabc2,0xd4a0,0xe144,0xe642),
 (0xa178,0xabc2,0xd4e8,0xe18c,0xe68a), (0xa182,0xabc4,0xd4f0,0xe194,0xe692),
 (0xa224,0xac66,0xd592,0xe236,0xe734), (0xa224,0xac66,0xd592,0xe254,0xe752),
 (0xa224,0xac66,0xd544,0xe206,0xe704), (0xa224,0xac66,0xd4f6,0xe1b8,0xe6b6),
 (0xa224,0xac6c,0xd528,0xe1ea,0xe6e8), (0xa224,0xac6c,0xd528,0xe1ea,0xe6e8),
)
def signed(value, bits):
    return value-(1<<bits) if value & (1<<(bits-1)) else value
def transfer_target(data, pc):
    h=int.from_bytes(data[:2], 'little')
    if h & 3 != 3:
        if h & 3 != 1 or (h >> 13) & 7 not in (1,5): return None
        imm=((h>>12&1)<<11)|((h>>11&1)<<4)|((h>>9&3)<<8)|((h>>8&1)<<10)|((h>>7&1)<<6)|((h>>6&1)<<7)|((h>>3&7)<<1)|((h>>2&1)<<5)
        return (pc+signed(imm,12)) & 0xffffffff
    if len(data)<4: return None
    w=int.from_bytes(data[:4], 'little')
    if w & 127 != 111: return None
    imm=((w>>31&1)<<20)|((w>>21&1023)<<1)|((w>>20&1)<<11)|((w>>12&255)<<12)
    return (pc+signed(imm,21)) & 0xffffffff
flag_offsets=(0xc264,0xc264,0xc264,0xc264,0xc264,0xc26c,0xc268,0xc26c,0xc264,
              0xc260,0xc264,0xc264,0xc264,0xc264,0xc264,0xc264,0xc268,0xc268)
for number,((ident,version,length,*_),setter_pc,expected,flag_offset) in enumerate(zip(cases,setter_pcs,expected_transfers,flag_offsets)):
    path=folder / ('ID-'+ident+'-V'+version+'-decoded.bin')
    actual=[]
    with path.open('rb') as f:
        for lo,hi in ((base,0x14056),(0x14c8a,0x1a69c),(0x1a6a0,base+length)):
            data=read_window(f,lo,hi-lo)
            for offset in range(0,len(data)-1,2):
                if transfer_target(data[offset:offset+4],lo+offset)==setter_pc:
                    actual.append(lo+offset)
        if tuple(actual)!=expected: raise SystemExit('Mode transfer candidates changed: '+ident)
        for index,back,value in ((0,4,3),(2,4,5),(3,2,3),(4,2,3)):
            # Compressed LI a0, 3 or 5 immediately preceding the transfer sequence.
            if read_window(f,expected[index]-back,2)!=bytes((0x0d if value==3 else 0x15,0x45)):
                raise SystemExit('Mode constant candidate changed: '+ident)
        prefixes=((0,8,'014685450d454101'),(2,8,'0546a94515454101'),
                  (3,6,'0546bd450d45'),(4,6,'014685450d45'))
        for index,back,hex_bytes in prefixes:
            if read_window(f,expected[index]-back,back)!=bytes.fromhex(hex_bytes):
                raise SystemExit('Mode three-argument prefix changed: '+ident)
        # Two branch encodings have different backward targets but the same fall-through.
        branch='c5d7' if ident in ('2389','2410','2527','2581','2590','2601','2603','2613','2816','2833','2841') else 'd5d7'
        suffix=bytes.fromhex('a183858b0d458945'+branch+'0146')
        if read_window(f,expected[1]-12,12)!=suffix:
            raise SystemExit('Second mode transfer prefix changed: '+ident)
        flag=pcrel_target(expected[1]-20,read_window(f,expected[1]-20,8),0x797,0x7d783)
        if flag!=0x20000000+flag_offset or not (0x20004000+(136 if number<8 else 128)<=flag and flag+2<=0x20000000+ends[number]):
            raise SystemExit('Second mode flag target or reset coverage changed: '+ident)
# V4.1.60 record helper: preserve the original window and independently decode its base.
with reference.open('rb') as f:
    record_helper=read_window(f,0x82a8,0x2c)
if hashlib.sha256(record_helper).hexdigest()!='ccc429b7070700aac8d5f1cbb6a1777b201f4284ce1aba424673bd30c5d728d0':
    raise SystemExit('Record helper window changed')
record_base=pcrel_target(0x82b6,record_helper[14:22],0x797,0x78793)
if record_base!=0x2000c1b8 or record_base+14*12+8!=0x2000c268 or record_base+14*12+9!=0x2000c269:
    raise SystemExit('Record 14 and mode flag relationship changed')
expected_record_transfers=(0xb600,0xc7d0,0xc838,0xd7e2,0xed7e,0xedfc,0xf4da,0xf584,0xfd48,0xfdcc,
                           0x14e6c,0x14ff2,0x1506e,0x150a2,0x15166,0x151bc,0x15204,0x15234,
                           0x152c0,0x17d10,0x17e20,0x1827a,0x1836a,0x184c6)
record_transfers=[]
with reference.open('rb') as f:
    for lo,hi in ((base,0x14056),(0x14c8a,0x1a69c),(0x1a6a0,0x1ac00)):
        data=read_window(f,lo,hi-lo)
        for offset in range(0,len(data)-1,2):
            if transfer_target(data[offset:offset+4],lo+offset)==0x82a8:
                record_transfers.append(lo+offset)
    if tuple(record_transfers)!=expected_record_transfers:
        raise SystemExit('Record helper direct-transfer candidates changed')
    for pc in record_transfers:
        before=read_window(f,pc-16,16)
        for offset in range(0,16,2):
            if before[offset:offset+2]==bytes.fromhex('b945') or before[offset:offset+4]==bytes.fromhex('9305e000'):
                raise SystemExit('Unexpected immediate index 14 candidate')
    variable=read_window(f,0x184aa,0x20)
    if hashlib.sha256(variable).hexdigest()!='5b161d1ecef63029d38139262560b8c6664628b6da15ebed116d119b568dd535':
        raise SystemExit('Variable record-index instruction window changed')
print('18 candidate data/consumers, reset bounds, mode setter and direct-transfer encodings verified. Excluded regions not read; target not executed.')
