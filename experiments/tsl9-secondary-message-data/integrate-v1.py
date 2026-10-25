"""Partially link the nine bodies and two DATA windows, preserving every accepted parent role."""
import argparse,hashlib,json,runpy,subprocess,sys
from collections import Counter
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
S=json.loads((HERE/'integration-v1.json').read_text())
OUTPUT='UNRESOLVED-EXPERIMENTAL-SECONDARY-MESSAGE.o'
def need(ok,label):
    if not ok:raise ValueError(label)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def lib(p):return runpy.run_path(str(ROOT/p),run_name='offline_secondary_component_library')
for p,h in S['pins'].items():need(sha(ROOT/p)==h,'Pinned component dependency '+p)
N=lib(S['CODE_build']);D=lib(S['DATA_build']);P=lib(S['parent_verifier']);E=lib(N['S']['reader'])['ELF']
def paths(mode):return [ROOT/S['parent_component']/mode/S['parent_object'],ROOT/S['CODE_trial']/mode/'unit.o',ROOT/S['DATA_trial']/mode/'unit.o']
def globals_of(e):
    rows=[v for v in e.symbols if v['info']>>4];m={v['name']:v for v in rows}
    need(len(rows)==len(m) and not any(v['section']==0xfff1 for v in rows),'Unique actual globals without ABS substitutes');return m
def source_proof(llvm):
    need(sha(llvm/'ld.lld.exe')==N['S']['tools']['ld.lld.exe'],'Pinned local linker')
    code=json.loads((ROOT/S['CODE_trial']/'measurement.json').read_text());data=json.loads((ROOT/S['DATA_trial']/'measurement.json').read_text())
    need(code['inputs']==N['portable'](N['inputs'](llvm),llvm),'Every original690-instruction compiler input unchanged')
    need(data['inputs']==D['inputs'](llvm) and data['static_audit']==D['static_audit'](),'Every observed40-byte DATA input/contract unchanged')
    generated=lib(S['CODE_derive'])['generate']()
    need(generated['source']==(ROOT/N['S']['source']).read_text(),'Exact generated original-context C')
    for k in ['regions','controls','PC_relative_pairs','literal_data','undefined']:need(generated[k]==N['S'][k],'Exact derived '+k)
    parent=[]
    for mode in ['c','cpp']:
        p,c,d=paths(mode);need(sha(p)==S['parent_sha256'],'Exact frozen accepted component')
        prior=P['audit_component'](p,mode);need(prior['passed'],'Whole actual accepted allocation/reference retention')
        need(N['audit_object'](c)==code['modes'][mode]['result'],'Actual690-instruction native object')
        need(D['audit_object'](d)==data['modes'][mode],'Actual40-byte native DATA object')
        parent.append(prior['object_sha256'])
    need(parent==[S['parent_sha256']]*2,'Both language parents are the frozen accepted object')
    return dict(passed=True,parent_from_frozen_accepted_component=True,parent_sha256=S['parent_sha256'],new_CODE_bytes=2048,new_instructions=690,new_DATA_bytes=40,new_positive_OBJECTs=2,curated_integration=False)
def audit(path,mode):
    ins=[E(p) for p in paths(mode)];out=E(path);maps=[globals_of(e) for e in ins];gm=globals_of(out)
    need(out.header[0]==1 and out.header[1]==243 and not out.program_headers,'Nonloadable RV32 ET_REL')
    need(set(gm)==set().union(*(set(m) for m in maps)),'Exact combined global inventory')
    alloc={}
    for e in ins:
        for sec in e.sections:
            if not(sec['flags']&2 and sec['size']):continue
            need(sec['name'] not in alloc,'Distinct real source allocations')
            alloc[sec['name']]=(sec['type'],sec['flags'],sec['size'],sec['align'])
            need(out.data(sec['name'])==e.data(sec),'Every accepted/new allocated byte unchanged')
    need({v['name']:(v['type'],v['flags'],v['size'],v['align']) for v in out.sections if v['flags']&2 and v['size']}==alloc,'Only accepted allocations plus the two measured source units')
    def role(v,e):return(v['name'],v['info'],v['other'],v['value'],v['size'],e.sections[v['section']]['name'] if v['section'] else '')
    for e,m in zip(ins,maps):
        for name,v in m.items():
            if v['section']:need(role(gm[name],out)==role(v,e),'Every positive provider and actual alias keeps its backing')
            elif not gm[name]['section']:need(role(gm[name],out)==role(v,e),'Remaining undefined dependency stays explicit')
    expected=Counter()
    for e in ins:
        for r in e.relocations:
            t=e.symbols[r['symbol']];target=role(gm[t['name']],out) if t['info']>>4 else role(t,e)
            expected[(e.sections[r['section']]['name'],r['offset'],r['type'],r['addend'],target)]+=1
    actual=Counter((out.sections[r['section']]['name'],r['offset'],r['type'],r['addend'],role(out.symbols[r['symbol']],out)) for r in out.relocations)
    need(expected==actual and len(out.relocations)==5215,'All4972 accepted and243 new relocation roles preserved')
    parent,code,data=maps;old_und={n for n,v in parent.items() if not v['section']};after={n for n,v in gm.items() if not v['section']}
    need(len(old_und)==6 and after==old_und,'Exactly the same six compiler UND remain')
    code_und={n for n,v in code.items() if not v['section']};data_providers={d['name'] for d in D['S']['data_regions']}
    need(len(code_und)==54 and code_und-data_providers=={n for n in code_und if n in parent and parent[n]['info']==18 and parent[n]['section'] and parent[n]['size']>0},'Exactly52 genuine existing CODE providers bind')
    need(data_providers<=code_und and len(data_providers)==2 and all(gm[n]['info']==17 and gm[n]['section'] for n in data_providers),'Both new DATA dependencies bind to actual storage')
    functions=[v for v in gm.values() if v['section'] and v['info']==18 and v['size']];objects=[v for v in gm.values() if v['section'] and v['info']==17 and v['size']]
    need(len(functions)==6118 and sum(v['size'] for v in functions)==68648,'All6118 positive FUNC regions and68648 CODE bytes')
    need(len(objects)==56 and sum(v['size'] for v in objects)==3962,'All56 positive DATA owners and3962 DATA bytes')
    labels={n for n,v in gm.items() if v['section'] and v['info']==17 and not v['size']}
    need(labels=={n for n,v in parent.items() if v['section'] and v['info']==17 and not v['size']} and len(labels)==6,'All six actual DATA labels unchanged')
    need(sum(bool(v['section'] and v['info']==18 and not v['size']) for v in gm.values())==71,'All71 true CODE aliases retained')
    need(sum(v['size'] for v in out.sections if v['flags']&2)==72610,'All72610 allocated bytes owned; no artificial padding')
    bindings=[];table=D['S']['data_regions'][0];storage=gm[table['name']]
    need(storage['info']==17 and storage['size']==28 and out.sections[storage['section']]['flags']==2,'Real readonly28-byte event table')
    raw=out.data(out.sections[storage['section']])
    for i,(target,name) in enumerate(zip(table['targets'],table['target_symbols'])):
        fn=gm[name];need(fn['info']==18 and fn['size']>0 and out.sections[fn['section']]['flags']==6,'Every event cell has positive CODE backing')
        need(table['start']+int.from_bytes(raw[i*4:i*4+4],'little',signed=True)==target,'Every signed cell retains its original CODE address')
        bindings.append(dict(index=i,original_target=target,CODE_provider=name,positive_CODE_bytes=fn['size']))
    need(len(bindings)==7 and len({b['original_target'] for b in bindings})==6,'Seven cells and six actual CODE entries')
    comparison=lib('experiments/tsl9-remaining-record-dispatch/compare-readers-v1.py')['audit'](path)
    need(comparison['passed'],'Independent ELF readers agree')
    return dict(passed=True,CODE_bytes=68648,DATA_bytes=3962,new_CODE_bytes=2048,new_DATA_bytes=40,new_instructions=690,positive_FUNC=6118,positive_DATA_OBJECTs=56,
                true_CODE_aliases=71,real_DATA_labels=6,RELA=5215,UND=sorted(after),resolved_existing_CODE_providers=52,resolved_new_DATA_providers=sorted(data_providers),event_CODE_bindings=bindings,
                all_parent_allocations_and_relocation_roles_preserved=True,independent_readers=comparison,object_sha256=sha(path),
                hidden_existing_DATA_dependency=0x1aae8,hidden_index_globally_bounded=False,compiler_UND_is_not_complete_runtime_gap_inventory=True,
                original_coordinate_link_performed=False,curated_integration=False,formal_coverage_percent=91.83,installed_ROM_ABI_verified=False,
                target_executed=False,HOST_model_executed=False,ISA_emulated=False,hardware_accessed=False,network=False,new_BIN=False,firmware_ready=False)
def inputs(llvm):
    for p,h in S['pins'].items():need(sha(ROOT/p)==h,'Current component input pin')
    native={str(p.relative_to(ROOT)).replace('\\','/'):sha(p) for mode in ['c','cpp'] for p in paths(mode)}
    return dict(checker=sha(__file__),spec=sha(HERE/'integration-v1.json'),pins=S['pins'],native_objects=native,CODE_inputs=N['portable'](N['inputs'](llvm),llvm),DATA_inputs=D['inputs'](llvm))
def main():
    p=argparse.ArgumentParser();p.add_argument('--tool-dir',type=Path,required=True);g=p.add_mutually_exclusive_group(required=True);g.add_argument('--trial');g.add_argument('--replay',type=Path);a=p.parse_args();llvm=a.tool_dir.resolve()
    before=inputs(llvm);source=source_proof(llvm)
    if a.replay:
        out=a.replay.resolve();need(out.parent==HERE/'build','Owned component trial');saved=json.loads((out/'measurement.json').read_text())
        need(saved['inputs']==before and saved['source_proof']==source,'Every retained actual link input unchanged')
        for mode in ['c','cpp']:need(saved['modes'][mode]==audit(out/mode/OUTPUT,mode),'Fresh actual component replay')
        print(json.dumps(dict(passed=True,mode='read-only-component-replay',target_executed=False)));return
    need(a.trial and Path(a.trial).name==a.trial,'Single owned trial name');out=HERE/'build'/a.trial;need(not out.exists(),'Create-only component trial')
    report=dict(inputs=before,source_proof=source,modes={})
    for mode in ['c','cpp']:
        folder=out/mode;folder.mkdir(parents=True);argv=[str(llvm/'ld.lld.exe'),'-m','elf32lriscv','-r','--no-relax','-o',str(folder/OUTPUT),*[str(p) for p in paths(mode)]]
        result=subprocess.run(argv,capture_output=True,timeout=60);(folder/'link.log').write_text(N['portable'](result.stderr.decode('utf-8','replace'),llvm),encoding='utf-8');need(result.returncode==0,'Partial link failed; local diagnostic retained')
        report['modes'][mode]=audit(folder/OUTPUT,mode)
    need(report['modes']['c']['object_sha256']==report['modes']['cpp']['object_sha256'],'Identical C/C++ component objects')
    need(inputs(llvm)==before,'Every actual source/link input unchanged during measurement')
    (out/'measurement.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    facts=report['modes']['c'];print(json.dumps({k:facts[k] for k in ['passed','CODE_bytes','DATA_bytes','RELA','UND','resolved_existing_CODE_providers','object_sha256','formal_coverage_percent','new_BIN']}))
if __name__=='__main__':
    try:main()
    except Exception as error:
        print(json.dumps(dict(passed=False,error_type=type(error).__name__,reason=str(error).replace(str(ROOT),'PROJECT_ROOT').replace(str(Path.home()),'USERPROFILE'))));raise SystemExit(1)
