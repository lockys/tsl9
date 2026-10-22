#!/usr/bin/env python3
"""Actual native ELF/IR diagnosis, explicitly not original-ABI admission."""
import hashlib
import json
from pathlib import Path
import re
import runpy
import struct

PARSER='00a231e3bbd881a9961c12fefd15565364cd813250a46a7b20851a6b9f3a2141'


def need(value,message):
    if not value:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dependency(root,path):
    p=root/path
    if not p.exists() and path.startswith('apk-analysis/tsl9-'):
        p=root/'analysis'/path[len('apk-analysis/tsl9-'):]
    return p


def functions(e):
    need(e.kind==2 and e.flags==1,'Actual linked RV32 RVC ELF witness')
    selected=[s for s in e.symbols if s['info']&15==2 and s['size']]
    need(len(selected) in (1,2),'Only observed typed main with optional self-owned opaque-call primitive')
    main=next(s for s in selected if s['name']=='tsl9_callback_native_8614')
    helper=next((s for s in selected if s['name'] in ('cb_native_call','_ZL14cb_native_callP9cb_nativejj')),None)
    need(main['info']==18 and main['other']==0 and 0<main['index']<len(e.sections),
         'Honest allocated GLOBAL main and LOCAL helper functions')
    if len(selected)==1:
        need(helper is None and main['size']==658,'Only the actually measured inline one-FUNC658 diagnostic profile')
    else:
        need(helper is not None and helper['info']==2 and helper['other']==0 and
             (main['size'],helper['size']) in ((938,90),(944,90)),
             'Only the measured pre-inline source diagnostics, not an open-ended acceptance profile')
    need(not [s for s in e.symbols if s['name'] and s['index']==0],
         'No hidden unresolved code/data provider in this component')
    allocations=[s for s in e.sections if s['flags']&2 and s['size']]
    need(len(allocations)==1 and allocations[0]['flags']==6 and
         main['index']==allocations[0]['index'] and
         main['value']==allocations[0]['address'] and
         allocations[0]['size']==main['size']+(helper['size'] if helper else 0) and
         (helper is None or (helper['index']==main['index'] and helper['value']==main['value']+main['size'])),
         'One complete allocated extent with both real source functions and no hidden padding')
    return main,helper


def machine(e):
    main,helper=functions(e);owner=e.sections[main['index']];raw=e.data(owner)
    main_at=main['value']-owner['address'];helper_at=helper['value']-owner['address'] if helper else 0
    # Bounded first-word decode of C.ADDI16SP, not a CPU state evaluator.
    def frame(at):
        word=int.from_bytes(raw[at:at+2],'little')
        if word&0xef83==0x0101:
            immediate=((word>>2)&31)|(((word>>12)&1)<<5)
            return immediate-64 if immediate&32 else immediate
        need(word&0xef83==0x6101,'Actual compressed stack-adjust prefix')
        immediate=(((word>>12)&1)<<9|((word>>6)&1)<<4|((word>>5)&1)<<6|
                   ((word>>3)&3)<<7|((word>>2)&1)<<5)
        return immediate-1024 if immediate&512 else immediate
    main_frame=frame(main_at);helper_frame=frame(helper_at) if helper else 0
    need(main_frame<0 and (helper is None or helper_frame<0),'Actual allocated native stack frames')
    prefix=[];at=main_at+2
    while at<main_at+main['size']:
        word=int.from_bytes(raw[at:at+2],'little')
        if not(word&3==2 and word>>13==6):break
        prefix.append(dict(register=(word>>2)&31,slot=(((word>>9)&15)<<2|((word>>7)&3)<<6)))
        at+=2
    if helper is None:
        need(main_frame==-48 and [(p['register'],p['slot']) for p in prefix]==
             [(1,44),(8,40),(9,36),(18,32),(19,28),(20,24),(21,20),(22,16),
              (23,12),(24,8),(25,4),(26,0)],'Actual measured inline profile48B/12-save prefix')
    call_owner=helper if helper else main
    helper_bytes=raw[helper_at:helper_at+helper['size']] if helper else raw
    indirect=[]
    at=0
    while at<len(helper_bytes):
        half=int.from_bytes(helper_bytes[at:at+2],'little');size=4 if half&3==3 else 2
        need(at+size<=len(helper_bytes),'All helper instruction boundaries fit actual extent')
        if size==2 and half&0xf07f==0x9002:
            indirect.append(dict(address=call_owner['value']+at,rd=1,
                                 target_register=(half>>7)&31,RA=call_owner['value']+at+2))
        at+=size
    expected=[15,16] if helper else [15]*14+[16]
    need(sorted(r['target_register'] for r in indirect)==expected,
         'Actual source-owned opaque calls retain observed RA-writing A5/A6 geometry')
    source_call_offsets=[p-0x8614+2 for p in (0x8640,0x865c,0x8666,0x86e0,0x8704,
                          0x873c,0x87a2,0x87ba,0x87c6,0x87d8,0x87f8,0x8812,0x882c,0x886a,0x8884)]
    normalized_RAs=sorted(r['RA']-main['value'] for r in indirect)
    return dict(main_bytes=main['size'],helper_bytes=helper['size'] if helper else 0,
                allocated_bytes=owner['size'],original_bytes=632,
                fits_original_extent=owner['size']<=632,
                main_frame_bytes=-main_frame,helper_frame_bytes=-helper_frame,
                resident_call_frame_bytes=-main_frame-helper_frame,
                source_resident_call_frame_bytes=48,resident_call_sites=indirect,
                original_fifteen_call_RAs_preserved=normalized_RAs==sorted(source_call_offsets),
                actual_return_offsets_from_entry=normalized_RAs,
                native_prefix_saves=prefix,
                original_unused_SP0_overwritten_by_S10=helper is None,
                physical_saved_S_register_layout_preserved=False,
                full_original_ABI_proved=False,placement_admitted=False)


def inspect(root,folder):
    parser=dependency(root,'apk-analysis/tsl9-v4160-irq-native-2026-10-21/compiler-review/elf32.py')
    need(sha(parser)==PARSER,'Pinned pure ELF parser')
    E=runpy.run_path(str(parser))['ELF'];path=folder/'COMPONENT-ONLY-NOT-FIRMWARE.elf';e=E(path)
    facts=machine(e);main,helper=functions(e);owner=e.sections[main['index']]
    disassembly=(folder/'complete-static-disassembly.log').read_text(encoding='utf8')
    rows=[]
    for line in disassembly.splitlines():
        match=re.match(r'^\s*([0-9a-f]+):\s+((?:[0-9a-f]{2}\s+)+)\s*([^\s]+)',line)
        if match:
            rows.append((int(match[1],16),bytes.fromhex(match[2]),match[3]))
    offset=0;payload=e.data(owner)
    for pc,raw,op in rows:
        need(pc==owner['address']+offset and len(raw) in (2,4) and
             payload[offset:offset+len(raw)]==raw and op not in ('.word','.2byte','<unknown>'),
             'Complete actual LLVM static rows exactly cover native code')
        offset+=len(raw)
    need(offset==len(payload),'No omitted native function instruction bytes')
    ir=(folder/'callback.ll').read_text(encoding='utf8')
    need('jalr ra,a5,0' in ir and 'jalr ra,a6,0' in ir and
         all(token in ir for token in ('load volatile i8','load volatile i16','load volatile i32',
                                        'store volatile i8','store volatile i16','store volatile i32')),
         'Actual shared-C IR retains typed volatile widths and explicit raw indirect call primitive')
    controls=[]
    class Bytes:
        def __init__(self,value):self.value=value
        def read_bytes(self):return self.value
    # Direct, actually changed ELF inputs; metadata honesty and raw call link checks.
    symbol_table=next(s for s in e.sections if s['type']==2)
    for name,make in (
        ('public_main_fabricated_ABS',lambda p:struct.pack_into('<H',p,symbol_table['offset']+main['number']*16+14,0xfff1)),
    ):
        p=bytearray(e.raw)
        # Parser symbol number is derived below when not exposed by the parser.
        try:
            make(p)
        except KeyError:
            table=e.symbol_tables[symbol_table['index']]
            number=next(i for i,s in enumerate(table) if s['name']==main['name'])
            struct.pack_into('<H',p,symbol_table['offset']+number*16+14,0xfff1)
        try:machine(E(Bytes(bytes(p))))
        except (ValueError,StopIteration,IndexError) as error:
            controls.append(dict(name=name,rejected=True,reason=str(error)))
        else:raise ValueError('Malformed native provider admitted')
    first=facts['resident_call_sites'][0];p=bytearray(e.raw)
    at=owner['offset']+first['address']-owner['address'];word=int.from_bytes(p[at:at+2],'little')
    p[at:at+2]=(word&~0x1000).to_bytes(2,'little')
    try:machine(E(Bytes(bytes(p))))
    except ValueError as error:controls.append(dict(name='opaque_helper_call_loses_RA',rejected=True,reason=str(error)))
    else:raise ValueError('No-link opaque-call countercase admitted')
    return dict(schema='TSL9-callback-independent-native-gap-v1',actual_native_artifacts_read=True,
                ELF_sha256=sha(path),IR_sha256=sha(folder/'callback.ll'),
                actual_function_rows=len(rows),facts=facts,raw_controls=controls,
                conditional_conventional_C_ABI_only=True,original_full_ABI_admitted=False,
                no_image_integration=True,target_execution=False,ISA_emulation=False,
                hardware_OTA_proved=False)
