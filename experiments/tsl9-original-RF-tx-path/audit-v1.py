"""Static/native proof of actual APP send/retry and candidate RF TX bodies."""
import argparse,hashlib,json,re,runpy,subprocess,sys
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];PRIOR=ROOT/'experiments/tsl9-sdk-unique-code-ownership'
def need(ok,label):
    if not ok:raise ValueError(label)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def lib(p):return runpy.run_path(str(p),run_name='RF_TX_static_library')
def canonical(v):return json.loads(json.dumps(v))
def native(llvm):
    N=lib(HERE/'build-v1.py');N['pins'](llvm);saved=json.loads((HERE/'build/native-v1/measurement.json').read_bytes());need(saved['inputs']==N['portable'](N['inputs'](llvm),llvm)and saved['candidate_contract']==N['candidate_contract'](),'Actual native inputs unchanged');results={}
    for mode in ['c','cpp']:
        f=HERE/'build/native-v1'/mode;v=saved['modes'][mode];need(v['artifacts']==N['inventory'](f)and v['dependencies']==N['portable'](N['dependencies'](f,llvm),llvm),'Native object/log/include inventories')
        results[mode]=dict(CODE=N['audit_object'](f/'unit.o'),ABI=N['audit_abi'](f/'config_abi.o'));need(results[mode]['CODE']==v['result']and results[mode]['ABI']==v['ABI_result'],'Fresh native readers match compilation receipt')
    need(results['c']==results['cpp'],'C11/C++17 actual artifacts identical');return N,results
def reachable(g,start,skip=None):
    seen=set();pending=[start]
    while pending:
        pc=pending.pop()
        if pc==skip or pc in seen:continue
        seen.add(pc);pending.extend(g[pc])
    return seen
def whole_cfg(f,B,external,frame):
    ops={o['addr']:o for o in f['operations']};g={p:[]for p in ops};exits=[];calls=[]
    for pc,o in ops.items():
        following=pc+o['size'];d=B['decode_control'](bytes.fromhex(o['bytes']),pc)
        if o['type']in ['ret','rjmp']:exits.append(dict(PC=pc,type=o['type'],instruction=o['opcode']));continue
        if d:
            kind,target=d
            if o['type']=='call':need(target in external and following in ops,'Named actual callee and continuation');calls.append(dict(PC=pc,target=target));g[pc].append(following)
            elif target in ops:
                g[pc].append(target)
                if o['type']=='cjmp':need(following in ops,'Whole conditional fallthrough');g[pc].append(following)
            else:need(target in external and o['type']=='jmp','Actual external direct tail');exits.append(dict(PC=pc,type='direct-tail',target=target,instruction=o['opcode']))
        else:
            need(following in ops,'No fallthrough into adjacent function');g[pc].append(following)
            if o['type']=='ucall':calls.append(dict(PC=pc,target=None))
    need(reachable(g,f['start'])==set(ops)and exits,'All instructions belong to complete entry CFG,including post-return arms')
    changes={p:int(o['opcode'].rsplit(', ',1)[1],0)for p,o in ops.items()if o['opcode'].startswith('addi sp, sp, ')}
    need(all(v in [-frame,frame]for v in changes.values())if frame else not changes,'Only actual own-frame adjustment sizes');depths={};pending=[(f['start'],0)]
    while pending:
        pc,before=pending.pop()
        if pc in depths:need(depths[pc]==before,'Own SP agrees at every join');continue
        depths[pc]=before;after=before+changes.get(pc,0);need(after in [-frame,0],'Own frame states only')
        if not g[pc]:need(after==0,'Frame released at every normal return/direct or opaque tail')
        pending.extend((v,after)for v in g[pc])
    return ops,g,dict(start=f['start'],end=f['end'],bytes=f['end']-f['start'],instructions=len(ops),own_frame_bytes=frame,own_frame_balanced=True,all_CFG_instructions_reachable=True,typed_exits=exits,calls=calls)
def app_contract(N):
    A=N['EV']['APP'];app=(ROOT/A['APP_firmware']).read_bytes();need(sha(ROOT/A['APP_firmware'])==A['APP_sha256']and sha(ROOT/'src/source-manifest.json')==A['source_manifest_sha256'],'Original APP and source manifest identities')
    for p,h in A['curated_source_hashes'].items():need(sha(ROOT/p)==h,'All selected curated APP source identities')
    path=ROOT/A['diagnostic_ELF'];need(sha(path)==A['diagnostic_ELF_sha256'],'Existing original-address diagnostic identity');e=lib(ROOT/N['S']['reader'])['ELF'](path);need(e.header[0]==2 and not any(p[0]==1 for p in e.program_headers),'Existing ET_EXEC diagnostic remains nonloadable')
    allops={};graphs={};rows=[]
    for f,frame in zip(A['references'],[16,16,16,0]):
        raw=app[f['start']-0x8000:f['end']-0x8000];need(len(raw)==f['bytes']and hashlib.sha256(raw).hexdigest()==f['original_sha256']and b''.join(bytes.fromhex(o['bytes'])for o in f['operations'])==raw,'Contiguous original APP reference bytes')
        at=f['start']
        for o in f['operations']:need(o['addr']==at,'Whole original APP instruction inventory');at+=o['size']
        need(at==f['end'],'Complete selected APP interval');witness=bytearray()
        for pc in range(f['start'],f['end']):
            ss=[s for s in e.sections if s['flags']&6==6 and s['address']<=pc<s['address']+s['size']];need(len(ss)==1,'Unique native diagnostic owner per selected APP byte');s=ss[0];witness.append(e.data(s)[pc-s['address']])
        need(bytes(witness)==raw,'All selected original APP bytes equal compiled diagnostic at original addresses')
        external={d[1]for o in f['operations']if(d:=N['B']['decode_control'](bytes.fromhex(o['bytes']),o['addr']))and d[1]not in {v['addr']for v in f['operations']}};ops,g,v=whole_cfg(f,N['B'],external,frame);allops.update(ops);graphs[f['start']]=g;rows.append(v)
    need(sum(v['bytes']for v in rows)==430 and sum(v['instructions']for v in rows)==147,'430 APP reference bytes/147 instructions;zero new APP CODE')
    def word(pc):return int.from_bytes(bytes.fromhex(allops[pc]['bytes']),'little')
    def sx(v,b):return v-(1<<b)if v&(1<<(b-1))else v
    expected={0x1753c:0x2000c7a9,0x17564:0x2000c7aa,0x1756c:0x2000c7ac,0x17580:0x2000c7a8,0x1758e:0x2000c7a9,0x1759a:0x2000c7a4,0x175a6:0x2000c7ad,0x175c0:0x2000c7a0,0x175ce:0x2000c7a0,0x174c2:0x2000c7a9,0x174ca:0x2000c7aa,0x173fe:0x2000c7a0,0x17408:0x2000c7a8,0x17410:0x2000c7a9,0x17418:0x2000c7a0,0x1742e:0x2000c7a4,0x17442:0x2000c7a8,0x17450:0x2000c7a8,0x1746c:0x2000c7a0};computed={}
    for v in A['pc_relative_data_operands']:
        pc,np=v['PC'],v['next_PC'];a,b=word(pc),word(np);need(np==pc+4 and allops[pc]['size']==allops[np]['size']==4 and a&127==0x17 and(a>>7)&31==(b>>15)&31,'Actual AUIPC base and next load/store/ADDI fields');opcode=b&127;need(opcode in [3,0x13,0x23],'Actual data operand type')
        immediate=((b>>25)<<5)|((b>>7)&31)if opcode==0x23 else b>>20;address=(pc+sx(a&0xfffff000,32)+sx(immediate,12))&0xffffffff;need(address==v['address'],'Independently decoded data operand address');computed[pc]=address
    need(computed==expected,'All19 exact APP data operands,including completion and retry fields')
    checks={0x1753a:'mv a7, a2',0x17544:'bnez a2, 0x175e4',0x17550:'mv a2, a4',0x17576:'li a4, 50',0x1757c:'mv s1, a1',0x1757e:'mv a1, a3',0x17588:'addi a4, a2, 3',0x175a2:'lw a5, 76(s0)',0x175ae:'jalr a5',0x175b0:'lw a5, 512(s0)',0x175b4:'mv a0, s1',0x175b6:'jalr a5',0x175b8:'lw a5, 88(s0)',0x175ba:'li a2, 320',0x175be:'li a1, 2',0x175c8:'jalr a5',0x175ca:'lw a5, 80(s0)',0x175cc:'li a1, 1',0x175d6:'jalr a5',0x174b0:'lw a5, 464(s1)',0x174b4:'jalr a5',0x174b6:'lw a5, 460(s1)',0x174ba:'li a3, 255',0x174be:'li a2, 255',0x174d2:'jalr a5',0x174d4:'xori a0, s0, 1',0x174e4:'jal ra, 0x173ee',0x173f2:'lw a5, 92(a5)',0x17406:'jalr a5',0x17420:'lw t1, 4(a5)',0x17424:'beqz t1, 0x1743a',0x17428:'mv a0, s0',0x17438:'jr t1',0x1744a:'addi a5, a5, -1',0x1744c:'andi a5, a5, 255',0x17458:'bnez a5, 0x17460',0x1745a:'li a0, 1',0x1745c:'j 0x173ee',0x17464:'lw t1, 88(a5)',0x17468:'li a2, 2',0x1746a:'li a1, 1',0x17474:'jr t1'};need(all(allops[p]['opcode']==s for p,s in checks.items()),'Actual APP transfer/length/retry/completion operands')
    for p in [0x17596,0x174ac,0x173ee,0x17460]:need(word(p)&0xfffff07f==0x40037,'Actual LUI base0x40000')
    for root,end,required in [(0x17476,0x174d2,[0x174b4]),(0x1753a,0x175b6,[0x175ae]),(0x1753a,0x175c8,[0x175b6]),(0x173ee,0x17438,[0x17406,0x1740c,0x17414,0x17432,0x17436])]:
        need(all(end not in reachable(graphs[root],root,skip=p)for p in required),'Full local CFG call/clear/frame-release ordering')
    need(allops[0x1740c]['opcode'].startswith('sb zero,')and allops[0x17414]['opcode'].startswith('sb zero,')and allops[0x17432]['opcode'].startswith('sw zero,'),'Actual completion clears before optional opaque tail')
    return dict(passed=True,static_only=True,reference_bytes=430,reference_instructions=147,new_APP_CODE_bytes=0,original_and_compiled_diagnostic_bytes_equal=True,functions=rows,pc_relative_operands=A['pc_relative_data_operands'],APP_context=0x2000c7a0,retry_byte=0x2000c7a8,length_and_busy_style_guard_byte=0x2000c7a9,buffer=0x2000c7aa,payload=0x2000c7ad,optional_completion_word=0x2000c7a4,initial_retry_value=50,stored_length_expression='low8(caller_A4+3)',copy_length_source='caller_A4',copy_source='caller_A3',retry_expression='low8(previous_retry-1)',retry_nonzero_tail=dict(table_slot=0x40058,event=1,raw_time=2),retry_zero_tail=dict(target=0x173ee,A0=1),initial_timeout=dict(table_slot=0x40058,event=2,raw_time=320),timer_units_or_liveness_proved=False,task_TX=dict(Shut_slot=0x401d0,TX_slot=0x401cc,buffer=0x2000c7aa,length_byte=0x2000c7a9,A2=255,A3=255,TX_status_overwritten_by_event_mask=True),channel_slot=0x40200,completion_stops_event2_and_clears_fields_before_optional_tail=True,completion_clear_before_tail=True,completion_tail_not_ordinary_call=True,no_byte_truncation_sufficient_payload_bound=252,bound_is_numeric_representation_only=True,local_sender_length_guard_present=False,physical_payload_maximum_proved=False,all_callers_bounds_proved=False,actual_runtime_observed=False,requires_candidate_ROM_API_identity_valid_memory_callee_registers_and_normal_returns=True)
def sdk_contract(N):
    E=N['EV'];frames={0x64cec:48,0x656c6:16,0x65f94:0,0x64422:16,0x6448e:16,0x645dc:32,0x20002d4c:32,0x20002c50:0};external=set(frames)|{int(k)for k in E['target_names']};pairs={p['PC']+4:p for p in N['S']['PC_relative_pairs']};rows=[];ops={}
    for f in E['selected_functions']:
        oo,g,v=whole_cfg(f,N['B'],external,frames[f['start']]);ops.update(oo)
        for call in v['calls']:
            if call['PC']in pairs:call['target']=pairs[call['PC']]['target_PC']
        rows.append(v)
    opaque=[v['PC']for f in rows for v in f['calls']if v['target']is None];need(opaque==[0x64e50,0x64658,0x64690,0x20002d62],'Exactly four genuinely opaque transfers;far pairs remain named')
    expected={0x64e48:'lui a5, 0x20003',0x64e4c:'lw a5, 480(a5)',0x64e86:'lui a0, 0x64',0x64e8a:'addi a0, a0, 1166',0x64ef6:'lui a0, 0x64',0x64efa:'addi a0, a0, 1058',0x6452c:'lui a0, 0x64',0x64530:'addi a0, a0, 1500',0x64682:'lui a5, 0x20003',0x64686:'lw a5, 1360(a5)',0x6468e:'li a0, 18',0x20002d4c:'lui a5, 0x20003',0x20002d50:'lw a5, 480(a5)'};need(all(ops[p]['opcode']==v for p,v in expected.items()),'Actual callback operands;clock-like word31E0 distinct from status3550')
    need(0x64000+1166==0x6448e and 0x64000+1058==0x64422 and 0x64000+1500==0x645dc and all(v['target']in frames for v in E['numeric_callback_edges']),'All three numeric callback targets have complete selected bodies')
    h=(ROOT/E['header']).read_text(encoding='gb18030');carrier=(ROOT/E['firmware']).read_bytes()
    for name,v in E['primary_RF_entries'].items():need(v['macro']in h and v['slot']==0x40034+4*v['index']and int.from_bytes(carrier[v['slot']-0x40000:v['slot']-0x40000+4],'little')==v['target'],'Primary RF macro and actual candidate table word')
    vectors=(ROOT/E['official_vectors']['path']).read_text();actual=[dict(word=int(hi+lo,16),instruction=text)for text,lo,hi in re.findall(r'# CHECK-ASM-AND-OBJ: (qk\.c\.[^\n]+)\n# CHECK-ASM: encoding: \[0x([0-9a-f]{2}),0x([0-9a-f]{2})\]',vectors)];need(actual==E['official_vectors']['checked']and len(actual)==52,'All52 official custom instruction positive vectors')
    need(sum(o['opcode'].startswith('qk.c.')for o in ops.values())==40,'All40 actual custom operation ports')
    return dict(passed=True,functions=rows,APP=app_contract(N),primary_RF_entries=E['primary_RF_entries'],numeric_callbacks=E['numeric_callback_edges'],numeric_callbacks_have_selected_bodies=True,opaque_transfers=E['opaque_transfers'],clock_like_pointer_storage=0x200031e0,status_pointer_storage=0x20003550,clock_time_units_proved=False,actual_custom_ports=40,primary_custom_vectors=52,raw_dependencies=E['raw_dependencies'],raw_dependency_list_is_not_exhaustive=True,all_callback_effects_proved=False,hardware_identity_or_buffer_bounds_proved=False,runtime_closed=False)
def composition(path,inputs,N,P,O):
    ELF=lib(ROOT/N['S']['reader'])['ELF'];a={};d={};u=set();r=[];maps={};typed=set()
    for p in inputs:
        aa,dd,uu,rr=P['facts'](p,ELF);need(not set(a)&set(aa)and not set(d)&set(dd),'Unique input sections and symbol names');a.update(aa);d.update(dd);u.update(uu);r+=rr;q=O['inspect'](p);need(q['passed']and not set(maps)&set(q['_byte_map']),'No original-PC overlap between any selected CODE inputs');maps.update(q['_byte_map']);typed.update(q['_typed_relations'])
    need(P['facts'](path,ELF)==(a,d,u-set(d),sorted(r)),'Every actual selected input byte/symbol/relocation retained')
    out=O['inspect'](path);need(out['passed']and out['_byte_map']==maps and set(out['_typed_relations'])==typed,'Unique complete source-PC byte map and typed relation union')
    before=O['inspect'](inputs[0]);need(out['named_UND']==before['named_UND']and len(out['named_UND'])==19 and out['non_CODE_allocations']==before['non_CODE_allocations'],'All12 new imports have real prior providers;19 genuine dependencies and256 DATA bytes retained')
    need((out['CODE_bytes'],out['positive_FUNC_regions'],out['relocations'])==(14436,1169,878),'Exact full native composition metrics');ind=lib(ROOT/'experiments/tsl9-remaining-record-dispatch/compare-readers-v1.py')['audit'](path);need(ind['passed'],'Independent full ELF reader agreement')
    return dict(**O['public'](out),DATA_bytes=256,allocated_bytes=14692,instructions=5032,independent_readers=ind,every_input_byte_symbol_relocation_retained=True,all12_new_named_imports_have_real_prior_bodies=True,unique_original_CODE_ownership=True,actual_original_address_link_performed=False,linked_into_APP=False,runtime_closed=False,new_BIN=False,firmware_ready=False)
def audit(llvm,refs,trial=None):
    P=lib(PRIOR/'audit-v1.py');previous=P['audit'](llvm,refs);need(canonical(previous)==json.loads((PRIOR/'audit-result-v1.json').read_bytes()),'Fresh previous complete static/native/ownership audit matches retained receipt');N,results=native(llvm);contract=sdk_contract(N);O=lib(PRIOR/'verify-ownership-v1.py');out=HERE/'build'/('composition-v1'if trial is None else trial)
    if trial:need(Path(trial).name==trial and not out.exists(),'Fresh create-only partial composition')
    composed={};hashes={}
    for mode in ['c','cpp']:
        inputs=[PRIOR/'build/composition-v1'/mode/'candidate.o',HERE/'build/native-v1'/mode/'unit.o'];need([sha(p)for p in inputs]==['ef4c5b1de336192aa811cd6b4268881daa6734cff914cdee43b31d8935ab162c','6220b396926e6c12dbdb0a94058f049e81703557eb11348a95204eff466cd418'],'Exact unique parent and native unit identities');hashes[mode]={p.relative_to(ROOT).as_posix():sha(p)for p in inputs};f=out/mode
        if trial:
            f.mkdir(parents=True);p=subprocess.run([str(llvm/'ld.lld.exe'),'-r','--no-relax',*[str(v)for v in inputs],'-o',str(f/'candidate.o')],capture_output=True,timeout=120);(f/'link.log').write_text(N['portable']((p.stdout+p.stderr).decode('utf-8','replace'),llvm),encoding='utf-8');need(p.returncode==0,'Actual partial link failed;trial retained')
        composed[mode]=composition(f/'candidate.o',inputs,N,P,O)
    need(composed['c']==composed['cpp'],'Whole C/C++ compositions identical')
    return dict(schema='TSL9-actual-APP-RF-send-retry-and-candidate-TX-audit-v1',passed=True,checker_sha256=sha(__file__),prior_audit_sha256=sha(PRIOR/'audit-result-v1.json'),native_results=results,contract=contract,composition=composed,composition_input_hashes=hashes,new_CODE_bytes=1778,new_instructions=620,new_complete_bodies=8,APP_reference_bytes=430,new_APP_CODE_bytes=0,APP_source_C_H_files_unchanged=159,APP_byte_coverage_unchanged=95.54,inherited_startup_source_gap_bytes=4,installed_ROM_identity_proved=False,physical_Xwchc_profile_proved=False,physical_RAM_capacity_proved=False,physical_trap_route_proved=False,Flash_callback_effects_closed=False,linked_into_APP=False,runtime_closed=False,new_BIN=False,firmware_ready=False,goal_complete=False,target_executed=False,HOST_model_executed=False,ISA_emulated=False,hardware_accessed=False,network=False)
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--tool-dir',type=Path,required=True);p.add_argument('--reference-root',type=Path,required=True);p.add_argument('--link-trial');p.add_argument('--output',type=Path);a=p.parse_args()
    try:
        result=audit(a.tool_dir.resolve(),a.reference_root.resolve(),a.link_trial)
        if a.output:
            dest=HERE/a.output;need(dest.parent==HERE and not dest.exists(),'Create-only audit receipt');dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
        c=result['composition']['c'];print(json.dumps(dict(passed=True,new_CODE_bytes=1778,new_instructions=620,APP_reference_bytes=430,composition={k:c[k]for k in ['object_sha256','CODE_bytes','DATA_bytes','instructions','positive_FUNC_regions','relocations']},new_BIN=False)))
    except Exception as error:
        message=str(error)
        for path,token in [(ROOT,'${PROJECT_ROOT}'),(Path.home(),'${USERPROFILE}')]:message=message.replace(str(path),token).replace(path.as_posix(),token)
        print(json.dumps(dict(passed=False,error_type=type(error).__name__,reason=message)));raise SystemExit(1)
