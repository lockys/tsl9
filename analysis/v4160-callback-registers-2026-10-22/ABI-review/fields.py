"""Pinned single-instruction field decoders; no register-state interpretation."""
import hashlib
from pathlib import Path
import runpy

PINS={
 'v4160-irq-native-2026-10-21/compiler-review/elf32.py':'00a231e3bbd881a9961c12fefd15565364cd813250a46a7b20851a6b9f3a2141',
 'v4160-ota-tx-2026-10-22/source-review/raw.py':'da17e505ec2b58cada40a80a12a645b7fa21c116ce76666544168f2c4ff6c6a7',
 'v4160-event-callback-2026-10-22/source-review/raw.py':'6d3c387695703e286429bcdb84a14833868ba6a9f37e03e78d3e1bd391388b7f'}


def need(value,message):
    if not value:raise ValueError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def context(root):
    modules=[]
    for slug,pin in PINS.items():
        p=next(p for p in (root/'apk-analysis'/('tsl9-'+slug),root/'analysis'/slug) if p.is_file())
        need(sha(p)==pin,'Pinned bounded static dependency '+slug)
        modules.append(runpy.run_path(str(p)))
    return dict(ELF=modules[0]['ELF'],base=modules[1]['decode'],extension=modules[2]['decode'])


def rows(raw,address,ctx):
    out=[];at=0
    while at<len(raw):
        try:
            row=ctx['extension'](raw[at:],address+at,ctx['base'])
        except ValueError:
            word=int.from_bytes(raw[at:at+4],'little')
            # Measured extra forms: RV32/C AND/OR, and signed halfword load.
            half=word&65535
            if half&0xfc63 in (0x8c61,0x8c41):
                reg=8+((half>>7)&7)
                row=dict(PC=address+at,bytes=2,raw_hex=raw[at:at+2].hex(),
                         op='and' if half&0x20 else 'or',
                         rd=reg,rs1=reg,rs2=8+((half>>2)&7),
                         immediate=None,target=None,memory_width=None)
            elif word&0x707f==0x1003:
                immediate=word>>20
                row=dict(PC=address+at,bytes=4,raw_hex=raw[at:at+4].hex(),op='lh',
                         rd=(word>>7)&31,rs1=(word>>15)&31,rs2=None,
                         immediate=immediate-4096 if immediate&2048 else immediate,
                         target=None,memory_width=16)
            else:
                need(at+4<=len(raw) and word&0xfe00707f in (0x7033,0x6033),
                     'Only measured extra RV32 AND/OR field form')
                row=dict(PC=address+at,bytes=4,raw_hex=raw[at:at+4].hex(),
                         op='and' if word&0x1000 else 'or',
                         rd=(word>>7)&31,rs1=(word>>15)&31,rs2=(word>>20)&31,
                         immediate=None,target=None,memory_width=None)
        need(row['bytes'] in (2,4) and at+row['bytes']<=len(raw) and
             row['raw_hex']==raw[at:at+row['bytes']].hex(),'Actual whole instruction fields')
        row['offset']=at;out.append(row);at+=row['bytes']
    need(at==len(raw),'Complete actual raw instruction coverage')
    return out
