#!/usr/bin/env python3
"""Read-only audit of compiler-owned save-prefix and success-tail scheduling."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import runpy
import sys

sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
NAMES={'tsl9_ota_tx_8a56':18,'tsl9_tx_valid_body':2,'_ZL18tsl9_tx_valid_bodyjjjj':2}


def need(value,message):
    if not value:
        raise ValueError(message)


def H(payload):
    return hashlib.sha256(payload).hexdigest()


def prepare(root,firmware):
    predicates=runpy.run_path(str(HERE/'predicates.py'))
    native=predicates['prior'](root)
    return native,native['context'](root,firmware)


def contract(e,n,context):
    need(e.kind==1 and e.flags==1,'Actual standalone RVC ET_REL source object')
    symbol=n['one'](e.symbols,lambda s:s['name'] in NAMES,'One selected typed function')
    owner=e.sections[symbol['index']]
    need((symbol['value'],symbol['size'],symbol['info'],symbol['other'])==
         (0,owner['size'],NAMES[symbol['name']],0),'Exact typed entry and whole FUNC owner')
    need((owner['type'],owner['flags'],owner['alignment'])==(1,6,2),'AX aligned standalone owner')
    need(len([s for s in e.sections if s['name']==owner['name']])==1,'Unique selected owner section name')
    need([s['index'] for s in e.sections if s['flags']&2 and s['size']]==[owner['index']],
         'No extra allocated storage in standalone function object')
    for section in e.sections:
        if section['index']==owner['index'] or section['type']==8 or not section['size']:
            continue
        need(section['offset']+section['size']<=owner['offset'] or
             owner['offset']+owner['size']<=section['offset'],'Selected physical storage has no section alias')
        need(section['name'] not in ('.eh_frame','.debug_frame'), 'No unhandled unwind metadata')
    body=e.function_bytes(symbol)
    rows=n['rows'](body,context)
    one=n['one']
    need(rows[0]['op']=='addi' and(rows[0]['rd'],rows[0]['rs1'],rows[0]['immediate'])==(2,2,-32),
         'Typed body starts with its actual32B frame allocation')
    prefix=[r for r in rows if 2<=r['offset']<12]
    slots={(1,28),(8,24),(9,20),(18,16),(19,12)}
    need(len(prefix)==5 and all(r['op']=='sw' and r['rs1']==2 and r['bytes']==2 and
                               r['memory_width']==32 for r in prefix) and
         {(r['rs2'],r['immediate']) for r in prefix}==slots,
         'Actual five compiler-owned compressed prefix saves')
    start=one(rows,lambda r:r['op']=='add' and(r['rd'],r['rs1'],r['rs2'])==(15,15,8),
              'One success checksum-address frontier')
    tail=one(rows,lambda r:r['op']=='jalr' and(r['rd'],r['rs1'])==(0,6),'One success JR T1')
    lower,upper=start['offset'],tail['offset']+tail['bytes']
    window=[r for r in rows if lower<=r['offset']<upper]
    need(window[0]==start and window[-1]==tail,'Whole bounded success window')
    for row in rows:
        if row['target'] is not None:
            target=row['target']-0x8a56
            need(not lower<target<upper,'No encoded incoming branch into a moved interior boundary')
            need(not 2<=target<12,'No encoded branch enters a prefix save word')
        if row['op']=='jalr' and row['rd']==1:
            need(not lower<=row['offset']+row['bytes']<upper,
                 'No opaque call continuation enters the success scheduling window')
    need(not any(r['target'] is not None or(r['op']=='jalr' and r!=tail) or r['op']=='auipc'
                 for r in window),'No internal branch/call/PC-relative word in the scheduling window')
    for s in e.symbols:
        if s['index']==owner['index']:
            need(not lower<s['value']<upper,'No interior symbol anchor may change semantic word')
            need(not 2<=s['value']<12,'No symbol anchors a prefix save word')
    for rela in e.relocations:
        if rela['owner']==owner['name']:
            need(not lower<=rela['offset']<upper,'No relocation site in the scheduling window')
            need(not 2<=rela['offset']<12,'No relocation site in prefix saves')
        if rela['symbol']['index']==owner['index']:
            target=rela['symbol']['value']+rela['addend']
            need(not lower<target<upper,'No recorded relocation target into moved interior')
            need(not 2<=target<12,'No recorded relocation target into prefix saves')
    loads=[r for r in window if r['op']=='lw' and r['rs1']==2]
    expected={(1,28),(8,24),(9,20),(18,16),(19,12)}
    need(len(loads)==5 and {(r['rd'],r['immediate']) for r in loads}==expected and
         all(r['bytes']==2 and r['memory_width']==32 for r in loads),
         'Exactly five existing compressed word frame restores with source slots')
    boundaries={
        'lane_shift':one(window,lambda r:r['op']=='slli' and(r['rd'],r['rs1'],r['immediate'])==(12,12,2),'Lane shift'),
        'argument_one':one(window,lambda r:r['op']=='addi' and(r['rd'],r['rs1'],r['immediate'])==(11,0,1),'Tail A1=1'),
        'length_store':one(window,lambda r:r['op']=='sh' and(r['rs1'],r['rs2'],r['immediate'])==(15,8,2),'Descriptor length SH16'),
        'zero_store':one(window,lambda r:r['op']=='sh' and(r['rs1'],r['rs2'],r['immediate'])==(15,0,4),'Descriptor zero SH16'),
        'ROM_base':one(window,lambda r:r['op']=='lui' and(r['rd'],r['immediate'])==(15,0x40000),'Fresh ROM pointer base'),
        'ROM_pointer':one(window,lambda r:r['op']=='lw' and(r['rd'],r['rs1'],r['immediate'])==(6,15,0x50),'Fresh ROM pointer LW32'),
        'task':one(window,lambda r:r['op']=='lbu' and(r['rd'],r['rs1'],r['immediate'])==(10,12,0),'Task LBU'),
        'pop':one(window,lambda r:r['op']=='addi' and(r['rd'],r['rs1'],r['immediate'])==(2,2,32),'SP restored after task load'),
    }
    return dict(symbol=symbol,owner=owner,body=body,rows=rows,prefix=prefix,window=window,loads=loads,
                boundaries=boundaries,lower=lower,upper=upper)


def audit(root,firmware,before,after):
    n,context=prepare(root,firmware)
    a,b=context['ELF'](before),context['ELF'](after)
    x,y=contract(a,n,context),contract(b,n,context)
    need(len(a.raw)==len(b.raw) and x['lower']==y['lower'] and x['upper']==y['upper'],
         'Object length and window geometry unchanged')
    lo=x['owner']['offset']+x['lower'];hi=x['owner']['offset']+x['upper']
    prefix_lo=x['owner']['offset']+2;prefix_hi=x['owner']['offset']+12
    need(a.raw[:prefix_lo]==b.raw[:prefix_lo] and a.raw[prefix_hi:lo]==b.raw[prefix_hi:lo] and
         a.raw[hi:]==b.raw[hi:],
         'All bytes outside two selected windows, including every ELF metadata byte, unchanged')
    need(Counter(r['raw_hex'] for r in x['prefix'])==Counter(r['raw_hex'] for r in y['prefix']),
         'Prefix only permutes the five actual compiler save words')
    need([r['rs2'] for r in y['prefix']]==[8,9,18,19,1],
         'Prefix save order is source S0/S1/S2/S3/RA')
    need(Counter(r['raw_hex'] for r in x['window'])==Counter(r['raw_hex'] for r in y['window']),
         'Only a permutation of actual compiler instruction words; no new opcode')
    def nonloads(c):
        offsets={r['offset'] for r in c['loads']}
        return [r['raw_hex'] for r in c['window'] if r['offset'] not in offsets]
    need(nonloads(x)==nonloads(y),'All non-restore words retain their exact order')
    need(x['window'][0]['raw_hex']==y['window'][0]['raw_hex'] and
         x['window'][-1]['raw_hex']==y['window'][-1]['raw_hex'],
         'Incoming start and terminal tail remain the same semantic words')
    loads={r['rd']:r for r in y['loads']};front=y['boundaries']
    order=[loads[reg]['offset'] for reg in (1,9,18,19)]
    need(order==sorted(order) and front['lane_shift']['offset']<order[0] and
         order[-1]<front['argument_one']['offset']<front['length_store']['offset'],
         'RA/S1/S2/S3 fresh read in source order before descriptor stores')
    need(front['length_store']['offset']<front['zero_store']['offset']<loads[8]['offset']<
         front['ROM_base']['offset']<front['ROM_pointer']['offset']<front['task']['offset']<
         front['pop']['offset'],'S0 after descriptor stores; ROM/task/SP frontier in source order')
    return dict(schema='TSL9-TX-independent-tail-scheduling-review-v1',
                actual_pre_and_post_ELF_read=True,before_sha256=H(a.raw),after_sha256=H(b.raw),
                function_name=x['symbol']['name'],window_offsets=[x['lower'],x['upper']],
                prefix_offsets=[2,12],frame_saves_scheduled=5,frame_restores_moved=5,no_new_instruction_word=True,
                outside_bytes_and_all_ELF_metadata_identical=True,
                fresh_restore_frontiers_proved=True,
                source_full_pointwise_identity_proved=False,
                original_ABI_admitted=False,hardware_OTA_proved=False,
                target_execution=False,ISA_emulation=False)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--project-root',type=Path,required=True)
    parser.add_argument('--firmware',type=Path,required=True)
    parser.add_argument('--before',type=Path,required=True)
    parser.add_argument('--after',type=Path,required=True)
    parser.add_argument('--receipt',type=Path,required=True)
    args=parser.parse_args()
    result=audit(args.project_root.resolve(),args.firmware.resolve(),args.before.resolve(),args.after.resolve())
    need(not args.receipt.exists(),'Create-only independent tail receipt')
    args.receipt.parent.mkdir(parents=True,exist_ok=True)
    args.receipt.write_bytes((json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode('utf8'))
    print(json.dumps(result))


if __name__=='__main__':
    main()
