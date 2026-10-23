#!/usr/bin/env python3
"""One fixed local compilation profile; never execute any produced target."""
from pathlib import Path
import argparse,hashlib,json,subprocess
ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def portable(value,llvm):
    if isinstance(value,dict):return {portable(k,llvm):portable(v,llvm) for k,v in value.items()}
    if isinstance(value,(list,tuple)):return [portable(x,llvm) for x in value]
    if isinstance(value,Path):value=str(value)
    if isinstance(value,str):
        for token,path in [(' ${CLANG_INCLUDE}',llvm.parent/'lib/clang/18/include'),(' ${LLVM_BIN}',llvm),(' ${TSL9_ROOT}',ROOT)]:
            value=value.replace(str(path),token.strip()).replace(str(path).replace('\\','/'),token.strip())
        return value.replace('\\','/')
    return value
def flags(language):
    return ['--target=riscv32-unknown-elf','-march=rv32imac_zicsr','-mabi=ilp32','-Oz','-mllvm','-enable-machine-outliner=never','-ffreestanding','-fno-builtin','-fno-stack-protector','-fno-unwind-tables','-fno-asynchronous-unwind-tables','-mno-relax','-ffunction-sections','-fdata-sections','-Wall','-Wextra','-Werror']+['-ffixed-x'+str(i) for i in range(1,32) if i not in (10,14,15)]+(['-x','c','-std=c11'] if language=='c' else ['-x','c++','-std=c++17','-fno-exceptions'])
def recipes(llvm,folder,language,source):
    clang=llvm/'clang.exe';objdump=llvm/'llvm-objdump.exe'
    return [('compile',[clang,*flags(language),'-MD','-MF',folder/'native.d','-MT','native.o','-c',source,'-o',folder/'native.o']),
     ('IR',[clang,*flags(language),'-S','-emit-llvm',source,'-o',folder/'native.ll']),
     ('object',[objdump,'--mattr=+m,+a,+c,+zicsr','-d','-r','-t','-h',folder/'native.o']),
     ('link',[llvm/'ld.lld.exe','--no-relax','-T',HERE/'component.ld',folder/'native.o','-o',folder/'COMPONENT-ONLY-NOT-FIRMWARE.elf']),
     ('linked',[objdump,'--mattr=+m,+a,+c,+zicsr','-d','-r','-t','-h',folder/'COMPONENT-ONLY-NOT-FIRMWARE.elf'])]
def build(llvm,folder,language,source):
    assert folder.is_relative_to(HERE/'build') and not folder.exists(),'fresh owned output only'
    inputs=[source,HERE/'component.ld',Path(__file__).resolve()]+[llvm/n for n in ('clang.exe','ld.lld.exe','llvm-objdump.exe')]+[llvm.parent/'lib/clang/18/include/stdint.h']
    before={str(p):sha(p) for p in inputs};folder.mkdir(parents=True);commands=[]
    for label,argv in recipes(llvm,folder,language,source):
        process=subprocess.run([str(x) for x in argv],cwd=folder,capture_output=True)
        (folder/(label+'.log')).write_bytes(process.stdout+process.stderr)
        commands.append(dict(label=label,argv=portable(argv,llvm),returncode=process.returncode))
        (folder/'recipes.json').write_bytes((json.dumps(commands,indent=2)+'\n').encode())
        assert process.returncode==0,'retained failing '+label+'; no profile search'
    assert before=={str(p):sha(p) for p in inputs}
    return commands
def main():
    p=argparse.ArgumentParser();p.add_argument('--version',required=True,type=int);p.add_argument('--out-dir',required=True,type=Path);p.add_argument('--llvm-bin',type=Path,default=Path.home()/'AppData/Local/Android/Sdk/ndk/27.1.12297006/toolchains/llvm/prebuilt/windows-x86_64/bin');a=p.parse_args();llvm=a.llvm_bin.resolve();source=HERE/'src'/('predicate.v'+str(a.version)+'.c')
    for language in ('c','cpp'):
        folder=a.out_dir.resolve()/language;build(llvm,folder,language,source);print(json.dumps(dict(language=language,source_sha256=sha(source),native_sha256=sha(folder/'native.o'),linked_sha256=sha(folder/'COMPONENT-ONLY-NOT-FIRMWARE.elf'))))
if __name__=='__main__':main()
