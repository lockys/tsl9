#!/usr/bin/env python3
"""Independent bounded caller bank and actual native object review; no execution."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
ENTRY='tsl9_adc_config_1892e'
MODEL_SEAL='2ede59286cfbd60bc19985b330ed46f8e1613697a5cc525ce26c549c0505c07f'
SOURCE_SEAL='0c3a18d757bc75e6d0bf43648f7129de4c56d9d166618556c1c2b3e451c5f677'
def need(v,m):
    if not v:raise ValueError(m)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def write(p,v):Path(p).write_bytes((json.dumps(v,indent=2)+'\n').encode('utf8'))
def case(root,n):return next(p for p in(root/'analysis'/n,root/'apk-analysis'/('tsl9-'+n)) if p.is_dir())
def locate(root,p):
    direct=root/p
    if direct.is_file():return direct
    if p.startswith('apk-analysis/tsl9-'):
        n,tail=p[len('apk-analysis/tsl9-'):].split('/',1);return case(root,n)/tail
    return direct
def module(p):
    s=importlib.util.spec_from_file_location('caller_abi_'+p.parent.name+'_'+p.stem,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def closed(folder,pin):
    need(sha(folder/'seal.json')==pin,'Exact previous sealed scope')
    for path,h in read(folder/'seal.json')['members'].items():need(sha(folder/path)==h,'Closed previous member '+path)
def contexts(root):
    previous=case(root,'v4160-adc-config-2026-10-22');closed(previous/'model-review',MODEL_SEAL);closed(previous/'source-review',SOURCE_SEAL)
    return module(previous/'model-review/native.py'),module(previous/'source-review/check.py')
def exact(rows,pc,**wanted):need(all(rows[pc][k]==v for k,v in wanted.items()),'Independent source operand '+hex(pc))
def caller_gate(groups):
    caller=groups['callback'];leaves={k:groups[k] for k in('18986','18a98','18a6e','189ae')};idx={x['PC']:x for x in caller+[x for v in leaves.values() for x in v]}
    for pc,reg,value in((0x1989a,11,1),(0x198a2,11,1),(0x198aa,10,1),(0x198b0,13,7),(0x198b2,12,1),(0x198b4,11,16)):
        exact(idx,pc,op='addi',rd=reg,rs1=0,immediate=value)
    for pc in(0x1989c,0x198a4,0x198b6):exact(idx,pc,op='mv',rd=10,rs1=9)
    for pc,target in((0x19896,0x1892e),(0x1989e,0x18986),(0x198a6,0x18a98),(0x198ac,0x18a6e),(0x198b8,0x189ae)):
        exact(idx,pc,op='jal',rd=1,target=target)
    middle=[x for x in caller if 0x1989a<=x['PC']<0x198b2]+leaves['18986']+leaves['18a98']+leaves['18a6e']
    need(not any(r in(x['rs1'],x['rs2']) for r in(12,16,17) for x in middle),'No A2/A6/A7 read before bounded overwrites')
    exact(idx,0x18986,op='lw',rd=15,rs1=10,immediate=8)
    exact(idx,0x18a9c,op='lui',rd=14,immediate=0x4000000);exact(idx,0x18aa0,op='or',rs2=14)
    exact(idx,0x18a7a,op='lui',rd=13,immediate=0x800000);exact(idx,0x18a7e,op='or',rs2=13)
    need(not any(14 in(x['rs1'],x['rs2']) for x in leaves['18986']),'A4 not read in first intervening helper')
    need(not any(13 in(x['rs1'],x['rs2']) for k in('18986','18a98') for x in leaves[k]),'A3 not read in earlier helpers')
    need(not any(14 in(x['rs1'],x['rs2']) for x in leaves['18a98'] if x['PC']<0x18a9c),'Enabled A4 path writes before read')
    need(not any(13 in(x['rs1'],x['rs2']) for x in leaves['18a6e'] if x['PC']<0x18a7a),'Enabled A3 path writes before read')
    exact(idx,0x189b0,op='bgeu',rs1=15,rs2=11,target=0x189fe);exact(idx,0x189ae,op='addi',rd=15,rs1=0,immediate=9)
    exact(idx,0x189be,op='lw',rd=16,rs1=10,immediate=12);exact(idx,0x189cc,op='and',rs2=16)
    need(not any(16 in(x['rs1'],x['rs2']) for x in leaves['189ae'] if x['PC']<0x189be),'Actual channel16 path writes A6 before first read')
    allrows=[x for v in groups.values() for x in v]
    preserved=[5,7,17,28,29,30,31]
    need(not any(x['rd'] in preserved or x['rs1'] in preserved or x['rs2'] in preserved for x in allrows),'A7/T0/T2/T3/T4/T5/T6 unread and preserved throughout bounded source')
    need([x['PC'] for x in allrows if x['rd']==6]==[0x8520] and [x['PC'] for x in allrows if 6 in(x['rs1'],x['rs2'])]==[0x8524],'Only original T1 write and read')
    exact({x['PC']:x for x in allrows},0x8520,op='addi',rd=6,rs1=0,immediate=15)
    return dict(A0_A6_redefined_before_later_use_for_actual_caller=True,first_writes={'A0':0x1989c,'A1':0x1989a,'A2':0x198b2,'A3':0x18a7a,'A4':0x18a9c,'A5':0x18986,'A6':0x189be},A7_T0_T2_T3_T4_T5_T6_unread_preserved=True,original_T1_normal_exit_value=15,depends_on_actual_enabled_paths_and_channel16=True,relies_on_PSABI=False)
def source(root,firmware=None):
    old,src=contexts(root);base=src.inspect(root);_,_,C,decode,_,_=src.context(root)
    paths=[case(root,'v4160-resident-native-2026-10-22')/'callback-review/ledger.json',case(root,'v4160-register-contract-2026-10-22')/'adc-review/ledger.json',case(root,'v4160-adc-config-2026-10-22')/'source-review/ledger.json'];groups={}
    for p in paths:groups.update(read(p)['groups'])
    blob=Path(firmware).read_bytes() if firmware is not None else None
    if blob is not None:need(len(blob)==76800 and hashlib.sha256(blob).hexdigest()==src.FW,'Actual original ID2966 full identity')
    total=0;rows=0
    for name,v in groups.items():
        raw=b''.join(bytes.fromhex(x['raw_hex']) for x in v);a=v[0]['PC'];need(C.rows(raw,a,decode)==v,'Independent complete original raw fields '+name)
        if blob is not None:need(blob[a-0x8000:a-0x8000+len(raw)]==raw,'Actual original caller/dependency bytes '+name)
        total+=len(raw);rows+=len(v)
    facts=caller_gate(groups);need(base['facts']['minimum_stack_bytes_including_nested']==144,'Existing144-byte callback interval premise')
    return dict(passed=True,facts=facts,source_bytes=total,source_rows=rows,actual_original_firmware_read=blob is not None,metadata_only=blob is None,minimum_stack_bytes_including_nested=144,premises=base['premises'],full_original_callee_ABI_proved=False,physical_ABI_proved=False,target_execution=False,ISA_emulation=False)
def stable(root):
    result=source(root);pins=read(HERE/'reference-pins.json')
    for path,pin in pins['sources'].items():need(sha(locate(root,path))==pin,'Frozen actual source input '+path)
    return result
def kernel(rows):
    keys=('PC','op','rd','rs1','rs2','immediate','target','memory_width');need([[x[k] for k in keys] for x in rows]==read(HERE/'native-kernel.json'),'Complete actual caller-bank selected operands/CFG')
def projection_gate(rows,report,IR):
    need(not report['fixed_GPR_writes'] and not set(report['written_GPRs'])-{1,2,*range(10,17)},'No escaping A7/T/S/GP/TP writes')
    need(not set(report['written_GPRs'])&{10,11},'Selected A0/A1 preserved by every own instruction')
    need(not report['control_transfers'],'No new nested or indirect calls')
    need(report['frame_changes']==[[0,-16],[report['bytes']-4,16]],'Exactly one balanced16-byte frame')
    accesses=report['stack_accesses'];need(len(accesses)==2,'Only savedRA stack word is touched')
    a,b=accesses;need((a['PC'],a['op'],a['rs1'],a['rs2'],a['immediate'],a['memory_width'])==(2,'sw',2,1,12,32),'Save inputRA before borrowing it')
    need((b['PC'],b['op'],b['rd'],b['rs1'],b['immediate'],b['memory_width'])==(report['bytes']-6,'lw',1,2,12,32),'Restore same inputRA word before SP/RET')
    need(not any(x['target'] is not None for x in rows),'Straightline normal path without skipped restore')
    return dict(conditionally_supported=True,scope='only original19896 caller normal mapped effect/result/register projection',public_A0_A1_unchanged=True,callee_frame_bytes=16,existing_callback_stack_interval_bytes=144,additional_stack_effect='save/restoreRA at callbackSP-4, private unused scratch below live config at callbackSP+32',allowed_dead_caller_register_writes=list(range(10,17)),escaping_A7_T_S_GP_TP_writes=False,required_premises=read(HERE/'projection.json')['required_premises'],source_algorithm_unchanged=True,normal_14_effect_SSA_matched=IR['normal_effect_projection'],full_original_callee_ABI=False,private_frame_contents_not_an_observable_projection_output=True,fault_async_IRQ_equivalence=False,placement_proved=False,flashability_proved=False)
def controls(blob,fields,ctx,ir,old):
    rows=fields['rows'](blob,0,ctx);kernel(rows);out=[]
    for pc,field,label in read(HERE/'control-sites.json'):
        row=next(x for x in rows if x['PC']==pc);found=None
        for bit in range(row['bytes']*8):
            b=bytearray(blob);b[pc+bit//8]^=1<<(bit%8)
            try:changed=fields['rows'](bytes(b),0,ctx)
            except ValueError:continue
            r=next((x for x in changed if x['PC']==pc),None);keys=('PC','bytes','op','rd','rs1','rs2','immediate','target','memory_width')
            if r and r[field]!=row[field] and all(r[k]==row[k] for k in keys if k!=field):found=bytes(b),changed,bit,r;break
        need(found is not None,'Actual single raw operand control')
        b,changed,bit,r=found
        try:kernel(changed)
        except ValueError:out.append(dict(case=label,PC=pc,bit=bit,original=row[field],mutated=r[field],mutated_body_sha256=hashlib.sha256(b).hexdigest(),rejected=True));continue
        raise ValueError('Accepted actual incorrect raw operand')
    tail=ir.index('define dso_local i32 @'+ENTRY);prefix=ir[:tail];body=ir[tail:]
    for label,before,after in(('missing_volatile','load volatile i32','load i32'),('wrong_fullword_shift','shl i32 %16, 8','shl i32 %16, 7')):
        need(before in body,'Actual selected IR mutation site');changed=prefix+body.replace(before,after,1)
        try:old.ir_gate(changed)
        except (ValueError,KeyError):out.append(dict(case=label,mutated_IR_sha256=hashlib.sha256(changed.encode()).hexdigest(),rejected=True));continue
        raise ValueError('Accepted wrong actual IR')
    return out
def inspect(root,folder):
    root=Path(root).resolve();folder=Path(folder).resolve();stable(root);old,_=contexts(root);raw_reader,(_,fields,llvm,ctx)=old.context(root)
    p=case(root,'v4160-adc-caller-2026-10-22')/'implementation/probe.py';need(sha(p)==read(HERE/'reference-pins.json')['producer'],'Frozen new compiler/provenance reader');provenance=module(p).replay(root,folder/'verification.json');record=read(folder/'verification.json')
    reserved=sorted(set(range(5,32))-set(range(10,17)));helptext=(folder/'compiler-help.log').read_text();supported={int(n) for n in re.findall(r'-ffixed-x(\d+)\s+Reserve the x\d+ register \(AArch64/RISC-V only\)',helptext)};need(set(reserved)<=supported,'Actual help advertises every complete caller-mask flag')
    for command in record['commands']:
        used=[int(n) for a in command['argv'] for n in re.findall(r'^-ffixed-x(\d+)$',a)];need(used==(reserved if command['label'] in('native-object','native-IR') else []),'Exactly one complete caller bank; no flag chasing')
    tools={'clang':'047dfde05acc6fcce5af669e25cd8d40b4f509b8842d151d6d8a43a1c6a35fd6','llvm-objdump':'de40d1188fe63ff373e1a5dd83a12e2cb4545ca3b314da16a476ecf072e5a0fa'}
    need(all(sha(Path(record['tools'][n]))==pin for n,pin in tools.items()),'Independent actual native tool hashes')
    resource=Path((folder/'compiler-resource-dir.log').read_text().strip())/'include/stdint.h';need(sha(resource)=='7ce5540d5fb6e8da9760928e76cbdd5ebef329d701ad598d30d8e6f9d5d78b34','Actual compiler resource header')
    text=(folder/'native.d').read_text().replace('\\\n',' ');lhs,_,rhs=text.partition(':');deps={Path(re.sub(r'\\(.)',r'\1',p)).resolve() for p in re.findall(r'(?:\\.|[^\s])+',rhs)}
    expected={root/'experiments/tsl9-adc-caller-bank/src/caller_bank.c',*[root/'experiments/tsl9-adc-config/src'/n for n in('native.c','adc_config.c','adc_config.h')],*[root/'experiments/tsl9-resident-memory-leaves/src'/n for n in('memory_leaves.h','io.h')],resource};need(lhs=='native.o' and deps==expected,'Independent complete actual -MD source/header/resource closure')
    e=ctx['ELF'](folder/'native.o');need(e.kind==1 and e.flags==1,'Actual RV32/RVC ET_REL');funcs=[f for f in e.symbols if f['info']&15==2 and f['size']];alloc=[s for s in e.sections if s['flags']&2 and s['size']]
    need(len(funcs)==len(alloc)==5 and {f['name'] for f in funcs}=={ENTRY,'tsl9_adc_config_io','ml_port_read8','ml_port_read32','ml_port_write32'} and all(f['info']==18 and f['other']==0 for f in funcs),'All five true global functions, unused functions retained')
    need(all(s['type']==1 and s['flags']==6 for s in alloc) and {s['index'] for s in alloc}=={f['index'] for f in funcs},'One whole genuine code allocation per function')
    need(not e.relocations and not any(s['name'] and s['index']==0 for s in e.symbols) and not any(s['index']==0xfff1 and s['info']>>4 for s in e.symbols),'UND0/RELA0/ABS0')
    parsed=raw_reader.parse_sections((folder/'complete-static-disassembly.log').read_text(),llvm);reports=[];selected_rows=None;selected_blob=None
    for f in funcs:
        s=e.sections[f['index']];need(f['value']==0 and f['size']==s['size'],'No function interior/tail borrowing');blob=e.function_bytes(f);rows=fields['rows'](blob,0,ctx)
        need([{k:v for k,v in x.items() if k!='offset'} for x in rows]==parsed[s['name']],'All actual raw operands independently equal complete LLVM text')
        starts={x['PC'] for x in rows};need(all(x['target'] is None or x['target'] in starts for x in rows),'Every encoded direct branch stays in real allocation')
        written=sorted({x['rd'] for x in rows if x['rd'] not in(None,0)});reports.append(dict(name=f['name'],bytes=f['size'],instructions=len(rows),written_GPRs=written,fixed_GPR_writes=sorted(set(written)&set(reserved)),frame_changes=[[x['PC'],x['immediate']] for x in rows if x['op']=='addi' and x['rd']==x['rs1']==2],stack_accesses=[x for x in rows if x['memory_width'] is not None and x['rs1']==2],memory=[x for x in rows if x['memory_width'] is not None],control_transfers=[x for x in rows if x['op'] in('jal','jalr') and not(x['op']=='jalr' and x['rd']==0 and x['rs1']==1 and x['immediate']==0)],code_sha256=hashlib.sha256(blob).hexdigest()))
        if f['name']==ENTRY:selected_rows=rows;selected_blob=blob
    kernel(selected_rows);s=next(x for x in reports if x['name']==ENTRY);ir=(folder/'native.ll').read_text();IR=old.ir_gate(ir);projection=projection_gate(selected_rows,s,IR)
    return dict(passed=True,mode=record['mode'],actual_native_artifacts_read=True,producer_provenance_replayed=provenance['passed'],producer_receipt_sha256=sha(folder/'verification.json'),object_sha256=sha(folder/'native.o'),IR_sha256=sha(folder/'native.ll'),register_bank=dict(allowed=list(range(10,17)),reserved=reserved,special=[1,2,3,4]),functions=reports,selected=s,IR=IR,total_function_bytes=sum(x['bytes'] for x in reports),total_instructions=sum(x['instructions'] for x in reports),unused_genuine_global_functions=4,RELA=0,undefined_symbols=[],actual_MD_inputs=[dict(path=str(p),sha256=sha(p)) for p in sorted(deps)],actual_controls=controls(selected_blob,fields,ctx,ir,old),normal_caller_projection=projection,full_original_callee_ABI_proved=False,physical_ABI_proved=False,target_execution=False,ISA_emulation=False,linked=False,BIN_exported=False)
def replay(root,p):
    r=read(p);need(r['checker_sha256']==sha(HERE/'review.py'),'Exact independent reader identity');result=inspect(root,Path(r['folder']));need(result==r['result'],'Actual caller-bank readback equals receipt');return result
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--project-root',required=True,type=Path);p.add_argument('--folder',type=Path);p.add_argument('--receipt',type=Path);p.add_argument('--replay',type=Path);p.add_argument('--firmware',type=Path);a=p.parse_args();root=a.project_root.resolve()
    if a.replay:need(a.folder is None and a.receipt is None and a.firmware is None,'Read-only replay');result=replay(root,a.replay)
    elif a.folder:
        need(a.receipt is not None and not a.receipt.exists() and a.firmware is None,'Create-only actual review');result=inspect(root,a.folder);write(a.receipt,dict(schema='TSL9-ADC-caller-independent-native-v1',checker_sha256=sha(HERE/'review.py'),folder=str(a.folder.resolve()),result=result))
    else:need(a.receipt is None,'Source-only mode');result=source(root,a.firmware)
    print(json.dumps(result))
