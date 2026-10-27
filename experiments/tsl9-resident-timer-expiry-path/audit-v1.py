"""Audit seven real SDK bodies and conditional slot3 provenance; never execute target code."""
import argparse,hashlib,json,runpy,subprocess,sys
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
READERS=ROOT/'experiments/tsl9-resident-root-chain-callees'
def need(ok,label):
    if not ok:raise ValueError(label)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p):return json.loads(Path(p).read_bytes())
def lib(p):return runpy.run_path(str(p),run_name='slot3_record_audit_library')
def canonical(v):return json.loads(json.dumps(v))

def native(llvm):
    N=lib(HERE/'build-v1.py');N['pins'](llvm);saved=load(HERE/'build/native-v1/measurement.json')
    need(saved['inputs']==N['portable'](N['inputs'](llvm),llvm)and saved['candidate_contract']==N['candidate_contract'](),'Every real native input retained');out={}
    for mode in ['c','cpp']:
        f=HERE/'build/native-v1'/mode;v=saved['modes'][mode]
        need(v['artifacts']==N['inventory'](f)and v['dependencies']==N['portable'](N['dependencies'](f,llvm),llvm),'Exact compile artifacts and includes')
        out[mode]=dict(CODE=N['audit_object'](f/'unit.o'),ABI=N['audit_abi'](f/'config_abi.o'))
        need(out[mode]['CODE']==v['result']and out[mode]['ABI']==v['ABI_result'],'Fresh independent native readers match receipt')
    need(out['c']==out['cpp'],'Actual C11 and C++17 objects identical');return N,out

def contract(N,O,prior):
    E=N['EV'];B=N['B'];V=lib(ROOT/'experiments/tsl9-original-RF-tx-path/audit-v1.py');ops={};graphs={};rows=[]
    for f in E['selected_functions']:
        ext={d[1]for o in f['operations']if(d:=B['decode_control'](bytes.fromhex(o['bytes']),o['addr']))}
        oo,g,q=V['whole_cfg'](f,B,ext,f['own_frame_bytes']);ops.update(oo);graphs[f['start']]=g;rows.append(q)
    need([(f['start'],f['end'])for f in rows]==[(0x60754,0x60838),(0x60838,0x60856)]and sum(f['bytes']for f in rows)==258 and sum(f['instructions']for f in rows)==84,'Two complete reachable CFGs with balanced own16-byte frames')
    parent=O['inspect'](ROOT/E['SDK_parent']/'c/candidate.o');newbytes={p for f in rows for p in range(f['start'],f['end'])}
    need(parent['passed']and not parent['named_UND']and not newbytes&set(parent['_byte_map']),'Disjoint new real CODE, parent has zero named UND')
    need(len(E['real_prior_providers'])==6 and all(p in parent['_byte_map']for p in E['real_prior_providers']),'Six actual prior callee bodies')
    required={0x60838:'addi sp, sp, -16',0x6083a:'sw ra, 12(sp)',0x6083c:'li a5, -1',0x6083e:'sb a5, 49(a0)',0x60842:'li a2, 17',0x60844:'li a1, 128',0x60848:'li a0, 0',0x6084a:'jal ra, 0x5e3a8',0x6084e:'lw ra, 12(sp)',0x60850:'addi sp, sp, 16',0x60852:'j 0x60754',
        0x60758:'lui a5, 0x40024',0x60762:'lw s2, 524(a5)',0x60766:'sw zero, 524(a5)',0x6076a:'fence.i',0x607a6:'lui a5, 0x20003',0x607aa:'lw s0, 1080(a5)',0x607b2:'addi s1, s1, 412',0x607b6:'lw a0, 68(s0)',0x607b8:'sh zero, 10(s0)',0x607bc:'sb zero, 8(s0)',
        0x607c8:'qk.c.lbu a0, 3(s1)',0x607ca:'li a1, 4',0x607cc:'sh zero, 64(s0)',0x607d0:'sw zero, 68(s0)',0x607d4:'sw zero, 72(s0)',0x607d8:'jal ra, 0x439a8',0x607dc:'qk.c.lbu a0, 3(s1)',0x607de:'li a1, 8',0x607e0:'jal ra, 0x439a8',
        0x607e4:'lbu a0, 49(s0)',0x607e8:'li a5, 255',0x607ec:'beq a0, a5, 0x607fa',0x607f0:'jal ra, 0x43a14',0x607f4:'li a5, -1',0x607f6:'sb a5, 49(s0)',0x607fa:'lbu a0, 48(s0)',0x607fe:'li a5, 255',0x60802:'beq a0, a5, 0x60810',0x60806:'jal ra, 0x43a14',0x6080a:'li a5, -1',0x6080c:'sb a5, 48(s0)',
        0x60810:'lui a5, 0x20003',0x60814:'lbu a5, 576(a5)',0x60818:'beqz a5, 0x60824',0x6081a:'li a0, 0',0x60828:'lui a5, 0x40024',0x6082c:'sw s2, 524(a5)',0x60834:'addi sp, sp, 16',0x60836:'ret'}
    need(all(ops[p]['opcode']==s for p,s in required.items()),'Actual entry sentinel, no-link tail, record release, event stop, cancellation guards and save/restore operands')
    word=int.from_bytes(bytes.fromhex(ops[0x60852]['bytes']),'little')
    need(word&127==0x6f and(word>>7)&31==0 and B['decode_control'](bytes.fromhex(ops[0x60852]['bytes']),0x60852)[1]==0x60754,'Actual no-link tail after frame release')
    need(all(0x60852 not in V['reachable'](graphs[0x60838],0x60838,skip=p)for p in [0x6083e,0x6084a,0x6084e,0x60850]),'Sentinel write, helper return, restored RA and released frame dominate tail')
    producer=load(ROOT/E['prior_study']/'evidence-v1.json');source_ops={o['addr']:o for f in producer['selected_functions']for o in f['operations']}
    producer_required={0x5e876:'qk.c.lhu a2, 56(s1)',0x5e878:'beqz a2, 0x5e88e',0x5e87a:'lui a0, 0x61',0x5e87e:'addi a3, s1, 49',0x5e882:'slli a2, a2, 0x4',0x5e884:'mv a1, s1',0x5e886:'addi a0, a0, -1992',0x5e88a:'jal ra, 0x43874'}
    need(all(source_ops[p]['opcode']==v for p,v in producer_required.items())and 0x61000-1992==0x60838,'Actual original callback literal, record argument, timer scale and output-ID field')
    need(prior['contract']['raw_timer_literal']['value']==0x60838 and not prior['contract']['raw_timer_literal']['body_provided']and 0x60838 in newbytes,'Previous raw dependency now has genuine complete body')
    need(prior['cumulative_conditional_domains']==40 and prior['SDK_register_transfer_sites']==51,'Prior conditional domains retained without new universal resolution')
    return dict(passed=True,functions=rows,original_operands={hex(p):v for p,v in required.items()},producer_operands={hex(p):v for p,v in producer_required.items()},
        supplied_prior_literal=dict(value=0x60838,complete_body_bytes=30,linked_tail=0x60754,tail_body_bytes=228),
        producer=dict(entry=0x5e76c,call=0x5e88a,helper=0x43874,callback=0x60838,record_argument='original_s1',output_ID_offset=49,delay_expression='uint16_at_record_plus56 << 4',runtime_units_or_delivery_proved=False),
        expiry=dict(entry=0x60838,sentinel_write_PC=0x6083e,incoming_record_offset=49,value=255,helper_call=0x6084a,helper=0x5e3a8,A0=0,A1=128,A2=17,tail_PC=0x60852,tail=0x60754,no_own_frame_outstanding=True),
        cleanup=dict(entry=0x60754,record_pointer_RAM=0x20003438,release_pointer_offset=68,release_target=0x20000110,cleared_fields=[dict(offset=8,width=1),dict(offset=10,width=2),dict(offset=64,width=2),dict(offset=68,width=4),dict(offset=72,width=4)],
            task_ID_RAM=0x2000319f,stop_event_masks=[4,8],stop_helper=0x439a8,cancel_ID_offsets=[49,48],cancel_skip_value=255,cancel_helper=0x43a14,post_cancel_sentinel=255,
            optional_callback_clear=dict(guard_RAM=0x20003240,requires_nonzero=True,setter=0x2000078a,A0=0,pointer_RAM=0x20002ef8,does_not_clear_flag_RAM=0x20002efc),
            raw_register_save_zero_restore=dict(address=0x4002420c,save_PC=0x60762,zero_PC=0x60766,fence_I_PC=0x6076a,restore_PC=0x6082c,physical_register_meaning_or_irq_safety_proved=False)),
        conditions=['matching ROM/ISA/RAM profile and original private ABI, unproved','valid incoming record, global record pointer, stack and allocation ownership','helper/callee normal returns and no concurrent replacement','incoming callback record equals global record only if separately established','actual timer delivery, initialization order and physical effects unproved'],
        reused_ABI_assertions_are_numeric_only=True,own_frames_verified_by_whole_CFG=True,all_runtime_dependencies_closed=False,installed_ROM_identity_proved=False)

def composition(path,inputs,N,O):
    P=lib(ROOT/'experiments/tsl9-sdk-unique-code-ownership/audit-v1.py');EL=lib(READERS/'elf_reader-v7.py')['ELF'];aa={};dd={};uu=set();rr=[];maps={};typed=set()
    for p in inputs:
        a,d,u,r=P['facts'](p,EL);need(not set(aa)&set(a)and not set(dd)&set(d),'Unique section and symbol ownership');aa.update(a);dd.update(d);uu.update(u);rr+=r
        q=O['inspect'](p);need(q['passed']and not set(maps)&set(q['_byte_map']),'Unique original-PC byte ownership');maps.update(q['_byte_map']);typed.update(q['_typed_relations'])
    need(P['facts'](path,EL)==(aa,dd,uu-set(dd),sorted(rr)),'All actual input bytes, symbols and relocations retained')
    out=O['inspect'](path);before=O['inspect'](inputs[0])
    need(out['passed']and out['_byte_map']==maps and set(out['_typed_relations'])==typed,'Exact non-overlapping CODE and typed-relocation union')
    need(out['CODE_bytes']==36762 and not out['named_UND']and out['non_CODE_allocations']==before['non_CODE_allocations'],'258 real CODE bytes added, zero named UND, DATA392 unchanged')
    ind=lib(READERS/'compare-readers-v3.py')['audit'](path);need(ind['passed'],'Independent complete native readers agree')
    return dict(**O['public'](out),DATA_bytes=392,instructions=12686,allocated_bytes=37154,independent_readers=ind,
        every_input_byte_symbol_relocation_retained=True,actual_original_address_link_performed=False,linked_into_APP=False,runtime_closed=False,new_BIN=False,firmware_ready=False)

def audit(llvm,link=False):
    E=load(HERE/'evidence-v1.json');prior=lib(ROOT/E['prior_study']/E['prior_verifier'])[E['prior_entry']](llvm)
    need(canonical(prior)==load(ROOT/E['prior_study']/E['prior_receipt'])and sha(ROOT/E['prior_study']/E['prior_receipt'])==E['prior_receipt_sha256'],'Fresh full prior proof chain matches retained receipt')
    N,result=native(llvm);O=lib(READERS/'verify-ownership-v3.py');sc=contract(N,O,prior);out=HERE/'build/composition-v1'
    if link:need(not out.exists(),'Create-only real partial-link trial')
    composed={}
    for mode in ['c','cpp']:
        inputs=[ROOT/E['SDK_parent']/mode/'candidate.o',HERE/'build/native-v1'/mode/'unit.o'];need([sha(p)for p in inputs]==[E['SDK_parent_sha256'],result[mode]['CODE']['object_sha256']],'Pinned real parent and new unit');f=out/mode
        if link:
            f.mkdir(parents=True);p=subprocess.run([str(llvm/'ld.lld.exe'),'-r','--no-relax',*[str(q)for q in inputs],'-o',str(f/'candidate.o')],capture_output=True,timeout=120)
            (f/'link.log').write_text(N['portable']((p.stdout+p.stderr).decode('utf-8','replace'),llvm),encoding='utf-8');need(p.returncode==0,'Actual partial link; log retained')
        composed[mode]=composition(f/'candidate.o',inputs,N,O)
    need(composed['c']==composed['cpp'],'Complete actual C/C++ composition objects identical')
    inventory=lib(HERE/'indirect-inventory-v1.py')['inventory'](composed['c']['object_sha256'])
    need(len(inventory['register_transfer_sites_requiring_separate_binding_analysis'])==51,'No new unresolved register-transfer sites introduced')
    return dict(schema='TSL9-timer-expiry-path-audit-v1',passed=True,checker_sha256=sha(__file__),evidence_sha256=sha(HERE/'evidence-v1.json'),
        native_results=result,contract=sc,composition=composed,indirect_inventory=inventory,inventory_checker_sha256=sha(HERE/'indirect-inventory-v1.py'),
        inherited_conditional_domains=40,new_conditional_domains=0,cumulative_conditional_domains=40,SDK_register_transfer_sites=51,
        count_is_not_universal_resolution_or_functional_completion=True,new_CODE_bytes=258,new_instructions=84,new_complete_functions=2,
        APP_source_C_H_files_unchanged=159,APP_byte_coverage_unchanged=95.54,inherited_startup_source_gap_bytes=4,
        installed_ROM_identity_proved=False,physical_RAM_ISA_IRQ_or_Flash_compatibility_proved=False,linked_into_APP=False,runtime_closed=False,
        new_BIN=False,firmware_ready=False,goal_complete=False,target_executed=False,HOST_model_executed=False,ISA_emulated=False,hardware_accessed=False,network=False)
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--tool-dir',type=Path,required=True);p.add_argument('--link',action='store_true');p.add_argument('--write-receipt',action='store_true');a=p.parse_args()
    try:
        v=audit(a.tool_dir.resolve(),a.link)
        if a.write_receipt:
            dest=HERE/'audit-result-v1.json';need(not dest.exists(),'Create-only audit receipt');dest.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')
        c=v['composition']['c'];print(json.dumps(dict(passed=True,new_CODE_bytes=258,new_instructions=84,composition_CODE_bytes=c['CODE_bytes'],composition_DATA_bytes=c['DATA_bytes'],named_UND=len(c['named_UND']),conditional_domains=40,SDK_register_transfer_sites=51,new_BIN=False)))
    except Exception as error:
        message=str(error)
        for path,token in [(ROOT,'${PROJECT_ROOT}'),(Path.home(),'${USERPROFILE}')]:message=message.replace(str(path),token).replace(path.as_posix(),token)
        print(json.dumps(dict(passed=False,error_type=type(error).__name__,reason=message)));raise SystemExit(1)
