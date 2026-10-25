#!/usr/bin/env python3
"""Inspect compiled relative dispatch tables and guards offline; never execute firmware."""
from pathlib import Path
from collections import Counter
import argparse,hashlib,json,runpy,sys
ROOT=Path(__file__).resolve().parents[2]
SPEC='experiments/tsl9-record-dispatch-tables/spec-v1.json'
def need(ok,label):
    if not ok:raise ValueError(label)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def analyze(b,linked,plan,insns):
    need(sha(ROOT/SPEC)==b['K']['pins'][SPEC],'Pinned actual DATA specification')
    s=json.loads((ROOT/SPEC).read_bytes());need(sha(ROOT/s['reference_candidate'])==s['reference_candidate_sha256'],'Pinned original guard/table evidence')
    e=json.loads((ROOT/s['reference_candidate']).read_bytes());need(sha(ROOT/e['firmware'])==e['firmware_sha256'],'Original image identity')
    owners={v['name']:v for v in plan['owners']};gm={v['name']:v for v in linked.symbols if v['info']>>4}
    def data(d):
        o=owners[d['name']];v=gm[d['name']]
        need(o['info']==17 and o['original_PC']==d['start']and o['bytes']==d['bytes']and o['alignment']==d['alignment'],'Genuine aligned DATA owner')
        need(v['info']==17 and v['value']==d['start']and v['size']==d['bytes']and v['section']not in(0,0xfff1),'Actual original-address OBJECT')
        raw=linked.data(o['section'])[o['section_offset']:o['section_offset']+o['bytes']]
        need(hashlib.sha256(raw).hexdigest()==d['original_sha256'],'All actual original table/lookup bytes')
        return raw
    def pair(pc,target):
        need(insns[pc]['width']==insns[pc+4]['width']==4,'Whole actual address pair')
        a=int.from_bytes(insns[pc]['raw'],'little');c=int.from_bytes(insns[pc+4]['raw'],'little');imm=c>>20;imm-=4096 if imm&2048 else 0
        need(a&127==0x17 and c&0x707f==0x13 and(a>>7)&31==(c>>7)&31==(c>>15)&31,'Actual AUIPC/ADDI register chain')
        need((pc+(a&0xfffff000)+imm)&0xffffffff==target,'Compiled original address points to real DATA')
    tables=[]
    for d in e['tables']:
        raw=data(d);g=d['guard'];n=len(d['entries']);need(d['bytes']==n*4 and g['maximum']==n-1,'Bounded word-table extent')
        chain=d['operations'];need(all(o['addr']in insns and bytes.fromhex(o['bytes'])==insns[o['addr']]['raw']for o in chain),'Every actual guard/lookup/jump instruction matches original')
        need(not any(o['type']in('call','ucall')for o in chain),'No intervening opaque call before indirect dispatch')
        w=int.from_bytes(insns[g['guard_PC']]['raw'],'little');need(insns[g['guard_PC']]['width']==4 and w&0x707f==0x6063 and(w>>15)&31==g['bound_register']and(w>>20)&31==15,'Actual unsigned maximum-versus-index branch')
        w=int.from_bytes(insns[g['limit_PC']]['raw'],'little');need(insns[g['limit_PC']]['width']==2 and w&0xe003==0x4001 and(w>>7)&31==g['bound_register']and(((w>>12)&1)<<5|((w>>2)&31))==n-1,'Actual maximum immediate')
        w=int.from_bytes(insns[g['mask_PC']]['raw'],'little');need(insns[g['mask_PC']]['width']==4 and w&0x707f==0x7013 and(w>>7)&31==(w>>15)&31==15 and w>>20==255,'Actual unsigned-byte index normalization')
        pair(g['base_pair_PC'],d['start']);p=g['base_pair_PC'];base='a'+str(g['bound_register']-10);ops={v['addr']:v for v in chain}
        expected={p+8:'slli a5, a5, 0x2',p+10:'add a5, a5, '+base,p+12:'lw a5, 0(a5)',p+14:'add a5, a5, '+base,p+16:'jr a5'}
        need(all(ops[pc]['opcode']==text for pc,text in expected.items()),'Original stride4/load/relative-base/jump chain')
        w=int.from_bytes(insns[g['indirect_jump_PC']]['raw'],'little');need(insns[g['indirect_jump_PC']]['width']==2 and w&0xf07f==0x8002 and(w>>7)&31==15,'Actual register-indirect jump through A5')
        targets=[];names=[]
        for row in d['entries']:
            slot=d['start']+4*row['index'];target=(d['start']+int.from_bytes(raw[4*row['index']:4*row['index']+4],'little',signed=True))&0xffffffff
            need(target==row['target_PC']and target in insns and insns[target]['owner']==row['target_symbol'],'Each compiled relative offset reaches its real original instruction owner')
            v=gm[row['target_symbol']];need(v['info']==18 and v['size']>0 and v['value']==target and v['section']not in(0,0xfff1),'Actual genuine nonempty CODE destination')
            actual=Counter((r['type'],r['addend'],linked.symbols[r['symbol']]['name'])for r in linked.relocations if r['offset']==slot)
            need(actual==Counter([(35,0,row['target_symbol']),(39,0,d['name'])]),'Exact applied ADD32/SUB32 target/base pair')
            targets.append(target);names.append(row['target_symbol'])
        tables.append(dict(table_PC=d['start'],entries=n,table_bytes=d['bytes'],mask_PC=g['mask_PC'],guard_PC=g['guard_PC'],jump_PC=g['indirect_jump_PC'],guard_fallthrough_maximum=n-1,target_PCs=targets,target_symbols=names,compiled_guard_and_table_bytes_proved=True,typed_relative_target_roles_proved=True,no_intervening_opaque_call=True,runtime_index_or_target_observed=False,asynchronous_ABI_interference_excluded=False))
    d=e['lookup'];raw=data(d);need(len(raw)==8 and raw.hex()==d['raw_hex'],'All eight original field lookup values')
    need(all(v['addr']in insns and bytes.fromhex(v['bytes'])==insns[v['addr']]['raw']for v in d['operations']),'Every actual byte-load/shift/index instruction')
    a=int.from_bytes(insns[d['load_PC']]['raw'],'little');c=int.from_bytes(insns[d['shift_PC']]['raw'],'little')
    need(a&0x707f==0x4003 and(a>>7)&31==14 and(a>>15)&31==12 and a>>20==0,'Actual unsigned byte source load')
    need(c&0xfe00707f==0x5013 and(c>>7)&31==13 and(c>>15)&31==14 and(c>>20)&31==5,'Actual logical shift right five yields0..7')
    pair(d['base_pair_PC'],d['start'])
    lookup=dict(table_PC=d['start'],bytes=8,source_load_PC=d['load_PC'],shift_PC=d['shift_PC'],lookup_PC=d['lookup_PC'],index_expression='unsigned_byte >> 5',index_maximum=7,compiled_lookup_bytes_proved=True,runtime_index_observed=False,original_declared_object_extent_proved=False)
    need(len(tables)==4 and sum(v['entries']for v in tables)==64,'All four new guarded dispatch tables and64 destinations')
    return tables,lookup
def inspect(mode):
    b=runpy.run_path(str(ROOT/'experiments/tsl9-original-layout/build-v55.py'),run_name='positive_static_library');folder=ROOT/'experiments/tsl9-original-layout/build/record-dispatch-tables-v1';record=json.loads((folder/'measurement.json').read_bytes());path=folder/mode/'NONLOADABLE-ORIGINAL-LAYOUT.elf'
    need(sha(path)==record['modes'][mode]['result']['ELF_sha256'],'Measured layout ELF identity')
    need(sha(b['source'](mode))==b['K']['source_sha256']and sha(ROOT/b['K']['reader'])==b['K']['reader_sha256'],'Measured component and reader identities')
    source=b['E'](b['source'](mode));plan=b['derive'](source);b['validate_original'](source,plan);need(b['audit_link'](path,source,plan)['passed'],'All original-address code and DATA bytes')
    linked=b['E'](path);insns={}
    for owner in plan['owners']:
        if owner['info']!=18:continue
        raw=linked.data(owner['section'])[owner['section_offset']:owner['section_offset']+owner['bytes']];at=0
        while at<len(raw):
            width=4 if raw[at]&3==3 else 2;need(at+width<=len(raw),'Whole actual original instruction');pc=owner['original_PC']+at;insns[pc]=dict(PC=pc,width=width,raw=raw[at:at+width],owner=owner['name']);at+=width
    tables,lookup=analyze(b,linked,plan,insns)
    return dict(passed=True,language=mode,tables=tables,lookup=lookup,original_relative_entries=64,target_executed=False,hardware_accessed=False,network=False)
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--language',choices=['c','cpp'],default='c');p.add_argument('--json',action='store_true');p.add_argument('--full',action='store_true');a=p.parse_args()
    try:
        result=inspect(a.language)
        if not a.full:
            for table in result['tables']:table.pop('target_PCs');table.pop('target_symbols')
        print(json.dumps(result,indent=2 if a.json else None))
    except (ValueError,OSError)as error:
        message=str(error).replace(str(ROOT),'${PROJECT_ROOT}').replace(str(Path.home()),'${USERPROFILE}');print('FAIL: '+message,file=sys.stderr);sys.exit(1)
