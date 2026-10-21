"""ID2966 original flash/OTA route, static raw/ELF evidence only."""
from pathlib import Path
import hashlib,importlib.util,json,runpy,struct,subprocess,sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;W=HERE.parents[2];ROOT=W/'experiments/tsl9-v4160-startup';SHA=lambda b:hashlib.sha256(b).hexdigest()
BASE=ROOT/'build/data-anchor-extension-ecb8f64d6d3640f2b8d2d6f6f6ad776e/verification.json';BASE_SHA='df90a9590431a62c937231117675a308feac9887a9aebce5825ee9bc76d86c09'
FW=W/'exports/TSL-firmware-options-22-BINs-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin';FW_SHA='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
OLD=W/'apk-analysis/tsl9-function-hardware/candidate-ota-compatibility/receiver-review/review.json'

def main():
    assert SHA(BASE.read_bytes())==BASE_SHA;baseline=json.loads(BASE.read_text());raw=FW.read_bytes();assert SHA(raw)==FW_SHA and len(raw)==76800
    host=runpy.run_path(str(ROOT/'verify.py'));ELF=host['ELF'];dt=runpy.run_path(str(ROOT/'verify-dependencies.py'))['direct_target'];alloc=baseline['allocations'];assert len(alloc)==614
    decoder=W/'apk-analysis/tsl9-v4160-platform-2026-10-20/vector-review/review-vectors.py';sp=importlib.util.spec_from_file_location('flash_route_flow',decoder);flow=importlib.util.module_from_spec(sp);sp.loader.exec_module(flow);flow.B=raw
    def containing(pc):return[dict(section=n,**a)for n,a in alloc.items()if a['originalVA']<=pc<a['originalVA']+a['bytes']]
    modes={};allrefs=None
    for mode in('c','cpp'):
        e=ELF(Path(baseline['modes'][mode]['integrated_object']));w=ELF(BASE.parent/mode/'ADDRESS-WITNESS-ONLY.elf');assert SHA(e.raw)==baseline['modes'][mode]['integrated_sha256']and len(e.relocations)==7238
        und={n:w.symbol[n]['value']for n in baseline['modes'][mode]['undefined_symbols']}
        def normal(r):
            s=e.symbols[r['symbol_index']]
            if s['index']==0:return(und[s['name']]if s['name']else 0)+r['addend']
            if s['index']==0xfff1:return s['value']+r['addend']
            return alloc[e.sections[s['index']]['name']]['originalVA']+s['value']+r['addend']
        refs=[dict(sourcePC=alloc[r['section']]['originalVA']+r['offset'],type=r['type'],target=normal(r),symbol=r['target'],addend=r['addend'],section=r['section'])for r in e.relocations]
        for r in refs:
            if r['type']in(16,17,44,45):
                pc=r['sourcePC'];half=int.from_bytes(raw[pc-0x8000:pc-0x8000+2],'little');width=4 if half&3==3 else 2;v=int.from_bytes(raw[pc-0x8000:pc-0x8000+width],'little');assert dt(pc,width,v)[1]==r['target']
        if allrefs is None:allrefs=refs
        else:assert refs==allrefs
        modes[mode]=dict(actual_object_sha256=SHA(e.raw),allocations=614,RELA=7238,UND=len(und))
    targets=[0x18e90,0x18e98,0x18eb6,0x18ec4,0x18ef2,0x197be,0x9c0a,0x9c4a,0x14056]
    actual_boundaries=set()
    for a in alloc.values():
        if a['kind']!='code':continue
        pc=a['originalVA'];end=pc+a['bytes']
        while pc<end:
            actual_boundaries.add(pc);width,_,_,_=flow.flow(pc);pc+=width
        assert pc==end
    rawhits={t:[]for t in targets}
    for off in range(0,len(raw)-3,2):
        half=int.from_bytes(raw[off:off+2],'little');width=4 if half&3==3 else 2;v=int.from_bytes(raw[off:off+width],'little');x=dt(off+0x8000,width,v)
        if x and x[1]in rawhits:rawhits[x[1]].append(dict(sourcePC=off+0x8000,type=x[0],bytes=width,raw_hex=raw[off:off+width].hex(),source_currently_captured=bool(containing(off+0x8000)),actual_captured_instruction_boundary=off+0x8000 in actual_boundaries))
    # These are exact actual old-code calls plus the newly identified uncaptured
    # raw route. All selected source rows below are independently checked by r2.
    expected={0x18e90:[0x9c26],0x18e98:[0x9c1e,0x197c8],0x18eb6:[0x9c38,0x197dc],0x18ec4:[0x9c2c,0x197ce],0x18ef2:[0x9c34,0x197d8],0x197be:[],0x9c0a:[0x9d00,0x9e7a,0x12e7a,0x12f0c,0x12f6e,0x13078,0x130fc,0x1315e],0x9c4a:[0x14094],0x14056:[0x8a48]}
    confirmed={t:[r for r in hits if r['actual_captured_instruction_boundary']or r['sourcePC']in(0x9d00,0x14094,0x8a48)]for t,hits in rawhits.items()}
    for t,pcs in expected.items():assert [r['sourcePC']for r in confirmed[t]]==pcs,(hex(t),confirmed[t])
    nodes={};todo=[0x9c4a]
    while todo:
        pc=todo.pop()
        if pc in nodes:continue
        assert 0x8000<=pc<0x8000+len(raw)and len(nodes)<40000
        width,kind,edges,call=flow.flow(pc);assert kind not in('unsupported_or_invalid','exception_instruction')
        nodes[pc]=dict(va=pc,bytes=width,raw_hex=raw[pc-0x8000:pc-0x8000+width].hex(),flow=kind,successors=edges,call=call);todo.extend(edges)
    assert set(v for pc,n in nodes.items()for v in range(pc,pc+n['bytes']))==set(range(0x9c4a,0x9e5c))
    slices=[(0x9c0a,64),(0x9c4a,530),(0x197be,50),(0x14056,100),(0x888c,58),(0x89f6,90),(0x8fbc,18),(0x92f2,66),(0x18e90,198)]
    command=[str(flow.R2),'-n','-q','-a','riscv','-b','32','-m','0x8000'];contexts=[]
    for pc,count in slices:command+=['-c',f'pDj {count} @ {pc}']
    run=subprocess.run(command+['-c','q',str(FW)],capture_output=True,text=True,encoding='utf-8',timeout=90);assert run.returncode==0
    rows={}
    for (start,size),line in zip(slices,[x for x in run.stdout.splitlines()if x.strip()]):
        decoded=json.loads(line);assert sum(n['size']for n in decoded)==size
        for n in decoded:
            pc=n['addr'];assert n['bytes']==raw[pc-0x8000:pc-0x8000+n['size']].hex()and'invalid'not in n['opcode'];rows[pc]=dict(PC=pc,bytes=n['size'],raw_hex=n['bytes'],disassembly=n['opcode'])
        contexts.append(dict(start=start,bytes=size,instructions=[rows[n['addr']]for n in decoded]))
    for pc,n in nodes.items():assert rows[pc]['bytes']==n['bytes'];n['disassembly']=rows[pc]['disassembly']
    w32=lambda pc:int.from_bytes(raw[pc-0x8000:pc-0x8000+4],'little')
    sext=lambda v,n:v-(1<<n)if v&(1<<(n-1))else v
    imm=lambda pc:sext(w32(pc)>>20,12)
    ci=lambda pc:sext(((int.from_bytes(raw[pc-0x8000:pc-0x8000+2],'little')>>12)&1)<<5|((int.from_bytes(raw[pc-0x8000:pc-0x8000+2],'little')>>2)&31),6)
    assert imm(0x9ca2)==1026 and w32(0x9ca2)&127==0x13
    upper=w32(0x9cb2)&0xfffff000;ch=int.from_bytes(raw[0x9cbc-0x8000:0x9cbe-0x8000],'little');cimm=sext(((ch>>12)&1)<<5|((ch>>2)&31),6);assert upper==0x20000 and cimm==4
    subtract=w32(0x9cc2)&0xfffff000;cl=int.from_bytes(raw[0x9cc6-0x8000:0x9cc8-0x8000],'little');limit=(sext(((cl>>12)&1)<<5|((cl>>2)&31),6)<<12)+imm(0x9cca)
    assert subtract==0xf7fff000 and limit==0x6f00
    pages=[p for p in range(65536)if((((upper+cimm+p)<<10)+subtract)&0xffffffff)<=limit];assert pages==list(range(28))
    assert dt(0x9cce,4,w32(0x9cce))==(16,0x9c7a)and(w32(0x9cce)>>12)&7==6
    assert imm(0x9cfc)==256 and imm(0x9cf0)==1024 and dt(0x9d00,2,int.from_bytes(raw[0x9d00-0x8000:0x9d02-0x8000],'little'))==(45,0x9c0a)
    assert dt(0x9d18,4,w32(0x9d18))==(16,0x9e52)and imm(0x9e52)==255
    assert ci(0x9e00)==15 and dt(0x9e02,4,w32(0x9e02))==(16,0x9c7a)
    assert ci(0x9dce)==16 and ci(0x9e0e)==14
    assert int.from_bytes(raw[0x19e00-0x8000:0x19e04-0x8000],'little')==0x888c
    assert any(r['sourcePC']==0x8fbc and r['type']==23 and r['target']==0x19dfc for r in allrefs)
    old=json.loads(OLD.read_text());oldruntime=next(r for r in old['source_hashes']if r['path'].endswith('TSL9-runtime-api-payload.bin'));assert oldruntime['sha256']=='32639d7d6df2abac1b966a72de663dc1c215165edf4f4ee0b58acc78e0f60bcc'and oldruntime['sha256']!=FW_SHA
    oldfile=Path(oldruntime['path']);oldraw=oldfile.read_bytes();assert SHA(oldraw)==oldruntime['sha256']
    old_command=[str(flow.R2),'-n','-q','-a','riscv','-b','32','-m','0x8000','-c','pDj 62 @ 0x9d38','-c','q',str(oldfile)]
    older=subprocess.run(old_command,capture_output=True,text=True,encoding='utf-8',timeout=60);assert older.returncode==0;oldE=json.loads(older.stdout)
    for n in oldE:assert n['bytes']==oldraw[n['addr']-0x8000:n['addr']-0x8000+n['size']].hex()
    assert [n['opcode']for n in oldE[:4]]==['lbu a5, 177(gp)','beqz a5, 0x9bd0','li a3, 0','li a2, 200']
    assert not any(n['opcode'].startswith(('lbu ','lhu '))for n in oldE[2:])
    assert not any(n['opcode'].startswith(('beq ','bne ','beqz ','bnez '))for n in oldE[2:])
    result=dict(schema='ID2966-V4160-original-OTA-flash-reachability-v1',passed=True,source=dict(path=str(FW),sha256=FW_SHA,bytes=len(raw),model_base=0x8000),baseline_receipt=dict(path=str(BASE),sha256=BASE_SHA),modes=modes,actual_reference_count=7238,selected_actual_references={hex(t):[r for r in allrefs if r['target']==t]for t in targets},all_image_aligned_raw_direct_target_candidates={hex(t):r for t,r in rawhits.items()},confirmed_raw_direct_calls={hex(t):r for t,r in confirmed.items()},unverified_or_rejected_aligned_raw_candidates={hex(t):[r for r in rawhits[t]if r not in confirmed[t]]for t in targets},all_confirmed_raw_calls_checked_against_raw_rows_or_actual_RELA_boundaries=True,handler=dict(entry=0x9c4a,end_exclusive=0x9e5c,bytes=530,instruction_count=len(nodes),instructions=[nodes[pc]for pc in sorted(nodes)],current_native_storage_available=False),upstream=dict(record_base=0x19dfc,record_pointer_offset=4,record_pointer_word_PC=0x19e00,raw_pointer_word_sha256=SHA(raw[0x19e00-0x8000:0x19e04-0x8000]),conditional_GATT_write_entry=0x888c,original_record_consumption_by_resident_ABI_proved=False,record_argument_materialization=0x8fbc,record_argument_register=13,nominal_registration_slot=0x40130,registration_call_PC=0x8fcc,frame_parser_callPC=0x8a48,data_dispatch_entry=0x14056,OTA_callPC=0x14094,dispatcher_W_selector_PC=0x140b2,dispatcher_W_branch_PC=0x140b6,upstream_raw_code_captured_in_baseline=False),W_contract=dict(command=0x57,selector_PC=0x9c94,selector_branch_PC=0x9c98,active_RAM_numeric_address=0x20004000+169,active_load_PC=0x9c9c,active_gate_PC=0x9ca0,payload_length=1026,length_constant_PC=0x9ca2,length_gate_PC=0x9ca6,page_u16_big_endian_PCs=[0x9caa,0x9cae,0x9cb6,0x9cb8],formula='((0x20004 + page_u16) << 10) modulo 2^32',destination_base=0x08001000,page_stride=1024,accepted_page_min=0,accepted_page_max=27,maximum_end_exclusive=0x08008000,guard_unsigned_offset_limit=0x6f00,guard_PC=0x9cce,all65536_u16_pages_checked=True,source_pointer='align_down(payload+2,4); if unaligned, opaque slot4004C copy1024 into aligned pointer',copy_call_PC=0x9cec,program_callPC=0x9d00,program_helper=0x9c0a,program_iteration_offsets=[0,256,512,768],program_loop_end=1024,readback_width=4,readback_offsets=list(range(0,1024,4)),readback_load_PCs=[0x9d10,0x9d16],readback_mismatch_branch_PC=0x9d18,mismatch_result_constant_PC=0x9e52,mismatch_result=255,page_ACK_setup_PCs=[0x9d22,0x9d24,0x9d28],page_ACK_response_call_PC=0x9df4,page_ACK_response_helper=0x9b8e,actual_data_and_ACK_transmission_unknown=True),wrapper=dict(entry=0x9c0a,bytes=64,existing_real_provider='__tsl9v4160_call_9c0a',interrupt_CSR=0x800,mask=0x88,disable_PC=0x9c1a,enable_PC=0x9c3c,status_clear_argument=0x31,call_chain=[dict(sourcePC=0x9c1e,target=0x18e98),dict(sourcePC=0x9c26,target=0x18e90),dict(sourcePC=0x9c2c,target=0x18ec4),dict(sourcePC=0x9c34,target=0x18ef2),dict(sourcePC=0x9c38,target=0x18eb6)],actual_MMIO_completion_and_hardware_success_proved=False),SNV_like_conditional_record_hook=dict(entry=0x197be,actual_direct_callers=[],original_record_materialization_PC=0x19a80,original_record_identity_remains_UND=True,same_as_GATT_OTA_handler=False,status_clear18e90_call_absent=True),new_E_contract=dict(active_required=True,length=15,length_constant_PC=0x9e00,length_gate_PC=0x9e02,mode0_gate_PC=0x9e0a,identity_helper=0x92f2,identity_call_PC=0x9e14,identity_return0_match_gate_PC=0x9e18,clear_active_PC=0x9e2c,scheduled_delay_values=[200,400],scheduler_calls=[0x9e30,0x9e44],empty_response_setup_PC=0x9e48),R_contract=dict(command=0x52,active_required=True,length=16,identity_pointer='payload+2',identity_bytes=14,identity_call_PC=0x9dda,page_big_endian=True,response_helper=0x9b8e,response_payload_bytes=1026),previous_receiver_review=dict(path=str(OLD),sha256=SHA(OLD.read_bytes()),reviewed_different_runtime_sha256=oldruntime['sha256'],old_PC_addresses_not_reused_as_proof=True),raw_r2_contexts=contexts,r2=dict(path=str(flow.R2),sha256=SHA(flow.R2.read_bytes()),command=command),actual_identifiers_read_or_printed=False,arbitrary_resident_dispatch_or_GATT_registration_ABI_proved=False,target_ready=False,ota_verified=False,physical_flash_alias_proved=False,network=False,target_execution=False,emulation=False,hardware=False,ROOT_written=False,D_written=False,native_BIN=False)
    result['old_vs_ID2966_E_byte_evidence']=dict(old_source=dict(path=str(oldfile),sha256=SHA(oldraw)),old_active_only_region_start=0x9d38,old_region_bytes=62,old_region_sha256=SHA(oldraw[0x9d38-0x8000:0x9d76-0x8000]),old_instructions=[dict(PC=n['addr'],bytes=n['size'],raw_hex=n['bytes'],disassembly=n['opcode'])for n in oldE],new_E_extra_length_mode_and_identity_gates=True,new_old_code_not_interchangeable=True)
    pdir=HERE.parent/'protocol-review';ppins={'review-protocol.py':'a09084d4b93a417ff431a9edfb47b4dfb4d59b2a295d02e065203bb2c5890443','review.json':'9a66b861219b9d0b2307f5968bd5e44081e40ccb48600ca397713485145d0564'}
    for name,digest in ppins.items():assert SHA((pdir/name).read_bytes())==digest
    result['independent_protocol_pins']=[dict(path=str(pdir/n),sha256=h)for n,h in ppins.items()]
    encoded=json.dumps(result,indent=2)+'\n'
    if '--check'in sys.argv:assert(HERE/'flash-route.json').read_text()==encoded
    else:(HERE/'flash-route.json').write_text(encoded)
    print(json.dumps(dict(passed=True,source='ID2966',handler='9C4A',handler_bytes=530,helper='9C0A',actual614_has_handler=False,W_pages=[0,27],destination='08001000',program_calls=4,E_length=15,new_native_generated=False)))

if __name__=='__main__':main()
