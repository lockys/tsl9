#!/usr/bin/env python3
"""One fixed offline C/C++ compilation profile; never execute target code."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
FIRMWARE_SHA = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
TOOLS = {'clang':'047dfde05acc6fcce5af669e25cd8d40b4f509b8842d151d6d8a43a1c6a35fd6',
         'ld.lld':'fe7f55c0c78b3d87f33b905a3874e10e872ca7beef53a8199d7ff9ac6641ec3f',
         'llvm-objdump':'de40d1188fe63ff373e1a5dd83a12e2cb4545ca3b314da16a476ecf072e5a0fa'}
STDINT_SHA = '7ce5540d5fb6e8da9760928e76cbdd5ebef329d701ad598d30d8e6f9d5d78b34'


def need(value, message):
    if not value:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def flags(mode):
    return ['--target=riscv32-unknown-elf','-march=rv32imac_zicsr','-mabi=ilp32','-Oz',
            '-mllvm','-enable-machine-outliner=never','-ffreestanding','-fno-builtin',
            '-fno-stack-protector','-fno-unwind-tables','-fno-asynchronous-unwind-tables',
            '-mno-relax','-ffunction-sections','-fdata-sections','-Wall','-Wextra','-Werror',
            *['-ffixed-x'+str(n) for n in range(1,32) if n not in (10,15)],
            '-x','c' if mode == 'c' else 'c++','-std=c11' if mode == 'c' else '-std=c++17',
            *(['-fno-exceptions'] if mode == 'cpp' else [])]


def recipes(tools, folder, mode):
    source = HERE/'src/providers.c'
    return [('compiler-help',[tools['clang'],'--help']),
            ('resource',[tools['clang'],'-print-resource-dir']),
            ('compile',[tools['clang'],*flags(mode),'-c','-MD','-MF',folder/'native.d','-MT','native.o',source,'-o',folder/'native.o']),
            ('IR',[tools['clang'],*flags(mode),'-S','-emit-llvm',source,'-o',folder/'native.ll']),
            ('link',[tools['ld.lld'],'--no-relax','-T',HERE/'component.ld',folder/'native.o','-o',folder/'COMPONENT-ONLY-NOT-FIRMWARE.elf']),
            ('disassemble-object',[tools['llvm-objdump'],'--mattr=+m,+a,+c,+zicsr','-d','-r',folder/'native.o']),
            ('disassemble-linked',[tools['llvm-objdump'],'--mattr=+m,+a,+c,+zicsr','-d','-r',folder/'COMPONENT-ONLY-NOT-FIRMWARE.elf'])]


def inputs(firmware, tools):
    stdint = tools['clang'].parent.parent/'lib/clang/18/include/stdint.h'
    paths = [HERE/'build.py',HERE/'src/providers.c',HERE/'component.ld',firmware,stdint,*tools.values()]
    return {str(p):sha(p) for p in paths}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--project-root',required=True,type=Path)
    p.add_argument('--tool-dir',required=True,type=Path)
    p.add_argument('--firmware',required=True,type=Path)
    p.add_argument('--build-root',required=True,type=Path)
    a = p.parse_args()
    need(HERE == a.project_root.resolve()/'experiments/tsl9-queue-small-providers','Owned canonical experiment')
    firmware = a.firmware.resolve()
    need(sha(firmware) == FIRMWARE_SHA and firmware.stat().st_size == 76800,'Official V4.1.60 identity')
    tools = {name:(a.tool_dir/(name+('.exe' if os.name == 'nt' else ''))).resolve() for name in TOOLS}
    need(all(sha(tools[n]) == pin for n,pin in TOOLS.items()),'Pinned existing local LLVM binaries')
    need(sha(tools['clang'].parent.parent/'lib/clang/18/include/stdint.h') == STDINT_SHA,'Actual stdint resource')
    output = a.build_root.resolve()
    need(output.is_relative_to(HERE/'build') and not output.exists(),'Create-only owned build directory')
    frozen = inputs(firmware,tools)
    output.mkdir(parents=True)
    receipts = []
    for mode in ('c','cpp'):
        folder = output/mode
        folder.mkdir()
        commands = []
        for label,argv in recipes(tools,folder,mode):
            try:
                run = subprocess.run([str(x) for x in argv],cwd=folder,capture_output=True,timeout=120)
            except subprocess.TimeoutExpired as error:
                (folder/(label+'.log')).write_bytes((error.stdout or b'')+(error.stderr or b''))
                raise
            log = folder/(label+'.log')
            log.write_bytes(run.stdout+run.stderr)
            commands.append(dict(label=label,argv=[str(x) for x in argv],exit=run.returncode,log_sha256=sha(log)))
            need(run.returncode == 0,'Retained '+label+' failure; no retry or new profile')
        need(frozen == inputs(firmware,tools),'Source/tool stability across compile')
        record = dict(schema='TSL9-queue-small-provider-build-v1',mode=mode,firmware=str(firmware),
                      tools={n:str(f) for n,f in tools.items()},inputs=frozen,commands=commands,
                      artifacts={f.name:sha(f) for f in folder.iterdir() if f.is_file()},
                      target_execution=False,HOST_execution=False,network=False,BIN_generated=False,
                      firmware_ready=False,physical_placement_proved=False,installed_ROM_proved=False)
        receipt = folder/'compile-receipt.json'
        receipt.write_bytes((json.dumps(record,indent=2)+'\n').encode())
        receipts.append(dict(path=str(receipt),sha256=sha(receipt)))
    print(json.dumps(dict(compiled=True,single_profile=True,receipts=receipts,target_execution=False)))


if __name__ == '__main__':
    main()
