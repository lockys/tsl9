#!/usr/bin/env python3
"""Compile authored C/C++ memory algorithms to ET_REL only; no target execution."""
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
MODEL='experiments/tsl9-resident-memory-leaves'
TOOLS={'clang':'047dfde05acc6fcce5af669e25cd8d40b4f509b8842d151d6d8a43a1c6a35fd6','llvm-objdump':'de40d1188fe63ff373e1a5dd83a12e2cb4545ca3b314da16a476ecf072e5a0fa'}
PARSER='00a231e3bbd881a9961c12fefd15565364cd813250a46a7b20851a6b9f3a2141'
RESOURCE='7ce5540d5fb6e8da9760928e76cbdd5ebef329d701ad598d30d8e6f9d5d78b34'
PORTS={'ml_port_read8','ml_port_read32','ml_port_write8','ml_port_write32','ml_port_fence_i'}
PUBLIC={'tsl9_candidate_compare_200004bc','tsl9_candidate_fill_2000039c','tsl9_candidate_copy_20000332'}
def H(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def need(v,m):
    if not v:raise ValueError(m)
def parser(root):
    p=next(p for p in(root/'analysis/v4160-irq-native-2026-10-21/compiler-review/elf32.py',root/'apk-analysis/tsl9-v4160-irq-native-2026-10-21/compiler-review/elf32.py') if p.is_file())
    need(H(p)==PARSER,'Pinned ELF32 reader');return p
def flags(mode):
    return ['--target=riscv32-unknown-elf','-march=rv32imac_zicsr','-mabi=ilp32','-Oz','-mllvm','-enable-machine-outliner=never','-ffreestanding','-fno-builtin','-fno-stack-protector','-fno-unwind-tables','-fno-asynchronous-unwind-tables','-mno-relax','-ffunction-sections','-fdata-sections','-Wall','-Wextra','-Werror','-x','c' if mode=='c' else 'c++','-std=c11' if mode=='c' else '-std=c++17']+(['-fno-exceptions'] if mode=='cpp' else [])
def recipes(root,folder,mode,tools):
    source=root/MODEL/'src/memory_leaves.c'
    return [('compiler-resource-dir',[tools['clang'],'-print-resource-dir']),('native-object',[tools['clang'],*flags(mode),'-c','-MD','-MF',folder/'memory_leaves.d','-MT','memory_leaves.o',source,'-o',folder/'memory_leaves.o']),('native-IR',[tools['clang'],*flags(mode),'-S','-emit-llvm',source,'-o',folder/'memory_leaves.ll']),('complete-static-disassembly',[tools['llvm-objdump'],'--mattr=+m,+a,+c,+zicsr','-d','-r',folder/'memory_leaves.o'])]
def pins(root,tools,resource=None):
    src=root/MODEL/'src';paths=[src/'memory_leaves.c',src/'memory_leaves.h',src/'io.h',Path(__file__).resolve(),parser(root),Path(sys.executable).resolve(),*tools.values()]+([resource] if resource is not None else [])
    return {str(p):H(p) for p in paths}
def inspect(root,folder,r):
    need(r['mode'] in('c','cpp'),'Language');commands=r['commands'];need(len(commands)==4,'Four actual recipes')
    tools={'clang':Path(commands[0]['argv'][0]),'llvm-objdump':Path(commands[3]['argv'][0])};need(all(H(p)==TOOLS[n] for n,p in tools.items()),'Actual pinned LLVM tools')
    need([(c['label'],c['argv']) for c in commands]==[(n,[str(x) for x in a]) for n,a in recipes(root,folder,r['mode'],tools)],'Exact source/flags/MD/IR/disassembly recipes')
    for c in commands:need(c['exit']==0 and c['log']==c['label']+'.log' and H(folder/c['log'])==c['sha256'] and c['TMP']==c['TEMP']==str(folder/'compiler-temp'),'Actual successful logs and owned temporary directory')
    resource=Path((folder/'compiler-resource-dir.log').read_text().strip())/'include/stdint.h';need(H(resource)==RESOURCE,'Actual compiler resource header')
    need(r['source_pins']==pins(root,tools,resource),'Stable source/tool/runner/resource identities')
    src=root/MODEL/'src';text=(folder/'memory_leaves.d').read_text().replace('\\\n',' ');lhs,_,rhs=text.partition(':');deps={Path(re.sub(r'\\(.)',r'\1',p)).resolve() for p in re.findall(r'(?:\\.|[^\s])+',rhs)}
    need(lhs=='memory_leaves.o' and deps=={src/'memory_leaves.c',src/'memory_leaves.h',src/'io.h',resource},'Exact actual -MD source/header/resource closure')
    E=runpy.run_path(str(parser(root)))['ELF'];e=E(folder/'memory_leaves.o');need(e.kind==1 and e.flags==1,'Actual RV32/RVC ET_REL')
    alloc=[s for s in e.sections if s['flags']&2 and s['size']];funcs=[f for f in e.symbols if f['info']&15==2 and f['size']]
    need({f['name'] for f in funcs if f['info']>>4==1}==PUBLIC,'Three genuine public functions')
    need(all(s['type']==1 and s['flags']==6 for s in alloc),'Code allocations only; no embedded original bytes/data')
    need({s['name'] for s in e.symbols if s['index']==0 and s['name']}==PORTS,'Exactly five unresolved real I/O ports, no numeric providers/libc')
    need(not any(s['index']==0xfff1 and s['info']>>4 for s in e.symbols),'No global ABS provider')
    text=(folder/'complete-static-disassembly.log').read_text();current=None;coverage={s['name']:0 for s in alloc};counts={s['name']:0 for s in alloc}
    for line in text.splitlines():
        m=re.match(r'Disassembly of section (.+):',line)
        if m:current=m[1];continue
        m=re.match(r'^\s*([0-9a-f]+):\s+((?:[0-9a-f]{2}\s+)+)\s*([^\s]+)',line)
        if not m:continue
        need(current in coverage,'Instruction belongs to actual allocated code');at=int(m[1],16);raw=bytes.fromhex(m[2]);need(at==coverage[current] and len(raw) in(2,4) and raw==e.data(e.byname[current])[at:at+len(raw)] and m[3] not in('<unknown>','.word','.2byte'),'Complete real contiguous instruction bytes')
        coverage[current]+=len(raw);counts[current]+=1
    need(all(coverage[s['name']]==s['size'] for s in alloc),'No unparsed/padded code tail')
    ir=(folder/'memory_leaves.ll').read_text();need(all('@'+p+'(' in ir for p in PORTS),'Actual typed I/O boundaries in LLVM IR')
    return dict(functions=[dict(name=f['name'],bytes=f['size'],info=f['info'],section=e.sections[f['index']]['name'],code_sha256=hashlib.sha256(e.function_bytes(f)).hexdigest()) for f in funcs],allocated_bytes=sum(s['size'] for s in alloc),instructions=sum(counts.values()),instructions_per_section=counts,undefined_symbols=sorted(PORTS),RELA=len(e.relocations),relocations=e.relocations,actual_MD_inputs=[dict(path=str(p),sha256=H(p)) for p in sorted(deps)],native_candidate_ABI_proved=False,installed_provider_proved=False,linked=False,BIN_exported=False,target_execution=False)
def replay(root,receipt):
    receipt=receipt.resolve();folder=receipt.parent;r=json.loads(receipt.read_bytes());need(r['passed'],'Successful retained build')
    actual={p.relative_to(folder).as_posix():dict(bytes=p.stat().st_size,sha256=H(p)) for p in folder.rglob('*') if p.is_file() and p!=receipt};need(r['artifacts']==actual,'Complete actual artifact inventory')
    checked=inspect(root,folder,r);need(checked==r['checks'],'Actual native readback equals receipt')
    return dict(passed=True,mode=r['mode'],receipt=str(receipt),sha256=H(receipt),actual_native_artifacts_read=True,**{k:checked[k] for k in('functions','allocated_bytes','instructions','undefined_symbols','RELA','native_candidate_ABI_proved','installed_provider_proved','linked','BIN_exported','target_execution')})
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--project-root',required=True,type=Path);p.add_argument('--tool-dir',type=Path);p.add_argument('--build-root',type=Path);p.add_argument('--language',choices=['c','cpp','both']);p.add_argument('--replay',type=Path);a=p.parse_args();root=a.project_root.resolve()
    if a.replay:need(a.tool_dir is None and a.build_root is None and a.language is None,'Read-only replay rejects generation options');print(json.dumps(replay(root,a.replay)));return
    need(a.tool_dir is not None,'Explicit pinned local LLVM required');tools={n:next(p.resolve() for p in(a.tool_dir/(n+'.exe'),a.tool_dir/n) if p.is_file()) for n in TOOLS};need(all(H(p)==TOOLS[n] for n,p in tools.items()),'Pinned tools')
    owner=root/MODEL/'build';base=a.build_root.resolve() if a.build_root else owner/('native-'+uuid.uuid4().hex);need(base.is_relative_to(owner) and base!=owner and not base.exists(),'Create-only owned build');base.mkdir(parents=True);results=[]
    for mode in ('c','cpp') if a.language in(None,'both') else(a.language,):
        folder=base/mode;folder.mkdir();tmp=folder/'compiler-temp';tmp.mkdir();env=dict(os.environ,TMP=str(tmp),TEMP=str(tmp));commands=[];before=pins(root,tools);resource=None
        for label,argv in recipes(root,folder,mode,tools):
            x=subprocess.run([str(v) for v in argv],cwd=folder,env=env,capture_output=True,timeout=120);log=folder/(label+'.log');log.write_bytes(x.stdout+x.stderr);commands.append(dict(label=label,argv=[str(v) for v in argv],exit=x.returncode,log=log.name,sha256=H(log),TMP=str(tmp),TEMP=str(tmp)));need(x.returncode==0,'Actual compiler failed: '+str(log))
            if resource is None:resource=Path(x.stdout.decode().strip())/'include/stdint.h';need(H(resource)==RESOURCE,'Pinned resource before compilation');before[str(resource)]=H(resource)
        need(before==pins(root,tools,resource),'Before/after source/tool/resource stability');r=dict(schema='TSL9-candidate-memory-native-v1',passed=True,mode=mode,commands=commands,source_pins=before);r['checks']=inspect(root,folder,r);r['artifacts']={p.relative_to(folder).as_posix():dict(bytes=p.stat().st_size,sha256=H(p)) for p in folder.rglob('*') if p.is_file()};receipt=folder/'verification.json';receipt.write_bytes((json.dumps(r,indent=2)+'\n').encode());results.append(replay(root,receipt))
    print(json.dumps(dict(passed=True,results=results,target_execution=False)))
if __name__=='__main__':main()
