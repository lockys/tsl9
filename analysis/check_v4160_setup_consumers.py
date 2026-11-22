"""Check direct JAL sites and their returned-status decisions, not peripheral effects."""
from hashlib import sha256
from pathlib import Path

B = Path('firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin').read_bytes()

def need(ok):
    if not ok: raise ValueError('setup caller evidence mismatch')

def word(pc,n): return int.from_bytes(B[pc-32768:pc-32768+n],'little')
def sx(x,b): return (x^(1<<(b-1)))-(1<<(b-1))
def jal(pc):
    w=word(pc,4)
    if w&4095!=0xef: return None
    return pc+sx((w>>31)<<20|(w>>12&255)<<12|(w>>20&1)<<11|(w>>21&1023)<<1,21)

def after(pc,status):
    h=word(pc,2); need(h&0xe383==0xe101)  # C.BNEZ a0
    off=(h>>12&1)<<8|(h>>10&3)<<3|(h>>5&3)<<6|(h>>3&3)<<1|(h>>2&1)<<5
    return pc+(sx(off,9) if status else 2)

def pin(pc,hexbytes):
    s=bytes.fromhex(hexbytes); need(B[pc-32768:pc-32768+len(s)]==s)

if __name__=='__main__':
    need(sha256(B).hexdigest()=='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667')
    sites=[pc for pc in range(32768,32768+len(B)-3,2) if jal(pc)==0x16e88]
    need(sites==[0x16f38,0x16f6c,0x16f86,0x16f8e])
    for site,fail in zip(sites,[0x16f24,0x16f60,0x16fa4,0x16fa4]):
        for status in [0,1,255,0xffffffff]: need(after(site+4,status)==(fail if status else site+6))
    for pc,target in [(0x16f40,0x16dd4),(0x16f74,0x16dd4),(0x16f94,0x9af0),(0x16f9a,0x12b24)]: need(jal(pc)==target)
    pin(0x16f24,'13452400'); pin(0x16f60,'13454400'); pin(0x16f9e,'13451400 59b7')
    pin(0x16fa4,'b7070400 bc4f 13060003 8545 2685 8297 edb7')
    print('PASS: 4 direct JAL ra sites, 16 status decisions, 4 follow-up targets and common retry request')
