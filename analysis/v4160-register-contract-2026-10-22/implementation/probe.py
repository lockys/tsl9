#!/usr/bin/env python3
"""Compile one fixed register bank per real leaf; inspect, never execute."""
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
MODEL='experiments/tsl9-resident-register-contract'
OLD='experiments/tsl9-resident-memory-native'
CONTRACT='apk-analysis/tsl9-v4160-resident-native-2026-10-22/abi-review/source-contracts.json'
PROBE='apk-analysis/tsl9-v4160-resident-native-2026-10-22/implementation/probe.py'
ENTRIES={'compare':'tsl9_native_compare_200004bc','fill':'tsl9_native_fill_2000039c','copy':'tsl9_native_copy_20000332'}
REGS=['zero','ra','sp','gp','tp','t0','t1','t2','s0','s1','a0','a1','a2','a3','a4','a5','a6','a7','s2','s3','s4','s5','s6','s7','s8','s9','s10','s11','t3','t4','t5','t6']
def H(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def need(v,m):
    if not v:raise ValueError(m)
def locate(root,name):
    p=root/name
    if p.is_file():return p
    if name.startswith('apk-analysis/tsl9-'):return root/('analysis/'+name[len('apk-analysis/tsl9-'):])
    return p
def prior(root):return runpy.run_path(str(locate(root,PROBE)))
def bank(root,leaf):
    c=json.loads(locate(root,CONTRACT).read_bytes())['leaves'][leaf]
    allowed=sorted(set(c['own_written_GPRs_excluding_zero'])|{10,11,12})
    return dict(original_written=c['own_written_GPRs_excluding_zero'],explicit_inputs=[10,11,12],allowed=allowed,reserved=sorted(set(range(5,32))-set(allowed)),dedicated=[0,1,2,3,4])
def recipes(root,folder,mode,leaf,tools):
    flags=prior(root)['flags'](mode)+['-ffixed-x'+str(n) for n in bank(root,leaf)['reserved']]
    source=root/MODEL/'src/register_contract.c'
    return [('compiler-help',[tools['clang'],'--help']),('compiler-resource-dir',[tools['clang'],'-print-resource-dir']),('native-object',[tools['clang'],*flags,'-c','-MD','-MF',folder/'native.d','-MT','native.o',source,'-o',folder/'native.o']),('native-IR',[tools['clang'],*flags,'-S','-emit-llvm',source,'-o',folder/'native.ll']),('complete-static-disassembly',[tools['llvm-objdump'],'--mattr=+m,+a,+c,+zicsr,+zifencei','-d','-r',folder/'native.o'])]
def pins(root,tools,resource=None):
    paths=[root/MODEL/'src/register_contract.c',root/OLD/'src/native.c',root/OLD/'src/native.h',locate(root,CONTRACT),locate(root,PROBE),Path(__file__).resolve(),prior(root)['parser'](root),Path(sys.executable).resolve(),*tools.values()]
    paths += [root/'experiments/tsl9-resident-memory-leaves/src'/n for n in ('memory_leaves.c','memory_leaves.h','io.h')]
    if resource:paths.append(resource)
    return {str(p):H(p) for p in paths}
def inspect(root,folder,r):
    old=prior(root);commands=r['commands'];tools={'clang':Path(commands[0]['argv'][0]),'llvm-objdump':Path(r['tools']['llvm-objdump'])}
    need(all(H(p)==old['TOOLS'][n] for n,p in tools.items()),'Pinned LLVM binaries')
    expected=recipes(root,folder,r['mode'],r['leaf'],tools)
    need([(c['label'],c['argv']) for c in commands]==[(n,[str(v) for v in a]) for n,a in expected[:len(commands)]],'Exact single bank recipe')
    for c in commands:need(c['log']==c['label']+'.log' and H(folder/c['log'])==c['sha256'] and c['TMP']==c['TEMP']==str(folder/'compiler-temp'),'Actual logs and temporary directory')
    b=bank(root,r['leaf']);need(r['register_bank']==b,'Source-derived bank')
    helptext=(folder/'compiler-help.log').read_text();supported={int(n) for n in re.findall(r'-ffixed-x(\d+)\s+Reserve the x\d+ register \(AArch64/RISC-V only\)',helptext)}
    need(set(b['reserved'])<=supported,'Every reserved flag advertised for RISC-V')
    resource=Path((folder/'compiler-resource-dir.log').read_text().strip())/'include/stdint.h';need(H(resource)==old['RESOURCE'],'Pinned compiler resource')
    need(r['source_pins']==pins(root,tools,resource),'Stable source/tool/header identities')
    base=dict(register_bank=b,selected_entry=ENTRIES[r['leaf']],compiler_success=r['compiler_success'],native_candidate_ABI_proved=False,installed_provider_proved=False,linked=False,BIN_exported=False,target_execution=False)
    if not r['compiler_success']:
        need(len(commands)>=3 and commands[-1]['exit']!=0 and all(c['exit']==0 for c in commands[:-1]),'Actual compiler failure retained')
        return dict(base,failure_label=commands[-1]['label'],failure_log=commands[-1]['log'])
    need(len(commands)==5 and all(c['exit']==0 for c in commands),'Five successful actual recipes')
    src=root/MODEL/'src';text=(folder/'native.d').read_text().replace('\\\n',' ');lhs,_,rhs=text.partition(':');deps={Path(re.sub(r'\\(.)',r'\1',p)).resolve() for p in re.findall(r'(?:\\.|[^\s])+',rhs)}
    need(lhs=='native.o' and deps=={src/'register_contract.c',root/OLD/'src/native.c',root/OLD/'src/native.h',*[root/'experiments/tsl9-resident-memory-leaves/src'/n for n in ('memory_leaves.c','memory_leaves.h','io.h')],resource},'Exact actual MD input closure')
    E=runpy.run_path(str(old['parser'](root)))['ELF'];e=E(folder/'native.o');need(e.kind==1 and e.flags==1,'RV32/RVC ET_REL')
    alloc=[s for s in e.sections if s['flags']&2 and s['size']];funcs=[f for f in e.symbols if f['info']&15==2 and f['size']]
    need({f['name'] for f in funcs if f['info']>>4==1}==old['PUBLIC']|old['ALGORITHMS']|old['PORTS'],'All eleven genuine global functions accounted')
    need(all(s['type']==1 and s['flags']==6 for s in alloc),'Code-only allocated sections')
    coverage={s['name']:0 for s in alloc};instructions={s['name']:[] for s in alloc};current=None
    for line in (folder/'complete-static-disassembly.log').read_text().splitlines():
        m=re.match(r'Disassembly of section (.+):',line)
        if m:current=m[1];continue
        m=re.match(r'^\s*([0-9a-f]+):\s+((?:[0-9a-f]{2}\s+)+)\s*([^\s]+)\s*(.*)',line)
        if not m:continue
        at=int(m[1],16);raw=bytes.fromhex(m[2]);need(current in coverage and at==coverage[current] and len(raw) in(2,4) and raw==e.data(e.byname[current])[at:at+len(raw)] and m[3] not in ('<unknown>','.word','.2byte'),'Complete actual instruction coverage')
        coverage[current]+=len(raw);instructions[current].append(dict(offset=at,bytes=raw.hex(),mnemonic=m[3],operands=m[4]))
    need(all(coverage[s['name']]==s['size'] for s in alloc),'No unparsed code tail')
    results=[]
    no_rd={'sb','sh','sw','sd','beq','bne','blt','bge','bltu','bgeu','beqz','bnez','blez','bgez','bltz','bgtz','ble','bgt','bleu','bgtu','j','jr','ret','fence','fence.i','unimp','nop'}
    for f in funcs:
        sec=e.sections[f['index']]['name'];ins=instructions[sec];written=[]
        for i in ins:
            if i['mnemonic'] in no_rd:continue
            first=i['operands'].split(',')[0].strip()
            if first in REGS and first!='zero':written.append(REGS.index(first))
            elif i['mnemonic'] in ('call','tail'):written.append(1)
            else:need(False,'Unclassified destination: '+str(i))
        selected=f['name']==ENTRIES[r['leaf']]
        results.append(dict(name=f['name'],bytes=f['size'],info=f['info'],section=sec,instructions=len(ins),code_sha256=hashlib.sha256(e.function_bytes(f)).hexdigest(),own_written_GPRs=sorted(set(written)),stack_or_saved_register_written=sorted(set(written)&{1,2,8,9,*range(18,28)}),stack_memory=any(re.search(r'\(sp\)',i['operands']) for i in ins),calls=any(i['mnemonic'] in ('call','tail','jal','jalr') for i in ins),selected=selected,extra_written_vs_original=sorted(set(written)-set(b['original_written'])) if selected else None))
    need(sum(f['selected'] for f in results)==1,'One actual selected entry')
    ir=(folder/'native.ll').read_text();need(all(x in ir for x in ('load volatile i8','load volatile i32','store volatile i8','store volatile i32','fence.i')),'Real volatile ports and fence in IR')
    return dict(base,functions=results,unused_global_functions=[f['name'] for f in results if not f['selected']],allocated_bytes=sum(s['size'] for s in alloc),instructions=sum(len(v) for v in instructions.values()),undefined_symbols=sorted({s['name'] for s in e.symbols if s['index']==0 and s['name']}),RELA=len(e.relocations),relocations=e.relocations,global_absolute_symbols=[s['name'] for s in e.symbols if s['index']==0xfff1 and s['info']>>4],actual_MD_inputs=[dict(path=str(p),sha256=H(p)) for p in sorted(deps)])
def replay(root,receipt):
    receipt=receipt.resolve();folder=receipt.parent;r=json.loads(receipt.read_bytes())
    need(r['artifacts']=={p.relative_to(folder).as_posix():dict(bytes=p.stat().st_size,sha256=H(p)) for p in folder.rglob('*') if p.is_file() and p!=receipt},'Complete actual artifact inventory')
    checks=inspect(root,folder,r);need(checks==r['checks'],'Read-only actual artifact replay')
    return dict(receipt=str(receipt),sha256=H(receipt),passed=True,**checks)
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--project-root',required=True,type=Path);p.add_argument('--tool-dir',type=Path);p.add_argument('--build-root',type=Path);p.add_argument('--replay',type=Path);a=p.parse_args();root=a.project_root.resolve()
    if a.replay:
        need(a.tool_dir is None and a.build_root is None,'Replay is read-only');print(json.dumps(replay(root,a.replay)));return
    need(a.tool_dir is not None,'Explicit local LLVM required');tools={n:next(p.resolve() for p in(a.tool_dir/(n+'.exe'),a.tool_dir/n) if p.is_file()) for n in prior(root)['TOOLS']};need(all(H(p)==prior(root)['TOOLS'][n] for n,p in tools.items()),'Pinned tools')
    owner=root/MODEL/'build';base=a.build_root.resolve() if a.build_root else owner/('register-'+uuid.uuid4().hex);need(base.is_relative_to(owner) and base!=owner and not base.exists(),'Create-only owned root');base.mkdir(parents=True);results=[]
    for leaf in ENTRIES:
        for mode in ('c','cpp'):
            folder=base/leaf/mode;folder.mkdir(parents=True);tmp=folder/'compiler-temp';tmp.mkdir();env=dict(os.environ,TMP=str(tmp),TEMP=str(tmp));commands=[];before=pins(root,tools);resource=None;success=True
            for label,argv in recipes(root,folder,mode,leaf,tools):
                x=subprocess.run([str(v) for v in argv],cwd=folder,env=env,capture_output=True,timeout=120);log=folder/(label+'.log');log.write_bytes(x.stdout+x.stderr);commands.append(dict(label=label,argv=[str(v) for v in argv],exit=x.returncode,log=log.name,sha256=H(log),TMP=str(tmp),TEMP=str(tmp)))
                if label=='compiler-help':
                    supported={int(n) for n in re.findall(r'-ffixed-x(\d+)\s+Reserve the x\d+ register \(AArch64/RISC-V only\)',x.stdout.decode())}
                    need(set(bank(root,leaf)['reserved'])<=supported,'All fixed flags supported before compilation')
                if label=='compiler-resource-dir':resource=Path(x.stdout.decode().strip())/'include/stdint.h';need(H(resource)==prior(root)['RESOURCE'],'Pinned resource before compile');before[str(resource)]=H(resource)
                if x.returncode!=0:success=False;break
            need(before==pins(root,tools,resource),'Before/after stability');r=dict(schema='TSL9-resident-register-contract-v1',mode=mode,leaf=leaf,tools={k:str(v) for k,v in tools.items()},register_bank=bank(root,leaf),commands=commands,source_pins=before,compiler_success=success);r['checks']=inspect(root,folder,r);r['artifacts']={p.relative_to(folder).as_posix():dict(bytes=p.stat().st_size,sha256=H(p)) for p in folder.rglob('*') if p.is_file()};receipt=folder/'verification.json';receipt.write_bytes((json.dumps(r,indent=2)+'\n').encode());results.append(replay(root,receipt))
    print(json.dumps(dict(passed=True,results=[dict(receipt=r['receipt'],sha256=r['sha256'],leaf=next(k for k,v in ENTRIES.items() if v==r['selected_entry']),compiler_success=r['compiler_success'],selected=[f for f in r.get('functions',[]) if f['selected']],allocated_bytes=r.get('allocated_bytes'),instructions=r.get('instructions')) for r in results],target_execution=False)))
if __name__=='__main__':main()
