#!/usr/bin/env python3
"""Compile/replay the bounded 52B private IRQ regions. Never execute them."""
from __future__ import annotations
import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import re
import runpy
import struct
import subprocess
import sys

sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
SOURCE=HERE/'src/irq_adapter.v2.c'
READER=ROOT/'experiments/tsl9-spi-transfer-leaf/verify.py'
FIRMWARE=ROOT/'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
PINS={SOURCE:'229b5510d9cf354bf27634e2edac5518dd4fa76f1054997e353cf9e0ef64b596',
 HERE/'component.ld':'a62578a70fb912fab3fc4805112dc4d9e1fc524e38a2992be525aff05d600e69',
 HERE/'probe.py':'7ab70199ac55c5276b6950daba8bdacb9d63f8bde1212a5944a330b8f2a195fa',
 READER:'8c8eb8e01b9fc30eb7150682aa8848e47fe4a1254c6f87b05e657244a11b6de8',
 FIRMWARE:'0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'}
TOOLS={'clang.exe':'047dfde05acc6fcce5af669e25cd8d40b4f509b8842d151d6d8a43a1c6a35fd6',
 'ld.lld.exe':'fe7f55c0c78b3d87f33b905a3874e10e872ca7beef53a8199d7ff9ac6641ec3f',
 'llvm-objdump.exe':'de40d1188fe63ff373e1a5dd83a12e2cb4545ca3b314da16a476ecf072e5a0fa'}
HEADER_PIN='7ce5540d5fb6e8da9760928e76cbdd5ebef329d701ad598d30d8e6f9d5d78b34'
ELF_PINS={True:'b9882d47ef30b0f24e8e15fc37f05e47f5bb4a602979f7cbdbbefa5d02b64c46',
 False:'fed68f34e4cb2b27855d4ed2f620871deef6dd76a80ab20b0d9907957560ac06'}
IR_PINS={'c':'3ed1aee15873e2be90748a980a97a399205720cf44dfd4feb129fcbc6a4756db',
 'cpp':'5d0031787fe6387fc511122611a1fcfbe91bb066da739e370ea72a3ebc3e30a2'}
ORIGINAL_PIN='44ab1cdae33f0151e8270b3769d9dca81847154bf88d3f691443d77200ece51a'
BASE=0x12c24
NAMES=['tsl9_ring_irq_entry_12c24','tsl9_ring_irq_frame_12c32','tsl9_ring_irq_dispatch_12c3c',
       'tsl9_ring_irq_finish_12c4e','tsl9_ring_irq_empty_12c54']
REGIONS=list(zip(NAMES,[0,14,24,42,48],[14,10,18,6,4]))
PROVIDER='tsl9_irq_provider_18d78'
RING='tsl9_ring_insert_entry_12bc8'
RELOCATIONS=[(12,44,NAMES[4]),(20,17,PROVIDER),(38,17,RING)]
EXPECTED=[[0,4,'LUI',10,0x40006000],[4,4,'ADDI',10,10,1024],[8,2,'LW32',15,10,12],
 [10,2,'ANDI',15,15,3],[12,2,'BEQZ',15,BASE+48],[14,2,'ADDI',2,2,-32],
 [16,2,'ADDI',12,2,12],[18,2,'ADDI',11,0,0],[20,4,'JAL',1,0x18d78],
 [24,4,'LBU8',12,2,22],[28,4,'LHU16',10,2,12],[32,4,'ADDI',11,2,23],
 [36,2,'ADDI',13,0,0],[38,4,'JAL',1,0x12bc8],[42,2,'ADDI',2,2,32],
 [44,4,'MRET'],[48,4,'MRET']]
# Complete parsed metadata and non-code section hashes calibrated from pinned
# probe-v2 native/partial objects. No ignored probe files are needed at runtime.
SCHEMAS = {'native': {'header': [1, 243, 1, 0, 0, 980, 1, 52, 0, 0, 40, 16, 1], 'program_headers': [], 'sections': [{'name_offset': 0, 'type': 0, 'flags': 0, 'address': 0, 'offset': 0, 'size': 0, 'link': 0, 'info': 0, 'align': 0, 'entsize': 0, 'index': 0, 'name': ''}, {'name_offset': 154, 'type': 3, 'flags': 0, 'address': 0, 'offset': 613, 'size': 364, 'link': 0, 'info': 0, 'align': 1, 'entsize': 0, 'index': 1, 'name': '.strtab'}, {'name_offset': 1, 'type': 1, 'flags': 6, 'address': 0, 'offset': 52, 'size': 0, 'link': 0, 'info': 0, 'align': 2, 'entsize': 0, 'index': 2, 'name': '.text'}, {'name_offset': 270, 'type': 1, 'flags': 6, 'address': 0, 'offset': 52, 'size': 14, 'link': 0, 'info': 0, 'align': 2, 'entsize': 0, 'index': 3, 'name': '.text.tsl9_ring_irq_entry_12c24'}, {'name_offset': 265, 'type': 4, 'flags': 64, 'address': 0, 'offset': 572, 'size': 12, 'link': 15, 'info': 3, 'align': 4, 'entsize': 12, 'index': 4, 'name': '.rela.text.tsl9_ring_irq_entry_12c24'}, {'name_offset': 317, 'type': 1, 'flags': 6, 'address': 0, 'offset': 66, 'size': 10, 'link': 0, 'info': 0, 'align': 2, 'entsize': 0, 'index': 5, 'name': '.text.tsl9_ring_irq_frame_12c32'}, {'name_offset': 312, 'type': 4, 'flags': 64, 'address': 0, 'offset': 584, 'size': 12, 'link': 15, 'info': 5, 'align': 4, 'entsize': 12, 'index': 6, 'name': '.rela.text.tsl9_ring_irq_frame_12c32'}, {'name_offset': 102, 'type': 1, 'flags': 6, 'address': 0, 'offset': 76, 'size': 18, 'link': 0, 'info': 0, 'align': 2, 'entsize': 0, 'index': 7, 'name': '.text.tsl9_ring_irq_dispatch_12c3c'}, {'name_offset': 97, 'type': 4, 'flags': 64, 'address': 0, 'offset': 596, 'size': 12, 'link': 15, 'info': 7, 'align': 4, 'entsize': 12, 'index': 8, 'name': '.rela.text.tsl9_ring_irq_dispatch_12c3c'}, {'name_offset': 64, 'type': 1, 'flags': 6, 'address': 0, 'offset': 94, 'size': 6, 'link': 0, 'info': 0, 'align': 2, 'entsize': 0, 'index': 9, 'name': '.text.tsl9_ring_irq_finish_12c4e'}, {'name_offset': 233, 'type': 1, 'flags': 6, 'address': 0, 'offset': 100, 'size': 4, 'link': 0, 'info': 0, 'align': 2, 'entsize': 0, 'index': 10, 'name': '.text.tsl9_ring_irq_empty_12c54'}, {'name_offset': 7, 'type': 1, 'flags': 48, 'address': 0, 'offset': 104, 'size': 159, 'link': 0, 'info': 0, 'align': 1, 'entsize': 1, 'index': 11, 'name': '.comment'}, {'name_offset': 34, 'type': 1, 'flags': 0, 'address': 0, 'offset': 263, 'size': 0, 'link': 0, 'info': 0, 'align': 1, 'entsize': 0, 'index': 12, 'name': '.note.GNU-stack'}, {'name_offset': 16, 'type': 1879048195, 'flags': 0, 'address': 0, 'offset': 263, 'size': 52, 'link': 0, 'info': 0, 'align': 1, 'entsize': 0, 'index': 13, 'name': '.riscv.attributes'}, {'name_offset': 50, 'type': 1879002115, 'flags': 2147483648, 'address': 0, 'offset': 608, 'size': 5, 'link': 15, 'info': 0, 'align': 1, 'entsize': 0, 'index': 14, 'name': '.llvm_addrsig'}, {'name_offset': 162, 'type': 2, 'flags': 0, 'address': 0, 'offset': 316, 'size': 256, 'link': 1, 'info': 9, 'align': 4, 'entsize': 16, 'index': 15, 'name': '.symtab'}], 'symbols': [{'index': 0, 'name': '', 'value': 0, 'size': 0, 'info': 0, 'other': 0, 'section': 0}, {'index': 1, 'name': 'irq_adapter.v2.c', 'value': 0, 'size': 0, 'info': 4, 'other': 0, 'section': 65521}, {'index': 2, 'name': '$x.0', 'value': 0, 'size': 0, 'info': 0, 'other': 0, 'section': 3}, {'index': 3, 'name': '$x.1', 'value': 0, 'size': 0, 'info': 0, 'other': 0, 'section': 5}, {'index': 4, 'name': '$x.2', 'value': 0, 'size': 0, 'info': 0, 'other': 0, 'section': 7}, {'index': 5, 'name': '$x.3', 'value': 0, 'size': 0, 'info': 0, 'other': 0, 'section': 9}, {'index': 6, 'name': '$x.4', 'value': 0, 'size': 0, 'info': 0, 'other': 0, 'section': 10}, {'index': 7, 'name': '$d.5', 'value': 0, 'size': 0, 'info': 0, 'other': 0, 'section': 11}, {'index': 8, 'name': '$d.6', 'value': 0, 'size': 0, 'info': 0, 'other': 0, 'section': 13}, {'index': 9, 'name': 'tsl9_ring_irq_entry_12c24', 'value': 0, 'size': 14, 'info': 18, 'other': 0, 'section': 3}, {'index': 10, 'name': 'tsl9_ring_irq_empty_12c54', 'value': 0, 'size': 4, 'info': 18, 'other': 0, 'section': 10}, {'index': 11, 'name': 'tsl9_ring_irq_frame_12c32', 'value': 0, 'size': 10, 'info': 18, 'other': 0, 'section': 5}, {'index': 12, 'name': 'tsl9_irq_provider_18d78', 'value': 0, 'size': 0, 'info': 16, 'other': 0, 'section': 0}, {'index': 13, 'name': 'tsl9_ring_irq_dispatch_12c3c', 'value': 0, 'size': 18, 'info': 18, 'other': 0, 'section': 7}, {'index': 14, 'name': 'tsl9_ring_insert_entry_12bc8', 'value': 0, 'size': 0, 'info': 16, 'other': 0, 'section': 0}, {'index': 15, 'name': 'tsl9_ring_irq_finish_12c4e', 'value': 0, 'size': 6, 'info': 18, 'other': 0, 'section': 9}], 'relocations': [{'section': 3, 'offset': 12, 'type': 44, 'symbol': 10, 'addend': 0}, {'section': 5, 'offset': 6, 'type': 17, 'symbol': 12, 'addend': 0}, {'section': 7, 'offset': 14, 'type': 17, 'symbol': 14, 'addend': 0}], 'noncode_section_hashes': {'': 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855', '.strtab': 'd3792735c031643a48d252a5268d6851c67bfaed067c5bbe7e886d61c6656ecf', '.rela.text.tsl9_ring_irq_entry_12c24': 'af3461fe0633f58e364e197eab4a5d94991bebe46b44ad634de48bdf642a7067', '.rela.text.tsl9_ring_irq_frame_12c32': 'bf59cc6cb8c2c68d94002c0e474a406663b333c9419add42a3d4ce46687a91aa', '.rela.text.tsl9_ring_irq_dispatch_12c3c': 'f61640314ed6688167cee8b103d976e2a2194c9e4281ad4963d058e9b9939a91', '.comment': '72c64fbc17a5d9f46f33ac0650b7d4f549d87c2ba9e77ebd765a25a3960e3017', '.note.GNU-stack': 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855', '.riscv.attributes': 'f2bd85b0ab58609a20dbdef6cc6e3f2dd1a34cdcb554580710aa3819cd24ad71', '.llvm_addrsig': '87a0e430eeeda2ff828c26cb5d337791d7680ea9a16a9bab4d624a7652db2d07', '.symtab': '4dfb7bcf5454553a3647e4049e0a593c41d871810f90aeb2f8b37b34473f8a12'}}, 'partial': {'header': [1, 243, 1, 0, 0, 736, 1, 52, 0, 0, 40, 8, 6], 'program_headers': [], 'sections': [{'name_offset': 0, 'type': 0, 'flags': 0, 'address': 0, 'offset': 0, 'size': 0, 'link': 0, 'info': 0, 'align': 0, 'entsize': 0, 'index': 0, 'name': ''}, {'name_offset': 1, 'type': 1, 'flags': 6, 'address': 0, 'offset': 52, 'size': 52, 'link': 0, 'info': 0, 'align': 2, 'entsize': 0, 'index': 1, 'name': '.irq'}, {'name_offset': 6, 'type': 1, 'flags': 6, 'address': 0, 'offset': 104, 'size': 0, 'link': 0, 'info': 0, 'align': 2, 'entsize': 0, 'index': 2, 'name': '.text'}, {'name_offset': 12, 'type': 4, 'flags': 64, 'address': 0, 'offset': 104, 'size': 36, 'link': 5, 'info': 1, 'align': 4, 'entsize': 12, 'index': 3, 'name': '.rela.irq'}, {'name_offset': 22, 'type': 1879002115, 'flags': 2147483648, 'address': 0, 'offset': 140, 'size': 5, 'link': 0, 'info': 0, 'align': 1, 'entsize': 0, 'index': 4, 'name': '.llvm_addrsig'}, {'name_offset': 36, 'type': 2, 'flags': 0, 'address': 0, 'offset': 148, 'size': 288, 'link': 7, 'info': 11, 'align': 4, 'entsize': 16, 'index': 5, 'name': '.symtab'}, {'name_offset': 44, 'type': 3, 'flags': 0, 'address': 0, 'offset': 436, 'size': 62, 'link': 0, 'info': 0, 'align': 1, 'entsize': 0, 'index': 6, 'name': '.shstrtab'}, {'name_offset': 54, 'type': 3, 'flags': 0, 'address': 0, 'offset': 498, 'size': 235, 'link': 0, 'info': 0, 'align': 1, 'entsize': 0, 'index': 7, 'name': '.strtab'}], 'symbols': [{'index': 0, 'name': '', 'value': 0, 'size': 0, 'info': 0, 'other': 0, 'section': 0}, {'index': 1, 'name': 'irq_adapter.v2.c', 'value': 0, 'size': 0, 'info': 4, 'other': 0, 'section': 65521}, {'index': 2, 'name': '$x.0', 'value': 0, 'size': 0, 'info': 0, 'other': 0, 'section': 1}, {'index': 3, 'name': '$x.1', 'value': 14, 'size': 0, 'info': 0, 'other': 0, 'section': 1}, {'index': 4, 'name': '$x.2', 'value': 24, 'size': 0, 'info': 0, 'other': 0, 'section': 1}, {'index': 5, 'name': '$x.3', 'value': 42, 'size': 0, 'info': 0, 'other': 0, 'section': 1}, {'index': 6, 'name': '$x.4', 'value': 48, 'size': 0, 'info': 0, 'other': 0, 'section': 1}, {'index': 7, 'name': '$d.6', 'value': 0, 'size': 0, 'info': 0, 'other': 0, 'section': 65521}, {'index': 8, 'name': '', 'value': 0, 'size': 0, 'info': 3, 'other': 0, 'section': 1}, {'index': 9, 'name': '', 'value': 0, 'size': 0, 'info': 3, 'other': 0, 'section': 2}, {'index': 10, 'name': '', 'value': 0, 'size': 0, 'info': 3, 'other': 0, 'section': 4}, {'index': 11, 'name': 'tsl9_ring_irq_entry_12c24', 'value': 0, 'size': 14, 'info': 18, 'other': 0, 'section': 1}, {'index': 12, 'name': 'tsl9_ring_irq_empty_12c54', 'value': 48, 'size': 4, 'info': 18, 'other': 0, 'section': 1}, {'index': 13, 'name': 'tsl9_ring_irq_frame_12c32', 'value': 14, 'size': 10, 'info': 18, 'other': 0, 'section': 1}, {'index': 14, 'name': 'tsl9_irq_provider_18d78', 'value': 0, 'size': 0, 'info': 16, 'other': 0, 'section': 0}, {'index': 15, 'name': 'tsl9_ring_irq_dispatch_12c3c', 'value': 24, 'size': 18, 'info': 18, 'other': 0, 'section': 1}, {'index': 16, 'name': 'tsl9_ring_insert_entry_12bc8', 'value': 0, 'size': 0, 'info': 16, 'other': 0, 'section': 0}, {'index': 17, 'name': 'tsl9_ring_irq_finish_12c4e', 'value': 42, 'size': 6, 'info': 18, 'other': 0, 'section': 1}], 'relocations': [{'section': 1, 'offset': 12, 'type': 44, 'symbol': 12, 'addend': 0}, {'section': 1, 'offset': 20, 'type': 17, 'symbol': 14, 'addend': 0}, {'section': 1, 'offset': 38, 'type': 17, 'symbol': 16, 'addend': 0}], 'noncode_section_hashes': {'': 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855', '.rela.irq': 'ed2bcc5738c8d68b809cfae48327506d16b5000ce0ba4f54c335605eb89cd51a', '.llvm_addrsig': '87a0e430eeeda2ff828c26cb5d337791d7680ea9a16a9bab4d624a7652db2d07', '.symtab': 'e156013225ee2abe923f84d8e4305b3b0c3e0c2a046bd5542768d3c50f2a4bf2', '.shstrtab': '4a4add977b7fb5505ad8fccdabed8a56e3afc3f8cf46982457802a3000b35c2e', '.strtab': '5377bac5d148c414da7b28ec5877aceb57949fed5cb48f802b1070a7f5c68abf'}}}


def need(ok,message):
    if not ok:raise ValueError(message)


def sha(data):return hashlib.sha256(data).hexdigest()
def digest(path):return sha(Path(path).read_bytes())
def sx(n,b):return n-(1<<b) if n&(1<<(b-1)) else n


need(digest(READER)==PINS[READER],'frozen ELF reader')
_reader=runpy.run_path(str(READER))
ELF,portable=_reader['ELF'],_reader['portable']


def decode(code):
    rows=[];at=0
    while at<len(code):
        need(at+2<=len(code),'instruction extent');w=int.from_bytes(code[at:at+2],'little');size=4 if w&3==3 else 2
        need(at+size<=len(code),'wide instruction extent')
        if size==4:
            w=int.from_bytes(code[at:at+4],'little');op=w&127;rd=(w>>7)&31;rs=(w>>15)&31;f3=(w>>12)&7
            if w==0x30200073:ins=['MRET']
            elif op==0x37:ins=['LUI',rd,w&0xfffff000]
            elif op==0x13 and f3==0:ins=['ADDI',rd,rs,sx(w>>20,12)]
            elif op==3 and f3 in (4,5):ins=['LBU8' if f3==4 else 'LHU16',rd,rs,sx(w>>20,12)]
            elif op==0x6f:
                imm=((w>>31)<<20)|(((w>>21)&1023)<<1)|(((w>>20)&1)<<11)|(((w>>12)&255)<<12)
                ins=['JAL',rd,BASE+at+sx(imm,21)]
            else:raise ValueError('forbidden wide opcode, ordinary RET/store/CSR not admitted')
        else:
            q=w&3;f3=w>>13;rd=(w>>7)&31;imm=sx(((w>>12)&1)*32+((w>>2)&31),6)
            if q==0 and f3==2:
                offset=(((w>>10)&7)<<3)|(((w>>6)&1)<<2)|(((w>>5)&1)<<6)
                ins=['LW32',8+((w>>2)&7),8+((w>>7)&7),offset]
            elif q==0 and f3==0:
                offset=(((w>>11)&3)<<4)|(((w>>7)&15)<<6)|(((w>>6)&1)<<2)|(((w>>5)&1)<<3)
                need(offset!=0,'valid ADDI4SPN');ins=['ADDI',8+((w>>2)&7),2,offset]
            elif q==1 and f3==0:ins=['ADDI',rd,rd,imm]
            elif q==1 and f3==2:ins=['ADDI',rd,0,imm]
            elif q==1 and f3==3 and rd==2:
                n=(((w>>12)&1)<<9)|(((w>>6)&1)<<4)|(((w>>5)&1)<<6)|(((w>>3)&3)<<7)|(((w>>2)&1)<<5)
                ins=['ADDI',2,2,sx(n,10)]
            elif q==1 and f3==4 and (w>>10)&3==2:
                rs=8+((w>>7)&7);ins=['ANDI',rs,rs,imm]
            elif q==1 and f3 in (6,7):
                n=(((w>>12)&1)<<8)|(((w>>10)&3)<<3)|(((w>>5)&3)<<6)|(((w>>3)&3)<<1)|(((w>>2)&1)<<5)
                ins=['BEQZ' if f3==6 else 'BNEZ',8+((w>>7)&7),BASE+at+sx(n,9)]
            else:raise ValueError('forbidden compressed opcode or ordinary RET/store')
        rows.append([at,size]+ins);at+=size
    return rows


def typed_contract(rows,pending):
    expected=copy.deepcopy(EXPECTED)
    if pending:
        for index in (4,8,13):expected[index][-1]=BASE+expected[index][0]
    need(rows==expected,'all17 typed operands/widths/order, physical SP and two MRET exits')
    return rows


def original():
    raw=FIRMWARE.read_bytes();need(len(raw)==76800 and sha(raw)==PINS[FIRMWARE],'whole original BIN identity')
    code=raw[BASE-0x8000:BASE-0x8000+52];typed_contract(decode(code),False)
    need(sha(code)==ORIGINAL_PIN,'original52B span pin');return code


def projection(code):
    return bytes(x for i,x in enumerate(code) if i not in set(range(12,14))|set(range(20,24))|set(range(38,42)))


def metadata(e):
    return dict(header=e.header,program_headers=e.program_headers,sections=e.sections,symbols=e.symbols,
                relocations=e.relocations,noncode_section_hashes={s['name']:sha(e.data(s)) for s in e.sections
                if not s['flags']&2 and s['type']!=8})


def elf_contract(e,native,official,full=True):
    need(e.header[0]==1 and e.header[6]==1 and not e.program_headers,'actual RV32 RVC ET_REL, never executable')
    expected_metadata=SCHEMAS['native' if native else 'partial']
    need(len(e.raw)==expected_metadata['header'][5]+40*expected_metadata['header'][11],
         'complete ELF extent, no unbound trailing bytes')
    globals_=[s for s in e.symbols if s['info']>>4]
    expected={n:(0 if native else at,z,18,0,('.text.'+n if native else '.irq')) for n,at,z in REGIONS}
    actual={s['name']:(s['value'],s['size'],s['info'],s['other'],e.sections[s['section']]['name'])
            for s in globals_ if s['section'] not in (0,65521)}
    need(actual==expected and len(globals_)==7,'five genuine FUNCs with exact region ownership/extent')
    und=[s for s in globals_ if s['section']==0]
    need(sorted(s['name'] for s in und)==[PROVIDER,RING] and all(s['info']==16 and s['other']==s['value']==s['size']==0 for s in und)
         and not any(s['section']==65521 for s in globals_),'two real UND providers, no ABS/fake/weak providers')
    alloc=[s for s in e.sections if s['flags']&2 and s['size']]
    need([(s['name'],s['size'],s['flags'],s['type'],s['align']) for s in alloc]==
         ([('.text.'+n,z,6,1,2) for n,_,z in REGIONS] if native else [('.irq',52,6,1,2)]),'exact AX-only allocation')
    code=b''.join(e.data('.text.'+n) for n in NAMES) if native else e.data('.irq')
    rows=typed_contract(decode(code),True);need(len(code)==52 and len(rows)==17,'52B17i')
    rel=[]
    starts={'.text.'+n:at for n,at,_ in REGIONS}
    for r in e.relocations:
        owner=e.sections[r['section']]['name'];symbol=e.symbols[r['symbol']]
        need(owner in starts if native else owner=='.irq','genuine relocation owner')
        offset=r['offset']+(starts[owner] if native else 0)
        rel.append((offset,r['type'],symbol['name'],r['addend']))
        need(symbol['info']==18 and symbol['section']!=0 if offset==12 else symbol['info']==16 and symbol['section']==0,
             'actual defined empty FUNC versus two genuine UND JAL targets')
    need(rel==[(at,kind,name,0) for at,kind,name in RELOCATIONS],'three genuine relocation families/offsets/targets/addends')
    need(code[12:14]==bytes.fromhex('81c3') and code[20:24]==code[38:42]==bytes.fromhex('ef000000'),
         'all three machine control immediates still pending; JAL rd=RA')
    need(len(projection(code))==42 and projection(code)==projection(official),'all42 original noncontrol bytes')
    need(metadata(e)==expected_metadata,'complete ELF metadata/non-code bytes exact')
    if full:need(sha(e.raw)==ELF_PINS[native],'whole measured ELF pin')
    return dict(sha256=sha(e.raw),header=e.header,program_headers=e.program_headers,sections=e.sections,
                symbols=e.symbols,relocations=e.relocations,code_hex=code.hex(),typed_rows=rows,
                UND_providers=[PROVIDER,RING],ABS_providers=[],local_ABS_metadata=sum(s['section']==65521 and s['info']>>4==0 for s in e.symbols),
                pending_machine_immediates=3,noncontrol_bytes=42,noncontrol_sha256=sha(projection(code)),
                nominal_JAL_continuations=[0x12c3c,0x12c4e],resolved_executable=False)


def ir_contract(text,language,full=True):
    normalized='\n'.join(text.splitlines()[2:])+'\n'
    names=re.findall(r'^define .*?@([^ (]+)\(',normalized,re.M);need(names==NAMES,'five real IR definitions in region order')
    need(len(re.findall(r'load volatile i32',normalized))==1 and not re.search(r'load volatile i(?:8|16|64)|\balloca\b|\bstore\b|\b(?:undef|poison)\b',normalized),
         'one true C volatile word read; no spills, widened/narrowed load, cached store or undefined SSA')
    entry=['(i32 1073766400)','%2 = add i32 %1, 1024','%4 = add i32 %3, 12','%5 = inttoptr i32 %4 to ptr',
           '%6 = load volatile i32, ptr %5, align 4','%7 = and i32 %6, 3','"{x15},{x10},~{memory}"(i32 %7, i32 %3)']
    need(all(s in normalized for s in entry),'C MMIO32 address/mask dataflow and physical A0/A5 input wiring')
    need('addi sp, sp, -32\\0Aaddi a2, sp, 12\\0Ali a1, 0\\0Ajal ra, '+PROVIDER+'\\0A' in normalized,'conditional frame/A2/A1/first JAL port order')
    need('lbu a2, 22(sp)\\0Alhu a0, 12(sp)\\0Aaddi a1, sp, 23\\0A' in normalized and
         '"={x12},={x10},={x11},~{memory}"()' in normalized,'fresh then-live physical SP load/address ports')
    need('"={x10},={x11},={x12},={x13},{x10},{x11},{x12},{x13},~{x14},~{x15},~{memory}"(i32 %3, i32 %4, i32 %2, i32 0)' in normalized,
         'ring inputs from fresh tuple and true C zero tag, not stale SSA')
    need('addi sp, sp, 32\\0Amret\\0A' in normalized and normalized.count('mret\\0A')==2 and
         not re.search(r'(?<!m)ret\\0A|sw ra|lw ra|[={]x2[},]',normalized),'two MRET ports, no RA save/restore or cached SP import')
    need('R_RISCV_RVC_BRANCH, '+NAMES[4] in normalized and normalized.count('jal ra, ')==2,'symbolic empty edge and two true JALs')
    need(not re.search(r'\bcall\b[^\n]*@|\.4byte|\.word|\.insn',normalized),'no ordinary C helper calls or opcode carriers')
    if full:need(sha(normalized.encode())==IR_PINS[language],'complete normalized IR including all SSA/constants/attributes')
    return dict(normalized_sha256=sha(normalized.encode()),C_volatile_word_reads=1,C_mask=3,C_zero_tag=True,
                SP_ports='then-live physical SP',functions=NAMES)


def inputs(llvm):
    expected=dict(PINS);expected[Path(__file__).resolve()]=digest(__file__)
    expected[llvm.parent/'lib/clang/18/include/stdint.h']=HEADER_PIN
    expected.update({llvm/n:pin for n,pin in TOOLS.items()})
    need(all(digest(p)==pin for p,pin in expected.items()),'all source/reader/probe/tool/header pins')
    return expected


def md_contract(text,llvm,out):
    text=text.replace('\\\n',' ').replace('\\\r\n',' ').replace('\\ ','\x01').replace('\\','/')
    target=str(out/'native.o').replace('\\','/');need(text.startswith(target+':'),'MD exact output target')
    deps=[s.replace('\x01',' ') for s in text[len(target)+1:].split()]
    want=[str(SOURCE).replace('\\','/'),str(llvm.parent/'lib/clang/18/include/stdint.h').replace('\\','/')]
    need(deps==want,'MD complete exact two-file source/header closure');return portable(want,ROOT,llvm)


def recipes(llvm,out,language):
    probe=runpy.run_path(str(HERE/'probe.py'));f=probe['flags'](language)
    need({int(s[9:]) for s in f if s.startswith('-ffixed-x')}==set(range(1,32))-set(range(10,16)) and
         '-march=rv32imac_zicsr' in f and '-Oz' in f,'frozen compiler profile and reserved RA/SP/bank')
    exe=lambda n:str(llvm/n);obj=str(out/'native.o');dump=['--mattr=+m,+a,+c,+zicsr','-d','-r','-t','-h']
    return [('compile',[exe('clang.exe'),*f,'-MD','-MF',str(out/'native.d'),'-MT',obj,'-c',str(SOURCE),'-o',obj]),
      ('IR',[exe('clang.exe'),*f,'-S','-emit-llvm',str(SOURCE),'-o',str(out/'native.ll')]),
      ('object',[exe('llvm-objdump.exe'),*dump,obj]),
      ('partial',[exe('ld.lld.exe'),'-r','--no-relax','-T',str(HERE/'component.ld'),obj,'-o',str(out/'partial.o')]),
      ('partial_object',[exe('llvm-objdump.exe'),*dump,str(out/'partial.o')])]


def negatives(native,partial,text,language,official,md,llvm,out):
    results=[]
    def check(name,scope,fn,full=False):
        try:fn()
        except (ValueError,IndexError,KeyError) as exc:results.append(dict(name=name,scope=scope,rejected=True,whole_ELF_hash_enabled=False,whole_IR_hash_enabled=full,reason=str(exc)))
        else:raise ValueError('negative accepted '+name)
    def raw(name,e,native_mode,position,fmt,value):
        b=bytearray(e.raw);struct.pack_into(fmt,b,position,value)
        check(name,'raw_ELF_reparsed',lambda:elf_contract(ELF(b),native_mode,official,False))
    for e,native_mode in [(native,True),(partial,False)]:
        tag='native' if native_mode else 'partial'
        globals_={s['name']:s for s in e.symbols if s['info']>>4};symtab=next(s for s in e.sections if s['type']==2)
        for name in [PROVIDER,RING,NAMES[4]]:
            at=symtab['offset']+globals_[name]['index']*16
            raw(tag+'_fakeABS_'+name,e,native_mode,at+14,'<H',65521)
            raw(tag+'_weak_'+name,e,native_mode,at+12,'<B',34)
        for i,r in enumerate(e.relocations):
            table=next(s for s in e.sections if s['type']==4 and s['info']==r['section']);j=0 if native_mode else i;at=table['offset']+12*j
            raw(tag+'_RELA_addend_'+str(i),e,native_mode,at+8,'<i',2)
            raw(tag+'_RELA_family_'+str(i),e,native_mode,at+4,'<I',(r['symbol']<<8)|(17 if i==0 else 44))
            other=globals_[RING if i==1 else PROVIDER]['index']
            raw(tag+'_RELA_target_'+str(i),e,native_mode,at+4,'<I',(other<<8)|r['type'])
        at=symtab['offset']+globals_[NAMES[2]]['index']*16
        raw(tag+'_FUNC_wrong_size',e,native_mode,at+8,'<I',20)
        raw(tag+'_FUNC_wrong_value',e,native_mode,at+4,'<I',2)
        section=next(s for s in e.sections if s['flags']&2 and s['size'])
        raw(tag+'_writable_code',e,native_mode,e.header[5]+40*section['index']+8,'<I',7)
        check(tag+'_trailing_bytes','raw_ELF_reparsed',lambda ee=e,nn=native_mode:elf_contract(ELF(ee.raw+b'\0\0'),nn,official,False))
        b=bytearray(e.raw)
        section=e.section('.text.'+NAMES[2] if native_mode else '.irq')
        at=section['offset']+(0 if native_mode else 24)
        b[at:at+4],b[at+4:at+8]=b[at+4:at+8],b[at:at+4]
        check(tag+'_fresh_load_order','raw_ELF_reparsed',lambda bb=b,nn=native_mode:elf_contract(ELF(bb),nn,official,False))
        for name,pc,delta,value in [('MMIO_destination_A4',8,0,None),('mask',10,0,None),('branch_A4',12,0,None),
                 ('SP_frame',14,0,None),('provider_A2_offset',16,0,None),('A1_nonzero',18,0,None),
                 ('JAL_rd_zero',20,0,None),('SP_LBU_offset',24,2,None),('SP_LHU_operand',28,1,None),
                 ('payload_offset',32,2,None),('tag_nonzero',36,0,None),('ring_JAL_rd_zero',38,0,None),
                 ('SP_cleanup',42,0,None),('first_MRET',44,0,None),('empty_MRET',48,0,None)]:
            if native_mode:
                region=next((n,a,z) for n,a,z in REGIONS if a<=pc<a+z);section=e.section('.text.'+region[0]);position=section['offset']+pc-region[1]+delta
            else:position=e.section('.irq')['offset']+pc+delta
            xor=128 if 'JAL_rd' in name or name=='branch_A4' else 4
            raw(tag+'_'+name,e,native_mode,position,'<B',e.raw[position]^xor)
    rows=decode(partial.data('.irq'))
    for name,index,field,value in [('MMIO_read16',2,2,'LHU16'),('freshLBU_wrongSPoffset',9,5,23),('ordinaryRET',15,2,'RET')]:
        changed=copy.deepcopy(rows);changed[index][field]=value
        check(name,'parsed_typed_rows',lambda c=changed:typed_contract(c,True))
    mutations=[('IR_MMIO16','load volatile i32','load volatile i16'),('IR_mask','and i32 %6, 3','and i32 %6, 1'),
     ('IR_base','1073766400','1073766404'),('IR_MMIO_offset','%4 = add i32 %3, 12','%4 = add i32 %3, 16'),
     ('IR_frame','addi sp, sp, -32','addi sp, sp, -16'),('IR_LBU','lbu a2, 22(sp)','lbu a2, 23(sp)'),
     ('IR_LHU','lhu a0, 12(sp)','lhu a0, 14(sp)'),('IR_payload','addi a1, sp, 23','addi a1, sp, 24'),
     ('IR_tag','i32 %3, i32 %4, i32 %2, i32 0','i32 %3, i32 %4, i32 %2, i32 1'),
     ('IR_tuple','i32 %3, i32 %4, i32 %2, i32 0','i32 %4, i32 %3, i32 %2, i32 0'),
     ('IR_MRET','mret\\0A','ret\\0A')]
    for name,old,new in mutations:
        need(old in text,'real IR negative fixture '+name);changed=text.replace(old,new,1)
        check(name,'IR_text',lambda c=changed:ir_contract(c,language,False))
    for name,old,new in [('IR_full_attributes','generic-rv32','other-rv32'),('IR_full_metadata','!"int"','!"other"')]:
        need(old in text,'real complete IR fixture');changed=text.replace(old,new,1)
        check(name,'IR_text_full_normalized_pin',lambda c=changed:ir_contract(c,language,True),True)
    for name,changed in [('MD_wrong_target',md.replace('native.o:', 'other.o:',1)),('MD_missing_header',' '.join(md.splitlines()[:-1])),
                         ('MD_extra_dependency',md+'\nextra.h\n')]:
        check(name,'MD_text',lambda c=changed:md_contract(c,llvm,out))
    return results


def evaluate(root,llvm,out,language):
    need(root.resolve()==ROOT,'canonical project root');before=inputs(llvm);official=original()
    native=ELF(out/'native.o');partial=ELF(out/'partial.o')
    nf=elf_contract(native,True,official);pf=elf_contract(partial,False,official)
    need(nf['code_hex']==pf['code_hex'],'partial link preserves all actual native bytes')
    text=(out/'native.ll').read_text(encoding='utf-8');ir=ir_contract(text,language)
    md=(out/'native.d').read_text(encoding='utf-8');deps=md_contract(md,llvm,out)
    commands=[dict(label=n,argv=portable(a,ROOT,llvm),returncode=0) for n,a in recipes(llvm,out,language)]
    need(json.loads((out/'recipes.json').read_bytes())==commands,'complete exact successful producer recipes')
    files=sorted(['native.o','partial.o','native.ll','native.d','recipes.json']+[n+'.log' for n,_ in recipes(llvm,out,language)])
    need(sorted(p.name for p in out.iterdir() if p.name!='verification.json')==files and
         all(p.is_file() and not p.is_symlink() for p in out.iterdir()),'complete exact output inventory')
    for name in ['compile','IR','partial']:need(not (out/(name+'.log')).read_bytes(),'empty successful diagnostic '+name)
    for name,artifact in [('object','native.o'),('partial_object','partial.o')]:
        log=(out/(name+'.log')).read_text();need(str(out/artifact) in log and all(n in log for n in NAMES+[PROVIDER,RING]),'retained artifact/symbol dump binding')
    artifacts=[dict(path=portable(str(out/n),ROOT,llvm),size=(out/n).stat().st_size,sha256=digest(out/n)) for n in files]
    controls=negatives(native,partial,text,language,official,md,llvm,out)
    need(before==inputs(llvm) and all(digest(out/Path(a['path']).name)==a['sha256'] for a in artifacts),'all read source/tool/header/artifact bytes stable')
    record=dict(schema='TSL9-ring-IRQ-adapter-native-v2-formal-v1',language=language,firmware_ready=False,target_executed=False,ISA_emulated=False,
       inputs=[dict(path=portable(str(p),ROOT,llvm),size=p.stat().st_size,sha256=v) for p,v in before.items()],
       original=dict(base=0x8000,start=BASE,end=BASE+52,bytes=52,instructions=17,sha256=ORIGINAL_PIN,typed_rows=EXPECTED),
       native=nf,partial=pf,ir=ir,md_dependencies=deps,recipes=commands,artifacts=artifacts,negative_controls=controls,
       static_contract=dict(MMIO_word_address=0x4000640c,status_mask=3,conditional_frame_bytes=32,
         provider_A1=0,provider_A2_SP_offset=12,fresh_dispatch=['LBU A2,SP+22','LHU A0,SP+12','A1=SP+23'],
         ring_A3=0,then_live_SP_cleanup=32,exits='two MRET; no ordinary RET or RA save/restore',
         provider_ABI_closed=False),limitations=[
        'Five symbols are private interrupt regions, not independent ordinary C ABI functions.',
        'All three control immediates remain pending in actual ET_REL bytes; two providers remain UND.',
        'Provider18D78 has not been established as readable C or a closed ABI; raw opcode archival bodies are not provider resolution.',
        'MRET has architectural state/privilege effects; IRQ entry, vector routing, stack ownership, resident/silicon behavior and physical hardware remain unproved.',
        'No target/ISA/MMIO execution, firmware BIN, OTA acceptance or successful flashing.'])
    encoded=(json.dumps(record,sort_keys=True,indent=2,ensure_ascii=True)+'\n').encode()
    need(not re.search(rb'(?i)[a-z]:[/\\]|/(?:users|home)/',encoded),'portable LF receipt has no host path')
    return record,encoded.decode()


def main():
    p=argparse.ArgumentParser(description=__doc__);a=p.add_mutually_exclusive_group(required=True)
    a.add_argument('--out-dir',type=Path);a.add_argument('--replay',type=Path)
    p.add_argument('--language',choices=['c','cpp']);p.add_argument('--llvm-bin',type=Path,
       default=Path(os.environ.get('USERPROFILE',str(Path.home())))/'AppData/Local/Android/Sdk/ndk/27.1.12297006/toolchains/llvm/prebuilt/windows-x86_64/bin')
    p.add_argument('--require-firmware-ready',action='store_true');args=p.parse_args();llvm=args.llvm_bin.resolve()
    if args.replay:
        receipt=args.replay.resolve();out=receipt.parent;saved=json.loads(receipt.read_bytes());language=saved['language']
        need(args.language is None or language==args.language,'replay language')
    else:need(args.language is not None,'build language');language=args.language;out=args.out_dir.resolve()
    need(out.is_relative_to(HERE/'build') and out.parent.name.startswith('verified-') and out.name==language,'owned formal IRQ output')
    if not args.replay:
        need(not out.exists(),'fresh output only');before=inputs(llvm);out.mkdir(parents=True);commands=[]
        for label,argv in recipes(llvm,out,language):
            child=subprocess.run(argv,cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
            (out/(label+'.log')).write_bytes(child.stdout);commands.append(dict(label=label,argv=portable(argv,ROOT,llvm),returncode=child.returncode))
            need(child.returncode==0,'actual compiler/linker recipe failed '+label)
        (out/'recipes.json').write_bytes((json.dumps(commands,indent=2)+'\n').encode());need(before==inputs(llvm),'inputs stable across actual build')
    record,encoded=evaluate(ROOT,llvm,out,language)
    if args.replay:need(saved==record and receipt.read_bytes()==encoded.encode(),'complete canonical LF replay equality')
    else:(out/'verification.json').write_bytes(encoded.encode())
    print(json.dumps(dict(result='PASS',language=language,bytes=52,instructions=17,FUNCs=5,UND=2,RELA=3,controls=len(record['negative_controls']),
                          receipt_sha256=sha(encoded.encode()),firmware_ready=False)))
    if args.require_firmware_ready:
        print('REJECTED: pending controls, unknown provider/IRQ/silicon ABI and hardware; firmware_ready=false.',file=sys.stderr);return 1
    return 0


if __name__=='__main__':
    try:sys.exit(main())
    except (ValueError,OSError,KeyError,IndexError,StopIteration) as exc:
        print('FAIL: '+str(exc),file=sys.stderr);sys.exit(1)
