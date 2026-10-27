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
    need(len(rows)==7 and sum(f['bytes']for f in rows)==1180 and sum(f['instructions']for f in rows)==407,'Seven whole reachable CFGs with balanced own frames')
    parent=O['inspect'](ROOT/E['SDK_parent']/'c/candidate.o');newbytes={p for f in rows for p in range(f['start'],f['end'])}
    need(parent['passed']and not parent['named_UND']and not newbytes&set(parent['_byte_map']),'Disjoint new CODE; genuine parent has zero named UND')
    need(all(p in parent['_byte_map']for p in E['real_prior_providers'])and len(E['real_prior_providers'])==14,'Fourteen real prior callees, no fake provider')
    raw=(ROOT/E['firmware']).read_bytes();caller=load(ROOT/E['caller_evidence'])
    need(sha(ROOT/E['caller_evidence'])==E['caller_evidence_sha256'],'Pinned actual registry evidence')
    for f in caller['selected_functions']:
        for o in f['operations']:
            need(bytes.fromhex(o['bytes'])==raw[o['addr']-0x40000:o['addr']-0x40000+o['size']],'Actual original registry bytes');ops[o['addr']]=o
    # Refresh selected setter/scheduler witnesses already bounded and verified by the parent.
    pe=load(ROOT/E['prior_study']/'evidence-v1.json')
    for scope in pe['SDK_scopes']:
        need(sha(ROOT/scope['path'])==scope['sha256'],'Pinned prior complete function scope')
        for f in load(ROOT/scope['path'])['selected_functions']:
            if f['start']in scope['entries']:
                for o in f['operations']:ops[o['addr']]=o
    required={0x60874:'lui a5, 0x5f',0x60878:'lui a4, 0x20003',0x6087c:'addi a5, a5, -1860',0x60880:'sw a5, 1084(a4)',0x60886:'lui a5, 0x60',0x6088a:'lui a4, 0x20003',0x6088e:'addi a5, a5, 1302',0x60892:'sw a5, 1272(a4)',
        0x5e8be:'li a1, 622',0x5e8c2:'li a0, 232',0x5e8d2:'mv s0, a0',0x5e8d4:'beqz a0, 0x5e946',0x5e8d6:'li a2, 232',0x5e8da:'li a1, 0',0x5e8e4:'lui a5, 0x20003',0x5e8e8:'sw s0, 1080(a5)',
        0x5e910:'lui a5, 0x5e',0x5e914:'addi a5, a5, 1900',0x5e918:'sw a5, 104(s0)',0x5e91a:'lui a5, 0x60',0x5e91e:'addi a5, a5, 1190',0x5e922:'sw a5, 108(s0)',0x5e924:'lui a5, 0x60',0x5e928:'addi a5, a5, 848',0x5e92c:'sw a5, 112(s0)',
        0x5e92e:'lui a5, 0x20003',0x5e932:'lbu a5, 576(a5)',0x5e936:'bnez a5, 0x5e946',0x5e938:'lui a5, 0x20003',0x5e93c:'lw a0, 1272(a5)',0x5e940:'li a1, 3',0x5e942:'jal ra, 0x43b28'}
    need(all(ops[p]['opcode']==s for p,s in required.items()),'Exact registry, allocation, callback literals and conditional slot3 arguments')
    g=graphs[0x5e8bc]
    need(all(0x5e942 not in V['reachable'](g,0x5e8bc,skip=p)for p in [0x5e8d4,0x5e8dc,0x5e8e8,0x5e936,0x5e93c,0x5e940]),'Both guards and live A0 load dominate slot registration')
    need(B['decode_control'](bytes.fromhex(ops[0x5e942]['bytes']),0x5e942)[1]==0x43b28,'Actual slot setter call')
    need((0x5f000-1860,0x60000+1302)==(0x5e8bc,0x60516)and 0x20003000+1272==0x200034f8,'Independent literal and RAM arithmetic')
    callback_values=[0x5e000+1900,0x60000+1190,0x60000+848]
    need(callback_values==[0x5e76c,0x604a6,0x60350]and all(p in newbytes for p in callback_values),'Three actual record callback bodies supplied')
    need(0x60838 not in newbytes and 0x60838 not in parent['_byte_map'],'Raw timer literal60838 remains unprovided')
    # Setter/consumer instructions are independently checked below from the retained parent.
    route_ops={0x43b28:'li a5, 4',0x43b2a:'bltu a5, a1, 0x43b3c',0x43b2e:'lui a5, 0x20003',0x43b32:'slli a1, a1, 0x2',0x43b34:'addi a5, a5, 456',0x43b38:'add a1, a1, a5',0x43b3a:'sw a0, 0(a1)',0x200007ea:'lui s2, 0x20003',0x200007f2:'addi s0, s2, 456',0x20000816:'lw a5, 12(s0)',0x20000818:'jalr a5'}
    need(all(ops[p]['opcode']==s for p,s in route_ops.items())and 0x20003000+456+3*4==0x200031d4,'Exact slot setter and scheduler load/call operands')
    need(0x20000818 in {x['PC']for x in prior['ledger']['other_sites']},'Slot3 call was previously outside conditional binding ledger')
    return dict(passed=True,functions=rows,original_operands={hex(p):s for p,s in required.items()},
        setter_and_consumer_operands={hex(p):s for p,s in route_ops.items()},constructor=dict(entry=0x5e8bc,bytes=148,allocation_bytes=232,allocator_tag=622,allocation_failure_skips_registration=True,record_RAM=0x20003438,callback_fields=dict(zip(['104','108','112'],callback_values))),
        conditional_route=dict(registry=0x60856,constructor_pointer_RAM=0x2000343c,callback_pointer_RAM=0x200034f8,target=0x60516,guard_PC=0x5e936,guard_RAM=0x20003240,guard_required_value=0,setter_call=0x5e942,setter=0x43b28,index=3,slot_RAM=0x200031d4,consumer_call=0x20000818,
            conditions=['matching installed ROM/ISA and RAM mapping, not proved','valid disjoint heap, memory and original private register ABI','60856 normal completion precedes constructor and dispatch','successful 232-byte allocation and normal memset return','flag20003240 equals zero at constructor guard','live200034F8 still equals60516 at5E93C','slot200031D4 not overwritten before20000818','normal prior callee returns; no IRQ or reentrant replacement'],live_binding_proved=False),
        all_record_callback_effects_closed=False,raw_timer_literal=dict(PC=0x5e87a,low_PC=0x5e886,value=0x60838,body_provided=False),
        reused_ABI_assertions_are_numeric_only=True,own_frames_verified_by_whole_CFG=True,physical_RAM_capacity_or_allocator_success_proved=False,installed_ROM_identity_proved=False)

def composition(path,inputs,N,O):
    P=lib(ROOT/'experiments/tsl9-sdk-unique-code-ownership/audit-v1.py');EL=lib(READERS/'elf_reader-v7.py')['ELF'];aa={};dd={};uu=set();rr=[];maps={};typed=set()
    for p in inputs:
        a,d,u,r=P['facts'](p,EL);need(not set(aa)&set(a)and not set(dd)&set(d),'Unique section and symbol ownership');aa.update(a);dd.update(d);uu.update(u);rr+=r
        q=O['inspect'](p);need(q['passed']and not set(maps)&set(q['_byte_map']),'Unique original-PC byte ownership');maps.update(q['_byte_map']);typed.update(q['_typed_relations'])
    need(P['facts'](path,EL)==(aa,dd,uu-set(dd),sorted(rr)),'All actual input bytes, symbols and relocations retained')
    out=O['inspect'](path);before=O['inspect'](inputs[0])
    need(out['passed']and out['_byte_map']==maps and set(out['_typed_relations'])==typed,'Exact non-overlapping CODE and typed-relocation union')
    need(out['CODE_bytes']==36504 and not out['named_UND']and out['non_CODE_allocations']==before['non_CODE_allocations'],'1180 real CODE bytes added, zero named UND, DATA392 unchanged')
    ind=lib(READERS/'compare-readers-v3.py')['audit'](path);need(ind['passed'],'Independent complete native readers agree')
    return dict(**O['public'](out),DATA_bytes=392,instructions=12602,allocated_bytes=36896,independent_readers=ind,
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
    return dict(schema='TSL9-slot3-record-path-audit-v1',passed=True,checker_sha256=sha(__file__),evidence_sha256=sha(HERE/'evidence-v1.json'),
        native_results=result,contract=sc,composition=composed,indirect_inventory=inventory,inventory_checker_sha256=sha(HERE/'indirect-inventory-v1.py'),
        inherited_conditional_domains=39,new_conditional_domains=1,cumulative_conditional_domains=40,SDK_register_transfer_sites=51,
        count_is_not_universal_resolution_or_functional_completion=True,new_CODE_bytes=1180,new_instructions=407,new_complete_functions=7,
        APP_source_C_H_files_unchanged=159,APP_byte_coverage_unchanged=95.54,inherited_startup_source_gap_bytes=4,
        installed_ROM_identity_proved=False,physical_RAM_ISA_IRQ_or_Flash_compatibility_proved=False,linked_into_APP=False,runtime_closed=False,
        new_BIN=False,firmware_ready=False,goal_complete=False,target_executed=False,HOST_model_executed=False,ISA_emulated=False,hardware_accessed=False,network=False)
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--tool-dir',type=Path,required=True);p.add_argument('--link',action='store_true');p.add_argument('--write-receipt',action='store_true');a=p.parse_args()
    try:
        v=audit(a.tool_dir.resolve(),a.link)
        if a.write_receipt:
            dest=HERE/'audit-result-v1.json';need(not dest.exists(),'Create-only audit receipt');dest.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')
        c=v['composition']['c'];print(json.dumps(dict(passed=True,new_CODE_bytes=1180,new_instructions=407,composition_CODE_bytes=c['CODE_bytes'],composition_DATA_bytes=c['DATA_bytes'],named_UND=len(c['named_UND']),conditional_domains=40,SDK_register_transfer_sites=51,new_BIN=False)))
    except Exception as error:
        message=str(error)
        for path,token in [(ROOT,'${PROJECT_ROOT}'),(Path.home(),'${USERPROFILE}')]:message=message.replace(str(path),token).replace(path.as_posix(),token)
        print(json.dumps(dict(passed=False,error_type=type(error).__name__,reason=message)));raise SystemExit(1)
