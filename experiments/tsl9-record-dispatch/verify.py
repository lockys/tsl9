#!/usr/bin/env python3
"""Bounded offline102B record-dispatch compiler/replay proof; no target execution."""
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
SOURCE=HERE/'src/record_dispatch.v2.c'
READER=ROOT/'experiments/tsl9-spi-transfer-leaf/verify.py'
FIRMWARE=ROOT/'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
DECODE=ROOT/'analysis/transport-frame-2026-10-23/next-provider-contract.json'
WINDOW=ROOT/'analysis/transport-frame-2026-10-23/next-provider.json'
PINS={READER:'8c8eb8e01b9fc30eb7150682aa8848e47fe4a1254c6f87b05e657244a11b6de8',
 FIRMWARE:'0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667',
 DECODE:'56031c4665154685e0617391647d6b21806ff95bc759901c410019db2f4c56af',
 WINDOW:'9dbe20f22d95848af10d09560e4d9eb34ed810a5057f35bced41a8656d354eb5',
 SOURCE:'6d90475b039233f5bea21aa3f7a3af3938f06e4c9ac4a293c1c5f43f6bc3cd1b',
 HERE/'probe.py':'a4c01d657fc0188c9f965affff5f8698232c4c71cd030cfcc35630666a53a2a2',
 HERE/'component.ld':'96163b2a7a9de7040b9d36bac23b158b17dbdc729a6f6e59426491bd0ce01dff'}
TOOLS={'clang.exe':'047dfde05acc6fcce5af669e25cd8d40b4f509b8842d151d6d8a43a1c6a35fd6',
 'ld.lld.exe':'fe7f55c0c78b3d87f33b905a3874e10e872ca7beef53a8199d7ff9ac6641ec3f',
 'llvm-objdump.exe':'de40d1188fe63ff373e1a5dd83a12e2cb4545ca3b314da16a476ecf072e5a0fa'}
HEADER_PIN='7ce5540d5fb6e8da9760928e76cbdd5ebef329d701ad598d30d8e6f9d5d78b34'
BASE=0x12a08
RESIDENT_CELL=0x40000+76
PERIPHERAL_BASE=0x40006000+1024
ORIGINAL_PIN='334494853a765e550af99f0e8dd95523efaf7cbb86d392e0340a5d5f004940c9'
NAMES=['tsl9_queue_external_12a08','tsl9_dispatch_status_12a14','tsl9_dispatch_ID_12a16',
 'tsl9_dispatch_query_12a20','tsl9_dispatch_tag_12a28','tsl9_dispatch_copy_12a2e',
 'tsl9_dispatch_peripheral_12a50','tsl9_dispatch_finish_12a5e','tsl9_dispatch_tagged_12a66']
REGIONS=list(zip(NAMES,[0,12,14,24,32,38,72,86,94],[12,2,10,8,6,34,14,8,8]))
UNDEFINED=['tsl9_queue_external_81aa','tsl9_dispatch_external_821e','tsl9_dispatch_external_18ca4','tsl9_dispatch_external_16b7c']
RELATIONS=[(8,17,UNDEFINED[0]),(12,44,NAMES[3]),(20,16,NAMES[7]),(26,17,UNDEFINED[1]),
 (30,44,NAMES[7]),(36,44,NAMES[8]),(82,17,UNDEFINED[2]),(96,17,UNDEFINED[3]),(100,45,NAMES[7])]
MASKS={16:(4,0x01fff07f),17:(4,0x00000fff),44:(2,0xe383),45:(2,0xe003)}
EXPECTED = [[0, 2, 'ADDI', 2, 2, -48], [2, 2, 'SW32', 8, 2, 40], [4, 2, 'SW32', 1, 2, 44], [6, 2, 'MV', 8, 10], [8, 4, 'JAL', 1, 33194], [12, 2, 'BNEZ', 10, 76320], [14, 4, 'LHU16', 14, 8, 0], [18, 2, 'ADDI', 15, 0, 1], [20, 4, 'BNE', 14, 15, 76382], [24, 2, 'ADDI', 10, 0, 0], [26, 4, 'JAL', 1, 33310], [30, 2, 'BEQZ', 10, 76382], [32, 4, 'LBU8', 15, 8, 11], [36, 2, 'BNEZ', 15, 76390], [38, 4, 'LHU16', 15, 8, 0], [42, 4, 'LBU8', 12, 8, 2], [46, 4, 'SH16', 0, 2, 20], [50, 2, 'SW32', 15, 2, 12], [52, 4, 'SB8', 12, 2, 22], [56, 4, 'LUI', 15, 262144], [60, 2, 'LW32', 15, 15, 76], [62, 4, 'ADDI', 11, 8, 3], [66, 4, 'ADDI', 10, 2, 23], [70, 2, 'JALR', 1, 15, 0], [72, 4, 'LUI', 10, 1073766400], [76, 2, 'ADDI', 11, 2, 12], [78, 4, 'ADDI', 10, 10, 1024], [82, 4, 'JAL', 1, 101540], [86, 2, 'LW32', 1, 2, 44], [88, 2, 'LW32', 8, 2, 40], [90, 2, 'ADDI', 2, 2, 48], [92, 2, 'RET', 1], [94, 2, 'MV', 10, 8], [96, 4, 'JAL', 1, 93052], [100, 2, 'J', 76382]]
ELF_PINS = {True: '10bd9009cbabec329a43cf2ab4c94d77bf465d8c219b37ad4bc18ba0f90fc913', False: '6692bce88ae9437f0932c0ace22c4c103f696733d3de8fe4cda19cc591ada58e'}
IR_PINS = {'c': '01a2dedd113626cb86a711e98a6df6a0fe6131ca929794f380c1997c4b1ab90f', 'cpp': 'f9d89a46b7f892296b92c682a85cfaa7c355c5182f59145fcab6676713e8a086'}
SCHEMAS = {'native': {'header': [1, 243, 1, 0, 0, 1496, 1, 52, 0, 0, 40, 24, 1], 'program_headers': [], 'sections': [{'name_offset': 0, 'type': 0, 'flags': 0, 'address': 0, 'offset': 0, 'size': 0, 'link': 0, 'info': 0, 'align': 0, 'entsize': 0, 'index': 0, 'name': ''}, {'name_offset': 206, 'type': 3, 'flags': 0, 'address': 0, 'offset': 901, 'size': 593, 'link': 0, 'info': 0, 'align': 1, 'entsize': 0, 'index': 1, 'name': '.strtab'}, {'name_offset': 1, 'type': 1, 'flags': 6, 'address': 0, 'offset': 52, 'size': 0, 'link': 0, 'info': 0, 'align': 2, 'entsize': 0, 'index': 2, 'name': '.text'}, {'name_offset': 292, 'type': 1, 'flags': 6, 'address': 0, 'offset': 52, 'size': 12, 'link': 0, 'info': 0, 'align': 2, 'entsize': 0, 'index': 3, 'name': '.text.tsl9_queue_external_12a08'}, {'name_offset': 287, 'type': 4, 'flags': 64, 'address': 0, 'offset': 784, 'size': 12, 'link': 23, 'info': 3, 'align': 4, 'entsize': 12, 'index': 4, 'name': '.rela.text.tsl9_queue_external_12a08'}, {'name_offset': 450, 'type': 1, 'flags': 6, 'address': 0, 'offset': 64, 'size': 2, 'link': 0, 'info': 0, 'align': 2, 'entsize': 0, 'index': 5, 'name': '.text.tsl9_dispatch_status_12a14'}, {'name_offset': 445, 'type': 4, 'flags': 64, 'address': 0, 'offset': 796, 'size': 12, 'link': 23, 'info': 5, 'align': 4, 'entsize': 12, 'index': 6, 'name': '.rela.text.tsl9_dispatch_status_12a14'}, {'name_offset': 377, 'type': 1, 'flags': 6, 'address': 0, 'offset': 66, 'size': 10, 'link': 0, 'info': 0, 'align': 2, 'entsize': 0, 'index': 7, 'name': '.text.tsl9_dispatch_ID_12a16'}, {'name_offset': 372, 'type': 4, 'flags': 64, 'address': 0, 'offset': 808, 'size': 12, 'link': 23, 'info': 7, 'align': 4, 'entsize': 12, 'index': 8, 'name': '.rela.text.tsl9_dispatch_ID_12a16'}, {'name_offset': 550, 'type': 1, 'flags': 6, 'address': 0, 'offset': 76, 'size': 8, 'link': 0, 'info': 0, 'align': 2, 'entsize': 0, 'index': 9, 'name': '.text.tsl9_dispatch_query_12a20'}, {'name_offset': 545, 'type': 4, 'flags': 64, 'address': 0, 'offset': 820, 'size': 24, 'link': 23, 'info': 9, 'align': 4, 'entsize': 12, 'index': 10, 'name': '.rela.text.tsl9_dispatch_query_12a20'}, {'name_offset': 257, 'type': 1, 'flags': 6, 'address': 0, 'offset': 84, 'size': 6, 'link': 0, 'info': 0, 'align': 2, 'entsize': 0, 'index': 11, 'name': '.text.tsl9_dispatch_tag_12a28'}, {'name_offset': 252, 'type': 4, 'flags': 64, 'address': 0, 'offset': 844, 'size': 12, 'link': 23, 'info': 11, 'align': 4, 'entsize': 12, 'index': 12, 'name': '.rela.text.tsl9_dispatch_tag_12a28'}, {'name_offset': 97, 'type': 1, 'flags': 6, 'address': 0, 'offset': 90, 'size': 34, 'link': 0, 'info': 0, 'align': 2, 'entsize': 0, 'index': 13, 'name': '.text.tsl9_dispatch_copy_12a2e'}, {'name_offset': 508, 'type': 1, 'flags': 6, 'address': 0, 'offset': 124, 'size': 14, 'link': 0, 'info': 0, 'align': 2, 'entsize': 0, 'index': 14, 'name': '.text.tsl9_dispatch_peripheral_12a50'}, {'name_offset': 503, 'type': 4, 'flags': 64, 'address': 0, 'offset': 856, 'size': 12, 'link': 23, 'info': 14, 'align': 4, 'entsize': 12, 'index': 15, 'name': '.rela.text.tsl9_dispatch_peripheral_12a50'}, {'name_offset': 64, 'type': 1, 'flags': 6, 'address': 0, 'offset': 138, 'size': 8, 'link': 0, 'info': 0, 'align': 2, 'entsize': 0, 'index': 16, 'name': '.text.tsl9_dispatch_finish_12a5e'}, {'name_offset': 339, 'type': 1, 'flags': 6, 'address': 0, 'offset': 146, 'size': 8, 'link': 0, 'info': 0, 'align': 2, 'entsize': 0, 'index': 17, 'name': '.text.tsl9_dispatch_tagged_12a66'}, {'name_offset': 334, 'type': 4, 'flags': 64, 'address': 0, 'offset': 868, 'size': 24, 'link': 23, 'info': 17, 'align': 4, 'entsize': 12, 'index': 18, 'name': '.rela.text.tsl9_dispatch_tagged_12a66'}, {'name_offset': 7, 'type': 1, 'flags': 48, 'address': 0, 'offset': 154, 'size': 159, 'link': 0, 'info': 0, 'align': 1, 'entsize': 1, 'index': 19, 'name': '.comment'}, {'name_offset': 34, 'type': 1, 'flags': 0, 'address': 0, 'offset': 313, 'size': 0, 'link': 0, 'info': 0, 'align': 1, 'entsize': 0, 'index': 20, 'name': '.note.GNU-stack'}, {'name_offset': 16, 'type': 1879048195, 'flags': 0, 'address': 0, 'offset': 313, 'size': 52, 'link': 0, 'info': 0, 'align': 1, 'entsize': 0, 'index': 21, 'name': '.riscv.attributes'}, {'name_offset': 50, 'type': 1879002115, 'flags': 2147483648, 'address': 0, 'offset': 892, 'size': 9, 'link': 23, 'info': 0, 'align': 1, 'entsize': 0, 'index': 22, 'name': '.llvm_addrsig'}, {'name_offset': 214, 'type': 2, 'flags': 0, 'address': 0, 'offset': 368, 'size': 416, 'link': 1, 'info': 13, 'align': 4, 'entsize': 16, 'index': 23, 'name': '.symtab'}], 'symbols': [{'index': 0, 'name': '', 'value': 0, 'size': 0, 'info': 0, 'other': 0, 'section': 0}, {'index': 1, 'name': 'record_dispatch.v2.c', 'value': 0, 'size': 0, 'info': 4, 'other': 0, 'section': 65521}, {'index': 2, 'name': '$x.0', 'value': 0, 'size': 0, 'info': 0, 'other': 0, 'section': 3}, {'index': 3, 'name': '$x.1', 'value': 0, 'size': 0, 'info': 0, 'other': 0, 'section': 5}, {'index': 4, 'name': '$x.2', 'value': 0, 'size': 0, 'info': 0, 'other': 0, 'section': 7}, {'index': 5, 'name': '$x.3', 'value': 0, 'size': 0, 'info': 0, 'other': 0, 'section': 9}, {'index': 6, 'name': '$x.4', 'value': 0, 'size': 0, 'info': 0, 'other': 0, 'section': 11}, {'index': 7, 'name': '$x.5', 'value': 0, 'size': 0, 'info': 0, 'other': 0, 'section': 13}, {'index': 8, 'name': '$x.6', 'value': 0, 'size': 0, 'info': 0, 'other': 0, 'section': 14}, {'index': 9, 'name': '$x.7', 'value': 0, 'size': 0, 'info': 0, 'other': 0, 'section': 16}, {'index': 10, 'name': '$x.8', 'value': 0, 'size': 0, 'info': 0, 'other': 0, 'section': 17}, {'index': 11, 'name': '$d.9', 'value': 0, 'size': 0, 'info': 0, 'other': 0, 'section': 19}, {'index': 12, 'name': '$d.10', 'value': 0, 'size': 0, 'info': 0, 'other': 0, 'section': 21}, {'index': 13, 'name': 'tsl9_queue_external_12a08', 'value': 0, 'size': 12, 'info': 18, 'other': 0, 'section': 3}, {'index': 14, 'name': 'tsl9_queue_external_81aa', 'value': 0, 'size': 0, 'info': 16, 'other': 0, 'section': 0}, {'index': 15, 'name': 'tsl9_dispatch_status_12a14', 'value': 0, 'size': 2, 'info': 18, 'other': 0, 'section': 5}, {'index': 16, 'name': 'tsl9_dispatch_query_12a20', 'value': 0, 'size': 8, 'info': 18, 'other': 0, 'section': 9}, {'index': 17, 'name': 'tsl9_dispatch_ID_12a16', 'value': 0, 'size': 10, 'info': 18, 'other': 0, 'section': 7}, {'index': 18, 'name': 'tsl9_dispatch_finish_12a5e', 'value': 0, 'size': 8, 'info': 18, 'other': 0, 'section': 16}, {'index': 19, 'name': 'tsl9_dispatch_external_821e', 'value': 0, 'size': 0, 'info': 16, 'other': 0, 'section': 0}, {'index': 20, 'name': 'tsl9_dispatch_tag_12a28', 'value': 0, 'size': 6, 'info': 18, 'other': 0, 'section': 11}, {'index': 21, 'name': 'tsl9_dispatch_tagged_12a66', 'value': 0, 'size': 8, 'info': 18, 'other': 0, 'section': 17}, {'index': 22, 'name': 'tsl9_dispatch_copy_12a2e', 'value': 0, 'size': 34, 'info': 18, 'other': 0, 'section': 13}, {'index': 23, 'name': 'tsl9_dispatch_peripheral_12a50', 'value': 0, 'size': 14, 'info': 18, 'other': 0, 'section': 14}, {'index': 24, 'name': 'tsl9_dispatch_external_18ca4', 'value': 0, 'size': 0, 'info': 16, 'other': 0, 'section': 0}, {'index': 25, 'name': 'tsl9_dispatch_external_16b7c', 'value': 0, 'size': 0, 'info': 16, 'other': 0, 'section': 0}], 'relocations': [{'section': 3, 'offset': 8, 'type': 17, 'symbol': 14, 'addend': 0}, {'section': 5, 'offset': 0, 'type': 44, 'symbol': 16, 'addend': 0}, {'section': 7, 'offset': 6, 'type': 16, 'symbol': 18, 'addend': 0}, {'section': 9, 'offset': 2, 'type': 17, 'symbol': 19, 'addend': 0}, {'section': 9, 'offset': 6, 'type': 44, 'symbol': 18, 'addend': 0}, {'section': 11, 'offset': 4, 'type': 44, 'symbol': 21, 'addend': 0}, {'section': 14, 'offset': 10, 'type': 17, 'symbol': 24, 'addend': 0}, {'section': 17, 'offset': 2, 'type': 17, 'symbol': 25, 'addend': 0}, {'section': 17, 'offset': 6, 'type': 45, 'symbol': 18, 'addend': 0}], 'noncode_section_hashes': {'': 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855', '.strtab': 'a2ffcb141ea57f4f4bcb529693af92f0c1b2b4b83bd0dad0fa7712bb1bf1ceb5', '.rela.text.tsl9_queue_external_12a08': 'b4e0f5ae26502c6abfe05cb6826699da8bbdd5f582bea164886b307f34f1c19a', '.rela.text.tsl9_dispatch_status_12a14': '732c535d3091df08205b2d9ebe90f1aa34c9b3f07005ee97c0e4bd664e3c586c', '.rela.text.tsl9_dispatch_ID_12a16': '029f12762ac5e4c73a662851d64e9af365238b91fb10db7b780f4eef5ac04e5d', '.rela.text.tsl9_dispatch_query_12a20': '5de5659bf62a8ad742ab9a17d6238815b1a8686de01d183b523bad191dcb63c7', '.rela.text.tsl9_dispatch_tag_12a28': 'b85209815ffaaa0d9d0aba24d02c6dfcc1204ca9bb9b5c1b1e613d635d3c0283', '.rela.text.tsl9_dispatch_peripheral_12a50': '9df01200a8e71486e130ff53cca143824aea6bd0ab411a5abc9a7ab3165a751b', '.rela.text.tsl9_dispatch_tagged_12a66': '8b33870a985a583d1ce4a6ce68728ae71c276fd6fbd4d8d55a3cf486ad5f9183', '.comment': '72c64fbc17a5d9f46f33ac0650b7d4f549d87c2ba9e77ebd765a25a3960e3017', '.note.GNU-stack': 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855', '.riscv.attributes': 'f2bd85b0ab58609a20dbdef6cc6e3f2dd1a34cdcb554580710aa3819cd24ad71', '.llvm_addrsig': '3cf439a3c94ea0f816bee2c9784bf8d84caa409112b8e3f5e7f3271628318588', '.symtab': 'fcacf66ed02aea7e67b80b7e6beedbd0fda048e5f20c3a501a70e274c0cc0608'}, 'outside_allocated_code_sha256': '851a95cea8cdae0ea8e78faea5616b7667b6be0887e684e865c38fa824b7322b'}, 'partial': {'header': [1, 243, 1, 0, 0, 1232, 1, 52, 0, 0, 40, 8, 6], 'program_headers': [], 'sections': [{'name_offset': 0, 'type': 0, 'flags': 0, 'address': 0, 'offset': 0, 'size': 0, 'link': 0, 'info': 0, 'align': 0, 'entsize': 0, 'index': 0, 'name': ''}, {'name_offset': 1, 'type': 1, 'flags': 6, 'address': 0, 'offset': 52, 'size': 102, 'link': 0, 'info': 0, 'align': 2, 'entsize': 0, 'index': 1, 'name': '.record_dispatch'}, {'name_offset': 18, 'type': 1, 'flags': 6, 'address': 0, 'offset': 154, 'size': 0, 'link': 0, 'info': 0, 'align': 2, 'entsize': 0, 'index': 2, 'name': '.text'}, {'name_offset': 24, 'type': 4, 'flags': 64, 'address': 0, 'offset': 156, 'size': 108, 'link': 5, 'info': 1, 'align': 4, 'entsize': 12, 'index': 3, 'name': '.rela.record_dispatch'}, {'name_offset': 46, 'type': 1879002115, 'flags': 2147483648, 'address': 0, 'offset': 264, 'size': 9, 'link': 0, 'info': 0, 'align': 1, 'entsize': 0, 'index': 4, 'name': '.llvm_addrsig'}, {'name_offset': 60, 'type': 2, 'flags': 0, 'address': 0, 'offset': 276, 'size': 448, 'link': 7, 'info': 15, 'align': 4, 'entsize': 16, 'index': 5, 'name': '.symtab'}, {'name_offset': 68, 'type': 3, 'flags': 0, 'address': 0, 'offset': 724, 'size': 86, 'link': 0, 'info': 0, 'align': 1, 'entsize': 0, 'index': 6, 'name': '.shstrtab'}, {'name_offset': 78, 'type': 3, 'flags': 0, 'address': 0, 'offset': 810, 'size': 420, 'link': 0, 'info': 0, 'align': 1, 'entsize': 0, 'index': 7, 'name': '.strtab'}], 'symbols': [{'index': 0, 'name': '', 'value': 0, 'size': 0, 'info': 0, 'other': 0, 'section': 0}, {'index': 1, 'name': 'record_dispatch.v2.c', 'value': 0, 'size': 0, 'info': 4, 'other': 0, 'section': 65521}, {'index': 2, 'name': '$x.0', 'value': 0, 'size': 0, 'info': 0, 'other': 0, 'section': 1}, {'index': 3, 'name': '$x.1', 'value': 12, 'size': 0, 'info': 0, 'other': 0, 'section': 1}, {'index': 4, 'name': '$x.2', 'value': 14, 'size': 0, 'info': 0, 'other': 0, 'section': 1}, {'index': 5, 'name': '$x.3', 'value': 24, 'size': 0, 'info': 0, 'other': 0, 'section': 1}, {'index': 6, 'name': '$x.4', 'value': 32, 'size': 0, 'info': 0, 'other': 0, 'section': 1}, {'index': 7, 'name': '$x.5', 'value': 38, 'size': 0, 'info': 0, 'other': 0, 'section': 1}, {'index': 8, 'name': '$x.6', 'value': 72, 'size': 0, 'info': 0, 'other': 0, 'section': 1}, {'index': 9, 'name': '$x.7', 'value': 86, 'size': 0, 'info': 0, 'other': 0, 'section': 1}, {'index': 10, 'name': '$x.8', 'value': 94, 'size': 0, 'info': 0, 'other': 0, 'section': 1}, {'index': 11, 'name': '$d.10', 'value': 0, 'size': 0, 'info': 0, 'other': 0, 'section': 65521}, {'index': 12, 'name': '', 'value': 0, 'size': 0, 'info': 3, 'other': 0, 'section': 1}, {'index': 13, 'name': '', 'value': 0, 'size': 0, 'info': 3, 'other': 0, 'section': 2}, {'index': 14, 'name': '', 'value': 0, 'size': 0, 'info': 3, 'other': 0, 'section': 4}, {'index': 15, 'name': 'tsl9_queue_external_12a08', 'value': 0, 'size': 12, 'info': 18, 'other': 0, 'section': 1}, {'index': 16, 'name': 'tsl9_queue_external_81aa', 'value': 0, 'size': 0, 'info': 16, 'other': 0, 'section': 0}, {'index': 17, 'name': 'tsl9_dispatch_status_12a14', 'value': 12, 'size': 2, 'info': 18, 'other': 0, 'section': 1}, {'index': 18, 'name': 'tsl9_dispatch_query_12a20', 'value': 24, 'size': 8, 'info': 18, 'other': 0, 'section': 1}, {'index': 19, 'name': 'tsl9_dispatch_ID_12a16', 'value': 14, 'size': 10, 'info': 18, 'other': 0, 'section': 1}, {'index': 20, 'name': 'tsl9_dispatch_finish_12a5e', 'value': 86, 'size': 8, 'info': 18, 'other': 0, 'section': 1}, {'index': 21, 'name': 'tsl9_dispatch_external_821e', 'value': 0, 'size': 0, 'info': 16, 'other': 0, 'section': 0}, {'index': 22, 'name': 'tsl9_dispatch_tag_12a28', 'value': 32, 'size': 6, 'info': 18, 'other': 0, 'section': 1}, {'index': 23, 'name': 'tsl9_dispatch_tagged_12a66', 'value': 94, 'size': 8, 'info': 18, 'other': 0, 'section': 1}, {'index': 24, 'name': 'tsl9_dispatch_copy_12a2e', 'value': 38, 'size': 34, 'info': 18, 'other': 0, 'section': 1}, {'index': 25, 'name': 'tsl9_dispatch_peripheral_12a50', 'value': 72, 'size': 14, 'info': 18, 'other': 0, 'section': 1}, {'index': 26, 'name': 'tsl9_dispatch_external_18ca4', 'value': 0, 'size': 0, 'info': 16, 'other': 0, 'section': 0}, {'index': 27, 'name': 'tsl9_dispatch_external_16b7c', 'value': 0, 'size': 0, 'info': 16, 'other': 0, 'section': 0}], 'relocations': [{'section': 1, 'offset': 8, 'type': 17, 'symbol': 16, 'addend': 0}, {'section': 1, 'offset': 12, 'type': 44, 'symbol': 18, 'addend': 0}, {'section': 1, 'offset': 20, 'type': 16, 'symbol': 20, 'addend': 0}, {'section': 1, 'offset': 26, 'type': 17, 'symbol': 21, 'addend': 0}, {'section': 1, 'offset': 30, 'type': 44, 'symbol': 20, 'addend': 0}, {'section': 1, 'offset': 36, 'type': 44, 'symbol': 23, 'addend': 0}, {'section': 1, 'offset': 82, 'type': 17, 'symbol': 26, 'addend': 0}, {'section': 1, 'offset': 96, 'type': 17, 'symbol': 27, 'addend': 0}, {'section': 1, 'offset': 100, 'type': 45, 'symbol': 20, 'addend': 0}], 'noncode_section_hashes': {'': 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855', '.rela.record_dispatch': 'b8d20a75c938267c41a3f2943098715451ec602e9441bae8d33971e0662371de', '.llvm_addrsig': '3cf439a3c94ea0f816bee2c9784bf8d84caa409112b8e3f5e7f3271628318588', '.symtab': '8450161224075d1612b37591b6f26d08aa22381f5b4c8c097628acdd787420c0', '.shstrtab': 'de1bc22b2c239451d836efff07f5f6452812237e9dfa5ab4f2548f71e8548485', '.strtab': 'f603ee7eef756a70d04db7d6a0867fa7393611735dd006a7da363fc6612d1b09'}, 'outside_allocated_code_sha256': '77b2ad0da1e7b8af62b80dbf197d79f72e4f2bc96d799ba463590ec8d88aa39b'}}
IR_CORE = {'tsl9_queue_external_12a08': ['tail call void asm sideeffect "addi sp, sp, -48\\0Asw s0, 40(sp)\\0Asw ra, 44(sp)\\0Amv s0, a0\\0A.Lrecord_status_call:\\0A.option push\\0A.option norvc\\0Ajal ra, .Lrecord_status_call\\0A.option pop\\0A.reloc .-4, R_RISCV_JAL, tsl9_queue_external_81aa\\0A", ""() #2', 'unreachable'], 'tsl9_dispatch_status_12a14': ['tail call void asm sideeffect ".Lrecord_status_nonzero:\\0Ac.bnez a0, .Lrecord_status_nonzero\\0A.reloc .-2, R_RISCV_RVC_BRANCH, tsl9_dispatch_query_12a20\\0A", "~{memory}"() #2', 'unreachable'], 'tsl9_dispatch_ID_12a16': ['%1 = tail call i32 asm sideeffect "lhu a4, 0(s0)\\0A", "={x14},~{x15},~{memory}"() #2', 'tail call void asm sideeffect ".Lrecord_ID_rejected:\\0Abne a4, a5, .Lrecord_ID_rejected\\0A.reloc .-4, R_RISCV_BRANCH, tsl9_dispatch_finish_12a5e\\0A", "{x14},{x15},~{memory}"(i32 %1, i32 1) #2', 'unreachable'], 'tsl9_dispatch_query_12a20': ['%1 = tail call i32 asm sideeffect ".Lrecord_query_call:\\0A.option push\\0A.option norvc\\0Ajal ra, .Lrecord_query_call\\0A.option pop\\0A.reloc .-4, R_RISCV_JAL, tsl9_dispatch_external_821e\\0A", "={x10},{x10},~{x11},~{x12},~{x13},~{x14},~{x15},~{memory}"(i32 0) #2', 'tail call void asm sideeffect ".Lrecord_query_zero:\\0Ac.beqz a0, .Lrecord_query_zero\\0A.reloc .-2, R_RISCV_RVC_BRANCH, tsl9_dispatch_finish_12a5e\\0A", "{x10},~{memory}"(i32 %1) #2', 'unreachable'], 'tsl9_dispatch_tag_12a28': ['%1 = tail call i32 asm sideeffect "lbu a5, 11(s0)\\0A", "={x15},~{memory}"() #2', 'tail call void asm sideeffect ".Lrecord_tagged:\\0Ac.bnez a5, .Lrecord_tagged\\0A.reloc .-2, R_RISCV_RVC_BRANCH, tsl9_dispatch_tagged_12a66\\0A", "{x15},~{memory}"(i32 %1) #2', 'unreachable'], 'tsl9_dispatch_copy_12a2e': ['%1 = tail call { i32, i32 } asm sideeffect "lhu a5, 0(s0)\\0Albu a2, 2(s0)\\0Ash zero, 20(sp)\\0Asw a5, 12(sp)\\0Asb a2, 22(sp)\\0A", "={x15},={x12},~{memory}"() #2', '%2 = extractvalue { i32, i32 } %1, 1', '%3 = tail call i32 asm sideeffect "", "={x15},{x12},{x15},~{memory}"(i32 %2, i32 262144) #2', '%4 = add i32 %3, 76', '%5 = inttoptr i32 %4 to ptr', '%6 = load volatile i32, ptr %5, align 4', 'tail call void asm sideeffect "addi a1, s0, 3\\0Aaddi a0, sp, 23\\0Ajalr a5\\0A", "{x15},{x12},~{x10},~{x11},~{x13},~{x14},~{memory}"(i32 %6, i32 %2) #2', 'unreachable'], 'tsl9_dispatch_peripheral_12a50': ['%1 = tail call { i32, i32 } asm sideeffect "addi a1, sp, 12\\0A", "={x11},={x10},{x10},~{memory}"(i32 1073766400) #2', '%2 = extractvalue { i32, i32 } %1, 0', '%3 = extractvalue { i32, i32 } %1, 1', '%4 = add i32 %3, 1024', 'tail call void asm sideeffect ".Lrecord_peripheral_call:\\0A.option push\\0A.option norvc\\0Ajal ra, .Lrecord_peripheral_call\\0A.option pop\\0A.reloc .-4, R_RISCV_JAL, tsl9_dispatch_external_18ca4\\0A", "{x10},{x11},~{x12},~{x13},~{x14},~{x15},~{memory}"(i32 %4, i32 %2) #2', 'unreachable'], 'tsl9_dispatch_finish_12a5e': ['tail call void asm sideeffect "lw ra, 44(sp)\\0Alw s0, 40(sp)\\0Aaddi sp, sp, 48\\0Aret\\0A", ""() #2', 'unreachable'], 'tsl9_dispatch_tagged_12a66': ['tail call void asm sideeffect "mv a0, s0\\0A.Lrecord_tag_call:\\0A.option push\\0A.option norvc\\0Ajal ra, .Lrecord_tag_call\\0A.option pop\\0A.reloc .-4, R_RISCV_JAL, tsl9_dispatch_external_16b7c\\0A.Lrecord_tag_finish:\\0Ac.j .Lrecord_tag_finish\\0A.reloc .-2, R_RISCV_RVC_JUMP, tsl9_dispatch_finish_12a5e\\0A", ""() #2', 'unreachable']}


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
    need(rows==expected,'all35 original instruction widths/physical operands/order/cold CFG targets')
    at={r[0]:r for r in rows}
    need([at[p] for p in (0,2,4,6,86,88,90,92)]==[[0,2,'ADDI',2,2,-48],[2,2,'SW32',8,2,40],
         [4,2,'SW32',1,2,44],[6,2,'MV',8,10],[86,2,'LW32',1,2,44],[88,2,'LW32',8,2,40],
         [90,2,'ADDI',2,2,48],[92,2,'RET',1]],'original48B frame and fresh then-live SP/RA/S0 restore')
    need([at[p] for p in (38,42,46,50,52)]==[[38,4,'LHU16',15,8,0],[42,4,'LBU8',12,8,2],
         [46,4,'SH16',0,2,20],[50,2,'SW32',15,2,12],[52,4,'SB8',12,2,22]],'fresh metadata input and exact halfword/word/byte stores in original order')
    own_stack_writes=[(r[5],{'SB8':1,'SH16':2,'SW32':4}[r[2]]) for r in rows if r[2] in ('SB8','SH16','SW32') and r[4]==2]
    need(not any(a<20 and a+width>16 for a,width in own_stack_writes),'own stores do not initialize SP+16..19')
    need([at[p] for p in (56,60,62,66,70)]==[[56,4,'LUI',15,0x40000],[60,2,'LW32',15,15,76],
         [62,4,'ADDI',11,8,3],[66,4,'ADDI',10,2,23],[70,2,'JALR',1,15,0]],'fresh resident cell0x4004C and then-live S0/SP inputs, real RA link')
    need([at[p] for p in (72,76,78)]==[[72,4,'LUI',10,0x40006000],[76,2,'ADDI',11,2,12],[78,4,'ADDI',10,10,1024]],
         'interleaved peripheral-looking base arithmetic and recomputed then-live SP+12')
    need(not any(r[2] in ('ADDI','MV','LW32','LHU16','LBU8','LUI') and r[3] in (12,13) for r in rows if 72<=r[0]<82),
         'A2/A3 after the resident call remain opaque residues before18CA4')
    need(all(at[p][0:4]==[p,4,'JAL',1] for p in (8,26,82,96)),'all four direct calls are4B JAL rd=RA')
    need(at[94]==[94,2,'MV',10,8] and at[100][0:3]==[100,2,'J'],'reachable tagged cold call then no-link jump to shared restore')
    return rows


def cfg_contract(rows,pending=False):
    typed_contract(rows,pending);result=[]
    for at,width,op,*args in rows:
        pc=BASE+at;following=pc+width;item=dict(PC=pc,width=width,operation=op)
        if op in ('BEQ','BNE','BEQZ','BNEZ'):item.update(kind='conditional',target=args[-1],fallthrough=following)
        elif op=='J':item.update(kind='direct_no_link',target=args[-1])
        elif op=='JAL':item.update(kind='direct_call',link_rd=args[0],target=args[-1],RA_continuation=following)
        elif op=='JALR':item.update(kind='opaque_resident_call',link_rd=args[0],target='fresh LW32[0x%X]'%RESIDENT_CELL,RA_continuation=following)
        elif op=='RET':item.update(kind='return',target='then-live RA')
        else:item.update(kind='linear',fallthrough=following)
        result.append(item)
    counts={k:sum(r['kind']==k for r in result) for k in ('conditional','direct_call','opaque_resident_call','direct_no_link','return','linear')}
    need(len(result)==35 and counts=={'conditional':4,'direct_call':4,'opaque_resident_call':1,'direct_no_link':1,'return':1,'linear':24},
         'complete35-node bounded CFG, including post-RET cold block')
    return result


def original():
    raw=FIRMWARE.read_bytes();need(len(raw)==76800 and sha(raw)==PINS[FIRMWARE],'whole original BIN identity')
    code=raw[BASE-0x8000:BASE-0x8000+102];need(sha(code)==ORIGINAL_PIN,'primary102B span identity')
    rows=decode(code);typed_contract(rows,False);cfg_contract(rows)
    need(digest(DECODE)==PINS[DECODE] and digest(WINDOW)==PINS[WINDOW],'primary contract plus historical source-window identity')
    evidence=json.loads(DECODE.read_bytes());span=evidence['span'];recorded=evidence['rows']
    need((span['start'],span['end_exclusive'],span['bytes'],span['instructions'],span['sha256'])==(BASE,BASE+102,102,35,ORIGINAL_PIN)
         and evidence['firmware']['sha256']==PINS[FIRMWARE] and evidence['firmware']['mapping_base']==0x8000,'primary contract bounds/identity')
    need(evidence['source_window']['sha256']==PINS[WINDOW] and b''.join(bytes.fromhex(r['bytes']) for r in recorded)==code and
         [(r['addr']-BASE,r['size']) for r in recorded]==[(r[0],r[1]) for r in EXPECTED],'complete primary row coverage; later source-window entries excluded')
    status=raw[0x81aa-0x8000:0x81aa-0x8000+6]
    need(sha(status)=='887c2bfb847a7e013acebac38c8be3f2bed06fd44305080ad6fc7ca3593e8fc3','known status6B original observation only, not component call resolution')
    return code


def masks():
    result=bytearray(b'\xff'*102)
    for at,kind,_ in RELATIONS:
        n,mask=MASKS[kind];result[at:at+n]=mask.to_bytes(n,'little')
    return result


def elf_contract(e,native,official,full=True):
    need(bool(ELF_PINS) and bool(SCHEMAS),'measured candidate not bound')
    schema=SCHEMAS['native' if native else 'partial']
    need(len(e.raw)==schema['header'][5]+40*schema['header'][11],'complete ELF extent without unbound trailing bytes')
    need(e.header[0]==1 and e.header[6]==1 and not e.program_headers,'actual RV32 RVC ET_REL only')
    gs=[s for s in e.symbols if s['info']>>4]
    expected={n:(0 if native else at,z,18,0,'.text.'+n if native else '.record_dispatch') for n,at,z in REGIONS}
    actual={s['name']:(s['value'],s['size'],s['info'],s['other'],e.sections[s['section']]['name']) for s in gs if s['section'] not in (0,65521)}
    need(actual==expected and len(gs)==13,'nine genuine FUNCs in exact order/ownership/extent')
    und=[s for s in gs if s['section']==0]
    need(sorted(s['name'] for s in und)==sorted(UNDEFINED) and all(s['info']==16 and s['other']==s['size']==s['value']==0 for s in und)
         and not any(s['section']==65521 for s in gs),'four genuine strong UND, no ABS/weak/fake provider')
    alloc=[s for s in e.sections if s['flags']&2 and s['size']]
    need([(s['name'],s['address'],s['size'],s['type'],s['flags'],s['align']) for s in alloc]==
       ([('.text.'+n,0,z,1,6,2) for n,_,z in REGIONS] if native else [('.record_dispatch',0,102,1,6,2)]),'exact AX-only allocation')
    code=b''.join(e.data('.text.'+n) for n in NAMES) if native else e.data('.record_dispatch')
    rows=typed_contract(decode(code),True);need(len(code)==102 and len(rows)==35,'102B35i')
    cfg=cfg_contract(rows,True);starts={'.text.'+n:at for n,at,_ in REGIONS};rels=[]
    for r in e.relocations:
        owner=e.sections[r['section']]['name'];symbol=e.symbols[r['symbol']]
        need(owner in starts if native else owner=='.record_dispatch','genuine relocation owner')
        offset=r['offset']+(starts[owner] if native else 0);rels.append((offset,r['type'],symbol['name'],r['addend']))
        need((symbol['info']==16 and symbol['section']==0) if r['type']==17 else
             (symbol['info']==18 and symbol['section'] not in (0,65521)),'real external JAL provider versus defined architectural branch target')
    need(rels==[(a,k,n,0) for a,k,n in RELATIONS],'all nine relocation offsets/types/targets/addends; exact81AA symbol')
    bitmasks=masks();need(all(not ((a^b)&mask) for a,b,mask in zip(code,official,bitmasks)),
         'all original nonrelocation bits, actual JAL rd/width and physical operands')
    need(metadata(e)==schema,'complete actual ELF metadata/noncode/gap bytes')
    if full:need(sha(e.raw)==ELF_PINS[native],'whole measured ELF pin')
    controls=[];original_rows={r[0]:r for r in EXPECTED}
    for at,kind,name in RELATIONS:
        row=original_rows[at];call=kind==17
        controls.append(dict(offset=at,kind=kind,target_symbol=name,nominal_PC=BASE+at,nominal_target=row[-1],
            pending_machine_target=BASE+at,link_rd=1 if call else 0,RA_continuation=BASE+at+row[1] if call else None,
            fallthrough=BASE+at+row[1] if kind in (16,44) else None))
    return dict(sha256=sha(e.raw),header=e.header,program_headers=e.program_headers,sections=e.sections,
       symbols=e.symbols,relocations=e.relocations,code_hex=code.hex(),code_sha256=sha(code),typed_rows=rows,cfg=cfg,
       cfg_coordinates='original nominal BASE plus joined source-span offset; unresolved ET_REL is not installed at these VAs',
       UND_providers=UNDEFINED,ABS_providers=[],local_ABS_metadata=sum(s['section']==65521 and not s['info']>>4 for s in e.symbols),
       controls=controls,retained_nonrelocation_bits=sum(n.bit_count() for n in bitmasks),fully_unmasked_bytes=sum(n==255 for n in bitmasks),
       whole_nonrelocation_instruction_bytes=74,pending_machine_immediates=9,defined_relocation_sites=5,UND_relocation_sites=4,
       unknown_resident_calls=1,firmware_ready=False)


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
        for name in UNDEFINED+[NAMES[7]]:
            at=symtab['offset']+gs[name]['index']*16
            raw(tag+'_fakeABS_'+name,e,n,at+14,'<H',65521)
            raw(tag+'_weak_'+name,e,n,at+12,'<B',34)
        at=symtab['offset']+gs[NAMES[5]]['index']*16
        raw(tag+'_FUNC_size',e,n,at+8,'<I',32);raw(tag+'_FUNC_value',e,n,at+4,'<I',2)
        sec=next(s for s in e.sections if s['flags']&2 and s['size'])
        raw(tag+'_writable_code',e,n,e.header[5]+40*sec['index']+8,'<I',7)
        check(tag+'_trailing_bytes','raw_ELF_reparsed',lambda ee=e,nn=n:elf_contract(ELF(ee.raw+b'\0\0'),nn,official,False))
        for i,r in enumerate(e.relocations):
            table=next(s for s in e.sections if s['type']==4 and s['info']==r['section'])
            previous=sum(z['section']==r['section'] for z in e.relocations[:i]);at=table['offset']+12*previous
            raw(tag+'_RELA_addend_'+str(i),e,n,at+8,'<i',2)
            raw(tag+'_RELA_family_'+str(i),e,n,at+4,'<I',(r['symbol']<<8)|(44 if r['type']==17 else 17))
            wrong=gs[UNDEFINED[1] if e.symbols[r['symbol']]['name']!=UNDEFINED[1] else UNDEFINED[2]]['index']
            raw(tag+'_RELA_target_'+str(i),e,n,at+4,'<I',(wrong<<8)|r['type'])
        def offset(pc):
            region=next((name,a,z) for name,a,z in REGIONS if a<=pc<a+z)
            return e.section('.text.'+region[0])['offset']+pc-region[1] if n else e.section('.record_dispatch')['offset']+pc
        for pc in (8,26,82,96):
            at=offset(pc);raw(tag+'_JAL_rd_zero_'+str(pc),e,n,at,'<B',e.raw[at]^128)
            # Valid compressed self-call + NOP stream has the same4-byte extent,
            # but differs from the original single4B JAL and its RA continuation.
            raw(tag+'_compressed_JAL_plus_NOP_'+str(pc),e,n,at,'<I',0x00012001)
        for name,pc,delta,xor in [('SP_frame48',0,0,4),('saved_S0_slot40',2,0,4),('saved_RA_slot44',4,0,4),
            ('captured_record_S0',6,0,4),('status_branch_A0',12,0,128),('ID_lhu_width',14,1,16),
            ('ID_constant1',18,0,4),('ID_compare',20,2,16),('query_index0',24,0,4),('query_zero_edge',30,1,32),
            ('tag_offset11',32,2,16),('tag_branch',36,1,32),('metadata_ID_width',38,1,16),('metadata_length_offset2',42,2,16),
            ('metadata_SH_as_SB',46,1,16),('metadata_SW_source',50,0,4),('metadata_SB_len_offset22',52,0,128),
            ('resident_LUI_base',56,2,16),('resident_LW_offset76',60,0,4),('source_record_plus3',62,2,16),
            ('destination_SP23',66,2,16),('resident_JALR_as_JR',70,1,16),('peripheral_LUI_base',72,2,16),
            ('peripheral_add1024',78,2,16),('fresh_RA_slot44',86,0,4),('fresh_S0_slot40',88,0,4),
            ('SP_cleanup48',90,0,4),('RET',92,0,4),('tagged_thenlive_S0',94,0,4),('cold_J_incorrectly_links',100,1,128)]:
            at=offset(pc)+delta;raw(tag+'_'+name,e,n,at,'<B',e.raw[at]^xor)
        for pc in (32,38,42):
            at=offset(pc);word=int.from_bytes(e.raw[at:at+4],'little')
            raw(tag+'_thenlive_S0_changed_'+str(pc),e,n,at,'<I',(word&~(31<<15))|(9<<15))
        at=offset(76);word=int.from_bytes(e.raw[at:at+2],'little')
        raw(tag+'_postresident_A2_residue_clobbered',e,n,at,'<H',(word&~0x1c)|(4<<2))
        at=offset(72);word=int.from_bytes(e.raw[at:at+4],'little')
        raw(tag+'_postresident_A3_residue_clobbered',e,n,at,'<I',(word&~0xf80)|(13<<7))
        b=bytearray(e.raw);a=offset(46);chunk=bytes(b[a:a+6]);b[a:a+6]=chunk[4:]+chunk[:4]
        check(tag+'_metadata_store_order','raw_ELF_reparsed',lambda bb=b,nn=n:elf_contract(ELF(bb),nn,official,False))
    rowmap={r[0]:i for i,r in enumerate(EXPECTED)}
    for name,pc,field,value in [('parsed_word_ID_as_halfword',50,2,'SH16'),('parsed_metadata_length_byte',52,3,15),
        ('parsed_thenlive_S0',38,4,9),('parsed_fresh_SP_after_resident',76,4,8),('parsed_A2_reloaded',76,3,12),
        ('parsed_A3_clobbered',72,3,13),('parsed_resident_no_link',70,3,0),('parsed_status_wrong_alias',8,4,0x81ac)]:
        changed=copy.deepcopy(EXPECTED);changed[rowmap[pc]][field]=value
        check(name,'parsed_typed_rows',lambda c=changed:typed_contract(c,False))
    changed=copy.deepcopy(EXPECTED);changed.insert(rowmap[46],[46,4,'SW32',0,2,16])
    check('parsed_false_zero_initialization_SP16_19','parsed_typed_rows',lambda:typed_contract(changed,False))
    return results


def ir_contract(text,language,full=True):
    normalized='\n'.join(text.splitlines()[2:])+'\n';core=core_ir(normalized)
    need(list(core)==NAMES and core==IR_CORE,'all literal SSA/constants/fresh physical ports in complete nine-region order')
    need(len(re.findall(r'load volatile i32',normalized))==1 and not re.search(r'load volatile i(?:8|16|64)|store volatile|\balloca\b|\b(?:undef|poison)\b',normalized),
         'one true C resident word load; record/stack operations remain explicit physical ports')
    metadata_port='lhu a5, 0(s0)\\0Albu a2, 2(s0)\\0Ash zero, 20(sp)\\0Asw a5, 12(sp)\\0Asb a2, 22(sp)\\0A'
    need(metadata_port in normalized and 'sw zero, 16(sp)' not in normalized,'exact fresh metadata width/order; no invented initialization of SP16..19')
    need('(i32 %2, i32 262144)' in normalized and '%4 = add i32 %3, 76' in normalized and
         '%6 = load volatile i32, ptr %5, align 4' in normalized,'actual resident cell derives0x40000+76=0x4004C')
    need('"={x10},{x10},~{x11},~{x12},~{x13},~{x14},~{x15},~{memory}"(i32 0)' in normalized and
         '"{x10},~{memory}"(i32 %1)' in normalized,'query zero input and fresh returned A0 predicate, not a cached zero')
    need('addi a1, s0, 3\\0Aaddi a0, sp, 23\\0Ajalr a5\\0A' in normalized and
         '"={x11},={x10},{x10},~{memory}"(i32 1073766400)' in normalized and '%4 = add i32 %3, 1024' in normalized,
         'then-live resident arguments and interleaved peripheral-base/SP arithmetic')
    need(normalized.count('.option norvc')==4 and normalized.count('R_RISCV_JAL, ')==4 and normalized.count('jal ra, ')==4 and
         normalized.count('jalr a5\\0A')==1 and normalized.count('ret\\0A')==1,
         'four explicit4B direct JAL ports, one RA resident call and sole shared RET')
    need(not re.search(r'\.4byte|\.word|\.insn|mret|csrr|csrw|\bcall\b[^\n]*@',normalized),
         'no opcode carrier, added privileged operation or hidden ordinary C helper')
    if full:need(sha(normalized.encode())==IR_PINS[language],'complete normalized IR with attributes/TBAA/srcloc metadata')
    return dict(normalized_sha256=sha(normalized.encode()),core_SSA=core,C_volatile_word_reads=1,
       C_constants_and_argument_arithmetic=True,physical_S0_SP_memory_ports=True,ordinary_C_ABI_proven=False)


def ir_md_negatives(text,language,md,llvm,out):
    results=[]
    def check(name,scope,fn,full=False):
        try:fn()
        except (ValueError,IndexError,KeyError) as exc:results.append(dict(name=name,scope=scope,rejected=True,
             whole_ELF_hash_enabled=False,whole_IR_hash_enabled=full,reason=str(exc)))
        else:raise ValueError('negative accepted '+name)
    mutations=[('IR_JAL_compression','option norvc','option rvc'),('IR_status_symbol','tsl9_queue_external_81aa','tsl9_queue_status_81aa'),
       ('IR_JAL_rd_zero','jal ra, .Lrecord_status_call','jal zero, .Lrecord_status_call'),('IR_frame48','addi sp, sp, -48','addi sp, sp, -32'),
       ('IR_ID_thenlive_S0','lhu a4, 0(s0)','lhu a4, 0(s1)'),('IR_ID_constant1','i32 %1, i32 1','i32 %1, i32 2'),
       ('IR_query_result_cached','"{x10},~{memory}"(i32 %1)','"{x10},~{memory}"(i32 0)'),('IR_tag_offset11','lbu a5, 11(s0)','lbu a5, 10(s0)'),
       ('IR_metadata_ID_fresh','lhu a5, 0(s0)','lhu a5, 0(s1)'),('IR_metadata_length2','lbu a2, 2(s0)','lbu a2, 3(s0)'),
       ('IR_metadata_word_as_halfword','sw a5, 12(sp)','sh a5, 12(sp)'),('IR_metadata_halfword_as_byte','sh zero, 20(sp)','sb zero, 20(sp)'),
       ('IR_false_zero_init_SP16_19','sw a5, 12(sp)\\0A','sw a5, 12(sp)\\0Asw zero, 16(sp)\\0A'),
       ('IR_resident_address_scale','i32 %2, i32 262144','i32 %2, i32 4194304'),('IR_resident_offset76','%4 = add i32 %3, 76','%4 = add i32 %3, 80'),
       ('IR_resident_read_cached','load volatile i32','load i32'),('IR_resident_read_width','load volatile i32','load volatile i16'),
       ('IR_source_thenlive_S0','addi a1, s0, 3','addi a1, s1, 3'),('IR_destination_thenlive_SP','addi a0, sp, 23','addi a0, sp, 24'),
       ('IR_resident_no_link','jalr a5','jr a5'),('IR_peripheral_record_cached','addi a1, sp, 12','mv a1, a0'),
       ('IR_peripheral_A2_residue','addi a1, sp, 12\\0A','addi a2, zero, 0\\0Aaddi a1, sp, 12\\0A'),
       ('IR_peripheral_base','i32 1073766400','i32 1073762304'),('IR_peripheral_add1024','%4 = add i32 %3, 1024','%4 = add i32 %3, 1020'),
       ('IR_restore_RA44','lw ra, 44(sp)','lw ra, 40(sp)'),('IR_restore_S0_40','lw s0, 40(sp)','lw s0, 36(sp)'),
       ('IR_cleanup48','addi sp, sp, 48','addi sp, sp, 32'),('IR_tagged_thenlive_S0','mv a0, s0','mv a0, s1')]
    for name,old,new in mutations:
        need(old in text,'real IR negative fixture '+name);changed=text.replace(old,new,1)
        check(name,'IR_text_structural_SSA',lambda c=changed:ir_contract(c,language,False))
    for name,old,new in [('IR_full_attributes','generic-rv32','other-rv32'),('IR_full_metadata','!"wchar_size"','!"other"')]:
        need(old in text,'real complete IR fixture');changed=text.replace(old,new,1)
        check(name,'IR_text_full_normalized_pin',lambda c=changed:ir_contract(c,language,True),True)
    for name,changed in [('MD_target',md.replace('native.o:','other.o:',1)),('MD_missing_header',' '.join(md.splitlines()[:-1])),('MD_extra',md+'\nextra.h\n')]:
        check(name,'MD_text',lambda c=changed:md_contract(c,llvm,out))
    return results


def evaluate(root,llvm,out,language):
    need(root.resolve()==ROOT,'canonical project root');before=inputs(llvm);official=original()
    native=ELF(out/'native.o');partial=ELF(out/'partial.o')
    nf=elf_contract(native,True,official);pf=elf_contract(partial,False,official)
    need(nf['code_hex']==pf['code_hex'],'partial composition preserves all actual native bytes')
    text=(out/'native.ll').read_text(encoding='utf-8');ir=ir_contract(text,language)
    md=(out/'native.d').read_text(encoding='utf-8');deps=md_contract(md,llvm,out)
    commands=[dict(label=n,argv=portable(a,ROOT,llvm),returncode=0) for n,a in recipes(llvm,out,language)]
    need(json.loads((out/'recipes.json').read_bytes())==json.loads(json.dumps(commands)),'exact five successful producer recipes')
    files=sorted(['native.o','partial.o','native.ll','native.d','recipes.json']+[n+'.log' for n,_ in recipes(llvm,out,language)])
    need(sorted(p.name for p in out.iterdir() if p.name!='verification.json')==files and all(p.is_file() and not p.is_symlink() for p in out.iterdir()),
         'complete exact output inventory')
    for name in ['compile','IR','link']:need(not (out/(name+'.log')).read_bytes(),'empty successful diagnostic '+name)
    for name,artifact in [('object','native.o'),('partial','partial.o')]:
        log=(out/(name+'.log')).read_text();need(str(out/artifact) in log and all(n in log for n in NAMES+UNDEFINED),'actual artifact/symbol dump binding')
    artifacts=[dict(path=portable(str(out/n),ROOT,llvm),size=(out/n).stat().st_size,sha256=digest(out/n)) for n in files]
    controls=elf_negatives(native,partial,official)+ir_md_negatives(text,language,md,llvm,out)
    need(before==inputs(llvm) and all(digest(out/Path(a['path']).name)==a['sha256'] for a in artifacts),'all read input/artifact bytes stable')
    record=dict(schema='TSL9-record-dispatch-native-v2-formal-v1',language=language,firmware_ready=False,target_executed=False,ISA_emulated=False,
       inputs=[dict(path=portable(str(p),ROOT,llvm),size=p.stat().st_size,sha256=v) for p,v in before.items()],
       original=dict(base=0x8000,start=BASE,end=BASE+102,bytes=102,instructions=35,sha256=ORIGINAL_PIN,typed_rows=EXPECTED,
         cfg=cfg_contract(copy.deepcopy(EXPECTED))),native=nf,partial=pf,ir=ir,md_dependencies=deps,recipes=commands,artifacts=artifacts,negative_controls=controls,
       static_contract=dict(architectural_frame_bytes=48,status_reference_symbol=UNDEFINED[0],status_reference_resolved=False,
         known_status_original_observation=dict(start=0x81aa,bytes=6,sha256='887c2bfb847a7e013acebac38c8be3f2bed06fd44305080ad6fc7ca3593e8fc3',
           own_normal_instructions='LBU A0,[GP+167]; RET',not_component_provider_resolution=True),
         metadata_explicit_writes=[dict(SP_offset=20,width=2,value=0),dict(SP_offset=12,width=4,value='fresh zero-extended LHU[S0]'),
           dict(SP_offset=22,width=1,value='fresh LBU[S0+2]')],metadata_unwritten_own_range=[16,20],
         resident=dict(PC=BASE+70,cell=RESIDENT_CELL,RA_continuation=BASE+72,A0='then-live SP+23',A1='then-live S0+3',A2='fresh LBU[S0+2] before call',identity='unknown'),
         peripheral_call=dict(PC=BASE+82,base=PERIPHERAL_BASE,RA_continuation=BASE+86,A1='recomputed then-live SP+12',A2_A3='resident-return residues'),
         exit_A0='path-dependent inherited or callee-return residue; no uniform boolean assignment',ordinary_C_ABI_proven=False),
       limitations=[
        'Only the primary102B/35i extent is proved; the historical182B source window includes other entries not reconstructed here.',
        'Nine FUNC symbols are private physical-register regions and fallthrough boundaries, not ordinary independent C ABI functions.',
        'Actual ET_REL bytes retain nine control immediates and four genuine UND. The6B status observation does not resolve this standalone call or a whole IRQ/ABI contract.',
        'Metadata operations are explicit architecture ports: halfwordSP20, wordSP12, byteSP22. Own code leavesSP16..19 untouched; no standard C structure or full initialization is inferred.',
        'S0/SP/GP and frame contents after opaque calls are then-live physical state. Post-resident A2/A3 are not restored, and numeric SP+12 may differ across the call.',
        'No memcpy, CAN, seat, DND, successful transmission, memory safety, callee effect or peripheral identity is established from these caller operations.',
        'Partial ET_REL has VA0 and pending calls; nominal CFG coordinates are not installed addresses.',
        'No target/ISA/MMIO execution, full firmware BIN, OTA acceptance, complete IRQ/silicon ABI or successful flashing.'])
    record=json.loads(json.dumps(record,ensure_ascii=True))
    encoded=(json.dumps(record,sort_keys=True,indent=2,ensure_ascii=True)+'\n').encode()
    need(not re.search(rb'(?i)(?<![a-z0-9_])[a-z]:[/\\]|/(?:users|home)/',encoded),'portable LF receipt has no host path')
    return record,encoded.decode()


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
    need({int(s[9:]) for s in f if s.startswith('-ffixed-x')}==set(range(1,32))-set(range(10,16)) and '-march=rv32imac_zicsr' in f and '-Oz' in f,
         'unchanged fixed A0..A5 compiler profile; RA/SP/S-registers/T1 reserved')
    exe=lambda n:str(llvm/n);obj=str(out/'native.o');dump=['--mattr=+m,+a,+c,+zicsr','-d','-r','-t','-h']
    return [('compile',[exe('clang.exe'),*f,'-MD','-MF',str(out/'native.d'),'-MT',obj,'-c',str(SOURCE),'-o',obj]),
      ('IR',[exe('clang.exe'),*f,'-S','-emit-llvm',str(SOURCE),'-o',str(out/'native.ll')]),
      ('object',[exe('llvm-objdump.exe'),*dump,obj]),
      ('link',[exe('ld.lld.exe'),'-r','--no-relax','-T',str(HERE/'component.ld'),obj,'-o',str(out/'partial.o')]),
      ('partial',[exe('llvm-objdump.exe'),*dump,str(out/'partial.o')])]

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
    need(out.parent==HERE/'build/verified-v1' and out.name==language,'owned formal v1 record-dispatch output only')
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
    print(json.dumps(dict(result='PASS',language=language,bytes=102,instructions=35,FUNCs=9,UND=4,retained_RELA=9,
       controls=len(record['negative_controls']),receipt_sha256=sha(encoded.encode()),firmware_ready=False)))
    if args.require_firmware_ready:
        print('REJECTED: unresolved indirect/private/silicon ABI and original placement; firmware_ready=false.',file=sys.stderr);return 1
    return 0

if __name__=='__main__':
    try:sys.exit(main())
    except (ValueError,OSError,KeyError,IndexError,StopIteration) as exc:
        print('FAIL: '+str(exc),file=sys.stderr);sys.exit(1)
