"""Verify one additive readonly DATA source while preserving the exact parent composite proof."""
import argparse,hashlib,json,runpy,sys
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def need(ok,label):
    if not ok:raise ValueError(label)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def lib(p):return runpy.run_path(str(ROOT/p),run_name='readonly_source_extension_library')
B=lib('experiments/tsl9-original-startup/build-v1.py');portable,encoded=B['portable'],B['encoded']
def expand(value,llvm):
    for key,path in [('PROJECT_ROOT',ROOT),('LLVM_BIN',llvm),('CLANG_RESOURCE',llvm.parent/'lib/clang/18')]:value=value.replace('${'+key+'}',str(path))
    return Path(value)
def inputs(llvm):
    K=read(HERE/'source-proof-v1.json');parent=read(HERE/'parent-proof-v1.json');files={Path(__file__),HERE/'source-proof-v1.json',HERE/'parent-proof-v1.json',ROOT/'src/source-manifest.json'}
    files.update(ROOT/p for p in K['pins']);files.update(expand(p,llvm)for p in parent['parent_input_inventory']);C=lib('scripts/verify-curated-source.py');files.update(Path(p)for p in C['inputs'](C['metadata']()));V=lib(K['DATA_builder']);files.update(Path(p)for p in V['inputs'](llvm,['origin','curated']));receipt=HERE/'build/data-v1/measurement.json';files.add(receipt);saved=read(receipt)
    for mode in ['c','cpp']:
        for variant in ['origin','curated']:files.update(receipt.parent/mode/variant/p for p in saved['modes'][mode][variant]['artifacts'])
    return {str(p):dict(bytes=p.stat().st_size,sha256=sha(p))for p in sorted(files)}
def proof(llvm):
    K=read(HERE/'source-proof-v1.json');parent_counts=K['parent_counts'];counts=K['counts']
    for p,h in K['pins'].items():need(sha(ROOT/p)==h,'Frozen source-extension input '+p)
    ext=read(HERE/'source-extension-v1.json');parent=read(HERE/'parent-proof-v1.json');raw=lib(K['parent_manifest_helper'])['raw_parent']();need(hashlib.sha256(raw).hexdigest()==ext['previous_manifest_sha256']==parent['parent_manifest_sha256'],'Exact frozen parent manifest bytes')
    expected=json.loads(raw)
    for group,key in [('files','new_file_entries'),('native_units','new_CODE_unit_entries'),('native_data_units','new_DATA_unit_entries')]:expected[group]+=ext[key]
    need(len(ext['new_file_entries'])==len(ext['new_DATA_unit_entries'])==1 and not ext['new_CODE_unit_entries'],'Only one source and one DATA unit appended')
    need(sha(ROOT/'src/source-manifest.json')==ext['new_manifest_sha256']and expected==read(ROOT/'src/source-manifest.json'),'Exact additive current manifest;all old entries retained')
    C=lib('scripts/verify-curated-source.py');m=C['metadata']();need([len(m['files']),len(m['native_units']),len(m['native_data_units'])]==counts[:3],'Complete current source/CODE/DATA inventory')
    p=parent['parent_result'];need(parent['passed']and parent['composite_proof_replayed_before_extension']and[p['source_C_H_files'],p['CODE_units'],p['independent_DATA_units'],p['total_source_comparisons'],p['total_source_objects']]==parent_counts,'Exact replayed parent composite provenance;no full-reparse claim')
    exceptions=[]
    for key,pin in parent['parent_input_inventory'].items():
        path=expand(key,llvm)
        if path==ROOT/'src/source-manifest.json':need(pin==dict(bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest()),'Only exact parent manifest exception');exceptions.append(key)
        else:need(path.is_file()and path.stat().st_size==pin['bytes']and sha(path)==pin['sha256'],'Every prior source/tool/artifact input retained')
    need(len(exceptions)==1 and len(parent['source_files'])==parent_counts[0]and all(sha(ROOT/p)==h for p,h in parent['source_files'].items()),'One manifest exception and all actual parent source files retained')
    V=lib(K['DATA_builder']);data=V['run'](llvm,replay=HERE/'build/data-v1');need(data['variants']==['origin','curated'],'Both actual DATA source variants')
    need(all(data['modes'][mode][variant]['result']['DATA_bytes']==K['new_DATA_bytes']and data['modes'][mode][variant]['result']['CODE_bytes']==0 for mode in ['c','cpp']for variant in ['origin','curated']),'All four actual objects contain only the selected readonly DATA')
    code_comparisons=2*counts[1];code_objects=4*counts[1];data_comparisons=2*counts[2];data_objects=4*counts[2]
    need(counts[3:]==[code_comparisons+data_comparisons,code_objects+data_objects]and counts[0]==parent_counts[0]+1 and counts[1]==parent_counts[1]and counts[2]==parent_counts[2]+1 and counts[3]==parent_counts[3]+2 and counts[4]==parent_counts[4]+4,'Exact additive provenance arithmetic')
    return dict(passed=True,source_C_H_files=counts[0],CODE_units=counts[1],independent_DATA_units=counts[2],CODE_comparisons=code_comparisons,CODE_objects=code_objects,DATA_comparisons=data_comparisons,DATA_objects=data_objects,total_source_comparisons=counts[3],total_source_objects=counts[4],parent_source_files_retained=parent_counts[0],parent_comparisons_retained=parent_counts[3],parent_objects_retained=parent_counts[4],parent_inputs_rehashed=len(parent['parent_input_inventory']),parent_composite_proof_replayed_before_extension=True,parent_source_proof_rerun_after_extension=False,original532_object_proof_retained=True,all_parent_objects_reparsed_now=False,new_DATA_comparisons=2,new_DATA_objects=4,new_DATA_bytes=K['new_DATA_bytes'],new_CODE_bytes=0,parent_proof_sha256=sha(HERE/'parent-proof-v1.json'),new_DATA_receipt_sha256=sha(HERE/'build/data-v1/measurement.json'),source_curated=True,global_state_invariant_proved=False,full_provider_binding_justified=False,original_coordinate_link_performed=False,physical_MCU_ROM_RAM_IRQ_OTA_proved=False,target_executed=False,HOST_model_executed=False,ISA_emulated=False,hardware_accessed=False,network=False,new_BIN=False,firmware_ready=False)
def main():
    p=argparse.ArgumentParser();p.add_argument('--tool-dir',type=Path,required=True);a=p.parse_args();llvm=a.tool_dir.resolve();before=portable(inputs(llvm),llvm);v=proof(llvm);need(before==portable(inputs(llvm),llvm),'All extended source inputs unchanged during proof');dest=HERE/'build/source-proof-v1.json';need(not dest.exists(),'Create-only extended source receipt');dest.write_bytes(encoded(dict(inputs=before,result=v)));print(json.dumps(v))
if __name__=='__main__':
    try:main()
    except Exception as error:
        message=str(error)
        for p,t in [(ROOT,'${PROJECT_ROOT}'),(Path.home(),'${USERPROFILE}')]:message=message.replace(str(p),t).replace(p.as_posix(),t)
        print(json.dumps(dict(passed=False,error_type=type(error).__name__,reason=message)));raise SystemExit(1)
