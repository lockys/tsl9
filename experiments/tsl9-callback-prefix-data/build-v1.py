#!/usr/bin/env python3
"""Compile exact readonly argument windows and audit an experimental partial link."""
from pathlib import Path
from collections import Counter
import argparse,hashlib,json,runpy,subprocess,sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
S=json.loads((HERE/'spec-v1.json').read_bytes());OUTPUT='UNRESOLVED-EXPERIMENTAL-CALLBACK-PREFIX-DATA.o'
def need(v,label):
 if not v:raise ValueError(label)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def lib(p):return runpy.run_path(str(ROOT/p),run_name='readonly_prefix_library')
def elf(p):return lib(S['reader'])['ELF'](p)
def parent_path(mode):return(ROOT/S['parent_component']).parent.parent/mode/Path(S['parent_component']).name
def static_audit():return lib(S['audit'])['audit']()
def globals_of(e):
 rows=[s for s in e.symbols if s['info']>>4];m={s['name']:s for s in rows};need(len(rows)==len(m)and all(v['section']!=0xfff1 for v in rows),'Unique globals without ABS substitutes');return m
def audit_object(path):
 e=elf(path);need(e.header[0]==1 and e.header[1]==243 and not e.program_headers,'RISC-V ET_REL DATA only');regions=S['data_regions'];expected={v['section']:(1,2,v['bytes'],4)for v in regions};need(len(expected)==14,'Fourteen distinct actual readonly sections')
 need({v['name']:(v['type'],v['flags'],v['size'],v['align'])for v in e.sections if v['flags']&2 and v['size']}==expected,'Exactly109 readonly bytes in14 original-size objects');gm=globals_of(e);need(set(gm)=={v['name']for v in regions},'Only actual original DATA providers')
 ev=json.loads((ROOT/S['evidence']).read_bytes());fw=(ROOT/ev['firmware']).read_bytes()
 for d in regions:
  sec=e.section(d['section']);v=gm[d['name']];need((v['info'],v['other'],v['section'],v['value'],v['size'])==(17,0,sec['index'],0,d['bytes']),'Every actual OBJECT has its selected window size and real section backing');raw=e.data(sec);need(raw==fw[d['start']-0x8000:d['end']-0x8000]and hashlib.sha256(raw).hexdigest()==d['original_sha256'],'Every compiled byte matches the original argument window')
 need(not e.relocations and not any(v['info']&15==2 and v['section']for v in e.symbols),'No functions,stubs or relocations');need(sum(v['size']for v in gm.values())==109,'No implicit NUL or guessed padding')
 return dict(passed=True,allocated_DATA_bytes=109,positive_OBJECT_owners=14,real_zero_size_DATA_labels=0,FUNC=0,UND=0,RELA=0,ABS_providers=0,object_sha256=sha(path),independent_readers=lib('experiments/tsl9-remaining-record-dispatch/compare-readers-v1.py')['audit'](path),firmware_ready=False)
def audit_partial(path,native,mode):
 p,n,e=elf(parent_path(mode)),elf(native),elf(path);pm,nm,em=globals_of(p),globals_of(n),globals_of(e);need(e.header[0]==1 and e.header[1]==243 and not e.program_headers,'Nonloadable experimental partial object')
 expected={v['name']:(v['type'],v['flags'],v['size'],v['align'])for v in p.sections if v['flags']&2 and v['size']}
 for d in S['data_regions']:need(d['section']not in expected,'Fresh readonly allocation');expected[d['section']]=(1,2,d['bytes'],4)
 need({v['name']:(v['type'],v['flags'],v['size'],v['align'])for v in e.sections if v['flags']&2 and v['size']}==expected,'Every parent allocation retained plus only14 new DATA windows')
 for sec in p.sections:
  if sec['flags']&2 and sec['size']:need(e.data(sec['name'])==p.data(sec),'All parent CODE/DATA bytes unchanged')
 for d in S['data_regions']:need(e.data(d['section'])==n.data(d['section']),'Every whole compiled readonly window retained')
 need(set(em)==set(pm)|set(nm),'Exact combined global inventory')
 def role(v,reader):return(v['name'],v['info'],v['other'],v['value'],v['size'],reader.sections[v['section']]['name']if v['section']else'')
 for name,v in pm.items():
  if v['section']:need(role(em[name],e)==role(v,p),'Every existing provider and true alias role retained')
  elif name not in nm:need(role(em[name],e)==role(v,p),'Every other dependency remains explicit')
 for name,v in nm.items():need(role(em[name],e)==role(v,n),'Every DATA provider retains actual storage and type')
 expected_relocations=Counter()
 for rel in p.relocations:
  target=p.symbols[rel['symbol']];target_role=role(em[target['name']],e)if target['info']>>4 else role(target,p);expected_relocations[(p.sections[rel['section']]['name'],rel['offset'],rel['type'],rel['addend'],target_role)]+=1
 actual=Counter((e.sections[rel['section']]['name'],rel['offset'],rel['type'],rel['addend'],role(e.symbols[rel['symbol']],e))for rel in e.relocations);need(actual==expected_relocations and len(e.relocations)==4861,'Every parent source,type,addend and actual relocation target role')
 prior={k for k,v in pm.items()if not v['section']};undefined={k for k,v in em.items()if not v['section']};provided={v['name']for v in S['data_regions']};need(len(prior)==22 and len(undefined)==8 and prior-undefined==provided and not undefined-prior,'Only the14 actual DATA references resolve')
 old_labels={k for k,v in pm.items()if v['info']==17 and v['section']and not v['size']};labels={k for k,v in em.items()if v['info']==17 and v['section']and not v['size']};need(len(labels)==6 and labels==old_labels,'All six existing real DATA labels retained');need(sum(v['info']==17 and v['section']and bool(v['size'])for v in em.values())==51,'Exactly51 positive DATA owners')
 need({'tsl9_registered_callbacks_static_data_1a638','tsl9_registered_callbacks_static_data_1a668','tsl9_registered_callbacks_static_data_1a674'}<=undefined,'The unprovided loop DATA and candidate callback tables remain explicit')
 return dict(passed=True,CODE_bytes=64544,DATA_bytes=3830,RELA=4861,UND=8,positive_DATA_owners=51,real_zero_size_DATA_labels=6,new_real_DATA_labels=0,code_unchanged=True,all_prior_readonly_bytes_preserved=True,resolved_original_DATA_providers=sorted(provided),remaining_undefined=sorted(undefined),ABS_providers=0,partial_object_sha256=sha(path),independent_readers=lib('experiments/tsl9-remaining-record-dispatch/compare-readers-v1.py')['audit'](path),source_manifest_updated=False,accepted_component_updated=False,original_coordinate_link_performed=False,coverage_added=0,firmware_ready=False)
def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--tool-dir',required=True,type=Path);g=parser.add_mutually_exclusive_group(required=True);g.add_argument('--trial');g.add_argument('--replay',type=Path);a=parser.parse_args();llvm=a.tool_dir.resolve()
 for name,pin in S['tools'].items():need(sha(llvm/name)==pin,'Pinned compiler tool '+name)
 need(sha(llvm.parent/'lib/clang/18/include/stdint.h')==S['stdint_sha256'],'Pinned compiler header');need(sha(ROOT/S['reader'])==S['reader_sha256']and sha(ROOT/S['curation_checker'])==S['curation_checker_sha256'],'Pinned ELF reader and compiler profile checker');need(S['flags']=={m:lib(S['curation_checker'])['flags']({'profile':S['profile']},m)for m in ['c','cpp']},'Unchanged native compilation flags')
 need(sha(ROOT/S['source'])==S['source_sha256']and sha(ROOT/S['audit'])==S['audit_sha256'],'Exact source and original-operand audit');need(all(sha(parent_path(m))==S['parent_component_sha256']for m in ['c','cpp']),'Both exact accepted parents');static=static_audit();need(static['selected_argument_bytes']==109 and static['positive_DATA_owners']==14,'Actual fixed-length argument provenance')
 portable=lib('experiments/tsl9-original-startup/build-v1.py')['portable'];ev=json.loads((ROOT/S['evidence']).read_bytes());paths=[Path(__file__),HERE/'spec-v1.json',ROOT/S['source'],ROOT/S['evidence'],ROOT/S['audit'],ROOT/S['reader'],ROOT/S['curation_checker'],ROOT/'experiments/tsl9-remaining-record-dispatch/compare-readers-v1.py',ROOT/'experiments/tsl9-original-startup/build-v1.py',llvm.parent/'lib/clang/18/include/stdint.h']+[parent_path(m)for m in ['c','cpp']]+[llvm/n for n in S['tools']]+[ROOT/p for p in ev['inputs']];inputs=portable({str(p):sha(p)for p in paths},llvm)
 if a.replay:
  out=a.replay.resolve();need(out.parent==HERE/'build','Owned experiment replay folder');saved=json.loads((out/'measurement.json').read_bytes());need(saved['inputs']==inputs and saved['static']==static,'Exact source/tool/static replay identities')
  for mode in ['c','cpp']:
   folder=out/mode;need(saved['modes'][mode]['artifacts']=={p.name:sha(p)for p in sorted(folder.iterdir())if p.is_file()},'Complete retained compiler/link inventory');need(saved['modes'][mode]['native']==audit_object(folder/'unit.o')and saved['modes'][mode]['partial']==audit_partial(folder/OUTPUT,folder/'unit.o',mode),'Actual DATA and partial-link replay')
  print(json.dumps(dict(passed=True,mode='read-only-callback-prefix-replay',DATA_bytes=109,positive_DATA_owners=14,experimental_UND=8,accepted_UND_unchanged=22,coverage_added=0,firmware_ready=False)));return
 need(Path(a.trial).name==a.trial,'Single trial basename');out=HERE/'build'/a.trial;need(not out.exists(),'Create-only output folder');report=dict(schema='TSL9-callback-prefix-native-measurement-v1',inputs=inputs,static=static,modes={})
 for mode in ['c','cpp']:
  folder=out/mode;folder.mkdir(parents=True);commands=[]
  for label,argv in [('compile',[str(llvm/'clang.exe')]+S['flags'][mode]+['-MD','-MF',str(folder/'unit.d'),'-MT','unit.o','-c',str(ROOT/S['source']),'-o',str(folder/'unit.o')]),('link',[str(llvm/'ld.lld.exe'),'-r','--no-relax',str(parent_path(mode)),str(folder/'unit.o'),'-o',str(folder/OUTPUT)])]:
   p=subprocess.run(argv,cwd=ROOT,capture_output=True,timeout=120);(folder/(label+'.log')).write_text(portable((p.stdout+p.stderr).decode('utf8','replace'),llvm),encoding='utf8');commands.append(dict(label=label,argv=portable(argv,llvm),exit=p.returncode));need(p.returncode==0,'Actual '+label+' failed;local log retained')
  (folder/'unit.d').write_text(portable((folder/'unit.d').read_text(encoding='utf8'),llvm),encoding='utf8');native=audit_object(folder/'unit.o');partial=audit_partial(folder/OUTPUT,folder/'unit.o',mode);report['modes'][mode]=dict(native=native,partial=partial,commands=commands,artifacts={p.name:sha(p)for p in sorted(folder.iterdir())if p.is_file()})
 need(sha(out/'c/unit.o')==sha(out/'cpp/unit.o')and sha(out/'c'/OUTPUT)==sha(out/'cpp'/OUTPUT),'Identical C11/C++17 DATA and experimental partial objects');need(inputs==portable({str(p):sha(p)for p in paths},llvm),'Every actual producer input unchanged');(out/'measurement.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n',encoding='utf8');print(json.dumps(dict(passed=True,DATA_bytes=109,positive_DATA_owners=14,experimental_UND=8,accepted_UND_unchanged=22,coverage_added=0,object_sha256=sha(out/'c/unit.o'),partial_object_sha256=sha(out/'c'/OUTPUT),new_callback_CODE_gaps=static['newly_identified_callback_CODE_gaps'],independent_readers_agree=True,firmware_ready=False)))
if __name__=='__main__':
 try:main()
 except Exception as e:
  print(json.dumps(dict(passed=False,error_type=type(e).__name__,reason=str(e).replace(str(ROOT),'PROJECT_ROOT').replace(str(Path.home()),'USERPROFILE'))));raise SystemExit(1)
