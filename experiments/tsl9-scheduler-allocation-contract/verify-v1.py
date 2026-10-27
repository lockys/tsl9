"""Check encoded allocation/partition relation and compile numeric assertions only."""
import argparse,hashlib,json,re,runpy,subprocess,sys
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def need(ok,label):
    if not ok:raise ValueError(label)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def lib(p):return runpy.run_path(str(ROOT/p),run_name='scheduler_allocation_static_library')
def norm(v):return json.loads(json.dumps(v))
def static_contract(E):
    need(all(sha(ROOT/p)==h for p,h in E['references'].items()),'All prior source/evidence/checker pins')
    raw=(ROOT/E['firmware']).read_bytes();need(hashlib.sha256(raw).hexdigest()==E['firmware_sha256'],'Actual candidate SDK carrier')
    B=lib('experiments/tsl9-original-startup/build-v1.py');V=lib('experiments/tsl9-original-RF-tx-path/audit-v1.py');C=lib('experiments/tsl9-original-APP-early-IRQ/verify-v1.py');maps={};graphs={};rows=[]
    frames={0x43b3e:16,0x2000039c:0,0x43414:48,0x43a14:32,0x43874:48,0x20000040:16}
    for s in E['selected_existing_bodies']:
        evidence=json.loads((ROOT/s['reference']).read_bytes());f=next(f for f in evidence['selected_functions']if f['start']==s['start']);need(f['end']==s['end']and len(f['operations'])==s['instructions'],'Exact whole prior body bounds')
        at=f['start']
        for o in f['operations']:
            source=o.get('source_flash_PC',o.get('source_PC',o['addr'] if o['addr']<0x20000000 else o['addr']-0x20000000+0x40270))
            b=bytes.fromhex(o['bytes']);need(o['addr']==at and len(b)==o['size']and raw[source-0x40000:source-0x40000+len(b)]==b,'Every original reference byte and actual instruction boundary');at+=len(b)
        need(at==f['end'],'Whole reference byte coverage');ext={d[1]for o in f['operations']if(d:=B['decode_control'](bytes.fromhex(o['bytes']),o['addr']))};ops,g,q=V['whole_cfg'](f,B,ext,frames[f['start']]);maps[f['start']]=ops;graphs[f['start']]=g;rows.append(q)
    need(sum(q['bytes']for q in rows)==E['reference_CODE_bytes']and sum(q['instructions']for q in rows)==E['reference_instructions'],'Actual complete prior body totals')
    op=maps[0x43b3e]
    expected={0x43b6a:'lui s0, 0x20003',0x43b8c:'lui a5, 0x20003',0x43b90:'lbu a5, 513(a5)',0x43b94:'addi s0, s0, 412',0x43b98:'li a1, 1',0x43b9a:'srli a0, a5, 0x2',0x43b9e:'andi a5, a5, 3',0x43ba0:'add a0, a0, a5',0x43ba2:'li a5, 3',0x43ba4:'mul a0, a0, a5',0x43ba8:'li a5, 6',0x43baa:'lui s1, 0x20003',0x43bae:'addi a0, a0, 14',0x43bb0:'andi a0, a0, 255',0x43bb4:'qk.c.sb a0, 2(s0)',0x43bb6:'mul a0, a0, a5',0x43bba:'addi a0, a0, 576',0x43bc6:'sw a0, 556(s1)',0x43bca:'beqz a0, 0x43c44',0x43bcc:'qk.c.lbu a2, 2(s0)',0x43bce:'li a5, 6',0x43bd0:'li a1, 0',0x43bd2:'mul a2, a2, a5',0x43bd6:'addi a2, a2, 576',0x43be2:'lw a5, 556(s1)',0x43be6:'qk.c.lbu a4, 2(s0)',0x43be8:'lui s1, 0x20003',0x43bec:'addi a5, a5, 576',0x43bf0:'slli a4, a4, 0x2',0x43bf2:'sw a5, 452(s1)',0x43bf6:'add a5, a5, a4',0x43bf8:'lui a4, 0x20003',0x43bfc:'sw a5, 484(a4)',0x43c44:'lw ra, 12(sp)',0x43c4a:'addi sp, sp, 16',0x43c4c:'ret'}
    need(all(op[p]['opcode']==s for p,s in expected.items()),'Exact encoded input/count/request/store/guard/partition operands')
    def far(pc):
        h=int.from_bytes(bytes.fromhex(op[pc]['bytes']),'little');l=int.from_bytes(bytes.fromhex(op[pc+4]['bytes']),'little');need(h&127==0x17 and l&0x707f==0x67 and(h>>7)&31==(l>>15)&31,'Actual typed AUIPC/JALR pair');imm=l>>20;imm=imm-4096 if imm&2048 else imm;return(pc+(h&0xfffff000)+imm)&0xffffffff
    need(far(0x43bbe)==0x20000040 and far(0x43bda)==0x2000039c,'Actual allocator and memset targets,not guessed names')
    need(C['constant'](op[0x43b8c],15)==C['constant'](op[0x43baa],9)==0x20003000 and 0x20003000+513==0x20003201 and 0x20003000+412+2==0x2000319e and 0x20003000+556==0x2000322c,'Independent numeric input/count/pointer slots')
    need(graphs[0x43b3e][0x43bca]==[0x43c44,0x43bcc],'Null allocator result skips clearing,partition assignments and later initializers')
    for point in [0x43bcc,0x43be2,0x43bf2,0x43bfc]:need(point not in V['reachable'](graphs[0x43b3e],0x43c44),'Null branch cannot reach suffix stores')
    alloc=maps[0x20000040];need(all(alloc[p]['opcode']==s for p,s in {0x20000066:'addi a5, a0, 3',0x2000006a:'slli a5, a5, 0x10',0x2000006c:'srli a5, a5, 0x10',0x2000006e:'andi a5, a5, -4'}.items()),'Actual allocator 16-bit truncate and4-byte rounding recipe')
    prior=json.loads((ROOT/E['prior_study']/'audit-result-v1.json').read_bytes());banks=prior['contract']['scheduler_banks'];need(banks['pointer_slot']==0x2000322c and banks['stride']==12 and banks['lower_half_open_indices']==[0,16]and banks['upper_half_open_indices']==[16,48]and banks['total_numeric_bytes']==576,'Same numeric pointer slot and576-byte bank union from prior complete proof')
    need(3*(63+3)+14==212 and 576+6*14==660 and 576+6*212==1848 and 1848+3<65536,'Algebraic unsigned-byte expression bounds;not input execution')
    ownership=lib('experiments/tsl9-original-RF-task-path/verify-ownership-v2.py');witness={}
    for mode in ['c','cpp']:
        p=ROOT/E['prior_study']/'build/composition-v1'/mode/'candidate.o';o=ownership['inspect'](p);need(o['passed']and all(pc in o['_byte_map']for f in rows for pc in range(f['start'],f['end'])),'Every complete referenced body exists in current unique native composition');witness[mode]=dict(object_sha256=sha(p),CODE_bytes=o['CODE_bytes'],non_CODE_allocations=o['non_CODE_allocations'],named_UND=o['named_UND'])
    need(witness['c']==witness['cpp'],'Same existing actual C/C++ composition witness')
    return dict(passed=True,existing_functions=rows,reference_CODE_bytes=E['reference_CODE_bytes'],reference_instructions=E['reference_instructions'],encoded_input_byte_address=0x20003201,count_byte_address=0x2000319e,count_expression='3*((x >> 2)+(x & 3))+14',algebraic_count_bounds=[14,212],count_expression_fits_unsigned_byte=True,allocator_pair_PC=0x43bbe,allocator_entry=0x20000040,allocator_A1=1,request_expression='576+6*n_alloc',algebraic_request_bounds=[660,1848],allocator_rounding='low16(low16(request+3)&~3)',no_16bit_request_wrap_for_encoded_bound=True,allocator_result_store_PC=0x43bc6,table_pointer_slot=0x2000322c,null_return_skips_following_initialization=True,clear_pair_PC=0x43bda,clear_entry=0x2000039c,clear_size_expression='576+6*n_clear',partition_pointer_fresh_load_PC=0x43be2,partition_count_fresh_load_PC=0x43be6,first_suffix_pointer_slot=0x200031c4,first_suffix_expression='p_after_clear+576',second_suffix_pointer_slot=0x200031e4,second_suffix_expression='p_after_clear+576+4*n_partition',scheduler_record_bytes=12,scheduler_record_count=48,scheduler_prefix_bytes=576,conditional_suffix_widths=[4,2],conditional_numeric_total='576+4*n+2*n',requires_n_alloc_equals_n_clear_equals_n_partition=True,requires_returned_pointer_equals_later_fresh_pointer=True,requires_valid_nonoverlapping_memory_and_compatible_callee_IRQ_contracts=True,allocation_capacity_ownership_lifetime_or_initialization_success_proved=False,all_subsequent_callback_array_writes_in_bounds_proved=False,physical_RAM_ROM_ISA_or_irq_atomicity_proved=False,native_existing_witness=witness)
def verify(llvm,refs,trial=None):
    S=json.loads((HERE/'spec-v1.json').read_bytes());E=json.loads((HERE/'evidence-v1.json').read_bytes());need(all(sha(ROOT/p)==h for p,h in S['sources'].items()),'Exact new numeric source/evidence inputs');need(all(sha(llvm/n)==h for n,h in S['tools'].items()),'Exact approved LLVM tools');need(sha(llvm.parent/'lib/clang/18/include/stdint.h')==S['stdint_sha256'],'Exact approved stdint resource')
    prior=lib(E['prior_study']+'/audit-v1.py')['audit'](llvm,refs);need(norm(prior)==json.loads((ROOT/E['prior_study']/'audit-result-v1.json').read_bytes())and sha(ROOT/E['prior_study']/'audit-result-v1.json')==E['prior_receipt_sha256'],'Fresh complete prior proof equals retained receipt');contract=static_contract(E)
    N=lib(E['prior_study']+'/build-v1.py');N['pins'](llvm);need(S['flags']==N['S']['flags'],'Exact approved C11/C++17 target compile recipe')
    folder=HERE/'build'/(trial or 'native-v1');need(trial is None or Path(trial).name==trial and not folder.exists(),'Create-only native assertion compilation');saved=None if trial else json.loads((folder/'measurement.json').read_bytes());inputs=N['portable']({str(p):sha(p)for p in [Path(__file__),HERE/'spec-v1.json',HERE/'scheduler_layout.h',HERE/'scheduler_layout_abi.c',HERE/'evidence-v1.json']},llvm)
    if saved:need(saved['inputs']==inputs,'Compile inputs unchanged')
    ELF=lib('experiments/tsl9-original-RF-task-path/elf_reader-v6.py')['ELF'];Compare=lib('experiments/tsl9-original-RF-task-path/compare-readers-v2.py')['audit'];modes={}
    for mode in ['c','cpp']:
        f=folder/mode
        if trial:
            f.mkdir(parents=True);p=subprocess.run([str(llvm/'clang.exe'),*S['flags'][mode],'-MD','-MF',str(f/'unit.d'),'-MT','unit.o','-c',str(HERE/'scheduler_layout_abi.c'),'-o',str(f/'unit.o')],capture_output=True,timeout=120);(f/'compile.log').write_text(N['portable']((p.stdout+p.stderr).decode('utf-8','replace'),llvm),encoding='utf-8');need(p.returncode==0,'Actual numeric assertion compile;retain failed trial')
        obj=f/'unit.o';e=ELF(obj);need(e.header[0]==1 and e.header[1]==243 and not e.program_headers and not e.relocations and not any(s['flags']&2 and s['size']for s in e.sections)and not any(s['info']>>4 for s in e.symbols),'Zero allocated bytes,providers,imports,relocations or entry point');ind=Compare(obj);need(ind['passed'],'Independent readers agree with every actual ELF byte/symbol/relocation')
        text=(f/'unit.d').read_text('utf-8').replace('\\\n',' ');target,sep,tail=text.partition(':');need(target=='unit.o'and sep,'Exact compiler dependency target');deps={Path(re.sub(r'\\(.)',r'\1',token)).resolve()for token in re.findall(r'(?:\\.|[^\s])+',tail)};required={(HERE/'scheduler_layout_abi.c').resolve(),(HERE/'scheduler_layout.h').resolve()};resource=(llvm.parent/'lib/clang/18').resolve();need(required<=deps and all(p in required or p.is_relative_to(resource)for p in deps),'Only current sources and approved compiler resources in include closure')
        result=dict(passed=True,object_sha256=sha(obj),allocated_bytes=0,providers=0,imports=0,relocations=0,independent_readers=ind);modes[mode]=dict(result=result,artifacts=N['inventory'](f),dependencies=N['portable']({str(p):sha(p)for p in sorted(deps)},llvm))
        if saved:need(saved['modes'][mode]==modes[mode],'Every compile artifact/include/result unchanged')
    need(modes['c']['result']==modes['cpp']['result'],'Actual C11/C++17 assertion objects identical')
    if trial:(folder/'measurement.json').write_text(json.dumps(dict(inputs=inputs,modes=modes),indent=2)+'\n',encoding='utf-8')
    return dict(schema='TSL9-scheduler-allocation-contract-verification-v1',passed=True,checker_sha256=sha(__file__),contract=contract,native_results={m:modes[m]['result']for m in modes},APP_source_C_H_files_unchanged=159,APP_byte_coverage_unchanged=95.54,SDK_CODE_bytes_unchanged=29848,SDK_DATA_bytes_unchanged=256,SDK_named_UND_unchanged=4,inherited_startup_source_gap_bytes=4,new_target_CODE_bytes=0,new_target_DATA_bytes=0,numeric_assertion_compilation_only=True,target_executed=False,HOST_model_executed=False,ISA_emulated=False,hardware_accessed=False,network=False,linked_into_APP=False,runtime_closed=False,new_BIN=False,firmware_ready=False,goal_complete=False)
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--tool-dir',type=Path,required=True);p.add_argument('--reference-root',type=Path,required=True);p.add_argument('--build-trial');p.add_argument('--output',type=Path);a=p.parse_args()
    try:
        v=verify(a.tool_dir.resolve(),a.reference_root.resolve(),a.build_trial)
        if a.output:
            dest=HERE/a.output;need(dest.parent==HERE and not dest.exists(),'Create-only verification receipt');dest.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')
        print(json.dumps(dict(passed=True,reference_CODE_bytes=v['contract']['reference_CODE_bytes'],reference_instructions=v['contract']['reference_instructions'],allocation_request_bounds=[660,1848],conditional_prefix_bytes=576,new_target_CODE_bytes=0,numeric_assertion_allocated_bytes=0,new_BIN=False,firmware_ready=False)))
    except Exception as error:
        message=str(error)
        for path,token in [(ROOT,'${PROJECT_ROOT}'),(Path.home(),'${USERPROFILE}')]:message=message.replace(str(path),token).replace(path.as_posix(),token)
        print(json.dumps(dict(passed=False,error_type=type(error).__name__,reason=message)));raise SystemExit(1)
