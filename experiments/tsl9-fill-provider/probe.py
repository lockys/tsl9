#!/usr/bin/env python3
"""Finite offline fill-provider measurement; retain genuine unresolved providers."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import runpy
import subprocess

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT/'experiments/tsl9-fill-provider'
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
    common += ['-ffixed-x'+str(i) for i in range(1,32) if i not in {5,6,10,11,12,13,14,15}]
    return common+(['-x','c','-std=c11'] if mode=='c' else ['-x','c++','-std=c++17','-fno-exceptions'])


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--version',required=True,type=int)
    parser.add_argument('--out-dir',required=True,type=Path)
    parser.add_argument('--llvm-bin',type=Path,default=Path(os.environ.get('USERPROFILE',str(Path.home())))/'AppData/Local/Android/Sdk/ndk/27.1.12297006/toolchains/llvm/prebuilt/windows-x86_64/bin')
    args=parser.parse_args();assert 1<=args.version<=99
    source=BASE/'src'/('fill.v'+str(args.version)+'.c');out=args.out_dir.resolve();llvm=args.llvm_bin.resolve();linker=BASE/'component.ld'
    assert out.is_relative_to(BASE/'build') and out!=BASE/'build' and not out.exists(), 'fresh owned output directory required'
    assert digest(READER)==READER_PIN and digest(FIRMWARE)==FIRMWARE_PIN
    for name,pin in TOOLS.items():assert digest(llvm/name)==pin
    helper=runpy.run_path(str(READER),run_name='fill_provider_probe_reader');E=helper['ELF'];portable=helper['portable']
    paths=[source,linker,Path(__file__).resolve(),READER,FIRMWARE]+[llvm/n for n in TOOLS]+[llvm.parent/'lib/clang/18/include/stdint.h']
    before={str(p):digest(p) for p in paths};original=FIRMWARE.read_bytes()[0x520:0x5c8]
    assert hashlib.sha256(original).hexdigest()=='50232f532bf996f5d738050c60480fab6069d6ef4cb842cfc582170e351630c6'
    record=dict(schema='TSL9-fill-provider-native-finite-probe-v1',candidate_version=args.version,firmware_ready=False,target_executed=False,ISA_emulated=False,flags_search=False,
                original_start='0x8520',original_bytes=len(original),ordinary_C_ABI_proved=False,
                inputs=[dict(path=str(p),sha256=before[str(p)]) for p in paths],modes={})
    for mode in ['c','cpp']:
        folder=out/mode;folder.mkdir(parents=True);common=flags(mode)
        commands=[('compile',[str(llvm/'clang.exe')]+common+['-MD','-MF',str(folder/'native.d'),'-MT',str(folder/'native.o'),'-c',str(source),'-o',str(folder/'native.o')]),
                  ('IR',[str(llvm/'clang.exe')]+common+['-S','-emit-llvm',str(source),'-o',str(folder/'native.ll')]),
                  ('object',[str(llvm/'llvm-objdump.exe'),'--mattr=+m,+a,+c,+zicsr','-d','-r','-t','-h',str(folder/'native.o')]),
                  ('link',[str(llvm/'ld.lld.exe'),'-r','--no-relax','-T',str(linker),str(folder/'native.o'),'-o',str(folder/'partial.o')]),
                  ('partial',[str(llvm/'llvm-objdump.exe'),'--mattr=+m,+a,+c,+zicsr','-d','-r','-t','-h',str(folder/'partial.o')])]
        recipes=[]
        for label,argv in commands:
            child=subprocess.run(argv,cwd=ROOT,capture_output=True);(folder/(label+'.log')).write_bytes(child.stdout+child.stderr)
            recipes.append(dict(label=label,argv=argv,returncode=child.returncode))
            if child.returncode:break
        result=dict(recipes=recipes,all_recipes_succeeded=len(recipes)==5 and not recipes[-1]['returncode'])
        if (folder/'native.o').is_file():
            e=E(folder/'native.o');fs=sorted([s for s in e.symbols if s['info']&15==2 and s['size']],key=lambda s:s['section']);code=b'';regions=[];starts={}
            for function in fs:
                starts[function['section']]=len(code);regions.append(dict(name=function['name'],offset=len(code),size=function['size']));code+=e.data(e.sections[function['section']])[function['value']:function['value']+function['size']]
            lines=[x for x in (folder/'object.log').read_text().splitlines() if re.match(r'^\s*[0-9a-f]+:\s+(?:[0-9a-f]{2} )+',x)] if (folder/'object.log').is_file() else []
            rels=[dict(offset=starts[x['section']]+x['offset'],type=x['type'],target=e.symbols[x['symbol']]['name'],addend=x['addend']) for x in e.relocations]
            result.update(ELF_sha256=digest(folder/'native.o'),code_bytes=len(code),instructions=len(lines),functions=regions,relocations=rels,code_hex=code.hex())
            # Measurement only: mask genuine pending control immediates,
            # preserving RD and the C.JAL/C.J distinction. Formal proof must
            # independently validate targets, typed fields and full closure.
            masks=bytearray(b'\xff'*len(original))
            for item in rels:
                kinds={16:(4,0x01fff07f),17:(4,0x00000fff),44:(2,0xe383),45:(2,0xe003)}
                if item['type'] in kinds:
                    n,mask=kinds[item['type']];off=item['offset']
                    if off+n<=len(masks):masks[off:off+n]=mask.to_bytes(n,'little')
            differences=[i for i,(a,b,m) in enumerate(zip(code,original,masks)) if (a^b)&m]
            result.update(nonrelocation_bit_differences=differences,all_nonrelocation_bits_equal=len(code)==len(original) and not differences,
                          undefined_symbols=[s['name'] for s in e.symbols if s['section']==0 and s['name']])
        if (folder/'partial.o').is_file() and result['all_recipes_succeeded']:
            linked=E(folder/'partial.o');code=linked.data('.fill_provider')
            result.update(partial_ELF_sha256=digest(folder/'partial.o'),partial_code_bytes=len(code),partial_code_sha256=hashlib.sha256(code).hexdigest(),partial_whole_code_equal_original=code==original,
                          retained_relocations=len(linked.relocations))
        (folder/'recipes.json').write_bytes((json.dumps(portable(recipes,ROOT,llvm),indent=2)+'\n').encode())
        result['artifacts']=[dict(path=str(p),size=p.stat().st_size,sha256=digest(p)) for p in sorted(folder.iterdir()) if p.is_file()]
        record['modes'][mode]=result
        print(json.dumps(portable(dict(language=mode,**{k:v for k,v in result.items() if k not in ('recipes','artifacts','code_hex','relocations')}),ROOT,llvm)))
    record['inputs_unchanged']=before=={str(p):digest(p) for p in paths};assert record['inputs_unchanged']
    measurement=out/'measurement.json';measurement.write_bytes((json.dumps(portable(record,ROOT,llvm),indent=2)+'\n').encode())
    print(json.dumps(dict(measurement_sha256=digest(measurement),firmware_ready=False)))
    return 0 if all(v['all_recipes_succeeded'] for v in record['modes'].values()) else 1


if __name__=='__main__':
    raise SystemExit(main())
