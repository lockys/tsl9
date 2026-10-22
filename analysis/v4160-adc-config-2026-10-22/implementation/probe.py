#!/usr/bin/env python3
"""Compile/run synthetic HOST C/C++; compile/static-inspect native only."""
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
MODEL='experiments/tsl9-adc-config'
OLD='apk-analysis/tsl9-v4160-resident-native-2026-10-22/implementation/probe.py'
GUARD='experiments/tsl9-v4160-flash-register-prefix/verify_host.py'
GPIN='76c6d512164da18cd0fc4641940301f2df2362251c584de0e6b049c21d0ad189'
ENTRY='tsl9_adc_config_1892e'
PORTS={'ml_port_read8','ml_port_read32','ml_port_write32'}
GLOBALS=PORTS|{'tsl9_adc_config_io',ENTRY}
REGS=['zero','ra','sp','gp','tp','t0','t1','t2','s0','s1','a0','a1','a2','a3','a4','a5','a6','a7','s2','s3','s4','s5','s6','s7','s8','s9','s10','s11','t3','t4','t5','t6']
MUTANTS=[('full_config_word','bits|=v<<8;','bits|=(v&255u)<<8;'),('byte_decrement_wrap','bits|=((v-1u)&255u)<<20;','bits|=(v-1u)<<20;'),('fresh_word_address','config+12u,&v','config+16u,&v')]
def H(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def need(v,m):
    if not v:raise ValueError(m)
def locate(root,name):
    p=root/name
    if p.is_file():return p
    if name.startswith('apk-analysis/tsl9-'):return root/('analysis/'+name[len('apk-analysis/tsl9-'):])
    return p
def prior(root):return runpy.run_path(str(locate(root,OLD)))
def guard(root):
    need(H(root/GUARD)==GPIN,'Immutable HOST-format launch guard')
    return runpy.run_path(str(root/GUARD))
def pins(root,tools,host_cc,resource=None):
    src=root/MODEL/'src';paths=[Path(__file__).resolve(),Path(sys.executable).resolve(),locate(root,OLD),prior(root)['parser'](root),root/GUARD,root/'scripts/portable_verify.py',host_cc,*tools.values(),*src.glob('*.c'),*src.glob('*.h'),root/MODEL/'tests/smoke.c',Path(__file__).resolve().parent/'source-proof.json']
    paths += [root/'experiments/tsl9-resident-memory-leaves/src'/n for n in ('memory_leaves.h','io.h')]
    if resource:paths.append(resource)
    return {str(p):H(p) for p in paths}
def native_recipes(root,folder,mode,tools):
    flags=prior(root)['flags'](mode);source=root/MODEL/'src/native.c'
    return [('compiler-resource-dir',[tools['clang'],'-print-resource-dir']),('native-object',[tools['clang'],*flags,'-c','-MD','-MF',folder/'native.d','-MT','native.o',source,'-o',folder/'native.o']),('native-IR',[tools['clang'],*flags,'-S','-emit-llvm',source,'-o',folder/'native.ll']),('complete-static-disassembly',[tools['llvm-objdump'],'--mattr=+m,+a,+c,+zicsr,+zifencei','-d','-r',folder/'native.o'])]
def host_args(root,folder,mode,cc,msvc,core):
    src=root/MODEL/'src';exe=folder/('tests.exe' if os.name=='nt' else 'tests');files=[core,src/'host_io.c',root/MODEL/'tests/smoke.c']
    if msvc:return [cc,'/nologo','/W4','/WX','/Od','/TP' if mode=='cpp' else '/TC','/std:c++17' if mode=='cpp' else '/std:c11','/I'+str(src),'/Fo'+str(folder)+os.sep,*files,'/Fe'+str(exe),'/link','/INCREMENTAL:NO']
    return [cc,'-x','c++' if mode=='cpp' else 'c','-std=c++17' if mode=='cpp' else '-std=c11','-O1','-Wall','-Wextra','-Werror','-I',src,*files,'-o',exe]
def native_inspect(root,folder,r):
    old=prior(root);tools={n:Path(v) for n,v in r['tools'].items()};need(all(H(p)==old['TOOLS'][n] for n,p in tools.items()),'Pinned native LLVM')
    expected=[(n,[str(v) for v in a]) for n,a in native_recipes(root,folder,r['mode'],tools)]
    need([(c['label'],c['argv']) for c in r['native_commands']]==expected,'Exact native recipe')
    resource=Path((folder/'compiler-resource-dir.log').read_text().strip())/'include/stdint.h';need(H(resource)==old['RESOURCE'],'Actual compiler resource header')
    need(r['source_pins']==pins(root,tools,Path(r['host_compiler']['path']),resource),'Current full source/helper/tool/resource identity')
    text=(folder/'native.d').read_text().replace('\\\n',' ');lhs,_,rhs=text.partition(':');deps={Path(re.sub(r'\\(.)',r'\1',p)).resolve() for p in re.findall(r'(?:\\.|[^\s])+',rhs)}
    src=root/MODEL/'src';expected_deps={src/n for n in ('native.c','adc_config.c','adc_config.h')}|{root/'experiments/tsl9-resident-memory-leaves/src'/n for n in ('memory_leaves.h','io.h')}|{resource}
    need(lhs=='native.o' and deps==expected_deps,'Exact actual -MD closure')
    E=runpy.run_path(str(old['parser'](root)))['ELF'];e=E(folder/'native.o');need(e.kind==1 and e.flags==1,'Actual RV32/RVC ET_REL')
    alloc=[s for s in e.sections if s['flags']&2 and s['size']];funcs=[f for f in e.symbols if f['info']&15==2 and f['size']]
    need({f['name'] for f in funcs if f['info']>>4==1}==GLOBALS,'Five actual global functions')
    need(all(s['type']==1 and s['flags']==6 for s in alloc),'Only code allocated')
    coverage={s['name']:0 for s in alloc};ins={s['name']:[] for s in alloc};current=None
    for line in (folder/'complete-static-disassembly.log').read_text().splitlines():
        m=re.match(r'Disassembly of section (.+):',line)
        if m:current=m[1];continue
        m=re.match(r'^\s*([0-9a-f]+):\s+((?:[0-9a-f]{2}\s+)+)\s*([^\s]+)\s*(.*)',line)
        if not m:continue
        at=int(m[1],16);raw=bytes.fromhex(m[2]);need(current in coverage and at==coverage[current] and len(raw) in(2,4) and raw==e.data(e.byname[current])[at:at+len(raw)] and m[3] not in ('<unknown>','.word','.2byte'),'Complete contiguous raw disassembly')
        coverage[current]+=len(raw);ins[current].append(dict(offset=at,raw=raw.hex(),mnemonic=m[3],operands=m[4]))
    need(all(coverage[s['name']]==s['size'] for s in alloc),'No omitted code tails')
    results=[];no_rd={'sb','sh','sw','sd','beq','bne','blt','bge','bltu','bgeu','beqz','bnez','blez','bgez','bltz','bgtz','ble','bgt','bleu','bgtu','j','jr','ret','fence','fence.i','unimp','nop'}
    for f in funcs:
        sec=e.sections[f['index']]['name'];rows=ins[sec];written=set()
        for i in rows:
            if i['mnemonic'] in no_rd:continue
            first=i['operands'].split(',')[0].strip()
            if first in REGS:
                if first!='zero':written.add(REGS.index(first))
            elif i['mnemonic'] in ('call','tail'):written.add(1)
            else:need(False,'Unclassified destination '+str(i))
        results.append(dict(name=f['name'],bytes=f['size'],instructions=len(rows),code_sha256=hashlib.sha256(e.function_bytes(f)).hexdigest(),section=sec,global_FUNC=f['info']>>4==1,own_written_GPRs=sorted(written),extra_written_vs_original=sorted(written-{13,14,15}) if f['name']==ENTRY else None,stack_or_RA_or_saved_written=sorted(written&{1,2,8,9,*range(18,28)}),stack_access=any('(sp)' in i['operands'] for i in rows),calls=any(i['mnemonic'] in ('call','tail','jal','jalr') for i in rows)))
    ir=(folder/'native.ll').read_text();signature=re.search(r'define[^@\n]* i32 @'+ENTRY+r'\(([^)]*)\)',ir);need(signature is not None and len(signature[1].split(','))==2 and 'ptr' not in signature[1],'Two-u32/u32 public ABI')
    body=ir[signature.start():ir.index('\n}',signature.start())];volatile=re.findall(r'(load|store) volatile i(8|32)',body);need(volatile.count(('load','32'))==10 and volatile.count(('load','8'))==1 and volatile.count(('store','32'))==3 and len(volatile)==14,'Fourteen genuine volatile effects in public LLVM IR')
    return dict(functions=results,unused_genuine_globals=[f['name'] for f in results if f['name']!=ENTRY],allocated_bytes=sum(s['size'] for s in alloc),instructions=sum(len(x) for x in ins.values()),UND=sorted({s['name'] for s in e.symbols if s['index']==0 and s['name']}),RELA=len(e.relocations),relocations=e.relocations,global_ABS=[s['name'] for s in e.symbols if s['index']==0xfff1 and s['info']>>4],public_volatile_effects=[list(v) for v in volatile],actual_MD_inputs=[dict(path=str(p),sha256=H(p)) for p in sorted(deps)],full_original_register_ABI_proved=False,installed_provider_proved=False,target_execution=False,linked=False,BIN_exported=False)
def inspect(root,folder,r):
    need(r['mode'] in ('c','cpp'),'C/C++ mode');g=guard(root)
    for row in r['native_commands']:
        need(row['exit']==0 and row['log']==row['label']+'.log' and H(folder/row['log'])==row['log_sha256'],'Actual native recipe logs')
        need(row['TMP']==row['TEMP']==str(folder/'compiler-temp'),'Native temporary ownership')
    need(H(Path(r['host_compiler']['path']))==r['host_compiler']['sha256'],'Actual HOST compiler')
    h=r['host_commands'];variants=[(folder,root/MODEL/'src/adc_config.c',False)]+[(folder/name,folder/name/'mutant-core.c',True) for name,_,_ in MUTANTS]
    need(len(h)==8,'Positive plus three compiled semantic controls')
    for i,(where,core,negative) in enumerate(variants):
        if negative:
            _,before,after=MUTANTS[i-1];text=(root/MODEL/'src/adc_config.c').read_text();need(text.count(before)==1 and core.read_bytes()==text.replace(before,after).encode(),'One exact compiled semantic mutation')
        compile_,run=h[2*i:2*i+2];need(compile_['argv']==[str(x) for x in host_args(root,where,r['mode'],Path(r['host_compiler']['path']),r['host_compiler']['msvc'],core)] and compile_['exit']==0,'Exact HOST source compilation')
        exe=where/('tests.exe' if os.name=='nt' else 'tests');need(run['argv']==[str(exe)] and run['host_executable_guard']==g['host_executable'](exe),'Actual local-machine HOST executable; no RV32 launch')
        need(run['exit']!=0 if negative else run['exit']==0,'Actual behavior exit')
        for c in (compile_,run):need(Path(c['folder'])==where and H(where/c['log'])==c['log_sha256'],'Actual HOST command/output identity')
        if negative:need('failure line' in (where/'tests.log').read_text(),'Semantic assertion failed, not compile/launch')
    tests=json.loads((folder/'tests.log').read_text());need(tests==r['HOST_tests'] and tests['passed'] and tests['cases']==80 and tests['synthetic_only'],'Actual synthetic HOST suite')
    return dict(HOST_tests=tests,compiled_semantic_controls=3,native=native_inspect(root,folder,r),HOST_original_firmware_execution=False,ISA_emulation=False,hardware_OTA_proved=False)
def replay(root,receipt):
    receipt=receipt.resolve();folder=receipt.parent;r=json.loads(receipt.read_bytes());need(r['artifacts']=={p.relative_to(folder).as_posix():dict(bytes=p.stat().st_size,sha256=H(p)) for p in folder.rglob('*') if p.is_file() and p!=receipt},'Complete actual artifact inventory')
    checked=inspect(root,folder,r);need(checked==r['checks'],'Exact read-only HOST/native readback')
    return dict(passed=True,receipt=str(receipt),sha256=H(receipt),mode=r['mode'],actual_artifacts_read=True,**checked)
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--project-root',required=True,type=Path);p.add_argument('--tool-dir',type=Path);p.add_argument('--build-root',type=Path);p.add_argument('--replay',type=Path);a=p.parse_args();root=a.project_root.resolve()
    if a.replay:need(a.tool_dir is None and a.build_root is None,'Read-only replay rejects build flags');print(json.dumps(replay(root,a.replay)));return
    need(a.tool_dir is not None,'Explicit fixed local LLVM required');old=prior(root);tools={n:next(p.resolve() for p in(a.tool_dir/(n+'.exe'),a.tool_dir/n) if p.is_file()) for n in old['TOOLS']};need(all(H(p)==old['TOOLS'][n] for n,p in tools.items()),'Pinned native LLVM');g=guard(root)
    owner=root/MODEL/'build';base=a.build_root.resolve() if a.build_root else owner/('adc-'+uuid.uuid4().hex);need(base.is_relative_to(owner) and base!=owner and not base.exists(),'Create-only owned build');base.mkdir(parents=True);results=[]
    for mode in ('c','cpp'):
        folder=base/mode;folder.mkdir();tmp=folder/'compiler-temp';tmp.mkdir();cc,host_env,msvc=g['host_tools'](root).compiler_for(mode);cc=Path(cc).resolve();env=dict(host_env,TMP=str(tmp),TEMP=str(tmp));before=pins(root,tools,cc);resource=None;native_commands=[];host_commands=[]
        for label,argv in native_recipes(root,folder,mode,tools):
            x=subprocess.run([str(v) for v in argv],cwd=folder,env=env,capture_output=True,timeout=120);log=folder/(label+'.log');log.write_bytes(x.stdout+x.stderr);native_commands.append(dict(label=label,argv=[str(v) for v in argv],exit=x.returncode,log=log.name,log_sha256=H(log),TMP=str(tmp),TEMP=str(tmp)));need(x.returncode==0,'Native compiler failed '+str(log))
            if resource is None:resource=Path(x.stdout.decode().strip())/'include/stdint.h';need(H(resource)==old['RESOURCE'],'Pinned resource');before[str(resource)]=H(resource)
        for i in range(4):
            if i==0:where=folder;core=root/MODEL/'src/adc_config.c'
            else:
                name,oldtext,newtext=MUTANTS[i-1];where=folder/name;where.mkdir();core=where/'mutant-core.c';text=(root/MODEL/'src/adc_config.c').read_text();need(text.count(oldtext)==1,'Unique semantic mutation');core.write_bytes(text.replace(oldtext,newtext).encode())
            c,_=g['execute'](host_args(root,where,mode,cc,msvc,core),where,'compile',env);host_commands.append(dict(folder=str(where),**c));exe=where/('tests.exe' if os.name=='nt' else 'tests');t,out=g['execute']([exe],where,'tests',env,expect=1 if i else 0,host_test=True);host_commands.append(dict(folder=str(where),**t))
        need(before==pins(root,tools,cc,resource),'Before/after stable source/tool closure');r=dict(schema='TSL9-readable-ADC-config-v1',mode=mode,tools={n:str(v) for n,v in tools.items()},host_compiler=dict(path=str(cc),sha256=H(cc),msvc=msvc),source_pins=before,native_commands=native_commands,host_commands=host_commands,HOST_tests=json.loads((folder/'tests.log').read_text()));r['checks']=inspect(root,folder,r);r['artifacts']={p.relative_to(folder).as_posix():dict(bytes=p.stat().st_size,sha256=H(p)) for p in folder.rglob('*') if p.is_file()};receipt=folder/'verification.json';receipt.write_bytes((json.dumps(r,indent=2)+'\n').encode());results.append(dict(receipt=str(receipt),sha256=H(receipt),HOST_tests=r['HOST_tests'],native=r['checks']['native']))
    print(json.dumps(dict(passed=True,results=results,target_execution=False)))
if __name__=='__main__':main()
