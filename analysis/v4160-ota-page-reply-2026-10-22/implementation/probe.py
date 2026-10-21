"""One source-grounded local profile. Native files are never executed."""
import argparse,hashlib,importlib.util,json,subprocess,uuid
from pathlib import Path
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--project-root',required=True,type=Path);p.add_argument('--tool-dir',required=True,type=Path);p.add_argument('--language',choices=['c','cpp','both'],default='both');a=p.parse_args();root=a.project_root.resolve();model=root/'experiments/tsl9-v4160-ota-page-reply';work=model/'build'/('first-native-'+uuid.uuid4().hex);results=[]
 parser=root/'apk-analysis/tsl9-v4160-irq-native-2026-10-21/compiler-review/elf32.py';assert sha(parser)=='00a231e3bbd881a9961c12fefd15565364cd813250a46a7b20851a6b9f3a2141';spec=importlib.util.spec_from_file_location('reply_probe_elf',parser);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 for mode in (['c','cpp'] if a.language=='both' else[a.language]):
  folder=work/mode;folder.mkdir(parents=True);commands=[]
  allowed={1,2,5,6,7,*range(10,18),*range(28,32)}
  flags=['--target=riscv32-unknown-elf','-march=rv32imac_zicsr','-mabi=ilp32','-Oz','-mllvm','-enable-machine-outliner=never','-ffreestanding','-fno-builtin','-fno-stack-protector','-fno-unwind-tables','-fno-asynchronous-unwind-tables','-mno-relax','-ffunction-sections','-fdata-sections','-Wall','-Wextra','-Werror',*['-ffixed-x'+str(i) for i in range(1,32) if i not in allowed],'-x','c' if mode=='c' else'c++','-std=c11' if mode=='c' else'-std=c++17',*(['-fno-exceptions']if mode=='cpp' else[])]
  def run(label,args):
   r=subprocess.run([str(x)for x in args],capture_output=True,cwd=folder,timeout=120);log=folder/(label+'.log');log.write_bytes(r.stdout+r.stderr);commands.append(dict(argv=[str(x)for x in args],exit=r.returncode,log=log.name,log_sha256=sha(log)));return r.returncode
  for suffix,action in[('.o',['-c']),('.ll',['-S','-emit-llvm'])]:run('compile'+suffix,[a.tool_dir/'clang.exe',*flags,*action,model/'src/page_reply.c','-o',folder/('page_reply'+suffix)])
  result=dict(mode=mode,source={p.name:sha(p)for p in(model/'src').glob('*')},commands=commands,compiled=all(x['exit']==0 for x in commands),target_execution=False,emulation=False,network=False)
  if result['compiled']:
   e=m.ELF(folder/'page_reply.o');s=next(x for x in e.symbols if x['name']=='tsl9_ota_page_reply_9b8e');result.update(bytes=s['size'],original_bytes=124,original_extent_fits=s['size']<=124,UND=[x['name']for x in e.symbols if x['index']==0 and x['name']],RELA=len(e.relocations));run('disassembly',[a.tool_dir/'llvm-objdump.exe','-d',folder/'page_reply.o'])
  (folder/'probe.json').write_bytes((json.dumps(result,indent=2)+'\n').encode());results.append(dict(receipt=str(folder/'probe.json'),**{k:v for k,v in result.items()if k not in('commands','source')}))
 print(json.dumps(dict(results=results,target_execution=False)))
if __name__=='__main__':main()
