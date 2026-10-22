"""Static App/resident callback bindings; source CFG/liveness, never ISA execution."""
import argparse
import hashlib
import json
import runpy
import sys
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
FW='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
PINS={
 'v4160-adc-config-2026-10-22/source-review':'0c3a18d757bc75e6d0bf43648f7129de4c56d9d166618556c1c2b3e451c5f677',
 'v4160-adc-caller-2026-10-22/continuation-review':'6d71e389571fd41d10f727e0fe645dfdb3c51c4f56a92274c9d793102e9b6133',
 'v4160-allocator-callback-2026-10-22/config-review':'963f2d22d8a1e6090cb91259ba2b65de6f76426af22a4ea99e4521931c9577b9',
 'v4160-ota-handler-compact-2026-10-22/callee-review':'fc9cb5eac8556bb00e86a598ad9fd9587ad2763318f5d6735c70f2cabe8be6f9',
 'v4160-resident-contracts-2026-10-21/flash-callers':'4e2f84890434fff9acf884dd226268e591130c9a2ab909193c1a45ff505b63cc',
}
MODEL='84f33520fad4078e97a0eb6a009fa5d5b6d1cfa91fc2a772b2fb9b7950ea8f5f'
RANGES={'App_config':(0x199e2,0x19b16),'read_cb':(0x1979a,0x197b8),'write_cb':(0x197be,0x197f0),'timer':(0x19764,0x1979a),'unlock':(0x18e98,0x18eb6),'lock':(0x18eb6,0x18ec4),'erase':(0x18ec4,0x18ef2),'program':(0x18ef2,0x18f56),'mac_source':(0x18f56,0x18f88)}
def need(v,s):
    if not v:raise ValueError(s)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def case(root,n):return next(p for p in (root/'analysis'/n,root/'apk-analysis'/('tsl9-'+n)) if p.is_dir())
def closed(folder,pin):
    need(sha(folder/'seal.json')==pin,'Exact previous sealed source')
    members=read(folder/'seal.json')['members'];members=members.items() if isinstance(members,dict) else [(x['path'],x) for x in members]
    for n,h in members:need(sha(folder/n)==(h if isinstance(h,str) else h['sha256']),'Closed source member '+n)
def context(root):
    folders={n:case(root,n) for n in PINS}
    for n,pin in PINS.items():closed(folders[n],pin)
    S=runpy.run_path(str(folders['v4160-adc-config-2026-10-22/source-review']/'check.py'))
    _,_,C,decode,_,_=S['context'](root)
    R=runpy.run_path(str(folders['v4160-adc-caller-2026-10-22/continuation-review']/'check.py'));R['validate_metadata'](root)
    model=next(p for p in (root/'experiments/tsl9-v4160-contract-model/src/flash_contract.c',root/'publish-tsl9/experiments/tsl9-v4160-contract-model/src/flash_contract.c') if p.is_file())
    need(sha(model)==MODEL,'Existing ID2966 write HOST-model source, no execution')
    return C,decode,R,folders
def exact(rows,pc,**fields):need(all(rows[pc][k]==v for k,v in fields.items()),'Source field '+hex(pc)+' '+str(fields))
def cfg(rows):
    idx={x['PC']:x for x in rows};seen=set();todo=[rows[0]['PC']];calls=[];returns=[];edges=[]
    while todo:
        pc=todo.pop()
        if pc in seen:continue
        need(pc in idx,'All direct CFG edges captured');seen.add(pc);x=idx[pc];op=x['op'];n=pc+x['bytes']
        if op=='jalr' and x['rd']==0:need((x['rs1'],x['immediate'])==(1,0),'Only RA return');returns.append(pc);dest=[]
        elif op=='jalr' or op=='jal' and x['rd']==1:calls.append(dict(PC=pc,target=x['target'],rs1=x['rs1']));dest=[n]
        elif op=='jal':need(x['rd']==0,'Admitted local jump');dest=[x['target']]
        elif op in ('beq','bne','bltu','bgeu','blt','bge'):dest=[n,x['target']]
        else:dest=[n]
        for q in dest:need(q in idx,'Bounded CFG destination');edges.append((pc,q));todo.append(q)
    need(seen==set(idx),'Every row in actual entry CFG')
    return dict(bytes=sum(x['bytes'] for x in rows),rows=len(rows),RET_PCs=sorted(returns),calls=sorted(calls,key=lambda x:x['PC']),backedges=[list(e) for e in edges if e[1]<=e[0]],normal_call_returns_conditional=True)
REGS={10:'A0',11:'A1',12:'A2',13:'A3',14:'A4',15:'A5',16:'A6',17:'A7',5:'T0',6:'T1',7:'T2',28:'T3',29:'T4',30:'T5',31:'T6'}
def post_read_liveness(record,R,zero52):
    """Finite static may-liveness over source CFGs, not values or CPU state."""
    groups={k:record['groups'][k] for k in ('table_init','allocator','fill','free')}
    idx={k:{x['PC']:x for x in g} for k,g in groups.items()};entry={g[0]['PC']:k for k,g in groups.items()}
    calls={k:{x['PC']:x['target'] for x in R['cfg'](g)['calls']} for k,g in groups.items()}
    tb=groups['table_init'][0]['PC'];allmask=sum(1<<n for n in REGS);todo=[('table_init',tb+0x36,(),allmask,'none')];seen={};reads={};boundaries={}
    def boundary(kind,pc,mask):boundaries[(kind,pc)]=boundaries.get((kind,pc),0)|mask
    while todo:
        owner,pc,stack,mask,outcome=todo.pop();node=(owner,pc,stack,outcome)
        if node in seen and not mask&~seen[node]:continue
        seen[node]=seen.get(node,0)|mask;x=idx[owner][pc];op=x['op']
        for n in (x['rs1'],x['rs2']):
            if n in REGS and mask&(1<<n):reads[(pc,owner,REGS[n])]=True
        if x['rd'] in REGS:mask&=~(1<<x['rd'])
        if pc in calls[owner]:
            target=calls[owner][pc]
            if target is None:
                boundary('next_config60' if owner=='table_init' and pc==tb+0x9c else 'unresolved_config52',pc,mask);continue
            need(target in entry,'Only sealed direct dependencies before next callback')
            todo.append((entry[target],target,stack+((owner,pc+x['bytes']),),mask,'none'));continue
        if op=='jalr' and x['rd']==0:
            if stack:
                o,q=stack[-1];todo.append((o,q,stack[:-1],mask,outcome))
            else:boundary('early_table_return',pc,mask)
            continue
        if op=='jal':edges=[x['target']]
        elif op in ('beq','bne','bltu','bgeu','blt','bge'):edges=[pc+x['bytes'],x['target']]
        else:edges=[pc+x['bytes']]
        # Fixed literal argument bindings: config block=256, caller tag=78,
        # first iteration S2=0 and unchanged config byte14=3. These are
        # explicit conditional source facts, not an ISA state interpreter.
        if owner=='allocator':
            if pc==0x20000062:outcome='allocator_zero'
            elif pc==0x200000f4:outcome='allocator_success_nonwrapping_pointer'
            if pc==0x20000056:edges=[0x20000058]
            elif pc==0x20000058:edges=[0x20000066]
            elif pc==0x20000078:edges=[0x200000a4]
            elif pc==0x20000098 and zero52:edges=[0x2000005a]
        elif owner=='table_init':
            if pc==tb+0x5a:
                need(outcome in ('allocator_zero','allocator_success_nonwrapping_pointer'),'Source allocation return class known')
                edges=[tb+0x16] if outcome=='allocator_zero' else [pc+x['bytes']]
                outcome='none'
            elif pc==tb+0x70:edges=[tb+0x8a]
        for q in edges:todo.append((owner,q,stack,mask,outcome))
    return dict(candidate=record['candidate'],conditional_fixed_config_block256_tag78_count3=True,
        conditional_config52_zero=zero52,valid_nonwrapping_heap_return_contract=True,
        allocation_zero_return_not_followed_by_success_branch=True,source_dataflow_nodes=len(seen),
        own_reads_before_post_read_write=[dict(PC=pc,body=o,register=n) for pc,o,n in sorted(reads)],
        boundaries=[dict(kind=k,PC=pc,may_retain_original_read_callback_exit=[REGS[n] for n in REGS if mask&(1<<n)]) for (k,pc),mask in sorted(boundaries.items())],
        unknown_callback_effects_assumed=False,no_PSABI_clobber_permission=True,
        normal_caller_replacement_proved=False,ISA_execution=False)
def gate(groups,copy):
    idx={k:{x['PC']:x for x in rows} for k,rows in groups.items()};a=idx['App_config'];r=idx['read_cb'];w=idx['write_cb'];t=idx['timer'];c={x['PC']:x for x in copy}
    graphs={k:cfg(rows) for k,rows in groups.items()}
    for pc,op,rd,rs1,imm in [(0x19a76,'auipc',14,None,0),(0x19a7a,'addi',14,14,-732),(0x19a80,'auipc',14,None,0),(0x19a84,'addi',14,14,-706)]:exact(a,pc,op=op,rd=rd,rs1=rs1,immediate=imm)
    exact(a,0x19a7e,op='sw',rs1=2,rs2=14,immediate=72);exact(a,0x19a88,op='sw',rs1=2,rs2=14,immediate=76)
    exact(a,0x19aea,op='addi',rd=10,rs1=2,immediate=16)
    need((0x19a76+a[0x19a76]['immediate']+a[0x19a7a]['immediate'])&0xffffffff==0x1979a,'Actual record56 pointer')
    need((0x19a80+a[0x19a80]['immediate']+a[0x19a84]['immediate'])&0xffffffff==0x197be,'Actual record60 pointer')
    exact(a,0x19a4a,op='lui',rd=15,immediate=0x08078000);exact(a,0x19a4e,op='addi',rd=15,rs1=15,immediate=-1024);exact(a,0x19a52,op='sw',rs1=2,rs2=15,immediate=24)
    exact(a,0x19a20,op='addi',rd=12,rs1=0,immediate=64);exact(a,0x19a2e,op='addi',rd=11,rs1=0,immediate=0);exact(a,0x19a36,op='addi',rd=10,rs1=2,immediate=16)
    writes=[x for x in groups['App_config'] if x['memory_width'] and x['op'] in ('sw','sh','sb')]
    need(not any(x['rs1']==2 and x['immediate']<72 and x['immediate']+x['memory_width']//8>68 for x in writes),'No explicit store at record52, including complete pointer word')
    exact(a,0x19ab4,op='jal',rd=1,target=0x18f56)
    exact(a,0x19aac,op='addi',rd=10,rs1=2,immediate=8)
    exact(a,0x19ab8,op='addi',rd=14,rs1=2,immediate=16);exact(a,0x19abc,op='addi',rd=13,rs1=0,immediate=6)
    exact(a,0x19ac8,op='addi',rd=14,rs1=14,immediate=1);exact(a,0x19aca,op='sb',rs1=14,rs2=12,immediate=23);exact(a,0x19ace,op='bne',rs1=15,rs2=13,target=0x19abe)
    exact(a,0x19a54,op='lui',rd=15,immediate=4096);exact(a,0x19a56,op='addi',rd=14,rs1=15,immediate=-2045);exact(a,0x19a5a,op='sh',rs1=2,rs2=14,immediate=30)
    exact(r,0x1979a,op='lui',rd=15,immediate=0x40000);exact(r,0x1979e,op='lw',rd=15,rs1=15,immediate=76)
    exact(r,0x197a0,op='addi',rd=2,rs1=2,immediate=-16);exact(r,0x197a2,op='mv',rd=14,rs1=12)
    exact(r,0x197a4,op='sw',rs1=2,rs2=1,immediate=12);exact(r,0x197a6,op='slli',rd=12,rs1=11,immediate=2)
    exact(r,0x197aa,op='mv',rd=11,rs1=10);exact(r,0x197ac,op='mv',rd=10,rs1=14);exact(r,0x197ae,op='jalr',rd=1,rs1=15,immediate=0)
    exact(r,0x197b0,op='lw',rd=1,rs1=2,immediate=12);exact(r,0x197b2,op='addi',rd=10,rs1=0,immediate=0);exact(r,0x197b4,op='addi',rd=2,rs1=2,immediate=16)
    exact(c,0x20000342,op='beq',rs1=10,rs2=0,target=0x2000034a);exact(c,0x20000344,op='beq',rs1=11,rs2=0,target=0x2000034a)
    exact(c,0x20000346,op='addi',rd=15,rs1=0,immediate=0);exact(c,0x20000348,op='bne',rs1=12,rs2=0,target=0x20000354)
    exact(c,0x20000354,op='add',rd=13,rs1=11,rs2=15);exact(c,0x20000358,op='lbu',rd=16,rs1=13,immediate=0);exact(c,0x2000035c,op='add',rd=13,rs1=10,rs2=15)
    need(not any(13 in (x['rs1'],x['rs2']) for x in copy if x['PC']<=0x20000354),'Conditional nonzero copy first defines A3 before read')
    protected=(3,4,8,9,*range(18,28),5,6,7,28,29,30,31,17)
    need(not any(x['rd'] in protected for x in groups['read_cb']+copy),'Read wrapper/copy source preserve S/GP/TP/T/A7')
    need([x['target'] for x in graphs['write_cb']['calls']]==[0x18e98,0x18ec4,0x18ef2,0x18eb6,0x19764],'Exact write dependency order')
    exact(w,0x197be,op='addi',rd=2,rs1=2,immediate=-32);exact(w,0x197c0,op='sw',rs1=2,rs2=1,immediate=28);exact(w,0x197c2,op='sw',rs1=2,rs2=8,immediate=24)
    exact(w,0x197c4,op='sw',rs1=2,rs2=12,immediate=12);exact(w,0x197c6,op='mv',rd=8,rs1=10)
    exact(w,0x197d2,op='lw',rd=12,rs1=2,immediate=12);exact(w,0x197d4,op='mv',rd=10,rs1=8);exact(w,0x197d6,op='mv',rd=11,rs1=12)
    exact(w,0x197e0,op='addi',rd=10,rs1=0,immediate=1);exact(w,0x197e6,op='lw',rd=1,rs1=2,immediate=28);exact(w,0x197e8,op='lw',rd=8,rs1=2,immediate=24)
    exact(w,0x197ea,op='addi',rd=10,rs1=0,immediate=0);exact(w,0x197ec,op='addi',rd=2,rs1=2,immediate=32)
    need(not any(11 in (x['rs1'],x['rs2']) for x in groups['write_cb'] if x['PC']<0x197d6),'Original write entry A1 not read')
    for k in ('unlock','lock','erase','program','timer','mac_source'):
        need(not graphs[k]['calls'],'Every required App helper is a leaf')
        need(not any(x['rd'] in (1,2,3,4,8,9,*range(18,28)) for x in groups[k]),'No helper own SP/RA/S/GP/TP write')
    exact(t,0x19764,op='lui',rd=15,immediate=0xe000f000);exact(t,0x19770,op='lbu',rd=14,rs1=3,immediate=382);exact(t,0x19774,op='mul',rd=12,rs1=14,rs2=10)
    exact(t,0x19790,op='beq',rs1=14,rs2=0,target=0x1978c)
    exact(idx['program'],0x18f16,op='addi',rd=12,rs1=0,immediate=256);exact(idx['program'],0x18f30,op='addi',rd=15,rs1=15,immediate=4)
    mac=[(x['immediate'],x['memory_width']) for x in groups['mac_source'] if x['op']=='sb']
    need(mac==[(i,8) for i in range(6)],'Six MAC-source destination bytes only, no actual UID data read')
    return dict(source_bytes=682,source_rows=248,groups=graphs,record56=0x1979a,record60=0x197be,record52_zero_only_conditional=True,
        numeric_NV_base=0x08077c00,Flash_ownership_proved=False,record12_zero_before_defaults_conditional=True,record14_byte=3,
        conditional_resident_default_block_bytes=256,conditional_write_call_words=64,conditional_write_call_iterations=3,
        conditional_numeric_destinations=[0x08077c00,0x08077d00,0x08077e00],conditional_numeric_extent_end=0x08077f00,
        read_slot=0x4004c,read_slot_load_before_frame=True,read_frame_bytes=16,read_saved_RA_offset=12,
        read_argument_map=['A0=entryA2','A1=entryA0','A2=u32(entryA1<<2)'],read_result_A0=0,
        read_preserved_S_GP_TP_T_A7_under_exact_candidate_copy=True,read_full_original_C_prototype_proved=False,
        first_read_source=0x08077c00,first_read_count_words=1,first_read_count_bytes=4,first_read_output='parent table SP+12..15',read_RA='parent table SP-4..-1',
        read_actual_nonzero4_copy_defines_A3_before_use=True,copy_A3_first_def_PC=0x20000354,copy_A3_first_use_PC=0x20000358,copy_nonzero_exit_A3='destination+count-1',
        extra_native_pre_copy_A3_clobber_erased_only_under_this_nonzero_copy=True,generic_zero_count_or_null_copy_preserves_entry_A3=True,
        word_count_wrap_to_zero_example=0x40000000,generic_read_native_ABI_proved=False,
        write_frame_bytes=32,write_entry_A1_unused=True,write_source='entry A2',write_fixed_program_bytes=256,write_program_source_words=64,
        write_calls=[0x18e98,0x18ec4,0x18ef2,0x18eb6,0x19764],write_return_A0=0,write_success_status_checked=False,
        write_S0_preserved_only_on_valid_normal_terminating_paths=True,timer_GP_byte_offset=382,timer_A0_argument=1,timer_scale_or_units_known=False,
        S0_after_read_resolved_conditionally=True,S0_plus60_absolute_only_after_preserving_intermediate_calls=True,
        existing_write_C_model='experiments/tsl9-v4160-contract-model/src/flash_contract.c:fc_write_registers',existing_write_model_kind='HOST provider/semantic model; not native wrapper/ABI proof',
        read_native_current_round_not_reviewed_here=True,poll_termination_or_hardware_success_proved=False,full_ABI_proved=False)
def metadata(root):
    C,decode,R,folders=context(root);ledger=read(HERE/'ledger.json');groups=ledger['groups'];blobs={}
    for k,(a,z) in RANGES.items():
        raw=b''.join(bytes.fromhex(x['raw_hex']) for x in groups[k]);bound=ledger['bounds'][k];blobs[k]=raw
        need(len(raw)==z-a and hashlib.sha256(raw).hexdigest()==bound['sha256'],'Pinned complete source '+k)
        need(C.rows(raw,a,decode)==groups[k],'Every raw source operand '+k)
    oldapp=read(folders['v4160-allocator-callback-2026-10-22/config-review']/'source-ledger.json')
    need(blobs['App_config'].hex()==oldapp['body_raw_hex'],'Unchanged308B App source')
    copy=read(folders['v4160-ota-handler-compact-2026-10-22/callee-review']/'copy-instructions.json')
    need(hashlib.sha256(b''.join(bytes.fromhex(x['raw_hex']) for x in copy)).hexdigest()=='558a82658cb54901945d4c2884f2e87e763f64d57c0cafa831307beb44ae0c36','Unchanged58B/18row conditional copy source')
    facts=gate(groups,copy)
    oldresident=read(folders['v4160-adc-caller-2026-10-22/continuation-review']/'ledger.json')
    live=[post_read_liveness(c,R,zero) for c in oldresident['candidates'].values() for zero in (False,True)]
    need(live==read(HERE/'post-read-liveness.json'),'Exact bounded CFG liveness replay')
    # Verify the numeric default premises used in the static liveness profile.
    _,_,_,_,old=R['context'](root)
    for rec in read(old/'ledger.json')['candidates']:
        ix={x['PC']:x for x in rec['rows']};e=rec['entry']
        exact(ix,e+0x76,op='addi',rd=14,rs1=0,immediate=256);exact(ix,e+0x7a,op='qk.c.sh',rs1=15,rs2=14,immediate=12)
        exact(ix,e+0x7e,op='bne',rs1=14,rs2=0,target=e+0x84)
    if (HERE/'r2-static.json').exists():
        P1=runpy.run_path(str(folders['v4160-adc-config-2026-10-22/source-review']/'r2_fields.py'))['parse'];P2=runpy.run_path(str(folders['v4160-adc-caller-2026-10-22/continuation-review']/'r2_fields.py'))['parse']
        for k,rs in read(HERE/'r2-static.json')['groups'].items():
            parsed=[]
            for x in rs:
                try:q=P1(x)
                except ValueError:q=P2(x)
                parsed.append(q)
            need(parsed==groups[k],'All independent static r2 operand fields '+k)
    return C,decode,R,folders,groups,blobs,copy,facts,live
def controls(groups,blobs,copy,C,decode):
    out=[]
    cases=[('App_config',0x19a7a,'immediate'),('App_config',0x19a88,'immediate'),('read_cb',0x1979e,'immediate'),('read_cb',0x197a6,'immediate'),('read_cb',0x197a4,'immediate'),('write_cb',0x197c4,'immediate'),('timer',0x19770,'immediate')]
    for k,pc,field in cases:
        a=RANGES[k][0];old=next(x for x in groups[k] if x['PC']==pc);chosen=None
        for bit in range(old['bytes']*8):
            raw=bytearray(blobs[k]);raw[pc-a+bit//8]^=1<<(bit%8)
            try:x=decode(raw[pc-a:],pc)
            except ValueError:continue
            keys=('PC','bytes','op','rd','rs1','rs2','immediate','target','memory_width')
            if x[field]==old[field] or any(x[z]!=old[z] for z in keys if z!=field):continue
            chosen=raw,bit,x;break
        need(chosen is not None,'Same-shape source operand mutation');raw,bit,x=chosen;changed=dict(groups);changed[k]=C.rows(raw,a,decode)
        try:gate(changed,copy)
        except ValueError as e:out.append(dict(PC=pc,field=field,bit=bit,original=old[field],mutated=x[field],raw_hex=x['raw_hex'],rejected=True,reason=str(e)));continue
        raise ValueError('Incorrect binding operand admitted')
    return out
def inspect(root,firmware=None,candidate_root=None):
    root=Path(root).resolve(strict=True)
    if (HERE/'seal.json').exists():closed(HERE,sha(HERE/'seal.json'))
    C,decode,R,folders,groups,blobs,copy,facts,live=metadata(root)
    result=dict(schema='TSL9-App-callback-frontier-binding-v1',passed=True,metadata_only=firmware is None,
        actual_original_firmware_read=False,actual_original_source_bytes=0,actual_original_source_rows=0,
        actual_candidate_HEX_files_read=0,actual_candidate_ranges_read=0,raw_controls_replayed=False,
        facts=facts,post_read_liveness=live,
        premises=['version guard reaches normal initialization; no bypass','valid frames and normal byte/word/MMIO/FENCE/return accesses','exact candidate slots and copied code if candidate projection used','preceding validation calls preserve required live SP/S0/S1 and copied input','no adverse stack/config/heap/code/MMIO aliases or asynchronous changes','polls terminate for normal write callback return'],
        config52_actual_runtime_zero_proved=False,read_generic_native_ABI_proved=False,actual_caller_A3_projection_only_conditional=True,
        normal_caller_replacement_proved=False,full_original_ABI_proved=False,installed_identity_proved=False,
        physical_NV_ownership_or_write_success_proved=False,whole_OTA_proved=False,
        old_HOST_suites_run=False,compiler_or_linker_run=False,target_or_ISA_or_ESIL_execution=False,new_BIN=False,network=False,hardware=False)
    need(candidate_root is None or firmware is not None,'Candidate input replay requires explicit original firmware')
    if firmware is not None:
        need(sha(firmware)==FW and Path(firmware).stat().st_size==76800,'Actual original official ID2966 firmware')
        raw=Path(firmware).read_bytes()
        for k,(a,z) in RANGES.items():need(C.rows(raw[a-0x8000:z-0x8000],a,decode)==groups[k],'Actual original complete source '+k)
        negative=controls(groups,blobs,copy,C,decode)
        result.update(actual_original_firmware_read=True,actual_original_source_bytes=682,actual_original_source_rows=248,raw_controls_replayed=True,raw_controls=len(negative),controls=negative)
        if candidate_root is not None:
            sources=R['actual_sources'](root,Path(candidate_root));oldresident=read(folders['v4160-adc-caller-2026-10-22/continuation-review']/'ledger.json')
            _,_,_,_,old=R['context'](root);initializers={x['candidate']:x for x in read(old/'ledger.json')['candidates']}
            for name,(take,_) in sources.items():
                for slot,value in [(0x40048,0x2000039c),(0x4004c,0x20000332)]:need(int.from_bytes(take(slot,4),'little')==value,'Actual candidate pointer-table word')
                need(C.rows(take(R['source_address'](name,0x20000332),58),0x20000332,decode)==copy,'Actual58B mapped copy')
                for k in ('fill','table_init'):
                    g=oldresident['candidates'][name]['groups'][k];a=g[0]['PC'];n=sum(x['bytes'] for x in g)
                    # Resident QK fields use the already sealed candidate decoder.
                    dec=R['context'](root)[3]
                    need(C.rows(take(R['source_address'](name,a),n),a,dec)==g,'Actual resident '+k)
                rec=initializers[name];need(C.rows(take(rec['entry'],228),rec['entry'],R['context'](root)[3])==rec['rows'],'Actual initializer record/default source')
            result.update(actual_candidate_HEX_files_read=2,actual_candidate_ranges_read=8,actual_candidate_source_bytes=984,actual_candidate_source_rows=370)
    return result
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--project-root',required=True,type=Path);p.add_argument('--firmware',type=Path);p.add_argument('--candidate-root',type=Path);a=p.parse_args();print(json.dumps(inspect(a.project_root,a.firmware,a.candidate_root)))
