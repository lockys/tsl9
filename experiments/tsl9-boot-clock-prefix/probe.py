#!/usr/bin/env python3
"""Compile/link the private clock ABI experiment; never execute its output."""
import argparse
import hashlib
import json
from pathlib import Path
import runpy
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--project-root', required=True, type=Path)
    p.add_argument('--tool-dir', required=True, type=Path)
    p.add_argument('--build-root', required=True, type=Path)
    a = p.parse_args()
    root, output = a.project_root.resolve(), a.build_root.resolve()
    if HERE != root/'experiments/tsl9-boot-clock-prefix' or output.exists() or not output.is_relative_to(HERE/'build'):
        raise ValueError('Use a new owned build directory')
    prior_path = root/'experiments/tsl9-boot-clock-registers/verify.py'
    if sha(prior_path) != '096660430ae0aa0f44813192aa30c49c958b8180e4123249a5aa36eeab11a7a8':
        raise ValueError('Reviewed baseline verifier')
    prior = runpy.run_path(str(prior_path))
    tools = {n:a.tool_dir/(n+'.exe' if sys.platform == 'win32' else n) for n in prior['TOOLS']}
    if not all(sha(tools[n]) == pin for n,pin in prior['TOOLS'].items()):
        raise ValueError('Only declared local LLVM tools')
    source, linker = HERE/'src/clock_prefix.c', HERE/'component.ld'
    reference = root/'experiments/tsl9-boot-clock-registers/src/clock_registers.c'
    stdint = tools['clang'].parent.parent/'lib/clang/18/include/stdint.h'
    if sha(stdint) != prior['STDINT_SHA']:
        raise ValueError('Reviewed compiler header')
    for name,pin in prior['SOURCE_PINS'].items():
        if sha(root/name) != pin:
            raise ValueError('Baseline source closure: '+name)
    inputs = {str(x):sha(x) for x in (Path(__file__).resolve(),prior_path,source,linker,stdint,
                                      *tools.values(),*(root/n for n in prior['SOURCE_PINS']))}
    output.mkdir(parents=True)
    for mode in ('c','cpp'):
        folder = output/mode
        folder.mkdir()
        obj, elf = folder/'native.o', folder/'COMPONENT-ONLY-NOT-FIRMWARE.elf'
        recipes = [
            ('compile',[tools['clang'],*prior['flags'](mode),'-c','-MD','-MF',folder/'native.d','-MT','native.o',source,'-o',obj]),
            ('IR',[tools['clang'],*prior['flags'](mode),'-S','-emit-llvm',source,'-o',folder/'native.ll']),
            ('reference-IR',[tools['clang'],*prior['flags'](mode),'-S','-emit-llvm',reference,'-o',folder/'reference.ll']),
            ('link',[tools['ld.lld'],'--no-relax','-T',linker,obj,'-o',elf]),
            ('object',[tools['llvm-objdump'],'--mattr=+m,+a,+c,+zicsr,+zifencei','-d','-r',obj]),
            ('linked',[tools['llvm-objdump'],'--mattr=+m,+a,+c,+zicsr,+zifencei','-d','-r',elf]),
        ]
        records = []
        for label,argv in recipes:
            argv = [str(x) for x in argv]
            result = subprocess.run(argv,capture_output=True,timeout=120)
            log = folder/(label+'.log')
            log.write_bytes(result.stdout+result.stderr)
            records.append(dict(label=label,argv=argv,exit=result.returncode,log_sha256=sha(log)))
            if result.returncode:
                raise ValueError('See '+str(log))
        record = dict(schema='TSL9-clock-prefix-probe-v1',mode=mode,
                      inputs=inputs,tools={n:str(x) for n,x in tools.items()},
                      commands=records,target_execution=False,full_ABI_proved=False,BIN_generated=False)
        (folder/'compile-receipt.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
        if not all(sha(Path(x)) == pin for x,pin in inputs.items()):
            raise ValueError('Inputs changed while building')
    print(json.dumps(dict(compiled=True,build_root=str(output),equivalence_proved=False,target_execution=False)))


if __name__ == '__main__':
    main()
