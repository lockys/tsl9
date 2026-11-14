#!/usr/bin/env python3
"""Project reference deallocator tag gate, stopping before unresolved RAM helper."""
import argparse
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import reference_free_slot as reference


def need(ok,message):
    if not ok: raise ValueError(message)


def project(pointer,tag,a1):
    if pointer==0: return ('null-return',5,a1)
    if tag!=255: return ('tag-return',4,a1)
    return ('helper-20000110',pointer,a1)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,default=reference.ROOT)
    root=parser.parse_args().root
    for path,digest,address,text in reference.CASES:
        file=root/path
        if not file.is_file(): raise SystemExit(f'SKIP: missing reference carrier {path}')
        data=file.read_bytes(); reference.check(data,digest,address,bytes.fromhex(text))
        counts={'tag-return':0,'helper-20000110':0}
        for tag in range(256):
            for low in range(256):
                incoming=0x12340000|low
                value=project(0x20001234,tag,incoming)
                counts[value[0]]+=1
                if tag==255:
                    need(value==('helper-20000110',0x20001234,incoming),'helper args')
                else:
                    need(value==('tag-return',4,incoming),'mismatch return')
        need(counts=={'tag-return':65280,'helper-20000110':256},'tag counts')
        for low in range(256):need(project(0,low,0x12345678)==('null-return',5,0x12345678),'null')
        print(f'PASS: {path}: 65536 nonzero-pointer projections {counts}; 256 null projections')
    print('LIMIT: hand projection based on pinned reference bytes; candidate mapping, access/order, no alias/trap/interruption assumed; no helper or hardware execution')


if __name__=='__main__': main()
