"""Extend the freshly verified159-source/532-object proof with four real DATA objects."""
import argparse,hashlib,json,runpy,sys
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def need(ok,label):
    if not ok:raise ValueError(label)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def lib(p):return runpy.run_path(str(ROOT/p),run_name='lookup_extended_source_library')
B=lib('experiments/tsl9-original-startup/build-v1.py');portable,encoded=B['portable'],B['encoded']
def expand(value,llvm):
    for key,path in [('PROJECT_ROOT',ROOT),('LLVM_BIN',llvm),('CLANG_RESOURCE',llvm.parent/'lib/clang/18')]:value=value.replace('${'+key+'}',str(path))
    return Path(value)
def inputs(llvm):
    K=read(HERE/'source-proof-v1.json');parent=read(HERE/'parent-proof-v1.json');files={Path(__file__),HERE/'source-proof-v1.json',HERE/'parent-proof-v1.json',ROOT/'src/source-manifest.json'}
    files.update(ROOT/p for p in K['pins']);files.update(expand(p,llvm)for p in parent['parent_input_inventory']);C=lib('scripts/verify-curated-source.py');files.update(Path(p)for p in C['inputs'](C['metadata']()))
    V=lib('experiments/tsl9-lookup-mode-integration/build-data-v1.py');files.update(Path(p)for p in V['inputs'](llvm,['origin','curated']))
    receipt=HERE/'build/data-v1/measurement.json';files.add(receipt);saved=read(receipt)
    for mode in ['c','cpp']:
        for variant in ['origin','curated']:files.update(receipt.parent/mode/variant/p for p in saved['modes'][mode][variant]['artifacts'])
    return {str(p):dict(bytes=p.stat().st_size,sha256=sha(p))for p in sorted(files)}
def proof(llvm):
    K=read(HERE/'source-proof-v1.json')
    for p,h in K['pins'].items():need(sha(ROOT/p)==h,'Frozen source-extension input '+p)
    ext=read(HERE/'source-extension-v1.json');parent=read(HERE/'parent-proof-v1.json');raw=lib('experiments/tsl9-lookup-mode-integration/parent-manifest-v1.py')['raw_parent']()
    need(hashlib.sha256(raw).hexdigest()==ext['previous_manifest_sha256']==parent['parent_manifest_sha256'],'Exact159-source parent, not a rewritten receipt')
    expected=json.loads(raw)
    for group,key in [('files','new_file_entries'),('native_units','new_CODE_unit_entries'),('native_data_units','new_DATA_unit_entries')]:expected[group]+=ext[key]
    need(sha(ROOT/'src/source-manifest.json')==ext['new_manifest_sha256']and expected==read(ROOT/'src/source-manifest.json'),'Only exact one-file/one-DATA extension; no CODE or previous entry changes')
    C=lib('scripts/verify-curated-source.py');m=C['metadata']();need((len(m['files']),len(m['native_units']),len(m['native_data_units']))==(160,125,9),'Complete160-source125-CODE/nine-DATA inventory')
    need(parent['passed']and parent['fresh_full_proof_before_extension']and parent['parent_result']['source_C_H_files']==159 and parent['parent_result']['total_source_comparisons']==266 and parent['parent_result']['total_source_objects']==532,'Retained actual full159-source/532-object proof performed before extension')
    exceptions=[]
    for key,pin in parent['parent_input_inventory'].items():
        p=expand(key,llvm)
        if p==ROOT/'src/source-manifest.json':need(pin==dict(bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest()),'Only exact parent manifest exception');exceptions.append(key)
        else:need(p.is_file()and p.stat().st_size==pin['bytes']and sha(p)==pin['sha256'],'Every prior full-proof source/tool/artifact input unchanged')
    need(len(exceptions)==1,'Exactly one proved manifest extension, no changed prior input')
    need(len(parent['source_files'])==159 and all(sha(ROOT/p)==h for p,h in parent['source_files'].items()),'All159 real source files retained')
    V=lib('experiments/tsl9-lookup-mode-integration/build-data-v1.py');data=V['run'](llvm,replay=HERE/'build/data-v1');need(data['variants']==['origin','curated'],'Actual new DATA provenance')
    return dict(passed=True,source_C_H_files=160,CODE_units=125,independent_DATA_units=9,CODE_comparisons=250,CODE_objects=500,DATA_comparisons=18,DATA_objects=36,total_source_comparisons=268,total_source_objects=536,parent_source_files_retained=159,parent_comparisons_retained=266,parent_objects_retained=532,parent_inputs_rehashed=len(parent['parent_input_inventory']),parent532_objects_fully_verified_before_manifest_extension=True,parent532_object_proof_rerun_after_extension=False,new_DATA_comparisons=2,new_DATA_objects=4,new_DATA_bytes=48,new_CODE_bytes=0,parent_proof_sha256=sha(HERE/'parent-proof-v1.json'),new_DATA_receipt_sha256=sha(HERE/'build/data-v1/measurement.json'),source_curated=True,global_mode_invariant_proved=False,full_provider_binding_justified=False,original_coordinate_link_performed=False,physical_MCU_ROM_RAM_IRQ_OTA_proved=False,target_executed=False,HOST_model_executed=False,ISA_emulated=False,hardware_accessed=False,network=False,new_BIN=False,firmware_ready=False)
def main():
    p=argparse.ArgumentParser();p.add_argument('--tool-dir',type=Path,required=True);a=p.parse_args();llvm=a.tool_dir.resolve();before=portable(inputs(llvm),llvm);v=proof(llvm);need(before==portable(inputs(llvm),llvm),'All extended source inputs unchanged during proof');dest=HERE/'build/source-proof-v1.json';need(not dest.exists(),'Create-only extended source proof');dest.write_bytes(encoded(dict(inputs=before,result=v)));print(json.dumps(v))
if __name__=='__main__':
    try:main()
    except Exception as error:
        message=str(error)
        for p,t in [(ROOT,'${PROJECT_ROOT}'),(Path.home(),'${USERPROFILE}')]:message=message.replace(str(p),t).replace(p.as_posix(),t)
        print(json.dumps(dict(passed=False,error_type=type(error).__name__,reason=message)));raise SystemExit(1)
