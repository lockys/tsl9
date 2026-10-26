#!/usr/bin/env python3
"""Positive byte/CFG/parameter checks and nonloadable SDK composition. No execution model."""
import argparse,hashlib,json,runpy,subprocess,sys
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
APP='firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
def need(ok,label):
    if not ok:raise ValueError(label)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def lib(p):return runpy.run_path(str(p),run_name='BLE_candidate_static_library')
def verify_native(folder,llvm):
    N=lib(folder/'build-v1.py');N['pins'](llvm);saved=json.loads((folder/'build/native-v1/measurement.json').read_bytes())
    need(saved['inputs']==N['portable'](N['inputs'](llvm),llvm)and saved['candidate_contract']==N['candidate_contract'](),'Every original native source/spec/tool input retained')
    result={}
    for mode in ['c','cpp']:
        f=folder/'build/native-v1'/mode;v=saved['modes'][mode]
        need(v['artifacts']==N['inventory'](f)and v['dependencies']==N['portable'](N['dependencies'](f,llvm),llvm),'Complete actual artifact and include inventories')
        result[mode]=dict(CODE=N['audit_object'](f/'unit.o'),ABI=N['audit_abi'](f/'config_abi.o'))
        need(result[mode]['CODE']==v['result']and result[mode]['ABI']==v['ABI_result'],'Fresh independent native/ABI readers agree')
    need(result['c']==result['cpp'],'Actual complete C/C++ object identity')
    return N,result
def audit_copy(path,N):
    need(sha(ROOT/'src/native/resident/copy_arch.c')=='d004661257866b3c8e11ad424dffc47c969f640f9d2bc87c6835aae9be9be660','Frozen real copy source')
    need(sha(path)=='d4e6f71c888be476d2e09c76b3e46c68fff8197236c899030ae6516303fe96b0','Frozen actual curated copy object')
    e=lib(ROOT/N['S']['reader'])['ELF'](path);B=N['B'];carrier=(ROOT/N['S']['firmware']).read_bytes();owners={};count=0
    need(e.header[0]==1 and e.header[1]==243 and not e.program_headers,'Nonloadable actual RV32 copy object')
    symbols=[s for s in e.symbols if s['info']>>4];need(len(symbols)==6,'Six real copy regions; no unresolved import or alias')
    for s in symbols:
        pc=int(s['name'].rsplit('_',1)[1],16);sec=e.sections[s['section']]
        need(s['info']==18 and s['value']==0 and s['size']==sec['size']and sec['flags']==6 and sec['name']=='.text.'+s['name'],'Positive original copy CODE owner')
        owners[sec['index']]=dict(PC=pc,symbol=s,section=sec)
    for owner in owners.values():
        pc=owner['PC'];sec=owner['section'];raw=e.data(sec);off=0x402b0+pc-0x20000040-0x40000
        ref=carrier[off:off+len(raw)];normal=bytearray(raw)
        for r in [v for v in e.relocations if v['section']==sec['index']]:
            target=e.symbols[r['symbol']];target_pc=int(target['name'].rsplit('_',1)[1],16);width,mask=B['MASKS'][r['type']];at=r['offset']
            a=int.from_bytes(raw[at:at+width],'little');b=int.from_bytes(ref[at:at+width],'little')
            need(r['addend']==0 and target['info']==18 and a&mask==b&mask and a&(~mask&((1<<(width*8))-1))==0,'Exact copy control/register bits and true owner target')
            need(B['decode_control'](ref[at:at+width],pc+at)==(r['type'],target_pc),'Original copy direct transfer')
            normal[at:at+width]=(a|B['immediate'](r['type'],target_pc-(pc+at))).to_bytes(width,'little')
        need(bytes(normal)==ref,'Every58 original mapped SDK copy byte equal')
        at=0
        while at<len(raw):
            width=4 if raw[at]&3==3 else 2;need(at+width<=len(raw),'Whole copy instruction');at+=width;count+=1
    need(sum(v['section']['size']for v in owners.values())==58 and count==18 and len(e.relocations)==5,'Complete original copy body')
    need({s['index']for s in e.sections if s['flags']&2 and s['size']}==set(owners),'No extra copy allocation')
    independent=lib(ROOT/'experiments/tsl9-remaining-record-dispatch/compare-readers-v1.py')['audit'](path);need(independent['passed'],'Independent copy readers agree')
    return dict(passed=True,CODE_bytes=58,instructions=18,positive_FUNC_regions=6,relocations=5,object_sha256=sha(path),all_original_SDK_VA_encoded_bytes_equal=True,independent_readers=independent)
def app_contract(N):
    need(sha(ROOT/APP)=='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667','Exact original APP input')
    a=(ROOT/APP).read_bytes();u16=lambda pc:int.from_bytes(a[pc-0x8000:pc-0x8000+2],'little');u32=lambda pc:int.from_bytes(a[pc-0x8000:pc-0x8000+4],'little')
    hi,lo=u32(0x19a3a),u32(0x19a3e);need(hi&0xfff==0x797 and lo&0xfffff==0x78793,'Actual AUIPC/ADDI RAM address role')
    imm=lo>>20;imm-=4096 if imm&2048 else 0;mem=(0x19a3a+(hi&0xfffff000)+imm)&0xffffffff;need(mem==0x2000418c,'Actual encoded declared arena base')
    v=u16(0x19a42);offset=((v>>9)&15)*4+((v>>7)&3)*64
    need(v&0xe003==0xc002 and(v>>2)&31==15 and offset==16,'Actual C.SWSP configuration MEMAddr')
    v=u16(0x19a44);imm=((v>>2)&31)|((v>>12)&1)<<5;imm-=64 if imm&32 else 0
    need(v&0xe003==0x6001 and(v>>7)&31==15 and imm<<12==0x7000,'Actual C.LUI MEMLen value')
    v=u32(0x19a46);offset=((v>>25)<<5)|((v>>7)&31)
    need(v&0x01fff07f==0x00f11023 and offset==20,'Actual halfword store at configuration+4')
    need(u32(0x19ae2)==0x000407b7 and u32(0x19ae6)&0xfffff==0x7a783 and u32(0x19ae6)>>20==164,'Actual immediate pointer slot400A4')
    v=u16(0x19aea);offset=((v>>11)&3)*16+((v>>7)&15)*64+((v>>6)&1)*4+((v>>5)&1)*8
    need(v&0xe003==0 and 8+((v>>2)&7)==10 and offset==16 and u16(0x19aec)==0x9782,'Actual configuration SP+16 and indirect call')
    carrier=(ROOT/N['S']['firmware']).read_bytes();need(int.from_bytes(carrier[0xa4:0xa8],'little')==0x43c7e,'Actual candidate BLE slot28 target')
    need(N['B']['decode_control'](a[0x19ab4-0x8000:0x19ab8-0x8000],0x19ab4)==(17,0x18f56),'Actual APP MAC helper call')
    need(u16(0x19aac)==0x0028,'Actual C.ADDI4SPN A0,SP,8 before the two stores and MAC call')
    writes=[];at=0x19a3a
    while at<0x19ab8:
        v=u32(at);size=4 if v&3==3 else 2
        if size==4 and v&127==35:
            need((v>>15)&31==2,'All local scalar stores address the original stack frame')
            off=((v>>25)<<5)|((v>>7)&31);off-=4096 if off&2048 else 0;width={0:1,1:2,2:4}[(v>>12)&7];writes.append(dict(PC=at,start=off,end=off+width))
        elif size==2 and v&0xe003==0xc002:
            off=((v>>9)&15)*4+((v>>7)&3)*64;writes.append(dict(PC=at,start=off,end=off+4))
        at+=size
    need(at==0x19ab8 and len(writes)==14 and all(v['end']<=68 or v['start']>=72 for v in writes),'All14 explicit local configuration writes avoid staCB bytes')
    for pc,value in [(0x19ab8,0x0818),(0x19aba,0x4781),(0x19abc,0x4699),(0x19abe,0x0030),(0x19ac0,0x963e),(0x19ac6,0x0785),(0x19ac8,0x0705)]:
        need(u16(pc)==value,'Exact six-byte MAC-copy loop operand '+hex(pc))
    need(u32(0x19ac2)==0x00064603,'MAC loop byte load through temporary buffer')
    v=u32(0x19aca);off=((v>>25)<<5)|((v>>7)&31)
    need(v&0x01fff07f==0x00c70023 and off==23,'MAC loop byte store through incremented frame pointer')
    v=u32(0x19ace)
    need(N['B']['decode_control'](a[0x19ace-0x8000:0x19ad2-0x8000],0x19ace)==(16,0x19abe)and(v>>15)&31==15 and(v>>20)&31==13 and(v>>12)&7==1,'Exactly bounded count0..5 MAC loop')
    pc=0x19ad2
    while pc<0x19aec:
        v=u32(pc);size=4 if v&3==3 else 2
        need(not(size==4 and v&127 in[35,47,103,111]),'Only read/branch instructions before the final library call')
        need(not(size==2 and v&0xe003 in[0xa000,0xa002,0xc000,0xc002,0xe000,0xe002,0x2001]),'No additional compressed store or direct call before BLE entry')
        pc+=size
    need(pc==0x19aec,'Complete post-MAC argument/guard instructions')
    mac_writes=[];pc=0x18f56
    while pc<0x18f88:
        v=u32(pc);size=4 if v&3==3 else 2
        if size==4:
            opcode=v&127
            if opcode==35:
                off=((v>>25)<<5)|((v>>7)&31);off-=4096 if off&2048 else 0
                need((v>>12)&7==0 and(v>>15)&31==10,'MAC helper only byte-stores through its argument');mac_writes.append(dict(PC=pc,offset=off,width=1))
            else:need(opcode in[3,19,55]and(v>>7)&31 in[13,14,15],'MAC helper only reads/updates its bounded scratch registers')
        elif pc==0x18f86:need(u16(pc)==0x8082,'Actual MAC helper return')
        else:need(u16(pc)&0xfc03==0x8001 and 8+((u16(pc)>>7)&7)==15,'MAC helper compressed SRLI only updates A5')
        pc+=size
    need(pc==0x18f88 and [v['offset']for v in mac_writes]==list(range(6)),'Complete50-byte MAC helper writes exactly offsets0..5')
    return dict(passed=True,original_APP_sha256=sha(ROOT/APP),MEMAddr_AUIPC_PC=0x19a3a,MEMAddr=mem,MEMLen=0x7000,declared_arena_end_exclusive=mem+0x7000,
        four_byte_aligned=True,physical_RAM_capacity_proved=False,configuration_SP_offset=16,configuration_bytes=64,staCB_SP_span=[68,72],explicit_local_stores=writes,
        MAC_helper_PC=0x18f56,MAC_helper_source='src/native/startup/peripheral_primitives.c',MAC_helper_bounded_bytes=50,MAC_argument_stores=mac_writes,MAC_argument_bytes=6,MAC_argument_SP_offset=8,MAC_argument_SP_span=[8,14],MAC_actual_ID_values_read=False,MAC_copy_configuration_offsets=[24,30],MAC_copy_SP_span=[40,46],
        candidate_BLE_pointer_slot=0x400a4,candidate_BLE_entry=0x43c7e,APP_indirect_call_PC=0x19aec,
        no_explicit_field_or_MAC_write_to_staCB=True,staCB_value_at_heap_call_proved=False,
        reasons_not_proved=['initial zero/copy effects require valid nonaliasing memory and MMIO/ISA contracts','opaque tsCB call at43D38 precedes heap initialization','global IRQ and alias ownership unproved','installed resident identity unproved'])
def cfg(N):
    EV,B,S=N['EV'],N['B'],N['S'];pairs={p['PC']+4:p for p in S['PC_relative_pairs']};graphs=[]
    for f in EV['selected_functions']:
        ops={o['addr']:o for o in f['operations']};pending=[(f['start'],False,False,False)];seen=set();returns=[];calls=[]
        while pending:
            pc,heap,task,zero=pending.pop()
            if(pc,heap,task,zero)in seen:continue
            need(pc in ops,'Every candidate CFG position owned');seen.add((pc,heap,task,zero));o=ops[pc];after=pc+o['size']
            if pc==0x43d4e:need(o['opcode']=='li a5, 0','Actual forced numeric-zero return');zero=True
            if o['opcode']=='ret':returns.append(dict(PC=pc,heap_call_seen=heap,task_call_seen=task,forced_zero_seen=zero));continue
            d=B['decode_control'](bytes.fromhex(o['bytes']),pc)
            if pc in pairs:
                p=pairs[pc];calls.append(dict(PC=pc,target=p['target_PC'],kind='real-far-call'));nexts=[after]
            elif pc==0x43d38:
                need(o['opcode']=='jalr a5','Actual opaque tsCB call');calls.append(dict(PC=pc,pointer_storage=0x20003218,kind='opaque-callback'));nexts=[after]
            elif d:
                kind,target=d;v=int.from_bytes(bytes.fromhex(o['bytes']),'little');call=(kind==17 and(v>>7)&31!=0)or(kind==45 and(v>>13)&7==1)
                if kind in[16,44]:nexts=[target,after]
                elif call:
                    calls.append(dict(PC=pc,target=target,kind='real-direct-call'));heap|=pc==0x43b88;task|=pc==0x43d4c;nexts=[after]
                else:nexts=[target]
            else:nexts=[after]
            for nxt in nexts:need(nxt in ops,'No local normal-return-position or branch gap');pending.append((nxt,heap,task,zero))
        need({v[0]for v in seen}==set(ops)and returns,'Complete local syntactic instruction coverage')
        if f['start']==0x43b3e:need(all(v['heap_call_seen']for v in returns),'Every local task-init normal return follows the real heap-init call')
        if f['start']==0x43c7e:need(any(v['task_call_seen']for v in returns)and all(v['task_call_seen']==v['forced_zero_seen']for v in returns),'Every forced-zero local return follows task-init normal return')
        graphs.append(dict(start=f['start'],end=f['end'],instructions=len(ops),returns=returns,calls=[dict(t)for t in sorted({tuple(sorted(v.items()))for v in calls})],
            all_local_CFG_positions_owned=True,all_calls_assume_normal_return=True,termination_proved=False,physical_execution_proved=False))
    task=EV['selected_functions'][0];ops={o['addr']:o for o in task['operations']};nulls=[o for o in ops.values()if o['opcode']=='beqz a0, 0x43c44'];need(len(nulls)==1,'One real allocation-null branch')
    pc=0x43c44;path=[]
    while pc in ops:
        o=ops[pc];path.append(pc)
        if o['opcode']=='ret':break
        need(not B['decode_control'](bytes.fromhex(o['bytes']),pc)and o['type']not in['call','ucall'],'Null suffix only restores and returns');pc+=o['size']
    need(path[-1]==0x43c4c,'Exact allocation-null return suffix')
    return dict(local_CFG=graphs,allocation_null_branch_PC=nulls[0]['addr'],allocation_null_normal_return_suffix=path,
        public_numeric_zero_is_not_full_initialization_proof=True,opaque_tsCB_effects_unbounded=True)
def composition(path,inputs,N):
    ELF=lib(ROOT/N['S']['reader'])['ELF']
    def facts(p):
        e=ELF(p);need(e.header[0]==1 and e.header[1]==243 and not e.program_headers,'Actual nonloadable composition ET_REL')
        allocated={s['name']:(s['flags'],e.data(s))for s in e.sections if s['flags']&2 and s['size']}
        defined={s['name']:(s['info'],s['other'],e.sections[s['section']]['name'],s['value'],s['size'])for s in e.symbols if s['info']>>4 and s['section']}
        und={s['name']for s in e.symbols if s['info']>>4 and not s['section']}
        rel=sorted((e.sections[r['section']]['name'],r['offset'],r['type'],r['addend'],e.symbols[r['symbol']]['name'])for r in e.relocations)
        return allocated,defined,und,rel
    allocated={};defined={};undefined=set();rel=[]
    for p in inputs:
        a,d,u,r=facts(p);need(not set(allocated).intersection(a)and not set(defined).intersection(d),'Unique real input CODE owners')
        allocated.update(a);defined.update(d);undefined.update(u);rel+=r
    remaining=undefined-set(defined);need(remaining=={'tsl9_candidate_isbufset_200004bc','tsl9_candidate_message_initialize_4329a','tsl9_candidate_system_task_initialize_44022'},'Exactly three genuine remaining named functions')
    need(facts(path)==(allocated,defined,remaining,sorted(rel)),'Every input code byte,positive symbol and typed relocation retained; only real definitions resolve imports')
    need(sum(len(v[1])for v in allocated.values())==1336 and len(defined)==116 and len(rel)==86,'Exact six-body-plus-prior-region composition')
    independent=lib(ROOT/'experiments/tsl9-remaining-record-dispatch/compare-readers-v1.py')['audit'](path);need(independent['passed'],'Independent complete composed ELF readers agree')
    return dict(passed=True,object_sha256=sha(path),CODE_bytes=1336,instructions=467,positive_FUNC_regions=116,relocations=86,
        named_UND=sorted(remaining),real_new_imports_resolved=sorted(undefined-remaining),independent_readers=independent,
        every_input_byte_symbol_relocation_retained=True,actual_original_address_link_performed=False,raw_RAM_and_callback_dependencies_provided=False,
        runtime_closed=False,linked_into_APP=False,new_BIN=False,firmware_ready=False)
def audit(llvm,trial=None):
    N,native=verify_native(HERE,llvm);_,initializer=verify_native(ROOT/'experiments/tsl9-resident-heap-initialization',llvm)
    H=ROOT/'experiments/tsl9-resident-heap-core';prior=lib(H/'audit-v1.py')['audit'](llvm)
    need(prior==json.loads((H/'audit-result-v2.json').read_bytes()),'Preceding584-byte composition and heap proof retained')
    contracts=app_contract(N);flow=cfg(N);out=HERE/'build'/('composition-v1'if trial is None else trial)
    if trial:need(Path(trial).name==trial and not out.exists(),'Create-only nonloadable composition trial')
    composed={};copy={};input_hashes={}
    for mode in ['c','cpp']:
        cp=ROOT/'build/curated-source/safe-gap-20261026-v1/resident-copy-arch'/mode/'curated/unit.o';copy[mode]=audit_copy(cp,N)
        inputs=[H/'build/composition-v1'/mode/'candidate.o',ROOT/'experiments/tsl9-resident-heap-initialization/build/native-v1'/mode/'unit.o',cp,HERE/'build/native-v1'/mode/'unit.o']
        input_hashes[mode]={p.relative_to(ROOT).as_posix():sha(p)for p in inputs};f=out/mode
        if trial:
            f.mkdir(parents=True);argv=[str(llvm/'ld.lld.exe'),'-r','--no-relax',*[str(p)for p in inputs],'-o',str(f/'candidate.o')]
            p=subprocess.run(argv,capture_output=True,timeout=120);(f/'link.log').write_text(N['portable']((p.stdout+p.stderr).decode('utf-8','replace'),llvm),encoding='utf-8');need(p.returncode==0,'Native partial link failed; local log retained')
        composed[mode]=composition(f/'candidate.o',inputs,N)
    need(composed['c']==composed['cpp'],'Identical actual C/C++ composition objects')
    return dict(schema='TSL9-public-SDK-BLE-initialization-audit-v1',passed=True,checker_sha256=sha(__file__),SDK_candidate_only=True,native_results=native,initializer_results=initializer,copy_results=copy,
        APP_parameter_contract=contracts,candidate_flow=flow,composition=composed,composition_input_hashes=input_hashes,
        limits=dict(installed_ROM_identity_proved=False,physical_Xwchc_profile_proved=False,physical_RAM_capacity_proved=False,staCB_value_at_heap_call_proved=False,
            opaque_tsCB_write_effects_bounded=False,global_IRQ_alias_or_stack_bound_proved=False,runtime_closed=False,APP_source_C_H_files_unchanged=159,APP_byte_coverage_unchanged=95.54,linked_into_APP=False,new_BIN=False,firmware_ready=False,goal_complete=False),
        target_executed=False,HOST_model_executed=False,ISA_emulated=False,hardware_accessed=False,network=False)
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--tool-dir',type=Path,required=True);p.add_argument('--link-trial');p.add_argument('--output',type=Path);a=p.parse_args()
    try:
        result=audit(a.tool_dir.resolve(),a.link_trial)
        if a.output:
            dest=HERE/a.output;need(dest.parent==HERE and not dest.exists(),'Create-only portable audit receipt');dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
        print(json.dumps(dict(passed=True,CODE_bytes=546,instructions=193,composition={k:v for k,v in result['composition']['c'].items()if k!='independent_readers'},APP_parameter_contract=result['APP_parameter_contract'],limits=result['limits'])))
    except Exception as error:
        message=str(error)
        for path,token in [(ROOT,'${PROJECT_ROOT}'),(Path.home(),'${USERPROFILE}')]:message=message.replace(str(path),token).replace(path.as_posix(),token)
        print(json.dumps(dict(passed=False,error_type=type(error).__name__,reason=message)));raise SystemExit(1)
