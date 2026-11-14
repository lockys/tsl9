#!/usr/bin/env python3
"""Conditionally compose f7 zero-object path with reference allocator entry."""
import argparse
import hashlib
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import case_f7_composition as gate
import case_f7_zero_provider as zero
import reference_alloc_slot as alloc


def need(ok,msg):
    if not ok: raise ValueError(msg)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--root',type=Path,default=alloc.ROOT)
    root=parser.parse_args().root
    app=gate.prefix.BIN.read_bytes()
    need(len(app)==76800 and hashlib.sha256(app).hexdigest()=='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667','APP identity')
    gate.prefix.check(app); gate.dispatch.check(app); zero.validate(app)
    for (path,digest,_,_),source in zip(alloc.CASES,alloc.SOURCES):
        p=root/path
        if not p.is_file(): raise SystemExit(f'SKIP: missing reference carrier {path}')
        alloc.check(p.read_bytes(),digest,source)
        n=0
        for status in range(256):
            for incoming in (0,1,0xf00c,0x2000c000,0xffffffff):
                first=gate.run(status,0,0,incoming)
                if status&8:
                    need(first==('return-to-167d8',incoming),'unexpected early return')
                    continue
                need(first==('pointer-zero',incoming),'unexpected object result')
                tail=zero.project(0,first[1],0x20000236)
                need(tail==('tail-40070',12,incoming,0x20000236),'unexpected resident tail')
                after=alloc.projection(tail[1],tail[2])
                need(after==('helper-20000040',20,0xf00c),'helper arguments changed')
                n+=1
        need(n==640,'wrong nonreturn count')
        print(f'PASS: {path}: {n} conditional compositions reach reference helper with (20, 0xf00c); 640 early returns')
    print('LIMIT: independent handwritten projections; candidate mapping, stable state, no alias/interruption and successful accesses assumed; no continuous execution, hardware or helper effect')


if __name__=='__main__':main()
