#!/usr/bin/env python3
"""Build/replay five private ring regions; never execute emitted target code.

Native ET_REL branches remain pending. The nominal ELF resolves those three
branches and reproduces 92 original bytes, but its indirect resident provider,
physical memory, IRQ/fault behavior and complete firmware remain unproved.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import runpy
import struct
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
BASE = 'experiments/tsl9-ring-insert/'
SOURCE = BASE+'src/ring_insert.v3.c'
LINKER = BASE+'component.ld'
PROBE = BASE+'probe.py'
READER = 'experiments/tsl9-spi-transfer-leaf/verify.py'
FIRMWARE = 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
PINS = {
    SOURCE:'5ad18a4a6cb607edd0fa26e475a58b544c3bbdef6929a3b9d53bd0c834c2262d',
    LINKER:'4c90c59b4ced05f2e2eae0e70b4a6951fd62ee83177edbc8d5ff1e5055b4c24e',
    PROBE:'5d1dca31cf969c5b2e17d3e3afa4f956736cdcc972d501697d8cf5b4de649574',
    READER:'8c8eb8e01b9fc30eb7150682aa8848e47fe4a1254c6f87b05e657244a11b6de8',
    FIRMWARE:'0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667',
}
TOOLS = {'clang.exe':'047dfde05acc6fcce5af669e25cd8d40b4f509b8842d151d6d8a43a1c6a35fd6',
         'ld.lld.exe':'fe7f55c0c78b3d87f33b905a3874e10e872ca7beef53a8199d7ff9ac6641ec3f',
         'llvm-objdump.exe':'de40d1188fe63ff373e1a5dd83a12e2cb4545ca3b314da16a476ecf072e5a0fa'}
HEADER_PIN='7ce5540d5fb6e8da9760928e76cbdd5ebef329d701ad598d30d8e6f9d5d78b34'
CODE_PIN='d3d9af9bcec8af13dfd424d3bfb2bd79f8fc3fd61308cb6ec0d7c18b1b78b13b'
ELF_PINS={True:'9e534a64569a4a28bcc4e7aded98b624f5b6902b58f8d657b422139760f9742c',
          False:'f41ea62095dee587f562cd3e1a9341b105187b097107413bebe6dc71f44b491c'}
IR_PINS={'c':'56a1a7d60d21c9ac5b018d6495105f9acc93c885d0625c0807a247ba22760b29',
         'cpp':'6a7c7e51673d5d4b36cfc522d5f4b9a9a8d215b93230b0220dbd315822310fa4'}
ADDRESS=0x12bc8
NAMES=['tsl9_ring_insert_entry_12bc8','tsl9_ring_init_12bd0','tsl9_ring_scan_12be0','tsl9_ring_finish_12c12','tsl9_ring_advance_12c1c']
STARTS=[0,8,24,74,84]
SIZES=[8,16,50,10,8]
RELOCATIONS=[(42,16,NAMES[4]),(86,16,NAMES[2]),(90,45,NAMES[3])]


def need(ok,message):
    if not ok:raise ValueError(message)


def sha(raw):return hashlib.sha256(raw).hexdigest()


for _name in (READER,PROBE):need(sha((ROOT/_name).read_bytes())==PINS[_name],'frozen imported helper '+_name)
_reader=runpy.run_path(str(ROOT/READER),run_name='ring_frozen_reader')
ELF,portable=_reader['ELF'],_reader['portable']
_probe=runpy.run_path(str(ROOT/PROBE),run_name='ring_frozen_flags')
flags=_probe['flags']


def signed(v,n):return v-(1<<n) if v&(1<<(n-1)) else v


def decode(code):
    """Bounded RV32IMC decoder, not execution or ISA emulation."""
    rows=[];at=0
    while at<len(code):
        need(at+2<=len(code),'short instruction')
        h=int.from_bytes(code[at:at+2],'little');width=4 if h&3==3 else 2
        need(at+width<=len(code),'wide instruction extent')
        w=int.from_bytes(code[at:at+width],'little');ins=None
        if width==4:
            op=w&127;rd=(w>>7)&31;rs1=(w>>15)&31;rs2=(w>>20)&31;f3=(w>>12)&7;f7=w>>25;imm=signed(w>>20,12)
            if op==0x13 and f3==0:ins=['addi',rd,rs1,imm]
            elif op==0x13 and f3==5 and f7==0:ins=['srli',rd,rs1,(w>>20)&31]
            elif op==0x17:ins=['auipc',rd,w&0xfffff000]
            elif op==0x37:ins=['lui',rd,w&0xfffff000]
            elif op==0x33 and f3==0 and f7 in (0,1):ins=['mul' if f7 else 'add',rd,rs1,rs2]
            elif op==3 and f3==5:ins=['lhu',rd,rs1,imm]
            elif op==0x23 and f3 in (0,1):ins=['sb' if f3==0 else 'sh',rs2,rs1,signed((w>>25)<<5|((w>>7)&31),12)]
            elif op==0x63 and f3==1:
                d=((w>>31)&1)<<12|((w>>7)&1)<<11|((w>>25)&63)<<5|((w>>8)&15)<<1
                ins=['bne',rs1,rs2,at+signed(d,13)]
        else:
            q=h&3;f3=h>>13;rd=(h>>7)&31;rs2=(h>>2)&31;ci=signed(((h>>12)&1)<<5|((h>>2)&31),6)
            if h==0x8082:ins=['ret',1]
            elif q==1 and f3==0:ins=['addi',rd,rd,ci]
            elif q==1 and f3==2:ins=['addi',rd,0,ci]
            elif q==2 and f3==6:ins=['sw',rs2,2,((h>>9)&15)<<2|((h>>7)&3)<<6]
            elif q==2 and f3==2:ins=['lw',rd,2,((h>>12)&1)<<5|((h>>4)&7)<<2|((h>>2)&3)<<6]
            elif q==0 and f3==2:ins=['lw',8+((h>>2)&7),8+((h>>7)&7),((h>>10)&7)<<3|((h>>6)&1)<<2|((h>>5)&1)<<6]
            elif q==2 and f3==0 and not (h>>12)&1:ins=['slli',rd,rd,(h>>2)&31]
            elif q==2 and f3==4 and (h>>12)&1 and not rs2 and rd:ins=['jalr',1,rd,0]
            elif q==2 and f3==4 and rs2 and rd:ins=['add',rd,rd,rs2] if (h>>12)&1 else ['mv',rd,rs2]
            elif q==1 and f3==5:
                d=((h>>12)&1)<<11|((h>>11)&1)<<4|((h>>9)&3)<<8|((h>>8)&1)<<10|((h>>7)&1)<<6|((h>>6)&1)<<7|((h>>3)&7)<<1|((h>>2)&1)<<5
                ins=['j',at+signed(d,12)]
        need(ins is not None,'forbidden/unknown ring instruction at '+str(at))
        rows.append(dict(offset=at,width=width,raw=code[at:at+width].hex(),instruction=ins));at+=width
    return rows


EXPECTED=[(0,['addi',2,2,-16]),(2,['sw',1,2,12]),(4,['sw',8,2,8]),(6,['sw',9,2,4]),
 (8,['addi',15,0,0]),(10,['auipc',17,0x1fff9000]),(14,['addi',17,17,1126]),(18,['addi',28,0,12]),(20,['addi',6,0,32]),
 (24,['mul',14,15,28]),(28,['add',8,17,14]),(32,['lhu',16,8,0]),(36,['slli',16,16,16]),(38,['srli',16,16,16]),
 (42,['bne',16,0,84]),(46,['sh',10,8,0]),(50,['sb',12,8,2]),(54,['lui',15,0x40000]),(58,['lw',15,15,76]),
 (60,['addi',14,14,3]),(62,['mv',9,13]),(64,['add',10,17,14]),(68,['jalr',1,15,0]),(70,['sb',9,8,11]),
 (74,['lw',1,2,12]),(76,['lw',8,2,8]),(78,['lw',9,2,4]),(80,['addi',2,2,16]),(82,['ret',1]),
 (84,['addi',15,15,1]),(86,['bne',15,6,24]),(90,['j',74])]
WIDTHS=[2,2,2,2,2,4,4,2,4,4,4,4,2,4,4,4,4,4,2,2,2,4,2,4,2,2,2,2,2,2,4,2]


def original():
    raw=(ROOT/FIRMWARE).read_bytes();need(len(raw)==76800 and sha(raw)==PINS[FIRMWARE],'complete official firmware')
    code=raw[0xabc8:0xac24];need(len(code)==92 and sha(code)==CODE_PIN,'official ring92B identity')
    rows=decode(code);need([(r['offset'],r['instruction']) for r in rows]==EXPECTED and [r['width'] for r in rows]==WIDTHS,'all32 original typed operations/widths')
    return code


def code_contract(code,native,official,full=True):
    rows=decode(code);pending={42:['bne',16,0,42],86:['bne',15,6,86],90:['j',90]}
    need([(r['offset'],r['instruction']) for r in rows]==[(o,pending.get(o,i) if native else i) for o,i in EXPECTED],'all32 typed operations/order/physical registers/control targets')
    need(len(code)==92 and [r['width'] for r in rows]==WIDTHS,'exact92B32i instruction boundaries')
    if full:
        if native:
            def projection(b):return bytes(v for i,v in enumerate(b) if not any(o<=i<o+(2 if t==45 else 4) for o,t,n in RELOCATIONS))
            need(projection(code)==projection(official),'82 noncontrol bytes original equal')
        else:need(code==official and sha(code)==CODE_PIN,'full nominal92B original equality')
    return rows


def elf_contract(e,native,official,full=True):
    need(e.header==([1,243,1,0,0,912,1,52,0,0,40,15,1] if native else [2,243,1,ADDRESS,52,3524,1,52,32,4,40,6,4]),'exact RV32 RVC ELF header/entry')
    need(e.program_headers==([] if native else [[6,52,73780,73780,128,128,4,4],[1,0,73728,73728,180,180,4,4096],[1,3016,ADDRESS,ADDRESS,92,92,5,4096],[1685382481,0,0,0,0,0,6,0]]),'exact nominal program headers')
    funcs=[s for s in e.symbols if s['info']&15==2]
    need(sorted(s['name'] for s in funcs)==sorted(NAMES),'exact five genuine FUNC symbols')
    need(not [s for s in e.symbols if s['name'] and s['section']==0],'no UND symbols')
    need(not [s for s in e.symbols if s['info']>>4 and s['section']==0xfff1],'no global ABS providers')
    need(all(s['info']==18 and s['name'] in NAMES for s in e.symbols if s['info']>>4),'only expected global FUNC definitions')
    starts={};code=b''
    if native:
        for name,start,size in zip(NAMES,STARTS,SIZES):
            f=next(s for s in funcs if s['name']==name);sec=e.sections[f['section']]
            need((f['value'],f['size'],f['info'],f['other'])==(0,size,18,0),'native genuine FUNC value/size/binding')
            need((sec['name'],sec['type'],sec['size'],sec['flags'],sec['address'],sec['align'])==('.text.'+name,1,size,6,0,2),'native separate region owner/AX/size/alignment')
            starts[sec['index']]=start;code+=e.data(sec)
        need(len(starts)==5,'five separate native sections')
    else:
        sec=e.section('.ring');need((sec['type'],sec['size'],sec['flags'],sec['address'],sec['align'])==(1,92,6,ADDRESS,2),'nominal ring placement')
        starts[sec['index']]=0;code=e.data(sec)
        for name,start,size in zip(NAMES,STARTS,SIZES):
            f=next(s for s in funcs if s['name']==name)
            need((f['value'],f['size'],f['info'],f['other'],f['section'])==(ADDRESS+start,size,18,0,sec['index']),'nominal genuine FUNC adjacency/ownership')
    need({s['index'] for s in e.sections if s['flags']&2 and s['size']}==set(starts),'only five native AX / one nominal AX allocation')
    need(not [s for s in e.sections if s['type']==8],'no invented NOBITS data')
    rels=[]
    for r in e.relocations:
        need(r['section'] in starts and r['addend']==0,'owned RELA site and zero addend')
        target=e.symbols[r['symbol']]
        need(target['info']==18 and target['name'] in NAMES and target['section'] in starts,'RELA target genuine defined FUNC')
        target_start=STARTS[NAMES.index(target['name'])]
        need(starts[target['section']]+target['value']==target_start and target['size']==SIZES[NAMES.index(target['name'])],'defined target value/owner')
        rels.append((starts[r['section']]+r['offset'],r['type'],target['name']))
    need(rels==(RELOCATIONS if native else []),'exact three native defined relocations / no nominal relocations')
    rows=code_contract(code,native,official,full)
    # Fixed AUIPC source is valid only at the verified nominal PC, not an
    # arbitrary partial-link placement. This does not prove physical RAM.
    derived=((ADDRESS+10)+0x1fff9000+1126)&0xffffffff
    need(derived==0x2000c038 and ADDRESS+68+2==0x12c0e,'PC-derived table and physical JALR RA')
    if full:need(sha(e.raw)==ELF_PINS[native],'whole measured ELF metadata/locals/sections')
    return dict(sha256=sha(e.raw),native_pending=native,header=e.header,program_headers=e.program_headers,sections=e.sections,symbols=e.symbols,
                relocations=e.relocations,code_hex=code.hex(),code_sha256=sha(code),instructions=rows,
                whole92_original_equal=not native,derived_table_if_nominal_PC=derived,indirect_call_RA=0x12c0e)


def ir_contract(text,language,full=True):
    blocks=re.findall(r'^define .*?@([^\(]+)\([^\n]*\{\n(.*?)^\}',text,re.M|re.S)
    need([n for n,t in blocks]==NAMES and not re.search(r'^declare ',text,re.M),'exact five IR regions/no helpers')
    b=dict(blocks);init=b[NAMES[1]];scan=b[NAMES[2]];advance=b[NAMES[4]]
    need('i32 0' in init and 'i32 12' in init and 'i32 32' in init and 'auipc a7, 0x1fff9\\0Aaddi a7, a7, 1126' in init,'IR index/stride/count/PC-base ports')
    need('"={x10},={x11},={x12},={x13},={x15},={x17},={x28},={x6},~{memory}"()' in scan,'fresh physical scan input bank')
    anchors=['%10 = mul i32 %6, %8','add s0, a7, a4','lhu a6, 0(s0)','%19 = shl i32 %18, 16','%21 = lshr i32 %20, 16','.Lring_occupied:',
             'sh a0, 0(s0)\\0Asb a2, 2(s0)','(i32 262144)','%23 = add i32 %22, 76','%25 = load volatile i32, ptr %24, align 4',
             '(i32 %25, i32 %15)','%29 = add i32 %28, 3','mv s1, a3','%33 = add i32 %32, %31','asm sideeffect "jalr a5','sb s1, 11(s0)']
    need(all(a in scan for a in anchors) and [scan.index(a) for a in anchors]==sorted(scan.index(a) for a in anchors),'IR ordered fresh slot/provider/call/postcall dataflow')
    need(text.count('load volatile i32')==1 and text.count('load volatile')==1 and 'store volatile' not in text,'one C volatile32 provider read; slot widths are architectural ports')
    need('"{x10},{x12},~{memory}"(i32 %2, i32 %4)' in scan,'full A2 retained beside byte-width slot store')
    need('"={x10},={x11},={x12},{x15},{x10},{x11},{x12},~{x13},~{x14},~{x16},~{x17},~{x6},~{x28},~{memory}"(i32 %27, i32 %33, i32 %3, i32 %4)' in scan,'provider pointer SSA/full A1/full A2 at physical JALR')
    need('%35 = extractvalue { i32, i32, i32 } %34, 0' in scan and '"sb s1, 11(s0)\\0A", "{x10},~{memory}"(i32 %35)' in scan and 'asm sideeffect "", "{x10},~{memory}"(i32 %35)' in scan,'then-live physical S0/S1 and resident A0 residue')
    need('%4 = add i32 %2, 1' in advance and '"{x15},{x6},~{memory}"(i32 %4, i32 %3)' in advance,'fresh increment/count control port')
    need(text.count('R_RISCV_BRANCH')==2 and text.count('R_RISCV_RVC_JUMP')==1 and text.count('asm sideeffect "lw ra, 12(sp)')==1,'three explicit control edges and unique fresh restore')
    lines=text.splitlines();need(lines[0].startswith('; ModuleID = ') and lines[1].startswith('source_filename = ') and all('ring_insert.v3.c' in x for x in lines[:2]),'two path-only producer IR headers')
    normalized='\n'.join(lines[2:])+'\n'
    if full:need(sha(normalized.encode())==IR_PINS[language],'complete normalized IR constants/SSA/order/attributes')
    return dict(normalized_sha256=sha(normalized.encode()),normalization='Exclude only two producer path header lines; LF.',provider_read_bits=32,
                input_A1='fresh scan input %3',input_A2='full fresh scan input %4',postcall='physical S0/S1; returned A0 %35',ordinary_C_ABI=False)


def recipes(root,llvm,out,language):
    f=flags(language);obj=str(out/'native.o');linked=str(out/'linked.elf');source=str(root/SOURCE)
    dump=['--mattr=+m,+a,+c,+zicsr','-d','-r','-t','-h']
    return [('compile',[str(llvm/'clang.exe')]+f+['-MD','-MF',str(out/'native.d'),'-MT',obj,'-c',source,'-o',obj]),
            ('IR',[str(llvm/'clang.exe')]+f+['-S','-emit-llvm',source,'-o',str(out/'native.ll')]),
            ('object',[str(llvm/'llvm-objdump.exe')]+dump+[obj]),
            ('link',[str(llvm/'ld.lld.exe'),'--no-relax','-T',str(root/LINKER),obj,'-o',linked]),
            ('linked',[str(llvm/'llvm-objdump.exe')]+dump+[linked])]


def inputs(root,llvm):
    items=[(root/n,pin) for n,pin in PINS.items()]+[(Path(__file__).resolve(),None),(llvm.parent/'lib/clang/18/include/stdint.h',HEADER_PIN)]+[(llvm/n,pin) for n,pin in TOOLS.items()]
    result=[]
    for path,pin in items:
        raw=path.read_bytes();need(pin is None or sha(raw)==pin,'pinned input '+path.name)
        result.append(dict(path=portable(str(path),root,llvm),size=len(raw),sha256=sha(raw)))
    return result


def md_contract(raw,root,llvm,out):
    t=raw.replace('\\\n',' ').replace('\\\r\n',' ').replace('\\ ','\x01').replace('\\','/');target=str(out/'native.o').replace('\\','/')
    need(t.startswith(target+':'),'exact MD target')
    deps=[x.replace('\x01',' ') for x in t[len(target)+1:].split()]
    want=[str(root/SOURCE).replace('\\','/'),str(llvm.parent/'lib/clang/18/include/stdint.h').replace('\\','/')]
    need(deps==want,'complete two-file MD source/header closure')
    return portable(want,root,llvm)


def negatives(native,linked,text,language,official,md,root,llvm,out):
    controls=[]
    def reject(label,call):
        try:call()
        except (ValueError,KeyError,IndexError,struct.error):controls.append(label);return
        raise ValueError('negative accepted: '+label)
    # Change physical operands/immediates in still-decodable instructions. The
    # typed contract runs before byte equality/hash gates; full hashes disabled.
    for label,at,mask in [('frame-size',0,4),('saved-RA-slot',3,2),('stride',18,4),('count',22,0x10),('mul-index',26,1),('LHU-slot',34,0x10),
                          ('occupancy-shift',36,4),('slot-ID-width',47,0x10),('slot-length-width',51,0x10),('provider-base',56,0x10),('provider-offset',58,4),
                          ('payload-offset',60,4),('channel-source',62,4),('copy-destination',66,1),('JALR-target',68,0x80),('postcall-channel',72,0x10),('restore-slot',74,4),('advance',84,4)]:
        code=bytearray(official);code[at]^=mask
        reject('typed-'+label,lambda code=code:code_contract(bytes(code),False,official,False))
    # Real relocation graph gates, independently from whole-file hashes.
    for label,field,value in [('type','type',45),('site','offset',16),('addend','addend',1),('target','symbol',9)]:
        e=ELF(native.raw);e.relocations[0][field]=value
        reject('relocation-'+label,lambda e=e:elf_contract(e,True,official,False))
    for label,change,is_native in [('FUNC-size',lambda e:e.symbols[9].update(size=10),True),('FUNC-ABS',lambda e:e.symbols[9].update(section=0xfff1),True),
                                 ('region-align',lambda e:e.sections[3].update(align=4),True),('extra-allocation',lambda e:e.sections[10].update(flags=50),True),
                                 ('nominal-PC',lambda e:e.sections[1].update(address=ADDRESS+2),False),('adjacency',lambda e:e.symbols[9].update(value=ADDRESS+10),False)]:
        e=ELF(native.raw if is_native else linked.raw);change(e)
        reject('metadata-'+label,lambda e=e,is_native=is_native:elf_contract(e,is_native,official,False))
    # Full metadata pin is intentional for local mapping symbols.
    e=ELF(native.raw);s=next(s for s in e.symbols if s['name']=='$d.6');tab=e.section('.symtab');raw=bytearray(e.raw)
    struct.pack_into('<I',raw,tab['offset']+16*s['index']+4,1)
    reject('whole-ELF-local-metadata',lambda:elf_contract(ELF(raw),True,official))
    for label,old,new in [('provider-width','load volatile i32','load volatile i16'),('provider-address','%23 = add i32 %22, 76','%23 = add i32 %22, 72'),
                          ('stride-SSA','%10 = mul i32 %6, %8','%10 = mul i32 %6, %9'),('occupancy-width','%19 = shl i32 %18, 16','%19 = shl i32 %18, 8'),
                          ('full-A2','i32 %27, i32 %33, i32 %3, i32 %4)','i32 %27, i32 %33, i32 %3, i32 %2)'),
                          ('fresh-A1','i32 %27, i32 %33, i32 %3, i32 %4)','i32 %27, i32 %33, i32 %2, i32 %4)'),
                          ('postcall-A0','"{x10},~{memory}"(i32 %35)','"{x10},~{memory}"(i32 %2)'),
                          ('postcall-S0','sb s1, 11(s0)','sb s1, 11(a0)'),('advance','%4 = add i32 %2, 1','%4 = add i32 %2, 2')]:
        need(old in text,'IR negative anchor '+label);mut=text.replace(old,new,1)
        reject('IR-'+label,lambda mut=mut:ir_contract(mut,language,False))
    reject('full-normalized-IR',lambda:ir_contract(text.replace('!"wchar_size", i32 4','!"wchar_size", i32 2'),language))
    reject('MD-missing-header',lambda:md_contract(md.splitlines()[0],root,llvm,out))
    return controls


def evaluate(root,llvm,out,language):
    before=inputs(root,llvm);official=original()
    native=ELF(out/'native.o');linked=ELF(out/'linked.elf')
    ns=elf_contract(native,True,official);ls=elf_contract(linked,False,official)
    source=(root/SOURCE).read_text(encoding='utf-8');need(not re.search(r'\.(?:byte|2byte|4byte|word|insn)\b',source),'no source rawopcode carrier')
    text=(out/'native.ll').read_text(encoding='utf-8');ir=ir_contract(text,language)
    md=(out/'native.d').read_text(encoding='utf-8');deps=md_contract(md,root,llvm,out)
    expected=[dict(label=n,argv=portable(a,root,llvm),returncode=0) for n,a in recipes(root,llvm,out,language)]
    need(json.loads((out/'recipes.json').read_text())==expected,'complete exact pinned producer recipes')
    files=sorted(['native.o','native.ll','native.d','linked.elf','recipes.json']+[n+'.log' for n,a in recipes(root,llvm,out,language)])
    need(sorted(p.name for p in out.iterdir() if p.name!='verification.json')==files and all(p.is_file() and not p.is_symlink() for p in out.iterdir()),'exact artifact/log inventory')
    for n in ('compile','IR','link'):need(not (out/(n+'.log')).read_bytes(),'successful empty compiler/linker diagnostics '+n)
    for n in ('object','linked'):need(all(name in (out/(n+'.log')).read_text() for name in NAMES),'retained disassembly coverage '+n)
    controls=negatives(native,linked,text,language,official,md,root,llvm,out)
    artifact=[dict(path=portable(str(out/n),root,llvm),size=(out/n).stat().st_size,sha256=sha((out/n).read_bytes())) for n in files]
    need(before==inputs(root,llvm),'stable all source/tool/header/helper inputs')
    record=dict(schema='TSL9-ring-native-v3-formal-v1',language=language,root='${TSL9_ROOT}',llvm_bin='${LLVM_BIN}',out_dir=portable(str(out),root,llvm),
                firmware_ready=False,target_executed=False,ISA_emulated=False,inputs=before,
                original=dict(base=0x8000,start=ADDRESS,end=ADDRESS+92,bytes=92,instructions=32,sha256=CODE_PIN),
                native=ns,nominal=ls,ir=ir,md_dependencies=deps,recipes=expected,artifacts=artifact,negative_controls=controls,
                static_contract=dict(frame_bytes=16,nominal_code_base=ADDRESS,table_address_if_nominal=0x2000c038,slot_stride=12,slot_count=32,
                  occupied_halfword_bits=16,slot_ID_write_bits=16,slot_length_write_bits=8,provider_pointer_read_address=0x4004c,provider_pointer_read_bits=32,
                  provider_target='dynamic value freshly read at 0x4004C; no identity or ABI claim',provider_call_A1='full input payload pointer',provider_call_A2='full input length, no ring-side bound check',
                  provider_call_A0='table + slot_index * 12 + 3',provider_RA=0x12c0e,postcall_channel='then-live S1 byte at then-live S0+11',
                  successful_return_A0='then-live resident output',full_ring_return_A0='input A0 residue if no asynchronous interference',fresh_restore=['RA from SP+12','S0 from SP+8','S1 from SP+4','SP +=16','RET']),
                limitations=['Static native compilation, IR and decode only; no target, ISA, MMIO or hardware execution.',
                  'Five genuine FUNC symbols are private architectural regions, not ordinary independently callable C ABI functions.',
                  'The nominal linked ELF resolves three local branches and matches 92 official bytes; it is not a full flashable image.',
                  'Fixed AUIPC requires verified nominal placement; arbitrary rebasing would change the computed table address.',
                  'No identity or complete preservation contract for the indirect resident provider is proved.',
                  'Ring source does not bound full A2 or validate A1; caller constraints, IRQ/fault interleaving, physical memory and complete firmware remain open.'])
    encoded=json.dumps(record,ensure_ascii=False,sort_keys=True,indent=2)+'\n'
    need(not re.search(r'(?i)[a-z]:[/\\]|/(?:users|home)/',encoded),'portable receipt contains host path')
    return record,encoded


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    action=parser.add_mutually_exclusive_group(required=True);action.add_argument('--out-dir',type=Path);action.add_argument('--replay',type=Path)
    parser.add_argument('--language',choices=['c','cpp']);parser.add_argument('--llvm-bin',type=Path,default=Path.home()/'AppData/Local/Android/Sdk/ndk/27.1.12297006/toolchains/llvm/prebuilt/windows-x86_64/bin')
    parser.add_argument('--require-firmware-ready',action='store_true');args=parser.parse_args();llvm=args.llvm_bin.resolve()
    if args.replay:
        receipt=args.replay.resolve();out=receipt.parent;saved=json.loads(receipt.read_text());language=saved['language']
        need(args.language is None or args.language==language,'replay language')
        record,encoded=evaluate(ROOT,llvm,out,language)
        need(record==saved and receipt.read_bytes()==encoded.encode(),'entire receipt equality and LF')
    else:
        need(args.language is not None,'--language required');language=args.language;out=args.out_dir.resolve();owned=ROOT/BASE/'build'
        need(out.is_relative_to(owned) and out!=owned and not out.exists(),'fresh owned output directory')
        before=inputs(ROOT,llvm);out.mkdir(parents=True);rs=[]
        for label,argv in recipes(ROOT,llvm,out,language):
            p=subprocess.run(argv,cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,check=False)
            (out/(label+'.log')).write_bytes(p.stdout);rs.append(dict(label=label,argv=portable(argv,ROOT,llvm),returncode=p.returncode))
            need(p.returncode==0,'native recipe failed '+label)
        (out/'recipes.json').write_bytes((json.dumps(rs,indent=2)+'\n').encode())
        need(before==inputs(ROOT,llvm),'stable producer inputs');record,encoded=evaluate(ROOT,llvm,out,language)
        (out/'verification.json').write_bytes(encoded.encode())
    print(json.dumps(dict(result='PASS',language=language,receipt_sha256=sha(encoded.encode()),elfs=2,bytes=92,instructions=32,controls=len(record['negative_controls']),nominal_full_code_equal=True,firmware_ready=False)))
    if args.require_firmware_ready:
        print('REJECTED: resident/hardware/full-firmware evidence absent; firmware_ready=false.',file=sys.stderr);return 1
    return 0


if __name__=='__main__':
    try:sys.exit(main())
    except (ValueError,KeyError,OSError,IndexError,struct.error) as exc:
        print('FAIL: '+str(exc),file=sys.stderr);sys.exit(1)
