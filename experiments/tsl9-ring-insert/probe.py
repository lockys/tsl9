#!/usr/bin/env python3
"""Finite native compiler measurement for versioned ring candidates; no target execution."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import runpy
import subprocess

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT/'experiments/tsl9-ring-insert'
READER = ROOT/'experiments/tsl9-spi-transfer-leaf/verify.py'
READER_PIN = '8c8eb8e01b9fc30eb7150682aa8848e47fe4a1254c6f87b05e657244a11b6de8'
FIRMWARE = ROOT/'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
FIRMWARE_PIN = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
TOOLS = {'clang.exe':'047dfde05acc6fcce5af669e25cd8d40b4f509b8842d151d6d8a43a1c6a35fd6',
         'ld.lld.exe':'fe7f55c0c78b3d87f33b905a3874e10e872ca7beef53a8199d7ff9ac6641ec3f',
         'llvm-objdump.exe':'de40d1188fe63ff373e1a5dd83a12e2cb4545ca3b314da16a476ecf072e5a0fa'}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def flags(mode):
    common=['--target=riscv32-unknown-elf','-march=rv32imac_zicsr','-mabi=ilp32','-Oz','-mllvm','-enable-machine-outliner=never','-ffreestanding','-fno-builtin','-fno-stack-protector','-fno-unwind-tables','-fno-asynchronous-unwind-tables','-mno-relax','-ffunction-sections','-fdata-sections','-Wall','-Wextra','-Werror']
    common += ['-ffixed-x'+str(i) for i in range(1,32) if i not in {6,10,11,12,13,14,15,16,17,28}]
    return common+(['-x','c','-std=c11'] if mode=='c' else ['-x','c++','-std=c++17','-fno-exceptions'])


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--version',required=True,type=int)
    parser.add_argument('--out-dir',required=True,type=Path)
    parser.add_argument('--llvm-bin',type=Path,default=Path(os.environ.get('USERPROFILE',str(Path.home())))/'AppData/Local/Android/Sdk/ndk/27.1.12297006/toolchains/llvm/prebuilt/windows-x86_64/bin')
    args=parser.parse_args();assert 1<=args.version<=99
    source=BASE/'src'/('ring_insert.v'+str(args.version)+'.c');out=args.out_dir.resolve();llvm=args.llvm_bin.resolve();linker=BASE/'component.ld'
    assert out.is_relative_to(BASE/'build') and out!=BASE/'build' and not out.exists(), 'fresh owned output directory required'
    assert digest(READER)==READER_PIN and digest(FIRMWARE)==FIRMWARE_PIN
    for name,pin in TOOLS.items():assert digest(llvm/name)==pin
    helper=runpy.run_path(str(READER),run_name='ring_probe_reader');E=helper['ELF'];portable=helper['portable']
    paths=[source,linker,Path(__file__).resolve(),READER,FIRMWARE]+[llvm/n for n in TOOLS]+[llvm.parent/'lib/clang/18/include/stdint.h']
    before={str(p):digest(p) for p in paths};original=FIRMWARE.read_bytes()[0xabc8:0xac24]
    record=dict(schema='TSL9-ring-native-finite-probe-v1',candidate_version=args.version,firmware_ready=False,target_executed=False,ISA_emulated=False,flags_search=False,
                inputs=[dict(path=str(p),sha256=before[str(p)]) for p in paths],modes={})
    for mode in ['c','cpp']:
        folder=out/mode;folder.mkdir(parents=True);common=flags(mode)
        commands=[('compile',[str(llvm/'clang.exe')]+common+['-MD','-MF',str(folder/'native.d'),'-MT',str(folder/'native.o'),'-c',str(source),'-o',str(folder/'native.o')]),
                  ('IR',[str(llvm/'clang.exe')]+common+['-S','-emit-llvm',str(source),'-o',str(folder/'native.ll')]),
                  ('object',[str(llvm/'llvm-objdump.exe'),'--mattr=+m,+a,+c,+zicsr','-d','-r','-t','-h',str(folder/'native.o')]),
                  ('link',[str(llvm/'ld.lld.exe'),'--no-relax','-T',str(linker),str(folder/'native.o'),'-o',str(folder/'linked.elf')]),
                  ('linked',[str(llvm/'llvm-objdump.exe'),'--mattr=+m,+a,+c,+zicsr','-d','-r','-t','-h',str(folder/'linked.elf')])]
        recipes=[]
        for label,argv in commands:
            p=subprocess.run(argv,cwd=ROOT,capture_output=True);(folder/(label+'.log')).write_bytes(p.stdout+p.stderr)
            recipes.append(dict(label=label,argv=argv,returncode=p.returncode))
            if p.returncode:break
        result=dict(recipes=recipes,all_recipes_succeeded=len(recipes)==5 and not recipes[-1]['returncode'])
        if (folder/'native.o').is_file():
            e=E(folder/'native.o');fs=sorted([s for s in e.symbols if s['info']&15==2 and s['size']],key=lambda s:s['section']);code=b'';regions=[];starts={}
            for f in fs:
                starts[f['section']]=len(code);regions.append(dict(name=f['name'],offset=len(code),size=f['size']));code+=e.data(e.sections[f['section']])[f['value']:f['value']+f['size']]
            lines=[x for x in (folder/'object.log').read_text().splitlines() if re.match(r'^\s*[0-9a-f]+:\s+(?:[0-9a-f]{2} )+',x)] if (folder/'object.log').is_file() else []
            rels=[dict(offset=starts[x['section']]+x['offset'],type=x['type'],target=e.symbols[x['symbol']]['name'],addend=x['addend']) for x in e.relocations]
            result.update(ELF_sha256=digest(folder/'native.o'),code_bytes=len(code),instructions=len(lines),functions=regions,relocations=rels,code_hex=code.hex(),first_raw_difference=next((i for i,(a,b) in enumerate(zip(code,original)) if a!=b),None))
        if (folder/'linked.elf').is_file() and result['all_recipes_succeeded']:
            linked=E(folder/'linked.elf');code=linked.data('.ring')
            result.update(linked_ELF_sha256=digest(folder/'linked.elf'),linked_code_bytes=len(code),linked_code_sha256=hashlib.sha256(code).hexdigest(),whole_code_equal_original=code==original)
        (folder/'recipes.json').write_bytes((json.dumps(portable(recipes,ROOT,llvm),indent=2)+'\n').encode())
        result['artifacts']=[dict(path=str(p),size=p.stat().st_size,sha256=digest(p)) for p in sorted(folder.iterdir()) if p.is_file()]
        record['modes'][mode]=result
        print(json.dumps(portable(dict(language=mode,**{k:v for k,v in result.items() if k not in ('recipes','artifacts','code_hex')}),ROOT,llvm)))
    record['inputs_unchanged']=before=={str(p):digest(p) for p in paths};assert record['inputs_unchanged']
    measurement=out/'measurement.json';measurement.write_bytes((json.dumps(portable(record,ROOT,llvm),indent=2)+'\n').encode())
    print(json.dumps(dict(measurement_sha256=digest(measurement),firmware_ready=False)))
    return 0 if all(v['all_recipes_succeeded'] for v in record['modes'].values()) else 1


if __name__=='__main__':
    raise SystemExit(main())
