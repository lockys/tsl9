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
    E=N['EV'];B=N['B'];V=lib(ROOT/'experiments/tsl9-original-RF-tx-path/audit-v1.py');rows=[];ops={};graphs={};pairs=[]
    parent=O['inspect'](ROOT/E['SDK_parent']/'c/candidate.o');newbytes={p for f in E['selected_functions']for p in range(f['start'],f['end'])};raw=(ROOT/E['firmware']).read_bytes()
    need(parent['passed']and len(parent['named_UND'])==3 and set(E['resolved_prior_dependencies'])==set(parent['named_UND'])and not newbytes&set(parent['_byte_map']),'All three genuine prior gaps supplied without duplicate CODE')
    for f in E['selected_functions']:
        a,z=f['start'],f['end'];source=a-0x20000000+0x40270 if a>=0x20000000 else a
        need(f['source_start']==source and f['source_end']==source+z-a and raw[source-0x40000:source-0x40000+z-a]==b''.join(bytes.fromhex(o['bytes'])for o in f['operations']),'Every original whole body byte and conditional source mapping')
        if a>=0x20000000:need(0x402b0<=source<source+z-a<=0x430e4,'RAM body stays within actual first inclusive startup-copy extent')
        ext={d[1]for o in f['operations']if(d:=B['decode_control'](bytes.fromhex(o['bytes']),o['addr']))};oo,g,q=V['whole_cfg'](f,B,ext,f['own_frame_bytes']);ops.update(oo);graphs[a]=g;rows.append(q)
        for pc,o in oo.items():
            h=int.from_bytes(bytes.fromhex(o['bytes']),'little');other=oo.get(pc+4)
            if o['size']==4 and h&127==0x17 and other and other['size']==4:
                l=int.from_bytes(bytes.fromhex(other['bytes']),'little')
                if l&0x707f==0x67 and(h>>7)&31==(l>>15)&31:
                    imm=l>>20;imm=imm-4096 if imm&2048 else imm;t=(pc+(h&0xfffff000)+imm)&0xfffffffe;link=(l>>7)&31;need(link in [0,1],'Only real normal calls and no-link tail');pairs.append(dict(PC=pc,target=t,link_register=link))
    need([(f['start'],f['end'])for f in rows]==[(0x436a8,0x43728),(0x20000d50,0x20001122),(0x20001122,0x2000138e),(0x200014c6,0x2000156c)]and sum(f['bytes']for f in rows)==1892 and sum(f['instructions']for f in rows)==626,'Four complete actual bodies with all post-return reachable arms')
    need(len(pairs)==17 and sum(p['link_register']==1 for p in pairs)==16 and [p for p in pairs if p['link_register']==0]==[dict(PC=0x2000111a,target=0x4354a,link_register=0)],'Sixteen normal far calls and one genuine no-link tail')
    need(len(E['real_prior_providers'])==10 and all(p in parent['_byte_map']for p in E['real_prior_providers']),'Ten actual prior provider bodies')
    need(E['new_genuine_code_dependency_entries']==[0x56972,0x2000156c]and len(E['new_genuine_code_dependencies'])==2 and all(p not in parent['_byte_map']and p not in newbytes for p in E['new_genuine_code_dependency_entries']),'Two deeper callee gaps preserved without fake providers')
    calls=[dict(owner=json.loads(v)[0],type=json.loads(v)[1],target=json.loads(v)[3])for v in parent['_typed_relations']if json.loads(v)[3][0]=='CODE'and json.loads(v)[3][1]in [0x436a8,0x20000d50,0x20001122]]
    need({c['target'][1]for c in calls}=={0x436a8,0x20000d50,0x20001122},'Real parent native relocations reference all three newly supplied callees')
    required={0x436c4:'li a5, 15',0x436c6:'bltu a5, a0, 0x4371c',0x436ca:'li a4, 12',0x436cc:'mul a4, a0, a4',0x436d0:'lui a5, 0x20003',0x436d4:'lw a5, 556(a5)',0x436d8:'add a5, a5, a4',0x436da:'lw a5, 0(a5)',0x436dc:'beqz a5, 0x4371c',0x436de:'li s0, 1',0x436e0:'sll s0, s0, a0',0x436e4:'slli s0, s0, 0x10',0x436e6:'c.srli s0, s0, 0x10',0x436e8:'mv s1, a1',0x436ea:'li a0, 0',0x436ec:'mv a1, s0',0x436f6:'mv s3, a0',0x436f8:'beqz a0, 0x43704',0x436fa:'mv a1, s0',0x436fc:'li a0, 0',0x436fe:'jal 0x4358a',0x43700:'sw s1, 8(s3)',0x4370c:'li a0, 0',0x43724:'li a0, 2',0x20000ec4:'addi sp, sp, 32',0x20000ec6:'jr t1',0x20001118:'addi sp, sp, 32',0x2000111a:'auipc t1, 0xe0042',0x2000111e:'jr 1072(t1)'}
    need(all(ops[p]['opcode']==v for p,v in required.items()),'Exact record-ID guard, timer lookup/update, null continuation, returns and released-frame tails')
    need(dict(PC=0x436ee,target=0x20000314,link_register=1)in pairs,'Actual timer lookup far call')
    need(0x43700 not in V['reachable'](graphs[0x436a8],0x43704)and 0x4358a not in ops,'Null lookup skips the write; real event-clear helper remains external')
    for pc in [0x20000ec6,0x2000111a]:
        release=0x20000ec4 if pc==0x20000ec6 else 0x20001118
        need(pc not in V['reachable'](graphs[0x20000d50],0x20000d50,skip=release),'Own32-byte frame released before each selected tail')
    opaque=E['opaque_transfers'];need(len(opaque)==11 and all(ops[o['PC']]['opcode']==o['instruction']for o in opaque),'Eleven exact original unjoined register-transfer sites retained')
    return dict(passed=True,functions=rows,source_CODE_bytes=1892,source_instructions=626,far_pairs=pairs,opaque_sites=opaque,prior_native_call_witnesses=calls,resolved_prior_dependencies=E['resolved_prior_dependencies'],genuine_missing_callee_entries=E['new_genuine_code_dependency_entries'],
        record_update_helper=dict(entry=0x436a8,ID_range=[0,15],record_stride=12,record_array_pointer_RAM=0x2000322c,requires_nonzero_callback_word=True,lookup=0x20000314,lookup_task_ID=0,lookup_event='low16(1 << input_ID)',normal_lookup_null_returns_zero_without_update=True,event_clear_helper=0x4358a,successful_lookup_write_offset=8,write_value='entry_A1',invalid_ID_or_empty_record_returns=2,normal_guard_pass_returns=0,return_zero_does_not_prove_timer_updated_or_physical_success=True),
        own_frames=[32,32,32,48],conditional_Xwchc_operations=26,all_post_return_arms_preserved=True,conditional_RAM_copy_mapping_only=True,reused_ABI_assertions_are_numeric_only=True,raw_MMIO_meaning_IRQ_safety_or_timer_units_proved=False,all_callback_values_or_callee_effects_closed=False,installed_ROM_identity_proved=False)

def composition(path,inputs,N,O):
    P=lib(ROOT/'experiments/tsl9-sdk-unique-code-ownership/audit-v1.py');EL=lib(READERS/'elf_reader-v7.py')['ELF'];aa={};dd={};uu=set();rr=[];maps={};typed=set()
    for p in inputs:
        a,d,u,r=P['facts'](p,EL);need(not set(aa)&set(a)and not set(dd)&set(d),'Unique section and symbol ownership');aa.update(a);dd.update(d);uu.update(u);rr+=r
        q=O['inspect'](p);need(q['passed']and not set(maps)&set(q['_byte_map']),'Unique original-PC byte ownership');maps.update(q['_byte_map']);typed.update(q['_typed_relations'])
    need(P['facts'](path,EL)==(aa,dd,uu-set(dd),sorted(rr)),'All actual input bytes, symbols and relocations retained')
    out=O['inspect'](path);before=O['inspect'](inputs[0])
    need(out['passed']and out['_byte_map']==maps and set(out['_typed_relations'])==typed,'Exact non-overlapping CODE and typed-relocation union')
    need(out['CODE_bytes']==38744 and out['named_UND']==sorted(N['EV']['new_genuine_code_dependencies'])and out['non_CODE_allocations']==before['non_CODE_allocations'],'1892 real CODE bytes added, two genuine named UND, DATA392 unchanged')
    ind=lib(READERS/'compare-readers-v3.py')['audit'](path);need(ind['passed'],'Independent complete native readers agree')
    return dict(**O['public'](out),DATA_bytes=392,instructions=13347,allocated_bytes=39136,independent_readers=ind,
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
    old=prior['ledger'];actual={o['PC']:o for o in inventory['register_transfer_sites_requiring_separate_binding_analysis']};joined={r['PC']for r in old['rows']};newsites=set(actual)-joined
    need(old['counts']['conditionally_joined']==51 and len(actual)==62 and len(newsites)==11 and newsites=={o['PC']for o in sc['opaque_sites']},'All51 inherited domains retained; eleven genuinely added sites are unjoined')
    ledger=dict(schema='TSL9-task0-RAM-dependency-cumulative-ledger-v1',passed=True,rows=old['rows'],other_sites=[dict(PC=p,outcome='not-joined-in-this-ledger',original_instruction=next(o['instruction']for o in sc['opaque_sites']if o['PC']==p),prior_proofs_not_overridden=True)for p in sorted(newsites)],counts=dict(actual_register_sites=62,conditionally_joined=51,conditional_target_or_target_set=41,conditional_skipped_or_caller_gated=10,not_joined_here=11),no_universal_or_live_binding_claim=True,missing_function_count_not_inferred=True)
    return dict(schema='TSL9-task0-RAM-dependencies-audit-v1',passed=True,checker_sha256=sha(__file__),evidence_sha256=sha(HERE/'evidence-v1.json'),
        native_results=result,contract=sc,ledger=ledger,composition=composed,indirect_inventory=inventory,inventory_checker_sha256=sha(HERE/'indirect-inventory-v1.py'),
        inherited_conditional_domains=51,new_conditional_domains=0,cumulative_conditional_domains=51,SDK_register_transfer_sites=62,
        count_is_not_universal_resolution_or_functional_completion=True,new_CODE_bytes=1892,new_instructions=626,new_complete_functions=4,
        APP_source_C_H_files_unchanged=159,APP_byte_coverage_unchanged=95.54,inherited_startup_source_gap_bytes=4,
        installed_ROM_identity_proved=False,physical_RAM_ISA_IRQ_or_Flash_compatibility_proved=False,linked_into_APP=False,runtime_closed=False,
        new_BIN=False,firmware_ready=False,goal_complete=False,target_executed=False,HOST_model_executed=False,ISA_emulated=False,hardware_accessed=False,network=False)
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--tool-dir',type=Path,required=True);p.add_argument('--link',action='store_true');p.add_argument('--write-receipt',action='store_true');a=p.parse_args()
    try:
        v=audit(a.tool_dir.resolve(),a.link)
        if a.write_receipt:
            dest=HERE/'audit-result-v1.json';need(not dest.exists(),'Create-only audit receipt');dest.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')
        c=v['composition']['c'];print(json.dumps(dict(passed=True,new_CODE_bytes=1892,new_instructions=626,composition_CODE_bytes=c['CODE_bytes'],composition_DATA_bytes=c['DATA_bytes'],named_UND=len(c['named_UND']),conditional_domains=51,SDK_register_transfer_sites=62,new_BIN=False)))
    except Exception as error:
        message=str(error)
        for path,token in [(ROOT,'${PROJECT_ROOT}'),(Path.home(),'${USERPROFILE}')]:message=message.replace(str(path),token).replace(path.as_posix(),token)
        print(json.dumps(dict(passed=False,error_type=type(error).__name__,reason=message)));raise SystemExit(1)
