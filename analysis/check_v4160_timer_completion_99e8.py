"""Bounded APP code/operand checks, no hardware access. Run from repo root."""
from hashlib import sha256
from pathlib import Path

b = Path('firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin').read_bytes()
def need(ok, label):
    if not ok: raise ValueError(label)
def raw(pc,n): return b[pc-0x8000:pc-0x8000+n]
def w(pc): return int.from_bytes(raw(pc,4),'little')
def pin(pc,text):
    s=bytes.fromhex(text); need(raw(pc,len(s))==s,hex(pc))
def call(pc):
    v=w(pc); need(v&4095==239,hex(pc)); return pc-(v>>31)*1048576+((v>>12&255)<<12)+((v>>20&1)<<11)+((v>>21&1023)<<1)
need(sha256(b).hexdigest()=='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667','identity')
pin(0x9942,'17270020 23230758 0145 8297'); pin(0x99e8,'4111 8545 37050002 06c6'); pin(0x99f6,'8145 37050002'); pin(0x9a00,'0545'); pin(0x9a06,'0945')
need([call(p) for p in (0x99f2,0x99fc,0x9a02,0x9a08)]==[0x1917e]*2+[0x16e0c]*2,'ordered calls')
pin(0x1917e,'99c5 37170240 1c4b 5d8d 08cb 8280 b7170240 984b 1345f5ff 798d 88cb 8280')
pin(0x16e52,'8944 93090008'); pin(0x16e5c,'33052541 63faa400 0545'); pin(0x16e74,'b945 2285'); need(call(0x16e78)==0x16994,'sample'); pin(0x16e7c,'1375050e e31c35fd 0145 c5b7')
pin(0x9a0c,'93078008 73b00780 b707efbe 37e700e0 93870708 3cc7 01a0')
# Decode compact SW and the constants it consumes.
h=int.from_bytes(raw(0x9a20,2),'little'); need((h&0xe003,8+(h>>7&7),8+(h>>2&7))==(0xc000,14,15),'C.SW')
off=((h>>10&7)<<3)|((h>>6&1)<<2)|((h>>5&1)<<6)
need(((w(0x9a18)&0xfffff000)+off,(w(0x9a14)&0xfffff000)+(w(0x9a1c)>>20))==(0xe000e048,0xbeef0080),'terminal store')
print('PASS: IRQ handoff, four ordered calls, polling exits, CSR/store operands and terminal self-jump')
