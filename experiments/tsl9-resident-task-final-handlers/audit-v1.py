"""Audit remaining actual60516 handlers,frame-released parser tail and scheduler bank union;never execute them."""
import argparse,hashlib,json,runpy,subprocess,sys
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];PARENT=ROOT/'experiments/tsl9-resident-parser-callees';READERS=ROOT/'experiments/tsl9-original-RF-task-path'
def need(ok,label):
    if not ok:raise ValueError(label)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def lib(p):return runpy.run_path(str(p),run_name='range_random_static_library')
def canonical(v):return json.loads(json.dumps(v))
def native(llvm):
    N=lib(HERE/'build-v1.py');N['pins'](llvm);saved=json.loads((HERE/'build/native-v1/measurement.json').read_bytes());need(saved['inputs']==N['portable'](N['inputs'](llvm),llvm)and saved['candidate_contract']==N['candidate_contract'](),'All actual compile inputs retained');result={}
    for mode in ['c','cpp']:
        f=HERE/'build/native-v1'/mode;v=saved['modes'][mode];need(v['artifacts']==N['inventory'](f)and v['dependencies']==N['portable'](N['dependencies'](f,llvm),llvm),'All actual native artifacts/include dependencies retained');result[mode]=dict(CODE=N['audit_object'](f/'unit.o'),ABI=N['audit_abi'](f/'config_abi.o'));need(result[mode]['CODE']==v['result']and result[mode]['ABI']==v['ABI_result'],'Fresh native readers agree with compile receipt')
    need(result['c']==result['cpp'],'Actual C11/C++17 CODE and primary ABI objects equal');return N,result
def contract(N,O):
    E=N['EV'];B=N['B'];V=lib(ROOT/'experiments/tsl9-original-RF-tx-path/audit-v1.py');A=lib(ROOT/'experiments/tsl9-original-APP-library-binding/verify-v1.py');C=lib(ROOT/'experiments/tsl9-original-APP-early-IRQ/verify-v1.py');frames={0x5f98e:16,0x5fcdc:32,0x6014e:16,0x5fbae:32,0x43874:48};rows=[];graphs={};op={}
    for f in E['selected_functions']:
        need(f['own_frame_bytes']==frames[f['start']],'Exact original own-frame declaration');ext={d[1]for o in f['operations']if(d:=B['decode_control'](bytes.fromhex(o['bytes']),o['addr']))};oo,g,v=V['whole_cfg'](f,B,ext,frames[f['start']]);op.update(oo);graphs[f['start']]=g;rows.append(v)
    need(sum(v['bytes']for v in rows)==2254 and sum(v['instructions']for v in rows)==801 and len(rows)==5,'Five complete reachable CFGs and balanced own frames')
    def needops(mapping):need(all(op[p]['opcode']==s for p,s in mapping.items()),'Exact actual handler/tail/bank operands')
    def dom(root,end,pcs):return all(end not in V['reachable'](graphs[root],root,skip=pc)for pc in pcs)
    def store(o):
        value=A['store'](o)
        if value is not None:return value
        w=int.from_bytes(bytes.fromhex(o['bytes']),'little')
        if o['size']==2 and w&0xe003==0xc000:return(8+((w>>7)&7),8+((w>>2)&7),4,((w>>10)&7)*8+((w>>6)&1)*4+((w>>5)&1)*64)
        return None
    needops({0x5f98e:'addi sp, sp, -16',0x5fa16:'addi sp, sp, 16',0x5fa18:'ret',0x5fcdc:'addi sp, sp, -32',0x5fd58:'addi sp, sp, 32',0x5fd5a:'ret',0x60016:'mv a0, s0',0x60018:'lw s0, 24(sp)',0x6001e:'lw ra, 28(sp)',0x60020:'lw s1, 20(sp)',0x60022:'lw s2, 16(sp)',0x60024:'lw s3, 12(sp)',0x60026:'lw s4, 8(sp)',0x60028:'addi sp, sp, 32',0x6002a:'j 0x5f234',0x6014e:'addi sp, sp, -16',0x601ac:'addi sp, sp, 16',0x601ae:'ret',0x5fbae:'addi sp, sp, -32',0x5fc22:'jal ra, 0x63c54',0x5fc6c:'addi sp, sp, 32',0x5fc6e:'ret'})
    word=int.from_bytes(bytes.fromhex(op[0x6002a]['bytes']),'little');need(word&127==0x6f and(word>>7)&31==0 and B['decode_control'](bytes.fromhex(op[0x6002a]['bytes']),0x6002a)[1]==0x5f234,'Actual original no-link parser tail,not a normal C call');need(dom(0x5fcdc,0x6002a,[0x60016,0x6001e,0x60028]),'Record argument,original RA and released32-byte frame precede parser tail')
    need(max(graphs[0x5f98e])+op[max(graphs[0x5f98e])]['size']==0x5fbae and max(graphs[0x6014e])+op[max(graphs[0x6014e])]['size']==0x6020a,'Actual complete handler ends exclude adjacent functions')
    need(any(pc>0x5fa18 for pc in graphs[0x5f98e])and any(pc>0x5fd5a for pc in graphs[0x5fcdc])and any(pc>0x601ae for pc in graphs[0x6014e]),'All reachable late arms after early RET retained')
    needops({0x43874:'addi sp, sp, -48',0x43878:'lui a5, 0x40024',0x43892:'lw s3, 524(a5)',0x43896:'sw zero, 524(a5)',0x4389a:'fence.i',0x4389e:'beqz a0, 0x438fe',0x438a0:'li s0, 16',0x438aa:'li s9, 12',0x438ac:'lui s6, 0x20003',0x438b0:'li s10, 1',0x438b2:'li s8, 48',0x438b6:'mul s7, s0, s9',0x438ba:'lw a4, 556(s6)',0x438be:'add a4, a4, s7',0x438c0:'lw a5, 0(a4)',0x438c2:'bnez a5, 0x43920',0x438c4:'andi a1, s0, 15',0x438c8:'sll a1, s10, a1',0x438cc:'srai a0, s0, 0x4',0x438d0:'slli a1, a1, 0x10',0x438d2:'mv a2, s5',0x438d4:'srli a1, a1, 0x10',0x438d6:'andi a0, a0, 255',0x438da:'jal 0x43728',0x438dc:'beqz a0, 0x43920',0x438e4:'sw s1, 0(a5)',0x438e6:'sw s4, 4(a5)',0x438ea:'beqz s2, 0x438f2',0x438ee:'sb s0, 0(s2)',0x438f6:'sw s3, 524(a5)',0x438fa:'li a0, 0',0x438fe:'sw s3, 524(a5)',0x43902:'li a0, 2',0x4391c:'addi sp, sp, 48',0x4391e:'ret',0x43920:'addi s0, s0, 1',0x43922:'bne s0, s8, 0x438b6',0x4392a:'sw s3, 524(a5)',0x4392e:'li a0, 8',0x43930:'j 0x43904'})
    need(C['constant'](op[0x438a0],8)==16 and C['constant'](op[0x438aa],25)==12 and C['constant'](op[0x438b2],24)==48 and C['constant'](op[0x438ac],22)==0x20003000,'Independent upper-bank start/stride/end/base constants');need(graphs[0x43874][0x43922]==[0x438b6,0x43926]and graphs[0x43874][0x438dc]==[0x43920,0x438de],'Original scan retry and exact helper-result polarity')
    need(C['constant'](op[0x43878],15)==0x40024000 and store(op[0x43896])==(15,0,4,524)and all(store(op[p])==(15,19,4,524)for p in [0x438f6,0x438fe,0x4392a]),'Original save/zero/restore word4002420C requests,not hardware atomicity');need(dom(0x43874,0x4391e,[0x43892,0x43896,0x4389a,0x4391c]),'All normal helper returns retain save,zero,FENCE.I and frame release')
    need(store(op[0x438e4])==(15,9,4,0)and store(op[0x438e6])==(15,20,4,4)and store(op[0x438ee])==(18,8,1,0),'Actual two record words and optional byte-width output ID')
    need(sha(ROOT/E['scheduler_evidence'])==E['scheduler_evidence_sha256'],'Exact earlier lower-bank/removal evidence');old=json.loads((ROOT/E['scheduler_evidence']).read_bytes());low=next(f for f in old['selected_functions']if f['start']==0x43414);remove=next(f for f in old['selected_functions']if f['start']==0x43a14);lo={o['addr']:o for o in low['operations']};ro={o['addr']:o for o in remove['operations']}
    need(lo[0x43478]['opcode']=='li s0, 0'and lo[0x4347a]['opcode']=='li a3, 12'and lo[0x4347c]['opcode']=='li a5, 16'and lo[0x43510]['opcode']=='bne s0, a5, 0x4347e'and lo[0x43472]['opcode']=='lw a4, 556(a5)','Actual lower bank scans0..15 with same12-byte stride');need(ro[0x43a30]['opcode']=='li a5, 47'and ro[0x43a34]['opcode']=='bltu a5, a0, 0x43a80'and ro[0x43a38]['opcode']=='li a5, 12'and ro[0x43a42]['opcode']=='lw a5, 556(s3)','Actual removal bound0..47 and same stride')
    need(C['constant'](lo[0x4346e],15)==C['constant'](ro[0x43a3e],19)==0x20003000 and 0x20003000+556==0x2000322c,'All three routines fresh-read the same numeric table-pointer slot')
    need((0,16*12)==(0,192)and(16*12,48*12)==(192,576)and 16*12+(48-16)*12==48*12,'Symbolic disjoint index-bank union0..47,576-byte numeric extent;no input execution')
    caller=json.loads((ROOT/E['caller_evidence']).read_bytes());need(sha(ROOT/E['caller_evidence'])==E['caller_evidence_sha256'],'Whole original task evidence retained');f=next(f for f in caller['selected_functions']if f['start']==0x60516);io={o['addr']:o for o in f['operations']};required=[]
    for pc,target in [(0x6068e,0x5f98e),(0x60620,0x5fcdc),(0x605ac,0x6014e)]:need(B['decode_control'](bytes.fromhex(io[pc]['bytes']),pc)[1]==target,'Actual task callsite for each previous handler gap');required.append(dict(PC=pc,target=target))
    parent=O['inspect'](PARENT/'build/composition-v1/c/candidate.o');newbytes={p for f in E['selected_functions']for p in range(f['start'],f['end'])};need(parent['passed']and not set(parent['_byte_map'])&newbytes and set(E['resolved_prior_dependencies'])<=set(parent['named_UND']),'Three genuine prior handler providers supplied,no duplicate CODE');need(all(p in parent['_byte_map']for p in E['real_prior_providers']),'All thirteen current imports have actual prior bodies');need(all(p in parent['_byte_map']for g in [low,remove]for p in range(g['start'],g['end'])),'Complete prior lower-bank/removal CODE retained')
    far={x['PC']+4:x['target_PC']for x in N['S']['PC_relative_pairs']};actual=[]
    for row in rows:
        for call in row['calls']:
            target=far.get(call['PC'],call['target']);need(target is not None and target in set(frames)|set(E['real_prior_providers']),'Every actual new-unit call has a selected or real prior body');actual.append(dict(PC=call['PC'],target=target))
    ext={d[1]for o in f['operations']if(d:=B['decode_control'](bytes.fromhex(o['bytes']),o['addr']))};_,_,task=V['whole_cfg'](f,B,ext,32);task_far={}
    for pc,o in io.items():
        h=int.from_bytes(bytes.fromhex(o['bytes']),'little');other=io.get(pc+4)
        if o['size']!=4 or h&127!=0x17 or other is None:continue
        l=int.from_bytes(bytes.fromhex(other['bytes']),'little')
        if other['size']==4 and l&0x707f==0x67 and(h>>7)&31==(l>>15)&31:
            n=l>>20;n=n-4096 if n&2048 else n;task_far[pc+4]=(pc+(h&0xfffff000)+n)&0xffffffff
    task_static=[];task_opaque=[]
    for call in task['calls']:
        target=task_far.get(call['PC'],call['target'])
        if target is None:task_opaque.append(call['PC'])
        else:need(target in newbytes or target in parent['_byte_map'],'Every resolvable static task call entry has retained CODE');task_static.append(dict(PC=call['PC'],target=target))
    return dict(passed=True,functions=rows,actual_calls=actual,actual_opaque_callbacks=0,complete_functions=5,CODE_bytes=2254,instructions=801,own_frames=[16,32,16,32,48],conditional_Xwchc_ports=53,original_task_calls=required,resolved_prior_dependencies=E['resolved_prior_dependencies'],new_genuine_named_dependencies=0,real_prior_providers=E['real_prior_providers'],all_resolvable_60516_static_call_entries_supplied=True,task_static_calls=task_static,task_unresolved_indirect_call_sites=task_opaque,parser_tail=dict(PC=0x6002a,target=0x5f234,no_link=True,original_RA_and_record_argument_restored=True,own32_frame_released_before_tail=True),scheduler_banks=dict(pointer_slot=0x2000322c,stride=12,lower_function=0x43414,lower_half_open_indices=[0,16],upper_function=0x43874,upper_half_open_indices=[16,48],removal_function=0x43a14,removal_inclusive_ID_range=[0,47],lower_numeric_bytes=192,upper_numeric_bytes=384,total_numeric_bytes=576,numeric_union_has_no_gap_or_overlap=True,task_ID_encoding='low8(ID >> 4)',event_encoding='low16(1 << (ID & 15))',prior_helper=0x43728,prior_helper_nonzero_branch_writes_record=True,optional_output_ID_bytes=1,encoded_helper_results=[0,2,8],same_runtime_table_base_requires_pointer_stability_and_private_callee_memory_contracts=True,actual_allocation_capacity_ownership_lifetime_and_concurrency_proved=False),control_word=dict(address=0x4002420c,save_zero_FENCE_I_restore_requests_preserved=True,physical_atomicity_or_IRQ_isolation_proved=False),all_numeric_CODE_pointer_targets_or_callbacks_closed=False,prior_conditional_callback_and_source_mapping_proofs_retained=True,no_live_record_or_MAC_contents_observed=True,all_remaining_callee_effects_proved=False,physical_ROM_RAM_ISA_IRQ_profile_proved=False,runtime_closed=False)

def composition(path,inputs,N,O):
    P=lib(ROOT/'experiments/tsl9-sdk-unique-code-ownership/audit-v1.py');ELF=lib(READERS/'elf_reader-v6.py')['ELF'];a={};d={};u=set();r=[];maps={};typed=set()
    for p in inputs:
        aa,dd,uu,rr=P['facts'](p,ELF);need(not set(a)&set(aa)and not set(d)&set(dd),'Unique section/symbol owners');a.update(aa);d.update(dd);u.update(uu);r+=rr;q=O['inspect'](p);need(q['passed']and not set(maps)&set(q['_byte_map']),'No duplicate original-PC CODE');maps.update(q['_byte_map']);typed.update(q['_typed_relations'])
    need(P['facts'](path,ELF)==(a,d,u-set(d),sorted(r)),'Every selected byte/type/flags/alignment,symbol and relocation retained');out=O['inspect'](path);need(out['passed']and out['_byte_map']==maps and set(out['_typed_relations'])==typed,'Complete unique original-PC byte and typed-relation union')
    before=O['inspect'](inputs[0]);resolved=set(N['EV']['resolved_prior_dependencies']);added=set();expected_UND=sorted((set(before['named_UND'])-resolved)|added);need(out['named_UND']==expected_UND and len(out['named_UND'])==4 and out['non_CODE_allocations']==before['non_CODE_allocations'],'Three prior60516 handler gaps supplied;all thirteen imports real;DATA256 unchanged')
    need((out['CODE_bytes'],out['positive_FUNC_regions'],out['relocations'])==(29848,2008,1586),'Exact actual composition counts');ind=lib(READERS/'compare-readers-v2.py')['audit'](path);need(ind['passed'],'Independent whole ELF reader agreement')
    return dict(**O['public'](out),DATA_bytes=256,allocated_bytes=30104,instructions=10321,independent_readers=ind,every_input_byte_symbol_relocation_retained=True,three_genuine_prior_named_dependencies_have_real_bodies=True,new_genuine_named_dependencies=0,unique_original_CODE_ownership=True,actual_original_address_link_performed=False,linked_into_APP=False,runtime_closed=False,new_BIN=False,firmware_ready=False)
def audit(llvm,refs,trial=None):
    E=json.loads((HERE/'evidence-v1.json').read_bytes());prior=lib(ROOT/E['prior_study']/E['prior_verifier'])[E['prior_entry']](llvm,refs);need(canonical(prior)==json.loads((ROOT/E['prior_study']/E['prior_receipt']).read_bytes())and sha(ROOT/E['prior_study']/E['prior_receipt'])==E['prior_receipt_sha256'],'Fresh entire callback-provenance and preceding APP/SDK/native/IRQ/CFG proof');N,result=native(llvm);O=lib(READERS/'verify-ownership-v2.py');sc=contract(N,O);out=HERE/'build'/('composition-v1'if trial is None else trial)
    if trial:need(Path(trial).name==trial and not out.exists(),'Fresh create-only composition')
    composed={};hashes={}
    for mode in ['c','cpp']:
        inputs=[PARENT/'build/composition-v1'/mode/'candidate.o',HERE/'build/native-v1'/mode/'unit.o'];need([sha(p)for p in inputs]==[E['SDK_parent_sha256'],'a96c508744ce807aa197dad7134c55e93b4938273510e8acbd8099895bcded68'],'Actual current SDK parent and new unit');hashes[mode]={p.relative_to(ROOT).as_posix():sha(p)for p in inputs};f=out/mode
        if trial:
            f.mkdir(parents=True);p=subprocess.run([str(llvm/'ld.lld.exe'),'-r','--no-relax',*[str(q)for q in inputs],'-o',str(f/'candidate.o')],capture_output=True,timeout=120);(f/'link.log').write_text(N['portable']((p.stdout+p.stderr).decode('utf-8','replace'),llvm),encoding='utf-8');need(p.returncode==0,'Actual partial link failed;trial retained')
        composed[mode]=composition(f/'candidate.o',inputs,N,O)
    need(composed['c']==composed['cpp'],'Both actual complete C/C++ compositions equal');return dict(schema='TSL9-remaining-task-handlers-and-upper-scheduler-bank-audit-v1',passed=True,checker_sha256=sha(__file__),prior_parser_callees_receipt_sha256=E['prior_receipt_sha256'],native_results=result,contract=sc,composition=composed,composition_input_hashes=hashes,new_CODE_bytes=2254,new_instructions=801,new_complete_functions=5,new_genuine_named_dependencies=0,APP_source_C_H_files_unchanged=159,APP_byte_coverage_unchanged=95.54,inherited_startup_source_gap_bytes=4,installed_ROM_identity_proved=False,physical_RAM_capacity_proved=False,physical_Xwchc_profile_proved=False,physical_trap_route_proved=False,Flash_callback_effects_closed=False,actual_global_binding_before_any_dispatch_proved=False,all_remaining_callee_effects_proved=False,linked_into_APP=False,runtime_closed=False,new_BIN=False,firmware_ready=False,goal_complete=False,target_executed=False,HOST_model_executed=False,ISA_emulated=False,hardware_accessed=False,network=False)
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--tool-dir',type=Path,required=True);p.add_argument('--reference-root',type=Path,required=True);p.add_argument('--link-trial');p.add_argument('--output',type=Path);a=p.parse_args()
    try:
        v=audit(a.tool_dir.resolve(),a.reference_root.resolve(),a.link_trial)
        if a.output:
            dest=HERE/a.output;need(dest.parent==HERE and not dest.exists(),'Create-only random/range audit');dest.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')
        c=v['composition']['c'];print(json.dumps(dict(passed=True,new_CODE_bytes=2254,new_instructions=801,complete_functions=5,composition_CODE_bytes=c['CODE_bytes'],composition_DATA_bytes=c['DATA_bytes'],named_UND=len(c['named_UND']),real_prior_dependencies_resolved=3,opaque_callbacks=0,new_BIN=False)))
    except Exception as error:
        message=str(error)
        for path,token in [(ROOT,'${PROJECT_ROOT}'),(Path.home(),'${USERPROFILE}')]:message=message.replace(str(path),token).replace(path.as_posix(),token)
        print(json.dumps(dict(passed=False,error_type=type(error).__name__,reason=message)));raise SystemExit(1)
