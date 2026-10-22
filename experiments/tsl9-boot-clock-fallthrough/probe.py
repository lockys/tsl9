#!/usr/bin/env python3
"""Compile/disassemble an offline clock component; never execute target code."""
import argparse
import hashlib
import json
from pathlib import Path
import runpy
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
MODEL = 'experiments/tsl9-boot-clock-fallthrough'
BASE = 'experiments/tsl9-boot-clock-registers/verify.py'
BASE_SHA = '096660430ae0aa0f44813192aa30c49c958b8180e4123249a5aa36eeab11a7a8'
PREFIX = 'experiments/tsl9-boot-clock-prefix'
PREFIX_SHA = '8befcde0b7afe9c890ad85207912e9fa2bc7ac9265334af090eff36cb65890bf'


def need(ok,message):
    if not ok:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(root,tool_dir):
    need(HERE==root/MODEL and sha(root/BASE)==BASE_SHA,'Canonical model and baseline')
    need(sha(root/PREFIX/'verify.py')==PREFIX_SHA,'Frozen prefix verifier')
    prior=runpy.run_path(str(root/BASE))
    for name,pin in prior['SOURCE_PINS'].items():
        need(sha(root/name)==pin,'Reviewed source dependency: '+name)
    tools={n:(tool_dir/(n+('.exe' if sys.platform=='win32' else ''))).resolve() for n in prior['TOOLS']}
    need(all(sha(tools[n])==pin for n,pin in prior['TOOLS'].items()),'Declared existing LLVM tools')
    header=tools['clang'].parent.parent/'lib/clang/18/include/stdint.h'
    need(sha(header)==prior['STDINT_SHA'],'Reviewed compiler header')
    return prior,tools,header


def portable(value,root,tools,header):
    text=str(value).replace('\\','/')
    bases=[(header.parent,'${CLANG_INCLUDE}'),(tools['clang'].parent,'${LLVM_BIN}'),(root,'${PROJECT_ROOT}')]
    for base,label in bases:
        prefix=base.as_posix()
        if text==prefix or text.startswith(prefix+'/'):
            return label+text[len(prefix):]
    return text


def inputs(root,prior,tools,header):
    paths={Path(__file__).resolve(),HERE/'src/clock_fallthrough.c',HERE/'component.ld',
           root/BASE,root/PREFIX/'verify.py',root/PREFIX/'src/clock_prefix.c',
           *[root/n for n in prior['SOURCE_PINS']],*tools.values(),header}
    return {portable(p,root,tools,header):sha(p) for p in sorted(paths)}


def recipes(root,folder,mode,prior,tools):
    source=HERE/'src/clock_fallthrough.c'
    old=root/PREFIX/'src/clock_prefix.c'
    common=[tools['clang'],*prior['flags'](mode)]
    elf=folder/'COMPONENT-ONLY-NOT-FIRMWARE.elf'
    return [
        ('compile',[*common,'-c','-MD','-MF',folder/'native.d','-MT','native.o',source,'-o',folder/'native.o']),
        ('IR',[*common,'-S','-emit-llvm',source,'-o',folder/'native.ll']),
        ('prefix-compile',[*common,'-c','-MD','-MF',folder/'prefix.d','-MT','prefix.o',old,'-o',folder/'prefix.o']),
        ('prefix-IR',[*common,'-S','-emit-llvm',old,'-o',folder/'prefix.ll']),
        ('register-IR',[*common,'-S','-emit-llvm',root/'experiments/tsl9-boot-clock-registers/src/clock_registers.c','-o',folder/'register.ll']),
        ('link',[tools['ld.lld'],'--no-relax','-T',HERE/'component.ld',folder/'native.o','-o',elf]),
        ('object',[tools['llvm-objdump'],'--mattr=+m,+a,+c,+zicsr,+zifencei','-d','-r',folder/'native.o']),
        ('prefix-object',[tools['llvm-objdump'],'--mattr=+m,+a,+c,+zicsr,+zifencei','-d','-r',folder/'prefix.o']),
        ('linked',[tools['llvm-objdump'],'--mattr=+m,+a,+c,+zicsr,+zifencei','-d','-r',elf]),
    ]


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--project-root',type=Path,required=True)
    p.add_argument('--tool-dir',type=Path,required=True)
    p.add_argument('--build-root',type=Path,required=True)
    a=p.parse_args();root=a.project_root.resolve();out=a.build_root.resolve()
    prior,tools,header=load(root,a.tool_dir.resolve())
    need(out.is_relative_to(HERE/'build') and not out.exists(),'New owned build directory required')
    frozen=inputs(root,prior,tools,header)
    out.mkdir(parents=True)
    for mode in ('c','cpp'):
        folder=out/mode;folder.mkdir()
        records=[]
        for label,argv in recipes(root,folder,mode,prior,tools):
            argv=[str(x) for x in argv]
            actual=subprocess.run(argv,capture_output=True,timeout=120,cwd=root)
            log=folder/(label+'.log');log.write_bytes(actual.stdout+actual.stderr)
            records.append(dict(label=label,argv=[portable(x,root,tools,header) for x in argv],
                                exit=actual.returncode,log_sha256=sha(log)))
            need(actual.returncode==0,'Failed command; inspect local '+label+'.log')
        need(inputs(root,prior,tools,header)==frozen,'Input changed during build')
        record=dict(schema='TSL9-clock-fallthrough-probe-v1',mode=mode,inputs=frozen,commands=records,
                    target_execution=False,ISA_emulation=False,BIN_generated=False)
        (folder/'compile-receipt.json').write_bytes((json.dumps(record,indent=2)+'\n').encode('utf-8'))
    print(json.dumps(dict(compiled=True,target_execution=False,BIN_generated=False)))


if __name__=='__main__':
    main()
