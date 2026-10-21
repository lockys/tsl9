#!/usr/bin/env python3
"""One bounded native C/C++ profile; target objects are never executed."""
import argparse,hashlib,importlib.util,json,subprocess,sys,uuid
from pathlib import Path
sys.dont_write_bytecode=True
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def need(x,m):
 if not x:raise ValueError(m)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--project-root',required=True,type=Path);p.add_argument('--tool-dir',required=True,type=Path);p.add_argument('--language',choices=['c','cpp','both'],default='both');a=p.parse_args();root=a.project_root.resolve();model=root/'experiments/tsl9-v4160-ota-tx';work=model/'build'/('first-native-'+uuid.uuid4().hex);parser=root/'apk-analysis/tsl9-v4160-irq-native-2026-10-21/compiler-review/elf32.py';need(sha(parser)=='00a231e3bbd881a9961c12fefd15565364cd813250a46a7b20851a6b9f3a2141','immutable ELF parser');s=importlib.util.spec_from_file_location('new_TX_probe_ELF',parser);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);results=[]
 tools={n:next(p for p in(a.tool_dir/(n+'.exe'),a.tool_dir/n) if p.is_file()) for n in('clang','llvm-objdump')};need(sha(tools['clang'])=='047dfde05acc6fcce5af669e25cd8d40b4f509b8842d151d6d8a43a1c6a35fd6','actual known LLVM compiler')
 for mode in (['c','cpp'] if a.language=='both' else[a.language]):
  folder=work/mode;folder.mkdir(parents=True);commands=[];allowed={1,2,5,6,7,*range(10,18),*range(28,32)};flags=['--target=riscv32-unknown-elf','-march=rv32imac_zicsr','-mabi=ilp32','-Oz','-mllvm','-enable-machine-outliner=never','-ffreestanding','-fno-builtin','-fno-stack-protector','-fno-unwind-tables','-fno-asynchronous-unwind-tables','-mno-relax','-ffunction-sections','-fdata-sections','-Wall','-Wextra','-Werror',*['-ffixed-x'+str(i) for i in range(1,32) if i not in allowed],'-x','c' if mode=='c' else'c++','-std=c11' if mode=='c' else'-std=c++17',*(['-fno-exceptions']if mode=='cpp' else[])];pins={str(p):sha(p) for p in[model/'src'/n for n in('tx_native.c','tx_native.h','tx_io.h')]}
  def run(label,argv):
   r=subprocess.run([str(x)for x in argv],capture_output=True,cwd=folder,timeout=120);log=folder/(label+'.log');log.write_bytes(r.stdout+r.stderr);commands.append(dict(argv=[str(x)for x in argv],exit=r.returncode,log=log.name,log_sha256=sha(log)));return r
  resource=Path(run('resource-dir',[tools['clang'],'-print-resource-dir']).stdout.decode().strip())/'include/stdint.h';pins[str(resource)]=sha(resource)
  for suffix,action in[('.o',['-c','-MD','-MF',folder/'tx_native.d','-MT','tx_native.o']),('.ll',['-S','-emit-llvm'])]:run('compile'+suffix,[tools['clang'],*flags,*action,model/'src/tx_native.c','-o',folder/('tx_native'+suffix)])
  r=dict(mode=mode,compiled=all(x['exit']==0 for x in commands),commands=commands,source_before_after=pins,RV32_execution=False,ISA_emulation=False,network=False)
  if r['compiled']:
   e=m.ELF(folder/'tx_native.o');symbol=next(s for s in e.symbols if s['name']=='tsl9_ota_tx_8a56');r.update(bytes=symbol['size'],original_bytes=280,original_extent_fits=symbol['size']<=280,UND=[s['name']for s in e.symbols if s['index']==0 and s['name']],RELA=len(e.relocations));run('disassembly',[tools['llvm-objdump'],'-d',folder/'tx_native.o'])
  need(all(sha(Path(n))==pin for n,pin in pins.items()),'stable source/resource beforeafter');(folder/'probe.json').write_bytes((json.dumps(r,indent=2)+'\n').encode());results.append(dict(receipt=str(folder/'probe.json'),**{k:v for k,v in r.items()if k not in('commands','source_before_after')}))
 print(json.dumps(dict(results=results,RV32_execution=False)))
