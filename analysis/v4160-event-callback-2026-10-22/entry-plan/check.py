#!/usr/bin/env python3
"""Read selected init operands as data, without target execution or ISA state."""
import argparse
import hashlib
import json
from pathlib import Path

FW = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
INIT = 'a6a0c6e308fb8480b628dc3b08e5aa9f1dcd0b1c1d879d37466a0eba9d16c542'
CALLBACK = '3e21432057f673abea404541e0745937d894448b492478b5fed5775e91b398bf'
BASE = 0x8000


def need(value, message):
    if not value:
        raise ValueError(message)


def H(data):
    return hashlib.sha256(data).hexdigest()


def signed(value, bits):
    return value - (1 << bits) if value & (1 << (bits - 1)) else value


def fields(raw):
    """Decode only selected data records; no CPU/register model."""
    half = int.from_bytes(raw[:2], 'little')
    size = 4 if half & 3 == 3 else 2
    need(len(raw) >= size, 'whole selected instruction')
    word = int.from_bytes(raw[:size], 'little')
    if size == 4:
        opcode = word & 127
        rd, rs1, rs2 = (word >> 7) & 31, (word >> 15) & 31, (word >> 20) & 31
        funct3 = (word >> 12) & 7
        if opcode in (0x37, 0x17):
            return size, 'lui' if opcode == 0x37 else 'auipc', rd, None, None, word & 0xFFFFF000
        if opcode == 0x13 and funct3 == 0:
            return size, 'addi', rd, rs1, None, signed(word >> 20, 12)
        if opcode == 3 and funct3 == 2:
            return size, 'lw', rd, rs1, None, signed(word >> 20, 12)
        if opcode == 0x23 and funct3 in (0, 1):
            immediate = ((word >> 25) << 5) | ((word >> 7) & 31)
            return size, 'sb' if funct3 == 0 else 'sh', None, rs1, rs2, signed(immediate, 12)
    else:
        quadrant, funct3, rd = half & 3, half >> 13, (half >> 7) & 31
        ci = signed((((half >> 12) & 1) << 5) | ((half >> 2) & 31), 6)
        if quadrant == 0 and funct3 == 2:
            immediate = (((half >> 10) & 7) << 3) | (((half >> 6) & 1) << 2) | (((half >> 5) & 1) << 6)
            return size, 'lw', 8 + ((half >> 2) & 7), 8 + ((half >> 7) & 7), None, immediate
        if quadrant == 1 and funct3 == 2:
            return size, 'addi', rd, 0, None, ci
        if quadrant == 1 and funct3 == 3 and rd not in (0, 2) and ci:
            return size, 'lui', rd, None, None, (ci << 12) & 0xFFFFFFFF
        if quadrant == 2 and funct3 == 4 and half & 0x1000 and not half & 0x7C and rd:
            return size, 'jalr', 1, rd, None, 0
    raise ValueError('unadmitted selected instruction form')


# Hand-reviewed against actual source-bound LLVM disassembly. These are operands,
# not an instruction interpreter or an expectation generated from this decoder.
EXPECTED = {
    0x8E8C: (4, 'lui', 8, None, None, 0x40000),
    0x8E90: (2, 'lw', 15, 8, None, 0x48),
    0x8E92: (2, 'lui', 12, None, None, 0x1000),
    0x8E96: (4, 'addi', 12, 12, None, -0x7B4),
    0x8E9A: (2, 'addi', 11, 0, None, 0),
    0x8E9C: (4, 'auipc', 10, None, None, 0x20002000),
    0x8EA0: (4, 'addi', 10, 10, None, 0x2F0),
    0x8EA6: (2, 'jalr', 1, 15, None, 0),
    0x8EC4: (4, 'lw', 15, 8, None, 0x80),
    0x8EC8: (4, 'auipc', 10, None, None, 0xFFFFF000),
    0x8ECC: (4, 'addi', 10, 10, None, 0x74C),
    0x8ED0: (2, 'jalr', 1, 15, None, 0),
    0x8ED2: (4, 'sb', None, 3, 10, 0x9D),
    0x8F5E: (4, 'lui', 8, None, None, 0x40000),
    0x8F7A: (2, 'addi', 9, 0, None, -2),
    0x8F7E: (4, 'lw', 15, 8, None, 0x80),
    0x8F82: (4, 'auipc', 10, None, None, 0xFFFFF000),
    0x8F86: (4, 'addi', 10, 10, None, 0x692),
    0x8F8A: (2, 'jalr', 1, 15, None, 0),
    0x8F8C: (4, 'sb', None, 3, 10, 0x94),
    0x8F90: (4, 'sh', None, 3, 9, 0x96),
    0x8F94: (4, 'lw', 15, 8, None, 0x80),
    0x8F98: (4, 'auipc', 10, None, None, 0xFFFFF000),
    0x8F9C: (4, 'addi', 10, 10, None, 0x67C),
    0x8FA0: (2, 'jalr', 1, 15, None, 0),
    0x8FA2: (4, 'sb', None, 3, 10, 0x98),
    0x8FA6: (4, 'sh', None, 3, 9, 0x9A),
}


def inspect(raw):
    rows = []
    for pc, expected in EXPECTED.items():
        start = pc - BASE
        observed = fields(raw[start:start + 4])
        need(observed == expected, 'selected raw operand mismatch at ' + hex(pc))
        rows.append({'PC': pc, 'fields': list(observed), 'raw_hex': raw[start:start + observed[0]].hex()})
    # Static PC-relative address arithmetic, not state stepping or call execution.
    buffer = (0x8E9C + EXPECTED[0x8E9C][-1] + EXPECTED[0x8EA0][-1]) & 0xFFFFFFFF
    callback = (0x8EC8 + EXPECTED[0x8EC8][-1] + EXPECTED[0x8ECC][-1]) & 0xFFFFFFFF
    count = EXPECTED[0x8E92][-1] + EXPECTED[0x8E96][-1]
    need(buffer == 0x2000B18C and callback == 0x8614 and count == 2124, 'static address/count arithmetic')
    lanes = []
    for hi, lo, load, call, store, handle in [(0x8F82, 0x8F86, 0x8F7E, 0x8F8A, 0x8F8C, 0x8F90),
                                              (0x8F98, 0x8F9C, 0x8F94, 0x8FA0, 0x8FA2, 0x8FA6)]:
        formed = (hi + EXPECTED[hi][-1] + EXPECTED[lo][-1]) & 0xFFFFFFFF
        need(formed == callback, 'additional genuine callback argument')
        lanes.append({'AUIPC_PC': hi, 'ADDI_PC': lo, 'pointer_load_PC': load, 'call_PC': call,
                      'return_PC': call + 2, 'A0': formed, 'slot_formula': 'S0_live + 0x80',
                      'context_byte_store_PC': store, 'context_byte_GP_offset': EXPECTED[store][-1],
                      'connection_halfword_store_PC': handle, 'connection_GP_offset': EXPECTED[handle][-1],
                      'connection_value': 'low16(S1_live); nominal 0xFFFE only if S1 preserved',
                      'A1_and_later': 'live residues after prior opaque calls',
                      'S0_S1_GP_preservation_proved': False})
    return {'selected_operands': rows,
            'buffer_call': {'call_PC': 0x8EA6, 'return_PC': 0x8EA8, 'pointer_load_PC': 0x8E90,
                            'nominal_slot': 0x40048, 'A0': buffer, 'A1': 0, 'A2': count,
                            'A3_and_later': 'unresolved incoming residues', 'callee_semantics_proved': False},
            'callback_call': {'call_PC': 0x8ED0, 'return_PC': 0x8ED2, 'pointer_load_PC': 0x8EC4,
                              'slot_formula': 'S0_live_at_8EC4 + 0x80',
                              'nominal_slot_if_S0_preserved': 0x40080, 'A0': callback,
                              'A1_and_later': 'live residues after intervening opaque calls',
                              'S0_preservation_across_prior_calls_proved': False},
            'result_store': {'PC': 0x8ED2, 'address_formula': 'GP_after_callback_call + 0x9D',
                             'width_bits': 8, 'value': 'low eight bits of returned A0',
                             'GP_preservation_proved': False},
            'lane_callback_calls': lanes}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--firmware', type=Path, required=True)
    p.add_argument('--report', type=Path)
    args = p.parse_args()
    raw = args.firmware.read_bytes()
    need(H(raw) == FW, 'authenticated original firmware')
    need(H(raw[0x8E88 - BASE:0x9008 - BASE]) == INIT, 'whole original init384 identity')
    need(H(raw[0x8614 - BASE:0x888C - BASE]) == CALLBACK, 'whole original callback632 identity')
    proof = inspect(raw)
    controls = []
    for pc in EXPECTED:
        changed = bytearray(raw)
        changed[pc - BASE] ^= 0x80
        try:
            inspect(changed)  # Explicitly bypass the file digest: test operands.
        except ValueError:
            controls.append({'PC': pc, 'actual_operand_bit_change_rejected': True})
        else:
            raise ValueError('selected operand mutation admitted')
    result = {'schema': 'TSL9-callback-init-selected-operands-v1', 'passed': True,
              'firmware_sha256': FW, 'init384_sha256': INIT, 'callback632_sha256': CALLBACK,
              'runner_sha256': H(Path(__file__).read_bytes()), 'proof': proof, 'controls': controls,
              'entire_init_semantics_proved': False, 'installed_ROM_identified': False,
              'callback_invocation_observed': False, 'BLE_transmission_observed': False,
              'target_execution': False, 'ISA_emulation': False, 'hardware': False, 'network': False}
    if args.report:
        need(not args.report.exists() and args.report.resolve() != args.firmware.resolve(), 'new distinct report')
        args.report.parent.mkdir(parents=True, exist_ok=True)
        with args.report.open('xb') as stream:
            stream.write((json.dumps(result, indent=2) + '\n').encode())
    print(json.dumps({'passed': True, 'selected_instructions': len(EXPECTED),
                      'operand_controls_rejected': len(controls), 'callback_argument': '0x8614',
                      'buffer_argument': '0x2000B18C', 'count_argument': 2124,
                      'ROM_semantics_proved': False, 'hardware_OTA_proved': False}))


if __name__ == '__main__':
    main()
