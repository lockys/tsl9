#!/usr/bin/env python3
"""Audit the complete helper, real readonly table and partial SDK composition statically."""
import argparse,hashlib,json,re,runpy,subprocess,sys
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
PRIOR=ROOT/'experiments/tsl9-resident-clock-services'
def need(ok,label):
    if not ok:raise ValueError(label)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def lib(p):return runpy.run_path(str(p),run_name='arithmetic_static_library')
def canonical(v):return json.loads(json.dumps(v))
def native(llvm):
    N=lib(HERE/'build-v1.py');N['pins'](llvm);saved=json.loads((HERE/'build/native-v1/measurement.json').read_bytes())
    need(saved['inputs']==N['portable'](N['inputs'](llvm),llvm)and saved['candidate_contract']==N['candidate_contract'](),'Every actual native input unchanged');result={}
    for mode in ['c','cpp']:
        f=HERE/'build/native-v1'/mode;v=saved['modes'][mode]
        need(v['artifacts']==N['inventory'](f)and v['dependencies']==N['portable'](N['dependencies'](f,llvm),llvm),'Complete native object and include inventories')
        result[mode]=dict(CODE=N['audit_object'](f/'unit.o'),ABI=N['audit_abi'](f/'config_abi.o'))
        need(result[mode]['CODE']==v['result']and result[mode]['ABI']==v['ABI_result'],'Fresh independent native readers match receipt')
    need(result['c']==result['cpp'],'Actual C11/C++17 objects and compile-only sizes identical');return N,result
def helper_contract(N,previous):
    E,B=N['EV'],N['B'];need(len(E['selected_functions'])==1,'One real complete arithmetic entry');f=E['selected_functions'][0];ops={o['addr']:o for o in f['operations']}
    need((f['start'],f['end'],f['end']-f['start'],len(ops))==(0x6df1a,0x6e2ac,914,296),'Exact complete helper boundary')
    edges=[];returns=[]
    for pc,o in ops.items():
        following=pc+o['size'];mn=o['opcode'].split(' ',1)[0];d=B['decode_control'](bytes.fromhex(o['bytes']),pc)
        if o['type']=='ret':need(o['opcode']=='ret','Only actual normal returns');returns.append(pc);continue
        need(o['type']not in ['ucall','call','rjmp'],'No external or opaque transfer in helper')
        need(mn not in ['sw','sh','sb','sd']and not mn.startswith('qk.c.s'),'No selected memory store')
        need(re.search(r'\bsp\b',o['opcode'])is None,'No SP operand or helper frame allocation')
        if d:
            kind,target=d;need(target in ops,'Every direct control remains in complete helper');edges.append([pc,target])
            if o['type']=='cjmp':need(following in ops,'Whole branch fallthrough');edges.append([pc,following])
        else:need(following in ops,'No fallthrough to neighboring function');edges.append([pc,following])
    graph={pc:[]for pc in ops}
    for a,b in edges:graph[a].append(b)
    visiting=set();done={}
    def depth(pc):
        need(pc not in visiting,'Actual complete helper CFG is acyclic')
        if pc in done:return done[pc]
        visiting.add(pc)
        if not graph[pc]:need(pc in returns,'Every terminal is a real return');n=1
        else:n=1+max(depth(v)for v in graph[pc])
        visiting.remove(pc);done[pc]=n;return n
    maximum=depth(f['start']);need(set(done)==set(ops),'Every selected instruction reachable in the full static entry CFG')
    expected={0x6df1a:'mv a5, a3',0x6df1c:'mv a7, a2',0x6df1e:'mv t1, a0',0x6df20:'mv a6, a1',0x6df22:'bnez a3, 0x6e078',0x6df26:'bleu a2, a1, 0x6dfd6',
        0x6df2a:'lui a4, 0x10',0x6df2c:'bltu a2, a4, 0x6e0e2',0x6df30:'lui a5, 0x1000',0x6df34:'bltu a2, a5, 0x6e274',0x6df38:'srli a3, a2, 0x18',0x6df3c:'li a5, 24',
        0x6df46:'add a4, a4, a3',0x6df48:'qk.c.lbu a4, 0(a4)',0x6df4a:'add a5, a5, a4',0x6df4c:'li a4, 32',0x6df50:'sub a4, a4, a5',
        0x6df6c:'divu a0, a6, a2',0x6df7a:'remu a4, a6, a2',0x6dfa0:'divu a4, a6, a2',0x6dfaa:'remu a6, a6, a2',0x6dfd2:'li a1, 0',
        0x6dfd6:'bnez a2, 0x6dfde',0x6dfd8:'li a4, 1',0x6dfda:'divu a7, a4, a2',0x6dfde:'lui a4, 0x10',0x6dfe0:'bltu a7, a4, 0x6e0d0',0x6dfe4:'lui a5, 0x1000',0x6dfe8:'bltu a7, a5, 0x6e27c',0x6dfec:'srli a3, a7, 0x18',0x6dff0:'li a5, 24',0x6dffa:'add a4, a4, a3',0x6dffc:'qk.c.lbu a3, 0(a4)',0x6dffe:'add a3, a3, a5',
        0x6e078:'bltu a1, a3, 0x6e0ba',0x6e07c:'lui a5, 0x10',0x6e07e:'bltu a3, a5, 0x6e0c0',0x6e082:'lui a5, 0x1000',0x6e086:'bltu a3, a5, 0x6e26c',0x6e08a:'srli a4, a3, 0x18',0x6e08e:'li a6, 24',0x6e098:'add a5, a5, a4',0x6e09a:'qk.c.lbu a4, 0(a5)',0x6e0a0:'add a4, a4, a6',
        0x6e0c0:'li a5, 255',0x6e0c4:'bleu a3, a5, 0x6e28a',0x6e0c8:'srli a4, a3, 0x8',0x6e0cc:'li a6, 8',0x6e0d0:'li a4, 255',0x6e0d4:'mv a3, a7',0x6e0d6:'bleu a7, a4, 0x6dff2',0x6e0da:'srli a3, a7, 0x8',0x6e0de:'li a5, 8',
        0x6e0e2:'li a4, 255',0x6e0e6:'mv a3, a2',0x6e0e8:'bleu a2, a4, 0x6df3e',0x6e0ec:'srli a3, a2, 0x8',0x6e0f0:'li a5, 8',0x6e26c:'srli a4, a3, 0x10',0x6e270:'li a6, 16',0x6e274:'srli a3, a2, 0x10',0x6e278:'li a5, 16',0x6e27c:'srli a3, a7, 0x10',0x6e280:'li a5, 16',0x6e28a:'mv a4, a3',0x6e28c:'li a6, 0',0x6e2aa:'j 0x6e042'}
    need(all(ops[pc]['opcode']==v for pc,v in expected.items()),'Actual entry limbs,unsigned bucket tests,table reads and arithmetic instructions')
    pairs=N['S']['PC_relative_pairs'];need([p['PC']for p in pairs]==[0x6df3e,0x6dff2,0x6e090]and all(p['target_PC']==0x6e95c and p['data_contents_provided']and p['reference_kind']=='direct-readonly-DATA-address-pair'for p in pairs),'Three actual primary-byte AUIPC/ADDI table pointers')
    loads=[o for o in ops.values()if o['type']=='load'];need([o['addr']for o in loads]==[0x6df48,0x6dffc,0x6e09a],'Only three memory reads,all from real readonly lookup table')
    data=E['selected_DATA'][0];need((data['start'],data['end'],data['bytes'])==(0x6e95c,0x6ea5c,256)and all(v==i.bit_length()for i,v in enumerate(data['contents'])),'Every original bit-length table entry')
    # This is a static range lemma for the observed unsigned branch buckets, not execution.
    buckets=[dict(lower=0,upper=255,shift=0),dict(lower=256,upper=65535,shift=8),dict(lower=65536,upper=16777215,shift=16),dict(lower=16777216,upper=4294967295,shift=24)]
    need(all(0<=b['lower']>>b['shift']<=b['upper']>>b['shift']<=255 for b in buckets),'Each selected unsigned bucket yields a real in-bounds byte index')
    need(previous['clock_contract']['delta_provider']['helper']==0x6df1a and previous['clock_contract']['WaitWindow']['helper']==0x6df1a,'Actual preceding clock-helper call provenance')
    clock=json.loads((PRIOR/'evidence-v1.json').read_bytes());clock_ops={o['addr']:o for body in clock['selected_functions']for o in body['operations']}
    need(all(clock_ops[pc]['opcode']=='li a3, 0'for pc in [0x43fc8,0x43d8c,0x43dbc]),'Each actual clock call explicitly resets high denominator A3')
    need(all(B['decode_control'](bytes.fromhex(clock_ops[pc]['bytes']),pc)==(17,0x6df1a)for pc in [0x43fcc,0x43d94,0x43dc6]),'All three actual caller JALs enter this real helper')
    return dict(passed=True,static_only=True,entry=f['start'],end=f['end'],CODE_bytes=914,instructions=296,direct_edges=edges,return_PCs=returns,CFG_acyclic=True,every_instruction_reachable_in_static_CFG=True,maximum_CFG_instructions_to_return=maximum,
        own_frame_bytes=0,memory_store_instructions=0,external_or_opaque_calls=0,readonly_table=dict(entry=0x6e95c,end=0x6ea5c,bytes=256,original_sha256=data['original_sha256'],all_entries_equal_unsigned_index_bit_length=True,loads=[o['addr']for o in loads],index_bounds=[0,255],unsigned_bucket_ranges=buckets),
        input_limb_observations=dict(entry_A0_copied_to='T1',entry_A1_copied_to='A6',entry_A2_copied_to='A7',entry_A3_copied_to='A5',entry_A3_zero_selects_low_denominator_path=True),
        existing_clock_call_sites=[0x43fcc,0x43d94,0x43dc6],existing_clock_calls_set_entry_A3_zero=True,WaitWindow_constant_denominator=1000000,delta_denominator='live ClockFrequency;nonzero/stability still requires clock-state contract',
        algorithm_inference='Unsigned64-bit division candidate using normalized base65536 quotient digits,32-bit DIVU/REMU and corrections',algorithm_inference_is_not_semantic_proof=True,full_input_domain_division_proved=False,zero_divisor_path_present_in_original=True,zero_divisor_target_or_model_tested=False,
        table_data_has_real_native_OBJECT=True,table_address_pairs_are_real_relocations=True,original_address_execution_link_performed=False,physical_ISA_or_ROM_identity_proved=False,target_executed=False,HOST_model_executed=False,ISA_emulated=False,hardware_accessed=False)
def composition(path,inputs,N):
    ELF=lib(ROOT/N['S']['reader'])['ELF']
    def facts(p):
        e=ELF(p);need(e.header[0]==1 and e.header[1]==243 and not e.program_headers,'Actual nonloadable RV32 ET_REL')
        allocated={s['name']:(s['flags'],e.data(s))for s in e.sections if s['flags']&2 and s['size']}
        definitions={s['name']:(s['info'],s['other'],e.sections[s['section']]['name'],s['value'],s['size'])for s in e.symbols if s['info']>>4 and s['section']}
        undefined={s['name']for s in e.symbols if s['info']>>4 and not s['section']}
        relocations=sorted((e.sections[v['section']]['name'],v['offset'],v['type'],v['addend'],e.symbols[v['symbol']]['name'])for v in e.relocations);return allocated,definitions,undefined,relocations
    a={};d={};u=set();rel=[]
    for p in inputs:
        aa,dd,uu,rr=facts(p);need(not set(a).intersection(aa)and not set(d).intersection(dd),'Unique real input CODE/DATA owners');a.update(aa);d.update(dd);u.update(uu);rel+=rr
    remaining=u-set(d);need(remaining=={'tsl9_candidate_external_flash_63dd0','tsl9_candidate_external_ram_2000061a','tsl9_candidate_external_ram_20002610'}and len(u)==4 and facts(path)==(a,d,remaining,sorted(rel)),'Every input byte,symbol and relocation retained;real arithmetic body resolves old import')
    code=sum(len(v[1])for v in a.values()if v[0]&4);data=sum(len(v[1])for v in a.values()if not v[0]&4);funcs=sum(v[0]==18 and v[4]>0 for v in d.values());objects=sum(v[0]==17 for v in d.values())
    need((code,data,funcs,objects,len(rel))==(4426,256,393,1,289),'Exact4426-CODE/256-DATA composition')
    independent=lib(ROOT/'experiments/tsl9-remaining-record-dispatch/compare-readers-v1.py')['audit'](path);need(independent['passed'],'Two independent complete ELF readers agree')
    return dict(passed=True,object_sha256=sha(path),CODE_bytes=4426,DATA_bytes=256,allocated_bytes=4682,instructions=1538,positive_FUNC_regions=393,positive_OBJECT_regions=1,relocations=289,named_UND=sorted(remaining),every_input_byte_symbol_relocation_retained=True,independent_readers=independent,
        arithmetic_import_has_real_body=True,readonly_table_has_real_OBJECT=True,all_three_table_pairs_have_real_relocations=True,zero_named_UND_is_not_runtime_closure=True,raw_RAM_and_callback_dependencies_provided=False,actual_original_address_link_performed=False,linked_into_APP=False,runtime_closed=False,new_BIN=False,firmware_ready=False)
def audit(llvm,trial=None):
    N,result=native(llvm);previous=lib(PRIOR/'audit-v1.py')['audit'](llvm)
    need(canonical(previous)==json.loads((PRIOR/'audit-result-v1.json').read_bytes()),'Fresh3512-byte clock,timer,scheduler and earlier proofs retained')
    contract=helper_contract(N,previous);out=HERE/'build'/('composition-v1'if trial is None else trial)
    if trial:need(Path(trial).name==trial and not out.exists(),'Fresh create-only partial composition')
    composed={};hashes={}
    for mode in ['c','cpp']:
        inputs=[PRIOR/'build/composition-v1'/mode/'candidate.o',HERE/'build/native-v1'/mode/'unit.o'];hashes[mode]={p.relative_to(ROOT).as_posix():sha(p)for p in inputs};f=out/mode
        if trial:
            f.mkdir(parents=True);argv=[str(llvm/'ld.lld.exe'),'-r','--no-relax',*[str(p)for p in inputs],'-o',str(f/'candidate.o')];p=subprocess.run(argv,capture_output=True,timeout=120);(f/'link.log').write_text(N['portable']((p.stdout+p.stderr).decode('utf-8','replace'),llvm),encoding='utf-8');need(p.returncode==0,'Actual partial link failed;retain trial')
        composed[mode]=composition(f/'candidate.o',inputs,N)
    need(composed['c']==composed['cpp'],'Actual entire C/C++ composition objects identical')
    return dict(schema='TSL9-public-SDK-arithmetic-helper-audit-v2',passed=True,checker_sha256=sha(__file__),SDK_candidate_only=True,native_results=result,helper_contract=contract,prior_clock_audit_sha256=sha(PRIOR/'audit-result-v1.json'),prior_SDK_composition_bytes=3512,prior_clock_timer_scheduler_binding_layout_and_Flash_contracts_retained=True,composition=composed,composition_input_hashes=hashes,
        APP_source_C_H_files_unchanged=159,APP_byte_coverage_unchanged=95.54,installed_ROM_identity_proved=False,physical_Xwchc_profile_proved=False,physical_RAM_capacity_proved=False,physical_atomicity_proved=False,Flash_callback_effects_closed=False,global_IRQ_alias_or_stack_bound_proved=False,runtime_closed=False,linked_into_APP=False,new_BIN=False,firmware_ready=False,goal_complete=False,target_executed=False,HOST_model_executed=False,ISA_emulated=False,hardware_accessed=False,network=False)
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--tool-dir',type=Path,required=True);p.add_argument('--link-trial');p.add_argument('--output',type=Path);a=p.parse_args()
    try:
        result=audit(a.tool_dir.resolve(),a.link_trial)
        if a.output:
            dest=HERE/a.output;need(dest.parent==HERE and not dest.exists(),'Create-only portable audit receipt');dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
        c=result['composition']['c'];print(json.dumps(dict(passed=True,CODE_bytes=914,DATA_bytes=256,instructions=296,composition={k:c[k]for k in ['object_sha256','CODE_bytes','DATA_bytes','instructions','positive_FUNC_regions','positive_OBJECT_regions','relocations','named_UND']},helper_static_maximum_instructions=result['helper_contract']['maximum_CFG_instructions_to_return'],division_semantics_proved=False,APP_byte_coverage=95.54,new_BIN=False)))
    except Exception as error:
        message=str(error)
        for path,token in [(ROOT,'${PROJECT_ROOT}'),(Path.home(),'${USERPROFILE}')]:message=message.replace(str(path),token).replace(path.as_posix(),token)
        print(json.dumps(dict(passed=False,error_type=type(error).__name__,reason=message)));raise SystemExit(1)
