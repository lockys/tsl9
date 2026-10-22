#!/usr/bin/env python3
"""Original TX entry/restore source obligations, not a replacement admission test."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
FW='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
RAW='da17e505ec2b58cada40a80a12a645b7fa21c116ce76666544168f2c4ff6c6a7'
OLD_SEAL='46da5762a0bc46c15a04ad6b2bf0f890a001de66b8ac006d0c507529505d76e2'
def need(v,m):
    if not v:raise ValueError(m)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_bytes())
def old_scope(root):return next(p for p in (root/'apk-analysis/tsl9-v4160-ota-tx-2026-10-22',root/'analysis/v4160-ota-tx-2026-10-22') if p.is_dir())
def load(p):
    spec=importlib.util.spec_from_file_location('TX_existing_static_decoder',p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def signature(row):return tuple(row[k] for k in ('op','rd','rs1','rs2','immediate','target','memory_width'))
def frontiers(rows):
    r={v['PC']:v for v in rows}
    expected={
        0x8a56:('addi',15,0,None,1039,None,None),
        0x8a5a:('bltu',None,15,13,None,0x8b6c,None),
        0x8a5e:('addi',2,2,None,-32,None,None),
        0x8a60:('sw',None,2,8,24,None,32),
        0x8a62:('sw',None,2,9,20,None,32),
        0x8a64:('sw',None,2,18,16,None,32),
        0x8a66:('sw',None,2,19,12,None,32),
        0x8a68:('sw',None,2,1,28,None,32),
        0x8a6a:('lhu',14,3,None,150,None,16),
        0x8b26:('lw',1,2,None,28,None,32),
        0x8b28:('lw',9,2,None,20,None,32),
        0x8b2a:('lw',18,2,None,16,None,32),
        0x8b2c:('lw',19,2,None,12,None,32),
        0x8b32:('sh',None,15,8,2,None,16),
        0x8b36:('sh',None,15,0,4,None,16),
        0x8b40:('lw',8,2,None,24,None,32),
        0x8b46:('lw',6,15,None,80,None,32),
        0x8b4a:('lbu',10,12,None,0,None,8),
        0x8b4e:('addi',2,2,None,32,None,None),
        0x8b50:('jalr',0,6,None,0,None,None),
        0x8b6c:('jalr',0,1,None,0,None,None)}
    for pc,v in expected.items():need(pc in r and signature(r[pc])==v,'Original entry/frame/restore boundary '+hex(pc))
    early=[v for v in rows if v['PC']<0x8a5e]
    need(not any(v['memory_width'] or v['rd']==2 for v in early),'No stack/memory effects on oversized path')
    return {'guard_PC':0x8a5a,'first_SP_write_PC':0x8a5e,'first_GP_read_PC':0x8a6a,'success_head_restores':[0x8b26,0x8b28,0x8b2a,0x8b2c],'metadata_writes':[0x8b32,0x8b36],'success_S0_restore_PC':0x8b40,'tail_slot_read_PC':0x8b46,'tail_handle_read_PC':0x8b4a,'tail_PC':0x8b50,'source_boundary_fields_checked':len(expected)}
def controls(raw,body):
    def mutate(pc,fn):
        b=bytearray(body);row=raw.decode(body[pc-0x8a56:],pc);n=row['bytes'];w=int.from_bytes(b[pc-0x8a56:pc-0x8a56+n],'little');b[pc-0x8a56:pc-0x8a56+n]=fn(w).to_bytes(n,'little');return bytes(b)
    shifted=body[8:12]+body[0:8]+body[12:]
    late=body[:0xd0]+body[0xd2:0xe4]+body[0xd0:0xd2]+body[0xe4:]
    candidates=[('guard_limit1038',mutate(0x8a56,lambda w:w-(1<<20))),
        ('frame_before_guard',shifted),('swap_save_S0_S1',body[:10]+body[12:14]+body[10:12]+body[14:]),
        ('late_RA_restore',late),('metadata_SW_width',mutate(0x8b36,lambda w:(w&~0x7000)|0x2000)),
        ('S0_wrong_restore_slot',mutate(0x8b40,lambda w:0x4472)),('tail_writes_link',mutate(0x8b50,lambda w:w^0x1000))]
    result=[]
    for name,b in candidates:
        need(len(b)==280 and b!=body,'Bounded actual-byte mutation')
        try:frontiers(raw.rows(b))
        except ValueError as error:result.append({'case':name,'rejected':True,'reason':str(error)})
        else:raise ValueError('Boundary mutation accepted '+name)
    return result
def alias_witness():
    base=0x2000b18c;sp=0x2000b170;before=0x12340003;n=1
    need(sp%16==0 and sp+28==base and (base+2)==sp+30,'Aligned stack interval witness')
    late=(before&65535)|(((n+6)&65535)<<16)
    need(late==0x00070003 and late!=before,'Independent halfword overwrite algebra')
    return {'base':base,'live_SP':sp,'entry_SP_if_unchanged':sp+32,'SP_alignment':16,'saved_RA_address':sp+28,'original_RA_read_before_metadata':before,'stable_post_gate_length':n,'first_metadata_address':base+2,'first_metadata_width':2,'first_metadata_value':n+6,'late_RA_word_after_metadata':late,'actual_runtime_reachability_proved':False,'instruction_execution':False}
def candidate_source(root):
    old=root/'experiments/tsl9-v4160-ota-tx/src';new=root/'experiments/tsl9-v4160-tx-register-abi/src'
    expected=(old/'tx_native.c').read_text(encoding='utf-8')
    changes=[('if(result==accepted) {lane=TX_LANE2(0u);','if(TX_EXPECT(result==accepted,0)) {lane=TX_LANE2(0u);'),('if(result!=accepted) {TX_RESTORE_FAILURE();','if(TX_EXPECT(result!=accepted,1)) {TX_RESTORE_FAILURE();')]
    for before,after in changes:
        need(expected.count(before)==1,'Unique comparison-only source delta')
        expected=expected.replace(before,after)
    need((new/'tx_native.c').read_text(encoding='utf-8')==expected,'Only two comparison branch hints in shared algorithm')
    relative='../../tsl9-v4160-ota-tx/src/host_io.h'
    header=(old/'tx_native.h').read_text(encoding='utf-8').replace('"host_io.h"','"'+relative+'"')
    need((new/'tx_native.h').read_text(encoding='utf-8')==header,'Public header only changes immutable HOST include path')
    io=(old/'tx_io.h').read_text(encoding='utf-8')
    before='#include "host_io.h"\n#else\n'
    after='#include "'+relative+'"\n#define TX_EXPECT(value,expectation) (value)\n#else\n#define TX_EXPECT(value,expectation) __builtin_expect(!!(value),(expectation))\n'
    need(io.count(before)==1 and (new/'tx_io.h').read_text(encoding='utf-8')==io.replace(before,after),'Only HOST identity/native expect macros and immutable HOST include')
    return {'comparison_only_hint_count':2,'HOST_hint_macro_is_identity':True,'old_HOST_provider_reused':True,'fresh_HOST_tests_run':False,'native_prefix_equivalence_proved':False}
def adapter_source(root,texts=None):
    base=root/'experiments/tsl9-v4160-tx-register-abi';folder=base/'adapter'
    source=texts or {n:(folder/n).read_text(encoding='utf-8') for n in ('entry.S','valid_body.c','return_leaf.c')}
    expected_entry='''/* Narrow returning entry adapter; all body logic is compiled typed C/C++. */
.section .text.tsl9_tx_entry,"ax",@progbits
.p2align 1
.globl tsl9_ota_tx_8a56
.type tsl9_ota_tx_8a56,@function
tsl9_ota_tx_8a56:
    li a5,1039
.Ltx_guard_branch:
    bltu a5,a3,0
    .reloc .Ltx_guard_branch,R_RISCV_BRANCH,tsl9_tx_oversized_return
.size tsl9_ota_tx_8a56,.-tsl9_ota_tx_8a56
'''
    need(source['entry.S']==expected_entry,'Exactly two mnemonic entry operations; no SP/A0/RA destination, raw code, alias or padding')
    expected=(base/'src/tx_native.c').read_text(encoding='utf-8')
    edits=[('#include "tx_native.h"','#include "../src/tx_native.h"'),('#include "tx_io.h"','#include "../src/tx_io.h"'),('tx_return tsl9_ota_tx_8a56(','static __attribute__((used,noinline,section(".text.tsl9_tx_valid_body"))) tx_return tsl9_tx_valid_body('),('uint32_t limit,gp,','uint32_t gp,'),('    limit=TX_LIMIT5();\n    if(length>limit)TX_RETURN_LARGE(context);\n','')]
    for before,after in edits:
        need(expected.count(before)==1,'Unique valid-only typed body extraction')
        expected=expected.replace(before,after)
    need(source['valid_body.c']==expected,'Valid-only body changes only includes/name/guard extraction, not typed algorithm')
    expected_leaf='''#include <stdint.h>
#ifdef __cplusplus
extern "C"
#endif
__attribute__((noinline,section(".text.tsl9_tx_oversized_return")))
uint32_t tsl9_tx_oversized_return(uint32_t context,uint32_t command,uint32_t source,uint32_t length)
{
    (void)command;(void)source;(void)length;
    return context;
}
'''
    need(source['return_leaf.c']==expected_leaf,'Actual typed identity-return leaf, no assembly/noreturn/unreachable')
    return {'mnemonic_entry_operations':2,'explicit_standard_branch_relocation':1,'valid_body_has_no_duplicate_guard':True,'body_is_exact_typed_extraction':True,'leaf_is_true_C_identity_return':True,'returning_signature_preserved':True,'source_raw_code_or_padding':False,'machine_fallthrough_and_return_leaf_still_require_actual_artifact':True,'full_original_ABI_admitted':False}
def adapter_controls(root):
    import copy
    folder=root/'experiments/tsl9-v4160-tx-register-abi/adapter';texts={n:(folder/n).read_text(encoding='utf-8') for n in ('entry.S','valid_body.c','return_leaf.c')};adapter_source(root,texts)
    cases=[('hidden_entry_stack','entry.S','    li a5,1039\n','    addi sp,sp,-16\n    li a5,1039\n'),('wrong_unsigned_guard','entry.S','bltu a5,a3,','bgeu a5,a3,'),('entry_changes_link','entry.S','    li a5,1039\n','    jal ra,tsl9_tx_oversized_return\n    li a5,1039\n'),('normalized_oversize_return','return_leaf.c','return context;','return 0u;'),('changed_typed_stride','valid_body.c','packet=TX_PACKET5(record,base);','packet=TX_PACKET5(record+2u,base);')]
    result=[]
    for name,member,before,after in cases:
        changed=copy.deepcopy(texts);need(changed[member].count(before)==1,'Unique bounded source control');changed[member]=changed[member].replace(before,after)
        try:adapter_source(root,changed)
        except ValueError as error:result.append({'case':name,'rejected':True,'reason':str(error),'compiled':False})
        else:raise ValueError('Adapter source control admitted '+name)
    return result
def entry_leaf_fields(raw,entry,leaf,entry_PC,leaf_PC,placeholder=False):
    need(len(entry)==8 and len(leaf)==2,'Exact entry8 and typed return2, no expanded trampoline')
    first=raw.decode(entry,entry_PC);guard=raw.decode(entry[4:],entry_PC+4);ret=raw.decode(leaf,leaf_PC)
    need(signature(first)==('addi',15,0,None,1039,None,None),'Only initial A5 limit; A0/RA/SP untouched')
    need(signature(guard)==('bltu',None,15,13,None,entry_PC+4 if placeholder else leaf_PC,None),'Exact unsigned A5<A3, standard branch target')
    need(signature(ret)==('jalr',0,1,None,0,None,None),'Typed leaf is only RET; no A0/SP/new link writes')
    return {'entry_bytes':8,'leaf_bytes':2,'guard_PC':entry_PC+4,'guard_target':guard['target'],'oversized_A0_RA_SP_unchanged':True,'entry_memory_accesses':0,'new_link_written':False}
def inspect_adapter(root,folder):
    scope=old_scope(root);raw=load(scope/'source-review/raw.py')
    parser=next(p for p in (root/'apk-analysis/tsl9-v4160-irq-native-2026-10-21/compiler-review/elf32.py',root/'analysis/v4160-irq-native-2026-10-21/compiler-review/elf32.py') if p.is_file())
    need(sha(parser)=='00a231e3bbd881a9961c12fefd15565364cd813250a46a7b20851a6b9f3a2141','Immutable existing ELF field parser')
    ELF=load(parser).ELF;folder=Path(folder).resolve();e=ELF(folder/'entry.o');body=ELF(folder/'valid_body.o');leaf=ELF(folder/'return_leaf.o');linked=ELF(folder/'COMPONENT-ONLY-NOT-FIRMWARE.elf')
    def only_code(obj,size):
        sections=[s for s in obj.sections if s['flags']&2 and s['size']]
        need(obj.kind==1 and obj.flags==1 and len(sections)==1 and sections[0]['size']==size and sections[0]['flags']==6 and sections[0]['alignment']==2,'One typed/entry actual AX allocation')
        functions=[s for s in obj.symbols if s['info']&15==2]
        need(len(functions)==1 and functions[0]['value']==0 and functions[0]['size']==size,'Honest actual one-function extent')
        return sections[0],functions[0],obj.function_bytes(functions[0])
    es,ef,eb=only_code(e,8);bs,bf,bb=only_code(body,270);ls,lf,lb=only_code(leaf,2)
    need(ef['name']=='tsl9_ota_tx_8a56' and ef['info']==18 and lf['name']=='tsl9_tx_oversized_return' and lf['info']==18,'Public real entry8 and typed real leaf2 symbols')
    need(len(e.relocations)==1,'Exactly one standard entry RELA')
    rel=e.relocations[0]
    need(rel['owner']==es['name'] and rel['offset']==4 and rel['type']==16 and rel['addend']==0 and rel['symbol']['name']==lf['name'],'Entry R_RISCV_BRANCH at+4 targets actual typed leaf')
    entry_leaf_fields(raw,eb,lb,0,0,True)
    alloc=[s for s in linked.sections if s['flags']&2 and s['size']]
    need(linked.kind==2 and linked.flags==1 and len(alloc)==1 and alloc[0]['address']==0x8a56 and alloc[0]['size']==280 and alloc[0]['flags']==6 and not linked.relocations,'Actual bounded280 linked component, no gaps/additional allocations')
    functions=[s for s in linked.symbols if s['info']&15==2]
    need(sorted((s['value'],s['size']) for s in functions)==[(0x8a56,8),(0x8a5e,270),(0x8b6c,2)],'Entry fallthrough/body/return adjacency and truthful sizes')
    image=linked.data(alloc[0]);fields=entry_leaf_fields(raw,image[:8],image[-2:],0x8a56,0x8b6c)
    need(eb[:4]==image[:4] and lb==image[-2:],'Entry limit and C leaf actual bytes retained')
    need(bb[:0x78]==image[8:8+0x78] and bb[0x80:]==image[8+0x80:-2],'Pre-motion typed body differs at only its PCREL address pair')
    need([(r['offset'],r['type']) for r in body.relocations]==[(0x78,23),(0x7c,24)],'Actual typed-body PCREL pair only')
    need(body.relocations[0]['symbol']['name']=='__tsl9v4160_data_2000b18c' and all(r['addend']==0 for r in body.relocations),'Real symbolic RAM role, not fabricated provider')
    hi=raw.decode(image[0x80:],0x8ad6);lo=raw.decode(image[0x84:],0x8ada)
    need(hi['op']=='auipc' and hi['rd']==13 and lo['op']=='addi' and lo['rd']==lo['rs1']==13 and (hi['PC']+hi['immediate']+lo['immediate'])&0xffffffff==0x2000b18c,'Linked PCREL target numeric SRAM witness only')
    need(not any(s['index']==0 and s['name'] for s in linked.symbols),'No unresolved component symbols')
    need(raw.decode(image[8:],0x8a5e)['rd']==2,'First stack operation occurs only on valid fallthrough')
    text=(folder/'return_leaf.ll').read_text(encoding='utf-8');need('ret i32 %0' in text and 'noreturn' not in text and 'unreachable' not in text,'Actual typed identity-return IR remains truthful')
    negatives=[]
    changes=[('limit1038',0,1<<20),('signed_guard',4,1<<13),('guard_wrong_target',4,1<<8),('entry_limit_writes_A0',0,5<<7)]
    for name,offset,xor in changes:
        mutant=bytearray(image[:8]);w=int.from_bytes(mutant[offset:offset+4],'little')^xor;mutant[offset:offset+4]=w.to_bytes(4,'little')
        try:entry_leaf_fields(raw,bytes(mutant),image[-2:],0x8a56,0x8b6c)
        except ValueError as error:negatives.append({'case':name,'actual_code_bytes_mutated':True,'rejected':True,'reason':str(error)})
        else:raise ValueError('Entry byte control accepted '+name)
    try:entry_leaf_fields(raw,image[:8],(int.from_bytes(image[-2:],'little')^0x1000).to_bytes(2,'little'),0x8a56,0x8b6c)
    except ValueError as error:negatives.append({'case':'typed_leaf_changes_link','actual_code_bytes_mutated':True,'rejected':True,'reason':str(error)})
    else:raise ValueError('Leaf link control accepted')
    return {'passed':True,'actual_pre_motion_adapter_subset_replayed':True,'actual_compile_recipe_replayed':False,'entry_leaf':fields,'component_bytes':280,'typed_body_bytes':270,'public_FUNC_bytes':8,'numeric_RAM_witness_only':True,'whole_original_FUNC_role_admitted':False,'original_success_restore_order_admitted':False,'full_original_ABI_admitted':False,'actual_code_byte_controls':negatives,'actual_files':{n:sha(folder/n) for n in ('entry.o','valid_body.o','return_leaf.o','return_leaf.ll','COMPONENT-ONLY-NOT-FIRMWARE.elf')},'target_execution':False}
def inspect(root,firmware,adapter_folders=()):
    scope=old_scope(root);old=scope/'source-review';need(sha(old/'seal.json')==OLD_SEAL and sha(old/'raw.py')==RAW,'Immutable original source proof/decoder')
    for n,pin in read(old/'seal.json')['members'].items():need(sha(old/n)==pin,'Original sealed member '+n)
    need(sha(firmware)==FW,'Exact original ID2966 firmware');body=firmware.read_bytes()[0xa56:0xb6e];raw=load(old/'raw.py');rows=raw.validate(body);f=frontiers(rows);negative=controls(raw,body)
    if (HERE/'source-review.json').exists():
        selected=read(HERE/'source-review.json')
        for name,pin in selected['reference_C_sources'].items():need(sha(root/name)==pin,'Unchanged old readable source '+name)
        need(selected['source_frontiers']==f and selected['raw_boundary_controls']==negative and selected['aligned_alias_witness']==alias_witness(),'Exact selected raw source/frontier/control readback')
        if 'candidate_source_pins' in selected:
            for name,pin in selected['candidate_source_pins'].items():need(sha(root/name)==pin,'Candidate source identity '+name)
            need(candidate_source(root)==selected['candidate_source_delta'],'Exact source delta and HOST identity expansion')
        if 'adapter_source_pins' in selected:
            for name,pin in selected['adapter_source_pins'].items():need(sha(root/name)==pin,'Narrow adapter source identity '+name)
            need(adapter_source(root)==selected['adapter_source_contract'] and adapter_controls(root)==selected['adapter_source_controls'],'Narrow adapter exact source contract and controls')
    if (HERE/'seal.json').exists():
        for n,pin in read(HERE/'seal.json')['members'].items():need(sha(HERE/n)==pin,'Immutable source-contract review '+n)
    actual=[inspect_adapter(root,p) for p in adapter_folders]
    return {'passed':True,'source_bytes':280,'source_instructions':96,'frontiers':f,'raw_boundary_controls':negative,'aligned_alias_witness':alias_witness(),'replacement_admission_checker':False,'compiled_C_CPP_tested':False,'ordinary_C_ABI_proved':False,'actual_native_artifacts_replayed':bool(actual),'actual_pre_motion_adapter_subsets':actual,'target_execution':False,'ISA_emulation':False,'hardware':False,'OTA_ready':False}
def main():
    p=argparse.ArgumentParser();p.add_argument('--project-root',type=Path,required=True);p.add_argument('--firmware',type=Path,required=True);p.add_argument('--adapter-folder',type=Path,action='append',default=[]);a=p.parse_args();print(json.dumps(inspect(a.project_root.resolve(),a.firmware.resolve(),a.adapter_folder)))
if __name__=='__main__':main()
