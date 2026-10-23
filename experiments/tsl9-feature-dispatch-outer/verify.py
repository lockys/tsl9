#!/usr/bin/env python3
"""Read-only replay and memory-only malformed-object controls; no ISA execution."""
import argparse
import hashlib
import json
from pathlib import Path
import runpy
import struct
import sys

sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
BUILDER_SHA='d8058bf49e092c9e7e8f9e29b25b167e885ce6422b510da5f7e71a03be37204d'
SPEC_SHA='68bccb73e2e38672b8171e58ffc512a0a90b0c6f6f9f2bc068179ba5e4436392'
SOURCE_SHA='bc94efda3e290fd63b65b1df058e5af59065529e9d3e19d79b6a929b96fc29f3'
OBJECT_SHA='626c4030b98de7e23fe1e4f0a770889bdde87e75884130a443973c0c79a36c7e'
RECEIPTS={'c':'eeef5a5918195bae650ab1a9bab3e77df81309f85980c96331a3a9c700b62653',
          'cpp':'de8b8020a3af940d2b96605e6a84535b42c1b43be0d207c2ba1bcaa022fbbb33'}


def need(ok,msg):
    if not ok: raise ValueError(msg)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


need(sha(HERE/'build.py')==BUILDER_SHA and sha(HERE/'spec.json')==SPEC_SHA,'Frozen builder and spec')
B=runpy.run_path(str(HERE/'build.py'))
S=B['S']
need(sha(ROOT/S['reader'])==S['reader_sha256'],'Pinned actual ELF reader')
E=runpy.run_path(str(ROOT/S['reader']))['ELF']


def gate(raw,fw):
    result=B['facts'](raw,fw)
    e=E(raw)
    masks={16:0x01fff07f,17:0x00000fff,23:0x00000fff,24:0x000fffff}
    for r in e.relocations:
        if r['type'] in masks:
            sec=e.sections[r['section']]
            v=int.from_bytes(e.data(sec)[r['offset']:r['offset']+4],'little')
            need(v & (~masks[r['type']]&0xffffffff)==0,'Canonical zero symbolic displacement')
    for s in e.symbols:
        if s['name'] and s['section']==0:
            need((s['info'],s['other'],s['value'],s['size'])==(16,0,0,0),'True canonical UND provider')
    return result


def rejected(raw,fw):
    try: gate(raw,fw)
    except (ValueError,KeyError,IndexError,struct.error): return True
    return False


def negatives(e,fw):
    count=0
    # Every actual code/table byte, including symbolic placeholders.
    for sec in e.sections:
        if not (sec['flags']&2 and sec['size']): continue
        for i in range(sec['size']):
            b=bytearray(e.raw); b[sec['offset']+i]^=1
            need(rejected(bytes(b),fw),'Altered allocated byte rejected'); count+=1
    for sec in e.sections:
        if sec['type']!=4: continue
        for i in range(sec['size']//12):
            at=sec['offset']+12*i
            for field,value in [(0,struct.unpack_from('<I',e.raw,at)[0]+1),(4,0),(8,1)]:
                b=bytearray(e.raw); struct.pack_into('<I',b,at+field,value)
                need(rejected(bytes(b),fw),'Altered relocation offset/identity/addend rejected'); count+=1
        b=bytearray(e.raw)
        struct.pack_into('<I',b,e.header[5]+40*sec['index']+20,0)
        owner=e.sections[sec['info']]
        funcs=[f for f in e.symbols if f['info']&15==2 and f['section']==owner['index']]
        if funcs:
            n=funcs[0]['name']; va=next(a for name,a,z in S['definitions'] if name==n)
            b[owner['offset']:owner['offset']+owner['size']]=fw[va-0x8000:va-0x8000+owner['size']]
        need(rejected(bytes(b),fw),'Missing RELA with restored original owner bytes rejected'); count+=1
    symtab=next(s for s in e.sections if s['type']==2)
    for f in [f for f in e.symbols if f['info']&15==2]:
        at=symtab['offset']+16*f['index']
        for offset,fmt,val in [(8,'<I',0),(12,'<B',17),(13,'<B',2),(14,'<H',0)]:
            b=bytearray(e.raw); struct.pack_into(fmt,b,at+offset,val)
            need(rejected(bytes(b),fw),'Altered FUNC extent/type/visibility/owner rejected'); count+=1
    return count


def verify():
    for k in ('firmware','listing','reader','profile_source'):
        need(sha(ROOT/S[k])==S[k+'_sha256'],'Pinned '+k)
    source=HERE/'src/outer.v2.c'
    need(sha(source)==SOURCE_SHA,'Frozen readable C source')
    fw=(ROOT/S['firmware']).read_bytes()
    results=[]
    for mode in ('c','cpp'):
        folder=HERE/'build/trial-v2'/mode
        need(sha(folder/'receipt.json')==RECEIPTS[mode],'Actual original compile receipt')
        receipt=json.loads((folder/'receipt.json').read_bytes())
        need(receipt['source_sha256']==SOURCE_SHA and receipt['builder_sha256']==BUILDER_SHA and receipt['spec_sha256']==SPEC_SHA and receipt['passed'],'Bound source/producer/spec/pass')
        for name,record in receipt['artifacts'].items():
            need(sha(folder/name)==record['sha256'] and (folder/name).stat().st_size==record['bytes'],'Actual artifact '+name)
        need(sha(folder/'unit.o')==OBJECT_SHA,'Actual C/C++ object')
        data=(folder/'unit.o').read_bytes()
        facts=gate(data,fw)
        need(json.loads(B['encoded'](facts))==receipt['facts'],'Exact static-fact replay')
        count=negatives(E(data),fw)
        results.append(dict(mode=mode,passed=True,negative_controls=count,object_sha256=OBJECT_SHA))
    return dict(schema='TSL9-outer-static-verification-v1',passed=True,source_sha256=SOURCE_SHA,builder_sha256=BUILDER_SHA,spec_sha256=SPEC_SHA,checker_sha256=sha(Path(__file__)),results=results,
                code_bytes=294,table_bytes=28,FUNC=21,RELA=41,direct_control_sites=25,table_PC_relative_ports=2,table_ADD_SUB_pairs=7,
                linked=False,unresolved_providers=13,target_executed=False,HOST_model_executed=False,ISA_emulated=False,network=False,hardware_accessed=False,firmware_ready=False,
                limits=['Private architecture regions with then-live S0/SP/RA ports; not ordinary C ABI.',
                        'Five S0-based lhu instructions are explicit architectural memory ports after actual reserved-SP compiler rejection.',
                        'Mode1/common return and eleven final tail providers remain unresolved; no fabricated ABS providers.',
                        'Getter reads byte at nominal0x2000BFB5; memory identity/validity and real vehicle effects unproved.',
                        'Static relocation matching is not an executable/flashable firmware or universal C semantic proof.'])


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path)
    a=p.parse_args(); result=verify()
    if a.output:
        dest=a.output.resolve()
        need(dest.is_relative_to(HERE) and not dest.exists(),'Create-only bounded verification receipt')
        dest.write_bytes(B['encoded'](result))
    print(json.dumps(result))
