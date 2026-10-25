#!/usr/bin/env python3
"""Compile only a readonly C/C++ pool with real interior labels; audit an experimental link."""
from pathlib import Path
from collections import Counter
import argparse,hashlib,json,runpy,struct,subprocess,sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
S=json.loads((HERE/'spec-v1.json').read_bytes())
OUTPUT='UNRESOLVED-EXPERIMENTAL-SEQUENCE-POOL.o'

def need(ok,label):
    if not ok:raise ValueError(label)

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def parent_path(mode):return (ROOT/S['parent_component']).parent.parent/mode/Path(S['parent_component']).name

def library(p):return runpy.run_path(str(ROOT/p),run_name='positive_pool_library')

def sx(v,n):return v-(1<<n)if v&(1<<(n-1))else v

def static_audit():
    need(sha(ROOT/S['evidence'])==S['evidence_sha256'],'Pinned original CODE and literal-envelope evidence')
    ev=json.loads((ROOT/S['evidence']).read_bytes());fw=(ROOT/ev['firmware']).read_bytes()
    need(sha(ROOT/ev['firmware'])==ev['firmware_sha256']and len(fw)==76800,'Original official firmware')
    need(sha(ROOT/S['source'])==S['source_sha256'],'Actual typed C source')
    need(sha(ROOT/ev['prior_index_evidence'])==ev['prior_index_evidence_sha256'],'Previous index/consumer evidence unchanged')
    need(sha(ROOT/S['parent_component'])==S['parent_component_sha256']==ev['parent_component_sha256'],'Exact retained accepted source component')
    need(all(sha(parent_path(mode))==S['parent_component_sha256']for mode in ['c','cpp']),'Both accepted parent-language objects have the same pinned identity')
    need(all(sha(ROOT/path)==pin for path,pin in S['proof_inputs'].items()),'Pinned static derivation and independent-reader helpers')
    ops={};count=0
    for window in ev['CODE_windows']:
        at=window['start']
        for o in window['operations']:
            need(o['addr']==at and bytes.fromhex(o['bytes'])==fw[at-0x8000:at-0x8000+o['size']],'Every original instruction byte and boundary')
            need(at not in ops,'Unique captured original instruction');ops[at]=o;at+=o['size'];count+=1
        need(at==window['end'],'Complete source-selection/state-consumer CODE window')
    need(count==245,'245 freshly captured original instructions')
    def word(pc):return int.from_bytes(bytes.fromhex(ops[pc]['bytes']),'little')
    def pair(hi,lo,reg):
        a,b=word(hi),word(lo)
        need(ops[hi]['size']==ops[lo]['size']==4 and a&127==0x17 and(a>>7)&31==reg,'Actual AUIPC register')
        need(b&0x707f==0x13 and(b>>7)&31==(b>>15)&31==reg,'Actual ADDI source pair')
        return (hi+(a&0xfffff000)+sx(b>>20,12))&0xffffffff
    def store(hi,pc,reg,kind,value_register,address):
        a,w=word(hi),word(pc);off=sx(((w>>25)<<5)|((w>>7)&31),12)
        need(ops[hi]['size']==ops[pc]['size']==4 and a&127==0x17 and(a>>7)&31==reg,'Actual memory-store AUIPC register')
        need(w&127==0x23 and(w>>15)&31==reg and(w>>12)&7==kind and(w>>20)&31==value_register,'Actual memory-store fields')
        need((hi+(a&0xfffff000)+off)&0xffffffff==address,'Exact original RAM destination')
    # Exact state fields and separate pointer/limit/index writes,not an atomic bundle.
    store(0xefb4,0xefb8,14,2,15,0x2000bf88)
    store(0xf000,0xf004,14,2,15,0x2000bf88)
    store(0xefc2,0xefc6,14,1,15,0x2000bf86)
    store(0xefca,0xefce,15,1,0,0x2000bf84)
    store(0xee58,0xee5c,15,1,0,0x2000bf86)
    store(0xee72,0xee76,14,1,15,0x2000bf84)
    store(0xeeba,0xeebe,15,2,0,0x2000bf84)
    need(word(0xefbc)==0x47c5 and word(0xf008)==0x03500793,'Actual local limit constants17 and53')
    need([pair(a,z,15)for a,z in [(0xefac,0xefb0),(0xefee,0xeff2),(0xeff8,0xeffc)]]==[0x1a430,0x1a454,0x1a478],'Actual three source literals')
    decoder=library('experiments/tsl9-original-startup/build-v1.py')['decode_control']
    for pc,target in [(0xef9c,0xefee),(0xefa2,0xeff8),(0xefa8,0xf00e),(0xeff6,0xefb4),(0xf00c,0xefbe)]:
        result=decoder(bytes.fromhex(ops[pc]['bytes']),pc);need(result is not None and result[1]==target,'Actual source-selection continuation')
    need(pair(0xefe0,0xefe4,10)==pair(0xee8c,0xee90,10)==pair(0xeeb2,0xeeb6,10)==0xee30,'Same original callback literal at setup,repetition and cancellation helper')
    need(decoder(bytes.fromhex(ops[0xeec2]['bytes']),0xeec2)==(17,0x90b0),'Original cancellation-helper call occurs after combined zeroing store')
    need(pair(0xbd46,0xbd4a,10)==0x2000bf11 and pair(0xbd50,0xbd54,10)==0x2000bf10,'Exact two adjacent state-byte address providers')
    need(pair(0xf0bc,0xf0c0,10)==0x2000bf84 and word(0xf0b0)==0x000407b7 and word(0xf0b4)==0x0487a303 and word(0xf0c4)==0x8302,'Actual resident-slot reset destination and tail transfer')
    need(ops[0xf0b8]['opcode']=='li a2, 12'and ops[0xf0ba]['opcode']=='li a1, 0','Original reset value/length arguments')
    combinations=[dict(pointer=p,limit=n,start=p,end=p+2*n,bytes=2*n)for p in [0x1a430,0x1a454,0x1a478]for n in [17,53]]
    need(combinations==ev['independent_literal_pointer_limit_combinations'],'All six conditional literal-address envelopes')
    merged=[]
    for c in sorted(combinations,key=lambda v:(v['start'],v['end'])):
        if merged and c['start']<=merged[-1]['end']:merged[-1]['end']=max(merged[-1]['end'],c['end'])
        else:merged.append(dict(start=c['start'],end=c['end']))
    need(merged==[dict(start=0x1a430,end=0x1a4e2)]and S['owner']['bytes']==178,'One178-byte conservative literal envelope,not neighboring-address inference')
    need([(d['pool_offset'],d['size'])for d in S['labels']]==[(0,0),(36,0),(72,0)],'Three true interior labels with no duplicate allocation')
    B=library('experiments/tsl9-original-layout/build-v57.py');parent=B['E'](ROOT/S['parent_component']);plan=B['derive'](parent)
    need(not any(S['owner']['start']<o['original_PC']+o['bytes']and o['original_PC']<S['owner']['end']for o in plan['owners']),'No overlap with any accepted CODE/DATA owner')
    return dict(passed=True,captured_instructions=245,selected_literal_combinations=6,conservative_literal_envelope_bytes=178,paired_profile_read_bytes=[34,34,106],interior_label_offsets=[0,36,72],separate_state_store_PCs=[0xefb8,0xf004,0xefc6,0xefce],combined_index_limit_zero_PC=0xeebe,clear_before_cancellation_helper=True,resident_zero_reset_slot=0x40048,conditional_resident_zero_reset_bytes=12,global_runtime_pointer_or_limit_bound_proved=False,installed_ROM_identity_proved=False,original_declared_pool_extent_proved=False,source_curated_or_accepted_component_updated=False,firmware_ready=False,target_executed=False,HOST_model_executed=False,ISA_emulated=False,hardware_accessed=False,network=False)

def elf(p):return library(S['reader'])['ELF'](p)

def globals_of(e):
    rows=[s for s in e.symbols if s['info']>>4];m={s['name']:s for s in rows}
    need(len(m)==len(rows)and all(s['section']!=0xfff1 for s in rows),'Unique globals without ABS substitutes');return m

def audit_object(path):
    e=elf(path);need(e.header[0]==1 and e.header[1]==243 and not e.program_headers,'Actual RISC-V relocatable DATA object')
    d=S['owner'];alloc=[s for s in e.sections if s['flags']&2 and s['size']]
    need(len(alloc)==1,'One actual readonly allocation');sec=alloc[0]
    need((sec['name'],sec['type'],sec['flags'],sec['size'],sec['align'])==(d['section'],1,2,178,4),'Exact readonly DATA pool allocation')
    gm=globals_of(e);need(set(gm)=={d['name']}|{v['name']for v in S['labels']},'Only genuine pool owner and its three interior labels')
    owner=gm[d['name']];need((owner['info'],owner['other'],owner['section'],owner['value'],owner['size'])==(17,0,sec['index'],0,178),'One actual178-byte OBJECT owner')
    for label in S['labels']:
        v=gm[label['name']];need((v['info'],v['other'],v['section'],v['value'],v['size'])==(17,0,sec['index'],label['pool_offset'],0),'True zero-allocation DATA label backed by the same real pool')
    ev=json.loads((ROOT/S['evidence']).read_bytes());fw=(ROOT/ev['firmware']).read_bytes()
    need(e.data(sec)==fw[d['start']-0x8000:d['end']-0x8000]and hashlib.sha256(e.data(sec)).hexdigest()==d['original_sha256'],'Every compiled readonly byte equals original firmware')
    need(not e.relocations and not any(v['info']&15==2 and v['section']for v in e.symbols),'No executable function,stub or relocation')
    comparison=library('experiments/tsl9-remaining-record-dispatch/compare-readers-v1.py')['audit'](path)
    return dict(passed=True,allocated_DATA_bytes=178,positive_size_OBJECT_owners=1,real_zero_size_DATA_labels=3,FUNC=0,UND=0,RELA=0,ABS_providers=0,object_sha256=sha(path),independent_readers=comparison,firmware_ready=False)

def audit_partial(path,native,mode):
    p,n,e=elf(parent_path(mode)),elf(native),elf(path);pm,nm,em=globals_of(p),globals_of(n),globals_of(e)
    need(e.header[0]==1 and e.header[1]==243 and not e.program_headers,'Experimental non-loadable partial component')
    expected={s['name']:(s['type'],s['flags'],s['size'],s['align'])for s in p.sections if s['flags']&2 and s['size']};expected[S['owner']['section']]=(1,2,178,4)
    need({s['name']:(s['type'],s['flags'],s['size'],s['align'])for s in e.sections if s['flags']&2 and s['size']}==expected,'Every parent allocation retained plus one readonly pool')
    for sec in p.sections:
        if sec['flags']&2 and sec['size']:need(e.data(sec['name'])==p.data(sec),'All original parent CODE/DATA carrier bytes unchanged')
    need(e.data(S['owner']['section'])==n.data(S['owner']['section']),'Whole compiled pool retained')
    need(set(em)==set(pm)|set(nm),'Exact combined global inventory')
    for name,v in pm.items():
        a=em[name]
        if v['section']:
            need((a['info'],a['other'],a['size'],a['value'],e.sections[a['section']]['name'])==(v['info'],v['other'],v['size'],v['value'],p.sections[v['section']]['name']),'Every parent provider role retained')
        elif name not in nm:need((a['info'],a['other'],a['section'],a['value'],a['size'])==(16,0,0,0,0),'Every other dependency remains explicit')
    for name,v in nm.items():
        a=em[name];need((a['info'],a['other'],a['value'],a['size'],e.sections[a['section']]['name'])==(v['info'],v['other'],v['value'],v['size'],n.sections[v['section']]['name']),'All real pool/interior-label roles retained')
    def role(s,reader):return(s['name'],s['info'],s['other'],s['value'],s['size'],reader.sections[s['section']]['name']if s['section']else'')
    expected_relocations=Counter()
    for rel in p.relocations:
        target=p.symbols[rel['symbol']]
        expected_target=role(em[target['name']],e)if target['info']>>4 else role(target,p)
        expected_relocations[(p.sections[rel['section']]['name'],rel['offset'],rel['type'],rel['addend'],expected_target)]+=1
    actual=Counter((e.sections[rel['section']]['name'],rel['offset'],rel['type'],rel['addend'],role(e.symbols[rel['symbol']],e))for rel in e.relocations)
    need(actual==expected_relocations and len(e.relocations)==4861,'Every parent typed relocation retains its source,addend and actual resolved target role')
    undefined=sorted(k for k,v in em.items()if not v['section']);prior=sorted(k for k,v in pm.items()if not v['section']);labels={v['name']for v in S['labels']}
    need(len(prior)==27 and len(undefined)==24 and set(prior)-set(undefined)==labels,'Only the three actual DATA references resolve')
    comparison=library('experiments/tsl9-remaining-record-dispatch/compare-readers-v1.py')['audit'](path)
    return dict(passed=True,CODE_bytes=64544,DATA_bytes=3289,RELA=4861,UND=24,resolved_real_DATA_labels=sorted(labels),code_unchanged=True,all_prior_readonly_bytes_preserved=True,ABS_providers=0,partial_object_sha256=sha(path),independent_readers=comparison,accepted_component_updated=False,source_manifest_updated=False,original_coordinate_link_performed=False,coverage_added=0,firmware_ready=False)

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--tool-dir',required=True,type=Path);g=parser.add_mutually_exclusive_group(required=True);g.add_argument('--trial');g.add_argument('--replay',type=Path);a=parser.parse_args();llvm=a.tool_dir.resolve()
    for name,pin in S['tools'].items():need(sha(llvm/name)==pin,'Pinned compiler tool '+name)
    need(sha(llvm.parent/'lib/clang/18/include/stdint.h')==S['stdint_sha256'],'Pinned compiler header')
    need(sha(ROOT/S['reader'])==S['reader_sha256']and sha(ROOT/S['curation_checker'])==S['curation_checker_sha256'],'Pinned reader and established compiler profile')
    need(S['flags']=={m:library(S['curation_checker'])['flags']({'profile':S['profile']},m)for m in ['c','cpp']},'Unmodified established native flags')
    shared=library('experiments/tsl9-original-startup/build-v1.py');portable=shared['portable'];static=static_audit()
    paths=[Path(__file__),HERE/'spec-v1.json',ROOT/S['source'],ROOT/S['evidence'],ROOT/S['parent_component'],ROOT/S['reader'],ROOT/S['curation_checker'],ROOT/'experiments/tsl9-remaining-record-dispatch/compare-readers-v1.py',llvm.parent/'lib/clang/18/include/stdint.h']+[llvm/p for p in S['tools']]
    paths+=[parent_path('cpp')]+[ROOT/p for p in S['proof_inputs']]
    inputs=portable({str(p):sha(p)for p in paths},llvm)
    if a.replay:
        out=a.replay.resolve();need(out.parent==HERE/'build','Owned experiment replay directory');saved=json.loads((out/'measurement.json').read_bytes());need(saved['inputs']==inputs and saved['static']==static,'Exact retained source/tool/static inputs')
        for mode in ['c','cpp']:
            f=out/mode;need(saved['modes'][mode]['artifacts']=={p.name:sha(p)for p in sorted(f.iterdir())if p.is_file()},'Complete retained compiler/link artifacts')
            need(saved['modes'][mode]['native']==audit_object(f/'unit.o')and saved['modes'][mode]['partial']==audit_partial(f/OUTPUT,f/'unit.o',mode),'Actual DATA and partial-link replay')
        print(json.dumps(dict(passed=True,mode='read-only-replay',DATA_bytes=178,real_interior_labels=3,experimental_UND=24,accepted_UND_unchanged=27,coverage_added=0,firmware_ready=False)));return
    need(Path(a.trial).name==a.trial,'Single trial basename');out=HERE/'build'/a.trial;need(not out.exists(),'Create-only experiment output');report=dict(schema='TSL9-sequence-pool-native-measurement-v1',inputs=inputs,static=static,modes={})
    for mode in ['c','cpp']:
        f=out/mode;f.mkdir(parents=True);commands=[]
        for label,argv in [('compile',[str(llvm/'clang.exe')]+S['flags'][mode]+['-MD','-MF',str(f/'unit.d'),'-MT','unit.o','-c',str(ROOT/S['source']),'-o',str(f/'unit.o')]),('link',[str(llvm/'ld.lld.exe'),'-r','--no-relax',str(parent_path(mode)),str(f/'unit.o'),'-o',str(f/OUTPUT)])]:
            p=subprocess.run(argv,cwd=ROOT,capture_output=True,timeout=120);(f/(label+'.log')).write_text(portable((p.stdout+p.stderr).decode('utf8','replace'),llvm),encoding='utf8');commands.append(dict(label=label,argv=portable(argv,llvm),exit=p.returncode));need(p.returncode==0,'Actual '+label+' failed;local log retained')
        deps=(f/'unit.d').read_text(encoding='utf8');(f/'unit.d').write_text(portable(deps,llvm),encoding='utf8')
        native=audit_object(f/'unit.o');partial=audit_partial(f/OUTPUT,f/'unit.o',mode);report['modes'][mode]=dict(native=native,partial=partial,commands=commands,artifacts={p.name:sha(p)for p in sorted(f.iterdir())if p.is_file()})
    need(sha(out/'c/unit.o')==sha(out/'cpp/unit.o')and sha(out/'c'/OUTPUT)==sha(out/'cpp'/OUTPUT),'Identical C/C++ normal DATA and partial component objects')
    need(inputs==portable({str(p):sha(p)for p in paths},llvm),'All producer inputs unchanged')
    (out/'measurement.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n',encoding='utf8');print(json.dumps(dict(passed=True,DATA_bytes=178,real_interior_labels=3,native_OBJECT_owners=1,native_FUNC=0,native_UND=0,experimental_UND=24,accepted_UND_unchanged=27,coverage_added=0,native_object_sha256=sha(out/'c/unit.o'),partial_object_sha256=sha(out/'c'/OUTPUT),independent_readers_agree=True,firmware_ready=False)))

if __name__=='__main__':
    try:main()
    except Exception as e:
        print(json.dumps(dict(passed=False,reason=str(e).replace(str(ROOT),'PROJECT_ROOT').replace(str(Path.home()),'USERPROFILE'))));sys.exit(1)
