"""Compile and execute only the host C slice, comparing it with bounded RV32 interpretation."""
import argparse
import ctypes
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

from oracle import BASE, Slice, need

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SIZE = 140000


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def corpus():
    for base_index in (100, 4096):
        for bank in (0, 1):
            d = base_index + 1062 * bank + 6
            for n in (0, 1, 2, 3, 4, 15, 31):
                for delta in (-8, -1, 0, 1, 2, 3, 4, 5, 6, 8, 16):
                    for cmd in (0, 255, 0x1234, 0xffffffff):
                        yield (base_index, d + delta, bank, n, cmd, 0xdeadbeef)
    for bank in (0, 1):
        for n in (255, 256, 1039, 1040, 1050, 1051, 1052, 65535):
            yield (100, 70000, bank, n, 0xfffffffe, 0x12345678)


def build(tools, folder, model, mode, optimization, name):
    unit = folder / (name + '.c')
    unit.write_text(model + '\n' + (HERE / 'wrapper.c').read_text('utf-8').replace('#include "model.c"', ''), encoding='utf-8')
    obj, dll = folder / (name + '.obj'), folder / (name + '.dll')
    args = [tools['clang'], '--target=x86_64-pc-windows-msvc', '-ffreestanding', '-fno-builtin',
            '-fno-stack-protector', optimization, '-Wall', '-Wextra', '-Werror',
            '-x', 'c' if mode == 'c' else 'c++', '-std=c11' if mode == 'c' else '-std=c++17',
            '-c', unit, '-o', obj]
    if mode == 'cpp':
        args += ['-fno-exceptions', '-fno-rtti']
    for command in (args, [tools['ld.lld'], '-flavor', 'link', '/dll', '/noentry', '/nodefaultlib',
                           '/out:' + str(dll), obj]):
        result = subprocess.run([str(x) for x in command], capture_output=True, text=True, timeout=30)
        need(result.returncode == 0, 'host compiler/linker failed: ' + result.stderr[:600])
    return dll


def exercise(dll, oracle, patterns, cases, expect_failure=False):
    import _ctypes
    lib = ctypes.CDLL(str(dll))
    fn = lib.tx_run
    fn.argtypes = [ctypes.POINTER(ctypes.c_ubyte)] + [ctypes.c_uint32] * 7 + [ctypes.POINTER(ctypes.c_uint32)]
    fn.restype = None
    checked = 0
    try:
        for i, (base, source, bank, n, cmd, a6) in enumerate(cases):
            origin = BASE - base
            initial = patterns[i % len(patterns)]
            expected, registers, events = oracle.run(initial, origin, base, source, bank, n, cmd, a6)
            memory = (ctypes.c_ubyte * SIZE).from_buffer_copy(initial)
            out = (ctypes.c_uint32 * 10)()
            fn(memory, origin, base, source, bank, n, cmd, a6, out)
            equal = bytes(memory) == expected and tuple(out) == registers
            if expect_failure and not equal:
                return {'rejected_at_case': i, 'length': n, 'bank': bank}
            need(equal, 'compiled C/original instruction differential mismatch at case ' + str(i))
            d = base + 1062 * bank + 6
            need(events == {'writes': n + 4, 'reads': n, 'write_start_index': d, 'write_end_index': d + 5 + n},
                 'original bounded memory operation counts and write extent')
            checked += 1
        need(not expect_failure, 'compiled semantic mutation accepted by all witnesses')
        return {'cases': checked}
    finally:
        del fn
        _ctypes.FreeLibrary(lib._handle)


def worker(tool_dir):
    need(os.name == 'nt' and ctypes.sizeof(ctypes.c_void_p) == 8, 'Windows x64 host worker required')
    tools = {n: tool_dir / (n + '.exe') for n in ('clang', 'ld.lld')}
    expected_tools = {'clang': '047dfde05acc6fcce5af669e25cd8d40b4f509b8842d151d6d8a43a1c6a35fd6',
                      'ld.lld': 'fe7f55c0c78b3d87f33b905a3874e10e872ca7beef53a8199d7ff9ac6641ec3f'}
    for name, expected in expected_tools.items():
        need(sha(tools[name]) == expected, 'pinned tool: ' + name)
    inputs = {p.name: sha(p) for p in (HERE / 'model.c', HERE / 'wrapper.c', HERE / 'oracle.py', HERE / 'verify.py')}
    image = (ROOT / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin').read_bytes()
    need(len(image) == 76800 and hashlib.sha256(image).hexdigest() == '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667', 'original image identity')
    oracle = Slice(image)
    patterns = [bytes((i * 37 + seed * 19) & 255 for i in range(SIZE)) for seed in range(8)]
    cases = list(corpus())
    model = (HERE / 'model.c').read_text('utf-8')
    profiles = {}
    with tempfile.TemporaryDirectory(prefix='tsl9-semantic-host-') as directory:
        folder = Path(directory)
        for mode in ('c', 'cpp'):
            for optimization in ('-O0', '-O2'):
                name = mode + optimization.replace('-', '_')
                dll = build(tools, folder, model, mode, optimization, name)
                profiles[name] = exercise(dll, oracle, patterns, cases)
        mutants = {'payload_source_offset': model.replace('ram[(uintmax_t)source_index + i]', 'ram[(uintmax_t)source_index + i + 1u]'),
                   'checksum_mask': model.replace('sum &= 255u;', 'sum &= 127u;', 1),
                   'length_header_offset': model.replace('ram[(uintmax_t)d_index + 4u]', 'ram[(uintmax_t)d_index + 3u]'),
                   'zero_length_a6': model.replace('uint32_t a6 = entry_a6;', 'uint32_t a6 = entry_a6 ^ 1u;')}
        mutations = {}
        for name, text in mutants.items():
            dll = build(tools, folder, text, 'c', '-O2', name)
            mutations[name] = exercise(dll, oracle, patterns, cases, expect_failure=True)
    for name, expected in inputs.items():
        need(sha(HERE / name) == expected, 'inputs unchanged after host execution')
    return {'passed': True, 'cases_per_profile': len(cases), 'profiles': profiles,
            'compiled_mutations_rejected': mutations, 'compared': ['entire_RAM_array', 'a0..a6', 's0', 's1', 's3'],
            'actual_C_executed_on_host': True, 'original_instructions_interpreted': True,
            'original_slice_write_range_relative_to_bank': '[6,11+length)',
            'slice_within_1062_byte_bank_iff_length_at_most': 1051,
            'entry_length_1039_remaining_bank_bytes_for_this_slice': 12,
            'providers_executed': False, 'device_executed': False, 'global_RAM_ownership_proved': False,
            'bus_width_or_atomicity_equivalence_proved': False, 'inputs_sha256': inputs, 'tools_sha256': expected_tools}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--tool-dir', type=Path, required=True)
    parser.add_argument('--worker', action='store_true')
    args = parser.parse_args()
    if args.worker:
        print(json.dumps(worker(args.tool_dir)))
    else:
        command = [sys.executable] + (['-O'] if sys.flags.optimize else []) + ['-B', str(Path(__file__).resolve()), '--worker', '--tool-dir', str(args.tool_dir.resolve())]
        result = subprocess.run(command, capture_output=True, text=True, timeout=120)
        need(result.returncode == 0, 'bounded host worker failed: ' + result.stderr[-1500:])
        print(result.stdout.strip())
