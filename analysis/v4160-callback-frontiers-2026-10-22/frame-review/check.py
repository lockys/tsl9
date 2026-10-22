#!/usr/bin/env python3
"""Bounded original callback CFG/stack proof; no CPU/ISA execution or emulation."""
import argparse
import hashlib
import importlib.util
import itertools
import json
from pathlib import Path
import sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
ABI_SEAL='51da11cabcafde788376f1cf5aac6306a959332798de96a8492a689df44ff36b'
def need(v,m):
    if not v:raise ValueError(m)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def write(p,v):Path(p).write_bytes((json.dumps(v,indent=2)+'\n').encode('utf8'))
def case(root,n):return next(p for p in(root/'analysis'/n,root/'apk-analysis'/('tsl9-'+n)) if p.is_dir())
def module(p):
    s=importlib.util.spec_from_file_location('frame_source_'+p.parent.name+'_'+p.stem,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def context(root):
    folder=case(root,'v4160-adc-caller-2026-10-22')/'abi-review';need(sha(folder/'seal.json')==ABI_SEAL,'Exact prior sealed caller projection')
    for n,pin in read(folder/'seal.json')['members'].items():need(sha(folder/n)==pin,'Unchanged prior ABI member '+n)
    abi=module(folder/'review.py');_,source=abi.contexts(root);_,_,C,decode,_,_=source.context(root)
    return abi,source,C,decode,folder
def exact(index,pc,**fields):need(all(index[pc][k]==v for k,v in fields.items()),'Source operand '+hex(pc)+' '+str(fields))
def graph(rows,normal_targets,tail_targets=()):
    index={x['PC']:x for x in rows};edges={};exits=[]
    for pc,x in index.items():
        nxt=pc+x['bytes'];op=x['op']
        if op=='jalr':need((x['rd'],x['rs1'],x['immediate'])==(0,1,0),'Only original normal RET');edges[pc]=[];exits.append(pc)
        elif op=='jal' and x['rd']==1:need(x['target'] in normal_targets,'Every call has a closed normal-return source contract');edges[pc]=[nxt]
        elif op=='jal' and x['rd']==0:
            if x['target'] in index:edges[pc]=[x['target']]
            else:need(x['target'] in tail_targets,'Only separately closed normal tail dependency');edges[pc]=[];exits.append(pc)
        elif op in('beq','bne','blt','bge','bltu','bgeu'):edges[pc]=[nxt,x['target']]
        else:edges[pc]=[nxt]
        need(all(y in index for y in edges[pc]),'Every CFG edge lies in retained source')
    return edges,exits
def reachable(edges,start,blocked=()):
    seen=set();todo=[start]
    while todo:
        pc=todo.pop()
        if pc in seen or pc in blocked:continue
        need(pc in edges,'Reachable raw boundary');seen.add(pc);todo.extend(edges[pc])
    return seen
def gate(groups,closed_calls):
    callback,reset,leaf=(groups[k] for k in('callback','reset188e2','leaf19160'));c={x['PC']:x for x in callback};r={x['PC']:x for x in reset};l={x['PC']:x for x in leaf}
    edges,exits=graph(callback,closed_calls);need(exits==[0x1995a],'Unique callback normal RET')
    need(reachable(edges,0x197f0)==set(c),'Complete callback source CFG coverage')
    suffix=reachable(edges,0x1989a);need(0x1995a in suffix and 0x1995a not in reachable(edges,0x1989a,{0x198e6}),'Final reset call dominates every normal exit after ADC return')
    exact(c,0x197f0,op='addi',rd=2,rs1=2,immediate=-128);exact(c,0x19958,op='addi',rd=2,rs1=2,immediate=128)
    need([x['PC'] for x in callback if x['rd']==2]==[0x197f0,0x19958],'Outer callbackSP constant until final restore')
    exact(c,0x19858,op='lui',rd=8,immediate=0x40012000);need([x['PC'] for x in callback if x['rd']==8]==[0x19858,0x1994e],'Source S0/MMIO base unchanged across normal closed calls')
    exact(c,0x198d6,op='beq',rs1=10,rs2=0,target=0x198c6)
    exact(c,0x198e2,op='addi',rd=10,rs1=8,immediate=1024);exact(c,0x198e6,op='jal',rd=1,target=0x188e2,bytes=4)
    exact(r,0x188e2,op='addi',rd=2,rs1=2,immediate=-16);exact(r,0x188e8,op='sw',rs1=2,rs2=1,immediate=12,memory_width=32)
    need(not any(x['rd']==1 for x in reset if x['PC']<0x188e8),'Input RA survives until the actual saved-word store')
    need([x['PC'] for x in reset if x['op']=='sw']==[0x188e8],'Only reset own store is savedRA word')
    re,returns=graph(reset,{0x19160},{0x19160});need(set(returns)=={0x18906,0x1892c},'Both reset normal-exit forms are closed')
    need(reachable(re,0x188e2)==set(r) and all(x not in reachable(re,0x188e2,{0x188e8}) for x in returns),'SavedRA store precedes every reset normal exit')
    exact(r,0x18902,op='lw',rd=1,rs1=2,immediate=12,memory_width=32);exact(r,0x18904,op='addi',rd=2,rs1=2,immediate=16)
    exact(r,0x18906,op='jal',rd=0,target=0x19160)
    exact(r,0x18928,op='lw',rd=1,rs1=2,immediate=12,memory_width=32);exact(r,0x1892a,op='addi',rd=2,rs1=2,immediate=16)
    need(0x18906 not in reachable(re,0x188e2,{0x18902}) and 0x1892c not in reachable(re,0x188e2,{0x18928}),'Every exit reloads that savedRA word')
    need(not any(x['rd'] in(1,2,8) or x['rs1']==2 or x['rs2']==2 for x in leaf),'Nested19160 has no RA/SP/S0 write or stack memory access')
    need([x['rs1'] for x in leaf if x['op']=='sw']==[14,15] and all(x['immediate']==12 for x in leaf if x['op']=='sw'),'Nested only writes fixed RCC+12 via known base')
    for pc in(0x19162,0x1916e):exact(l,pc,op='lui',immediate=0x40021000)
    after=[x for x in callback if x['PC']>=0x198ea]
    need(not any(x['op']=='jal' for x in after),'No call after final reset returns')
    need(not any(x['op'] in('sw','sb','sh') and x['rs1']==2 for x in after),'No later callback own stack store')
    exact(c,0x198ea,op='lui',rd=15,immediate=0x40021000)
    need([x['rs1'] for x in after if x['op']=='sw'][:2]==[15,15] and all(x['rs1']==8 for x in after if x['op']=='sw' and x['PC']>=0x198f6),'Later stores have only the fixed RCC/ADC bases')
    need(all(x['immediate']>=0 for x in after if x['memory_width'] is not None and x['rs1']==2),'Later stack reads stay at nonnegative callbackSP offsets')
    return dict(callback_normal_RET=0x1995a,post_ADC_normal_CFG_nodes=len(suffix),final_call_PC=0x198e6,final_call_target=0x188e2,final_call_dominates_normal_exit=True,final_call_link_RA=0x198ea,reset_store_PC=0x188e8,reset_frame_bytes=16,reset_slot_newSP_offset=12,slot_callbackSP_offset=-4,slot_entrySP_offset=-132,slot_width_bits=32,normal_exit_slot_word=0x198ea,slot_definitely_overwritten_before_normal_exit=True,later_own_stack_store=False,later_aliasing_MMIO_store_excluded_by_premise=True,both_original_and_candidate_final_slot_equal_conditionally=True,callee_return_boundary_equality_proved=False,private_intermediate_observer_equivalence_proved=False,poll_backedge=[0x198d6,0x198c6],unconditional_termination_or_overwrite_proved=False,full_RAM_or_IRQ_equivalence_proved=False)
def controls(groups,C,decode,closed_calls):
    out=[]
    for name,pc,field,label in(('callback',0x198e6,'rd','final_call_link_register'),('reset188e2',0x188e8,'immediate','same_saved_slot'),('reset188e2',0x188e8,'rs2','saved_value_is_input_RA'),('reset188e2',0x188e2,'immediate','frame_displacement'),('callback',0x19958,'immediate','outerSP_restore')):
        rows=groups[name];start=rows[0]['PC'];original=next(x for x in rows if x['PC']==pc);blob=bytearray(b''.join(bytes.fromhex(x['raw_hex']) for x in rows));found=None
        for bit in range(original['bytes']*8):
            raw=bytearray(blob);raw[pc-start+bit//8]^=1<<(bit%8)
            try:row=decode(raw[pc-start:],pc)
            except ValueError:continue
            keys=('PC','bytes','op','rd','rs1','rs2','immediate','target','memory_width')
            if row[field]!=original[field] and all(row[k]==original[k] for k in keys if k!=field):found=bytes(raw),bit,row;break
        need(found is not None,'Meaningful single-operand raw control');raw,bit,row=found;changed=dict(groups);changed[name]=C.rows(raw,start,decode)
        try:gate(changed,closed_calls)
        except ValueError as e:out.append(dict(case=label,PC=pc,bit=bit,field=field,original=original[field],mutated=row[field],mutated_range_sha256=hashlib.sha256(raw).hexdigest(),rejected=True,reason=str(e)));continue
        raise ValueError('Accepted incorrect source frame operand')
    # Find a bounded source-byte branch mutation that reaches the actual normal
    # epilogue while bypassing the overwrite call. This is a CFG counterexample,
    # never an ISA state transition or generated firmware patch.
    rows=groups['callback'];start=rows[0]['PC'];blob=b''.join(bytes.fromhex(x['raw_hex']) for x in rows);pc=0x198d6;at=pc-start;old=next(x for x in rows if x['PC']==pc);found=None
    for count in(1,2,3):
        for bits in itertools.combinations(range(old['bytes']*8),count):
            raw=bytearray(blob)
            for bit in bits:raw[at+bit//8]^=1<<(bit%8)
            try:row=decode(raw[at:],pc)
            except ValueError:continue
            if row['op']!=old['op'] or any(row[k]!=old[k] for k in('bytes','rd','rs1','rs2','immediate','memory_width')) or row['target'] not in {x['PC'] for x in rows if 0x198ea<=x['PC']<=0x1990e}:continue
            changed=dict(groups);changed['callback']=C.rows(raw,start,decode)
            edges,_=graph(changed['callback'],closed_calls)
            if 0x1995a in reachable(edges,0x1989a,{0x198e6}):found=bytes(raw),list(bits),row,changed;break
        if found:break
    need(found is not None,'Real source-byte normal-exit bypass counterexample control');raw,bits,row,changed=found
    try:gate(changed,closed_calls)
    except ValueError:out.append(dict(case='branch_bypasses_required_overwrite',PC=pc,bits=bits,original_target=old['target'],mutated_target=row['target'],original_RA_SP_restore_epilogue_still_reachable=True,normal_RET_CFG_reachable_avoiding_call=True,mutated_range_sha256=hashlib.sha256(raw).hexdigest(),rejected=True))
    else:raise ValueError('Accepted source CFG bypass of overwrite')
    return out
def inspect(root,firmware=None):
    root=Path(root).resolve();abi,source,C,decode,folder=context(root)
    if (HERE/'seal.json').exists():
        for n,pin in read(HERE/'seal.json')['members'].items():need(sha(HERE/n)==pin,'Immutable new frame-review member '+n)
    inherited=abi.source(root,firmware);ledger=read(HERE/'ledger.json');groups={};total=0;count=0
    fw=Path(firmware).read_bytes() if firmware is not None else None
    for name,v in ledger['groups'].items():
        blob=bytes.fromhex(v['raw_hex']);need(hashlib.sha256(blob).hexdigest()==v['sha256'],'Pinned new bounded original source range');rows=C.rows(blob,v['start'],decode);need(rows==v['rows'] and len(blob)==v['end']-v['start'],'Complete bounded raw operand ledger')
        if fw is not None:need(fw[v['start']-0x8000:v['end']-0x8000]==blob,'Actual original frame source bytes')
        groups[name]=rows;total+=len(blob);count+=len(rows)
    proof=source.inspect(root);closed_calls={x[1] for x in read(HERE/'ledger.json')['callback_calls']};need(proof['facts']['unreviewed_direct_callback_targets']==[],'Original direct callback dependency closure')
    actualcalls=[(x['PC'],x['target']) for x in groups['callback'] if x['op']=='jal' and x['rd']==1];need([list(x) for x in actualcalls]==ledger['callback_calls'],'Exact original normal-call summaries, no assumed ABI calls')
    facts=gate(groups,closed_calls)
    retained=read(folder/'selected.json');need(all(v['normal_caller_projection']['conditionally_supported'] and v['normal_caller_projection']['callee_frame_bytes']==16 and v['normal_caller_projection']['additional_stack_effect'].startswith('save/restoreRA at callbackSP-4') and len(v['selected']['stack_accesses'])==2 for v in retained.values()),'Prior newADC sole privateRA saved-word contract')
    return dict(schema='TSL9-callback-final-frame-source-v1',passed=True,metadata_only=firmware is None,actual_original_firmware_read=firmware is not None,own_bounded_ranges=len(groups),own_source_bytes=total,own_source_rows=count,reused_distinct_closure_source_bytes=inherited['source_bytes'],reused_distinct_closure_source_rows=inherited['source_rows'],own_ranges_are_subset_of_reused_closure=True,source_CFG_only=True,normal_call_summaries_not_CPU_stepping=True,facts=facts,premises=read(HERE/'premises.json')['premises'],raw_controls=controls(groups,C,decode,closed_calls) if firmware is not None else [],raw_controls_replayed=firmware is not None,full_original_callee_ABI_proved=False,fault_async_IRQ_equivalence=False,whole_RAM_equivalence_proved=False,installed_identity_proved=False,Flash_NV_ownership_proved=False,hardware_OTA_proved=False,target_execution=False,ISA_emulation=False,HOST_matrix_rerun=False,network=False,hardware=False,linked=False,BIN_generated=False)
def replay(root,p):
    r=read(p);need(r['checker_sha256']==sha(HERE/'check.py'),'Exact frame checker source');result=inspect(root,Path(r['firmware']));need(result==r['result'],'Read-only actual original FW proof replay');return result
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--project-root',required=True,type=Path);p.add_argument('--firmware',type=Path);p.add_argument('--receipt',type=Path);p.add_argument('--replay',type=Path);a=p.parse_args();root=a.project_root.resolve()
    if a.replay:need(a.firmware is None and a.receipt is None,'Read-only replay');result=replay(root,a.replay)
    else:
        need(a.receipt is None or a.firmware is not None and not a.receipt.exists(),'Only create new actual proof receipts');result=inspect(root,a.firmware)
        if a.receipt:write(a.receipt,dict(schema='TSL9-callback-frame-actual-review-v1',checker_sha256=sha(HERE/'check.py'),firmware=str(a.firmware.resolve()),result=result))
    print(json.dumps(result))
