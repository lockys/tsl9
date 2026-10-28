"""Integrate the source-proven32-byte DATA extension with all real APP component roles."""
import argparse,hashlib,json,runpy,subprocess,sys
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];K=json.loads((HERE/'integration-v1.json').read_bytes());OUTPUT='UNRESOLVED-STARTUP-MODE-ROWS-DATA.o'
def need(ok,label):
    if not ok:raise ValueError(label)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def lib(p):return runpy.run_path(str(ROOT/p),run_name='lookup_source_component_library')
Q=lib('experiments/tsl9-record-mode-row-integration/verify-source-v1.py');portable,encoded=Q['portable'],Q['encoded'];E=lib(K['reader'])['ELF']
def paths(mode):return [ROOT/K['parent_component']/mode/K['parent_object'],HERE/'build/data-v1'/mode/'curated/unit.o']
def inventory(folder):return {p.name:dict(bytes=p.stat().st_size,sha256=sha(p))for p in sorted(folder.iterdir())if p.is_file()}
def source_proof(llvm):
    for p,h in K['pins'].items():need(sha(ROOT/p)==h,'Frozen source integration input '+p)
    need(sha(llvm/'ld.lld.exe')==K['lld_sha256'],'Pinned actual linker');saved=json.loads((HERE/'build/source-proof-v1.json').read_bytes());need(saved['inputs']==portable(Q['inputs'](llvm),llvm),'Every complete163-source input retained');proof=Q['proof'](llvm);need(proof==saved['result'],'Fresh additive163-source proof equals successful receipt')
    for mode in ['c','cpp']:need(sha(paths(mode)[0])==K['parent_sha256']and sha(paths(mode)[1])==K['curated_DATA_sha256'],'Exact real source-parent and curated DATA object')
    return proof
def audit_component(path,mode):
    F=lib('experiments/tsl9-sdk-unique-code-ownership/audit-v1.py');ins=paths(mode);a,d,u,r=F['facts'](ins[0],E);aa,dd,uu,rr=F['facts'](ins[1],E);need(not set(a)&set(aa)and not set(d)&set(dd)and not uu and not rr,'Unique readonly extension without new imports/relocations')
    out=E(path);need(F['facts'](path,E)==({**a,**aa},{**d,**dd},u-set(dd),sorted(r+rr)),'Every input allocated byte,global definition and typed relocation retained')
    need(len(u)==6 and not set(dd)&u and len(out.relocations)==5270,'Same six genuine imports and all5270 relocation roles')
    f=[s for s in out.symbols if s['info']==18 and s['size']];data=[s for s in out.symbols if s['info']==17 and s['size']]
    need((len(f),sum(s['size']for s in f),len(data),sum(s['size']for s in data))==(6182,69412,63,4098),'All old6182 CODE owners,61 old DATA and two new DATA owners')
    labels=[s for s in out.symbols if s['info']==17 and not s['size']and s['section']];aliases=[s for s in out.symbols if s['info']==18 and not s['size']and s['section']];need(len(labels)==6 and len(aliases)==71,'Existing DATA labels and CODE aliases retained; no new provider alias')
    need(out.header[0]==1 and not out.program_headers and sum(s['size']for s in out.sections if s['flags']&2)==73510,'Actual nonloadable ET_REL with exactly73510 allocated bytes')
    comparison=lib('experiments/tsl9-remaining-record-dispatch/compare-readers-v1.py')['audit'](path);need(comparison['passed'],'Independent complete ELF readers agree')
    return dict(passed=True,CODE_bytes=69412,DATA_bytes=4098,positive_FUNC=6182,positive_DATA_OBJECTs=63,true_CODE_aliases=71,real_DATA_labels=6,RELA=5270,UND=sorted(u),object_sha256=sha(path),independent_readers=comparison,all_parent_allocations_global_symbols_and_relocation_roles_retained=True,curated_integration=True,source_curated=True,source_C_H_files=163,source_comparisons=274,source_objects=548,CODE_units=125,DATA_units=12,new_CODE_bytes=0,new_DATA_bytes=32,original_coordinate_link_performed=False,full_provider_binding_justified=False,global_state_invariant_proved=False,target_executed=False,HOST_model_executed=False,ISA_emulated=False,hardware_accessed=False,network=False,new_BIN=False,firmware_ready=False)
def inputs(llvm):
    result=Q['inputs'](llvm)
    for p in [Path(__file__),HERE/'integration-v1.json',HERE/'build/source-proof-v1.json',*[ROOT/p for p in K['pins']],*paths('c'),*paths('cpp')]:result[str(p)]=dict(bytes=p.stat().st_size,sha256=sha(p))
    return result
def main():
    p=argparse.ArgumentParser();p.add_argument('--tool-dir',type=Path,required=True);g=p.add_mutually_exclusive_group(required=True);g.add_argument('--trial');g.add_argument('--replay',type=Path);a=p.parse_args();llvm=a.tool_dir.resolve();proof=source_proof(llvm);before=portable(inputs(llvm),llvm);out=HERE/'build'/(a.trial if a.trial else'component-v1')
    if a.trial:need(Path(a.trial).name==a.trial and not out.exists(),'Create-only real source component')
    else:need(a.replay.resolve()==out,'Owned retained component replay')
    report=dict(schema='TSL9-source-curated-mode-row-DATA-component-v1',inputs=before,source_proof=proof,modes={})
    for mode in ['c','cpp']:
        folder=out/mode
        if a.trial:
            folder.mkdir(parents=True);p=subprocess.run([str(llvm/'ld.lld.exe'),'-m','elf32lriscv','-r','--no-relax',*[str(p)for p in paths(mode)],'-o',str(folder/OUTPUT)],capture_output=True,timeout=120);(folder/'link.log').write_text(portable((p.stdout+p.stderr).decode('utf-8','replace'),llvm),encoding='utf-8');need(p.returncode==0,'Actual source-proven partial link;log retained')
        report['modes'][mode]=dict(result=audit_component(folder/OUTPUT,mode),artifacts=inventory(folder))
    need(report['modes']['c']==report['modes']['cpp'],'Actual full C/C++ component identical');need(before==portable(inputs(llvm),llvm),'Every component input retained')
    if a.trial:(out/'measurement.json').write_bytes(encoded(report))
    else:need(report==json.loads((out/'measurement.json').read_bytes()),'Exact retained component replay')
    print(json.dumps(dict(passed=True,source_C_H_files=163,source_comparisons=274,source_objects=548,CODE_bytes=69412,DATA_bytes=4098,compiler_UND=6,object_sha256=report['modes']['c']['result']['object_sha256'],new_BIN=False)))
if __name__=='__main__':
    try:main()
    except Exception as error:
        message=str(error)
        for p,t in [(ROOT,'${PROJECT_ROOT}'),(Path.home(),'${USERPROFILE}')]:message=message.replace(str(p),t).replace(p.as_posix(),t)
        print(json.dumps(dict(passed=False,error_type=type(error).__name__,reason=message)));raise SystemExit(1)
