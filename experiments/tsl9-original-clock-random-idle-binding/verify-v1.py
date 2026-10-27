"""Check conditional clock/random/idle routes in existing C/C++ artifacts offline."""
import argparse,hashlib,json,re,runpy,sys
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def need(ok,label):
    if not ok:raise ValueError(label)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p):return json.loads(Path(p).read_bytes())
def lib(p):return runpy.run_path(str(ROOT/p),run_name='clock_random_idle_static_library')
def canonical(v):return json.loads(json.dumps(v))

def verify(llvm):
    E=load(HERE/'evidence-v1.json')
    for key in ['reference_inputs','whole_reader_inputs']:
        need(all(sha(ROOT/p)==h for p,h in E[key].items()),'Pinned '+key)
    for p,h in [('APP_firmware','APP_sha256'),('SDK_firmware','SDK_sha256'),('primary_header','primary_header_sha256'),('SDK_native_object','SDK_native_object_sha256')]:
        need(sha(ROOT/E[p])==E[h],'Exact '+p)
    prior=lib(E['prior_study']+'/verify-v1.py')['verify'](llvm)
    need(canonical(prior)==load(ROOT/E['prior_verification']),'Fresh prior SNV/Flash/native/provenance chain')
    V=lib('experiments/tsl9-original-RF-tx-path/audit-v1.py');B=lib('experiments/tsl9-original-startup/build-v1.py')
    A=lib('experiments/tsl9-original-APP-library-binding/verify-v1.py')
    rd='experiments/tsl9-resident-root-chain-callees';O=lib(rd+'/verify-ownership-v3.py')
    native=O['inspect'](ROOT/E['SDK_native_object']);need(native['passed'],'Unique actual SDK CODE')
    sdk=(ROOT/E['SDK_firmware']).read_bytes();app=(ROOT/E['APP_firmware']).read_bytes()
    op,graphs,owners,functions={},{},{},[]
    def whole(f,domain):
        start,end=f['start'],f['end'];raw=b''.join(bytes.fromhex(o['bytes'])for o in f['operations'])
        at=f.get('source_start',start);source,base=(sdk,0x40000)if domain=='SDK'else(app,0x8000)
        need(len(raw)==end-start and raw==source[at-base:at-base+len(raw)],'Every complete original '+domain+' byte')
        if 'original_sha256'in f:need(hashlib.sha256(raw).hexdigest()==f['original_sha256'],'Exact whole-function original SHA')
        frame=max([int(m[1])for o in f['operations']if(m:=re.fullmatch(r'addi sp, sp, -(\d+)',o['opcode']))]or[0])
        ext={d[1]for o in f['operations']if(d:=B['decode_control'](bytes.fromhex(o['bytes']),o['addr']))}
        oo,g,row=V['whole_cfg'](f,B,ext,frame);need(not set(op)&set(oo),'No selected function overlap')
        op.update(oo);graphs[start]=g;owners.update({p:start for p in oo});row['domain']=domain;functions.append(row)
        if domain=='SDK':need(all(p in native['_byte_map']for p in range(start,end)),'Complete current native SDK owner')
    for scope in E['SDK_scopes']:
        need(sha(ROOT/scope['path'])==scope['sha256'],'Exact SDK scope evidence')
        selected=[f for f in load(ROOT/scope['path'])['selected_functions']if f['start']in scope['entries']]
        need(len(selected)==len(scope['entries']),'All selected complete SDK functions exist')
        for f in selected:whole(f,'SDK')
    appf=next(f for f in load(ROOT/E['APP_evidence'])['selected_functions']if f['start']==0x199e2);whole(appf,'APP')
    need(len(functions)==12 and sum(f['bytes']for f in functions if f['domain']=='SDK')==3840 and appf['end']-appf['start']==308,'Eleven SDK functions3840B plus complete APP initializer308B')
    EL=lib(rd+'/elf_reader-v7.py')['ELF'];Other=lib('analysis/v4160-irq-native-2026-10-21/compiler-review/elf32.py')['ELF']
    for mode,path in E['APP_native_diagnostic_paths'].items():
        need(sha(ROOT/path)==E['APP_native_diagnostic_sha256'],'Unchanged actual native APP diagnostic')
        e,other=EL(ROOT/path),Other(ROOT/path)
        need(e.header[0]==other.kind==2 and not any(p[0]==1 for p in e.program_headers),'Existing diagnostic has no loadable segment')
        x,a=A['native_bytes'](e,appf['start'],appf['end'],True);y,b=A['native_bytes'](other,appf['start'],appf['end'],True)
        need(x==y==app[appf['start']-0x8000:appf['end']-0x8000]and a==b,'Two native readers agree with original APP bytes')
    def exact(values):
        for p,s in values.items():need(op[p]['opcode']==s,f'Exact operand at {p:#x}: expected {s}; found {op[p]["opcode"]}')
    def dominates(site,pcs,g=None):
        root=owners[site];g=graphs[root]if g is None else g
        need(all(site not in V['reachable'](g,root,skip=p)for p in pcs),'Setup/guard dominates the actual use')
    def flow(use,definition,reg,g=None):
        root=owners[use];g=graphs[root]if g is None else g;dominates(use,[definition],g)
        rev={p:[]for p in g}
        for p,ns in g.items():
            for n in ns:rev[n].append(p)
        # Stop reverse traversal at the definition: an earlier loop iteration
        # that necessarily reloads the pointer is not a clobber of this use.
        path=sorted((V['reachable'](g,definition,skip=use)&V['reachable'](rev,use,skip=definition))|{definition})
        calls=[]
        for p in path:
            if p==definition:continue
            o=op[p]
            if o['type']in ['call','ucall']:
                need(reg.startswith('s'),'Live value across call must use saved register with explicit ABI assumption');calls.append(p)
            elif o['type']not in ['store','cjmp','jmp']:
                need(o['opcode'].partition(' ')[2].split(',')[0]!=reg,'No explicit overwrite between last definition and use')
        return dict(definition_PC=definition,use_PC=use,register=reg,path_PCs=path,
                    local_dominance_and_last_definition_proved=True,intervening_calls_require_saved_register_contract=calls)
    exact({0x199f0:'lui s0, 0x40',0x19a74:'lw a5, 124(s0)',0x19a90:'sw a5, 52(sp)',0x19aec:'jalr a5'})
    need(int.from_bytes(sdk[0x7c:0x80],'little')==0x43520,'Actual candidate slot4007C points to43520')
    seed_setup=flow(0x19a74,0x199f0,'s0');seed_store=flow(0x19a90,0x19a74,'a5')
    dominates(0x19aec,[0x19a38,0x19a90])
    stores=[A['store'](o)for p,o in op.items()if 0x199e2<=p<0x19b16 and A['store'](o)]
    need(not any(rs==2 and off<60 and 56<off+width for rs,rd,width,off in stores),'No explicit stack overwrite of zero idleCB SP56..60')
    common=['matching installed ROM profile is required and unproved','known original configuration copy and stable pointer fields',
        'valid disjoint memory and stacks','original private ABI and normal callee returns','no IRQ/reentrant overwrite']
    new=[]
    def add(site,family,target=None,slot=None,outcome='conditional-target',conditions=None,witnesses=None):
        new.append(dict(PC=site,function=owners[site],family=family,outcome=outcome,target_original_PC=target,pointer_slot=slot,
            conditions=common+(conditions or []),witnesses=witnesses or {},live_binding_proved=False))
    clocks=[(0x58cf2,0x58cc2,'s3',0x58cea,564),(0x58e0a,0x58c66,'s5',0x58dfe,564),
        (0x58e4a,0x58c66,'s5',0x58dfe,564),(0x64e50,0x64e48,'a5',0x64e4c,480),
        (0x20000560,0x20000528,'s5',0x2000055c,480),(0x2000067a,0x20000672,'s2',0x20000676,480),
        (0x20000686,0x20000672,'s2',0x20000680,480),(0x200006ca,0x200006be,'a5',0x200006c2,480),
        (0x20000770,0x200006be,'a5',0x200006c2,480),(0x20002d62,0x20002d4c,'a5',0x20002d50,480)]
    for site,base,reg,load_pc,off in clocks:
        exact({base:'lui '+reg+', 0x20003',load_pc:f'lw a5, {off}({reg})',site:'jalr a5'})
        add(site,'raw-clock',0x191c6,0x20003000+off,conditions=['after accepted original nonnull clock configuration; does not prove order before every call'],
            witnesses=dict(base=flow(load_pc,base,reg),pointer=flow(site,load_pc,'a5')))
    exact({0x433c0:'lui a5, 0x20003',0x433c4:'lw a5, 528(a5)',0x433d0:'beqz a5, 0x433dc',0x433d2:'jalr a5',
        0x433d4:'lw a5, 0(s0)',0x433d6:'add a0, a0, a5',0x433d8:'sw a0, 0(s0)',0x433da:'j 0x433e6',
        0x433dc:'lui a5, 0x20003',0x433e0:'lw a5, 480(a5)',0x433e4:'bnez a5, 0x433d2',
        0x433c8:'lui s0, 0x20003',0x433cc:'addi s0, s0, -312',0x433e6:'lw a5, 0(s0)',
        0x433e8:'lui a4, 0x34',0x433ec:'addi a4, a4, 1021',0x433f0:'mul a5, a5, a4',
        0x433f4:'lui a4, 0x26a',0x433f8:'addi a4, a4, -317',0x433fe:'add a5, a5, a4',
        0x43400:'sw a5, 0(s0)',0x4340a:'lw a0, 0(s0)'})
    g={p:list(ns)for p,ns in graphs[0x433a8].items()};need(g[0x433d0]==[0x433dc,0x433d2],'Original primary-seed guard polarity')
    g[0x433d0]=[0x433d2] # Known nonzero43520 in this domain only.
    seed_flow=flow(0x433d2,0x433c4,'a5',g)
    add(0x433d2,'configured-seed',0x43520,0x20003210,
        conditions=['post-known BLE copy: original srandCB is nonzero43520 from candidate4007C',
            'this target does not require prior successful clock configuration; provider slot3230 has its own guard',
            'zero-primary fallback is a different configuration domain'],
        witnesses=dict(APP_slot_load=seed_setup,APP_field_store=seed_store,known_nonzero_domain_pointer=seed_flow))
    exact({0x43524:'lw a5, 560(a5)',0x43536:'beqz a5, 0x43540',0x43538:'jalr a5',0x4353a:'lw a5, 20(s0)',
        0x4353c:'add a0, a0, a5',0x4353e:'sw a0, 20(s0)',0x43540:'lw a0, 20(s0)',0x43d7a:'jalr a5'})
    need(0x43538 not in V['reachable'](graphs[0x43520],0x43540),'Zero provider guard skips nested call without assuming initialized clock')
    status=[(0x6537c,0x6536c,0x65370,0x65374,0x6537e),(0x655f6,0x655e6,0x655ea,0x655ee,0x655f8)]
    for site,base,load_pc,guard,zero in status:
        exact({base:'lui a5, 0x20003',load_pc:'lw a5, 544(a5)',guard:f'beqz a5, {hex(zero)}',site:'jalr a5'})
        dominates(site,[guard,load_pc]);need(graphs[owners[site]][guard][0]==zero and site not in V['reachable'](graphs[owners[site]],zero),'Post-copy zero status branch skips the call')
        add(site,'status-zero',slot=0x20003220,outcome='conditional-skipped',conditions=['post-known BLE copy: staCB remains zero at guard; earlier heap-call value remains unproved'],
            witnesses=dict(guard_PC=guard,zero_branch=zero,base=flow(load_pc,base,'a5'),pointer=flow(site,load_pc,'a5')))
    exact({0x20000874:'lui a5, 0x20003',0x20000878:'lw a5, 532(a5)',0x2000087c:'beqz a5, 0x2000094e',
        0x200008be:'j 0x2000061a',0x20000716:'lui a5, 0x20003',0x2000071a:'lw a5, 532(a5)',0x2000071e:'jalr a5'})
    dominates(0x200008be,[0x20000878,0x2000087c])
    need(0x200008be not in V['reachable'](graphs[0x200007d0],0x2000094e),'Scheduler zero-idle branch cannot reach its idle tail')
    add(0x2000071e,'idle-caller-gate',slot=0x20003214,outcome='conditional-skipped-via-caller',conditions=[
        'post-known BLE copy idleCB remains zero at SystemProcess guard2000087C',
        'scope is ONLY entry through SystemProcess200007D0 and its idle tail200008BE',
        'idle service itself has no local null guard; other callers or nonzero idleCB are not resolved'],
        witnesses=dict(caller=0x200007d0,guard_PC=0x2000087c,zero_branch=0x2000094e,tail_PC=0x200008be,
            internal_base=flow(0x2000071a,0x20000716,'a5'),internal_pointer=flow(0x2000071e,0x2000071a,'a5'),local_null_guard_present=False))
    inherited=load(ROOT/E['old_ledger'])['rows']
    flash=[dict(r,conditions=prior['contract']['conditions'],source=E['prior_verification'])for r in prior['contract']['conditional_new_bindings']]
    allrows=inherited+flash+new;all_sites={s['PC']for s in load(ROOT/E['whole_inventory'])['register_transfer_sites_requiring_separate_binding_analysis']}
    need(len(new)==14 and len(allrows)==len({r['PC']for r in allrows})==35 and {r['PC']for r in allrows}<=all_sites and len(all_sites)==51,'Fourteen distinct new joins plus twenty-one retained joins')
    rest=sorted(all_sites-{r['PC']for r in allrows});need(len(rest)==16,'Sixteen remaining sites; no missing-function inference')
    ledger=dict(schema='TSL9-clock-random-idle-cumulative-ledger-v1',passed=True,rows=sorted(allrows,key=lambda r:r['PC']),
        other_sites=[dict(PC=p,outcome='not-joined-in-this-ledger',prior_proofs_not_overridden=True)for p in rest],
        counts=dict(actual_register_sites=51,conditionally_joined=35,conditional_target=27,conditional_skipped_or_caller_gated=8,not_joined_here=16),
        new_families=dict(raw_clock=10,configured_seed=1,status_zero=2,idle_caller_gate=1),
        no_universal_or_live_binding_claim=True,missing_function_count_not_inferred=True)
    contract=dict(passed=True,original_srandCB=dict(slot=0x4007c,candidate_value=0x43520,APP_load=0x19a74,APP_store=0x19a90,field_offset=36,SDK_slot=0x20003210),
        original_idleCB=dict(field_offset=40,own_stack_span=[56,60],conditional_post_copy_value=0,SDK_slot=0x20003214),
        random=dict(seed_slot=0x20002ec8,multiplier=0x34000+1021,increment=0x26a000-317,
            after_callback='(fresh_seed_word_after_callback + callback_A0) modulo 2^32',
            result='(updated_seed_word * 214013 + 2531011) modulo 2^32',
            configured_callback_target=0x43520,zero_primary_can_fall_back_to_raw_clock=True,
            provider_zero_domain_returns_stored_word31B0_without_nested_call=True,
            provider_nonzero_registered_domain='43520 -> 43D62 -> 191C6 under prior registration/clock conditions',
            initial_seed_value_or_entropy_or_cryptographic_quality_proved=False,
            MMIO4002420C_and_FENCEI_do_not_prove_physical_IRQ_atomicity=True),
        idle_local_null_guard_present=False,idle_protection_only_proved_in_known_caller_domain=True,
        original_clock_config_precedes_every_call_proved=False,earlier_status_or_idle_values_proved=False)
    need(contract['random']['multiplier']==214013 and contract['random']['increment']==2531011,'Exact observed unsigned recurrence constants')
    return dict(schema='TSL9-clock-random-idle-binding-verification-v1',passed=True,checker_sha256=sha(__file__),evidence_sha256=sha(HERE/'evidence-v1.json'),
        contract=contract,ledger=ledger,whole_functions=functions,SDK_reference_CODE_bytes=3840,APP_reference_CODE_bytes=308,
        reference_instructions=sum(f['instructions']for f in functions),prior_composition=prior['prior_composition'],
        APP_source_C_H_files_unchanged=159,APP_byte_coverage_unchanged=95.54,new_target_CODE_bytes=0,new_target_DATA_bytes=0,new_target_compilation=False,
        inherited_startup_source_gap_bytes=4,physical_compatibility_proved=False,Flash_callback_effects_closed=False,
        actual_global_binding_before_any_dispatch_proved=False,runtime_closed=False,new_BIN=False,firmware_ready=False,goal_complete=False,
        target_executed=False,HOST_model_executed=False,ISA_emulated=False,hardware_accessed=False,network=False)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--tool-dir',type=Path,required=True);p.add_argument('--write-receipts',action='store_true');a=p.parse_args()
    try:
        v=verify(a.tool_dir.resolve())
        if a.write_receipts:
            for name,value in [('ledger-v1.json',v['ledger']),('verification-v1.json',v)]:
                dest=HERE/name;need(not dest.exists(),'Create-only clock/random/idle receipt');dest.write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8')
        print(json.dumps(dict(passed=True,**v['ledger']['counts'],new_conditional_sites=14,reference_instructions=v['reference_instructions'],new_BIN=False,firmware_ready=False)))
    except Exception as error:
        message=str(error)
        for path,token in [(ROOT,'${PROJECT_ROOT}'),(Path.home(),'${USERPROFILE}')]:message=message.replace(str(path),token).replace(path.as_posix(),token)
        print(json.dumps(dict(passed=False,error_type=type(error).__name__,reason=message)));raise SystemExit(1)
