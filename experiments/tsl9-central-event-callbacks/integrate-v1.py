"""Experimental partial link; preserve every parent allocation and reference role."""
import argparse,hashlib,json,runpy,subprocess,sys
from collections import Counter
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
OUTPUT='UNRESOLVED-EXPERIMENTAL-CENTRAL-CALLBACKS.o'
PARENT='experiments/tsl9-callback-prefix-data/build/component-v2'
PARENT_NAME='UNRESOLVED-STARTUP-CALLBACK-PREFIX-DATA.o'
PARENT_SHA='6105d593a33c9e279ddb939fa0e5e54343196b6c9ba36d78490e0952c7a0e9d0'
LEAVES='experiments/tsl9-central-callback-leaves'
def need(ok,label):
    if not ok:raise ValueError(label)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def lib(p):return runpy.run_path(str(ROOT/p),run_name='offline_central_component_library')
N=lib('experiments/tsl9-central-event-callbacks/build-v1.py')
E=lib('experiments/tsl9-feature-dispatch-tree/elf_reader-v5.py')['ELF']
def globals_of(e):
    rows=[s for s in e.symbols if s['info']>>4];gm={s['name']:s for s in rows}
    need(len(rows)==len(gm) and all(s['section']!=0xfff1 for s in rows),'Unique globals; no ABS substitutes')
    return gm
def paths(mode):
    return [ROOT/PARENT/mode/PARENT_NAME,ROOT/LEAVES/'build/v1'/(mode+'.o'),HERE/'build/native-v1'/mode/'unit.o']
def source_proof(llvm):
    need(sha(llvm/'ld.lld.exe')==N['S']['tools']['ld.lld.exe'],'Pinned linker')
    need(sha(llvm/'clang.exe')==N['S']['tools']['clang.exe'],'Pinned compiler')
    generated=lib('experiments/tsl9-central-event-callbacks/derive-v1.py')['generate']()
    need(generated['source']==(ROOT/N['S']['source']).read_text(),'Exact current derived event source')
    for key in ['regions','controls','PC_relative_pairs','literal_data','undefined']:
        need(generated[key]==N['S'][key],'Exact derived event metadata')
    saved=json.loads((HERE/'build/native-v1/measurement.json').read_text())
    need(saved['inputs']==N['portable'](N['inputs'](llvm),llvm),'Every compiled event input unchanged')
    leaves=json.loads((ROOT/LEAVES/'spec-v1.json').read_text())
    receipt=json.loads((ROOT/LEAVES/'build/v1/verification.json').read_text())
    need(sha(ROOT/leaves['source'])==leaves['source_sha256']==receipt['source_sha256'],'Exact source-proven leaves')
    for mode in ['c','cpp']:
        parent,leaf,event=paths(mode)
        need(sha(parent)==PARENT_SHA,'Exact source-proven parent')
        need(sha(leaf)==next(r for r in receipt['results'] if r['mode']==mode)['object_sha256'],'Exact source-proven leaf object')
        need(N['audit_object'](event)==saved['modes'][mode]['result'],'Fresh actual event object proof')
    return dict(event_code_bytes=1938,event_instructions=645,leaf_code_bytes=118,leaf_instructions=41,
                complete_bodies=9,curated_integration=False)
def audit(path,mode):
    ins=[E(p) for p in paths(mode)];out=E(path)
    need(out.header[0]==1 and out.header[1]==243 and not out.program_headers,'Nonloadable RV32 ET_REL')
    maps=[globals_of(e) for e in ins];gm=globals_of(out)
    need(set(gm)==set().union(*(set(m) for m in maps)),'Exact combined global inventory')
    expected_alloc={}
    for e in ins:
        for sec in e.sections:
            if not (sec['flags']&2 and sec['size']):continue
            need(sec['name'] not in expected_alloc,'Distinct source allocations')
            expected_alloc[sec['name']]=(sec['type'],sec['flags'],sec['size'],sec['align'])
            need(out.data(sec['name'])==e.data(sec),'Every parent/new allocation byte unchanged')
    need({s['name']:(s['type'],s['flags'],s['size'],s['align']) for s in out.sections if s['flags']&2 and s['size']}==expected_alloc,'Only measured original and new allocations')
    def role(v,e):return (v['name'],v['info'],v['other'],v['value'],v['size'],e.sections[v['section']]['name'] if v['section'] else '')
    for e,m in zip(ins,maps):
        for name,v in m.items():
            if v['section']:need(role(gm[name],out)==role(v,e),'Every positive provider and real alias retains exact backing')
            elif not gm[name]['section']:need(role(gm[name],out)==role(v,e),'Unprovided dependency remains explicit')
    expected=Counter()
    for e in ins:
        for r in e.relocations:
            target=e.symbols[r['symbol']]
            target_role=role(gm[target['name']],out) if target['info']>>4 else role(target,e)
            expected[(e.sections[r['section']]['name'],r['offset'],r['type'],r['addend'],target_role)]+=1
    actual=Counter((out.sections[r['section']]['name'],r['offset'],r['type'],r['addend'],role(out.symbols[r['symbol']],out)) for r in out.relocations)
    need(actual==expected and len(out.relocations)==4967,'All 4967 actual source/type/addend/target roles retained')
    parent=maps[0]
    old_undefined={n for n,s in parent.items() if not s['section']}
    undefined={n for n,s in gm.items() if not s['section']}
    need(len(old_undefined)==8 and undefined==old_undefined|{'tsl9_central_event_callbacks_static_data_1a548'},'Only new unresolved jump-table DATA; all eleven CODE dependencies bind')
    code=[s for s in gm.values() if s['section'] and s['info']==18 and s['size']]
    data=[s for s in gm.values() if s['section'] and s['info']==17 and s['size']]
    labels={n for n,s in gm.items() if s['section'] and s['info']==17 and not s['size']}
    old_labels={n for n,s in parent.items() if s['section'] and s['info']==17 and not s['size']}
    need(len(code)==5846 and sum(s['size'] for s in code)==66600,'Exactly 2056 new CODE bytes in 158 actual regions')
    need(len(data)==51 and sum(s['size'] for s in data)==3830 and labels==old_labels and len(labels)==6,'All prior DATA owners and six real labels retained')
    need(sum(s['info']==18 and s['section'] and not s['size'] for s in gm.values())==71,'All true CODE aliases retained')
    need(sum(sec['size'] for sec in out.sections if sec['flags']&2)==70430,'Every allocated byte owned; no added padding/data')
    comparison=lib('experiments/tsl9-remaining-record-dispatch/compare-readers-v1.py')['audit'](path)
    return dict(passed=True,CODE_bytes=66600,DATA_bytes=3830,new_CODE_bytes=2056,new_instructions=686,
                positive_FUNC=5846,true_CODE_aliases=71,positive_DATA_owners=51,real_DATA_labels=6,
                RELA=4967,UND=sorted(undefined),new_undefined=['tsl9_central_event_callbacks_static_data_1a548'],
                all_parent_allocations_and_relocation_roles_preserved=True,all_eleven_external_CODE_providers_bound=True,
                independent_readers=comparison,object_sha256=sha(path),curated_integration=False,
                original_coordinate_link_performed=False,formal_coverage_percent=89.03,
                installed_ROM_ABI_verified=False,target_executed=False,new_BIN=False,firmware_ready=False)
def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tool-dir',type=Path,required=True);parser.add_argument('--trial',required=True)
    args=parser.parse_args();llvm=args.tool_dir.resolve()
    need(Path(args.trial).name==args.trial,'Single owned trial name')
    source=source_proof(llvm);out=HERE/'build'/args.trial
    need(not out.exists(),'Create-only experimental trial')
    report=dict(source_proof=source,modes={})
    for mode in ['c','cpp']:
        folder=out/mode;folder.mkdir(parents=True)
        argv=[str(llvm/'ld.lld.exe'),'-m','elf32lriscv','-r','--no-relax','-o',str(folder/OUTPUT),*[str(p) for p in paths(mode)]]
        result=subprocess.run(argv,capture_output=True,timeout=60)
        (folder/'link.log').write_text(N['portable'](result.stderr.decode('utf-8',errors='replace'),llvm),encoding='utf-8')
        need(result.returncode==0,'Partial link; diagnostic retained locally')
        facts=audit(folder/OUTPUT,mode);report['modes'][mode]=facts
    need(report['modes']['c']['object_sha256']==report['modes']['cpp']['object_sha256'],'Identical measured C/C++ combined objects')
    (out/'measurement.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report))
if __name__=='__main__':main()
