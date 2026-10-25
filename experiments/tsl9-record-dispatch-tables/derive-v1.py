#!/usr/bin/env python3
"""Derive typed relative table references and a bounded byte lookup; no target execution."""
from pathlib import Path
import argparse,hashlib,json,runpy,struct
ROOT=Path(__file__).resolve().parents[2]
EVIDENCE=ROOT/'analysis/record-dispatch-tables-2026-10-25/evidence.json'
def need(ok,label):
    if not ok:raise ValueError(label)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def generate():
    e=json.loads(EVIDENCE.read_bytes());fw=(ROOT/e['firmware']).read_bytes();need(sha(ROOT/e['firmware'])==e['firmware_sha256'],'Original firmware identity')
    need(sha(ROOT/e['source_operations'])==e['source_operations_sha256']and sha(ROOT/e['parent_component'])==e['parent_component_sha256'],'Original operations and real code owners unchanged')
    parser=ROOT/'experiments/tsl9-feature-dispatch-tree/elf_reader-v5.py';need(sha(parser)=='a56503572e8b65308ae1c8978ba5a6d44d0a20cd969315dc1b12103b59a9b43a','Pinned reader')
    parent=runpy.run_path(str(parser))['ELF'](ROOT/e['parent_component']);gm={v['name']:v for v in parent.symbols if v['info']>>4};objects=[];lines=['#include <stdint.h>','/* RV32 relative jump-table DATA with real code-label relocations.',' * No executable function or handler stub is defined here.',' * Original declared object extents and physical behavior remain unproved. */','']
    for t in e['tables']:
        raw=fw[t['start']-0x8000:t['end']-0x8000];need(len(raw)==t['bytes']==4*len(t['entries'])and hashlib.sha256(raw).hexdigest()==t['original_sha256'],'Whole bounded original table')
        ops={v['addr']:v for v in t['operations']}
        for pc,o in ops.items():need(bytes.fromhex(o['bytes'])==fw[pc-0x8000:pc-0x8000+o['size']],'Original guard and lookup bytes')
        g=t['guard'];word=int.from_bytes(bytes.fromhex(ops[g['guard_PC']]['bytes']),'little')
        need(word&0x707f==0x6063 and(word>>15)&31==g['bound_register']and(word>>20)&31==15,'Unsigned bound-register versus index guard')
        op=ops[g['limit_PC']];w=int.from_bytes(bytes.fromhex(op['bytes']),'little')
        need(op['size']==2 and w&0xe003==0x4001 and(w>>7)&31==g['bound_register']and(((w>>12)&1)<<5|((w>>2)&31))==len(t['entries'])-1,'Actual maximum immediate determines table count')
        o=ops[g['mask_PC']];w=int.from_bytes(bytes.fromhex(o['bytes']),'little')
        need(o['size']==4 and w&0x707f==0x7013 and(w>>7)&31==(w>>15)&31==15 and w>>20==255,'Actual byte-normalized index')
        name=t['name'];lines+=['#if defined(__cplusplus)','extern "C" {',f'extern const int32_t {name}[{len(t["entries"])}];','}','#else',f'extern const int32_t {name}[{len(t["entries"])}];','#endif']
        asm=f'.pushsection {t["section"]},"a",@progbits\n.p2align 2\n.globl {name}\n.type {name},@object\n{name}:\n'
        for row in t['entries']:
            at=4*row['index'];offset=struct.unpack_from('<i',raw,at)[0];need(offset==row['original_signed_offset']and t['start']+offset==row['target_PC'],'Actual original relative target')
            v=gm[row['target_symbol']];need(v['info']==18 and v['size']>0 and v['section']not in(0,0xfff1)and int(v['name'].rsplit('_',1)[1],16)==row['target_PC'],'Real nonempty existing code owner at target')
            asm+='\n'.join(['.word 0','.reloc .-4,R_RISCV_ADD32,'+v['name'],'.reloc .-4,R_RISCV_SUB32,'+name])+'\n'
        asm+=f'.size {name},.-{name}\n.popsection\n';lines.append('__asm__('+json.dumps(asm)+');');lines.append('');objects.append(dict(t,kind='relative-offset-table'))
    d=e['lookup'];raw=fw[d['start']-0x8000:d['end']-0x8000];need(len(raw)==8 and raw.hex()==d['raw_hex']and hashlib.sha256(raw).hexdigest()==d['original_sha256'],'Original eight-byte lookup window')
    ops={o['addr']:o for o in d['operations']}
    for pc,o in ops.items():need(bytes.fromhex(o['bytes'])==fw[pc-0x8000:pc-0x8000+o['size']],'Original byte-load/shift lookup sequence')
    need(ops[d['load_PC']]['opcode']=='lbu a4, 0(a2)'and ops[d['shift_PC']]['opcode']=='srli a3, a4, 0x5'and d['index_maximum']==7,'Unsigned byte right shift five gives index0..7')
    lines+=['#if defined(__cplusplus)','#define LOOKUP_DATA extern "C" __attribute__((used,aligned(1),section("'+d['section']+'")))','#else','#define LOOKUP_DATA __attribute__((used,aligned(1),section("'+d['section']+'")))','#endif','LOOKUP_DATA const uint8_t '+d['name']+'[8] = {'+', '.join('0x'+format(v,'02x')for v in raw)+'};',''];objects.append(dict(d,kind='bounded-byte-lookup'))
    need(len(objects)==5 and sum(v['bytes']for v in objects)==264 and sum(len(v.get('entries',[]))for v in objects)==64,'Five genuine DATA objects and64 typed relative slots')
    return dict(source='\n'.join(lines),objects=objects,undefined=sorted({r['target_symbol']for t in e['tables']for r in t['entries']}))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--counts',action='store_true');a=p.parse_args();g=generate();print(json.dumps(dict(objects=len(g['objects']),data_bytes=264,relative_entries=64,undefined=len(g['undefined']),source_chars=len(g['source']))if a.counts else g))
