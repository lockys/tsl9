"""Check selected APP producers of the timer's sequence-end delay, not runtime order."""
from hashlib import sha256
from pathlib import Path

b = Path('firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin').read_bytes()
def need(ok, label):
    if not ok: raise ValueError(label)
def word(pc): return int.from_bytes(b[pc-0x8000:pc-0x8000+4], 'little')
def pin(pc, h):
    s=bytes.fromhex(h); need(b[pc-0x8000:pc-0x8000+len(s)]==s,hex(pc))
def pair(pc):
    hi,lo=word(pc),word(pc+4); rd=hi>>7&31
    need(hi&127==23 and lo&0x707f==19 and rd==lo>>15&31 and rd==lo>>7&31,hex(pc))
    return (pc+(hi&0xfffff000)+(lo>>20)-(lo>>31<<12))&0xffffffff
need(sha256(b).hexdigest()=='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667','identity')
need(pair(0x94ee)==pair(0x9966)==0x2000bebc,'shared state')
pin(0x94f6,'0547 2a83 2382e700 2394c700 ccc7 0145 0283'); pin(0x9958,'b7070400 bc47 4111 06c6 5146 8145'); pin(0x996e,'8297')
need([pair(p) for p in (0xeaf2,0xeafa,0x13ffe,0x14a28)]==[0x99e8,0x954e,0x9508,0x9508],'wrapper operands')
pin(0xeaee,'13064006'); pin(0x13ffa,'0546 8145'); pin(0x14a24,'0546 8145')
for pc,rd in [(0xeb02,1),(0x14008,0),(0x14a30,1)]:
    w=word(pc); d=-(w>>31)*1048576+((w>>12&255)<<12)+((w>>20&1)<<11)+((w>>21&1023)<<1)
    need(w&4095==rd<<7|111 and pc+d==0x94ee,hex(pc))
for pc in (0x9902,0x9910):
    hi,lo=word(pc),word(pc+4); need(hi&4095==0x797 and lo&0xfffff==0x7d783 and pc+(hi&0xfffff000)+(lo>>20)==0x2000bec4,hex(pc))
pin(0x990a,'8dc3'); pin(0x9918,'3e95'); pin(0x9922,'97270020 2391075a 8db7'); pin(0x992c,'c934'); pin(0x993a,'553c 8327c900 99c7')
print('PASS: init and wrapper share base; three call/tail operands; both end-delay loads target 0x2000bec4')
