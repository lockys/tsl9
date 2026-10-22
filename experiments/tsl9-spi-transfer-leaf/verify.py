#!/usr/bin/env python3
"""Bounded offline RV32 SPI leaf compiler/reader; never execute emitted code.

The eight FUNC symbols are architectural regions, not independent C ABI calls.
Receipts describe this 72-byte component only, never a flash-ready firmware.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import struct
import subprocess
import sys
from pathlib import Path

BASE = 0x16896
SOURCE = 'experiments/tsl9-spi-transfer-leaf/src/spi_transfer_ports.c'
LINKER = 'experiments/tsl9-spi-transfer-leaf/component.ld'
FIRMWARE = 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
SOURCE_PIN = '1f68851e9ae71d1ef56147e554fdaa53ae0918e2bfac73bad32a110549fe3182'
LINKER_PIN = '755acb8fd08dcd580a1f11394f88ba68f3fb1224ccc6549eea0a9035db4a3a5e'
FIRMWARE_PIN = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
CODE_PIN = '654d0f600794c1548c617d0f476ca4f0fa5aaf780f49be7c328b3df69e8878dc'
NATIVE_PIN = 'e900eae885f3601bd7f30ac8fee012a7e03db65a1d2f07bf512736acea7eb663'
LINKED_PIN = 'e29870dec29fa8662bf1e22de3d364e88fa1a6c5fbc043933da01918214ae731'
HEADER_PIN = '7ce5540d5fb6e8da9760928e76cbdd5ebef329d701ad598d30d8e6f9d5d78b34'
TOOLS = {'clang': '047dfde05acc6fcce5af669e25cd8d40b4f509b8842d151d6d8a43a1c6a35fd6',
         'ld.lld': 'fe7f55c0c78b3d87f33b905a3874e10e872ca7beef53a8199d7ff9ac6641ec3f',
         'llvm-objdump': 'de40d1188fe63ff373e1a5dd83a12e2cb4545ca3b314da16a476ecf072e5a0fa'}
IR_PINS = {'c': 'f54522a8e9f710c9e4e67f1e2805097a12d61c673e9ec569fa0373e2276bcc1b',
           'cpp': '5f1a6c2b2f3cdb4363e67ef908a10fa8c8706ba9dc6fb4a78d7b01a95bc077ff'}
NAMES = ['tsl9_spi_transfer_entry_16896', 'tsl9_spi_tx_poll_1689e',
         'tsl9_spi_tx_ready_168a6', 'tsl9_spi_rx_poll_168b6',
         'tsl9_spi_rx_done_168be', 'tsl9_spi_tx_wait_168c8',
         'tsl9_spi_timeout_168d0', 'tsl9_spi_rx_wait_168d4']
STARTS = [0, 8, 16, 32, 40, 50, 58, 62]
SIZES = [8, 8, 16, 8, 10, 8, 4, 10]
RELATIONS = [(14, 44, 5), (38, 44, 7), (56, 44, 1), (68, 44, 3), (70, 45, 6)]
EXPECTED_HEX = ('9307f00fb736014003d78600098b15c3420541812396a6009307f00fb7360140'
                '03d78600058b01cf03d5c6001375f50f8280fd1793f7f70fe1fb01458280fd17'
                '93f7f70ff1ffd5bf')


def require(ok, message):
    if not ok:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def file_sha(path):
    return sha(Path(path).read_bytes())


class ELF:
    """Strict little-endian ELF32 reader. Accepts Path/str or actual bytes.

    Public API: header, sections, symbols, relocations, section(name), data(s).
    Parsed records retain actual section indices, ownership and symbol indices.
    No target execution and no dependency on another project parser.
    """
    def __init__(self, path_or_bytes):
        self.raw = bytes(path_or_bytes) if isinstance(path_or_bytes, (bytes, bytearray)) else Path(path_or_bytes).read_bytes()
        b = self.raw
        require(len(b) >= 52, 'ELF short header')
        h = struct.unpack_from('<16sHHIIIIIHHHHHH', b)
        require(h[0] == b'\x7fELF\x01\x01\x01' + b'\0' * 9, 'ELF ident')
        require(h[2] == 243 and h[3] == 1 and h[8] == 52 and h[11] == 40, 'ELF architecture/header')
        require(0 < h[12] < 64 and h[13] < h[12], 'ELF section count')
        self.header = list(h[1:])
        self.program_headers = []
        if h[10]:
            require(h[9] == 32 and h[10] < 16, 'ELF program header shape')
            for i in range(h[10]):
                self.program_headers.append(list(self.unpack('<8I', h[5] + 32*i)))
        rows = [self.unpack('<10I', h[6] + 40*i) for i in range(h[12])]
        ns = rows[h[13]]
        names = self.slice(ns[4], ns[5])
        keys = ['name_offset', 'type', 'flags', 'address', 'offset', 'size', 'link', 'info', 'align', 'entsize']
        self.sections = []
        for i, r in enumerate(rows):
            s = dict(zip(keys, r)); s['index'] = i; s['name'] = self.string(names, r[0])
            if r[1] != 8:
                self.slice(r[4], r[5])
            self.sections.append(s)
        require(len({s['name'] for s in self.sections}) == len(rows), 'duplicate section names')
        tables = [s for s in self.sections if s['type'] == 2]
        require(len(tables) == 1, 'exactly one symbol table')
        table = tables[0]
        require(table['entsize'] == 16 and table['size'] % 16 == 0 and table['link'] < len(rows), 'symbol table shape')
        strings = self.data(self.sections[table['link']])
        self.symbols = []
        for i in range(table['size']//16):
            n, v, z, info, other, si = self.unpack('<IIIBBH', table['offset'] + 16*i)
            require(si < len(rows) or si == 0xfff1, 'symbol section index')
            self.symbols.append(dict(index=i, name=self.string(strings, n), value=v, size=z, info=info, other=other, section=si))
        self.relocations = []
        for s in self.sections:
            require(s['type'] != 9, 'REL records forbidden')
            if s['type'] == 4:
                require(s['entsize'] == 12 and s['size'] % 12 == 0 and s['link'] == table['index'] and s['info'] < len(rows), 'RELA shape')
                for i in range(s['size']//12):
                    offset, info, addend = self.unpack('<IIi', s['offset'] + 12*i)
                    require(info >> 8 < len(self.symbols), 'RELA symbol index')
                    self.relocations.append(dict(section=s['info'], offset=offset, type=info & 255, symbol=info >> 8, addend=addend))

    def slice(self, start, size):
        require(0 <= start <= len(self.raw) and 0 <= size <= len(self.raw)-start, 'ELF extent')
        return self.raw[start:start+size]

    def unpack(self, fmt, at):
        self.slice(at, struct.calcsize(fmt))
        return struct.unpack_from(fmt, self.raw, at)

    @staticmethod
    def string(buf, at):
        require(at < len(buf), 'ELF string offset')
        end = buf.find(b'\0', at)
        require(end >= at, 'ELF unterminated string')
        return buf[at:end].decode('ascii')

    def section(self, name):
        matches = [s for s in self.sections if s['name'] == name]
        require(len(matches) == 1, 'missing/duplicate section ' + name)
        return matches[0]

    def data(self, section):
        s = self.section(section) if isinstance(section, str) else section
        require(s['type'] != 8, 'NOBITS has no file bytes')
        return self.slice(s['offset'], s['size'])


def signed(v, bits):
    return v - (1 << bits) if v & (1 << (bits-1)) else v


def decode(code):
    """Decode only the RV32 instructions actually permitted by this leaf."""
    rows = []
    at = 0
    while at < len(code):
        require(at+2 <= len(code), 'instruction extent')
        h = int.from_bytes(code[at:at+2], 'little'); width = 4 if h & 3 == 3 else 2
        require(at+width <= len(code), 'wide instruction extent')
        w = int.from_bytes(code[at:at+width], 'little')
        if width == 4:
            op, rd, rs1, rs2, f3 = w & 127, (w >> 7) & 31, (w >> 15) & 31, (w >> 20) & 31, (w >> 12) & 7
            imm = signed(w >> 20, 12)
            if op == 0x13 and f3 == 0: ins = ['addi', rd, rs1, imm]
            elif op == 0x13 and f3 == 7: ins = ['andi', rd, rs1, imm]
            elif op == 0x37: ins = ['lui', rd, w & 0xfffff000]
            elif op == 3 and f3 == 5: ins = ['lhu', rd, rs1, imm]
            elif op == 0x23 and f3 == 1: ins = ['sh', rs2, rs1, signed(((w >> 25) << 5) | ((w >> 7) & 31), 12)]
            else: raise ValueError('forbidden/unknown wide instruction')
        else:
            q, f3, rd = h & 3, h >> 13, (h >> 7) & 31
            ci = signed(((h >> 12) & 1) << 5 | (h >> 2) & 31, 6)
            if h == 0x8082: ins = ['ret', 1]
            elif q == 1 and f3 == 2: ins = ['addi', rd, 0, ci]
            elif q == 1 and f3 == 0: ins = ['addi', rd, rd, ci]
            elif q == 2 and f3 == 0: ins = ['slli', rd, rd, (h >> 2) & 31]
            elif q == 1 and f3 == 4 and (h >> 10) & 3 == 0: ins = ['srli', 8+((h >> 7)&7), 8+((h >> 7)&7), (h >> 2)&31]
            elif q == 1 and f3 == 4 and (h >> 10) & 3 == 2: ins = ['andi', 8+((h >> 7)&7), 8+((h >> 7)&7), ci]
            elif q == 1 and f3 in (6, 7):
                d = ((h >> 12)&1)<<8 | ((h >> 10)&3)<<3 | ((h >> 5)&3)<<6 | ((h >> 3)&3)<<1 | ((h >> 2)&1)<<5
                ins = ['beqz' if f3 == 6 else 'bnez', 8+((h >> 7)&7), at+signed(d, 9)]
            elif q == 1 and f3 == 5:
                d = ((h>>12)&1)<<11 | ((h>>11)&1)<<4 | ((h>>9)&3)<<8 | ((h>>8)&1)<<10 | ((h>>7)&1)<<6 | ((h>>6)&1)<<7 | ((h>>3)&7)<<1 | ((h>>2)&1)<<5
                ins = ['j', at+signed(d, 12)]
            else: raise ValueError('forbidden/unknown compressed instruction')
        rows.append(dict(offset=at, width=width, raw=code[at:at+width].hex(), instruction=ins))
        at += width
    return rows


EXPECTED = [
 [0,4,['addi',15,0,255]], [4,4,['lui',13,0x40013000]],
 [8,4,['lhu',14,13,8]], [12,2,['andi',14,14,2]], [14,2,['beqz',14,50]],
 [16,2,['slli',10,10,16]], [18,2,['srli',10,10,16]], [20,4,['sh',10,13,12]],
 [24,4,['addi',15,0,255]], [28,4,['lui',13,0x40013000]],
 [32,4,['lhu',14,13,8]], [36,2,['andi',14,14,1]], [38,2,['beqz',14,62]],
 [40,4,['lhu',10,13,12]], [44,4,['andi',10,10,255]], [48,2,['ret',1]],
 [50,2,['addi',15,15,-1]], [52,4,['andi',15,15,255]], [56,2,['bnez',15,8]],
 [58,2,['addi',10,0,0]], [60,2,['ret',1]],
 [62,2,['addi',15,15,-1]], [64,4,['andi',15,15,255]], [68,2,['bnez',15,32]], [70,2,['j',58]]]


def code_contract(code, native=False, full=True):
    rows = decode(code)
    got = [[r['offset'], r['width'], r['instruction']] for r in rows]
    want = copy.deepcopy(EXPECTED)
    if native:
        for row in want:
            if row[0] in [x[0] for x in RELATIONS]: row[2][-1] = row[0]
    require(got == want, 'typed instructions/order/width/register/control contract')
    require(len(code) == 72 and len(rows) == 25, 'code span/instruction count')
    if full and not native: require(sha(code) == CODE_PIN, 'full code SHA')
    return rows


def elf_contract(elf, native, full=True):
    require(elf.header == ([1,243,1,0,0,1136,1,52,0,0,40,20,1] if native else [2,243,1,BASE,52,2876,1,52,32,4,40,6,4]), 'exact ELF header')
    require(elf.program_headers == ([] if native else [[6,52,90164,90164,128,128,4,4],[1,0,90112,90112,180,180,4,4096],[1,2198,BASE,BASE,72,72,5,4096],[1685382481,0,0,0,0,0,6,0]]), 'exact program headers; only expected executable mapping')
    regions = [elf.section('.text.'+n) for n in NAMES] if native else [elf.section('.spi')]
    require([(s['size'],s['flags'],s['type'],s['align'],s['address']) for s in regions] == ([(z,6,1,2,0) for z in SIZES] if native else [(72,6,1,2,BASE)]), 'region sizes/AX/alignment/address')
    require([s['name'] for s in elf.sections if s['flags'] & 2 and s['size']] == [s['name'] for s in regions], 'only expected allocated regions')
    require(not any(s['type']==8 for s in elf.sections), 'no NOBITS/data allocation')
    globals_ = [s for s in elf.symbols if s['info'] >> 4]
    expected_symbols = []
    for i in [0,1,5,2,3,7,4,6]:
        expected_symbols.append(dict(index=12+len(expected_symbols) if native else 11+len(expected_symbols),name=NAMES[i],value=0 if native else BASE+STARTS[i],size=SIZES[i],info=18,other=0,section=regions[i]['index'] if native else 1))
    require(globals_ == expected_symbols, 'exact genuine global FUNC ownership/values/sizes')
    locals_ = [dict(s) for s in elf.symbols if not s['info'] >> 4]
    want_locals = [dict(index=0,name='',value=0,size=0,info=0,other=0,section=0),dict(index=1,name='spi_transfer_ports.c',value=0,size=0,info=4,other=0,section=0xfff1)]
    for i in range(8):
        want_locals.append(dict(index=i+2,name='$x.'+str(i),value=0 if native else BASE+STARTS[i],size=0,info=0,other=0,section=regions[i]['index'] if native else 1))
    if native: want_locals.append(dict(index=10,name='$d.8',value=0,size=0,info=0,other=0,section=15))
    want_locals.append(dict(index=len(want_locals),name='$d.9',value=0,size=0,info=0,other=0,section=17 if native else 0xfff1))
    require(locals_ == want_locals, 'exact local metadata symbols; no invented ABS providers')
    code = b''.join(elf.data(s) for s in regions)
    code_contract(code, native, full)
    want_rel = []
    if native:
        for site, kind, target in RELATIONS:
            owner = max(i for i, start in enumerate(STARTS) if start <= site)
            symbol = next(s for s in globals_ if s['name'] == NAMES[target])
            want_rel.append(dict(section=regions[owner]['index'],offset=site-STARTS[owner],type=kind,symbol=symbol['index'],addend=0))
    require(elf.relocations == want_rel, 'exact real-FUNC symbolic relocation graph')
    # Exact all-section metadata, including offsets, string/symbol table shapes,
    # attributes and addrsig. Full-file hash additionally binds program headers.
    shapes = [(s['name'],s['type'],s['flags'],s['address'],s['offset'],s['size'],s['link'],s['info'],s['align'],s['entsize']) for s in elf.sections]
    if native:
        expected_shapes = [('',0,0,0,0,0,0,0,0,0),('.strtab',3,0,0,724,411,0,0,1,0),('.text',1,6,0,52,0,0,0,2,0)]
        indices = [3,4,6,7,9,10,12,13]
        reloff = {1:(656,12),3:(668,12),5:(680,12),7:(692,24)}
        for i,n in enumerate(NAMES):
            expected_shapes.append(('.text.'+n,1,6,0,52+STARTS[i],SIZES[i],0,0,2,0))
            if i in reloff:
                off,z = reloff[i];expected_shapes.append(('.rela.text.'+n,4,64,0,off,z,19,indices[i],4,12))
        expected_shapes += [('.comment',1,48,0,124,159,0,0,1,1),('.note.GNU-stack',1,0,0,283,0,0,0,1,0),('.riscv.attributes',0x70000003,0,0,283,52,0,0,1,0),('.llvm_addrsig',0x6fff4c03,0x80000000,0,716,8,19,0,1,0),('.symtab',2,0,0,336,320,1,12,4,16)]
    else:
        expected_shapes = [('',0,0,0,0,0,0,0,0,0),('.spi',1,6,BASE,2198,72,0,0,2,0),('.text',1,6,BASE+72,2270,0,0,0,2,0),('.symtab',2,0,0,2272,304,5,11,4,16),('.shstrtab',3,0,0,2576,38,0,0,1,0),('.strtab',3,0,0,2614,259,0,0,1,0)]
    require(shapes == expected_shapes, 'exact all-section metadata inventory')
    if full: require(sha(elf.raw) == (NATIVE_PIN if native else LINKED_PIN), 'whole ELF pin')
    return dict(sha256=sha(elf.raw),header=elf.header,program_headers=elf.program_headers,sections=elf.sections,symbols=elf.symbols,relocations=elf.relocations,code_sha256=sha(code),instructions=decode(code))


def normalized_ir(text):
    return '\n'.join(text.splitlines()[2:])+'\n'


def ir_contract(text, language, full=True):
    norm = normalized_ir(text)
    blocks = re.findall(r'^define .*?@([^(]+)\([^\n]*\{\n(.*?)^\}', text, re.M|re.S)
    require([n for n,_ in blocks] == NAMES, 'IR exact eight regions')
    b = dict(blocks)
    require(norm.count('load volatile i16,') == 3 and norm.count('store volatile i16 ') == 1 and norm.count('load volatile') == 3 and norm.count('store volatile') == 1, 'IR exact volatile widths/counts')
    require(norm.count('R_RISCV_RVC_BRANCH') == 4 and norm.count('R_RISCV_RVC_JUMP') == 1, 'IR five symbolic control ports')
    bodies='\n'.join(t for _,t in blocks)
    require(not re.search(r'call[^\n]*@|\bcallbr\b|llvm\.assume|\bfence\b|\batomic\b|\balloca\b',bodies), 'IR no ordinary calls/assumptions/frame')
    require('i32 255' in b[NAMES[0]] and 'i32 1073819648, i32 %0' in b[NAMES[0]], 'IR entry count/base/input live port')
    for name, mask, target in [(NAMES[1],2,NAMES[5]),(NAMES[3],1,NAMES[7])]:
        t=b[name]
        require('"={x13},~{memory}"()' in t and '%2 = add i32 %1, 8' in t and '%4 = load volatile i16, ptr %3' in t and f'%5 = and i16 %4, {mask}\n' in t and '%6 = zext nneg i16 %5 to i32' in t and target in t and '(i32 %6)' in t, 'IR fresh status/mask/control dataflow')
    t=b[NAMES[2]]
    anchors=['"={x10},={x13},~{memory}"()', '%4 = and i32 %2, 65535', '(i32 %4)', '%6 = trunc i32 %5 to i16', '%7 = add i32 %3, 12', 'store volatile i16 %6, ptr %8', '(i32 255)', '(i32 1073819648)']
    require(all(a in t for a in anchors) and [t.index(a) for a in anchors] == sorted(t.index(a) for a in anchors), 'IR TX live import/trunc16/SH before count/base reinit')
    t=b[NAMES[4]]
    require('%2 = add i32 %1, 12' in t and '%4 = load volatile i16, ptr %3' in t and '%5 = and i16 %4, 255\n' in t and '%6 = zext nneg i16 %5 to i32' in t and '(i32 %6)' in t and 'ret i32 %7' in t, 'IR RX fresh16/mask8/return residue')
    for name,target in [(NAMES[5],NAMES[1]),(NAMES[7],NAMES[3])]:
        t=b[name]
        require('"={x15},~{memory}"()' in t and '%2 = add i32 %1, 255\n' in t and '%3 = and i32 %2, 255\n' in t and '(i32 %3)' in t and target in t, 'IR fresh count decrement/mask8/control dataflow')
    require('(i32 0)' in b[NAMES[6]] and 'ret i32 %1' in b[NAMES[6]], 'IR timeout zero return')
    require(NAMES[6] in b[NAMES[7]] and b[NAMES[7]].index(NAMES[3]) < b[NAMES[7]].index(NAMES[6]), 'IR RX wait branch before timeout jump')
    if full: require(sha(norm.encode()) == IR_PINS[language], 'full normalized SSA pin')
    return dict(normalized_sha256=sha(norm.encode()),volatile_load16=3,volatile_store16=1,explicit_control_ports=5,function_names=NAMES)


def source_contract(text):
    require(sha(text.encode()) == SOURCE_PIN, 'source exact bytes/LF pin')
    require(not re.search(r'\.(?:byte|2byte|4byte|word|insn)|__builtin_(?:assume|expect)',text), 'source no handbyte/probability/assumption carrier')
    require(text.count('R_RISCV_RVC_BRANCH') == 4 and text.count('R_RISCV_RVC_JUMP') == 1, 'source explicit control ports')
    return dict(sha256=SOURCE_PIN,architectural_regions=8,ordinary_c_abi_functions=False)


def flags(language):
    f=['--target=riscv32-unknown-elf','-march=rv32imac_zicsr','-mabi=ilp32','-Oz','-mllvm','-enable-machine-outliner=never','-ffreestanding','-fno-builtin','-fno-stack-protector','-fno-unwind-tables','-fno-asynchronous-unwind-tables','-mno-relax','-ffunction-sections','-fdata-sections','-Wall','-Wextra','-Werror']
    f += ['-ffixed-x'+str(i) for i in range(1,32) if i not in (10,13,14,15)]
    return f+(['-x','c','-std=c11'] if language=='c' else ['-x','c++','-std=c++17','-fno-exceptions'])


def recipes(root, llvm, out, language):
    exe=lambda n:str(llvm/(n+('.exe' if sys.platform=='win32' else '')))
    src=str(root/SOURCE);obj=str(out/'native.o'); linked=str(out/'linked.elf'); f=flags(language)
    dump=['--mattr=+m,+a,+c,+zicsr','-d','-r','-t','-h']
    return [('compile',[exe('clang')]+f+['-MD','-MF',str(out/'native.d'),'-MT',obj,'-c',src,'-o',obj]),
            ('IR',[exe('clang')]+f+['-S','-emit-llvm',src,'-o',str(out/'native.ll')]),
            ('object',[exe('llvm-objdump')]+dump+[obj]),
            ('link',[exe('ld.lld'),'--no-relax','-T',str(root/LINKER),obj,'-o',linked]),
            ('linked',[exe('llvm-objdump')]+dump+[linked])]


def portable(value, root, llvm):
    if isinstance(value,str):
        # Header lies outside bin; replace the prebuilt prefix before bin.
        for old,new in [(str(llvm),'${LLVM_BIN}'),(str(llvm.parent),'${LLVM_BIN}/..'),(str(root),'${TSL9_ROOT}')]:
            value=value.replace(old.replace('\\','/'),new).replace(old.replace('/','\\'),new)
        return value.replace('\\','/')
    if isinstance(value,list):return [portable(v,root,llvm) for v in value]
    if isinstance(value,dict):return {portable(k,root,llvm):portable(v,root,llvm) for k,v in value.items()}
    return value


def inputs(root, llvm):
    paths=[root/SOURCE,root/LINKER,root/FIRMWARE,Path(__file__).resolve(),llvm.parent/'lib/clang/18/include/stdint.h']
    expected=[SOURCE_PIN,LINKER_PIN,FIRMWARE_PIN,None,HEADER_PIN]
    for n,pin in TOOLS.items():paths.append(llvm/(n+('.exe' if sys.platform=='win32' else '')));expected.append(pin)
    records=[]
    for path,pin in zip(paths,expected):
        actual=file_sha(path);require(pin is None or actual==pin,'pinned input '+path.name)
        records.append(dict(path=portable(str(path),root,llvm),size=path.stat().st_size,sha256=actual))
    return records


def md_contract(raw, root, llvm, out):
    # Clang Make output uses backslash continuations and escapes spaces only;
    # normalize Windows path separators before exact closure comparison.
    t=raw.replace('\\\n',' ').replace('\\\r\n',' ').replace('\\ ','\x01').replace('\\','/')
    target=str(out/'native.o').replace('\\','/')
    require(t.startswith(target+':'), 'MD exact output target')
    rest=t[len(target)+1:].strip()
    deps=[x.replace('\x01',' ') for x in rest.split()]
    want=[str(root/SOURCE).replace('\\','/'),str(llvm.parent/'lib/clang/18/include/stdint.h').replace('\\','/')]
    require(deps==want,'MD complete two-file source/header closure')
    return portable(want,root,llvm)


def negatives(native, linked, text, language):
    results=[]
    def rejected(label, check):
        try:check()
        except (ValueError,KeyError,IndexError,struct.error):results.append(dict(name=label,rejected=True));return
        raise ValueError('negative accepted: '+label)
    # Independent instruction gates: no full code SHA or ELF SHA is consulted.
    for label,at,xor in [('TX-count',0,0x10),('base',6,1),('TX-LHU-width',9,0x10),('TX-status-mask',12,4),('TX-branch-polarity',15,0x20),('truncate16',16,4),('SH-width',21,0x10),('RX-count',24,0x10),('RX-mask',36,4),('RX-LHU-offset',42,0x10),('RX-mask8',46,0x10),('TX-decrement',50,4),('TX-mask8',54,0x10),('TX-backedge',56,4),('timeout-zero',58,4),('RX-backedge',68,4),('timeout-tail-target',70,4)]:
        code=bytearray(bytes.fromhex(EXPECTED_HEX));code[at]^=xor
        rejected('typed-'+label,lambda code=code:code_contract(bytes(code),False,False))
    for label,key,value in [('type','type',45),('addend','addend',2),('site','offset',4),('target','symbol',12)]:
        e=copy.deepcopy(native);e.relocations[0][key]=value
        rejected('relocation-'+label,lambda e=e:elf_contract(e,True,False))
    for label,change in [('function-size',lambda e:e.symbols[12].update(size=10)),('function-ABS',lambda e:e.symbols[12].update(section=0xfff1)),('section-alignment',lambda e:e.sections[3].update(align=4)),('extra-allocated-data',lambda e:e.sections[15].update(flags=50)),('linked-adjacency',lambda e:e.symbols[12].update(value=BASE+10))]:
        e=copy.deepcopy(linked if label=='linked-adjacency' else native);change(e)
        rejected('metadata-'+label,lambda e=e,label=label:elf_contract(e,label!='linked-adjacency',False))
    e=copy.deepcopy(linked);e.program_headers[2][5]+=4
    rejected('metadata-executable-mapping',lambda:elf_contract(e,False,False))
    for label,old,new in [('volatile-width','load volatile i16','load volatile i32'),('fresh-base','"={x13},~{memory}"()','"={x14},~{memory}"()'),('status-mask','%5 = and i16 %4, 2\n','%5 = and i16 %4, 1\n'),('TX-store-order','store volatile i16 %6','store volatile i16 %5'),('truncate16','%4 = and i32 %2, 65535','%4 = and i32 %2, 255'),('fresh-count','%2 = add i32 %1, 255\n','%2 = add i32 %1, 254\n'),('count-mask','%3 = and i32 %2, 255\n','%3 = and i32 %2, 511\n'),('timeout-return','ret i32 %1','ret i32 1')]:
        require(old in text,'negative IR anchor');mut=text.replace(old,new,1)
        rejected('IR-'+label,lambda mut=mut:ir_contract(mut,language,False))
    rejected('full-SSA-only',lambda:ir_contract(text.replace('!"wchar_size", i32 4','!"wchar_size", i32 2'),language,True))
    return results


def evaluate(root, llvm, out, language):
    before=inputs(root,llvm)
    firmware=(root/FIRMWARE).read_bytes();require(len(firmware)==76800,'firmware size')
    code=firmware[BASE-0x8000:BASE-0x8000+72]
    require(code==bytes.fromhex(EXPECTED_HEX) and sha(code)==CODE_PIN,'official complete SPI bytes')
    require(firmware[BASE-0x8000+72:BASE-0x8000+88].hex()=='011122cc26ca06ce937715003284b684','next unowned bytes')
    native=ELF(out/'native.o');linked=ELF(out/'linked.elf');text=(out/'native.ll').read_text(encoding='utf-8')
    source=source_contract((root/SOURCE).read_bytes().decode())
    ns=elf_contract(native,True);ls=elf_contract(linked,False);irs=ir_contract(text,language)
    md=md_contract((out/'native.d').read_text(encoding='utf-8'),root,llvm,out)
    expected_recipes=[dict(label=label,argv=portable(argv,root,llvm),returncode=0) for label,argv in recipes(root,llvm,out,language)]
    require(json.loads((out/'recipes.json').read_text())==expected_recipes,'complete exact command recipes')
    expected_files=sorted(['native.o','native.ll','native.d','linked.elf','recipes.json']+[n+'.log' for n,_ in recipes(root,llvm,out,language)])
    actual=sorted(p.name for p in out.iterdir() if p.name!='verification.json')
    require(actual==expected_files and all(p.is_file() and not p.is_symlink() for p in out.iterdir()),'exact output/log inventory')
    for name in ('compile.log','IR.log','link.log'):require(not (out/name).read_bytes(),'successful compiler/linker logs empty')
    for name in ('object.log','linked.log'):
        log=(out/name).read_text();require(all(n in log for n in NAMES),'retained objdump function coverage')
    artifact=[dict(path=portable(str(out/name),root,llvm),size=(out/name).stat().st_size,sha256=file_sha(out/name)) for name in expected_files]
    controls=negatives(native,linked,text,language)
    require(before==inputs(root,llvm),'inputs changed during evaluation')
    record=dict(schema='tsl9-spi-transfer-leaf-v1',language=language,firmware_ready=False,
                root='${TSL9_ROOT}',llvm_bin='${LLVM_BIN}',out_dir=portable(str(out),root,llvm),inputs=before,
                source=source,original=dict(file_sha256=FIRMWARE_PIN,base=0x8000,start=BASE,end=BASE+72,sha256=CODE_PIN,next_unowned16='011122cc26ca06ce937715003284b684'),
                native=ns,linked=ls,ir=irs,md_dependencies=md,recipes=expected_recipes,artifacts=artifact,negative_controls=controls,
                static_contract=dict(max_status_polls_per_phase=255,status_read_precedes_decrement=True,tx_store_width=16,rx_data_load_width=16,rx_result_mask=255,
                  normal_success=dict(a0='fresh DATA16 & 255',a3='0x40013000',a4=1,a5='256 - RX ready poll index (1..255)'),
                  either_timeout=dict(a0=0,a3='0x40013000',a4=0,a5=0),own_written_gprs=[10,13,14,15],frame_bytes=0,calls=0,csr=0,fences=0),
                limitations=['Static decode/IR and native compilation only; no target or ISA execution.',
                  'Eight symbols are architectural fallthrough/control regions, not ordinary independently callable C functions.',
                  'No physical hardware, IRQ/fault interleaving, peripheral timing, full image placement or whole firmware equivalence proved.',
                  'This diagnostic component is not a flashable BIN; firmware_ready remains false.'])
    encoded=json.dumps(record,ensure_ascii=False,sort_keys=True,indent=2)+'\n'
    require(not re.search(r'(?i)[a-z]:[/\\]|/(?:users|home)/',encoded),'receipt personal/absolute host path')
    return record,encoded


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    action=parser.add_mutually_exclusive_group(required=True)
    action.add_argument('--out-dir',type=Path);action.add_argument('--replay',type=Path)
    parser.add_argument('--language',choices=['c','cpp'])
    parser.add_argument('--llvm-bin',type=Path,default=Path.home()/'AppData/Local/Android/Sdk/ndk/27.1.12297006/toolchains/llvm/prebuilt/windows-x86_64/bin')
    parser.add_argument('--require-firmware-ready',action='store_true')
    args=parser.parse_args();root=Path(__file__).resolve().parents[2];llvm=args.llvm_bin.resolve()
    if args.replay:
        receipt=args.replay.resolve();saved=json.loads(receipt.read_text(encoding='utf-8'));out=receipt.parent
        language=saved['language'];require(args.language is None or args.language==language,'replay language')
        record,encoded=evaluate(root,llvm,out,language)
        require(record==saved and receipt.read_bytes()==encoded.encode(),'complete receipt equality and portable LF')
    else:
        require(args.language is not None,'--language required for build');language=args.language;out=args.out_dir.resolve()
        require(out.is_relative_to(root/'experiments/tsl9-spi-transfer-leaf/build') and out!=root/'experiments/tsl9-spi-transfer-leaf/build','owned output directory')
        require(not out.exists(),'fresh output directory required')
        before=inputs(root,llvm);out.mkdir(parents=True)
        rs=[]
        for label,argv in recipes(root,llvm,out,language):
            result=subprocess.run(argv,cwd=root,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,check=False)
            (out/(label+'.log')).write_bytes(result.stdout)
            rs.append(dict(label=label,argv=portable(argv,root,llvm),returncode=result.returncode))
            require(result.returncode==0,'native recipe failed: '+label)
        (out/'recipes.json').write_bytes((json.dumps(rs,indent=2)+'\n').encode())
        require(before==inputs(root,llvm),'inputs changed during native build')
        record,encoded=evaluate(root,llvm,out,language)
        (out/'verification.json').write_bytes(encoded.encode())
    print(json.dumps(dict(result='PASS',language=language,receipt_sha256=sha(encoded.encode()),elfs=2,instructions=25,bytes=72,controls=len(record['negative_controls']),firmware_ready=False)))
    if args.require_firmware_ready:
        print('REJECTED: firmware_ready=false; component-only static/native evidence.',file=sys.stderr)
        return 1
    return 0


if __name__=='__main__':
    try:sys.exit(main())
    except (ValueError,OSError,KeyError,struct.error) as error:
        print('FAIL: '+str(error),file=sys.stderr);sys.exit(1)
