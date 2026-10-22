#!/usr/bin/env python3
"""Fresh real C alias/weak-copy source wiring; final ROM resolution is numeric-only."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import runpy
import subprocess
import sys
import uuid
sys.dont_write_bytecode=True
MODEL='experiments/tsl9-v4160-ota-source-wiring'
IMAGE='NOT-FLASH-VALIDATED-ota-source-wired.bin'
OLD_IMAGE='NOT-FLASH-VALIDATED-tx-integrated.bin'
ENTRY='__tsl9v4160_ota_code_9c4a'
NATIVE='tsl9_ota_handler_native_9c4a'
ROM='__tsl9v4160_rom_entry'
MACHINE='8ae835ad43422b764f1e03563312ad9987fc568432ba4f6bc2e469f4d99d6e56'
FLAGS='fc3005e95419c73ab82a4554d3f0af5b3174b1a95736d52d656cefc5678289ab'
PARSER='00a231e3bbd881a9961c12fefd15565364cd813250a46a7b20851a6b9f3a2141'
LAYOUT='651a8f14d09e373cb5523ec12f97d1fcce3ff26a51b3d835ae55d0239945507b'
RESOURCE='7ce5540d5fb6e8da9760928e76cbdd5ebef329d701ad598d30d8e6f9d5d78b34'
TOOLS={'clang':'047dfde05acc6fcce5af669e25cd8d40b4f509b8842d151d6d8a43a1c6a35fd6','ld.lld':'fe7f55c0c78b3d87f33b905a3874e10e872ca7beef53a8199d7ff9ac6641ec3f','llvm-objcopy':'e5590a8f45e93f322f0829b91dbddb74e8c1eb91436d13161abc773aebf64469','llvm-objdump':'de40d1188fe63ff373e1a5dd83a12e2cb4545ca3b314da16a476ecf072e5a0fa'}
def H(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def read(path):return json.loads(path.read_bytes())
def canonical(value):return json.loads(json.dumps(value))
def need(value,message):
    if not value:raise ValueError(message)
def case(root,name):return next(p for p in(root/'analysis'/name,root/'apk-analysis'/('tsl9-'+name)) if p.is_dir())
def context(root):
    model=root/MODEL;machine=case(root,'v4160-ota-source-wiring-2026-10-22')/'ABI-review/machine.py'
    parser=case(root,'v4160-irq-native-2026-10-21')/'compiler-review/elf32.py'
    flagger=case(root,'v4160-ota-handler-compact-2026-10-22')/'implementation/verify_native.py'
    layout=root/'experiments/tsl9-v4160-tx-image-integration/original-image-layout.ld'
    need(H(machine)==MACHINE and H(parser)==PARSER and H(flagger)==FLAGS and H(layout)==LAYOUT,'Exact sealed static kernel/parser/profile/historical layout')
    return dict(model=model,machine=machine,parser=parser,flagger=flagger,layout=layout,extension=model/'extension.ld',M=runpy.run_path(str(machine)),E=runpy.run_path(str(parser))['ELF'],flags=runpy.run_path(str(flagger))['flags'])
def input_gate(ctx,paths):
    record=read(paths['base_receipt']);mode=record['mode'];m=ctx['M']
    need(record['passed'] and mode in('c','cpp'),'Successful retained baseline generation')
    named={'base_object':'source-integrated.o','base_witness':'ADDRESS-WITNESS-ONLY.elf','base_image':OLD_IMAGE,'historical_numeric_script':'NUMERIC-ROM-WITNESS-ONLY.ld'}
    for key,name in named.items():
        p=paths[key];need(record['artifacts'][name]==dict(bytes=p.stat().st_size,sha256=H(p)),'Actual retained input artifact identity '+key)
    need(H(paths['base_object'])==m['BASE'][mode][0] and H(paths['base_witness'])==m['BASE'][mode][1] and H(paths['base_image'])==m['IMAGE'],'Exact supported inherited object/witness/image')
    need(paths['historical_numeric_script'].read_bytes()==(ROM+' = 0x40000;\n').encode(),'Only exact historical numeric-ROM address boundary')
    return mode
def source_pins(root,ctx,tools,resource):
    compact=root/'experiments/tsl9-v4160-ota-handler-compact/src'
    paths=[Path(__file__).resolve(),Path(sys.executable).resolve(),ctx['machine'],ctx['parser'],ctx['flagger'],ctx['layout'],ctx['extension'],ctx['model']/'src/native_alias.c',ctx['model']/'src/page_tail.S',*(compact/n for n in('ota_handler.c','ota_handler.h','io.h')),*tools.values()]
    if resource is not None:paths.append(resource)
    return {str(p):H(p) for p in paths}
def recipes(root,ctx,folder,mode,paths,tools):
    flags=ctx['flags'](mode);src=ctx['model']/'src/native_alias.c';padding=ctx['model']/'src/page_tail.S'
    common=[tools['ld.lld'],'--no-relax','--error-limit=0','-T',ctx['layout'],'-T',ctx['extension']]
    return [('compiler-resource-dir',[tools['clang'],'-print-resource-dir']),
            ('alias-object',[tools['clang'],*flags,'-c','-MD','-MF',folder/'native_alias.d','-MT','native_alias.o',src,'-o',folder/'native_alias.o']),
            ('alias-IR',[tools['clang'],*flags,'-S','-emit-llvm',src,'-o',folder/'native_alias.ll']),
            ('alias-disassembly',[tools['llvm-objdump'],'--mattr=+m,+a,+c,+zicsr','-d','-r',folder/'native_alias.o']),
            ('page-tail-object',[tools['clang'],'--target=riscv32-unknown-elf','-march=rv32imac_zicsr','-mabi=ilp32','-mno-relax','-x','assembler','-c',padding,'-o',folder/'page_tail.o']),
            ('weaken-old-entry',[tools['llvm-objcopy'],'--weaken-symbol='+ENTRY,paths['base_object'],folder/'base-weakened.o']),
            ('partial-source-wiring',[tools['ld.lld'],'--no-relax','-r',folder/'base-weakened.o',folder/'native_alias.o',folder/'page_tail.o','-o',folder/'source-integrated.o']),
            ('strict-missing-ROM',[*common,folder/'source-integrated.o','-o',folder/'STRICT-MISSING-ROM.elf']),
            ('numeric-address-witness',[*common,'-T',folder/'NUMERIC-ROM-WITNESS-ONLY.ld',folder/'source-integrated.o','-o',folder/'ADDRESS-WITNESS-ONLY.elf']),
            ('binary-address-witness',[tools['llvm-objcopy'],'-O','binary',folder/'ADDRESS-WITNESS-ONLY.elf',folder/IMAGE]),
            ('selected-native-disassembly',[tools['llvm-objdump'],'--mattr=+m,+a,+c,+zicsr','-d','--section=.text.tsl9_ota_handler_native_9c4a','--section=.text.tsl9v4160.gatt_ingress_13f7e',folder/'ADDRESS-WITNESS-ONLY.elf'])]
def disassembly(e,log):
    owner=e.sections[next(s for s in e.symbols if s['name']==NATIVE)['index']];payload=e.data(owner);active=False;covered=0;count=0
    for line in log.read_text().splitlines():
        section=re.match(r'Disassembly of section (.+):',line)
        if section:active=section[1]==owner['name'];continue
        row=re.match(r'^\s*([0-9a-f]+):\s+((?:[0-9a-f]{2}\s+)+)\s*([^\s]+)',line)
        if not active or not row:continue
        at=int(row[1],16)-owner['address'];raw=bytes.fromhex(row[2])
        need(at==covered and len(raw) in(2,4) and raw==payload[at:at+len(raw)] and row[3] not in('<unknown>','.word','.2byte','.byte'),'Full actual C instruction-byte disassembly coverage')
        covered+=len(raw);count+=1
    need(covered==len(payload)==568 and count==193,'Measured C body coverage without borrowed extent/padding')
    return dict(bytes=covered,instructions=count)
def file_coverage(e,blob,loads):
    sections=sorted((s for s in e.sections if s['flags']&2 and s['type']!=8 and s['size']),key=lambda s:s['address'])
    need(sections[0]['address']==0x8000 and sections[-1]['address']+sections[-1]['size']==0x1b000 and all(a['address']+a['size']==b['address'] for a,b in zip(sections,sections[1:])),'All77824 exported bytes owned by contiguous real file sections; no holes/fallback')
    file_loads=sorted((p for p in loads if p['filesz']),key=lambda p:p['address'])
    need(file_loads[0]['address']==0x8000 and file_loads[-1]['address']+file_loads[-1]['filesz']==0x1b000 and all(a['address']+a['filesz']==b['address'] for a,b in zip(file_loads,file_loads[1:])),'Complete file LOAD extent without extra mapped bytes')
    for p in file_loads:
        need(p['filesz']==p['memsz'] and e.raw[p['offset']:p['offset']+p['filesz']]==blob[p['address']-0x8000:p['address']-0x8000+p['filesz']],'Every actual file LOAD byte matches exported witness')
    ram=[p for p in loads if not p['filesz']]
    need(len(loads)==17 and len(ram)==1 and (ram[0]['address'],ram[0]['memsz'],ram[0]['flags'])==(0x20004000,35160,6),'Only actual original NOBITS RAM memory load; no RAM bytes exported')
    return dict(owned_export_bytes=77824,file_sections=len(sections),LOADs=len(loads),unowned_holes=0,RAM_exported=False)
def static_checks(root,ctx,folder,record):
    paths={k:Path(v) for k,v in record['paths'].items()};mode=input_gate(ctx,paths);need(mode==record['mode'],'Actual baseline/compile language')
    tools={n:Path(v['path']) for n,v in record['tools'].items()};need(set(tools)==set(TOOLS) and all(H(p)==record['tools'][n]['sha256']==TOOLS[n] for n,p in tools.items()),'Current exact native tools')
    expected=recipes(root,ctx,folder,mode,paths,tools)
    need([(r['label'],r['argv']) for r in record['commands']]==[(name,[str(x) for x in argv]) for name,argv in expected],'Exact chronological11 actual source/ASM/objcopy/partial/strict/numeric/export recipes')
    for row in record['commands']:
        need(row['log']==row['label']+'.log' and H(folder/row['log'])==row['sha256'] and row['TMP']==row['TEMP']==str(folder/'compiler-temp'),'Actual complete recipe log and owned temporary environment')
        need(row['exit']!=0 if row['label']=='strict-missing-ROM' else row['exit']==0,'Actual strict/non-strict command outcomes')
    errors=[line for line in(folder/'strict-missing-ROM.log').read_text().splitlines() if 'error:' in line]
    need(errors==['ld.lld: error: undefined symbol: '+ROM] and not(folder/'STRICT-MISSING-ROM.elf').exists(),'Strict final link genuinely rejects only the missing ROM provider')
    need((folder/'NUMERIC-ROM-WITNESS-ONLY.ld').read_bytes()==paths['historical_numeric_script'].read_bytes(),'Exact old numeric witness text only; not a ROM body/provider')
    resource=Path((folder/'compiler-resource-dir.log').read_text().strip())/'include/stdint.h';need(H(resource)==RESOURCE,'Actual pinned Clang resource header')
    need(record['source_pins']==source_pins(root,ctx,tools,resource) and record['input_pins']=={str(p):H(p) for p in paths.values()},'Actual before/after source/tool/input identities')
    text=(folder/'native_alias.d').read_text().replace('\\\n',' ').replace('\\\r\n',' ');lhs,_,rhs=text.partition(':');deps={Path(re.sub(r'\\(.)',r'\1',n)).resolve() for n in re.findall(r'(?:\\.|[^\s])+',rhs)}
    compact=root/'experiments/tsl9-v4160-ota-handler-compact/src';wanted={ctx['model']/'src/native_alias.c',compact/'ota_handler.c',compact/'ota_handler.h',compact/'io.h',resource}
    need(lhs=='native_alias.o' and deps==wanted,'Exact actual MD primary+four project inputs and compiler resource header')
    ir=(folder/'native_alias.ll').read_text();alias='@'+ENTRY+' = dso_local alias i32 (i32, i32, i32, i32, i32, i32, i32, i32), ptr @'+NATIVE
    calls=[s for s in ir.splitlines() if 'asm sideeffect "jal' in s]
    need(alias in ir and len(calls)==13 and all(all('={x'+str(n)+'}' in s and ',{x'+str(n)+'}' in s for n in range(10,18)) and '~{memory}' in s and '~{x1}' in s for s in calls),'Genuine same-TU eight-input alias and complete eight-register read/write call bridges')
    m=ctx['M'];E=ctx['E'];base=E(paths['base_object']);weak=E(folder/'base-weakened.o');native=E(folder/'native_alias.o');tail=E(folder/'page_tail.o');merged=E(folder/'source-integrated.o');linked=E(folder/'ADDRESS-WITNESS-ONLY.elf');blob=(folder/IMAGE).read_bytes()
    results=dict(weakened=m['weakened'](base,weak),partial=m['partial'](base,native,tail,merged),metadata=m['metadata'](base,native,tail,merged,linked),native_relocations=m['relocated_component'](native,linked),witness=m['final'](E(paths['base_witness']),merged,linked,paths['base_image'].read_bytes(),blob),raw_coverage=disassembly(native,folder/'alias-disassembly.log'),linked_coverage=disassembly(linked,folder/'selected-native-disassembly.log'),MD_inputs=[dict(path=str(p),sha256=H(p)) for p in sorted(deps)])
    results['file_coverage']=file_coverage(linked,blob,results['witness']['LOADs']);results['ROM_provider']=False;results['original_ABI_admitted']=False;results['hardware_OTA_proved']=False
    return canonical(results)
def replay(root,receipt):
    receipt=receipt.resolve();folder=receipt.parent;record=read(receipt);ctx=context(root);need(record['passed'],'Successful actual source wiring generation')
    need(record['artifacts']=={p.relative_to(folder).as_posix():dict(bytes=p.stat().st_size,sha256=H(p)) for p in folder.rglob('*') if p.is_file() and p!=receipt},'Complete actual file inventory, no omitted IR/MD/logs or hidden outputs')
    actual=static_checks(root,ctx,folder,record);need(actual==record['checks'],'Read-only complete actual recipe/source/object/metadata/relocation/LOAD/image replay')
    return dict(passed=True,mode=record['mode'],receipt=str(receipt),sha256=H(receipt),actual_build_artifacts_read=True,image_bytes=actual['witness']['image_bytes'],image_sha256=actual['witness']['image_sha256'],source_entry_wired=True,ROM_provider=False,installed_ROM_proved=False,Flash_NV_free_proved=False,original_ABI_admitted=False,hardware_OTA_proved=False,target_execution=False)
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--project-root',required=True,type=Path);p.add_argument('--replay',type=Path)
    for name in('tool-dir','base-object','base-receipt','base-witness','base-image','build-root'):p.add_argument('--'+name,type=Path)
    a=p.parse_args();root=a.project_root.resolve()
    if a.replay:
        need(all(getattr(a,n) is None for n in('tool_dir','base_object','base_receipt','base_witness','base_image','build_root')),'Read-only replay rejects all generation options');print(json.dumps(replay(root,a.replay)));return
    need(all(getattr(a,n) is not None for n in('tool_dir','base_object','base_receipt','base_witness','base_image')),'Explicit local tools and actual retained baseline artifacts required')
    ctx=context(root);tools={n:next(p for p in(a.tool_dir/(n+'.exe'),a.tool_dir/n) if p.is_file()).resolve() for n in TOOLS};need(all(H(v)==TOOLS[n] for n,v in tools.items()),'Pinned local compiler/linker/objcopy/objdump')
    paths={n:getattr(a,n).resolve() for n in('base_object','base_receipt','base_witness','base_image')};paths['historical_numeric_script']=paths['base_receipt'].parent/'NUMERIC-ROM-WITNESS-ONLY.ld';mode=input_gate(ctx,paths)
    owner=ctx['model']/'build';folder=a.build_root.resolve() if a.build_root else owner/('native-'+uuid.uuid4().hex);need(folder.is_relative_to(owner) and folder!=owner and not folder.exists(),'Create-only new owned output scope');folder.mkdir(parents=True);tmp=folder/'compiler-temp';tmp.mkdir();env=dict(os.environ,TMP=str(tmp),TEMP=str(tmp))
    input_pins={str(v):H(v) for v in paths.values()};pins=source_pins(root,ctx,tools,None);commands=[];plans=recipes(root,ctx,folder,mode,paths,tools)
    def run(label,argv):
        result=subprocess.run([str(v) for v in argv],cwd=folder,env=env,capture_output=True,timeout=120);log=folder/(label+'.log');log.write_bytes(result.stdout+result.stderr);commands.append(dict(label=label,argv=[str(v) for v in argv],exit=result.returncode,log=log.name,sha256=H(log),TMP=str(tmp),TEMP=str(tmp)))
        need(result.returncode!=0 if label=='strict-missing-ROM' else result.returncode==0,'Actual tool outcome: '+str(log));return result
    # Locate and pin the real resource header before the first source compile.
    first=run(*plans[0]);resource=Path(first.stdout.decode().strip())/'include/stdint.h';need(H(resource)==RESOURCE,'Actual current resource header');pins[str(resource)]=H(resource)
    for name,argv in plans[1:]:
        if name=='numeric-address-witness':(folder/'NUMERIC-ROM-WITNESS-ONLY.ld').write_bytes(paths['historical_numeric_script'].read_bytes())
        run(name,argv)
    need(input_pins=={str(v):H(v) for v in paths.values()} and pins==source_pins(root,ctx,tools,resource),'Stable source/tool/header/input identities before/after generation')
    record=dict(schema='TSL9-real-source-wiring-formal-v1',passed=True,mode=mode,paths={n:str(v) for n,v in paths.items()},tools={n:dict(path=str(v),sha256=H(v)) for n,v in tools.items()},source_pins=pins,input_pins=input_pins,commands=commands,ROM_provider=False,original_ABI_admitted=False,hardware_OTA_proved=False,target_execution=False)
    record['checks']=static_checks(root,ctx,folder,record);record['artifacts']={v.relative_to(folder).as_posix():dict(bytes=v.stat().st_size,sha256=H(v)) for v in folder.rglob('*') if v.is_file()}
    receipt=folder/'verification.json';receipt.write_bytes((json.dumps(record,indent=2)+'\n').encode());print(json.dumps(replay(root,receipt)))
if __name__=='__main__':main()
