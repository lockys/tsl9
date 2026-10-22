#!/usr/bin/env python3
"""Compile genuine C helpers/write/timer, then static-read every actual function."""
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
MODEL='experiments/tsl9-nv-write-callback'
FLASH='experiments/tsl9-v4160-flash-entry-order/src'
OLD='apk-analysis/tsl9-v4160-resident-native-2026-10-22/implementation/probe.py'
CLASSIFIER='apk-analysis/tsl9-function-hardware/fifty-seventh-round/independent-provider-witness/audit_gp_elf.py'
CLASSIFIER_IMPORT='apk-analysis/tsl9-function-hardware/fifty-fifth-round/independent-service-events-contract/elf_service_events.py'
BINDING='apk-analysis/tsl9-v4160-callback-frontiers-2026-10-22/binding-review'
BINDING_PIN='16d33830cd05b0fb49b4ecf576b1657cf4c6a5bedabd4ccc63dc73ef3ef1f551'
WRITE='tsl9_nv_write_callback_197be'
TIMER='tsl9_delay_19764'
CALLS=['tsl9_flash_unlock_18e98','tsl9_flash_erase_18ec4','tsl9_flash_program_18ef2','tsl9_flash_lock_18eb6',TIMER]
GLOBALS=set(CALLS)|{WRITE,'tsl9_flash_status_18e90','tsl9_flash_quarter_9c0a'}
def H(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def need(v,m):
    if not v:raise ValueError(m)
def locate(root,name):
    p=root/name
    if p.is_file():return p
    if name.startswith('apk-analysis/tsl9-'):return root/('analysis/'+name[len('apk-analysis/tsl9-'):])
    return p
def prior(root):return runpy.run_path(str(locate(root,OLD)))
def binding(root):
    need(H(locate(root,BINDING+'/seal.json'))==BINDING_PIN,'Sealed original write/timer bindings')
def recipes(root,folder,mode,tools):
    flags=prior(root)['flags'](mode);source=root/MODEL/'src/nv_write_callback.c'
    return [('compiler-resource-dir',[tools['clang'],'-print-resource-dir']),('native-object',[tools['clang'],*flags,'-c','-MD','-MF',folder/'native.d','-MT','native.o',source,'-o',folder/'native.o']),('native-IR',[tools['clang'],*flags,'-S','-emit-llvm',source,'-o',folder/'native.ll']),('complete-static-disassembly',[tools['llvm-objdump'],'--mattr=+m,+a,+c,+zicsr,+zifencei','-d','-r',folder/'native.o'])]
def pins(root,tools,resource=None):
    case=Path(__file__).resolve().parent;paths=[Path(__file__).resolve(),Path(sys.executable).resolve(),locate(root,OLD),prior(root)['parser'](root),locate(root,CLASSIFIER),locate(root,CLASSIFIER_IMPORT),*[locate(root,BINDING+'/'+n) for n in ('seal.json','ledger.json','check.py')],*[root/FLASH/n for n in ('flash_native.c','flash_native.h','native_io.h')],root/MODEL/'src/nv_write_callback.c',root/MODEL/'src/nv_write_callback.h',case/'source-proof.json',case/'original-write-197be.bin',case/'original-timer-19764.bin',*tools.values()]
    if resource:paths.append(resource)
    return {str(p):H(p) for p in paths}
def body(ir,name):
    m=re.search(r'define[^@\n]* i32 @'+name+r'\(([^)]*)\)',ir);need(m is not None,'Actual public IR '+name);return m,ir[m.start():ir.index('\n}',m.start())]
def inspect(root,folder,r):
    binding(root);old=prior(root);tools={n:Path(v) for n,v in r['tools'].items()};need(all(H(p)==old['TOOLS'][n] for n,p in tools.items()),'Pinned LLVM')
    need([(c['label'],c['argv']) for c in r['commands']]==[(n,[str(v) for v in a]) for n,a in recipes(root,folder,r['mode'],tools)],'Exact ordinary compiler recipe')
    for c in r['commands']:need(c['exit']==0 and c['log']==c['label']+'.log' and H(folder/c['log'])==c['log_sha256'] and c['TMP']==c['TEMP']==str(folder/'compiler-temp'),'Actual raw logs/temporary ownership')
    resource=Path((folder/'compiler-resource-dir.log').read_text().strip())/'include/stdint.h';need(H(resource)==old['RESOURCE'],'Actual resource stdint.h');need(r['source_pins']==pins(root,tools,resource),'Complete stable direct inputs and decoder imports')
    text=(folder/'native.d').read_text().replace('\\\n',' ');lhs,_,rhs=text.partition(':');deps={Path(re.sub(r'\\(.)',r'\1',p)).resolve() for p in re.findall(r'(?:\\.|[^\s])+',rhs)};src=root/MODEL/'src';need(lhs=='native.o' and deps=={src/'nv_write_callback.c',src/'nv_write_callback.h',*[root/FLASH/n for n in ('flash_native.c','flash_native.h','native_io.h')],resource},'Complete actual MD closure')
    E=runpy.run_path(str(old['parser'](root)))['ELF'];e=E(folder/'native.o');need(e.kind==1 and e.flags==1,'RV32/RVC ET_REL');alloc=[s for s in e.sections if s['flags']&2 and s['size']];funcs=[f for f in e.symbols if f['info']&15==2 and f['size']];need({f['name'] for f in funcs if f['info']>>4==1}==GLOBALS,'Eight genuine C global functions including unused status/quarter');need(all(s['type']==1 and s['flags']==6 for s in alloc),'All allocations genuine code')
    classifier=runpy.run_path(str(locate(root,CLASSIFIER)));coverage={s['name']:0 for s in alloc};instructions={s['name']:[] for s in alloc};current=None
    for line in (folder/'complete-static-disassembly.log').read_text().splitlines():
        m=re.match(r'Disassembly of section (.+):',line)
        if m:current=m[1];continue
        m=re.match(r'^\s*([0-9a-f]+):\s+((?:[0-9a-f]{2}\s+)+)\s*([^\s]+)\s*(.*)',line)
        if not m:continue
        at=int(m[1],16);raw=bytes.fromhex(m[2]);need(current in coverage and at==coverage[current] and len(raw) in (2,4) and raw==e.data(e.byname[current])[at:at+len(raw)] and m[3] not in ('<unknown>','.word','.2byte'),'Complete contiguous real disassembly');coverage[current]+=len(raw);rd,kind,known=classifier['decode16' if len(raw)==2 else 'decode32'](int.from_bytes(raw,'little'));need(known,'Finite RV32IMAC/CSR integer destination recognized');instructions[current].append(dict(offset=at,raw=raw.hex(),rd=rd,kind=kind,LLVM_mnemonic=m[3],LLVM_operands=m[4]))
    need(all(coverage[s['name']]==s['size'] for s in alloc),'No omitted machine code');out=[]
    for f in funcs:
        sec=e.sections[f['index']]['name'];rows=instructions[sec];written={i['rd'] for i in rows if i['rd'] not in (None,0)}
        out.append(dict(name=f['name'],global_FUNC=f['info']>>4==1,bytes=f['size'],instructions=len(rows),code_sha256=hashlib.sha256(e.function_bytes(f)).hexdigest(),section=sec,own_written_GPRs=sorted(written),stack_accesses=[i for i in rows if '(sp)' in i['LLVM_operands']],stack_adjustments=[i for i in rows if i['LLVM_mnemonic']=='addi' and i['LLVM_operands'].startswith('sp, sp,')],GP_read_rows=[i for i in rows if re.search(r'\bgp\b',i['LLVM_operands'])],raw_rows=rows))
    ir=(folder/'native.ll').read_text();wsig,wbody=body(ir,WRITE);tsig,tbody=body(ir,TIMER);need(len(wsig[1].split(','))==3 and len(tsig[1].split(','))==1 and 'ptr' not in wsig[1]+tsig[1],'Public scalar surfaces without context/sret')
    call_names=re.findall(r'\bcall(?: noundef)? i32 @([A-Za-z0-9_]+)\(',wbody);need(call_names==CALLS and 'ret i32 0' in wbody,'Five real C calls in exact original order and normal zero result')
    need(tbody.count('load volatile i32')==5 and tbody.count('load volatile i8')==1 and tbody.count('store volatile i32')==6 and 'mv $0, gp' in tbody,'Timer twelve static volatile sites and genuine live-GP read')
    return dict(functions=out,unused_genuine_global_functions=['tsl9_flash_status_18e90','tsl9_flash_quarter_9c0a'],allocated_bytes=sum(s['size'] for s in alloc),instructions=sum(len(v) for v in instructions.values()),UND=sorted({s['name'] for s in e.symbols if s['index']==0 and s['name']}),RELA=len(e.relocations),relocations=e.relocations,global_ABS=[s['name'] for s in e.symbols if s['index']==0xfff1 and s['info']>>4],actual_write_IR=wbody,actual_timer_IR=tbody,actual_write_call_order=call_names,actual_MD_inputs=[dict(path=str(p),sha256=H(p)) for p in sorted(deps)],real_helper_definitions_retained=True,HOST_tests_run=False,native_execution=False,ISA_emulation=False,linked=False,BIN_exported=False,full_original_register_ABI_proved=False,installed_provider_proved=False,placement_proved=False)
def replay(root,receipt):
    receipt=receipt.resolve();folder=receipt.parent;r=json.loads(receipt.read_bytes());need(r['artifacts']=={p.relative_to(folder).as_posix():dict(bytes=p.stat().st_size,sha256=H(p)) for p in folder.rglob('*') if p.is_file() and p!=receipt},'Complete actual artifact inventory');checked=inspect(root,folder,r);need(checked==r['checks'],'Exact actual static replay');return dict(passed=True,receipt=str(receipt),sha256=H(receipt),mode=r['mode'],actual_artifacts_read=True,**checked)
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--project-root',required=True,type=Path);p.add_argument('--tool-dir',type=Path);p.add_argument('--build-root',type=Path);p.add_argument('--replay',type=Path);a=p.parse_args();root=a.project_root.resolve()
    if a.replay:need(a.tool_dir is None and a.build_root is None,'Replay rejects compile options');print(json.dumps(replay(root,a.replay)));return
    need(a.tool_dir is not None,'Explicit pinned local LLVM');old=prior(root);tools={n:next(p.resolve() for p in (a.tool_dir/(n+'.exe'),a.tool_dir/n) if p.is_file()) for n in old['TOOLS']};need(all(H(p)==old['TOOLS'][n] for n,p in tools.items()),'Pinned LLVM');binding(root);owner=root/MODEL/'build';base=a.build_root.resolve() if a.build_root else owner/('write-'+uuid.uuid4().hex);need(base.is_relative_to(owner) and base!=owner and not base.exists(),'Create-only owned build');base.mkdir(parents=True);results=[]
    for mode in ('c','cpp'):
        folder=base/mode;folder.mkdir();tmp=folder/'compiler-temp';tmp.mkdir();env=dict(os.environ,TMP=str(tmp),TEMP=str(tmp));before=pins(root,tools);resource=None;commands=[]
        for label,argv in recipes(root,folder,mode,tools):
            x=subprocess.run([str(v) for v in argv],cwd=folder,env=env,capture_output=True,timeout=120);log=folder/(label+'.log');log.write_bytes(x.stdout+x.stderr);commands.append(dict(label=label,argv=[str(v) for v in argv],exit=x.returncode,log=log.name,log_sha256=H(log),TMP=str(tmp),TEMP=str(tmp)));need(x.returncode==0,'Actual compiler failure '+str(log))
            if resource is None:resource=Path(x.stdout.decode().strip())/'include/stdint.h';need(H(resource)==old['RESOURCE'],'Pinned resource before compile');before[str(resource)]=H(resource)
        need(before==pins(root,tools,resource),'Before/after actual input stability');r=dict(schema='TSL9-real-NV-write-timer-C-v1',mode=mode,tools={n:str(v) for n,v in tools.items()},source_pins=before,commands=commands);r['checks']=inspect(root,folder,r);r['artifacts']={p.relative_to(folder).as_posix():dict(bytes=p.stat().st_size,sha256=H(p)) for p in folder.rglob('*') if p.is_file()};receipt=folder/'verification.json';receipt.write_bytes((json.dumps(r,indent=2)+'\n').encode());checked=replay(root,receipt);results.append(dict(mode=mode,receipt=str(receipt),sha256=H(receipt),functions=[{k:f[k] for k in ('name','bytes','instructions','code_sha256','own_written_GPRs')} for f in checked['functions']],allocated_bytes=checked['allocated_bytes'],instructions=checked['instructions'],UND=checked['UND'],RELA=checked['RELA']))
    print(json.dumps(dict(passed=True,results=results,HOST_tests_run=False,native_execution=False)))
if __name__=='__main__':main()
