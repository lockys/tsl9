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
import re
sys.dont_write_bytecode=True
MODEL='experiments/tsl9-v4160-ota-handler-compact'
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

UND={'__tsl9v4160_ota_code_92f2','__tsl9v4160_call_9c0a','__tsl9v4160_call_9124',
     '__tsl9v4160_ota_code_13f66','__tsl9v4160_conditional_code_13e98',
     '__tsl9v4160_ota_code_9b8e','__tsl9v4160_ota_code_8e18',
     '__tsl9v4160_ota_code_9ee0','__tsl9v4160_captured_body_99e8'}
def parser_at(root):
    p=next(p for p in(root/'analysis/v4160-irq-native-2026-10-21/compiler-review/elf32.py',root/'apk-analysis/tsl9-v4160-irq-native-2026-10-21/compiler-review/elf32.py') if p.is_file())
    need(H(p)==PARSER,'Immutable actual ELF reader');return p

def expected_recipes(root,folder,mode,tools):
    source=root/MODEL/'src/ota_handler.c'
    return [('compiler-resource-dir',[tools['clang'],'-print-resource-dir']),
            ('native-object',[tools['clang'],*flags(mode),'-c','-MD','-MF',folder/'ota_handler.d','-MT','ota_handler.o',source,'-o',folder/'ota_handler.o']),
            ('native-IR',[tools['clang'],*flags(mode),'-S','-emit-llvm',source,'-o',folder/'ota_handler.ll']),
            ('complete-static-disassembly',[tools['llvm-objdump'],'--mattr=+m,+a,+c,+zicsr','-d','-r',folder/'ota_handler.o'])]

def stack_adjust(raw):
    w=int.from_bytes(raw,'little');sx=lambda n,b:n-(1<<b) if n&(1<<(b-1)) else n
    if len(raw)==4 and w&0x000fffff==0x10113:return sx(w>>20,12)
    if len(raw)==2 and w&3==1 and (w>>7)&31==2:
        if w>>13==0:return sx(((w>>2)&31)|(((w>>12)&1)<<5),6)
        if w>>13==3:return sx((((w>>12)&1)<<9)|(((w>>6)&1)<<4)|(((w>>5)&1)<<6)|(((w>>3)&3)<<7)|(((w>>2)&1)<<5),10)
    return None

def static_checks(root,folder,record):
    mode=record['mode'];commands=record['commands'];need(mode in('c','cpp'),'Actual language identity')
    tools={'clang':Path(commands[0]['argv'][0]),'llvm-objdump':Path(commands[3]['argv'][0])}
    need(all(H(p)==TOOLS[n] for n,p in tools.items()),'Actual pinned LLVM identities')
    need([(r['label'],r['argv']) for r in commands]==[(n,[str(v) for v in a]) for n,a in expected_recipes(root,folder,mode,tools)],'Four exact compile/resource/IR/disassembly recipes')
    for command in commands:
        need(command['exit']==0 and command['log']==command['label']+'.log' and H(folder/command['log'])==command['sha256'],'Actual tool log hash and successful exit')
        need(command['TMP']==command['TEMP']==str(folder/'compiler-temp'),'Owned compiler temporary directory')
    resource=Path((folder/'compiler-resource-dir.log').read_text().strip())/'include/stdint.h'
    need(H(resource)=='7ce5540d5fb6e8da9760928e76cbdd5ebef329d701ad598d30d8e6f9d5d78b34','Actual Clang resource header')
    parser=parser_at(root);source=root/MODEL/'src/ota_handler.c'
    expected={str(p):H(p) for p in [source,source.with_name('io.h'),source.with_name('ota_handler.h'),Path(__file__).resolve(),parser,Path(sys.executable).resolve(),*tools.values(),resource]}
    need(record['source_pins']==expected,'Complete stable native source/runner/tool/resource identities')
    text=(folder/'ota_handler.d').read_text().replace('\\\n',' ').replace('\\\r\n',' ');lhs,_,rhs=text.partition(':')
    deps={Path(re.sub(r'\\(.)',r'\1',n)).resolve() for n in re.findall(r'(?:\\.|[^\s])+',rhs)}
    need(lhs=='ota_handler.o' and deps=={source,source.with_name('io.h'),source.with_name('ota_handler.h'),resource},'Exact actual -MD target and source/header closure')
    E=runpy.run_path(str(parser))['ELF'];e=E(folder/'ota_handler.o')
    need(e.kind==1 and e.flags==1,'Actual RV32/RVC relocatable object; no linker witness')
    functions=[s for s in e.symbols if s['info']&15==2 and s['size']];alloc=[s for s in e.sections if s['flags']&2 and s['size']]
    need(len(functions)==len(alloc)==1,'One real native function/allocation, no hidden helper or data')
    f=functions[0];s=alloc[0];need((f['name'],f['size'],f['index'],f['value'],f['info'],f['other'])==('tsl9_ota_handler_native_9c4a',s['size'],s['index'],0,18,0) and(s['type'],s['flags'],s['alignment'])==(1,6,2),'Honest actual function extent/owner')
    und={s['name'] for s in e.symbols if s['name'] and s['index']==0};need(und==UND,'Exactly six actual directcallee and three callback-address UND; no libc/stub provider')
    for relocation in e.relocations:
        need(relocation['owner']==s['name'] and relocation['type'] in(17,26,27) and relocation['addend']==0 and relocation['symbol']['name'] in UND and relocation['symbol']['index']==0,'Only real unresolved directcall/address relocations')
    need(not any(t['name'].startswith('__tsl9') and t['index']==0xfff1 for t in e.symbols),'No numeric ABS provider')
    payload=e.data(s);covered=0;rows=[];adjust=[]
    for line in(folder/'complete-static-disassembly.log').read_text().splitlines():
        match=re.match(r'^\s*([0-9a-f]+):\s+((?:[0-9a-f]{2}\s+)+)\s*([^\s]+)',line)
        if not match:continue
        at=int(match[1],16);raw=bytes.fromhex(match[2]);need(at==covered and len(raw) in(2,4) and raw==payload[at:at+len(raw)] and match[3] not in('<unknown>','.word','.2byte'),'Complete contiguous actual ELF/disassembly instruction bytes')
        rows.append(dict(offset=at,raw=raw.hex(),mnemonic=match[3]));covered+=len(raw);delta=stack_adjust(raw)
        if delta is not None:adjust.append(dict(offset=at,delta=delta))
    need(covered==len(payload)==f['size'],'Every function byte covered, no unparsed hidden tail')
    ir=(folder/'ota_handler.ll').read_text();need('load volatile i8' in ir and 'load volatile i32' in ir and 'store volatile i8' in ir,'Typed fresh memory effect widths retained')
    return dict(native_bytes=f['size'],instructions=len(rows),code_sha256=hashlib.sha256(payload).hexdigest(),
                stack_adjustments=adjust,undefined_symbols=sorted(und),relocation_count=len(e.relocations),
                relocations=e.relocations,actual_MD_inputs=[dict(path=str(p),sha256=H(p)) for p in sorted(deps)],
                instructions_raw=rows,original_bytes=530,numerical_size_fits=f['size']<=530,
                original_ABI_admitted=False,original_placement_admitted=False,real_callee_providers_linked=False,
                no_numeric_provider=True,target_execution=False,BIN_exported=False)

def replay(root,receipt):
    receipt=receipt.resolve();folder=receipt.parent;r=json.loads(receipt.read_bytes());need(r['passed'],'Successful retained native generation')
    need(r['artifacts']=={p.relative_to(folder).as_posix():dict(bytes=p.stat().st_size,sha256=H(p)) for p in folder.rglob('*') if p.is_file() and p!=receipt},'Complete actual native artifact identities')
    checked=static_checks(root,folder,r);need(checked==r['checks'],'Actual native recipe/source/MD/object/IR/coverage replay')
    return dict(passed=True,receipt=str(receipt),sha256=H(receipt),actual_native_artifacts_read=True,native_bytes=checked['native_bytes'],instructions=checked['instructions'],undefined_symbols=checked['undefined_symbols'],relocations=checked['relocation_count'],original_ABI_admitted=False,original_placement_admitted=False,target_execution=False,linked=False)

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--project-root',required=True,type=Path)
    p.add_argument('--tool-dir',type=Path);p.add_argument('--build-root',type=Path);p.add_argument('--replay',type=Path)
    p.add_argument('--language',choices=['c','cpp','both']);a=p.parse_args();root=a.project_root.resolve()
    if a.replay:need(a.tool_dir is None and a.build_root is None and a.language is None,'Readonly replay rejects fresh arguments');print(json.dumps(replay(root,a.replay)));return
    need(a.tool_dir is not None,'Explicit local pinned LLVM required')
    tools={n:next(p for p in(a.tool_dir/(n+'.exe'),a.tool_dir/n) if p.is_file()).resolve() for n in TOOLS}
    need(all(H(p)==TOOLS[n] for n,p in tools.items()),'Explicit pinned local LLVM binaries')
    parser=next(p for p in(root/'analysis/v4160-irq-native-2026-10-21/compiler-review/elf32.py',root/'apk-analysis/tsl9-v4160-irq-native-2026-10-21/compiler-review/elf32.py') if p.is_file())
    need(H(parser)==PARSER,'Immutable ELF field reader');E=runpy.run_path(str(parser))['ELF']
    owner=(root/MODEL/'build').resolve();base=a.build_root.resolve() if a.build_root else owner/('probe-'+uuid.uuid4().hex)
    need(base.is_relative_to(owner) and base!=owner and not base.exists(),'Create-only owned output scope');base.mkdir(parents=True)
    results=[]
    for mode in ('c','cpp') if a.language in(None,'both') else(a.language,):
        folder=base/mode;folder.mkdir();tmp=folder/'compiler-temp';tmp.mkdir();env=dict(os.environ,TMP=str(tmp),TEMP=str(tmp))
        source=root/MODEL/'src/ota_handler.c';inputs=[source,source.with_name('io.h'),source.with_name('ota_handler.h'),Path(__file__).resolve(),parser,Path(sys.executable).resolve(),*tools.values()]
        pins={str(p):H(p) for p in inputs};commands=[]
        def run(label,argv):
            x=subprocess.run([str(v) for v in argv],cwd=folder,env=env,capture_output=True,timeout=120)
            log=folder/(label+'.log');log.write_bytes(x.stdout+x.stderr)
            commands.append(dict(label=label,argv=[str(v) for v in argv],exit=x.returncode,log=log.name,sha256=H(log),TMP=str(tmp),TEMP=str(tmp)))
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
        record=dict(schema='TSL9-readable-OTA-handler-native-formal-v1',passed=True,mode=mode,source_pins=pins,commands=commands,
                    functions=functions,allocated_sections=allocated,allocated_bytes=sum(s['size'] for s in allocated),
                    undefined_symbols=und,relocations=e.relocations,ET_REL=True,original_bytes=530,
                    original_ABI_admitted=False,original_placement_admitted=False,target_execution=False,linked=False,
                    metadata_embedded_as_code=False,artifacts={p.relative_to(folder).as_posix():dict(bytes=p.stat().st_size,sha256=H(p)) for p in folder.rglob('*') if p.is_file()})
        record['checks']=static_checks(root,folder,record)
        receipt=folder/'verification.json';receipt.write_bytes((json.dumps(record,indent=2)+'\n').encode())
        results.append(dict(mode=mode,**replay(root,receipt)))
    print(json.dumps(dict(passed=True,results=results,target_execution=False,linked=False)))
if __name__=='__main__':main()
