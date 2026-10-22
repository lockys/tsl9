#!/usr/bin/env python3
"""Source-only calibration-byte relation; arithmetic examples are not target execution."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
FW = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
BASE = 0x8000
OLD = 'analysis/v4160-system-clock-query-2026-10-21/source/'


def need(v, message):
    if not v:
        raise ValueError(message)


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def read(p):
    return json.loads(p.read_bytes())


def locate(root, name):
    p = root / name
    if name.startswith('analysis/') and not p.is_file():
        p = root / ('apk-analysis/tsl9-' + name.removeprefix('analysis/'))
    return p


def module(p):
    spec = importlib.util.spec_from_file_location('nv_calibration_primary_fields', p)
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj


def gate(raw, old):
    need(old.addi(raw, 0x1973c) == (15, 3, 108), 'Fresh word address at live GP+108')
    need(old.c_mem(raw, 0x19740) == (15, 15, 0), 'Fresh word read before deriving calibration')
    need(old.pair(raw, 0x19742, 0x19746, 14) == 8000000, 'Unsigned divisor8000000')
    old.r_op(raw, 0x1974a, 15, 15, 14, 5, 1)
    word = old.word(raw, 0x1974e)
    need((word & 127, (word >> 12) & 7, (word >> 7) & 31, (word >> 15) & 31, word >> 20)
         == (0x13, 7, 15, 15, 255), 'Mask quotient to byte before both stores')
    need(old.store(raw, 0x19752) == (15, 3, 382, 0), 'Unsigned quotient byte outputGP+382')
    need(old.addi(raw, 0x19756) == (14, 0, 1000), 'Halfword multiplier1000')
    old.r_op(raw, 0x1975a, 15, 15, 14, 0, 1)
    need(old.store(raw, 0x1975e) == (15, 3, 380, 1), 'Halfword outputGP+380')
    need(old.half(raw, 0x19762) == 0x8082, 'Live RA normal return')
    need(old.load(raw, 0x19770) == (14, 3, 382, 4), 'Timer fresh unsigned byte from live GP+382')


def relation():
    examples = []
    for frequency, argument in [(0, 1), (7999999, 1), (8000000, 1), (2048000000, 1),
                                (2147483648, 1), (4294967295, 0xffffffff), (2040000000, 0xffffffff)]:
        q = (frequency // 8000000) & 255
        examples.append(dict(synthetic_frequency_word=frequency, synthetic_argument=argument,
                             unsigned_quotient_byte=q, halfword=(q * 1000) & 65535,
                             timer_product_low32=(q * argument) & 0xffffffff))
    return dict(formula='q=(unsigned READ32(GP+108)/8000000)&255; WRITE8(GP+382,q); WRITE16(GP+380,(q*1000)&65535)',
                timer_relation='If the live GP and stored byte are preserved, timer READ8(GP+382)=q and low32 product=q*input modulo2^32',
                input_frequency_word_actual_value_proved=False, same_GP_across_functions_proved=False,
                no_intervening_write_proved=False, calibrated_physical_time_units_proved=False,
                quotient_byte_truncated_before_multiplication=True, zero_quotient_possible=True,
                synthetic_arithmetic_examples=examples, examples_are_target_execution=False)


def metadata(root):
    seal = read(HERE / 'seal.json')
    for name, pin in seal['members'].items():
        p = (HERE / name).resolve()
        need(p.is_relative_to(HERE) and sha(p) == pin, 'Calibration member ' + name)
    for name, pin in seal['external_inputs'].items():
        need(sha(locate(root, name)) == pin, 'Pinned calibration dependency ' + name)
    need((HERE / 'README.md').read_bytes() == (HERE / 'readme.zh-TW.md').read_bytes(), 'Traditional Chinese default')
    ledger = read(HERE / 'ledger.json')
    rows = ledger['calibration_rows']
    need(len(rows) == 11 and sum(x['size'] for x in rows) == 40, 'Complete retained calibration body')
    need(hashlib.sha256(b''.join(bytes.fromhex(x['bytes']) for x in rows)).hexdigest()
         == '54981bbd3ffcfe30f15091ac55558d66f221f32712e54ac53e33f9ff2c2afb43', 'Retained original40B digest')
    return ledger


def inspect(root, firmware=None):
    ledger = metadata(root)
    controls = []
    if firmware is not None:
        raw = firmware.read_bytes()
        need(len(raw) == 76800 and hashlib.sha256(raw).hexdigest() == FW, 'Exact original application only')
        old = module(locate(root, OLD + 'inspect-source.py'))
        for x in ledger['calibration_rows']:
            need(raw[x['addr'] - BASE:x['addr'] - BASE + x['size']] == bytes.fromhex(x['bytes']), 'Every retained calibration instruction')
        need(raw[0x11770:0x11774].hex() == ledger['timer_byte_load_hex'], 'Whole timer byte-load instruction')
        gate(raw, old)
        for label, pc, bit in [('wrong_frequency_word', 0x1973c, 20), ('signed_division', 0x1974a, 12),
                               ('wrong_quotient_mask', 0x1974e, 20), ('wrong_byte_destination', 0x19752, 7),
                               ('wrong_halfword_multiplier', 0x19756, 20), ('halfword_becomes_byte', 0x1975e, 12),
                               ('timer_reads_other_byte', 0x19770, 20)]:
            changed = bytearray(raw)
            changed[pc - BASE + bit // 8] ^= 1 << (bit % 8)
            try:
                gate(bytes(changed), old)
            except ValueError:
                controls.append(dict(case=label, PC=pc, bit=bit, rejected=True,
                                     mutated_FW_sha256=hashlib.sha256(changed).hexdigest()))
            else:
                raise ValueError('Accepted incorrect calibration source operand')
    return dict(passed=True, metadata_only=firmware is None, actual_original_firmware_read=firmware is not None,
                reviewed_source_bytes=44, reviewed_source_rows=12, calibration_body_bytes=40,
                timer_load_is_subset_of_separate_timer_source_review=True, relation=relation(), controls=controls,
                old_source_full_matrix_run=False, compiler_or_linker_invoked=False, target_execution=False,
                CPU_or_ISA_or_ESIL_emulation=False, hardware=False, network=False, new_BIN=False,
                installed_ROM_or_clock_proved=False, hardware_OTA_proved=False, rebuilt_flashable_BIN=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project-root', required=True, type=Path)
    parser.add_argument('--firmware', type=Path)
    args = parser.parse_args()
    print(json.dumps(inspect(args.project_root.resolve(), args.firmware)))
