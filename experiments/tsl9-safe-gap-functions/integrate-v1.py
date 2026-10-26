"""Link one source-proven CODE extension and preserve every accepted native role."""
import argparse,hashlib,json,runpy,subprocess,sys
from collections import Counter
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
K=json.loads((HERE/'integration-v1.json').read_bytes())
OUTPUT='UNRESOLVED-STARTUP-SAFE-GAP.o'

def need(ok,label):
    if not ok:raise ValueError(label)

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def lib(p):return runpy.run_path(str(ROOT/p),run_name='safe_gap_component_library')
Q=lib('experiments/tsl9-safe-gap-functions/verify-source-v1.py')
portable,encoded,E=Q['portable'],Q['encoded'],Q['E']

def paths(mode):
    return [ROOT/K['parent_component']/mode/K['parent_object'],ROOT/K['curation_folder']/'safe-gap-functions'/mode/'curated/unit.o']

def inventory(folder):return {p.name:dict(bytes=p.stat().st_size,sha256=sha(p))for p in sorted(folder.iterdir())if p.is_file()}

def globals_of(e):
    rows=[s for s in e.symbols if s['info']>>4];result={s['name']:s for s in rows}
    need(len(rows)==len(result) and not any(s['section']==0xfff1 for s in rows),'Unique real globals without ABS substitutes')
    return result

def source_proof(llvm):
    for p,h in K['pins'].items():need(sha(ROOT/p)==h,'Pinned source integration input '+p)
    need(sha(llvm/'ld.lld.exe')=='fe7f55c0c78b3d87f33b905a3874e10e872ca7beef53a8199d7ff9ac6641ec3f','Pinned actual linker')
    saved=json.loads((ROOT/K['source_receipt']).read_bytes())
    need(saved['inputs']==portable(Q['inputs'](llvm),llvm),'Every actual complete source input retained')
    proof=Q['proof'](llvm)
    need(proof==saved['result'] and proof['source_curated'] and proof['source_C_H_files']==159 and proof['total_source_comparisons']==266 and proof['total_source_objects']==532,'Fresh complete159-file proof')
    for mode in ['c','cpp']:need(sha(paths(mode)[0])==K['parent_sha256'],'Exact source-proven accepted parent')
    return proof

def audit_component(path,mode):
    ins=[E(p)for p in paths(mode)];out=E(path);maps=[globals_of(e)for e in ins];gm=globals_of(out)
    need(out.header[0]==1 and out.header[1]==243 and not out.program_headers,'Actual nonloadable RV32 ET_REL')
    need(set(gm)==set().union(*(set(m)for m in maps)),'Exact combined global inventory')
    alloc={}
    for e in ins:
        for sec in e.sections:
            if not(sec['flags']&2 and sec['size']):continue
            need(sec['name']not in alloc,'Distinct genuine source allocations')
            alloc[sec['name']]=(sec['type'],sec['flags'],sec['size'],sec['align'])
            need(out.data(sec['name'])==e.data(sec),'Every accepted and new allocated byte retained')
    need({s['name']:(s['type'],s['flags'],s['size'],s['align'])for s in out.sections if s['flags']&2 and s['size']}==alloc,'Only actual parent plus new CODE allocations')
    def role(s,e):return (s['name'],s['info'],s['other'],s['value'],s['size'],e.sections[s['section']]['name']if s['section']else '')
    for e,m in zip(ins,maps):
        for name,s in m.items():
            if s['section']:need(role(gm[name],out)==role(s,e),'Every definition and real alias keeps backing')
            elif not gm[name]['section']:need(role(gm[name],out)==role(s,e),'Every remaining UND stays explicit')
    expected=Counter()
    for e in ins:
        for r in e.relocations:
            target=e.symbols[r['symbol']];resolved=role(gm[target['name']],out)if target['info']>>4 else role(target,e)
            expected[(e.sections[r['section']]['name'],r['offset'],r['type'],r['addend'],resolved)]+=1
    actual=Counter((out.sections[r['section']]['name'],r['offset'],r['type'],r['addend'],role(out.symbols[r['symbol']],out))for r in out.relocations)
    need(expected==actual and len(out.relocations)==5270,'Every5215 accepted and55 new reference roles retained')
    parent,extension=maps;prior_und={n for n,s in parent.items()if not s['section']};after={n for n,s in gm.items()if not s['section']}
    need(len(prior_und)==6 and after==prior_und,'The exact same six genuine compiler UND remain')
    extension_und={n for n,s in extension.items()if not s['section']}
    need(len(extension_und)==17 and all(n in parent and parent[n]['info']==18 and parent[n]['size']>0 and parent[n]['section']for n in extension_und),'All17 new UND bind to actual positive parent FUNC providers')
    functions=[s for s in gm.values()if s['section']and s['info']==18 and s['size']]
    objects=[s for s in gm.values()if s['section']and s['info']==17 and s['size']]
    need(len(functions)==6182 and sum(s['size']for s in functions)==69412,'All6182 positive FUNC owners and69412 CODE bytes')
    need(len(objects)==56 and sum(s['size']for s in objects)==3962,'All56 positive DATA owners and3962 DATA bytes retained')
    aliases={n for n,s in gm.items()if s['section']and s['info']==18 and not s['size']}
    labels={n for n,s in gm.items()if s['section']and s['info']==17 and not s['size']}
    need(aliases=={n for n,s in parent.items()if s['section']and s['info']==18 and not s['size']}and len(aliases)==71,'All71 actual CODE aliases unchanged')
    need(labels=={n for n,s in parent.items()if s['section']and s['info']==17 and not s['size']}and len(labels)==6,'All six genuine DATA labels unchanged')
    need(sum(s['size']for s in out.sections if s['flags']&2)==73374,'Every73374 allocated byte owned without invented padding')
    comparison=lib('experiments/tsl9-remaining-record-dispatch/compare-readers-v1.py')['audit'](path)
    need(comparison['passed'],'Independent actual ELF readers agree')
    return dict(passed=True,CODE_bytes=69412,DATA_bytes=3962,positive_FUNC=6182,positive_DATA_OBJECTs=56,
        true_CODE_aliases=71,real_DATA_labels=6,RELA=5270,UND=sorted(after),resolved_existing_CODE_providers=17,
        all_parent_allocations_and_relocation_roles_preserved=True,independent_readers=comparison,object_sha256=sha(path),
        curated_integration=True,source_curated=True,source_C_H_files=159,source_comparisons=266,source_objects=532,CODE_units=125,DATA_units=8,
        new_CODE_bytes=764,new_original_instructions=288,new_DATA_bytes=0,
        previous_accepted_coordinate_coverage_percent=94.54,accepted_original_coordinate_coverage_updated=False,original_coordinate_link_performed=False,
        hidden_existing_DATA_dependency=0x1aae8,hidden_index_globally_bounded=False,compiler_UND_is_not_complete_runtime_gap_inventory=True,
        candidate_runtime_invocations_proved=False,installed_ROM_ABI_verified=False,
        target_executed=False,HOST_model_executed=False,ISA_emulated=False,hardware_accessed=False,network=False,new_BIN=False,firmware_ready=False)

def inputs(llvm):
    result=Q['inputs'](llvm)
    for p in [Path(__file__),HERE/'integration-v1.json',ROOT/K['source_receipt'],*[ROOT/p for p in K['pins']]]:
        result[str(p)]=dict(bytes=p.stat().st_size,sha256=sha(p))
    return result

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--tool-dir',type=Path,required=True)
    group=p.add_mutually_exclusive_group(required=True);group.add_argument('--trial');group.add_argument('--replay',type=Path)
    a=p.parse_args();llvm=a.tool_dir.resolve();proof=source_proof(llvm);before=portable(inputs(llvm),llvm)
    if a.replay:
        out=a.replay.resolve();need(out.parent==HERE/'build','Owned retained component trial')
        saved=json.loads((out/'measurement.json').read_bytes());need(saved['inputs']==before and saved['source_proof']==proof,'Exact retained component inputs')
        for mode in ['c','cpp']:
            folder=out/mode;need(saved['modes'][mode]['artifacts']==inventory(folder),'Complete retained component outputs')
            need(saved['modes'][mode]['result']==audit_component(folder/OUTPUT,mode),'Actual component replay')
        print(json.dumps(dict(passed=True,source_C_H_files=159,CODE_bytes=69412,DATA_bytes=3962,compiler_UND=6,target_executed=False)));return
    need(a.trial and Path(a.trial).name==a.trial,'Single owned trial name');out=HERE/'build'/a.trial;need(not out.exists(),'Create-only component folder')
    report=dict(inputs=before,source_proof=proof,modes={})
    for mode in ['c','cpp']:
        folder=out/mode;folder.mkdir(parents=True)
        argv=[str(llvm/'ld.lld.exe'),'-m','elf32lriscv','-r','--no-relax','-o',str(folder/OUTPUT),*[str(p)for p in paths(mode)]]
        result=subprocess.run(argv,capture_output=True,timeout=120)
        (folder/'link.log').write_text(portable(result.stderr.decode('utf-8','replace'),llvm),encoding='utf-8')
        need(result.returncode==0,'Actual native link failed; local diagnostic retained')
        report['modes'][mode]=dict(result=audit_component(folder/OUTPUT,mode),command=portable(argv,llvm),artifacts=inventory(folder))
    need(report['modes']['c']['result']['object_sha256']==report['modes']['cpp']['result']['object_sha256'],'Identical actual C/C++ components')
    need(before==portable(inputs(llvm),llvm),'Every input unchanged during actual link')
    (out/'measurement.json').write_bytes(encoded(report))
    print(json.dumps({k:v for k,v in report['modes']['c']['result'].items()if k!='independent_readers'}))

if __name__=='__main__':
    try:main()
    except Exception as error:
        message=str(error)
        for path,token in [(ROOT,'${PROJECT_ROOT}'),(Path.home(),'${USERPROFILE}')]:message=message.replace(str(path),token).replace(path.as_posix(),token)
        print(json.dumps(dict(passed=False,error_type=type(error).__name__,reason=message)));raise SystemExit(1)
