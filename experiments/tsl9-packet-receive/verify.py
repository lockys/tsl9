#!/usr/bin/env python3
"""Compile/replay the v5 private packet regions. Never execute target code.

The result is an ET_REL component with two real unresolved providers. Four
JALs and two cross-region branches remain pending; there is no flashable BIN.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import runpy
import struct
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
BASE = 'experiments/tsl9-packet-receive/'
SOURCE = BASE + 'src/packet_receive.v5.c'
LINKER = BASE + 'component.ld'
READER = 'experiments/tsl9-spi-transfer-leaf/verify.py'
FIRMWARE = 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
PINS = {
    SOURCE: '0e42490f8d2cc17bf9e5ab414827ee7158777f132928c61502b300089aaa520d',
    LINKER: 'eddda2351acbdc4883caccbdc411e9f1d847ac1f6e134f055d9bd52dff702226',
    READER: '8c8eb8e01b9fc30eb7150682aa8848e47fe4a1254c6f87b05e657244a11b6de8',
    FIRMWARE: '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667',
}
TOOLS = {
    'clang.exe': '047dfde05acc6fcce5af669e25cd8d40b4f509b8842d151d6d8a43a1c6a35fd6',
    'ld.lld.exe': 'fe7f55c0c78b3d87f33b905a3874e10e872ca7beef53a8199d7ff9ac6641ec3f',
    'llvm-objdump.exe': 'de40d1188fe63ff373e1a5dd83a12e2cb4545ca3b314da16a476ecf072e5a0fa',
}
# The supported producer is the already-installed, pinned NDK Windows toolchain.
HEADER_PIN = '7ce5540d5fb6e8da9760928e76cbdd5ebef329d701ad598d30d8e6f9d5d78b34'
ORIGINAL_PIN = 'd823c819bbe92c3b7ee17c92411825549084d08dc32c36378d8e60d4915f40e2'
PROJECTION_PIN = '528b69f7ec290450aa7b0338bdfbf25b88571693b0f2142199ccdb37c34479f6'
ELF_PINS = {True: '394bc5852488b60d17f7ccebeb18cdd85df9952a2684df26df132a30bf931854',
            False: 'd22086e49e7a50eb80b022a814a77248024a6c02555dfae2229cc111d1909ae0'}
IR_PINS = {'c': '32d17a54f3e31fa7ec33638fc3ce826ef4819c4622aa4a7e7e04e8571e2fe2e3',
           'cpp': '41d7339b8ef9b33141e900ebe5eed94df57d632b6ae7d3ee43e2de7fd7f1102a'}
NAMES = ['tsl9_receive_buffer_entry_16a7c', 'tsl9_packet_receive_body', 'tsl9_packet_receive_finish_16afe']
REGIONS = [(NAMES[0], 0, 14), (NAMES[1], 14, 116), (NAMES[2], 130, 12)]
SPI = 'tsl9_spi_transfer_entry_16896'
RING = 'tsl9_ring_insert_entry_12bc8'
RELOCATIONS = [(34,17,SPI), (46,17,SPI), (52,17,SPI),
               (88,44,NAMES[2]), (106,16,NAMES[2]), (126,17,RING)]


def need(ok, message):
    if not ok:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


need(sha((ROOT/READER).read_bytes()) == PINS[READER], 'frozen ELF reader input')
_reader = runpy.run_path(str(ROOT/READER), run_name='packet_frozen_reader')
ELF, portable = _reader['ELF'], _reader['portable']


def signed(n, bits):
    return n - (1 << bits) if n & (1 << (bits-1)) else n


def decode(code):
    """Bounded static decoder for the 52 allowed packet instructions; no CPU model."""
    rows = []
    at = 0
    while at < len(code):
        need(at+2 <= len(code), 'short instruction')
        h = int.from_bytes(code[at:at+2], 'little')
        width = 4 if h & 3 == 3 else 2
        need(at+width <= len(code), 'instruction extent')
        w = int.from_bytes(code[at:at+width], 'little')
        ins = None
        if width == 4:
            op, rd, rs1, rs2, f3 = w&127, (w>>7)&31, (w>>15)&31, (w>>20)&31, (w>>12)&7
            imm = signed(w>>20,12)
            if op == 0x13 and f3 in (0,7): ins = ['addi' if f3==0 else 'andi',rd,rs1,imm]
            elif op == 0x37: ins = ['lui',rd,w&0xfffff000]
            elif op == 3 and f3 in (2,4): ins = ['lw' if f3==2 else 'lbu',rd,rs1,imm]
            elif op == 0x23 and f3 in (0,2):
                ins = ['sb' if f3==0 else 'sw',rs2,rs1,signed(((w>>25)<<5)|((w>>7)&31),12)]
            elif op == 0x63 and f3 in (1,6):
                d = ((w>>31)&1)<<12 | ((w>>25)&63)<<5 | ((w>>8)&15)<<1 | ((w>>7)&1)<<11
                ins = ['bne' if f3==1 else 'bltu',rs1,rs2,at+signed(d,13)]
            elif op == 0x6f:
                d = ((w>>31)&1)<<20 | ((w>>21)&1023)<<1 | ((w>>20)&1)<<11 | ((w>>12)&255)<<12
                ins = ['jal',rd,at+signed(d,21)]
        else:
            q, f3, rd, rs2 = h&3,h>>13,(h>>7)&31,(h>>2)&31
            ci = signed(((h>>12)&1)<<5 | (h>>2)&31,6)
            if h == 0x8082: ins = ['ret',1]
            elif q==1 and f3==0: ins = ['addi',rd,rd,ci]
            elif q==1 and f3==2: ins = ['addi',rd,0,ci]
            elif q==1 and f3==3 and rd==2:
                d = ((h>>12)&1)<<9 | ((h>>6)&1)<<4 | ((h>>5)&1)<<6 | ((h>>3)&3)<<7 | ((h>>2)&1)<<5
                ins = ['addi',2,2,signed(d,10)]
            elif q==0 and f3==0:
                d = ((h>>11)&3)<<4 | ((h>>7)&15)<<6 | ((h>>6)&1)<<2 | ((h>>5)&1)<<3
                ins = ['addi',8+((h>>2)&7),2,d]
            elif q==2 and f3==6:
                ins = ['sw',rs2,2,((h>>9)&15)<<2 | ((h>>7)&3)<<6]
            elif q==2 and f3==2:
                ins = ['lw',rd,2,((h>>12)&1)<<5 | ((h>>4)&7)<<2 | ((h>>2)&3)<<6]
            elif q==0 and f3==6:
                ins = ['sw',8+((h>>2)&7),8+((h>>7)&7),((h>>10)&7)<<3 | ((h>>6)&1)<<2 | ((h>>5)&1)<<6]
            elif q==2 and f3==4 and rd and rs2:
                ins = ['add',rd,rd,rs2] if (h>>12)&1 else ['mv',rd,rs2]
            elif q==2 and f3==0: ins = ['slli',rd,rd,(h>>2)&31]
            elif q==1 and f3==4:
                r = 8+((h>>7)&7)
                if (h>>10)&3==0: ins = ['srli',r,r,(h>>2)&31]
                elif (h>>10)&3==2: ins = ['andi',r,r,ci]
                elif (h>>10)&3==3 and not (h>>12)&1 and (h>>5)&3==2:
                    ins = ['or',r,r,8+((h>>2)&7)]
            elif q==1 and f3==7:
                d = ((h>>12)&1)<<8 | ((h>>10)&3)<<3 | ((h>>5)&3)<<6 | ((h>>3)&3)<<1 | ((h>>2)&1)<<5
                ins = ['bnez',8+((h>>7)&7),at+signed(d,9)]
        need(ins is not None, 'forbidden/unknown packet instruction at '+str(at))
        rows.append(dict(offset=at,width=width,raw=code[at:at+width].hex(),instruction=ins))
        at += width
    return rows


EXPECTED = [
    (0,['addi',2,2,-48]), (2,['sw',9,2,36]), (4,['lui',15,0x40011000]),
    (8,['sw',1,2,44]), (10,['sw',8,2,40]), (12,['sw',18,2,32]),
    (14,['addi',14,0,1]), (16,['mv',9,10]), (18,['addi',15,15,-2048]),
    (22,['bne',10,14,28]), (26,['addi',14,0,16]), (28,['sw',14,15,20]),
    (30,['addi',10,0,3]), (32,['sw',11,2,12]), (34,['jal',1,0x16896-0x16a7c]),
    (38,['lw',11,2,12]), (40,['addi',8,0,0]), (42,['addi',18,0,13]),
    (44,['mv',10,11]), (46,['jal',1,0x16896-0x16a7c]), (50,['addi',10,0,0]),
    (52,['jal',1,0x16896-0x16a7c]), (56,['addi',15,2,16]), (58,['add',15,15,8]),
    (60,['sb',10,15,0]), (64,['addi',8,8,1]), (66,['bne',8,18,50]),
    (70,['lui',15,0x40011000]), (74,['addi',14,0,17]), (76,['sw',14,15,-2032]),
    (80,['lbu',15,2,17]), (84,['andi',14,15,24]), (88,['bnez',14,130]),
    (90,['lbu',12,2,20]), (94,['addi',13,0,7]), (96,['andi',12,12,15]),
    (98,['addi',14,12,-1]), (102,['andi',14,14,255]), (106,['bltu',13,14,130]),
    (110,['lbu',10,2,16]), (114,['srli',15,15,5]), (116,['mv',13,9]),
    (118,['slli',10,10,3]), (120,['addi',11,2,21]), (124,['or',10,10,15]),
    (126,['jal',1,0x12bc8-0x16a7c]), (130,['lw',1,2,44]), (132,['lw',8,2,40]),
    (134,['lw',9,2,36]), (136,['lw',18,2,32]), (138,['addi',2,2,48]), (140,['ret',1]),
]


def original():
    raw = (ROOT/FIRMWARE).read_bytes()
    need(len(raw)==76800 and sha(raw)==PINS[FIRMWARE], 'complete original firmware identity')
    code = raw[0xea7c:0xeb0a]
    need(sha(code)==ORIGINAL_PIN and len(code)==142, 'original packet span')
    need([(x['offset'],x['instruction']) for x in decode(code)]==EXPECTED, 'all 52 original typed operations')
    return code


def projection(code):
    spans = [(o,2 if t==44 else 4) for o,t,_ in RELOCATIONS]
    return bytes(b for i,b in enumerate(code) if not any(o<=i<o+n for o,n in spans))


def elf_contract(e, native, official):
    need(e.header[0]==1 and e.header[3:5]==[0,0] and e.header[6]==1 and not e.program_headers, 'ET_REL RV32 RVC, no load/entry')
    funcs = [s for s in e.symbols if s['info']&15==2]
    need(sorted(s['name'] for s in funcs)==sorted(NAMES), 'exact genuine FUNC names')
    global_abs = [s for s in e.symbols if s['info']>>4 and s['section']==0xfff1]
    need(not global_abs, 'no ABS providers')
    und = [s for s in e.symbols if s['section']==0 and s['name']]
    need(sorted(s['name'] for s in und)==sorted([SPI,RING]) and all(s['info']==16 and s['value']==s['size']==0 for s in und), 'two actual UND provider records')
    starts = {}; code = b''
    if native:
        for name,start,size in REGIONS:
            f = next(s for s in funcs if s['name']==name);sec = e.sections[f['section']]
            need(f['info']==18 and f['other']==0 and f['value']==0 and f['size']==size, 'native FUNC shape '+name)
            need(sec['name']=='.text.'+name and sec['type']==1 and sec['flags']==6 and sec['size']==size and sec['address']==0 and sec['align']==2, 'native exact owner '+name)
            starts[sec['index']]=start;code += e.data(sec)
        need(len(starts)==3, 'separate native architectural regions')
    else:
        sec = e.section('.packet')
        need(sec['type']==1 and sec['flags']==6 and sec['size']==142 and sec['address']==0 and sec['align']==2, 'actual partial packet region')
        starts[sec['index']]=0;code = e.data(sec)
        for name,start,size in REGIONS:
            f = next(s for s in funcs if s['name']==name)
            need(f['info']==18 and f['other']==0 and f['section']==sec['index'] and f['value']==start and f['size']==size, 'partial genuine FUNC adjacency '+name)
    allocated = [s for s in e.sections if s['flags']&2 and s['size']]
    need({s['index'] for s in allocated}==set(starts), 'no extra allocated data/code or padding')
    need(len(code)==142, '142 genuine file bytes')
    rels = []
    for rel in e.relocations:
        need(rel['section'] in starts, 'RELA owner')
        target = e.symbols[rel['symbol']]
        rels.append((starts[rel['section']]+rel['offset'],rel['type'],target['name']))
        need(rel['addend']==0, 'zero addend')
        if target['name']==NAMES[2]:
            need(target['info']==18 and target['section'] in starts and starts[target['section']]+target['value']==130 and target['size']==12, 'real defined finish edge')
        else:
            need(target['name'] in (SPI,RING) and target['section']==0, 'honest unresolved call')
    need(sorted(rels)==RELOCATIONS, 'all six exact relocation sites/types/targets')
    rows = decode(code);need(len(rows)==52, '52 instruction boundaries')
    by = {r['offset']:r for r in rows}
    for offset,kind,_ in RELOCATIONS:
        expected = ['jal',1,offset] if kind==17 else ['bnez',14,offset] if kind==44 else ['bltu',13,14,offset]
        need(by[offset]['instruction']==expected, 'pending immediate and physical operands '+str(offset))
    pending = {o: (['jal',1,o] if t==17 else ['bnez',14,o] if t==44 else ['bltu',13,14,o]) for o,t,_ in RELOCATIONS}
    need([(r['offset'],r['instruction']) for r in rows]==[(o,pending.get(o,ins)) for o,ins in EXPECTED], 'all 52 native typed operations with only pending control targets')
    need([(r['offset'],r['width']) for r in rows]==[(r['offset'],r['width']) for r in decode(official)], 'complete original instruction widths/offsets')
    projected = projection(code)
    need(len(projected)==120 and sha(projected)==PROJECTION_PIN and projected==projection(official), 'all 120 noncontrol bytes original equal')
    need(code[130:]==bytes.fromhex('b25022549254025945618280'), 'single original fresh-restore sequence')
    need(code!=official, 'pending component must not masquerade as resolved bytes')
    # Supplement the finite semantic/ownership gates with the entire measured
    # ELF, including local mapping symbols, headers and nonallocated metadata.
    need(sha(e.raw)==ELF_PINS[native], 'whole measured ELF metadata/locals/sections')
    return dict(elf_sha256=sha(e.raw),code_bytes=142,instructions=52,regions=[dict(name=n,offset=o,size=z) for n,o,z in REGIONS],
                code_hex=code.hex(),relocations=[dict(offset=o,type=t,target=n,addend=0,pending=True) for o,t,n in RELOCATIONS],
                undefined_providers=[SPI,RING],noncontrol_bytes=120,noncontrol_sha256=sha(projected),noncontrol_equal_original=True,
                full_resolved_bytes_equal_original=False,operations=rows)


def ir_contract(text, language):
    need(len(re.findall(r'^define ',text,re.M))==3 and not re.search(r'^declare ',text,re.M), 'three IR regions, no helpers')
    for n in NAMES: need('@'+n+'(' in text, 'IR FUNC '+n)
    need('load volatile' not in text and len(re.findall(r'store volatile i32 ',text))==2 and len(re.findall(r'store volatile i8 ',text))==1, 'C volatile GPIO32/SPI-buffer8 widths')
    for token in ['and i32','shl i32','lshr i32','or i32']: need(token in text, 'C arithmetic '+token)
    spi_lines=[s for s in text.splitlines() if 'asm sideeffect "jal ra, '+SPI in s]
    need(len(spi_lines)==3, 'three static SPI call sites')
    match=re.search(r'^\s*(%\d+) = .*asm sideeffect "jal ra, '+SPI+r'.*\(i32 0\)',text,re.M)
    need(match is not None, 'fresh zero-poll SPI A0 output')
    spi_value=match.group(1)
    for label,constraint in [('header','{x14},{x15},{x10},~{memory}'),('length','{x13},{x14},{x10},{x12},{x15},~{memory}')]:
        line=next((s for s in text.splitlines() if 'asm sideeffect ".Lpacket_'+label+'_reject:' in s),'')
        need(constraint in line and 'i32 '+spi_value in line, 'physical reject A0 port '+label)
    need('"={x11},{x11},~{memory}"' in next(s for s in text.splitlines() if 'asm sideeffect "li s0, 0' in s), 'A1 dependency orders S0/S2 init before address transfer')
    ring_line=next(s for s in text.splitlines() if 'asm sideeffect "jal ra, '+RING in s)
    ring_value=re.search(r'(%\d+) = ',ring_line).group(1)
    extracted=re.search(r'(%\d+) = extractvalue \{ i32, i32, i32, i32 \} '+re.escape(ring_value)+r', 0',text)
    need(extracted is not None, 'ring physical A0 extraction')
    need('asm sideeffect "", "{x10},~{memory}"(i32 '+extracted.group(1)+')' in text, 'fallthrough consumes ring A0 instead of SPI A0')
    need(text.count('asm sideeffect "lw ra, 44(sp)')==1, 'one restore IR region')
    need('asm sideeffect "sw a1, 12(sp)\\0A", "{x11},~{memory}"' in text, 'incoming A1 explicitly live at slot save')
    incoming=re.search(r'(%\d+) = extractvalue \{ i32, i32, i32 \} %1, 2',text)
    need(incoming is not None and 'asm sideeffect "sw a1, 12(sp)\\0A", "{x11},~{memory}"(i32 '+incoming.group(1)+')' in text, 'incoming A1 SSA reaches the actual save')
    need(re.findall(r'= and i32 %\d+, (\d+)',text)==['24','15','255'], 'ordered header/DLC/unsigned-underflow masks')
    need(re.search(r'= add nsw i32 %\d+, -1',text) is not None and re.search(r'= lshr i32 %\d+, 5',text) is not None and re.search(r'= shl i32 %\d+, 3',text) is not None, 'DLC decrement and ID shifts')
    lines=text.splitlines()
    need(lines[0].startswith('; ModuleID = ') and lines[1].startswith('source_filename = ') and all('packet_receive.v5.c' in x for x in lines[:2]), 'two producer path-only IR header fields')
    normalized='\n'.join(lines[2:])+'\n'
    need(sha(normalized.encode())==IR_PINS[language], 'complete normalized IR including constants/SSA/order/attributes')
    return dict(three_real_regions=True,C_GPIO_store_bits=32,C_buffer_store_bits=8,reject_A0=spi_value,success_A0=extracted.group(1),language=language,ordinary_C_ABI=False,
                normalized_IR_sha256=sha(normalized.encode()),normalization='Exclude only the two producer path header lines; normalize line endings to LF.')


def flags(language):
    value=['--target=riscv32-unknown-elf','-march=rv32imac_zicsr','-mabi=ilp32','-Oz','-mllvm','-enable-machine-outliner=never','-ffreestanding','-fno-builtin','-fno-stack-protector','-fno-unwind-tables','-fno-asynchronous-unwind-tables','-mno-relax','-ffunction-sections','-fdata-sections','-Wall','-Wextra','-Werror']
    value += ['-ffixed-x'+str(i) for i in range(1,32) if i not in (10,11,12,13,14,15)]
    return value+(['-x','c','-std=c11'] if language=='c' else ['-x','c++','-std=c++17','-fno-exceptions'])


def recipes(root, llvm, out, language):
    clang=str(llvm/'clang.exe');objdump=str(llvm/'llvm-objdump.exe');common=flags(language)
    return [
        ('compile',[clang]+common+['-MD','-MF',str(out/'native.d'),'-MT',str(out/'native.o'),'-c',str(root/SOURCE),'-o',str(out/'native.o')]),
        ('IR',[clang]+common+['-S','-emit-llvm',str(root/SOURCE),'-o',str(out/'native.ll')]),
        ('object',[objdump,'--mattr=+m,+a,+c,+zicsr','-d','-r','-t','-h',str(out/'native.o')]),
        ('partial-link',[str(llvm/'ld.lld.exe'),'-r','--no-relax','-T',str(root/LINKER),str(out/'native.o'),'-o',str(out/'PACKET-PROVIDERS-OPEN.o')]),
        ('partial-object',[objdump,'--mattr=+m,+a,+c,+zicsr','-d','-r','-t','-h',str(out/'PACKET-PROVIDERS-OPEN.o')]),
    ]


def inputs(root, llvm):
    items=[(root/n,pin) for n,pin in PINS.items()]+[(Path(__file__).resolve(),None),(llvm.parent/'lib/clang/18/include/stdint.h',HEADER_PIN)]+[(llvm/n,pin) for n,pin in TOOLS.items()]
    records=[]
    for path,pin in items:
        raw=path.read_bytes();need(pin is None or sha(raw)==pin,'pinned input '+path.name)
        records.append(dict(path=portable(str(path),root,llvm),size=len(raw),sha256=sha(raw)))
    return records


def md_contract(raw, root, llvm, out):
    t=raw.replace('\\\n',' ').replace('\\\r\n',' ').replace('\\ ','\x01').replace('\\','/')
    target=str(out/'native.o').replace('\\','/');need(t.startswith(target+':'), 'exact MD target')
    deps=[x.replace('\x01',' ') for x in t[len(target)+1:].split()]
    want=[str(root/SOURCE).replace('\\','/'),str(llvm.parent/'lib/clang/18/include/stdint.h').replace('\\','/')]
    need(deps==want,'complete MD source/header closure')
    return portable(want,root,llvm)


def negatives(native, linked, text, language, official, md, root, llvm, out):
    controls=[]
    def reject(label, call):
        try: call()
        except (ValueError,StopIteration): controls.append(label);return
        raise ValueError('negative control accepted: '+label)
    def flip(e, where):
        b=bytearray(e.raw);b[where]^=1;return ELF(b)
    body=next(s for s in native.symbols if s['name']==NAMES[1]);bs=native.sections[body['section']]
    for offset in [16,28,32,40,42,60,76,80,96,98,102,116,120,124,130,138]:
        region=next((n,o,z) for n,o,z in REGIONS if o<=offset<o+z)
        f=next(s for s in native.symbols if s['name']==region[0]);sec=native.sections[f['section']]
        reject('native-code-'+str(offset),lambda sec=sec,region=region,offset=offset:elf_contract(flip(native,sec['offset']+offset-region[1]),True,official))
    for i,rel in enumerate(native.relocations):
        table=next(s for s in native.sections if s['type']==4 and s['info']==rel['section'])
        b=bytearray(native.raw);struct.pack_into('<i',b,table['offset']+i*12+8,1)
        reject('nonzero-relocation-addend-'+str(i),lambda b=b:elf_contract(ELF(b),True,official))
    for offset,kind,_ in RELOCATIONS:
        # Change only the pending immediate field, retaining the opcode/registers.
        b=bytearray(linked.raw);sec=linked.section('.packet');at=sec['offset']+offset
        if kind==17:b[at+1]^=0x10
        elif kind==44:b[at]^=0x08
        else:b[at+1]^=0x01
        reject('applied-or-wrong-pending-immediate-'+str(offset),lambda b=b:elf_contract(ELF(b),False,official))
    symtab=native.section('.symtab')
    for name,field,value in [(NAMES[2],'size',14),(NAMES[2],'section',0xfff1),(NAMES[1],'value',2),(SPI,'section',0xfff1),(RING,'section',0xfff1)]:
        s=next(x for x in native.symbols if x['name']==name);b=bytearray(native.raw)
        at=symtab['offset']+16*s['index'];struct.pack_into('<H' if field=='section' else '<I',b,at+({'section':14,'size':8,'value':4}[field]),value)
        reject('symbol-'+name+'-'+field,lambda b=b:elf_contract(ELF(b),True,official))
    reject('IR-reject-A0-contract',lambda:ir_contract(text.replace('{x14},{x15},{x10},~{memory}','{x14},{x15},~{memory}'),language))
    reject('IR-success-A0-contract',lambda:ir_contract(text.replace('asm sideeffect "", "{x10},~{memory}"','asm sideeffect "", "~{memory}"'),language))
    reject('IR-store-width',lambda:ir_contract(text.replace('store volatile i8 ','store volatile i16 '),language))
    reject('IR-header-mask',lambda:ir_contract(text.replace('and i32 %35, 24','and i32 %35, 16'),language))
    reject('IR-DLC-mask',lambda:ir_contract(text.replace('and i32 %43, 15','and i32 %43, 7'),language))
    reject('IR-incoming-A1-SSA',lambda:ir_contract(text.replace('"{x11},~{memory}"(i32 %4)','"{x11},~{memory}"(i32 %2)'),language))
    marker=next(s for s in native.symbols if s['name']=='$d.4');b=bytearray(native.raw)
    struct.pack_into('<I',b,symtab['offset']+16*marker['index']+4,1)
    reject('ELF-local-mapping-symbol-value',lambda:elf_contract(ELF(b),True,official))
    reject('MD-missing-header',lambda:md_contract(md.splitlines()[0],root,llvm,out))
    return controls


def evaluate(root, llvm, out, language):
    before=inputs(root,llvm);official=original()
    native=ELF(out/'native.o');linked=ELF(out/'PACKET-PROVIDERS-OPEN.o')
    ns=elf_contract(native,True,official);ls=elf_contract(linked,False,official)
    need(ns['code_hex']==ls['code_hex'], 'actual partial link preserves exact native projection')
    text=(out/'native.ll').read_text(encoding='utf-8');ir=ir_contract(text,language)
    md=(out/'native.d').read_text(encoding='utf-8');deps=md_contract(md,root,llvm,out)
    expected=[dict(label=n,argv=portable(a,root,llvm),returncode=0) for n,a in recipes(root,llvm,out,language)]
    need(json.loads((out/'recipes.json').read_text())==expected,'complete exact producer recipes')
    files=sorted(['native.o','native.ll','native.d','PACKET-PROVIDERS-OPEN.o','recipes.json']+[n+'.log' for n,_ in recipes(root,llvm,out,language)])
    need(sorted(p.name for p in out.iterdir() if p.name!='verification.json')==files and all(p.is_file() and not p.is_symlink() for p in out.iterdir()),'exact artifact inventory')
    for n in ['compile','IR','partial-link']:need(not (out/(n+'.log')).read_bytes(), 'successful empty compiler/linker diagnostic '+n)
    for n in ['object','partial-object']:
        log=(out/(n+'.log')).read_text();need(all(x in log for x in NAMES+[SPI,RING]),'retained disassembly coverage '+n)
    controls=negatives(native,linked,text,language,official,md,root,llvm,out)
    artifacts=[dict(path=portable(str(out/n),root,llvm),size=(out/n).stat().st_size,sha256=sha((out/n).read_bytes())) for n in files]
    need(before==inputs(root,llvm),'stable source/tool/header inputs')
    record=dict(schema='TSL9-packet-receive-native-v5',language=language,root='${TSL9_ROOT}',llvm_bin='${LLVM_BIN}',out_dir=portable(str(out),root,llvm),
                firmware_ready=False,target_executed=False,ISA_emulated=False,inputs=before,
                original=dict(base=0x8000,start=0x16a7c,end=0x16b0a,bytes=142,instructions=52,sha256=ORIGINAL_PIN),
                native=ns,partial_link=ls,ir=ir,md_dependencies=deps,recipes=expected,artifacts=artifacts,negative_controls=controls,
                static_contract=dict(frame_bytes=48,selector='channel == 1 ? 16 : 1',incoming_A1_slot=12,buffer_start=16,
                  loop_condition='then-live S0/S2 after opaque SPI call',SPI_data_iterations_if_provider_preserves_S0_S2=13,
                  cleanup_GPIO_before_validation=True,header_reject_mask=24,DLC_mask=15,DLC_allowed=[1,8],
                  ID='(buffer[0] << 3) | (buffer[1] >> 5)',payload_SP_offset=21,
                  reject_result='last SPI A0',success_result='then-live ring A0',ring_continuation=0x16afe,
                  unique_fresh_restore=['RA from SP+44','S0 from SP+40','S1 from SP+36','S2 from SP+32','SP += 48','RET']),
                limitations=['Static native compilation/IR/ELF decode only; no target/ISA/MMIO execution.',
                  'Three FUNC symbols are private architectural regions, not ordinary independently callable C ABI functions.',
                  'All six control relocations are pending in actual ET_REL bytes. Two external providers remain unresolved.',
                  'Ring/resident ABI, IRQ/fault interleaving, physical memory/peripheral identity and full image placement remain unproved.',
                  'No flashable BIN, whole firmware equivalence, OTA acceptance or hardware functionality is claimed.'])
    encoded=json.dumps(record,ensure_ascii=False,sort_keys=True,indent=2)+'\n'
    need(not re.search(r'(?i)[a-z]:[/\\]|/(?:users|home)/',encoded),'portable receipt contains host path')
    return record,encoded


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    action=parser.add_mutually_exclusive_group(required=True);action.add_argument('--out-dir',type=Path);action.add_argument('--replay',type=Path)
    parser.add_argument('--language',choices=['c','cpp']);parser.add_argument('--llvm-bin',type=Path,default=Path(os.environ.get('USERPROFILE',str(Path.home())))/'AppData/Local/Android/Sdk/ndk/27.1.12297006/toolchains/llvm/prebuilt/windows-x86_64/bin')
    parser.add_argument('--require-firmware-ready',action='store_true');args=parser.parse_args();llvm=args.llvm_bin.resolve()
    if args.replay:
        receipt=args.replay.resolve();out=receipt.parent;saved=json.loads(receipt.read_text(encoding='utf-8'));language=saved['language']
        need(args.language is None or args.language==language,'replay language')
        record,encoded=evaluate(ROOT,llvm,out,language)
        need(saved==record and receipt.read_bytes()==encoded.encode(),'entire receipt equality and portable LF')
    else:
        need(args.language is not None,'--language required');language=args.language;out=args.out_dir.resolve()
        owned=ROOT/BASE/'build';need(out.is_relative_to(owned) and out!=owned and not out.exists(),'fresh owned output directory')
        before=inputs(ROOT,llvm);out.mkdir(parents=True);rs=[]
        for label,argv in recipes(ROOT,llvm,out,language):
            p=subprocess.run(argv,cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,check=False)
            (out/(label+'.log')).write_bytes(p.stdout);rs.append(dict(label=label,argv=portable(argv,ROOT,llvm),returncode=p.returncode))
            need(p.returncode==0,'native recipe failed '+label)
        (out/'recipes.json').write_bytes((json.dumps(rs,indent=2)+'\n').encode())
        need(before==inputs(ROOT,llvm),'stable build inputs');record,encoded=evaluate(ROOT,llvm,out,language)
        (out/'verification.json').write_bytes(encoded.encode())
    print(json.dumps(dict(result='PASS',language=language,receipt_sha256=sha(encoded.encode()),elfs=2,bytes=142,instructions=52,noncontrol_bytes=120,pending_relocations=6,controls=len(record['negative_controls']),firmware_ready=False)))
    if args.require_firmware_ready:
        print('REJECTED: unresolved providers and private component evidence; firmware_ready=false.',file=sys.stderr);return 1
    return 0


if __name__=='__main__':
    try: sys.exit(main())
    except (ValueError,KeyError,StopIteration) as exc:
        print('FAIL: '+str(exc),file=sys.stderr);sys.exit(1)
