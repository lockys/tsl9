#!/usr/bin/env python3
"""Static conditional allocation bounds plus compile-only ABI assertions;no target execution."""
import argparse,hashlib,json,re,runpy,subprocess,sys
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];S=json.loads((HERE/'spec-v1.json').read_bytes())
QUEUE=ROOT/'experiments/tsl9-resident-message-queue'
def need(ok,label):
    if not ok:raise ValueError(label)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def lib(p):return runpy.run_path(str(p),run_name='task_layout_static_library')
def canonical(v):return json.loads(json.dumps(v))
def pins(llvm):
    need(sha(ROOT/S['ABI_source'])==S['ABI_source_sha256'],'Exact compile-only layout assertion source')
    for k,p in S['primary_paths'].items():need(sha(ROOT/p)==S['primary_sha256'][k],'Pinned primary instruction evidence '+k)
    need(sha(ROOT/S['prior_queue_audit'])==S['prior_queue_audit_sha256'],'Pinned retained queue/event receipt')
    N=lib(QUEUE/'build-v1.py');N['pins'](llvm)
    need(N['S']['flags']==S['flags']and N['S']['tools']==S['tools']and N['S']['reader_sha256']==S['reader_sha256'],'Same actual RV32 compile/read recipe')
    return N
def numerical_contract(N):
    es={k:json.loads((ROOT/p).read_bytes())for k,p in S['primary_paths'].items()}
    op={k:{o['addr']:o for f in e['selected_functions']for o in f['operations']}for k,e in es.items()}
    def check(key,want):need(all(op[key][pc]['opcode']==v for pc,v in want.items()),'Exact allocation-layout instruction roles '+key)
    check('BLE',{0x43b76:'addi a0, s0, 412',0x43b7a:'li a2, 40',0x43b7e:'li a1, 0',0x43b90:'lbu a5, 513(a5)',0x43b94:'addi s0, s0, 412',0x43b98:'li a1, 1',0x43b9a:'srli a0, a5, 0x2',0x43b9e:'andi a5, a5, 3',0x43ba0:'add a0, a0, a5',0x43ba2:'li a5, 3',0x43ba4:'mul a0, a0, a5',0x43ba8:'li a5, 6',0x43bae:'addi a0, a0, 14',0x43bb0:'andi a0, a0, 255',0x43bb4:'qk.c.sb a0, 2(s0)',0x43bb6:'mul a0, a0, a5',0x43bba:'addi a0, a0, 576',0x43bc6:'sw a0, 556(s1)',0x43bca:'beqz a0, 0x43c44',0x43bcc:'qk.c.lbu a2, 2(s0)',0x43bce:'li a5, 6',0x43bd0:'li a1, 0',0x43bd2:'mul a2, a2, a5',0x43bd6:'addi a2, a2, 576',0x43be2:'lw a5, 556(s1)',0x43be6:'qk.c.lbu a4, 2(s0)',0x43bec:'addi a5, a5, 576',0x43bf0:'slli a4, a4, 0x2',0x43bf2:'sw a5, 452(s1)',0x43bf6:'add a5, a5, a4',0x43bfc:'sw a5, 484(a4)',0x43c06:'qk.c.lbu a5, 1(s0)',0x43c1a:'sw a2, 0(a4)',0x43c30:'sw a2, 0(a4)',0x43c3e:'qk.c.sb a4, 1(s0)',0x43c42:'sw a2, 0(a5)'})
    check('heap_init',{0x43108:'lw a1, 492(a5)',0x43114:'addi a2, a1, 544',0x4311c:'qk.c.lhu a4, 4(a5)',0x4311e:'addi a5, a1, -8',0x43128:'add a5, a5, a4',0x43132:'addi a0, a0, 7',0x43134:'srli a3, a4, 0x3',0x43138:'bleu a4, a0, 0x43140',0x4313c:'li a3, 512',0x43140:'add a4, a2, a3',0x43150:'addi a3, a3, -8',0x43152:'qk.c.sh a3, 4(a2)',0x43158:'sw a5, 0(a4)',0x4315a:'sub a5, a5, a4',0x4315c:'addi a5, a5, -8',0x4315e:'qk.c.sh a5, 4(a4)'})
    check('heap',{0x20000066:'addi a5, a0, 3',0x2000006a:'slli a5, a5, 0x10',0x2000006c:'srli a5, a5, 0x10',0x2000006e:'andi a5, a5, -4',0x20000074:'li a4, 52',0x20000078:'bltu a4, a5, 0x200000a4',0x200000a8:'lw a0, 400(a4)',0x200000ae:'qk.c.lhu a4, 6(a0)',0x200000b2:'qk.c.lhu a4, 4(a0)',0x200000c6:'bleu a2, a6, 0x200000f0',0x200000d2:'addi a2, a5, 8',0x200000d8:'add a2, a2, a0',0x200000da:'addi a4, a4, -8',0x200000dc:'qk.c.sh a4, 4(a2)',0x200000e8:'qk.c.sh a5, 4(a0)',0x200000f4:'addi a0, a0, 8'})
    check('APP',{0x19a54:'lui a5, 0x1',0x19a56:'addi a4, a5, -2045',0x19a5a:'sh a4, 30(sp)',0x19a5e:'li a4, 251',0x19a62:'sh a4, 32(sp)',0x19a66:'addi a5, a5, -449',0x19a6a:'li a4, 3',0x19a6c:'sb a4, 34(sp)',0x19a70:'sh a5, 36(sp)'})
    # The complete straight-line instruction sequence has no intervening A5 writer except ADDI19A66.
    segment=[o for pc,o in sorted(op['APP'].items())if 0x19a54<=pc<=0x19a70]
    need([o['addr']for o in segment]==[0x19a54,0x19a56,0x19a5a,0x19a5e,0x19a62,0x19a66,0x19a6a,0x19a6c,0x19a70],'Complete literal-def/use segment')
    app=(ROOT/'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin').read_bytes()
    for o in segment:need(app[o['addr']-0x8000:o['addr']-0x8000+o['size']]==bytes.fromhex(o['bytes']),'Actual original APP constant/store bytes')
    word=(1<<12)-449;config_stack_offset=16;store_stack_offset=36;connection_offset=store_stack_offset+1-config_stack_offset
    need(word==0x0e3f and connection_offset==21,'Actual little-endian configuration byte placement')
    connection=(word>>8)&255;capacity=3*((connection>>2)+(connection&3))+14;requested=576+6*capacity;rounded=(requested+3)&~3
    need(connection==14 and capacity==29 and requested==750 and rounded==752,'Original APP supplied conditional numeric allocation')
    # Pure integer inequalities over a byte domain;no machine state,memory or firmware model is executed.
    qmin,qmax,rmin,rmax=0,255>>2,0,3;cap_min=3*(qmin+rmin)+14;cap_max=3*(qmax+rmax)+14
    req_min=576+6*cap_min;req_max=576+6*cap_max
    need((cap_min,cap_max,req_min,req_max)==(14,212,660,1848)and cap_max<256 and req_max%4==0 and req_max<65532,'No capacity-byte or allocator16-bit rounding overflow in the byte-domain bounds')
    A=lib(ROOT/'experiments/tsl9-resident-ble-initialization/audit-v1.py');BN=lib(ROOT/'experiments/tsl9-resident-ble-initialization/build-v1.py');p=A['app_contract'](BN)
    mem,length=p['MEMAddr'],p['MEMLen'];need((mem,length)==(0x2000418c,0x7000),'Fresh original APP arena parameter proof')
    small=min(length>>3,512);first=mem+544;large=first+small;sentinel=mem+length-8;available=sentinel-large-8
    need(length>4103 and small==512 and available==27600 and req_max<available-8 and req_min>52,'Every byte-domain task allocation fits this pristine declared large block and takes the split path')
    payload=large+8;split=payload+rounded;split_payload=split+8;remaining=available-rounded-8
    records=[payload,payload+576];handlers=[records[1],records[1]+4*capacity];events=[handlers[1],handlers[1]+2*capacity]
    need(events[1]==payload+requested<=payload+rounded==split and split_payload+remaining==sentinel,'Exact numeric partition,rounding padding and residual block span')
    need(payload%4==handlers[0]%4==events[0]%4==0 and remaining<65536 and remaining>0,'Observed word/halfword alignment and residual halfword capacity')
    need((16*2+15+1)*12==576 and 3*4<=4*cap_min and 3*2<=2*cap_min,'All record fields for callback task IDs0..2 and bits0..15,three handler stores and three event halfwords fit')
    return dict(passed=True,static_integer_bounds_only=True,concrete_machine_or_memory_simulated=False,original_APP_store=dict(PC=0x19a70,word=word,SP_offset=36,configuration_SP_offset=16,ConnectNumber_offset=21,supplied_ConnectNumber=connection,ConnectNumber_at_later_task_call_proved=False),
        formulas=dict(capacity='3*((ConnectNumber >> 2)+(ConnectNumber & 3))+14',requested='576+6*capacity',rounded='(requested+3)&~3',records='[payload,payload+576)',handlers='[payload+576,payload+576+4*capacity)',events='[payload+576+4*capacity,payload+576+6*capacity)'),
        byte_domain_bounds=dict(capacity_min=cap_min,capacity_max=cap_max,request_min=req_min,request_max=req_max,no_capacity_byte_or16bit_request_wrap=True,large_pool_threshold=52,all_requests_choose_large_pool=True),
        conditional_original_values=dict(ConnectNumber=connection,capacity=capacity,requested_bytes=requested,rounded_payload_bytes=rounded,rounding_padding_bytes=rounded-requested,record_bytes=576,record_count=48,record_stride=12,handler_bytes=4*capacity,event_bytes=2*capacity),
        declared_arena=dict(start=mem,end=mem+length,bytes=length,first_small_node=first,small_span_bytes=small,large_node=large,large_free_payload_bytes=available,sentinel=sentinel),
        conditional_pristine_first_fit=dict(payload=payload,records=records,handlers=handlers,events=events,rounded_payload_end=split,split_free_node=split,split_free_payload=split_payload,split_free_payload_bytes=remaining),
        bounds=dict(record_task_ID_min=0,record_task_ID_max=2,event_bit_index_min=0,event_bit_index_max=15,all_selected_record_fields_within_576_bytes=True,three_registration_words_fit=True,valid_event_halfwords_fit_if_registered_count_le_capacity=True),
        assumptions=['SDK ConnectNumber at43B90 still equals the APP-supplied14 for the concrete address example','declared MEMAddr/MEMLen correspond to valid writable RAM','initialized heap metadata is pristine at the first task allocation','all calls return normally and relevant MMIO/IRQ/DMA aliases do not change metadata','task-count byte2000319D is zero at43C06 for the three0..2 registrations after the intervening SNV path','allocation pointers and capacities remain stable and the task buffer remains allocated','later registered task count does not exceed capacity for event-array bounds'],
        task_count_zero_after_SNV_proved=False,physical_RAM_capacity_proved=False,heap_or_APP_global_ownership_proved=False,whole_program_stack_or_IRQ_bound_proved=False,installed_ROM_identity_proved=False,runtime_closed=False,new_BIN=False)
def layout_dependencies(folder,llvm,N):
    text=(folder/'unit.d').read_text(encoding='utf-8').replace('\\\n',' ');target,separator,tail=text.partition(':')
    need(separator and target=='unit.o','Actual compiler dependency target')
    paths={Path(re.sub(r'\\(.)',r'\1',token)).resolve()for token in re.findall(r'(?:\\.|[^\s])+',tail)}
    source=(ROOT/S['ABI_source']).resolve();header=(ROOT/N['EV']['header']).resolve();resource=(llvm.parent/'lib/clang/18').resolve()
    need({source,header}<=paths and all(p in {source,header}or p.is_relative_to(resource)for p in paths),'Only exact layout source,pinned official header and compiler resources are included')
    need(sha(header)==N['EV']['header_sha256'],'Actual included official header remains pinned')
    return N['portable']({str(p):sha(p)for p in sorted(paths)},llvm)
def abi_assertions(llvm,N,trial=None):
    out=HERE/'build'/('abi-v2'if trial is None else trial)
    if trial:need(Path(trial).name==trial and not out.exists(),'Fresh retained compile-only ABI trial')
    results={};artifacts={}
    for mode in ['c','cpp']:
        f=out/mode
        if trial:
            f.mkdir(parents=True);argv=[str(llvm/'clang.exe')]+S['flags'][mode]+['-MD','-MF',str(f/'unit.d'),'-MT','unit.o','-c',str(ROOT/S['ABI_source']),'-o',str(f/'unit.o')]
            p=subprocess.run(argv,capture_output=True,timeout=120);(f/'compile.log').write_text(N['portable']((p.stdout+p.stderr).decode('utf-8','replace'),llvm),encoding='utf-8');need(p.returncode==0,'Compile-only ABI assertion failed;retain trial')
        results[mode]=dict(base_ABI=N['audit_abi'](f/'unit.o'),ConnectNumber_offset=21,ConnectNumber_bytes=1,record_stride=12,record_alignment=4,record_offsets=[0,4,8],allocated_runtime_bytes=0)
        artifacts[mode]=dict(files=N['inventory'](f),dependencies=layout_dependencies(f,llvm,N))
    need(results['c']==results['cpp'],'Actual complete C11/C++17 ABI assertion objects identical')
    inputs=N['portable']({str(p):sha(p)for p in [Path(__file__),HERE/'spec-v1.json',ROOT/S['ABI_source'],*[ROOT/p for p in S['primary_paths'].values()]]},llvm)
    current=dict(inputs=inputs,results=results,artifacts=artifacts)
    if trial:(out/'measurement.json').write_text(json.dumps(current,indent=2)+'\n',encoding='utf-8')
    else:need(current==json.loads((out/'measurement.json').read_bytes()),'Every retained ABI input,object and include dependency unchanged')
    return current
def audit(llvm,trial=None):
    N=pins(llvm);Q=lib(QUEUE/'audit-v1.py');previous=Q['audit'](llvm);need(canonical(previous)==json.loads((ROOT/S['prior_queue_audit']).read_bytes()),'Fresh full2264-byte native and previous Flash proof unchanged')
    for mode in ['c','cpp']:need(sha(QUEUE/'build/composition-v1'/mode/'candidate.o')==S['prior_queue_composition_sha256'],'Actual prior SDK composition retained')
    result=numerical_contract(N);abi=abi_assertions(llvm,N,trial)
    return dict(schema='TSL9-conditional-task-RAM-layout-verification-v1',passed=True,checker_sha256=sha(__file__),spec_sha256=sha(HERE/'spec-v1.json'),ABI_source_sha256=sha(ROOT/S['ABI_source']),numerical_contract=result,ABI_assertions=abi,prior_queue_audit_sha256=sha(ROOT/S['prior_queue_audit']),prior_SDK_composition_bytes=2264,prior_SDK_composition_sha256=S['prior_queue_composition_sha256'],prior_Flash_argument_contract_retained=True,
        APP_source_C_H_files_unchanged=159,APP_byte_coverage_unchanged=95.54,new_reconstructed_CODE_bytes=0,ABI_assertion_compilation=True,new_allocated_runtime_bytes=0,physical_RAM_capacity_proved=False,heap_or_APP_global_ownership_proved=False,whole_program_stack_or_IRQ_bound_proved=False,installed_ROM_identity_proved=False,linked_into_APP=False,runtime_closed=False,new_BIN=False,firmware_ready=False,goal_complete=False,target_executed=False,HOST_model_executed=False,ISA_emulated=False,hardware_accessed=False,network=False)
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--tool-dir',type=Path,required=True);p.add_argument('--trial');p.add_argument('--output',type=Path);a=p.parse_args()
    try:
        result=audit(a.tool_dir.resolve(),a.trial)
        if a.output:
            dest=HERE/a.output;need(dest.parent==HERE and not dest.exists(),'Create-only portable layout receipt');dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
        n=result['numerical_contract'];print(json.dumps(dict(passed=True,supplied_ConnectNumber=14,conditional_capacity=29,conditional_requested_bytes=750,rounded_bytes=752,conditional_spans=n['conditional_pristine_first_fit'],ABI_allocated_runtime_bytes=0,new_CODE_bytes=0,APP_byte_coverage=95.54,physical_RAM_capacity_proved=False,new_BIN=False)))
    except Exception as error:
        message=str(error)
        for path,token in [(ROOT,'${PROJECT_ROOT}'),(Path.home(),'${USERPROFILE}')]:message=message.replace(str(path),token).replace(path.as_posix(),token)
        print(json.dumps(dict(passed=False,error_type=type(error).__name__,reason=message)));raise SystemExit(1)
