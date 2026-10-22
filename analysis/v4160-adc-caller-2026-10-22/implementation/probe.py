#!/usr/bin/env python3
"""One complete caller-derived register bank; compile/static readback only."""
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
MODEL='experiments/tsl9-adc-caller-bank'
ADC='experiments/tsl9-adc-config'
OLD='apk-analysis/tsl9-v4160-resident-native-2026-10-22/implementation/probe.py'
REVIEW='apk-analysis/tsl9-v4160-adc-config-2026-10-22/source-review'
REVIEW_PIN='9cc7d0cd8a2d8150060556e9ade6baa11fc424d7c378ff694e63416358143624'
ENTRY='tsl9_adc_config_1892e'
GLOBALS={'ml_port_read8','ml_port_read32','ml_port_write32','tsl9_adc_config_io',ENTRY}
REGS=['zero','ra','sp','gp','tp','t0','t1','t2','s0','s1','a0','a1','a2','a3','a4','a5','a6','a7','s2','s3','s4','s5','s6','s7','s8','s9','s10','s11','t3','t4','t5','t6']
def H(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def need(v,m):
    if not v:raise ValueError(m)
def locate(root,name):
    p=root/name
    if p.is_file():return p
    if name.startswith('apk-analysis/tsl9-'):return root/('analysis/'+name[len('apk-analysis/tsl9-'):])
    return p
def prior(root):return runpy.run_path(str(locate(root,OLD)))
def review(root,name):return locate(root,REVIEW+'/'+name)
def bank(root):
    need(H(review(root,'seal.json'))==REVIEW_PIN,'Sealed original caller liveness')
    seal=json.loads(review(root,'seal.json').read_bytes())
    for name in ('actual-source-check.json','check.py'):need(H(review(root,name))==seal['members'][name],'Exact original liveness source')
    facts=json.loads(review(root,'actual-source-check.json').read_bytes())['facts']['post_config_register_liveness']
    need(facts['A0_through_A6_entry_clobbers_overwritten_for_this_caller'] and facts['original_A7_unread_and_preserved_to_normal_exit'] and facts['original_T0_T2_T3_T4_T5_T6_unread_and_preserved_to_normal_exit'] and facts['original_T1_exit_value']==15 and facts['any_new_T_clobber_requires_separate_exit_proof'],'Actual caller write-before-read and exit constraints')
    allowed=list(range(10,17));return dict(allowed=allowed,reserved=sorted(set(range(5,32))-set(allowed)),dedicated_separately_checked=[0,1,2,3,4],original_callee_own_written=[13,14,15],specific_caller_normal_dead_inputs=allowed,original_T1_normal_exit=15,full_original_callee_ABI_proved=False)
def recipes(root,folder,mode,tools):
    flags=prior(root)['flags'](mode)+['-ffixed-x'+str(n) for n in bank(root)['reserved']];source=root/MODEL/'src/caller_bank.c'
    return [('compiler-help',[tools['clang'],'--help']),('compiler-resource-dir',[tools['clang'],'-print-resource-dir']),('native-object',[tools['clang'],*flags,'-c','-MD','-MF',folder/'native.d','-MT','native.o',source,'-o',folder/'native.o']),('native-IR',[tools['clang'],*flags,'-S','-emit-llvm',source,'-o',folder/'native.ll']),('complete-static-disassembly',[tools['llvm-objdump'],'--mattr=+m,+a,+c,+zicsr,+zifencei','-d','-r',folder/'native.o'])]
def pins(root,tools,resource=None):
    paths=[Path(__file__).resolve(),Path(sys.executable).resolve(),root/MODEL/'src/caller_bank.c',locate(root,OLD),prior(root)['parser'](root),*tools.values(),*[root/ADC/'src'/n for n in ('native.c','adc_config.c','adc_config.h')],*[root/'experiments/tsl9-resident-memory-leaves/src'/n for n in ('memory_leaves.h','io.h')],*[review(root,n) for n in ('seal.json','check.py','actual-source-check.json')]]
    if resource:paths.append(resource)
    return {str(p):H(p) for p in paths}
def help_support(text,b):
    supported={int(n) for n in re.findall(r'-ffixed-x(\d+)\s+Reserve the x\d+ register \(AArch64/RISC-V only\)',text)};need(set(b['reserved'])<=supported,'Every fixed flag advertised for RISC-V before compile')
def inspect(root,folder,r):
    tools={n:Path(v) for n,v in r['tools'].items()};old=prior(root);need(all(H(p)==old['TOOLS'][n] for n,p in tools.items()),'Pinned local LLVM')
    expected=recipes(root,folder,r['mode'],tools);commands=r['commands'];need([(c['label'],c['argv']) for c in commands]==[(n,[str(v) for v in a]) for n,a in expected[:len(commands)]],'Exact one-bank recipes')
    for c in commands:need(c['log']==c['label']+'.log' and H(folder/c['log'])==c['log_sha256'] and c['TMP']==c['TEMP']==str(folder/'compiler-temp'),'Actual raw logs and temporary ownership')
    b=bank(root);need(r['register_bank']==b,'Source-derived single caller bank');help_support((folder/'compiler-help.log').read_text(),b)
    resource=Path((folder/'compiler-resource-dir.log').read_text().strip())/'include/stdint.h';need(H(resource)==old['RESOURCE'],'Actual compiler resource header');need(r['source_pins']==pins(root,tools,resource),'Exact stable source/helper/tools/resource identities')
    result=dict(register_bank=b,compiler_success=r['compiler_success'],full_original_callee_ABI_proved=False,specific_caller_normal_projection_proved=False,installed_provider_proved=False,placement_proved=False,target_execution=False,HOST_matrix_rerun=False,linked=False,BIN_exported=False)
    if not r['compiler_success']:
        need(commands[-1]['exit']!=0 and all(c['exit']==0 for c in commands[:-1]),'Retained genuine compiler failure');return dict(result,failure_label=commands[-1]['label'],failure_log=commands[-1]['log'])
    need(len(commands)==5 and all(c['exit']==0 for c in commands),'Five actual successful recipes')
    text=(folder/'native.d').read_text().replace('\\\n',' ');lhs,_,rhs=text.partition(':');deps={Path(re.sub(r'\\(.)',r'\1',p)).resolve() for p in re.findall(r'(?:\\.|[^\s])+',rhs)}
    need(lhs=='native.o' and deps=={root/MODEL/'src/caller_bank.c',*[root/ADC/'src'/n for n in ('native.c','adc_config.c','adc_config.h')],*[root/'experiments/tsl9-resident-memory-leaves/src'/n for n in ('memory_leaves.h','io.h')],resource},'Complete actual -MD closure')
    E=runpy.run_path(str(old['parser'](root)))['ELF'];e=E(folder/'native.o');need(e.kind==1 and e.flags==1,'RV32/RVC ET_REL')
    alloc=[s for s in e.sections if s['flags']&2 and s['size']];funcs=[f for f in e.symbols if f['info']&15==2 and f['size']];need({f['name'] for f in funcs if f['info']>>4==1}==GLOBALS,'All five genuine globals reported');need(all(s['type']==1 and s['flags']==6 for s in alloc),'Only code allocated')
    coverage={s['name']:0 for s in alloc};ins={s['name']:[] for s in alloc};current=None
    for line in (folder/'complete-static-disassembly.log').read_text().splitlines():
        m=re.match(r'Disassembly of section (.+):',line)
        if m:current=m[1];continue
        m=re.match(r'^\s*([0-9a-f]+):\s+((?:[0-9a-f]{2}\s+)+)\s*([^\s]+)\s*(.*)',line)
        if not m:continue
        at=int(m[1],16);raw=bytes.fromhex(m[2]);need(current in coverage and at==coverage[current] and len(raw) in(2,4) and raw==e.data(e.byname[current])[at:at+len(raw)] and m[3] not in ('<unknown>','.word','.2byte'),'Complete real contiguous disassembly');coverage[current]+=len(raw);ins[current].append(dict(offset=at,raw=raw.hex(),mnemonic=m[3],operands=m[4]))
    need(all(coverage[s['name']]==s['size'] for s in alloc),'No omitted/padded code tails')
    no_rd={'sb','sh','sw','sd','beq','bne','blt','bge','bltu','bgeu','beqz','bnez','blez','bgez','bltz','bgtz','ble','bgt','bleu','bgtu','j','jr','ret','fence','fence.i','unimp','nop'};functions=[]
    for f in funcs:
        sec=e.sections[f['index']]['name'];rows=ins[sec];written=set()
        for i in rows:
            if i['mnemonic'] in no_rd:continue
            first=i['operands'].split(',')[0].strip()
            if first in REGS:
                if first!='zero':written.add(REGS.index(first))
            elif i['mnemonic'] in ('call','tail'):written.add(1)
            else:need(False,'Unclassified destination '+str(i))
        selected=f['name']==ENTRY
        functions.append(dict(name=f['name'],global_FUNC=f['info']>>4==1,selected=selected,bytes=f['size'],instructions=len(rows),code_sha256=hashlib.sha256(e.function_bytes(f)).hexdigest(),section=sec,own_written_GPRs=sorted(written),fixed_bank_writes=sorted(written&set(b['reserved'])),dedicated_writes=sorted(written&{1,2,3,4}),stack_access=any('(sp)' in i['operands'] for i in rows),calls=any(i['mnemonic'] in ('call','tail','jal','jalr') for i in rows),extra_written_vs_original_callee=sorted(written-{13,14,15}) if selected else None))
    ir=(folder/'native.ll').read_text();signature=re.search(r'define[^@\n]* i32 @'+ENTRY+r'\(([^)]*)\)',ir);need(signature is not None and len(signature[1].split(','))==2 and 'ptr' not in signature[1],'Two-u32 public entry without context/sret');body=ir[signature.start():ir.index('\n}',signature.start())];volatile=re.findall(r'(load|store) volatile i(8|32)',body);need(volatile.count(('load','32'))==10 and volatile.count(('load','8'))==1 and volatile.count(('store','32'))==3 and len(volatile)==14,'Fourteen real ordered volatile effects')
    return dict(result,functions=functions,unused_genuine_globals=[f['name'] for f in functions if not f['selected']],allocated_bytes=sum(s['size'] for s in alloc),instructions=sum(len(v) for v in ins.values()),UND=sorted({s['name'] for s in e.symbols if s['index']==0 and s['name']}),RELA=len(e.relocations),relocations=e.relocations,global_ABS=[s['name'] for s in e.symbols if s['index']==0xfff1 and s['info']>>4],public_volatile_effects=[list(v) for v in volatile],actual_MD_inputs=[dict(path=str(p),sha256=H(p)) for p in sorted(deps)])
def replay(root,receipt):
    receipt=receipt.resolve();folder=receipt.parent;r=json.loads(receipt.read_bytes());need(r['artifacts']=={p.relative_to(folder).as_posix():dict(bytes=p.stat().st_size,sha256=H(p)) for p in folder.rglob('*') if p.is_file() and p!=receipt},'Complete actual artifact inventory');checked=inspect(root,folder,r);need(checked==r['checks'],'Exact actual read-only native replay');return dict(passed=True,receipt=str(receipt),sha256=H(receipt),mode=r['mode'],actual_native_artifacts_read=True,**checked)
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--project-root',required=True,type=Path);p.add_argument('--tool-dir',type=Path);p.add_argument('--build-root',type=Path);p.add_argument('--replay',type=Path);a=p.parse_args();root=a.project_root.resolve()
    if a.replay:need(a.tool_dir is None and a.build_root is None,'Read-only replay rejects build flags');print(json.dumps(replay(root,a.replay)));return
    need(a.tool_dir is not None,'Explicit pinned local LLVM');old=prior(root);tools={n:next(p.resolve() for p in(a.tool_dir/(n+'.exe'),a.tool_dir/n) if p.is_file()) for n in old['TOOLS']};need(all(H(p)==old['TOOLS'][n] for n,p in tools.items()),'Pinned LLVM');bank(root)
    owner=root/MODEL/'build';base=a.build_root.resolve() if a.build_root else owner/('caller-'+uuid.uuid4().hex);need(base.is_relative_to(owner) and base!=owner and not base.exists(),'Create-only owned build');base.mkdir(parents=True);results=[]
    for mode in ('c','cpp'):
        folder=base/mode;folder.mkdir();tmp=folder/'compiler-temp';tmp.mkdir();env=dict(os.environ,TMP=str(tmp),TEMP=str(tmp));before=pins(root,tools);resource=None;commands=[];success=True
        for label,argv in recipes(root,folder,mode,tools):
            x=subprocess.run([str(v) for v in argv],cwd=folder,env=env,capture_output=True,timeout=120);log=folder/(label+'.log');log.write_bytes(x.stdout+x.stderr);commands.append(dict(label=label,argv=[str(v) for v in argv],exit=x.returncode,log=log.name,log_sha256=H(log),TMP=str(tmp),TEMP=str(tmp)))
            if label=='compiler-help':help_support(x.stdout.decode(),bank(root))
            if label=='compiler-resource-dir':resource=Path(x.stdout.decode().strip())/'include/stdint.h';need(H(resource)==old['RESOURCE'],'Pinned resource before compile');before[str(resource)]=H(resource)
            if x.returncode!=0:success=False;break
        need(before==pins(root,tools,resource),'Stable source/tool/resource before/after');r=dict(schema='TSL9-ADC-caller-bank-v1',mode=mode,tools={n:str(v) for n,v in tools.items()},register_bank=bank(root),compiler_success=success,source_pins=before,commands=commands);r['checks']=inspect(root,folder,r);r['artifacts']={p.relative_to(folder).as_posix():dict(bytes=p.stat().st_size,sha256=H(p)) for p in folder.rglob('*') if p.is_file()};receipt=folder/'verification.json';receipt.write_bytes((json.dumps(r,indent=2)+'\n').encode());results.append(replay(root,receipt))
    print(json.dumps(dict(passed=True,results=results,target_execution=False,HOST_matrix_rerun=False)))
if __name__=='__main__':main()
