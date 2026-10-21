"""Bounded actual compile profile derived from each original write/argument set."""
import argparse,hashlib,importlib.util,json,os,subprocess,uuid
from pathlib import Path
H=Path(__file__).resolve().parent;R=H.parents[2];M='experiments/tsl9-v4160-flash-entry-order'
NAMES={0x9c0a:('quarter',64,{1,2,8,9,10,11,12,13,14,15,16}),0x18e90:('status',8,{10,15}),0x18e98:('unlock',30,{10,13,14,15}),0x18eb6:('lock',14,{10,13,14,15}),0x18ec4:('erase',46,{10,13,14,15}),0x18ef2:('program',100,{10,11,12,13,14,15,16})}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def need(v,m):
    if not v:raise ValueError(m)
def case(root,slug):
    return next(p for p in [root/'apk-analysis'/('tsl9-'+slug),root/'analysis'/slug] if p.is_dir())
def parser(root):
    p=case(root,'v4160-irq-native-2026-10-21')/'compiler-review/elf32.py';need(sha(p)=='00a231e3bbd881a9961c12fefd15565364cd813250a46a7b20851a6b9f3a2141','pinned parser');s=importlib.util.spec_from_file_location('flash_elf',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m.ELF
def flags(address,mode):
    allowed=NAMES[address][2]
    return ['--target=riscv32-unknown-elf','-march=rv32imac_zicsr','-mabi=ilp32','-Oz','-mllvm','-enable-machine-outliner=never','-ffreestanding','-fno-builtin','-fno-stack-protector','-fno-unwind-tables','-fno-asynchronous-unwind-tables','-mno-relax','-ffunction-sections','-fdata-sections','-Wall','-Wextra','-Werror',*['-ffixed-x'+str(i) for i in range(1,32) if i not in allowed],'-x','c' if mode=='c' else 'c++','-std=c11' if mode=='c' else '-std=c++17',*(['-fno-exceptions'] if mode=='cpp' else []),'-DFN_ONLY='+hex(address)]
def symbol(address):return 'tsl9_flash_'+NAMES[address][0]+'_'+format(address,'x')
def write(p,d):p.write_bytes((json.dumps(d,indent=2)+'\n').encode())
def build(root,folder,tool,mode):
    folder.mkdir(parents=True);E=parser(root);rows=[]
    def run(label,args):
        p=subprocess.run([str(x) for x in args],capture_output=True,cwd=folder,timeout=120);log=folder/(label+'.log');log.write_bytes(p.stdout+p.stderr)
        return dict(argv=[str(x) for x in args],exit=p.returncode,log=log.name,log_sha256=sha(log))
    for address,(name,limit,allowed) in NAMES.items():
        f=folder/(name+'.o');commands=[]
        for ext,action in [('.o',['-c']),('.ll',['-S','-emit-llvm'])]:commands.append(run(name+ext,[tool/'clang.exe',*flags(address,mode),*action,root/M/'src/flash_native.c','-o',folder/(name+ext)]))
        if any(r['exit'] for r in commands):rows.append(dict(address=address,name=name,compiled=False,commands=commands));continue
        e=E(f);fs=[s for s in e.symbols if s['index'] and s['info']&15==2 and s['size']];need(len(fs)==1 and fs[0]['name']==symbol(address),'single actual function')
        r=run(name+'-disassembly',[tool/'llvm-objdump.exe','-d',f]);commands.append(r)
        rows.append(dict(address=address,name=name,compiled=True,bytes=fs[0]['size'],original_bytes=limit,fits=fs[0]['size']<=limit,code_sha256=hashlib.sha256(e.function_bytes(fs[0])).hexdigest(),relocations=len(e.relocations),UND=sorted({s['name'] for s in e.symbols if s['index']==0 and s['name']}),commands=commands))
    if all(r['compiled'] for r in rows):
        script=folder/'original-entry-component.ld';script.write_bytes(('ENTRY('+symbol(0x9c0a)+')\nSECTIONS {\n'+''.join(' .flash_'+format(a,'x')+' '+hex(a)+' : { *(.text.'+symbol(a)+') }\n' for a in NAMES)+'}\n').encode())
        command=run('component-link',[tool/'ld.lld.exe','--no-relax','--no-undefined','-T',script,*[folder/(name+'.o') for name,_,_ in NAMES.values()],'-o',folder/'COMPONENT-ONLY-NOT-FIRMWARE.elf']);need(command['exit']==0,'actual complete six-provider component link')
        command2=run('component-disassembly',[tool/'llvm-objdump.exe','-d',folder/'COMPONENT-ONLY-NOT-FIRMWARE.elf'])
    else:command=command2=None
    result=dict(schema='TSL9-fixed-A0-flash-entry-order-native-probe-v1',mode=mode,source={p.name:sha(p) for p in (root/M/'src').glob('*') if p.is_file()},functions=rows,link_commands=[command,command2],profile_derived_from_original_write_and_argument_registers=True,target_execution=False,emulation=False,hardware=False,network=False)
    write(folder/'probe.json',result);return result
def main():
    p=argparse.ArgumentParser();p.add_argument('--project-root',type=Path,default=R);p.add_argument('--tool-dir',type=Path,required=True);p.add_argument('--language',choices=['c','cpp','both'],default='both');a=p.parse_args();root=a.project_root.resolve();work=root/M/'build'/('first-native-'+uuid.uuid4().hex);results=[]
    for mode in (['c','cpp'] if a.language=='both' else [a.language]):
        d=build(root,work/mode,a.tool_dir.resolve(),mode);results.append(dict(mode=mode,receipt=str(work/mode/'probe.json'),functions=[{k:r.get(k) for k in ('name','compiled','bytes','original_bytes','fits')} for r in d['functions']]))
    print(json.dumps(dict(results=results,target_execution=False)))
if __name__=='__main__':main()
