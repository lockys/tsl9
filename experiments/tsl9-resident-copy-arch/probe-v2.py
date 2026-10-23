#!/usr/bin/env python3
"""Compile/read only: candidate resident bytes are never executed."""
import argparse, hashlib, json, os, re, runpy, subprocess, sys
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
READER=ROOT/'experiments/tsl9-spi-transfer-leaf/verify.py'
READER_SHA='8c8eb8e01b9fc30eb7150682aa8848e47fe4a1254c6f87b05e657244a11b6de8'
CARRIER=ROOT/'analysis/resident-copy-reference-2026-10-21/reference-carrier/REFERENCE-CANDIDATE-ONLY-00040000-0006EA66.bin'
CARRIER_SHA='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22'
BODY_SHA='558a82658cb54901945d4c2884f2e87e763f64d57c0cafa831307beb44ae0c36'
TOOLS={'clang.exe':'047dfde05acc6fcce5af669e25cd8d40b4f509b8842d151d6d8a43a1c6a35fd6',
'ld.lld.exe':'fe7f55c0c78b3d87f33b905a3874e10e872ca7beef53a8199d7ff9ac6641ec3f',
'llvm-objdump.exe':'de40d1188fe63ff373e1a5dd83a12e2cb4545ca3b314da16a476ecf072e5a0fa'}

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def flags(mode):
    common=['--target=riscv32-unknown-elf','-march=rv32imac_zicsr_zifencei','-mabi=ilp32','-Oz',
        '-mllvm','-enable-machine-outliner=never','-ffreestanding','-fno-builtin','-fno-stack-protector',
        '-fno-unwind-tables','-fno-asynchronous-unwind-tables','-mno-relax','-ffunction-sections',
        '-fdata-sections','-Wall','-Wextra','-Werror','-x','c' if mode=='c' else 'c++',
        '-std=c11' if mode=='c' else '-std=c++17']
    if mode=='cpp':common+=['-fno-exceptions']
    return common+['-ffixed-x'+str(i) for i in range(1,32) if i not in {10,11,12,13,14,15,16}]

def recipes(folder,llvm,mode):
    source=HERE/'src/copy.v1.c'
    return [('compile',[str(llvm/'clang.exe')]+flags(mode)+['-MD','-MF',str(folder/'native.d'),'-MT','native.o','-c',str(source),'-o',str(folder/'native.o')]),
            ('IR',[str(llvm/'clang.exe')]+flags(mode)+['-S','-emit-llvm',str(source),'-o',str(folder/'native.ll')]),
            ('object',[str(llvm/'llvm-objdump.exe'),'-d','-r','-h','-t',str(folder/'native.o')]),
            ('link',[str(llvm/'ld.lld.exe'),'--no-relax','-T',str(HERE/'component.ld'),str(folder/'native.o'),'-o',str(folder/'CANDIDATE-COMPONENT-ONLY.elf')]),
            ('linked',[str(llvm/'llvm-objdump.exe'),'-d','-h','-t',str(folder/'CANDIDATE-COMPONENT-ONLY.elf')])]

def consumed(label,folder,llvm):
    paths=[llvm/('clang.exe' if label in ('compile','IR') else 'ld.lld.exe' if label=='link' else 'llvm-objdump.exe')]
    if label in ('compile','IR'):paths += [HERE/'src/copy.v1.c',llvm.parent/'lib/clang/18/include/stdint.h']
    elif label in ('object','link'):paths += [folder/'native.o']
    else:paths += [folder/'CANDIDATE-COMPONENT-ONLY.elf']
    if label=='link':paths += [HERE/'component.ld']
    return [dict(path=str(p),bytes=p.stat().st_size,sha256=sha(p)) for p in paths]

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--out-dir',required=True,type=Path)
    ap.add_argument('--llvm-bin',type=Path,default=Path(os.environ.get('USERPROFILE',str(Path.home())))/'AppData/Local/Android/Sdk/ndk/27.1.12297006/toolchains/llvm/prebuilt/windows-x86_64/bin')
    a=ap.parse_args();out=a.out_dir.resolve();llvm=a.llvm_bin.resolve()
    assert out.is_relative_to(HERE/'build') and not out.exists() and out!=HERE/'build'
    assert sha(READER)==READER_SHA and sha(CARRIER)==CARRIER_SHA
    for n,h in TOOLS.items():assert sha(llvm/n)==h
    E=runpy.run_path(str(READER))['ELF'];portable=runpy.run_path(str(READER))['portable']
    body=CARRIER.read_bytes()[0x5a2:0x5dc];assert hashlib.sha256(body).hexdigest()==BODY_SHA
    source=HERE/'src/copy.v1.c'
    inputs=[source,HERE/'component.ld',Path(__file__),READER,CARRIER]+[llvm/n for n in TOOLS]+[llvm.parent/'lib/clang/18/include/stdint.h']
    before={str(p):sha(p) for p in inputs}
    record=dict(schema='TSL9-SDK-candidate-copy-arch-probe-v1',inputs=before,modes={},
        installed_identity_proved=False,target_executed=False,ISA_emulated=False,firmware_ready=False)
    for mode in ('c','cpp'):
        folder=out/mode;folder.mkdir(parents=True)
        cmds=recipes(folder,llvm,mode)
        records=[]
        for label,argv in cmds:
            before_command=consumed(label,folder,llvm)
            child=subprocess.run(argv,cwd=ROOT,capture_output=True)
            (folder/(label+'.log')).write_bytes(child.stdout+child.stderr)
            records.append(dict(label=label,argv=argv,exit=child.returncode,consumed=before_command,log_sha256=sha(folder/(label+'.log'))))
            if child.returncode:break
        result=dict(recipes=records,all_recipes_succeeded=len(records)==5 and not records[-1]['exit'])
        if (folder/'native.o').exists():
            e=E(folder/'native.o');fs=sorted([s for s in e.symbols if s['info']&15==2 and s['size']],key=lambda s:s['section'])
            result['functions']=[[s['name'],s['size']] for s in fs]
            result['relocations']=[[r['offset'],r['type'],e.symbols[r['symbol']]['name'],r['addend']] for r in e.relocations]
        if result['all_recipes_succeeded']:
            e=E(folder/'CANDIDATE-COMPONENT-ONLY.elf');code=e.data('.copy')
            result.update(code_bytes=len(code),code_sha256=hashlib.sha256(code).hexdigest(),whole_code_equal_candidate=code==body,
                ELF_sha256=sha(folder/'CANDIDATE-COMPONENT-ONLY.elf'))
        result['artifacts']=[dict(path=str(p),bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(folder.iterdir()) if p.is_file()]
        record['modes'][mode]=result
        print(json.dumps({k:v for k,v in result.items() if k not in ('recipes','artifacts')},ensure_ascii=True))
    assert before=={str(p):sha(p) for p in inputs}
    (out/'measurement.json').write_text(json.dumps(portable(record,ROOT,llvm),indent=2)+'\n',encoding='utf8')
    return 0 if all(v['all_recipes_succeeded'] for v in record['modes'].values()) else 1
if __name__=='__main__':raise SystemExit(main())
