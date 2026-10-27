"""Audit seven real SDK bodies and conditional slot3 provenance; never execute target code."""
import argparse,hashlib,json,re,runpy,subprocess,sys
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

PURE={'beq','beqz','bgez','ble','bleu','blez','bltu','bltz','bge','bgeu','bgtu','bne','bnez','j','jr','ret','fence.i','nop'}
STORES={'sb','sh','sw','qk.c.sb','qk.c.sh','qk.c.sbsp','qk.c.shsp'}
RESULT={'add','addi','and','andi','auipc','divu','lb','lbu','lh','lhu','li','lui','lw','mv','mul','neg','or','ori','qk.c.lbu','qk.c.lbusp','qk.c.lhu','qk.c.lhusp','remu','seqz','sll','slli','sltu','sltiu','snez','sra','srai','srl','srli','sub','xor','xori'}
def reaching(site,reg):
    root=owners[site];key=root,reg
    if key not in cache:
        g=graphs[root];incoming={p:set()for p in g};incoming[root].add(-1);todo=[root]
        while todo:
            pc=todo.pop();o=ops[pc];mn=o['opcode'].split()[0]
            if o['type']in ['call','ucall']or mn in ['jal','jalr']:writes=not reg.startswith('s')
            elif mn in PURE|STORES:writes=False
            else:
                assert mn in RESULT,('unmodelled writer',hex(pc),mn)
                writes=o['opcode'].partition(' ')[2].split(',')[0]==reg
            outgoing={pc}if writes else incoming[pc]
            for n in g[pc]:
                before=len(incoming[n]);incoming[n]|=outgoing
                if before!=len(incoming[n]):todo.append(n)
        cache[key]=incoming
    return cache[key][site]

def contract(N,O,prior):
    global ops,graphs,owners,cache
    P=load(HERE/'provenance-inputs-v1.json');need(all(sha(ROOT/p)==h for p,h in P['reference_inputs'].items()),'Frozen actual producer/consumer/reaching-definition references')
    B=N['B'];V=lib(ROOT/'experiments/tsl9-original-RF-tx-path/audit-v1.py');ops={};graphs={};owners={};cache={};rows=[]
    raw=(ROOT/N['EV']['firmware']).read_bytes();parent=O['inspect'](ROOT/N['EV']['SDK_parent']/'c/candidate.o')
    for name,entries in P['scopes'].items():
        fs=[f for f in load(ROOT/'experiments'/name/'evidence-v1.json')['selected_functions']if f['start']in entries];need(len(fs)==len(entries),'Every requested complete source body')
        for f in fs:
            a,z=f['start'],f['end'];data=raw[a-0x40000:z-0x40000];need(b''.join(bytes.fromhex(o['bytes'])for o in f['operations'])==data and hashlib.sha256(data).hexdigest()==f['original_sha256']and all(p in parent['_byte_map']for p in range(a,z)),'Every whole original reference byte has actual prior native owner')
            frame=max([int(m[1])for o in f['operations']if(m:=re.fullmatch(r'addi sp, sp, -(\d+)',o['opcode']))]or[0]);ext={d[1]for o in f['operations']if(d:=B['decode_control'](bytes.fromhex(o['bytes']),o['addr']))};oo,g,q=V['whole_cfg'](f,B,ext,frame)
            need(not set(ops)&set(oo),'Disjoint complete references');ops.update(oo);graphs[a]=g;owners.update({p:a for p in oo});rows.append(q)
    def exact(values):need(all(ops[p]['opcode']==v for p,v in values.items()),'Actual producer, index and callback operands')
    exact({0x567a0:'lw a4, 140(a1)',0x567a4:'lui a0, 0x20001',0x567ac:'addi a0, a0, 910',0x567b0:'addi a3, a1, 41',0x567b4:'j 0x43414',0x43462:'mv s5, a4',0x43464:'mv s4, a3',0x43466:'mv s7, a2',0x43468:'mv s6, a1',0x4346a:'mv s3, a0',0x43478:'li s0, 0',0x4347a:'li a3, 12',0x4347c:'li a5, 16',0x4347e:'mul s8, s0, a3',0x43482:'add a2, a4, s8',0x43486:'lw a2, 0(a2)',0x43488:'bnez a2, 0x4350e',0x434ca:'lw a5, 556(s2)',0x434e2:'add a5, a5, s8',0x434e4:'sw s3, 0(a5)',0x434e8:'sw s6, 4(a5)',0x434ec:'sw s5, 8(a5)',0x434f4:'sb s0, 0(s4)',0x4350e:'addi s0, s0, 1',0x43510:'bne s0, a5, 0x4347e',
        0x432be:'slli a0, a0, 0x4',0x432c0:'li a4, 12',0x432c2:'add a0, a0, s0',0x432c4:'mul a0, a0, a4',0x432c8:'lui a5, 0x20003',0x432cc:'lw s2, 556(a5)',0x432dc:'add s2, s2, a0',0x432de:'lw a4, 0(s2)',0x432e2:'beqz a4, 0x432ee',0x432e4:'lw a0, 4(s2)',0x432ea:'jalr a4',0x432f0:'mul s0, s0, a4',0x432f4:'lw a5, 556(s3)',0x432f8:'add s0, s0, a5',0x432fa:'lw a5, 8(s0)',0x432fc:'bnez a5, 0x43306',0x432fe:'sw zero, 0(s2)',0x43302:'sw zero, 4(s2)'})
    h=int.from_bytes(bytes.fromhex(ops[0x567a4]['bytes']),'little');l=int.from_bytes(bytes.fromhex(ops[0x567ac]['bytes']),'little');imm=l>>20;imm=imm-4096 if imm&2048 else imm
    need(h&127==0x37 and(h>>7)&31==10 and l&0x707f==0x13 and(l>>7)&31==(l>>15)&31==10 and((h&0xfffff000)+imm)&0xffffffff==0x2000138e,'Raw LUI/ADDI callback literal')
    paths=[]
    for use,definition,reg in [(0x567ac,0x567a4,'a0'),(0x567b4,0x567ac,'a0'),(0x434e4,0x4346a,'s3'),(0x434e8,0x43468,'s6'),(0x434ec,0x43462,'s5'),(0x432ea,0x432de,'a4'),(0x432de,0x432dc,'s2'),(0x432dc,0x432cc,'s2')]:
        actual=reaching(use,reg);need(actual=={definition},'Every reaching literal/register/pointer definition accounted for');paths.append(dict(use=use,register=reg,definitions=sorted(actual)))
    need(B['decode_control'](bytes.fromhex(ops[0x567b4]['bytes']),0x567b4)[1]==0x43414,'Actual direct no-link registration tail')
    f=N['EV']['selected_functions'][0];ext={d[1]for o in f['operations']if(d:=B['decode_control'](bytes.fromhex(o['bytes']),o['addr']))};newops,g,newcfg=V['whole_cfg'](f,B,ext,32)
    need((f['start'],f['end'],newcfg['bytes'],newcfg['instructions'])==(0x2000138e,0x200013e8,90,35),'Real whole RAM callback, including early return and post-return branch')
    need(f['source_start']==0x415fe and f['source_end']==0x41658 and raw[0x415fe-0x40000:0x41658-0x40000]==b''.join(bytes.fromhex(o['bytes'])for o in f['operations']),'Exact conditional startup RAM copy mapping')
    missing=N['EV']['new_genuine_code_dependencies'];need(len(missing)==3 and not parent['named_UND']and set(N['S']['undefined'])==set(missing)and not set(range(f['start'],f['end']))&set(parent['_byte_map']),'Three genuine missing bodies preserved; no overlap or fabricated provider')
    old=prior['ledger'];need(old['counts']['conditionally_joined']==50 and [r['PC']for r in old['other_sites']]==[0x432ea],'One previously unjoined SDK site')
    conditions=['matching installed ROM/ISA/RAM/copy profile, unproved','original56716 path reaches its tail43414 with literal2000138E','successful registration stores into actual first16 record slot k in0..15','record-array pointer and selected callback/parameter remain unchanged to consumer load','scheduler enters432A4 with original taskID0 and the selected event bit k','valid disjoint memory, record argument, stack and original private ABI','all prior callee normal returns; no IRQ/reentrant replacement','three callback callee bodies remain absent; target effects unproved']
    row=dict(PC=0x432ea,function=0x432a4,family='original-task0-record-callback',outcome='conditional-target',target_original_PC=0x2000138e,pointer_slot='RAM[2000322C] + 12*k',parameter_slot='RAM[2000322C] + 12*k + 4',conditions=conditions,live_binding_proved=False)
    ledger=dict(schema='TSL9-task0-record-cumulative-ledger-v1',passed=True,rows=sorted(old['rows']+[row],key=lambda r:r['PC']),other_sites=[],counts=dict(actual_register_sites=51,conditionally_joined=51,conditional_target_or_target_set=41,conditional_skipped_or_caller_gated=10,not_joined_here=0),no_universal_or_live_binding_claim=True,missing_function_count_not_inferred=True)
    need(len(ledger['rows'])==len({r['PC']for r in ledger['rows']})==51,'Exactly51 distinct evidenced domains, not global resolution')
    contract=dict(passed=True,reference_functions=rows,new_callback_CFG=newcfg,reaching_definitions=paths,literal_target=0x2000138e,registration_tail=0x567b4,registration_API=0x43414,record_array_pointer_RAM=0x2000322c,record_stride=12,registration_indices=[0,15],consumer_call=0x432ea,consumer_task_ID_domain=0,parameter_from_record_second_word=True,
        registration_fields=dict(callback_offset=0,parameter_offset=4,cleanup_mode_offset=8),conditional_consumer_formula='index=16*taskID+k; taskID0 => index=k',
        post_callback_cleanup=dict(fresh_record_array_pointer_load=0x432f4,third_word_load=0x432fa,nonzero_skips_clear=True,zero_clears_selected_callback_and_parameter=True,same_record_only_if_taskID0_and_stable_array_base=True,no_replacement_safety_proved=True),
        callback_source_mapping=dict(source=[0x415fe,0x41658],RAM=[0x2000138e,0x200013e8],installed_mapping_proved=False),genuine_missing_callee_entries=N['EV']['new_genuine_code_dependency_entries'],all_record_writers_or_callback_values_closed=False,actual_live_binding_or_all_callback_effects_proved=False,conditions=conditions)
    return contract,ledger

def composition(path,inputs,N,O):
    P=lib(ROOT/'experiments/tsl9-sdk-unique-code-ownership/audit-v1.py');EL=lib(READERS/'elf_reader-v7.py')['ELF'];aa={};dd={};uu=set();rr=[];maps={};typed=set()
    for p in inputs:
        a,d,u,r=P['facts'](p,EL);need(not set(aa)&set(a)and not set(dd)&set(d),'Unique section and symbol ownership');aa.update(a);dd.update(d);uu.update(u);rr+=r
        q=O['inspect'](p);need(q['passed']and not set(maps)&set(q['_byte_map']),'Unique original-PC byte ownership');maps.update(q['_byte_map']);typed.update(q['_typed_relations'])
    need(P['facts'](path,EL)==(aa,dd,uu-set(dd),sorted(rr)),'All actual input bytes, symbols and relocations retained')
    out=O['inspect'](path);before=O['inspect'](inputs[0])
    need(out['passed']and out['_byte_map']==maps and set(out['_typed_relations'])==typed,'Exact non-overlapping CODE and typed-relocation union')
    need(out['CODE_bytes']==36852 and out['named_UND']==sorted(N['EV']['new_genuine_code_dependencies'])and out['non_CODE_allocations']==before['non_CODE_allocations'],'90 real CODE bytes added, three genuine named UND, DATA392 unchanged')
    ind=lib(READERS/'compare-readers-v3.py')['audit'](path);need(ind['passed'],'Independent complete native readers agree')
    return dict(**O['public'](out),DATA_bytes=392,instructions=12721,allocated_bytes=37244,independent_readers=ind,
        every_input_byte_symbol_relocation_retained=True,actual_original_address_link_performed=False,linked_into_APP=False,runtime_closed=False,new_BIN=False,firmware_ready=False)

def audit(llvm,link=False):
    E=load(HERE/'evidence-v1.json');prior=lib(ROOT/E['prior_study']/E['prior_verifier'])[E['prior_entry']](llvm)
    need(canonical(prior)==load(ROOT/E['prior_study']/E['prior_receipt'])and sha(ROOT/E['prior_study']/E['prior_receipt'])==E['prior_receipt_sha256'],'Fresh full prior proof chain matches retained receipt')
    N,result=native(llvm);O=lib(READERS/'verify-ownership-v3.py');sc,ledger=contract(N,O,prior);out=HERE/'build/composition-v1'
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
    return dict(schema='TSL9-task0-RAM-callback-audit-v1',passed=True,checker_sha256=sha(__file__),evidence_sha256=sha(HERE/'evidence-v1.json'),
        native_results=result,contract=sc,ledger=ledger,composition=composed,indirect_inventory=inventory,inventory_checker_sha256=sha(HERE/'indirect-inventory-v1.py'),
        inherited_conditional_domains=50,new_conditional_domains=1,cumulative_conditional_domains=51,SDK_register_transfer_sites=51,
        count_is_not_universal_resolution_or_functional_completion=True,new_CODE_bytes=90,new_instructions=35,new_complete_functions=1,
        APP_source_C_H_files_unchanged=159,APP_byte_coverage_unchanged=95.54,inherited_startup_source_gap_bytes=4,
        installed_ROM_identity_proved=False,physical_RAM_ISA_IRQ_or_Flash_compatibility_proved=False,linked_into_APP=False,runtime_closed=False,
        new_BIN=False,firmware_ready=False,goal_complete=False,target_executed=False,HOST_model_executed=False,ISA_emulated=False,hardware_accessed=False,network=False)
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--tool-dir',type=Path,required=True);p.add_argument('--link',action='store_true');p.add_argument('--write-receipt',action='store_true');a=p.parse_args()
    try:
        v=audit(a.tool_dir.resolve(),a.link)
        if a.write_receipt:
            dest=HERE/'audit-result-v1.json';need(not dest.exists(),'Create-only audit receipt');dest.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')
        c=v['composition']['c'];print(json.dumps(dict(passed=True,new_CODE_bytes=90,new_instructions=35,composition_CODE_bytes=c['CODE_bytes'],composition_DATA_bytes=c['DATA_bytes'],named_UND=len(c['named_UND']),conditional_domains=51,SDK_register_transfer_sites=51,new_BIN=False)))
    except Exception as error:
        message=str(error)
        for path,token in [(ROOT,'${PROJECT_ROOT}'),(Path.home(),'${USERPROFILE}')]:message=message.replace(str(path),token).replace(path.as_posix(),token)
        print(json.dumps(dict(passed=False,error_type=type(error).__name__,reason=message)));raise SystemExit(1)
