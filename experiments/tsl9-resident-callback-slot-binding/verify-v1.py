"""Trace seven literal callback installations and exact conditional clear semantics."""
import argparse,hashlib,json,re,runpy,sys
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def need(ok,label):
    if not ok:raise ValueError(label)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p):return json.loads(Path(p).read_bytes())
def lib(p):return runpy.run_path(str(ROOT/p),run_name='callback_slot_static_library')
def canonical(v):return json.loads(json.dumps(v))
def verify(llvm):
    E=load(HERE/'evidence-v1.json')
    need(all(sha(ROOT/p)==h for p,h in E['reference_inputs'].items())and all(sha(ROOT/p)==h for p,h in E['whole_reader_inputs'].items()),'Exact prior sources,native receipts and readers')
    for p,h in [('SDK_firmware','SDK_sha256'),('SDK_native_object','SDK_native_object_sha256')]:need(sha(ROOT/E[p])==E[h],'Exact '+p)
    prior=lib(E['prior_study']+'/verify-v1.py')['verify'](llvm);need(canonical(prior)==load(ROOT/E['prior_receipt']),'Fresh complete prior APP/native/ABI chain')
    V=lib('experiments/tsl9-original-RF-tx-path/audit-v1.py');B=lib('experiments/tsl9-original-startup/build-v1.py')
    O=lib('experiments/tsl9-resident-root-chain-callees/verify-ownership-v3.py');native=O['inspect'](ROOT/E['SDK_native_object']);need(native['passed'],'Unique actual SDK CODE')
    sdk=(ROOT/E['SDK_firmware']).read_bytes();op,graphs,owners,functions={},{},{},[]
    for scope in E['SDK_scopes']:
        need(sha(ROOT/scope['path'])==scope['sha256'],'Exact selected SDK scope')
        fs=[f for f in load(ROOT/scope['path'])['selected_functions']if f['start']in scope['entries']];need(len(fs)==len(scope['entries']),'All requested complete functions')
        for f in fs:
            start,end=f['start'],f['end'];raw=b''.join(bytes.fromhex(o['bytes'])for o in f['operations']);at=f.get('source_start',start)
            need(len(raw)==end-start and raw==sdk[at-0x40000:at-0x40000+len(raw)]and hashlib.sha256(raw).hexdigest()==f['original_sha256'],'Every actual original whole-function byte')
            need(all(p in native['_byte_map']for p in range(start,end)),'Complete current native owner for every selected byte')
            frame=max([int(m[1])for o in f['operations']if(m:=re.fullmatch(r'addi sp, sp, -(\d+)',o['opcode']))]or[0])
            ext={d[1]for o in f['operations']if(d:=B['decode_control'](bytes.fromhex(o['bytes']),o['addr']))}
            oo,g,row=V['whole_cfg'](f,B,ext,frame);need(not set(op)&set(oo),'Disjoint complete selected functions')
            op.update(oo);graphs[start]=g;owners.update({p:start for p in oo});functions.append(row)
    need(len(functions)==17 and sum(f['bytes']for f in functions)==5602,'Seventeen complete original SDK functions5602B')
    def exact(values):
        for p,s in values.items():need(op[p]['opcode']==s,f'Exact callback-slot operand at {p:#x}: expected {s}; found {op[p]["opcode"]}')
    def dom(site,pcs):
        for p in pcs:need(site not in V['reachable'](graphs[owners[site]],owners[site],skip=p),f'Complete CFG dominance: {p:#x} before {site:#x}')
    def flow(use,definition,reg):
        root=owners[use];g=graphs[root];dom(use,[definition]);rev={p:[]for p in g}
        for p,ns in g.items():
            for n in ns:rev[n].append(p)
        path=sorted((V['reachable'](g,definition,skip=use)&V['reachable'](rev,use,skip=definition))|{definition})
        for p in path:
            if p==definition:continue
            o=op[p]
            if o['type']in ['call','ucall']:need(reg.startswith('s'),'Cross-callee value needs saved-register assumption')
            elif o['type']not in ['store','cjmp','jmp']:need(o['opcode'].partition(' ')[2].split(',')[0]!=reg,'No explicit clobber before use')
        return dict(definition_PC=definition,use_PC=use,register=reg,path_PCs=path,last_definition_preserved=True)
    def pair(pc,rd):
        hi=int.from_bytes(bytes.fromhex(op[pc]['bytes']),'little');lo=int.from_bytes(bytes.fromhex(op[pc+4]['bytes']),'little')
        need(op[pc]['size']==op[pc+4]['size']==4 and hi&127==0x17 and lo&0x707f==0x67 and(hi>>7)&31==(lo>>15)&31 and(lo>>7)&31==rd,'Actual far pair register/link role')
        imm=lo>>20;imm=imm-4096 if imm&2048 else imm;return(pc+(hi&0xfffff000)+imm)&0xfffffffe
    def literal(hi_pc,lo_pc):
        h=int.from_bytes(bytes.fromhex(op[hi_pc]['bytes']),'little');l=int.from_bytes(bytes.fromhex(op[lo_pc]['bytes']),'little')
        need(op[hi_pc]['size']==op[lo_pc]['size']==4 and h&127==0x37 and(h>>7)&31==10 and l&0x707f==0x13 and(l>>7)&31==(l>>15)&31==10,'Independent original A0 LUI/ADDI literal')
        imm=l>>20;imm=imm-4096 if imm&2048 else imm;return((h&0xfffff000)+imm)&0xffffffff
    reaching_cache={}
    def reaching_A0(site):
        root=owners[site]
        if root not in reaching_cache:
            g=graphs[root];incoming={p:set()for p in g};incoming[root].add(-1);pending=[root]
            pure_control={'beq','beqz','bgez','bleu','bltu','bltz','bne','bnez','j','jr','ret','fence.i','nop'}
            stores={'sb','sh','sw','qk.c.sb'}
            single_result={'add','addi','and','andi','auipc','divu','lb','lbu','li','lui','lw','mv','or','ori','qk.c.lbu','qk.c.lbusp','remu','slli','srai','srli','sub'}
            def writes_A0(o):
                mnemonic=o['opcode'].split()[0]
                if o['type']in ['call','ucall']or mnemonic in ['jal','jalr']:return True
                if mnemonic in pure_control|stores:return False
                need(mnemonic in single_result,'No unmodelled implicit register writer in reaching-definition scope')
                return o['opcode'].partition(' ')[2].split(',')[0]=='a0'
            # Finite forward may-reaching-definitions, not concrete execution.
            # Calls conservatively clobber A0; joins union definition PCs.
            while pending:
                pc=pending.pop();out={pc}if writes_A0(op[pc])else incoming[pc]
                for n in g[pc]:
                    before=len(incoming[n]);incoming[n]|=out
                    if len(incoming[n])!=before:pending.append(n)
            reaching_cache[root]=incoming
        return reaching_cache[root][site]
    producers=[];expected_definitions={}
    for hi,lo,call,target in [(0x6452c,0x64530,0x64534,0x645dc),(0x6494e,0x64954,0x64962,0x65de6),
        (0x64e86,0x64e8a,0x64e8e,0x6448e),(0x64ef6,0x64efa,0x64e8e,0x64422),
        (0x650fa,0x650fe,0x65102,0x653a0),(0x6515a,0x6515e,0x65102,0x65164),(0x65500,0x65504,0x65508,0x65620)]:
        need(literal(hi,lo)==target and pair(call,1)==0x2000078a and target in graphs,'Actual literal target,normal registration call and complete real target body')
        source_path=flow(lo,hi,'a0');need(lo in reaching_A0(call),'Literal definition reaches original registration call without another A0 definition')
        expected_definitions.setdefault(call,set()).add(lo)
        producers.append(dict(caller=owners[call],literal_PCs=[hi,lo],call_PC=call,setter=0x2000078a,target_original_PC=target,
            constant_source_path=source_path,A0_reaching_definition_PC=lo,call_reaching_A0_definitions=sorted(reaching_A0(call))))
    need(all(reaching_A0(call)==defs for call,defs in expected_definitions.items()),'Every reaching A0 definition at these five call sites is one of the seven decoded literals')
    exact({0x2000078a:'lui a5, 0x20003',0x2000078e:'sw a0, -264(a5)',0x20000792:'beqz a0, 0x2000079e',
        0x20000794:'lui a5, 0x20003',0x20000798:'li a4, 1',0x2000079a:'sb a4, -260(a5)',
        0x200007a0:'lui a5, 0x20003',0x200007a4:'lw a4, -264(a5)',0x200007ae:'addi s0, a5, -264',
        0x200007b2:'beqz a4, 0x200007b6',0x200007b4:'jalr a4',0x200007b6:'lui a5, 0x20003',
        0x200007ba:'lbu a5, -260(a5)',0x200007be:'andi a5, a5, 255',0x200007c2:'bnez a5, 0x200007c8',0x200007c4:'sw zero, 0(s0)'})
    need(graphs[0x2000078a][0x20000792]==[0x2000079e,0x20000794]and 0x2000079a not in V['reachable'](graphs[0x2000078a],0x2000079e),'Zero installation writes pointer0 but does not clear flag')
    need(graphs[0x200007a0][0x200007c2]==[0x200007c8,0x200007c4]and 0x200007b4 not in V['reachable'](graphs[0x200007a0],0x200007b6),'Null consumer guard and fresh post-callback flag polarity')
    pointer=flow(0x200007b4,0x200007a4,'a4');dom(0x200007ba,[0x200007b2])
    # The load occurs after any callback return; no cached entry flag is used.
    need(0x200007ba>0x200007b4 and graphs[0x200007a0][0x200007b4]==[0x200007b6],'Fresh flag read follows the opaque call')
    exact({0x60734:'li a0, 0',0x60736:'addi sp, sp, 32',0x60738:'auipc t1, 0x1ffa0',0x6073c:'jr 82(t1)'})
    need(pair(0x60738,0)==0x2000078a,'Original no-link tail setter target');dom(0x60738,[0x60734,0x60736])
    exact({0x43b46:'lui a0, 0x20003',0x43b54:'li a2, 20',0x43b5a:'li a1, 0',0x43b5c:'addi a0, a0, 456'})
    need(pair(0x43b6e,1)==0x2000039c and 0x2000039c in native['_byte_map'],'Actual initializer requests20-byte clear through real prior provider')
    dom(0x43b6e,[0x43b46,0x43b54,0x43b5a,0x43b5c])
    exact({0x43b28:'li a5, 4',0x43b2a:'bltu a5, a1, 0x43b3c',0x43b2e:'lui a5, 0x20003',
        0x43b32:'slli a1, a1, 0x2',0x43b34:'addi a5, a5, 456',0x43b38:'add a1, a1, a5',0x43b3a:'sw a0, 0(a1)',
        0x657bc:'li a1, 2',0x657be:'li a0, 0',0x657c0:'addi sp, sp, 16',0x657c2:'j 0x43b28'})
    raw=int.from_bytes(bytes.fromhex(op[0x657c2]['bytes']),'little');need(raw&127==0x6f and(raw>>7)&31==0 and B['decode_control'](bytes.fromhex(op[0x657c2]['bytes']),0x657c2)[1]==0x43b28,'Real RF-cleanup no-link direct tail')
    dom(0x657c2,[0x657bc,0x657be,0x657c0])
    exact({0x200007ea:'lui s2, 0x20003',0x200007f2:'addi s0, s2, 456',0x2000081a:'lw a5, 8(s0)',
        0x2000081c:'beqz a5, 0x20000820',0x2000081e:'jalr a5',0x20000936:'lw a5, 456(s2)',
        0x2000093a:'beqz a5, 0x20000942',0x2000093c:'jalr a5',0x2000093e:'sw zero, 456(s2)'})
    for site,guard,zero in [(0x2000081e,0x2000081c,0x20000820),(0x2000093c,0x2000093a,0x20000942)]:
        dom(site,[guard]);need(site not in V['reachable'](graphs[0x200007d0],zero),'Known zero guard cannot reach this activation call')
    flow(0x2000081a,0x200007f2,'s0');flow(0x20000936,0x200007ea,'s2')
    common=['matching installed candidate ROM/ISA/RAM profile remains required and unproved','valid disjoint memory and original full register/stack/private ABI context',
        'normal callee returns and no IRQ/reentrant overwrite of the selected binding until consumer load','actual initialization or registration ordering is not globally proved']
    rows=[dict(PC=0x200007b4,function=0x200007a0,family='literal-installed-callback',outcome='conditional-target-set',pointer_slot=0x20002ef8,
        conditional_targets=sorted({p['target_original_PC']for p in producers}),installation_contexts=producers,consumer_pointer_path=pointer,
        conditions=common+['one specified producer path reaches its setter call and pointer remains unchanged to the consumer load'],
        optional_null_domain_also_proved=True,other_installers_or_values_not_resolved=True,live_binding_proved=False),
        dict(PC=0x2000081e,function=0x200007d0,family='optional-array-slot2-zero',outcome='conditional-skipped',pointer_slot=0x200031d0,
            conditions=common+['after expected initializer20-byte clear OR the actual657C2 cleanup tail with A0=0,A1=2','slot2 stays zero until guard2000081C'],live_binding_proved=False),
        dict(PC=0x2000093c,function=0x200007d0,family='optional-array-slot0-zero',outcome='conditional-skipped',pointer_slot=0x200031c8,
            conditions=common+['after expected initializer20-byte clear OR a prior normal callback return followed by zero store2000093E','slot0 stays zero until guard2000093A'],live_binding_proved=False)]
    old=load(ROOT/E['prior_ledger']);newsites={r['PC']for r in rows};need(len(old['rows'])==36 and newsites<={r['PC']for r in old['other_sites']},'Three distinct new sites from prior unjoined list')
    ledger=dict(schema='TSL9-callback-slot-cumulative-ledger-v1',passed=True,rows=sorted(old['rows']+rows,key=lambda r:r['PC']),
        other_sites=[r for r in old['other_sites']if r['PC']not in newsites],
        counts=dict(actual_register_sites=51,conditionally_joined=39,conditional_target_or_target_set=29,conditional_skipped_or_caller_gated=10,not_joined_here=12),
        inherited_APP_API_bindings_not_in_SDK_51=old['new_APP_API_bindings_not_in_SDK_51'],
        no_universal_or_live_binding_claim=True,missing_function_count_not_inferred=True)
    contract=dict(passed=True,producers=producers,literal_installation_contexts=7,selected_registration_call_sites=5,
        all_reaching_A0_definitions_at_selected_calls_proved=True,all_other_installers_closed=False,
        callback_pointer_slot=0x20002ef8,flag_slot=0x20002efc,
        setter=dict(entry=0x2000078a,pointer_store_PC=0x2000078e,nonzero_sets_flag1=True,zero_does_not_clear_flag=True),
        consumer=dict(entry=0x200007a0,call_PC=0x200007b4,null_guard=0x200007b2,fresh_post_callback_flag_load=0x200007ba,
            clear_PC=0x200007c4,zero_flag_clears_then_current_pointer=True,nonzero_flag_skips_clear=True,
            all_flag_writers_closed=False,unconditional_one_shot_or_replacement_safety_proved=False,ordinary_void_void_callback_ABI_proved=False),
        null_install_tail=dict(caller=0x60516,pair_PC=0x60738,target=0x2000078a,A0=0,own_frame_released=True,link_RA_written=False,
            applies_only_when_this_tail_path_is_reached=True),
        optional_array=dict(base=0x200031c8,entries=5,stride=4,initializer_clear_request=[0x200031c8,0x200031dc],
            expected_clear_completion_or_live_zeros_proved=False,slot2_cleanup_tail=0x657c2,slot2_index=2,slot2_zero_value=0,
            slot0_post_normal_callback_zero_store=0x2000093e,slot0_has_no_replacement_flag_check=True,
            slot0_replacement_protection_proved=False,unguarded_other_array_call_sites_not_resolved=True),all_remaining_callee_effects_proved=False)
    return dict(schema='TSL9-callback-slot-binding-verification-v1',passed=True,checker_sha256=sha(__file__),evidence_sha256=sha(HERE/'evidence-v1.json'),
        contract=contract,ledger=ledger,whole_functions=functions,reference_CODE_bytes=5602,reference_instructions=sum(f['instructions']for f in functions),
        composition=prior['composition'],APP_source_C_H_files_unchanged=159,APP_byte_coverage_unchanged=95.54,
        new_target_CODE_bytes=0,new_target_DATA_bytes=0,new_target_compilation=False,inherited_startup_source_gap_bytes=4,
        installed_ROM_identity_proved=False,physical_RAM_ISA_IRQ_or_Flash_compatibility_proved=False,
        actual_global_binding_before_any_dispatch_proved=False,linked_into_APP=False,runtime_closed=False,new_BIN=False,firmware_ready=False,goal_complete=False,
        target_executed=False,HOST_model_executed=False,ISA_emulated=False,hardware_accessed=False,network=False)
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--tool-dir',type=Path,required=True);p.add_argument('--write-receipts',action='store_true');a=p.parse_args()
    try:
        v=verify(a.tool_dir.resolve())
        if a.write_receipts:
            for name,value in [('ledger-v1.json',v['ledger']),('verification-v1.json',v)]:
                dest=HERE/name;need(not dest.exists(),'Create-only callback-slot receipt');dest.write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8')
        print(json.dumps(dict(passed=True,**v['ledger']['counts'],literal_installation_contexts=7,reference_instructions=v['reference_instructions'],new_BIN=False,firmware_ready=False)))
    except Exception as error:
        message=str(error)
        for path,token in [(ROOT,'${PROJECT_ROOT}'),(Path.home(),'${USERPROFILE}')]:message=message.replace(str(path),token).replace(path.as_posix(),token)
        print(json.dumps(dict(passed=False,error_type=type(error).__name__,reason=message)));raise SystemExit(1)
