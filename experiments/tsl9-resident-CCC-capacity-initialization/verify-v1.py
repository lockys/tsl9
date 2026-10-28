"""Offline whole-body/native proof of the conditional CCC capacity initialization chain."""
import argparse,hashlib,json,re,runpy,subprocess,sys
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
R=HERE.parents[1]

def need(ok,label):
    if not ok:raise ValueError(label)

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def lib(p):return runpy.run_path(str(R/p),run_name='CCC_capacity_static_library')

def reaching(f,ops,g,reg):
    pure=set('beq beqz bgez blt bleu bltu bne bnez j jr ret'.split())
    stores={'sb','sh','sw','qk.c.sb','qk.c.sh'}
    results=set('add addi and andi auipc lb lbu lhu li lui lw mul mv or slli srai srli xor xori qk.c.lbu qk.c.lhu'.split())
    volatile=set('ra t0 t1 t2 t3 t4 t5 t6 a0 a1 a2 a3 a4 a5 a6 a7'.split())
    incoming={p:set()for p in g};incoming[f['start']].add(-1);todo=[f['start']]
    while todo:
        pc=todo.pop();o=ops[pc];mn=o['opcode'].split()[0]
        need(mn in pure|stores|results|{'jal','jalr'},'Every register-transfer opcode is modelled')
        call=o['type']in ['call','ucall']
        writes=(mn in results and o['opcode'].partition(' ')[2].split(',')[0]==reg)or(call and reg in volatile)
        out={pc}if writes else incoming[pc]
        for n in g[pc]:
            before=len(incoming[n]);incoming[n]|=out
            if len(incoming[n])!=before:todo.append(n)
    return incoming

def contract(K,parent):
    B=lib('experiments/tsl9-original-startup/build-v1.py')
    V=lib('experiments/tsl9-original-RF-tx-path/audit-v1.py')
    P=lib(K['parent_checker'])
    E=lib(K['reader'])['ELF'];diag=E(R/K['APP_ELF'])
    app=(R/K['APP']).read_bytes();carrier=(R/K['carrier']).read_bytes()
    refs=[];cfgs=[];proofs=[]
    def whole(f,frame,origin):
        at=f['start'];payload=b''
        for o in f['operations']:
            b=bytes.fromhex(o['bytes']);need(o['addr']==at and len(b)==o['size']==(4 if b[0]&3==3 else 2),'Contiguous original reference instructions')
            payload+=b;at+=len(b)
        need(at==f['end'],'Whole original function,without adjacent bytes')
        base=0x8000 if origin=='APP'else 0x40000
        raw=app if origin=='APP'else carrier
        need(payload==raw[f['start']-base:f['end']-base],'Every selected raw reference byte')
        if origin=='APP':need(payload==P['native_bytes'](diag,f['start'],f['end']),'Actual formal APP diagnostic equals whole original function')
        ext={d[1]for o in f['operations']if(d:=B['decode_control'](bytes.fromhex(o['bytes']),o['addr']))}
        ops,g,c=V['whole_cfg'](f,B,ext,frame)
        cfgs.append(c);refs.append(dict(start=f['start'],end=f['end'],bytes=len(payload),instructions=len(ops),source=origin))
        return ops,g,c
    def operands(ops,wanted):need(all(ops[p]['opcode']==t for p,t in wanted.items()),'Exact original capacity/configuration/call operands')
    def rd(f,ops,g,reg,pc,want):
        need(reaching(f,ops,g,reg)[pc]==set(want),'Whole-CFG unique reaching definitions')
        proofs.append(dict(register=reg,PC=pc,definitions=sorted(want)))
    def dominates(f,g,a,b):return b not in V['reachable'](g,f['start'],skip=a)
    main=next(f for f in read(R/K['main_evidence'])['selected_functions']if f['start']==0x8e88)
    mo,mg,mc=whole(main,32,'APP')
    need((main['end'],len(mo))==(0x9008,126),'Full384-byte APP main initializer')
    operands(mo,{0x8e8c:'lui s0, 0x40',0x8ea8:'jal ra, 0x199e2',0x8eb2:'lw a5, 416(s0)',0x8eb6:'jalr a5',0x8eb8:'lw a5, 428(s0)',0x8ebc:'jalr a5',0x8f5e:'lui s0, 0x40',0x8faa:'lw a5, 312(s0)',0x8fae:'lui a0, 0x10',0x8fb0:'addi a1, gp, 128',0x8fb4:'addi a0, a0, -1',0x8fb6:'jalr a5'})
    for reg,pc,w in [('s0',0x8eb2,[0x8e8c]),('a5',0x8eb6,[0x8eb2]),('s0',0x8eb8,[0x8e8c]),('a5',0x8ebc,[0x8eb8]),('s0',0x8faa,[0x8f5e]),('a5',0x8fb6,[0x8faa]),('a0',0x8fb6,[0x8fb4]),('a0',0x8fb4,[0x8fae]),('a1',0x8fb6,[0x8fb0])]:rd(main,mo,mg,reg,pc,w)
    need(dominates(main,mg,0x8ea8,0x8eb6)and dominates(main,mg,0x8eb6,0x8fb6)and dominates(main,mg,0x8ebc,0x8fb6),'APP configuration and role-init calls dominate later CCC initialization on normal CFG')
    conf=next(f for f in read(R/K['config_evidence'])['selected_functions']if f['start']==0x199e2)
    co,cg,cc=whole(conf,96,'APP')
    need((conf['end'],len(co))==(0x19b16,106),'Full308-byte APP configuration initializer')
    operands(co,{0x19a54:'lui a5, 0x1',0x19a66:'addi a5, a5, -449',0x19a70:'sh a5, 36(sp)',0x19ab4:'jal ra, 0x18f56',0x19ab8:'addi a4, sp, 16',0x19aba:'li a5, 0',0x19abc:'li a3, 6',0x19ac6:'addi a5, a5, 1',0x19ac8:'addi a4, a4, 1',0x19aca:'sb a2, 23(a4)',0x19ace:'bne a5, a3, 0x19abe',0x19ae2:'lui a5, 0x40',0x19ae6:'lw a5, 164(a5)',0x19aea:'addi a0, sp, 16',0x19aec:'jalr a5'})
    for reg,pc,w in [('a5',0x19a70,[0x19a66]),('a5',0x19a66,[0x19a54]),('a5',0x19aec,[0x19ae6]),('a5',0x19ae6,[0x19ae2]),('a0',0x19aec,[0x19aea])]:rd(conf,co,cg,reg,pc,w)
    need(dominates(conf,cg,0x19a70,0x19aec),'Original config halfword store dominates library-init call')
    direct_stores=[]
    for p,o in co.items():
        if not 0x19a70<p<0x19aec:continue
        m=re.fullmatch(r'(sb|sh|sw) \w+, (-?\d+)\(sp\)',o['opcode'])
        if m:
            width={'sb':1,'sh':2,'sw':4}[m[1]];off=int(m[2]);need(not off<=37<off+width,'No subsequent explicit SP-relative store overlaps ConnectNumber')
            direct_stores.append(dict(PC=p,offset=off,bytes=width))
    need(((0x1000-449)>>8)&255==14 and 16+21==37,'Halfword high byte is nominal ConnectNumber0E')
    need([16+i+23 for i in range(1,7)]==list(range(40,46)),'Six-byte copy loop has numeric offsets40..45,not configuration byte37;no content inspected')
    ble=next(f for f in read(R/K['BLE_evidence'])['selected_functions']if f['start']==0x43c7e)
    bo,bg,bc=whole(ble,16,'SDK')
    need((ble['end'],len(bo))==(0x43d62,92),'Whole228-byte BLE_LibInit candidate')
    operands(bo,{0x43c9a:'mv s1, a0',0x43cc4:'lui s0, 0x20003',0x43cc8:'li a2, 64',0x43ccc:'li a1, 0',0x43cce:'addi a0, s0, 492',0x43cda:'li a2, 64',0x43cde:'mv a1, s1',0x43ce0:'addi a0, s0, 492',0x43ce4:'auipc ra, 0x1ffbc',0x43ce8:'jalr 1614(ra)',0x43d38:'jalr a5'})
    need(dominates(ble,bg,0x43ce8,0x43d38),'Copied configuration precedes optional library callback')
    need((0x43ce4+0x1ffbc000+1614)&0xffffffff==0x20000332,'Actual64-byte copy provider target')
    need(0x20003000+492==0x200031ec and 0x200031ec+21==0x20003201,'Copied ConnectNumber address')
    owned=lib('experiments/tsl9-resident-root-chain-callees/verify-ownership-v3.py')['inspect'](R/K['SDK_parent']/'c/SDK.o')
    bm=owned['_byte_map'];roles={tuple([json.loads(x)[0][1],json.loads(x)[1],json.loads(x)[3][1]])for x in owned['_typed_relations']}
    for p,o in bo.items():
        raw=bytes.fromhex(o['bytes']);native=bytes(bm[p+i]for i in range(len(raw)));d=B['decode_control'](raw,p)
        rels=[v for v in roles if v[0]==p]
        if d:
            kind,target=d;need((p,kind,target)in roles,'Retained native direct control role')
            mask=B['MASKS'][kind][1];need(int.from_bytes(raw,'little')&mask==int.from_bytes(native,'little')&mask,'Native reference control opcode bits')
        elif rels:
            need(len(rels)==1 and rels[0][1]in [23,24],'Retained native far pair roles')
            kind=rels[0][1];mask=B['MASKS'][kind][1];need(int.from_bytes(raw,'little')&mask==int.from_bytes(native,'little')&mask,'Native reference PC-relative opcode bits')
            if p in [0x43cd2,0x43ce4]:need(rels[0][2]=={0x43cd2:0x2000039c,0x43ce4:0x20000332}[p],'Actual retained fill/copy CODE provider')
        else:need(raw==native,'Every native nonrelocated BLE reference byte')
    targets={p:int.from_bytes(carrier[p-0x40000:p-0x40000+4],'little')for p in [0x400a4,0x40138,0x401a0,0x401ac]}
    need(targets=={0x400a4:0x43c7e,0x40138:0x4cfd0,0x401a0:0x6dd16,0x401ac:0x6dd86},'Actual archived library/CCC/Peripheral/Central API table words')
    ev=read(HERE/'evidence-v1.json');roles_refs=ev['role_init_references'];need([(f['start'],f['end'])for f in roles_refs]==[(0x6dd16,0x6dd86),(0x6dd86,0x6de0c)],'Only the two whole role-init references')
    rf,cf=roles_refs;ro,rg,rc=whole(rf,16,'SDK');xo,xg,xc=whole(cf,16,'SDK')
    operands(ro,{0x6dd2a:'jal ra, 0x4da70',0x6dd80:'addi sp, sp, 16',0x6dd82:'j 0x6d572'})
    operands(xo,{0x6dd92:'lbu a5, 1525(a5)',0x6dd9a:'addi a5, a5, -1',0x6dd9c:'andi a5, a5, 255',0x6dda0:'bleu a5, a4, 0x6de04',0x6ddb0:'jal ra, 0x4da70',0x6de08:'j 0x6ae7c'})
    need(dominates(rf,rg,0x6dd2a,0x6dd82),'Peripheral normal tail requires common initializer call')
    need(not dominates(cf,xg,0x6ddb0,0x6de08),'Central conditional skip preserved;no universal initialization claim')
    by={};new_cfg=[]
    for f in ev['selected_functions']:
        ops,g,c=whole(f,f['own_frame_bytes'],'SDK');by.update(ops);new_cfg.append(c)
        if f['start']==0x4da70:need(dominates(f,g,0x4dace,0x4dbd8),'Capacity initializer call dominates common parent normal tail')
        if f['start']==0x4edd2:
            need(all(dominates(f,g,0x4edec,e['PC'])for e in c['typed_exits']),'Capacity assignment dominates every normal initializer exit')
            need(g[0x4ee0c]==[0x4ee10]and all(g[a]==[b]for a,b in [(0x4ee10,0x4ee12),(0x4ee12,0x4ee16),(0x4ee16,0x4ee18),(0x4ee18,0x4ee1c),(0x4ee1c,0x4ee20),(0x4ee20,0x4ee24)]),'No allocator-null guard before fill call')
    operands(by,{0x4dace:'jal ra, 0x4edd2',0x4dbce:'lui a0, 0x4e',0x4dbd2:'addi a0, a0, -1770',0x4dbd6:'addi sp, sp, 48',0x4dbd8:'j 0x4efe2',0x4edd2:'lui a5, 0x20003',0x4edd6:'lbu a0, 513(a5)',0x4ede2:'andi a5, a0, 3',0x4ede6:'addi s0, s0, 940',0x4edea:'srli a0, a0, 0x2',0x4edec:'qk.c.sb a5, 9(s0)',0x4edee:'add a5, a5, a0',0x4edf4:'qk.c.sb a5, 8(s0)',0x4edf6:'beqz a5, 0x4ee68',0x4edf8:'li a0, 60',0x4edfc:'mul a0, a5, a0',0x4ee10:'qk.c.lbu a2, 8(s0)',0x4ee1c:'sw a0, 852(s1)',0x4ee2c:'qk.c.lbu a3, 8(s0)',0x4ee42:'li a2, 48',0x4ee48:'addi a0, a0, 856',0x4ee4c:'addi sp, sp, 16',0x4ee56:'qk.c.sh a2, 0(a5)',0x4ee58:'sb zero, 2(a5)',0x4ee5c:'sw zero, 42(a5)',0x4ee62:'addi a5, a5, 60',0x4efd8:'lui a5, 0x20003',0x4efdc:'lbu a0, 948(a5)',0x4efea:'li a5, 0',0x4eff0:'li a2, 12',0x4eff2:'lw a1, 0(a3)',0x4eff4:'bnez a1, 0x4f000',0x4eff6:'slli a5, a5, 0x2',0x4effa:'sw a0, 0(a5)',0x4effc:'li a0, 0',0x4f004:'bne a5, a2, 0x4eff2',0x4f008:'li a0, 19'})
    need(0x20003000+513==0x20003201 and 0x20003000+940+9==0x200033b5 and 0x20003000+940+8==0x200033b4,'Capacity writer source/destination addresses')
    need(0x4e000-1770==0x4d916,'Unprovided literal callback address')
    c=parent['contract'];need(c['CCC_capacity_byte']==0x200033b5 and c['CCC_record_stride']==4 and c['CCC_initializer_APP_call']==0x8fb6,'Fresh parent CCC reader and APP table provenance')
    cap=14&3;total=(14&3)+(14>>2)
    need((cap,total,total*60,cap*4,0x20004080+cap*4)==(2,5,300,8,0x20004088),'Conditional nominal configuration footprint;no runtime model executed')
    return dict(passed=True,whole_references=refs,whole_CFGs=cfgs,unique_reaching_definitions=proofs,APP_main_bytes=384,APP_main_instructions=126,APP_configuration_bytes=308,APP_configuration_instructions=106,APP_config_halfword_store_PC=0x19a70,APP_config_store_width=2,APP_nominal_config_halfword=0xe3f,APP_ConnectNumber_offset=21,APP_config_stack_start=16,APP_ConnectNumber_stack_offset=37,APP_nominal_ConnectNumber=14,later_explicit_SP_stores=direct_stores,six_byte_copy_stack_offsets=[40,46],BLE_library_config_copy_bytes=64,BLE_library_config_base=0x200031ec,BLE_copied_ConnectNumber=0x20003201,APP_Peripheral_call=0x8eb6,APP_Central_call=0x8ebc,APP_CCC_initializer_call=0x8fb6,APP_Peripheral_call_dominates_CCC_normal_CFG=True,Peripheral_common_init_call=0x6dd2a,Peripheral_common_init_dominates_normal_tail=True,Central_common_init_call=0x6ddb0,Central_can_skip_common_init=True,role_references_new_native_CODE=False,capacity_parent=0x4da70,capacity_call=0x4dace,capacity_helper=0x4edd2,capacity_store_PC=0x4edec,CCC_capacity_address=0x200033b5,CCC_capacity_formula='c & 3',CCC_capacity_written_range=[0,3],total_connections_address=0x200033b4,total_connections_formula='(c & 3) + (c >> 2)',total_connections_written_range=[0,66],allocation_formula='60 * total',allocation_written_range_bytes=[0,3960],allocator_pointer_address=0x20003354,allocator_null_guard_present=False,capacity_assignment_dominates_normal_helper_exits=True,zero_total_skips_allocation_and_callback_table_clear=True,fresh_total_loads_after_calls_preserved=True,callback_table=[0x20003358,0x20003388],callback_slots=12,callback_full_status=19,unprovided_literal_callback=0x4d916,unprovided_callback_body_selected=False,nominal_ConnectNumber_case=dict(c=14,CCC_capacity=2,total_connections=5,allocation_bytes=300,CCC_table_start=0x20004080,CCC_table_bytes=8,CCC_table_end=0x20004088),local_normal_call_order_proved=True,global_assignment_order_or_exhaustive_writer_set_proved=False,live_config_or_capacity_value_proved=False,RAM_ownership_or_callback_lifetime_proved=False,conditions=['Actual installed ROM/Xwchc/header and saved-register/argument ABI match the archived candidate','Earlier normal calls return;configuration byte remains unchanged from APP store through copy and helper read','No aliased,IRQ,DMA,reentrant or callback overwrite of configuration,capacity,API slots,GP or tables','Allocation and all fresh memory accesses are valid;the helper has no allocator-null guard','The role wrappers are whole raw CFG references,not newly implemented providers;physical RAM/Flash/IRQ/OTA remain unproved'],inherited_startup_missing_source_bytes=4,router_body_selected=False,withheld_payload_or_individual_hash_output=False,target_executed=False,HOST_model_executed=False,ISA_emulated=False,hardware_accessed=False,network=False)

def run(llvm,trial=None):
    K=read(HERE/'inputs-v1.json')
    for p,h in K['pins'].items():need(sha(R/p)==h,'Frozen input '+p)
    for n,h in K['tools'].items():need(sha(llvm/n)==h,'Pinned LLVM tool '+n)
    need(sha(llvm.parent/'lib/clang/18/include/stdint.h')==K['stdint_sha256'],'Pinned compiler resource')
    P=lib(K['parent_checker']);parent=P['run'](llvm)
    need(parent==read(R/K['parent_receipt']),'Fresh full parent CCC proof')
    N=lib(K['builder']);N['pins'](llvm);saved=read(HERE/'build/native-v2/measurement.json')
    need(saved['inputs']==N['portable'](N['inputs'](llvm),llvm),'Every corrected native C/C++ input retained')
    native={}
    for mode in ['c','cpp']:
        folder=HERE/'build/native-v2'/mode
        need(N['inventory'](folder)==saved['modes'][mode]['artifacts'],'Retained complete native artifacts')
        need(N['portable'](N['dependencies'](folder,llvm),llvm)==saved['modes'][mode]['dependencies'],'Complete native include provenance')
        native[mode]=N['audit_object'](folder/'unit.o')
        need(native[mode]==saved['modes'][mode]['result']and N['audit_abi'](folder/'config_abi.o')==saved['modes'][mode]['ABI_result'],'Fresh native598-byte/ABI comparison')
    need(native['c']==native['cpp']and len(native['c']['UND'])==2 and native['c']['opaque_callbacks_not_provided']==1,'Identical native CODE with two real imports and one unprovided callback')
    c=contract(K,parent);out=HERE/'build'/(trial if trial else'composition-v1')
    if trial:need(Path(trial).name==trial and not out.exists(),'Create-only composition trial')
    else:need(out.exists(),'Retained composition required')
    sdk={};O=lib('experiments/tsl9-resident-root-chain-callees/verify-ownership-v3.py')
    for mode in ['c','cpp']:
        folder=out/mode;ins=[R/K['SDK_parent']/mode/'SDK.o',HERE/'build/native-v2'/mode/'unit.o'];obj=folder/'candidate.o'
        if trial:
            folder.mkdir(parents=True)
            p=subprocess.run([str(llvm/'ld.lld.exe'),'-m','elf32lriscv','-r','--no-relax',*[str(x)for x in ins],'-o',str(obj)],capture_output=True,timeout=60)
            (folder/'link.log').write_text(P['portable']((p.stdout+p.stderr).decode('utf-8','replace'),llvm),encoding='utf-8')
            need(p.returncode==0,'Actual SDK partial link')
        sdk[mode]=P['union'](obj,ins,K,(42282,412,2950,5,2353,0));owned=O['inspect'](obj)
        need(owned['CODE_bytes']==owned['distinct_original_CODE_bytes']==42282 and owned['duplicate_original_CODE_bytes']==0 and not owned['named_UND'],'Unique SDK CODE ownership and genuine import resolution')
        bm=owned['_byte_map'];pending=set(bm);count=0
        while pending:
            pc=min(pending)
            while pc in pending:
                width=4 if bm[pc]&3==3 else 2;need(all(pc+i in pending for i in range(width)),'Every whole native instruction owned once')
                pending.difference_update(range(pc,pc+width));pc+=width;count+=1
        need(count==14592,'Actual whole SDK instruction count')
        sdk[mode]['instructions']=count;sdk[mode]['ownership']={k:v for k,v in owned.items()if not k.startswith('_')}
    need(sdk['c']==sdk['cpp'],'Actual full SDK C/C++ composition identical')
    result=dict(schema='TSL9-CCC-capacity-initialization-verification-v1',passed=True,checker_sha256=sha(__file__),inputs_sha256=sha(HERE/'inputs-v1.json'),contract=c,native_CODE=native,native_ABI=saved['modes']['c']['ABI_result'],SDK_composition=sdk,new_SDK_CODE_bytes=598,new_SDK_instructions=198,new_SDK_DATA_bytes=0,new_normal_imports_resolved=2,unprovided_callbacks=1,new_APP_CODE_or_DATA_bytes=0,formal_APP_source_files_unchanged=162,formal_APP_original_coordinate_bytes_unchanged=73478,formal_APP_byte_coverage_unchanged=95.67,APP_compiler_UND_unchanged=6,source_curated=False,SDK_linked_into_APP=False,original_address_link_performed=False,physical_compatibility_proved=False,new_BIN=False,firmware_ready=False,goal_complete=False,target_executed=False,HOST_model_executed=False,ISA_emulated=False,hardware_accessed=False,network=False)
    result=json.loads(json.dumps(result))
    if trial:
        need(not(HERE/'verification-v1.json').exists(),'Create-only successful receipt')
        (HERE/'verification-v1.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    else:need(result==read(HERE/'verification-v1.json'),'Fresh full proof equals exact successful receipt')
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--tool-dir',type=Path,required=True);p.add_argument('--trial');a=p.parse_args()
    try:
        v=run(a.tool_dir.resolve(),a.trial)
        print(json.dumps({k:v[k]for k in ['passed','new_SDK_CODE_bytes','new_SDK_instructions','new_normal_imports_resolved','formal_APP_byte_coverage_unchanged','new_BIN']}))
    except Exception as e:
        message=str(e)
        for p,t in [(R,'${PROJECT_ROOT}'),(Path.home(),'${USERPROFILE}')]:message=message.replace(str(p),t).replace(p.as_posix(),t)
        print(json.dumps(dict(passed=False,error_type=type(e).__name__,reason=message)));raise SystemExit(1)
