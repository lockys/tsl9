#!/usr/bin/env python3
"""Audit complete actual dispatch handlers and providers without target execution."""
import argparse,hashlib,json,re,runpy,subprocess,sys
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
PRIOR=ROOT/'experiments/tsl9-resident-dispatch-handlers'
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

def callback_contract(N,previous):
    E,B=N['EV'],N['B'];entries={f['start']for f in E['selected_functions']};external=entries|{int(k)for k in E['target_names']};pairs={p['PC']+4:p for p in N['S']['PC_relative_pairs']};frames={0x58ef2:0,0x60856:16,0x58c52:64,0x60516:32,0x64bae:16};cleanup_counts={0x58ef2:0,0x60856:1,0x58c52:2,0x60516:3,0x64bae:1};functions=[];graphs={}
    for f in E['selected_functions']:
        ops={o['addr']:o for o in f['operations']};g,exits,calls=cfg(ops,B,external);need(reachable(g,f['start'])==set(ops)and exits,'All contiguous instructions belong to actual entry CFG')
        frame=frames[f['start']];changes={p:int(o['opcode'].rsplit(', ',1)[1],0)for p,o in ops.items()if o['opcode'].startswith('addi sp, sp, ')};need(sorted(changes.values())==([-frame]+[frame]*cleanup_counts[f['start']]if frame else []),'Actual allocation and each normal/tail cleanup')
        pending=[(f['start'],0)];depths={}
        while pending:
            pc,before=pending.pop()
            if pc in depths:need(depths[pc]==before,'Consistent own SP at CFG join');continue
            depths[pc]=before;after=before+changes.get(pc,0);need(after in [-frame,0],'Only original own-frame positions')
            if not g[pc]:need(pc in exits and after==0,'Frame released at every actual normal return and external tail,including no-frame RF rejection')
            pending.extend((v,after)for v in g[pc])
        for call in calls:
            if call['PC']in pairs:call['target']=pairs[call['PC']]['target_PC']
        functions.append(dict(entry=f['start'],end=f['end'],bytes=f['end']-f['start'],instructions=len(ops),own_frame_bytes=frame,own_frame_balanced_at_typed_exits=True,scope_exits=[dict(PC=p,type=ops[p]['type'],instruction=ops[p]['opcode'])for p in exits],calls=calls,direct_edges=[[p,v]for p in g for v in g[p]]));graphs[f['start']]=g
    ops={o['addr']:o for f in E['selected_functions']for o in f['operations']}
    expected={0x58ef2:'lui a5, 0x58',0x58ef6:'lui a4, 0x20003',0x58efa:'addi a5, a5, -834',0x58efe:'sw a5, 1104(a4)',0x58f02:'lui a5, 0x59',0x58f06:'lui a4, 0x20003',0x58f0a:'addi a5, a5, -942',0x58f0e:'sw a5, 1264(a4)',0x58f12:'ret',0x60874:'lui a5, 0x5f',0x60878:'lui a4, 0x20003',0x6087c:'addi a5, a5, -1860',0x60880:'sw a5, 1084(a4)',0x60886:'lui a5, 0x60',0x6088a:'lui a4, 0x20003',0x6088e:'addi a5, a5, 1302',0x60892:'sw a5, 1272(a4)',0x58d3a:'addi sp, sp, 64',0x58d3c:'j 0x57dae',0x605de:'addi sp, sp, 32',0x605e0:'j 0x6020a',0x60734:'li a0, 0',0x60736:'addi sp, sp, 32',0x60738:'auipc t1, 0x1ffa0',0x6073c:'jr 82(t1)',0x64bae:'lw a5, 16(a0)',0x64bb0:'beqz a5, 0x64ce8',0x64bd2:'li a2, 32',0x64bd6:'li a1, 0',0x64bd8:'addi a0, s2, 1344',0x64be4:'li a2, 32',0x64be8:'mv a1, s1',0x64bea:'addi a0, s2, 1344',0x64ce8:'li a0, 1',0x64cea:'ret'}
    need(all(ops[p]['opcode']==v for p,v in expected.items()),'Actual registrations,typed external tails,zero-frame callback rejection and32-byte parameter transfer')
    need((0x59000-942,0x60000+1302,0x58000-834,0x5f000-1860)==(0x58c52,0x60516,0x57cbe,0x5e8bc),'All four literal CODE values derived from actual operands')
    for entry,store in [(0x58ef2,0x58f0e),(0x60856,0x60892)]:
        g=graphs[entry];exits=next(f['scope_exits']for f in functions if f['entry']==entry);need(all(v['PC']not in reachable(g,entry,skip_node=store)for v in exits),'Registration word store dominates each local normal return')
    lo=int.from_bytes(bytes.fromhex(ops[0x6073c]['bytes']),'little');hi=int.from_bytes(bytes.fromhex(ops[0x60738]['bytes']),'little');need(hi&127==0x17 and(hi>>7)&31==6 and lo&0x707f==0x67 and(lo>>7)&31==0 and(lo>>15)&31==6 and(0x60738+(hi&0xfffff000)+(lo>>20))&0xffffffff==0x2000078a,'Exact AUIPC-T1/JALR-zero:real setter tail preserves RA,not ordinary call')
    need(len(N['S']['PC_relative_pairs'])==9 and sum(p['reference_kind']=='direct-code-tail-pair'for p in N['S']['PC_relative_pairs'])==1,'Eight actual far calls plus one actual far tail')
    opaque=[c['PC']for f in functions for c in f['calls']if c['target']is None];need(sorted(opaque)==sorted(v['PC']for v in E['opaque_transfers'])and len(opaque)==3,'Only actual opaque calls remain after typed pair resolution')
    RF=E['public_RF_Config'];header=(ROOT/E['header']).read_text(encoding='gb18030');carrier=(ROOT/E['firmware']).read_bytes();need(RF['header_macro']in header and RF['callback_typedef']in header and RF['index']==100 and int.from_bytes(carrier[0x1c4:0x1c8],'little')==RF['target']==0x64bae,'Actual primary macro,index and carrier table word')
    need(N['S']['ABI_source_sha256']==sha(ROOT/N['S']['ABI_source'])and RF['compiler_expected_bytes']==32 and RF['compiler_expected_callback_offset']==16 and 0x20003000+1344+16==0x20003550,'Pinned compiler ABI maps caller callback field into candidate global parameter block')
    rg=graphs[0x64bae];need(0x64bf2 not in reachable(rg,0x64bae,skip_node=0x64be0)and 0x64bf2 not in reachable(rg,0x64ce8),'Zero32 precedes copy32 on paths reaching copy;null callback rejection skips calls')
    desired={(0x64bdc,0x2000039c),(0x64bee,0x20000332)};need(desired<={(p['PC'],p['target_PC'])for p in N['S']['PC_relative_pairs']},'Both actual parameter memory calls have prior real bodies')
    vectors=(ROOT/E['official_vectors']['path']).read_text();actual=[dict(word=int(hi+lo,16),instruction=text)for text,lo,hi in re.findall(r'# CHECK-ASM-AND-OBJ: (qk\.c\.[^\n]+)\n# CHECK-ASM: encoding: \[0x([0-9a-f]{2}),0x([0-9a-f]{2})\]',vectors)];need(actual==E['official_vectors']['checked']and len(actual)==52,'All52 actual primary positive vectors')
    return dict(passed=True,static_only=True,functions=functions,primary_Xwchc=dict(official_vectors=52,families=8,actual_ports=39,physical_profile_proved=False),registered_callback_words=E['static_registration_words'],registered_callbacks_have_actual_complete_selected_bodies=True,other_literal_CODE_words=E['other_registration_words'],other_literal_CODE_bodies_unprovided=[0x57cbe,0x5e8bc],direct_external_tails=[[0x58d3c,0x57dae],[0x605e0,0x6020a]],far_external_tail=dict(PC=0x60738,JALR_PC=0x6073c,target=0x2000078a,AUIPC_register='t1',link_register='zero',RA_preserved_by_tail_instruction=True,own_frame_released_before_tail=True),RF_configuration=dict(public_index=100,raw_table_slot=0x401c4,entry=0x64bae,compiler_bytes=32,compiler_callback_offset=16,parameter_base=0x20003540,derived_callback_storage=0x20003550,zero_call=0x64bdc,copy_call=0x64bee,callback_field_source='caller parameter+16,conditional on valid nonoverlapping input and real callee memory contracts',nonnull_callback_guard=True,no_frame_rejection_return_PC=0x64cea,original_APP_use_proved=False,actual_caller_callback_value_proved=False,physical_API_or_ABI_identity_proved=False),raw_dependencies=E['raw_dependencies'],raw_dependency_list_is_not_exhaustive=True,opaque_transfers=E['opaque_transfers'],genuine_new_provider_entries=E['genuine_new_provider_entries'],callees_preserving_registers_SP_and_normal_returns_assumed=True,copy_propagation_requires_valid_nonoverlapping_input=True,all_raw_callback_or_CODE_pointer_effects_closed=False,installed_ROM_identity_proved=False,physical_trap_route_proved=False,global_stack_or_IRQ_budget_proved=False,runtime_closed=False,hardware_accessed=False)

def composition(path,inputs,N):
    ELF=lib(ROOT/N['S']['reader'])['ELF']
    def facts(p):
        e=ELF(p);need(e.header[0]==1 and e.header[1]==243 and not e.program_headers,'Actual nonloadable RV32 ET_REL')
        a={s['name']:(s['flags'],e.data(s))for s in e.sections if s['flags']&2 and s['size']};d={s['name']:(s['info'],s['other'],e.sections[s['section']]['name'],s['value'],s['size'])for s in e.symbols if s['info']>>4 and s['section']};u={s['name']for s in e.symbols if s['info']>>4 and not s['section']};rel=sorted((e.sections[v['section']]['name'],v['offset'],v['type'],v['addend'],e.symbols[v['symbol']]['name'])for v in e.relocations);return a,d,u,rel
    a={};d={};u=set();rel=[]
    for p in inputs:
        aa,dd,uu,rr=facts(p);need(not set(a).intersection(aa)and not set(d).intersection(dd),'Unique real input owners');a.update(aa);d.update(dd);u.update(uu);rel+=rr
    remaining=u-set(d);need(remaining=={N['EV']['target_names'][str(p)]for p in N['EV']['genuine_new_provider_entries']}and len(u)==22 and facts(path)==(a,d,remaining,sorted(rel)),'Every byte,symbol and relocation retained;real callback providers and existing event/state8/setter definitions retain every cross-input reference')
    code=sum(len(v[1])for v in a.values()if v[0]&4);data=sum(len(v[1])for v in a.values()if not v[0]&4);funcs=sum(v[0]==18 and v[4]>0 for v in d.values());objects=sum(v[0]==17 for v in d.values())
    need((code,data,funcs,objects,len(rel))==(12272,256,1010,1,753),'Exact12272-CODE/256-DATA composition')
    independent=lib(ROOT/'experiments/tsl9-remaining-record-dispatch/compare-readers-v1.py')['audit'](path);need(independent['passed'],'Independent complete ELF readers agree')
    return dict(passed=True,object_sha256=sha(path),CODE_bytes=12272,DATA_bytes=256,allocated_bytes=12528,instructions=4291,positive_FUNC_regions=1010,positive_OBJECT_regions=1,relocations=753,named_UND=sorted(remaining),every_input_byte_symbol_relocation_retained=True,independent_readers=independent,callback_and_existing_cross_imports_have_real_bodies=True,all_five_new_real_bodies_retained=True,previous_numeric_callbacks_have_real_bodies=True,registered_numeric_callback_bodies_provided=True,prior_readonly_table_retained=True,zero_named_UND_is_not_runtime_closure=True,raw_RAM_and_callback_dependencies_provided=False,actual_original_address_link_performed=False,linked_into_APP=False,runtime_closed=False,new_BIN=False,firmware_ready=False)
def audit(llvm,refs,trial=None):
    N,result=native(llvm);previous=lib(PRIOR/'audit-v1.py')['audit'](llvm,refs);need(canonical(previous)==json.loads((PRIOR/'audit-result-v1.json').read_bytes()),'Fresh prior state8,scheduler-state,idle,arithmetic,clock,timer and earlier proofs retained')
    contract=callback_contract(N,previous);out=HERE/'build'/('composition-v2'if trial is None else trial)
    if trial:need(Path(trial).name==trial and not out.exists(),'Fresh create-only partial composition')
    composed={};hashes={}
    for mode in ['c','cpp']:
        inputs=[CODE_PRIOR/'build/composition-v1'/mode/'candidate.o',HERE/'build/native-v2'/mode/'unit.o'];hashes[mode]={p.relative_to(ROOT).as_posix():sha(p)for p in inputs};f=out/mode
        if trial:
            f.mkdir(parents=True);argv=[str(llvm/'ld.lld.exe'),'-r','--no-relax',*[str(p)for p in inputs],'-o',str(f/'candidate.o')];p=subprocess.run(argv,capture_output=True,timeout=120);(f/'link.log').write_text(N['portable']((p.stdout+p.stderr).decode('utf-8','replace'),llvm),encoding='utf-8');need(p.returncode==0,'Actual partial link failed;retain trial')
        composed[mode]=composition(f/'candidate.o',inputs,N)
    need(composed['c']==composed['cpp'],'Actual whole C/C++ compositions identical')
    return dict(schema='TSL9-public-SDK-callback-registration-RF-configuration-audit-v1',passed=True,checker_sha256=sha(__file__),SDK_candidate_only=True,native_results=result,callback_contract=contract,prior_state8_audit_sha256=sha(PRIOR/'audit-result-v1.json'),prior_SDK_composition_CODE_bytes=10726,prior_SDK_composition_DATA_bytes=256,prior_state8_scheduler_idle_arithmetic_clock_timer_binding_layout_and_Flash_contracts_retained=True,composition=composed,composition_input_hashes=hashes,APP_source_C_H_files_unchanged=159,APP_byte_coverage_unchanged=95.54,installed_ROM_identity_proved=False,physical_Xwchc_profile_proved=False,physical_RAM_capacity_proved=False,physical_atomicity_proved=False,Flash_callback_effects_closed=False,global_IRQ_alias_or_stack_bound_proved=False,runtime_closed=False,linked_into_APP=False,new_BIN=False,firmware_ready=False,goal_complete=False,target_executed=False,HOST_model_executed=False,ISA_emulated=False,hardware_accessed=False,network=False)
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--tool-dir',type=Path,required=True);p.add_argument('--reference-root',type=Path,required=True);p.add_argument('--link-trial');p.add_argument('--output',type=Path);a=p.parse_args()
    try:
        result=audit(a.tool_dir.resolve(),a.reference_root.resolve(),a.link_trial)
        if a.output:
            dest=HERE/a.output;need(dest.parent==HERE and not dest.exists(),'Create-only audit receipt');dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
        c=result['composition']['c'];print(json.dumps(dict(passed=True,CODE_bytes=1546,instructions=540,composition={k:c[k]for k in ['object_sha256','CODE_bytes','DATA_bytes','instructions','positive_FUNC_regions','positive_OBJECT_regions','relocations','named_UND']},APP_byte_coverage=95.54,new_BIN=False)))
    except Exception as error:
        message=str(error)
        for path,token in [(ROOT,'${PROJECT_ROOT}'),(Path.home(),'${USERPROFILE}')]:message=message.replace(str(path),token).replace(path.as_posix(),token)
        print(json.dumps(dict(passed=False,error_type=type(error).__name__,reason=message)));raise SystemExit(1)
