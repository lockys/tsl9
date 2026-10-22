#!/usr/bin/env python3
"""Read original BOOT clock bytes and existing Runtime raw-field evidence only."""
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
BOOT = 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2580-V1.0.00-decoded.bin'
APP = 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
REVIEW = 'analysis/boot2580-clock-2026-10-22/original_fields.py'
SNAPSHOT = 'analysis/boot2580-clock-2026-10-22/original-runtime-rows.json'
SOURCES = ['experiments/tsl9-v4160-clock-contract/src/clock_contract.c',
           'experiments/tsl9-v4160-clock-contract/src/clock_contract.h']
DELTA = 0x2c78 - 0x1874a


def need(value, message):
    if not value:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def inspect(root, r2):
    boot, app = (root / BOOT).read_bytes(), (root / APP).read_bytes()
    need(len(boot) == 12288 and sha(boot) == '650cbb626d45c94ea7617c4647c6fc184bc6dcf0d21615f62c5d4b119e8162bb', 'Official BOOT identity')
    need(len(app) == 76800 and sha(app) == '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667', 'Official Runtime identity')
    blob = boot[0x1c78:0x1d62]
    need(len(blob) == 234 and blob == app[0x1074a:0x10834], 'Whole clock byte equality')
    spec = importlib.util.spec_from_file_location('retained_clock_raw', root / REVIEW)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    snapshot = json.loads((root / SNAPSHOT).read_bytes())
    # This function performs raw operand gates only. Do not call report(): it
    # executes the old HOST suite and is outside this offline source scope.
    raw = module.raw_contract(app, snapshot)
    rows = []
    for old in snapshot['instructions']:
        pc = old['addr'] + DELTA
        opcode = old['opcode']
        if opcode.split(' ')[0] in ('bnez', 'bne', 'bgez', 'j'):
            opcode = re.sub(r'0x[0-9a-f]+$', lambda x: hex(int(x[0], 16) + DELTA), opcode)
        rows.append(dict(PC=pc, bytes=old['bytes'], size=old['size'], opcode=opcode))
    cursor = 0x2c78
    for row in rows:
        need(row['PC'] == cursor and boot[cursor - 0x1000:cursor - 0x1000 + row['size']].hex() == row['bytes'], 'Continuous original instruction rows')
        cursor += row['size']
    need(cursor == 0x2d62 and len(rows) == 93, 'Full clock extent')
    reg = {'sp':2, 'a2':12, 'a3':13, 'a4':14, 'a5':15}
    writes = set()
    for row in rows:
        op, _, operands = row['opcode'].partition(' ')
        if op in ('lui', 'lw', 'addi', 'ori', 'and', 'or', 'slli', 'li', 'andi'):
            writes.add(reg[operands.split(',')[0]])
        else:
            need(op in ('sw', 'bnez', 'bne', 'bgez', 'ret', 'j'), 'No unreviewed call/opcode')
    need(writes == {2,12,13,14,15}, 'All original own-written GPRs')
    capture = None
    if r2:
        args = [str(r2), '-q', '-n', '-a', 'riscv', '-b', '32', '-m', '0x1000',
                '-e', 'scr.color=false', '-e', 'io.cache=false', '-c', 'pDj 234 @ 0x2c78;q', str(root / BOOT)]
        result = subprocess.run(args, capture_output=True, timeout=60)
        need(result.returncode == 0, 'Static r2 decode')
        actual = [dict(PC=x['addr'], bytes=x['bytes'], size=x['size'], opcode=x['opcode']) for x in json.loads(result.stdout)]
        need(actual == rows, 'All 93 fresh BOOT static operands equal translated Runtime operands')
        capture = dict(executable_sha256=sha(r2.read_bytes()), stdout_sha256=sha(result.stdout),
                       rows=93, static_only=True, exit=result.returncode)
    memory = [dict(x, PC=x['PC'] + DELTA) for x in raw['memory_accesses']]
    counts = {label:sum(x['kind'] == kind and (x['base_register'] == 2) == stack for x in memory)
              for label,kind,stack in [('MMIO_read32','READ32',False), ('MMIO_write32','WRITE32',False),
                                       ('stack_read32','READ32',True), ('stack_write32','WRITE32',True)]}
    need(counts == dict(MMIO_read32=18, MMIO_write32=15, stack_read32=4, stack_write32=6), 'All static memory sites')
    rmw = [dict(x, read_PC=x['read_PC'] + DELTA, write_PC=x['write_PC'] + DELTA) for x in raw['RMW_order']]
    answer = dict(schema='ID2580-clock-static-source-v1', draft=True,
                firmware={BOOT:sha(boot), APP:sha(app)}, range=[0x2c78, 0x2d62],
                bytes=234, instructions=93, code_sha256=sha(blob), runtime_range=[0x1874a, 0x18834],
                byte_identical=True, PC_delta=DELTA, rows=rows, memory=memory, RMW_order=rmw,
                static_memory_sites=counts,
                calls=[], return_PC=0x2d5c, cold_tail=[0x2d5e, 0x2d60], frame_bytes=16,
                local_stack_offsets=[8,12], own_written_GPRs=sorted(writes),
                original_A0_success_code=False, whole_function_normal_return_guaranteed=False,
                minimal_readable_C=SOURCES, inputs={p:sha((root / p).read_bytes()) for p in [REVIEW,SNAPSHOT]+SOURCES},
                checker_sha256=sha(Path(__file__).read_bytes()), target_execution=False,
                HOST_execution=False, ISA_emulation=False, ESIL_execution=False, MMIO_execution=False,
                network=False, new_BIN=False, installed_resident_identity_proved=False,
                physical_clock_frequency_proved=False)
    if capture:
        answer['static_capture'] = capture
    return answer


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--project-root', type=Path, required=True)
    p.add_argument('--r2-exe', type=Path)
    p.add_argument('--emit-ledger', action='store_true', help='Print JSON; never write files.')
    a = p.parse_args()
    actual = inspect(a.project_root.resolve(), a.r2_exe)
    if a.emit_ledger:
        need(a.r2_exe is not None, 'Initial capture needs independent static r2 readback')
        print(json.dumps(actual, ensure_ascii=False, indent=2))
    else:
        expected = json.loads((HERE / 'ledger.json').read_bytes())
        capture = expected.pop('static_capture')
        if a.r2_exe:
            need(actual.pop('static_capture') == capture, 'Fresh static tool capture equality')
        need(actual == expected, 'Whole source ledger equality')
        print(json.dumps(dict(passed=True, bytes=234, instructions=93, byte_identical=True,
                             fresh_r2_rows=93 if a.r2_exe else 0, calls=0, normal_return_guaranteed=False,
                             target_execution=False, HOST_execution=False, network=False)))


if __name__ == '__main__':
    main()
