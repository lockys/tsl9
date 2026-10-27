"""Prove conditional original-APP RF callback sources across all ten call sites; no execution."""
import argparse,hashlib,json,re,runpy,sys
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;R=HERE.parents[1]
def need(ok,label):
    if not ok:raise ValueError(label)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read_json(p):return json.loads(Path(p).read_bytes())
def lib(p):return runpy.run_path(str(R/p),run_name='RF_status_proof_library')
def canonical(v):return json.loads(json.dumps(v))
need(__debug__,'Strict assertions required; do not use optimized Python')
E=read_json(HERE/'evidence-v1.json')
need(all(sha(R/p)==h for p,h in E['reference_inputs'].items()),'All actual frozen reference sources and receipts')
SCOPES=E['scopes']
ROUTES=[(0x63f26,0x63f1c,'a5',0x63f18,None,'a5',1360),(0x64452,0x6443e,'t1',0x6443a,None,'a5',1360),(0x64588,0x64570,'t1',0x644bc,0x644c8,'s0',16),(0x64658,0x6464e,'a5',0x64638,0x6464a,'a5',16),(0x64690,0x64686,'a5',0x64682,None,'a5',1360),(0x6534c,0x65340,'a5',0x651a2,0x6533c,'s2',16),(0x6553e,0x65534,'a5',0x6540e,0x65530,'s2',16),(0x6555a,0x65550,'a5',0x6540e,0x6554a,'s2',16),(0x6565e,0x6564e,'t1',0x6563c,0x6564a,'a5',16),(0x657ae,0x657a4,'a5',0x65774,0x65778,'s0',16)]
B=runpy.run_path(str(R/'experiments/tsl9-original-startup/build-v1.py'));V=runpy.run_path(str(R/'experiments/tsl9-original-RF-tx-path/audit-v1.py'))
functions=[];selected=[];ops={};owners={};graphs={};cache={}
for name,entries in SCOPES.items():
    fs=[f for f in json.loads((R/'experiments'/name/'evidence-v1.json').read_bytes())['selected_functions']if f['start']in entries];assert len(fs)==len(entries)
    for f in fs:
        selected.append(f)
        frame=max([int(m[1])for o in f['operations']if(m:=re.fullmatch(r'addi sp, sp, -(\d+)',o['opcode']))]or[0]);ext={d[1]for o in f['operations']if(d:=B['decode_control'](bytes.fromhex(o['bytes']),o['addr']))}
        oo,g,q=V['whole_cfg'](f,B,ext,frame);assert not set(ops)&set(oo);ops.update(oo);owners.update({p:f['start']for p in oo});graphs[f['start']]=g;functions.append(q)
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

def native_witness(native):
    values=native['_byte_map'];relations=[json.loads(v)for v in native['_typed_relations']];rel={(v[0][1],v[1]):v[3]for v in relations if v[0][0]=='CODE'};sdk=(R/E['SDK_firmware']).read_bytes();need(sha(R/E['SDK_firmware'])==E['SDK_sha256'],'Actual SDK carrier')
    for f in selected:
        start,end=f['start'],f['end'];raw=sdk[start-0x40000:end-0x40000]
        need(len(raw)==end-start and b''.join(bytes.fromhex(o['bytes'])for o in f['operations'])==raw and hashlib.sha256(raw).hexdigest()==f['original_sha256'],'Every original complete selected body byte')
        current=bytes(values[p]for p in range(start,end));norm=bytearray(current);skip=set()
        for o in f['operations']:
            pc=o['addr'];off=pc-start;width=o['size'];ref=bytes.fromhex(o['bytes']);word=int.from_bytes(ref,'little')
            if pc in skip:continue
            d=B['decode_control'](ref,pc)
            if d:
                kind,target=d;w,mask=B['MASKS'][kind];n=int.from_bytes(current[off:off+w],'little')
                need(w==width and rel[(pc,kind)]==['CODE',target]and n&mask==word&mask and n&(~mask&((1<<(8*w))-1))==0,'Exact native direct transfer opcode, register and typed original target')
                norm[off:off+w]=(n|B['immediate'](kind,target-pc)).to_bytes(w,'little')
            elif width==4 and word&127==0x17 and rel.get((pc,23)):
                target=rel[(pc,23)];need(target[0]=='CODE'and rel[(pc+4,24)]==['CODE',pc],'Actual far-call HI/LO anchors')
                delta=(target[1]-pc)&0xffffffff
                for at,mask,imm in [(off,0xfff,(delta+0x800)&0xfffff000),(off+4,0xfffff,(delta&0xfff)<<20)]:
                    n=int.from_bytes(current[at:at+4],'little');v=int.from_bytes(raw[at:at+4],'little');need(n&mask==v&mask and not n&(~mask&0xffffffff),'Exact native far-call opcode/register and zero displacement');norm[at:at+4]=((n&mask)|imm).to_bytes(4,'little')
                skip.add(pc+4)
        need(bytes(norm)==raw,'Every native selected CODE byte equals original after address re-encoding')
    return dict(passed=True,complete_functions=9,CODE_bytes=2666,instructions=940,all_original_address_reencoded_bytes_equal=True)

def verify(llvm):
    prior=lib(E['prior_study']+'/'+E['prior_verifier'])[E['prior_entry']](llvm)
    need(canonical(prior)==read_json(R/E['prior_receipt']),'Fresh complete prior APP/native/ABI/CFG proof chain')
    O=lib('experiments/tsl9-resident-root-chain-callees/verify-ownership-v3.py');native=O['inspect'](R/E['SDK_native_object'])
    need(native['passed']and sha(R/E['SDK_native_object'])==E['SDK_native_object_sha256']==prior['composition']['c']['object_sha256'],'Actual current SDK native object')
    need(sha(R/E['SDK_native_object'].replace('/c/','/cpp/'))==E['SDK_native_object_sha256'],'Identical retained C/C++ native union')
    witness=native_witness(native);need(len(functions)==9 and sum(f['bytes']for f in functions)==2666 and sum(f['instructions']for f in functions)==940,'Nine complete whole CFGs')
    extra={0x64452:[(0x64468,0x64464,None,'a5',1360)],0x64588:[(0x645b2,0x645ae,None,'a5',1360)],0x6565e:[(0x6567e,0x6566c,0x6567a,'a5',16)],0x657ae:[(0x657cc,0x65774,0x65778,'s0',16)]}
    proof=[]
    for site,load,rd,hi,low,base,offset in ROUTES:
        loads=[(load,hi,low,base,offset)]+extra.get(site,[]);definitions={x[0]for x in loads}
        need(reaching(site,rd)==definitions,'All reaching callback definitions, including branch joins, accounted for')
        paths=[]
        for load,hi,low,base,offset in loads:
            need(ops[load]['opcode']==f'lw {rd}, {offset}({base})','Actual callback pointer load operands')
            h=int.from_bytes(bytes.fromhex(ops[hi]['bytes']),'little');need(ops[hi]['size']==4 and h&127==0x37 and h&0xfffff000==0x20003000,'Raw-decoded constant RAM LUI')
            need(ops[hi]['opcode'].startswith('lui '+base+', ')and reaching(load,base)=={low or hi},'Unique actual base definition reaches pointer load')
            value=h&0xfffff000
            if low is not None:
                need(ops[low]['opcode']==f'addi {base}, {base}, 1344'and reaching(low,base)=={hi},'Unchanged base reaches ADDI on every path');value+=1344
            need(value+offset==0x20003550,'All fourteen original loads read the same callback slot')
            paths.append(dict(load_PC=load,high_PC=hi,low_PC=low,base=base,offset=offset,slot=value+offset))
        arguments={}
        for reg in ['a0','a1','a2']:
            defs=sorted(reaching(site,reg));need(all(p in ops for p in defs),'No unknown incoming/call-clobbered argument definition');arguments[reg]=[dict(PC=p,instruction=ops[p]['opcode'])for p in defs]
        statuses=[]
        for d in arguments['a0']:
            m=re.fullmatch(r'li a0, (\d+)',d['instruction']);need(m is not None,'Every reaching status value is a literal');statuses.append(int(m[1]))
        proof.append(dict(PC=site,function=owners[site],pointer_register=rd,pointer_loads=paths,all_reaching_pointer_definitions=sorted(definitions),arguments=arguments,status_values=sorted(set(statuses)),direct_no_link_tail=ops[site]['opcode'].startswith('jr ')))
    bridge=lib('experiments/tsl9-original-RF-bridge/audit-v2.py')['APP_bridge'](lib('experiments/tsl9-original-RF-bridge/build-v1.py'))
    need(bridge['passed']and bridge['configuration_callback_literal']==0x174ee and bridge['conditional_global_RF_callback_storage']==0x20003550,'Fresh original APP source/BIN/native diagnostic route')
    ae=read_json(R/'experiments/tsl9-original-RF-bridge/evidence-v1.json');ao={o['addr']:o for f in ae['APP']['references']for o in f['operations']}
    need(ao[0x1763a]['opcode']=='lui a5, 0x2'and ao[0x1763c]['opcode']=='addi a5, a5, 1281'and ao[0x17640]['opcode']=='sh a5, 0(sp)','Original config bytes0/1 are01/25 after requested32-byte clear')
    config_exact={0x64bae:'lw a5, 16(a0)',0x64bb0:'beqz a5, 0x64ce8',0x64bc2:'andi a5, a5, 64',0x64bc6:'beqz a5, 0x64bce',0x64bce:'lui s2, 0x20003',0x64bd2:'li a2, 32',0x64bd6:'li a1, 0',0x64bd8:'addi a0, s2, 1344',0x64be4:'li a2, 32',0x64be8:'mv a1, s1',0x64bea:'addi a0, s2, 1344'}
    need(all(ops[p]['opcode']==v for p,v in config_exact.items()),'Actual config guard, clear and copy operands')
    need(1&64==0 and 0x20003000+1344+16==0x20003550,'Original mode bypasses alternate frequency guard and copied callback lands at3550')
    for pc,target in [(0x64bdc,0x2000039c),(0x64bee,0x20000332)]:
        hi=int.from_bytes(bytes.fromhex(ops[pc]['bytes']),'little');lo=int.from_bytes(bytes.fromhex(ops[pc+4]['bytes']),'little');imm=lo>>20;imm=imm-4096 if imm&2048 else imm
        need(hi&127==0x17 and lo&0x707f==0x67 and(hi>>7)&31==(lo>>15)&31==(lo>>7)&31==1 and(pc+(hi&0xfffff000)+imm)&0xfffffffe==target,'Actual normal clear/copy far-call target')
    common=['matching installed candidate ROM/ISA/RAM profile, not proved','valid disjoint config, global state, stack and original private ABI','original APP config reaches RF_Config with callback174EE and mode01','requested32-byte clear/copy completes normally under its memory contract','copied20003550 stays174EE until the particular pointer load','normal prior callees and no asynchronous or reentrant overwrite','actual initialization ordering and live binding not observed']
    rows=[dict(PC=p['PC'],function=p['function'],family='original-APP-RF-status',outcome='conditional-target',target_original_PC=0x174ee,pointer_slot=0x20003550,status_values=p['status_values'],all_reaching_pointer_loads=p['pointer_loads'],conditions=common+(['status2 with A1=0 requires at least4 readable A2 bytes; no local length/null guard']if 2 in p['status_values']else[]),live_binding_proved=False)for p in proof]
    old=read_json(R/'experiments/tsl9-resident-callback-slot-binding/ledger-v1.json');slot=read_json(R/'experiments/tsl9-resident-slot3-record-path/audit-result-v1.json')['contract']['conditional_route']
    slotrow=dict(PC=slot['consumer_call'],family='conditional-slot3',outcome='conditional-target',target_original_PC=slot['target'],pointer_slot=slot['slot_RAM'],conditions=slot['conditions'],live_binding_proved=False)
    new={r['PC']for r in rows+[slotrow]};need(len(old['rows'])==39 and len(new)==11 and new<={r['PC']for r in old['other_sites']},'Ten new RF sites plus the already proved slot3 site')
    ledger=dict(schema='TSL9-original-RF-status-cumulative-ledger-v1',passed=True,rows=sorted(old['rows']+[slotrow]+rows,key=lambda r:r['PC']),other_sites=[r for r in old['other_sites']if r['PC']not in new],counts=dict(actual_register_sites=51,conditionally_joined=50,conditional_target_or_target_set=40,conditional_skipped_or_caller_gated=10,not_joined_here=1),no_universal_or_live_binding_claim=True,missing_function_count_not_inferred=True)
    need(len(ledger['rows'])==50 and len({r['PC']for r in ledger['rows']})==50 and [r['PC']for r in ledger['other_sites']]==[0x432ea],'One remaining unjoined SDK register site')
    return dict(schema='TSL9-original-RF-status-binding-verification-v1',passed=True,checker_sha256=sha(__file__),evidence_sha256=sha(HERE/'evidence-v1.json'),whole_functions=functions,native_witness=witness,APP_bridge=bridge,consumer_proofs=proof,
        contract=dict(passed=True,new_conditional_sites=10,original_pointer_load_contexts=14,pointer_slot=0x20003550,target_original_PC=0x174ee,config_base=0x20003540,config_copy_bytes=32,original_mode_byte=1,original_channel_byte=37,all_reaching_pointer_definitions_accounted_for=True,copy_contract_and_stable_binding_required=True,status2_site=0x64658,status2_A1_zero_requires_readable_buffer_bytes=4,local_status2_pointer_or_length_guard=False,actual_live_or_all_callback_effects_proved=False),
        ledger=ledger,composition=prior['composition']['c'],APP_source_C_H_files_unchanged=159,APP_byte_coverage_unchanged=95.54,new_target_CODE_bytes=0,new_target_DATA_bytes=0,new_target_compilation=False,inherited_startup_source_gap_bytes=4,
        installed_ROM_identity_proved=False,physical_RAM_ISA_IRQ_or_Flash_compatibility_proved=False,actual_global_binding_before_any_dispatch_proved=False,linked_into_APP=False,runtime_closed=False,new_BIN=False,firmware_ready=False,goal_complete=False,target_executed=False,HOST_model_executed=False,ISA_emulated=False,hardware_accessed=False,network=False)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--tool-dir',type=Path,required=True);p.add_argument('--write-receipt',action='store_true');a=p.parse_args()
    try:
        v=verify(a.tool_dir.resolve())
        if a.write_receipt:
            for name,value in [('verification-v1.json',v),('ledger-v1.json',v['ledger'])]:
                dest=HERE/name;need(not dest.exists(),'Create-only proof receipt');dest.write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8')
        print(json.dumps(dict(passed=True,complete_SDK_functions=9,reference_SDK_bytes=2666,reference_SDK_instructions=940,new_conditional_sites=10,counts=v['ledger']['counts'],new_BIN=False)))
    except Exception as error:
        message=str(error)
        for path,token in [(R,'${PROJECT_ROOT}'),(Path.home(),'${USERPROFILE}')]:message=message.replace(str(path),token).replace(path.as_posix(),token)
        print(json.dumps(dict(passed=False,error_type=type(error).__name__,reason=message)));raise SystemExit(1)
