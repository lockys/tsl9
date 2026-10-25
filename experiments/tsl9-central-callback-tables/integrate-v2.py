"""Link the source-proven curated CODE/DATA extension without target execution."""
import argparse,hashlib,json,runpy,subprocess,sys
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
K=json.loads((HERE/'integration-v2.json').read_text())
OUTPUT='UNRESOLVED-STARTUP-CENTRAL-CALLBACKS.o'
def need(ok,label):
    if not ok:raise ValueError(label)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def lib(p):return runpy.run_path(str(ROOT/p),run_name='curated_central_component_library')
Q=lib('experiments/tsl9-central-callback-tables/verify-source-v2.py')
D=lib(K['retention_checker'])
portable,encoded=Q['portable'],Q['encoded']
def paths(mode):
    return [ROOT/K['parent_component']/mode/K['parent_object'],
            *[ROOT/K['curation_folder']/unit/mode/'curated/unit.o' for unit in K['CODE_units']],
            ROOT/K['DATA_folder']/mode/'curated/unit.o']
def inventory(folder):return {p.name:dict(bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(folder.iterdir()) if p.is_file()}
def source_proof(llvm):
    for p,h in K['pins'].items():need(sha(ROOT/p)==h,'Pinned source integration input '+p)
    saved=json.loads((ROOT/K['source_receipt']).read_text())
    need(saved['inputs']==portable(Q['inputs'](llvm),llvm),'Every full source-proof input unchanged')
    proof=Q['proof'](llvm)
    need(proof==saved['result'] and proof['total_source_comparisons']==260 and proof['total_source_objects']==520 and proof['source_C_H_files']==156,'Fresh complete156-file source proof')
    for mode in ['c','cpp']:need(sha(paths(mode)[0])==K['parent_sha256'],'Exact accepted parent component')
    return proof
def audit_component(path,mode):
    measured=D['audit'](path,mode)
    need(measured['passed'] and measured['CODE_bytes']==66600 and measured['DATA_bytes']==3922 and measured['RELA']==4972 and len(measured['UND'])==6,'Exact whole curated component role retention')
    need(measured['real_DATA_labels']==6 and measured['true_CODE_aliases']==71 and not measured['unprovided_candidate_callback_CODE_targets'],'Every real alias and callback CODE backing retained')
    measured={k:v for k,v in measured.items() if k!='formal_coverage_percent'}
    return measured|dict(curated_integration=True,source_curated=True,source_C_H_files=156,
                         source_comparisons=260,source_objects=520,CODE_units=123,DATA_units=7,
                         new_CODE_bytes=2056,new_original_instructions=686,new_DATA_bytes=92,
                         previous_accepted_coordinate_coverage_percent=89.03,
                         accepted_original_coordinate_coverage_updated=False,
                         original_coordinate_link_performed=False,firmware_ready=False)
def inputs(llvm):
    values=Q['inputs'](llvm)
    for p in [Path(__file__),HERE/'integration-v2.json',ROOT/K['source_receipt'],*[ROOT/p for p in K['pins']]]:
        values[str(p)]=dict(bytes=p.stat().st_size,sha256=sha(p))
    return values
def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--tool-dir',type=Path,required=True)
    group=parser.add_mutually_exclusive_group(required=True);group.add_argument('--trial');group.add_argument('--replay',type=Path)
    args=parser.parse_args();llvm=args.tool_dir.resolve();proof=source_proof(llvm);before=portable(inputs(llvm),llvm)
    if args.replay:
        out=args.replay.resolve();need(out.parent==HERE/'build','Owned current component trial')
        saved=json.loads((out/'measurement.json').read_text());need(saved['inputs']==before and saved['source_proof']==proof,'Exact retained source/component inputs')
        for mode in ['c','cpp']:
            folder=out/mode;need(saved['modes'][mode]['artifacts']==inventory(folder),'Complete retained native component artifacts')
            need(saved['modes'][mode]['result']==audit_component(folder/OUTPUT,mode),'Actual curated component replay')
        print(json.dumps(dict(passed=True,source_C_H_files=156,code_bytes=66600,data_bytes=3922,UND=6,source_curated=True,target_executed=False)));return
    need(args.trial and Path(args.trial).name==args.trial,'Single owned trial name');out=HERE/'build'/args.trial
    need(not out.exists(),'Create-only curated component output')
    report=dict(inputs=before,source_proof=proof,modes={})
    for mode in ['c','cpp']:
        folder=out/mode;folder.mkdir(parents=True)
        argv=[str(llvm/'ld.lld.exe'),'-m','elf32lriscv','-r','--no-relax','-o',str(folder/OUTPUT),*[str(p) for p in paths(mode)]]
        result=subprocess.run(argv,capture_output=True,timeout=120)
        (folder/'link.log').write_text(portable(result.stderr.decode('utf-8',errors='replace'),llvm),encoding='utf-8')
        need(result.returncode==0,'Curated native link failed; local diagnostic retained')
        facts=audit_component(folder/OUTPUT,mode)
        report['modes'][mode]=dict(result=facts,command=portable(argv,llvm),artifacts=inventory(folder))
    need(report['modes']['c']['result']['object_sha256']==report['modes']['cpp']['result']['object_sha256'],'Identical curated C/C++ components')
    need(before==portable(inputs(llvm),llvm),'Every actual source input unchanged during link')
    (out/'measurement.json').write_bytes(encoded(report))
    print(json.dumps({k:v for k,v in report['modes']['c']['result'].items() if k not in ['table_CODE_bindings','independent_readers']}))
if __name__=='__main__':main()
