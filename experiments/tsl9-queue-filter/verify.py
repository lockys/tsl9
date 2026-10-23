#!/usr/bin/env python3
"""Finite offline 188B filter compiler/replay proof; never execute target code."""
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
SOURCE=HERE/'src/queue_filter.v1.c'
READER=ROOT/'experiments/tsl9-spi-transfer-leaf/verify.py'
FIRMWARE=ROOT/'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
DECODE=ROOT/'analysis/queue-consumer-2026-10-23/next-filter.json'
PINS={SOURCE:'14b1dd7be476e51e4ab53da33008996932e6f94962ab62f13876c44c3413c511',
 HERE/'component.ld':'1682fc10e4039ee7c950870f7c08a533e69a779e36325bd346a74324f39fd728',
 HERE/'probe.py':'5c01e6c9c2a27da9649fe9ba4b57e9675d7cdbc3c0c4112d580f0c590d84fbb4',
 READER:'8c8eb8e01b9fc30eb7150682aa8848e47fe4a1254c6f87b05e657244a11b6de8',
 FIRMWARE:'0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667',
 DECODE:'126704daa831099e311b3a50ac617225b27d32c0bfefcaa9f16c5272399e2e22'}
TOOLS={'clang.exe':'047dfde05acc6fcce5af669e25cd8d40b4f509b8842d151d6d8a43a1c6a35fd6',
 'ld.lld.exe':'fe7f55c0c78b3d87f33b905a3874e10e872ca7beef53a8199d7ff9ac6641ec3f',
 'llvm-objdump.exe':'de40d1188fe63ff373e1a5dd83a12e2cb4545ca3b314da16a476ecf072e5a0fa'}
HEADER_PIN='7ce5540d5fb6e8da9760928e76cbdd5ebef329d701ad598d30d8e6f9d5d78b34'
ELF_PINS={True:'57bc33780d5860e47d5709c313092923fdbc12890a0070d0492cfa3e67745f20',
 False:'4aec21de70e609dc851ff4ac1d6f13db2eb89ea559c7c15137109c3789eb06af'}
IR_PINS={'c':'602ccf9ef2f2ab744a49b62cee82a7a54fbcb7d345e4699b31bf4564ae30163e',
 'cpp':'5de3348cf6de7d98c80b3d341e86bc9656ab9ba45bde63c9ea4ad600ec4e4869'}
BASE=0x82d2
ORIGINAL_PIN='7a49eb89a2c698b0a9d4a97083329c2a12e200c1f27fbdadec16784a6edb0e30'
NAMES=['tsl9_queue_external_82d2','tsl9_filter_scan_8308','tsl9_filter_pack_8328','tsl9_filter_emit_8358',
 'tsl9_filter_test_836a','tsl9_filter_finish_836e','tsl9_filter_second_838a']
REGIONS=list(zip(NAMES,[0,54,86,134,152,156,184],[54,32,48,18,4,28,4]))
UNDEFINED=['tsl9_filter_external_8a56']
RELATIONS=[(64,16,NAMES[4]),(72,16,NAMES[4]),(84,44,NAMES[4]),(92,16,NAMES[4]),
 (150,45,UNDEFINED[0]),(152,16,NAMES[6]),(186,45,NAMES[1])]
MASKS={16:(4,0x01fff07f),44:(2,0xe383),45:(2,0xe003)}
# Literal typed rows/SSA/metadata are calibrated from pinned real artifacts
# and then independently checked against the original BIN and bit decoder.
EXPECTED = [[0, 2, 'ADDI', 2, 2, -64], [2, 2, 'SW32', 19, 2, 44], [4, 2, 'LUI', 19, 65536], [6, 2, 'SW32', 9, 2, 52], [8, 2, 'SW32', 18, 2, 48], [10, 2, 'SW32', 20, 2, 40], [12, 2, 'SW32', 21, 2, 36], [14, 2, 'SW32', 22, 2, 32], [16, 2, 'SW32', 23, 2, 28], [18, 2, 'SW32', 24, 2, 24], [20, 2, 'SW32', 25, 2, 20], [22, 2, 'SW32', 1, 2, 60], [24, 2, 'SW32', 8, 2, 56], [26, 2, 'MV', 9, 10], [28, 2, 'ADDI', 18, 0, 0], [30, 2, 'ADDI', 20, 0, 0], [32, 4, 'AUIPC', 21, 536887296], [36, 4, 'ADDI', 21, 21, 1186], [40, 2, 'ADDI', 19, 19, -2], [42, 2, 'ADDI', 22, 0, 2], [44, 2, 'ADDI', 23, 0, 8], [46, 4, 'ADDI', 24, 10, 3], [50, 4, 'LUI', 25, 262144], [54, 4, 'SLLI', 8, 18, 2], [58, 2, 'ADD', 8, 8, 21], [60, 4, 'LHU16', 15, 8, 2], [64, 4, 'BEQ', 19, 15, 33642], [68, 4, 'LBU8', 15, 8, 5], [72, 4, 'BNE', 22, 15, 33642], [76, 4, 'LBU8', 15, 8, 4], [80, 4, 'ANDI', 15, 15, 255], [84, 2, 'BEQZ', 15, 33642], [86, 4, 'LBU8', 12, 9, 2], [90, 2, 'MV', 20, 15], [92, 4, 'BLTU', 23, 12, 33642], [96, 4, 'LHU16', 13, 9, 0], [100, 4, 'LBU8', 15, 9, 11], [104, 2, 'MV', 11, 24], [106, 4, 'SB8', 13, 2, 5], [110, 4, 'SLLI', 14, 15, 4], [114, 4, 'SRLI', 15, 13, 8], [118, 2, 'OR', 15, 15, 14], [120, 4, 'SB8', 15, 2, 4], [124, 4, 'LW32', 15, 25, 76], [128, 4, 'ADDI', 10, 2, 6], [132, 2, 'JALR', 1, 15, 0], [134, 4, 'LBU8', 13, 9, 2], [138, 4, 'LHU16', 10, 8, 2], [142, 2, 'ADDI', 12, 2, 4], [144, 2, 'ADDI', 13, 13, 2], [146, 4, 'ADDI', 11, 0, 192], [150, 2, 'JAL', 1, 35414], [152, 4, 'BEQ', 18, 0, 33674], [156, 2, 'LW32', 1, 2, 60], [158, 2, 'LW32', 8, 2, 56], [160, 2, 'MV', 10, 20], [162, 2, 'LW32', 9, 2, 52], [164, 2, 'LW32', 18, 2, 48], [166, 2, 'LW32', 19, 2, 44], [168, 2, 'LW32', 20, 2, 40], [170, 2, 'LW32', 21, 2, 36], [172, 2, 'LW32', 22, 2, 32], [174, 2, 'LW32', 23, 2, 28], [176, 2, 'LW32', 24, 2, 24], [178, 2, 'LW32', 25, 2, 20], [180, 2, 'ADDI', 2, 2, 64], [182, 2, 'RET', 1], [184, 2, 'ADDI', 18, 0, 1], [186, 2, 'J', 33544]]
SCHEMAS = {'native': {'header': [1, 243, 1, 0, 0, 1244, 1, 52, 0, 0, 40, 20, 1], 'program_headers': [], 'sections': [{'name_offset': 0, 'type': 0, 'flags': 0, 'address': 0, 'offset': 0, 'size': 0, 'link': 0, 'info': 0, 'align': 0, 'entsize': 0, 'index': 0, 'name': ''}, {'name_offset': 112, 'type': 3, 'flags': 0, 'address': 0, 'offset': 847, 'size': 397, 'link': 0, 'info': 0, 'align': 1, 'entsize': 0, 'index': 1, 'name': '.strtab'}, {'name_offset': 1, 'type': 1, 'flags': 6, 'address': 0, 'offset': 52, 'size': 0, 'link': 0, 'info': 0, 'align': 2, 'entsize': 0, 'index': 2, 'name': '.text'}, {'name_offset': 351, 'type': 1, 'flags': 6, 'address': 0, 'offset': 52, 'size': 54, 'link': 0, 'info': 0, 'align': 2, 'entsize': 0, 'index': 3, 'name': '.text.tsl9_queue_external_82d2'}, {'name_offset': 267, 'type': 1, 'flags': 6, 'address': 0, 'offset': 106, 'size': 32, 'link': 0, 'info': 0, 'align': 2, 'entsize': 0, 'index': 4, 'name': '.text.tsl9_filter_scan_8308'}, {'name_offset': 262, 'type': 4, 'flags': 64, 'address': 0, 'offset': 756, 'size': 36, 'link': 19, 'info': 4, 'align': 4, 'entsize': 12, 'index': 5, 'name': '.rela.text.tsl9_filter_scan_8308'}, {'name_offset': 234, 'type': 1, 'flags': 6, 'address': 0, 'offset': 138, 'size': 48, 'link': 0, 'info': 0, 'align': 2, 'entsize': 0, 'index': 6, 'name': '.text.tsl9_filter_pack_8328'}, {'name_offset': 229, 'type': 4, 'flags': 64, 'address': 0, 'offset': 792, 'size': 12, 'link': 19, 'info': 6, 'align': 4, 'entsize': 12, 'index': 7, 'name': '.rela.text.tsl9_filter_pack_8328'}, {'name_offset': 201, 'type': 1, 'flags': 6, 'address': 0, 'offset': 186, 'size': 18, 'link': 0, 'info': 0, 'align': 2, 'entsize': 0, 'index': 8, 'name': '.text.tsl9_filter_emit_8358'}, {'name_offset': 196, 'type': 4, 'flags': 64, 'address': 0, 'offset': 804, 'size': 12, 'link': 19, 'info': 8, 'align': 4, 'entsize': 12, 'index': 9, 'name': '.rela.text.tsl9_filter_emit_8358'}, {'name_offset': 168, 'type': 1, 'flags': 6, 'address': 0, 'offset': 204, 'size': 4, 'link': 0, 'info': 0, 'align': 2, 'entsize': 0, 'index': 10, 'name': '.text.tsl9_filter_test_836a'}, {'name_offset': 163, 'type': 4, 'flags': 64, 'address': 0, 'offset': 816, 'size': 12, 'link': 19, 'info': 10, 'align': 4, 'entsize': 12, 'index': 11, 'name': '.rela.text.tsl9_filter_test_836a'}, {'name_offset': 64, 'type': 1, 'flags': 6, 'address': 0, 'offset': 208, 'size': 28, 'link': 0, 'info': 0, 'align': 2, 'entsize': 0, 'index': 12, 'name': '.text.tsl9_filter_finish_836e'}, {'name_offset': 133, 'type': 1, 'flags': 6, 'address': 0, 'offset': 236, 'size': 4, 'link': 0, 'info': 0, 'align': 2, 'entsize': 0, 'index': 13, 'name': '.text.tsl9_filter_second_838a'}, {'name_offset': 128, 'type': 4, 'flags': 64, 'address': 0, 'offset': 828, 'size': 12, 'link': 19, 'info': 13, 'align': 4, 'entsize': 12, 'index': 14, 'name': '.rela.text.tsl9_filter_second_838a'}, {'name_offset': 7, 'type': 1, 'flags': 48, 'address': 0, 'offset': 240, 'size': 159, 'link': 0, 'info': 0, 'align': 1, 'entsize': 1, 'index': 15, 'name': '.comment'}, {'name_offset': 34, 'type': 1, 'flags': 0, 'address': 0, 'offset': 399, 'size': 0, 'link': 0, 'info': 0, 'align': 1, 'entsize': 0, 'index': 16, 'name': '.note.GNU-stack'}, {'name_offset': 16, 'type': 1879048195, 'flags': 0, 'address': 0, 'offset': 399, 'size': 52, 'link': 0, 'info': 0, 'align': 1, 'entsize': 0, 'index': 17, 'name': '.riscv.attributes'}, {'name_offset': 50, 'type': 1879002115, 'flags': 2147483648, 'address': 0, 'offset': 840, 'size': 7, 'link': 19, 'info': 0, 'align': 1, 'entsize': 0, 'index': 18, 'name': '.llvm_addrsig'}, {'name_offset': 120, 'type': 2, 'flags': 0, 'address': 0, 'offset': 452, 'size': 304, 'link': 1, 'info': 11, 'align': 4, 'entsize': 16, 'index': 19, 'name': '.symtab'}], 'symbols': [{'index': 0, 'name': '', 'value': 0, 'size': 0, 'info': 0, 'other': 0, 'section': 0}, {'index': 1, 'name': 'queue_filter.v1.c', 'value': 0, 'size': 0, 'info': 4, 'other': 0, 'section': 65521}, {'index': 2, 'name': '$x.0', 'value': 0, 'size': 0, 'info': 0, 'other': 0, 'section': 3}, {'index': 3, 'name': '$x.1', 'value': 0, 'size': 0, 'info': 0, 'other': 0, 'section': 4}, {'index': 4, 'name': '$x.2', 'value': 0, 'size': 0, 'info': 0, 'other': 0, 'section': 6}, {'index': 5, 'name': '$x.3', 'value': 0, 'size': 0, 'info': 0, 'other': 0, 'section': 8}, {'index': 6, 'name': '$x.4', 'value': 0, 'size': 0, 'info': 0, 'other': 0, 'section': 10}, {'index': 7, 'name': '$x.5', 'value': 0, 'size': 0, 'info': 0, 'other': 0, 'section': 12}, {'index': 8, 'name': '$x.6', 'value': 0, 'size': 0, 'info': 0, 'other': 0, 'section': 13}, {'index': 9, 'name': '$d.7', 'value': 0, 'size': 0, 'info': 0, 'other': 0, 'section': 15}, {'index': 10, 'name': '$d.8', 'value': 0, 'size': 0, 'info': 0, 'other': 0, 'section': 17}, {'index': 11, 'name': 'tsl9_queue_external_82d2', 'value': 0, 'size': 54, 'info': 18, 'other': 0, 'section': 3}, {'index': 12, 'name': 'tsl9_filter_scan_8308', 'value': 0, 'size': 32, 'info': 18, 'other': 0, 'section': 4}, {'index': 13, 'name': 'tsl9_filter_test_836a', 'value': 0, 'size': 4, 'info': 18, 'other': 0, 'section': 10}, {'index': 14, 'name': 'tsl9_filter_pack_8328', 'value': 0, 'size': 48, 'info': 18, 'other': 0, 'section': 6}, {'index': 15, 'name': 'tsl9_filter_emit_8358', 'value': 0, 'size': 18, 'info': 18, 'other': 0, 'section': 8}, {'index': 16, 'name': 'tsl9_filter_external_8a56', 'value': 0, 'size': 0, 'info': 16, 'other': 0, 'section': 0}, {'index': 17, 'name': 'tsl9_filter_second_838a', 'value': 0, 'size': 4, 'info': 18, 'other': 0, 'section': 13}, {'index': 18, 'name': 'tsl9_filter_finish_836e', 'value': 0, 'size': 28, 'info': 18, 'other': 0, 'section': 12}], 'relocations': [{'section': 4, 'offset': 10, 'type': 16, 'symbol': 13, 'addend': 0}, {'section': 4, 'offset': 18, 'type': 16, 'symbol': 13, 'addend': 0}, {'section': 4, 'offset': 30, 'type': 44, 'symbol': 13, 'addend': 0}, {'section': 6, 'offset': 6, 'type': 16, 'symbol': 13, 'addend': 0}, {'section': 8, 'offset': 16, 'type': 45, 'symbol': 16, 'addend': 0}, {'section': 10, 'offset': 0, 'type': 16, 'symbol': 17, 'addend': 0}, {'section': 13, 'offset': 2, 'type': 45, 'symbol': 12, 'addend': 0}], 'noncode_section_hashes': {'': 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855', '.strtab': 'ddce2735474465f98ebc0eb9a50f8250c7034a3f493d80326f5aea939a0ce690', '.rela.text.tsl9_filter_scan_8308': '6752872dfe72be118e21a2443915c5a63c4bacf018ff231782f393fb55f60f4d', '.rela.text.tsl9_filter_pack_8328': '409766f5477c303ac039e77e075afdd593ecfa3c003283a508ed8ead63050791', '.rela.text.tsl9_filter_emit_8358': 'b71572f973a6618c2f4e496209429c4438f0ba10923b6edfcdf47228ca8204a6', '.rela.text.tsl9_filter_test_836a': '8cbd3d6ee14243e11cdd66bd46ea76b947dfb024c4d0f90d4fc23b4537f31b4a', '.rela.text.tsl9_filter_second_838a': 'dcd4525204b852623a9fb16aefd0769b3d54190d9859cebe72377adb7dda29e2', '.comment': '72c64fbc17a5d9f46f33ac0650b7d4f549d87c2ba9e77ebd765a25a3960e3017', '.note.GNU-stack': 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855', '.riscv.attributes': 'f2bd85b0ab58609a20dbdef6cc6e3f2dd1a34cdcb554580710aa3819cd24ad71', '.llvm_addrsig': '3ba56241c4e81a3b379da3a681c492ce9fe7a713d7bfe5617198fdc4c840baf5', '.symtab': '09f9b58d72f3b36755658eea3ccfad961a915f8d58eceb5b566477567c12c6f5'}, 'outside_allocated_code_sha256': '52ed16cf0cc89bcede6f812e6a79d2504dab0f39f42deb2ea324b4274dbb8cde'}, 'partial': {'header': [1, 243, 1, 0, 0, 984, 1, 52, 0, 0, 40, 8, 6], 'program_headers': [], 'sections': [{'name_offset': 0, 'type': 0, 'flags': 0, 'address': 0, 'offset': 0, 'size': 0, 'link': 0, 'info': 0, 'align': 0, 'entsize': 0, 'index': 0, 'name': ''}, {'name_offset': 1, 'type': 1, 'flags': 6, 'address': 0, 'offset': 52, 'size': 188, 'link': 0, 'info': 0, 'align': 2, 'entsize': 0, 'index': 1, 'name': '.filter'}, {'name_offset': 9, 'type': 1, 'flags': 6, 'address': 0, 'offset': 240, 'size': 0, 'link': 0, 'info': 0, 'align': 2, 'entsize': 0, 'index': 2, 'name': '.text'}, {'name_offset': 15, 'type': 4, 'flags': 64, 'address': 0, 'offset': 240, 'size': 84, 'link': 5, 'info': 1, 'align': 4, 'entsize': 12, 'index': 3, 'name': '.rela.filter'}, {'name_offset': 28, 'type': 1879002115, 'flags': 2147483648, 'address': 0, 'offset': 324, 'size': 7, 'link': 0, 'info': 0, 'align': 1, 'entsize': 0, 'index': 4, 'name': '.llvm_addrsig'}, {'name_offset': 42, 'type': 2, 'flags': 0, 'address': 0, 'offset': 332, 'size': 336, 'link': 7, 'info': 13, 'align': 4, 'entsize': 16, 'index': 5, 'name': '.symtab'}, {'name_offset': 50, 'type': 3, 'flags': 0, 'address': 0, 'offset': 668, 'size': 68, 'link': 0, 'info': 0, 'align': 1, 'entsize': 0, 'index': 6, 'name': '.shstrtab'}, {'name_offset': 60, 'type': 3, 'flags': 0, 'address': 0, 'offset': 736, 'size': 246, 'link': 0, 'info': 0, 'align': 1, 'entsize': 0, 'index': 7, 'name': '.strtab'}], 'symbols': [{'index': 0, 'name': '', 'value': 0, 'size': 0, 'info': 0, 'other': 0, 'section': 0}, {'index': 1, 'name': 'queue_filter.v1.c', 'value': 0, 'size': 0, 'info': 4, 'other': 0, 'section': 65521}, {'index': 2, 'name': '$x.0', 'value': 0, 'size': 0, 'info': 0, 'other': 0, 'section': 1}, {'index': 3, 'name': '$x.1', 'value': 54, 'size': 0, 'info': 0, 'other': 0, 'section': 1}, {'index': 4, 'name': '$x.2', 'value': 86, 'size': 0, 'info': 0, 'other': 0, 'section': 1}, {'index': 5, 'name': '$x.3', 'value': 134, 'size': 0, 'info': 0, 'other': 0, 'section': 1}, {'index': 6, 'name': '$x.4', 'value': 152, 'size': 0, 'info': 0, 'other': 0, 'section': 1}, {'index': 7, 'name': '$x.5', 'value': 156, 'size': 0, 'info': 0, 'other': 0, 'section': 1}, {'index': 8, 'name': '$x.6', 'value': 184, 'size': 0, 'info': 0, 'other': 0, 'section': 1}, {'index': 9, 'name': '$d.8', 'value': 0, 'size': 0, 'info': 0, 'other': 0, 'section': 65521}, {'index': 10, 'name': '', 'value': 0, 'size': 0, 'info': 3, 'other': 0, 'section': 1}, {'index': 11, 'name': '', 'value': 0, 'size': 0, 'info': 3, 'other': 0, 'section': 2}, {'index': 12, 'name': '', 'value': 0, 'size': 0, 'info': 3, 'other': 0, 'section': 4}, {'index': 13, 'name': 'tsl9_queue_external_82d2', 'value': 0, 'size': 54, 'info': 18, 'other': 0, 'section': 1}, {'index': 14, 'name': 'tsl9_filter_scan_8308', 'value': 54, 'size': 32, 'info': 18, 'other': 0, 'section': 1}, {'index': 15, 'name': 'tsl9_filter_test_836a', 'value': 152, 'size': 4, 'info': 18, 'other': 0, 'section': 1}, {'index': 16, 'name': 'tsl9_filter_pack_8328', 'value': 86, 'size': 48, 'info': 18, 'other': 0, 'section': 1}, {'index': 17, 'name': 'tsl9_filter_emit_8358', 'value': 134, 'size': 18, 'info': 18, 'other': 0, 'section': 1}, {'index': 18, 'name': 'tsl9_filter_external_8a56', 'value': 0, 'size': 0, 'info': 16, 'other': 0, 'section': 0}, {'index': 19, 'name': 'tsl9_filter_second_838a', 'value': 184, 'size': 4, 'info': 18, 'other': 0, 'section': 1}, {'index': 20, 'name': 'tsl9_filter_finish_836e', 'value': 156, 'size': 28, 'info': 18, 'other': 0, 'section': 1}], 'relocations': [{'section': 1, 'offset': 64, 'type': 16, 'symbol': 15, 'addend': 0}, {'section': 1, 'offset': 72, 'type': 16, 'symbol': 15, 'addend': 0}, {'section': 1, 'offset': 84, 'type': 44, 'symbol': 15, 'addend': 0}, {'section': 1, 'offset': 92, 'type': 16, 'symbol': 15, 'addend': 0}, {'section': 1, 'offset': 150, 'type': 45, 'symbol': 18, 'addend': 0}, {'section': 1, 'offset': 152, 'type': 16, 'symbol': 19, 'addend': 0}, {'section': 1, 'offset': 186, 'type': 45, 'symbol': 14, 'addend': 0}], 'noncode_section_hashes': {'': 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855', '.rela.filter': '665ff89f36311d217805723daefe273fe57728e26333105af75883a331421bdf', '.llvm_addrsig': '3ba56241c4e81a3b379da3a681c492ce9fe7a713d7bfe5617198fdc4c840baf5', '.symtab': '22db5edab95c8d171ca34c9986235406969bc28b562bf7b47a9bed08826b6807', '.shstrtab': '9241ad7af6ae2012f3bf2a5c816daa948f47c61255b1b53e44c77109d7473705', '.strtab': 'ee9db3808f7cdab1fece450bf2623faeae8b31faad2167518625725a11a9a6e0'}, 'outside_allocated_code_sha256': '56777a9da7474e4f278b03982d2b6be6746b26f8b7e203da930b3db88bd7c84b'}}
IR_CORE = {'tsl9_queue_external_82d2': ['tail call void asm sideeffect "addi sp, sp, -64\\0Asw s3, 44(sp)\\0Alui s3, 0x10\\0Asw s1, 52(sp)\\0Asw s2, 48(sp)\\0Asw s4, 40(sp)\\0Asw s5, 36(sp)\\0Asw s6, 32(sp)\\0Asw s7, 28(sp)\\0Asw s8, 24(sp)\\0Asw s9, 20(sp)\\0Asw ra, 60(sp)\\0Asw s0, 56(sp)\\0Amv s1, a0\\0Ali s2, 0\\0Ali s4, 0\\0Aauipc s5, 0x20004\\0Aaddi s5, s5, 1186\\0Aaddi s3, s3, -2\\0Ali s6, 2\\0Ali s7, 8\\0Aaddi s8, a0, 3\\0Alui s9, 0x40\\0A", ""() #2', 'unreachable'], 'tsl9_filter_scan_8308': ['%1 = tail call i32 asm sideeffect "slli s0, s2, 2\\0Aadd s0, s0, s5\\0Alhu a5, 2(s0)\\0A", "={x15},~{memory}"() #2', 'tail call void asm sideeffect ".Lfilter_sentinel:\\0Abeq s3, a5, .Lfilter_sentinel\\0A.reloc .-4, R_RISCV_BRANCH, tsl9_filter_test_836a\\0A", "{x15},~{memory}"(i32 %1) #2', '%2 = tail call i32 asm sideeffect "lbu a5, 5(s0)\\0A", "={x15},~{memory}"() #2', 'tail call void asm sideeffect ".Lfilter_kind:\\0Abne s6, a5, .Lfilter_kind\\0A.reloc .-4, R_RISCV_BRANCH, tsl9_filter_test_836a\\0A", "{x15},~{memory}"(i32 %2) #2', '%3 = tail call i32 asm sideeffect "lbu a5, 4(s0)\\0A", "={x15},~{memory}"() #2', '%4 = and i32 %3, 255', 'tail call void asm sideeffect ".Lfilter_disabled:\\0Ac.beqz a5, .Lfilter_disabled\\0A.reloc .-2, R_RISCV_RVC_BRANCH, tsl9_filter_test_836a\\0A", "{x15},~{memory}"(i32 %4) #2', 'unreachable'], 'tsl9_filter_pack_8328': ['%1 = tail call i32 asm sideeffect "", "={x15},~{memory}"() #2', '%2 = tail call i32 asm sideeffect "lbu a2, 2(s1)\\0Amv s4, a5\\0A", "={x12},{x15},~{memory}"(i32 %1) #2', 'tail call void asm sideeffect ".Lfilter_long:\\0Abltu s7, a2, .Lfilter_long\\0A.reloc .-4, R_RISCV_BRANCH, tsl9_filter_test_836a\\0A", "{x12},~{memory}"(i32 %2) #2', '%3 = tail call { i32, i32 } asm sideeffect "lhu a3, 0(s1)\\0Albu a5, 11(s1)\\0Amv a1, s8\\0Asb a3, 5(sp)\\0A", "={x13},={x15},{x12},~{x11},~{memory}"(i32 %2) #2', '%4 = extractvalue { i32, i32 } %3, 0', '%5 = extractvalue { i32, i32 } %3, 1', '%6 = shl i32 %5, 4', '%7 = tail call { i32, i32, i32 } asm sideeffect "", "={x14},={x15},={x13},{x12},{x14},{x15},{x13},~{memory}"(i32 %2, i32 %6, i32 %5, i32 %4) #2', '%8 = extractvalue { i32, i32, i32 } %7, 0', '%9 = extractvalue { i32, i32, i32 } %7, 2', '%10 = lshr i32 %9, 8', '%11 = tail call { i32, i32, i32 } asm sideeffect "", "={x15},={x14},={x13},{x12},{x15},{x14},{x13},~{memory}"(i32 %2, i32 %10, i32 %8, i32 %9) #2', '%12 = extractvalue { i32, i32, i32 } %11, 0', '%13 = extractvalue { i32, i32, i32 } %11, 1', '%14 = extractvalue { i32, i32, i32 } %11, 2', '%15 = or i32 %12, %13', '%16 = tail call i32 asm sideeffect "sb a5, 4(sp)\\0Alw a5, 76(s9)\\0Aaddi a0, sp, 6\\0A", "={x15},{x12},{x13},{x14},{x15},~{x10},~{memory}"(i32 %2, i32 %14, i32 %13, i32 %15) #2', 'tail call void asm sideeffect "jalr a5\\0A", "{x15},{x12},~{x10},~{x11},~{x13},~{x14},~{memory}"(i32 %16, i32 %2) #2', 'unreachable'], 'tsl9_filter_emit_8358': ['%1 = tail call i32 asm sideeffect "lbu a3, 2(s1)\\0Alhu a0, 2(s0)\\0Aaddi a2, sp, 4\\0A", "={x13},~{x10},~{x12},~{memory}"() #2', '%2 = add i32 %1, 2', '%3 = tail call i32 asm sideeffect "", "={x13},{x13},~{memory}"(i32 %2) #2', 'tail call void asm sideeffect ".Lfilter_emit:\\0Ac.jal .Lfilter_emit\\0A.reloc .-2, R_RISCV_RVC_JUMP, tsl9_filter_external_8a56\\0A", "{x11},{x13},~{x10},~{x12},~{x14},~{x15},~{memory}"(i32 192, i32 %3) #2', 'unreachable'], 'tsl9_filter_test_836a': ['tail call void asm sideeffect ".Lfilter_second:\\0Abeq s2, zero, .Lfilter_second\\0A.reloc .-4, R_RISCV_BRANCH, tsl9_filter_second_838a\\0A", "~{memory}"() #2', 'unreachable'], 'tsl9_filter_finish_836e': ['tail call void asm sideeffect "lw ra, 60(sp)\\0Alw s0, 56(sp)\\0Amv a0, s4\\0Alw s1, 52(sp)\\0Alw s2, 48(sp)\\0Alw s3, 44(sp)\\0Alw s4, 40(sp)\\0Alw s5, 36(sp)\\0Alw s6, 32(sp)\\0Alw s7, 28(sp)\\0Alw s8, 24(sp)\\0Alw s9, 20(sp)\\0Aaddi sp, sp, 64\\0Aret\\0A", ""() #2', 'unreachable'], 'tsl9_filter_second_838a': ['tail call void asm sideeffect "li s2, 1\\0A.Lfilter_scan:\\0Ac.j .Lfilter_scan\\0A.reloc .-2, R_RISCV_RVC_JUMP, tsl9_filter_scan_8308\\0A", ""() #2', 'unreachable']}


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
            elif op==0x13 and f3==7:ins=['ANDI',rd,rs,sx(w>>20,12)]
            elif op==0x13 and f3==0:ins=['ADDI',rd,rs,sx(w>>20,12)]
            elif op==3 and f3 in (2,4,5):ins=[{2:'LW32',4:'LBU8',5:'LHU16'}[f3],rd,rs,sx(w>>20,12)]
            elif op==0x23 and f3 in (0,1,2):
                offset=((w>>25)<<5)|((w>>7)&31);ins=[{0:'SB8',1:'SH16',2:'SW32'}[f3],rs2,rs,sx(offset,12)]
            elif op==0x33 and f3==0 and w>>25==1:ins=['MUL',rd,rs,rs2]
            elif op==0x73 and f3 in (2,3):ins=['CSRRS' if f3==2 else 'CSRRC',rd,w>>20,rs]
            elif op==0x63 and f3 in (0,1,6):
                imm=((w>>31)<<12)|(((w>>7)&1)<<11)|(((w>>25)&63)<<5)|(((w>>8)&15)<<1)
                ins=[{0:'BEQ',1:'BNE',6:'BLTU'}[f3],rs,rs2,BASE+at+sx(imm,13)]
            elif op==0x6f:
                imm=((w>>31)<<20)|(((w>>21)&1023)<<1)|(((w>>20)&1)<<11)|(((w>>12)&255)<<12)
                ins=['JAL',rd,BASE+at+sx(imm,21)]
            else:raise ValueError('wide opcode/width outside exact bounded filter instruction families')
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
            elif q==2 and f3==4 and (w>>12)&1 and rd and not rs2:ins=['JALR',1,rd,0]
            elif q==2 and f3==4 and not (w>>12)&1 and rd and rs2:ins=['MV',rd,rs2]
            elif q==2 and f3==4 and (w>>12)&1 and rd and rs2:ins=['ADD',rd,rd,rs2]
            elif q==1 and f3 in (6,7):
                n=(((w>>12)&1)<<8)|(((w>>10)&3)<<3)|(((w>>5)&3)<<6)|(((w>>3)&3)<<1)|(((w>>2)&1)<<5)
                ins=['BEQZ' if f3==6 else 'BNEZ',8+((w>>7)&7),BASE+at+sx(n,9)]
            elif q==1 and f3 in (1,5):
                n=(((w>>12)&1)<<11)|(((w>>11)&1)<<4)|(((w>>9)&3)<<8)|(((w>>8)&1)<<10)|(((w>>7)&1)<<6)|(((w>>6)&1)<<7)|(((w>>3)&7)<<1)|(((w>>2)&1)<<5)
                ins=['JAL',1,BASE+at+sx(n,12)] if f3==1 else ['J',BASE+at+sx(n,12)]
            else:raise ValueError('compressed opcode/width outside exact bounded filter families')
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


def recipes(llvm,out,language):
    f=runpy.run_path(str(HERE/'probe.py'))['flags'](language)
    need({int(s[9:]) for s in f if s.startswith('-ffixed-x')}==set(range(1,32))-set(range(10,16)) and '-march=rv32imac_zicsr' in f and '-Oz' in f,
         'unchanged fixed compiler profile; reserved RA/SP/S-register bank')
    exe=lambda n:str(llvm/n);obj=str(out/'native.o');dump=['--mattr=+m,+a,+c,+zicsr','-d','-r','-t','-h']
    return [('compile',[exe('clang.exe'),*f,'-MD','-MF',str(out/'native.d'),'-MT',obj,'-c',str(SOURCE),'-o',obj]),
      ('IR',[exe('clang.exe'),*f,'-S','-emit-llvm',str(SOURCE),'-o',str(out/'native.ll')]),
      ('object',[exe('llvm-objdump.exe'),*dump,obj]),
      ('link',[exe('ld.lld.exe'),'-r','--no-relax','-T',str(HERE/'component.ld'),obj,'-o',str(out/'partial.o')]),
      ('partial',[exe('llvm-objdump.exe'),*dump,str(out/'partial.o')])]


def inputs(llvm):
    expected=dict(PINS);expected[Path(__file__).resolve()]=digest(__file__)
    expected[llvm.parent/'lib/clang/18/include/stdint.h']=HEADER_PIN
    expected.update({llvm/n:pin for n,pin in TOOLS.items()})
    need(all(digest(p)==pin for p,pin in expected.items()),'all source/decode/reader/probe/tool/header pins')
    for path in [SOURCE,HERE/'component.ld',HERE/'probe.py']:
        raw=path.read_bytes();need(b'\r' not in raw and raw.endswith(b'\n') and not raw.endswith(b'\n\n'),'frozen LF source/probe/linker each have exactly one EOF LF')
    return expected


def typed_contract(rows,pending):
    expected=copy.deepcopy(EXPECTED)
    if pending:
        for row in expected:
            if row[0] in {r[0] for r in RELATIONS}:row[-1]=BASE+row[0]
    need(rows==expected,'all69 typed widths/physical operands/order/control targets')
    at={r[0]:r for r in rows}
    need(at[0]==[0,2,'ADDI',2,2,-64] and at[180]==[180,2,'ADDI',2,2,64] and at[182]==[182,2,'RET',1],
         'original64B architectural frame and return')
    need(at[90]==[90,2,'MV',20,15] and at[92][2:5]==['BLTU',23,12],
         'S4 is assigned before the unsigned length rejection; nonzero is not a forwarding proof')
    need(at[132]==[132,2,'JALR',1,15,0] and at[150][0:4]==[150,2,'JAL',1],
         'C.JALR and C.JAL both actually link RA, despite RVC_JUMP relocation45')
    need(at[186][0:3]==[186,2,'J'],'cold local C.J does not link RA')
    need([at[p] for p in (134,138,142)]==[[134,4,'LBU8',13,9,2],[138,4,'LHU16',10,8,2],[142,2,'ADDI',12,2,4]],
         'postopaque fresh S1/S0/SP inputs are physical, not cached C values')
    need(at[124]==[124,4,'LW32',15,25,76] and at[104]==[104,2,'MV',11,24] and at[160]==[160,2,'MV',10,20],
         'fresh then-live S9 pointer and S8 payload source, return from then-live S4')
    return rows


def original():
    raw=FIRMWARE.read_bytes();need(len(raw)==76800 and sha(raw)==PINS[FIRMWARE],'whole original BIN')
    code=raw[BASE-0x8000:BASE-0x8000+188];need(sha(code)==ORIGINAL_PIN,'original188B span identity')
    typed_contract(decode(code),False)
    need(digest(DECODE)==PINS[DECODE],'pinned independent static decode')
    evidence=json.loads(DECODE.read_bytes());rows=evidence['rows']
    need((int(evidence['start'],0),int(evidence['end_exclusive'],0),evidence['bytes'],evidence['instructions'],evidence['span_sha256'])==
         (BASE,BASE+188,188,69,ORIGINAL_PIN) and int(evidence['mapping_base'],0)==0x8000 and evidence['firmware_sha256']==PINS[FIRMWARE],
         'decode bounds/identity')
    need(b''.join(bytes.fromhex(r['bytes']) for r in rows)==code and
         [(r['addr']-BASE,r['size']) for r in rows]==[(r[0],r[1]) for r in EXPECTED],'complete original decode row coverage')
    return code


def masks():
    result=bytearray(b'\xff'*188)
    for at,kind,_ in RELATIONS:
        n,mask=MASKS[kind];result[at:at+n]=mask.to_bytes(n,'little')
    return result


def elf_contract(e,native,official,full=True):
    schema=SCHEMAS['native' if native else 'partial']
    need(len(e.raw)==schema['header'][5]+40*schema['header'][11],'complete ELF extent without unbound trailing bytes')
    need(e.header[0]==1 and e.header[6]==1 and not e.program_headers,'actual RV32 RVC ET_REL only')
    gs=[s for s in e.symbols if s['info']>>4]
    expected={n:(0 if native else at,z,18,0,'.text.'+n if native else '.filter') for n,at,z in REGIONS}
    actual={s['name']:(s['value'],s['size'],s['info'],s['other'],e.sections[s['section']]['name']) for s in gs if s['section'] not in (0,65521)}
    need(actual==expected and len(gs)==8,'seven genuine FUNCs with exact order/region ownership/extent')
    und=[s for s in gs if s['section']==0]
    need([s['name'] for s in und]==UNDEFINED and all(s['info']==16 and s['other']==s['size']==s['value']==0 for s in und)
         and not any(s['section']==65521 for s in gs),'one genuine strong UND; no ABS/weak/fake provider')
    alloc=[s for s in e.sections if s['flags']&2 and s['size']]
    need([(s['name'],s['address'],s['size'],s['type'],s['flags'],s['align']) for s in alloc]==
       ([('.text.'+n,0,z,1,6,2) for n,_,z in REGIONS] if native else [('.filter',0,188,1,6,2)]),'exact AX-only allocation')
    code=b''.join(e.data('.text.'+n) for n in NAMES) if native else e.data('.filter')
    rows=typed_contract(decode(code),True);need(len(code)==188 and len(rows)==69,'188B69i')
    starts={'.text.'+n:at for n,at,_ in REGIONS};rels=[]
    for r in e.relocations:
        owner=e.sections[r['section']]['name'];symbol=e.symbols[r['symbol']]
        need(owner in starts if native else owner=='.filter','genuine relocation owner')
        offset=r['offset']+(starts[owner] if native else 0);rels.append((offset,r['type'],symbol['name'],r['addend']))
        if symbol['name'] in UNDEFINED:
            need(symbol['info']==16 and symbol['section']==0 and offset==150 and r['type']==45,
                 'genuine UND target of the compressed RA-linking call')
        else:need(symbol['info']==18 and symbol['section'] not in (0,65521),'six genuine defined architectural control targets')
    need(rels==[(a,k,n,0) for a,k,n in RELATIONS],'all seven relocation sites/types/targets/addends')
    bitmasks=masks();need(all(not ((a^b)&mask) for a,b,mask in zip(code,official,bitmasks)),
         'all original nonrelocation bits, including C.JAL versus C.J funct3 and physical operands')
    need(metadata(e)==schema,'complete actual ELF metadata/noncode/gap bytes')
    if full:need(sha(e.raw)==ELF_PINS[native],'whole measured ELF pin')
    controls=[];original_rows={r[0]:r for r in EXPECTED}
    for at,kind,name in RELATIONS:
        row=original_rows[at];call=row[2]=='JAL'
        controls.append(dict(offset=at,kind=kind,target_symbol=name,nominal_PC=BASE+at,nominal_target=row[-1],
            pending_machine_target=BASE+at,link_rd=1 if call else 0,
            RA_continuation=BASE+at+row[1] if call else None,fallthrough=BASE+at+row[1] if kind in (16,44) else None))
    return dict(sha256=sha(e.raw),header=e.header,program_headers=e.program_headers,sections=e.sections,
       symbols=e.symbols,relocations=e.relocations,code_hex=code.hex(),code_sha256=sha(code),typed_rows=rows,
       UND_providers=UNDEFINED,ABS_providers=[],local_ABS_metadata=sum(s['section']==65521 and not s['info']>>4 for s in e.symbols),
       controls=controls,retained_nonrelocation_bits=sum(n.bit_count() for n in bitmasks),
       fully_unmasked_bytes=sum(n==255 for n in bitmasks),whole_nonrelocation_instruction_bytes=166,
       pending_machine_immediates=7,defined_relocation_targets=6,UND_relocation_sites=1,firmware_ready=False)


def ir_contract(text,language,full=True):
    normalized='\n'.join(text.splitlines()[2:])+'\n';core=core_ir(normalized)
    need(list(core)==NAMES and core==IR_CORE,'all literal SSA/constants/masks/fresh physical ports in seven-function order')
    need('%4 = and i32 %3, 255' in normalized and '%6 = shl i32 %5, 4' in normalized and
         '%10 = lshr i32 %9, 8' in normalized and '%15 = or i32 %12, %13' in normalized and '%2 = add i32 %1, 2' in normalized,
         'real C unsigned mask/packing/length dataflow')
    need('lbu a2, 2(s1)\\0Amv s4, a5\\0A' in normalized and 'bltu s7, a2, .Lfilter_long' in normalized,
         'physical S4 update is before the DLC rejection edge')
    need('lbu a3, 2(s1)\\0Alhu a0, 2(s0)\\0Aaddi a2, sp, 4\\0A' in normalized,
         'fresh then-live postopaque S1/S0/SP tuple port')
    need(normalized.count('c.jal .Lfilter_emit')==1 and normalized.count('c.j .Lfilter_scan')==1 and
         normalized.count('jalr a5\\0A')==1,'one compressed RA call, one no-link local jump, one indirect RA call')
    need(not re.search(r'\balloca\b|\b(?:undef|poison)\b|\.4byte|\.word|\.insn|mret|csrr|csrw',normalized) and normalized.count('ret\\0A')==1,
         'no compiler frame/spill/opcode carrier or extra privileged operation')
    if full:need(sha(normalized.encode())==IR_PINS[language],'complete normalized IR including all metadata/attributes')
    return dict(normalized_sha256=sha(normalized.encode()),core_SSA=core,C_unsigned_mask=255,
       C_channel_shift=4,C_identifier_shift=8,C_length_add=2,ordinary_C_ABI_proven=False)


def negatives(native,partial,text,language,official,md,llvm,out):
    results=[]
    def check(name,scope,fn,full=False):
        try:fn()
        except (ValueError,IndexError,KeyError) as exc:results.append(dict(name=name,scope=scope,rejected=True,whole_ELF_hash_enabled=False,whole_IR_hash_enabled=full,reason=str(exc)))
        else:raise ValueError('negative accepted '+name)
    def raw(name,e,n,position,fmt,value):
        b=bytearray(e.raw);struct.pack_into(fmt,b,position,value)
        check(name,'raw_ELF_reparsed',lambda:elf_contract(ELF(b),n,official,False))
    for e,n in [(native,True),(partial,False)]:
        tag='native' if n else 'partial';symtab=next(s for s in e.sections if s['type']==2)
        gs={s['name']:s for s in e.symbols if s['info']>>4}
        for name in [UNDEFINED[0],NAMES[4],NAMES[6]]:
            at=symtab['offset']+gs[name]['index']*16
            raw(tag+'_fakeABS_'+name,e,n,at+14,'<H',65521)
            raw(tag+'_weak_'+name,e,n,at+12,'<B',34)
        at=symtab['offset']+gs[NAMES[2]]['index']*16
        raw(tag+'_FUNC_size',e,n,at+8,'<I',46);raw(tag+'_FUNC_value',e,n,at+4,'<I',2)
        sec=next(s for s in e.sections if s['flags']&2 and s['size'])
        raw(tag+'_writable_code',e,n,e.header[5]+40*sec['index']+8,'<I',7)
        check(tag+'_trailing_bytes','raw_ELF_reparsed',lambda ee=e,nn=n:elf_contract(ELF(ee.raw+b'\0\0'),nn,official,False))
        for i,r in enumerate(e.relocations):
            table=next(s for s in e.sections if s['type']==4 and s['info']==r['section'])
            previous=sum(z['section']==r['section'] for z in e.relocations[:i]);at=table['offset']+12*previous
            raw(tag+'_RELA_addend_'+str(i),e,n,at+8,'<i',2)
            raw(tag+'_RELA_family_'+str(i),e,n,at+4,'<I',(r['symbol']<<8)|(44 if r['type']==45 else 45))
            wrong=gs[NAMES[0]]['index']
            raw(tag+'_RELA_target_'+str(i),e,n,at+4,'<I',(wrong<<8)|r['type'])
        def offset(pc):
            region=next((name,a,z) for name,a,z in REGIONS if a<=pc<a+z)
            return e.section('.text.'+region[0])['offset']+pc-region[1] if n else e.section('.filter')['offset']+pc
        for name,pc,delta,xor in [('SP_frame64',0,0,4),('saved_S4',10,0,4),('saved_RA_slot',22,0,4),
            ('S1_initial_message',26,0,4),('initial_index',28,0,4),('initial_S4',30,0,4),('original_AUIPC',32,2,16),
            ('S8_payload_base',46,2,16),('scan_S2_shift',54,2,16),('scan_record_S0',60,2,8),
            ('sentinel_S3',64,2,8),('kind_byte_slot',68,2,16),('kind_S6',72,2,16),('enabled_byte_slot',76,2,16),
            ('mask255',80,2,16),('enabled_branch',84,0,128),('length_S1',86,2,8),('selected_S4',90,0,4),
            ('unsigned_length_branch',92,1,32),('identifier_S1',96,2,8),('channel_byte11',100,2,16),
            ('payload_thenlive_S8',104,0,4),('identifier_low_store',106,0,128),('channel_shift4',110,2,16),
            ('identifier_shift8',114,2,16),('OR_channel_source',118,0,4),('packed_byte4',120,0,128),
            ('fresh_resident_S9',124,2,8),('copy_destination_SP',128,2,16),('indirect_call_as_JR',132,1,16),
            ('postopaque_S1_length',134,2,8),('postopaque_S0_identifier',138,2,8),('postopaque_SP_buffer',142,0,4),
            ('length_add2',144,0,4),('command192',146,2,16),('C_JAL_as_no_link_C_J',150,1,128),
            ('thenlive_S2_test',152,2,8),('return_thenlive_S4',160,0,4),('restore_S4_slot',168,0,4),
            ('SP_cleanup64',180,0,4),('RET',182,0,4),('cold_index1',184,0,4),('local_C_J_as_linking_C_JAL',186,1,128)]:
            at=offset(pc)+delta;raw(tag+'_'+name,e,n,at,'<B',e.raw[at]^xor)
        # Preserve byte count, but move original S4 assignment after BLTU.
        b=bytearray(e.raw);a=offset(90);chunk=bytes(b[a:a+6]);b[a:a+6]=chunk[2:]+chunk[:2]
        check(tag+'_S4_after_rejection','raw_ELF_reparsed',lambda bb=b,nn=n:elf_contract(ELF(bb),nn,official,False))
        b=bytearray(e.raw);a=offset(134);b[a:a+4],b[a+4:a+8]=b[a+4:a+8],b[a:a+4]
        check(tag+'_postopaque_fresh_read_order','raw_ELF_reparsed',lambda bb=b,nn=n:elf_contract(ELF(bb),nn,official,False))
    rowmap={r[0]:i for i,r in enumerate(EXPECTED)}
    for name,pc,field,value in [('parsed_C_JAL_rd_zero',150,3,0),('parsed_C_JALR_rd_zero',132,3,0),
       ('parsed_C_JAL_return_target',150,4,0x8a58),('parsed_DLC_signed',92,2,'BLT'),('parsed_S4_result',160,4,21),
       ('parsed_postcall_S1',134,4,10),('parsed_postcall_S0',138,4,9),('parsed_postcall_SP',142,4,9),('parsed_S2_test',152,3,19)]:
        changed=copy.deepcopy(EXPECTED);changed[rowmap[pc]][field]=value
        check(name,'parsed_typed_rows',lambda c=changed:typed_contract(c,False))
    mutations=[('IR_CJAL_no_link','c.jal .Lfilter_emit','c.j .Lfilter_emit'),('IR_localJ_links','c.j .Lfilter_scan','c.jal .Lfilter_scan'),
      ('IR_indirect_no_link','jalr a5','jr a5'),('IR_external_target','tsl9_filter_external_8a56','tsl9_filter_external_8a58'),
      ('IR_frame','addi sp, sp, -64','addi sp, sp, -48'),('IR_selected_S4','mv s4, a5','mv s4, a4'),
      ('IR_signed_length','bltu s7, a2','blt s7, a2'),('IR_postcall_S1','lbu a3, 2(s1)','lbu a3, 2(s2)'),
      ('IR_postcall_S0','lhu a0, 2(s0)','lhu a0, 2(s1)'),('IR_postcall_SP','addi a2, sp, 4','addi a2, sp, 8'),
      ('IR_resident_S9','lw a5, 76(s9)','lw a5, 76(s8)'),('IR_payload_S8','mv a1, s8','mv a1, s9'),
      ('IR_return_S4','mv a0, s4','mv a0, s5'),('IR_postcall_S2','beq s2, zero','beq s3, zero'),
      ('IR_mask255','%4 = and i32 %3, 255','%4 = and i32 %3, 127'),('IR_channel_shift','%6 = shl i32 %5, 4','%6 = shl i32 %5, 3'),
      ('IR_identifier_shift','%10 = lshr i32 %9, 8','%10 = lshr i32 %9, 7'),('IR_pack_OR','%15 = or i32 %12, %13','%15 = and i32 %12, %13'),
      ('IR_length_add','%2 = add i32 %1, 2','%2 = add i32 %1, 1'),('IR_command','i32 192, i32 %3','i32 193, i32 %3')]
    for name,old,new in mutations:
        need(old in text,'real IR negative fixture '+name);changed=text.replace(old,new,1)
        check(name,'IR_text_structural_SSA',lambda c=changed:ir_contract(c,language,False))
    for name,old,new in [('IR_full_attributes','generic-rv32','other-rv32'),('IR_full_metadata','!"wchar_size"','!"other"')]:
        need(old in text,'real full IR fixture');changed=text.replace(old,new,1)
        check(name,'IR_text_full_normalized_pin',lambda c=changed:ir_contract(c,language,True),True)
    for name,changed in [('MD_target',md.replace('native.o:','other.o:',1)),('MD_missing_header',' '.join(md.splitlines()[:-1])),('MD_extra',md+'\nextra.h\n')]:
        check(name,'MD_text',lambda c=changed:md_contract(c,llvm,out))
    return results


def evaluate(root,llvm,out,language):
    need(root.resolve()==ROOT,'canonical project root');before=inputs(llvm);official=original()
    native=ELF(out/'native.o');partial=ELF(out/'partial.o')
    nf=elf_contract(native,True,official);pf=elf_contract(partial,False,official)
    need(nf['code_hex']==pf['code_hex'],'partial composition preserves actual native bytes')
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
    controls=negatives(native,partial,text,language,official,md,llvm,out)
    need(before==inputs(llvm) and all(digest(out/Path(a['path']).name)==a['sha256'] for a in artifacts),'all read input/artifact bytes stable')
    record=dict(schema='TSL9-queue-filter-native-v1-formal-v1',language=language,firmware_ready=False,target_executed=False,ISA_emulated=False,
       inputs=[dict(path=portable(str(p),ROOT,llvm),size=p.stat().st_size,sha256=v) for p,v in before.items()],
       original=dict(base=0x8000,start=BASE,end=BASE+188,bytes=188,instructions=69,sha256=ORIGINAL_PIN,typed_rows=EXPECTED),
       native=nf,partial=pf,ir=ir,md_dependencies=deps,recipes=commands,artifacts=artifacts,negative_controls=controls,
       static_contract=dict(architectural_frame_bytes=64,C_byte_mask=255,C_channel_shift=4,C_identifier_shift=8,C_length_add=2,
         selected_S4_updated_before_DLC_reject=True,nonzero_proves_forwarding=False,two_records_guaranteed=False,
         indirect_call=dict(PC=0x8356,RA_continuation=0x8358,read='fresh LW A5,76(then-live S9)',target='unknown'),
         external_call=dict(PC=0x8368,width=2,link_rd=1,RA_continuation=0x836a,relocation_type=45,UND=UNDEFINED[0]),
         local_jump=dict(PC=0x838c,width=2,link_rd=0,target_symbol=NAMES[1]),
         postopaque_inputs=['fresh LBU A3,2(S1)','fresh LHU A0,2(S0)','A2=SP+4'],returned_A0='then-live S4 before restoring saved S4',
         initial_AUIPC_PC=BASE+32,nominal_initial_S5=(BASE+32+0x20004000+1186)&0xffffffff,
         all_relocations_resolved=False,ordinary_C_ABI_proven=False),limitations=[
        'Seven FUNC symbols are private physical-register regions and fallthrough boundaries, not independent ordinary C ABI functions.',
        'Actual ET_REL bytes retain all seven control immediates; external8A56 is a genuine UND and no ABS provider is invented.',
        'C.JAL at8368 has rd=RA and returns at836A despite relocation45; cold C.J at838C has no link. Resident JALR returns at8358.',
        'S0/S1/S2/S4/S8/S9/SP are then-live physical state after opaque calls, not assumed ordinary callee-saved values.',
        'S4 is set before the length>8 rejection. A nonzero return does not establish emission; two records processed is not guaranteed without callee contracts.',
        'Nominal AUIPC address requires original placement. Partial ET_REL has VA0; indirect resident identity/ABI, IRQ/silicon and physical timing remain unproved.',
        'No target/ISA/MMIO execution, full firmware BIN, OTA acceptance or successful flashing.'])
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
    need(out.parent==HERE/'build/verified-v1' and out.name==language,'owned formal v1 filter output only')
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
    print(json.dumps(dict(result='PASS',language=language,bytes=188,instructions=69,FUNCs=7,UND=1,retained_RELA=7,
       controls=len(record['negative_controls']),receipt_sha256=sha(encoded.encode()),firmware_ready=False)))
    if args.require_firmware_ready:
        print('REJECTED: unresolved symbolic/indirect/private/silicon ABI; firmware_ready=false.',file=sys.stderr);return 1
    return 0


if __name__=='__main__':
    try:sys.exit(main())
    except (ValueError,OSError,KeyError,IndexError,StopIteration) as exc:
        print('FAIL: '+str(exc),file=sys.stderr);sys.exit(1)
