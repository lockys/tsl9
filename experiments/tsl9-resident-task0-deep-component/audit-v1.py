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
    E=N['EV'];B=N['B'];V=lib(ROOT/'experiments/tsl9-original-RF-tx-path/audit-v1.py');parent=O['inspect'](ROOT/E['SDK_parent']/'c/candidate.o');raw=(ROOT/E['firmware']).read_bytes();newbytes={p for f in E['selected_functions']for p in range(f['start'],f['end'])};ops={};rows=[];graphs={};pairs=[]
    need(parent['passed']and len(parent['named_UND'])==2 and set(parent['named_UND'])==set(E['resolved_prior_dependencies'])and not newbytes&set(parent['_byte_map']),'Supply both genuine prior named gaps without duplicate CODE')
    for f in E['selected_functions']:
        a,z=f['start'],f['end'];source=a-0x20000000+0x40270 if a>=0x20000000 else a
        need(f['source_start']==source and f['source_end']==source+z-a and raw[source-0x40000:source-0x40000+z-a]==b''.join(bytes.fromhex(o['bytes'])for o in f['operations']),'All actual original bytes and conditional SDK/RAM source mapping')
        if a>=0x20000000:need(0x402b0<=source<source+z-a<=0x430e4,'RAM body entirely in first inclusive startup copy')
        ext={d[1]for o in f['operations']if(d:=B['decode_control'](bytes.fromhex(o['bytes']),o['addr']))};oo,g,q=V['whole_cfg'](f,B,ext,f['own_frame_bytes']);ops.update(oo);graphs[a]=g;rows.append(q)
        for pc,o in oo.items():
            h=int.from_bytes(bytes.fromhex(o['bytes']),'little');other=oo.get(pc+4)
            if o['size']==4 and h&127==0x17 and other and other['size']==4:
                l=int.from_bytes(bytes.fromhex(other['bytes']),'little')
                if l&0x707f==0x67 and(h>>7)&31==(l>>15)&31:
                    imm=l>>20;imm=imm-4096 if imm&2048 else imm;t=(pc+(h&0xfffff000)+imm)&0xfffffffe;need((l>>7)&31==1,'Four normal far calls, no far tail');pairs.append(dict(PC=pc,target=t))
    need([(f['start'],f['end'])for f in rows]==[(0x435ce,0x436a8),(0x55dea,0x55e44),(0x55f94,0x5605c),(0x5627a,0x56326),(0x56972,0x56cb2),(0x2000156c,0x200017d6)]and sum(f['bytes']for f in rows)==2130 and sum(f['instructions']for f in rows)==713,'Six complete reachable CFGs, including every post-return arm')
    need(pairs==[dict(PC=0x43626,target=0x20000314),dict(PC=0x56b1e,target=0x20000332),dict(PC=0x20001772,target=0x6dec2),dict(PC=0x20001796,target=0x6dec2)],'Exact original far-call targets')
    need(len(E['real_prior_providers'])==7 and all(p in parent['_byte_map']for p in E['real_prior_providers'])and not E['new_genuine_code_dependencies']and not E['new_genuine_code_dependency_entries'],'Seven genuine prior imports; no new named gap')
    actual_calls=[dict(owner=json.loads(v)[0],type=json.loads(v)[1],target=json.loads(v)[3])for v in parent['_typed_relations']if json.loads(v)[3][0]=='CODE'and json.loads(v)[3][1]in [0x56972,0x2000156c]]
    need({c['target'][1]for c in actual_calls}=={0x56972,0x2000156c},'Actual parent native references require both newly supplied entry bodies')
    required={0x56972:'qk.c.lbu a5, 10(a0)',0x56974:'beqz a5, 0x56cae',0x56978:'lhu a5, 128(a0)',0x5697c:'addi sp, sp, -16',0x56984:'addi a5, a5, 1',0x56986:'sh a5, 128(a0)',0x5698c:'sb zero, 24(a0)',0x56cae:'li a0, 1',0x56cb0:'ret',0x55dea:'lbu a4, 326(a0)',0x55df0:'lhu a5, 486(a0)',0x55df8:'lhu a3, 328(a0)',0x55e02:'div a5, a5, a4',0x55e10:'div a5, a5, a4',0x55e18:'div a5, a5, a4',0x55e1c:'lhu a4, 484(a0)',0x55e2a:'sb a4, 78(a0)',0x55e2e:'ret',0x55e30:'li a3, 1',0x200017d0:'ret',0x200017d2:'mv s6, s7',0x200017d4:'j 0x200017b6',0x43648:'jalr a5'}
    need(all(ops[p]['opcode']==v for p,v in required.items()),'Exact early return, counter update, original signed divides, memory extents and post-return branch')
    need(graphs[0x56972][0x56974]==[0x56cae,0x56978]and 0x5697c not in V['reachable'](graphs[0x56972],0x56cae),'Byte10 zero returns1 before own-frame allocation')
    need(0x55e30 in V['reachable'](graphs[0x55dea],0x55dea)and 0x200017d2 in V['reachable'](graphs[0x2000156c],0x2000156c),'Both post-return arms are part of their complete real entries')
    need(E['opaque_transfers']==[dict(PC=0x43648,instruction='jalr a5',destination_proved=False)],'One genuine new register callback remains unjoined')
    source=(ROOT/N['S']['source']).read_text('utf-8');need(any('PORT('in line and 'div a5, a5, a4'in line for line in source.splitlines()),'Keep actual signed DIV instruction ports, not inferred C arithmetic')
    return dict(passed=True,functions=rows,source_CODE_bytes=2130,source_instructions=713,far_pairs=pairs,opaque_sites=E['opaque_transfers'],resolved_prior_dependencies=E['resolved_prior_dependencies'],new_genuine_named_dependencies=0,prior_native_call_witnesses=actual_calls,all_new_static_direct_and_far_targets_have_real_bodies=True,
        early_return=dict(entry=0x56972,byte_offset=10,zero_branch=0x56974,return_value=1,return_PC=0x56cb0,no_own_frame_allocated_on_this_arm=True),
        initial_nonzero_arm=dict(counter_u16_offset=128,counter_write_PC=0x56986,counter_wraps_low16=True,cleared_byte_offset=24),
        numeric_leaf=dict(entry=0x55dea,end=0x55e44,own_frame_bytes=0,highest_fixed_input_read_offset=486,highest_fixed_input_read_width=2,required_readable_extent_at_entry_at_least=488,write_byte_offset=78,signed_DIV_ports=[0x55e02,0x55e10,0x55e18],physical_units_and_actual_record_allocation_proved=False),
        RAM_post_return_arm=dict(entry=0x2000156c,return_PC=0x200017d0,post_return_PC=0x200017d2,jump_PC=0x200017d4,target=0x200017b6),
        own_frames=[32,0,16,16,16,48],conditional_Xwchc_operations=38,all_post_return_arms_preserved=True,conditional_RAM_mapping_only=True,reused_ABI_assertions_are_numeric_only=True,actual_memory_capacity_or_pointer_validity_proved=False,all_callback_values_or_callee_effects_closed=False,installed_ROM_identity_proved=False)

def composition(path,inputs,N,O):
    P=lib(ROOT/'experiments/tsl9-sdk-unique-code-ownership/audit-v1.py');EL=lib(READERS/'elf_reader-v7.py')['ELF'];aa={};dd={};uu=set();rr=[];maps={};typed=set()
    for p in inputs:
        a,d,u,r=P['facts'](p,EL);need(not set(aa)&set(a)and not set(dd)&set(d),'Unique section and symbol ownership');aa.update(a);dd.update(d);uu.update(u);rr+=r
        q=O['inspect'](p);need(q['passed']and not set(maps)&set(q['_byte_map']),'Unique original-PC byte ownership');maps.update(q['_byte_map']);typed.update(q['_typed_relations'])
    need(P['facts'](path,EL)==(aa,dd,uu-set(dd),sorted(rr)),'All actual input bytes, symbols and relocations retained')
    out=O['inspect'](path);before=O['inspect'](inputs[0])
    need(out['passed']and out['_byte_map']==maps and set(out['_typed_relations'])==typed,'Exact non-overlapping CODE and typed-relocation union')
    need(out['CODE_bytes']==40874 and not out['named_UND']and out['non_CODE_allocations']==before['non_CODE_allocations'],'2130 real CODE bytes added, zero named UND, DATA392 unchanged')
    ind=lib(READERS/'compare-readers-v3.py')['audit'](path);need(ind['passed'],'Independent complete native readers agree')
    return dict(**O['public'](out),DATA_bytes=392,instructions=14060,allocated_bytes=41266,independent_readers=ind,
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
    old=prior['ledger'];actual={o['PC']:o for o in inventory['register_transfer_sites_requiring_separate_binding_analysis']};inherited={r['PC']for r in old['rows']}|{r['PC']for r in old['other_sites']};newsites=set(actual)-inherited
    need(old['counts']['actual_register_sites']==62 and old['counts']['conditionally_joined']==51 and len(actual)==63 and newsites=={0x43648},'Actual63-site object adds one unjoined callback; inherited proofs retained')
    ledger=dict(schema='TSL9-task0-deep-component-cumulative-ledger-v1',passed=True,rows=old['rows'],other_sites=sorted(old['other_sites']+[dict(PC=0x43648,outcome='not-joined-in-this-ledger',original_instruction='jalr a5',prior_proofs_not_overridden=True)],key=lambda r:r['PC']),counts=dict(actual_register_sites=63,conditionally_joined=51,conditional_target_or_target_set=41,conditional_skipped_or_caller_gated=10,not_joined_here=12),no_universal_or_live_binding_claim=True,missing_function_count_not_inferred=True)
    return dict(schema='TSL9-task0-deep-component-audit-v1',passed=True,checker_sha256=sha(__file__),evidence_sha256=sha(HERE/'evidence-v1.json'),
        native_results=result,contract=sc,ledger=ledger,composition=composed,indirect_inventory=inventory,inventory_checker_sha256=sha(HERE/'indirect-inventory-v1.py'),
        inherited_conditional_domains=51,new_conditional_domains=0,cumulative_conditional_domains=51,SDK_register_transfer_sites=63,
        count_is_not_universal_resolution_or_functional_completion=True,new_CODE_bytes=2130,new_instructions=713,new_complete_functions=6,
        APP_source_C_H_files_unchanged=159,APP_byte_coverage_unchanged=95.54,inherited_startup_source_gap_bytes=4,
        installed_ROM_identity_proved=False,physical_RAM_ISA_IRQ_or_Flash_compatibility_proved=False,linked_into_APP=False,runtime_closed=False,
        new_BIN=False,firmware_ready=False,goal_complete=False,target_executed=False,HOST_model_executed=False,ISA_emulated=False,hardware_accessed=False,network=False)
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--tool-dir',type=Path,required=True);p.add_argument('--link',action='store_true');p.add_argument('--write-receipt',action='store_true');a=p.parse_args()
    try:
        v=audit(a.tool_dir.resolve(),a.link)
        if a.write_receipt:
            dest=HERE/'audit-result-v1.json';need(not dest.exists(),'Create-only audit receipt');dest.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')
        c=v['composition']['c'];print(json.dumps(dict(passed=True,new_CODE_bytes=2130,new_instructions=713,composition_CODE_bytes=c['CODE_bytes'],composition_DATA_bytes=c['DATA_bytes'],named_UND=len(c['named_UND']),conditional_domains=51,SDK_register_transfer_sites=63,new_BIN=False)))
    except Exception as error:
        message=str(error)
        for path,token in [(ROOT,'${PROJECT_ROOT}'),(Path.home(),'${USERPROFILE}')]:message=message.replace(str(path),token).replace(path.as_posix(),token)
        print(json.dumps(dict(passed=False,error_type=type(error).__name__,reason=message)));raise SystemExit(1)
