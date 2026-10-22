#!/usr/bin/env python3
"""Read-only candidate bytes and authored ET_REL review, no target execution."""
import argparse
import collections
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import runpy
import sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
MODEL='experiments/tsl9-resident-memory-leaves'
DEPS={
 'v4160-ota-handler-compact-2026-10-22/callee-review/review.py':'ef19f4db8f469250c136982c462b409bf4292fd4565c387295b51d9f6f410286',
 'v4160-ota-handler-compact-2026-10-22/ABI-review/native.py':'1b378718c84e31bf7a6f03a3f3f22f9db755d6b804dd410b29f0224559b1dca9'}
PORTS={'ml_port_read8','ml_port_read32','ml_port_write8','ml_port_write32','ml_port_fence_i'}
PUBLIC={'tsl9_candidate_compare_200004bc','tsl9_candidate_fill_2000039c','tsl9_candidate_copy_20000332'}
def need(v,m):
    if not v:raise ValueError(m)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(p.read_bytes())
def write(p,v):p.write_bytes((json.dumps(v,indent=2)+'\n').encode('utf8'))
def case(root,slug):return next(p for p in (root/'apk-analysis'/('tsl9-'+slug),root/'analysis'/slug) if p.is_dir())
def module(p):
    s=importlib.util.spec_from_file_location('independent_memory_'+p.stem,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def contexts(root):
    modules={}
    for slug,pin in DEPS.items():
        folder,name=slug.rsplit('/',1);p=case(root,folder)/name;need(sha(p)==pin,'Immutable static reader '+slug);modules[name]=module(p)
    return modules['review.py'],modules['native.py']
def sources(root,refs=None):
    copy,_=contexts(root);decode,_,_=copy.context(root);ledger=read(HERE/'source-ledger.json');out=[]
    for leaf in ledger['leaves']:
        blob=bytes.fromhex(leaf['raw_hex']);need(len(blob)==leaf['bytes'] and hashlib.sha256(blob).hexdigest()==leaf['sha256'],'Exact complete candidate raw body')
        rows=copy.rows(blob,leaf['entry'],decode);need(len(rows)==leaf['instructions'],'Complete static candidate instruction coverage');starts={r['PC'] for r in rows}
        need(all(r['target'] is None or r['target'] in starts for r in rows),'Bounded local candidate control targets')
        need(not any(r['rd'] in (1,2,3,4,8,9,18,19,20,21,22,23,24,25,26,27) for r in rows),'Source leaf has no SP/RA/GP/S destination')
        need(not any(r['op'] in ('jal','jalr') and r['rd']==1 for r in rows),'Source leaf makes no nested calls')
        need(rows[0]['op']=='lui' and rows[0]['immediate']==0x40024000 and rows[1]['op']=='lw' and rows[1]['immediate']==0x20c and rows[2]['op']=='sw' and rows[2]['rs2']==0 and rows[3]['op']=='fence.i','Guard before first argument test')
        saved=rows[1]['rd'];restores=[r for r in rows if r['op']=='sw' and r['immediate']==0x20c and r['rs2']==saved];need(len(restores)==(2 if leaf['name']=='compare' else 1),'Normal paths restore original MMIO word')
        if leaf['name']=='compare':
            need(any(r['op']=='bne' and r['rs1']==13 and r['rs2']==11 for r in rows),'LBU compared against full A1')
        elif leaf['name']=='fill':need(any(r['op']=='sb' and r['rs2']==11 and r['immediate']==-1 for r in rows),'Fill low byte and advanced pointer source site')
        else:
            need(not any(r['rd'] in (10,11,12) for r in rows),'Copy leaves arguments unchanged')
            need([r['op'] for r in rows if r['memory_width']==8]==['lbu','sb'],'Forward read then byte write')
        out.append(dict(name=leaf['name'],bytes=len(blob),instructions=len(rows),body_sha256=leaf['sha256']))
    observed=[]
    if refs is not None:
        ref=read(case(root,'v4160-ota-handler-compact-2026-10-22')/'callee-review/reference-pins.json')['candidate_files']
        for i,(name,pin) in enumerate(ref.items()):
            p=refs/name/pin['segment'];need(sha(p)==pin['segment_sha256'],'Actual existing candidate segment');data=p.read_bytes()
            for leaf in ledger['leaves']:
                at=leaf['source_flash_entries'][i]-0x40000;need(data[at:at+leaf['bytes']]==bytes.fromhex(leaf['raw_hex']),'Actual candidate mapping '+name+'/'+leaf['name'])
            observed.append(dict(candidate=name,sha256=sha(p),bodies=3))
    return dict(passed=True,candidate_bodies=out,actual_candidate_segments_read=refs is not None,segments=observed,installed_provider_proved=False)
def inspect(root,folder):
    root=Path(root).resolve();folder=Path(folder).resolve();_,native=contexts(root);fields,llvm,ctx=native.context(root)
    need(all(sha(root/MODEL/'src'/name)==pin for name,pin in read(HERE/'core-pins.json').items()),'Frozen four source files')
    previous=ctx['extension']
    def extended(raw,pc,base):
        word=int.from_bytes(raw[:4],'little')
        if len(raw)>=4 and word&0x707f==0x67:
            immediate=word>>20
            return dict(PC=pc,bytes=4,raw_hex=raw[:4].hex(),op='jalr',rd=(word>>7)&31,rs1=(word>>15)&31,rs2=None,immediate=immediate-4096 if immediate&2048 else immediate,target=None,memory_width=None)
        return previous(raw,pc,base)
    ctx['extension']=extended
    producer=case(root,'v4160-resident-memory-2026-10-22')/'implementation/probe.py'
    need(sha(producer)==read(HERE/'reference-pins.json')['producer'],'Frozen actual compiler/provenance reader')
    provenance=module(producer).replay(root,folder/'verification.json')
    r=read(folder/'verification.json');e=ctx['ELF'](folder/'memory_leaves.o');need(e.kind==1 and e.flags==1,'Actual RV32/RVC relocatable object')
    und={s['name'] for s in e.symbols if s['index']==0 and s['name']};need(und==PORTS,'Exactly five true unresolved ports')
    need(not any(s['index']==0xfff1 and s['info']>>4 for s in e.symbols),'No fake numeric provider')
    funcs=[f for f in e.symbols if f['info']&15==2 and f['size']];need(len(funcs)==4 and {f['name'] for f in funcs if f['info']>>4==1}==PUBLIC,'Three real typed public functions and one actual local helper')
    alloc=[s for s in e.sections if s['flags']&2 and s['size']];need(len(alloc)==4 and all(s['type']==1 and s['flags']==6 for s in alloc),'Four real code owners only')
    text=(folder/'complete-static-disassembly.log').read_text();pieces=re.split(r'Disassembly of section ([^\n:]+):',text);parsed={}
    for i in range(1,len(pieces),2):parsed[pieces[i]]=llvm['parse'](re.sub(r' <[^>]*>','',pieces[i+1]))
    reports=[];call_counts=collections.Counter()
    for f in funcs:
        section=e.sections[f['index']];need(f['value']==0 and f['size']==section['size'],'Whole actual unique function allocation')
        rows=fields['rows'](e.function_bytes(f),0,ctx);need([{k:v for k,v in x.items() if k!='offset'} for x in rows]==parsed[section['name']],'All native raw fields independently equal actual LLVM disassembly')
        first=rows[0];need(first['op']=='addi' and first['rd']==first['rs1']==2 and first['immediate']<0,'Measured native stack frame');frame=-first['immediate']
        need(frame%16==0,'Native frame alignment');starts={x['PC'] for x in rows};need(all(x['target'] is None or x['target'] in starts for x in rows),'Every native encoded branch target is inside complete allocation')
        saves=[[x['rs2'],x['immediate']] for x in rows if x['op']=='sw' and x['rs1']==2];restores=[[x['rd'],x['immediate']] for x in rows if x['op']=='lw' and x['rs1']==2 and x['rd'] in (1,8,9,18,19,20,21)]
        need(all(0<=x['immediate'] and x['immediate']+x['memory_width']//8<=frame for x in rows if x['memory_width'] is not None and x['rs1']==2),'All explicit SP accesses inside measured frame')
        need(set(map(tuple,saves))==set(map(tuple,restores)),'Every measured saved register has an explicit restore (path count may duplicate)')
        bypc={x['PC']:x for x in rows};calls=[]
        for rel in [x for x in e.relocations if x['owner']==section['name']]:
            at=rel['offset'];a=bypc[at];b=bypc[at+4];name=rel['symbol']['name']
            need(rel['type']==19 and rel['addend']==0 and a['op']=='auipc' and b['op']=='jalr' and b['rs1']==a['rd'] and b['rd'] in (0,1),'Actual CALL_PLT AUIPC/JALR shape')
            need(name in PORTS or rel['symbol']['index']>0,'Real unresolved port or actual allocated local helper')
            calls.append(dict(offset=at,target=name,link_register=b['rd']));call_counts[name]+=1
        need(len([x for x in rows if x['op']=='jalr' and not (x['rd']==0 and x['rs1']==1 and x['immediate']==0)])==len(calls),'No hidden indirect calls beyond actual port/helper relocations')
        reports.append(dict(name=f['name'],section=section['name'],bytes=f['size'],instructions=len(rows),frame_bytes=frame,saves=saves,restores=restores,calls=calls,code_sha256=hashlib.sha256(e.function_bytes(f)).hexdigest()))
    ir=(folder/'memory_leaves.ll').read_text();need(ir.count('sret(%struct.ml_result)')==3 and len(re.findall(r'^define ',ir,re.M))==4,'Actual three sret/context interfaces plus outlined begin helper')
    need(all('@'+name+'(' in ir for name in PORTS) and 'asm' not in ir,'Typed external I/O in actual IR; no borrowed whole-function assembly')
    result=dict(passed=True,actual_native_artifacts_read=True,mode=r['mode'],object_sha256=sha(folder/'memory_leaves.o'),IR_sha256=sha(folder/'memory_leaves.ll'),functions=reports,allocated_bytes=sum(x['bytes'] for x in reports),instructions=sum(x['instructions'] for x in reports),RELA=len(e.relocations),undefined_symbols=sorted(und),call_target_counts=dict(call_counts),source_pins=read(HERE/'core-pins.json'),producer_receipt_sha256=sha(folder/'verification.json'),producer_provenance_replayed=provenance['passed'],linked=False,BIN_exported=False,target_execution=False,ISA_emulation=False,physical_ABI_proof=False,installed_provider_proved=False)
    return result
def replay(root,path):
    r=read(path);need(r['checker_sha256']==sha(HERE/'review.py'),'Actual reviewer identity')
    result=inspect(root,Path(r['folder']));need(result==r['result'],'Read-only actual native artifact replay')
    return result
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--project-root',type=Path,required=True);p.add_argument('--folder',type=Path);p.add_argument('--receipt',type=Path);p.add_argument('--replay',type=Path);p.add_argument('--candidate-refs',type=Path);a=p.parse_args();root=a.project_root.resolve()
    if a.replay:need(a.folder is None and a.receipt is None and a.candidate_refs is None,'Readonly actual replay');result=replay(root,a.replay.resolve())
    elif a.folder:
        need(a.receipt is not None and not a.receipt.exists() and a.candidate_refs is None,'Create-only independent metadata receipt');result=inspect(root,a.folder);a.receipt.parent.mkdir(parents=True,exist_ok=True);write(a.receipt,dict(schema='TSL9-resident-memory-independent-native-review-v1',checker_sha256=sha(HERE/'review.py'),folder=str(a.folder.resolve()),result=result))
    else:need(a.receipt is None,'No receipt without actual native input');result=sources(root,a.candidate_refs.resolve() if a.candidate_refs else None)
    print(json.dumps(result))
