"""Check the bounded TX loop CFG and body encodings; do not execute target."""
from pathlib import Path
import json

root=Path(__file__).resolve().parents[2]
paths=(root/'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin',
       root/'artifacts/offline-images/ID2966-V4.1.60-tx-integrated/NOT-FLASH-VALIDATED-tx-integrated.bin')
base,end=0x8b0a,0x8b6c
def read(path):
    if path.stat().st_size!=76800: raise ValueError('unexpected image size')
    with path.open('rb') as stream:
        stream.seek(base-0x8000)
        data=stream.read(end-base)
    if len(data)!=end-base: raise ValueError('short window')
    return data
def branch(raw,pc):
    w=int.from_bytes(raw,'little')
    if w&0x7f!=0x63: raise ValueError('not branch')
    imm=((w>>31)&1)<<12|((w>>7)&1)<<11|((w>>25)&63)<<5|((w>>8)&15)<<1
    if imm&0x1000: imm-=0x2000
    return ((w>>12)&7,(w>>15)&31,(w>>20)&31,pc+imm)
def cjump(raw,pc):
    w=int.from_bytes(raw,'little')
    if (w&3)!=1 or (w>>13)!=5: raise ValueError('not c.j')
    imm=((w>>12)&1)<<11|((w>>11)&1)<<4|((w>>9)&3)<<8|((w>>8)&1)<<10|((w>>7)&1)<<6|((w>>6)&1)<<7|((w>>3)&7)<<1|((w>>2)&1)<<5
    if imm&0x800: imm-=0x1000
    return pc+imm
a,b=map(read,paths)
def at(data,addr,size): return data[addr-base:addr-base+size]
if at(a,0x8b0a,6)!=bytes.fromhex('139505014181') or at(b,0x8b0a,6)!=at(a,0x8b0a,6):
    raise ValueError('index truncation changed')
if branch(at(a,0x8b10,4),0x8b10)!=(6,10,8,0x8b52):
    raise ValueError('original unsigned branch changed')
if branch(at(b,0x8b10,4),0x8b10)!=(7,10,8,0x8b2e):
    raise ValueError('candidate unsigned branch changed')
old=at(a,0x8b52,26);new=at(b,0x8b14,26)
if old[:8]!=new[:8] or old[12:24]!=new[12:24]:
    raise ValueError('loop body order changed')
if old[8:12]!=bytes.fromhex('3388b700') or new[8:12]!=bytes.fromhex('3388f500'):
    raise ValueError('commutative address-add encoding changed')
if cjump(old[24:26],0x8b6a)!=0x8b0a or cjump(new[24:26],0x8b2c)!=0x8b0a:
    raise ValueError('loop back-edge changed')
print(json.dumps({'original_body':'0x8b52','candidate_body':'0x8b14',
 'original_finish':'0x8b14','candidate_finish':'0x8b2e','common_backedge':'0x8b0a',
 'body_difference':'address-add source operands reversed','comparison':'unsigned complementary branches',
 'scope':'local normal loop; inputs, memory, alternate entry and later code unverified',
 'excluded_app_read':False,'target_executed':False}))
