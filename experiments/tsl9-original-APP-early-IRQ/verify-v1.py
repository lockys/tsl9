"""Prove encoded early IRQ requests against original/native bytes;never execute them."""
import argparse,hashlib,json,re,runpy,sys
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def need(ok,label):
    if not ok:raise ValueError(label)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def lib(p):return runpy.run_path(str(ROOT/p),run_name='early_IRQ_static_library')
def canonical(v):return json.loads(json.dumps(v))
def word(o):return int.from_bytes(bytes.fromhex(o['bytes']),'little')
def sx(v,n):return v-(1<<n)if v&(1<<(n-1))else v
def constant(o,rd):
    w=word(o)
    if o['size']==4:
        need((w>>7)&31==rd,'Actual constant destination')
        if w&127==0x37:return w&0xfffff000
        need(w&0x707f==0x13 and(w>>15)&31==0,'Actual ADDI zero literal');return sx(w>>20,12)&0xffffffff
    need((w>>7)&31==rd and w&3==1,'Actual compressed constant destination');n=((w>>2)&31)|((w>>12)&1)*32
    if w&0xe003==0x4001:return sx(n,6)&0xffffffff
    need(w&0xe003==0x6001 and rd not in [0,2]and n!=0,'Actual C.LUI constant');return(sx(n,6)<<12)&0xffffffff
def csr(o,funct3,rs):
    w=word(o);need(o['size']==4 and w&127==0x73 and(w>>7)&31==0 and(w>>12)&7==funct3 and(w>>15)&31==rs and w>>20==0x800,'Independent CSR800 operation/zero destination/source register fields')
def store(o):
    w=word(o);need(o['size']==4 and w&127==0x23 and(w>>12)&7 in [0,2],'Actual byte/word S-type store');return((w>>15)&31,(w>>20)&31,1<<((w>>12)&7),sx(((w>>25)<<5)|((w>>7)&31),12))
def official(E,refs):
    text={};pins={}
    for v in E['official_references']:
        p=refs/v['path'].removeprefix('${REFERENCE_ROOT}/');need(sha(p)==v['sha256'],'Retained official header identity');text[p.name]=p.read_text(encoding='utf-8');pins[v['path']]=v['sha256']
    h=text['wch-core_riscv.h'];c=text['wch-ch32v20x.h'];need('__asm volatile ("csrs 0x800, %0" : : "r" (0x88) );'in h and '__asm volatile ("csrc 0x800, %0" : : "r" (0x88) );'in h,'Official global enable/disable CSR operations,not physical profile identity')
    layout=h.split('typedef struct{',1)[1].split('}PFIC_Type;',1)[0];offset=0;fields={}
    for bits,name,count in re.findall(r'(?:__I|__O|__IO)?\s*uint(8|32)_t\s+(\w+)(?:\[([^\]]+)\])?\s*;',layout):
        size=int(bits)//8;offset=(offset+size-1)//size*size;fields[name]=offset;offset+=size*(int(count,0)if count else 1)
    need([fields[n]for n in ['IENR','IRER','IPSR','IPRR','IPRIOR']]==[0x100,0x180,0x200,0x280,0x400],'Official reference numerical32/8-bit PFIC member offsets')
    need('#define PFIC            ((PFIC_Type *) 0xE000E000 )'in h and 'NVIC->IENR[((uint32_t)(IRQn) >> 5)] = (1 << ((uint32_t)(IRQn) & 0x1F));'in h,'Official reference enable address/mask arithmetic')
    enums={name:int(value)for name,value in re.findall(r'(\w+_IRQn)\s*=\s*(\d+)',c)};expected={'USB_LP_CAN1_RX0_IRQn':36,'EXTI9_5_IRQn':39,'TIM3_IRQn':45,'BB_IRQn':63,'LLE_IRQn':64};need(all(enums[k]==v for k,v in expected.items()),'Official reference enum positions')
    return dict(passed=True,references=pins,PFIC_numeric_member_offsets={k:fields[k]for k in ['IENR','IRER','IPSR','IPRR','IPRIOR']},candidate_IRQ_names=expected,global_CSR=0x800,global_mask=0x88,official_disable_macro_also_has_fence_i=True,selected_APP_initializer_has_no_fence_i=True,installed_profile_proved=False)
def verify(llvm,refs):
    S=json.loads((HERE/'spec-v1.json').read_bytes());need(all(sha(ROOT/p)==h for p,h in S['inputs'].items()),'All original/curated/native checker inputs retained');need(sha(ROOT/S['evidence'])==S['evidence_sha256'],'Exact positive evidence');E=json.loads((ROOT/S['evidence']).read_bytes());raw=(ROOT/E['firmware']).read_bytes();need(sha(ROOT/E['firmware'])==E['firmware_sha256']and sha(ROOT/'src/source-manifest.json')==E['source_manifest_sha256'],'Original BIN and159-file manifest retained')
    prior=lib(E['prior_startup_study']+'/audit-v1.py')['audit'](llvm,refs);need(canonical(prior)==json.loads((ROOT/E['prior_startup_study']/'audit-result-v1.json').read_bytes())and prior['passed'],'Fresh complete prior startup/APP/SDK/native/CFG/CPU-store/trap proof')
    need(sha(ROOT/E['prior_startup_study']/'audit-result-v1.json')==E['prior_startup_receipt_sha256'],'Retained prior receipt identity');B=lib('experiments/tsl9-original-startup/build-v1.py');V=lib('experiments/tsl9-original-RF-tx-path/audit-v1.py');A=lib('experiments/tsl9-original-APP-library-binding/verify-v1.py');P=lib('experiments/tsl9-original-RF-task-path/elf_reader-v6.py')['ELF'];I=lib('analysis/v4160-irq-native-2026-10-21/compiler-review/elf32.py')['ELF'];ops={};graphs={};functions=[]
    for f in E['references']:
        bb=raw[f['start']-0x8000:f['end']-0x8000];need(hashlib.sha256(bb).hexdigest()==f['original_sha256']and b''.join(bytes.fromhex(o['bytes'])for o in f['operations'])==bb,'Contiguous actual original function bytes');at=f['start']
        for o in f['operations']:need(o['addr']==at and o['size']==(4 if word(o)&3==3 else 2),'Complete original instruction boundaries');at+=o['size']
        need(at==f['end'],'Whole selected function interval');external={d[1]for o in f['operations']if(d:=B['decode_control'](bytes.fromhex(o['bytes']),o['addr']))};oo,g,v=V['whole_cfg'](f,B,external,16 if f['start']in [0x9a42,0x9250]else 0);ops.update(oo);graphs[f['start']]=g;functions.append(v)
    need(sum(f['bytes']for f in functions)==328 and sum(f['instructions']for f in functions)==113,'Six whole original functions328B/113i')
    for mode in ['c','cpp']:
        p=ROOT/'experiments/tsl9-original-layout/build/safe-gap-v2'/mode/'NONLOADABLE-ORIGINAL-LAYOUT.elf';need(sha(p)==E['diagnostic_ELF_sha256'],'Unchanged original-address diagnostic');a,b=P(p),I(p);need(a.header[0]==b.kind==2 and not any(h[0]==1 for h in a.program_headers),'Actual diagnostic remains nonloadable,not firmware')
        for f in E['references']:
            x,xo=A['native_bytes'](a,f['start'],f['end'],True);y,yo=A['native_bytes'](b,f['start'],f['end'],True);need(x==y==raw[f['start']-0x8000:f['end']-0x8000]and xo==yo,'Original and both independent native CODE readers agree')
        for v in E['vector_words']:
            pc=v['storage'];bb=raw[pc-0x8000:pc-0x8000+4];x,xo=A['native_bytes'](a,pc,pc+4,False);y,yo=A['native_bytes'](b,pc,pc+4,False);need(x==y==bb and xo==yo and int.from_bytes(bb,'little')==v['value']and hashlib.sha256(bb).hexdigest()==v['original_sha256'],'Five actual readonly vector words agree with independent native readers')
    op=ops;need(constant(op[0x9a4c],18)==0x88,'Independent originalS2 mask literal');csr(op[0x9a50],3,18);csr(op[0x9ac2],2,18)
    own=[o for o in op.values()if 0x9a42<=o['addr']<0x9ad2]
    need([o['addr']for o in own if o['opcode'].split()[0].startswith('csr')]==[0x9a50,0x9ac2],'Complete initializer has only mask-clear/set CSR sites,no saved-state CSR read')
    need([o['addr']for o in own if o['opcode'].split()[0]not in ['sw','sb','sh']and o['opcode'].split(' ',1)[-1].split(',')[0]=='s2']==[0x9a4c,0x9acc],'All initializerS2 destination sites are literal mask and final incoming reload')
    need(not any('fence' in o['opcode']for o in op.values()if 0x9a42<=o['addr']<0x9ad2),'Original IRQ initializer has no fence.i;not identical to entire official disable macro')
    calls=[v for f in functions if f['start']==0x9a42 for v in f['calls']];need([(v['PC'],v['target'])for v in calls]==[(0x9a5e,0x19142),(0x9a6a,0x19124),(0x9a74,0x1917e),(0x9a7e,0x1917e),(0x9a88,0x19160),(0x9a92,0x19160)],'All six actual RCC callees have complete selected bodies')
    helper_rows=[]
    for f,offset in zip(E['references'][1:5],[24,28,12,16]):
        p=f['start'];expected=[f'beqz a1, 0x{p+14:x}','lui a4, 0x40021',f'lw a5, {offset}(a4)','or a0, a0, a5',f'sw a0, {offset}(a4)','ret','lui a5, 0x40021',f'lw a4, {offset}(a5)','not a0, a0','and a0, a0, a4',f'sw a0, {offset}(a5)','ret'];need([o['opcode']for o in f['operations']]==expected,'Whole actual helper has only RCC word RMW and leavesS2/S0/S1/GP/CSR untouched')
        helper_rows.append(dict(start=p,end=f['end'],MMIO_address=0x40021000+offset,branches='fresh32-bit OR on enable;AND complement on disable',own_frame_bytes=0,no_calls_or_CSR_or_S2_GP_writes=True))
    need(constant(op[0x9a96],15)==0xe000e000 and constant(op[0x9a9e],14)==0x2000 and constant(op[0x9aa4],14)==0x20 and constant(op[0x9aac],14)==0x10 and constant(op[0x9ab2],14)==0x30 and constant(op[0x9aba],14)==0x80,'Independent actual PFIC base and six immediate fields')
    stores=[(pc,*store(op[pc]))for pc in [0x9a9a,0x9aa0,0x9aa8,0x9aae,0x9ab6,0x9abe]];need(stores==[(0x9a9a,15,0,1,1069),(0x9aa0,15,14,4,260),(0x9aa8,15,14,1,1060),(0x9aae,15,14,4,260),(0x9ab6,15,14,1,1063),(0x9abe,15,14,4,260)],'Independent original store widths,bases,sources and offsets')
    g=graphs[0x9a42];required=[0x9a50,*[v['PC']for v in calls],0x9a9a,0x9aa0,0x9aa8,0x9aae,0x9ab6,0x9abe,0x9ac2];need(all(0x9ad0 not in V['reachable'](g,0x9a42,skip=pc)for pc in required),'Clear/six RCC calls/all PFIC writes/set dominate normal return')
    need(op[0x9acc]['opcode']=='lw s2, 0(sp)'and 0x9acc not in V['reachable'](g,0x9a42,skip=0x9ac2),'Mask restored into CSR before saved incomingS2 reload')
    main=graphs[0x9250];need(B['decode_control'](bytes.fromhex(op[0x9258]['bytes']),0x9258)[1]==0x9a42 and B['decode_control'](bytes.fromhex(op[0x9268]['bytes']),0x9268)[1]==0x8e88 and 0x9268 not in V['reachable'](main,0x9250,skip=0x9258),'Main initializer calls IRQ setup before entering8E88 on every local normal-return path')
    official_result=official(E,refs);enable=[]
    for pc,mask,index,priority in [(0x9aa0,0x2000,45,0),(0x9aae,0x10,36,0x20),(0x9abe,0x80,39,0x30)]:
        need(0xe000e000+0x100+4*(index//32)==0xe000e104 and 1<<(index%32)==mask,'Numeric official IENR address/mask correspondence');v=next(v for v in E['vector_words']if v['IRQ']==index);enable.append(dict(store_PC=pc,address=0xe000e104,mask=mask,candidate_IRQ=index,candidate_name=next(k for k,n in official_result['candidate_IRQ_names'].items()if n==index),priority=priority,vector_storage=v['storage'],vector_target=v['value']))
    need(all(v['candidate_IRQ']not in [63,64]for v in enable),'These three explicit requests are not BB63 orLLE64;other lines state is unknown')
    bind=json.loads((ROOT/'experiments/tsl9-original-APP-library-binding/verification-v1.json').read_bytes());need(bind['passed']and prior['contract']['APP_bridge']['initializer_call_to8E88']==0x9268,'Fresh prior199EC binding chain retained')
    return dict(schema='TSL9-original-APP-early-IRQ-proof-v1',passed=True,checker_sha256=sha(__file__),prior_startup_receipt_sha256=E['prior_startup_receipt_sha256'],reference_CODE_bytes=328,reference_DATA_bytes=20,reference_instructions=113,complete_functions=6,original_and_both_C_Cpp_native_bytes_equal=True,independent_ELF_readers=2,functions=functions,official_reference=official_result,global_mask=dict(CSR=0x800,value=0x88,clear_PC=0x9a50,set_PC=0x9ac2,actualS2_preserved_by_all_six_complete_RCC_calls=True,set_dominates_normal_return=True,no_saved_global_state_read=True,not_restore_incoming_mask_state=True,selected_initializer_has_fence_i=False),RCC_helpers=helper_rows,enable_requests=enable,vector_words=E['vector_words'],ordering=dict(IRQ_initializer_call=0x9258,global_set_before_own_return=0x9ac2,library_path_call=0x9268,library_main=0x8e88,library_initializer=0x199e2,LLE_binding_store=0x199ec,encoded_early_global_enable_request_before_library_path=True,original_program_does_not_simply_hold_all_global_IRQs_disabled_until_binding=True,requires_standard_instruction_semantics_valid_memory_no_faults_normal_returns_stable_callee_registers_and_no_async_interference=True),three_requests_explicitly_enable_BB_or_LLE=False,BB_LLE_enable_pending_reset_or_live_states_proved=False,prebinding_IRQ_dispatch_occurred_proved=False,all_prebinding_callback_memory_effects_closed=False,no_early_unbound_LLE_dispatch_proved=False,physical_CSR800_semantics_or_controller_identity_proved=False,installed_ROM_identity_proved=False,startup_completed_proved=False,actual_global_binding_before_any_dispatch_proved=False,APP_source_C_H_files_unchanged=159,APP_byte_coverage_unchanged=95.54,SDK_composition_CODE_bytes_unchanged=20346,SDK_composition_DATA_bytes_unchanged=256,SDK_named_UND_unchanged=11,inherited_startup_source_gap_bytes=4,new_target_CODE_bytes=0,new_target_DATA_bytes=0,new_target_compilation=False,linked_into_APP=False,runtime_closed=False,new_BIN=False,firmware_ready=False,goal_complete=False,target_executed=False,HOST_model_executed=False,ISA_emulated=False,hardware_accessed=False,network=False)
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--tool-dir',type=Path,required=True);p.add_argument('--reference-root',type=Path,required=True);p.add_argument('--output',type=Path);a=p.parse_args()
    try:
        v=verify(a.tool_dir.resolve(),a.reference_root.resolve())
        if a.output:
            dest=HERE/a.output;need(dest.parent==HERE and not dest.exists(),'Create-only original early IRQ receipt');dest.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')
        print(json.dumps(dict(passed=True,reference_CODE_bytes=328,reference_DATA_bytes=20,reference_instructions=113,encoded_early_global_enable_before_library=True,enabled_candidate_IRQs=[v['candidate_IRQ']for v in v['enable_requests']],actual_prebinding_dispatch_proved=False,new_target_CODE_bytes=0,new_BIN=False)))
    except Exception as error:
        message=str(error)
        for path,token in [(ROOT,'${PROJECT_ROOT}'),(Path.home(),'${USERPROFILE}')]:message=message.replace(str(path),token).replace(path.as_posix(),token)
        print(json.dumps(dict(passed=False,error_type=type(error).__name__,reason=message)));raise SystemExit(1)
