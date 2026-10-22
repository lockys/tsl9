"""Read-only fresh-source/recipe/dependency/IR closure for the new actual alias TU."""
from collections import Counter
import json
from pathlib import Path
import re
import runpy
import machine as M

MODEL='experiments/tsl9-v4160-ota-source-wiring'
CORE={'ota_handler.c':'3c3df0dcbdc91ab798a67857e789b090342b6727651d095fd300f32ff04c423b',
      'io.h':'0d54c0e7900b24b4a2d4e5e6153f30b2ffbcffdfbd5b195ca837d16eb319d5c1',
      'ota_handler.h':'fa6165d20e935b5c69dbab733c2340de13093a8827840bbffbce491bf9dd61de'}
TOOLS={'clang.exe':'047dfde05acc6fcce5af669e25cd8d40b4f509b8842d151d6d8a43a1c6a35fd6',
       'ld.lld.exe':'fe7f55c0c78b3d87f33b905a3874e10e872ca7beef53a8199d7ff9ac6641ec3f',
       'llvm-objcopy.exe':'e5590a8f45e93f322f0829b91dbddb74e8c1eb91436d13161abc773aebf64469',
       'llvm-objdump.exe':'de40d1188fe63ff373e1a5dd83a12e2cb4545ca3b314da16a476ecf072e5a0fa'}
def inspect(root,folder,record,native):
    need=M.need;sha=M.sha;mode=record['mode'];need(mode in M.BASE,'Actual C11/CPP17 language')
    src=root/MODEL/'src/native_alias.c';tail=root/MODEL/'src/page_tail.S';extension=root/MODEL/'extension.ld'
    core=root/'experiments/tsl9-v4160-ota-handler-compact/src'
    for n,pin in CORE.items():need(sha(core/n)==pin,'Immutable shared algorithm/bridge '+n)
    text=src.read_text();need(text.count('#include "../../tsl9-v4160-ota-handler-compact/src/ota_handler.c"')==1 and
        text.count('__attribute__((alias("'+M.NEW+'")))')==1,'Actual same-TU include and real source alias declaration')
    need(sha(src)=='4a030fde1d21b76470ab203d0ceb128c197cc4a6dadd8ef906b1b75ac9ec8cb0' and
         sha(tail)=='f2b73f1f541aba166f072e26c06ada37972c88fc90007b520d8b2febd88f8a95' and
         sha(extension)=='6a88b4829913331d80e13d0ccbf473023bb30f5ae6214bc26013f51c2e98f958',
         'Bounded alias/page-data/layout source identity')
    commands=record['commands'];labels=['compiler-resource-dir','alias-object','alias-IR','alias-disassembly','page-tail-object',
        'weaken-old-entry','partial-source-wiring','strict-missing-ROM','numeric-address-witness','binary-address-witness','selected-native-disassembly']
    need([x['label'] for x in commands]==labels,'Exact11 compile/IR/objcopy/link/extraction recipes in order')
    tools={Path(c['argv'][0]).name:c['argv'][0] for c in commands}
    need(set(tools)==set(TOOLS) and all(sha(Path(p))==TOOLS[n] for n,p in tools.items()),'Actual compiler/objcopy/linker/disassembler tool identities')
    cc,ld,oc,od=(tools[n] for n in ('clang.exe','ld.lld.exe','llvm-objcopy.exe','llvm-objdump.exe'))
    flags=['--target=riscv32-unknown-elf','-march=rv32imac_zicsr','-mabi=ilp32','-Oz','-mllvm','-enable-machine-outliner=never',
           '-ffreestanding','-fno-builtin','-fno-stack-protector','-fno-unwind-tables','-fno-asynchronous-unwind-tables','-mno-relax',
           '-ffunction-sections','-fdata-sections','-Wall','-Wextra','-Werror','-x','c' if mode=='c' else 'c++','-std=c11' if mode=='c' else '-std=c++17']
    if mode=='cpp':flags+=['-fno-exceptions']
    f=lambda n:str(folder/n);base=record['paths']['base_object'];oldlayout=str(root/'experiments/tsl9-v4160-tx-image-integration/original-image-layout.ld')
    link=[ld,'--no-relax','--error-limit=0','-T',oldlayout,'-T',str(extension)]
    expected=[[cc,'-print-resource-dir'],[cc,*flags,'-c','-MD','-MF',f('native_alias.d'),'-MT','native_alias.o',str(src),'-o',f('native_alias.o')],
        [cc,*flags,'-S','-emit-llvm',str(src),'-o',f('native_alias.ll')],[od,'--mattr=+m,+a,+c,+zicsr','-d','-r',f('native_alias.o')],
        [cc,'--target=riscv32-unknown-elf','-march=rv32imac_zicsr','-mabi=ilp32','-mno-relax','-x','assembler','-c',str(tail),'-o',f('page_tail.o')],
        [oc,'--weaken-symbol='+M.OLD,base,f('base-weakened.o')],
        [ld,'--no-relax','-r',f('base-weakened.o'),f('native_alias.o'),f('page_tail.o'),'-o',f('source-integrated.o')],
        [*link,f('source-integrated.o'),'-o',f('STRICT-MISSING-ROM.elf')],
        [*link,'-T',f('NUMERIC-ROM-WITNESS-ONLY.ld'),f('source-integrated.o'),'-o',f('ADDRESS-WITNESS-ONLY.elf')],
        [oc,'-O','binary',f('ADDRESS-WITNESS-ONLY.elf'),f('NOT-FLASH-VALIDATED-ota-source-wired.bin')],
        [od,'--mattr=+m,+a,+c,+zicsr','-d','--section=.text.tsl9_ota_handler_native_9c4a','--section=.text.tsl9v4160.gatt_ingress_13f7e',f('ADDRESS-WITNESS-ONLY.elf')]]
    for c,want in zip(commands,expected):
        need(c['argv']==want and (c['exit']!=0 if c['label']=='strict-missing-ROM' else c['exit']==0),'Actual bounded recipe '+c['label'])
        need(sha(folder/c['log'])==c['sha256'],'Actual recipe log '+c['label'])
    need(not (folder/'STRICT-MISSING-ROM.elf').exists() and M.ROM in (folder/'strict-missing-ROM.log').read_text(),'Strict missing-realROM link fails; no output')
    need((folder/'NUMERIC-ROM-WITNESS-ONLY.ld').read_text()=='__tsl9v4160_rom_entry = 0x40000;\n','Numeric address witness declared explicitly')
    for p,pin in record['source_pins'].items():need(sha(Path(p))==pin,'Observed source/tool/input/resource identity '+p)
    required={src,tail,extension,*[core/n for n in CORE],Path(oldlayout)}
    need(all(str(p) in record['source_pins'] and record['source_pins'][str(p)]==sha(p) for p in required),'Actual new/shared generation inputs pinned')
    need(sha(Path(oldlayout))=='651a8f14d09e373cb5523ec12f97d1fcce3ff26a51b3d835ae55d0239945507b','Unchanged historical691-owner address script')
    for name,item in record['artifacts'].items():
        p=(folder/name).resolve();need(p.is_relative_to(folder) and p.is_file() and item==dict(bytes=p.stat().st_size,sha256=sha(p)),'Actual generation artifact '+name)
    dep=(folder/'native_alias.d').read_text().replace('\\\n','');target,sep,rest=dep.partition(': ')
    need(sep and target=='native_alias.o','Actual MD target')
    paths={Path(t.replace('\\ ',' ')).resolve() for t in re.findall(r'(?:\\.|[^\s])+',rest)}
    resource=Path((folder/'compiler-resource-dir.log').read_text().strip())/'include/stdint.h'
    need(paths=={src,*[core/n for n in CORE],resource},'MD exact4project+actual compiler stdint resource')
    need(sha(resource)=='7ce5540d5fb6e8da9760928e76cbdd5ebef329d701ad598d30d8e6f9d5d78b34','Actual observed stdint header identity')
    ir=(folder/'native_alias.ll').read_text();need(len(re.findall(r'^define ',ir,re.M))==1,'Fresh IR has one real defined C function')
    need('@'+M.OLD+' = dso_local alias i32 (i32, i32, i32, i32, i32, i32, i32, i32), ptr @'+M.NEW in ir,'Actual IR strongalias of real8arg C definition')
    lines=[x for x in ir.splitlines() if 'asm sideeffect "jal' in x]
    expected_constraint=','.join(['={x'+str(i)+'}' for i in range(10,18)]+['{x'+str(i)+'}' for i in range(10,18)])
    need(len(lines)==13 and all(expected_constraint in x and '~{memory}' in x and all('~{x'+str(i)+'}' in x for i in (1,5,6,7,28,29,30,31)) for x in lines),
         'All13 actual opaque calls retain full8register read/write bridges and caller/memory clobbers')
    need(Counter(re.findall(r'asm sideeffect "jal ra,([^" ]+)"',ir))==Counter({n:count for n,count in
        [('__tsl9v4160_ota_code_92f2',4),('__tsl9v4160_call_9c0a',1),('__tsl9v4160_call_9124',4),('__tsl9v4160_ota_code_13f66',1),('__tsl9v4160_conditional_code_13e98',1),('__tsl9v4160_ota_code_9b8e',1)]}),
         'Actual IR directcallee topology unchanged')
    old=M.case(root,'v4160-ota-handler-compact-2026-10-22')/'ABI-review/native.py';module=runpy.run_path(str(old));fields,llvm,ctx=module['context'](root)
    raw=native.function_bytes(M.symbol(native,M.NEW));rows=fields['rows'](raw,0,ctx)
    need([{k:v for k,v in x.items() if k!='offset'} for x in rows]==llvm['parse']((folder/'alias-disassembly.log').read_text()),'All193 raw native fields equal actual LLVM disassembly')
    need(len(rows)==193,'Frozen compact instruction inventory')
    loop=runpy.run_path(str(old.parent/'loop.py'));response=loop['response_ir'](ir);frame=loop['frame_contents'](rows)
    return dict(fresh_recipe_count=11,project_MD_dependencies=4,resource_headers=1,source_algorithm_unchanged=True,
        same_TU_source_alias=True,IR_defined_C_functions=1,IR_raw8_opaque_calls=13,native_instructions=len(rows),
        response=response,frame_contents=frame,strict_ROM_link_failed=True,numeric_ROM_witness_not_provider=True,
        source_pins=dict(record['source_pins']),generation_artifact_count=len(record['artifacts']))
