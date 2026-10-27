"""Trace original APP task registration/table dispatch and event returns offline."""
import argparse,hashlib,json,re,runpy,sys
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def need(ok,label):
    if not ok:raise ValueError(label)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p):return json.loads(Path(p).read_bytes())
def lib(p):return runpy.run_path(str(ROOT/p),run_name='APP_task_static_library')
def canonical(v):return json.loads(json.dumps(v))
def verify(llvm):
    E=load(HERE/'evidence-v1.json')
    need(all(sha(ROOT/p)==h for p,h in E['reference_inputs'].items())and all(sha(ROOT/p)==h for p,h in E['whole_reader_inputs'].items()),'All exact prior source/native/reader references')
    for p,h in [('APP_firmware','APP_sha256'),('SDK_firmware','SDK_sha256'),('SDK_native_object','SDK_native_object_sha256'),('primary_header','primary_header_sha256')]:need(sha(ROOT/E[p])==E[h],'Pinned '+p)
    prior=lib(E['prior_study']+'/audit-v1.py')['audit'](llvm);need(canonical(prior)==load(ROOT/E['prior_receipt']),'Fresh prior sparse-data/native/callback proof')
    abi=lib('experiments/tsl9-original-APP-task-binding/build-v1.py')['replay'](llvm)
    V=lib('experiments/tsl9-original-RF-tx-path/audit-v1.py');B=lib('experiments/tsl9-original-startup/build-v1.py');A=lib('experiments/tsl9-original-APP-library-binding/verify-v1.py')
    rd='experiments/tsl9-resident-root-chain-callees/';O=lib(rd+'verify-ownership-v3.py');native=O['inspect'](ROOT/E['SDK_native_object']);need(native['passed'],'Unique real SDK CODE')
    app=(ROOT/E['APP_firmware']).read_bytes();sdk=(ROOT/E['SDK_firmware']).read_bytes();op,graphs,owners,functions={},{},{},[]
    for scope in E['source_scopes']:
        need(sha(ROOT/scope['path'])==scope['sha256'],'Exact selected evidence scope')
        selected=[f for f in load(ROOT/scope['path'])[scope['key']]if f['start']in scope['entries']];need(len(selected)==len(scope['entries']),'All whole scopes exist')
        for f in selected:
            start,end=f['start'],f['end'];raw=b''.join(bytes.fromhex(o['bytes'])for o in f['operations']);at=f.get('source_start',start)
            source,base=(app,0x8000)if scope['domain']=='APP'else(sdk,0x40000)
            need(len(raw)==end-start and raw==source[at-base:at-base+len(raw)],'Every original whole-function byte')
            if 'original_sha256'in f:need(hashlib.sha256(raw).hexdigest()==f['original_sha256'],'Original whole-function hash')
            frame=max([int(m[1])for o in f['operations']if(m:=re.fullmatch(r'addi sp, sp, -(\d+)',o['opcode']))]or[0])
            ext={d[1]for o in f['operations']if(d:=B['decode_control'](bytes.fromhex(o['bytes']),o['addr']))}
            oo,g,row=V['whole_cfg'](f,B,ext,frame);need(not set(op)&set(oo),'Disjoint selected whole functions')
            op.update(oo);graphs[start]=g;owners.update({p:start for p in oo});row['domain']=scope['domain'];functions.append(row)
            if scope['domain']=='SDK':need(all(p in native['_byte_map']for p in range(start,end)),'Every selected SDK byte has actual current native owner')
    appfs=[f for f in functions if f['domain']=='APP'];sdkfs=[f for f in functions if f['domain']=='SDK']
    need(len(appfs)==5 and len(sdkfs)==7 and sum(f['bytes']for f in appfs)==896 and sum(f['bytes']for f in sdkfs)==1536,'Five APP896B and seven SDK1536B complete functions')
    EL=lib(rd+'elf_reader-v7.py')['ELF'];Other=lib('analysis/v4160-irq-native-2026-10-21/compiler-review/elf32.py')['ELF']
    for mode,path in E['APP_native_diagnostic_paths'].items():
        need(sha(ROOT/path)==E['APP_native_diagnostic_sha256'],'Exact existing nonloadable APP witness');e,other=EL(ROOT/path),Other(ROOT/path)
        need(e.header[0]==other.kind==2 and not any(p[0]==1 for p in e.program_headers),'APP diagnostic is not loadable firmware')
        for f in appfs:
            x,a=A['native_bytes'](e,f['start'],f['end'],True);y,b=A['native_bytes'](other,f['start'],f['end'],True)
            need(x==y==app[f['start']-0x8000:f['end']-0x8000]and a==b,'Two native readers equal every original selected APP byte')
    def exact(values):
        for p,s in values.items():need(op[p]['opcode']==s,f'Exact APP task operand at {p:#x}: expected {s}; found {op[p]["opcode"]}')
    def dom(root,site,pcs):need(all(site not in V['reachable'](graphs[root],root,skip=p)for p in pcs),'Complete CFG argument/initialization dominance')
    def slot(off):return int.from_bytes(sdk[off:off+4],'little')
    exact({0x8ea8:'jal ra, 0x199e2',0x8eac:'jal ra, 0x19b16',0x19b1a:'lui s1, 0x40',0x19b1e:'lw a5, 128(s1)',
        0x19b2e:'jalr a5',0x19b30:'addi s0, gp, 388',0x19b34:'sb a0, 0(s0)',0x19b3a:'lbu a0, 0(s0)',
        0x19b40:'lw t1, 88(s1)',0x19b48:'lui a2, 0x2f',0x19b4c:'addi a2, a2, -512',0x19b50:'lui a1, 0x2',
        0x19b52:'addi sp, sp, 16',0x19b54:'jr t1'})
    need(A['address_pair'](op,0x19b26)==0x1995c and slot(0x80)==0x43c4e and slot(0x58)==0x43728,'Actual original callback literal and candidate registration/start slots')
    dom(0x8e88,0x8eac,[0x8ea8])
    dom(0x19b16,0x19b2e,[0x19b1e,0x19b26,0x19b2a]);dom(0x19b16,0x19b54,[0x19b34,0x19b3a,0x19b40,0x19b52])
    exact({0x43b90:'lbu a5, 513(a5)',0x43b9a:'srli a0, a5, 0x2',0x43b9e:'andi a5, a5, 3',0x43ba0:'add a0, a0, a5',
        0x43ba2:'li a5, 3',0x43ba4:'mul a0, a0, a5',0x43ba8:'li a5, 6',0x43bae:'addi a0, a0, 14',0x43bb0:'andi a0, a0, 255',
        0x43bb4:'qk.c.sb a0, 2(s0)',0x43bb6:'mul a0, a0, a5',0x43bba:'addi a0, a0, 576',
        0x43be2:'lw a5, 556(s1)',0x43be6:'qk.c.lbu a4, 2(s0)',0x43be8:'lui s1, 0x20003',0x43bec:'addi a5, a5, 576',0x43bf0:'slli a4, a4, 0x2',
        0x43bf2:'sw a5, 452(s1)',0x43bf6:'add a5, a5, a4',0x43bfc:'sw a5, 484(a4)',
        0x43c06:'qk.c.lbu a5, 1(s0)',0x43c08:'lw a3, 452(s1)',0x43c0c:'lui a2, 0x43',0x43c16:'addi a2, a2, 676',
        0x43c10:'slli a4, a5, 0x2',0x43c14:'add a4, a4, a3',0x43c1a:'sw a2, 0(a4)',0x43c1c:'addi a4, a5, 1',
        0x43c20:'andi a4, a4, 255',0x43c24:'slli a4, a4, 0x2',0x43c26:'lui a2, 0x43',0x43c2a:'add a4, a4, a3',0x43c2c:'addi a2, a2, 806',
        0x43c30:'sw a2, 0(a4)',0x43c32:'addi a4, a5, 3',0x43c36:'addi a5, a5, 2',0x43c38:'andi a5, a5, 255',
        0x43c3c:'slli a5, a5, 0x2',0x43c3e:'qk.c.sb a4, 1(s0)',0x43c40:'add a5, a5, a3',0x43c42:'sw a2, 0(a5)'})
    need(0x43000+676==0x432a4 and 0x43000+806==0x43326,'Exact three internal handler literals')
    alloc=load(ROOT/E['allocation_proof'])['contract'];need(alloc['passed']and alloc['algebraic_count_bounds']==[14,212]and not alloc['allocation_capacity_ownership_lifetime_or_initialization_success_proved'],'Retain prior conditional allocation and its physical/capacity limits')
    need(3*(63+3)+14==212 and 3*0+14==14 and 4*4<=4*14 and 2*4<=2*14,'Encoded byte expression bounds and first-four suffix widths')
    exact({0x43c4e:'lui a4, 0x20003',0x43c52:'addi a4, a4, 412',0x43c56:'qk.c.lbu a5, 1(a4)',
        0x43c58:'qk.c.lbu a3, 2(a4)',0x43c5a:'bleu a3, a5, 0x43c78',0x43c62:'lw a3, 452(a3)',
        0x43c66:'addi a2, a5, 1',0x43c6a:'qk.c.sb a2, 1(a4)',0x43c6c:'slli a4, a5, 0x2',
        0x43c70:'add a4, a4, a3',0x43c72:'sw a0, 0(a4)',0x43c74:'mv a0, a5',0x43c78:'li a5, 255'})
    need(graphs[0x43c4e][0x43c5a]==[0x43c78,0x43c5e],'Capacity<=count rejects without handler store')
    dom(0x43c4e,0x43c72,[0x43c56,0x43c58,0x43c5a,0x43c62,0x43c6a])
    exact({0x200008e4:'slli a5, a5, 0x1',0x200008e8:'qk.c.lhu a1, 0(a4)',0x200008ea:'sh zero, 0(a4)',
        0x200008ee:'lbu a0, 412(s0)',0x200008f2:'lui a5, 0x20003',0x200008f6:'lw a5, 452(a5)',0x200008fa:'slli a4, a0, 0x2',
        0x20000902:'add a5, a5, a4',0x20000904:'lw a5, 0(a5)',0x20000906:'sh zero, 476(s5)',0x2000090a:'jalr a5',
        0x2000090c:'lhu a5, 476(s5)',0x20000910:'lbu a4, 412(s0)',0x20000914:'not a5, a5',0x20000918:'and a0, a0, a5',
        0x2000091a:'slli a5, a4, 0x1',0x2000091e:'lw a4, 484(s3)',0x20000924:'qk.c.lhu a5, 0(a4)',
        0x20000926:'or a0, a0, a5',0x20000928:'qk.c.sh a0, 0(a4)'})
    dom(0x200007d0,0x2000090a,[0x200008e8,0x200008ea,0x200008ee,0x200008f6,0x20000904,0x20000906])
    exact({0x1995e:'slli a5, a1, 0x10',0x19968:'srai a5, a5, 0x10',0x1996a:'mv s0, a1',0x1996c:'bgez a5, 0x1998c',
        0x19970:'lui s1, 0x40',0x19974:'lw a5, 108(s1)',0x19976:'jalr a5',0x19978:'beqz a0, 0x1997e',0x1997a:'lw a5, 104(s1)',0x1997c:'jalr a5',
        0x1997e:'lui a0, 0x8',0x19980:'xor a0, a0, s0',0x1998c:'andi a5, a1, 1',0x19990:'xori a0, a1, 1',
        0x19994:'bnez a5, 0x19982',0x19996:'slli a5, a1, 0x12',0x1999a:'bgez a5, 0x199c2',0x1999e:'lui s1, 0x40',0x199a2:'lw a5, 492(s1)',
        0x199a6:'jalr a5',0x199a8:'jal ra, 0x197b8',0x199ac:'lw a5, 88(s1)',0x199ae:'lui a2, 0x2f',0x199b2:'addi a2, a2, -512',
        0x199b6:'lui a1, 0x2',0x199b8:'lbu a0, 388(gp)',0x199bc:'jalr a5',0x199be:'lui a0, 0x2',0x199c0:'j 0x19980',
        0x199c2:'slli a5, a1, 0x11',0x199c6:'li a0, 0',0x199c8:'bgez a5, 0x19982',0x199cc:'lui a5, 0x40',0x199d0:'lw a5, 88(a5)',
        0x199d2:'li a2, 1600',0x199d6:'lui a1, 0x4',0x199d8:'lbu a0, 388(gp)',0x199dc:'jalr a5',0x199de:'lui a0, 0x4',0x199e0:'j 0x19980',
        0x197b8:'li a0, 3',0x197ba:'j 0x1929a'})
    expected={0x80:0x43c4e,0x58:0x43728,0x6c:0x2000028c,0x68:0x431ba,0x1ec:0x641b0}
    need(all(slot(off)==target and target in native['_byte_map']for off,target in expected.items()),'All actual original APP API slots have real current candidate CODE')
    handler_g=graphs[0x1995c]
    need(handler_g[0x1996c]==[0x1998c,0x19970]and handler_g[0x19994]==[0x19982,0x19996]
         and handler_g[0x1999a]==[0x199c2,0x1999e]and handler_g[0x199c8]==[0x19982,0x199cc],'Original event priority and branch polarity')
    dom(0x1995c,0x199bc,[0x199a6,0x199a8,0x199ac,0x199b8]);dom(0x1995c,0x199dc,[0x199d0,0x199d2,0x199d8])
    conditions=['matching installed ROM profile is required and unproved','valid disjoint allocation satisfying576+6*n with stable n/p across allocation,clear,partition and dispatch',
        'internal initializer count at43C06 is0; no intervening registration or overwrite before original APP registration',
        'original register/task/heap ABI and valid original APP GP+388 context','normal callee returns with no IRQ/reentrant table or index replacement',
        'known initializer and APP call sequence is conditional; global-before-every-dispatch is unproved']
    row=dict(PC=0x2000090a,family='initialized-task-handler-table',outcome='conditional-target-set',pointer_table_base_slot=0x200031c4,
        conditional_targets_by_task_ID={'0':0x432a4,'1':0x43326,'2':0x43326,'3':0x1995c},table_stride=4,conditions=conditions,
        live_binding_proved=False,handler_count_before_APP_registration=3,handler_count_after_accepted_registration=4)
    old=load(ROOT/E['prior_ledger']);need(row['PC']in {r['PC']for r in old['other_sites']}and len(old['rows'])==35,'One distinct new SDK site')
    ledger=dict(schema='TSL9-original-APP-task-cumulative-ledger-v1',passed=True,rows=sorted(old['rows']+[row],key=lambda r:r['PC']),
        other_sites=[r for r in old['other_sites']if r['PC']!=row['PC']],
        counts=dict(actual_register_sites=51,conditionally_joined=36,conditional_target_or_target_set=28,conditional_skipped_or_caller_gated=8,not_joined_here=15),
        new_APP_API_bindings_not_in_SDK_51=[dict(PC=p,slot=0x40000+off,target=expected[off])for p,off in [(0x19b2e,0x80),(0x19b54,0x58),(0x19976,0x6c),(0x1997c,0x68),(0x199a6,0x1ec),(0x199bc,0x58),(0x199dc,0x58)]],
        no_universal_or_live_binding_claim=True,missing_function_count_not_inferred=True)
    contract=dict(passed=True,conditions=conditions,registration=dict(APP_callback=0x1995c,APP_site=0x19b2e,candidate_API=0x43c4e,
        conditional_task_ID=3,capacity_bounds=[14,212],rejection_value=255,rejection_not_checked_by_APP_before_scheduling=True,
        handler_array_slot=0x200031c4,handler_index_stride=4,APP_task_ID_storage='original GP+388'),
        suffix_bounds=dict(handlers_first4_bytes=16,handler_array_min_bytes=56,events_first4_bytes=8,event_array_min_bytes=28,
            conditional_numeric_bounds_proved=True,actual_allocation_capacity_or_ownership_proved=False),
        event_priority=[dict(mask=0x8000,effect='receive; deallocate only if nonnull',return_value='events XOR0x8000'),
            dict(mask=1,effect='acknowledge',return_value='events XOR1'),
            dict(mask=0x2000,effect='candidate641B0; calibration197B8; reschedule same bit',raw_delay=0x2ee00,return_value='events XOR0x2000'),
            dict(mask=0x4000,effect='reschedule same bit',raw_delay=1600,return_value='events XOR0x4000')],
        unmatched_bits_normal_return=0,entry_events_domain='zero-extended16-bit from original scheduler',one_priority_arm_per_invocation=True,
        initial_schedule=dict(site=0x19b54,tail=True,mask=0x2000,raw_delay=0x2ee00,physical_time_units_proved=False),
        callback_reschedule_or_calibration_success_proved=False,all_remaining_callee_effects_proved=False,
        scheduler_return_store='low16((returned_A0 & ~fresh_clear_mask) | fresh_pending_events) at freshly reread task index',
        return_applied_to_original_task_when_index_changes_proved=False,public_ABI_shape_only=True)
    return dict(schema='TSL9-original-APP-task-binding-verification-v1',passed=True,checker_sha256=sha(__file__),builder_sha256=sha(HERE/'build-v1.py'),
        evidence_sha256=sha(HERE/'evidence-v1.json'),ABI=abi,contract=contract,ledger=ledger,whole_functions=functions,
        APP_reference_CODE_bytes=896,SDK_reference_CODE_bytes=1536,reference_instructions=sum(f['instructions']for f in functions),
        composition=prior['composition']['c'],new_target_CODE_bytes=0,new_target_DATA_bytes=0,numeric_ABI_compilation_only=True,
        APP_source_C_H_files_unchanged=159,APP_byte_coverage_unchanged=95.54,inherited_startup_source_gap_bytes=4,
        installed_ROM_identity_proved=False,physical_RAM_ISA_IRQ_or_Flash_compatibility_proved=False,
        actual_global_binding_before_any_dispatch_proved=False,linked_into_APP=False,runtime_closed=False,new_BIN=False,firmware_ready=False,goal_complete=False,
        target_executed=False,HOST_model_executed=False,ISA_emulated=False,hardware_accessed=False,network=False)
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--tool-dir',type=Path,required=True);p.add_argument('--write-receipts',action='store_true');a=p.parse_args()
    try:
        v=verify(a.tool_dir.resolve())
        if a.write_receipts:
            for name,value in [('ledger-v1.json',v['ledger']),('verification-v1.json',v)]:
                dest=HERE/name;need(not dest.exists(),'Create-only APP task receipt');dest.write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8')
        print(json.dumps(dict(passed=True,**v['ledger']['counts'],new_APP_API_sites=7,reference_instructions=v['reference_instructions'],conditional_APP_task_ID=3,new_BIN=False,firmware_ready=False)))
    except Exception as error:
        message=str(error)
        for path,token in [(ROOT,'${PROJECT_ROOT}'),(Path.home(),'${USERPROFILE}')]:message=message.replace(str(path),token).replace(path.as_posix(),token)
        print(json.dumps(dict(passed=False,error_type=type(error).__name__,reason=message)));raise SystemExit(1)
