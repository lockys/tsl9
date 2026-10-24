#!/usr/bin/env python3
"""One fixed genuine compiler recipe; inspect actual object/IR, never execute it."""
import hashlib
import json
import os
from pathlib import Path
import re
import runpy
import subprocess
import sys
sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
MODEL = Path(__file__).resolve().parent
TOOLS = Path(os.environ.get('TSL9_LLVM_BIN', str(Path.home() / 'AppData/Local/Android/Sdk/ndk/27.1.12297006/toolchains/llvm/prebuilt/windows-x86_64/bin')))
PRIOR = ROOT / 'analysis/v4160-resident-native-2026-10-22/implementation/probe.py'
NV = ROOT / 'analysis/v4160-nv-write-2026-10-22/implementation/probe.py'
PUBLIC = 'tsl9_nv_write_frame_197be'
CALLEES = ['tsl9_flash_unlock_18e98', 'tsl9_flash_erase_18ec4', 'tsl9_flash_program_18ef2', 'tsl9_flash_lock_18eb6', 'tsl9_delay_19764']
H = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()

def need(condition, message):
    if not condition:
        raise ValueError(message)

def inspect(folder):
    old = runpy.run_path(str(PRIOR))
    E = runpy.run_path(str(old['parser'](ROOT)))['ELF']
    e = E(folder / 'native.o')
    nv = runpy.run_path(str(NV))
    classifier = runpy.run_path(str(nv['locate'](ROOT, nv['CLASSIFIER'])))
    functions = [f for f in e.symbols if f['info'] & 15 == 2 and f['size']]
    need(len(functions) == 1 and functions[0]['name'] == PUBLIC, 'Only genuine new wrapper definition')
    function = functions[0]
    code = e.function_bytes(function)
    rows = []
    for line in (folder / 'static-disassembly.log').read_text().splitlines():
        m = re.match(r'^\s*([0-9a-f]+):\s+((?:[0-9a-f]{2}\s+)+)\s*([^\s]+)\s*(.*)', line)
        if not m:
            continue
        offset = int(m[1], 16)
        raw = bytes.fromhex(m[2])
        need(offset == sum(len(bytes.fromhex(r['raw'])) for r in rows), 'Complete contiguous LLVM coverage')
        need(raw == code[offset:offset + len(raw)] and len(raw) in (2, 4), 'Actual raw code identity')
        rd, kind, known = classifier['decode16' if len(raw) == 2 else 'decode32'](int.from_bytes(raw, 'little'))
        need(known and m[3] != '<unknown>', 'Known finite instruction destination classification')
        rows.append(dict(offset=offset, raw=raw.hex(), mnemonic=m[3], operands=m[4], rd=rd, kind=kind))
    need(sum(len(bytes.fromhex(r['raw'])) for r in rows) == len(code), 'No omitted actual instructions')
    ir = (folder / 'native.ll').read_text()
    calls = re.findall(r'call[^@\n]*@([A-Za-z0-9_]+)\(', ir)
    actual_calls = [n for n in calls if n in CALLEES]
    need(actual_calls == CALLEES, 'Five genuine C calls in original order')
    volatile_store = re.findall(r'store volatile i32 ([^\n]+)', ir)
    volatile_load = re.findall(r'load volatile i32, ([^\n]+)', ir)
    need(len(volatile_store) == len(volatile_load) == 1, 'One genuine volatile source save/reload')
    erase = ir.index('@tsl9_flash_erase_18ec4(')
    reload = ir.index('load volatile i32, ')
    program = ir.index('@tsl9_flash_program_18ef2(')
    need(erase < reload < program, 'Fresh source-slot read after erase and before program')
    undefined = sorted({s['name'] for s in e.symbols if s['index'] == 0 and s['name']})
    need(undefined == sorted(CALLEES), 'Only genuine externally defined providers remain unresolved')
    need(len(e.relocations) == 5 and all(r['type'] == 19 for r in e.relocations), 'Five genuine CALL_PLT relocations')
    abs_symbols = [s['name'] for s in e.symbols if s['index'] == 0xfff1 and s['info'] >> 4]
    need(not abs_symbols and e.kind == 1 and e.flags == 1, 'Actual RV32/RVC ET_REL, no ABS provider')
    allocated = [s for s in e.sections if s['flags'] & 2 and s['size']]
    need(len(allocated) == 1 and allocated[0]['flags'] == 6 and allocated[0]['size'] == len(code), 'All allocated real code inventoried')
    return dict(passed=True, bytes=len(code), instructions=len(rows), global_functions=[PUBLIC],
                own_written_GPRs=sorted({r['rd'] for r in rows if r['rd'] not in (None, 0)}),
                stack_adjustments=[r for r in rows if r['mnemonic'] == 'addi' and r['operands'].startswith('sp, sp,')],
                stack_accesses=[r for r in rows if '(sp)' in r['operands']], rows=rows,
                code_sha256=hashlib.sha256(code).hexdigest(), UND=undefined, RELA=e.relocations,
                global_ABS=abs_symbols, C_calls=actual_calls, volatile_source_stores=volatile_store,
                volatile_source_loads=volatile_load, source_reloaded_after_erase=True,
                full_original_ABI_proved=False, original_stack_slot_proved=False,
                installed_provider_proved=False, target_execution=False, HOST_tests_run=False,
                linked=False, BIN_generated=False, hardware_tested=False)

def main():
    old = runpy.run_path(str(PRIOR))
    paths = {name: TOOLS / (name + '.exe') for name in old['TOOLS']}
    need(all(H(p) == old['TOOLS'][name] for name, p in paths.items()), 'Pinned existing LLVM')
    source = MODEL / 'src/write_frame.c'
    parser = old['parser'](ROOT)
    nv = runpy.run_path(str(NV))
    inputs = [Path(__file__), source, PRIOR, NV, parser,
              nv['locate'](ROOT, nv['CLASSIFIER']), nv['locate'](ROOT, nv['CLASSIFIER_IMPORT']),
              ROOT / 'experiments/tsl9-nv-write-callback/src/nv_write_callback.h',
              ROOT / 'experiments/tsl9-v4160-flash-entry-order/src/flash_native.h']
    pins = {str(p): H(p) for p in inputs}
    base = MODEL / 'build/native-v1'
    need(not base.exists(), 'Single create-only profile; do not repeat compilation')
    base.mkdir(parents=True)
    output = []
    for mode in ('c', 'cpp'):
        folder = base / mode
        folder.mkdir()
        tmp = folder / 'compiler-temp'
        tmp.mkdir()
        env = dict(os.environ, TMP=str(tmp), TEMP=str(tmp))
        flags = old['flags'](mode)
        commands = [('resource', [paths['clang'], '-print-resource-dir']),
                    ('native-object', [paths['clang'], *flags, '-c', '-MD', '-MF', folder / 'native.d', '-MT', 'native.o', source, '-o', folder / 'native.o']),
                    ('native-IR', [paths['clang'], *flags, '-S', '-emit-llvm', source, '-o', folder / 'native.ll']),
                    ('static-disassembly', [paths['llvm-objdump'], '--mattr=+m,+a,+c,+zicsr,+zifencei', '-d', '-r', folder / 'native.o'])]
        history = []
        for label, argv in commands:
            actual = subprocess.run([str(a) for a in argv], cwd=folder, env=env, capture_output=True, timeout=120)
            log = folder / (label + '.log')
            log.write_bytes(actual.stdout + actual.stderr)
            history.append(dict(label=label, argv=[str(a) for a in argv], exit=actual.returncode, log=log.name, sha256=H(log)))
            need(actual.returncode == 0, 'Actual compiler/static tool failure; retain this output: ' + str(log))
        resource = Path((folder / 'resource.log').read_text().strip()) / 'include/stdint.h'
        need(H(resource) == old['RESOURCE'], 'Pinned actual compiler resource')
        md = (folder / 'native.d').read_text().replace('\\\n', ' ')
        lhs, _, rhs = md.partition(':')
        deps = {Path(re.sub(r'\\(.)', r'\1', p)).resolve() for p in re.findall(r'(?:\\.|[^\s])+', rhs)}
        expected = {source, ROOT / 'experiments/tsl9-nv-write-callback/src/nv_write_callback.h', ROOT / 'experiments/tsl9-v4160-flash-entry-order/src/flash_native.h', resource}
        need(lhs == 'native.o' and deps == expected, 'Complete four-file actual MD closure')
        facts = inspect(folder)
        record = dict(schema='TSL9-NV-write-volatile-frame-v1', mode=mode, tools={n:dict(path=str(p),sha256=H(p)) for n,p in paths.items()},
                      source_pins=pins, resource=dict(path=str(resource),sha256=H(resource)),
                      MD_inputs=[dict(path=str(p),sha256=H(p)) for p in sorted(deps)], commands=history, result=facts)
        record['artifacts'] = {p.name:dict(bytes=p.stat().st_size,sha256=H(p)) for p in folder.iterdir() if p.is_file()}
        receipt = folder / 'verification.json'
        receipt.write_bytes((json.dumps(record, indent=2) + '\n').encode())
        need(inspect(folder) == facts and all(H(Path(p)) == h for p,h in pins.items()), 'Actual read-only native readback and source stability')
        output.append(dict(mode=mode,receipt=str(receipt),sha256=H(receipt),**{k:facts[k] for k in ('bytes','instructions','own_written_GPRs','stack_adjustments','stack_accesses')}))
    print(json.dumps(dict(passed=True,results=output,target_execution=False),indent=2))

if __name__ == '__main__':
    main()
