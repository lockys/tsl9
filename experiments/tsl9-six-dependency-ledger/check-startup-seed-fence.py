"""Pin candidate seed-copy and first RAM-helper call windows; do not execute them."""
import hashlib
from pathlib import Path

root = Path(__file__).resolve().parents[2]
image = root / 'analysis/wch-resident-candidate-2026-10-21/carrier-dec2023/REFERENCE-CANDIDATE-ONLY-00040000-0006EA66.bin'
source = root / 'experiments/tsl9-resident-slot2-startup/resident_slot2_startup.c'
if hashlib.sha256(source.read_bytes()).hexdigest() != 'c003ee916a75750c99289f98592e8df74d2fe47d6d22650c99954dd1f5d4c37a':
    raise SystemExit('Candidate annotated startup source changed')
windows = ((0x6de7e,0x44,'98fe32a0b24638e9f678c2112dbae4fa05ad6e45d2a9fb84bedb67c3831880b0'),
           (0x6de0c,0x46,'0c73bc66988cfdf20e82fa7bb732df5195b596cf195629e15704299fadada263'),
           (0x40280,0x30,'1b443f8c3926fac2d65fda618f0ead0c9d2f50cafe5b0ff9c72eb030c13fd5a8'))
with image.open('rb') as f:
    for address,size,expected in windows:
        f.seek(address-0x40000)
        data=f.read(size)
        if hashlib.sha256(data).hexdigest()!=expected:
            raise SystemExit('Candidate startup window changed')
        if address == 0x40280:
            continue
        pos=0
        while pos<len(data):
            n=4 if data[pos]&3==3 else 2
            if pos+n>len(data):
                raise SystemExit('Truncated instruction')
            if n==4 and data[pos:pos+4]==bytes.fromhex('0f100000'):
                raise SystemExit('Unexpected FENCE.I in startup window')
            pos+=n
if 0x20000040-0x20000010 != 48 or 0x402b0-0x40280 != 48:
    raise SystemExit('Seed copy range changed')
v140 = root / 'analysis/wch-resident-candidate-2026-10-21/original/wchble_rom.hex'
raw = v140.read_bytes()
if hashlib.sha256(raw).hexdigest() != '5a4331c80f71dda3fc28e13481e185bda6877d8be7977cbfa0238c2f0baadf23':
    raise SystemExit('V1.40 HEX changed')
selected = ((0x40000,4,'4dd31e5bdf6aebe918c1bd4fc24413aab164164e22edabf933190a1d9e6e8804'),
            (0x6e06e,0x44,'be10a8a9345b43c9581cade65059b0aa39b9e6cf46953b5179b7cd909aaa926c'),
            (0x6dffc,0x46,'e9cc946e02171437be8bb15015329891a33036905bff49afb457f9ec1634b9b8'),
            (0x402c0,0x30,'d72cd5c9c489436d5ee4d42aa49a24683766d546beb7cd3d3be6adfb07592950'))
wanted = {x for address,size,_ in selected for x in range(address,address+size)}
found = {}
upper = 0
eof = False
for line in raw.splitlines():
    if eof or not line.startswith(b':'):
        raise SystemExit('Invalid HEX record order')
    rec=bytes.fromhex(line[1:].decode('ascii'))
    if len(rec)<5 or len(rec)!=rec[0]+5 or sum(rec)&255:
        raise SystemExit('Invalid HEX record')
    size,address,kind=rec[0],int.from_bytes(rec[1:3],'big'),rec[3]
    payload=rec[4:4+size]
    if kind in (2,4):
        if size!=2:
            raise SystemExit('Invalid HEX address')
        upper=int.from_bytes(payload,'big')<<(4 if kind==2 else 16)
    elif kind==0:
        for i,value in enumerate(payload):
            absolute=upper+address+i
            if absolute in wanted:
                if absolute in found:
                    raise SystemExit('Overlapping HEX record')
                found[absolute]=value
    elif kind==1:
        if size:
            raise SystemExit('Invalid HEX EOF')
        eof=True
    elif kind not in (3,5):
        raise SystemExit('Unsupported HEX record')
if not eof or set(found)!=wanted:
    raise SystemExit('Incomplete V1.40 candidate windows')
for address,size,expected in selected:
    data=bytes(found[x] for x in range(address,address+size))
    if hashlib.sha256(data).hexdigest()!=expected:
        raise SystemExit('V1.40 candidate window changed')
    if address not in (0x6e06e,0x6dffc):
        continue
    pos=0
    while pos<len(data):
        n=4 if data[pos]&3==3 else 2
        if pos+n>len(data):
            raise SystemExit('Truncated V1.40 instruction')
        if n==4 and data[pos:pos+4]==bytes.fromhex('0f100000'):
            raise SystemExit('Unexpected V1.40 FENCE.I in startup window')
        pos+=n
with image.open('rb') as f:
    f.seek(0x40280-0x40000)
    v131_helper=f.read(18)
if v131_helper!=bytes(found[x] for x in range(0x402c0,0x402d2)):
    raise SystemExit('Candidate word-copy helper instructions differ')
print('Candidate seed and first RAM-helper windows verified; target not executed.')
