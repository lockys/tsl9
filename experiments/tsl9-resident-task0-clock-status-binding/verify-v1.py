"""Prove twelve conditional clock/status domains and retain the raw-clock progress obligation."""
import argparse,hashlib,json,re,runpy,sys
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;R=HERE.parents[1]
def need(ok,label):
    if not ok:raise ValueError(label)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read_json(p):return json.loads(Path(p).read_bytes())
def lib(p):return runpy.run_path(str(R/p),run_name='task0_clock_status_library')
def canonical(v):return json.loads(json.dumps(v))
need(__debug__,'Strict assertions required; do not use optimized Python')
E=read_json(HERE/'evidence-v1.json');need(all(sha(R/p)==h for p,h in E['reference_inputs'].items()),'Frozen actual source and proof references');SCOPES=E['scopes']
ROUTES=[(276040, 276028, 'a5', 276024, None, 'a5', 480), (536874414, 536874406, 'a5', 536874402, None, 's4', 480), (536874472, 536874468, 'a5', 536874402, None, 's4', 480), (536874620, 536874616, 'a5', 536874402, None, 's4', 480), (536874894, 536874890, 'a5', 536874402, None, 's4', 480), (536874902, 536874898, 'a5', 536874402, None, 's4', 480), (536874916, 536874908, 'a5', 536874402, None, 's4', 480), (536875538, 536875530, 'a5', 536875526, None, 's3', 480), (536875564, 536875552, 'a5', 536875526, None, 's3', 480), (536875720, 536875712, 'a5', 536875526, None, 's3', 480), (536874694, 536874664, 't1', 536874660, None, 'a5', 544), (536875898, 536875866, 'a5', 536875862, None, 'a5', 544)]
B=runpy.run_path(str(R/'experiments/tsl9-original-startup/build-v1.py'));V=runpy.run_path(str(R/'experiments/tsl9-original-RF-tx-path/audit-v1.py'))
functions=[];selected=[];ops={};owners={};graphs={};cache={}
for name,entries in SCOPES.items():
    fs=[f for f in json.loads((R/'experiments'/name/'evidence-v1.json').read_bytes())['selected_functions']if f['start']in entries];assert len(fs)==len(entries)
    for f in fs:
        selected.append(f)
        frame=max([int(m[1])for o in f['operations']if(m:=re.fullmatch(r'addi sp, sp, -(\d+)',o['opcode']))]or[0]);ext={d[1]for o in f['operations']if(d:=B['decode_control'](bytes.fromhex(o['bytes']),o['addr']))}
        oo,g,q=V['whole_cfg'](f,B,ext,frame);assert not set(ops)&set(oo);ops.update(oo);owners.update({p:f['start']for p in oo});graphs[f['start']]=g;functions.append(q)
PURE={'beq','beqz','bgez','ble','bleu','blez','bltu','bltz','bge','bgeu','bgtu','bne','bnez','j','jr','ret','fence.i','nop'}
STORES={'sb','sh','sw','qk.c.sb','qk.c.sh','qk.c.sbsp','qk.c.shsp'}
RESULT={'add','addi','and','andi','auipc','divu','lb','lbu','lh','lhu','li','lui','lw','mv','mul','mulhu','neg','or','ori','qk.c.lbu','qk.c.lbusp','qk.c.lhu','qk.c.lhusp','remu','seqz','sll','slli','sltu','sltiu','snez','sra','srai','srl','srli','c.srli','sub','xor','xori'}
def reaching(site,reg):
    root=owners[site];key=root,reg
    if key not in cache:
        g=graphs[root];incoming={p:set()for p in g};incoming[root].add(-1);todo=[root]
        while todo:
            pc=todo.pop();o=ops[pc];mn=o['opcode'].split()[0]
            if o['type']in ['call','ucall']or mn in ['jal','jalr']:writes=not reg.startswith('s')
            elif mn in PURE|STORES:writes=False
            else:
                assert mn in RESULT,('unmodelled writer',hex(pc),mn)
                writes=o['opcode'].partition(' ')[2].split(',')[0]==reg
            outgoing={pc}if writes else incoming[pc]
            for n in g[pc]:
                before=len(incoming[n]);incoming[n]|=outgoing
                if before!=len(incoming[n]):todo.append(n)
        cache[key]=incoming
    return cache[key][site]

def native_witness(native):
    values=native['_byte_map'];relations=[json.loads(v)for v in native['_typed_relations']];rel={(v[0][1],v[1]):v[3]for v in relations if v[0][0]=='CODE'};sdk=(R/E['SDK_firmware']).read_bytes();need(sha(R/E['SDK_firmware'])==E['SDK_sha256'],'Actual SDK carrier')
    for f in selected:
        start,end=f['start'],f['end'];source=f['source_start'];raw=sdk[source-0x40000:source-0x40000+end-start]
        need(len(raw)==end-start and b''.join(bytes.fromhex(o['bytes'])for o in f['operations'])==raw and hashlib.sha256(raw).hexdigest()==f['original_sha256'],'Every original complete selected body byte')
        current=bytes(values[p]for p in range(start,end));norm=bytearray(current);skip=set()
        for o in f['operations']:
            pc=o['addr'];off=pc-start;width=o['size'];ref=bytes.fromhex(o['bytes']);word=int.from_bytes(ref,'little')
            if pc in skip:continue
            d=B['decode_control'](ref,pc)
            if d:
                kind,target=d;w,mask=B['MASKS'][kind];n=int.from_bytes(current[off:off+w],'little')
                need(w==width and rel[(pc,kind)]==['CODE',target]and n&mask==word&mask and n&(~mask&((1<<(8*w))-1))==0,'Exact native direct transfer opcode, register and typed original target')
                norm[off:off+w]=(n|B['immediate'](kind,target-pc)).to_bytes(w,'little')
            elif width==4 and word&127==0x17 and rel.get((pc,23)):
                target=rel[(pc,23)];need(target[0]=='CODE'and rel[(pc+4,24)]==['CODE',pc],'Actual far-call HI/LO anchors')
                delta=(target[1]-pc)&0xffffffff
                for at,mask,imm in [(off,0xfff,(delta+0x800)&0xfffff000),(off+4,0xfffff,(delta&0xfff)<<20)]:
                    n=int.from_bytes(current[at:at+4],'little');v=int.from_bytes(raw[at:at+4],'little');need(n&mask==v&mask and not n&(~mask&0xffffffff),'Exact native far-call opcode/register and zero displacement');norm[at:at+4]=((n&mask)|imm).to_bytes(4,'little')
                skip.add(pc+4)
        need(bytes(norm)==raw,'Every native selected CODE byte equals original after address re-encoding')
    return dict(passed=True,complete_functions=3,CODE_bytes=1816,instructions=592,all_original_address_reencoded_bytes_equal=True)

def verify(llvm):
    prior=lib(E['prior_study']+'/'+E['prior_verifier'])[E['prior_entry']](llvm);need(canonical(prior)==read_json(R/E['prior_receipt']),'Fresh entire prior native/APP/CFG proof chain')
    O=lib('experiments/tsl9-resident-root-chain-callees/verify-ownership-v3.py');native=O['inspect'](R/E['SDK_native_object']);need(native['passed']and sha(R/E['SDK_native_object'])==E['SDK_native_object_sha256']==prior['composition']['c']['object_sha256']and sha(R/E['SDK_native_object'].replace('/c/','/cpp/'))==E['SDK_native_object_sha256'],'Actual identical retained C/C++ SDK union')
    witness=native_witness(native);need(len(functions)==3 and sum(f['bytes']for f in functions)==1816 and sum(f['instructions']for f in functions)==592,'Three complete source CFGs1816B592i')
    C=lib('experiments/tsl9-original-callback-provenance/verify-v1.py');folder=R/'experiments/tsl9-original-callback-provenance';cb=C['static_contract'](read_json(folder/'spec-v1.json'),read_json(folder/'evidence-v1.json'))
    need(canonical(cb)==read_json(folder/'verification-v1.json')['contract'],'Fresh original APP configuration, memory-copy and native callback witnesses')
    clock=cb['clock_configuration'];status=cb['status_configuration'];need(clock['conditional_slots_both_equal']==0x191c6 and clock['SDK_raw_clock_slot']==0x200031e0 and status['conditional_value_after_zero_copy_and_no_overwrite']==0 and status['SDK_pointer_slot']==0x20003220,'Correct raw-clock and status slots from original APP, not the distinct clock provider')
    need(cb['clock_callback']['saved_registers_RA_SP_GP_preserved_by_encoded_writes']and not cb['clock_callback']['termination_coherence_frequency_and_physical_MMIO_semantics_proved'],'Original raw-clock encoded preservation and physical limitations retained')
    regnums={name:i for i,name in enumerate(['zero','ra','sp','gp','tp','t0','t1','t2','s0','s1','a0','a1','a2','a3','a4','a5','a6','a7','s2','s3','s4','s5','s6','s7','s8','s9','s10','s11','t3','t4','t5','t6'])};proof=[];rows=[]
    common=['matching installed ROM/ISA/RAM profile remains unproved','valid disjoint memory/stack and original private ABI','normal prior callees preserve saved-register context','no asynchronous/reentrant pointer replacement; each selected slot remains stable','actual initialization order and live values unobserved']
    for site,load_pc,rd,hi,low,base,offset in ROUTES:
        need(low is None and reaching(site,rd)=={load_pc}and reaching(load_pc,base)=={hi},'All reaching pointer/base definitions uniquely accounted for')
        h=int.from_bytes(bytes.fromhex(ops[hi]['bytes']),'little');l=int.from_bytes(bytes.fromhex(ops[load_pc]['bytes']),'little')
        need(ops[hi]['size']==4 and h&127==0x37 and(h>>7)&31==regnums[base]and h&0xfffff000==0x20003000,'Raw-decoded base LUI')
        need(ops[load_pc]['size']==4 and l&0x707f==0x2003 and(l>>7)&31==regnums[rd]and(l>>15)&31==regnums[base]and l>>20==offset and ops[load_pc]['opcode']==f'lw {rd}, {offset}({base})','Raw-decoded LW register and exact callback field')
        slot=0x20003000+offset;item=dict(PC=site,function=owners[site],pointer_load=load_pc,base_definition=hi,pointer_register=rd,base_register=base,pointer_slot=slot,all_reaching_definitions=[load_pc],base_reaching_definitions=[hi])
        if offset==480:
            need(slot==0x200031e0,'Raw-clock slot, not provider word');item.update(outcome='conditional-target',target_original_PC=0x191c6)
            rows.append(dict(PC=site,function=owners[site],family='original-task0-raw-clock',outcome='conditional-target',target_original_PC=0x191c6,pointer_slot=slot,witnesses=item,conditions=common+['accepted original nonnull16-byte clock configuration copied; raw slot remains191C6 at every load','clock MMIO coherence, frequency, progress and loop termination are unproved'],live_binding_proved=False))
        else:
            guard,zero,nonnull=(0x20000eac,0x20001092,0x20000eb0)if site==0x20000ec6 else(0x2000135e,0x20001360,0x20001376)
            need(slot==0x20003220 and set(graphs[owners[site]][guard])=={zero,nonnull}and site not in V['reachable'](graphs[owners[site]],zero)and site not in V['reachable'](graphs[owners[site]],owners[site],skip=guard),'Actual local null guard dominates; known zero cannot reach call')
            need(reaching(guard,rd)=={load_pc},'Guard tests same freshly loaded pointer');item.update(outcome='conditional-skipped',guard_PC=guard,zero_branch=zero,nonnull_branch=nonnull,zero_branch_cannot_reach_call=True)
            rows.append(dict(PC=site,function=owners[site],family='original-task0-status-zero',outcome='conditional-skipped',pointer_slot=slot,witnesses=item,conditions=common+['after known BLE64-byte configuration zero/copy and no overwrite, staCB remains zero','pre-copy/earlier heap-call value and all other status values remain unproved'],live_binding_proved=False))
        proof.append(item)
    need(sum(r['outcome']=='conditional-target'for r in rows)==10 and sum(r['outcome']=='conditional-skipped'for r in rows)==2,'Ten raw-clock targets and two status null domains')
    need(ops[0x20000f90]['opcode']=='mv s2, a0'and ops[0x20000f92]['opcode']=='lw a5, 480(s4)'and ops[0x20000f96]['opcode']=='jalr a5'and ops[0x20000f98]['opcode']=='beq a0, s2, 0x20000f92','Actual wait-for-changed-clock loop, not an assumed bounded poll')
    need(graphs[0x20000d50][0x20000f98]==[0x20000f92,0x20000f9c]and reaching(0x20000f98,'a0')=={0x20000f96}and reaching(0x20000f98,'s2')=={0x20000f90},'Compare fresh returned value against saved first result on every back edge')
    old=prior['ledger'];newsites={r['PC']for r in rows};need(old['counts']['conditionally_joined']==51 and old['counts']['actual_register_sites']==63 and newsites=={r['PC']for r in old['other_sites']},'Exactly twelve previously unjoined actual sites')
    ledger=dict(schema='TSL9-task0-clock-status-cumulative-ledger-v1',passed=True,rows=sorted(old['rows']+rows,key=lambda r:r['PC']),other_sites=[],counts=dict(actual_register_sites=63,conditionally_joined=63,conditional_target_or_target_set=51,conditional_skipped_or_caller_gated=12,not_joined_here=0),no_universal_or_live_binding_claim=True,missing_function_count_not_inferred=True)
    need(len(ledger['rows'])==len({r['PC']for r in ledger['rows']})==63,'Sixty-three distinct conditional domains only in the current partial object')
    contract=dict(passed=True,new_conditional_sites=12,raw_clock_sites=10,status_zero_sites=2,raw_clock_slot=0x200031e0,raw_clock_target=0x191c6,status_slot=0x20003220,status_value_in_selected_domain=0,all_reaching_pointer_and_base_definitions_accounted_for=True,
        clock_wait_loop=dict(first_call=0x20000f8e,saved_first_result=0x20000f90,fresh_pointer_load=0x20000f92,repeat_call=0x20000f96,equality_back_edge=0x20000f98,back_target=0x20000f92,different_value_exit=0x20000f9c,explicit_retry_bound_or_timeout_present=False,requires_clock_value_change_for_exit=True,termination_frequency_MMIO_coherence_or_real_elapsed_time_proved=False),
        all_clock_calls_after_configuration_or_live_values_proved=False,earlier_status_values_or_all_other_status_bindings_proved=False,installed_ROM_identity_proved=False)
    return dict(schema='TSL9-task0-clock-status-binding-verification-v1',passed=True,checker_sha256=sha(__file__),evidence_sha256=sha(HERE/'evidence-v1.json'),contract=contract,consumer_proofs=proof,whole_functions=functions,native_witness=witness,original_APP_callback_contract=cb,ledger=ledger,composition=prior['composition']['c'],APP_source_C_H_files_unchanged=159,APP_byte_coverage_unchanged=95.54,new_target_CODE_bytes=0,new_target_DATA_bytes=0,new_target_compilation=False,inherited_startup_source_gap_bytes=4,installed_ROM_identity_proved=False,physical_RAM_ISA_IRQ_or_Flash_compatibility_proved=False,actual_global_binding_before_any_dispatch_proved=False,linked_into_APP=False,runtime_closed=False,new_BIN=False,firmware_ready=False,goal_complete=False,target_executed=False,HOST_model_executed=False,ISA_emulated=False,hardware_accessed=False,network=False)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--tool-dir',type=Path,required=True);p.add_argument('--write-receipt',action='store_true');a=p.parse_args()
    try:
        v=verify(a.tool_dir.resolve())
        if a.write_receipt:
            for name,value in [('verification-v1.json',v),('ledger-v1.json',v['ledger'])]:
                dest=HERE/name;need(not dest.exists(),'Create-only proof receipt');dest.write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8')
        print(json.dumps(dict(passed=True,new_conditional_sites=12,raw_clock_sites=10,status_zero_sites=2,counts=v['ledger']['counts'],clock_loop_termination_proved=False,new_BIN=False)))
    except Exception as error:
        message=str(error)
        for path,token in [(R,'${PROJECT_ROOT}'),(Path.home(),'${USERPROFILE}')]:message=message.replace(str(path),token).replace(path.as_posix(),token)
        print(json.dumps(dict(passed=False,error_type=type(error).__name__,reason=message)));raise SystemExit(1)
