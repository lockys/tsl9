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
print('18 candidate data matches; PC-relative consumer candidates: sequence 15, counter 10, mode 18. Excluded regions not read.')
