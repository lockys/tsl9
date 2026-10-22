#!/usr/bin/env python3
"""Compile a diagnostic reset/clock composition; no target execution or BIN."""
import argparse
import hashlib
import json
from pathlib import Path
import runpy
import subprocess
import sys

sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
MODEL='experiments/tsl9-runtime-reset-clock-fit'
OLD='experiments/tsl9-runtime-reset-clock'
FALL='experiments/tsl9-boot-clock-fallthrough'
PINS={
    "experiments/tsl9-runtime-reset-clock/verify.py": "9e6e518c4abbc5f3299b3061cd73256714fdae43c6ce931d0e37c91daadee513",
    "experiments/tsl9-runtime-reset-clock/probe.py": "76755454ec4b52cccecd11f16c7f8884ca8020ec1bee6bd91b7d913c5a787d53",
    "experiments/tsl9-boot-clock-fallthrough/verify.py": "419e4c60188f18a805a2f28926412e788622c68e0972cd0e478f4538b9c618e3",
    "experiments/tsl9-boot-clock-fallthrough/probe.py": "138406641a99941b13c19065952c36ae586658a84d5e66aa1b8dabb40614b963",
    "experiments/tsl9-boot-clock-fallthrough/source_edges.py": "9151f5a1fbe1f7cde4878d674d1a5e1cc48860161e8ea2cd028505fa9ba02a2b",
    "experiments/tsl9-boot-clock-fallthrough/src/clock_fallthrough.c": "a5469ac723d8f4c462049b84b0a22ac15d78c182dd2d22dc61ccec641e97066c"
}


def need(ok,message):
    if not ok:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(root,tool_dir):
    need(HERE==root/MODEL,'Canonical composition model')
    for name,pin in PINS.items():
        need(sha(root/name)==pin,'Frozen reviewed reader/source: '+name)
    parent=runpy.run_path(str(root/OLD/'verify.py'))
    for name,pin in parent['PINS'].items():
        need(sha(root/name)==pin,'Frozen original reset dependency: '+name)
    shared=runpy.run_path(str(root/FALL/'probe.py'))
    prior,tools,header=shared['load'](root,tool_dir)
    flag_owner=runpy.run_path(str(root/OLD/'probe.py'))
    return prior,tools,header,parent,shared,flag_owner


def sources(root,policy):
    need(policy in ('origin','curated'),'Explicit reviewed clock source policy')
    origin=root/FALL/'src/clock_fallthrough.c'
    result=dict(memory=root/'src/native/startup/reset_memory.c',ports=root/'src/native/startup/reset_ports.c',
                data=root/'src/native/startup/reset_data.c',
                clock=origin if policy=='origin' else root/'src/native/clock/clock_init.c')
    for unit in ('memory','ports','data'):
        need(result[unit].read_bytes()==(root/OLD/'src'/result[unit].name).read_bytes(),
             'Curated reset source equals frozen original reconstruction')
    need(result['clock'].read_bytes()==origin.read_bytes(),'Clock source equals reviewed fall-through C')
    return result


def inputs(root,policy,prior,tools,header,parent,shared):
    paths={Path(__file__).resolve(),HERE/'component.ld',*[root/n for n in PINS],
           *[root/n for n in parent['PINS']],*[root/n for n in prior['SOURCE_PINS']],
           *sources(root,policy).values(),root/'experiments/tsl9-boot-clock-prefix/src/clock_prefix.c',
           *tools.values(),header}
    return {shared['portable'](path,root,tools,header):sha(path) for path in sorted(paths)}


def recipes(root,folder,mode,policy,prior,tools,flag_owner):
    units=sources(root,policy);jobs=[]
    for unit,source in units.items():
        common=[tools['clang'],*flag_owner['flags'](prior,mode,unit)]
        jobs += [
            (unit+'-compile',[*common,'-c','-MD','-MF',folder/(unit+'.d'),'-MT',unit+'.o',source,'-o',folder/(unit+'.o')]),
            (unit+'-IR',[*common,'-S','-emit-llvm',source,'-o',folder/(unit+'.ll')])]
    common=[tools['clang'],*prior['flags'](mode)]
    prefix=root/'experiments/tsl9-boot-clock-prefix/src/clock_prefix.c'
    elf=folder/'COMPONENT-ONLY-NOT-FIRMWARE.elf'
    jobs += [
        ('prefix-compile',[*common,'-c','-MD','-MF',folder/'prefix.d','-MT','prefix.o',prefix,'-o',folder/'prefix.o']),
        ('prefix-IR',[*common,'-S','-emit-llvm',prefix,'-o',folder/'prefix.ll']),
        ('register-IR',[*common,'-S','-emit-llvm',root/'experiments/tsl9-boot-clock-registers/src/clock_registers.c','-o',folder/'register.ll']),
        ('link',[tools['ld.lld'],'--no-relax','-T',HERE/'component.ld',*[folder/(u+'.o') for u in units],'-o',elf]),
        ('linked',[tools['llvm-objdump'],'--mattr=+m,+a,+c,+zicsr,+zifencei','-d','-r',elf]),
        ('memory-object',[tools['llvm-objdump'],'--mattr=+m,+a,+c,+zicsr,+zifencei','-d','-r',folder/'memory.o']),
        ('clock-object',[tools['llvm-objdump'],'--mattr=+m,+a,+c,+zicsr,+zifencei','-d','-r',folder/'clock.o']),
        ('prefix-object',[tools['llvm-objdump'],'--mattr=+m,+a,+c,+zicsr,+zifencei','-d','-r',folder/'prefix.o'])]
    return jobs


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--project-root',type=Path,required=True)
    p.add_argument('--tool-dir',type=Path,required=True)
    p.add_argument('--build-root',type=Path,required=True)
    p.add_argument('--clock-source',choices=('origin','curated'),default='origin')
    a=p.parse_args();root=a.project_root.resolve();out=a.build_root.resolve()
    prior,tools,header,parent,shared,flag_owner=load(root,a.tool_dir.resolve())
    need(out.is_relative_to(HERE/'build') and not out.exists(),'New owned diagnostic build directory')
    frozen=inputs(root,a.clock_source,prior,tools,header,parent,shared)
    out.mkdir(parents=True)
    for mode in ('c','cpp'):
        folder=out/mode;folder.mkdir();commands=[]
        for label,argv in recipes(root,folder,mode,a.clock_source,prior,tools,flag_owner):
            run=subprocess.run([str(x) for x in argv],capture_output=True,timeout=120,cwd=root)
            log=folder/(label+'.log');log.write_bytes(run.stdout+run.stderr)
            commands.append(dict(label=label,argv=[shared['portable'](x,root,tools,header) for x in argv],
                                 exit=run.returncode,log_sha256=sha(log)))
            need(run.returncode==0,'Failed local command; inspect '+label+'.log')
        need(inputs(root,a.clock_source,prior,tools,header,parent,shared)==frozen,'Compile input stability')
        record=dict(schema='TSL9-runtime-reset-clock-fit-probe-v1',mode=mode,clock_source=a.clock_source,
                    inputs=frozen,commands=commands,target_execution=False,ISA_emulation=False,BIN_generated=False)
        (folder/'compile-receipt.json').write_bytes((json.dumps(record,indent=2)+'\n').encode())
    print(json.dumps(dict(compiled=True,clock_source=a.clock_source,target_execution=False,BIN_generated=False)))


if __name__=='__main__':
    main()
