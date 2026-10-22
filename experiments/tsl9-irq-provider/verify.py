#!/usr/bin/env python3
"""Compile/replay the bounded 164B private provider; never execute target code."""
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
SOURCE=HERE/'src/irq_provider.v2.c'
READER=ROOT/'experiments/tsl9-spi-transfer-leaf/verify.py'
FIRMWARE=ROOT/'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
PINS={SOURCE:'f6d76a207fc3415ff8362c580d225f4a4e1d2714fdfcfeac63d54a77ad1ce653',
 HERE/'component.ld':'bbf51846ab09a20aff1fc620f1341a3e62a1b22f90d762b8112c3dc18a5e61f5',
 HERE/'probe.py':'d8f88950bf3d00d5f5873c856beb4380cc9f4a83653f855bc97ebcff5116f9e3',
 READER:'8c8eb8e01b9fc30eb7150682aa8848e47fe4a1254c6f87b05e657244a11b6de8',
 FIRMWARE:'0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'}
TOOLS={'clang.exe':'047dfde05acc6fcce5af669e25cd8d40b4f509b8842d151d6d8a43a1c6a35fd6',
 'ld.lld.exe':'fe7f55c0c78b3d87f33b905a3874e10e872ca7beef53a8199d7ff9ac6641ec3f',
 'llvm-objdump.exe':'de40d1188fe63ff373e1a5dd83a12e2cb4545ca3b314da16a476ecf072e5a0fa'}
HEADER_PIN='7ce5540d5fb6e8da9760928e76cbdd5ebef329d701ad598d30d8e6f9d5d78b34'
ELF_PINS={True:'21f174eee24576a90958cc724a55606a00928085d9deff242f0baf35a9823c00',
 False:'6e3fb128208d759cb84f3dfc112ab7c5e7bbce4b10cd613c9d0944c9c7d2d7d9'}
IR_PINS={'c':'9076986eac36a05c1952dac53360d737e914e4e3f00e208cad69eed6b45bfe3b',
 'cpp':'eebddfce055a2541b8d4baba575f698250c7be3d21c9794155305c59857e1762'}
BASE=0x18d78
ORIGINAL_PIN='678a3cbf42bc02d5c730973675858a18e538af9fdc1cb74dd9296f220f487ae3'
NAMES=['tsl9_irq_provider_18d78','tsl9_irq_provider_standard_18d8a','tsl9_irq_provider_common_18d92',
 'tsl9_irq_provider_bank0_18dfe','tsl9_irq_provider_extended_18e08','tsl9_irq_provider_bank1_18e12']
REGIONS=list(zip(NAMES,[0,18,26,134,144,154],[18,8,108,10,10,10]))
RELATIONS=[(16,44,NAMES[4]),(132,44,NAMES[5]),(152,45,NAMES[2])]
# Operands: arithmetic destination/source/immediate; memory data/base/offset;
# control source/absolute target. All widths are actual instruction widths.
EXPECTED=[[0,4,'SLLI',15,11,4],[4,2,'ADD',15,15,10],[6,4,'LW32',14,15,432],
 [10,2,'ANDI',14,14,4],[12,4,'SB8',14,12,8],[16,2,'BNEZ',14,BASE+144],
 [18,4,'LW32',14,15,432],[22,2,'SRLI',14,14,21],[24,2,'SW32',14,12,0],
 [26,4,'LW32',14,15,432],[30,2,'ANDI',14,14,2],[32,4,'SB8',14,12,9],
 [36,4,'LW32',14,15,436],[40,2,'ANDI',14,14,15],[42,4,'SB8',14,12,10],
 [46,4,'LW32',14,15,436],[50,2,'SRLI',14,14,8],[52,4,'SB8',14,12,19],
 [56,4,'LW32',14,15,440],[60,4,'SB8',14,12,11],[64,4,'LW32',14,15,440],
 [68,2,'SRLI',14,14,8],[70,4,'SB8',14,12,12],[74,4,'LW32',14,15,440],
 [78,2,'SRLI',14,14,16],[80,4,'SB8',14,12,13],[84,4,'LW32',14,15,440],
 [88,2,'SRLI',14,14,24],[90,4,'SB8',14,12,14],[94,4,'LW32',14,15,444],
 [98,4,'SB8',14,12,15],[102,4,'LW32',14,15,444],[106,2,'SRLI',14,14,8],
 [108,4,'SB8',14,12,16],[112,4,'LW32',14,15,444],[116,2,'SRLI',14,14,16],
 [118,4,'SB8',14,12,17],[122,4,'LW32',15,15,444],[126,2,'SRLI',15,15,24],
 [128,4,'SB8',15,12,18],[132,2,'BNEZ',11,BASE+154],[134,2,'LW32',15,10,12],
 [136,4,'ORI',15,15,32],[140,2,'SW32',15,10,12],[142,2,'RET',1],
 [144,4,'LW32',14,15,432],[148,2,'SRLI',14,14,3],[150,2,'SW32',14,12,4],
 [152,2,'J',BASE+26],[154,2,'LW32',15,10,16],[156,4,'ORI',15,15,32],
 [160,2,'SW32',15,10,16],[162,2,'RET',1]]
# Complete metadata and literal SSA instruction lists calibrated from pinned
# probe-v2 artifacts, then checked against the independently decoded BIN.
SCHEMAS = {'native': {'header': [1, 243, 1, 0, 0, 1096, 1, 52, 0, 0, 40, 17, 1], 'program_headers': [], 'sections': [{'name_offset': 0, 'type': 0, 'flags': 0, 'address': 0, 'offset': 0, 'size': 0, 'link': 0, 'info': 0, 'align': 0, 'entsize': 0, 'index': 0, 'name': ''}, {'name_offset': 118, 'type': 3, 'flags': 0, 'address': 0, 'offset': 726, 'size': 370, 'link': 0, 'info': 0, 'align': 1, 'entsize': 0, 'index': 1, 'name': '.strtab'}, {'name_offset': 1, 'type': 1, 'flags': 6, 'address': 0, 'offset': 52, 'size': 0, 'link': 0, 'info': 0, 'align': 2, 'entsize': 0, 'index': 2, 'name': '.text'}, {'name_offset': 178, 'type': 1, 'flags': 6, 'address': 0, 'offset': 52, 'size': 18, 'link': 0, 'info': 0, 'align': 2, 'entsize': 0, 'index': 3, 'name': '.text.tsl9_irq_provider_18d78'}, {'name_offset': 173, 'type': 4, 'flags': 64, 'address': 0, 'offset': 684, 'size': 12, 'link': 16, 'info': 3, 'align': 4, 'entsize': 12, 'index': 4, 'name': '.rela.text.tsl9_irq_provider_18d78'}, {'name_offset': 134, 'type': 1, 'flags': 6, 'address': 0, 'offset': 70, 'size': 8, 'link': 0, 'info': 0, 'align': 2, 'entsize': 0, 'index': 5, 'name': '.text.tsl9_irq_provider_standard_18d8a'}, {'name_offset': 282, 'type': 1, 'flags': 6, 'address': 0, 'offset': 78, 'size': 108, 'link': 0, 'info': 0, 'align': 2, 'entsize': 0, 'index': 6, 'name': '.text.tsl9_irq_provider_common_18d92'}, {'name_offset': 277, 'type': 4, 'flags': 64, 'address': 0, 'offset': 696, 'size': 12, 'link': 16, 'info': 6, 'align': 4, 'entsize': 12, 'index': 7, 'name': '.rela.text.tsl9_irq_provider_common_18d92'}, {'name_offset': 64, 'type': 1, 'flags': 6, 'address': 0, 'offset': 186, 'size': 10, 'link': 0, 'info': 0, 'align': 2, 'entsize': 0, 'index': 8, 'name': '.text.tsl9_irq_provider_bank0_18dfe'}, {'name_offset': 213, 'type': 1, 'flags': 6, 'address': 0, 'offset': 196, 'size': 10, 'link': 0, 'info': 0, 'align': 2, 'entsize': 0, 'index': 9, 'name': '.text.tsl9_irq_provider_extended_18e08'}, {'name_offset': 208, 'type': 4, 'flags': 64, 'address': 0, 'offset': 708, 'size': 12, 'link': 16, 'info': 9, 'align': 4, 'entsize': 12, 'index': 10, 'name': '.rela.text.tsl9_irq_provider_extended_18e08'}, {'name_offset': 319, 'type': 1, 'flags': 6, 'address': 0, 'offset': 206, 'size': 10, 'link': 0, 'info': 0, 'align': 2, 'entsize': 0, 'index': 11, 'name': '.text.tsl9_irq_provider_bank1_18e12'}, {'name_offset': 7, 'type': 1, 'flags': 48, 'address': 0, 'offset': 216, 'size': 159, 'link': 0, 'info': 0, 'align': 1, 'entsize': 1, 'index': 12, 'name': '.comment'}, {'name_offset': 34, 'type': 1, 'flags': 0, 'address': 0, 'offset': 375, 'size': 0, 'link': 0, 'info': 0, 'align': 1, 'entsize': 0, 'index': 13, 'name': '.note.GNU-stack'}, {'name_offset': 16, 'type': 1879048195, 'flags': 0, 'address': 0, 'offset': 375, 'size': 52, 'link': 0, 'info': 0, 'align': 1, 'entsize': 0, 'index': 14, 'name': '.riscv.attributes'}, {'name_offset': 50, 'type': 1879002115, 'flags': 2147483648, 'address': 0, 'offset': 720, 'size': 6, 'link': 16, 'info': 0, 'align': 1, 'entsize': 0, 'index': 15, 'name': '.llvm_addrsig'}, {'name_offset': 126, 'type': 2, 'flags': 0, 'address': 0, 'offset': 428, 'size': 256, 'link': 1, 'info': 10, 'align': 4, 'entsize': 16, 'index': 16, 'name': '.symtab'}], 'symbols': [{'index': 0, 'name': '', 'value': 0, 'size': 0, 'info': 0, 'other': 0, 'section': 0}, {'index': 1, 'name': 'irq_provider.v2.c', 'value': 0, 'size': 0, 'info': 4, 'other': 0, 'section': 65521}, {'index': 2, 'name': '$x.0', 'value': 0, 'size': 0, 'info': 0, 'other': 0, 'section': 3}, {'index': 3, 'name': '$x.1', 'value': 0, 'size': 0, 'info': 0, 'other': 0, 'section': 5}, {'index': 4, 'name': '$x.2', 'value': 0, 'size': 0, 'info': 0, 'other': 0, 'section': 6}, {'index': 5, 'name': '$x.3', 'value': 0, 'size': 0, 'info': 0, 'other': 0, 'section': 8}, {'index': 6, 'name': '$x.4', 'value': 0, 'size': 0, 'info': 0, 'other': 0, 'section': 9}, {'index': 7, 'name': '$x.5', 'value': 0, 'size': 0, 'info': 0, 'other': 0, 'section': 11}, {'index': 8, 'name': '$d.6', 'value': 0, 'size': 0, 'info': 0, 'other': 0, 'section': 12}, {'index': 9, 'name': '$d.7', 'value': 0, 'size': 0, 'info': 0, 'other': 0, 'section': 14}, {'index': 10, 'name': 'tsl9_irq_provider_18d78', 'value': 0, 'size': 18, 'info': 18, 'other': 0, 'section': 3}, {'index': 11, 'name': 'tsl9_irq_provider_extended_18e08', 'value': 0, 'size': 10, 'info': 18, 'other': 0, 'section': 9}, {'index': 12, 'name': 'tsl9_irq_provider_standard_18d8a', 'value': 0, 'size': 8, 'info': 18, 'other': 0, 'section': 5}, {'index': 13, 'name': 'tsl9_irq_provider_common_18d92', 'value': 0, 'size': 108, 'info': 18, 'other': 0, 'section': 6}, {'index': 14, 'name': 'tsl9_irq_provider_bank1_18e12', 'value': 0, 'size': 10, 'info': 18, 'other': 0, 'section': 11}, {'index': 15, 'name': 'tsl9_irq_provider_bank0_18dfe', 'value': 0, 'size': 10, 'info': 18, 'other': 0, 'section': 8}], 'relocations': [{'section': 3, 'offset': 16, 'type': 44, 'symbol': 11, 'addend': 0}, {'section': 6, 'offset': 106, 'type': 44, 'symbol': 14, 'addend': 0}, {'section': 9, 'offset': 8, 'type': 45, 'symbol': 13, 'addend': 0}], 'noncode_section_hashes': {'': 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855', '.strtab': 'e5b07ec6e4a160311825d2440eeda97b1477eac377ff1f93ccff5232bdf22b1a', '.rela.text.tsl9_irq_provider_18d78': 'a444dc580e2527f5e798d762cd1b548a6c336f595b1e0566a9b40e7fef367224', '.rela.text.tsl9_irq_provider_common_18d92': 'b7d554ab4122593d265fb675657e25767dbe9166616ad47c2e2e39a1fd934a21', '.rela.text.tsl9_irq_provider_extended_18e08': '7f04812082f370e54e7bd2a7ee98c11d8205ce3d1b84f5004750a4bb7dda840a', '.comment': '72c64fbc17a5d9f46f33ac0650b7d4f549d87c2ba9e77ebd765a25a3960e3017', '.note.GNU-stack': 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855', '.riscv.attributes': 'f2bd85b0ab58609a20dbdef6cc6e3f2dd1a34cdcb554580710aa3819cd24ad71', '.llvm_addrsig': '2b1f56447e37f9c508f22ba89caeaada3f7a2dc813df431ccbb380a4d143a2f1', '.symtab': 'e2f4da32a9e9db1a08a1eb1d21f7db1aaec7e514144e45a38f929c86cc367252'}, 'outside_allocated_code_sha256': '0c09c5c915f849ed020948c9756770a7bc2cb857199887d773655a03665ffb6c'}, 'linked': {'header': [2, 243, 1, 101752, 52, 4132, 1, 52, 32, 4, 40, 6, 4], 'program_headers': [[6, 52, 98356, 98356, 128, 128, 4, 4], [1, 0, 98304, 98304, 180, 180, 4, 4096], [1, 3448, 101752, 101752, 164, 164, 5, 4096], [1685382481, 0, 0, 0, 0, 0, 6, 0]], 'sections': [{'name_offset': 0, 'type': 0, 'flags': 0, 'address': 0, 'offset': 0, 'size': 0, 'link': 0, 'info': 0, 'align': 0, 'entsize': 0, 'index': 0, 'name': ''}, {'name_offset': 1, 'type': 1, 'flags': 6, 'address': 101752, 'offset': 3448, 'size': 164, 'link': 0, 'info': 0, 'align': 2, 'entsize': 0, 'index': 1, 'name': '.provider'}, {'name_offset': 11, 'type': 1, 'flags': 6, 'address': 101916, 'offset': 3612, 'size': 0, 'link': 0, 'info': 0, 'align': 2, 'entsize': 0, 'index': 2, 'name': '.text'}, {'name_offset': 17, 'type': 2, 'flags': 0, 'address': 0, 'offset': 3612, 'size': 240, 'link': 5, 'info': 9, 'align': 4, 'entsize': 16, 'index': 3, 'name': '.symtab'}, {'name_offset': 25, 'type': 3, 'flags': 0, 'address': 0, 'offset': 3852, 'size': 43, 'link': 0, 'info': 0, 'align': 1, 'entsize': 0, 'index': 4, 'name': '.shstrtab'}, {'name_offset': 35, 'type': 3, 'flags': 0, 'address': 0, 'offset': 3895, 'size': 235, 'link': 0, 'info': 0, 'align': 1, 'entsize': 0, 'index': 5, 'name': '.strtab'}], 'symbols': [{'index': 0, 'name': '', 'value': 0, 'size': 0, 'info': 0, 'other': 0, 'section': 0}, {'index': 1, 'name': 'irq_provider.v2.c', 'value': 0, 'size': 0, 'info': 4, 'other': 0, 'section': 65521}, {'index': 2, 'name': '$x.0', 'value': 101752, 'size': 0, 'info': 0, 'other': 0, 'section': 1}, {'index': 3, 'name': '$x.1', 'value': 101770, 'size': 0, 'info': 0, 'other': 0, 'section': 1}, {'index': 4, 'name': '$x.2', 'value': 101778, 'size': 0, 'info': 0, 'other': 0, 'section': 1}, {'index': 5, 'name': '$x.3', 'value': 101886, 'size': 0, 'info': 0, 'other': 0, 'section': 1}, {'index': 6, 'name': '$x.4', 'value': 101896, 'size': 0, 'info': 0, 'other': 0, 'section': 1}, {'index': 7, 'name': '$x.5', 'value': 101906, 'size': 0, 'info': 0, 'other': 0, 'section': 1}, {'index': 8, 'name': '$d.7', 'value': 0, 'size': 0, 'info': 0, 'other': 0, 'section': 65521}, {'index': 9, 'name': 'tsl9_irq_provider_18d78', 'value': 101752, 'size': 18, 'info': 18, 'other': 0, 'section': 1}, {'index': 10, 'name': 'tsl9_irq_provider_extended_18e08', 'value': 101896, 'size': 10, 'info': 18, 'other': 0, 'section': 1}, {'index': 11, 'name': 'tsl9_irq_provider_standard_18d8a', 'value': 101770, 'size': 8, 'info': 18, 'other': 0, 'section': 1}, {'index': 12, 'name': 'tsl9_irq_provider_common_18d92', 'value': 101778, 'size': 108, 'info': 18, 'other': 0, 'section': 1}, {'index': 13, 'name': 'tsl9_irq_provider_bank1_18e12', 'value': 101906, 'size': 10, 'info': 18, 'other': 0, 'section': 1}, {'index': 14, 'name': 'tsl9_irq_provider_bank0_18dfe', 'value': 101886, 'size': 10, 'info': 18, 'other': 0, 'section': 1}], 'relocations': [], 'noncode_section_hashes': {'': 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855', '.symtab': '7c562df3dd8dd8d8d6c4061551e7720a0af256d281f936b107b42ba442404565', '.shstrtab': '7f0b8e09551ae4d56979b359fdabb5bbf6fb257f2f68250024cabf940249d988', '.strtab': '091502b5f0f0260cf6ee478e60fd732d05ac3dbe83661d69364d47b9bdb6cb8a'}, 'outside_allocated_code_sha256': '8c99e4f4868aa517d3af2b0540b353aee8ce02b67bf3d610272b5b8eefea2614'}}
IR_CORE = {'tsl9_irq_provider_18d78': ['%1 = tail call { i32, i32, i32 } asm sideeffect "", "={x10},={x11},={x12},~{memory}"() #1', '%2 = extractvalue { i32, i32, i32 } %1, 0', '%3 = extractvalue { i32, i32, i32 } %1, 1', '%4 = extractvalue { i32, i32, i32 } %1, 2', '%5 = shl i32 %3, 4', '%6 = tail call i32 asm sideeffect "", "={x15},{x10},{x11},{x12},{x15},~{memory}"(i32 %2, i32 %3, i32 %4, i32 %5) #1', '%7 = add i32 %6, %2', '%8 = tail call i32 asm sideeffect "", "={x15},{x10},{x11},{x12},{x15},~{memory}"(i32 %2, i32 %3, i32 %4, i32 %7) #1', '%9 = add i32 %8, 432', '%10 = inttoptr i32 %9 to ptr', '%11 = load volatile i32, ptr %10, align 4', '%12 = and i32 %11, 4', '%13 = trunc i32 %12 to i8', '%14 = add i32 %4, 8', '%15 = inttoptr i32 %14 to ptr', 'store volatile i8 %13, ptr %15, align 1', 'tail call void asm sideeffect ".Lprovider_extended:\\0Ac.bnez a4, .Lprovider_extended\\0A.reloc .Lprovider_extended, R_RISCV_RVC_BRANCH, tsl9_irq_provider_extended_18e08\\0A", "{x14},{x15},{x10},{x11},{x12},~{memory}"(i32 %12, i32 %8, i32 %2, i32 %3, i32 %4) #1', 'unreachable'], 'tsl9_irq_provider_standard_18d8a': ['%1 = tail call { i32, i32 } asm sideeffect "", "={x15},={x12},~{memory}"() #1', '%2 = extractvalue { i32, i32 } %1, 0', '%3 = extractvalue { i32, i32 } %1, 1', '%4 = add i32 %2, 432', '%5 = inttoptr i32 %4 to ptr', '%6 = load volatile i32, ptr %5, align 4', '%7 = lshr i32 %6, 21', '%8 = inttoptr i32 %3 to ptr', 'store volatile i32 %7, ptr %8, align 4', 'tail call void asm sideeffect "", "{x15},{x12},{x14},~{memory}"(i32 %2, i32 %3, i32 %7) #1', 'unreachable'], 'tsl9_irq_provider_common_18d92': ['%1 = tail call { i32, i32, i32, i32 } asm sideeffect "", "={x10},={x11},={x12},={x15},~{memory}"() #1', '%2 = extractvalue { i32, i32, i32, i32 } %1, 0', '%3 = extractvalue { i32, i32, i32, i32 } %1, 1', '%4 = extractvalue { i32, i32, i32, i32 } %1, 2', '%5 = extractvalue { i32, i32, i32, i32 } %1, 3', '%6 = add i32 %5, 432', '%7 = inttoptr i32 %6 to ptr', '%8 = load volatile i32, ptr %7, align 4', '%9 = trunc i32 %8 to i8', '%10 = and i8 %9, 2', '%11 = add i32 %4, 9', '%12 = inttoptr i32 %11 to ptr', 'store volatile i8 %10, ptr %12, align 1', '%13 = add i32 %5, 436', '%14 = inttoptr i32 %13 to ptr', '%15 = load volatile i32, ptr %14, align 4', '%16 = trunc i32 %15 to i8', '%17 = and i8 %16, 15', '%18 = add i32 %4, 10', '%19 = inttoptr i32 %18 to ptr', 'store volatile i8 %17, ptr %19, align 1', '%20 = load volatile i32, ptr %14, align 4', '%21 = lshr i32 %20, 8', '%22 = trunc i32 %21 to i8', '%23 = add i32 %4, 19', '%24 = inttoptr i32 %23 to ptr', 'store volatile i8 %22, ptr %24, align 1', '%25 = add i32 %5, 440', '%26 = inttoptr i32 %25 to ptr', '%27 = load volatile i32, ptr %26, align 4', '%28 = trunc i32 %27 to i8', '%29 = add i32 %4, 11', '%30 = inttoptr i32 %29 to ptr', 'store volatile i8 %28, ptr %30, align 1', '%31 = load volatile i32, ptr %26, align 4', '%32 = lshr i32 %31, 8', '%33 = trunc i32 %32 to i8', '%34 = add i32 %4, 12', '%35 = inttoptr i32 %34 to ptr', 'store volatile i8 %33, ptr %35, align 1', '%36 = load volatile i32, ptr %26, align 4', '%37 = lshr i32 %36, 16', '%38 = trunc i32 %37 to i8', '%39 = add i32 %4, 13', '%40 = inttoptr i32 %39 to ptr', 'store volatile i8 %38, ptr %40, align 1', '%41 = load volatile i32, ptr %26, align 4', '%42 = lshr i32 %41, 24', '%43 = trunc i32 %42 to i8', '%44 = add i32 %4, 14', '%45 = inttoptr i32 %44 to ptr', 'store volatile i8 %43, ptr %45, align 1', '%46 = add i32 %5, 444', '%47 = inttoptr i32 %46 to ptr', '%48 = load volatile i32, ptr %47, align 4', '%49 = trunc i32 %48 to i8', '%50 = add i32 %4, 15', '%51 = inttoptr i32 %50 to ptr', 'store volatile i8 %49, ptr %51, align 1', '%52 = load volatile i32, ptr %47, align 4', '%53 = lshr i32 %52, 8', '%54 = trunc i32 %53 to i8', '%55 = add i32 %4, 16', '%56 = inttoptr i32 %55 to ptr', 'store volatile i8 %54, ptr %56, align 1', '%57 = load volatile i32, ptr %47, align 4', '%58 = lshr i32 %57, 16', '%59 = trunc i32 %58 to i8', '%60 = add i32 %4, 17', '%61 = inttoptr i32 %60 to ptr', 'store volatile i8 %59, ptr %61, align 1', '%62 = tail call { i32, i32 } asm sideeffect "", "={x14},={x15},{x10},{x11},{x12},{x14},{x15},~{memory}"(i32 %2, i32 %3, i32 %4, i32 %58, i32 %5) #1', '%63 = extractvalue { i32, i32 } %62, 0', '%64 = extractvalue { i32, i32 } %62, 1', '%65 = add i32 %64, 444', '%66 = inttoptr i32 %65 to ptr', '%67 = load volatile i32, ptr %66, align 4', '%68 = lshr i32 %67, 24', '%69 = trunc i32 %68 to i8', '%70 = add i32 %4, 18', '%71 = inttoptr i32 %70 to ptr', 'store volatile i8 %69, ptr %71, align 1', 'tail call void asm sideeffect ".Lprovider_bank1:\\0Ac.bnez a1, .Lprovider_bank1\\0A.reloc .Lprovider_bank1, R_RISCV_RVC_BRANCH, tsl9_irq_provider_bank1_18e12\\0A", "{x10},{x11},{x12},{x14},{x15},~{memory}"(i32 %2, i32 %3, i32 %4, i32 %63, i32 %68) #1', 'unreachable'], 'tsl9_irq_provider_bank0_18dfe': ['%1 = tail call i32 asm sideeffect "", "={x10},~{memory}"() #1', '%2 = add i32 %1, 12', '%3 = inttoptr i32 %2 to ptr', '%4 = load volatile i32, ptr %3, align 4', '%5 = tail call i32 asm sideeffect "", "={x15},{x10},{x15},~{memory}"(i32 %1, i32 %4) #1', '%6 = or i32 %5, 32', 'store volatile i32 %6, ptr %3, align 4', 'tail call void asm sideeffect "ret\\0A", "{x10},{x15},~{memory}"(i32 %1, i32 %6) #1', 'unreachable'], 'tsl9_irq_provider_extended_18e08': ['%1 = tail call { i32, i32 } asm sideeffect "", "={x15},={x12},~{memory}"() #1', '%2 = extractvalue { i32, i32 } %1, 0', '%3 = extractvalue { i32, i32 } %1, 1', '%4 = add i32 %2, 432', '%5 = inttoptr i32 %4 to ptr', '%6 = load volatile i32, ptr %5, align 4', '%7 = lshr i32 %6, 3', '%8 = add i32 %3, 4', '%9 = inttoptr i32 %8 to ptr', 'store volatile i32 %7, ptr %9, align 4', 'tail call void asm sideeffect ".Lprovider_common:\\0Ac.j .Lprovider_common\\0A.reloc .Lprovider_common, R_RISCV_RVC_JUMP, tsl9_irq_provider_common_18d92\\0A", "{x15},{x12},{x14},~{memory}"(i32 %2, i32 %3, i32 %7) #1', 'unreachable'], 'tsl9_irq_provider_bank1_18e12': ['%1 = tail call i32 asm sideeffect "", "={x10},~{memory}"() #1', '%2 = add i32 %1, 16', '%3 = inttoptr i32 %2 to ptr', '%4 = load volatile i32, ptr %3, align 4', '%5 = tail call i32 asm sideeffect "", "={x15},{x10},{x15},~{memory}"(i32 %1, i32 %4) #1', '%6 = or i32 %5, 32', 'store volatile i32 %6, ptr %3, align 4', 'tail call void asm sideeffect "ret\\0A", "{x10},{x15},~{memory}"(i32 %1, i32 %6) #1', 'unreachable']}


def need(ok,message):
    if not ok:raise ValueError(message)
def sha(data):return hashlib.sha256(data).hexdigest()
def digest(path):return sha(Path(path).read_bytes())
def sx(n,b):return n-(1<<b) if n&(1<<(b-1)) else n


need(digest(READER)==PINS[READER],'frozen ELF reader')
_reader=runpy.run_path(str(READER));ELF,portable=_reader['ELF'],_reader['portable']


def decode(code):
    """Finite static RV32 decoder only; no evaluation or device accesses."""
    rows=[];at=0
    while at<len(code):
        need(at+2<=len(code),'instruction extent');w=int.from_bytes(code[at:at+2],'little');size=4 if w&3==3 else 2
        need(at+size<=len(code),'wide instruction extent')
        if size==4:
            w=int.from_bytes(code[at:at+4],'little');op=w&127;rd=(w>>7)&31;rs=(w>>15)&31;f3=(w>>12)&7
            if op==0x13 and f3==1 and w>>25==0:ins=['SLLI',rd,rs,(w>>20)&31]
            elif op==0x13 and f3==6:ins=['ORI',rd,rs,sx(w>>20,12)]
            elif op==3 and f3==2:ins=['LW32',rd,rs,sx(w>>20,12)]
            elif op==0x23 and f3==0:
                offset=((w>>25)<<5)|((w>>7)&31);ins=['SB8',(w>>20)&31,rs,sx(offset,12)]
            else:raise ValueError('forbidden wide opcode/width: no calls, SP/RA stores, CSR or opcode carriers')
        else:
            q=w&3;f3=w>>13;rd=(w>>7)&31;rs2=(w>>2)&31
            if q==0 and f3 in (2,6):
                offset=(((w>>10)&7)<<3)|(((w>>6)&1)<<2)|(((w>>5)&1)<<6)
                ins=['LW32' if f3==2 else 'SW32',8+((w>>2)&7),8+((w>>7)&7),offset]
            elif q==1 and f3==4 and ((w>>10)&3) in (0,2):
                rs=8+((w>>7)&7);imm=(((w>>12)&1)<<5)|((w>>2)&31)
                ins=['SRLI',rs,rs,imm] if ((w>>10)&3)==0 else ['ANDI',rs,rs,sx(imm,6)]
            elif q==2 and f3==4 and (w>>12)&1 and rd and rs2:ins=['ADD',rd,rd,rs2]
            elif w==0x8082:ins=['RET',1]
            elif q==1 and f3==7:
                n=(((w>>12)&1)<<8)|(((w>>10)&3)<<3)|(((w>>5)&3)<<6)|(((w>>3)&3)<<1)|(((w>>2)&1)<<5)
                ins=['BNEZ',8+((w>>7)&7),BASE+at+sx(n,9)]
            elif q==1 and f3==5:
                n=(((w>>12)&1)<<11)|(((w>>11)&1)<<4)|(((w>>9)&3)<<8)|(((w>>8)&1)<<10)|(((w>>7)&1)<<6)|(((w>>6)&1)<<7)|(((w>>3)&7)<<1)|(((w>>2)&1)<<5)
                ins=['J',BASE+at+sx(n,12)]
            else:raise ValueError('forbidden compressed opcode/width')
        rows.append([at,size]+ins);at+=size
    return rows


def typed_contract(rows,pending):
    expected=copy.deepcopy(EXPECTED)
    if pending:
        for row in expected:
            if row[0] in (16,132,152):row[-1]=BASE+row[0]
    need(rows==expected,'all53 typed operands/widths/order and all control targets')
    writes=[r for r in rows if r[2] in ('SLLI','ADD','LW32','ANDI','SRLI','ORI')]
    need(all(r[3] in (14,15) for r in writes),'only physical A4/A5 written; A0/A1/A2 and all other GPR preserved')
    loads=[r[3:] for r in rows if r[2]=='LW32'];stores=[r[2:] for r in rows if r[2] in ('SB8','SW32')]
    need(loads==[[14,15,432]]*3+[[14,15,436]]*2+[[14,15,440]]*4+[[14,15,444]]*3+
         [[15,15,444],[15,10,12],[14,15,432],[15,10,16]],'all16 fresh word loads, physical order and final self-overwrite')
    need(len(stores)==16 and sum(r[0]=='SB8' for r in stores)==12 and sum(r[0]=='SW32' for r in stores)==4,
         'all12 byte stores and four word stores, no narrowed word output')
    need([r[0] for r in rows if r[2]=='RET']==[142,162],'two RA returns, no call/SP/RA/CSR writes')
    return rows


def original():
    raw=FIRMWARE.read_bytes();need(len(raw)==76800 and sha(raw)==PINS[FIRMWARE],'whole original BIN identity')
    code=raw[BASE-0x8000:BASE-0x8000+164];typed_contract(decode(code),False)
    need(sha(code)==ORIGINAL_PIN,'whole original164B');return code


def projection(code):return bytes(v for i,v in enumerate(code) if i not in {16,17,132,133,152,153})


def metadata(e,native):
    ranges=[(s['offset'],s['offset']+s['size']) for s in e.sections if s['flags']&2 and s['size']]
    outside=bytes(v for i,v in enumerate(e.raw) if not any(a<=i<b for a,b in ranges))
    return dict(header=e.header,program_headers=e.program_headers,sections=e.sections,symbols=e.symbols,
                relocations=e.relocations,noncode_section_hashes={s['name']:sha(e.data(s)) for s in e.sections
                if not s['flags']&2 and s['type']!=8},outside_allocated_code_sha256=sha(outside))


def elf_contract(e,native,official,full=True):
    expected_metadata=SCHEMAS['native' if native else 'linked']
    need(len(e.raw)==expected_metadata['header'][5]+40*expected_metadata['header'][11],
         'complete ELF extent, no unbound trailing bytes')
    need(e.header[0]==(1 if native else 2) and e.header[6]==1 and (not native or not e.program_headers),
         'RV32 RVC native ET_REL versus nominal ET_EXEC')
    globals_=[s for s in e.symbols if s['info']>>4]
    expected={n:(0 if native else BASE+at,z,18,0,('.text.'+n if native else '.provider')) for n,at,z in REGIONS}
    actual={s['name']:(s['value'],s['size'],s['info'],s['other'],e.sections[s['section']]['name'])
            for s in globals_ if s['section'] not in (0,65521)}
    need(actual==expected and len(globals_)==6,'six genuine FUNCs with exact region ownership/extent')
    need(not any(s['section'] in (0,65521) for s in globals_),'no UND/ABS/fake/weak providers')
    alloc=[s for s in e.sections if s['flags']&2 and s['size']]
    need([(s['name'],s['address'],s['size'],s['flags'],s['type'],s['align']) for s in alloc]==
         ([('.text.'+n,0,z,6,1,2) for n,_,z in REGIONS] if native else [('.provider',BASE,164,6,1,2)]),'exact AX-only allocation')
    code=b''.join(e.data('.text.'+n) for n in NAMES) if native else e.data('.provider')
    rows=typed_contract(decode(code),native);need(len(code)==164 and len(rows)==53,'164B53i')
    rel=[];starts={'.text.'+n:at for n,at,_ in REGIONS}
    for r in e.relocations:
        owner=e.sections[r['section']]['name'];symbol=e.symbols[r['symbol']]
        need(native and owner in starts,'genuine native relocation owner; nominal has no RELA')
        rel.append((r['offset']+starts[owner],r['type'],symbol['name'],r['addend']))
        need(symbol['info']==18 and symbol['section'] not in (0,65521),'actual defined FUNC relocation target')
    need(rel==([(at,kind,name,0) for at,kind,name in RELATIONS] if native else []),'three native edges fully resolved in nominal')
    if native:
        need(code[16:18]==bytes.fromhex('01e3') and code[132:134]==bytes.fromhex('81e1') and code[152:154]==bytes.fromhex('01a0'),
             'native RVC immediates remain self-target placeholders')
    else:need(code==official,'whole nominal164B equals official, all three genuine local edges resolved')
    need(len(projection(code))==158 and projection(code)==projection(official),'all158 original noncontrol bytes')
    need(metadata(e,native)==expected_metadata,'complete actual ELF metadata/non-code/gap bytes exact')
    if full:need(sha(e.raw)==ELF_PINS[native],'whole measured ELF pin')
    return dict(sha256=sha(e.raw),header=e.header,program_headers=e.program_headers,sections=e.sections,
       symbols=e.symbols,relocations=e.relocations,code_hex=code.hex(),code_sha256=sha(code),typed_rows=rows,
       UND_providers=[],ABS_providers=[],local_ABS_metadata=sum(s['section']==65521 and s['info']>>4==0 for s in e.symbols),
       pending_machine_immediates=3 if native else 0,noncontrol_bytes=158,noncontrol_sha256=sha(projection(code)),
       whole_original_equal=not native,firmware_ready=False)


def core_ir(text):
    blocks={}
    for name,body in re.findall(r'^define .*?@([^ (]+)\([^\n]*\{\n(.*?)^\}',text,re.M|re.S):
        blocks[name]=[re.sub(r', !(?:tbaa|srcloc) !\d+','',line.strip()) for line in body.splitlines() if line.strip()]
    return blocks


def ir_contract(text,language,full=True):
    normalized='\n'.join(text.splitlines()[2:])+'\n';core=core_ir(normalized)
    need(list(core)==NAMES,'six genuine IR definitions in physical region order')
    need(core==IR_CORE,'complete literal SSA/volatile/address/shift/store/physical-register port sequence')
    need(len(re.findall(r'load volatile i32',normalized))==16 and not re.search(r'load volatile i(?:8|16|64)|\balloca\b|\b(?:undef|poison)\b',normalized),
         '16 fresh true volatile word reads; no cached/narrowed reads or compiler frame')
    need(len(re.findall(r'store volatile i8 ',normalized))==12 and len(re.findall(r'store volatile i32 ',normalized))==4,
         '12 C byte stores and four word stores')
    need(normalized.count('ret\\0A')==2 and not re.search(r'jal|mret|csrr|csrw|\bsp\b|\.4byte|\.word|\.insn',normalized),
         'two physical RET ports; no call/SP/CSR/opcode carriers')
    need(normalized.count('R_RISCV_RVC_BRANCH')==2 and normalized.count('R_RISCV_RVC_JUMP')==1,'three symbolic architectural region edges')
    if full:need(sha(normalized.encode())==IR_PINS[language],'complete normalized IR including attributes/TBAA/SSA')
    return dict(normalized_sha256=sha(normalized.encode()),C_volatile_word_reads=16,C_byte_stores=12,C_word_stores=4,
       core_SSA=core,physical_scratch_registers=['A4','A5'],input_registers=['A0','A1','A2'],functions=NAMES)


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
    need(deps==want,'MD exact complete source/header closure');return portable(want,ROOT,llvm)


def recipes(llvm,out,language):
    probe=runpy.run_path(str(HERE/'probe.py'));f=probe['flags'](language)
    need({int(s[9:]) for s in f if s.startswith('-ffixed-x')}==set(range(1,32))-{10,11,12,14,15} and
         '-march=rv32imac_zicsr' in f and '-Oz' in f,'frozen compiler profile, reserved RA/SP/all noninput-nonscratch bank')
    exe=lambda n:str(llvm/n);obj=str(out/'native.o');dump=['--mattr=+m,+a,+c,+zicsr','-d','-r','-t','-h']
    return [('compile',[exe('clang.exe'),*f,'-MD','-MF',str(out/'native.d'),'-MT',obj,'-c',str(SOURCE),'-o',obj]),
      ('IR',[exe('clang.exe'),*f,'-S','-emit-llvm',str(SOURCE),'-o',str(out/'native.ll')]),
      ('object',[exe('llvm-objdump.exe'),*dump,obj]),
      ('link',[exe('ld.lld.exe'),'--no-relax','-T',str(HERE/'component.ld'),obj,'-o',str(out/'linked.elf')]),
      ('linked',[exe('llvm-objdump.exe'),*dump,str(out/'linked.elf')])]


def negatives(native,linked,text,language,official,md,llvm,out):
    results=[]
    def check(name,scope,fn,full=False):
        try:fn()
        except (ValueError,IndexError,KeyError) as exc:results.append(dict(name=name,scope=scope,rejected=True,whole_ELF_hash_enabled=False,whole_IR_hash_enabled=full,reason=str(exc)))
        else:raise ValueError('negative accepted '+name)
    def raw(name,e,n,position,fmt,value):
        b=bytearray(e.raw);struct.pack_into(fmt,b,position,value)
        check(name,'raw_ELF_reparsed',lambda:elf_contract(ELF(b),n,official,False))
    for e,n in [(native,True),(linked,False)]:
        tag='native' if n else 'linked';symtab=next(s for s in e.sections if s['type']==2)
        globals_={s['name']:s for s in e.symbols if s['info']>>4}
        for name in [NAMES[0],NAMES[2],NAMES[4]]:
            at=symtab['offset']+globals_[name]['index']*16
            raw(tag+'_fakeABS_'+name,e,n,at+14,'<H',65521)
            raw(tag+'_UND_'+name,e,n,at+14,'<H',0)
            raw(tag+'_weak_'+name,e,n,at+12,'<B',34)
        at=symtab['offset']+globals_[NAMES[2]]['index']*16
        raw(tag+'_FUNC_size',e,n,at+8,'<I',106);raw(tag+'_FUNC_value',e,n,at+4,'<I',2)
        sec=next(s for s in e.sections if s['flags']&2 and s['size'])
        raw(tag+'_writable_code',e,n,e.header[5]+40*sec['index']+8,'<I',7)
        check(tag+'_trailing_bytes','raw_ELF_reparsed',lambda ee=e,nn=n:elf_contract(ELF(ee.raw+b'\0\0'),nn,official,False))
        def offset(pc):
            region=next((name,a,z) for name,a,z in REGIONS if a<=pc<a+z)
            return e.section('.text.'+region[0])['offset']+pc-region[1] if n else e.section('.provider')['offset']+pc
        # Actual raw operand/width/order faults, not metadata-only proxies.
        for name,pc,delta,xor in [('selector_shift',0,2,16),('bank_base',4,0,4),('first_LW_halfwidth',6,1,48),
             ('mask4',10,0,4),('format_output_offset',12,0,128),('extended_branch_A5',16,0,128),
             ('standard_shift',22,0,4),('standard_word_store',24,1,128),('common_mask2',30,0,4),
             ('low_nibble_mask15',40,0,4),('second436_address',46,2,64),('payload19_offset',52,0,128),
             ('440_read_address',56,2,64),('payload12_offset',70,0,128),('word16_shift',78,0,4),
             ('word24_shift',88,0,4),('444_read_address',94,2,64),('final_A5_overwrite',122,0,128),
             ('final_A5_shift',126,0,4),('final_byte_source',128,2,16),('selector_branch_A0',132,0,128),
             ('bank0_fresh_LW',134,0,4),('bank0_OR32',136,2,16),('bank0_word_store',140,1,128),
             ('bank0_RET',142,0,4),('extended_shift3',148,0,4),('extended_word_store',150,1,128),
             ('bank1_fresh_LW',154,0,4),('bank1_OR32',156,2,16),('bank1_RET',162,0,4)]:
            at=offset(pc)+delta;raw(tag+'_'+name,e,n,at,'<B',e.raw[at]^xor)
        b=bytearray(e.raw);a=offset(36);z=offset(42);b[a:a+4],b[z:z+4]=b[z:z+4],b[a:a+4]
        check(tag+'_fresh_read_store_order','raw_ELF_reparsed',lambda bb=b,nn=n:elf_contract(ELF(bb),nn,official,False))
        # Delete an actual fresh read from the decoded stream without relying
        # on the ELF or full-code hashes. This is a parsed-model control.
        rows=decode(b''.join(e.data('.text.'+name) for name in NAMES) if n else e.data('.provider'))
        changed=copy.deepcopy(rows);del changed[15]
        check(tag+'_missing_fresh436_read','parsed_typed_rows',lambda c=changed,nn=n:typed_contract(c,nn))
    for i,r in enumerate(native.relocations):
        table=next(s for s in native.sections if s['type']==4 and s['info']==r['section']);at=table['offset']
        raw('native_RELA_addend_'+str(i),native,True,at+8,'<i',2)
        raw('native_RELA_family_'+str(i),native,True,at+4,'<I',(r['symbol']<<8)|(45 if i<2 else 44))
        wrong=next(s['index'] for s in native.symbols if s['name']==NAMES[0])
        raw('native_RELA_target_'+str(i),native,True,at+4,'<I',(wrong<<8)|r['type'])
    rows=copy.deepcopy(EXPECTED)
    for name,index,field,value in [('parsed_LW16',2,2,'LHU16'),('parsed_byte_to_word',4,2,'SW32'),
          ('parsed_output19',17,5,18),('parsed_final_bank_A4',37,3,14),('parsed_call_instead_RET',44,2,'JAL')]:
        changed=copy.deepcopy(rows);changed[index][field]=value
        check(name,'parsed_typed_rows',lambda c=changed:typed_contract(c,False))
    mutations=[('IR_read_width','load volatile i32','load volatile i16'),('IR_store_width','store volatile i32','store volatile i8'),
      ('IR_cached_read','%20 = load volatile i32','%20 = load i32'),('IR_selector_shift','%5 = shl i32 %3, 4','%5 = shl i32 %3, 3'),
      ('IR_bank_address','%9 = add i32 %8, 432','%9 = add i32 %8, 436'),('IR_mask4','%12 = and i32 %11, 4','%12 = and i32 %11, 2'),
      ('IR_standard_shift','%7 = lshr i32 %6, 21','%7 = lshr i32 %6, 20'),('IR_output19','%23 = add i32 %4, 19','%23 = add i32 %4, 18'),
      ('IR_read440','%25 = add i32 %5, 440','%25 = add i32 %5, 444'),('IR_read444','%46 = add i32 %5, 444','%46 = add i32 %5, 440'),
      ('IR_final_bank','%65 = add i32 %64, 444','%65 = add i32 %5, 444'),('IR_residue','i32 %63, i32 %68','i32 %58, i32 %68'),
      ('IR_bank_read_port','={x15},{x10},{x15}','={x14},{x10},{x14}'),('IR_bank_OR','%6 = or i32 %5, 32','%6 = or i32 %5, 16'),
      ('IR_cold_edge','c.bnez a4, .Lprovider_extended','c.bnez a5, .Lprovider_extended'),('IR_RET','ret\\0A','mret\\0A')]
    for name,old,new in mutations:
        need(old in text,'real IR negative fixture '+name);changed=text.replace(old,new,1)
        check(name,'IR_text_structural_SSA',lambda c=changed:ir_contract(c,language,False))
    for name,old,new in [('IR_full_attributes','generic-rv32','other-rv32'),('IR_full_metadata','!"int"','!"other"')]:
        need(old in text,'real full IR fixture');changed=text.replace(old,new,1)
        check(name,'IR_text_full_normalized_pin',lambda c=changed:ir_contract(c,language,True),True)
    for name,changed in [('MD_wrong_target',md.replace('native.o:', 'other.o:',1)),('MD_missing_header',' '.join(md.splitlines()[:-1])),
                         ('MD_extra_dependency',md+'\nextra.h\n')]:
        check(name,'MD_text',lambda c=changed:md_contract(c,llvm,out))
    return results


def evaluate(root,llvm,out,language):
    need(root.resolve()==ROOT,'canonical project root');before=inputs(llvm);official=original()
    native=ELF(out/'native.o');linked=ELF(out/'linked.elf')
    nf=elf_contract(native,True,official);lf=elf_contract(linked,False,official)
    text=(out/'native.ll').read_text(encoding='utf-8');ir=ir_contract(text,language)
    md=(out/'native.d').read_text(encoding='utf-8');deps=md_contract(md,llvm,out)
    commands=[dict(label=n,argv=portable(a,ROOT,llvm),returncode=0) for n,a in recipes(llvm,out,language)]
    need(json.loads((out/'recipes.json').read_bytes())==commands,'complete exact successful producer recipes')
    files=sorted(['native.o','linked.elf','native.ll','native.d','recipes.json']+[n+'.log' for n,_ in recipes(llvm,out,language)])
    need(sorted(p.name for p in out.iterdir() if p.name!='verification.json')==files and
         all(p.is_file() and not p.is_symlink() for p in out.iterdir()),'complete exact output inventory')
    for name in ['compile','IR','link']:need(not (out/(name+'.log')).read_bytes(),'empty successful diagnostic '+name)
    for name,artifact in [('object','native.o'),('linked','linked.elf')]:
        log=(out/(name+'.log')).read_text();need(str(out/artifact) in log and all(n in log for n in NAMES),'retained actual artifact/symbol dump binding')
    artifacts=[dict(path=portable(str(out/n),ROOT,llvm),size=(out/n).stat().st_size,sha256=digest(out/n)) for n in files]
    controls=negatives(native,linked,text,language,official,md,llvm,out)
    need(before==inputs(llvm) and all(digest(out/Path(a['path']).name)==a['sha256'] for a in artifacts),'all read input/artifact bytes stable')
    record=dict(schema='TSL9-IRQ-provider-native-v2-formal-v1',language=language,firmware_ready=False,target_executed=False,ISA_emulated=False,
       inputs=[dict(path=portable(str(p),ROOT,llvm),size=p.stat().st_size,sha256=v) for p,v in before.items()],
       original=dict(base=0x8000,start=BASE,end=BASE+164,bytes=164,instructions=53,sha256=ORIGINAL_PIN,typed_rows=EXPECTED),
       native=nf,linked=lf,ir=ir,md_dependencies=deps,recipes=commands,artifacts=artifacts,negative_controls=controls,
       static_contract=dict(bank_address='A0+(A1<<4)',entry_status_mask=4,common_status_mask=2,length_field_mask=15,
         static_LW32_instructions=16,C_SB8_instructions=12,C_SW32_instructions=4,
         payload_output_order=[19,11,12,13,14,15,16,17,18],last_bank_read_overwrites='A5',
         last_A4='previous444 word logically shifted right16',return_A5='fresh LW32[A0+12 or16] OR32',
         preserved_GPRs='all except A4/A5',exits='two RET through unchanged RA; no SP/call/explicit CSR writes',provider_ordinary_C_ABI_proven=False),
       limitations=[
        'Six FUNC symbols are private architectural regions with inherited physical-register values and fallthroughs, not independent ordinary C ABI functions.',
        'Nominal original-layout component matches164B only; native3 RVC relocations resolve to genuine FUNCs at the original component addresses.',
        'Peripheral identity, volatile bus/MMIO physical timing, interrupt context, vector routing, installed silicon and resident contracts remain unproved.',
        'ELF program headers and alignment gaps are retained/pinned metadata; this ELF is not a flashable firmware image.',
        'No target/ISA/MMIO execution, full firmware BIN, OTA acceptance or successful flashing.'])
    encoded=(json.dumps(record,sort_keys=True,indent=2,ensure_ascii=True)+'\n').encode()
    # A RISC-V label ending in a letter followed by :\0A is not a drive path.
    # Require a drive-letter boundary while still rejecting real host roots.
    need(not re.search(rb'(?i)(?<![a-z0-9_])[a-z]:[/\\]|/(?:users|home)/',encoded),'portable LF receipt has no host path')
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
    need(out.is_relative_to(HERE/'build') and out.parent.name.startswith('verified-') and out.name==language,'owned formal provider output')
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
    print(json.dumps(dict(result='PASS',language=language,bytes=164,instructions=53,FUNCs=6,nativeRELA=3,nominalUND=0,nominalRELA=0,
       controls=len(record['negative_controls']),receipt_sha256=sha(encoded.encode()),firmware_ready=False)))
    if args.require_firmware_ready:
        print('REJECTED: private architectural/IRQ/silicon ABI and physical firmware remain unproved; firmware_ready=false.',file=sys.stderr);return 1
    return 0


if __name__=='__main__':
    try:sys.exit(main())
    except (ValueError,OSError,KeyError,IndexError,StopIteration) as exc:
        print('FAIL: '+str(exc),file=sys.stderr);sys.exit(1)
