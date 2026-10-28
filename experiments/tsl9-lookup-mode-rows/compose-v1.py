"""Partially link the real APP source component and48 DATA bytes; no image or execution."""
import argparse,hashlib,json,runpy,subprocess,sys
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;R=HERE.parents[1]
def need(ok,label):
    if not ok:raise ValueError(label)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def lib(p):return runpy.run_path(str(R/p),run_name='lookup_rows_composition_library')
def compose(llvm,trial=None):
    E=read(HERE/'composition-inputs-v1.json')
    for p,h in E['reference_inputs'].items():need(sha(R/p)==h,'Frozen composition input: '+p)
    N=runpy.run_path(str(HERE/'verify-v1.py'),run_name='lookup_rows_native_library');native=N['run'](llvm,replay=HERE/'build/native-v1');need(native==read(HERE/'verification-v1.json'),'Fresh DATA/static proof retained')
    need(sha(llvm/'ld.lld.exe')==E['lld_sha256'],'Pinned actual local linker')
    EL=lib(E['reader'])['ELF'];F=lib(E['facts_helper']);I=lib(E['independent_reader']);layout=read(R/E['original_layout_map'])
    owned={p for o in layout['owners']for p in range(o['original_PC'],o['original_PC']+o['bytes'])};added={p for row in native['state_contract']['rows']if row['new_experimental_DATA']for p in range(row['start'],row['end'])}
    need(len(owned)==73374 and len(added)==48 and not owned&added,'Genuine new original-coordinate DATA selection, without overlap or padding')
    for a,z in read(HERE/'inputs-v1.json')['withheld_ranges']:need(not added&set(range(a,z)),'No withheld DATA/CODE selected')
    out=HERE/'build'/(trial if trial else 'composition-v1')
    if trial:need(Path(trial).name==trial and not out.exists(),'Create-only partial composition folder')
    results={}
    for mode in ['c','cpp']:
        inputs=[R/E['APP_component'].replace('/c/','/'+mode+'/'),HERE/'build/native-v1'/mode/'unit.o']
        need([sha(p)for p in inputs]==[E['APP_component_sha256'],E['row_object_sha256']],'Exact real parent component and new readonly object')
        folder=out/mode
        if trial:
            folder.mkdir(parents=True);p=subprocess.run([str(llvm/'ld.lld.exe'),'-r','--no-relax',*[str(x)for x in inputs],'-o',str(folder/'candidate.o')],capture_output=True,timeout=120)
            (folder/'link.log').write_text(N['portable']((p.stdout+p.stderr).decode('utf-8','replace'),llvm),encoding='utf-8');need(p.returncode==0,'Actual nonloadable partial link completed; log retained')
        a,d,u,r=F['facts'](inputs[0],EL);aa,dd,uu,rr=F['facts'](inputs[1],EL)
        need(not set(a)&set(aa)and not set(d)&set(dd)and not uu and not rr,'No input section/symbol collision or new imports/relocations')
        path=folder/'candidate.o';facts=F['facts'](path,EL);need(facts==({**a,**aa},{**d,**dd},u-set(dd),sorted(r+rr)),'Every input allocated section byte, global symbol and typed relocation retained')
        need(len(u)==6 and not set(dd)&u and facts[2]==u,'All six genuine compiler imports remain; no provider alias introduced')
        e=EL(path);need(e.header[0]==1 and not e.program_headers,'Actual ET_REL, no executable entry/load segments')
        code=sum(s['size']for s in e.sections if s['flags']&6==6);data=sum(s['size']for s in e.sections if s['flags']&2 and not s['flags']&4)
        need((code,data)==(69412,4010),'Exact original69412 CODE,3962 prior DATA and48 new DATA; no fill/padding')
        independent=I['audit'](path);need(independent['passed'],'Independent complete large-object reader agreement')
        results[mode]=dict(passed=True,object_sha256=sha(path),CODE_bytes=code,DATA_bytes=data,allocated_bytes=code+data,new_DATA_bytes=48,named_UND=sorted(u),relocations=len(e.relocations),all_input_allocated_bytes_global_symbols_and_relocations_retained=True,new_DATA_original_coordinate_intervals=[[x['start'],x['end']]for x in native['state_contract']['rows']if x['new_experimental_DATA']],new_DATA_selection_does_not_overlap_existing_or_withheld=True,independent_readers=independent,original_address_link_performed=False,linked_into_APP_image=False)
    need(results['c']==results['cpp'],'Actual complete C/C++ partial compositions identical')
    v=dict(schema='TSL9-APP-plus-conditional-lookup-DATA-composition-v1',passed=True,checker_sha256=sha(__file__),inputs_sha256=sha(HERE/'composition-inputs-v1.json'),native_verification_sha256=sha(HERE/'verification-v1.json'),composition=results,new_experimental_DATA_bytes=48,new_CODE_bytes=0,formal_APP_source_C_H_files_unchanged=159,formal_APP_covered_bytes_unchanged=73374,formal_APP_byte_coverage_unchanged=95.54,compiler_UND_unchanged=6,source_curated=False,provider_resolved=False,original_address_link_performed=False,withheld_payload_or_individual_hash_output=False,new_BIN=False,firmware_ready=False,goal_complete=False,target_executed=False,HOST_model_executed=False,ISA_emulated=False,hardware_accessed=False,network=False)
    dest=HERE/'composition-v1.json'
    if trial:
        need(not dest.exists(),'Create-only partial composition receipt');dest.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')
    else:need(v==read(dest),'Fresh actual composition replay equals successful receipt')
    return v
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--tool-dir',type=Path,required=True);p.add_argument('--link-trial');a=p.parse_args()
    try:
        v=compose(a.tool_dir.resolve(),a.link_trial);c=v['composition']['c'];print(json.dumps(dict(passed=True,CODE_bytes=c['CODE_bytes'],DATA_bytes=c['DATA_bytes'],allocated_bytes=c['allocated_bytes'],new_experimental_DATA_bytes=48,compiler_UND=6,formal_APP_byte_coverage=95.54,new_BIN=False)))
    except Exception as error:
        message=str(error)
        for p,t in [(R,'${PROJECT_ROOT}'),(Path.home(),'${USERPROFILE}')]:message=message.replace(str(p),t).replace(p.as_posix(),t)
        print(json.dumps(dict(passed=False,error_type=type(error).__name__,reason=message)));raise SystemExit(1)
