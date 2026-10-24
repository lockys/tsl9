#!/usr/bin/env python3
"""Positive offline proof of the exact 127-to-128 source extension. No target execution."""
import argparse,hashlib,json,runpy,subprocess,sys
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
K=json.loads((HERE/'source-proof-v1.json').read_bytes())

def need(ok,label):
    if not ok:raise ValueError(label)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def library(rel):return runpy.run_path(str(ROOT/rel),run_name='positive_static_library')
N=library('experiments/tsl9-record-helpers/build-v1.py')
P=library('experiments/tsl9-record-actions/integrate-v1.py')
D=library('experiments/tsl9-original-vectors/build-v1.py')
portable,encoded=N['portable'],N['encoded']
def expand(value,llvm):
    for key,path in [('PROJECT_ROOT',ROOT),('LLVM_BIN',llvm),('CLANG_RESOURCE',llvm.parent/'lib/clang/18')]:
        value=value.replace('$'+'{'+key+'}',str(path))
    return Path(value)
def parent(mode):return ROOT/K['parent_component']/mode/K['parent_object']
def inventory(folder):return {p.name:dict(bytes=p.stat().st_size,sha256=sha(p))for p in sorted(folder.iterdir())if p.is_file()}
def inputs(llvm):
    paths={Path(__file__),HERE/'source-proof-v1.json',ROOT/'src/source-manifest.json'}
    paths.update(ROOT/p for p in K['pins'])
    paths.update(Path(p)for p in N['inputs'](llvm))
    record=json.loads((ROOT/K['parent_component']/'measurement.json').read_bytes())
    paths.update(expand(p,llvm)for p in record['inputs'])
    data=json.loads((ROOT/K['data_receipt']).read_bytes())
    paths.update(Path(p)for p in D['inputs'](llvm,data['variants']))
    for mode in ('c','cpp'):paths.add(parent(mode))
    return {str(p):dict(bytes=p.stat().st_size,sha256=sha(p))for p in sorted(paths)}

def proof(llvm):
    for p,pin in K['pins'].items():need(sha(ROOT/p)==pin,'Pinned proof input '+p)
    ext=json.loads((HERE/'source-extension-v1.json').read_bytes())
    old=library('experiments/tsl9-record-helpers/parent-manifest-v1.py')['raw_parent']()
    need(hashlib.sha256(old).hexdigest()==ext['previous_manifest_sha256'],'Exact retained 127-file manifest')
    current=ROOT/'src/source-manifest.json'
    need(sha(current)==ext['new_manifest_sha256'],'Exact extended manifest bytes')
    expected=json.loads(old)
    expected['files'].append(ext['new_file_entry'])
    expected['native_units'].append(ext['new_unit_entry'])
    need(expected==json.loads(current.read_bytes()),'Only one source and one unit appended')
    reader_check=json.loads((ROOT/K['reader_proof']).read_bytes())
    need(reader_check==library('experiments/tsl9-registered-callbacks/verify-reader-v1.py')['proof'](),'Independent positive613-section parser comparison')
    C=library('scripts/verify-curated-source.py')
    metadata=C['metadata']()
    need(len(metadata['files'])==128 and len(metadata['native_units'])==101 and len(metadata['native_data_units'])==1,'Complete current source scope')
    previous=json.loads((ROOT/K['previous_curation']).read_bytes())
    now=json.loads((ROOT/K['curation']).read_bytes())
    need(len(previous['results'])==200 and len(now['results'])==202 and now['results'][:200]==previous['results'],'All prior 200 projections unchanged')
    need(len(previous['artifacts'])==1201 and len(now['artifacts'])==1213 and all(now['artifacts'].get(p)==pin for p,pin in previous['artifacts'].items()),'All prior 1201 artifact records unchanged')
    base=(ROOT/K['curation']).parent
    need(now['artifacts']==C['inventory'](base),'Complete current curation artifact inventory')
    need(C['audit'](base,now,metadata)==now['results'],'All actual current source-object projections replayed')
    native=json.loads((ROOT/K['native_receipt']).read_bytes())
    need(native['inputs']==portable(N['inputs'](llvm),llvm),'All standalone native producer inputs unchanged')
    parent_record=json.loads((ROOT/K['parent_component']/'measurement.json').read_bytes())
    exceptions=[]
    for key,pin in parent_record['inputs'].items():
        p=expand(key,llvm)
        if p==current:
            need(pin['sha256']==ext['previous_manifest_sha256'] and pin['bytes']==len(old),'Only exact manifest extension exception')
            exceptions.append('src/source-manifest.json')
        else:
            need(p.is_file() and p.stat().st_size==pin['bytes'] and sha(p)==pin['sha256'],'Every other recorded parent input unchanged')
    need(exceptions==['src/source-manifest.json'],'Exactly one retained-parent input extension')
    data=json.loads((ROOT/K['data_receipt']).read_bytes())
    need(data['variants']==['origin','curated'] and data['inputs']==portable(D['inputs'](llvm,data['variants']),llvm),'Unchanged independent data inputs')
    result={}
    for mode in ('c','cpp'):
        job=native['modes'][mode];folder=(ROOT/K['native_receipt']).parent/mode
        need(N['inventory'](folder)==job['artifacts'],'Complete native leaf output inventory')
        need(N['audit_object'](folder/'unit.o')==job['result'],'Actual standalone910B state/control code original-code audit')
        need(portable(N['dependencies'](folder,llvm),llvm)==job['dependencies'],'Every standalone compiler dependency')
        curated=base/'record-helpers'/mode/'curated/unit.o'
        fact=N['audit_object'](curated)
        need(fact==dict(job['result'],native_object_sha256=sha(curated)),'Actual curated910B state/control code original-code audit')
        need(sha(parent(mode))==K['parent_object_sha256'],'Unchanged retained startup component')
        need(P['inventory'](parent(mode).parent)==parent_record['modes'][mode]['artifacts'],'Complete retained parent artifacts unchanged')
        pf=P['audit_component'](parent(mode),mode)
        need(pf==parent_record['modes'][mode]['result'],'Positive whole retained startup/table component audit')
        for variant in ('origin','curated'):
            f=(ROOT/K['data_receipt']).parent/mode/variant;j=data['modes'][mode][variant]
            need(D['inventory'](f)==j['artifacts'] and D['audit_object'](f/'unit.o')==j['result'],'Independent pointer-data actual artifact audit')
            need(portable(D['dependencies'](f,variant,llvm),llvm)==j['dependencies'],'Independent data dependencies')
        need(D['complete_projection_equal']((ROOT/K['data_receipt']).parent/mode/'origin/unit.o',(ROOT/K['data_receipt']).parent/mode/'curated/unit.o'),'Independent pointer-data projections equal')
        candidates={}
        for unit,helper in [('state-access','experiments/tsl9-state-access/build-v1.py'),('feature-callback','experiments/tsl9-feature-callback/build-v4.py'),('state-events','experiments/tsl9-state-events/build-v2.py')]:
            H=library(helper);u=next(u for u in metadata['native_units']if u['name']==unit)
            need(sha(ROOT/u['origin_unit'])==H['S']['source_sha256'],'Correct accepted provider version')
            q=H['audit_object'](base/unit/mode/'curated/unit.o')
            candidates[unit]={k:q[k]for k in ('passed','code_bytes','instructions','FUNC','RELA','native_object_sha256')}
        need([candidates[u]['code_bytes']for u in ('state-access','feature-callback','state-events')]==[336,314,1308],'Complete future provider scope')
        result[mode]=dict(record_helpers=fact,parent_component=pf,candidate_original_byte_audits=candidates)
    return dict(passed=True,source_C_H_files=128,native_code_units=101,independent_data_units=1,
        function_source_comparisons=202,function_source_objects=404,
        independent_data_comparisons=2,independent_data_objects=4,
        total_source_comparisons=204,total_source_objects=408,
        prior200_results_and1201_artifact_records_unchanged=True,
        exact127_to128_manifest_extension=True,retained_parent_manifest_only_exception=True,
        retained_parent_whole_manifest_replay_claimed=False,retained_parent_positive_audit_passed=True,
        modes=result,independent_large_ELF_reader_comparison_passed=True,providers_merged_into_startup_component=False,firmware_ready=False,firmware_BIN_generated=False,
        target_executed=False,HOST_model_executed=False,ISA_emulated=False,hardware_accessed=False,network=False,negative_cases_executed=0)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--tool-dir',required=True,type=Path)
    g=p.add_mutually_exclusive_group(required=True)
    g.add_argument('--output',type=Path);g.add_argument('--replay',type=Path)
    a=p.parse_args();llvm=a.tool_dir.resolve()
    before=portable(inputs(llvm),llvm);facts=proof(llvm)
    need(before==portable(inputs(llvm),llvm),'All actual inputs unchanged during positive proof')
    report=dict(schema='TSL9-record-helpers-source-extension-proof-v1',inputs=before,result=facts)
    if a.replay:
        need(a.replay.resolve().is_relative_to(HERE/'build'),'Owned retained proof')
        need(json.loads(a.replay.read_bytes())==report,'Exact positive proof replay')
    else:
        need(a.output.resolve().parent==HERE/'build' and not a.output.exists(),'Create-only local proof')
        a.output.write_bytes(encoded(report))
    print(json.dumps({k:v for k,v in facts.items()if k!='modes'}))
if __name__=='__main__':
    try:main()
    except Exception as e:
        msg=str(e)
        for path,token in [(ROOT,'$'+'{PROJECT_ROOT}'),(Path.home(),'$'+'{USERPROFILE}')]:
            msg=msg.replace(str(path),token).replace(path.as_posix(),token)
        print(json.dumps(dict(passed=False,error_type=type(e).__name__,error=msg)),file=sys.stderr)
        sys.exit(1)
