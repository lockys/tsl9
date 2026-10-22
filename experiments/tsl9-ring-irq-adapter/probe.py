#!/usr/bin/env python3
"""Finite IRQ candidate compile/partial-link measurement; no target execution."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import runpy
import subprocess

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
READER = ROOT/'experiments/tsl9-spi-transfer-leaf/verify.py'
READER_PIN = '8c8eb8e01b9fc30eb7150682aa8848e47fe4a1254c6f87b05e657244a11b6de8'
FIRMWARE = ROOT/'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
FIRMWARE_PIN = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
TOOLS = {'clang.exe':'047dfde05acc6fcce5af669e25cd8d40b4f509b8842d151d6d8a43a1c6a35fd6',
         'ld.lld.exe':'fe7f55c0c78b3d87f33b905a3874e10e872ca7beef53a8199d7ff9ac6641ec3f',
         'llvm-objdump.exe':'de40d1188fe63ff373e1a5dd83a12e2cb4545ca3b314da16a476ecf072e5a0fa'}


def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def flags(mode):
    common=['--target=riscv32-unknown-elf','-march=rv32imac_zicsr','-mabi=ilp32','-Oz',
            '-mllvm','-enable-machine-outliner=never','-ffreestanding','-fno-builtin',
            '-fno-stack-protector','-fno-unwind-tables','-fno-asynchronous-unwind-tables',
            '-mno-relax','-ffunction-sections','-fdata-sections','-Wall','-Wextra','-Werror']
    common += ['-ffixed-x'+str(i) for i in range(1,32) if i not in {10,11,12,13,14,15}]
    return common+(['-x','c','-std=c11'] if mode=='c' else ['-x','c++','-std=c++17','-fno-exceptions'])


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--version',type=int,required=True);p.add_argument('--out-dir',type=Path,required=True)
    p.add_argument('--llvm-bin',type=Path,default=Path(os.environ.get('USERPROFILE',str(Path.home())))/'AppData/Local/Android/Sdk/ndk/27.1.12297006/toolchains/llvm/prebuilt/windows-x86_64/bin')
    a=p.parse_args();assert 1<=a.version<=99
    source=HERE/'src'/('irq_adapter.v'+str(a.version)+'.c');out=a.out_dir.resolve();llvm=a.llvm_bin.resolve()
    assert out.is_relative_to(HERE/'build') and out!=HERE/'build' and not out.exists(),'fresh owned output only'
    assert digest(READER)==READER_PIN and digest(FIRMWARE)==FIRMWARE_PIN
    for name,pin in TOOLS.items():assert digest(llvm/name)==pin
    m=runpy.run_path(str(READER));E=m['ELF'];portable=m['portable']
    paths=[source,HERE/'component.ld',Path(__file__).resolve(),READER,FIRMWARE]+[llvm/n for n in TOOLS]+[llvm.parent/'lib/clang/18/include/stdint.h']
    before={str(p):digest(p) for p in paths};original=FIRMWARE.read_bytes()[0xac24:0xac58]
    result=dict(schema='TSL9-IRQ-adapter-finite-probe-v1',version=a.version,firmware_ready=False,target_executed=False,ISA_emulated=False,flag_search=False,inputs=before,modes={})
    for lang in ['c','cpp']:
        d=out/lang;d.mkdir(parents=True);f=flags(lang)
        jobs=[('compile',[str(llvm/'clang.exe'),*f,'-MD','-MF',str(d/'native.d'),'-MT',str(d/'native.o'),'-c',str(source),'-o',str(d/'native.o')]),
              ('IR',[str(llvm/'clang.exe'),*f,'-S','-emit-llvm',str(source),'-o',str(d/'native.ll')]),
              ('object',[str(llvm/'llvm-objdump.exe'),'--mattr=+m,+a,+c,+zicsr','-d','-r','-t','-h',str(d/'native.o')]),
              ('partial',[str(llvm/'ld.lld.exe'),'-r','--no-relax','-T',str(HERE/'component.ld'),str(d/'native.o'),'-o',str(d/'partial.o')]),
              ('partial_object',[str(llvm/'llvm-objdump.exe'),'--mattr=+m,+a,+c,+zicsr','-d','-r','-t','-h',str(d/'partial.o')])]
        recipes=[]
        for name,argv in jobs:
            child=subprocess.run(argv,cwd=ROOT,capture_output=True);(d/(name+'.log')).write_bytes(child.stdout+child.stderr)
            recipes.append(dict(label=name,argv=argv,returncode=child.returncode))
            if child.returncode:break
        ok=len(recipes)==5 and recipes[-1]['returncode']==0
        rec=dict(recipes=recipes,all_recipes_succeeded=ok)
        if (d/'native.o').is_file():
            e=E(d/'native.o');funcs=sorted([s for s in e.symbols if s['info']&15==2 and s['size']],key=lambda s:s['section']);code=b'';starts={};regions=[]
            for fn in funcs:
                starts[fn['section']]=len(code);regions.append(dict(name=fn['name'],offset=len(code),size=fn['size']));code+=e.data(e.sections[fn['section']])
            reloc=[dict(offset=starts[x['section']]+x['offset'],type=x['type'],target=e.symbols[x['symbol']]['name'],addend=x['addend']) for x in e.relocations]
            excluded={i for x in reloc for i in range(x['offset'],x['offset']+(2 if x['type']==44 else 4))}
            projection=lambda b:bytes(v for i,v in enumerate(b) if i not in excluded)
            rec.update(native_ELF_sha256=digest(d/'native.o'),bytes=len(code),regions=regions,relocations=reloc,code_hex=code.hex(),noncontrol_bytes=len(projection(code)),noncontrol_original_equal=projection(code)==projection(original))
        if ok:rec.update(partial_ELF_sha256=digest(d/'partial.o'),partial_code_equal_native=E(d/'partial.o').data('.irq')==code)
        (d/'recipes.json').write_bytes((json.dumps(portable(recipes,ROOT,llvm),indent=2)+'\n').encode())
        rec['artifacts']={p.name:digest(p) for p in sorted(d.iterdir()) if p.is_file()};result['modes'][lang]=rec
        print(json.dumps({k:v for k,v in rec.items() if k not in ('recipes','artifacts','code_hex')},sort_keys=True))
    assert before=={str(p):digest(p) for p in paths};result['inputs_unchanged']=True
    receipt=out/'measurement.json';receipt.write_bytes((json.dumps(portable(result,ROOT,llvm),indent=2)+'\n').encode())
    print(json.dumps(dict(measurement_sha256=digest(receipt),firmware_ready=False)))
    return 0 if all(x['all_recipes_succeeded'] for x in result['modes'].values()) else 1


if __name__=='__main__':raise SystemExit(main())
