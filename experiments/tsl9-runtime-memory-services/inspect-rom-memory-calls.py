#!/usr/bin/env python3
"""Decode exact-image ROM memory-call arguments offline; never execute firmware.

Python 3.10+ only. No disassembler, compiler, network or hardware dependency.
The optional saved SDK header verifies a default profile, not installed ROM.
"""
import argparse
import hashlib
import json
from pathlib import Path
import struct

ROOT = Path(__file__).resolve().parents[2]
FW = 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
FW_SHA256 = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
SDK_SHA256 = 'fab43e7b8e351596a14d2a434eea4fa79587a8b9bba12738897d35ee2c3dbf2e'
SPANS = [(0xa37c, 0xa38e), (0xb0ba, 0xb0d0), (0xb5e0, 0xb5f6),
         (0xceaa, 0xcec0), (0xd196, 0xd1a8), (0xd4f4, 0xd50a),
         (0xd75a, 0xd76c), (0xe0a4, 0xe0ba), (0xf0b0, 0xf0c6),
         (0xfa50, 0xfa62), (0xfb0c, 0xfb1e), (0xff44, 0xff56),
         (0x10158, 0x1016e), (0x10276, 0x10288)]


def need(ok, message):
    if not ok:
        raise ValueError(message)


def signed(value, bits):
    return value - (1 << bits) if value & (1 << (bits - 1)) else value


def word(image, pc):
    offset = pc - 0x8000
    need(0 <= offset <= len(image) - 4, 'Instruction outside exact image')
    return struct.unpack_from('<I', image, offset)[0]


def half(image, pc):
    offset = pc - 0x8000
    need(0 <= offset <= len(image) - 2, 'Compressed instruction outside exact image')
    return struct.unpack_from('<H', image, offset)[0]


def pair(image, pc, reg):
    a, b = word(image, pc), word(image, pc + 4)
    need(a & 127 == 0x17 and (a >> 7) & 31 == reg, 'Expected AUIPC destination')
    need(b & 0x707f == 0x13 and (b >> 7) & 31 == reg and (b >> 15) & 31 == reg,
         'Expected ADDI pair register relationship')
    return (pc + (a & 0xfffff000) + signed(b >> 20, 12)) & 0xffffffff


def compressed_li(image, pc, reg):
    value = half(image, pc)
    need(value & 0xe003 == 0x4001 and (value >> 7) & 31 == reg,
         'Expected compressed LI and register')
    return signed(((value >> 12) & 1) << 5 | ((value >> 2) & 31), 6)


def inspect(image, sdk_header=None):
    need(len(image) == 76800 and hashlib.sha256(image).hexdigest() == FW_SHA256,
         'Expected exact ID2966 V4.1.60 image; no version guessing')
    gp = pair(image, 0x186aa, 3)
    zero_end = pair(image, 0x186e2, 11)
    start_word = word(image, 0x186de)
    need(start_word & 0xfffff == 0x18513, 'Expected GP-relative zero start setup')
    zero_begin = (gp + signed(start_word >> 20, 12)) & 0xffffffff
    need((gp, zero_begin, zero_end) == (0x20004000, 0x20004080, 0x2000c958),
         'Exact-image initialization range')
    checked = False
    if sdk_header is not None:
        need(hashlib.sha256(sdk_header).hexdigest() == SDK_SHA256, 'Saved SDK header digest mismatch')
        lines = sdk_header.decode('gb18030').splitlines()
        need('LIB_FLASH_BASE_ADDRESSS' in lines[2713] and '0x00040000' in lines[2713], 'Saved SDK default base')
        need('FUNCITON_BASE_ADDRESSS' in lines[2720] and '+0x34' in lines[2720], 'Saved SDK default table offset')
        need('tmos_memset' in lines[2775] and 'BLE_LIB_JT(5)' in lines[2775], 'Saved SDK default index5')
        checked = True
    calls = []
    for start, end in SPANS:
        first, load = word(image, start), word(image, start + 4)
        need(first & 127 == 0x37 and (first >> 7) & 31 == 15 and first & 0xfffff000 == 0x40000,
             'Expected LUI A5 library base')
        need(load & 0x707f == 0x2003 and (load >> 15) & 31 == 15 and (load >> 7) & 31 == 6,
             'Expected LW T1 through A5')
        slot = ((first & 0xfffff000) + signed(load >> 20, 12)) & 0xffffffff
        need(slot == 0x40048, 'Pointer storage slot must be40048')
        count = compressed_li(image, start + 8, 12)
        fill = compressed_li(image, start + 10, 11)
        need(fill == 0 and 3 <= count <= 28, 'Original zero-value and length range')
        setup_pc = start + 12
        setup = word(image, setup_pc)
        if setup & 127 == 0x13:
            need(setup & 0x707f == 0x13 and (setup >> 7) & 31 == 10 and (setup >> 15) & 31 == 3,
                 'Expected ADDI A0,GP destination')
            offset = signed(setup >> 20, 12)
            destination = (gp + offset) & 0xffffffff
            source = 'live_gp_relative'
            tail = setup_pc + 4
        else:
            destination = pair(image, setup_pc, 10)
            offset = None
            source = 'pc_relative_literal'
            tail = setup_pc + 8
        need(tail + 2 == end and half(image, tail) == 0x8302, 'Exact final compressed JR T1')
        fits = zero_begin <= destination and destination + count <= zero_end
        need(fits, 'Conditional destination range must fit current startup zero span')
        calls.append(dict(start=start, end=end, pointer_slot=slot, pointer_slot_is_function_entry=False,
                          A0_destination=destination, destination_source=source, GP_offset=offset,
                          destination_setup_PC=setup_pc, tail_PC=tail, A1_value=fill, A2_length=count,
                          destination_end_exclusive=destination + count, conditional_zero_span_fit=fits,
                          requires_live_GP_equal_initial=(source == 'live_gp_relative')))
    need(len(calls) == 14 and sum(v['end'] - v['start'] for v in calls) == 280,
         'Fourteen exact complete original wrappers')
    return dict(schema='TSL9-ROM-memory-arguments-v1', passed=True, firmware_sha256=FW_SHA256,
                startup=dict(initial_GP=gp, zero_begin=zero_begin, zero_end_exclusive=zero_end), calls=calls,
                sum_of_requested_lengths=sum(v['A2_length'] for v in calls),
                sdk_default_profile=dict(name='tmos_memset', table_base=0x40034, index=5, pointer_slot=0x40048,
                                         expected_header_sha256=SDK_SHA256, header_checked=checked,
                                         interpretation_is_conditional=True, installed_implementation_proved=False),
                limits=dict(function_pointer_value_known=False, private_ABI_proved=False,
                            RAM_ownership_proved=False, invocations_observed=False,
                            target_executed=False, hardware_accessed=False, network=False,
                            firmware_ready=False, BIN_created=False))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--firmware', type=Path, default=ROOT / FW)
    parser.add_argument('--sdk-header', type=Path, help='optional previously saved pinned header')
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args()
    try:
        result = inspect(args.firmware.read_bytes(), args.sdk_header.read_bytes() if args.sdk_header else None)
    except (ValueError, OSError) as error:
        reason = 'Unable to read selected local input' if isinstance(error, OSError) else str(error)
        print(json.dumps(dict(passed=False, reason=reason)))
        raise SystemExit(1)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print('14 exact-image wrappers; requested lengths total %d bytes (not observed execution).' % result['sum_of_requested_lengths'])
        print('All conditional ranges fit startup zero span. Installed ROM, private ABI and RAM ownership remain unknown.')


if __name__ == '__main__':
    main()
