"""Audit final direct initializer providers and full original caller target inventory;never execute them."""
import argparse,hashlib,json,runpy,subprocess,sys
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];PARENT=ROOT/'experiments/tsl9-resident-address-state';READERS=ROOT/'experiments/tsl9-original-RF-task-path'
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
    E=N['EV'];B=N['B'];A=lib(ROOT/'experiments/tsl9-original-APP-library-binding/verify-v1.py');C=lib(ROOT/'experiments/tsl9-original-APP-early-IRQ/verify-v1.py');fs=E['selected_functions'];op={o['addr']:o for f in fs for o in f['operations']}
    expected={0x57ac4:'lui a0, 0x20003',0x57ac8:'li a2, 28',0x57aca:'li a1, 0',0x57acc:'addi a0, a0, 1108',0x57ad0:'auipc t1, 0x1ffa9',0x57ad4:'jr -1844(t1)',0x63704:'lui a5, 0x20003',0x63708:'addi a5, a5, 952',0x6370c:'sw zero, 196(a5)',0x63710:'sb zero, 192(a5)',0x63714:'ret'}
    need([(f['start'],f['end'])for f in fs]==[(0x57ac4,0x57ad8),(0x63704,0x63716)]and {p:o['opcode']for p,o in op.items()}==expected,'Two full straight-line bodies,all eleven operands,adjacent siblings excluded')
    def word(pc):return int.from_bytes(bytes.fromhex(op[pc]['bytes']),'little')
    for f in fs:
        at=f['start']
        for o in f['operations']:
            raw=bytes.fromhex(o['bytes']);need(o['addr']==at and len(raw)==o['size']==(4 if raw[0]&3==3 else 2),'Every complete contiguous raw instruction');at+=o['size']
        need(at==f['end'],'Whole selected body')
    need(C['constant'](op[0x57ac4],10)==0x20003000 and C['constant'](op[0x57ac8],12)==28 and C['constant'](op[0x57aca],11)==0,'Raw memset destination base,fill0,count28')
    a=word(0x57acc);need(a&0x707f==0x13 and(a>>7)&31==10 and(a>>15)&31==10 and a>>20==1108,'Raw ADDI destination offset1108')
    hi=word(0x57ad0);lo=word(0x57ad4);imm=lo>>20;imm=imm-4096 if imm&2048 else imm
    need(hi&127==0x17 and(hi>>7)&31==6 and lo&0x707f==0x67 and(lo>>7)&31==0 and(lo>>15)&31==6 and(0x57ad0+(hi&0xfffff000)+imm)&0xffffffff==0x2000039c,'Independent AUIPC t1/JALR zero,t1 actual no-link target')
    pairs=N['S']['PC_relative_pairs'];need(len(pairs)==1 and pairs[0]['PC']==0x57ad0 and pairs[0]['target_PC']==0x2000039c and pairs[0]['reference_kind']=='direct-code-tail-pair'and not N['S']['controls'],'Typed original far-tail reference,no direct branches')
    need(C['constant'](op[0x63704],15)==0x20003000 and A['store'](op[0x6370c])==(15,0,4,196)and A['store'](op[0x63710])==(15,0,1,192),'Independent word/byte zero widths and base offsets')
    a=word(0x63708);need(a&0x707f==0x13 and(a>>7)&31==15 and(a>>15)&31==15 and a>>20==952 and word(0x63714)==0x8082,'Raw state base addition and original compressed return')
    need(0x20003000+1108==0x20003454 and 0x20003454+28==0x20003470 and 0x200033b8+196==0x2000347c and 0x200033b8+192==0x20003478,'Exact numeric zero-request spans')
    spans=[(0x20003454,0x20003470),(0x2000347c,0x20003480),(0x20003478,0x20003479)];need(all(0x200033b8<=a<b<=0x200033b8+296 for a,b in spans),'All current requests inside earlier296-byte state request;not new RAM capacity')
    caller=json.loads((ROOT/E['caller_evidence']).read_bytes());need(sha(ROOT/E['caller_evidence'])==E['caller_evidence_sha256'],'Original initializer evidence retained');f=caller['selected_functions'][0];io={o['addr']:o for o in f['operations']}
    for pc,target in [(0x537b6,0x57ac4),(0x537ba,0x63704)]:need(B['decode_control'](bytes.fromhex(io[pc]['bytes']),pc)[1]==target,'Actual two initializer direct calls')
    need(io[0x537c6]['opcode']=='addi sp, sp, 16'and B['decode_control'](bytes.fromhex(io[0x537c8]['bytes']),0x537c8)[1]==0x5e758,'Original frame release before later tail')
    parent=O['inspect'](PARENT/'build/composition-v1/c/candidate.o');newbytes={p for f in fs for p in range(f['start'],f['end'])};resolved={'tsl9_candidate_external_flash_57ac4','tsl9_candidate_external_flash_63704'}
    need(parent['passed']and not set(parent['_byte_map'])&newbytes and resolved<=set(parent['named_UND'])and 0x2000039c in parent['_byte_map'],'Two genuine prior missing bodies and real prior memset provider,no duplicate CODE')
    complete=[]
    for study,root in [('tsl9-resident-init-leaves',0x43e24),('tsl9-resident-init-leaves',0x55bd4),('tsl9-resident-init-leaves',0x55c48),('tsl9-resident-init-final',0x57ac4),('tsl9-resident-init-final',0x63704),('tsl9-resident-address-state',0x5e758),('tsl9-original-RF-bridge',0x64298)]:
        q=json.loads((ROOT/'experiments'/study/'evidence-v1.json').read_bytes());matches=[x for x in q['selected_functions']if x['start']==root];need(len(matches)==1,'Exactly one complete required root evidence');x=matches[0];need(all(p in newbytes or p in parent['_byte_map']for p in range(x['start'],x['end'])),'Every byte of actual required root body supplied');complete.append(dict(start=root,end=x['end'],bytes=x['end']-root,evidence='experiments/'+study+'/evidence-v1.json',evidence_sha256=sha(ROOT/'experiments'/study/'evidence-v1.json')))
    direct=[]
    for o in f['operations']:
        d=B['decode_control'](bytes.fromhex(o['bytes']),o['addr'])
        if d and not f['start']<=d[1]<f['end']:direct.append(dict(PC=o['addr'],target=d[1]))
    need({x['target']for x in direct}=={x['start']for x in complete},'All actual external direct initializer targets,not arbitrary chosen subset')
    return dict(passed=True,complete_functions=2,CODE_bytes=38,instructions=11,own_frame_bytes=[0,0],actual_opaque_callbacks=0,no_new_CSR_requests=True,incoming_SP_GP_RA_saved_registers_preserved_by_new_bodies=True,memset_tail=dict(PC=0x57ad0,target=0x2000039c,destination=0x20003454,fill=0,bytes=28,end=0x20003470,no_link=True,normal_return_requires_prior_memset_contract=True),stores=[dict(PC=0x6370c,address=0x2000347c,bytes=4,value=0),dict(PC=0x63710,address=0x20003478,bytes=1,value=0)],all_new_requests_inside_prior296_byte_span=True,original_initializer_external_direct_transfers=direct,all_seven_external_direct_initializer_roots_have_complete_bodies=True,complete_required_roots=complete,remaining_transitive_indirect_memory_IRQ_effects_closed=False,initialization_success_or_final_all_zero_proved=False,actual_binding_before_any_global_dispatch_proved=False,physical_ROM_RAM_ISA_IRQ_profile_proved=False,runtime_closed=False)

def composition(path,inputs,N,O):
    P=lib(ROOT/'experiments/tsl9-sdk-unique-code-ownership/audit-v1.py');ELF=lib(READERS/'elf_reader-v6.py')['ELF'];a={};d={};u=set();r=[];maps={};typed=set()
    for p in inputs:
        aa,dd,uu,rr=P['facts'](p,ELF);need(not set(a)&set(aa)and not set(d)&set(dd),'Unique section/symbol owners');a.update(aa);d.update(dd);u.update(uu);r+=rr;q=O['inspect'](p);need(q['passed']and not set(maps)&set(q['_byte_map']),'No duplicate original-PC CODE');maps.update(q['_byte_map']);typed.update(q['_typed_relations'])
    need(P['facts'](path,ELF)==(a,d,u-set(d),sorted(r)),'Every selected byte/type/flags/alignment,symbol and relocation retained');out=O['inspect'](path);need(out['passed']and out['_byte_map']==maps and set(out['_typed_relations'])==typed,'Complete unique original-PC byte and typed-relation union')
    before=O['inspect'](inputs[0]);resolved={'tsl9_candidate_external_flash_57ac4','tsl9_candidate_external_flash_63704'};expected_UND=sorted(set(before['named_UND'])-resolved);need(out['named_UND']==expected_UND and len(out['named_UND'])==9 and out['non_CODE_allocations']==before['non_CODE_allocations'],'Both actual initializer providers resolve two prior dependencies;memset import uses real prior body;DATA256 unchanged')
    need((out['CODE_bytes'],out['positive_FUNC_regions'],out['relocations'])==(21408,1377,1040),'Exact actual composition counts');ind=lib(READERS/'compare-readers-v2.py')['audit'](path);need(ind['passed'],'Independent whole ELF reader agreement')
    return dict(**O['public'](out),DATA_bytes=256,allocated_bytes=21664,instructions=7331,independent_readers=ind,every_input_byte_symbol_relocation_retained=True,two_genuine_prior_named_dependencies_have_real_bodies=True,new_genuine_named_dependencies=0,unique_original_CODE_ownership=True,actual_original_address_link_performed=False,linked_into_APP=False,runtime_closed=False,new_BIN=False,firmware_ready=False)
def audit(llvm,refs,trial=None):
    E=json.loads((HERE/'evidence-v1.json').read_bytes());prior=lib(ROOT/E['prior_study']/'audit-v1.py')['audit'](llvm,refs);need(canonical(prior)==json.loads((ROOT/E['prior_study']/'audit-result-v1.json').read_bytes())and sha(ROOT/E['prior_study']/'audit-result-v1.json')==E['prior_receipt_sha256'],'Fresh entire prior NVM/settings/IRQ/startup/APP/SDK/native/reader/CFG proof');N,result=native(llvm);O=lib(READERS/'verify-ownership-v2.py');sc=contract(N,O);out=HERE/'build'/('composition-v1'if trial is None else trial)
    if trial:need(Path(trial).name==trial and not out.exists(),'Fresh create-only composition')
    composed={};hashes={}
    for mode in ['c','cpp']:
        inputs=[PARENT/'build/composition-v1'/mode/'candidate.o',HERE/'build/native-v1'/mode/'unit.o'];need([sha(p)for p in inputs]==[E['SDK_parent_sha256'],'ac8e501c8c7987b0ac05a103bbd0add6124bb0662089314a8a55662a98c01fd4'],'Actual current SDK parent and new unit');hashes[mode]={p.relative_to(ROOT).as_posix():sha(p)for p in inputs};f=out/mode
        if trial:
            f.mkdir(parents=True);p=subprocess.run([str(llvm/'ld.lld.exe'),'-r','--no-relax',*[str(q)for q in inputs],'-o',str(f/'candidate.o')],capture_output=True,timeout=120);(f/'link.log').write_text(N['portable']((p.stdout+p.stderr).decode('utf-8','replace'),llvm),encoding='utf-8');need(p.returncode==0,'Actual partial link failed;trial retained')
        composed[mode]=composition(f/'candidate.o',inputs,N,O)
    need(composed['c']==composed['cpp'],'Both actual complete C/C++ compositions equal');return dict(schema='TSL9-required-initializer-final-direct-providers-audit-v1',passed=True,checker_sha256=sha(__file__),prior_state_receipt_sha256=E['prior_receipt_sha256'],native_results=result,contract=sc,composition=composed,composition_input_hashes=hashes,new_CODE_bytes=38,new_instructions=11,new_complete_functions=2,new_genuine_named_dependencies=0,APP_source_C_H_files_unchanged=159,APP_byte_coverage_unchanged=95.54,inherited_startup_source_gap_bytes=4,installed_ROM_identity_proved=False,physical_RAM_capacity_proved=False,physical_Xwchc_profile_proved=False,physical_trap_route_proved=False,Flash_callback_effects_closed=False,actual_global_binding_before_any_dispatch_proved=False,all_remaining_callee_effects_proved=False,linked_into_APP=False,runtime_closed=False,new_BIN=False,firmware_ready=False,goal_complete=False,target_executed=False,HOST_model_executed=False,ISA_emulated=False,hardware_accessed=False,network=False)
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--tool-dir',type=Path,required=True);p.add_argument('--reference-root',type=Path,required=True);p.add_argument('--link-trial');p.add_argument('--output',type=Path);a=p.parse_args()
    try:
        v=audit(a.tool_dir.resolve(),a.reference_root.resolve(),a.link_trial)
        if a.output:
            dest=HERE/a.output;need(dest.parent==HERE and not dest.exists(),'Create-only random/range audit');dest.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')
        c=v['composition']['c'];print(json.dumps(dict(passed=True,new_CODE_bytes=38,new_instructions=11,complete_functions=2,composition_CODE_bytes=c['CODE_bytes'],composition_DATA_bytes=c['DATA_bytes'],named_UND=len(c['named_UND']),real_prior_dependencies_resolved=2,opaque_callbacks=0,new_BIN=False)))
    except Exception as error:
        message=str(error)
        for path,token in [(ROOT,'${PROJECT_ROOT}'),(Path.home(),'${USERPROFILE}')]:message=message.replace(str(path),token).replace(path.as_posix(),token)
        print(json.dumps(dict(passed=False,error_type=type(error).__name__,reason=message)));raise SystemExit(1)
