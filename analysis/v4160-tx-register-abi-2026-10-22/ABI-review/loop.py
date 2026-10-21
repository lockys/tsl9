#!/usr/bin/env python3
"""Bounded original/candidate loop CFG correspondence; no ISA state evaluation."""
import argparse
import hashlib
import json
from pathlib import Path
import runpy
import sys

sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
ENTRY=0x8a56


def need(value,message):
    if not value:
        raise ValueError(message)


def H(raw):
    return hashlib.sha256(raw).hexdigest()


def fields(row):
    return (row['op'],row['rd'],row['rs1'],row['rs2'],row['immediate'],row['memory_width'],row['bytes'])


def blocks(rows,n,candidate):
    one=n['one'];by_PC={r['PC']:r for r in rows}
    first=one(rows,lambda r:r['op']=='slli' and(r['rd'],r['rs1'],r['immediate'])==(10,11,16),
              'Unique low16 counter comparison header')
    second=by_PC[first['PC']+first['bytes']]
    need(fields(second)==('srli',10,10,None,16,None,2),'Counter truncation is logical low16')
    guard=by_PC[second['PC']+second['bytes']]
    need(guard['op']==('bgeu' if candidate else 'bltu') and
         (guard['rs1'],guard['rs2'],guard['bytes'])==(10,8,4),
         'Unsigned complementary branch compares counter A0 against live S0')
    payload_PC=guard['PC']+guard['bytes'] if candidate else guard['target']
    finish_PC=guard['target'] if candidate else guard['PC']+guard['bytes']
    payload=[];pc=payload_PC
    for _ in range(8):
        need(pc in by_PC,'Payload instruction is in actual decoded owner')
        row=by_PC[pc];payload.append(row);pc+=row['bytes']
    need(payload[-1]['op']=='jal' and payload[-1]['rd']==0 and payload[-1]['bytes']==2 and
         payload[-1]['target']==first['PC'],'Actual no-link payload backedge returns to same counter header')
    need(finish_PC in by_PC,'Actual loop finish boundary exists')
    finish=[by_PC[finish_PC]]
    finish.append(by_PC[finish_PC+finish[0]['bytes']])
    need(fields(finish[0])==('add',15,15,8,None,None,2) and
         fields(finish[1])==('sb',None,15,14,5,8,4),'Finish computes packet+liveS0 then stores checksum byte')
    need(not any(r['rd']==16 for r in rows if r not in payload),
         'No additional local A6 writes outside the payload block')
    return dict(header=[first,second],guard=guard,payload=payload,finish=finish)


def compare(original,candidate,n):
    source=blocks(original,n,False);target=blocks(candidate,n,True)
    need([fields(r) for r in source['header']]==[fields(r) for r in target['header']],
         'Same full counter-to-low16 sequence')
    pairs=[]
    for index,(a,b) in enumerate(zip(source['payload'][:-1],target['payload'][:-1])):
        same=fields(a)==fields(b)
        commuted=(index==2 and a['op']==b['op']=='add' and a['rd']==b['rd']==16 and
                  a['rs1']==b['rs2']==15 and a['rs2']==b['rs1']==11 and
                  a['immediate']==b['immediate']==None and
                  a['memory_width']==b['memory_width']==None and a['bytes']==b['bytes']==4)
        need(same or commuted,'Payload semantic fields differ outside the allowed A6 ADD operand swap')
        pairs.append(dict(source=a,candidate=b,relation='same semantic fields' if same else
                          'same ADD A6 result under corresponding A1/A5 inputs; rs1/rs2 reversed'))
    need([fields(r) for r in source['finish']]==[fields(r) for r in target['finish']],
         'Same checksum finish operations and widths')
    return dict(source=source,candidate=target,payload_correspondence=pairs,
                source_true_edge='low16(A1)<liveS0 -> payload',
                candidate_false_edge='not(low16(A1)>=liveS0) -> fallthrough payload',
                complementary_unsigned_predicate=True,backedge_header_correspondence=True,
                zero_iterations_skip_A6_write=True,
                source_payload_bytes=sum(r['bytes'] for r in source['payload']),
                candidate_payload_bytes=sum(r['bytes'] for r in target['payload']))


def inspect(root,firmware,elf_path):
    p=runpy.run_path(str(HERE/'predicates.py'));n=p['prior'](root);context=n['context'](root,firmware)
    source=context['raw']['validate'](context['original'])
    e=context['ELF'](elf_path)
    entry=n['one'](e.symbols,lambda s:s['name']=='tsl9_ota_tx_8a56','Actual linked entry provider')
    owner=e.sections[entry['index']]
    need(e.kind==2 and e.flags==1 and (owner['type'],owner['flags'],owner['address'],owner['size'])==
         (1,6,ENTRY,280),'Actual complete linked280 allocation at original entry')
    body=e.data(owner);rows=n['rows'](body,context);proof=compare(source,rows,n)
    k=proof['candidate'];tests=[('noncomplementary_branch',k['guard'],4,1<<12),
                               ('wrong_live_length_GPR',k['guard'],4,1<<20),
                               ('counter_not_low16',k['header'][0],4,1<<20),
                               ('payload_counter_address_changed',k['payload'][0],4,1<<20),
                               ('payload_load_wrong_width',k['payload'][1],4,6<<12),
                               ('payload_A6_destination_changed',k['payload'][2],4,1<<7),
                               ('counter_increment_changed',k['payload'][3],2,1<<2),
                               ('payload_store_offset_changed',k['payload'][5],4,1<<7),
                               ('backedge_header_changed',k['payload'][-1],2,1<<3)]
    controls=[]
    for name,row,width,mask in tests:
        offset=row['offset'];raw=bytearray(body)
        raw[offset:offset+width]=(int.from_bytes(raw[offset:offset+width],'little')^mask).to_bytes(width,'little')
        try:
            compare(source,n['rows'](bytes(raw),context),n)
        except ValueError as error:
            controls.append(dict(name=name,actual_linked_instruction_bytes_mutated=True,rejected=True,
                                 offset=offset,reason=str(error)))
        else:
            raise ValueError('Incorrect loop counterpart admitted:'+name)
    return dict(schema='TSL9-TX-independent-loop-CFG-correspondence-v1',
                actual_original_and_linked_body_read=True,linked_ELF_sha256=H(e.raw),
                linked_body_sha256=H(body),original_body_sha256=H(context['original']),
                loop_CFG_correspondence_proved=True,proof=proof,controls=controls,
                assumptions=['corresponding A1 full counter, A4 checksum, A5 packet pointer, live S0/S1 values at header',
                             'corresponding memory byte responses at each paired logical access',
                             'no asynchronous interference or inspection of differing instruction PCs',
                             'payload/data reads do not distinguish replaced instruction bytes as data'],
                argument_domain_not_proved_from_all_callers=True,
                opaque_ROM_ABI_proved=False,arbitrary_computed_interior_entries_absent_proved=False,
                original_full_ABI_admitted=False,target_execution=False,ISA_emulation=False)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--project-root',type=Path,required=True)
    parser.add_argument('--firmware',type=Path,required=True)
    parser.add_argument('--elf',type=Path,required=True)
    parser.add_argument('--receipt',type=Path,required=True)
    args=parser.parse_args()
    result=inspect(args.project_root.resolve(),args.firmware.resolve(),args.elf.resolve())
    need(not args.receipt.exists(),'Create-only loop CFG receipt')
    args.receipt.parent.mkdir(parents=True,exist_ok=True)
    args.receipt.write_bytes((json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode('utf8'))
    print(json.dumps(dict(actual_original_and_linked_body_read=True,loop_CFG_correspondence_proved=True,
                         actual_operand_controls=len(result['controls']),original_full_ABI_admitted=False)))


if __name__=='__main__':
    main()
