#!/usr/bin/env python3
"""Independent bounded call/frame/PCREL facts; no instruction-state execution."""
import hashlib
import json
from pathlib import Path

ORIGINAL='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
CALLBACK='3e21432057f673abea404541e0745937d894448b492478b5fed5775e91b398bf'
ENTRY=0x8614
CALLS=((0x8640,15),(0x865c,15),(0x8666,15),(0x86e0,15),(0x8704,15),
       (0x873c,15),(0x87a2,15),(0x87ba,15),(0x87c6,15),(0x87d8,15),
       (0x87f8,15),(0x8812,15),(0x882c,15),(0x886a,16),(0x8884,15))
SAVES=((0x861a,8,40),(0x861c,1,44),(0x861e,9,36),(0x8620,18,32),
       (0x8622,19,28),(0x8624,20,24),(0x8626,21,20),(0x8628,22,16),
       (0x862a,23,12),(0x862c,24,8),(0x862e,25,4))
RESTORES=((0x866c,1,44),(0x866e,8,40),(0x8670,9,36),(0x8672,18,32),
          (0x8674,19,28),(0x8676,20,24),(0x8678,21,20),(0x867a,22,16),
          (0x867c,23,12),(0x867e,24,8),(0x8680,25,4))


def need(value,message):
    if not value:
        raise ValueError(message)


def sign(value,bits):
    return value-(1<<bits) if value&(1<<(bits-1)) else value


def validate(body):
    need(len(body)==632,'Actual original callback extent632')
    def h(pc):
        return int.from_bytes(body[pc-ENTRY:pc-ENTRY+2],'little')
    need(h(ENTRY)==0x7179 and h(0x8682)==0x6145 and h(0x8684)==0x8082,
         'Original SP-48/SP+48/normal RET instruction words')
    call_rows=[]
    for pc,target in CALLS:
        word=h(pc)
        need((word&0xf07f)==0x9002 and (word>>7)&31==target,
             'Compressed indirect call writes RA from exact source target register '+hex(pc))
        call_rows.append(dict(PC=pc,raw_hex=word.to_bytes(2,'little').hex(),width=2,
                              rd=1,target_register=target,RA=pc+2))
    for pc,register,slot in SAVES:
        word=h(pc)
        need(word&3==2 and word>>13==6 and (word>>2)&31==register and
             (((word>>9)&15)<<2|((word>>7)&3)<<6)==slot,
             'Actual compressed SWSP source/slot '+hex(pc))
    for pc,register,slot in RESTORES:
        word=h(pc)
        need(word&3==2 and word>>13==2 and (word>>7)&31==register and
             (((word>>12)&1)<<5|((word>>4)&7)<<2|((word>>2)&3)<<6)==slot,
             'Actual fresh compressed LWSP destination/slot '+hex(pc))
    addresses=[]
    for pc,reg,target in ((0x86c0,9,0x2000b18c),(0x870a,15,0x2000bdf8),
                          (0x876c,25,0x2000b18c),(0x8784,9,0x2000bdf8),
                          (0x887a,12,0x19de0)):
        at=pc-ENTRY;hi=int.from_bytes(body[at:at+4],'little');lo=int.from_bytes(body[at+4:at+8],'little')
        need(hi&127==0x17 and (hi>>7)&31==reg and lo&0x707f==0x13 and
             (lo>>7)&31==reg and (lo>>15)&31==reg,'Actual PCREL instruction fields')
        actual=(pc+sign(hi&0xfffff000,32)+sign(lo>>20,12))&0xffffffff
        need(actual==target,'Actual source-carried static address '+hex(pc))
        addresses.append(dict(PC=pc,destination=reg,address=actual))
    return dict(bytes=632,calls=call_rows,frame_bytes=48,
                saves=[dict(PC=p,register=r,slot=s) for p,r,s in SAVES],
                fresh_restores=[dict(PC=p,register=r,slot=s) for p,r,s in RESTORES],
                PCREL=addresses,normal_return_PC=0x8684,
                opaque_call_standard_ABI_preservation_assumed=False)


def inspect(firmware):
    raw=firmware.read_bytes()
    need(hashlib.sha256(raw).hexdigest()==ORIGINAL,'Pinned official runtime validation input')
    body=raw[ENTRY-0x8000:ENTRY-0x8000+632]
    need(hashlib.sha256(body).hexdigest()==CALLBACK,'Exact original632B callback')
    result=validate(body);controls=[]
    for name,pc,value in (('call_loses_RA',0x8640,0x8782),
                           ('five_argument_call_wrong_target_register',0x87a2,0x9802),
                           ('save_wrong_SP_slot',0x861a,0xd222),
                           ('fresh_restore_wrong_register',0x866c,0x54b2),
                           ('frame_pop_wrong_size',0x8682,0x6105)):
        changed=bytearray(body);changed[pc-ENTRY:pc-ENTRY+2]=value.to_bytes(2,'little')
        try:
            validate(bytes(changed))
        except ValueError as error:
            controls.append(dict(name=name,rejected=True,reason=str(error)))
        else:
            raise ValueError('Actual call/frame raw countercase admitted '+name)
    return dict(schema='TSL9-callback-independent-call-frame-v1',original_sha256=ORIGINAL,
                callback_sha256=CALLBACK,actual_original_firmware_read=True,
                facts=result,raw_countercases=controls,target_execution=False,
                ISA_emulation=False,full_original_ABI_proved=False,hardware_OTA_proved=False)
