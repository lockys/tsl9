"""Audit conditional scheduled56CDC provenance,complete original bodies and whole indirect inventory."""
import argparse,hashlib,json,runpy,subprocess,sys
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];PARENT=ROOT/'experiments/tsl9-resident-root-chain-callees';READERS=PARENT
def need(ok,label):
    if not ok:raise ValueError(label)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def lib(p):return runpy.run_path(str(p),run_name='scheduled_record_static_library')
def canonical(v):return json.loads(json.dumps(v))
CHECKER_PINS={'indirect-inventory-v1.py': '9c5ca2ac702bfa9c5cbb516e9bb5b8d608d8125129eed6e68bee2a1bc05c5f82', 'provenance-v1.py': '2be85aba73b773107dc6c446cdaf56a478ef86cea8cc234d7f4956699a76b1fb'}
def native(llvm):
    N=lib(HERE/'build-v1.py');N['pins'](llvm);saved=json.loads((HERE/'build/native-v1/measurement.json').read_bytes());need(saved['inputs']==N['portable'](N['inputs'](llvm),llvm)and saved['candidate_contract']==N['candidate_contract'](),'All actual compile inputs retained');result={}
    for mode in ['c','cpp']:
        f=HERE/'build/native-v1'/mode;v=saved['modes'][mode];need(v['artifacts']==N['inventory'](f)and v['dependencies']==N['portable'](N['dependencies'](f,llvm),llvm),'All actual native artifacts/include dependencies retained');result[mode]=dict(CODE=N['audit_object'](f/'unit.o'),ABI=N['audit_abi'](f/'config_abi.o'));need(result[mode]['CODE']==v['result']and result[mode]['ABI']==v['ABI_result'],'Fresh native readers agree with compile receipt')
    need(result['c']==result['cpp'],'Actual C11/C++17 CODE and primary ABI objects equal');return N,result

def contract(N,O):
    E=N['EV'];B=N['B'];V=lib(ROOT/'experiments/tsl9-original-RF-tx-path/audit-v1.py');op={};graphs={};rows=[]
    for f in E['selected_functions']:
        ext={d[1]for o in f['operations']if(d:=B['decode_control'](bytes.fromhex(o['bytes']),o['addr']))};oo,g,q=V['whole_cfg'](f,B,ext,16);op.update(oo);graphs[f['start']]=g;rows.append(q)
    need(len(rows)==2 and sum(q['bytes']for q in rows)==174 and sum(q['instructions']for q in rows)==62,'Two complete actual bodies and balanced delayed16-byte frame paths')
    exact={0x56cdc:'beqz a0, 0x56d0c',0x56cde:'addi sp, sp, -16',0x56ce4:'qk.c.lbu a5, 15(a0)',0x56ce6:'mv s0, a0',0x56ce8:'li a1, 62',0x56cec:'andi a5, a5, 2',0x56cee:'beqz a5, 0x56cf2',0x56cf0:'li a1, 8',0x56cf2:'jal ra, 0x568f6',0x56cf6:'li a5, -1',0x56cf8:'sb a0, 43(s0)',0x56cfc:'sb zero, 16(s0)',0x56d00:'sb a5, 40(s0)',0x56d04:'lw ra, 12(sp)',0x56d08:'addi sp, sp, 16',0x56d0a:'ret',0x56d0c:'ret',0x568f6:'lui a5, 0x20003',0x568fa:'addi a5, a5, 952',0x568fe:'lw a4, 168(a5)',0x5690a:'mv s0, a0',0x5690c:'mv s1, a1',0x5690e:'bne a4, a0, 0x56916',0x56912:'sw zero, 168(a5)',0x56916:'lw a5, 288(s0)',0x5691a:'beqz a5, 0x56928',0x5691c:'qk.c.lhu a0, 8(s0)',0x5691e:'li a2, 0',0x56920:'li a1, 128',0x56924:'jal ra, 0x5e3a8',0x56928:'lhu a5, 68(s0)',0x5692c:'beqz a5, 0x5693a',0x5692e:'qk.c.lhu a0, 8(s0)',0x56930:'li a2, 19',0x56932:'li a1, 129',0x56936:'jal ra, 0x5e3a8',0x5693a:'qk.c.lhu a0, 8(s0)',0x5693c:'li a2, 5',0x5693e:'li a1, 129',0x56942:'jal ra, 0x5e3a8',0x56946:'lui a5, 0x20003',0x5694a:'addi a5, a5, 1300',0x5694e:'qk.c.lbu a4, 7(a5)',0x56950:'sb zero, 10(s0)',0x56954:'sb zero, 16(s0)',0x56958:'sb s1, 84(s0)',0x5695c:'li a3, 5',0x5695e:'bne a3, a4, 0x56966',0x56962:'sb zero, 7(a5)',0x5696c:'li a0, 0',0x5696e:'addi sp, sp, 16',0x56970:'ret'}
    need(all(op[p]['opcode']==s for p,s in exact.items()),'Exact original null guard,mode selection,message arguments and encoded record/global stores');need(graphs[0x56cdc][0x56cdc]==[0x56d0c,0x56cde]and graphs[0x56cdc][0x56cee]==[0x56cf2,0x56cf0],'Original null and flag-bit branch polarities');need(0x20003000+952+168==0x20003460 and 0x20003000+1300+7==0x2000351b,'Numeric global-word and flag-byte addresses')
    parent=O['inspect'](PARENT/'build/composition-v1/c/candidate.o');newbytes={pc for q in rows for pc in range(q['start'],q['end'])};need(parent['passed']and not newbytes&set(parent['_byte_map'])and not parent['named_UND'],'No duplicate CODE and zero parent named UND');need(E['real_prior_providers']==[0x5e3a8]and 0x5e3a8 in parent['_byte_map']and not E['new_genuine_code_dependencies'],'Actual existing message helper is the sole import')
    calls=[call for q in rows for call in q['calls']];need(all(call['target']in newbytes|{0x5e3a8}for call in calls),'Every actual new call has selected or real prior CODE')
    return dict(passed=True,functions=rows,CODE_bytes=174,instructions=62,complete_functions=2,own_frames=[16,16],conditional_Xwchc_ports=5,actual_static_calls=calls,actual_opaque_callbacks=0,resolved_prior_dependencies=[],real_prior_providers=[0x5e3a8],new_genuine_named_dependencies=0,callback_original_PC=0x56cdc,callback_original_PC_bytes_included=True,actual_original_address_link_performed=False,helper_message_calls=[dict(PC=0x56924,A1=128,A2=0,conditional='record.word288 !=0'),dict(PC=0x56936,A1=129,A2=19,conditional='record.u16_at68 !=0'),dict(PC=0x56942,A1=129,A2=5,conditional='normal encoded path')],helper_encoded_stores=dict(record_byte10=0,record_byte16=0,record_byte84='low8(entry_A1)',global_word3460='zero only if equal to entry_A0',global_byte351B='zero only if equal to5'),helper_normal_return_A0=0,physical_message_delivery_or_hardware_success_proved=False,inherited_previous_callbacks_and_memory_holds_retained=True,all_remaining_callee_effects_proved=False,runtime_closed=False)

def composition(path,inputs,N,O):
    P=lib(ROOT/'experiments/tsl9-sdk-unique-code-ownership/audit-v1.py');ELF=lib(READERS/'elf_reader-v7.py')['ELF'];a={};d={};u=set();r=[];maps={};typed=set()
    for p in inputs:
        aa,dd,uu,rr=P['facts'](p,ELF);need(not set(a)&set(aa)and not set(d)&set(dd),'Unique section/symbol owners');a.update(aa);d.update(dd);u.update(uu);r+=rr;q=O['inspect'](p);need(q['passed']and not set(maps)&set(q['_byte_map']),'No duplicate original-PC CODE');maps.update(q['_byte_map']);typed.update(q['_typed_relations'])
    need(P['facts'](path,ELF)==(a,d,u-set(d),sorted(r)),'Every selected byte/type/flags/alignment,symbol and relocation retained');out=O['inspect'](path);need(out['passed']and out['_byte_map']==maps and set(out['_typed_relations'])==typed,'Complete unique original-PC byte and typed-relation union')
    before=O['inspect'](inputs[0]);resolved=set(N['EV']['resolved_prior_dependencies']);added=set(N['EV']['new_genuine_code_dependencies']);expected_UND=sorted((set(before['named_UND'])-resolved)|added);need(out['named_UND']==expected_UND and len(out['named_UND'])==0 and out['non_CODE_allocations']==before['non_CODE_allocations'],'One real existing import,no new named gaps,DATA256 unchanged')
    need((out['CODE_bytes'],out['positive_FUNC_regions'],out['relocations'])==(35324,2401,1914),'Exact actual composition counts');ind=lib(READERS/'compare-readers-v3.py')['audit'](path);need(ind['passed'],'Independent whole ELF reader agreement')
    return dict(**O['public'](out),DATA_bytes=256,allocated_bytes=35580,instructions=12195,independent_readers=ind,every_input_byte_symbol_relocation_retained=True,all_new_named_imports_have_real_prior_bodies=True,new_genuine_named_dependencies=0,unique_original_CODE_ownership=True,actual_original_address_link_performed=False,linked_into_APP=False,runtime_closed=False,new_BIN=False,firmware_ready=False)

def audit(llvm,refs,trial=None):
    E=json.loads((HERE/'evidence-v1.json').read_bytes());need(all(sha(ROOT/p)==h for p,h in E['whole_reader_inputs'].items())and all(sha(HERE/p)==h for p,h in CHECKER_PINS.items()),'Exact frozen whole readers and current provenance/inventory checkers');prior=lib(ROOT/E['prior_study']/E['prior_verifier'])[E['prior_entry']](llvm,refs);need(canonical(prior)==json.loads((ROOT/E['prior_study']/E['prior_receipt']).read_bytes())and sha(ROOT/E['prior_study']/E['prior_receipt'])==E['prior_receipt_sha256'],'Fresh complete prior APP/SDK/native/reader/IRQ/source proof retained');N,result=native(llvm);O=lib(READERS/'verify-ownership-v3.py');sc=contract(N,O);prov=lib(HERE/'provenance-v1.py')['provenance']();out=HERE/'build'/('composition-v1'if trial is None else trial)
    if trial:need(Path(trial).name==trial and not out.exists(),'Fresh create-only partial link')
    composed={};hashes={}
    for mode in ['c','cpp']:
        inputs=[PARENT/'build/composition-v1'/mode/'candidate.o',HERE/'build/native-v1'/mode/'unit.o'];need([sha(p)for p in inputs]==[E['SDK_parent_sha256'],result[mode]['CODE']['object_sha256']],'Exact current parent and new native unit');hashes[mode]={p.relative_to(ROOT).as_posix():sha(p)for p in inputs};f=out/mode
        if trial:
            f.mkdir(parents=True);p=subprocess.run([str(llvm/'ld.lld.exe'),'-r','--no-relax',*[str(q)for q in inputs],'-o',str(f/'candidate.o')],capture_output=True,timeout=120);(f/'link.log').write_text(N['portable']((p.stdout+p.stderr).decode('utf-8','replace'),llvm),encoding='utf-8');need(p.returncode==0,'Actual partial link failed;trial retained')
        composed[mode]=composition(f/'candidate.o',inputs,N,O)
    need(composed['c']==composed['cpp'],'Actual complete C/C++ composition objects equal');inventory=lib(HERE/'indirect-inventory-v1.py')['inventory'](composed['c']['object_sha256']);need(inventory['counts']=={'return':169,'encoded-static-AUIPC-JALR-pair':146,'encoded-register-transfer':51}and inventory['literal56CDC']['destination_bytes_included'],'Whole actual instruction inventory and newly included56CDC body')
    return dict(schema='TSL9-scheduled-record-callback-audit-v1',passed=True,checker_sha256=sha(__file__),inventory_checker_sha256=CHECKER_PINS['indirect-inventory-v1.py'],provenance_checker_sha256=CHECKER_PINS['provenance-v1.py'],native_results=result,contract=sc,provenance=prov,indirect_inventory=inventory,composition=composed,composition_input_hashes=hashes,prior_root_callees_receipt_sha256=E['prior_receipt_sha256'],new_CODE_bytes=174,new_instructions=62,new_complete_functions=2,new_genuine_named_dependencies=0,APP_source_C_H_files_unchanged=159,APP_byte_coverage_unchanged=95.54,inherited_startup_source_gap_bytes=4,installed_ROM_identity_proved=False,physical_RAM_capacity_proved=False,physical_Xwchc_profile_proved=False,physical_trap_route_proved=False,Flash_callback_effects_closed=False,actual_global_binding_before_any_dispatch_proved=False,all_remaining_callee_effects_proved=False,linked_into_APP=False,runtime_closed=False,new_BIN=False,firmware_ready=False,goal_complete=False,target_executed=False,HOST_model_executed=False,ISA_emulated=False,hardware_accessed=False,network=False)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--tool-dir',type=Path,required=True);p.add_argument('--reference-root',type=Path,required=True);p.add_argument('--link-trial');p.add_argument('--output',type=Path);a=p.parse_args()
    try:
        v=audit(a.tool_dir.resolve(),a.reference_root.resolve(),a.link_trial)
        if a.output:
            target=HERE/a.output;need(target.parent==HERE and not target.exists(),'Create-only scheduled-record audit receipt');target.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')
        c=v['composition']['c'];print(json.dumps(dict(passed=True,new_CODE_bytes=174,new_instructions=62,complete_functions=2,composition_CODE_bytes=c['CODE_bytes'],composition_DATA_bytes=c['DATA_bytes'],named_UND=len(c['named_UND']),register_transfer_sites_requiring_binding_analysis=51,conditional_callback_original_PC=0x56cdc,ID31_and47_not_covered=True,new_BIN=False)))
    except Exception as error:
        message=str(error)
        for path,token in [(ROOT,'${PROJECT_ROOT}'),(Path.home(),'${USERPROFILE}')]:message=message.replace(str(path),token).replace(path.as_posix(),token)
        print(json.dumps(dict(passed=False,error_type=type(error).__name__,reason=message)));raise SystemExit(1)
