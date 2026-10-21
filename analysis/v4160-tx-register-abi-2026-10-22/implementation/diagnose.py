#!/usr/bin/env python3
"""Bounded LLVM lowering diagnosis; never execute the RISC-V output."""
import argparse,hashlib,json,runpy,subprocess,sys,uuid
from pathlib import Path
sys.dont_write_bytecode=True
MODEL='experiments/tsl9-v4160-tx-register-abi'
OLDPIN='adeeaddea4c46d92dd4ce33a5beaa329779781a0611e97b965c1f023f5ef4eca'
CLANG='047dfde05acc6fcce5af669e25cd8d40b4f509b8842d151d6d8a43a1c6a35fd6'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def need(v,m):
 if not v:raise ValueError(m)
def write(p,r):p.write_bytes((json.dumps(r,indent=2)+'\n').encode())
def main():
 p=argparse.ArgumentParser();p.add_argument('--project-root',type=Path,required=True);p.add_argument('--tool-dir',type=Path,required=True);p.add_argument('--language',choices=['c','cpp','both'],default='both');p.add_argument('--build-root',type=Path);p.add_argument('--source-dir',type=Path);p.add_argument('--enable-shrink-wrap',action='store_true');p.add_argument('--split-restore-region',action='store_true');a=p.parse_args();root=a.project_root.resolve();model=root/MODEL;source=a.source_dir.resolve() if a.source_dir else model/'src';need(source.is_relative_to(model),'owned source directory');old=next(p for p in (root/'analysis/v4160-ota-tx-2026-10-22/implementation/verify_native.py',root/'apk-analysis/tsl9-v4160-ota-tx-2026-10-22/implementation/verify_native.py') if p.is_file());need(sha(old)==OLDPIN,'immutable prior profile');flags=runpy.run_path(str(old))['flags'];tools={n:next(p for p in (a.tool_dir/(n+'.exe'),a.tool_dir/n) if p.is_file()) for n in ('clang','llvm-objdump')};need(sha(tools['clang'])==CLANG,'actual LLVM identity');base=a.build_root.resolve() if a.build_root else model/'build'/('lowering-'+uuid.uuid4().hex);need(not base.exists() and base.is_relative_to(root),'create-only project build');base.mkdir(parents=True);initial={str(p):sha(p) for p in [*source.glob('*'),old,Path(__file__),*tools.values()]};results=[]
 def run(folder,label,argv):
  x=subprocess.run([str(v) for v in argv],cwd=folder,capture_output=True,timeout=120);log=folder/(label+'.log');log.write_bytes(x.stdout+x.stderr);need(x.returncode==0,'actual tool status '+label);return dict(label=label,argv=[str(v) for v in argv],exit=x.returncode,log=log.name,sha256=sha(log))
 helpcmd=run(base,'help-hidden',[tools['clang'],'--target=riscv32-unknown-elf','-x','c','-c','NUL' if sys.platform=='win32' else '/dev/null','-o',base/'NO-HELP-OBJECT.o','-mllvm','--help-hidden']);helptext=(base/'help-hidden.log').read_text();matched=[l.strip() for l in helptext.splitlines() if 'shrink-wrap' in l or 'prologepilog' in l];need(any('enable-shrink-wrap' in l for l in matched),'actual supported shrink-wrap option')
 for mode in ('c','cpp') if a.language=='both' else [a.language]:
  folder=base/mode;folder.mkdir();commands=[];f=flags(mode)+(['-mllvm','-enable-shrink-wrap=true'] if a.enable_shrink_wrap else [])+(['-mllvm','-enable-shrink-wrap-region-split=true'] if a.split_restore_region else []);src=source/'tx_native.c'
  commands.append(run(folder,'resource-dir',[tools['clang'],'-print-resource-dir']));resource=Path((folder/'resource-dir.log').read_text().strip())/'include/stdint.h';resource_pin=sha(resource)
  for name,extra in [('tx_native.o',['-c','-MD','-MF',folder/'tx_native.d','-MT','tx_native.o']),('tx_native.ll',['-S','-emit-llvm']),('before-prologepilog.mir',['-S','-mllvm','-stop-before=prologepilog']),('after-prologepilog.mir',['-S','-mllvm','-stop-after=prologepilog'])]:commands.append(run(folder,name,[tools['clang'],*f,*extra,src,'-o',folder/name]))
  commands.append(run(folder,'disassembly',[tools['llvm-objdump'],'-d',folder/'tx_native.o']));need(sha(resource)==resource_pin,'stable actual resource header');r=dict(schema='TSL9-TX-bounded-lowering-diagnosis-v1',mode=mode,profile='enable-shrink-wrap=true' if a.enable_shrink_wrap else 'unchanged-published-profile',commands=commands,resource=dict(path=str(resource),sha256=resource_pin),input_pins=initial,artifacts={p.name:dict(bytes=p.stat().st_size,sha256=sha(p)) for p in folder.iterdir() if p.is_file()},RV32_execution=False,ISA_emulation=False,hardware=False,network=False);write(folder/'diagnosis.json',r);results.append(dict(mode=mode,receipt=str(folder/'diagnosis.json'),sha256=sha(folder/'diagnosis.json')))
 need(all(sha(Path(n))==pin for n,pin in initial.items()),'stable exact sources/tools/runner');write(base/'results.json',dict(results=results,matched_LLVM_options=matched,help_command=helpcmd));print(json.dumps(dict(passed=True,results=results,matched_LLVM_options=matched,RV32_execution=False)))
if __name__=='__main__':main()
