#!/usr/bin/env python3
"""Independent static fixed-register ET_REL review; never executes target code."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
OLD='v4160-resident-native-2026-10-22'
OLD_REVIEW='00fd4f88327b6b98f51dd5ef2e70a91076a1f2a427799b85ca03af6c0caf9add'
NAMES={'compare':'tsl9_native_compare_200004bc','fill':'tsl9_native_fill_2000039c','copy':'tsl9_native_copy_20000332'}

def need(v,m):
    if not v:raise ValueError(m)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def write(p,v):Path(p).write_bytes((json.dumps(v,indent=2)+'\n').encode('utf8'))
def module(p):
    s=importlib.util.spec_from_file_location('register_review_'+p.parent.name+'_'+p.stem,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def case(root,slug):return next(p for p in(root/'apk-analysis'/('tsl9-'+slug),root/'analysis'/slug) if p.is_dir())
def context(root):
    p=case(root,OLD)/'abi-review/review.py';need(sha(p)==OLD_REVIEW,'Pinned sealed previous reviewer');old=module(p);old.source(root);return old,old.context(root)
def contracts(root):
    old,_=context(root);c=read(case(root,OLD)/'abi-review/source-contracts.json');out={}
    for leaf,value in c['leaves'].items():
        allowed=sorted(set(value['own_written_GPRs_excluding_zero'])|{10,11,12})
        out[leaf]=dict(original=value,allowed_allocator_GPRs=allowed,fixed_allocator_GPRs=sorted(set(range(5,32))-set(allowed)),special_GPRs_checked_from_machine_code=[1,2,3,4])
    return out
def source(root):
    c=contracts(root);pins=read(HERE/'reference-pins.json')
    for relative,pin in pins['sources'].items():need(sha(root/relative)==pin,'Frozen review input '+relative)
    return dict(passed=True,contracts=c,metadata_only=True,actual_native_artifacts_read=False,physical_ABI_proved=False,target_execution=False)

def section_inventory(e,old,fields,llvm,ctx,text):
    funcs=[f for f in e.symbols if f['info']&15==2 and f['size']];alloc=[s for s in e.sections if s['flags']&2 and s['size']]
    need(e.kind==1 and e.flags==1,'Actual RV32/RVC ET_REL')
    expected=set(NAMES.values())|{n.replace('tsl9_native_','tsl9_candidate_') for n in NAMES.values()}|{'ml_port_read8','ml_port_read32','ml_port_write8','ml_port_write32','ml_port_fence_i'}
    need(len(funcs)==11 and {f['name'] for f in funcs}==expected and all(f['info']==18 and f['other']==0 for f in funcs),'All eleven genuine global FUNC definitions')
    need(all(s['type']==1 and s['flags']==6 for s in alloc),'Only genuine executable allocations')
    need({s['index'] for s in alloc}=={f['index'] for f in funcs} and len(alloc)==len(funcs),'Exactly one actual function owns every allocation')
    need(not any(s['index']==0xfff1 and s['info']>>4 for s in e.symbols),'No absolute provider aliases')
    parsed=old.parse_sections(text,llvm);reports=[];rows_by_name={};blobs={}
    for f in funcs:
        s=e.sections[f['index']];need(f['value']==0 and f['size']==s['size'],'Whole real function, no interior/tail borrowing')
        blob=e.function_bytes(f);rows=fields['rows'](blob,0,ctx)
        need([{k:v for k,v in x.items() if k!='offset'} for x in rows]==parsed[s['name']],'Complete raw operands independently equal LLVM text')
        starts={x['PC'] for x in rows};need(all(x['target'] is None or x['target'] in starts for x in rows),'All direct branches are real local boundaries')
        writes=sorted({x['rd'] for x in rows if x['rd'] not in(None,0)})
        reports.append(dict(name=f['name'],bytes=f['size'],instructions=len(rows),code_sha256=hashlib.sha256(blob).hexdigest(),written_GPRs=writes,stack_changes=[[x['PC'],x['immediate']] for x in rows if x['op']=='addi' and x['rd']==x['rs1']==2],stack_accesses=[x for x in rows if x['memory_width'] is not None and x['rs1']==2],memory=[x for x in rows if x['memory_width'] is not None],fence_i_sites=[x['PC'] for x in rows if x['op']=='fence.i'],control_transfers=[x for x in rows if x['op'] in('jal','jalr') and not(x['op']=='jalr' and x['rd']==0 and x['rs1']==1 and x['immediate']==0)],relocations=[x for x in e.relocations if x['owner']==s['name']]))
        rows_by_name[f['name']]=rows;blobs[f['name']]=blob
    return reports,rows_by_name,blobs

def kernel(leaf,rows):
    keys=('PC','op','rd','rs1','rs2','immediate','target','memory_width')
    actual=[[x[k] for k in keys] for x in rows]
    need(actual==read(HERE/'selected-kernels.json')[leaf],'Complete measured selected operand/CFG inventory '+leaf)
    return dict(complete_operand_inventory=True,guard_preceded_by_new_stack_access=True,real_fence_i=True,normal_mapped_effect_result_projection=True,normal_A1_A2_restored=True,stack_valid_private_nonaliasing_premise_required=True,full_original_register_ABI=False,fault_or_asynchronous_prefix_equivalence=False)

def controls(leaf,blob,fields,ctx,old,ir):
    out=[]
    # Actual complete selected bodies are accepted first. Change only their raw
    # operands, then statically decode; this is no CPU/ISA state execution.
    kernel(leaf,fields['rows'](blob,0,ctx))
    edits=[(2,bytes.fromhex('06c4'),'RA_save_slot_12_changed_to_8')]
    if leaf=='compare':
        word=int.from_bytes(blob[28:32],'little');word=(word&~(31<<7))|(17<<7)
        edits.append((28,word.to_bytes(4,'little'),'byte_load_writes_reserved_x17'))
    elif leaf=='fill':edits.append((60,bytes.fromhex('2a86'),'A2_restore_uses_A0_not_RA'))
    else:
        word=int.from_bytes(blob[34:38],'little');word=(word&~(7<<12))|(5<<12)
        edits.append((34,word.to_bytes(4,'little'),'fresh_byte_load_changed_to_halfword'))
    for at,replacement,label in edits:
        changed=blob[:at]+replacement+blob[at+len(replacement):]
        need(changed!=blob,'Meaningful actual raw mutation')
        try:kernel(leaf,fields['rows'](changed,0,ctx))
        except ValueError:out.append(dict(case=label,offset=at,replacement_hex=replacement.hex(),mutated_body_sha256=hashlib.sha256(changed).hexdigest(),rejected=True));continue
        raise ValueError('Accepted raw control '+label)
    name=NAMES[leaf];old.ir_kernel(ir,name)
    match=re.search(r'^define[^\n]*@'+name+r'\([^\n]*\)[^\n]*\{\n(.*?)^}',ir,re.M|re.S);need(match is not None,'Actual selected IR body')
    changed=ir[:match.start(1)]+match[1].replace('load volatile i32','load i32',1)+ir[match.end(1):]
    try:old.ir_kernel(changed,name)
    except ValueError:out.append(dict(case='selected_guard_read_loses_volatile',mutated_IR_sha256=hashlib.sha256(changed.encode()).hexdigest(),rejected=True));return out
    raise ValueError('Accepted selected IR control')

def inspect(root,folder):
    root=Path(root).resolve();folder=Path(folder).resolve();source(root);old,(_,fields,llvm,ctx)=context(root)
    producer=case(root,'v4160-register-contract-2026-10-22')/'implementation/probe.py'
    need(sha(producer)==read(HERE/'reference-pins.json')['producer'],'Frozen new compiler/provenance reader')
    provenance=module(producer).replay(root,folder/'verification.json');record=read(folder/'verification.json');leaf=record['leaf'];mode=record['mode'];need(record['compiler_success'],'Actual successful compile')
    c=contracts(root)[leaf];bank=record['register_bank']
    need(bank['allowed']==c['allowed_allocator_GPRs'] and bank['reserved']==c['fixed_allocator_GPRs'] and bank['original_written']==c['original']['own_written_GPRs_excluding_zero'],'Independently complete per-leaf mask')
    support={int(n) for n in re.findall(r'-ffixed-x(\d+)\s+Reserve the x\d+ register \(AArch64/RISC-V only\)',(folder/'compiler-help.log').read_text())}
    need(set(bank['reserved'])<=support,'All actual reserved flags advertised for RISC-V')
    for command in record['commands']:
        actual=[int(n) for a in command['argv'] for n in re.findall(r'^-ffixed-x(\d+)$',a)]
        need(actual==(bank['reserved'] if command['label'] in('native-object','native-IR') else []),'Exactly one complete bank in object and IR recipes')
    e=ctx['ELF'](folder/'native.o');reports,allrows,blobs=section_inventory(e,old,fields,llvm,ctx,(folder/'complete-static-disassembly.log').read_text())
    for report in reports:report['fixed_GPR_writes']=sorted(set(report['written_GPRs'])&set(bank['reserved']))
    name=NAMES[leaf];rows=allrows[name];selected=next(x for x in reports if x['name']==name);written=selected['written_GPRs'];original=c['original'];ir=(folder/'native.ll').read_text()
    signature=re.search(r'^define[^\n]*\bi32 @'+name+r'\(([^\n]*)\)[^\n]*\{',ir,re.M)
    need(signature is not None and len(re.findall(r'\bi32\b',signature[1]))==3 and 'sret' not in signature[1] and 'ptr' not in signature[1],'Actual selected three-u32/u32 interface without hidden context')
    need(not selected['fixed_GPR_writes'],'Selected code does not write reserved allocator bank')
    need(not e.relocations and not any(s['index']==0 and s['name'] for s in e.symbols),'Actual UND0 and RELA0')
    need(selected['stack_changes']==[[0,-16],[selected['bytes']-4,16]],'Actual new aligned16-byte SP frame')
    need(not any(x['op']=='jalr' or x['rd']!=0 for x in selected['control_transfers']),'Selected entry has no nested/indirect runtime calls')
    for x in selected['stack_accesses']:need(0<=x['immediate'] and x['immediate']+x['memory_width']//8<=16,'Actual explicit stack access inside new16-byte frame')
    oldextras={'compare':[16],'fill':[13,16,17],'copy':[5,17]}[leaf]
    entry=dict(leaf=leaf,name=name,original_bytes=original['bytes'],new_bytes=selected['bytes'],byte_length_fits_only=selected['bytes']<=original['bytes'],original_full_extent_ownership_proved=False,written_GPRs=written,additional_own_written_GPRs=sorted(set(written)-set(original['own_written_GPRs_excluding_zero'])),previous_extra_allocator_writes_removed=not set(oldextras)&set(written),new_frame_bytes=16,RA_SP_own_written=all(n in written for n in(1,2)),A1_own_written=11 in written,A2_own_written=12 in written,kernel=kernel(leaf,rows),IR=old.ir_kernel(ir,name),normal_scratch_and_fault_differences=read(HERE/'semantic-deltas.json')[leaf])
    return dict(passed=True,actual_native_artifacts_read=True,leaf=leaf,mode=mode,register_contract=c,advertised_fixed_GPRs=sorted(support),producer_receipt_sha256=sha(folder/'verification.json'),producer_provenance_replayed=provenance['passed'],object_sha256=sha(folder/'native.o'),IR_sha256=sha(folder/'native.ll'),functions=reports,selected=entry,unused_genuine_global_functions=10,unused_function_bytes=sum(x['bytes'] for x in reports if x['name']!=name),unused_instructions=sum(x['instructions'] for x in reports if x['name']!=name),total_function_bytes=sum(x['bytes'] for x in reports),total_instructions=sum(x['instructions'] for x in reports),RELA=len(e.relocations),undefined_symbols=[],actual_controls=controls(leaf,blobs[name],fields,ctx,old,ir),linked=False,BIN_exported=False,target_execution=False,ISA_emulation=False,physical_ABI_proved=False,installed_provider_proved=False)

def replay(root,p):
    r=read(p);need(r['checker_sha256']==sha(HERE/'review.py'),'Frozen checker identity');result=inspect(root,Path(r['folder']));need(result==r['result'],'Actual static readback equals receipt');return result

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--project-root',required=True,type=Path);p.add_argument('--folder',type=Path);p.add_argument('--receipt',type=Path);p.add_argument('--replay',type=Path);a=p.parse_args();root=a.project_root.resolve()
    if a.replay:need(a.folder is None and a.receipt is None,'Read-only replay');result=replay(root,a.replay)
    elif a.folder:
        need(a.receipt is not None and not a.receipt.exists(),'Create-only review receipt');result=inspect(root,a.folder.resolve());write(a.receipt,dict(schema='TSL9-register-independent-review-v1',checker_sha256=sha(HERE/'review.py'),folder=str(a.folder.resolve()),result=result))
    else:need(a.receipt is None,'Metadata-only mode');result=source(root)
    print(json.dumps(result))
