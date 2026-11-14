#!/usr/bin/env python3
"""Bounded projection from 0xa114 to the counter lookup or its two exits."""
import argparse,hashlib,importlib.util
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
BIN='firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
SHA='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
CODE=bytes.fromhex('a2470347a100a183bd8ba207d98f93877785c207c1831307200b636df70aefe0cf8b05479307807a6306e5028947630df50a')
def need(ok,msg):
    if not ok:raise ValueError(msg)
def branch(pc,w):
    need(w&127==0x63,'opcode');v=((w>>31)&1)<<12|((w>>7)&1)<<11|((w>>25)&63)<<5|((w>>8)&15)<<1
    return (pc+(v-8192 if v&4096 else v))&0xffffffff
def jal(pc,w):
    need(w&127==0x6f,'jal opcode');v=((w>>31)&1)<<20|((w>>12)&255)<<12|((w>>20)&1)<<11|((w>>21)&1023)<<1
    return (pc+(v-(1<<21) if v&(1<<20) else v))&0xffffffff
def project(word8,byte10,result):
    x=(((word8>>8)&15)<<8)|byte10
    if ((x-1961)&0xffff)>178:return (0xa1e8,None)
    if result==1:return (0xa168,1960)
    if result==2:return (0xa1fc,None)
    return (0xa146,None)
def main():
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=ROOT);root=p.parse_args().root
    b=(root/BIN).read_bytes();need(len(b)==76800 and hashlib.sha256(b).hexdigest()==SHA,'APP identity')
    need(b[0xa114-0x8000:0xa146-0x8000]==CODE,'original code')
    for pc,target in ((0xa12e,0xa1e8),(0xa13c,0xa168),(0xa142,0xa1fc)):
        need(branch(pc,int.from_bytes(b[pc-0x8000:pc-0x8000+4],'little'))==target,'branch target')
    need(jal(0xa132,int.from_bytes(b[0xa132-0x8000:0xa136-0x8000],'little'))==0x81ee,'call target')
    reached=0
    for value in range(4096):
        word=((value>>8)&15)<<8;byte=value&255
        for result in (0,1,2,3,0xffffffff):
            pc,_=project(word,byte,result)
            expected=0xa1e8 if not 1961<=value<=2139 else (0xa168 if result==1 else 0xa1fc if result==2 else 0xa146)
            need(pc==expected,'projection mismatch');reached+=pc==0xa146
    need(reached==179*3,'count')
    spec=importlib.util.spec_from_file_location('counter_bypass',Path(__file__).with_name('counter-writer-bypass.py'))
    bypass=importlib.util.module_from_spec(spec);spec.loader.exec_module(bypass)
    for old,aux in ((1,0),(0,1)):
        pc,counter,wrote=bypass.projection(old,old,255,aux)
        need((pc,counter,wrote)==(0xa114,255,False),'bypass witness')
        need(project(0x700,0xa9,0)[0]==0xa146,'lookup witness')
    print(f'PASS: 20480 synthetic cases; {reached} reach lookup for selected callee results; range 1961..2139 inclusive')
    print('PASS: two synthetic bypass-to-lookup boundary compositions preserve counter 255, assuming no intervening writes')
    print('LIMIT: successful stack reads, no asynchronous change, normal stubbed 0x81ee return; earlier path and callee effects are not executed; not device evidence')
if __name__=='__main__':main()
