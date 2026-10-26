#!/usr/bin/env python3
"""Audit complete actual dispatch handlers and providers without target execution."""
import argparse,hashlib,json,re,runpy,subprocess,sys
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
PRIOR=ROOT/'experiments/tsl9-resident-callback-registration'
CODE_PRIOR=PRIOR
def need(ok,label):
    if not ok:raise ValueError(label)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def lib(p):return runpy.run_path(str(p),run_name='idle_static_library')
def canonical(v):return json.loads(json.dumps(v))
def native(llvm):
    N=lib(HERE/'build-v1.py');N['pins'](llvm);saved=json.loads((HERE/'build/native-v2/measurement.json').read_bytes())
    need(saved['inputs']==N['portable'](N['inputs'](llvm),llvm)and saved['candidate_contract']==N['candidate_contract'](),'All actual native inputs unchanged');result={}
    for mode in ['c','cpp']:
        f=HERE/'build/native-v2'/mode;v=saved['modes'][mode]
        need(v['artifacts']==N['inventory'](f)and v['dependencies']==N['portable'](N['dependencies'](f,llvm),llvm),'Complete actual object/include inventories')
        result[mode]=dict(CODE=N['audit_object'](f/'unit.o'),ABI=N['audit_abi'](f/'config_abi.o'))
        need(result[mode]['CODE']==v['result']and result[mode]['ABI']==v['ABI_result'],'Fresh native readers match compile receipt')
    need(result['c']==result['cpp'],'Actual C11/C++17 objects identical');return N,result
def reachable(graph,start,skip_node=None,skip_edge=None):
    seen=set();pending=[start]
    while pending:
        pc=pending.pop()
        if pc==skip_node or pc in seen:continue
        seen.add(pc);pending.extend(v for v in graph[pc]if(pc,v)!=skip_edge)
    return seen
def cfg(ops,B,external):
    graph={p:[]for p in ops};exits=[];calls=[]
    for pc,o in ops.items():
        following=pc+o['size'];d=B['decode_control'](bytes.fromhex(o['bytes']),pc)
        if o['type']in ['ret','rjmp']:exits.append(pc);continue
        if d:
            kind,target=d
            if o['type']=='call':need(target in external and following in ops,'Real named callee and continuation');calls.append(dict(PC=pc,target=target));graph[pc].append(following)
            elif target in ops:
                graph[pc].append(target)
                if o['type']=='cjmp':need(following in ops,'Whole conditional fallthrough');graph[pc].append(following)
            else:need(target in external and o['type']=='jmp','Actual direct external tail');exits.append(pc)
        else:
            need(following in ops,'No fallthrough into adjacent body');graph[pc].append(following)
            if o['type']=='ucall':calls.append(dict(PC=pc,target=None))
    return graph,exits,calls

def own_frame(f,B,external,frame):
    ops={o['addr']:o for o in f['operations']};g,exits,calls=cfg(ops,B,external);need(reachable(g,f['start'])==set(ops)and exits,'Every instruction belongs to this complete entry CFG')
    changes={p:int(o['opcode'].rsplit(', ',1)[1],0)for p,o in ops.items()if o['opcode'].startswith('addi sp, sp, ')};need(sorted(changes.values())==([-frame,frame]if frame else []),'Exact actual allocation/cleanup')
    pending=[(f['start'],0)];depths={}
    while pending:
        pc,before=pending.pop()
        if pc in depths:need(depths[pc]==before,'Consistent own SP at branch join');continue
        depths[pc]=before;after=before+changes.get(pc,0);need(after in [-frame,0],'Only original own-frame states')
        if not g[pc]:need(pc in exits and after==0,'Own frame balanced at each normal return or tail')
        pending.extend((v,after)for v in g[pc])
    return ops,g,exits,calls

def APP_bridge(N):
    E,B=N['EV'],N['B'];A=E['APP'];app=(ROOT/A['APP_firmware']).read_bytes();need(sha(ROOT/A['APP_firmware'])==A['APP_sha256']and sha(ROOT/'src/source-manifest.json')==A['source_manifest_sha256'],'Actual original APP and current curated inventory')
    for p,h in A['curated_source_hashes'].items():need(sha(ROOT/p)==h,'Every actual APP bridge source unchanged')
    path=ROOT/A['diagnostic_ELF'];need(sha(path)==A['diagnostic_ELF_sha256'],'Existing nonloadable original-address diagnostic identity');elf=lib(ROOT/N['S']['reader'])['ELF'](path);need(elf.header[0]==2 and elf.header[1]==243,'Actual RV32 diagnostic ET_EXEC')
    graphs={};allops={};witnesses=[]
    for ref,frame in zip(A['references'],[32,48,0]):
        raw=app[ref['start']-0x8000:ref['end']-0x8000];need(len(raw)==ref['bytes']and hashlib.sha256(raw).hexdigest()==ref['original_sha256']and b''.join(bytes.fromhex(o['bytes'])for o in ref['operations'])==raw,'Actual contiguous original APP reference bytes')
        at=ref['start']
        for o in ref['operations']:need(o['addr']==at,'Actual original APP instruction addresses');at+=o['size']
        need(at==ref['end'],'Full APP function interval')
        original=bytearray();owners=set()
        for pc in range(ref['start'],ref['end']):
            sections=[s for s in elf.sections if s['flags']&6==6 and s['address']<=pc<s['address']+s['size']];need(len(sections)==1,'One actual executable owner for each selected APP byte');sec=sections[0];original.append(elf.data(sec)[pc-sec['address']]);owners.add(sec['name'])
        need(bytes(original)==raw,'Existing compiled original-address diagnostic matches all selected APP bytes')
        external={d[1]for o in ref['operations']if(d:=B['decode_control'](bytes.fromhex(o['bytes']),o['addr']))and d[1]not in {v['addr']for v in ref['operations']}};ops,g,exits,calls=own_frame(ref,B,external,frame);graphs[ref['start']]=g;allops.update(ops);witnesses.append(dict(start=ref['start'],end=ref['end'],bytes=ref['bytes'],native_CODE_sections=sorted(owners),original_and_diagnostic_bytes_equal=True,own_frame_bytes=frame,own_frame_balanced=True))
    need(sum(v['bytes']for v in witnesses)==586,'586 reference bytes,no new APP CODE');ops=allops
    expected={0x8e8c:'lui s0, 0x40',0x8ebe:'lw a5, 448(s0)',0x8ec2:'jalr a5',0x8fdc:'jal ra, 0x175e8',0x175e8:'addi sp, sp, -48',0x175ec:'lui s0, 0x40',0x1761a:'lw a5, 72(s0)',0x1761c:'mv a0, sp',0x1761e:'li a2, 32',0x17622:'li a1, 0',0x17624:'jalr a5',0x17644:'auipc a5, 0x0',0x17648:'addi a5, a5, -342',0x1764c:'sw a5, 16(sp)',0x17650:'sb a5, 25(sp)',0x17654:'lw a5, 452(s0)',0x17658:'mv a0, sp',0x1765a:'jalr a5',0x174ee:'li a5, 2',0x174f0:'beq a0, a5, 0x17508',0x174f4:'bltu a0, a5, 0x17538',0x174f8:'addi a0, a0, -17',0x174fa:'andi a0, a0, 255',0x17500:'bltu a5, a0, 0x17538',0x17504:'j 0x17442',0x17508:'bnez a1, 0x17504',0x1750a:'lbu a5, 1(a2)',0x1750e:'bne a5, a0, 0x17504',0x17512:'lbu a4, 2(a2)',0x17522:'lbu a4, 3(a2)',0x17532:'li a0, 0',0x17534:'j 0x173ee',0x17538:'ret'}
    need(all(ops[p]['opcode']==v for p,v in expected.items()),'Actual ROM slots,constructor callback,stack stores and status callback dispatch')
    def w(p):return int.from_bytes(bytes.fromhex(ops[p]['bytes']),'little')
    def sx(v,b):return v-(1<<b)if v&(1<<(b-1))else v
    def up(p,rd,opcode):
        a=w(p);need(ops[p]['size']==4 and a&127==opcode and(a>>7)&31==rd,'Original U-type fields');return sx(a&0xfffff000,32)
    def imm(p,rd,rs):
        a=w(p);need(ops[p]['size']==4 and a&0x707f==0x13 and(a>>7)&31==rd and(a>>15)&31==rs,'Original ADDI fields');return sx(a>>20,12)
    def load(p,off):
        a=w(p);need(a&0x707f==0x2003 and(a>>7)&31==15 and(a>>15)&31==8 and sx(a>>20,12)==off,'Original LW slot fields')
    need(up(0x8e8c,8,0x37)==up(0x175ec,8,0x37)==0x40000,'Actual S0 ROM base operands');load(0x8ebe,448);load(0x17654,452)
    for p in [0x8ec2,0x1765a]:need(w(p)&0xf07f==0x9002 and(w(p)>>7)&31==15,'Actual C.JALR throughA5')
    callback=(0x17644+up(0x17644,15,0x17)+imm(0x17648,15,15))&0xffffffff;need(callback==0x174ee,'Actual PC-relative APP callback literal')
    a=w(0x1764c);need(ops[0x1764c]['size']==2 and a&0xe003==0xc002 and(a>>2)&31==15 and(((a>>9)&15)*4+((a>>7)&3)*64)==16,'Actual C.SWSP caller callback slot16')
    main=graphs[0x8e88];ctor=graphs[0x175e8];need(0x8fdc not in reachable(main,0x8e88,skip_node=0x8ec2),'RF slot99 call dominates constructor call in full normal-return APP CFG');need(0x1765a not in reachable(ctor,0x175e8,skip_node=0x1764c)and 0x1765a not in reachable(ctor,0x175e8,skip_node=0x17624),'Constructor callback store andzero32 call dominate RF slot100 call')
    slots=[(int(m[1]),o['addr'])for o in A['references'][1]['operations']if(m:=re.fullmatch(r'sw (?:ra|s0|s1), (\d+)\(sp\)',o['opcode']))];need(sorted(off for off,p in slots)==[36,40,44]and 16+4<=32<=36 and 44+4==48,'Actual32-byte configuration is within48-byte own frame and disjoint saved registers')
    task=(0x1760c+up(0x1760c,10,0x17)+imm(0x17610,10,10))&0xffffffff;need(task==0x17476,'Actual APP process-event callback literal')
    context=(0x175f4+up(0x175f4,9,0x17)+imm(0x175f8,9,9))&0xffffffff;need(context==0x2000c7a0,'Actual APP RF context literal')
    def byte_source(pc,reg,base_reg):
        a=w(pc);need(a&0x707f==0x4003 and(a>>7)&31==reg and(a>>15)&31==base_reg,'Actual LBU field');return sx(a>>20,12)
    cmp1=(0x17516+up(0x17516,15,0x17)+byte_source(0x1751a,15,15))&0xffffffff;cmp2=(0x17526+up(0x17526,15,0x17)+byte_source(0x1752a,15,15))&0xffffffff;need((cmp1,cmp2)==(0x2000c7aa,0x2000c7ab),'Actual two APP comparison-byte storage addresses')
    return dict(passed=True,static_only=True,reference_bytes=586,new_APP_CODE_bytes=0,diagnostic_ELF_sha256=sha(path),native_original_address_byte_witnesses=witnesses,main_entry=0x8e88,RoleInit_table_word=0x401c0,RoleInit_call_PC=0x8ec2,constructor_call_PC=0x8fdc,RoleInit_call_dominates_constructor_on_normal_CFG=True,constructor_frame_bytes=48,configuration_bytes=32,saved_register_offsets=[36,40,44],configuration_disjoint_own_saved_registers=True,configuration_callback_literal=callback,configuration_callback_store_PC=0x1764c,configuration_slot_word=0x401c4,configuration_call_PC=0x1765a,APP_task_callback_literal=task,APP_context=context,APP_context_bytes=268,status_callback=dict(entry=0x174ee,own_frame_bytes=0,status2_requires_A1_zero_and_buffer_checks=True,buffer_byte_offsets_read=[1,2,3],minimum_readable_buffer_bytes_on_that_path=4,comparison_storage=[cmp1,cmp2],other_status_test='A0>=2 and low8(A0-17)<=1 after excludingA0==2',failure_or_17_18_tail=0x17442,matching_packet_tail=0x173ee,matching_packet_tail_A0=0,pointer_or_length_guard=False,byte_meaning_or_full_protocol_proved=False),conditional_global_RF_callback_storage=0x20003550,conditional_global_RF_callback_value=callback,requires_installed_candidate_ROM_valid_disjoint_memory_normal_returns_and_register_preservation=True,actual_runtime_or_physical_callback_value_observed=False,physical_installed_ROM_identity_proved=False)

def callback_contract(N,previous):
    E,B=N['EV'],N['B'];external={f['start']for f in E['selected_functions']}|{int(k)for k in E['target_names']};pairs={p['PC']+4:p for p in N['S']['PC_relative_pairs']};frames={0x66056:16,0x641b0:32,0x64298:16,0x65920:16};functions=[];ops={}
    for f in E['selected_functions']:
        oo,g,exits,calls=own_frame(f,B,external,frames[f['start']]);ops.update(oo)
        for call in calls:
            if call['PC']in pairs:call['target']=pairs[call['PC']]['target_PC']
        need(all(v['target']is not None for v in calls),'No new opaque SDK calls;all actual references named honestly')
        functions.append(dict(entry=f['start'],end=f['end'],bytes=f['end']-f['start'],instructions=len(oo),own_frame_bytes=frames[f['start']],own_frame_balanced_at_typed_exits=True,scope_exits=[dict(PC=p,type=oo[p]['type'],instruction=oo[p]['opcode'])for p in exits],calls=calls,direct_edges=[[p,v]for p in g for v in g[p]]))
    expected={0x6605c:'jal ra, 0x64298',0x66060:'lui s0, 0x20003',0x66064:'addi a0, s0, 1376',0x66068:'li a2, 36',0x6606c:'li a1, 0',0x66076:'lui a0, 0x66',0x6607c:'addi a0, a0, -1760',0x66084:'jal ra, 0x43c4e',0x6608c:'qk.c.sb a0, 16(s0)',0x66092:'li a0, 0',0x642a4:'sw zero, 1292(a5)',0x642ac:'addi a3, a5, 768',0x642b4:'sw a3, 1284(a4)',0x642b8:'addi a3, a5, 512',0x642c0:'sw a3, 1340(a4)',0x642c4:'lui a3, 0x40025',0x642cc:'sw a3, 1424(a4)',0x642d0:'addi a5, a5, 256',0x642da:'sw a5, 1288(a4)',0x64308:'addi sp, sp, 16',0x6430a:'j 0x641b0'};need(all(ops[p]['opcode']==v for p,v in expected.items()),'Actual initializer,task literal,MMIO pointer stores and frame-released reset tail')
    need((0x66000-1760)==0x65920 and 0x65920 in frames and 0x20003000+1376+16==0x20003570,'Registered RF task has actual selected body and ID byte storage')
    need([(p['PC'],p['target_PC'])for p in N['S']['PC_relative_pairs']]==[(0x6606e,0x2000039c)],'Actual real memset call pair')
    h=(ROOT/E['header']).read_text(encoding='gb18030');carrier=(ROOT/E['firmware']).read_bytes();need(all(v in h for v in E['primary_RF_macros'].values())and int.from_bytes(carrier[0x1c0:0x1c4],'little')==0x66056 and int.from_bytes(carrier[0x1c4:0x1c8],'little')==0x64bae,'Pinned primary RF indices and actual candidate table words')
    app=APP_bridge(N);vectors=(ROOT/E['official_vectors']['path']).read_text();actual=[dict(word=int(hi+lo,16),instruction=text)for text,lo,hi in re.findall(r'# CHECK-ASM-AND-OBJ: (qk\.c\.[^\n]+)\n# CHECK-ASM: encoding: \[0x([0-9a-f]{2}),0x([0-9a-f]{2})\]',vectors)];need(actual==E['official_vectors']['checked']and len(actual)==52,'All52 primary instruction vectors retained')
    return dict(passed=True,static_only=True,functions=functions,APP_bridge=app,primary_Xwchc=dict(official_vectors=52,families=8,actual_ports=12,physical_profile_proved=False),public_RF_RoleInit_entry=0x66056,RF_task_callback=0x65920,RF_task_body_provided=True,RF_task_ID_storage=0x20003570,RF_context=0x20003560,RF_context_zero_bytes=36,MMIO_pointer_stores=E['initialized_pointer_stores'],MMIO_pointer_values_after_unknown_callees_or_async_effects_proved=False,reset_direct_tail=[0x6430a,0x641b0],other_internal_callback_initialization_order_proved=False,raw_dependencies=E['raw_dependencies'],raw_dependency_list_is_not_exhaustive=True,opaque_transfers=[],genuine_new_provider_entries=E['genuine_new_provider_entries'],actual_APP_slot_calls_and_callback_literal_proved=True,physical_ROM_API_identity_proved=False,actual_RF_callback_value_observed=False,callees_preserving_SP_and_registers_and_normal_returns_assumed=True,valid_memory_bounds_nonalias_and_global_stack_assumed=True,installed_ROM_identity_proved=False,physical_trap_route_proved=False,runtime_closed=False,hardware_accessed=False)

def composition(path,inputs,N):
    ELF=lib(ROOT/N['S']['reader'])['ELF']
    def facts(p):
        e=ELF(p);need(e.header[0]==1 and e.header[1]==243 and not e.program_headers,'Actual nonloadable RV32 ET_REL')
        a={s['name']:(s['flags'],e.data(s))for s in e.sections if s['flags']&2 and s['size']};d={s['name']:(s['info'],s['other'],e.sections[s['section']]['name'],s['value'],s['size'])for s in e.symbols if s['info']>>4 and s['section']};u={s['name']for s in e.symbols if s['info']>>4 and not s['section']};rel=sorted((e.sections[v['section']]['name'],v['offset'],v['type'],v['addend'],e.symbols[v['symbol']]['name'])for v in e.relocations);return a,d,u,rel
    a={};d={};u=set();rel=[]
    for p in inputs:
        aa,dd,uu,rr=facts(p);need(not set(a).intersection(aa)and not set(d).intersection(dd),'Unique real input owners');a.update(aa);d.update(dd);u.update(uu);rel+=rr
    remaining=u-set(d);need(remaining==set(N['EV']['prior_named_UND'])|{N['EV']['target_names'][str(p)]for p in N['EV']['genuine_new_provider_entries']}and len(u)==25 and facts(path)==(a,d,remaining,sorted(rel)),'Every byte,symbol and relocation retained;real callback providers and existing event/state8/setter definitions retain every cross-input reference')
    code=sum(len(v[1])for v in a.values()if v[0]&4);data=sum(len(v[1])for v in a.values()if not v[0]&4);funcs=sum(v[0]==18 and v[4]>0 for v in d.values());objects=sum(v[0]==17 for v in d.values())
    need((code,data,funcs,objects,len(rel))==(12936,256,1053,1,790),'Exact12936-CODE/256-DATA composition')
    independent=lib(ROOT/'experiments/tsl9-remaining-record-dispatch/compare-readers-v1.py')['audit'](path);need(independent['passed'],'Independent complete ELF readers agree')
    return dict(passed=True,object_sha256=sha(path),CODE_bytes=12936,DATA_bytes=256,allocated_bytes=13192,instructions=4507,positive_FUNC_regions=1053,positive_OBJECT_regions=1,relocations=790,named_UND=sorted(remaining),every_input_byte_symbol_relocation_retained=True,independent_readers=independent,callback_and_existing_cross_imports_have_real_bodies=True,all_four_new_real_bodies_retained=True,previous_numeric_callbacks_have_real_bodies=True,registered_RF_task_callback_body_provided=True,prior_readonly_table_retained=True,zero_named_UND_is_not_runtime_closure=True,raw_RAM_and_callback_dependencies_provided=False,actual_original_address_link_performed=False,linked_into_APP=False,runtime_closed=False,new_BIN=False,firmware_ready=False)
def audit(llvm,refs,trial=None):
    N,result=native(llvm);previous=lib(PRIOR/'audit-v2.py')['audit'](llvm,refs);need(canonical(previous)==json.loads((PRIOR/'audit-result-v2.json').read_bytes()),'Fresh prior state8,scheduler-state,idle,arithmetic,clock,timer and earlier proofs retained')
    contract=callback_contract(N,previous);out=HERE/'build'/('composition-v1'if trial is None else trial)
    if trial:need(Path(trial).name==trial and not out.exists(),'Fresh create-only partial composition')
    composed={};hashes={}
    for mode in ['c','cpp']:
        inputs=[CODE_PRIOR/'build/composition-v2'/mode/'candidate.o',HERE/'build/native-v2'/mode/'unit.o'];hashes[mode]={p.relative_to(ROOT).as_posix():sha(p)for p in inputs};f=out/mode
        if trial:
            f.mkdir(parents=True);argv=[str(llvm/'ld.lld.exe'),'-r','--no-relax',*[str(p)for p in inputs],'-o',str(f/'candidate.o')];p=subprocess.run(argv,capture_output=True,timeout=120);(f/'link.log').write_text(N['portable']((p.stdout+p.stderr).decode('utf-8','replace'),llvm),encoding='utf-8');need(p.returncode==0,'Actual partial link failed;retain trial')
        composed[mode]=composition(f/'candidate.o',inputs,N)
    need(composed['c']==composed['cpp'],'Actual whole C/C++ compositions identical')
    return dict(schema='TSL9-original-APP-candidate-RF-init-bridge-audit-v1',passed=True,checker_sha256=sha(__file__),SDK_candidate_only=True,native_results=result,callback_contract=contract,prior_state8_audit_sha256=sha(PRIOR/'audit-result-v2.json'),prior_SDK_composition_CODE_bytes=12272,prior_SDK_composition_DATA_bytes=256,prior_state8_scheduler_idle_arithmetic_clock_timer_binding_layout_and_Flash_contracts_retained=True,composition=composed,composition_input_hashes=hashes,APP_source_C_H_files_unchanged=159,APP_byte_coverage_unchanged=95.54,installed_ROM_identity_proved=False,physical_Xwchc_profile_proved=False,physical_RAM_capacity_proved=False,physical_atomicity_proved=False,Flash_callback_effects_closed=False,global_IRQ_alias_or_stack_bound_proved=False,runtime_closed=False,linked_into_APP=False,new_BIN=False,firmware_ready=False,goal_complete=False,target_executed=False,HOST_model_executed=False,ISA_emulated=False,hardware_accessed=False,network=False)
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--tool-dir',type=Path,required=True);p.add_argument('--reference-root',type=Path,required=True);p.add_argument('--link-trial');p.add_argument('--output',type=Path);a=p.parse_args()
    try:
        result=audit(a.tool_dir.resolve(),a.reference_root.resolve(),a.link_trial)
        if a.output:
            dest=HERE/a.output;need(dest.parent==HERE and not dest.exists(),'Create-only audit receipt');dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
        c=result['composition']['c'];print(json.dumps(dict(passed=True,CODE_bytes=664,instructions=216,composition={k:c[k]for k in ['object_sha256','CODE_bytes','DATA_bytes','instructions','positive_FUNC_regions','positive_OBJECT_regions','relocations','named_UND']},APP_byte_coverage=95.54,new_BIN=False)))
    except Exception as error:
        message=str(error)
        for path,token in [(ROOT,'${PROJECT_ROOT}'),(Path.home(),'${USERPROFILE}')]:message=message.replace(str(path),token).replace(path.as_posix(),token)
        print(json.dumps(dict(passed=False,error_type=type(error).__name__,reason=message)));raise SystemExit(1)
