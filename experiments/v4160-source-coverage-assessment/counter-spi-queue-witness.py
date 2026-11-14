#!/usr/bin/env python3
"""Conditional SPI header to queue record, not a device reachability proof."""
import argparse,hashlib,importlib.util
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
BIN='firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
SHA='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
def need(v,msg):
    if not v: raise ValueError(msg)
def load(filename,name):
    s=importlib.util.spec_from_file_location(name,Path(__file__).with_name(filename));m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,default=ROOT);image=(ap.parse_args().root/BIN).read_bytes()
    need(len(image)==76800 and hashlib.sha256(image).hexdigest()==SHA,'APP identity')
    # Independently pin exact original instructions through the call and queue writes.
    windows=((0x16acc,'8347110113f787010de7034641019d463d8a1307f6ff1377f70f63ece600034501019583a6860e05930551015d8defc0ef8c'),(0x12bf6,'2310a4002301c400'),(0x12c0e,'a3059400'))
    for pc,h in windows:
        b=bytes.fromhex(h);need(image[pc-0x8000:pc-0x8000+len(b)]==b,f'original bytes {pc:x}')
    check=load('counter-input-checksum-witness.py','check'); gate=load('counter-input-conditions.py','inp')
    headers=[]
    for a in range(256):
        for b in range(256):
            if not b&24 and ((a<<3)|(b>>5))==0x370:headers.append((a,b))
    need(headers==[(0x6e,i) for i in range(8)],'header classification')
    count=0
    for packed in range(1961,2140):
        for checksum in range(256):
            record=bytearray(12);record[0:3]=bytes((0x70,3,8));record[5]=packed>>8;record[6]=packed&255;record[9]=0x40;record[10]=checksum
            record[3]=(checksum-check.checksum(record))&255
            spi=bytes((0x6e,0,0,0,8))+record[3:11]
            need(len(spi)==13 and (spi[4]&15)==8,'SPI frame')
            slot=bytearray(12);slot[0:2]=((spi[0]<<3)|(spi[1]>>5)).to_bytes(2,'little');slot[2]=spi[4]&15;slot[3:11]=spi[5:13];slot[11]=0
            need(slot==record and check.checksum(slot)==slot[10] and gate.input_gate(slot[9],slot[11],0),'queue witness')
            count+=1
    print(f'PASS: 65536 SPI header pairs; 8 match ID 0x370; {count} synthetic frames reproduce queue checksum/input witnesses')
    print('LIMIT: assumed channel 0, successful stable SPI bytes, available slot, forward copy and preserved registers; consumer guards, provider, interrupts and physical reachability unverified')
if __name__=='__main__':main()
