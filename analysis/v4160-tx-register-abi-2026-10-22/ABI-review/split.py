#!/usr/bin/env python3
"""Inspect the actual source-only split-entry diagnostic; no target execution."""
import argparse
import hashlib
import json
from pathlib import Path
import runpy
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent


def need(value, message):
    if not value:
        raise ValueError(message)


def H(payload):
    return hashlib.sha256(payload).hexdigest()


def entry_contract(body, n, context):
    need(len(body)==18, 'Actual 18B diagnostic wrapper')
    rows = n['rows'](body[:14], context)
    word = int.from_bytes(body[14:18], 'little')
    need(word&127==0x67 and(word>>12)&7==0, 'Actual 32-bit entry JALR encoding')
    immediate = word>>20
    if immediate&0x800:
        immediate -= 1<<12
    rows.append(dict(PC=0x8a56+14,offset=14,op='jalr',rd=(word>>7)&31,
                     rs1=(word>>15)&31,rs2=None,immediate=immediate,
                     memory_width=None,bytes=4,target=None,raw_hex=body[14:18].hex()))
    need(len(rows)==5, 'Actual five-instruction diagnostic wrapper')
    def fields(row):
        return row['op'],row['rd'],row['rs1'],row['rs2'],row['immediate'],row['memory_width']
    need(fields(rows[0])==('addi',15,0,None,1039,None), 'Entry A5 literal1039')
    need(fields(rows[1])[:4]==('bgeu',None,15,13) and rows[1]['target']==0x8a56+10,
         'Unsigned A5>=A3 reaches source-only tail adapter')
    need(fields(rows[2])[:4]==('jalr',0,1,None), 'Oversized path RET without RA link')
    need(fields(rows[3])==('auipc',6,None,None,0,None), 'Actual compiler-owned T1 PCREL tail address')
    need(fields(rows[4])==('jalr',0,6,None,0,None), 'Actual no-link JR T1 entry transfer')
    need(all(r['memory_width'] is None and r['rd'] not in (1,2,8,9,18,19) for r in rows),
         'Entry path has no frame/memory effect or saved-register write')
    return rows


def inspect(root, firmware, folder):
    p = runpy.run_path(str(HERE/'predicates.py'))
    n = p['prior'](root)
    context = n['context'](root,firmware)
    e = context['ELF'](folder/'tx_native.o')
    entry = n['one'](e.symbols,lambda s:s['name']=='tsl9_ota_tx_8a56','Actual wrapper symbol')
    valid = n['one'](e.symbols,lambda s:s['name'] in ('tx_valid_body','_ZL13tx_valid_bodyjjjj'),
                     'Actual C or C++ static valid-body symbol')
    need(e.kind==1 and e.flags==1 and (entry['info'],entry['other'],entry['value'],entry['size'])==(18,0,0,18),
         'Actual ET_REL public FUNC18 wrapper')
    need((valid['info'],valid['other'],valid['value'],valid['size'])==(2,0,0,272),
         'Actual local FUNC272 valid body')
    need({s['index'] for s in e.sections if s['flags']&2 and s['size']}=={entry['index'],valid['index']},
         'Exactly two nonempty allocated function owners')
    for symbol in (entry,valid):
        owner=e.sections[symbol['index']]
        need((owner['type'],owner['flags'],owner['alignment'],owner['size'])==(1,6,2,symbol['size']),
             'Actual exact AX function section')
    body=e.function_bytes(entry)
    entry_rows=entry_contract(body,n,context)
    valid_rows=n['rows'](e.function_bytes(valid),context)
    gates=[r for r in valid_rows if r['op']=='jalr' and(r['rd'],r['rs1'])==(1,15)]
    need(len(gates)==2,'Two actual valid-body opaque gate calls')
    wrapper_rela=[r for r in e.relocations if r['owner']==e.sections[entry['index']]['name']]
    need(len(wrapper_rela)==1 and wrapper_rela[0]['type']==19 and wrapper_rela[0]['offset']==10 and
         wrapper_rela[0]['addend']==0 and wrapper_rela[0]['symbol']['index']==valid['index'] and
         wrapper_rela[0]['symbol']['value']==0,'Actual no-relax compiler CALL_PLT target is valid-body entry')
    need(len(e.relocations)==3 and sorted(r['type'] for r in e.relocations)==[19,23,24],
         'Only entry-tail and original RAM PCREL relocations')
    controls=[]
    for name,offset,width,mask in [('wrong_unsigned_condition',4,4,1<<12),
                                   ('oversized_RET_changes_RA',8,2,1<<12),
                                   ('tail_address_wrong_GPR',10,4,128),
                                   ('entry_tail_creates_RA',14,4,128)]:
        changed=bytearray(body)
        value=int.from_bytes(changed[offset:offset+width],'little')^mask
        changed[offset:offset+width]=value.to_bytes(width,'little')
        try:
            entry_contract(bytes(changed),n,context)
        except ValueError as error:
            controls.append(dict(name=name,actual_compiled_entry_bytes_mutated=True,rejected=True,
                                 original_hex=body[offset:offset+width].hex(),
                                 changed_hex=bytes(changed[offset:offset+width]).hex(),reason=str(error)))
        else:
            raise ValueError('Entry countercase admitted: '+name)
    return dict(schema='TSL9-TX-split-entry-static-review-v1',actual_compiler_object_read=True,
                object_sha256=H(e.raw),entry_bytes=18,valid_body_bytes=272,total_owned_bytes=290,
                actual_valid_body_symbol=valid['name'],
                original_extent=280,combined_original_extent_fits=False,
                oversized_path_no_frame_proved=True,entry_rows=entry_rows,
                entry_tail_no_new_RA=True,entry_tail_writes_T1=True,
                valid_body_writes_T1_before_first_gate=any(r['rd']==6 for r in valid_rows
                                                         if r['offset']<gates[0]['offset']),
                original_locally_writes_T1_before_first_gate=False,
                extra_T1_provider_boundary_equivalence_proved=False,
                valid_body_gate_offsets=[r['offset'] for r in gates],
                actual_linked_gate_RAs_proved=False,entry_tail_RELA_type=19,
                original_ABI_admitted=False,whole_image_admitted=False,
                controls=controls,target_execution=False,ISA_emulation=False)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--project-root',type=Path,required=True)
    parser.add_argument('--firmware',type=Path,required=True)
    parser.add_argument('--folder',type=Path,required=True)
    parser.add_argument('--receipt',type=Path,required=True)
    args=parser.parse_args()
    result=inspect(args.project_root.resolve(),args.firmware.resolve(),args.folder.resolve())
    need(not args.receipt.exists(),'Create-only split diagnostic receipt')
    args.receipt.parent.mkdir(parents=True,exist_ok=True)
    args.receipt.write_bytes((json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode('utf8'))
    print(json.dumps(dict(actual_compiler_object_read=True,oversized_path_no_frame_proved=True,
                         total_owned_bytes=290,original_ABI_admitted=False,
                         raw_entry_controls=len(result['controls']))))


if __name__=='__main__':
    main()
