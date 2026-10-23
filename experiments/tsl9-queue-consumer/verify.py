#!/usr/bin/env python3
"""Finite queue-consumer compiler/replay proof; never execute emitted code."""
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
SOURCE=HERE/'src/queue_consumer.v3.c'
READER=ROOT/'experiments/tsl9-spi-transfer-leaf/verify.py'
FIRMWARE=ROOT/'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
DECODE=ROOT/'analysis/irq-provider-2026-10-23/next-consumer.json'
PINS={SOURCE:'7347a1b541e034ff2a677dd32af78764993f5d542e2d5c85c0dc5e66ccdcf0e6',
 HERE/'component.ld':'0892b58d98599b6aa4ffad06da24acb0463973e4d8324476342ff803c964921a',
 HERE/'probe.py':'bd3ec537a705eb23ec8c6bec57bd2aa03072e3fdce3ea14801b77d9f6cf6624f',
 READER:'8c8eb8e01b9fc30eb7150682aa8848e47fe4a1254c6f87b05e657244a11b6de8',
 FIRMWARE:'0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667',
 DECODE:'8dc9dc3d4cd75aa5e4c22812ed0a45098f83f994bf78152fad9a2f7bb4dd03ca'}
TOOLS={'clang.exe':'047dfde05acc6fcce5af669e25cd8d40b4f509b8842d151d6d8a43a1c6a35fd6',
 'ld.lld.exe':'fe7f55c0c78b3d87f33b905a3874e10e872ca7beef53a8199d7ff9ac6641ec3f',
 'llvm-objdump.exe':'de40d1188fe63ff373e1a5dd83a12e2cb4545ca3b314da16a476ecf072e5a0fa'}
HEADER_PIN='7ce5540d5fb6e8da9760928e76cbdd5ebef329d701ad598d30d8e6f9d5d78b34'
ELF_PINS={True:'6e77c11e6107507c8641a29155615c5696ece76b2291ed36f184270804129e56',
 False:'81066ab0ecc727e9c10ede9afd1a91191a884863cc9ffe974437489c7fc04e6d'}
IR_PINS={'c':'1f7d36e76969234c49706032e1964ba6388b660a509d9d81bca37ea77a03cfd6',
 'cpp':'7da2f01a809c4d465163733ee569dea7e683554fc034ca93ab1ffab163233ed9'}
BASE=0x12c58
ORIGINAL_PIN='89905d7666bbe8295d09c752f1fcd34246847ea86c6428b539406450f8980c0f'
NAMES=['tsl9_queue_entry_12c58','tsl9_queue_scan_12c86','tsl9_queue_release_12ca6','tsl9_queue_validate_12cb4',
 'tsl9_queue_advance_12cee','tsl9_queue_finish_12cf8','tsl9_queue_zero_12d0e','tsl9_queue_emit_12d42',
 'tsl9_queue_response_12d4c','tsl9_queue_other_12d78']
REGIONS=list(zip(NAMES,[0,46,78,92,150,160,182,234,244,288],[46,32,14,58,10,22,52,10,44,26]))
UNDEFINED=['tsl9_queue_external_'+s for s in ['82d2','820c','9454','9b36','12abe','12a08','81aa','14d2e']]
RELATIONS=[(60,44,NAMES[4]),(88,17,UNDEFINED[0]),(92,44,NAMES[4]),(98,16,NAMES[9]),
 (108,16,NAMES[4]),(120,16,NAMES[4]),(132,16,NAMES[4]),(140,44,NAMES[6]),(146,16,NAMES[8]),
 (156,16,NAMES[1]),(182,17,UNDEFINED[1]),(190,17,UNDEFINED[2]),(196,17,UNDEFINED[3]),
 (212,17,UNDEFINED[4]),(228,16,NAMES[7]),(238,17,UNDEFINED[4]),(242,45,NAMES[4]),
 (252,16,NAMES[4]),(282,17,UNDEFINED[5]),(286,45,NAMES[4]),(298,44,NAMES[4]),
 (300,17,UNDEFINED[6]),(304,44,NAMES[4]),(308,17,UNDEFINED[7]),(312,45,NAMES[4])]
MASKS={16:(4,0x01fff07f),17:(4,0x00000fff),44:(2,0xe383),45:(2,0xe003)}
# Literal typed rows are independently cross-checked with the actual BIN,
# pinned static decode and a finite raw instruction decoder below.
EXPECTED = [[0, 2, 'ADDI', 2, 2, -80], [2, 2, 'SW32', 9, 2, 68], [4, 2, 'SW32', 18, 2, 64], [6, 2, 'SW32', 19, 2, 60], [8, 2, 'SW32', 20, 2, 56], [10, 2, 'SW32', 21, 2, 52], [12, 2, 'SW32', 22, 2, 48], [14, 2, 'SW32', 23, 2, 44], [16, 2, 'SW32', 1, 2, 76], [18, 2, 'SW32', 8, 2, 72], [20, 2, 'ADDI', 9, 0, 0], [22, 4, 'AUIPC', 21, 536842240], [26, 4, 'ADDI', 21, 21, 970], [30, 2, 'ADDI', 22, 0, 12], [32, 4, 'ADDI', 18, 0, 136], [36, 4, 'LUI', 19, 262144], [40, 2, 'ADDI', 20, 0, 1], [42, 4, 'ADDI', 23, 3, 84], [46, 4, 'MUL', 8, 9, 22], [50, 2, 'ADD', 8, 8, 21], [52, 4, 'LHU16', 15, 8, 0], [56, 2, 'SLLI', 15, 15, 16], [58, 2, 'SRLI', 15, 15, 16], [60, 2, 'BEQZ', 15, 77038], [62, 4, 'CSRRC', 0, 2048, 18], [66, 4, 'LW32', 15, 19, 76], [70, 2, 'ADDI', 12, 0, 12], [72, 2, 'MV', 11, 8], [74, 2, 'ADDI', 10, 2, 8], [76, 2, 'JALR', 1, 15, 0], [78, 4, 'SH16', 0, 8, 0], [82, 4, 'CSRRS', 0, 2048, 18], [86, 2, 'ADDI', 10, 2, 8], [88, 4, 'JAL', 1, 33490], [92, 2, 'BNEZ', 10, 77038], [94, 4, 'LHU16', 15, 2, 8], [98, 4, 'BNE', 15, 20, 77176], [102, 4, 'LBU8', 14, 2, 10], [106, 2, 'ADDI', 15, 0, 4], [108, 4, 'BNE', 14, 15, 77038], [112, 4, 'LBU8', 14, 2, 11], [116, 4, 'ADDI', 15, 0, 181], [120, 4, 'BNE', 14, 15, 77038], [124, 4, 'LBU8', 14, 2, 12], [128, 4, 'ADDI', 15, 0, 98], [132, 4, 'BNE', 14, 15, 77038], [136, 4, 'LBU8', 15, 2, 13], [140, 2, 'BEQZ', 15, 77070], [142, 4, 'ADDI', 14, 0, 90], [146, 4, 'BEQ', 15, 14, 77132], [150, 2, 'ADDI', 9, 9, 1], [152, 4, 'ADDI', 15, 0, 32], [156, 4, 'BNE', 9, 15, 76934], [160, 2, 'LW32', 1, 2, 76], [162, 2, 'LW32', 8, 2, 72], [164, 2, 'LW32', 9, 2, 68], [166, 2, 'LW32', 18, 2, 64], [168, 2, 'LW32', 19, 2, 60], [170, 2, 'LW32', 20, 2, 56], [172, 2, 'LW32', 21, 2, 52], [174, 2, 'LW32', 22, 2, 48], [176, 2, 'LW32', 23, 2, 44], [178, 2, 'ADDI', 2, 2, 80], [180, 2, 'RET', 1], [182, 4, 'JAL', 1, 33292], [186, 4, 'LBU8', 10, 2, 14], [190, 4, 'JAL', 1, 37972], [194, 2, 'ADDI', 10, 0, 0], [196, 4, 'JAL', 1, 39734], [200, 4, 'LBU8', 10, 2, 19], [204, 2, 'ADDI', 12, 0, 2], [206, 2, 'ADDI', 11, 2, 20], [208, 4, 'SH16', 0, 2, 20], [212, 4, 'JAL', 1, 76478], [216, 4, 'LBU8', 14, 2, 19], [220, 4, 'SH16', 20, 2, 20], [224, 2, 'ADDI', 15, 0, 2], [226, 2, 'ADDI', 10, 0, 1], [228, 4, 'BEQ', 14, 15, 77122], [232, 2, 'ADDI', 10, 0, 2], [234, 2, 'ADDI', 12, 0, 2], [236, 2, 'ADDI', 11, 2, 20], [238, 4, 'JAL', 1, 76478], [242, 2, 'J', 77038], [244, 4, 'LBU8', 14, 2, 14], [248, 4, 'ADDI', 15, 0, 85], [252, 4, 'BNE', 14, 15, 77038], [256, 4, 'LW32', 15, 19, 76], [260, 2, 'ADDI', 10, 2, 20], [262, 2, 'ADDI', 12, 0, 12], [264, 2, 'ADDI', 11, 2, 8], [266, 2, 'JALR', 1, 15, 0], [268, 4, 'ADDI', 15, 0, 86], [272, 2, 'ADDI', 10, 2, 20], [274, 4, 'SB8', 15, 2, 26], [278, 4, 'SB8', 0, 2, 31], [282, 4, 'JAL', 1, 76296], [286, 2, 'J', 77038], [288, 4, 'LW32', 15, 23, 0], [292, 4, 'LBU8', 15, 15, 4], [296, 2, 'ANDI', 15, 15, 8], [298, 2, 'BNEZ', 15, 77038], [300, 4, 'JAL', 1, 33194], [304, 2, 'BEQZ', 10, 77038], [306, 2, 'ADDI', 10, 2, 8], [308, 4, 'JAL', 1, 85294], [312, 2, 'J', 77038]]
SCHEMAS = {'native': {'header': [1, 243, 1, 0, 0, 2108, 1, 52, 0, 0, 40, 26, 1], 'program_headers': [], 'sections': [{'name_offset': 0, 'type': 0, 'flags': 0, 'address': 0, 'offset': 0, 'size': 0, 'link': 0, 'info': 0, 'align': 0, 'entsize': 0, 'index': 0, 'name': ''}, {'name_offset': 267, 'type': 3, 'flags': 0, 'address': 0, 'offset': 1402, 'size': 703, 'link': 0, 'info': 0, 'align': 1, 'entsize': 0, 'index': 1, 'name': '.strtab'}, {'name_offset': 1, 'type': 1, 'flags': 6, 'address': 0, 'offset': 52, 'size': 0, 'link': 0, 'info': 0, 'align': 2, 'entsize': 0, 'index': 2, 'name': '.text'}, {'name_offset': 377, 'type': 1, 'flags': 6, 'address': 0, 'offset': 52, 'size': 46, 'link': 0, 'info': 0, 'align': 2, 'entsize': 0, 'index': 3, 'name': '.text.tsl9_queue_entry_12c58'}, {'name_offset': 483, 'type': 1, 'flags': 6, 'address': 0, 'offset': 98, 'size': 32, 'link': 0, 'info': 0, 'align': 2, 'entsize': 0, 'index': 4, 'name': '.text.tsl9_queue_scan_12c86'}, {'name_offset': 478, 'type': 4, 'flags': 64, 'address': 0, 'offset': 1092, 'size': 12, 'link': 25, 'info': 4, 'align': 4, 'entsize': 12, 'index': 5, 'name': '.rela.text.tsl9_queue_scan_12c86'}, {'name_offset': 447, 'type': 1, 'flags': 6, 'address': 0, 'offset': 130, 'size': 14, 'link': 0, 'info': 0, 'align': 2, 'entsize': 0, 'index': 6, 'name': '.text.tsl9_queue_release_12ca6'}, {'name_offset': 442, 'type': 4, 'flags': 64, 'address': 0, 'offset': 1104, 'size': 12, 'link': 25, 'info': 6, 'align': 4, 'entsize': 12, 'index': 7, 'name': '.rela.text.tsl9_queue_release_12ca6'}, {'name_offset': 551, 'type': 1, 'flags': 6, 'address': 0, 'offset': 144, 'size': 58, 'link': 0, 'info': 0, 'align': 2, 'entsize': 0, 'index': 8, 'name': '.text.tsl9_queue_validate_12cb4'}, {'name_offset': 546, 'type': 4, 'flags': 64, 'address': 0, 'offset': 1116, 'size': 84, 'link': 25, 'info': 8, 'align': 4, 'entsize': 12, 'index': 9, 'name': '.rela.text.tsl9_queue_validate_12cb4'}, {'name_offset': 69, 'type': 1, 'flags': 6, 'address': 0, 'offset': 202, 'size': 10, 'link': 0, 'info': 0, 'align': 2, 'entsize': 0, 'index': 10, 'name': '.text.tsl9_queue_advance_12cee'}, {'name_offset': 64, 'type': 4, 'flags': 64, 'address': 0, 'offset': 1200, 'size': 12, 'link': 25, 'info': 10, 'align': 4, 'entsize': 12, 'index': 11, 'name': '.rela.text.tsl9_queue_advance_12cee'}, {'name_offset': 313, 'type': 1, 'flags': 6, 'address': 0, 'offset': 212, 'size': 22, 'link': 0, 'info': 0, 'align': 2, 'entsize': 0, 'index': 12, 'name': '.text.tsl9_queue_finish_12cf8'}, {'name_offset': 157, 'type': 1, 'flags': 6, 'address': 0, 'offset': 234, 'size': 52, 'link': 0, 'info': 0, 'align': 2, 'entsize': 0, 'index': 13, 'name': '.text.tsl9_queue_zero_12d0e'}, {'name_offset': 152, 'type': 4, 'flags': 64, 'address': 0, 'offset': 1212, 'size': 60, 'link': 25, 'info': 13, 'align': 4, 'entsize': 12, 'index': 14, 'name': '.rela.text.tsl9_queue_zero_12d0e'}, {'name_offset': 648, 'type': 1, 'flags': 6, 'address': 0, 'offset': 286, 'size': 10, 'link': 0, 'info': 0, 'align': 2, 'entsize': 0, 'index': 15, 'name': '.text.tsl9_queue_emit_12d42'}, {'name_offset': 643, 'type': 4, 'flags': 64, 'address': 0, 'offset': 1272, 'size': 24, 'link': 25, 'info': 15, 'align': 4, 'entsize': 12, 'index': 16, 'name': '.rela.text.tsl9_queue_emit_12d42'}, {'name_offset': 190, 'type': 1, 'flags': 6, 'address': 0, 'offset': 296, 'size': 44, 'link': 0, 'info': 0, 'align': 2, 'entsize': 0, 'index': 17, 'name': '.text.tsl9_queue_response_12d4c'}, {'name_offset': 185, 'type': 4, 'flags': 64, 'address': 0, 'offset': 1296, 'size': 36, 'link': 25, 'info': 17, 'align': 4, 'entsize': 12, 'index': 18, 'name': '.rela.text.tsl9_queue_response_12d4c'}, {'name_offset': 348, 'type': 1, 'flags': 6, 'address': 0, 'offset': 340, 'size': 26, 'link': 0, 'info': 0, 'align': 2, 'entsize': 0, 'index': 19, 'name': '.text.tsl9_queue_other_12d78'}, {'name_offset': 343, 'type': 4, 'flags': 64, 'address': 0, 'offset': 1332, 'size': 60, 'link': 25, 'info': 19, 'align': 4, 'entsize': 12, 'index': 20, 'name': '.rela.text.tsl9_queue_other_12d78'}, {'name_offset': 7, 'type': 1, 'flags': 48, 'address': 0, 'offset': 366, 'size': 159, 'link': 0, 'info': 0, 'align': 1, 'entsize': 1, 'index': 21, 'name': '.comment'}, {'name_offset': 34, 'type': 1, 'flags': 0, 'address': 0, 'offset': 525, 'size': 0, 'link': 0, 'info': 0, 'align': 1, 'entsize': 0, 'index': 22, 'name': '.note.GNU-stack'}, {'name_offset': 16, 'type': 1879048195, 'flags': 0, 'address': 0, 'offset': 525, 'size': 52, 'link': 0, 'info': 0, 'align': 1, 'entsize': 0, 'index': 23, 'name': '.riscv.attributes'}, {'name_offset': 50, 'type': 1879002115, 'flags': 2147483648, 'address': 0, 'offset': 1392, 'size': 10, 'link': 25, 'info': 0, 'align': 1, 'entsize': 0, 'index': 24, 'name': '.llvm_addrsig'}, {'name_offset': 275, 'type': 2, 'flags': 0, 'address': 0, 'offset': 580, 'size': 512, 'link': 1, 'info': 14, 'align': 4, 'entsize': 16, 'index': 25, 'name': '.symtab'}], 'symbols': [{'index': 0, 'name': '', 'value': 0, 'size': 0, 'info': 0, 'other': 0, 'section': 0}, {'index': 1, 'name': 'queue_consumer.v3.c', 'value': 0, 'size': 0, 'info': 4, 'other': 0, 'section': 65521}, {'index': 2, 'name': '$x.0', 'value': 0, 'size': 0, 'info': 0, 'other': 0, 'section': 3}, {'index': 3, 'name': '$x.1', 'value': 0, 'size': 0, 'info': 0, 'other': 0, 'section': 4}, {'index': 4, 'name': '$x.2', 'value': 0, 'size': 0, 'info': 0, 'other': 0, 'section': 6}, {'index': 5, 'name': '$x.3', 'value': 0, 'size': 0, 'info': 0, 'other': 0, 'section': 8}, {'index': 6, 'name': '$x.4', 'value': 0, 'size': 0, 'info': 0, 'other': 0, 'section': 10}, {'index': 7, 'name': '$x.5', 'value': 0, 'size': 0, 'info': 0, 'other': 0, 'section': 12}, {'index': 8, 'name': '$x.6', 'value': 0, 'size': 0, 'info': 0, 'other': 0, 'section': 13}, {'index': 9, 'name': '$x.7', 'value': 0, 'size': 0, 'info': 0, 'other': 0, 'section': 15}, {'index': 10, 'name': '$x.8', 'value': 0, 'size': 0, 'info': 0, 'other': 0, 'section': 17}, {'index': 11, 'name': '$x.9', 'value': 0, 'size': 0, 'info': 0, 'other': 0, 'section': 19}, {'index': 12, 'name': '$d.10', 'value': 0, 'size': 0, 'info': 0, 'other': 0, 'section': 21}, {'index': 13, 'name': '$d.11', 'value': 0, 'size': 0, 'info': 0, 'other': 0, 'section': 23}, {'index': 14, 'name': 'tsl9_queue_entry_12c58', 'value': 0, 'size': 46, 'info': 18, 'other': 0, 'section': 3}, {'index': 15, 'name': 'tsl9_queue_scan_12c86', 'value': 0, 'size': 32, 'info': 18, 'other': 0, 'section': 4}, {'index': 16, 'name': 'tsl9_queue_advance_12cee', 'value': 0, 'size': 10, 'info': 18, 'other': 0, 'section': 10}, {'index': 17, 'name': 'tsl9_queue_release_12ca6', 'value': 0, 'size': 14, 'info': 18, 'other': 0, 'section': 6}, {'index': 18, 'name': 'tsl9_queue_external_82d2', 'value': 0, 'size': 0, 'info': 16, 'other': 0, 'section': 0}, {'index': 19, 'name': 'tsl9_queue_validate_12cb4', 'value': 0, 'size': 58, 'info': 18, 'other': 0, 'section': 8}, {'index': 20, 'name': 'tsl9_queue_other_12d78', 'value': 0, 'size': 26, 'info': 18, 'other': 0, 'section': 19}, {'index': 21, 'name': 'tsl9_queue_zero_12d0e', 'value': 0, 'size': 52, 'info': 18, 'other': 0, 'section': 13}, {'index': 22, 'name': 'tsl9_queue_response_12d4c', 'value': 0, 'size': 44, 'info': 18, 'other': 0, 'section': 17}, {'index': 23, 'name': 'tsl9_queue_finish_12cf8', 'value': 0, 'size': 22, 'info': 18, 'other': 0, 'section': 12}, {'index': 24, 'name': 'tsl9_queue_external_820c', 'value': 0, 'size': 0, 'info': 16, 'other': 0, 'section': 0}, {'index': 25, 'name': 'tsl9_queue_external_9454', 'value': 0, 'size': 0, 'info': 16, 'other': 0, 'section': 0}, {'index': 26, 'name': 'tsl9_queue_external_9b36', 'value': 0, 'size': 0, 'info': 16, 'other': 0, 'section': 0}, {'index': 27, 'name': 'tsl9_queue_external_12abe', 'value': 0, 'size': 0, 'info': 16, 'other': 0, 'section': 0}, {'index': 28, 'name': 'tsl9_queue_emit_12d42', 'value': 0, 'size': 10, 'info': 18, 'other': 0, 'section': 15}, {'index': 29, 'name': 'tsl9_queue_external_12a08', 'value': 0, 'size': 0, 'info': 16, 'other': 0, 'section': 0}, {'index': 30, 'name': 'tsl9_queue_external_81aa', 'value': 0, 'size': 0, 'info': 16, 'other': 0, 'section': 0}, {'index': 31, 'name': 'tsl9_queue_external_14d2e', 'value': 0, 'size': 0, 'info': 16, 'other': 0, 'section': 0}], 'relocations': [{'section': 4, 'offset': 14, 'type': 44, 'symbol': 16, 'addend': 0}, {'section': 6, 'offset': 10, 'type': 17, 'symbol': 18, 'addend': 0}, {'section': 8, 'offset': 0, 'type': 44, 'symbol': 16, 'addend': 0}, {'section': 8, 'offset': 6, 'type': 16, 'symbol': 20, 'addend': 0}, {'section': 8, 'offset': 16, 'type': 16, 'symbol': 16, 'addend': 0}, {'section': 8, 'offset': 28, 'type': 16, 'symbol': 16, 'addend': 0}, {'section': 8, 'offset': 40, 'type': 16, 'symbol': 16, 'addend': 0}, {'section': 8, 'offset': 48, 'type': 44, 'symbol': 21, 'addend': 0}, {'section': 8, 'offset': 54, 'type': 16, 'symbol': 22, 'addend': 0}, {'section': 10, 'offset': 6, 'type': 16, 'symbol': 15, 'addend': 0}, {'section': 13, 'offset': 0, 'type': 17, 'symbol': 24, 'addend': 0}, {'section': 13, 'offset': 8, 'type': 17, 'symbol': 25, 'addend': 0}, {'section': 13, 'offset': 14, 'type': 17, 'symbol': 26, 'addend': 0}, {'section': 13, 'offset': 30, 'type': 17, 'symbol': 27, 'addend': 0}, {'section': 13, 'offset': 46, 'type': 16, 'symbol': 28, 'addend': 0}, {'section': 15, 'offset': 4, 'type': 17, 'symbol': 27, 'addend': 0}, {'section': 15, 'offset': 8, 'type': 45, 'symbol': 16, 'addend': 0}, {'section': 17, 'offset': 8, 'type': 16, 'symbol': 16, 'addend': 0}, {'section': 17, 'offset': 38, 'type': 17, 'symbol': 29, 'addend': 0}, {'section': 17, 'offset': 42, 'type': 45, 'symbol': 16, 'addend': 0}, {'section': 19, 'offset': 10, 'type': 44, 'symbol': 16, 'addend': 0}, {'section': 19, 'offset': 12, 'type': 17, 'symbol': 30, 'addend': 0}, {'section': 19, 'offset': 16, 'type': 44, 'symbol': 16, 'addend': 0}, {'section': 19, 'offset': 20, 'type': 17, 'symbol': 31, 'addend': 0}, {'section': 19, 'offset': 24, 'type': 45, 'symbol': 16, 'addend': 0}], 'noncode_section_hashes': {'': 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855', '.strtab': '9151a2f7793636fab8f2ae56f7ad395ee67418b84368f295f70dab68b0c92396', '.rela.text.tsl9_queue_scan_12c86': 'c0dc9bf22cceaab43e05b6943e6f17c8f73d009b12f7882713dc40a340abc6c3', '.rela.text.tsl9_queue_release_12ca6': 'f0fbbfbed5dab78aa71ee8cb27e40880f88eeda4cf0d3b97fa1eb481498649f2', '.rela.text.tsl9_queue_validate_12cb4': '05ffe485ad8095ffb64d35cb9dc41f32ad464b4c24981a848bf5b05bb37125e6', '.rela.text.tsl9_queue_advance_12cee': 'f4a8290b8ad62b3db0e89ea2a783aaeb09258d0cb327b1197ac2ed8f8cdc790d', '.rela.text.tsl9_queue_zero_12d0e': 'ebdb18cc4bd0b2779e18c33faeb5ecad15d72310753d1283ad658d6d1b228d64', '.rela.text.tsl9_queue_emit_12d42': '9750cf3089a7243d7405cabc9930e0f45d580cb3f6fbb34ca56ed08abe842afa', '.rela.text.tsl9_queue_response_12d4c': '98cc1b5e8cc57c16dec90b38c2a50ce46f475ad629dd7d450fe37994fbf93d0c', '.rela.text.tsl9_queue_other_12d78': '6a00ae828cd79c0b1d10b4d6cbda2ce6f1f00d73748a0dc05123287051b84dc3', '.comment': '72c64fbc17a5d9f46f33ac0650b7d4f549d87c2ba9e77ebd765a25a3960e3017', '.note.GNU-stack': 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855', '.riscv.attributes': 'f2bd85b0ab58609a20dbdef6cc6e3f2dd1a34cdcb554580710aa3819cd24ad71', '.llvm_addrsig': 'b8c353fe25ab46c4241fbfcfa5aba43e7e4e5f5ee54fb82435e927be60c8aad3', '.symtab': '204762e09159ef7b992ec78e20ae383b45a45275e4b6c25843b99263a7ea1c7a'}, 'outside_allocated_code_sha256': '9de35df7188281c73f25e0677b385b685c59f4187b083fa4ee747037eddb8b2e'}, 'partial': {'header': [1, 243, 1, 0, 0, 1808, 1, 52, 0, 0, 40, 8, 6], 'program_headers': [], 'sections': [{'name_offset': 0, 'type': 0, 'flags': 0, 'address': 0, 'offset': 0, 'size': 0, 'link': 0, 'info': 0, 'align': 0, 'entsize': 0, 'index': 0, 'name': ''}, {'name_offset': 1, 'type': 1, 'flags': 6, 'address': 0, 'offset': 52, 'size': 314, 'link': 0, 'info': 0, 'align': 2, 'entsize': 0, 'index': 1, 'name': '.queue'}, {'name_offset': 8, 'type': 1, 'flags': 6, 'address': 0, 'offset': 366, 'size': 0, 'link': 0, 'info': 0, 'align': 2, 'entsize': 0, 'index': 2, 'name': '.text'}, {'name_offset': 14, 'type': 4, 'flags': 64, 'address': 0, 'offset': 368, 'size': 300, 'link': 5, 'info': 1, 'align': 4, 'entsize': 12, 'index': 3, 'name': '.rela.queue'}, {'name_offset': 26, 'type': 1879002115, 'flags': 2147483648, 'address': 0, 'offset': 668, 'size': 10, 'link': 0, 'info': 0, 'align': 1, 'entsize': 0, 'index': 4, 'name': '.llvm_addrsig'}, {'name_offset': 40, 'type': 2, 'flags': 0, 'address': 0, 'offset': 680, 'size': 544, 'link': 7, 'info': 16, 'align': 4, 'entsize': 16, 'index': 5, 'name': '.symtab'}, {'name_offset': 48, 'type': 3, 'flags': 0, 'address': 0, 'offset': 1224, 'size': 66, 'link': 0, 'info': 0, 'align': 1, 'entsize': 0, 'index': 6, 'name': '.shstrtab'}, {'name_offset': 58, 'type': 3, 'flags': 0, 'address': 0, 'offset': 1290, 'size': 518, 'link': 0, 'info': 0, 'align': 1, 'entsize': 0, 'index': 7, 'name': '.strtab'}], 'symbols': [{'index': 0, 'name': '', 'value': 0, 'size': 0, 'info': 0, 'other': 0, 'section': 0}, {'index': 1, 'name': 'queue_consumer.v3.c', 'value': 0, 'size': 0, 'info': 4, 'other': 0, 'section': 65521}, {'index': 2, 'name': '$x.0', 'value': 0, 'size': 0, 'info': 0, 'other': 0, 'section': 1}, {'index': 3, 'name': '$x.1', 'value': 46, 'size': 0, 'info': 0, 'other': 0, 'section': 1}, {'index': 4, 'name': '$x.2', 'value': 78, 'size': 0, 'info': 0, 'other': 0, 'section': 1}, {'index': 5, 'name': '$x.3', 'value': 92, 'size': 0, 'info': 0, 'other': 0, 'section': 1}, {'index': 6, 'name': '$x.4', 'value': 150, 'size': 0, 'info': 0, 'other': 0, 'section': 1}, {'index': 7, 'name': '$x.5', 'value': 160, 'size': 0, 'info': 0, 'other': 0, 'section': 1}, {'index': 8, 'name': '$x.6', 'value': 182, 'size': 0, 'info': 0, 'other': 0, 'section': 1}, {'index': 9, 'name': '$x.7', 'value': 234, 'size': 0, 'info': 0, 'other': 0, 'section': 1}, {'index': 10, 'name': '$x.8', 'value': 244, 'size': 0, 'info': 0, 'other': 0, 'section': 1}, {'index': 11, 'name': '$x.9', 'value': 288, 'size': 0, 'info': 0, 'other': 0, 'section': 1}, {'index': 12, 'name': '$d.11', 'value': 0, 'size': 0, 'info': 0, 'other': 0, 'section': 65521}, {'index': 13, 'name': '', 'value': 0, 'size': 0, 'info': 3, 'other': 0, 'section': 1}, {'index': 14, 'name': '', 'value': 0, 'size': 0, 'info': 3, 'other': 0, 'section': 2}, {'index': 15, 'name': '', 'value': 0, 'size': 0, 'info': 3, 'other': 0, 'section': 4}, {'index': 16, 'name': 'tsl9_queue_entry_12c58', 'value': 0, 'size': 46, 'info': 18, 'other': 0, 'section': 1}, {'index': 17, 'name': 'tsl9_queue_scan_12c86', 'value': 46, 'size': 32, 'info': 18, 'other': 0, 'section': 1}, {'index': 18, 'name': 'tsl9_queue_advance_12cee', 'value': 150, 'size': 10, 'info': 18, 'other': 0, 'section': 1}, {'index': 19, 'name': 'tsl9_queue_release_12ca6', 'value': 78, 'size': 14, 'info': 18, 'other': 0, 'section': 1}, {'index': 20, 'name': 'tsl9_queue_external_82d2', 'value': 0, 'size': 0, 'info': 16, 'other': 0, 'section': 0}, {'index': 21, 'name': 'tsl9_queue_validate_12cb4', 'value': 92, 'size': 58, 'info': 18, 'other': 0, 'section': 1}, {'index': 22, 'name': 'tsl9_queue_other_12d78', 'value': 288, 'size': 26, 'info': 18, 'other': 0, 'section': 1}, {'index': 23, 'name': 'tsl9_queue_zero_12d0e', 'value': 182, 'size': 52, 'info': 18, 'other': 0, 'section': 1}, {'index': 24, 'name': 'tsl9_queue_response_12d4c', 'value': 244, 'size': 44, 'info': 18, 'other': 0, 'section': 1}, {'index': 25, 'name': 'tsl9_queue_finish_12cf8', 'value': 160, 'size': 22, 'info': 18, 'other': 0, 'section': 1}, {'index': 26, 'name': 'tsl9_queue_external_820c', 'value': 0, 'size': 0, 'info': 16, 'other': 0, 'section': 0}, {'index': 27, 'name': 'tsl9_queue_external_9454', 'value': 0, 'size': 0, 'info': 16, 'other': 0, 'section': 0}, {'index': 28, 'name': 'tsl9_queue_external_9b36', 'value': 0, 'size': 0, 'info': 16, 'other': 0, 'section': 0}, {'index': 29, 'name': 'tsl9_queue_external_12abe', 'value': 0, 'size': 0, 'info': 16, 'other': 0, 'section': 0}, {'index': 30, 'name': 'tsl9_queue_emit_12d42', 'value': 234, 'size': 10, 'info': 18, 'other': 0, 'section': 1}, {'index': 31, 'name': 'tsl9_queue_external_12a08', 'value': 0, 'size': 0, 'info': 16, 'other': 0, 'section': 0}, {'index': 32, 'name': 'tsl9_queue_external_81aa', 'value': 0, 'size': 0, 'info': 16, 'other': 0, 'section': 0}, {'index': 33, 'name': 'tsl9_queue_external_14d2e', 'value': 0, 'size': 0, 'info': 16, 'other': 0, 'section': 0}], 'relocations': [{'section': 1, 'offset': 60, 'type': 44, 'symbol': 18, 'addend': 0}, {'section': 1, 'offset': 88, 'type': 17, 'symbol': 20, 'addend': 0}, {'section': 1, 'offset': 92, 'type': 44, 'symbol': 18, 'addend': 0}, {'section': 1, 'offset': 98, 'type': 16, 'symbol': 22, 'addend': 0}, {'section': 1, 'offset': 108, 'type': 16, 'symbol': 18, 'addend': 0}, {'section': 1, 'offset': 120, 'type': 16, 'symbol': 18, 'addend': 0}, {'section': 1, 'offset': 132, 'type': 16, 'symbol': 18, 'addend': 0}, {'section': 1, 'offset': 140, 'type': 44, 'symbol': 23, 'addend': 0}, {'section': 1, 'offset': 146, 'type': 16, 'symbol': 24, 'addend': 0}, {'section': 1, 'offset': 156, 'type': 16, 'symbol': 17, 'addend': 0}, {'section': 1, 'offset': 182, 'type': 17, 'symbol': 26, 'addend': 0}, {'section': 1, 'offset': 190, 'type': 17, 'symbol': 27, 'addend': 0}, {'section': 1, 'offset': 196, 'type': 17, 'symbol': 28, 'addend': 0}, {'section': 1, 'offset': 212, 'type': 17, 'symbol': 29, 'addend': 0}, {'section': 1, 'offset': 228, 'type': 16, 'symbol': 30, 'addend': 0}, {'section': 1, 'offset': 238, 'type': 17, 'symbol': 29, 'addend': 0}, {'section': 1, 'offset': 242, 'type': 45, 'symbol': 18, 'addend': 0}, {'section': 1, 'offset': 252, 'type': 16, 'symbol': 18, 'addend': 0}, {'section': 1, 'offset': 282, 'type': 17, 'symbol': 31, 'addend': 0}, {'section': 1, 'offset': 286, 'type': 45, 'symbol': 18, 'addend': 0}, {'section': 1, 'offset': 298, 'type': 44, 'symbol': 18, 'addend': 0}, {'section': 1, 'offset': 300, 'type': 17, 'symbol': 32, 'addend': 0}, {'section': 1, 'offset': 304, 'type': 44, 'symbol': 18, 'addend': 0}, {'section': 1, 'offset': 308, 'type': 17, 'symbol': 33, 'addend': 0}, {'section': 1, 'offset': 312, 'type': 45, 'symbol': 18, 'addend': 0}], 'noncode_section_hashes': {'': 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855', '.rela.queue': 'b0b5a1e066288ce231500b0e702e5ee2ea96ce2e715bc6f01d87fb3803ab1031', '.llvm_addrsig': 'b8c353fe25ab46c4241fbfcfa5aba43e7e4e5f5ee54fb82435e927be60c8aad3', '.symtab': 'dbef84ec149ea8b16bc8f51cde3021ecd11161cf78c22506d82f0d15b97975fc', '.shstrtab': 'a52993ee65b3a8a50f6d145fc0a74f577629b2d252f8f1ade01f0e05d8611f59', '.strtab': '493667c58cf034f7704ffcf035b0d144d10fdb31972d9fe2971eca7b04cd26ff'}, 'outside_allocated_code_sha256': '7007b9a23345fdc510f53816badca5afce6d133134d5257db977b80e9a58178e'}}
IR_CORE = {'tsl9_queue_entry_12c58': ['tail call void asm sideeffect "addi sp, sp, -80\\0Asw s1, 68(sp)\\0Asw s2, 64(sp)\\0Asw s3, 60(sp)\\0Asw s4, 56(sp)\\0Asw s5, 52(sp)\\0Asw s6, 48(sp)\\0Asw s7, 44(sp)\\0Asw ra, 76(sp)\\0Asw s0, 72(sp)\\0Ali s1, 0\\0Aauipc s5, 0x1fff9\\0Aaddi s5, s5, 970\\0Ali s6, 12\\0Ali s2, 136\\0Alui s3, 0x40\\0Ali s4, 1\\0Aaddi s7, gp, 84\\0A", ""() #2', 'unreachable'], 'tsl9_queue_scan_12c86': ['%1 = tail call i32 asm sideeffect "mul s0, s1, s6\\0Aadd s0, s0, s5\\0Alhu a5, 0(s0)\\0A", "={x15},~{memory}"() #2', '%2 = tail call i32 asm sideeffect "", "={x15},{x15},~{memory}"(i32 %1) #2', '%3 = shl i32 %2, 16', '%4 = tail call i32 asm sideeffect "", "={x15},{x15},~{memory}"(i32 %3) #2', '%5 = lshr i32 %4, 16', 'tail call void asm sideeffect ".Lqempty:\\0Ac.beqz a5, .Lqempty\\0A.reloc .-2, R_RISCV_RVC_BRANCH, tsl9_queue_advance_12cee\\0A", "{x15},~{memory}"(i32 %5) #2', '%6 = tail call i32 asm sideeffect "csrc 0x800, s2\\0Alw a5, 76(s3)\\0A", "={x15},~{memory}"() #2', '%7 = tail call i32 asm sideeffect "", "={x12},{x15},{x12},~{memory}"(i32 %6, i32 12) #2', 'tail call void asm sideeffect "mv a1, s0\\0Aaddi a0, sp, 8\\0Ajalr a5\\0A", "{x12},{x15},~{x10},~{x11},~{x13},~{x14},~{memory}"(i32 %7, i32 %6) #2', 'unreachable'], 'tsl9_queue_release_12ca6': ['tail call void asm sideeffect "sh zero, 0(s0)\\0Acsrs 0x800, s2\\0Aaddi a0, sp, 8\\0A", "~{x10},~{memory}"() #2', 'tail call void asm sideeffect "jal ra, tsl9_queue_external_82d2\\0A", "~{x10},~{x11},~{x12},~{x13},~{x14},~{x15},~{memory}"() #2', 'unreachable'], 'tsl9_queue_validate_12cb4': ['%1 = tail call i32 asm sideeffect "", "={x10},~{memory}"() #2', 'tail call void asm sideeffect ".Lqhandled:\\0Ac.bnez a0, .Lqhandled\\0A.reloc .-2, R_RISCV_RVC_BRANCH, tsl9_queue_advance_12cee\\0A", "{x10},~{memory}"(i32 %1) #2', '%2 = tail call i32 asm sideeffect "lhu a5, 8(sp)\\0A", "={x15},~{memory}"() #2', 'tail call void asm sideeffect ".Lqother:\\0Abne a5, s4, .Lqother\\0A.reloc .-4, R_RISCV_BRANCH, tsl9_queue_other_12d78\\0A", "{x15},~{memory}"(i32 %2) #2', '%3 = tail call i32 asm sideeffect "lbu a4, 10(sp)\\0A", "={x14},~{memory}"() #2', 'tail call void asm sideeffect ".Lqlength:\\0Abne a4, a5, .Lqlength\\0A.reloc .-4, R_RISCV_BRANCH, tsl9_queue_advance_12cee\\0A", "{x14},{x15},~{memory}"(i32 %3, i32 4) #2', '%4 = tail call i32 asm sideeffect "lbu a4, 11(sp)\\0A", "={x14},~{memory}"() #2', 'tail call void asm sideeffect ".Lqmarker1:\\0Abne a4, a5, .Lqmarker1\\0A.reloc .-4, R_RISCV_BRANCH, tsl9_queue_advance_12cee\\0A", "{x14},{x15},~{memory}"(i32 %4, i32 181) #2', '%5 = tail call i32 asm sideeffect "lbu a4, 12(sp)\\0A", "={x14},~{memory}"() #2', 'tail call void asm sideeffect ".Lqmarker2:\\0Abne a4, a5, .Lqmarker2\\0A.reloc .-4, R_RISCV_BRANCH, tsl9_queue_advance_12cee\\0A", "{x14},{x15},~{memory}"(i32 %5, i32 98) #2', '%6 = tail call i32 asm sideeffect "lbu a5, 13(sp)\\0A", "={x15},~{memory}"() #2', 'tail call void asm sideeffect ".Lqzero:\\0Ac.beqz a5, .Lqzero\\0A.reloc .-2, R_RISCV_RVC_BRANCH, tsl9_queue_zero_12d0e\\0A", "{x15},~{memory}"(i32 %6) #2', 'tail call void asm sideeffect ".Lqresponse:\\0Abeq a5, a4, .Lqresponse\\0A.reloc .-4, R_RISCV_BRANCH, tsl9_queue_response_12d4c\\0A", "{x15},{x14},~{memory}"(i32 %6, i32 90) #2', 'unreachable'], 'tsl9_queue_advance_12cee': ['tail call void asm sideeffect "addi s1, s1, 1\\0A", "~{memory}"() #2', 'tail call void asm sideeffect ".Lqnext:\\0Abne s1, a5, .Lqnext\\0A.reloc .-4, R_RISCV_BRANCH, tsl9_queue_scan_12c86\\0A", "{x15},~{memory}"(i32 32) #2', 'unreachable'], 'tsl9_queue_finish_12cf8': ['tail call void asm sideeffect "lw ra, 76(sp)\\0Alw s0, 72(sp)\\0Alw s1, 68(sp)\\0Alw s2, 64(sp)\\0Alw s3, 60(sp)\\0Alw s4, 56(sp)\\0Alw s5, 52(sp)\\0Alw s6, 48(sp)\\0Alw s7, 44(sp)\\0Aaddi sp, sp, 80\\0Aret\\0A", ""() #2', 'unreachable'], 'tsl9_queue_zero_12d0e': ['tail call void asm sideeffect "jal ra, tsl9_queue_external_820c\\0A", "~{x10},~{x11},~{x12},~{x13},~{x14},~{x15},~{memory}"() #2', '%1 = tail call i32 asm sideeffect "lbu a0, 14(sp)\\0A", "={x10},~{memory}"() #2', 'tail call void asm sideeffect "", "{x10},~{memory}"(i32 %1) #2', 'tail call void asm sideeffect "jal ra, tsl9_queue_external_9454\\0A", "~{x10},~{x11},~{x12},~{x13},~{x14},~{x15},~{memory}"() #2', '%2 = tail call i32 asm sideeffect "", "={x10},{x10},~{memory}"(i32 0) #2', 'tail call void asm sideeffect "jal ra, tsl9_queue_external_9b36\\0A", "~{x10},~{x11},~{x12},~{x13},~{x14},~{x15},~{memory}"() #2', '%3 = tail call i32 asm sideeffect "lbu a0, 19(sp)\\0A", "={x10},~{memory}"() #2', '%4 = tail call i32 asm sideeffect "", "={x12},{x10},{x12},~{memory}"(i32 %3, i32 2) #2', 'tail call void asm sideeffect "addi a1, sp, 20\\0Ash zero, 20(sp)\\0A", "{x10},{x12},~{x11},~{memory}"(i32 %3, i32 %4) #2', 'tail call void asm sideeffect "jal ra, tsl9_queue_external_12abe\\0A", "~{x10},~{x11},~{x12},~{x13},~{x14},~{x15},~{memory}"() #2', '%5 = tail call i32 asm sideeffect "lbu a4, 19(sp)\\0Ash s4, 20(sp)\\0A", "={x14},~{memory}"() #2', '%6 = tail call i32 asm sideeffect "", "={x15},{x14},{x15},~{memory}"(i32 %5, i32 2) #2', 'tail call void asm sideeffect ".Lqselector:\\0Abeq a4, a5, .Lqselector\\0A.reloc .-4, R_RISCV_BRANCH, tsl9_queue_emit_12d42\\0A", "{x14},{x15},{x10},~{memory}"(i32 %5, i32 %6, i32 1) #2', 'tail call void asm sideeffect "", "{x10},{x14},{x15},~{memory}"(i32 2, i32 %5, i32 %6) #2', 'unreachable'], 'tsl9_queue_emit_12d42': ['%1 = tail call i32 asm sideeffect "", "={x12},{x12},~{memory}"(i32 2) #2', 'tail call void asm sideeffect "addi a1, sp, 20\\0A", "{x12},~{x11},~{memory}"(i32 %1) #2', 'tail call void asm sideeffect "jal ra, tsl9_queue_external_12abe\\0A", "~{x10},~{x11},~{x12},~{x13},~{x14},~{x15},~{memory}"() #2', 'tail call void asm sideeffect ".Lqemitted:\\0Ac.j .Lqemitted\\0A.reloc .-2, R_RISCV_RVC_JUMP, tsl9_queue_advance_12cee\\0A", "~{memory}"() #2', 'unreachable'], 'tsl9_queue_response_12d4c': ['%1 = tail call i32 asm sideeffect "lbu a4, 14(sp)\\0A", "={x14},~{memory}"() #2', 'tail call void asm sideeffect ".Lqresponse_reject:\\0Abne a4, a5, .Lqresponse_reject\\0A.reloc .-4, R_RISCV_BRANCH, tsl9_queue_advance_12cee\\0A", "{x14},{x15},~{memory}"(i32 %1, i32 85) #2', '%2 = tail call i32 asm sideeffect "lw a5, 76(s3)\\0Aaddi a0, sp, 20\\0A", "={x15},~{x10},~{memory}"() #2', '%3 = tail call i32 asm sideeffect "", "={x12},{x15},{x12},~{memory}"(i32 %2, i32 12) #2', 'tail call void asm sideeffect "addi a1, sp, 8\\0Ajalr a5\\0A", "{x12},{x15},~{x10},~{x11},~{x13},~{x14},~{memory}"(i32 %3, i32 %2) #2', '%4 = tail call i32 asm sideeffect "", "={x15},{x15},~{memory}"(i32 86) #2', 'tail call void asm sideeffect "addi a0, sp, 20\\0Asb a5, 26(sp)\\0Asb zero, 31(sp)\\0A", "{x15},~{x10},~{memory}"(i32 %4) #2', 'tail call void asm sideeffect "jal ra, tsl9_queue_external_12a08\\0A", "~{x10},~{x11},~{x12},~{x13},~{x14},~{x15},~{memory}"() #2', 'tail call void asm sideeffect ".Lqresponded:\\0Ac.j .Lqresponded\\0A.reloc .-2, R_RISCV_RVC_JUMP, tsl9_queue_advance_12cee\\0A", "~{memory}"() #2', 'unreachable'], 'tsl9_queue_other_12d78': ['%1 = tail call i32 asm sideeffect "lw a5, 0(s7)\\0A", "={x15},~{memory}"() #2', '%2 = add i32 %1, 4', '%3 = inttoptr i32 %2 to ptr', '%4 = load volatile i8, ptr %3, align 1', '%5 = and i8 %4, 8', '%6 = zext nneg i8 %5 to i32', 'tail call void asm sideeffect ".Lqother_gated:\\0Ac.bnez a5, .Lqother_gated\\0A.reloc .-2, R_RISCV_RVC_BRANCH, tsl9_queue_advance_12cee\\0A", "{x15},~{memory}"(i32 %6) #2', 'tail call void asm sideeffect "jal ra, tsl9_queue_external_81aa\\0A", "~{x10},~{x11},~{x12},~{x13},~{x14},~{x15},~{memory}"() #2', '%7 = tail call i32 asm sideeffect "", "={x10},~{memory}"() #2', 'tail call void asm sideeffect ".Lqother_disabled:\\0Ac.beqz a0, .Lqother_disabled\\0A.reloc .-2, R_RISCV_RVC_BRANCH, tsl9_queue_advance_12cee\\0A", "{x10},~{memory}"(i32 %7) #2', 'tail call void asm sideeffect "addi a0, sp, 8\\0A", "~{x10},~{memory}"() #2', 'tail call void asm sideeffect "jal ra, tsl9_queue_external_14d2e\\0A", "~{x10},~{x11},~{x12},~{x13},~{x14},~{x15},~{memory}"() #2', 'tail call void asm sideeffect ".Lqother_done:\\0Ac.j .Lqother_done\\0A.reloc .-2, R_RISCV_RVC_JUMP, tsl9_queue_advance_12cee\\0A", "~{memory}"() #2', 'unreachable']}


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
            elif op==0x13 and f3==0:ins=['ADDI',rd,rs,sx(w>>20,12)]
            elif op==3 and f3 in (2,4,5):ins=[{2:'LW32',4:'LBU8',5:'LHU16'}[f3],rd,rs,sx(w>>20,12)]
            elif op==0x23 and f3 in (0,1,2):
                offset=((w>>25)<<5)|((w>>7)&31);ins=[{0:'SB8',1:'SH16',2:'SW32'}[f3],rs2,rs,sx(offset,12)]
            elif op==0x33 and f3==0 and w>>25==1:ins=['MUL',rd,rs,rs2]
            elif op==0x73 and f3 in (2,3):ins=['CSRRS' if f3==2 else 'CSRRC',rd,w>>20,rs]
            elif op==0x63 and f3 in (0,1):
                imm=((w>>31)<<12)|(((w>>7)&1)<<11)|(((w>>25)&63)<<5)|(((w>>8)&15)<<1)
                ins=['BEQ' if f3==0 else 'BNE',rs,rs2,BASE+at+sx(imm,13)]
            elif op==0x6f:
                imm=((w>>31)<<20)|(((w>>21)&1023)<<1)|(((w>>20)&1)<<11)|(((w>>12)&255)<<12)
                ins=['JAL',rd,BASE+at+sx(imm,21)]
            else:raise ValueError('wide opcode/width outside exact bounded queue instruction families')
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
            elif q==1 and f3==5:
                n=(((w>>12)&1)<<11)|(((w>>11)&1)<<4)|(((w>>9)&3)<<8)|(((w>>8)&1)<<10)|(((w>>7)&1)<<6)|(((w>>6)&1)<<7)|(((w>>3)&7)<<1)|(((w>>2)&1)<<5)
                ins=['J',BASE+at+sx(n,12)]
            else:raise ValueError('compressed opcode/width outside exact bounded queue families')
        rows.append([at,size]+ins);at+=size
    return rows


def typed_contract(rows,pending):
    expected=copy.deepcopy(EXPECTED)
    if pending:
        for row in expected:
            if row[0] in {r[0] for r in RELATIONS}:row[-1]=BASE+row[0]
    need(rows==expected,'all107 typed instructions/widths/physical operands/order/cold control targets')
    at={r[0]:r for r in rows}
    need(at[0]==[0,2,'ADDI',2,2,-80] and at[178]==[178,2,'ADDI',2,2,80] and at[180]==[180,2,'RET',1],
         'one original80B architectural frame and exact return cleanup')
    need(at[78]==[78,4,'SH16',0,8,0] and at[72]==[72,2,'MV',11,8],
         'then-live physical S0 used across opaque call, no saved C SSA slot')
    need([at[p] for p in (62,82)]==[[62,4,'CSRRC',0,0x800,18],[82,4,'CSRRS',0,0x800,18]],
         'paired original CSR operations using then-live S2, no assumed fixed postcallee value')
    need(at[66]==[66,4,'LW32',15,19,76] and at[256]==[256,4,'LW32',15,19,76],
         'fresh physical S3 resident pointer load at each indirect call')
    need([at[p] for p in (76,266)]==[[76,2,'JALR',1,15,0],[266,2,'JALR',1,15,0]],'two true RA-linking indirect calls')
    # After the response indirect call, the original explicitly writes A5/A0
    # and two bytes, leaving A1/A2 as the unknown callee actually returned them.
    need(not any(r[2] in ('ADDI','MV','LW32','LHU16','LBU8') and r[3] in (11,12) for r in rows if 268<=r[0]<282),
         'response A1/A2 residues remain then-live, no synthetic recopy or constant')
    return rows


def original():
    raw=FIRMWARE.read_bytes();need(len(raw)==76800 and sha(raw)==PINS[FIRMWARE],'whole original BIN')
    code=raw[BASE-0x8000:BASE-0x8000+314];need(sha(code)==ORIGINAL_PIN,'original314B span identity')
    typed_contract(decode(code),False)
    need(digest(DECODE)==PINS[DECODE],'pinned independent static decode')
    evidence=json.loads(DECODE.read_bytes());rows=evidence['rows']
    need((evidence['start'],evidence['end'],evidence['bytes'],evidence['instructions'],evidence['span_sha256'])==
         (BASE,BASE+314,314,107,ORIGINAL_PIN) and evidence['firmware_sha256']==PINS[FIRMWARE],'decode bounds/identity')
    need(b''.join(bytes.fromhex(r['bytes']) for r in rows)==code and
         [(r['addr']-BASE,r['size']) for r in rows]==[(r[0],r[1]) for r in EXPECTED],'complete original decode row coverage')
    return code


def masks():
    result=bytearray(b'\xff'*314)
    for at,kind,_ in RELATIONS:
        n,mask=MASKS[kind];result[at:at+n]=mask.to_bytes(n,'little')
    return result


def metadata(e):
    spans=[(s['offset'],s['offset']+s['size']) for s in e.sections if s['flags']&2 and s['size']]
    outside=bytes(v for i,v in enumerate(e.raw) if not any(a<=i<b for a,b in spans))
    return dict(header=e.header,program_headers=e.program_headers,sections=e.sections,symbols=e.symbols,
       relocations=e.relocations,noncode_section_hashes={s['name']:sha(e.data(s)) for s in e.sections if not s['flags']&2 and s['type']!=8},
       outside_allocated_code_sha256=sha(outside))


def elf_contract(e,native,official,full=True):
    schema=SCHEMAS['native' if native else 'partial']
    need(len(e.raw)==schema['header'][5]+40*schema['header'][11],'complete ELF extent without trailing bytes')
    need(e.header[0]==1 and e.header[6]==1 and not e.program_headers,'actual RV32 RVC ET_REL only, not an executable')
    gs=[s for s in e.symbols if s['info']>>4]
    expected={n:(0 if native else at,z,18,0,'.text.'+n if native else '.queue') for n,at,z in REGIONS}
    actual={s['name']:(s['value'],s['size'],s['info'],s['other'],e.sections[s['section']]['name']) for s in gs if s['section'] not in (0,65521)}
    need(actual==expected and len(gs)==18,'ten genuine FUNCs, exact region order/extent/ownership')
    und=[s for s in gs if s['section']==0]
    need(sorted(s['name'] for s in und)==sorted(UNDEFINED) and all(s['info']==16 and s['other']==s['size']==s['value']==0 for s in und)
         and not any(s['section']==65521 for s in gs),'eight genuine strong UND; no ABS/weak/fake resolution')
    alloc=[s for s in e.sections if s['flags']&2 and s['size']]
    need([(s['name'],s['address'],s['size'],s['type'],s['flags'],s['align']) for s in alloc]==
       ([('.text.'+n,0,z,1,6,2) for n,_,z in REGIONS] if native else [('.queue',0,314,1,6,2)]),'exact AX-only sections')
    code=b''.join(e.data('.text.'+n) for n in NAMES) if native else e.data('.queue')
    rows=typed_contract(decode(code),True);need(len(code)==314 and len(rows)==107,'actual314B107i')
    starts={'.text.'+n:at for n,at,_ in REGIONS};rels=[]
    for r in e.relocations:
        owner=e.sections[r['section']]['name'];s=e.symbols[r['symbol']]
        need(owner in starts if native else owner=='.queue','real relocation owner')
        at=r['offset']+(starts[owner] if native else 0);rels.append((at,r['type'],s['name'],r['addend']))
        need((s['info']==16 and s['section']==0) if r['type']==17 else (s['info']==18 and s['section'] not in (0,65521)),
             'genuine external call versus defined architectural branch target')
    need(rels==[(a,k,n,0) for a,k,n in RELATIONS],'all25 actual relocation sites/types/targets/addends')
    bitmasks=masks();need(all(not ((a^b)&mask) for a,b,mask in zip(code,official,bitmasks)),'all original nonrelocation bits, including link rd and branch register fields')
    need(metadata(e)==schema,'full actual ELF metadata/noncode/gap bytes')
    if full:need(sha(e.raw)==ELF_PINS[native],'whole measured ELF identity')
    controls=[]
    original_rows={r[0]:r for r in EXPECTED}
    for at,kind,name in RELATIONS:
        row=original_rows[at];controls.append(dict(offset=at,kind=kind,target_symbol=name,nominal_PC=BASE+at,
          nominal_target=row[-1],pending_machine_target=BASE+at,RA_continuation=BASE+at+row[1] if kind==17 else None,
          link_rd=1 if kind==17 else None,fallthrough=BASE+at+row[1] if kind in (16,44) else None))
    return dict(sha256=sha(e.raw),header=e.header,program_headers=e.program_headers,sections=e.sections,
       symbols=e.symbols,relocations=e.relocations,code_hex=code.hex(),code_sha256=sha(code),typed_rows=rows,
       UND_providers=UNDEFINED,ABS_providers=[],local_ABS_metadata=sum(s['section']==65521 and not s['info']>>4 for s in e.symbols),
       controls=controls,retained_nonrelocation_bits=sum(n.bit_count() for n in bitmasks),fully_unmasked_bytes=sum(n==255 for n in bitmasks),
       pending_machine_immediates=25,defined_relocation_targets=16,UND_relocation_sites=9,firmware_ready=False)


def core_ir(text):
    result={}
    for name,body in re.findall(r'^define .*?@([^ (]+)\([^\n]*\{\n(.*?)^\}',text,re.M|re.S):
        result[name]=[re.sub(r', !(?:tbaa|srcloc) !\d+','',line.strip()) for line in body.splitlines() if line.strip()]
    return result


def ir_contract(text,language,full=True):
    normalized='\n'.join(text.splitlines()[2:])+'\n';core=core_ir(normalized)
    need(list(core)==NAMES and core==IR_CORE,'all literal SSA/constants/fresh physical-register ports in complete ten-function order')
    need(len(re.findall(r'load volatile i8',normalized))==1 and not re.search(r'\balloca\b|\b(?:undef|poison)\b|\.4byte|\.word|\.insn',normalized),
         'one real C volatile byte load, no frame/spill or opcode carrier')
    need('%3 = shl i32 %2, 16' in normalized and '%5 = lshr i32 %4, 16' in normalized and '%5 = and i8 %4, 8' in normalized,
         'C zero-extension and indirect byte mask dataflow')
    need(normalized.count('jal ra, tsl9_queue_external_')==9 and normalized.count('jalr a5\\0A')==2,
         'nine genuine external calls and two then-live A5 indirect calls')
    need(normalized.count('ret\\0A')==1 and 'mret' not in normalized and normalized.count('csrc 0x800, s2')==1 and normalized.count('csrs 0x800, s2')==1,
         'original RET and paired physical S2 CSR effects; IRQ ABI not assumed')
    if full:need(sha(normalized.encode())==IR_PINS[language],'complete normalized IR with all attributes/metadata')
    return dict(normalized_sha256=sha(normalized.encode()),core_SSA=core,C_volatile_byte_loads=1,
       C_zero_extension_shifts=[16,16],C_indirect_byte_mask=8,ordinary_C_ABI_proven=False)


def inputs(llvm):
    expected=dict(PINS);expected[Path(__file__).resolve()]=digest(__file__)
    expected[llvm.parent/'lib/clang/18/include/stdint.h']=HEADER_PIN
    expected.update({llvm/n:pin for n,pin in TOOLS.items()})
    need(all(digest(p)==pin for p,pin in expected.items()),'all source/decode/reader/probe/tool/header pins')
    return expected


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
        for name in [UNDEFINED[0],UNDEFINED[4],UNDEFINED[7],NAMES[6]]:
            at=symtab['offset']+gs[name]['index']*16
            raw(tag+'_fakeABS_'+name,e,n,at+14,'<H',65521)
            raw(tag+'_weak_'+name,e,n,at+12,'<B',34)
        at=symtab['offset']+gs[NAMES[8]]['index']*16
        raw(tag+'_FUNC_size',e,n,at+8,'<I',42);raw(tag+'_FUNC_value',e,n,at+4,'<I',2)
        sec=next(s for s in e.sections if s['flags']&2 and s['size'])
        raw(tag+'_writable_code',e,n,e.header[5]+40*sec['index']+8,'<I',7)
        check(tag+'_trailing_bytes','raw_ELF_reparsed',lambda ee=e,nn=n:elf_contract(ELF(ee.raw+b'\0\0'),nn,official,False))
        # Reparse actual mutated relocation records; these controls exercise
        # the specific target/family/addend gates before full metadata pins.
        for i,r in enumerate(e.relocations):
            table=next(s for s in e.sections if s['type']==4 and s['info']==r['section'])
            previous=sum(z['section']==r['section'] for z in e.relocations[:i]);at=table['offset']+12*previous
            raw(tag+'_RELA_addend_'+str(i),e,n,at+8,'<i',2)
            raw(tag+'_RELA_family_'+str(i),e,n,at+4,'<I',(r['symbol']<<8)|(16 if r['type']==17 else 17))
            wrong=gs[UNDEFINED[7] if e.symbols[r['symbol']]['name']!=UNDEFINED[7] else UNDEFINED[0]]['index']
            raw(tag+'_RELA_target_'+str(i),e,n,at+4,'<I',(wrong<<8)|r['type'])
        def offset(pc):
            region=next((name,a,z) for name,a,z in REGIONS if a<=pc<a+z)
            return e.section('.text.'+region[0])['offset']+pc-region[1] if n else e.section('.queue')['offset']+pc
        for name,pc,delta,xor in [('SP_frame80',0,0,4),('save_RA_slot',16,0,4),('queue_AUIPC',22,2,16),
            ('S2_initial_mask',32,2,16),('slot_MUL_operand',46,2,16),('LHU_slot_width',52,1,16),
            ('zeroextend_shift',56,0,4),('empty_branch_source',60,0,128),('CSR_clear_S2',62,2,8),
            ('S3_fresh_LW',66,2,8),('copy_source_S0',72,0,4),('dynamic_linkrd',76,1,16),
            ('thenlive_S0_release',78,2,8),('CSR_set_S2',82,2,8),('external_linkrd',88,0,128),
            ('result_branch',92,0,128),('ID_compare_S4',98,2,16),('length_byte_slot',102,2,16),
            ('marker1_constant',116,2,16),('marker2_constant',128,2,16),('commandzero_edge',140,1,32),
            ('response_selector',142,2,16),('scan_bound32',152,2,16),('restore_S0_slot',162,0,4),
            ('SP_cleanup80',178,0,4),('RET',180,0,4),('zero_arg14',186,2,16),('emit_arg19',200,2,16),
            ('SH_zero20',208,0,128),('thenlive_S4_store',220,2,16),('cold_selector_branch',228,2,16),
            ('emit_A1_address',236,0,4),('response_reject',252,2,16),('response_S3_fresh',256,2,8),
            ('response_A1_before_indirect',264,0,4),('response_dynamic_linkrd',266,1,16),
            ('response_byte26',274,0,128),('response_zero31',278,0,128),('other_live_S7',288,2,8),
            ('indirect_byte_width',292,1,16),('indirect_mask8',296,0,4),('other_disable_edge',304,1,32)]:
            at=offset(pc)+delta;raw(tag+'_'+name,e,n,at,'<B',e.raw[at]^xor)
        # Explicitly introduce writes to the two physical residue registers.
        for name,pc,reg in [('response_clobbers_A2',268,12),('response_clobbers_A1',272,11)]:
            at=offset(pc);width=4 if pc==268 else 2;word=int.from_bytes(e.raw[at:at+width],'little')
            raw(tag+'_'+name,e,n,at,'<I' if width==4 else '<H',(word&~0xf80)|(reg<<7))
        b=bytearray(e.raw);a=offset(256);z=offset(260);b[a:a+4],b[z:z+2]=b[z:z+2]+b[a:a+2],b[a+2:a+4]
        check(tag+'_response_fresh_load_order','raw_ELF_reparsed',lambda bb=b,nn=n:elf_contract(ELF(bb),nn,official,False))
    rowmap={r[0]:i for i,r in enumerate(EXPECTED)}
    for name,pc,field,value in [('parsed_thenlive_S0',78,4,9),('parsed_S3_load',256,4,20),('parsed_S2_CSR',82,5,17),
       ('parsed_SP_frame',0,5,-64),('parsed_ID0_edge',140,2,'BNEZ'),('parsed_cold_target',228,5,BASE+150),
       ('parsed_JAL_rd',88,3,0),('parsed_response_residue_A1',272,3,11)]:
        changed=copy.deepcopy(EXPECTED);changed[rowmap[pc]][field]=value
        check(name,'parsed_typed_rows',lambda c=changed:typed_contract(c,False))
    mutations=[('IR_thenlive_S0','sh zero, 0(s0)','sh zero, 0(s1)'),('IR_S3_fresh','lw a5, 76(s3)','lw a5, 76(s4)'),
      ('IR_S2_CSR','csrs 0x800, s2','csrs 0x800, s1'),('IR_SPframe','addi sp, sp, -80','addi sp, sp, -64'),
      ('IR_ID0edge','c.beqz a5, .Lqzero','c.bnez a5, .Lqzero'),('IR_coldbranch','beq a4, a5, .Lqselector','bne a4, a5, .Lqselector'),
      ('IR_external_target','jal ra, tsl9_queue_external_82d2','jal ra, tsl9_queue_external_820c'),
      ('IR_linkrd','jal ra, tsl9_queue_external_82d2','jal zero, tsl9_queue_external_82d2'),
      ('IR_resident_linkrd','jalr a5','jr a5'),('IR_response_A1_residue','addi a0, sp, 20\\0Asb a5, 26(sp)','addi a1, sp, 20\\0Asb a5, 26(sp)'),
      ('IR_response_A2_residue','(i32 86)','(i32 12)'),('IR_byte_fresh','load volatile i8','load i8'),
      ('IR_indirect_offset','%2 = add i32 %1, 4','%2 = add i32 %1, 8'),('IR_indirect_mask','%5 = and i8 %4, 8','%5 = and i8 %4, 4'),
      ('IR_zeroextension','%3 = shl i32 %2, 16','%3 = shl i32 %2, 15'),('IR_zero_arg','(i32 0)','(i32 1)'),
      ('IR_restore_RA','lw ra, 76(sp)','lw ra, 72(sp)'),('IR_marker181','i32 %4, i32 181','i32 %4, i32 180')]
    for name,old,new in mutations:
        need(old in text,'real IR mutation fixture '+name);changed=text.replace(old,new,1)
        check(name,'IR_text_structural_SSA',lambda c=changed:ir_contract(c,language,False))
    for name,old,new in [('IR_full_attributes','generic-rv32','other-rv32'),('IR_full_metadata','!"omnipotent char"','!"other"')]:
        need(old in text,'real complete IR fixture');changed=text.replace(old,new,1)
        check(name,'IR_text_full_normalized_pin',lambda c=changed:ir_contract(c,language,True),True)
    for name,changed in [('MD_target',md.replace('native.o:','other.o:',1)),('MD_missing_header',' '.join(md.splitlines()[:-1])),('MD_extra',md+'\nextra.h\n')]:
        check(name,'MD_text',lambda c=changed:md_contract(c,llvm,out))
    return results


def evaluate(root,llvm,out,language):
    need(root.resolve()==ROOT,'canonical project root');before=inputs(llvm);official=original()
    native=ELF(out/'native.o');partial=ELF(out/'partial.o')
    nf=elf_contract(native,True,official);pf=elf_contract(partial,False,official)
    need(nf['code_hex']==pf['code_hex'],'partial composition preserves all native bytes')
    text=(out/'native.ll').read_text(encoding='utf-8');ir=ir_contract(text,language)
    md=(out/'native.d').read_text(encoding='utf-8');deps=md_contract(md,llvm,out)
    commands=[dict(label=n,argv=portable(a,ROOT,llvm),returncode=0) for n,a in recipes(llvm,out,language)]
    need(json.loads((out/'recipes.json').read_bytes())==json.loads(json.dumps(commands)),'exact five successful producer recipes')
    files=sorted(['native.o','partial.o','native.ll','native.d','recipes.json']+[n+'.log' for n,_ in recipes(llvm,out,language)])
    need(sorted(p.name for p in out.iterdir() if p.name!='verification.json')==files and
         all(p.is_file() and not p.is_symlink() for p in out.iterdir()),'complete exact output inventory')
    for name in ['compile','IR','link']:need(not (out/(name+'.log')).read_bytes(),'empty successful diagnostic '+name)
    for name,artifact in [('object','native.o'),('partial','partial.o')]:
        log=(out/(name+'.log')).read_text();need(str(out/artifact) in log and all(n in log for n in NAMES+UNDEFINED),'actual artifact/symbol dump binding')
    artifacts=[dict(path=portable(str(out/n),ROOT,llvm),size=(out/n).stat().st_size,sha256=digest(out/n)) for n in files]
    controls=negatives(native,partial,text,language,official,md,llvm,out)
    need(before==inputs(llvm) and all(digest(out/Path(a['path']).name)==a['sha256'] for a in artifacts),'all read inputs/artifacts stable')
    record=dict(schema='TSL9-queue-consumer-native-v3-formal-v3',language=language,firmware_ready=False,target_executed=False,ISA_emulated=False,
       inputs=[dict(path=portable(str(p),ROOT,llvm),size=p.stat().st_size,sha256=v) for p,v in before.items()],
       original=dict(base=0x8000,start=BASE,end=BASE+314,bytes=314,instructions=107,sha256=ORIGINAL_PIN,typed_rows=EXPECTED),
       native=nf,partial=pf,ir=ir,md_dependencies=deps,recipes=commands,artifacts=artifacts,negative_controls=controls,
       static_contract=dict(architectural_frame_bytes=80,CSR_number=0x800,CSR_source='then-live S2',initial_S2=136,
         resident_calls=[dict(PC=BASE+p,RA_continuation=BASE+p+2,read='fresh LW A5,76(then-live S3)',target='unknown') for p in (76,266)],
         initial_S3=0x40000,initial_AUIPC_PC=BASE+22,nominal_initial_S5=(BASE+22+0x1fff9000+970)&0xffffffff,
         slot_release='SH zero,0(then-live S0) after opaque indirect call',response_A1_A2='unmodified callee residues before external12A08',
         all_relocations_resolved=False,ordinary_C_ABI_proven=False),limitations=[
        'Ten FUNC symbols are private physical-register regions and fallthrough boundaries, not independent ordinary C ABI functions.',
        'Actual ET_REL bytes retain all25 symbolic control immediates; eight external providers remain genuine UND and no ABS provider is invented.',
        'S0/S2/S3/SP and response A1/A2 are read as then-live physical state after opaque calls, not assumed ordinary callee-saved values.',
        'The AUIPC address calculation requires nominal original placement; the partial ET_REL has VA0 and is not an installed image.',
        'Two indirect calls depend on fresh LW[then-live S3+76]; resident identity/ABI, CSR meaning, interrupts, silicon and physical timing are unproved.',
        'No target/ISA/MMIO execution, full firmware BIN, OTA acceptance or successful flashing.'])
    # portable() intentionally preserves tuples: normalize the full record to
    # JSON data before exact replay comparison, not merely its recipe subset.
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
    need(out.is_relative_to(HERE/'build/verified-v3') and out.parent==HERE/'build/verified-v3' and out.name==language,'owned formal v3 queue output only')
    if not args.replay:
        need(not out.exists(),'fresh output only');before=inputs(llvm);out.mkdir(parents=True);commands=[]
        for label,argv in recipes(llvm,out,language):
            child=subprocess.run(argv,cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
            (out/(label+'.log')).write_bytes(child.stdout);commands.append(dict(label=label,argv=portable(argv,ROOT,llvm),returncode=child.returncode))
            need(child.returncode==0,'actual compiler/linker recipe failed '+label)
        (out/'recipes.json').write_bytes((json.dumps(commands,indent=2)+'\n').encode());need(before==inputs(llvm),'inputs stable across actual build')
    record,encoded=evaluate(ROOT,llvm,out,language)
    if args.replay:need(saved==record and receipt.read_bytes()==encoded.encode(),'complete saved record and canonical LF bytes equal replay')
    else:(out/'verification.json').write_bytes(encoded.encode())
    print(json.dumps(dict(result='PASS',language=language,bytes=314,instructions=107,FUNCs=10,UND=8,retained_RELA=25,
       controls=len(record['negative_controls']),receipt_sha256=sha(encoded.encode()),firmware_ready=False)))
    if args.require_firmware_ready:
        print('REJECTED: unresolved symbolic/indirect/CSR/physical ABI; firmware_ready=false.',file=sys.stderr);return 1
    return 0


if __name__=='__main__':
    try:sys.exit(main())
    except (ValueError,OSError,KeyError,IndexError,StopIteration) as exc:
        print('FAIL: '+str(exc),file=sys.stderr);sys.exit(1)
