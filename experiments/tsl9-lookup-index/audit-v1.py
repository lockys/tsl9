#!/usr/bin/env python3
"""Read-only provenance audit over original selected CODE; never execute a firmware/model."""
from pathlib import Path
from collections import Counter
import argparse,hashlib,json,runpy,sys
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent

def need(ok,message):
    if not ok:raise ValueError(message)

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def sx(v,n):return v-(1<<n)if v&(1<<(n-1))else v

def audit():
    spec=json.loads((HERE/'spec-v1.json').read_bytes())
    need(sha(ROOT/spec['evidence'])==spec['evidence_sha256'],'Exact captured original evidence')
    evidence=json.loads((ROOT/spec['evidence']).read_bytes())
    need(all(sha(ROOT/p)==h for p,h in evidence['inputs'].items()),'Exact selected native source/layout/flow inputs')
    fw=(ROOT/evidence['firmware']).read_bytes()
    need(len(fw)==76800 and sha(ROOT/evidence['firmware'])==evidence['firmware_sha256'],'Exact original official firmware')
    b=runpy.run_path(str(ROOT/evidence['layout_builder']),run_name='selected_CODE_library')
    need(all(sha(ROOT/p)==pin for p,pin in b['K']['pins'].items()),'All transitive selected-layout source/proof inputs')
    need(sha(ROOT/b['K']['reader'])==b['K']['reader_sha256'],'Pinned native ELF reader')
    component=b['E'](b['source']('c'));plan=b['derive'](component);linked=b['E'](ROOT/evidence['original_layout'])
    insns={};selected_bytes=0
    for owner in plan['owners']:
        if owner['info']!=18:continue
        raw=linked.data(owner['section'])[owner['section_offset']:owner['section_offset']+owner['bytes']]
        pc=owner['original_PC']
        need(raw==fw[pc-0x8000:pc-0x8000+owner['bytes']],'Every selected CODE byte equals the original BIN')
        selected_bytes+=len(raw);at=0
        while at<len(raw):
            width=4 if raw[at]&3==3 else 2
            need(at+width<=len(raw)and pc+at not in insns,'Whole unique original instruction')
            insns[pc+at]=dict(width=width,raw=raw[at:at+width],owner=owner['name']);at+=width
    need(len(insns)==21938 and selected_bytes==64544,'Exact selected CODE audit scope')
    captured={};captured_count=0
    for window in evidence['captured_CODE_windows']:
        pc=window['start']
        for operation in window['operations']:
            need(operation['addr']==pc and pc in insns and operation['size']==insns[pc]['width']and bytes.fromhex(operation['bytes'])==insns[pc]['raw'],'Fresh r2 evidence is within selected original CODE')
            if pc in captured:need(captured[pc]==operation,'Consistent overlapping instruction captures')
            captured[pc]=operation;pc+=operation['size'];captured_count+=1
        need(pc==window['end'],'Complete bounded disassembly window')
    need(captured_count==174,'All captured original instructions')
    def word(pc):return int.from_bytes(insns[pc]['raw'],'little')
    def fields(pc):
        w=word(pc);return w&127,(w>>7)&31,(w>>12)&7,(w>>15)&31,(w>>20)&31,sx(w>>20,12)
    def pc_pair(hi,lo,reg):
        a,c=word(hi),word(lo)
        need(insns[hi]['width']==insns[lo]['width']==4 and a&0x7f==0x17 and(a>>7)&31==reg,'Actual selected AUIPC register')
        need(c&0x707f==0x13 and(c>>7)&31==(c>>15)&31==reg,'Actual selected ADDI pair register')
        return (hi+(a&0xfffff000)+sx(c>>20,12))&0xffffffff
    def cli(pc,rd,imm):
        w=word(pc);need(insns[pc]['width']==2 and w&0xe003==0x4001 and(w>>7)&31==rd and sx((((w>>12)&1)<<5)|((w>>2)&31),6)==imm,'Actual compressed LI operand')
    def caddi(pc,rd,imm):
        w=word(pc);need(insns[pc]['width']==2 and w&0xe003==1 and(w>>7)&31==rd and sx((((w>>12)&1)<<5)|((w>>2)&31),6)==imm,'Actual compressed ADDI operand')
    stores=[];loads=[];addresses=[];dynamic_gp=[]
    for pc,instruction in sorted(insns.items()):
        if instruction['width']!=4:continue
        opcode,rd,kind,rs1,rs2,imm=fields(pc)
        if opcode==0x23 and rs1==3:
            size={0:1,1:2,2:4}.get(kind);offset=sx(((word(pc)>>25)<<5)|((word(pc)>>7)&31),12)
            if size and offset<=176<offset+size:stores.append(dict(PC=pc,bytes=size,offset=offset,source_register=rs2,owner=instruction['owner']))
        if opcode==3 and rs1==3 and imm==176:loads.append(dict(PC=pc,destination_register=rd,load_kind=kind))
        if opcode==0x13 and kind==0 and rs1==3:addresses.append(dict(PC=pc,destination_register=rd,GP_offset=imm))
        if opcode==0x33 and 3 in (rs1,rs2):dynamic_gp.append(pc)
    need([r['PC']for r in stores]==[0xa0fa,0xa344]and all(r['bytes']==1 and r['source_register']==15 for r in stores),'Exactly two selected direct GP stores overlap this byte')
    need([r['PC']for r in loads]==[0xa0f2,0xa146,0xa33a]and all(r['load_kind']==4 for r in loads),'Three selected unsigned-byte reads of GP+176')
    need(len(addresses)==185 and not dynamic_gp,'Selected literal GP address materialization inventory')
    gp_initializers=[v for v in addresses if v['destination_register']==3]
    need(len(gp_initializers)==1,'One selected GP self-ADDI initializer')
    gp_low=gp_initializers[0]['PC'];gp=pc_pair(gp_low-4,gp_low,3)
    zero_end=pc_pair(0x186e2,0x186e6,11)
    need(gp==0x20004000 and zero_end==0x2000c958 and fields(0x186de)==(0x13,10,0,3,0,128),'Actual GP setup and zero-loop source/end operands')
    need(word(0x186ee)==0x00052023,'Original SW ZERO,0(A0) zeroing store')
    caddi(0x186f2,10,4)
    need(b['B']['decode_control'](insns[0x186ea]['raw'],0x186ea)==(16,0x186f8)and fields(0x186ea)[2:5]==(7,10,11),'Original zero-loop entry bound')
    need(b['B']['decode_control'](insns[0x186f4]['raw'],0x186f4)==(16,0x186ee)and fields(0x186f4)[2:5]==(6,10,11),'Original zero-loop word iteration bound')
    need((gp+128)%4==zero_end%4==0 and gp+128<=gp+176<zero_end,'Index byte is covered by original aligned zeroing path')
    flow=json.loads((ROOT/evidence['flow']).read_bytes());writers=[]
    for load,increment,mask,store in [(0xa0f2,0xa0f6,0xa0f8,0xa0fa),(0xa33a,0xa33e,0xa340,0xa344)]:
        need(fields(load)==(3,15,4,3,16,176),'Actual LBU A5,176(GP)')
        caddi(increment,15,1);w=word(mask)
        need(insns[mask]['width']==2 and w&0xec03==0x8801 and 8+((w>>7)&7)==15 and sx((((w>>12)&1)<<5)|((w>>2)&31),6)==3,'Actual C.ANDI A5,3')
        if store==0xa344:need(word(0xa342)==0x4422,'Intervening stack reload writes S0,not A5')
        incoming=[d['PC']for d in flow['direct_transfers']if mask<d['target_PC']<=store]
        need(not incoming,'No selected direct transfer bypasses the mask into this writer tail')
        writers.append(dict(load_PC=load,increment_PC=increment,mask_PC=mask,store_PC=store,post_value_minimum=0,post_value_maximum=3,selected_direct_mask_bypasses=incoming,all_indirect_entry_or_async_paths_proved=False))
    # Exact syntactic lookup, with no local index mask at its read site.
    need(fields(0xa146)==(3,15,4,3,16,176),'Actual unsigned-byte lookup index')
    need(word(0xa14a)==0x00179713,'Actual SLLI A4,A5,1')
    table=pc_pair(0xa14e,0xa152,15);need(table==0x1ab48,'Actual original halfword table address')
    need(word(0xa156)==0x97ba and fields(0xa158)==(3,15,5,15,0,0),'Actual scaled address addition and LHU')
    # The indirect reset overlaps the byte, but its ROM identity is not proved.
    need(fields(0xa37c)[:2]==(0x37,15)and word(0xa37c)&0xfffff000==0x40000,'Actual literal resident table base')
    need(fields(0xa380)==(3,6,2,15,8,72),'Actual LW T1,72(A5) slot')
    cli(0xa384,12,5);cli(0xa386,11,0)
    need(fields(0xa388)==(0x13,10,0,3,12,172)and word(0xa38c)==0x8302,'Actual destination GP+172 and tail transfer through T1')
    sdk=evidence['cached_SDK_reference'];slot=sdk['default_base']+sdk['table_offset']+sdk['memset_index']*sdk['stride']
    need(slot==0x40048,'Cached default SDK slot arithmetic matches the original slot load')
    escapes=[v for v in addresses if v['GP_offset']==128 and v['destination_register']==11]
    need([v['PC']for v in escapes]==[0x86cc,0x87c0,0x8a8a,0x8aae,0x8fb0],'Five selected GP+128 pointer arguments')
    # The apparent table-state getter is NOT the scheduled sequence consumer.
    w=word(0xef6c);need(w&0xfff==0x517 and fields(0xef70)==(3,10,4,10,0,32)and word(0xef74)==0x8082,'Three-instruction status-byte getter')
    getter_address=(0xef6c+(w&0xfffff000)+32)&0xffffffff;need(getter_address==0x2000bf8c,'Actual getter RAM byte')
    target=pc_pair(0xefe0,0xefe4,10);self_target=pc_pair(0xee8c,0xee90,10)
    need(target==self_target==0xee30,'Actual selected initial and repeated callback address literals')
    need(b['B']['decode_control'](insns[0xee54]['raw'],0xee54)==(16,0xee7e)and fields(0xee54)[2:5]==(6,15,14),'Actual unsigned counter-less-than-limit guard')
    need(fields(0xee40)==(3,15,5,15,8,328)and fields(0xee48)==(3,14,5,14,2,322),'Actual halfword counter and limit loads')
    counter=(0xee3c+(word(0xee3c)&0xfffff000)+328)&0xffffffff;limit=(0xee44+(word(0xee44)&0xfffff000)+322)&0xffffffff
    need(counter==0x2000bf84 and limit==0x2000bf86,'Original sequence RAM fields')
    need(word(0xee7e)==0x4058 and word(0xee80)==0x0786 and word(0xee84)==0x97ba and fields(0xee86)==(3,12,5,15,0,0),'Pointer at counter+4,index shifted1,and unsigned halfword source read')
    cli(0xefbc,15,17)
    wide_limit=fields(0xf008)
    need(insns[0xf008]['width']==4 and wide_limit[0:4]==(0x13,15,0,0)and wide_limit[5]==53,'Actual full-width LI A5,53')
    sequences=[]
    for hi,lo,n in [(0xefac,0xefb0,17),(0xefee,0xeff2,17),(0xeff8,0xeffc,53)]:
        start=pc_pair(hi,lo,15);sequences.append(dict(source_start=start,configured_limit=n,conditional_maximum_index=n-1,conditional_read_bytes=2*n,conditional_end=start+2*n,original_declared_extent_proved=False,source_DATA_provided=False))
    need([v['source_start']for v in sequences]==[0x1a430,0x1a454,0x1a478],'Actual three sequence source address literals')
    return dict(passed=True,schema='TSL9-lookup-index-audit-v1',selected_CODE_bytes=selected_bytes,selected_instructions=len(insns),captured_instructions=captured_count,direct_GP176_writers=writers,direct_GP176_reads=loads,GP_ADDI_materializations=addresses,GP_ADDI_offset_counts={str(k):v for k,v in sorted(Counter(v['GP_offset']for v in addresses).items())},dynamic_GP_R_type_uses=dynamic_gp,
        lookup=dict(base=table,index_bits=8,index_scale_bytes=2,read_bytes=2,local_mask_present=False,byte_only_syntactic_index_maximum=255,byte_only_syntactic_envelope_bytes=512,byte_only_syntactic_envelope_end=table+512,image_end=0x1ac00,index_zero_to_three_proved_for_all_runtime_paths=False,conditional_four_entry_window_bytes=8,conditional_four_entry_window_end=table+8,source_DATA_provided=False),
        indirect_reset=dict(wrapper_PC=0xa37c,slot_load_PC=0xa380,slot_address=slot,destination_GP_offset=172,length_argument=5,value_argument=0,conditional_memset_end_GP_offset=177,index_byte_overlapped=True,cached_SDK_default_formula_matches=True,installed_ROM_identity_or_ABI_proved=False,conditional_effect='If this installed slot obeys the cached SDK tmos_memset contract,it writes zero to GP+176'),
        unresolved_pointer_escapes=escapes,all_alias_writers_or_opaque_side_effects_closed=False,
        startup_zeroing=dict(GP=gp,GP_pair_high_PC=gp_low-4,GP_pair_low_PC=gp_low,zero_start=gp+128,zero_end=zero_end,index_byte_address=gp+176,index_byte_is_zero_after_this_coded_startup_path=True,installed_startup_and_ROM_side_effects_proved=False),
        sequence=dict(scheduled_callback_literal=target,repeated_callback_literal=self_target,counter_address=counter,limit_address=limit,pointer_address=counter+4,load_guard_PC=0xee54,halfword_read_PC=0xee86,configured_source_profiles=sequences,all_runtime_pointer_limit_correlations_proved=False,former_candidate_ef6c_is_consumer=False,status_getter=dict(entry=0xef6c,read_address=getter_address,read_bytes=1),physical_feature_name_proved=False),
        known_initialization_and_masked_writers_suggest_four_states=True,unconditional_global_index_bound_proved=False,provided_data_bytes=0,coverage_added=0,firmware_BIN_generated=False,firmware_ready=False,target_executed=False,HOST_model_executed=False,ISA_emulated=False,hardware_accessed=False,network=False)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--full',action='store_true');a=p.parse_args()
    try:
        r=audit()
        print(json.dumps(r if a.full else dict(passed=r['passed'],selected_CODE_bytes=r['selected_CODE_bytes'],selected_instructions=r['selected_instructions'],captured_instructions=r['captured_instructions'],masked_direct_writers=len(r['direct_GP176_writers']),indirect_reset_slot=r['indirect_reset']['slot_address'],unresolved_GP128_pointer_escapes=len(r['unresolved_pointer_escapes']),global_index_bound_proved=False,sequence_callback=r['sequence']['scheduled_callback_literal'],provided_data_bytes=0,firmware_ready=False)))
    except (ValueError,OSError)as e:
        print(json.dumps(dict(passed=False,reason=str(e).replace(str(ROOT),'PROJECT_ROOT').replace(str(Path.home()),'USERPROFILE'))));sys.exit(1)
