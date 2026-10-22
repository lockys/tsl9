#!/usr/bin/env python3
"""Compile/link diagnostic reset/clock components without executing targets."""
import argparse
import hashlib
import json
from pathlib import Path
import runpy
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
BASE = 'experiments/tsl9-boot-clock-registers/verify.py'
BASE_SHA = '096660430ae0aa0f44813192aa30c49c958b8180e4123249a5aa36eeab11a7a8'
CLOCK_SHA = '9cbdc2d1e74ae0d6facc5db02cd1d9d5e08f2d7791e4df800eba716d6d32b142'


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def flags(prior,mode,unit):
    flags = prior['flags'](mode)
    if unit != 'clock':
        flags = [x for x in flags if not x.startswith('-ffixed-x')]
        flags += ['-ffixed-x'+str(n) for n in range(1,32) if n not in {2,5,10,11,12}]
    return flags


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--project-root',required=True,type=Path)
    p.add_argument('--tool-dir',required=True,type=Path)
    p.add_argument('--build-root',required=True,type=Path)
    a = p.parse_args()
    root,out = a.project_root.resolve(),a.build_root.resolve()
    if HERE!=root/'experiments/tsl9-runtime-reset-clock' or out.exists() or not out.is_relative_to(HERE/'build'):
        raise ValueError('New canonical owned build directory required')
    if sha(root/BASE)!=BASE_SHA:
        raise ValueError('Reviewed baseline')
    prior = runpy.run_path(str(root/BASE))
    tools = {n:a.tool_dir/(n+'.exe' if sys.platform=='win32' else n) for n in prior['TOOLS']}
    if not all(sha(tools[n])==pin for n,pin in prior['TOOLS'].items()):
        raise ValueError('Declared existing LLVM tools only')
    sources = dict(memory=root/'src/native/startup/reset_memory.c',ports=root/'src/native/startup/reset_ports.c',
                   data=root/'src/native/startup/reset_data.c',clock=root/'src/native/clock/clock_init.c')
    origins = [HERE/'src'/sources[n].name for n in ('memory','ports','data')]
    if not all(origin.read_bytes()==sources[n].read_bytes() for origin,n in zip(origins,('memory','ports','data'))):
        raise ValueError('Curated startup files must equal the reviewed experiment sources')
    if sha(sources['clock'])!=CLOCK_SHA:
        raise ValueError('Reviewed actual clock entry')
    stdint = tools['clang'].parent.parent/'lib/clang/18/include/stdint.h'
    if sha(stdint)!=prior['STDINT_SHA']:
        raise ValueError('Reviewed header')
    inputs = {str(x):sha(x) for x in (Path(__file__).resolve(),root/BASE,HERE/'component.ld',stdint,*sources.values(),*origins,*tools.values())}
    out.mkdir(parents=True)
    for mode in ('c','cpp'):
        folder = out/mode
        folder.mkdir()
        jobs = []
        for unit,source in sources.items():
            common = [tools['clang'],*flags(prior,mode,unit)]
            jobs += [(unit+'-compile', [*common,'-c','-MD','-MF',folder/(unit+'.d'),'-MT',unit+'.o',source,'-o',folder/(unit+'.o')]),
                     (unit+'-IR', [*common,'-S','-emit-llvm',source,'-o',folder/(unit+'.ll')])]
        elf = folder/'COMPONENT-ONLY-NOT-FIRMWARE.elf'
        jobs += [('link',[tools['ld.lld'],'--no-relax','-T',HERE/'component.ld',*[folder/(u+'.o') for u in sources],'-o',elf]),
                 ('linked',[tools['llvm-objdump'],'--mattr=+m,+a,+c,+zicsr,+zifencei','-d','-r',elf]),
                 ('memory-object',[tools['llvm-objdump'],'--mattr=+m,+a,+c,+zicsr,+zifencei','-d','-r',folder/'memory.o'])]
        commands = []
        for label,argv in jobs:
            argv = [str(x) for x in argv]
            run = subprocess.run(argv,capture_output=True,timeout=120)
            log = folder/(label+'.log')
            log.write_bytes(run.stdout+run.stderr)
            commands.append(dict(label=label,argv=argv,exit=run.returncode,log_sha256=sha(log)))
            if run.returncode:
                raise ValueError('See '+str(log))
        if not all(sha(Path(x))==pin for x,pin in inputs.items()):
            raise ValueError('Input changed while building')
        record = dict(schema='TSL9-runtime-reset-clock-probe-v1',mode=mode,inputs=inputs,
                      tools={n:str(x) for n,x in tools.items()},commands=commands,
                      target_execution=False,BIN_generated=False,resident_implemented=False)
        (folder/'compile-receipt.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(compiled=True,build_root=str(out),target_execution=False,BIN_generated=False)))


if __name__=='__main__':
    main()
