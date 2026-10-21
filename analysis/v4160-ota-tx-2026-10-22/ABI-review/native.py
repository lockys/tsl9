#!/usr/bin/env python3
"""Static component checks and explicit original-ABI rejection ledger; no execution."""
import argparse,hashlib,json,re,runpy,struct,sys
from collections import Counter
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
RAW='da17e505ec2b58cada40a80a12a645b7fa21c116ce76666544168f2c4ff6c6a7'
ENTRY=0x8a56
NAME='tsl9_ota_tx_8a56'
def need(v,m):
    if not v:raise ValueError(m)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def H(b):return hashlib.sha256(b).hexdigest()
def context(root,firmware):
    original=runpy.run_path(str(HERE/'original.py'));original['inspect'](root,firmware);ELF,helper=original['helpers'](root);path=original['case'](root,'v4160-ota-tx-2026-10-22')/'source-review/raw.py';need(sha(path)==RAW,'Pinned independent original operand decoder');raw=runpy.run_path(str(path));body=firmware.read_bytes()[ENTRY-0x8000:0x8b6e-0x8000];raw['validate'](body);return dict(ELF=ELF,helper=helper,raw=raw,original=body)
def rows(body,c):
    out=[];offset=0
    while offset<len(body):
        payload=body[offset:];width=4 if int.from_bytes(payload[:2],'little')&3==3 else 2;need(offset+width<=len(body),'Whole actual native instruction');word=int.from_bytes(payload[:width],'little')
        if width==4 and word&127==0x63 and (word>>12)&7==7:
            # BGEU has the same immediate/register fields as BLTU; decode fields,
            # then retain the actual reversed condition and actual input bytes.
            r=c['raw']['decode']((word^(1<<12)).to_bytes(4,'little'),ENTRY+offset);r.update(op='bgeu',raw_hex=payload[:4].hex())
        else:r=c['raw']['decode'](payload,ENTRY+offset)
        r['offset']=offset;out.append(r);offset+=r['bytes']
    need(offset==len(body),'All actual native bytes decoded without ISA execution');return out
def one(rules,predicate,message):
    found=[r for r in rules if predicate(r)];need(len(found)==1,message);return found[0]
def kernel(rules):
    limit=one(rules,lambda r:r['op']=='addi' and (r['rd'],r['rs1'],r['immediate'])==(15,0,1039),'One actual1039 limit inA5');guard=one(rules,lambda r:r['op']=='bltu' and(r['rs1'],r['rs2'])==(15,13),'Actual full32 unsigned entrylength guard');frame=one(rules,lambda r:r['op']=='addi' and(r['rd'],r['rs1'],r['immediate'])==(2,2,-32),'Actual32B frame')
    gates=[r for r in rules if r['op']=='jalr' and(r['rd'],r['rs1'])==(1,15)];need(len(gates)==2,'Two opaque gate calls with actualRA links');slots=[r for r in rules if r['op']=='lw' and(r['rd'],r['rs1'],r['immediate'])==(15,15,316)];need(len(slots)==2,'Two fresh32-bit gate pointer reads')
    desc=one(rules,lambda r:r['op']=='sh' and(r['rs1'],r['rs2'],r['immediate'])==(15,0,4),'ActualdescriptorSHzero atoffset4');tail_slot=one(rules,lambda r:r['op']=='lw' and(r['rd'],r['rs1'],r['immediate'])==(6,15,80),'Fresh terminalROM+50 pointer read');task=one(rules,lambda r:r['op']=='lbu' and(r['rd'],r['rs1'],r['immediate'])==(10,12,0),'Terminaltask LBUthroughA2');tail=one(rules,lambda r:r['op']=='jalr' and(r['rd'],r['rs1'])==(0,6),'No-link terminalJR T1')
    trunc=one(rules,lambda r:r['op']=='slli' and(r['rd'],r['rs1'],r['immediate'])==(10,11,16),'Guardcounter leftshift16');restore=one(rules,lambda r:r['op']=='srli' and(r['rd'],r['rs1'],r['immediate'])==(10,10,16),'Guardcounter logicalrightshift16');need(trunc['offset']<restore['offset'],'Actual low16 guard sequence');loop=one(rules,lambda r:r['op'] in('bltu','bgeu') and r['rs1']==10 and r['rs2'] in(8,17),'Actual counter comparison againstsourceS0 or cachedA7 diagnostic')
    bounds={r['PC'] for r in rules};edges=[]
    for row in rules:
        if row['target'] is not None:need(row['target'] in bounds,'Every actual localcontrol target is an internalinstructionboundary');edges.append(dict(site=row['PC'],op=row['op'],target=row['target']))
        if row['op']=='jalr' and row['rd']==1:need(row['PC']+row['bytes'] in bounds,'Every opaque callreturn is an internalinstructionboundary')
    hi=one(rules,lambda r:r['op']=='auipc' and r['rd']==13 and r['immediate']==0,'Actual unresolvedPCRELHI inA3');lo=one(rules,lambda r:r['offset']==hi['offset']+4 and r['op']=='addi' and(r['rd'],r['rs1'],r['immediate'])==(13,13,0),'Actual adjacent unresolvedPCRELLO inA3')
    need(all(r['memory_width']==32 for r in slots+[tail_slot]) and desc['memory_width']==16 and task['memory_width']==8,'Exact pointer/descriptor/task memorywidths');return dict(limit=limit,guard=guard,frame=frame,gates=gates,gate_slots=slots,descriptor_zero=desc,tail_slot=tail_slot,task_LBU=task,tail=tail,loop_guard=loop,RAM_PCREL_pair=[hi,lo],static_local_control_edges=edges)
def object_contract(e):
    need(e.kind==1 and e.flags==1,'Actual RVC soft-float ET_REL');symbol=one(e.symbols,lambda s:s['name']==NAME,'One actual nativeTX symbol');owner=e.sections[symbol['index']];need((symbol['value'],symbol['info'],symbol['other'])==(0,18,0) and symbol['size']==owner['size'] and(owner['type'],owner['flags'],owner['alignment'])==(1,6,2),'Actual whole nativeFUNC/AX owner extent');need([s['index'] for s in e.sections if s['flags']&2 and s['size']]==[owner['index']],'Component-only allocated extent')
    need([s['name'] for s in e.symbols if s['index']==0 and s['name']]==['__tsl9v4160_data_2000b18c'],'Sole unresolved original RAMalias');need(len(e.relocations)==2 and sorted(r['type'] for r in e.relocations)==[23,24],'Only actual PCRELHI/LO RAMaddress pair');hi=next(r for r in e.relocations if r['type']==23);lo=next(r for r in e.relocations if r['type']==24);need(hi['symbol']['name']=='__tsl9v4160_data_2000b18c' and hi['addend']==lo['addend']==0 and lo['owner']==hi['owner']==owner['name'] and lo['offset']==hi['offset']+4 and lo['symbol']['index']==owner['index'] and lo['symbol']['value']==hi['offset'],'Actual localpairedPCREL anchor, no fabricated RAMprovider');return symbol,owner
def ir_contract(text):
    calls=[line for line in text.splitlines() if 'asm sideeffect "jalr ra, $4, 0"' in line];need(len(calls)==2,'Two actual five-output opaque gate asm calls')
    for line in calls:
        for reg in(10,11,12,13,15):need('={x'+str(reg)+'}' in line,'Actualreadwriteopaque outputx'+str(reg))
        for reg in(1,14,16,17,5,6,7,28,29,30,31):need('~{x'+str(reg)+'}' in line,'Honest opaque callerclobberx'+str(reg))
    need(len(re.findall(r'musttail call (?:noundef )?i32 %\d+\(i32 noundef %\d+, i32 noundef %\d+, i32 noundef %\d+, i32 noundef %\d+\)',text))==1,'Four-register musttail adapter, not claimed actualROMsignature');return dict(opaque_gate_calls=2,gate_readwrite_GPRs=[10,11,12,13,15],four_argument_tail_adapter=True,resident_function_C_signature_proved=False)
def gaps(body,rules,facts,c):
    fallback=one(rules,lambda r:r['op']=='lhu' and(r['rd'],r['rs1'],r['immediate'])==(15,3,154),'Actual secondhandle LHU');second=facts['gates'][1];range_=[r for r in rules if fallback['offset']<=r['offset']<second['offset']];ambient=[r for r in range_ if r['rd'] in(12,13)];sentinel=[r for r in range_ if r['op']=='mv' and(r['rd'],r['rs1'])==(11,15)];a7=[r for r in rules if r['rd']==17];tail_region=[r for r in rules if r['offset']>facts['descriptor_zero']['offset'] and r['offset']<facts['tail']['offset']];restores=[r for r in tail_region if r['op']=='lw' and r['rs1']==2 and r['rd'] in(1,8,9,18,19)];before=[r for r in rules if facts['loop_guard']['target']<=r['PC']<facts['descriptor_zero']['PC'] and r['op']=='lw' and r['rs1']==2 and r['rd'] in(1,9,18,19)] if facts['loop_guard']['op']=='bgeu' else []
    fixes=[]
    if facts['guard']['offset']>facts['frame']['offset']:fixes.append('Restore pre-frame oversized early-return behavior')
    if ambient or sentinel or a7:fixes.append('Close the specifically recorded ambient/failure/tail register differences')
    if len(before)!=4 or any(r['rd']==8 and r['offset']>facts['tail_slot']['offset'] for r in restores):fixes.append('Restore source fresh-frame-read timing around descriptor writes and ROM pointer load')
    if len(body)>280:fixes.append('Fit original280B extent without padding or unowned storage')
    fixes.append('Prove original interior/control/return boundaries before wholeimage replacement; size equality alone is insufficient')
    return dict(original_extent_bytes=280,actual_native_bytes=len(body),extra_bytes=len(body)-280,fits_original_extent=len(body)<=280,whole_original_instruction_stream_equal=body==c['original'],entryguard_precedes_frame=facts['guard']['offset']<facts['frame']['offset'],source_gate1_offset=0x38,actual_gate1_offset=facts['gates'][0]['offset'],source_gate2_offset=0x5e,actual_gate2_offset=second['offset'],second_gate_A2_A3_not_overwritten=len(ambient)==0,fallback_A2_A3_writes=ambient,sentinel_failure_A1_extra_writes=sentinel,source_loop_compares_liveS0=facts['loop_guard']['rs2']==8,actual_loop_length_GPR=facts['loop_guard']['rs2'],extra_local_A7_writes=a7,source_restore_RA_S1_S2_S3_before_descriptor=len(before)==4,actual_late_stack_restores=restores,source_S0_restore_precedes_ROMtail_load=any(r['rd']==8 and r['offset']<facts['tail_slot']['offset'] for r in restores),original_ABI_admitted=False,original_280B_placement_admitted=False,next_required_fixes=fixes,conditional_normal_C_ABI_only=True,arbitrary_saved_frame_alias_or_interrupt_equivalence=False)
def inventory(rules,c):
    def signature(r):
        immediate=r['immediate']
        if r['op']=='auipc' and r['rd']==13:immediate='PCREL_HI'
        if r['op']=='addi' and(r['rd'],r['rs1'])==(13,13):immediate='PCREL_LO'
        return json.dumps([r['op'],r['rd'],r['rs1'],r['rs2'],immediate,r['memory_width']])
    a=Counter(map(signature,c['raw']['validate'](c['original'])));b=Counter(map(signature,rules));return dict(source_instruction_count=sum(a.values()),native_instruction_count=sum(b.values()),branch_destinations_and_PCREL_immediates_normalized=True,shape_inventory_matches_after_limited_normalization=a==b,original_only_shapes=[dict(shape=json.loads(s),count=n) for s,n in(a-b).items()],native_only_shapes=[dict(shape=json.loads(s),count=n) for s,n in(b-a).items()],existing_word_permutation_only_admitted=False)
def controls(body,c):
    results=[];r=rows(body,c);k=kernel(r)
    tests=[('gate_no_RA_link',k['gates'][0]['offset'],2,0x1000),('counter_not_low16',one(r,lambda x:x['op']=='srli' and(x['rd'],x['rs1'],x['immediate'])==(10,10,16),'Countertruncationrow')['offset'],2,4),('descriptor_not_zero',k['descriptor_zero']['offset'],4,10<<20),('tail_reads_word_not_byte',k['task_LBU']['offset'],4,6<<12),('tail_creates_RA',k['tail']['offset'],2,0x1000),('wrong_RAM_PCREL_GPR',k['RAM_PCREL_pair'][0]['offset'],4,128),('guard_jumps_outside_component',k['guard']['offset'],4,1<<31)]
    for name,at,n,mask in tests:
        b=bytearray(body);w=int.from_bytes(b[at:at+n],'little')^mask;b[at:at+n]=w.to_bytes(n,'little')
        try:kernel(rows(bytes(b),c))
        except ValueError as error:results.append(dict(name=name,actual_native_bytes_mutated=True,offset=at,original_hex=body[at:at+n].hex(),mutated_hex=bytes(b[at:at+n]).hex(),rejected=True,reason=str(error)));continue
        raise ValueError('Incorrect structural/effectsubset operand admitted:'+name)
    return results
def inspect_native(root,folder,firmware):
    c=context(root,firmware);e=c['ELF'](folder/'tx_native.o');symbol,owner=object_contract(e);body=e.function_bytes(symbol);r=rows(body,c);k=kernel(r);ir=(folder/'tx_native.ll').read_text(encoding='utf8');result=dict(schema='TSL9-TX-native-static-gap-review-v1',review_completed=True,actual_artifacts_read=True,checked_subset_passed=True,original_ABI_admitted=False,object_sha256=H(e.raw),body_sha256=H(body),bytes=len(body),instructions=len(r),rows=r,checked_subset=k,IR=ir_contract(ir),gap_ledger=gaps(body,r,k,c),normalized_instruction_inventory=inventory(r,c),operand_controls=controls(body,c),firmware_sha256=sha(firmware),target_execution=False,ISA_emulation=False,network=False,hardware_OTA_proved=False)
    probe=folder/'probe.json'
    if probe.is_file():result['probe_sha256']=sha(probe);result['draft_source_pins']=json.loads(probe.read_bytes()).get('source_before_after',{})
    return result
def main():
    p=argparse.ArgumentParser();p.add_argument('--project-root',type=Path,required=True);p.add_argument('--folder',type=Path,required=True);p.add_argument('--firmware',type=Path,required=True);p.add_argument('--report',type=Path,required=True);a=p.parse_args();r=inspect_native(a.project_root.resolve(),a.folder.resolve(),a.firmware.resolve());need(not a.report.exists(),'Create-only ABI rejection/evidence report');a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_bytes((json.dumps(r,ensure_ascii=False,indent=2)+'\n').encode());print(json.dumps(dict(review_completed=True,checked_subset_passed=True,original_ABI_admitted=False,bytes=r['bytes'],original_extent_fits=r['gap_ledger']['fits_original_extent'],operand_controls=len(r['operand_controls']))))
if __name__=='__main__':main()
