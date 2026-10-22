#!/usr/bin/env python3
"""Static original clock exit operands and caller suffix; never execute code."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import runpy
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
CLOCK = 'analysis/boot2580-clock-2026-10-22'
CLASSIFIER = 'analysis/function-hardware/fifty-seventh-round/independent-provider-witness/audit_gp_elf.py'
CLASSIFIER_IMPORT = 'analysis/function-hardware/fifty-fifth-round/independent-service-events-contract/elf_service_events.py'


def need(value, message):
    if not value:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def sx(value, bits):
    return value - (1 << bits) if value & (1 << (bits - 1)) else value


def fields(blob, pc, size):
    offset = pc - 0x2c78
    return int.from_bytes(blob[offset:offset + size], 'little')


def operand_contract(blob, rows, classifier):
    """Decode only selected fixed forms already defined by retained readers."""
    need(len(blob) == 234 and len(rows) == 93, 'Complete original leaf')
    by = {r['PC']: r for r in rows}
    writers = []
    for row in rows:
        word = fields(blob, row['PC'], row['size'])
        rd, kind, known = classifier['decode16' if row['size'] == 2 else 'decode32'](word)
        need(known, 'Admitted original GPR destination form')
        if rd not in (None, 0):
            writers.append(dict(PC=row['PC'], RD=rd, kind=kind))

    def lui(pc, rd, value):
        word = fields(blob, pc, 4)
        need((word & 127, word >> 7 & 31, word & 0xfffff000) == (0x37, rd, value), 'LUI operand at ' + hex(pc))

    def li(pc, rd, value):
        word = fields(blob, pc, 2)
        need((word & 3, word >> 13, word >> 7 & 31,
              sx((word >> 12 & 1) << 5 | (word >> 2 & 31), 6)) == (1, 2, rd, value), 'C.LI operand at ' + hex(pc))

    def lwsp(pc, rd, offset):
        word = fields(blob, pc, 2)
        imm = (word >> 12 & 1) << 5 | (word >> 4 & 7) << 2 | (word >> 2 & 3) << 6
        need((word & 3, word >> 13, word >> 7 & 31, imm) == (2, 2, rd, offset), 'Fresh C.LWSP operand at ' + hex(pc))

    def branch(pc, funct, rs1, rs2, target):
        word = fields(blob, pc, 4)
        imm = sx((word >> 31) << 12 | (word >> 7 & 1) << 11 | (word >> 25 & 63) << 5 | (word >> 8 & 15) << 1, 13)
        need((word & 127, word >> 12 & 7, word >> 15 & 31, word >> 20 & 31, pc + imm)
             == (0x63, funct, rs1, rs2, target), 'Branch operands at ' + hex(pc))

    lui(0x2c8c, 12, 0x20000)
    lui(0x2cca, 13, 0x40021000)
    lwsp(0x2cf8, 14, 12)
    li(0x2cfa, 15, 1)
    branch(0x2cfc, 1, 14, 15, 0x2d5a)
    lui(0x2d40, 13, 0x40021000)
    li(0x2d50, 14, 8)
    # Final C.LW A5,4(A3) then C.ANDI A5,12, followed by the exit test.
    word = fields(blob, 0x2d52, 2)
    imm = (word >> 10 & 7) << 3 | (word >> 6 & 1) << 2 | (word >> 5 & 1) << 6
    need((word & 3, word >> 13, 8 + (word >> 7 & 7), 8 + (word >> 2 & 7), imm)
         == (0, 2, 13, 15, 4), 'Fresh final C.LW operands')
    word = fields(blob, 0x2d54, 2)
    need((word & 3, word >> 13, word >> 10 & 3, 8 + (word >> 7 & 7),
          sx((word >> 12 & 1) << 5 | (word >> 2 & 31), 6)) == (1, 4, 2, 15, 12), 'Final ANDI mask/operand')
    branch(0x2d56, 1, 15, 14, 0x2d52)
    need(fields(blob, 0x2d5a, 2) == 0x0141 and fields(blob, 0x2d5c, 2) == 0x8082, 'Shared SP restore and RET')
    # Both mutually exclusive selector stores converge on the same fresh load.
    need(fields(blob, 0x2cf4, 2) == 0x4785 and fields(blob, 0x2cf6, 2) == 0xc63e
         and fields(blob, 0x2d5e, 2) == 0xc602 and fields(blob, 0x2d60, 2) == 0xbf61,
         'Selector 1/0 stores and cold return to fresh selector load')
    branch(0x2cf0, 5, 14, 0, 0x2d5e)
    need(fields(blob, 0x2cea, 2) == 0x439c and fields(blob, 0x2cec, 4) == 0x00e79713,
         'Independent fresh postloop control sample and bit17 selection')
    last = lambda cohort: {str(rd): [r['PC'] for r in cohort if r['RD'] == rd][-1] for rd in range(12,16)}
    skip_last = last([r for r in writers if r['PC'] <= 0x2cfc])
    full_last = last(writers)
    need(skip_last == {'12':0x2c8c,'13':0x2cca,'14':0x2cf8,'15':0x2cfa}, 'All skip-path last GPR writes')
    need(full_last == {'12':0x2c8c,'13':0x2d40,'14':0x2d50,'15':0x2d54}, 'All configure-path last GPR writes')
    return dict(all_own_writers=writers, skip_last_writes=skip_last, configure_last_writes=full_last,
                selector_fresh_load_PC=0x2cf8, selector_name='W = full u32 freshly loaded at 0x2CF8',
                fixed_A2=0x20000, fixed_A3=0x40021000,
                skip=dict(condition='W != 1', A4='W', A5=1, branch_PC=0x2cfc),
                configure_normal_RET=dict(condition='W == 1 AND both later polls return normally', A4=8, A5=8,
                                          final_read_PC=0x2d52, final_mask_PC=0x2d54, final_exit_test_PC=0x2d56),
                coherent_private_stack_skip=dict(condition='valid disjoint coherent private stack; no asynchronous/interfering writes; skip path', A4=0, A5=1),
                normal_return_guaranteed=False, return_is_success_code=False)


def suffix(image, base, call_pc, clock_target, mepc):
    words = [int.from_bytes(image[pc-base:pc-base+4], 'little') for pc in range(call_pc, call_pc+20, 4)]
    def jal(word, pc, rd, target):
        imm = sx((word >> 31) << 20 | (word >> 12 & 255) << 12 | (word >> 20 & 1) << 11 | (word >> 21 & 1023) << 1, 21)
        need((word & 127, word >> 7 & 31, pc + imm) == (0x6f, rd, target), 'Actual caller JAL target/link operands')
    jal(words[0], call_pc, 1, clock_target)
    hi, lo, csr = words[1:4]
    need((hi & 127, hi >> 7 & 31) == (0x17,5), 'Post-clock AUIPC uses only T0')
    need((lo & 127, lo >> 12 & 7, lo >> 7 & 31, lo >> 15 & 31) == (0x13,0,5,5), 'Post-clock ADDI reads/writes only T0')
    value = (call_pc + 4 + (hi & 0xfffff000) + sx(lo >> 20,12)) & 0xffffffff
    need(value == mepc, 'Actual post-clock MEPC numeric value')
    need((csr & 127, csr >> 12 & 7, csr >> 7 & 31, csr >> 15 & 31, csr >> 20)
         == (0x73,1,0,5,0x341), 'MEPC CSRRW consumes only T0')
    jal(words[4], call_pc+16, 0, 0x40000)
    return dict(rows=[dict(PC=call_pc+i*4, raw_hex=w.to_bytes(4,'little').hex()) for i,w in enumerate(words)],
                clock_call_PC=call_pc, return_link=call_pc+4, MEPC=mepc, handoff_PC=call_pc+16,
                handoff_target=0x40000, suffix_A2_A5_reads=[], suffix_A2_A5_writes=[],
                A2_A5_forwarded_unchanged=True, A2_A5_dead_at_external_handoff_proved=False,
                downstream_resident_observation_proved=False)


def inspect(root):
    spec = importlib.util.spec_from_file_location('published_clock_source', root/CLOCK/'check.py')
    clock = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(clock)
    source = clock.inspect(root, None)
    recorded = json.loads((root/CLOCK/'ledger.json').read_bytes())
    recorded.pop('static_capture')
    need(source == recorded, 'Whole published actual original source ledger equality')
    classifier = runpy.run_path(str(root/CLASSIFIER))
    boot, app = (root/clock.BOOT).read_bytes(), (root/clock.APP).read_bytes()
    blob = boot[0x1c78:0x1d62]
    contract = operand_contract(blob, source['rows'], classifier)
    negatives = []
    for pc, mask, label in [(0x2c8c,0x1000,'A2_constant'),(0x2cf8,0x20,'fresh_selector_stack_offset'),
                            (0x2cfa,4,'skip_A5_literal'),(0x2cfc,0x1000,'skip_branch_polarity'),
                            (0x2d40,0x80,'configure_A3_destination'),(0x2d54,4,'final_A5_mask')]:
        changed = bytearray(blob)
        size = next(r['size'] for r in source['rows'] if r['PC'] == pc)
        start = pc-0x2c78
        value = int.from_bytes(changed[start:start+size],'little') ^ mask
        changed[start:start+size] = value.to_bytes(size,'little')
        try:
            operand_contract(bytes(changed),source['rows'],classifier)
        except ValueError as error:
            negatives.append(dict(PC=pc,xor_mask=mask,case=label,rejected=True,gate=str(error)))
        else:
            raise ValueError('Accepted original operand negative: '+label)
    inputs = [CLOCK+'/'+name for name in ('check.py','ledger.json','original_fields.py','original-runtime-rows.json')]
    inputs += source['minimal_readable_C'] + [CLASSIFIER,CLASSIFIER_IMPORT]
    return dict(schema='ID2580-ID2966-original-clock-normal-exit-v1',draft=True,
                firmware=source['firmware'], original_body_SHA256=source['code_sha256'],
                BOOT_range=source['range'], Runtime_range=source['runtime_range'], source_rows=93,
                original_body_bytes=234, byte_identical=True, contract=contract,
                callers=dict(BOOT=suffix(boot,0x1000,0x2c4e,0x2c78,0x1a52),
                             Runtime=suffix(app,0x8000,0x18720,0x1874a,0x9008)),
                static_condition_counterexamples=[
                    dict(case='arbitrary fresh selector',premise='live ready word may differ from prior store', W=0xdeadbeef,A4=0xdeadbeef,A5=1),
                    dict(case='first poll ready but fresh postloop status not ready',premise='coherent private stack; fresh MMIO values independent',postloop_bit17=0,selector=0,skip=True),
                    dict(case='first poll counter reaches4096 but fresh postloop status ready',premise='coherent private stack; fresh MMIO values independent',postloop_bit17=1,selector=1,configure_selected=True)],
                counterexamples_are_static_source_inferences=True, operand_negatives=negatives,
                inputs={p:sha((root/p).read_bytes()) for p in inputs}, checker_sha256=sha(Path(__file__).read_bytes()),
                target_execution=False, HOST_execution=False, ISA_emulation=False, MMIO_execution=False, network=False,
                physical_readiness_proved=False, installed_resident_identity_proved=False)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--project-root',required=True,type=Path)
    p.add_argument('--emit-ledger',action='store_true',help='Print draft JSON; never write files.')
    a = p.parse_args()
    result = inspect(a.project_root.resolve())
    if a.emit_ledger:
        print(json.dumps(result,ensure_ascii=False,indent=2))
    else:
        need(result == json.loads((HERE/'ledger.json').read_bytes()), 'Whole source contract replay')
        print(json.dumps(dict(passed=True,source_rows=93,source_bytes=234,normal_RET_cases=2,
                             caller_suffixes=2,actual_operand_negatives=len(result['operand_negatives']),
                             target_execution=False,HOST_execution=False,network=False)))


if __name__ == '__main__':
    main()
