#!/usr/bin/env python3
"""Independent actual 8B entry + typed body + real returning-leaf audit."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import runpy
import sys

sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent


def need(value,message):
    if not value:
        raise ValueError(message)


def H(payload):
    return hashlib.sha256(payload).hexdigest()


def entry_object(e,n,context):
    need(e.kind==1 and e.flags==1,'Actual standalone RVC entry ET_REL')
    symbol=n['one'](e.symbols,lambda s:s['name']=='tsl9_ota_tx_8a56','Actual entry symbol')
    owner=e.sections[symbol['index']]
    need((symbol['value'],symbol['size'],symbol['info'],symbol['other'])==(0,8,18,0),
         'Honest public entry FUNC8, not fabricated aggregate FUNC280')
    need((owner['type'],owner['flags'],owner['alignment'],owner['size'])==(1,6,2,8),'Actual entry AX8')
    need([s['index'] for s in e.sections if s['flags']&2 and s['size']]==[owner['index']],
         'Only actual entry bytes allocated')
    body=e.function_bytes(symbol)
    rows=n['rows'](body,context)
    need(len(rows)==2 and rows[0]['op']=='addi' and
         (rows[0]['rd'],rows[0]['rs1'],rows[0]['immediate'])==(15,0,1039), 'Actual A5 entry limit')
    need(rows[1]['op']=='bltu' and(rows[1]['rs1'],rows[1]['rs2'])==(15,13),
         'Actual single 4B unsigned branch, no expanded BGEU/JAL')
    need(len(e.relocations)==1,'Exactly one real entry relocation')
    rela=e.relocations[0]
    need((rela['owner'],rela['offset'],rela['type'],rela['addend'])==(owner['name'],4,16,0) and
         rela['symbol']['name']=='tsl9_tx_oversized_return' and rela['symbol']['index']==0,
         'Actual standard R_RISCV_BRANCH at +4 targets the real typed return provider')
    return symbol,body


def linked_contract(e,entry,valid,leaf,n,context):
    need(e.kind==2 and e.flags==1 and not e.relocations,'Actual resolved linked RVC component')
    selected=[]
    expected=[('tsl9_ota_tx_8a56',0x8a56,8,18),
              ('tsl9_tx_valid_body',0x8a5e,270,2),
              ('_ZL18tsl9_tx_valid_bodyjjjj',0x8a5e,270,2),
              ('tsl9_tx_oversized_return',0x8b6c,2,18)]
    for names in [('tsl9_ota_tx_8a56',),('tsl9_tx_valid_body','_ZL18tsl9_tx_valid_bodyjjjj'),
                  ('tsl9_tx_oversized_return',)]:
        s=n['one'](e.symbols,lambda x:x['name'] in names,'One actual linked component role')
        target=next(t for t in expected if t[0]==s['name'])
        need((s['value'],s['size'],s['info'],s['other'])==(target[1],target[2],target[3],0),
             'Honest linked entry/body/leaf sizes and adjacent addresses')
        selected.append(s)
    need(len({s['index'] for s in selected})==1,'Actual fallthrough functions share one contiguous owner')
    owner=e.sections[selected[0]['index']]
    need((owner['type'],owner['flags'],owner['alignment'],owner['address'],owner['size'])==
         (1,6,2,0x8a56,280),'Aggregate allocated extent280, distinct from entry FUNC8')
    need([s['index'] for s in e.sections if s['flags']&2 and s['size']]==[owner['index']],
         'No extra allocated component storage')
    need(not [s for s in e.symbols if s['index']==0 and s['name']],'No unresolved component provider')
    provider=n['one'](e.symbols,lambda s:s['name']=='__tsl9v4160_data_2000b18c','Numeric RAM witness')
    need(provider['index']==0xfff1 and provider['value']==0x2000b18c,'Numeric ABS RAM witness only')
    body=e.data(owner)
    need(body[:4]==entry[:4] and body[-2:]==leaf and leaf==bytes.fromhex('8280'),
         'Entry literal and real typed RET leaf retain their actual source bytes')
    all_rows=n['rows'](body,context)
    guard=all_rows[1]
    need(guard['op']=='bltu' and(guard['rs1'],guard['rs2'],guard['target'])==(15,13,0x8b6c),
         'Linked unsigned branch actually targets the typed RET at8B6C')
    gates=[r for r in all_rows if r['op']=='jalr' and(r['rd'],r['rs1'])==(1,15)]
    need([(r['PC'],r['PC']+r['bytes']) for r in gates]==[(0x8a8e,0x8a90),(0x8ab4,0x8ab6)],
         'Both actual linked opaque call sites and RA continuations are source-exact')
    hi=n['one'](all_rows,lambda r:r['op']=='auipc' and r['rd']==13,'Linked actual RAM HI in A3')
    lo=n['one'](all_rows,lambda r:r['offset']==hi['offset']+4 and r['op']=='addi' and
                (r['rd'],r['rs1'])==(13,13),'Linked actual paired RAM LO in A3')
    need((hi['PC']+hi['immediate']+lo['immediate'])&0xffffffff==0x2000b18c,
         'Actual linked PCREL pair resolves to the original numeric RAM target')
    linked_valid=bytearray(body[8:278])
    for r in (hi,lo):
        offset=r['offset']-8
        linked_valid[offset:offset+4]=valid[offset:offset+4]
    need(bytes(linked_valid)==valid,'All body bytes outside actual RAM relocation pair equal supplied typed object')
    need(all_rows[-1]['op']=='jalr' and(all_rows[-1]['rd'],all_rows[-1]['rs1'])==(0,1),
         'Real oversized leaf returns without a new RA or frame effects')
    return dict(entry_bytes=8,typed_body_bytes=270,typed_return_bytes=2,allocated_bytes=280,
                entry_FUNC_bytes=8,aggregate_FUNC280_fabricated=False,
                fallthrough_address=0x8a5e,oversized_return_address=0x8b6c,
                opaque_gate_RAs=[0x8a90,0x8ab6],RAM_PCREL_target=0x2000b18c,
                actual_body_SHA256=H(body),oversized_path_no_frame_proved=True,
                new_T1_transfer_not_introduced=True,
                original_known_incoming_linked_here=False,private_original_roles_linked_here=False,
                full_pointwise_identity_proved=False,original_ABI_admitted=False)


def inspect(root,firmware,folder,body_object='valid_body.o',elf_name='COMPONENT-ONLY-NOT-FIRMWARE.elf',providers=None):
    p=runpy.run_path(str(HERE/'predicates.py'));n=p['prior'](root);context=n['context'](root,firmware)
    providers=folder if providers is None else providers
    entry=context['ELF'](providers/'entry.o');_,entry_bytes=entry_object(entry,n,context)
    typed=context['ELF'](folder/body_object)
    tail=runpy.run_path(str(HERE/'tail.py'));typed_facts=tail['contract'](typed,n,context)
    need(len(typed_facts['body'])==270,'Actual valid-only typed body270')
    leaf=context['ELF'](providers/'return_leaf.o')
    symbol=n['one'](leaf.symbols,lambda s:s['name']=='tsl9_tx_oversized_return','Actual compiled return leaf')
    need((symbol['value'],symbol['size'],symbol['info'],symbol['other'])==(0,2,18,0),
         'Actual returning typed leaf FUNC2')
    leaf_bytes=leaf.function_bytes(symbol)
    need(leaf_bytes==bytes.fromhex('8280'),'Compiler-emitted real RET identity leaf')
    leaf_ir=(providers/'return_leaf.ll').read_text(encoding='utf8')
    need(len(re.findall(r'^define ',leaf_ir,re.M))==1 and 'ret i32 %0' in leaf_ir and
         'i32 noundef returned %0, i32 noundef %1, i32 noundef %2, i32 noundef %3' in leaf_ir and
         not re.search(r'\b(call|asm)\b',leaf_ir),'Typed four-argument C return identity, not an unreachable surrogate')
    n['ir_contract']((providers/'valid_body.ll').read_text(encoding='utf8'))
    linked=context['ELF'](folder/elf_name)
    result=linked_contract(linked,entry_bytes,typed_facts['body'],leaf_bytes,n,context)
    controls=[]
    owner=next(s for s in linked.sections if s['flags']&2 and s['size'])
    for name,offset,mask in [('inverted_length_condition',owner['offset']+5,16),
                              ('branch_to_wrong_leaf',owner['offset']+4,128),
                              ('return_leaf_links_RA',owner['offset']+279,16)]:
        raw=bytearray(linked.raw);raw[offset]^=mask
        try:
            changed=context['ELF'](context['helper']['BytesInput'](bytes(raw)))
            linked_contract(changed,entry_bytes,typed_facts['body'],leaf_bytes,n,context)
        except ValueError as error:
            controls.append(dict(name=name,actual_linked_ELF_bytes_mutated=True,rejected=True,reason=str(error)))
        else:
            raise ValueError('Linked entry countercase admitted:'+name)
    return dict(schema='TSL9-TX-independent-narrow-entry-review-v1',
                actual_objects_IR_and_linked_ELF_read=True,checked_entry_prefix_passed=True,
                entry_object_sha256=H(entry.raw),supplied_body_object_sha256=H(typed.raw),
                supplied_body_object_name=body_object,
                body_ordering_provenance_requires_separate_pre_post_audit=True,
                leaf_object_sha256=H(leaf.raw),linked_ELF_sha256=H(linked.raw),
                actual_entry_RELA_count=1,actual_entry_RELA_type=16,
                contract=result,controls=controls,
                source_owned_assembly_layer_explicit=True,whole_algorithm_assembly=False,
                original_ABI_admitted=False,hardware_OTA_proved=False,
                target_execution=False,ISA_emulation=False)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--project-root',type=Path,required=True)
    parser.add_argument('--firmware',type=Path,required=True)
    parser.add_argument('--folder',type=Path,required=True)
    parser.add_argument('--body-object',default='valid_body.o')
    parser.add_argument('--elf-name',default='COMPONENT-ONLY-NOT-FIRMWARE.elf')
    parser.add_argument('--providers',type=Path)
    parser.add_argument('--receipt',type=Path,required=True)
    args=parser.parse_args()
    result=inspect(args.project_root.resolve(),args.firmware.resolve(),args.folder.resolve(),args.body_object,args.elf_name,
                   args.providers.resolve() if args.providers else None)
    need(not args.receipt.exists(),'Create-only narrow-entry review receipt')
    args.receipt.parent.mkdir(parents=True,exist_ok=True)
    args.receipt.write_bytes((json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode('utf8'))
    print(json.dumps(dict(actual_objects_IR_and_linked_ELF_read=True,checked_entry_prefix_passed=True,
                         allocated_bytes=result['contract']['allocated_bytes'],original_ABI_admitted=False,
                         actual_linked_controls=len(result['controls']))))


if __name__=='__main__':
    main()
