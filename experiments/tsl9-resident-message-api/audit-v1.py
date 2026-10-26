#!/usr/bin/env python3
"""Re-derive candidate API CFG,store ordering and bounded SDK-version differences."""
import argparse,hashlib,json,runpy
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]

def need(ok,label):
    if not ok:raise ValueError(label)

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def audit(llvm):
    N=runpy.run_path(str(HERE/'build-v1.py'),run_name='candidate_native_library');N['pins'](llvm)
    S,EV,B=N['S'],N['EV'],N['B'];saved=json.loads((HERE/'build/native-v1/measurement.json').read_bytes())
    need(saved['inputs']==N['portable'](N['inputs'](llvm),llvm)and saved['caller_contract']==N['caller_contract'](),'Every actual candidate/caller input unchanged')
    native={}
    for mode in ['c','cpp']:
        f=HERE/'build/native-v1'/mode;job=saved['modes'][mode]
        need(job['artifacts']==N['inventory'](f),'Complete actual native artifact inventory')
        need(job['dependencies']==N['portable'](N['dependencies'](f,llvm),llvm),'Every compiler include dependency retained')
        native[mode]=N['audit_object'](f/'unit.o');need(native[mode]==job['result'],'Fresh two-reader native byte audit')
    need(native['c']['object_sha256']==native['cpp']['object_sha256'],'Actual C/C++ object identity')
    ops={o['addr']:o for f in EV['selected_functions']for o in f['operations']}
    def at(pc,text):need(ops[pc]['opcode']==text,'Actual candidate instruction '+hex(pc))
    for pc,text in [(0x2000023c,'lui s1, 0x40024'),(0x20000244,'lw s2, 524(s1)'),(0x20000248,'sw zero, 524(s1)'),(0x2000024c,'fence.i'),(0x20000250,'bnez a0, 0x20000262'),(0x20000264,'addi a0, a0, 8'),(0x20000266,'lui a1, 0xf'),(0x20000268,'slli a0, a0, 0x10'),(0x2000026a,'or a1, a1, s0'),(0x2000026c,'srli a0, a0, 0x10'),(0x20000274,'sw zero, 0(a0)'),(0x20000278,'qk.c.sh s0, 4(a0)'),(0x2000027a,'qk.c.sb a5, 6(a0)'),(0x20000280,'addi a0, a0, 8'),(0x431c0,'lui s0, 0x40024'),(0x431c6,'lw s1, 524(s0)'),(0x431ca,'sw zero, 524(s0)'),(0x431ce,'fence.i'),(0x431e4,'lbu a4, -2(a0)'),(0x431e8,'li a5, 255'),(0x431d8,'li a0, 5'),(0x431f4,'li a0, 4'),(0x43200,'li a0, 0')]:at(pc,text)
    for pc,word in [(0x20000278,0xa142),(0x2000027a,0xa17c)]:need(int.from_bytes(bytes.fromhex(ops[pc]['bytes']),'little')==word and ops[pc]['conditional_Xwchc'],'Exact reviewed vendor word')
    zero_stores={0x20000248,0x431ca};restore_stores={0x20000252,0x2000027c,0x20000284,0x431d4,0x431f0,0x43202}
    for pc in restore_stores:at(pc,'sw s2, 524(s1)'if pc>=0x20000000 else'sw s1, 524(s0)')
    graphs=[];calls=[]
    for f in EV['selected_functions']:
        local={o['addr']:o for o in f['operations']};pending=[(f['start'],False)];seen=set();rets=[]
        while pending:
            pc,restored=pending.pop()
            if (pc,restored)in seen:continue
            need(pc in local,'Every CFG position is an actual whole candidate instruction');seen.add((pc,restored));o=local[pc]
            if pc in zero_stores:restored=False
            if pc in restore_stores:restored=True
            if o['opcode']=='ret':rets.append(dict(PC=pc,local_restore_store_seen=restored));continue
            after=pc+o['size'];decoded=B['decode_control'](bytes.fromhex(o['bytes']),pc)
            if pc==0x431fc:
                pair=S['PC_relative_pairs'][0];need(pair['PC']==0x431f8 and pair['target_PC']==0x20000110,'One statically resolved far heap call')
                calls.append(dict(PC=pc,target_PC=pair['target_PC'],kind='AUIPC-JALR',callee_body_provided=False));nexts=[after]
            elif decoded:
                kind,target=decoded;v=int.from_bytes(bytes.fromhex(o['bytes']),'little');call=(kind==17 and(v>>7)&31!=0)or(kind==45 and(v>>13)&7==1)
                if kind in [16,44]:nexts=[target,after]
                elif call:
                    need(target==0x20000040,'Actual unresolved near heap helper');calls.append(dict(PC=pc,target_PC=target,kind='direct',callee_body_provided=False));nexts=[after]
                else:nexts=[target]
            else:nexts=[after]
            for nxt in nexts:need(nxt in local,'No local sequential,branch or normal-return-position gap');pending.append((nxt,restored))
        need({pc for pc,state in seen}==set(local)and rets and all(v['local_restore_store_seen']for v in rets),'All candidate instructions traversed;every local normal return has an explicit restore store')
        graphs.append(dict(start=f['start'],end=f['end'],instructions=len(local),return_paths=rets,local_CFG_positions_closed_assuming_calls_return=True,physical_restoration_guaranteed=False))
    need(len(calls)==2 and {v['target_PC']for v in calls}=={0x20000040,0x20000110},'Two genuine unresolved heap callees only')
    other='analysis/wch-resident-candidate-2026-10-21/carrier/REFERENCE-CANDIDATE-ONLY-00040000-0006EC56.bin'
    need(sha(ROOT/other)=='b02cf8ec6829425a558887bd6bc10d28ae1f0e2e9e1850333f0bab6088e9e941','Pinned V1.40 public comparison carrier')
    raw=(ROOT/other).read_bytes();entry=json.loads((ROOT/'analysis/wch-resident-candidate-2026-10-21/resident-entry/contract.json').read_bytes())['entry']['raw_operands']
    need((entry['copy1_source'],entry['copy1_destination'])==(0x402f0,0x20000040),'Separate V1.40 conditional RAM-copy mapping')
    def word(pc):return int.from_bytes(raw[pc-0x40000:pc-0x40000+4],'little')
    need(word(0x40070)==0x20000236 and word(0x40068)==0x43246,'Actual V1.40 API slot values')
    alloc40_start=0x402f0+(0x20000236-0x20000040);allocate40=raw[alloc40_start-0x40000:alloc40_start-0x40000+86]
    allocate31=N['original'](0x20000236,0x2000028c);need(allocate40==allocate31,'All86 allocation bytes agree after each version-specific conditional mapping')
    free31=N['original'](0x431ba,0x43208);free40=raw[0x43246-0x40000:0x43246-0x40000+78]
    normalized=[]
    for start,body in [(0x431ba,free31),(0x43246,free40)]:
        need(len(body)==78,'Whole corresponding deallocation candidate');pc=start+62;hi=int.from_bytes(body[62:66],'little');lo=int.from_bytes(body[66:70],'little')
        need(hi&0xfff==0x97 and lo&0xfffff==0x80e7,'Same real AUIPC/JALR register fields')
        imm=lo>>20;imm-=4096 if imm&2048 else 0;need((pc+(hi&0xfffff000)+imm)&0xffffffff==0x20000110,'Both far calls target the same numeric RAM helper')
        b=bytearray(body);b[62:66]=(hi&0xfff).to_bytes(4,'little');b[66:70]=(lo&0xfffff).to_bytes(4,'little');normalized.append(bytes(b))
    need(normalized[0]==normalized[1],'All78 free bytes equal modulo the single original-VA far-call encoding')
    return dict(schema='TSL9-public-SDK-message-API-audit-v1',passed=True,SDK_candidate_only=True,
        native_results=native,local_CFG=graphs,heap_calls=calls,caller_contract=saved['caller_contract'],
        SDK_version_comparison=dict(V131_carrier=EV['carrier'],V131_carrier_sha256=EV['carrier_sha256'],V140_carrier=other,V140_carrier_sha256=sha(ROOT/other),
            slot_40070_target_both=0x20000236,V131_allocation_source=0x404a6,V140_allocation_source=alloc40_start,allocation86_bytes_equal=True,
            slot_40068_V131_target=0x431ba,slot_40068_V140_target=0x43246,deallocation78_bytes_equal_modulo_one_far_call=True,deallocation_raw_bytes_equal=free31==free40,
            helper_implementations_compared=False,installed_resident_identity_proved=False),
        limits=dict(physical_Xwchc_profile_proved=False,installed_ROM_identity_proved=False,heap_helpers_provided=False,global_heap_or_IRQ_ownership_proved=False,
            actual_original_address_link_performed=False,APP_byte_coverage_unchanged=95.54,APP_source_C_H_files_unchanged=159,linked_into_APP=False,new_BIN=False,firmware_ready=False),
        target_executed=False,HOST_model_executed=False,ISA_emulated=False,hardware_accessed=False,network=False)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--tool-dir',type=Path,required=True);p.add_argument('--output',type=Path);a=p.parse_args()
    try:
        result=audit(a.tool_dir.resolve())
        if a.output:
            out=a.output if a.output.is_absolute()else HERE/a.output
            need(out.resolve().parent==HERE and not out.exists(),'Create-only experiment receipt');out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
        print(json.dumps(dict(passed=True,CODE_bytes=164,instructions=62,local_CFG_bodies=len(result['local_CFG']),SDK_version_comparison=result['SDK_version_comparison'],limits=result['limits'])))
    except Exception as error:
        message=str(error)
        for path,token in [(ROOT,'${PROJECT_ROOT}'),(Path.home(),'${USERPROFILE}')]:message=message.replace(str(path),token).replace(path.as_posix(),token)
        print(json.dumps(dict(passed=False,error_type=type(error).__name__,reason=message)));raise SystemExit(1)
