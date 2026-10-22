#!/usr/bin/env python3
"""Bounded static BOOT reset operands; no CPU, HOST model, or MMIO execution."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
FW_SHA = '650cbb626d45c94ea7617c4647c6fc184bc6dcf0d21615f62c5d4b119e8162bb'
FW_NAME = 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2580-V1.0.00-decoded.bin'
CAPTURE = 'analysis/v4160-ota-handler-2026-10-22/source-review/capture-source.py'
ORI = 'analysis/v4160-adc-config-2026-10-22/source-review/raw.py'
REFERENCE = 'analysis/v4160-adc-config-2026-10-22/instruction-reference/rv_i-excerpt.txt'
REG = ['zero', 'ra', 'sp', 'gp', 'tp', 't0', 't1', 't2', 's0', 's1',
       'a0', 'a1', 'a2', 'a3', 'a4', 'a5', 'a6', 'a7', 's2', 's3',
       's4', 's5', 's6', 's7', 's8', 's9', 's10', 's11', 't3', 't4', 't5', 't6']
FIELDS = ('PC', 'bytes', 'raw_hex', 'op', 'rd', 'rs1', 'rs2', 'immediate', 'target', 'memory_width', 'CSR')


def need(value, message):
    if not value:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def csr_fields(word):
    # Standard CSR operand bits, corroborated against the retained/fresh r2
    # text for every CSR row in this bounded reset. No CSR state is evaluated.
    need(word & 127 == 0x73 and (word >> 12) & 7 in (1, 2, 3),
         'Admitted standard register CSR operation')
    return dict(CSR=word >> 20,
                operation={1: 'CSRRW_write', 2: 'CSRRS_set_bits',
                           3: 'CSRRC_clear_bits'}[(word >> 12) & 7],
                rd=(word >> 7) & 31, rs1=(word >> 15) & 31)


def decoder(root):
    inherited = load(root / CAPTURE, 'boot_reset_inherited').context(root)[0]
    extension = load(root / ORI, 'boot_reset_existing_ori')

    def decode(raw, pc):
        word = int.from_bytes(raw[:4], 'little')
        if word == 0x30200073:
            row = dict(PC=pc, bytes=4, raw_hex=raw[:4].hex(), op='mret', rd=None,
                       rs1=None, rs2=None, immediate=None, target=None, memory_width=None)
        elif word & 127 == 0x73 and (word >> 12) & 7 in (1, 2, 3):
            item = csr_fields(word)
            row = dict(PC=pc, bytes=4, raw_hex=raw[:4].hex(), op=item['operation'],
                       rd=item['rd'], rs1=item['rs1'], rs2=None, immediate=None,
                       target=None, memory_width=None, CSR=item['CSR'])
        else:
            row = extension.decode(raw, pc, inherited)
        return {key: row.get(key) for key in FIELDS}
    return decode


def rows(image, decode, start, end):
    result = []
    pc = start
    while pc < end:
        row = decode(image[pc - 0x1000:], pc)
        need(row['bytes'] in (2, 4) and pc + row['bytes'] <= end, 'Whole bounded instruction')
        result.append(row)
        pc += row['bytes']
    need(pc == end, 'Exact source end')
    return result


def exact(index, pc, **fields):
    need(all(index[pc][key] == value for key, value in fields.items()), 'Operand gate at ' + hex(pc))


def pair(index, pc, rd):
    hi, lo = index[pc], index[pc + 4]
    exact(index, pc, op='auipc', rd=rd)
    exact(index, pc + 4, op='addi', rd=rd, rs1=rd)
    return (pc + hi['immediate'] + lo['immediate']) & 0xffffffff


def facts(vector, body, adjacent):
    need(len(vector) == 1 and len(body) == 37 and len(adjacent) == 1, 'Full vector/reset/MRET row counts')
    exact({x['PC']: x for x in vector}, 0x1000, op='jal', rd=0, target=0x2bd8)
    index = {x['PC']: x for x in body}
    gp, sp, source = pair(index, 0x2bd8, 3), pair(index, 0x2be0, 2), pair(index, 0x2be8, 10)
    need((gp, sp, source) == (0x20004000, 0x20010000, 0x3e90), 'GP/SP/initializer numeric pairs')
    exact(index, 0x2bf0, op='addi', rd=11, rs1=3, immediate=0)
    exact(index, 0x2bf4, op='addi', rd=12, rs1=3, immediate=104)
    exact(index, 0x2bf8, op='bgeu', rs1=11, rs2=12, target=0x2c0c)
    exact(index, 0x2bfc, op='lw', rd=5, rs1=10, immediate=0, memory_width=32)
    exact(index, 0x2c00, op='sw', rs1=11, rs2=5, immediate=0, memory_width=32)
    exact(index, 0x2c04, op='addi', rd=10, rs1=10, immediate=4)
    exact(index, 0x2c06, op='addi', rd=11, rs1=11, immediate=4)
    exact(index, 0x2c08, op='bltu', rs1=11, rs2=12, target=0x2bfc)
    exact(index, 0x2c0c, op='addi', rd=10, rs1=3, immediate=104)
    end = pair(index, 0x2c10, 11)
    need(end == 0x200099a0, 'BSS numeric end')
    exact(index, 0x2c18, op='bgeu', rs1=10, rs2=11, target=0x2c26)
    exact(index, 0x2c1c, op='sw', rs1=10, rs2=0, immediate=0, memory_width=32)
    exact(index, 0x2c20, op='addi', rd=10, rs1=10, immediate=4)
    exact(index, 0x2c22, op='bltu', rs1=10, rs2=11, target=0x2c1c)
    exact(index, 0x2c26, op='addi', rd=5, rs1=0, immediate=31)
    exact(index, 0x2c28, op='CSRRW_write', CSR=0xbc0, rd=0, rs1=5)
    exact(index, 0x2c2c, op='addi', rd=5, rs1=0, immediate=3)
    exact(index, 0x2c2e, op='CSRRW_write', CSR=0x804, rd=0, rs1=5)
    exact(index, 0x2c32, op='lui', rd=5, immediate=0x2000)
    exact(index, 0x2c36, op='addi', rd=5, rs1=5, immediate=-1912)
    exact(index, 0x2c3a, op='CSRRS_set_bits', CSR=0x300, rd=0, rs1=5)
    mtvec_base = pair(index, 0x2c3e, 5)
    exact(index, 0x2c46, op='ori', rd=5, rs1=5, immediate=3)
    exact(index, 0x2c4a, op='CSRRW_write', CSR=0x305, rd=0, rs1=5)
    exact(index, 0x2c4e, op='jal', rd=1, target=0x2c78)
    mepc = pair(index, 0x2c52, 5)
    need((mtvec_base | 3, mepc) == (0x103b, 0x1a52), 'MTVEC and post-clock MEPC values')
    exact(index, 0x2c5a, op='CSRRW_write', CSR=0x341, rd=0, rs1=5)
    exact(index, 0x2c5e, op='jal', rd=0, target=0x40000)
    exact({x['PC']: x for x in adjacent}, 0x2c62, op='mret', raw_hex='73002030')
    need([x['PC'] for x in body if x['op'] == 'sw'] == [0x2c00, 0x2c1c], 'Only two local store instructions')
    return dict(initial_gp=gp, initial_sp=sp,
                copy=dict(read_PC=0x2bfc, write_PC=0x2c00, source=[source, source + 104],
                          destination=[gp, gp + 104], end_exclusive=True, bytes=104, words=26),
                zero=dict(write_PC=0x2c1c, destination=[gp + 104, end], end_exclusive=True,
                          bytes=end - gp - 104, words=(end - gp - 104) // 4),
                CSR=[dict(PC=0x2c28, CSR=0xbc0, operation='WRITE', value=31),
                     dict(PC=0x2c2e, CSR=0x804, operation='WRITE', value=3),
                     dict(PC=0x2c3a, CSR=0x300, operation='SET_BITS', mask=0x1888),
                     dict(PC=0x2c4a, CSR=0x305, operation='WRITE', value=0x103b),
                     dict(PC=0x2c5a, CSR=0x341, operation='WRITE', value=0x1a52)],
                clock_call=dict(PC=0x2c4e, rd=1, target=0x2c78, link=0x2c52,
                                effects_and_normal_return_proved=False),
                resident_handoff=dict(PC=0x2c5e, rd=0, target=0x40000,
                                      local_return_or_fallthrough=False),
                adjacent_MRET=dict(PC=0x2c62, reached_by_reset_fallthrough=False),
                bounded_numeric_store_union=[gp, end], bounded_direct_slot4004c_store=False,
                global_slot_writer_absence_proved=False, clock_does_not_write_slot_proved=False,
                installed_resident_identity_proved=False, physical_memory_map_proved=False)


def r2_fields(item):
    """Parse only these existing static text spellings; do not evaluate ESIL."""
    text = item['opcode']
    op, _, arguments = text.partition(' ')
    args = [x.strip() for x in arguments.split(',')] if arguments else []
    reg = lambda value: REG.index(value)
    value = lambda text: int(text, 0)
    row = {key: None for key in FIELDS}
    row.update(PC=item['addr'], bytes=item['size'], raw_hex=item['bytes'], op=op)
    if op in ('auipc', 'lui'):
        row.update(rd=reg(args[0]), immediate=(value(args[1]) << 12) & 0xffffffff)
    elif op in ('addi', 'ori'):
        row.update(rd=reg(args[0]), rs1=reg(args[1]), immediate=value(args[2]))
    elif op in ('mv', 'li'):
        row.update(op='addi', rd=reg(args[0]), rs1=reg(args[1]) if op == 'mv' else 0,
                   immediate=0 if op == 'mv' else value(args[1]))
    elif op in ('lw', 'sw'):
        address = re.fullmatch(r'(-?(?:0x[0-9a-f]+|\d+))\((\w+)\)', args[1])
        need(address is not None, 'Static memory operand spelling')
        row.update(rs1=reg(address[2]), immediate=value(address[1]), memory_width=32)
        row['rd' if op == 'lw' else 'rs2'] = reg(args[0])
    elif op in ('bleu', 'bltu'):
        row.update(op='bgeu' if op == 'bleu' else op,
                   rs1=reg(args[1] if op == 'bleu' else args[0]),
                   rs2=reg(args[0] if op == 'bleu' else args[1]), target=value(args[2]))
    elif op in ('csrw', 'csrs'):
        names = {'mstatus': 0x300, 'mtvec': 0x305, 'mepc': 0x341}
        row.update(op='CSRRW_write' if op == 'csrw' else 'CSRRS_set_bits', rd=0,
                   rs1=reg(args[1]), CSR=names[args[0]] if args[0] in names else value(args[0]))
    elif op in ('jal', 'j'):
        row.update(op='jal', rd=0 if op == 'j' else reg(args[0]), target=value(args[-1]))
    else:
        need(op == 'mret', 'Unreviewed static text opcode: ' + op)
    return row


def negative_controls(image, decode):
    tests = [(0x2bf4, 0x100000, 'copy_end_104_changed'),
             (0x2bf8, 0x1000, 'copy_guard_polarity_changed'),
             (0x2c14, 0x100000, 'BSS_end_changed'),
             (0x2c3a, 0x1000, 'MSTATUS_SET_changed_to_CLEAR'),
             (0x2c5a, 0x3000, 'MEPC_WRITE_changed_to_SET'),
             (0x2c5e, 0x80, 'resident_handoff_changed_to_linked_call'),
             (0x2c62, 0x30208014, 'adjacent_MRET_changed_to_RET')]
    result = []
    for pc, mask, name in tests:
        changed = bytearray(image)
        at = pc - 0x1000
        word = int.from_bytes(changed[at:at + 4], 'little') ^ mask
        changed[at:at + 4] = word.to_bytes(4, 'little')
        try:
            facts(rows(changed, decode, 0x1000, 0x1004), rows(changed, decode, 0x2bd8, 0x2c62),
                  rows(changed, decode, 0x2c62, 0x2c66))
        except ValueError:
            result.append(dict(PC=pc, case=name, xor_mask=mask, rejected=True))
        else:
            raise ValueError('Accepted actual raw operand negative: ' + name)
    return result


def inspect(root, firmware, r2=None):
    image = firmware.read_bytes()
    need(len(image) == 12288 and digest(image) == FW_SHA, 'Exact official BOOT ID2580')
    decode = decoder(root)
    vector = rows(image, decode, 0x1000, 0x1004)
    body = rows(image, decode, 0x2bd8, 0x2c62)
    adjacent = rows(image, decode, 0x2c62, 0x2c66)
    result = dict(schema='ID2580-bounded-reset-resident-source-v2', draft=False,
                  firmware=dict(path=FW_NAME, bytes=len(image), sha256=FW_SHA, analysis_base=0x1000),
                  reset_range=[0x2bd8, 0x2c62], reset_bytes=138, reset_rows=len(body),
                  reset_sha256=digest(image[0x1bd8:0x1c62]), adjacent_MRET_range=[0x2c62, 0x2c66],
                  vector=vector, reset=body, adjacent=adjacent, facts=facts(vector, body, adjacent),
                  initializer_source_sha256=digest(image[0x2e90:0x2ef8]),
                  inputs={name: digest((root / name).read_bytes()) for name in (CAPTURE, ORI, REFERENCE)},
                  local_checker_sha256=digest(Path(__file__).read_bytes()),
                  raw_operand_negatives=negative_controls(image, decode),
                  target_execution=False, HOST_execution=False, MMIO_execution=False,
                  ISA_emulation=False, ESIL_execution=False, network=False, new_BIN=False,
                  global_no_slot_writer_proved=False, installed_resident_proved=False)
    if r2:
        args = [str(r2), '-q', '-n', '-a', 'riscv', '-b', '32', '-m', '0x1000',
                '-e', 'scr.color=false', '-e', 'io.cache=false', '-c', 'pDj 142 @ 0x2bd8;q', str(firmware)]
        actual = subprocess.run(args, capture_output=True, timeout=60)
        need(actual.returncode == 0, 'Read-only static r2 capture')
        items = json.loads(actual.stdout)
        parsed = [r2_fields(item) for item in items]
        need(parsed == body + adjacent, 'All independent r2 raw/operand rows equal existing typed fields')
        result['r2_capture'] = dict(executable_sha256=digest(r2.read_bytes()),
            stdout_sha256=digest(actual.stdout), exit=actual.returncode, static_only=True,
            rows=[{key: item[key] for key in ('addr', 'size', 'bytes', 'opcode')} for item in items])
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project-root', required=True, type=Path)
    parser.add_argument('--firmware', required=True, type=Path)
    parser.add_argument('--r2-exe', type=Path)
    parser.add_argument('--emit-ledger', action='store_true', help='Print source JSON; this program never writes files.')
    args = parser.parse_args()
    actual = inspect(args.project_root.resolve(), args.firmware.resolve(), args.r2_exe)
    if args.emit_ledger:
        need(args.r2_exe is not None, 'Initial evidence capture requires independent static r2 readback')
        print(json.dumps(actual, ensure_ascii=False, indent=2))
        return
    expected = json.loads((HERE / 'ledger.json').read_bytes())
    captured = expected.pop('r2_capture')
    if args.r2_exe:
        need(actual.pop('r2_capture') == captured, 'Fresh static capture equality')
    else:
        need([r2_fields(row) for row in captured['rows']] == actual['reset'] + actual['adjacent'],
             'Retained actual r2 capture equals newly read firmware operands')
    need(actual == expected, 'Whole read-only source ledger equality')
    print(json.dumps(dict(passed=True, draft=False, actual_firmware_read=True, reset_bytes=138,
                         reset_rows=len(actual['reset']), adjacent_MRET_rows=1,
                         actual_raw_operand_negatives=len(actual['raw_operand_negatives']),
                         independent_static_operand_rows=len(captured['rows']),
                         global_no_slot_writer_proved=False, installed_resident_proved=False,
                         target_execution=False, HOST_execution=False, ISA_emulation=False, network=False)))


if __name__ == '__main__':
    main()
