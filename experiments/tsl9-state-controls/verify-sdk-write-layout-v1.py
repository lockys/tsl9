#!/usr/bin/env python3
"""Compile SDK candidate descriptor metadata only; never execute SDK or target code."""
from pathlib import Path
import argparse,hashlib,json,re,runpy,struct,subprocess,sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
CONFIG=HERE/'sdk-write-layout-v1.json';K=json.loads(CONFIG.read_bytes())
def need(x,label):
 if not x:raise ValueError(label)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def enc(x):return(json.dumps(x,indent=2,sort_keys=True)+'\n').encode()
def portable(x,llvm,header):
 pairs=[(header,'${SDK_HEADER}'),(llvm.parent/'lib/clang/18','${CLANG_RESOURCE}'),(llvm,'${LLVM_BIN}'),(ROOT,'${PROJECT_ROOT}')]
 if isinstance(x,str):
  for p,t in pairs:
   for form in [str(p),p.as_posix()]:x=x.replace(form,t)
  return x
 if isinstance(x,list):return[portable(v,llvm,header)for v in x]
 if isinstance(x,dict):return{portable(k,llvm,header):portable(v,llvm,header)for k,v in x.items()}
 return x
def inventory(folder):return{p.name:dict(bytes=p.stat().st_size,sha256=sha(p))for p in sorted(folder.iterdir())if p.is_file()}
def context(llvm,header):
 for key in ['source','native_spec','evidence','saved_profile']:need(sha(ROOT/K[key])==K[key+'_sha256'],'Pinned '+key)
 S=json.loads((ROOT/K['native_spec']).read_bytes());need(sha(header)==K['header_sha256'],'Exact saved SDK header')
 lines=header.read_bytes().decode(K['header_encoding']).splitlines()
 need(not any(re.search(r'#\s*pragma\s+pack',s)for s in lines),'No omitted SDK packing directives')
 for row in K['type_lines']+K['macro_profile']+K['opcode']:need(lines[row['line']-1]==row['text'],'Exact source-bound SDK declaration/macro line')
 declaration='\n'.join(x['text']for x in K['type_lines'])
 need(declaration in(ROOT/K['source']).read_text(),'Exact saved typedef retained in data-only source')
 profile=json.loads((ROOT/K['saved_profile']).read_bytes())
 need(profile['header_sha256']==K['header_sha256'] and profile['default_function_table_base']==K['default_function_table_base'],'Retained default-profile correspondence')
 for row in K['macro_profile']:
  need(row['default_slot_address']==K['default_function_table_base']+4*row['table_index'],'Typed default slot arithmetic only')
  need(not row['installed_implementation_proved'],'No runtime table identity asserted')
 for name in ['clang.exe','llvm-objdump.exe']:need(sha(llvm/name)==S['tools'][name],'Pinned existing '+name)
 need(sha(llvm.parent/'lib/clang/18/include/stdint.h')==S['stdint_sha256'],'Pinned compiler header')
 need(sha(ROOT/S['reader'])==S['reader_sha256'],'Pinned static ELF reader')
 C=runpy.run_path(str(ROOT/S['curation_checker']),run_name='positive_static_library')
 need(S['flags']=={m:C['flags']({'profile':S['profile']},m)for m in ['c','cpp']},'Existing measured compiler profiles unchanged')
 E=runpy.run_path(str(ROOT/S['reader']),run_name='positive_static_library')['ELF']
 evidence=json.loads((ROOT/K['evidence']).read_bytes());fw=(ROOT/S['firmware']).read_bytes();need(hashlib.sha256(fw).hexdigest()==S['firmware_sha256'],'Original firmware')
 ops={o['addr']:o for f in evidence['selected_functions']for o in f['operations']}
 for row in K['original_writes']:
  op=ops[row['PC']];need(op['opcode']==row['opcode'] and bytes.fromhex(op['bytes'])==fw[op['addr']-0x8000:op['addr']-0x8000+op['size']],'Actual original descriptor write')
  need(row['field_offset']+K['descriptor_frame_offset']==row['frame_offset'],'Observed descriptor-relative stack offset')
 need(ops[0x10ca4]['opcode']=='li a1, 18' and ops[0x10cd0]['opcode']=='li a1, 18','Original allocation/release opcode18')
 need(len(K['opcode'])==1 and re.search(r'ATT_WRITE_REQ\s+0x12\b',K['opcode'][0]['text']),'Saved ATT Write Request value')
 paths={Path(__file__),CONFIG,header,ROOT/K['source'],ROOT/K['native_spec'],ROOT/K['evidence'],ROOT/K['saved_profile'],ROOT/S['reader'],ROOT/S['curation_checker'],ROOT/S['firmware'],llvm/'clang.exe',llvm/'llvm-objdump.exe',llvm.parent/'lib/clang/18/include/stdint.h'}
 inputs=portable({str(p):dict(bytes=p.stat().st_size,sha256=sha(p))for p in sorted(paths)},llvm,header)
 return S,E,inputs
def audit(path,E):
 e=E(path);need(e.header[0]==1 and e.header[1]==243 and not e.program_headers,'Actual non-executable RV32 ET_REL')
 symbols=[s for s in e.symbols if s['info']>>4];need(len(symbols)==1,'One genuine data global only')
 s=symbols[0];sec=e.sections[s['section']]
 need((s['name'],s['info'],s['other'],s['value'],s['size'])==(K['symbol'],17,0,0,48),'Actual48-byte readonly SDK metadata object')
 need((sec['name'],sec['type'],sec['flags'],sec['address'],sec['size'],sec['align'])==(K['section'],1,2,0,48,4),'Exact readonly allocation and alignment')
 need({x['index']for x in e.sections if x['flags']&2 and x['size']}=={sec['index']},'No executable,constructor or extra data carriers')
 need(not e.relocations and not any((s['info']&15)==2 for s in e.symbols),'Zero relocations and zero FUNC symbols')
 words=list(struct.unpack('<12I',e.data(sec)));need(words==K['expected_words'],'Actual native sizeof/alignment/offset/width data')
 need(words[2:7]==[x['field_offset']for x in K['original_writes'][:3]]+[8,9],'Native layout equals observed original offsets')
 return dict(passed=True,data_bytes=48,functions=0,relocations=0,undefined_providers=0,words=words,labels=K['word_labels'],native_object_sha256=sha(path),scope='Saved SDK candidate ILP32 data layout and original stack offsets only',source_header_checked=True,installed_ROM_identity_proved=False,private_caller_ABI_proved=False,physical_RAM_or_hardware_proved=False,SDK_functions_executed=False,target_executed=False,HOST_model_executed=False,ISA_emulated=False,hardware_accessed=False,network=False,linked_into_firmware=False,firmware_ready=False)
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--tool-dir',required=True,type=Path);p.add_argument('--sdk-header',required=True,type=Path)
 g=p.add_mutually_exclusive_group(required=True);g.add_argument('--trial');g.add_argument('--replay',type=Path);a=p.parse_args();llvm=a.tool_dir.resolve();header=a.sdk_header.resolve();S,E,before=context(llvm,header)
 out=(a.replay or HERE/'build'/a.trial).resolve();need(out.parent==HERE/'build','Owned SDK data-only artifact directory')
 if a.replay:
  rec=json.loads((out/'measurement.json').read_bytes());need(rec['inputs']==before,'All SDK candidate inputs unchanged')
  for mode in ['c','cpp']:need(rec['modes'][mode]['artifacts']==inventory(out/mode) and rec['modes'][mode]['result']==audit(out/mode/'unit.o',E),'Actual retained SDK data-only replay')
  print(json.dumps(dict(passed=True,mode='read-only-SDK-candidate-data-replay',data_objects=2,SDK_functions_executed=False,firmware_ready=False)));return
 need(Path(a.trial).name==a.trial and not out.exists(),'Create-only SDK data trial')
 rec=dict(schema='TSL9-SDK-attWriteReq-data-layout-proof-v1',inputs=before,modes={})
 for mode in ['c','cpp']:
  folder=out/mode;folder.mkdir(parents=True);commands=[]
  jobs=[('compile',[str(llvm/'clang.exe')]+S['flags'][mode]+['-MD','-MF',str(folder/'unit.d'),'-MT','unit.o','-c',str(ROOT/K['source']),'-o',str(folder/'unit.o')]),('read',[str(llvm/'llvm-objdump.exe'),'-h','-t','-r',str(folder/'unit.o')])]
  for label,argv in jobs:
   proc=subprocess.run(argv,cwd=ROOT,capture_output=True,timeout=120);(folder/(label+'.log')).write_text(portable((proc.stdout+proc.stderr).decode('utf-8','replace'),llvm,header),encoding='utf-8');need(proc.returncode==0,'Actual SDK metadata '+label+';log retained')
   commands.append(dict(label=label,argv=portable(argv,llvm,header),exit=proc.returncode))
  result=audit(folder/'unit.o',E);rec['modes'][mode]=dict(result=result,commands=commands,artifacts=inventory(folder));print(json.dumps(dict(mode=mode,**result)))
 need(rec['modes']['c']['result']['words']==rec['modes']['cpp']['result']['words'],'Same candidate layout in both languages')
 need(context(llvm,header)[2]==before,'Every actual input unchanged during compilation')
 (out/'measurement.json').write_bytes(enc(rec))
if __name__=='__main__':
 try:main()
 except Exception as e:
  msg=str(e).replace(str(ROOT),'PROJECT_ROOT').replace(str(Path.home()),'USERPROFILE');print(json.dumps(dict(passed=False,error_type=type(e).__name__,reason=msg)));sys.exit(1)
