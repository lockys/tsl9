#!/usr/bin/env python3
"""Audit conditional LLE/gateway and original APP frame evidence without target execution."""
import argparse,hashlib,json,re,runpy,subprocess,sys
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
PRIOR=ROOT/'experiments/tsl9-resident-state8-callbacks'
def need(ok,label):
    if not ok:raise ValueError(label)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def lib(p):return runpy.run_path(str(p),run_name='idle_static_library')
def canonical(v):return json.loads(json.dumps(v))
def native(llvm):
    N=lib(HERE/'build-v1.py');N['pins'](llvm);saved=json.loads((HERE/'build/native-v1/measurement.json').read_bytes())
    need(saved['inputs']==N['portable'](N['inputs'](llvm),llvm)and saved['candidate_contract']==N['candidate_contract'](),'All actual native inputs unchanged');result={}
    for mode in ['c','cpp']:
        f=HERE/'build/native-v1'/mode;v=saved['modes'][mode]
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
    graph={pc:[]for pc in ops};returns=[];calls=[]
    for pc,o in ops.items():
        following=pc+o['size'];d=B['decode_control'](bytes.fromhex(o['bytes']),pc)
        if o['type']in ['ret','privileged-return','exception-transfer','rjmp']:returns.append(pc);continue
        if d:
            kind,target=d
            if o['type']=='call':need(target in external and following in ops,'Actual selected/external callee and normal continuation');calls.append(dict(PC=pc,target=target));graph[pc].append(following)
            elif target in ops:
                graph[pc].append(target)
                if o['type']=='cjmp':need(following in ops,'Whole conditional fallthrough');graph[pc].append(following)
            else:need(target in external and o['type']=='jmp','Actual terminal external tail transfer')
        else:
            need(following in ops,'No fallthrough into adjacent function');graph[pc].append(following)
            if o['type']=='ucall':calls.append(dict(PC=pc,target=None))
    return graph,returns,calls
def callback_contract(N,previous):
    E,B=N['EV'],N['B'];entries={f['start']for f in E['selected_functions']};external=entries|{int(k)for k in E['target_names']};functions=[];graphs={}
    need(previous['callback_contract']['new_numeric_CODE_callbacks_unprovided']==[0x65620]and 0x65620 in entries,'Previous numeric callback has its actual complete body')
    for f in E['selected_functions']:
        ops={o['addr']:o for o in f['operations']};g,terminals,calls=cfg(ops,B,external);need(reachable(g,f['start'])==set(ops)and terminals,'Whole selected entry CFG reaches every actual instruction')
        frame=16 if f['start']==0x65620 else 0;changes={pc:int(o['opcode'].rsplit(', ',1)[1],0)for pc,o in ops.items()if o['opcode'].startswith('addi sp, sp, ')}
        need(sorted(changes.values())==([-16,16,16]if frame else []),'Only actual own-frame allocation and both cleanup arms')
        pending=[(f['start'],0)];depths={}
        while pending:
            pc,before=pending.pop()
            if pc in depths:need(depths[pc]==before,'Consistent own SP at CFG join');continue
            depths[pc]=before;after=before+changes.get(pc,0);need(after in [-frame,0],'Only actual own-frame positions')
            if not g[pc]:need(pc in terminals and after==0,'Own frame released at each explicitly typed scope exit')
            pending.extend((v,after)for v in g[pc])
        functions.append(dict(entry=f['start'],end=f['end'],bytes=f['end']-f['start'],instructions=len(ops),own_frame_bytes=frame,own_SP_balanced_at_scope_exits=True,scope_exits=[dict(PC=p,type=ops[p]['type'],instruction=ops[p]['opcode'])for p in terminals],calls=calls,direct_edges=[[p,v]for p in g for v in g[p]]));graphs[f['start']]=g
    ops={o['addr']:o for f in E['selected_functions']for o in f['operations']}
    expected={0x65620:'addi sp, sp, -16',0x6565e:'jr t1',0x656b2:'ret',0x20002e34:'auipc t0, 0x0',0x20002e38:'addi t0, t0, 200',0x20002e3c:'lb t1, 0(t0)',0x20002e40:'sb zero, 0(t0)',0x20002e44:'beqz t1, 0x20002e62',0x20002e48:'csrr a1, mepc',0x20002e4c:'sw a1, 0(sp)',0x20002e4e:'auipc a1, 0x0',0x20002e52:'addi a1, a1, -38',0x20002e56:'csrw mepc, a1',0x20002e5a:'jal ra, 0x20002b4c',0x20002e5e:'mret',0x20002e62:'sw ra, 120(sp)',0x20002e64:'jal ra, 0x2000298e',0x20002e68:'lw ra, 120(sp)',0x20002e6a:'ret',0x20002e28:'jal ra, 0x200007a0',0x20002e2c:'ecall'}
    need(all(ops[p]['opcode']==v for p,v in expected.items()),'Exact actual handoff flag,MEPC,scratch frame,gateway and typed terminal sequence')
    need(ops[0x20002e5e]['bytes']=='73002030'and ops[0x20002e2c]['bytes']=='73000000','Actual MRET and ECALL words,not ordinary ABI returns')
    need([(p['PC'],p['next_PC'],p['target'],p['linker_relocation'])for p in E['pc_relative_address_dependencies']]==[(0x20002e34,0x20002e38,0x20002efc,False),(0x20002e4e,0x20002e52,0x20002e28,False)]and not N['S']['PC_relative_pairs'],'Actual AUIPC/ADDI raw address forms,not fabricated call relocations')
    need(0x20002e34+200==0x20002efc and 0x20002e4e-38==0x20002e28,'PC-relative address arithmetic')
    for entry in [0x2000298e,0x20002b4c]:
        helper=next(f for f in E['selected_functions']if f['start']==entry)
        need(not any(o['opcode'].startswith(('csrr','csrw','csrs','csrrw','addi sp,'))for o in helper['operations']),'Selected register helpers have no direct CSR or SP arithmetic writes;aliasing remains open')
    A=E['original_APP'];app=(ROOT/A['path']).read_bytes();need(hashlib.sha256(app).hexdigest()==A['sha256'],'Pinned original APP carrier')
    for path,h in A['existing_curated_source_hashes'].items():need(sha(ROOT/path)==h,'Existing curated original APP source unchanged')
    for ref in A['references']:
        data=app[ref['start']-0x8000:ref['end']-0x8000];need(len(data)==ref['bytes']and hashlib.sha256(data).hexdigest()==ref['original_sha256'],'Actual original APP reference bytes at Flash base0x8000')
        need(b''.join(bytes.fromhex(o['bytes'])for o in ref['operations'])==data,'Complete contiguous original reference instruction bytes')
        need([o['addr']for o in ref['operations']]==[ref['start']+sum(v['size']for v in ref['operations'][:i])for i in range(len(ref['operations']))],'Original reference address continuity')
    need(sum(r['bytes']for r in A['references'])==226 and E['APP_reference_CODE_added']==0,'226 original reference bytes,no new APP CODE')
    restore,wrapper,binding=A['references'];ro={o['addr']:o['opcode']for o in restore['operations']};wo={o['addr']:o['opcode']for o in wrapper['operations']};bo={o['addr']:o['opcode']for o in binding['operations']}
    def slots(ref,kind):
        return [(m[1],int(m[2]))for o in ref['operations']if(m:=re.fullmatch(kind+r' ([a-z0-9]+), (\d+)\(sp\)',o['opcode']))]
    saved=slots(wrapper,'sw');loaded=slots(wrapper,'lw');restored=slots(restore,'lw');need(len(saved)==29 and saved==loaded and restored==[('a1',0)]+saved and [off for reg,off in saved]==list(range(4,120,4)),'Exact29 register pairs in saved4..116;restore additionally readsMEPC fromSP0')
    need('gp'not in [reg for reg,off in saved]and wo[0x8498]=='addi sp, sp, -128'and wo[0x8518]=='addi sp, sp, 128'and wo[0x851a]=='mret','Original128-byte wrapper with inherited unsaved GP')
    need(wo[0x84d4]=='addi a1, gp, 384'and wo[0x84d8]=='lw a0, 0(a1)'and wo[0x84da]=='jalr a0','Actual GP+384 callback load/call')
    need(ro[0x8448]=='li a1, 32'and ro[0x844c]=='csrs 0x804, a1'and ro[0x8450]=='lw a1, 0(sp)'and ro[0x8452]=='csrw mepc, a1'and ro[0x8490]=='addi sp, sp, 128'and ro[0x8492]=='mret','Original ECALL restore shape;CSR804 physical meaning unproved')
    need(bo[0x199e2]=='lui a5, 0x20000'and bo[0x199e6]=='lw a5, 8(a5)'and bo[0x199ec]=='sw a5, 384(gp)','Original initializer copiesRAM slot2 into liveGP+384')
    startup=E['candidate_startup_reference'];raw=b''.join(bytes.fromhex(o['bytes'])for o in startup['operations']);carrier=(ROOT/E['firmware']).read_bytes();need(raw==carrier[startup['source_start']-0x40000:startup['source_end']-0x40000]and hashlib.sha256(raw).hexdigest()==startup['original_sha256'],'Actual candidate startup binding bytes')
    so={o['addr']:o['opcode']for o in startup['operations']};need(so[0x6de14]=='lui a5, 0x20000'and so[0x6de28]=='lui a4, 0x20003'and so[0x6de2c]=='addi a4, a4, -460'and so[0x6de3c]=='sw a4, 8(a5)'and(0x20003<<12)-460==0x20002e34,'Candidate startup stores actual LLE entry intoRAM8')
    need(not any(re.match(r'(?:lui|addi|mv|lw) a5[, ]',o['opcode'])for o in startup['operations'][1:]),'Startup reference preservesRAM table base A5')
    header=(ROOT/E['header']).read_text(encoding='gb18030');need(E['official_LLE_binding']['header_line']in header and E['official_LLE_binding']['RAM_index']==2,'Pinned official slot2 macro')
    need(A['vector_words_for_restore_entry']==[dict(storage=0x804c,value=0x8448),dict(storage=0x8058,value=0x8448)]and all(int.from_bytes(app[v['storage']-0x8000:v['storage']-0x8000+4],'little')==v['value']for v in A['vector_words_for_restore_entry']),'Actual vector carrier words,without assuming cause/mode dispatch')
    reserved=[0,120];need(all(0<=off and off+4<=128 for off in reserved)and not set(reserved)&{off for reg,off in saved},'Candidate SP0/SP120 fit original128-byte frame and avoid saved4..116')
    primary=(ROOT/E['official_vectors']['path']).read_text();actual=[dict(word=int(hi+lo,16),instruction=text)for text,lo,hi in re.findall(r'# CHECK-ASM-AND-OBJ: (qk\.c\.[^\n]+)\n# CHECK-ASM: encoding: \[0x([0-9a-f]{2}),0x([0-9a-f]{2})\]',primary)]
    need(actual==E['official_vectors']['checked']and len(actual)==52,'All52 official vectors remain primary source evidence')
    assumptions=['installed ROM/table matches candidate','SDK initialization completes in required order','live GP remains stable and GP+384 is not aliased or overwritten','inherited128-byte frame remains valid and callees preserveSP','no asynchronous or MMIO aliasing clobbers frame or MEPC','physical ECALL dispatch preserves expected current frame or is otherwise accounted','vendor vector cause/mode and CSR804 semantics verified']
    return dict(passed=True,static_only=True,functions=functions,previous_numeric_callback_65620_has_real_body=True,actual_LLE_MEPC_target_is_selected_gateway=True,raw_PC_relative_forms=E['pc_relative_address_dependencies'],no_fabricated_PC_relative_relocations=True,original_APP_reference_bytes=226,new_APP_CODE_bytes=0,APP_frame=dict(bytes=128,saved_register_slots=saved,GP_saved=False,reserved_SDK_word_offsets=reserved,minimum_inherited_frame_bytes=124,structural_fit=True,actual_GP_plus384_call=True,RAM_slot2_to_GP_plus384_initializer=True,candidate_slot2_value=0x20002e34,ECALL_restore_entry=0x8448,vector_words=A['vector_words_for_restore_entry'],vector_cause_mode_proved=False,CSR804_mask=32,CSR804_physical_semantics_proved=False),gateway=dict(entry=0x20002e28,real_prior_runner=0x200007a0,exception_transfer=0x20002e2c,ECALL_is_not_an_ordinary_return=True,physical_trap_route_proved=False),raw_dependencies=E['raw_dependencies'],opaque_transfers=E['opaque_transfers'],primary_Xwchc=dict(official_vectors=52,families=8,actual_ports=24,physical_profile_proved=False),required_execution_assumptions=assumptions,inherited_four_byte_copy_gap_retained=True,physical_trap_route_proved=False,global_stack_budget_proved=False,installed_ROM_identity_proved=False,runtime_closed=False,hardware_accessed=False)

def composition(path,inputs,N):
    ELF=lib(ROOT/N['S']['reader'])['ELF']
    def facts(p):
        e=ELF(p);need(e.header[0]==1 and e.header[1]==243 and not e.program_headers,'Actual nonloadable RV32 ET_REL')
        a={s['name']:(s['flags'],e.data(s))for s in e.sections if s['flags']&2 and s['size']};d={s['name']:(s['info'],s['other'],e.sections[s['section']]['name'],s['value'],s['size'])for s in e.symbols if s['info']>>4 and s['section']};u={s['name']for s in e.symbols if s['info']>>4 and not s['section']};rel=sorted((e.sections[v['section']]['name'],v['offset'],v['type'],v['addend'],e.symbols[v['symbol']]['name'])for v in e.relocations);return a,d,u,rel
    a={};d={};u=set();rel=[]
    for p in inputs:
        aa,dd,uu,rr=facts(p);need(not set(a).intersection(aa)and not set(d).intersection(dd),'Unique real input owners');a.update(aa);d.update(dd);u.update(uu);rel+=rr
    remaining=u-set(d);need(remaining=={'tsl9_candidate_external_flash_57dae','tsl9_candidate_external_flash_6020a'}and len(u)==5 and facts(path)==(a,d,remaining,sorted(rel)),'Every byte,symbol and relocation retained;real callback providers and existing event/state8/setter definitions retain every cross-input reference')
    code=sum(len(v[1])for v in a.values()if v[0]&4);data=sum(len(v[1])for v in a.values()if not v[0]&4);funcs=sum(v[0]==18 and v[4]>0 for v in d.values());objects=sum(v[0]==17 for v in d.values())
    need((code,data,funcs,objects,len(rel))==(9608,256,800,1,582),'Exact9608-CODE/256-DATA composition')
    independent=lib(ROOT/'experiments/tsl9-remaining-record-dispatch/compare-readers-v1.py')['audit'](path);need(independent['passed'],'Independent complete ELF readers agree')
    return dict(passed=True,object_sha256=sha(path),CODE_bytes=9608,DATA_bytes=256,allocated_bytes=9864,instructions=3367,positive_FUNC_regions=800,positive_OBJECT_regions=1,relocations=582,named_UND=sorted(remaining),every_input_byte_symbol_relocation_retained=True,independent_readers=independent,callback_and_existing_cross_imports_have_real_bodies=True,all_five_new_real_bodies_retained=True,previous_numeric_callbacks_have_real_bodies=True,new_numeric_callback_65620_provided=True,prior_readonly_table_retained=True,zero_named_UND_is_not_runtime_closure=True,raw_RAM_and_callback_dependencies_provided=False,actual_original_address_link_performed=False,linked_into_APP=False,runtime_closed=False,new_BIN=False,firmware_ready=False)
def audit(llvm,trial=None):
    N,result=native(llvm);previous=lib(PRIOR/'audit-v1.py')['audit'](llvm);need(canonical(previous)==json.loads((PRIOR/'audit-result-v1.json').read_bytes()),'Fresh prior state8,scheduler-state,idle,arithmetic,clock,timer and earlier proofs retained')
    contract=callback_contract(N,previous);out=HERE/'build'/('composition-v1'if trial is None else trial)
    if trial:need(Path(trial).name==trial and not out.exists(),'Fresh create-only partial composition')
    composed={};hashes={}
    for mode in ['c','cpp']:
        inputs=[PRIOR/'build/composition-v1'/mode/'candidate.o',HERE/'build/native-v1'/mode/'unit.o'];hashes[mode]={p.relative_to(ROOT).as_posix():sha(p)for p in inputs};f=out/mode
        if trial:
            f.mkdir(parents=True);argv=[str(llvm/'ld.lld.exe'),'-r','--no-relax',*[str(p)for p in inputs],'-o',str(f/'candidate.o')];p=subprocess.run(argv,capture_output=True,timeout=120);(f/'link.log').write_text(N['portable']((p.stdout+p.stderr).decode('utf-8','replace'),llvm),encoding='utf-8');need(p.returncode==0,'Actual partial link failed;retain trial')
        composed[mode]=composition(f/'candidate.o',inputs,N)
    need(composed['c']==composed['cpp'],'Actual whole C/C++ compositions identical')
    return dict(schema='TSL9-public-SDK-LLE-callback-gateway-audit-v1',passed=True,checker_sha256=sha(__file__),SDK_candidate_only=True,native_results=result,callback_contract=contract,prior_state8_audit_sha256=sha(PRIOR/'audit-result-v1.json'),prior_SDK_composition_CODE_bytes=8672,prior_SDK_composition_DATA_bytes=256,prior_state8_scheduler_idle_arithmetic_clock_timer_binding_layout_and_Flash_contracts_retained=True,composition=composed,composition_input_hashes=hashes,APP_source_C_H_files_unchanged=159,APP_byte_coverage_unchanged=95.54,installed_ROM_identity_proved=False,physical_Xwchc_profile_proved=False,physical_RAM_capacity_proved=False,physical_atomicity_proved=False,Flash_callback_effects_closed=False,global_IRQ_alias_or_stack_bound_proved=False,runtime_closed=False,linked_into_APP=False,new_BIN=False,firmware_ready=False,goal_complete=False,target_executed=False,HOST_model_executed=False,ISA_emulated=False,hardware_accessed=False,network=False)
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--tool-dir',type=Path,required=True);p.add_argument('--link-trial');p.add_argument('--output',type=Path);a=p.parse_args()
    try:
        result=audit(a.tool_dir.resolve(),a.link_trial)
        if a.output:
            dest=HERE/a.output;need(dest.parent==HERE and not dest.exists(),'Create-only audit receipt');dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
        c=result['composition']['c'];print(json.dumps(dict(passed=True,CODE_bytes=936,instructions=338,composition={k:c[k]for k in ['object_sha256','CODE_bytes','DATA_bytes','instructions','positive_FUNC_regions','positive_OBJECT_regions','relocations','named_UND']},APP_byte_coverage=95.54,new_BIN=False)))
    except Exception as error:
        message=str(error)
        for path,token in [(ROOT,'${PROJECT_ROOT}'),(Path.home(),'${USERPROFILE}')]:message=message.replace(str(path),token).replace(path.as_posix(),token)
        print(json.dumps(dict(passed=False,error_type=type(error).__name__,reason=message)));raise SystemExit(1)
