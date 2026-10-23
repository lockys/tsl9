#!/usr/bin/env python3
"""Bounded offline transport formal checker; never execute target instructions."""
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
SOURCE=HERE/'src/transport_frame.v6.c'
READER=ROOT/'experiments/tsl9-spi-transfer-leaf/verify.py'
FIRMWARE=ROOT/'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
DECODE=ROOT/'analysis/queue-filter-2026-10-23/next-transport.json'
PINS={READER:'8c8eb8e01b9fc30eb7150682aa8848e47fe4a1254c6f87b05e657244a11b6de8',
 FIRMWARE:'0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667',
 DECODE:'0579c86255421f8e313dffb88c4289d2db8087a0632f832389fa9d474a06237a',
 SOURCE:'6908f14f0fc37e6491cdcd043a909059117eee04a0e15cf0013fda2950a119e8',
 HERE/'probe.py':'23f666f4f9acccad76b094401b1655c6a6a826156380a6962fbce321f5b5df3c',
 HERE/'component.ld':'5e30a96739dfdebe25d5e028602279c56754c2496c395ff9a7488609be0e6c9e'}
TOOLS={'clang.exe':'047dfde05acc6fcce5af669e25cd8d40b4f509b8842d151d6d8a43a1c6a35fd6',
 'ld.lld.exe':'fe7f55c0c78b3d87f33b905a3874e10e872ca7beef53a8199d7ff9ac6641ec3f',
 'llvm-objdump.exe':'de40d1188fe63ff373e1a5dd83a12e2cb4545ca3b314da16a476ecf072e5a0fa'}
HEADER_PIN='7ce5540d5fb6e8da9760928e76cbdd5ebef329d701ad598d30d8e6f9d5d78b34'
BASE=0x8a56
ADMISSION_CELL=0x40000+316
TAIL_CELL=0x40000+80
ORIGINAL_PIN='3b01d76ded6b08cb239ca3c8d7e789db8b0b7149d4c6d4e48c50d987a1ef2f0b'
NAMES=['tsl9_filter_external_8a56','tsl9_transport_frame_8a5e','tsl9_transport_first_8a7a',
 'tsl9_transport_first_result_8a90','tsl9_transport_second_8a96','tsl9_transport_second_result_8ab6',
 'tsl9_transport_reject_8abe','tsl9_transport_select0_8acc','tsl9_transport_pack_8ace',
 'tsl9_transport_test_8b0a','tsl9_transport_finish_8b14','tsl9_transport_copy_8b52','tsl9_transport_bare_return_8b6c']
REGIONS=list(zip(NAMES,[0,8,36,58,64,96,104,118,120,180,190,252,278],[8,28,22,6,32,8,14,2,60,10,62,26,2]))
RELATIONS=[(4,16,NAMES[12]),(32,16,NAMES[4]),(40,16,NAMES[4]),(60,16,NAMES[7]),(68,16,NAMES[6]),
 (76,16,NAMES[6]),(100,16,NAMES[8]),(186,16,NAMES[11]),(276,45,NAMES[9])]
MASKS={16:(4,0x01fff07f),45:(2,0xe003)}
EXPECTED = [[0, 4, 'ADDI', 15, 0, 1039], [4, 4, 'BLTU', 15, 13, 35692], [8, 2, 'ADDI', 2, 2, -32], [10, 2, 'SW32', 8, 2, 24], [12, 2, 'SW32', 9, 2, 20], [14, 2, 'SW32', 18, 2, 16], [16, 2, 'SW32', 19, 2, 12], [18, 2, 'SW32', 1, 2, 28], [20, 4, 'LHU16', 14, 3, 150], [24, 2, 'MV', 18, 10], [26, 2, 'MV', 8, 13], [28, 2, 'MV', 9, 12], [30, 2, 'MV', 19, 11], [32, 4, 'BNE', 14, 10, 35478], [36, 2, 'LUI', 15, 65536], [38, 2, 'ADDI', 15, 15, -2], [40, 4, 'BEQ', 14, 15, 35478], [44, 4, 'LUI', 15, 262144], [48, 4, 'LW32', 15, 15, 316], [52, 4, 'ADDI', 11, 3, 128], [56, 2, 'JALR', 1, 15, 0], [58, 2, 'ADDI', 15, 0, 1], [60, 4, 'BEQ', 10, 15, 35532], [64, 4, 'LHU16', 15, 3, 154], [68, 4, 'BNE', 15, 18, 35518], [72, 2, 'LUI', 15, 65536], [74, 2, 'ADDI', 15, 15, -2], [76, 4, 'BEQ', 18, 15, 35518], [80, 4, 'LUI', 15, 262144], [84, 4, 'LW32', 15, 15, 316], [88, 4, 'ADDI', 11, 3, 128], [92, 2, 'MV', 10, 18], [94, 2, 'JALR', 1, 15, 0], [96, 2, 'ADDI', 15, 0, 1], [98, 2, 'ADDI', 12, 0, 1], [100, 4, 'BEQ', 10, 15, 35534], [104, 2, 'LW32', 1, 2, 28], [106, 2, 'LW32', 8, 2, 24], [108, 2, 'LW32', 9, 2, 20], [110, 2, 'LW32', 18, 2, 16], [112, 2, 'LW32', 19, 2, 12], [114, 2, 'ADDI', 2, 2, 32], [116, 2, 'RET', 1], [118, 2, 'ADDI', 12, 0, 0], [120, 4, 'ADDI', 15, 0, 1062], [124, 4, 'MUL', 15, 12, 15], [128, 4, 'AUIPC', 13, 536879104], [132, 4, 'ADDI', 13, 13, 1718], [136, 2, 'LUI', 14, 4294934528], [138, 4, 'XORI', 14, 14, -171], [142, 4, 'ANDI', 11, 8, 255], [146, 2, 'ADDI', 15, 15, 6], [148, 2, 'ADD', 15, 15, 13], [150, 4, 'SH16', 14, 15, 0], [154, 4, 'SB8', 11, 15, 4], [158, 4, 'SRLI', 14, 8, 8], [162, 2, 'ADD', 11, 11, 19], [164, 4, 'SB8', 14, 15, 3], [168, 2, 'ADD', 14, 14, 11], [170, 4, 'SB8', 19, 15, 2], [174, 4, 'ANDI', 14, 14, 255], [178, 2, 'ADDI', 11, 0, 0], [180, 4, 'SLLI', 10, 11, 16], [184, 2, 'SRLI', 10, 10, 16], [186, 4, 'BLTU', 10, 8, 35666], [190, 2, 'ADD', 15, 15, 8], [192, 4, 'SB8', 14, 15, 5], [196, 4, 'ADDI', 15, 0, 1062], [200, 4, 'MUL', 15, 12, 15], [204, 2, 'ADDI', 8, 8, 6], [206, 2, 'SLLI', 12, 12, 2], [208, 2, 'LW32', 1, 2, 28], [210, 2, 'LW32', 9, 2, 20], [212, 2, 'LW32', 18, 2, 16], [214, 2, 'LW32', 19, 2, 12], [216, 2, 'ADDI', 11, 0, 1], [218, 2, 'ADD', 15, 15, 13], [220, 4, 'SH16', 8, 15, 2], [224, 4, 'SH16', 0, 15, 4], [228, 4, 'ADDI', 15, 3, 148], [232, 2, 'ADD', 12, 12, 15], [234, 2, 'LW32', 8, 2, 24], [236, 4, 'LUI', 15, 262144], [240, 4, 'LW32', 6, 15, 80], [244, 4, 'LBU8', 10, 12, 0], [248, 2, 'ADDI', 2, 2, 32], [250, 2, 'JR', 6], [252, 4, 'ADD', 10, 9, 11], [256, 4, 'LBU8', 10, 10, 0], [260, 4, 'ADD', 16, 15, 11], [264, 2, 'ADDI', 11, 11, 1], [266, 2, 'ADD', 14, 14, 10], [268, 4, 'SB8', 10, 16, 5], [272, 4, 'ANDI', 14, 14, 255], [276, 2, 'J', 35594], [278, 2, 'RET', 1]]
ELF_PINS = {True: 'e722e2ce3361c930be307507328e1305280e5cc06c4f854fa84b6882b07d6984', False: '8c9c84504250b95495d9a82bb8ce1c58d3e333c0801a46fe1174a792a3cd20de'}
IR_PINS = {'c': 'db805dc687d2aa2c24044455e0205c94e2e85ca9ab6e444752b58a5a2b57b3af', 'cpp': 'd4b944e10b8598636ae1f5dcd4df0904782713f81e262ea9abd474cd560cbe43'}
SCHEMAS = {'native': {'header': [1, 243, 1, 0, 0, 1808, 1, 52, 0, 0, 40, 29, 1], 'program_headers': [], 'sections': [{'name_offset': 0, 'type': 0, 'flags': 0, 'address': 0, 'offset': 0, 'size': 0, 'link': 0, 'info': 0, 'align': 0, 'entsize': 0, 'index': 0, 'name': ''}, {'name_offset': 258, 'type': 3, 'flags': 0, 'address': 0, 'offset': 1145, 'size': 660, 'link': 0, 'info': 0, 'align': 1, 'entsize': 0, 'index': 1, 'name': '.strtab'}, {'name_offset': 1, 'type': 1, 'flags': 6, 'address': 0, 'offset': 52, 'size': 0, 'link': 0, 'info': 0, 'align': 2, 'entsize': 0, 'index': 2, 'name': '.text'}, {'name_offset': 450, 'type': 1, 'flags': 6, 'address': 0, 'offset': 52, 'size': 8, 'link': 0, 'info': 0, 'align': 2, 'entsize': 0, 'index': 3, 'name': '.text.tsl9_filter_external_8a56'}, {'name_offset': 445, 'type': 4, 'flags': 64, 'address': 0, 'offset': 1024, 'size': 12, 'link': 28, 'info': 3, 'align': 4, 'entsize': 12, 'index': 4, 'name': '.rela.text.tsl9_filter_external_8a56'}, {'name_offset': 133, 'type': 1, 'flags': 6, 'address': 0, 'offset': 60, 'size': 28, 'link': 0, 'info': 0, 'align': 2, 'entsize': 0, 'index': 5, 'name': '.text.tsl9_transport_frame_8a5e'}, {'name_offset': 128, 'type': 4, 'flags': 64, 'address': 0, 'offset': 1036, 'size': 12, 'link': 28, 'info': 5, 'align': 4, 'entsize': 12, 'index': 6, 'name': '.rela.text.tsl9_transport_frame_8a5e'}, {'name_offset': 279, 'type': 1, 'flags': 6, 'address': 0, 'offset': 88, 'size': 22, 'link': 0, 'info': 0, 'align': 2, 'entsize': 0, 'index': 7, 'name': '.text.tsl9_transport_first_8a7a'}, {'name_offset': 274, 'type': 4, 'flags': 64, 'address': 0, 'offset': 1048, 'size': 12, 'link': 28, 'info': 7, 'align': 4, 'entsize': 12, 'index': 8, 'name': '.rela.text.tsl9_transport_first_8a7a'}, {'name_offset': 610, 'type': 1, 'flags': 6, 'address': 0, 'offset': 110, 'size': 6, 'link': 0, 'info': 0, 'align': 2, 'entsize': 0, 'index': 9, 'name': '.text.tsl9_transport_first_result_8a90'}, {'name_offset': 605, 'type': 4, 'flags': 64, 'address': 0, 'offset': 1060, 'size': 12, 'link': 28, 'info': 9, 'align': 4, 'entsize': 12, 'index': 10, 'name': '.rela.text.tsl9_transport_first_result_8a90'}, {'name_offset': 412, 'type': 1, 'flags': 6, 'address': 0, 'offset': 116, 'size': 32, 'link': 0, 'info': 0, 'align': 2, 'entsize': 0, 'index': 11, 'name': '.text.tsl9_transport_second_8a96'}, {'name_offset': 407, 'type': 4, 'flags': 64, 'address': 0, 'offset': 1072, 'size': 24, 'link': 28, 'info': 11, 'align': 4, 'entsize': 12, 'index': 12, 'name': '.rela.text.tsl9_transport_second_8a96'}, {'name_offset': 367, 'type': 1, 'flags': 6, 'address': 0, 'offset': 148, 'size': 8, 'link': 0, 'info': 0, 'align': 2, 'entsize': 0, 'index': 13, 'name': '.text.tsl9_transport_second_result_8ab6'}, {'name_offset': 362, 'type': 4, 'flags': 64, 'address': 0, 'offset': 1096, 'size': 12, 'link': 28, 'info': 13, 'align': 4, 'entsize': 12, 'index': 14, 'name': '.rela.text.tsl9_transport_second_result_8ab6'}, {'name_offset': 95, 'type': 1, 'flags': 6, 'address': 0, 'offset': 156, 'size': 14, 'link': 0, 'info': 0, 'align': 2, 'entsize': 0, 'index': 15, 'name': '.text.tsl9_transport_reject_8abe'}, {'name_offset': 165, 'type': 1, 'flags': 6, 'address': 0, 'offset': 170, 'size': 2, 'link': 0, 'info': 0, 'align': 2, 'entsize': 0, 'index': 16, 'name': '.text.tsl9_transport_select0_8acc'}, {'name_offset': 64, 'type': 1, 'flags': 6, 'address': 0, 'offset': 172, 'size': 60, 'link': 0, 'info': 0, 'align': 2, 'entsize': 0, 'index': 17, 'name': '.text.tsl9_transport_pack_8ace'}, {'name_offset': 316, 'type': 1, 'flags': 6, 'address': 0, 'offset': 232, 'size': 10, 'link': 0, 'info': 0, 'align': 2, 'entsize': 0, 'index': 18, 'name': '.text.tsl9_transport_test_8b0a'}, {'name_offset': 311, 'type': 4, 'flags': 64, 'address': 0, 'offset': 1108, 'size': 12, 'link': 28, 'info': 18, 'align': 4, 'entsize': 12, 'index': 19, 'name': '.rela.text.tsl9_transport_test_8b0a'}, {'name_offset': 492, 'type': 1, 'flags': 6, 'address': 0, 'offset': 242, 'size': 62, 'link': 0, 'info': 0, 'align': 2, 'entsize': 0, 'index': 20, 'name': '.text.tsl9_transport_finish_8b14'}, {'name_offset': 552, 'type': 1, 'flags': 6, 'address': 0, 'offset': 304, 'size': 26, 'link': 0, 'info': 0, 'align': 2, 'entsize': 0, 'index': 21, 'name': '.text.tsl9_transport_copy_8b52'}, {'name_offset': 547, 'type': 4, 'flags': 64, 'address': 0, 'offset': 1120, 'size': 12, 'link': 28, 'info': 21, 'align': 4, 'entsize': 12, 'index': 22, 'name': '.rela.text.tsl9_transport_copy_8b52'}, {'name_offset': 199, 'type': 1, 'flags': 6, 'address': 0, 'offset': 330, 'size': 2, 'link': 0, 'info': 0, 'align': 2, 'entsize': 0, 'index': 23, 'name': '.text.tsl9_transport_bare_return_8b6c'}, {'name_offset': 7, 'type': 1, 'flags': 48, 'address': 0, 'offset': 332, 'size': 159, 'link': 0, 'info': 0, 'align': 1, 'entsize': 1, 'index': 24, 'name': '.comment'}, {'name_offset': 34, 'type': 1, 'flags': 0, 'address': 0, 'offset': 491, 'size': 0, 'link': 0, 'info': 0, 'align': 1, 'entsize': 0, 'index': 25, 'name': '.note.GNU-stack'}, {'name_offset': 16, 'type': 1879048195, 'flags': 0, 'address': 0, 'offset': 491, 'size': 52, 'link': 0, 'info': 0, 'align': 1, 'entsize': 0, 'index': 26, 'name': '.riscv.attributes'}, {'name_offset': 50, 'type': 1879002115, 'flags': 2147483648, 'address': 0, 'offset': 1132, 'size': 13, 'link': 28, 'info': 0, 'align': 1, 'entsize': 0, 'index': 27, 'name': '.llvm_addrsig'}, {'name_offset': 266, 'type': 2, 'flags': 0, 'address': 0, 'offset': 544, 'size': 480, 'link': 1, 'info': 17, 'align': 4, 'entsize': 16, 'index': 28, 'name': '.symtab'}], 'symbols': [{'index': 0, 'name': '', 'value': 0, 'size': 0, 'info': 0, 'other': 0, 'section': 0}, {'index': 1, 'name': 'transport_frame.v6.c', 'value': 0, 'size': 0, 'info': 4, 'other': 0, 'section': 65521}, {'index': 2, 'name': '$x.0', 'value': 0, 'size': 0, 'info': 0, 'other': 0, 'section': 3}, {'index': 3, 'name': '$x.1', 'value': 0, 'size': 0, 'info': 0, 'other': 0, 'section': 5}, {'index': 4, 'name': '$x.2', 'value': 0, 'size': 0, 'info': 0, 'other': 0, 'section': 7}, {'index': 5, 'name': '$x.3', 'value': 0, 'size': 0, 'info': 0, 'other': 0, 'section': 9}, {'index': 6, 'name': '$x.4', 'value': 0, 'size': 0, 'info': 0, 'other': 0, 'section': 11}, {'index': 7, 'name': '$x.5', 'value': 0, 'size': 0, 'info': 0, 'other': 0, 'section': 13}, {'index': 8, 'name': '$x.6', 'value': 0, 'size': 0, 'info': 0, 'other': 0, 'section': 15}, {'index': 9, 'name': '$x.7', 'value': 0, 'size': 0, 'info': 0, 'other': 0, 'section': 16}, {'index': 10, 'name': '$x.8', 'value': 0, 'size': 0, 'info': 0, 'other': 0, 'section': 17}, {'index': 11, 'name': '$x.9', 'value': 0, 'size': 0, 'info': 0, 'other': 0, 'section': 18}, {'index': 12, 'name': '$x.10', 'value': 0, 'size': 0, 'info': 0, 'other': 0, 'section': 20}, {'index': 13, 'name': '$x.11', 'value': 0, 'size': 0, 'info': 0, 'other': 0, 'section': 21}, {'index': 14, 'name': '$x.12', 'value': 0, 'size': 0, 'info': 0, 'other': 0, 'section': 23}, {'index': 15, 'name': '$d.13', 'value': 0, 'size': 0, 'info': 0, 'other': 0, 'section': 24}, {'index': 16, 'name': '$d.14', 'value': 0, 'size': 0, 'info': 0, 'other': 0, 'section': 26}, {'index': 17, 'name': 'tsl9_filter_external_8a56', 'value': 0, 'size': 8, 'info': 18, 'other': 0, 'section': 3}, {'index': 18, 'name': 'tsl9_transport_bare_return_8b6c', 'value': 0, 'size': 2, 'info': 18, 'other': 0, 'section': 23}, {'index': 19, 'name': 'tsl9_transport_frame_8a5e', 'value': 0, 'size': 28, 'info': 18, 'other': 0, 'section': 5}, {'index': 20, 'name': 'tsl9_transport_second_8a96', 'value': 0, 'size': 32, 'info': 18, 'other': 0, 'section': 11}, {'index': 21, 'name': 'tsl9_transport_first_8a7a', 'value': 0, 'size': 22, 'info': 18, 'other': 0, 'section': 7}, {'index': 22, 'name': 'tsl9_transport_first_result_8a90', 'value': 0, 'size': 6, 'info': 18, 'other': 0, 'section': 9}, {'index': 23, 'name': 'tsl9_transport_select0_8acc', 'value': 0, 'size': 2, 'info': 18, 'other': 0, 'section': 16}, {'index': 24, 'name': 'tsl9_transport_reject_8abe', 'value': 0, 'size': 14, 'info': 18, 'other': 0, 'section': 15}, {'index': 25, 'name': 'tsl9_transport_second_result_8ab6', 'value': 0, 'size': 8, 'info': 18, 'other': 0, 'section': 13}, {'index': 26, 'name': 'tsl9_transport_pack_8ace', 'value': 0, 'size': 60, 'info': 18, 'other': 0, 'section': 17}, {'index': 27, 'name': 'tsl9_transport_test_8b0a', 'value': 0, 'size': 10, 'info': 18, 'other': 0, 'section': 18}, {'index': 28, 'name': 'tsl9_transport_copy_8b52', 'value': 0, 'size': 26, 'info': 18, 'other': 0, 'section': 21}, {'index': 29, 'name': 'tsl9_transport_finish_8b14', 'value': 0, 'size': 62, 'info': 18, 'other': 0, 'section': 20}], 'relocations': [{'section': 3, 'offset': 4, 'type': 16, 'symbol': 18, 'addend': 0}, {'section': 5, 'offset': 24, 'type': 16, 'symbol': 20, 'addend': 0}, {'section': 7, 'offset': 4, 'type': 16, 'symbol': 20, 'addend': 0}, {'section': 9, 'offset': 2, 'type': 16, 'symbol': 23, 'addend': 0}, {'section': 11, 'offset': 4, 'type': 16, 'symbol': 24, 'addend': 0}, {'section': 11, 'offset': 12, 'type': 16, 'symbol': 24, 'addend': 0}, {'section': 13, 'offset': 4, 'type': 16, 'symbol': 26, 'addend': 0}, {'section': 18, 'offset': 6, 'type': 16, 'symbol': 28, 'addend': 0}, {'section': 21, 'offset': 24, 'type': 45, 'symbol': 27, 'addend': 0}], 'noncode_section_hashes': {'': 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855', '.strtab': '9048f91ac692b2ead00c3d4e520a927f7ada9b7e5c80b46bda80f811f1e639a1', '.rela.text.tsl9_filter_external_8a56': 'eba4eb484ffd460ad36f9b65cdadbfce84cf76313318232d5438821f2ecbdcd3', '.rela.text.tsl9_transport_frame_8a5e': 'e4a2d83fd5dc116712bebcb13df23cf69261388c8957e255d57dd535750e6082', '.rela.text.tsl9_transport_first_8a7a': 'f33a3a886e24f393a2dfeb134dfa1e51887f10482a4d73bc33044c23e3bd7579', '.rela.text.tsl9_transport_first_result_8a90': 'ef7ab7872c335cd958621205955a456ff6cd6f3d3f9588881f081c7b70f0bca9', '.rela.text.tsl9_transport_second_8a96': '46a9705c09e24a809ebdca70719223669703436946fb8886429040cb00c019a4', '.rela.text.tsl9_transport_second_result_8ab6': 'db77e285d52024f38495ce8348d3788526126f25088f373a369253573c1eff32', '.rela.text.tsl9_transport_test_8b0a': '5ad9e65d37decee4604d112b75bd5729038cd6111652455ffdb4bb1eedd95a42', '.rela.text.tsl9_transport_copy_8b52': '73370847a06dcf2edb49f340187f1260af3e90110e79de6995d0220e0ccd05f2', '.comment': '72c64fbc17a5d9f46f33ac0650b7d4f549d87c2ba9e77ebd765a25a3960e3017', '.note.GNU-stack': 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855', '.riscv.attributes': 'f2bd85b0ab58609a20dbdef6cc6e3f2dd1a34cdcb554580710aa3819cd24ad71', '.llvm_addrsig': '0677afe46689d31030af52b75715f2701677905c5f99decb8bb20dff096f49cb', '.symtab': '86df11455b7c6aaff29493330cc35f5f3c303f05f518a3f1fc9aaf9a53dd09ab'}, 'outside_allocated_code_sha256': 'fa8b2651df81f481d3edca7af4e724b778e23506b7461b61ab4e2fc5943582a9'}, 'partial': {'header': [1, 243, 1, 0, 0, 1500, 1, 52, 0, 0, 40, 8, 6], 'program_headers': [], 'sections': [{'name_offset': 0, 'type': 0, 'flags': 0, 'address': 0, 'offset': 0, 'size': 0, 'link': 0, 'info': 0, 'align': 0, 'entsize': 0, 'index': 0, 'name': ''}, {'name_offset': 1, 'type': 1, 'flags': 6, 'address': 0, 'offset': 52, 'size': 280, 'link': 0, 'info': 0, 'align': 2, 'entsize': 0, 'index': 1, 'name': '.transport'}, {'name_offset': 12, 'type': 1, 'flags': 6, 'address': 0, 'offset': 332, 'size': 0, 'link': 0, 'info': 0, 'align': 2, 'entsize': 0, 'index': 2, 'name': '.text'}, {'name_offset': 18, 'type': 4, 'flags': 64, 'address': 0, 'offset': 332, 'size': 108, 'link': 5, 'info': 1, 'align': 4, 'entsize': 12, 'index': 3, 'name': '.rela.transport'}, {'name_offset': 34, 'type': 1879002115, 'flags': 2147483648, 'address': 0, 'offset': 440, 'size': 13, 'link': 0, 'info': 0, 'align': 1, 'entsize': 0, 'index': 4, 'name': '.llvm_addrsig'}, {'name_offset': 48, 'type': 2, 'flags': 0, 'address': 0, 'offset': 456, 'size': 512, 'link': 7, 'info': 19, 'align': 4, 'entsize': 16, 'index': 5, 'name': '.symtab'}, {'name_offset': 56, 'type': 3, 'flags': 0, 'address': 0, 'offset': 968, 'size': 74, 'link': 0, 'info': 0, 'align': 1, 'entsize': 0, 'index': 6, 'name': '.shstrtab'}, {'name_offset': 66, 'type': 3, 'flags': 0, 'address': 0, 'offset': 1042, 'size': 457, 'link': 0, 'info': 0, 'align': 1, 'entsize': 0, 'index': 7, 'name': '.strtab'}], 'symbols': [{'index': 0, 'name': '', 'value': 0, 'size': 0, 'info': 0, 'other': 0, 'section': 0}, {'index': 1, 'name': 'transport_frame.v6.c', 'value': 0, 'size': 0, 'info': 4, 'other': 0, 'section': 65521}, {'index': 2, 'name': '$x.0', 'value': 0, 'size': 0, 'info': 0, 'other': 0, 'section': 1}, {'index': 3, 'name': '$x.1', 'value': 8, 'size': 0, 'info': 0, 'other': 0, 'section': 1}, {'index': 4, 'name': '$x.2', 'value': 36, 'size': 0, 'info': 0, 'other': 0, 'section': 1}, {'index': 5, 'name': '$x.3', 'value': 58, 'size': 0, 'info': 0, 'other': 0, 'section': 1}, {'index': 6, 'name': '$x.4', 'value': 64, 'size': 0, 'info': 0, 'other': 0, 'section': 1}, {'index': 7, 'name': '$x.5', 'value': 96, 'size': 0, 'info': 0, 'other': 0, 'section': 1}, {'index': 8, 'name': '$x.6', 'value': 104, 'size': 0, 'info': 0, 'other': 0, 'section': 1}, {'index': 9, 'name': '$x.7', 'value': 118, 'size': 0, 'info': 0, 'other': 0, 'section': 1}, {'index': 10, 'name': '$x.8', 'value': 120, 'size': 0, 'info': 0, 'other': 0, 'section': 1}, {'index': 11, 'name': '$x.9', 'value': 180, 'size': 0, 'info': 0, 'other': 0, 'section': 1}, {'index': 12, 'name': '$x.10', 'value': 190, 'size': 0, 'info': 0, 'other': 0, 'section': 1}, {'index': 13, 'name': '$x.11', 'value': 252, 'size': 0, 'info': 0, 'other': 0, 'section': 1}, {'index': 14, 'name': '$x.12', 'value': 278, 'size': 0, 'info': 0, 'other': 0, 'section': 1}, {'index': 15, 'name': '$d.14', 'value': 0, 'size': 0, 'info': 0, 'other': 0, 'section': 65521}, {'index': 16, 'name': '', 'value': 0, 'size': 0, 'info': 3, 'other': 0, 'section': 1}, {'index': 17, 'name': '', 'value': 0, 'size': 0, 'info': 3, 'other': 0, 'section': 2}, {'index': 18, 'name': '', 'value': 0, 'size': 0, 'info': 3, 'other': 0, 'section': 4}, {'index': 19, 'name': 'tsl9_filter_external_8a56', 'value': 0, 'size': 8, 'info': 18, 'other': 0, 'section': 1}, {'index': 20, 'name': 'tsl9_transport_bare_return_8b6c', 'value': 278, 'size': 2, 'info': 18, 'other': 0, 'section': 1}, {'index': 21, 'name': 'tsl9_transport_frame_8a5e', 'value': 8, 'size': 28, 'info': 18, 'other': 0, 'section': 1}, {'index': 22, 'name': 'tsl9_transport_second_8a96', 'value': 64, 'size': 32, 'info': 18, 'other': 0, 'section': 1}, {'index': 23, 'name': 'tsl9_transport_first_8a7a', 'value': 36, 'size': 22, 'info': 18, 'other': 0, 'section': 1}, {'index': 24, 'name': 'tsl9_transport_first_result_8a90', 'value': 58, 'size': 6, 'info': 18, 'other': 0, 'section': 1}, {'index': 25, 'name': 'tsl9_transport_select0_8acc', 'value': 118, 'size': 2, 'info': 18, 'other': 0, 'section': 1}, {'index': 26, 'name': 'tsl9_transport_reject_8abe', 'value': 104, 'size': 14, 'info': 18, 'other': 0, 'section': 1}, {'index': 27, 'name': 'tsl9_transport_second_result_8ab6', 'value': 96, 'size': 8, 'info': 18, 'other': 0, 'section': 1}, {'index': 28, 'name': 'tsl9_transport_pack_8ace', 'value': 120, 'size': 60, 'info': 18, 'other': 0, 'section': 1}, {'index': 29, 'name': 'tsl9_transport_test_8b0a', 'value': 180, 'size': 10, 'info': 18, 'other': 0, 'section': 1}, {'index': 30, 'name': 'tsl9_transport_copy_8b52', 'value': 252, 'size': 26, 'info': 18, 'other': 0, 'section': 1}, {'index': 31, 'name': 'tsl9_transport_finish_8b14', 'value': 190, 'size': 62, 'info': 18, 'other': 0, 'section': 1}], 'relocations': [{'section': 1, 'offset': 4, 'type': 16, 'symbol': 20, 'addend': 0}, {'section': 1, 'offset': 32, 'type': 16, 'symbol': 22, 'addend': 0}, {'section': 1, 'offset': 40, 'type': 16, 'symbol': 22, 'addend': 0}, {'section': 1, 'offset': 60, 'type': 16, 'symbol': 25, 'addend': 0}, {'section': 1, 'offset': 68, 'type': 16, 'symbol': 26, 'addend': 0}, {'section': 1, 'offset': 76, 'type': 16, 'symbol': 26, 'addend': 0}, {'section': 1, 'offset': 100, 'type': 16, 'symbol': 28, 'addend': 0}, {'section': 1, 'offset': 186, 'type': 16, 'symbol': 30, 'addend': 0}, {'section': 1, 'offset': 276, 'type': 45, 'symbol': 29, 'addend': 0}], 'noncode_section_hashes': {'': 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855', '.rela.transport': 'e0d12d91e6eae6299b74e6fe4cc45e42b7e6c697af8e35c775779ace989951bf', '.llvm_addrsig': '0677afe46689d31030af52b75715f2701677905c5f99decb8bb20dff096f49cb', '.symtab': 'eeb674135ee53d7acb9155f07d4b7a33948c298342c5ba0685aa70cbd1ba0f3f', '.shstrtab': '7136a2e6212e5c981dc26aaf773931ed706817479911cefc850b723c74c9c237', '.strtab': '5eb0102530284fb8014ce839522cfbadced23df7d44acee6d5cf19bfdf0212bb'}, 'outside_allocated_code_sha256': '0146469a02d0d38eb737705c0ee3f5606a32ea16e93b7f956426df2c16af84cd'}}
IR_CORE = {'tsl9_filter_external_8a56': ['tail call void asm sideeffect ".Ltransport_large:\\0Abltu a5, a3, .Ltransport_large\\0A.reloc .-4, R_RISCV_BRANCH, tsl9_transport_bare_return_8b6c\\0A", "{x15},~{memory}"(i32 1039) #2', 'unreachable'], 'tsl9_transport_frame_8a5e': ['tail call void asm sideeffect "addi sp, sp, -32\\0Asw s0, 24(sp)\\0Asw s1, 20(sp)\\0Asw s2, 16(sp)\\0Asw s3, 12(sp)\\0Asw ra, 28(sp)\\0Alhu a4, 150(gp)\\0Amv s2, a0\\0Amv s0, a3\\0Amv s1, a2\\0Amv s3, a1\\0A.Ltransport_first_miss:\\0Abne a4, a0, .Ltransport_first_miss\\0A.reloc .-4, R_RISCV_BRANCH, tsl9_transport_second_8a96\\0A", ""() #2', 'unreachable'], 'tsl9_transport_first_8a7a': ['tail call void asm sideeffect ".Ltransport_first_empty:\\0Abeq a4, a5, .Ltransport_first_empty\\0A.reloc .-4, R_RISCV_BRANCH, tsl9_transport_second_8a96\\0A", "{x15},~{memory}"(i32 65534) #2', '%1 = tail call i32 asm sideeffect "", "={x15},{x15},~{memory}"(i32 262144) #2', '%2 = add i32 %1, 316', '%3 = inttoptr i32 %2 to ptr', '%4 = load volatile i32, ptr %3, align 4', 'tail call void asm sideeffect "addi a1, gp, 128\\0Ajalr a5\\0A", "{x15},~{x10},~{x11},~{x12},~{x13},~{x14},~{x16},~{memory}"(i32 %4) #2', 'unreachable'], 'tsl9_transport_first_result_8a90': ['tail call void asm sideeffect ".Ltransport_first_admitted:\\0Abeq a0, a5, .Ltransport_first_admitted\\0A.reloc .-4, R_RISCV_BRANCH, tsl9_transport_select0_8acc\\0A", "{x15},~{memory}"(i32 1) #2', 'unreachable'], 'tsl9_transport_second_8a96': ['%1 = tail call i32 asm sideeffect "lhu a5, 154(gp)\\0A", "={x15},~{memory}"() #2', 'tail call void asm sideeffect ".Ltransport_second_miss:\\0Abne a5, s2, .Ltransport_second_miss\\0A.reloc .-4, R_RISCV_BRANCH, tsl9_transport_reject_8abe\\0A", "{x15},~{memory}"(i32 %1) #2', '%2 = tail call i32 asm sideeffect "lui a5, 0x10\\0Aaddi a5, a5, -2\\0A", "={x15},~{memory}"() #2', 'tail call void asm sideeffect ".Ltransport_second_empty:\\0Abeq s2, a5, .Ltransport_second_empty\\0A.reloc .-4, R_RISCV_BRANCH, tsl9_transport_reject_8abe\\0A", "{x15},~{memory}"(i32 %2) #2', '%3 = tail call i32 asm sideeffect "", "={x15},{x15},~{memory}"(i32 262144) #2', '%4 = add i32 %3, 316', '%5 = inttoptr i32 %4 to ptr', '%6 = load volatile i32, ptr %5, align 4', 'tail call void asm sideeffect "addi a1, gp, 128\\0Amv a0, s2\\0Ajalr a5\\0A", "{x15},~{x10},~{x11},~{x12},~{x13},~{x14},~{x16},~{memory}"(i32 %6) #2', 'unreachable'], 'tsl9_transport_second_result_8ab6': ['%1 = tail call i32 asm sideeffect "", "={x15},{x15},~{memory}"(i32 1) #2', 'tail call void asm sideeffect ".Ltransport_second_admitted:\\0Abeq a0, a5, .Ltransport_second_admitted\\0A.reloc .-4, R_RISCV_BRANCH, tsl9_transport_pack_8ace\\0A", "{x15},{x12},~{memory}"(i32 %1, i32 1) #2', 'unreachable'], 'tsl9_transport_reject_8abe': ['tail call void asm sideeffect "lw ra, 28(sp)\\0Alw s0, 24(sp)\\0Alw s1, 20(sp)\\0Alw s2, 16(sp)\\0Alw s3, 12(sp)\\0Aaddi sp, sp, 32\\0Aret\\0A", ""() #2', 'unreachable'], 'tsl9_transport_select0_8acc': ['tail call void asm sideeffect "", "{x12},~{memory}"(i32 0) #2', 'unreachable'], 'tsl9_transport_pack_8ace': ['%1 = tail call i32 asm sideeffect "", "={x12},~{memory}"() #2', '%2 = tail call { i32, i32 } asm sideeffect "", "={x15},={x12},{x15},{x12},~{memory}"(i32 1062, i32 %1) #2', '%3 = extractvalue { i32, i32 } %2, 0', '%4 = extractvalue { i32, i32 } %2, 1', '%5 = mul i32 %4, %3', '%6 = tail call { i32, i32 } asm sideeffect "auipc a3, 0x20002\\0Aaddi a3, a3, 1718\\0A", "={x13},={x15},{x15},~{memory}"(i32 %5) #2', '%7 = extractvalue { i32, i32 } %6, 0', '%8 = extractvalue { i32, i32 } %6, 1', '%9 = tail call { i32, i32 } asm sideeffect "", "={x14},={x15},{x13},{x14},{x15},~{memory}"(i32 %7, i32 -32768, i32 %8) #2', '%10 = extractvalue { i32, i32 } %9, 0', '%11 = extractvalue { i32, i32 } %9, 1', '%12 = xor i32 %10, -171', '%13 = tail call { i32, i32 } asm sideeffect "", "={x14},={x15},{x13},{x14},{x15},~{memory}"(i32 %7, i32 %12, i32 %11) #2', '%14 = extractvalue { i32, i32 } %13, 0', '%15 = extractvalue { i32, i32 } %13, 1', '%16 = tail call i32 asm sideeffect "andi a1, s0, 255", "={x11},~{memory}"() #2', '%17 = tail call { i32, i32, i32 } asm sideeffect "", "={x11},={x15},={x14},{x13},{x11},{x15},{x14},~{memory}"(i32 %7, i32 %16, i32 %15, i32 %14) #2', '%18 = extractvalue { i32, i32, i32 } %17, 0', '%19 = extractvalue { i32, i32, i32 } %17, 1', '%20 = extractvalue { i32, i32, i32 } %17, 2', '%21 = add i32 %19, 6', '%22 = tail call { i32, i32, i32 } asm sideeffect "", "={x15},={x11},={x14},{x13},{x15},{x11},{x14},~{memory}"(i32 %7, i32 %21, i32 %18, i32 %20) #2', '%23 = extractvalue { i32, i32, i32 } %22, 0', '%24 = extractvalue { i32, i32, i32 } %22, 1', '%25 = extractvalue { i32, i32, i32 } %22, 2', '%26 = add i32 %23, %7', '%27 = trunc i32 %25 to i16', '%28 = inttoptr i32 %26 to ptr', 'store volatile i16 %27, ptr %28, align 2', '%29 = trunc i32 %24 to i8', '%30 = add i32 %26, 4', '%31 = inttoptr i32 %30 to ptr', 'store volatile i8 %29, ptr %31, align 1', '%32 = tail call i32 asm sideeffect "srli a4, s0, 8", "={x14},~{memory}"() #2', '%33 = tail call { i32, i32, i32 } asm sideeffect "", "={x14},={x11},={x15},{x14},{x11},{x15},~{memory}"(i32 %32, i32 %24, i32 %26) #2', '%34 = extractvalue { i32, i32, i32 } %33, 0', '%35 = extractvalue { i32, i32, i32 } %33, 1', '%36 = extractvalue { i32, i32, i32 } %33, 2', '%37 = tail call i32 asm sideeffect "add a1, a1, s3", "={x11},{x11},~{memory}"(i32 %35) #2', '%38 = tail call { i32, i32, i32 } asm sideeffect "", "={x11},={x14},={x15},{x11},{x14},{x15},~{memory}"(i32 %37, i32 %34, i32 %36) #2', '%39 = extractvalue { i32, i32, i32 } %38, 0', '%40 = extractvalue { i32, i32, i32 } %38, 1', '%41 = extractvalue { i32, i32, i32 } %38, 2', '%42 = trunc i32 %40 to i8', '%43 = add i32 %41, 3', '%44 = inttoptr i32 %43 to ptr', 'store volatile i8 %42, ptr %44, align 1', '%45 = tail call { i32, i32, i32 } asm sideeffect "", "={x14},={x11},={x15},{x14},{x11},{x15},~{memory}"(i32 %40, i32 %39, i32 %41) #2', '%46 = extractvalue { i32, i32, i32 } %45, 0', '%47 = extractvalue { i32, i32, i32 } %45, 1', '%48 = extractvalue { i32, i32, i32 } %45, 2', '%49 = add i32 %46, %47', '%50 = tail call { i32, i32, i32 } asm sideeffect "", "={x14},={x11},={x15},{x14},{x11},{x15},~{memory}"(i32 %49, i32 %47, i32 %48) #2', '%51 = extractvalue { i32, i32, i32 } %50, 0', '%52 = extractvalue { i32, i32, i32 } %50, 1', '%53 = extractvalue { i32, i32, i32 } %50, 2', '%54 = tail call { i32, i32, i32 } asm sideeffect "sb s3, 2(a5)", "={x14},={x11},={x15},{x14},{x11},{x15},~{memory}"(i32 %51, i32 %52, i32 %53) #2', '%55 = extractvalue { i32, i32, i32 } %54, 0', '%56 = extractvalue { i32, i32, i32 } %54, 1', '%57 = extractvalue { i32, i32, i32 } %54, 2', '%58 = and i32 %55, 255', '%59 = tail call { i32, i32, i32 } asm sideeffect "", "={x14},={x11},={x15},{x14},{x11},{x15},~{memory}"(i32 %58, i32 %56, i32 %57) #2', '%60 = extractvalue { i32, i32, i32 } %59, 0', '%61 = extractvalue { i32, i32, i32 } %59, 2', 'tail call void asm sideeffect "", "{x11},{x15},{x14},{x12},{x13},~{memory}"(i32 0, i32 %61, i32 %60, i32 %4, i32 %7) #2', 'unreachable'], 'tsl9_transport_test_8b0a': ['%1 = tail call i32 asm sideeffect "", "={x11},~{memory}"() #2', '%2 = shl i32 %1, 16', '%3 = tail call i32 asm sideeffect "", "={x10},{x11},{x10},~{memory}"(i32 %1, i32 %2) #2', '%4 = lshr i32 %3, 16', 'tail call void asm sideeffect ".Ltransport_copy_more:\\0Abltu a0, s0, .Ltransport_copy_more\\0A.reloc .-4, R_RISCV_BRANCH, tsl9_transport_copy_8b52\\0A", "{x10},{x11},~{memory}"(i32 %4, i32 %1) #2', 'unreachable'], 'tsl9_transport_finish_8b14': ['%1 = tail call { i32, i32, i32, i32 } asm sideeffect "", "={x15},={x14},={x12},={x13},~{memory}"() #2', '%2 = extractvalue { i32, i32, i32, i32 } %1, 0', '%3 = extractvalue { i32, i32, i32, i32 } %1, 1', '%4 = extractvalue { i32, i32, i32, i32 } %1, 2', '%5 = extractvalue { i32, i32, i32, i32 } %1, 3', '%6 = tail call i32 asm sideeffect "add a5, a5, s0", "={x15},{x15},~{memory}"(i32 %2) #2', '%7 = trunc i32 %3 to i8', '%8 = add i32 %6, 5', '%9 = inttoptr i32 %8 to ptr', 'store volatile i8 %7, ptr %9, align 1', '%10 = tail call { i32, i32 } asm sideeffect "", "={x15},={x12},{x15},{x12},~{memory}"(i32 1062, i32 %4) #2', '%11 = extractvalue { i32, i32 } %10, 0', '%12 = extractvalue { i32, i32 } %10, 1', '%13 = mul i32 %12, %11', '%14 = tail call { i32, i32 } asm sideeffect "addi s0, s0, 6", "={x15},={x12},{x15},{x12},~{memory}"(i32 %13, i32 %12) #2', '%15 = extractvalue { i32, i32 } %14, 0', '%16 = extractvalue { i32, i32 } %14, 1', '%17 = shl i32 %16, 2', '%18 = tail call { i32, i32 } asm sideeffect "lw ra, 28(sp)\\0Alw s1, 20(sp)\\0Alw s2, 16(sp)\\0Alw s3, 12(sp)\\0A", "={x12},={x15},{x12},{x15},~{memory}"(i32 %17, i32 %15) #2', '%19 = extractvalue { i32, i32 } %18, 0', '%20 = extractvalue { i32, i32 } %18, 1', '%21 = tail call { i32, i32 } asm sideeffect "", "={x11},={x15},{x11},{x15},~{memory}"(i32 1, i32 %20) #2', '%22 = extractvalue { i32, i32 } %21, 0', '%23 = extractvalue { i32, i32 } %21, 1', '%24 = add i32 %23, %5', 'tail call void asm sideeffect "sh s0, 2(a5)", "{x15},~{memory}"(i32 %24) #2', '%25 = add i32 %24, 4', '%26 = inttoptr i32 %25 to ptr', 'store volatile i16 0, ptr %26, align 2', '%27 = tail call i32 asm sideeffect "addi a5, gp, 148\\0A", "={x15},{x12},{x11},~{memory}"(i32 %19, i32 %22) #2', '%28 = add i32 %27, %19', '%29 = tail call { i32, i32 } asm sideeffect "lw s0, 24(sp)\\0Alui a5, 0x40\\0Alw t1, 80(a5)\\0A", "={x12},={x15},{x11},{x12},~{memory}"(i32 %22, i32 %28) #2', '%30 = extractvalue { i32, i32 } %29, 0', '%31 = extractvalue { i32, i32 } %29, 1', '%32 = inttoptr i32 %30 to ptr', '%33 = load volatile i8, ptr %32, align 1', '%34 = zext i8 %33 to i32', 'tail call void asm sideeffect "addi sp, sp, 32\\0Ajr t1\\0A", "{x10},{x12},{x11},{x15},~{memory}"(i32 %34, i32 %30, i32 %22, i32 %31) #2', 'unreachable'], 'tsl9_transport_copy_8b52': ['%1 = tail call { i32, i32, i32 } asm sideeffect "", "={x11},={x15},={x14},~{memory}"() #2', '%2 = extractvalue { i32, i32, i32 } %1, 0', '%3 = extractvalue { i32, i32, i32 } %1, 1', '%4 = extractvalue { i32, i32, i32 } %1, 2', '%5 = tail call i32 asm sideeffect "add a0, s1, a1", "={x10},{x11},~{memory}"(i32 %2) #2', '%6 = tail call i32 asm sideeffect "", "={x10},{x11},{x15},{x14},{x10},~{memory}"(i32 %2, i32 %3, i32 %4, i32 %5) #2', '%7 = inttoptr i32 %6 to ptr', '%8 = load volatile i8, ptr %7, align 1', '%9 = zext i8 %8 to i32', '%10 = add i32 %3, %2', '%11 = tail call { i32, i32, i32 } asm sideeffect "", "={x16},={x10},={x11},{x15},{x14},{x16},{x10},{x11},~{memory}"(i32 %3, i32 %4, i32 %10, i32 %9, i32 %2) #2', '%12 = extractvalue { i32, i32, i32 } %11, 0', '%13 = extractvalue { i32, i32, i32 } %11, 1', '%14 = extractvalue { i32, i32, i32 } %11, 2', '%15 = add i32 %14, 1', '%16 = tail call { i32, i32, i32 } asm sideeffect "", "={x11},={x10},={x14},{x16},{x11},{x10},{x14},~{memory}"(i32 %12, i32 %15, i32 %13, i32 %4) #2', '%17 = extractvalue { i32, i32, i32 } %16, 0', '%18 = extractvalue { i32, i32, i32 } %16, 1', '%19 = extractvalue { i32, i32, i32 } %16, 2', '%20 = add i32 %19, %18', '%21 = tail call { i32, i32 } asm sideeffect "", "={x14},={x10},{x16},{x11},{x14},{x10},~{memory}"(i32 %12, i32 %17, i32 %20, i32 %18) #2', '%22 = extractvalue { i32, i32 } %21, 0', '%23 = extractvalue { i32, i32 } %21, 1', '%24 = trunc i32 %23 to i8', '%25 = add i32 %12, 5', '%26 = inttoptr i32 %25 to ptr', 'store volatile i8 %24, ptr %26, align 1', '%27 = tail call { i32, i32, i32, i32 } asm sideeffect "", "={x14},={x11},={x10},={x16},{x14},{x11},{x10},{x16},~{memory}"(i32 %22, i32 %17, i32 %23, i32 %12) #2', '%28 = extractvalue { i32, i32, i32, i32 } %27, 0', '%29 = extractvalue { i32, i32, i32, i32 } %27, 1', '%30 = extractvalue { i32, i32, i32, i32 } %27, 2', '%31 = extractvalue { i32, i32, i32, i32 } %27, 3', '%32 = and i32 %28, 255', 'tail call void asm sideeffect ".Ltransport_copy_test:\\0Ac.j .Ltransport_copy_test\\0A.reloc .-2, R_RISCV_RVC_JUMP, tsl9_transport_test_8b0a\\0A", "{x14},{x11},{x10},{x16},~{memory}"(i32 %32, i32 %29, i32 %30, i32 %31) #2', 'unreachable'], 'tsl9_transport_bare_return_8b6c': ['tail call void asm sideeffect "ret\\0A", ""() #2', 'unreachable']}


def need(ok,message):
    if not ok:raise ValueError(message)


def sha(data):return hashlib.sha256(data).hexdigest()


def digest(path):return sha(Path(path).read_bytes())


def sx(n,b):return n-(1<<b) if n&(1<<(b-1)) else n

need(digest(READER)==PINS[READER],'frozen ELF reader')
_reader=runpy.run_path(str(READER));ELF,portable=_reader['ELF'],_reader['portable']


def decode(code):
    """Static RV32IMAC/Zicsr bit decoding, not instruction execution."""
    rows=[];at=0
    while at<len(code):
        need(at+2<=len(code),'instruction extent');w=int.from_bytes(code[at:at+2],'little');size=4 if w&3==3 else 2
        need(at+size<=len(code),'wide instruction extent')
        if size==4:
            w=int.from_bytes(code[at:at+4],'little');op=w&127;rd=(w>>7)&31;rs=(w>>15)&31;rs2=(w>>20)&31;f3=(w>>12)&7
            if op in (0x37,0x17):ins=['LUI' if op==0x37 else 'AUIPC',rd,w&0xfffff000]
            elif op==0x13 and f3 in (1,5) and w>>25==0:ins=['SLLI' if f3==1 else 'SRLI',rd,rs,(w>>20)&31]
            elif op==0x13 and f3 in (4,7):ins=['XORI' if f3==4 else 'ANDI',rd,rs,sx(w>>20,12)]
            elif op==0x13 and f3==0:ins=['ADDI',rd,rs,sx(w>>20,12)]
            elif op==3 and f3 in (2,4,5):ins=[{2:'LW32',4:'LBU8',5:'LHU16'}[f3],rd,rs,sx(w>>20,12)]
            elif op==0x23 and f3 in (0,1,2):
                offset=((w>>25)<<5)|((w>>7)&31);ins=[{0:'SB8',1:'SH16',2:'SW32'}[f3],rs2,rs,sx(offset,12)]
            elif op==0x33 and f3==0 and w>>25 in (0,1):ins=['MUL' if w>>25==1 else 'ADD',rd,rs,rs2]
            elif op==0x73 and f3 in (2,3):ins=['CSRRS' if f3==2 else 'CSRRC',rd,w>>20,rs]
            elif op==0x63 and f3 in (0,1,6):
                imm=((w>>31)<<12)|(((w>>7)&1)<<11)|(((w>>25)&63)<<5)|(((w>>8)&15)<<1)
                ins=[{0:'BEQ',1:'BNE',6:'BLTU'}[f3],rs,rs2,BASE+at+sx(imm,13)]
            elif op==0x6f:
                imm=((w>>31)<<20)|(((w>>21)&1023)<<1)|(((w>>20)&1)<<11)|(((w>>12)&255)<<12)
                ins=['JAL',rd,BASE+at+sx(imm,21)]
            else:raise ValueError('wide opcode/width outside exact bounded transport instruction families')
        else:
            q=w&3;f3=w>>13;rd=(w>>7)&31;rs2=(w>>2)&31;imm=sx((((w>>12)&1)<<5)|((w>>2)&31),6)
            if q==0 and f3==0:
                n=(((w>>11)&3)<<4)|(((w>>7)&15)<<6)|(((w>>6)&1)<<2)|(((w>>5)&1)<<3)
                need(n!=0,'valid ADDI4SPN');ins=['ADDI',8+((w>>2)&7),2,n]
            elif q==0 and f3==2:
                n=(((w>>10)&7)<<3)|(((w>>6)&1)<<2)|(((w>>5)&1)<<6)
                ins=['LW32',8+((w>>2)&7),8+((w>>7)&7),n]
            elif q==2 and f3==6:
                n=(((w>>9)&15)<<2)|(((w>>7)&3)<<6);ins=['SW32',rs2,2,n]
            elif q==2 and f3==2:
                n=(((w>>12)&1)<<5)|(((w>>4)&7)<<2)|(((w>>2)&3)<<6)
                need(rd!=0,'valid LWSP');ins=['LW32',rd,2,n]
            elif q==1 and f3 in (0,2):ins=['ADDI',rd,rd if f3==0 else 0,imm]
            elif q==1 and f3==3 and rd==2:
                n=(((w>>12)&1)<<9)|(((w>>6)&1)<<4)|(((w>>5)&1)<<6)|(((w>>3)&3)<<7)|(((w>>2)&1)<<5)
                ins=['ADDI',2,2,sx(n,10)]
            elif q==1 and f3==3 and rd not in (0,2):ins=['LUI',rd,(imm<<12)&0xffffffff]
            elif q==1 and f3==4 and ((w>>10)&3)==3 and not (w>>12)&1 and ((w>>5)&3)==2:
                rs=8+((w>>7)&7);ins=['OR',rs,rs,8+((w>>2)&7)]
            elif q==2 and f3==0:
                need(not (w>>12)&1,'RV32 SLLI range');ins=['SLLI',rd,rd,(w>>2)&31]
            elif q==1 and f3==4 and ((w>>10)&3) in (0,2):
                rs=8+((w>>7)&7)
                if ((w>>10)&3)==0:need(not (w>>12)&1,'RV32 SRLI range');ins=['SRLI',rs,rs,(w>>2)&31]
                else:ins=['ANDI',rs,rs,imm]
            elif w==0x8082:ins=['RET',1]
            elif q==2 and f3==4 and not (w>>12)&1 and rd and not rs2:ins=['JR',rd]
            elif q==2 and f3==4 and (w>>12)&1 and rd and not rs2:ins=['JALR',1,rd,0]
            elif q==2 and f3==4 and not (w>>12)&1 and rd and rs2:ins=['MV',rd,rs2]
            elif q==2 and f3==4 and (w>>12)&1 and rd and rs2:ins=['ADD',rd,rd,rs2]
            elif q==1 and f3 in (6,7):
                n=(((w>>12)&1)<<8)|(((w>>10)&3)<<3)|(((w>>5)&3)<<6)|(((w>>3)&3)<<1)|(((w>>2)&1)<<5)
                ins=['BEQZ' if f3==6 else 'BNEZ',8+((w>>7)&7),BASE+at+sx(n,9)]
            elif q==1 and f3 in (1,5):
                n=(((w>>12)&1)<<11)|(((w>>11)&1)<<4)|(((w>>9)&3)<<8)|(((w>>8)&1)<<10)|(((w>>7)&1)<<6)|(((w>>6)&1)<<7)|(((w>>3)&7)<<1)|(((w>>2)&1)<<5)
                ins=['JAL',1,BASE+at+sx(n,12)] if f3==1 else ['J',BASE+at+sx(n,12)]
            else:raise ValueError('compressed opcode/width outside exact bounded transport families')
        rows.append([at,size]+ins);at+=size
    return rows


def metadata(e):
    spans=[(s['offset'],s['offset']+s['size']) for s in e.sections if s['flags']&2 and s['size']]
    outside=bytes(v for i,v in enumerate(e.raw) if not any(a<=i<b for a,b in spans))
    return dict(header=e.header,program_headers=e.program_headers,sections=e.sections,symbols=e.symbols,
       relocations=e.relocations,noncode_section_hashes={s['name']:sha(e.data(s)) for s in e.sections if not s['flags']&2 and s['type']!=8},
       outside_allocated_code_sha256=sha(outside))


def core_ir(text):
    result={}
    for name,body in re.findall(r'^define .*?@([^ (]+)\([^\n]*\{\n(.*?)^\}',text,re.M|re.S):
        result[name]=[re.sub(r', !(?:tbaa|srcloc) !\d+','',line.strip()) for line in body.splitlines() if line.strip()]
    return result


def md_contract(text,llvm,out):
    text=text.replace('\\\n',' ').replace('\\\r\n',' ').replace('\\ ','\x01').replace('\\','/')
    target=str(out/'native.o').replace('\\','/');need(text.startswith(target+':'),'MD exact output target')
    deps=[s.replace('\x01',' ') for s in text[len(target)+1:].split()]
    want=[str(SOURCE).replace('\\','/'),str(llvm.parent/'lib/clang/18/include/stdint.h').replace('\\','/')]
    need(deps==want,'complete exact source/header MD closure');return portable(want,ROOT,llvm)


def typed_contract(rows,pending):
    expected=copy.deepcopy(EXPECTED)
    if pending:
        for row in expected:
            if row[0] in {r[0] for r in RELATIONS}:row[-1]=BASE+row[0]
    need(rows==expected,'all96 original widths/physical operands/order/cold CFG targets')
    at={r[0]:r for r in rows}
    need(at[0]==[0,4,'ADDI',15,0,1039] and at[4][2:5]==['BLTU',15,13] and at[278]==[278,2,'RET',1],
         'initial A3 guard before frame/calls and inherited A0 on bare return')
    need([at[p] for p in (180,184,186)]==[[180,4,'SLLI',10,11,16],[184,2,'SRLI',10,10,16],
         [186,4,'BLTU',10,8,BASE+186 if pending else BASE+252]],'only the comparison temporary is narrowed to uint16')
    need([at[p] for p in (252,256,260,264)]==[[252,4,'ADD',10,9,11],[256,4,'LBU8',10,10,0],
         [260,4,'ADD',16,15,11],[264,2,'ADDI',11,11,1]],'cold source/destination use full32 A1, increment modulo32')
    need(at[268]==[268,4,'SB8',10,16,5] and at[272]==[272,4,'ANDI',14,14,255],
         'fresh payload byte store and byte-masked running checksum')
    need([at[p] for p in (44,48,52,56,80,84,88,92,94)]==
         [[44,4,'LUI',15,0x40000],[48,4,'LW32',15,15,316],[52,4,'ADDI',11,3,128],[56,2,'JALR',1,15,0],
          [80,4,'LUI',15,0x40000],[84,4,'LW32',15,15,316],[88,4,'ADDI',11,3,128],[92,2,'MV',10,18],[94,2,'JALR',1,15,0]],
         'two fresh admission pointer loads, then-live GP/S2 and actual RA calls')
    need([at[p] for p in (208,210,212,214,234,236,240,244,248,250)]==
         [[208,2,'LW32',1,2,28],[210,2,'LW32',9,2,20],[212,2,'LW32',18,2,16],[214,2,'LW32',19,2,12],
          [234,2,'LW32',8,2,24],[236,4,'LUI',15,0x40000],[240,4,'LW32',6,15,80],[244,4,'LBU8',10,12,0],
          [248,2,'ADDI',2,2,32],[250,2,'JR',6]],'RA and saved-register restore ordering, late S0, no-link tail through T1')
    need(not any(r[2] in ('ADDI','ADD','MV','LW32','LBU8','SLLI','SRLI','XORI','ANDI','MUL','AUIPC','LUI') and r[3]==16 for r in rows if r[0]<252),
         'A6 remains inherited on zero-copy path; only cold copy writes it')
    return rows


def cfg_contract(rows,pending=False):
    """One static record per instruction; opaque targets remain unknown."""
    typed_contract(rows,pending);result=[]
    for row in rows:
        at,width,op,*args=row;pc=BASE+at;following=pc+width
        item=dict(PC=pc,width=width,operation=op)
        if op in ('BEQ','BNE','BLTU','BEQZ','BNEZ'):
            item.update(kind='conditional',target=args[-1],fallthrough=following)
        elif op=='J':item.update(kind='direct_no_link',target=args[-1])
        elif op=='JALR':item.update(kind='opaque_admission_call',link_rd=args[0],target='fresh LW32[0x%X]'%ADMISSION_CELL,RA_continuation=following)
        elif op=='JR':item.update(kind='opaque_tail',link_rd=0,target='fresh LW32[0x%X]'%TAIL_CELL,RA_continuation=None)
        elif op=='RET':item.update(kind='return',target='then-live RA',RA_continuation=None)
        else:item.update(kind='linear',fallthrough=following)
        result.append(item)
    need(len(result)==96 and sum(z['kind']=='conditional' for z in result)==8 and
         sum(z['kind']=='direct_no_link' for z in result)==1 and sum(z['kind']=='opaque_admission_call' for z in result)==2 and
         sum(z['kind']=='opaque_tail' for z in result)==1 and sum(z['kind']=='return' for z in result)==2,'complete bounded CFG coverage')
    return result


def original():
    raw=FIRMWARE.read_bytes();need(len(raw)==76800 and sha(raw)==PINS[FIRMWARE],'whole original BIN identity')
    code=raw[BASE-0x8000:BASE-0x8000+280];need(sha(code)==ORIGINAL_PIN,'original280B span identity')
    rows=decode(code);typed_contract(rows,False);cfg_contract(rows)
    need(digest(DECODE)==PINS[DECODE],'pinned independent static decode')
    evidence=json.loads(DECODE.read_bytes());recorded=evidence['rows']
    need((int(evidence['start'],0),int(evidence['end_exclusive'],0),evidence['bytes'],evidence['instructions'],evidence['span_sha256'])==
         (BASE,BASE+280,280,96,ORIGINAL_PIN) and int(evidence['mapping_base'],0)==0x8000 and evidence['firmware_sha256']==PINS[FIRMWARE],
         'decode bounds/identity')
    need(b''.join(bytes.fromhex(r['bytes']) for r in recorded)==code and
         [(r['addr']-BASE,r['size']) for r in recorded]==[(r[0],r[1]) for r in EXPECTED],'complete original decode coverage')
    return code


def masks():
    result=bytearray(b'\xff'*280)
    for at,kind,_ in RELATIONS:
        n,mask=MASKS[kind];result[at:at+n]=mask.to_bytes(n,'little')
    return result


def elf_contract(e,native,official,full=True):
    need(bool(ELF_PINS) and bool(SCHEMAS),'candidate native/partial measurements not bound')
    schema=SCHEMAS['native' if native else 'partial']
    need(len(e.raw)==schema['header'][5]+40*schema['header'][11],'complete ELF extent without unbound trailing bytes')
    need(e.header[0]==1 and e.header[6]==1 and not e.program_headers,'RV32 RVC ET_REL only; not an executable firmware')
    gs=[s for s in e.symbols if s['info']>>4]
    expected={n:(0 if native else at,z,18,0,'.text.'+n if native else '.transport') for n,at,z in REGIONS}
    actual={s['name']:(s['value'],s['size'],s['info'],s['other'],e.sections[s['section']]['name']) for s in gs if s['section'] not in (0,65521)}
    need(actual==expected and len(gs)==13,'13 genuine FUNCs in exact region order/ownership/extent')
    need(not any(s['section'] in (0,65521) for s in gs),'no UND/ABS/fake/weak providers; indirect calls remain unknown')
    alloc=[s for s in e.sections if s['flags']&2 and s['size']]
    need([(s['name'],s['address'],s['size'],s['type'],s['flags'],s['align']) for s in alloc]==
       ([('.text.'+n,0,z,1,6,2) for n,_,z in REGIONS] if native else [('.transport',0,280,1,6,2)]),'exact AX-only allocation')
    code=b''.join(e.data('.text.'+n) for n in NAMES) if native else e.data('.transport')
    rows=typed_contract(decode(code),True);need(len(code)==280 and len(rows)==96,'280B96i')
    cfg=cfg_contract(rows,True);starts={'.text.'+n:at for n,at,_ in REGIONS};rels=[]
    for r in e.relocations:
        owner=e.sections[r['section']]['name'];symbol=e.symbols[r['symbol']]
        need(owner in starts if native else owner=='.transport','genuine relocation owner')
        offset=r['offset']+(starts[owner] if native else 0);rels.append((offset,r['type'],symbol['name'],r['addend']))
        need(symbol['info']==18 and symbol['section'] not in (0,65521),'genuine defined architectural control target')
    need(rels==[(a,k,n,0) for a,k,n in RELATIONS],'all nine genuine relocation offsets/types/targets/addends')
    bitmasks=masks();need(all(not ((a^b)&mask) for a,b,mask in zip(code,official,bitmasks)),
         'all original nonrelocation bits, physical rd/rs operands and no-link jump opcode')
    need(metadata(e)==schema,'complete actual ELF metadata/noncode/gap bytes')
    if full:need(sha(e.raw)==ELF_PINS[native],'whole measured ELF pin')
    controls=[];original_rows={r[0]:r for r in EXPECTED}
    for at,kind,name in RELATIONS:
        row=original_rows[at];controls.append(dict(offset=at,kind=kind,target_symbol=name,nominal_PC=BASE+at,
            nominal_target=row[-1],pending_machine_target=BASE+at,link_rd=0,
            fallthrough=BASE+at+row[1] if kind==16 else None))
    return dict(sha256=sha(e.raw),header=e.header,program_headers=e.program_headers,sections=e.sections,
       symbols=e.symbols,relocations=e.relocations,code_hex=code.hex(),code_sha256=sha(code),typed_rows=rows,cfg=cfg,
       cfg_coordinates='original nominal BASE plus joined source-span offset; unresolved ET_REL is not installed at these VAs',
       UND_providers=[],ABS_providers=[],local_ABS_metadata=sum(s['section']==65521 and not s['info']>>4 for s in e.symbols),
       controls=controls,retained_nonrelocation_bits=sum(n.bit_count() for n in bitmasks),
       fully_unmasked_bytes=sum(n==255 for n in bitmasks),whole_nonrelocation_instruction_bytes=246,
       pending_machine_immediates=9,defined_relocation_sites=9,unknown_admission_calls=2,unknown_tail_calls=1,firmware_ready=False)


def elf_negatives(native,partial,official):
    results=[]
    def check(name,scope,fn):
        try:fn()
        except (ValueError,IndexError,KeyError) as exc:results.append(dict(name=name,scope=scope,rejected=True,
             whole_ELF_hash_enabled=False,whole_IR_hash_enabled=False,reason=str(exc)))
        else:raise ValueError('negative accepted '+name)
    def raw(name,e,n,position,fmt,value):
        b=bytearray(e.raw);struct.pack_into(fmt,b,position,value)
        check(name,'raw_ELF_reparsed',lambda:elf_contract(ELF(b),n,official,False))
    for e,n in [(native,True),(partial,False)]:
        tag='native' if n else 'partial';symtab=next(s for s in e.sections if s['type']==2)
        gs={s['name']:s for s in e.symbols if s['info']>>4}
        for name in [NAMES[0],NAMES[8],NAMES[11],NAMES[12]]:
            at=symtab['offset']+gs[name]['index']*16
            raw(tag+'_fakeABS_'+name,e,n,at+14,'<H',65521)
            raw(tag+'_fakeUND_'+name,e,n,at+14,'<H',0)
            raw(tag+'_weak_'+name,e,n,at+12,'<B',34)
        at=symtab['offset']+gs[NAMES[10]]['index']*16
        raw(tag+'_FUNC_size',e,n,at+8,'<I',60);raw(tag+'_FUNC_value',e,n,at+4,'<I',2)
        sec=next(s for s in e.sections if s['flags']&2 and s['size'])
        raw(tag+'_writable_code',e,n,e.header[5]+40*sec['index']+8,'<I',7)
        check(tag+'_trailing_bytes','raw_ELF_reparsed',lambda ee=e,nn=n:elf_contract(ELF(ee.raw+b'\0\0'),nn,official,False))
        for i,r in enumerate(e.relocations):
            table=next(s for s in e.sections if s['type']==4 and s['info']==r['section'])
            previous=sum(z['section']==r['section'] for z in e.relocations[:i]);at=table['offset']+12*previous
            raw(tag+'_RELA_addend_'+str(i),e,n,at+8,'<i',2)
            raw(tag+'_RELA_family_'+str(i),e,n,at+4,'<I',(r['symbol']<<8)|(45 if r['type']==16 else 16))
            raw(tag+'_RELA_target_'+str(i),e,n,at+4,'<I',(gs[NAMES[0]]['index']<<8)|r['type'])
        def offset(pc):
            region=next((name,a,z) for name,a,z in REGIONS if a<=pc<a+z)
            return e.section('.text.'+region[0])['offset']+pc-region[1] if n else e.section('.transport')['offset']+pc
        for name,pc,delta,xor in [('initial_limit1039',0,2,16),('unsigned_guard_A3',4,2,16),('SP_frame32',8,0,4),
            ('save_RA_slot',18,0,4),('first_GP150',20,2,16),('input_S0_length',26,0,4),('input_S1_source',28,0,4),
            ('first_id_compare',32,2,16),('first_sentinel',38,0,4),('fresh_admission1_offset',48,2,16),
            ('admission1_GP_context',52,2,16),('admission1_as_no_link_JR',56,1,16),('first_result_one',58,0,4),
            ('second_GP154',64,2,16),('thenlive_S2_compare',68,2,16),('second_sentinel',74,0,4),
            ('fresh_admission2_offset',84,2,16),('admission2_GP_context',88,2,16),('thenlive_S2_arg',92,0,4),
            ('admission2_as_no_link_JR',94,1,16),('selected_bank1',98,0,4),('failure_RA_slot',104,0,4),
            ('failure_SP32',114,0,4),('failure_RET',116,0,4),('selected_bank0',118,0,4),('stride1062',120,2,16),
            ('MUL_bank_order',124,2,16),('nominal_AUIPC',128,2,16),('header_magic_XOR',138,2,16),
            ('postcall_length_low_S0',142,2,8),('header_halfword_width',150,1,16),('header_low_byte4',154,0,128),
            ('postcall_length_high_S0',158,2,8),('postcall_command_S3',162,0,4),('header_high_byte3',164,0,128),
            ('command_byte2',170,2,16),('header_checksum_mask',174,2,16),('comparison_clobbers_full_A1',180,0,128),
            ('narrow_compare_shift16',184,0,4),('postcall_length_compare_S0',186,2,8),('checksum_position_S0',190,0,4),
            ('trailing_checksum_byte5',192,0,128),('finish_stride1062',196,2,16),('total_length_add6',204,0,4),
            ('context_bank_shift2',206,0,4),('success_RA_restore',208,0,4),('metadata_total_word',220,1,16),
            ('metadata_zero_word',224,1,16),('late_S0_restore',234,0,4),('tail_cell80',240,2,16),
            ('tail_context_fresh_byte',244,1,16),('tail_SP32',248,0,4),('tail_JR_incorrectly_links',250,1,16),
            ('source_address_narrowed_index',252,2,16),('payload_fresh_byte_width',256,1,16),
            ('destination_address_wrong_index',260,2,16),('full_counter_increment',264,0,4),('running_checksum_source',266,0,4),
            ('payload_store_byte5',268,0,128),('running_checksum_mask',272,2,16),('cold_jump_links',276,1,128),('bare_RET',278,0,4)]:
            at=offset(pc)+delta;raw(tag+'_'+name,e,n,at,'<B',e.raw[at]^xor)
        # Reproduce the specific 0x4013C versus 0x40013C scale error.
        for pc in (44,80):
            at=offset(pc);word=int.from_bytes(e.raw[at:at+4],'little')
            raw(tag+'_admission_address_scale_'+str(pc),e,n,at,'<I',(word&0xfff)|0x400000)
        b=bytearray(e.raw);a=offset(208);z=offset(220);b[a:a+2],b[z:z+2]=b[z:z+2],b[a:a+2]
        check(tag+'_RA_restore_after_metadata','raw_ELF_reparsed',lambda bb=b,nn=n:elf_contract(ELF(bb),nn,official,False))
    rowmap={r[0]:i for i,r in enumerate(EXPECTED)}
    for name,pc,field,value in [('parsed_initial_guard_signed',4,2,'BLT'),('parsed_postcall_S0',142,4,9),
       ('parsed_uint16_counter_clobbers_A1',180,3,11),('parsed_full_source_index',252,5,10),
       ('parsed_full_destination_index',260,5,10),('parsed_tail_links',250,2,'JALR'),
       ('parsed_tail_uses_synthetic_RA',208,3,5),('parsed_second_arg_stale',92,4,17),('parsed_wrong_admission_cell',44,4,0x400000)]:
        changed=copy.deepcopy(EXPECTED);changed[rowmap[pc]][field]=value
        check(name,'parsed_typed_rows',lambda c=changed:typed_contract(c,False))
    changed=copy.deepcopy(EXPECTED);changed.insert(rowmap[120],[120,4,'BLTU',15,8,BASE+104])
    check('parsed_added_postcall_length_guard','parsed_typed_rows',lambda:typed_contract(changed,False))
    changed=copy.deepcopy(EXPECTED);changed.insert(rowmap[120],[120,2,'ADDI',16,0,0])
    check('parsed_zero_copy_clobbers_A6','parsed_typed_rows',lambda:typed_contract(changed,False))
    return results


def ir_contract(text,language,full=True):
    normalized='\n'.join(text.splitlines()[2:])+'\n';core=core_ir(normalized)
    need(list(core)==NAMES and core==IR_CORE,'all literal SSA/constants/fresh physical ports in complete13-region order')
    need(len(re.findall(r'load volatile i32',normalized))==2 and len(re.findall(r'load volatile i8',normalized))==2,
         'two fresh C admission word loads and two C byte loads')
    need(len(re.findall(r'store volatile i16',normalized))==2 and len(re.findall(r'store volatile i8',normalized))==4,
         'actual C subset: two halfword/four byte stores; S-register stores stay explicit ports')
    need(normalized.count('(i32 262144)')==2 and len(re.findall(r'add i32 %\d+, 316',normalized))==2,
         'admission cells derive from0x40000+316=0x4013C, not0x40013C')
    need('%2 = shl i32 %1, 16' in '\n'.join(core[NAMES[9]]) and '%4 = lshr i32 %3, 16' in '\n'.join(core[NAMES[9]]),
         'C uint16 comparison temporary leaves full32 A1 physical counter untouched')
    copy_core='\n'.join(core[NAMES[11]])
    need('add a0, s1, a1' in copy_core and '%10 = add i32 %3, %2' in copy_core and '%15 = add i32 %14, 1' in copy_core,
         'cold source/destination addresses and increment use full32 index')
    need('%12 = xor i32 %10, -171' in '\n'.join(core[NAMES[8]]) and '%58 = and i32 %55, 255' in '\n'.join(core[NAMES[8]]) and
         '%32 = and i32 %28, 255' in copy_core,'real C magic XOR and header/running checksum masks')
    need(normalized.count('i32 1039')==1 and normalized.count('jalr a5\\0A')==2 and normalized.count('jr t1\\0A')==1 and normalized.count('ret\\0A')==2,
         'initial guard only, two opaque RA admissions, no-link tail and two actual RET exits')
    need(not re.search(r'\balloca\b|\b(?:undef|poison)\b|\.4byte|\.word|\.insn|mret|csrr|csrw',normalized),
         'no compiler frame/spill, opcode carriers or added privileged operations')
    if full:need(sha(normalized.encode())==IR_PINS[language],'complete normalized IR including attributes/TBAA/srcloc metadata')
    return dict(normalized_sha256=sha(normalized.encode()),core_SSA=core,C_volatile_word_reads=2,C_volatile_byte_reads=2,
       C_halfword_stores=2,C_byte_stores=4,physical_S_register_ports=True,ordinary_C_ABI_proven=False)


def ir_md_negatives(text,language,md,llvm,out):
    results=[]
    def check(name,scope,fn,full=False):
        try:fn()
        except (ValueError,IndexError,KeyError) as exc:results.append(dict(name=name,scope=scope,rejected=True,
             whole_ELF_hash_enabled=False,whole_IR_hash_enabled=full,reason=str(exc)))
        else:raise ValueError('negative accepted '+name)
    mutations=[('IR_guard_limit','i32 1039','i32 1040'),('IR_guard_signed','bltu a5, a3','blt a5, a3'),
       ('IR_admission_cell_scale','(i32 262144)','(i32 4194304)'),('IR_admission_offset','%2 = add i32 %1, 316','%2 = add i32 %1, 312'),
       ('IR_admission_cached','load volatile i32','load i32'),('IR_admission_width','load volatile i32','load volatile i16'),
       ('IR_GP_context','addi a1, gp, 128','addi a1, gp, 124'),('IR_second_live_S2','mv a0, s2','mv a0, s3'),
       ('IR_frame32','addi sp, sp, -32','addi sp, sp, -48'),('IR_reject_RA','lw ra, 28(sp)','lw ra, 24(sp)'),
       ('IR_stride1062','i32 1062','i32 1060'),('IR_header_magic','%12 = xor i32 %10, -171','%12 = xor i32 %10, -170'),
       ('IR_live_S0_low','andi a1, s0, 255','andi a1, s1, 255'),('IR_live_S0_high','srli a4, s0, 8','srli a4, s1, 8'),
       ('IR_live_S3_command','add a1, a1, s3','add a1, a1, s2'),('IR_command_store','sb s3, 2(a5)','sb s2, 2(a5)'),
       ('IR_compare_width','%2 = shl i32 %1, 16','%2 = shl i32 %1, 15'),('IR_compare_live_S0','bltu a0, s0','bltu a0, s1'),
       ('IR_full_source_index','add a0, s1, a1','add a0, s1, a0'),('IR_full_dest_index','%10 = add i32 %3, %2','%10 = add i32 %3, %9'),
       ('IR_full_counter_increment','%15 = add i32 %14, 1','%15 = add i32 %14, 2'),('IR_payload_cached','load volatile i8','load i8'),
       ('IR_payload_address_offset','%25 = add i32 %12, 5','%25 = add i32 %12, 4'),('IR_checksum_mask','%32 = and i32 %28, 255','%32 = and i32 %28, 127'),
       ('IR_finish_live_S0','add a5, a5, s0','add a5, a5, s1'),('IR_total_length_add6','addi s0, s0, 6','addi s0, s0, 5'),
       ('IR_metadata_word','sh s0, 2(a5)','sb s0, 2(a5)'),('IR_context_GP148','addi a5, gp, 148','addi a5, gp, 144'),
       ('IR_tail_cell80','lw t1, 80(a5)','lw t1, 84(a5)'),('IR_tail_incorrectly_links','jr t1','jalr t1'),
       ('IR_tail_SP32','addi sp, sp, 32\\0Ajr t1','addi sp, sp, 16\\0Ajr t1')]
    for name,old,new in mutations:
        need(old in text,'real IR negative fixture '+name);changed=text.replace(old,new,1)
        check(name,'IR_text_structural_SSA',lambda c=changed:ir_contract(c,language,False))
    for name,old,new in [('IR_full_attributes','generic-rv32','other-rv32'),('IR_full_metadata','!"wchar_size"','!"other"')]:
        need(old in text,'real complete IR fixture');changed=text.replace(old,new,1)
        check(name,'IR_text_full_normalized_pin',lambda c=changed:ir_contract(c,language,True),True)
    for name,changed in [('MD_target',md.replace('native.o:','other.o:',1)),('MD_missing_header',' '.join(md.splitlines()[:-1])),('MD_extra',md+'\nextra.h\n')]:
        check(name,'MD_text',lambda c=changed:md_contract(c,llvm,out))
    return results


def inputs(llvm):
    need(SOURCE in PINS and bool(ELF_PINS) and bool(IR_PINS),'candidate freeze must be bound before any formal result')
    expected=dict(PINS);expected[Path(__file__).resolve()]=digest(__file__)
    expected[llvm.parent/'lib/clang/18/include/stdint.h']=HEADER_PIN
    expected.update({llvm/n:pin for n,pin in TOOLS.items()})
    need(all(digest(p)==pin for p,pin in expected.items()),'all source/decode/reader/probe/linker/tool/header pins')
    for path in [SOURCE,HERE/'component.ld',HERE/'probe.py']:
        raw=path.read_bytes();need(b'\r' not in raw and raw.endswith(b'\n') and not raw.endswith(b'\n\n'),'frozen LF source/probe/linker have exactly one EOF LF')
    return expected


def recipes(llvm,out,language):
    f=runpy.run_path(str(HERE/'probe.py'))['flags'](language)
    need({int(s[9:]) for s in f if s.startswith('-ffixed-x')}==set(range(1,32))-set(range(10,17)) and '-march=rv32imac_zicsr' in f and '-Oz' in f,
         'unchanged fixed A0..A6 compiler profile; RA/SP/S-registers/T1 reserved')
    exe=lambda n:str(llvm/n);obj=str(out/'native.o');dump=['--mattr=+m,+a,+c,+zicsr','-d','-r','-t','-h']
    return [('compile',[exe('clang.exe'),*f,'-MD','-MF',str(out/'native.d'),'-MT',obj,'-c',str(SOURCE),'-o',obj]),
      ('IR',[exe('clang.exe'),*f,'-S','-emit-llvm',str(SOURCE),'-o',str(out/'native.ll')]),
      ('object',[exe('llvm-objdump.exe'),*dump,obj]),
      ('link',[exe('ld.lld.exe'),'-r','--no-relax','-T',str(HERE/'component.ld'),obj,'-o',str(out/'partial.o')]),
      ('partial',[exe('llvm-objdump.exe'),*dump,str(out/'partial.o')])]


def evaluate(root,llvm,out,language):
    need(root.resolve()==ROOT,'canonical project root');before=inputs(llvm);official=original()
    native=ELF(out/'native.o');partial=ELF(out/'partial.o')
    nf=elf_contract(native,True,official);pf=elf_contract(partial,False,official)
    need(nf['code_hex']==pf['code_hex'],'partial link preserves all actual native bytes')
    text=(out/'native.ll').read_text(encoding='utf-8');ir=ir_contract(text,language)
    md=(out/'native.d').read_text(encoding='utf-8');deps=md_contract(md,llvm,out)
    commands=[dict(label=n,argv=portable(a,ROOT,llvm),returncode=0) for n,a in recipes(llvm,out,language)]
    need(json.loads((out/'recipes.json').read_bytes())==json.loads(json.dumps(commands)),'exact five successful producer recipes')
    files=sorted(['native.o','partial.o','native.ll','native.d','recipes.json']+[n+'.log' for n,_ in recipes(llvm,out,language)])
    need(sorted(p.name for p in out.iterdir() if p.name!='verification.json')==files and all(p.is_file() and not p.is_symlink() for p in out.iterdir()),
         'complete exact output inventory')
    for name in ['compile','IR','link']:need(not (out/(name+'.log')).read_bytes(),'empty successful diagnostic '+name)
    for name,artifact in [('object','native.o'),('partial','partial.o')]:
        log=(out/(name+'.log')).read_text();need(str(out/artifact) in log and all(n in log for n in NAMES),'actual artifact/symbol dump binding')
    artifacts=[dict(path=portable(str(out/n),ROOT,llvm),size=(out/n).stat().st_size,sha256=digest(out/n)) for n in files]
    controls=elf_negatives(native,partial,official)+ir_md_negatives(text,language,md,llvm,out)
    need(before==inputs(llvm) and all(digest(out/Path(a['path']).name)==a['sha256'] for a in artifacts),'all read input/artifact bytes stable')
    record=dict(schema='TSL9-transport-frame-native-v6-formal-v1',language=language,firmware_ready=False,target_executed=False,ISA_emulated=False,
       inputs=[dict(path=portable(str(p),ROOT,llvm),size=p.stat().st_size,sha256=v) for p,v in before.items()],
       original=dict(base=0x8000,start=BASE,end=BASE+280,bytes=280,instructions=96,sha256=ORIGINAL_PIN,typed_rows=EXPECTED,
         cfg=cfg_contract(copy.deepcopy(EXPECTED))),native=nf,partial=pf,ir=ir,md_dependencies=deps,recipes=commands,artifacts=artifacts,negative_controls=controls,
       static_contract=dict(initial_unsigned_A3_guard=1039,postopaque_S0_guard=False,architectural_frame_bytes=32,
         admission_cell=ADMISSION_CELL,admission_calls=[dict(PC=BASE+p,RA_continuation=BASE+p+2,unknown_provider_ABI=True) for p in (56,94)],
         loop_comparison='uint16(A1) < uint32(then-live S0)',address_counter='full uint32 A1, increment modulo2^32',
         copy_addresses=['then-live S1+A1','A5+A1+5'],zero_copy_A6='inherited physical A6',stride=1062,magic_halfword=0x7f55,
         checksum='command+length-low+length-shift8+payload bytes, masked255',
         initial_AUIPC_PC=BASE+128,nominal_table_base=(BASE+128+0x20002000+1718)&0xffffffff,
         tail=dict(PC=BASE+250,target_cell=TAIL_CELL,link_rd=0,RA='restored from then-live SP+28',SP='then-live SP+32',A1=1),
         guard_return_A0='inherited',rejection_return_A0='inherited or last opaque admission residue',ordinary_C_ABI_proven=False),
       limitations=[
        'Thirteen FUNC symbols are private physical-register regions and fallthrough boundaries, not independent ordinary C ABI functions.',
        'Actual ET_REL bytes retain nine symbolic control immediates. Zero UND does not resolve two admission targets or the resident tail provider.',
        'Admission address is0x4013C from LUI0x40000+316;0x40013C is not the original operand-derived address.',
        'The initial1039 guard applies before opaque calls only. Then-live S0/S1/S2/S3/SP/GP and A6 may differ after them; no new bound or ordinary preservation contract is claimed.',
        'Only the comparison temporary is uint16. The address counter is full32; no termination, postcall payload bound or memory safety is established for arbitrary opaque-callee effects.',
        'Physical S-register operations are explicit architecture ports; arithmetic/volatile C is a subset, not a claim of portable C equivalence.',
        'Nominal AUIPC/table interpretation requires original placement. The partial ET_REL has VA0 and is not an installed image.',
        'No target/ISA/MMIO execution, full firmware BIN, OTA acceptance, complete IRQ/silicon ABI or successful flashing.'])
    record=json.loads(json.dumps(record,ensure_ascii=True))
    encoded=(json.dumps(record,sort_keys=True,indent=2,ensure_ascii=True)+'\n').encode()
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
    need(out.parent==HERE/'build/verified-v1' and out.name==language,'owned formal v1 transport output only')
    if not args.replay:
        need(not out.exists(),'fresh output only');before=inputs(llvm);out.mkdir(parents=True);commands=[]
        for label,argv in recipes(llvm,out,language):
            child=subprocess.run(argv,cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
            (out/(label+'.log')).write_bytes(child.stdout);commands.append(dict(label=label,argv=portable(argv,ROOT,llvm),returncode=child.returncode))
            need(child.returncode==0,'actual compiler/linker recipe failed '+label)
        (out/'recipes.json').write_bytes((json.dumps(commands,indent=2)+'\n').encode());need(before==inputs(llvm),'inputs stable across actual build')
    record,encoded=evaluate(ROOT,llvm,out,language)
    if args.replay:need(saved==record and receipt.read_bytes()==encoded.encode(),'complete saved record and canonical LF replay byte equality')
    else:(out/'verification.json').write_bytes(encoded.encode())
    print(json.dumps(dict(result='PASS',language=language,bytes=280,instructions=96,FUNCs=13,UND=0,retained_RELA=9,
       controls=len(record['negative_controls']),receipt_sha256=sha(encoded.encode()),firmware_ready=False)))
    if args.require_firmware_ready:
        print('REJECTED: unresolved indirect/private/silicon ABI and original placement; firmware_ready=false.',file=sys.stderr);return 1
    return 0


if __name__=='__main__':
    try:sys.exit(main())
    except (ValueError,OSError,KeyError,IndexError,StopIteration) as exc:
        print('FAIL: '+str(exc),file=sys.stderr);sys.exit(1)
