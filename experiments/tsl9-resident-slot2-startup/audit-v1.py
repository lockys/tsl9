"""Audit candidate startup slot2 stores and actual APP transfer;never execute code."""
import argparse,hashlib,json,runpy,subprocess,sys
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];PRIOR=ROOT/'experiments/tsl9-original-RF-task-path';BIND=ROOT/'experiments/tsl9-original-APP-library-binding'
def need(ok,label):
    if not ok:raise ValueError(label)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def lib(p):return runpy.run_path(str(p),run_name='slot2_startup_static_library')
def canonical(v):return json.loads(json.dumps(v))
def native(llvm):
    N=lib(HERE/'build-v1.py');N['pins'](llvm);saved=json.loads((HERE/'build/native-v1/measurement.json').read_bytes());need(saved['inputs']==N['portable'](N['inputs'](llvm),llvm)and saved['candidate_contract']==N['candidate_contract'](),'Actual complete native inputs retained');results={}
    for mode in ['c','cpp']:
        f=HERE/'build/native-v1'/mode;v=saved['modes'][mode];need(v['artifacts']==N['inventory'](f)and v['dependencies']==N['portable'](N['dependencies'](f,llvm),llvm),'All native artifacts and include dependencies retained');results[mode]=dict(CODE=N['audit_object'](f/'unit.o'),ABI=N['audit_abi'](f/'config_abi.o'));need(results[mode]['CODE']==v['result']and results[mode]['ABI']==v['ABI_result'],'Fresh native readers match compile receipt')
    need(results['c']==results['cpp'],'Actual C11/C++17 CODE and numeric-assertion objects identical');return N,results
def reachable(g,start,skip=None):
    todo=[start];seen=set()
    while todo:
        pc=todo.pop()
        if pc==skip or pc in seen:continue
        seen.add(pc);todo.extend(g[pc])
    return seen
def stages(N):
    E=N['EV'];entries={f['start']for f in E['selected_functions']};pairs={p['PC']+4:p for p in N['S']['PC_relative_pairs']};rows=[];allops={};graphs={}
    for f in E['selected_functions']:
        ops={o['addr']:o for o in f['operations']};g={pc:[]for pc in ops};exits=[];calls=[]
        for pc,o in ops.items():
            after=pc+o['size'];d=N['B']['decode_control'](bytes.fromhex(o['bytes']),pc)
            if o['opcode']=='mret':need(o['bytes']=='73002030','Actual MRET encoding');exits.append(dict(PC=pc,kind='MRET',ordinary_C_return=False));continue
            if o['type']=='ret':exits.append(dict(PC=pc,kind='RET'));continue
            if o['type']=='rjmp':need(pc in pairs and pairs[pc]['reference_kind']=='direct-code-tail-pair','Far tail must have real selected target');exits.append(dict(PC=pc,kind='far-tail',target=pairs[pc]['target_PC']));continue
            if d:
                kind,target=d
                if o['type']=='call':need(target in entries and after in ops,'Actual selected direct callee and continuation');calls.append(dict(PC=pc,target=target,kind='direct-call'));g[pc].append(after)
                elif target in ops:
                    g[pc].append(target)
                    if o['type']=='cjmp':need(after in ops,'Whole conditional fallthrough');g[pc].append(after)
                else:need(o['type']=='jmp'and target in entries,'Actual selected direct tail');exits.append(dict(PC=pc,kind='direct-tail',target=target))
            else:
                need(after in ops,'No fallthrough into adjacent stage');g[pc].append(after)
                if o['type']=='ucall':need(pc in pairs and pairs[pc]['reference_kind']=='direct-code-call-pair','No fabricated opaque code provider');calls.append(dict(PC=pc,target=pairs[pc]['target_PC'],kind='far-call'))
        need(reachable(g,f['start'])==set(ops)and exits,'Every captured instruction belongs to whole stage CFG,including loop exits')
        own=None if f['start']==0x6de7e else(16 if f['start']==0x6de0c else 0)
        if own is not None:
            changes={pc:int(o['opcode'].rsplit(', ',1)[1],0)for pc,o in ops.items()if o['opcode'].startswith('addi sp, sp, ')};need(sorted(changes.values())==([-own,own]if own else []),'Exact local frame changes outside machine entry');seen={};pending=[(f['start'],0)]
            while pending:
                pc,before=pending.pop()
                if pc in seen:need(seen[pc]==before,'Consistent local SP at branch joins');continue
                seen[pc]=before;after=before+changes.get(pc,0);need(after in [-own,0],'Only actual own-frame states')
                if not g[pc]:need(after==0,'Own frame released at local return/tail')
                pending.extend((q,after)for q in g[pc])
        rows.append(dict(start=f['start'],end=f['end'],bytes=f['end']-f['start'],instructions=len(ops),own_frame_bytes=own,entry_replaces_GP_SP=f['start']==0x6de7e,local_frame_balanced_or_machine_entry=True,typed_exits=exits,calls=calls));graphs[f['start']]=g;allops.update(ops)
    return rows,graphs,allops
def word(ops,p):return int.from_bytes(bytes.fromhex(ops[p]['bytes']),'little')
def sx(v,b):return v-(1<<b)if v&(1<<(b-1))else v
def upper(ops,p,rd,opcode):
    w=word(ops,p);need(ops[p]['size']==4 and w&127==opcode and(w>>7)&31==rd,'Actual U-type opcode/destination');return w&0xfffff000
def immediate(ops,p,rd,rs):
    w=word(ops,p);need(ops[p]['size']==4 and w&0x707f==0x13 and(w>>7)&31==rd and(w>>15)&31==rs,'Actual ADDI opcode/registers');return sx(w>>20,12)
def absolute_pair(ops,hi,lo,rd,AUIPC=False):return((hi if AUIPC else 0)+upper(ops,hi,rd,0x17 if AUIPC else 0x37)+immediate(ops,lo,rd,rd))&0xffffffff
def store_word(o):
    w=int.from_bytes(bytes.fromhex(o['bytes']),'little')
    if o['size']==4:
        need(w&0x707f==0x2023,'Actual word S-type store');return((w>>15)&31,(w>>20)&31,sx(((w>>25)<<5)|((w>>7)&31),12))
    need(w&0xe003==0xc000,'Actual standard compressed C.SW');return(8+((w>>7)&7),8+((w>>2)&7),((w>>10)&7)*8+((w>>6)&1)*4+((w>>5)&1)*64)
def APP_bridge(N):
    A=N['EV']['APP'];app=(ROOT/A['APP_firmware']).read_bytes();need(sha(ROOT/A['APP_firmware'])==A['APP_sha256']and sha(ROOT/'src/source-manifest.json')==A['source_manifest_sha256'],'Actual APP and curated inventory identities');need(sum(f['bytes']for f in A['references'])==98,'Correct reset fragment and whole main/initializer intervals,not adjacent event handler');ELF=lib(PRIOR/'elf_reader-v6.py')['ELF'];I=lib(ROOT/'analysis/v4160-irq-native-2026-10-21/compiler-review/elf32.py')['ELF'];W=lib(BIND/'verify-v1.py');V=lib(ROOT/'experiments/tsl9-original-RF-tx-path/audit-v1.py');ops={};ginit=None;rows=[]
    for p,h in A['curated_source_hashes'].items():need(sha(ROOT/p)==h,'Actual APP transfer/main curated sources retained')
    for mode in ['c','cpp']:
        p=ROOT/'experiments/tsl9-original-layout/build/safe-gap-v2'/mode/'NONLOADABLE-ORIGINAL-LAYOUT.elf';need(sha(p)==A['diagnostic_ELF_sha256'],'Existing nonloadable diagnostic identity');e,i=ELF(p),I(p);need(e.header[0]==i.kind==2 and not any(h[0]==1 for h in e.program_headers),'Native APP remains a nonloadable diagnostic')
        for f in A['references']:
            raw=app[f['start']-0x8000:f['end']-0x8000];need(hashlib.sha256(raw).hexdigest()==f['original_sha256']and b''.join(bytes.fromhex(o['bytes'])for o in f['operations'])==raw,'Actual original APP reference bytes');x,xo=W['native_bytes'](e,f['start'],f['end'],True);y,yo=W['native_bytes'](i,f['start'],f['end'],True);need(x==y==raw and xo==yo,'Every selected APP byte equals both readers and existing C/C++ diagnostics')
    for f in A['references']:
        oo={o['addr']:o for o in f['operations']};ops.update(oo)
        if f['start']==0x18724:continue
        external={d[1]for o in f['operations']if(d:=N['B']['decode_control'](bytes.fromhex(o['bytes']),o['addr']))};_,g,v=V['whole_cfg'](f,N['B'],external,16);rows.append(v)
        if f['start']==0x9250:ginit=g
    target=absolute_pair(ops,0x18724,0x18728,5,True);need(target==0x9008 and ops[0x1872c]['opcode']=='csrw mepc, t0','Actual original APP MEPC preparation');w=word(ops,0x1872c);need(w>>20==0x341 and(w>>15)&31==5 and(w>>7)&31==0,'Independent CSR341 operand fields');need(N['B']['decode_control'](bytes.fromhex(ops[0x18730]['bytes']),0x18730)==(17,0x40000)and(word(ops,0x18730)>>7)&31==0,'Original APP no-link transfer to resident40000')
    need(N['B']['decode_control'](bytes.fromhex(ops[0x900c]['bytes']),0x900c)[1]==0x9250 and N['B']['decode_control'](bytes.fromhex(ops[0x9268]['bytes']),0x9268)[1]==0x8e88,'Actual main9008 calls initializer9250,which calls original8E88');need(0x928c not in V['reachable'](ginit,0x9250,skip=0x9268),'Initializer normal-CFG tail requires prior8E88 call')
    return dict(passed=True,reference_bytes=98,reference_instructions=31,original_and_both_C_Cpp_diagnostic_bytes_equal=True,reset_continuation=[0x18724,0x18734],MEPC_prepared=target,resident_no_link_transfer=0x40000,main=0x9008,initializer=0x9250,initializer_call_to8E88=0x9268,initializer_call_dominates_own_tail=True,whole_main_and_initializer_frames=rows,clock_setup_callees_normal_returns_and_register_preservation_assumed=True,actual_global_dispatch_order_proved=False)
def contract(N,O):
    rows,graphs,ops=stages(N);E=N['EV'];expected={0x40000:'j 0x6de7e',0x6de0c:'addi sp, sp, -16',0x6de12:'sw ra, 12(sp)',0x6de14:'lui a5, 0x20000',0x6de3c:'sw a4, 8(a5)',0x6de72:'lw ra, 12(sp)',0x6de74:'addi sp, sp, 16',0x6de7a:'jr 428(t1)',0x6dea6:'bleu a2, a1, 0x6debe',0x6deaa:'lw t0, 0(a0)',0x6deae:'sw t0, 0(a1)',0x6deb2:'addi a0, a0, 4',0x6deb4:'addi a1, a1, 4',0x6deb6:'bltu a1, a2, 0x6deaa',0x6deba:'jal ra, 0x6de0c',0x6debe:'mret',0x20000010:'bleu a1, a2, 0x20000016',0x20000014:'ret',0x20000016:'lw a5, 0(a0)',0x20000018:'addi a1, a1, 4',0x2000001a:'addi a0, a0, 4',0x2000001c:'sw a5, -4(a1)',0x20000020:'j 0x20000010',0x20000032:'bleu a5, a4, 0x20000038',0x20000036:'ret',0x20000038:'sw zero, 0(a5)',0x2000003c:'addi a5, a5, 4',0x2000003e:'j 0x20000032'};need(all(ops[p]['opcode']==v for p,v in expected.items()),'Actual header,frames,MRET,seed and inclusive-copy/zero loop operands')
    values=[absolute_pair(ops,*x)for x in [(0x6de0e,0x6de18,14),(0x6de1e,0x6de22,14),(0x6de28,0x6de2c,14)]];need(values==[0x200007d0,0x2000251c,0x20002e34]and upper(ops,0x6de14,15,0x37)==0x20000000,'Independent raw slot0/1/2 pointer derivation');need([store_word(ops[p])for p in [0x6de1c,0x6de26,0x6de3c]]==[(15,14,0),(15,14,4),(15,14,8)],'Independent raw word-store bases,values and slot offsets')
    g=graphs[0x6de0c];need(all(p not in reachable(g,0x6de0c,skip=0x6de3c)for p in [0x6de4e,0x6de6e,0x6de7a]),'Slot2 store dominates both copies and final tail in whole loader CFG');need(0x6de7a not in reachable(g,0x6de0c,skip=0x6de74),'Own16-byte frame released before far tail')
    gp=absolute_pair(ops,0x6de7e,0x6de82,3,True);sp=absolute_pair(ops,0x6de86,0x6de8a,2,True);seed=[absolute_pair(ops,hi,lo,rd,True)for hi,lo,rd in [(0x6de8e,0x6de92,10),(0x6de96,0x6de9a,11),(0x6de9e,0x6dea2,12)]];need((gp,sp,seed)==(0x20004000,0x20010000,[0x40280,0x20000010,0x20000040]),'Actual entryGP/SP and half-open48-byte seed extent')
    first=[absolute_pair(ops,hi,lo,rd)for hi,lo,rd in [(0x6de38,0x6de46,10),(0x6de34,0x6de42,11),(0x6de30,0x6de3e,12)]];second=[absolute_pair(ops,hi,lo,rd)for hi,lo,rd in [(0x6de5a,0x6de66,10),(0x6de56,0x6de62,11),(0x6de52,0x6de5e,12)]];zero=[absolute_pair(ops,hi,lo,rd)for hi,lo,rd in [(0x20000022,0x2000002a,15),(0x20000026,0x2000002e,14)]];need(first==[0x402b0,0x20000040,0x20002e70]and second==[0x6eaa4,0x20002e70,0x20002ef8]and zero==[0x20002ef8,0x20003614],'Actual inclusive-copy arguments and inclusive-zero bounds')
    need((seed[2]-seed[1],first[2]-first[1]+4,second[2]-second[1]+4,zero[1]-zero[0]+4)==(48,11828,140,1824),'Numeric nonwrapping loop extents,not machine execution');pairs=N['S']['PC_relative_pairs'];need([(p['PC'],p['target_PC'],p['reference_kind'])for p in pairs]==[(0x6de4a,0x20000010,'direct-code-call-pair'),(0x6de6a,0x20000010,'direct-code-call-pair'),(0x6de76,0x20000022,'direct-code-tail-pair')],'Two true far calls and frame-released no-link far tail')
    lleE=json.loads((ROOT/'experiments/tsl9-resident-lle-callback-gateway/evidence-v1.json').read_bytes());f=next(f for f in lleE['selected_functions']if f['start']==0x20002e34);carrier=(ROOT/E['firmware']).read_bytes();source=first[0]+f['start']-first[1];raw=carrier[source-0x40000:source+f['end']-f['start']-0x40000];need((source,f['end'])==(0x430a4,0x20002e6c)and hashlib.sha256(raw).hexdigest()==f['original_sha256'],'Actual complete56-byte prior LLE body lies in first-copy source');need(first[1]<=f['start']<f['end']<=second[1]and f['end']<=zero[0]and 0x20000008+4<=seed[1],'Seed/copy/zero numeric ranges exclude slot2 and later writes exclude LLE code')
    q=O['inspect'](PRIOR/'build/composition-v2/c/candidate.o');need(q['passed']and all(p in q['_byte_map']for p in range(f['start'],f['end'])),'Prior actual candidate composition provides all56 LLE CODE bytes')
    cc=json.loads((ROOT/E['copy_contract']).read_bytes());need(sha(ROOT/E['copy_contract'])==E['copy_contract_sha256']and cc['inherited_startup_gap']['missing_source']==[dict(start=0x6eb2c,end_exclusive=0x6eb30,bytes=4)]and cc['inherited_startup_gap']['later_zero_does_not_prove_missing_source_read_can_complete'],'Inherited four-byte source gap remains;later zero is not source-read proof')
    need(not any('mepc' in o['opcode']for o in ops.values()),'Selected SDK startup stages do not explicitly rewrite prepared MEPC');app=APP_bridge(N)
    return dict(passed=True,stages=rows,APP_bridge=app,slot_stores=E['slot_stores'],slot2_numeric_target=0x20002e34,slot2_store_PC=0x6de3c,slot2_store_precedes_copies=True,initial_GP=gp,initial_SP=sp,entry_is_not_hosted_C_callable=True,seed=E['seed'],first_copy=E['first_copy'],second_copy=E['second_copy'],zero=E['zero'],copy_interface=dict(A0='source',A1='destination',A2='inclusive last destination word',ordinary_memcpy_signature=False),seed_loop_is_half_open=True,word_copy_and_zero_loops_are_inclusive=True,LLE_target=dict(start=f['start'],end=f['end'],bytes=56,source=source,source_sha256=f['original_sha256'],existing_C_provider=f['name'],all_native_CODE_bytes_provided=True,inside_first_copy=True,later_copy_and_zero_ranges_disjoint=True),conditional_control_chain=['APP18724 setsMEPC9008','APP18730 no-link jumps40000','candidate40000 tails6DE7E','seed48 then loader6DE0C','slot2 store then first/second copy and zero tail','candidate6DEBE MRET uses then-liveMEPC','APP9008 calls9250;9250 calls8E88','prior originalAPP199EC copies slot2 toGP+384'],requires_candidate_ROM_identity_standard_instruction_semantics_valid_stable_nonalias_memory_no_faults_and_no_interrupt_CSR_or_memory_interference=True,missing_source_bytes=4,later_zero_does_not_prove_earlier_source_read_success=True,slot2_actual_live_value_observed=False,startup_completed_proved=False,global_binding_before_any_dispatch_proved=False,physical_MRET_vector_or_IRQ_frame_proved=False,runtime_closed=False)
def composition(path,inputs,N,P,O):
    ELF=lib(PRIOR/'elf_reader-v6.py')['ELF'];a={};d={};u=set();r=[];maps={};typed=set()
    for p in inputs:
        aa,dd,uu,rr=P['facts'](p,ELF);need(not set(a)&set(aa)and not set(d)&set(dd),'Unique input section and symbol names');a.update(aa);d.update(dd);u.update(uu);r+=rr;q=O['inspect'](p);need(q['passed']and not set(maps)&set(q['_byte_map']),'No duplicate original-PC CODE ownership');maps.update(q['_byte_map']);typed.update(q['_typed_relations'])
    need(P['facts'](path,ELF)==(a,d,u-set(d),sorted(r)),'Every selected input byte/type/flags/alignment,symbol and relocation retained');out=O['inspect'](path);need(out['passed']and out['_byte_map']==maps and set(out['_typed_relations'])==typed,'Complete unique original-PC byte/typed-relation union');before=O['inspect'](inputs[0]);need(out['named_UND']==before['named_UND']and len(out['named_UND'])==11 and out['non_CODE_allocations']==before['non_CODE_allocations'],'All startup transfers have real selected bodies;11 prior genuine dependencies and256 DATA unchanged');need((out['CODE_bytes'],out['positive_FUNC_regions'],out['relocations'])==(20346,1313,991),'Exact unique composition counts');ind=lib(PRIOR/'compare-readers-v2.py')['audit'](path);need(ind['passed'],'Independent full ELF reader agreement');return dict(**O['public'](out),DATA_bytes=256,allocated_bytes=20602,instructions=6973,independent_readers=ind,every_input_byte_symbol_relocation_retained=True,new_genuine_named_dependencies=0,unique_original_CODE_ownership=True,entry_is_not_ordinary_C_callable=True,actual_original_address_link_performed=False,linked_into_APP=False,runtime_closed=False,new_BIN=False,firmware_ready=False)
def audit(llvm,refs,trial=None):
    previous=lib(BIND/'verify-v1.py')['verify'](llvm,refs);need(canonical(previous)==json.loads((BIND/'verification-v1.json').read_bytes()),'Fresh complete prior APP/SDK/native/reader/CFG/CPU-store/trap proof retained');N,result=native(llvm);O=lib(PRIOR/'verify-ownership-v2.py');sc=contract(N,O);P=lib(ROOT/'experiments/tsl9-sdk-unique-code-ownership/audit-v1.py');out=HERE/'build'/('composition-v1'if trial is None else trial)
    if trial:need(Path(trial).name==trial and not out.exists(),'Fresh create-only composition trial')
    composed={};hashes={}
    for mode in ['c','cpp']:
        inputs=[PRIOR/'build/composition-v2'/mode/'candidate.o',HERE/'build/native-v1'/mode/'unit.o'];need([sha(p)for p in inputs]==['55ff02256dbcdd6964c259b99d722e4b98f04a7c313206b689b84733a5fc0d35','05ff832738ce07ecf1977e55bdee561bd57b5fd416cad5d8c49ee3821224d806'],'Exact actual current SDK parent and startup unit');hashes[mode]={p.relative_to(ROOT).as_posix():sha(p)for p in inputs};f=out/mode
        if trial:
            f.mkdir(parents=True);p=subprocess.run([str(llvm/'ld.lld.exe'),'-r','--no-relax',*[str(q)for q in inputs],'-o',str(f/'candidate.o')],capture_output=True,timeout=120);(f/'link.log').write_text(N['portable']((p.stdout+p.stderr).decode('utf-8','replace'),llvm),encoding='utf-8');need(p.returncode==0,'Actual partial link failed;trial retained')
        composed[mode]=composition(f/'candidate.o',inputs,N,P,O)
    need(composed['c']==composed['cpp'],'Actual whole C/C++ compositions identical');return dict(schema='TSL9-candidate-slot2-startup-audit-v1',passed=True,checker_sha256=sha(__file__),prior_APP_binding_receipt_sha256=sha(BIND/'verification-v1.json'),native_results=result,contract=sc,composition=composed,composition_input_hashes=hashes,new_CODE_bytes=234,new_instructions=67,new_complete_stages=5,new_genuine_named_dependencies=0,APP_reference_bytes=98,new_APP_CODE_bytes=0,APP_source_C_H_files_unchanged=159,APP_byte_coverage_unchanged=95.54,inherited_startup_source_gap_bytes=4,startup_completed_proved=False,slot2_actual_live_value_observed=False,actual_global_binding_before_any_dispatch_proved=False,installed_ROM_identity_proved=False,physical_RAM_capacity_proved=False,physical_Xwchc_profile_proved=False,physical_trap_route_proved=False,Flash_callback_effects_closed=False,linked_into_APP=False,runtime_closed=False,new_BIN=False,firmware_ready=False,goal_complete=False,target_executed=False,HOST_model_executed=False,ISA_emulated=False,hardware_accessed=False,network=False)
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--tool-dir',type=Path,required=True);p.add_argument('--reference-root',type=Path,required=True);p.add_argument('--link-trial');p.add_argument('--output',type=Path);a=p.parse_args()
    try:
        v=audit(a.tool_dir.resolve(),a.reference_root.resolve(),a.link_trial)
        if a.output:
            dest=HERE/a.output;need(dest.parent==HERE and not dest.exists(),'Create-only startup audit receipt');dest.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')
        c=v['composition']['c'];print(json.dumps(dict(passed=True,new_CODE_bytes=234,new_instructions=67,slot2_expected='0x20002E34',LLE_body_bytes=56,composition={k:c[k]for k in ['object_sha256','CODE_bytes','DATA_bytes','instructions','positive_FUNC_regions','relocations']},inherited_missing_source_bytes=4,startup_completed_proved=False,new_BIN=False)))
    except Exception as error:
        message=str(error)
        for path,token in [(ROOT,'${PROJECT_ROOT}'),(Path.home(),'${USERPROFILE}')]:message=message.replace(str(path),token).replace(path.as_posix(),token)
        print(json.dumps(dict(passed=False,error_type=type(error).__name__,reason=message)));raise SystemExit(1)
