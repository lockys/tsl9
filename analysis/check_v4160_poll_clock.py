"""Check APP clock scaling and poll gate; no assumed wall-clock rate."""
from pathlib import Path
from hashlib import sha256

U=1<<32
b=Path('firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin').read_bytes()
def need(x,why):
    if not x: raise ValueError(why)
def pin(pc,h):
    s=bytes.fromhex(h); need(b[pc-0x8000:pc-0x8000+len(s)]==s,hex(pc))
def clock(r): return ((10*r)%U)>>4
def gap(base,now): return (clock(now)-clock(base))%U
need(sha256(b).hexdigest()=='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667','image')
pin(0x81b0,'b7070400 fc5f 4111 06c6 8297 a947 3305f502 b240 4101 1181 8280')
pin(0x16e4c,'ef104fb6 2a89 8944 93090008 ef108fb5 33052541 63faa400 0545')
# For any product p = low32(10*r), increasing raw by five adds 50.
# Enumerate all possible p mod 16 for the non-wrap case and all 50 tail values.
for p in [*range(16),*range(U-50,U)]:
    step=(((p+50)%U)>>4)-(p>>4)
    need(step%U>2,'five raw ticks')
# Cross-check full raw arithmetic around every product-wrap threshold, incl raw wrap.
for k in range(11):
    cut=(k*U+9)//10
    for r in range(cut-16,cut+17):
        need(gap(r,r)==gap(r,r+U//2)==0,'alias')
        need(gap(r,r+5)>2,'raw boundary')
need([gap(0,n) for n in range(6)]==[0,0,1,1,2,3],'threshold')
print('PASS: 66 product representatives; 363 raw boundary cases; +5 timeout and half-range alias')
