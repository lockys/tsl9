#!/usr/bin/env python3
"""Compile real NV-read callback; finite static native readback, no execution."""
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
MODEL='experiments/tsl9-nv-read-callback'
OLD='apk-analysis/tsl9-v4160-resident-native-2026-10-22/implementation/probe.py'
DECODER='apk-analysis/tsl9-v4160-resident-memory-2026-10-22/continuation-review/check.py'
COPY='apk-analysis/tsl9-v4160-ota-handler-compact-2026-10-22/callee-review'
COPY_PIN='5b915632290d82c30545fa9ec517fc96bb67d706abf71f592e53354c3a622a8c'
ENTRY='tsl9_nv_read_callback_1979a'
def H(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def need(v,m):
    if not v:raise ValueError(m)
def locate(root,name):
    p=root/name
    if p.is_file():return p
    if name.startswith('apk-analysis/tsl9-'):return root/('analysis/'+name[len('apk-analysis/tsl9-'):])
    return p
def prior(root):return runpy.run_path(str(locate(root,OLD)))
def decoder(root):return runpy.run_path(str(locate(root,DECODER)))['decoder'](root)
def projection(root):
    seal=locate(root,COPY+'/seal.json');need(H(seal)==COPY_PIN,'Pinned conditional original copy proof')
    return dict(call_arguments=['entryA2 destination','entryA0 source','uint32(entryA1 words<<2)'],slot=0x4004c,fresh_slot_before_call=True,normal_callback_A0=0,callee_result_ignored=True,original_C_prototype_recovered=False,full_callee_ABI_proved=False,slot_target_identity_installed_proved=False)
def recipes(root,folder,mode,tools):
    source=root/MODEL/'src/nv_read_callback.c';flags=prior(root)['flags'](mode)
    return [('compiler-resource-dir',[tools['clang'],'-print-resource-dir']),('native-object',[tools['clang'],*flags,'-c','-MD','-MF',folder/'native.d','-MT','native.o',source,'-o',folder/'native.o']),('native-IR',[tools['clang'],*flags,'-S','-emit-llvm',source,'-o',folder/'native.ll']),('complete-static-disassembly',[tools['llvm-objdump'],'--mattr=+m,+a,+c,+zicsr,+zifencei','-d','-r',folder/'native.o'])]
def pins(root,tools,resource=None):
    case=Path(__file__).resolve().parent;paths=[Path(__file__).resolve(),Path(sys.executable).resolve(),locate(root,OLD),locate(root,DECODER),prior(root)['parser'](root),root/MODEL/'src/nv_read_callback.c',root/MODEL/'src/nv_read_callback.h',case/'source-proof.json',case/'original-1979a-197b8.bin',locate(root,COPY+'/seal.json'),locate(root,COPY+'/copy-instructions.json'),*tools.values()]
    if resource:paths.append(resource)
    return {str(p):H(p) for p in paths}
def inspect(root,folder,r):
    need(r['mode'] in ('c','cpp'),'C11/C++17');tools={n:Path(v) for n,v in r['tools'].items()};old=prior(root);need(all(H(p)==old['TOOLS'][n] for n,p in tools.items()),'Pinned local LLVM')
    need([(c['label'],c['argv']) for c in r['commands']]==[(n,[str(v) for v in a]) for n,a in recipes(root,folder,r['mode'],tools)],'Exact one ordinary-C recipe')
    for c in r['commands']:need(c['exit']==0 and c['log']==c['label']+'.log' and H(folder/c['log'])==c['log_sha256'] and c['TMP']==c['TEMP']==str(folder/'compiler-temp'),'Actual logs and owned temporary directory')
    resource=Path((folder/'compiler-resource-dir.log').read_text().strip())/'include/stdint.h';need(H(resource)==old['RESOURCE'],'Actual compiler resource header');need(r['source_pins']==pins(root,tools,resource),'Stable full source/tool/resource closure');need(r['conditional_projection']==projection(root),'Explicit conditional call projection')
    text=(folder/'native.d').read_text().replace('\\\n',' ');lhs,_,rhs=text.partition(':');deps={Path(re.sub(r'\\(.)',r'\1',p)).resolve() for p in re.findall(r'(?:\\.|[^\s])+',rhs)};src=root/MODEL/'src';need(lhs=='native.o' and deps=={src/'nv_read_callback.c',src/'nv_read_callback.h',resource},'Exact actual MD closure')
    E=runpy.run_path(str(old['parser'](root)))['ELF'];e=E(folder/'native.o');need(e.kind==1 and e.flags==1,'RV32/RVC ET_REL');alloc=[s for s in e.sections if s['flags']&2 and s['size']];funcs=[f for f in e.symbols if f['info']&15==2 and f['size']];need({f['name'] for f in funcs if f['info']>>4==1}=={ENTRY},'All actual global functions');need(all(s['type']==1 and s['flags']==6 for s in alloc),'Only genuine code allocated')
    coverage={s['name']:0 for s in alloc};instructions={s['name']:[] for s in alloc};current=None;decode=decoder(root)
    for line in (folder/'complete-static-disassembly.log').read_text().splitlines():
        m=re.match(r'Disassembly of section (.+):',line)
        if m:current=m[1];continue
        m=re.match(r'^\s*([0-9a-f]+):\s+((?:[0-9a-f]{2}\s+)+)\s*([^\s]+)\s*(.*)',line)
        if not m:continue
        at=int(m[1],16);raw=bytes.fromhex(m[2]);need(current in coverage and at==coverage[current] and len(raw) in (2,4) and raw==e.data(e.byname[current])[at:at+len(raw)] and m[3] not in ('<unknown>','.word','.2byte'),'Complete actual raw LLVM disassembly');coverage[current]+=len(raw);fields=decode(raw,at);need(fields['bytes']==len(raw) and fields['raw_hex']==raw.hex(),'Pinned finite operand decoder consumes actual instruction');instructions[current].append(dict(**fields,LLVM_mnemonic=m[3],LLVM_operands=m[4]))
    need(all(coverage[s['name']]==s['size'] for s in alloc),'No omitted code tails');out=[]
    for f in funcs:
        sec=e.sections[f['index']]['name'];rows=instructions[sec];written={i['rd'] for i in rows if i['rd'] not in (None,0)};calls=[i for i in rows if i['op']=='jalr' and i['rd']==1]
        out.append(dict(name=f['name'],global_FUNC=f['info']>>4==1,bytes=f['size'],instructions=len(rows),code_sha256=hashlib.sha256(e.function_bytes(f)).hexdigest(),section=sec,own_written_GPRs=sorted(written),own_extra_written_vs_original=sorted(written-{1,2,10,11,12,14,15}),frame_deltas=[i['immediate'] for i in rows if i['op']=='addi' and i['rd']==2 and i['rs1']==2],stack_accesses=[i for i in rows if i['memory_width'] is not None and i['rs1']==2],indirect_calls=calls,raw_rows=rows))
    selected=next(f for f in out if f['name']==ENTRY);need(len(selected['indirect_calls'])==1,'One actual indirect JALR-with-RA call')
    ir=(folder/'native.ll').read_text();signature=re.search(r'define[^@\n]* i32 @'+ENTRY+r'\(([^)]*)\)',ir);need(signature is not None and len(signature[1].split(','))==3 and 'ptr' not in signature[1],'Three-u32 public surface');body=ir[signature.start():ir.index('\n}',signature.start())];need(body.count('load volatile i32')==1 and str(0x4004c) in body and 'ret i32 0' in body,'Fresh slot source and zero normal return in actual IR');call_lines=[line.strip() for line in body.splitlines() if re.search(r'\bcall (?:noundef )?i32 %',line)];need(len(call_lines)==1 and call_lines[0].count('i32')==4,'One actual three-u32 indirect call surface')
    return dict(functions=out,unused_genuine_global_functions=[f['name'] for f in out if f['name']!=ENTRY],allocated_bytes=sum(s['size'] for s in alloc),instructions=sum(len(v) for v in instructions.values()),UND=sorted({s['name'] for s in e.symbols if s['index']==0 and s['name']}),RELA=len(e.relocations),relocations=e.relocations,global_ABS=[s['name'] for s in e.symbols if s['index']==0xfff1 and s['info']>>4],actual_public_IR=body,actual_indirect_call_IR=call_lines,actual_MD_inputs=[dict(path=str(p),sha256=H(p)) for p in sorted(deps)],normal_projection_conditional=True,full_original_ABI_proved=False,installed_provider_proved=False,placement_proved=False,HOST_tests_run=False,target_execution=False,ISA_emulation=False,linked=False,BIN_exported=False)
def replay(root,receipt):
    receipt=receipt.resolve();folder=receipt.parent;r=json.loads(receipt.read_bytes());need(r['artifacts']=={p.relative_to(folder).as_posix():dict(bytes=p.stat().st_size,sha256=H(p)) for p in folder.rglob('*') if p.is_file() and p!=receipt},'Complete actual archive');checked=inspect(root,folder,r);need(checked==r['checks'],'Actual native read-only replay');return dict(passed=True,receipt=str(receipt),sha256=H(receipt),mode=r['mode'],actual_artifacts_read=True,**checked)
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--project-root',required=True,type=Path);p.add_argument('--tool-dir',type=Path);p.add_argument('--build-root',type=Path);p.add_argument('--replay',type=Path);a=p.parse_args();root=a.project_root.resolve()
    if a.replay:need(a.tool_dir is None and a.build_root is None,'Read-only replay rejects compile flags');print(json.dumps(replay(root,a.replay)));return
    need(a.tool_dir is not None,'Explicit pinned local LLVM');old=prior(root);tools={n:next(p.resolve() for p in (a.tool_dir/(n+'.exe'),a.tool_dir/n) if p.is_file()) for n in old['TOOLS']};need(all(H(p)==old['TOOLS'][n] for n,p in tools.items()),'Pinned LLVM');projection(root);owner=root/MODEL/'build';base=a.build_root.resolve() if a.build_root else owner/('nv-'+uuid.uuid4().hex);need(base.is_relative_to(owner) and base!=owner and not base.exists(),'Create-only owned build');base.mkdir(parents=True);results=[]
    for mode in ('c','cpp'):
        folder=base/mode;folder.mkdir();tmp=folder/'compiler-temp';tmp.mkdir();env=dict(os.environ,TMP=str(tmp),TEMP=str(tmp));before=pins(root,tools);resource=None;commands=[]
        for label,argv in recipes(root,folder,mode,tools):
            x=subprocess.run([str(v) for v in argv],cwd=folder,env=env,capture_output=True,timeout=120);log=folder/(label+'.log');log.write_bytes(x.stdout+x.stderr);commands.append(dict(label=label,argv=[str(v) for v in argv],exit=x.returncode,log=log.name,log_sha256=H(log),TMP=str(tmp),TEMP=str(tmp)));need(x.returncode==0,'Actual compilation failed '+str(log))
            if resource is None:resource=Path(x.stdout.decode().strip())/'include/stdint.h';need(H(resource)==old['RESOURCE'],'Pinned resource before compile');before[str(resource)]=H(resource)
        need(before==pins(root,tools,resource),'Stable source/tool/resource before and after');r=dict(schema='TSL9-native-NV-read-callback-v1',mode=mode,tools={n:str(v) for n,v in tools.items()},source_pins=before,conditional_projection=projection(root),commands=commands);r['checks']=inspect(root,folder,r);r['artifacts']={p.relative_to(folder).as_posix():dict(bytes=p.stat().st_size,sha256=H(p)) for p in folder.rglob('*') if p.is_file()};receipt=folder/'verification.json';receipt.write_bytes((json.dumps(r,indent=2)+'\n').encode());checked=replay(root,receipt);results.append(dict(mode=mode,receipt=str(receipt),sha256=H(receipt),functions=[{k:f[k] for k in ('name','bytes','instructions','code_sha256','own_written_GPRs','frame_deltas')} for f in checked['functions']],UND=checked['UND'],RELA=checked['RELA']))
    print(json.dumps(dict(passed=True,results=results,HOST_tests_run=False,target_execution=False)))
if __name__=='__main__':main()
