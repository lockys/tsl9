#!/usr/bin/env python3
"""First measured source-wiring experiment; compile/link/static only."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import runpy
import struct
import subprocess
import sys
import uuid
sys.dont_write_bytecode=True
MODEL='experiments/tsl9-v4160-ota-source-wiring'
TOOLS={'clang':'047dfde05acc6fcce5af669e25cd8d40b4f509b8842d151d6d8a43a1c6a35fd6','ld.lld':'fe7f55c0c78b3d87f33b905a3874e10e872ca7beef53a8199d7ff9ac6641ec3f','llvm-objcopy':'e5590a8f45e93f322f0829b91dbddb74e8c1eb91436d13161abc773aebf64469','llvm-objdump':'de40d1188fe63ff373e1a5dd83a12e2cb4545ca3b314da16a476ecf072e5a0fa'}
ENTRY='__tsl9v4160_ota_code_9c4a'
NATIVE='tsl9_ota_handler_native_9c4a'
ROM='__tsl9v4160_rom_entry'
def H(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def need(v,m):
    if not v:raise ValueError(m)
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--project-root',required=True,type=Path);p.add_argument('--tool-dir',required=True,type=Path);p.add_argument('--base-object',required=True,type=Path);p.add_argument('--base-receipt',required=True,type=Path);p.add_argument('--base-witness',required=True,type=Path);p.add_argument('--base-image',required=True,type=Path);p.add_argument('--build-root',type=Path);a=p.parse_args();root=a.project_root.resolve();model=root/MODEL
    base,receipt,witness,image=[x.resolve() for x in(a.base_object,a.base_receipt,a.base_witness,a.base_image)]
    old=json.loads(receipt.read_bytes());mode=old['mode'];need(mode in('c','cpp') and old['passed'],'Retained input generation')
    need(old['artifacts'][base.relative_to(receipt.parent).as_posix()]==dict(bytes=base.stat().st_size,sha256=H(base)),'Actual retained base artifact identity')
    need(H(image)=='28697eab551bd9b3ca74a69c44db24fc02e07bedbb5bf02380e4bcb1a390ce89','Exact inherited complete-image validation input')
    tools={n:next(x for x in(a.tool_dir/(n+'.exe'),a.tool_dir/n) if x.is_file()).resolve() for n in TOOLS};need(all(H(x)==TOOLS[n] for n,x in tools.items()),'Pinned local LLVM tools')
    parser=next(x for x in(root/'analysis/v4160-irq-native-2026-10-21/compiler-review/elf32.py',root/'apk-analysis/tsl9-v4160-irq-native-2026-10-21/compiler-review/elf32.py') if x.is_file());need(H(parser)=='00a231e3bbd881a9961c12fefd15565364cd813250a46a7b20851a6b9f3a2141','Pinned parser');E=runpy.run_path(str(parser))['ELF']
    oldrunner=next(x for x in(root/'analysis/v4160-ota-handler-compact-2026-10-22/implementation/verify_native.py',root/'apk-analysis/tsl9-v4160-ota-handler-compact-2026-10-22/implementation/verify_native.py') if x.is_file());need(H(oldrunner)=='fc3005e95419c73ab82a4554d3f0af5b3174b1a95736d52d656cefc5678289ab','Unchanged compact flags');flags=runpy.run_path(str(oldrunner))['flags'](mode)
    layout=root/'experiments/tsl9-v4160-tx-image-integration/original-image-layout.ld';extension=model/'extension.ld'
    folder=a.build_root.resolve() if a.build_root else model/'build'/('prototype-'+uuid.uuid4().hex);need(folder.is_relative_to(model/'build') and not folder.exists(),'Create-only owned output');folder.mkdir(parents=True);commands=[]
    inputs=[base,receipt,witness,image,layout,extension,model/'src/native_alias.c',model/'src/page_tail.S',oldrunner,parser,Path(__file__).resolve(),Path(sys.executable).resolve(),*tools.values(),*(root/'experiments/tsl9-v4160-ota-handler-compact/src').glob('*')];pins={str(x):H(x) for x in inputs}
    def run(label,argv,negative=False):
        done=subprocess.run([str(x) for x in argv],cwd=folder,env=dict(os.environ,TMP=str(folder),TEMP=str(folder)),capture_output=True,timeout=120);log=folder/(label+'.log');log.write_bytes(done.stdout+done.stderr);commands.append(dict(label=label,argv=[str(x) for x in argv],exit=done.returncode,log=log.name,sha256=H(log)));need(done.returncode!=0 if negative else done.returncode==0,'Actual command outcome '+str(log));return done
    resource=Path(run('compiler-resource-dir',[tools['clang'],'-print-resource-dir']).stdout.decode().strip())/'include/stdint.h';pins[str(resource)]=H(resource)
    run('alias-object',[tools['clang'],*flags,'-c','-MD','-MF',folder/'native_alias.d','-MT','native_alias.o',model/'src/native_alias.c','-o',folder/'native_alias.o'])
    run('alias-IR',[tools['clang'],*flags,'-S','-emit-llvm',model/'src/native_alias.c','-o',folder/'native_alias.ll'])
    run('alias-disassembly',[tools['llvm-objdump'],'--mattr=+m,+a,+c,+zicsr','-d','-r',folder/'native_alias.o'])
    n=E(folder/'native_alias.o');functions=[s for s in n.symbols if s['name'] in(ENTRY,NATIVE)];need(len(functions)==2 and all(s['size']==568 and s['info']==18 and s['value']==0 for s in functions) and functions[0]['index']==functions[1]['index'],'Real same-TU strong FUNC568 alias');need(hashlib.sha256(n.function_bytes(functions[0])).hexdigest()=='b486c6eed0d3465c8947fd338e790f1441f29c64827a47b20e1fada18ff863af','Unchanged full-eight-register compiled body')
    run('page-tail-object',[tools['clang'],'--target=riscv32-unknown-elf','-march=rv32imac_zicsr','-mabi=ilp32','-mno-relax','-x','assembler','-c',model/'src/page_tail.S','-o',folder/'page_tail.o'])
    run('weaken-old-entry',[tools['llvm-objcopy'],'--weaken-symbol='+ENTRY,base,folder/'base-weakened.o'])
    run('partial-source-wiring',[tools['ld.lld'],'--no-relax','-r',folder/'base-weakened.o',folder/'native_alias.o',folder/'page_tail.o','-o',folder/'source-integrated.o'])
    partial=E(folder/'source-integrated.o');need({s['name'] for s in partial.symbols if s['index']==0 and s['name']}=={ROM},'Partial retains sole real ROM UND')
    common=[tools['ld.lld'],'--no-relax','--error-limit=0','-T',layout,'-T',extension]
    strict=folder/'STRICT-MISSING-ROM.elf';run('strict-missing-ROM',[*common,folder/'source-integrated.o','-o',strict],True);need(not strict.exists() and ROM in(folder/'strict-missing-ROM.log').read_text(),'Strict failure without ROM provider')
    numeric=folder/'NUMERIC-ROM-WITNESS-ONLY.ld';numeric.write_bytes((ROM+' = 0x40000;\n').encode())
    run('numeric-address-witness',[*common,'-T',numeric,folder/'source-integrated.o','-o',folder/'ADDRESS-WITNESS-ONLY.elf'])
    run('binary-address-witness',[tools['llvm-objcopy'],'-O','binary',folder/'ADDRESS-WITNESS-ONLY.elf',folder/'NOT-FLASH-VALIDATED-ota-source-wired.bin'])
    run('selected-native-disassembly',[tools['llvm-objdump'],'--mattr=+m,+a,+c,+zicsr','-d','--section=.text.tsl9_ota_handler_native_9c4a','--section=.text.tsl9v4160.gatt_ingress_13f7e',folder/'ADDRESS-WITNESS-ONLY.elf'])
    final=E(folder/'ADDRESS-WITNESS-ONLY.elf');alias=next(s for s in final.symbols if s['name']==ENTRY);need((alias['value'],alias['size'],alias['info'])==(0x1ac00,568,18),'Strong real C alias wins')
    blob=(folder/'NOT-FLASH-VALIDATED-ota-source-wired.bin').read_bytes();oldblob=image.read_bytes();diff=[dict(offset=i,VA=0x8000+i,before=x,after=y) for i,(x,y) in enumerate(zip(oldblob,blob)) if x!=y]
    need(len(blob)==77824 and all(0x14094<=x['VA']<0x14098 for x in diff),'Only original caller changes in inherited bytes; measured complete extent')
    word=int.from_bytes(blob[0x14094-0x8000:0x14098-0x8000],'little');imm=((word>>31)&1)<<20|((word>>12)&255)<<12|((word>>20)&1)<<11|((word>>21)&1023)<<1;imm=imm-(1<<21) if imm&(1<<20) else imm
    need(word&127==0x6f and (word>>7)&31==1 and 0x14094+imm==0x1ac00,'Actual original caller JAL -> new C with RA14098')
    need(all(H(Path(name))==pin for name,pin in pins.items()),'Stable actual inputs/source/tools')
    record=dict(schema='TSL9-first-real-source-wiring-prototype-v1',passed=True,mode=mode,paths=dict(base_object=str(base),base_receipt=str(receipt),base_witness=str(witness),base_image=str(image)),source_pins=pins,commands=commands,alias_functions=functions,partial_remaining_undefined=[ROM],final_alias=alias,image_bytes=len(blob),image_sha256=hashlib.sha256(blob).hexdigest(),inherited_differences=diff,caller=dict(PC=0x14094,target=0x1ac00,RA=0x14098,raw=word.to_bytes(4,'little').hex()),ROM_provider=False,numeric_address_witness_only=True,installed_ROM_proved=False,Flash_NV_free_proved=False,original_ABI_admitted=False,hardware_OTA_proved=False,target_execution=False,artifacts={x.relative_to(folder).as_posix():dict(bytes=x.stat().st_size,sha256=H(x)) for x in folder.rglob('*') if x.is_file()})
    out=folder/'prototype.json';out.write_bytes((json.dumps(record,indent=2)+'\n').encode());print(json.dumps(dict(passed=True,receipt=str(out),sha256=H(out),mode=mode,image_bytes=len(blob),image_sha256=record['image_sha256'],inherited_diff_bytes=len(diff),caller=record['caller'],ROM_provider=False,hardware_OTA_proved=False)))
if __name__=='__main__':main()
