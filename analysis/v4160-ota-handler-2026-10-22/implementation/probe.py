#!/usr/bin/env python3
"""Compile readable OTA C/C++ to ET_REL/IR only; never link or execute RV32."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import runpy
import subprocess
import sys
import uuid
sys.dont_write_bytecode=True
MODEL='experiments/tsl9-v4160-ota-handler'
TOOLS={'clang':'047dfde05acc6fcce5af669e25cd8d40b4f509b8842d151d6d8a43a1c6a35fd6',
       'llvm-objdump':'de40d1188fe63ff373e1a5dd83a12e2cb4545ca3b314da16a476ecf072e5a0fa'}
PARSER='00a231e3bbd881a9961c12fefd15565364cd813250a46a7b20851a6b9f3a2141'
def H(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def need(v,m):
    if not v:raise ValueError(m)
def flags(mode):
    return ['--target=riscv32-unknown-elf','-march=rv32imac_zicsr','-mabi=ilp32','-Oz',
            '-mllvm','-enable-machine-outliner=never','-ffreestanding','-fno-builtin',
            '-fno-stack-protector','-fno-unwind-tables','-fno-asynchronous-unwind-tables',
            '-mno-relax','-ffunction-sections','-fdata-sections','-Wall','-Wextra','-Werror',
            '-x','c' if mode=='c' else 'c++','-std=c11' if mode=='c' else '-std=c++17']+(['-fno-exceptions'] if mode=='cpp' else [])
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--project-root',required=True,type=Path)
    p.add_argument('--tool-dir',required=True,type=Path);p.add_argument('--build-root',type=Path)
    p.add_argument('--language',choices=['c','cpp','both'],default='both');a=p.parse_args();root=a.project_root.resolve()
    tools={n:next(p for p in(a.tool_dir/(n+'.exe'),a.tool_dir/n) if p.is_file()).resolve() for n in TOOLS}
    need(all(H(p)==TOOLS[n] for n,p in tools.items()),'Explicit pinned local LLVM binaries')
    parser=next(p for p in(root/'analysis/v4160-irq-native-2026-10-21/compiler-review/elf32.py',root/'apk-analysis/tsl9-v4160-irq-native-2026-10-21/compiler-review/elf32.py') if p.is_file())
    need(H(parser)==PARSER,'Immutable ELF field reader');E=runpy.run_path(str(parser))['ELF']
    owner=(root/MODEL/'build').resolve();base=a.build_root.resolve() if a.build_root else owner/('probe-'+uuid.uuid4().hex)
    need(base.is_relative_to(owner) and base!=owner and not base.exists(),'Create-only owned output scope');base.mkdir(parents=True)
    results=[]
    for mode in ('c','cpp') if a.language=='both' else(a.language,):
        folder=base/mode;folder.mkdir();tmp=folder/'compiler-temp';tmp.mkdir();env=dict(os.environ,TMP=str(tmp),TEMP=str(tmp))
        source=root/MODEL/'src/ota_handler.c';inputs=[source,source.with_name('io.h'),source.with_name('ota_handler.h'),Path(__file__).resolve(),parser,*tools.values()]
        pins={str(p):H(p) for p in inputs};commands=[]
        def run(label,argv):
            x=subprocess.run([str(v) for v in argv],cwd=folder,env=env,capture_output=True,timeout=120)
            log=folder/(label+'.log');log.write_bytes(x.stdout+x.stderr)
            commands.append(dict(label=label,argv=[str(v) for v in argv],exit=x.returncode,log=log.name,sha256=H(log)))
            need(x.returncode==0,'Actual tool failed: '+str(log));return x
        resource=Path(run('compiler-resource-dir',[tools['clang'],'-print-resource-dir']).stdout.decode().strip())/'include/stdint.h'
        pins[str(resource)]=H(resource)
        run('native-object',[tools['clang'],*flags(mode),'-c','-MD','-MF',folder/'ota_handler.d','-MT','ota_handler.o',source,'-o',folder/'ota_handler.o'])
        run('native-IR',[tools['clang'],*flags(mode),'-S','-emit-llvm',source,'-o',folder/'ota_handler.ll'])
        run('complete-static-disassembly',[tools['llvm-objdump'],'--mattr=+m,+a,+c,+zicsr','-d','-r',folder/'ota_handler.o'])
        need(all(H(Path(n))==pin for n,pin in pins.items()),'Stable source/tool/resource identities')
        e=E(folder/'ota_handler.o');functions=[dict(name=s['name'],size=s['size'],section=e.sections[s['index']]['name'],info=s['info']) for s in e.symbols if s['info']&15==2 and s['size']]
        allocated=[dict(name=s['name'],type=s['type'],flags=s['flags'],size=s['size']) for s in e.sections if s['flags']&2 and s['size']]
        und=[dict(name=s['name'],info=s['info']) for s in e.symbols if s['index']==0 and s['name']]
        record=dict(schema='TSL9-readable-OTA-handler-native-ETREL-probe-v1',passed=True,mode=mode,source_pins=pins,commands=commands,
                    functions=functions,allocated_sections=allocated,allocated_bytes=sum(s['size'] for s in allocated),
                    undefined_symbols=und,relocations=e.relocations,ET_REL=True,original_bytes=530,
                    original_ABI_admitted=False,original_placement_admitted=False,target_execution=False,linked=False,
                    metadata_embedded_as_code=False,artifacts={p.name:dict(bytes=p.stat().st_size,sha256=H(p)) for p in folder.iterdir() if p.is_file()})
        receipt=folder/'probe.json';receipt.write_bytes((json.dumps(record,indent=2)+'\n').encode())
        results.append(dict(mode=mode,receipt=str(receipt),sha256=H(receipt),functions=functions,allocated_bytes=record['allocated_bytes'],undefined_symbols=und))
    print(json.dumps(dict(passed=True,results=results,target_execution=False,linked=False)))
if __name__=='__main__':main()
