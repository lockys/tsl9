#!/usr/bin/env python3
"""Compile a readonly C/C++ read-window pool and check an experimental ET_REL link."""
from pathlib import Path
from collections import Counter
import argparse,hashlib,json,runpy,subprocess,sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
S=json.loads((HERE/'spec-v1.json').read_bytes());OUTPUT='UNRESOLVED-EXPERIMENTAL-GRID-READ-WINDOWS.o'
def need(v,label):
 if not v:raise ValueError(label)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def lib(p):return runpy.run_path(str(ROOT/p),run_name='readonly_grid_library')
def elf(p):return lib(S['reader'])['ELF'](p)
def parent_path(mode):return(ROOT/S['parent_component']).parent.parent/mode/Path(S['parent_component']).name
def globals_of(e):
 rows=[s for s in e.symbols if s['info']>>4];out={s['name']:s for s in rows};need(len(rows)==len(out)and all(s['section']!=0xfff1 for s in rows),'Unique global roles,no ABS substitutes');return out
def audit_object(path):
 e=elf(path);d=S['owner'];need(e.header[0]==1 and e.header[1]==243 and not e.program_headers,'RISC-V ET_REL DATA only')
 alloc=[s for s in e.sections if s['flags']&2 and s['size']];need(len(alloc)==1,'One real readonly allocation');sec=alloc[0]
 need((sec['name'],sec['type'],sec['flags'],sec['size'],sec['align'])==(d['section'],1,2,432,4),'Exact432-byte readonly owner')
 gm=globals_of(e);need(set(gm)=={d['name']}|{v['name']for v in S['labels']},'Only one owner and two genuine DATA labels')
 v=gm[d['name']];need((v['info'],v['other'],v['section'],v['value'],v['size'])==(17,0,sec['index'],0,432),'Actual allocated OBJECT owner')
 for label in S['labels']:
  v=gm[label['name']];need((v['info'],v['other'],v['section'],v['value'],v['size'])==(17,0,sec['index'],label['pool_offset'],0),'Genuine zero-allocation labels backed by one pool')
 ev=json.loads((ROOT/S['evidence']).read_bytes());fw=(ROOT/ev['firmware']).read_bytes();need(e.data(sec)==fw[d['start']-0x8000:d['end']-0x8000]and hashlib.sha256(e.data(sec)).hexdigest()==d['original_sha256'],'All compiled DATA equals original selected bytes')
 need(not e.relocations and not any(v['info']&15==2 and v['section']for v in e.symbols),'No functions,stubs,relocations')
 return dict(passed=True,allocated_DATA_bytes=432,positive_OBJECT_owners=1,real_zero_size_DATA_labels=2,FUNC=0,UND=0,RELA=0,ABS_providers=0,object_sha256=sha(path),independent_readers=lib('experiments/tsl9-remaining-record-dispatch/compare-readers-v1.py')['audit'](path),firmware_ready=False)
def audit_partial(path,native,mode):
 p,n,e=elf(parent_path(mode)),elf(native),elf(path);pm,nm,em=globals_of(p),globals_of(n),globals_of(e);need(e.header[0]==1 and e.header[1]==243 and not e.program_headers,'Nonloadable experimental partial component')
 expected={s['name']:(s['type'],s['flags'],s['size'],s['align'])for s in p.sections if s['flags']&2 and s['size']};need(S['owner']['section']not in expected,'Fresh independent DATA section');expected[S['owner']['section']]=(1,2,432,4)
 need({s['name']:(s['type'],s['flags'],s['size'],s['align'])for s in e.sections if s['flags']&2 and s['size']}==expected,'Every exact parent allocation plus only432 DATA bytes')
 for sec in p.sections:
  if sec['flags']&2 and sec['size']:need(e.data(sec['name'])==p.data(sec),'Every parent CODE/DATA byte preserved')
 need(e.data(S['owner']['section'])==n.data(S['owner']['section']),'Entire compiled pool retained');need(set(em)==set(pm)|set(nm),'Exact combined global inventory')
 def role(v,reader):return(v['name'],v['info'],v['other'],v['value'],v['size'],reader.sections[v['section']]['name']if v['section']else'')
 for name,v in pm.items():
  a=em[name]
  if v['section']:need(role(a,e)==role(v,p),'Every existing provider and real DATA label retained')
  elif name not in nm:need((a['info'],a['other'],a['section'],a['value'],a['size'])==(16,0,0,0,0),'Every other dependency remains explicit')
 for name,v in nm.items():need(role(em[name],e)==role(v,n),'All actual owner/interior-label roles retained')
 expected_relocations=Counter()
 for rel in p.relocations:
  target=p.symbols[rel['symbol']];target_role=role(em[target['name']],e)if target['info']>>4 else role(target,p);expected_relocations[(p.sections[rel['section']]['name'],rel['offset'],rel['type'],rel['addend'],target_role)]+=1
 actual=Counter((e.sections[rel['section']]['name'],rel['offset'],rel['type'],rel['addend'],role(e.symbols[rel['symbol']],e))for rel in e.relocations)
 need(actual==expected_relocations and len(e.relocations)==4861,'Every original relocation source,type,addend and actual target role')
 prior={k for k,v in pm.items()if not v['section']};undefined={k for k,v in em.items()if not v['section']};labels={v['name']for v in S['labels']}
 need(len(prior)==24 and len(undefined)==22 and prior-undefined==labels and not undefined-prior,'Only two evidenced DATA references resolve')
 need('tsl9_record_field_transitions_static_data_1a078'in undefined,'Third unbounded reader remains unresolved')
 need(sum(v['info']==17 and v['size']==0 and bool(v['section'])for v in em.values())==6,'Four existing DATA labels plus two new labels')
 return dict(passed=True,CODE_bytes=64544,DATA_bytes=3721,RELA=4861,UND=22,real_zero_size_DATA_labels=6,new_real_DATA_labels=2,code_unchanged=True,all_prior_readonly_bytes_preserved=True,ABS_providers=0,partial_object_sha256=sha(path),independent_readers=lib('experiments/tsl9-remaining-record-dispatch/compare-readers-v1.py')['audit'](path),source_manifest_updated=False,accepted_component_updated=False,original_coordinate_link_performed=False,coverage_added=0,firmware_ready=False)
def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--tool-dir',required=True,type=Path);g=parser.add_mutually_exclusive_group(required=True);g.add_argument('--trial');g.add_argument('--replay',type=Path);a=parser.parse_args();llvm=a.tool_dir.resolve()
 for name,pin in S['tools'].items():need(sha(llvm/name)==pin,'Pinned compiler tool '+name)
 need(sha(llvm.parent/'lib/clang/18/include/stdint.h')==S['stdint_sha256'],'Pinned compiler header');need(sha(ROOT/S['reader'])==S['reader_sha256']and sha(ROOT/S['curation_checker'])==S['curation_checker_sha256'],'Pinned reader and compiler profile checker')
 need(S['flags']=={m:lib(S['curation_checker'])['flags']({'profile':S['profile']},m)for m in ['c','cpp']},'Existing native compiler flags unchanged')
 need(sha(ROOT/S['source'])==S['source_sha256']and sha(ROOT/S['audit'])==S['audit_sha256'],'Actual audited source identities');need(all(sha(parent_path(m))==S['parent_component_sha256']for m in ['c','cpp']),'Both actual accepted parent components')
 static=lib(S['audit'])['audit']();portable=lib('experiments/tsl9-original-startup/build-v1.py')['portable'];ev=json.loads((ROOT/S['evidence']).read_bytes())
 paths=[Path(__file__),HERE/'spec-v1.json',ROOT/S['source'],ROOT/S['evidence'],ROOT/S['audit'],ROOT/S['reader'],ROOT/S['curation_checker'],ROOT/'experiments/tsl9-remaining-record-dispatch/compare-readers-v1.py',ROOT/'experiments/tsl9-original-startup/build-v1.py',llvm.parent/'lib/clang/18/include/stdint.h']+[parent_path(m)for m in ['c','cpp']]+[llvm/n for n in S['tools']]+[ROOT/p for p in ev['inputs']]
 inputs=portable({str(p):sha(p)for p in paths},llvm)
 if a.replay:
  out=a.replay.resolve();need(out.parent==HERE/'build','Owned experiment replay directory');saved=json.loads((out/'measurement.json').read_bytes());need(saved['inputs']==inputs and saved['static']==static,'Exact source/tool/static replay identities')
  for mode in ['c','cpp']:
   folder=out/mode;need(saved['modes'][mode]['artifacts']=={p.name:sha(p)for p in sorted(folder.iterdir())if p.is_file()},'Complete retained artifacts');need(saved['modes'][mode]['native']==audit_object(folder/'unit.o')and saved['modes'][mode]['partial']==audit_partial(folder/OUTPUT,folder/'unit.o',mode),'Actual independently parsed DATA/link replay')
  print(json.dumps(dict(passed=True,mode='read-only-replay',DATA_bytes=432,real_interior_labels=2,experimental_UND=22,accepted_UND_unchanged=24,coverage_added=0,firmware_ready=False)));return
 need(Path(a.trial).name==a.trial,'Single trial basename');out=HERE/'build'/a.trial;need(not out.exists(),'Create-only output directory');report=dict(schema='TSL9-grid-read-windows-native-measurement-v1',inputs=inputs,static=static,modes={})
 for mode in ['c','cpp']:
  folder=out/mode;folder.mkdir(parents=True);commands=[]
  for label,argv in [('compile',[str(llvm/'clang.exe')]+S['flags'][mode]+['-MD','-MF',str(folder/'unit.d'),'-MT','unit.o','-c',str(ROOT/S['source']),'-o',str(folder/'unit.o')]),('link',[str(llvm/'ld.lld.exe'),'-r','--no-relax',str(parent_path(mode)),str(folder/'unit.o'),'-o',str(folder/OUTPUT)])]:
   p=subprocess.run(argv,cwd=ROOT,capture_output=True,timeout=120);(folder/(label+'.log')).write_text(portable((p.stdout+p.stderr).decode('utf8','replace'),llvm),encoding='utf8');commands.append(dict(label=label,argv=portable(argv,llvm),exit=p.returncode));need(p.returncode==0,'Actual '+label+' failed;local log retained')
  (folder/'unit.d').write_text(portable((folder/'unit.d').read_text(encoding='utf8'),llvm),encoding='utf8');native=audit_object(folder/'unit.o');partial=audit_partial(folder/OUTPUT,folder/'unit.o',mode);report['modes'][mode]=dict(native=native,partial=partial,commands=commands,artifacts={p.name:sha(p)for p in sorted(folder.iterdir())if p.is_file()})
 need(sha(out/'c/unit.o')==sha(out/'cpp/unit.o')and sha(out/'c'/OUTPUT)==sha(out/'cpp'/OUTPUT),'Identical C/C++ DATA and experimental partial objects');need(inputs==portable({str(p):sha(p)for p in paths},llvm),'Inputs unchanged during build')
 (out/'measurement.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n',encoding='utf8');print(json.dumps(dict(passed=True,DATA_bytes=432,real_interior_labels=2,experimental_UND=22,accepted_UND_unchanged=24,coverage_added=0,object_sha256=sha(out/'c/unit.o'),partial_object_sha256=sha(out/'c'/OUTPUT),independent_readers_agree=True,firmware_ready=False)))
if __name__=='__main__':
 try:main()
 except Exception as e:
  print(json.dumps(dict(passed=False,reason=str(e).replace(str(ROOT),'PROJECT_ROOT').replace(str(Path.home()),'USERPROFILE'))));raise SystemExit(1)
