#!/usr/bin/env python3
"""Negative tests: byte and fixture mutations never modify the BIN."""
from contextlib import ExitStack
import importlib.util
import os
from pathlib import Path
import py_compile
import sys
import tempfile


def load_source(path, name):
    """Load exactly the source bytes, without reading or writing bytecode."""
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    previous = sys.modules.get(name)
    sys.modules[name] = module
    try:
        exec(compile(path.read_bytes(), str(path), 'exec'), module.__dict__)
    except BaseException:
        if previous is None:
            del sys.modules[name]
        else:
            sys.modules[name] = previous
        raise
    return module


e = load_source(Path(__file__).resolve().with_name('evidence.py'), 'evidence')


def rejects(fn):
    try:
        fn()
    except ValueError:
        return
    raise RuntimeError('expected rejection')


def changed_instruction(pc, bit):
    offset = pc - e.START
    data = bytearray(e.WINDOW)
    data[offset + bit // 8] ^= 1 << (bit % 8)
    rejects(lambda: e.inspect(bytes(data)))
    original = e.decode(e.WINDOW[offset:], pc)
    try:
        result = e.decode(data[offset:], pc)
    except ValueError:
        return
    if result == original:
        raise RuntimeError(f'mutation did not change decoded fields: {pc:#x}, bit {bit}')


def fixture_change(pc, pos, value):
    rows = list(e.ROWS)
    index = next(i for i, row in enumerate(rows) if row[0] == pc)
    row = list(rows[index]); row[pos] = value; rows[index] = tuple(row)
    rejects(lambda: e.inspect(e.WINDOW, rows))


def real_pin_and_window():
    data = e.BIN.read_bytes()
    e.check_pin(data)
    rows = e.inspect(data[e.START-e.BASE:e.END-e.BASE])
    e.need(len(rows) == 36, 'wrong instruction count')


def bad_pin():
    data = bytearray(e.BIN.read_bytes()); data[0] ^= 1
    rejects(lambda: e.check_pin(data))
    rejects(lambda: e.check_pin(bytes(data[:-1])))
    rejects(lambda: e.check_pin(bytes(data) + b'\0'))


def bad_windows():
    rejects(lambda: e.inspect(b''))
    rejects(lambda: e.inspect(e.WINDOW[:-1]))
    rejects(lambda: e.inspect(e.WINDOW + b'\0'))
    rejects(lambda: e.inspect(e.WINDOW, ()))
    rejects(lambda: e.decode(b'\x03', 0xc364))
    rejects(lambda: e.decode(b'\x03\x00', 0xc364))


def branch_offset():
    for pc in (0xc37a, 0xc38a, 0xc39a):
        changed_instruction(pc, 3)
    fixture_change(0xc37a, 4, 0xc380)
    fixture_change(0xc38a, 4, 0xc390)
    fixture_change(0xc39a, 4, 0xc3a2)


def direct_call_target():
    changed_instruction(0xc37e, 21)
    changed_instruction(0xc38e, 21)
    changed_instruction(0xc3ba, 21)
    fixture_change(0xc37e, 3, 0xef78)


def memory_width_and_registers():
    changed_instruction(0xc392, 12)  # lbu funct3
    changed_instruction(0xc392, 7)   # destination
    changed_instruction(0xc392, 15)  # base
    changed_instruction(0xc382, 20)  # displacement
    changed_instruction(0xc392, 20)  # displacement
    changed_instruction(0xc3a0, 12)  # sb funct3
    changed_instruction(0xc3a0, 20)  # source zero
    changed_instruction(0xc3a0, 15)  # base
    changed_instruction(0xc3c2, 12)  # lw width
    fixture_change(0xc3a0, 2, 1)
    fixture_change(0xc392, 4, 22)


def pcrel_and_indirect():
    changed_instruction(0xc39c, 12)
    changed_instruction(0xc3a0, 7)
    changed_instruction(0xc3ce, 20)
    changed_instruction(0xc3d2, 7)
    fixture_change(0xc3d2, 3, 7)
    e.need(e.pcrel(0xc39c, -1161) == 0x2000bf13, 'bad computed target')
    e.need(e.pcrel(0xc39c, -1160) != 0x2000bf13, 'target mutation undetected')


def stale_timestamp_cache():
    # All bytecode creation and ordinary import happen inside this disposable directory.
    with tempfile.TemporaryDirectory() as directory, ExitStack() as cleanup:
        cleanup.callback(setattr, sys, 'pycache_prefix', sys.pycache_prefix)
        sys.pycache_prefix = None
        path = Path(directory) / 'cache_probe.py'
        old, new = b'value = "old"\n', b'value = "new"\n'
        e.need(len(old) == len(new), 'probe sources must have equal size')
        path.write_bytes(old)
        os.utime(path, (1000000000, 1000000000))
        cache = Path(importlib.util.cache_from_source(str(path)))
        py_compile.compile(str(path), cfile=str(cache), doraise=True,
                           invalidation_mode=py_compile.PycInvalidationMode.TIMESTAMP)
        original_cache = cache.read_bytes()
        e.need(original_cache[:4] == importlib.util.MAGIC_NUMBER and
               int.from_bytes(original_cache[4:8], 'little') == 0 and
               int.from_bytes(original_cache[8:12], 'little') == 1000000000 and
               int.from_bytes(original_cache[12:16], 'little') == len(old),
               'probe did not create a timestamp cache for old source')
        path.write_bytes(new)
        os.utime(path, (1000000000, 1000000000))
        e.need(path.read_bytes() == new and int(path.stat().st_mtime) == 1000000000 and
               path.stat().st_size == len(old), 'probe source metadata changed')
        name = '_evidence_cache_probe'
        e.need(name not in sys.modules, 'probe module name already in use')
        try:
            spec = importlib.util.spec_from_file_location(name, path)
            control = importlib.util.module_from_spec(spec)
            sys.modules[name] = control
            spec.loader.exec_module(control)
            e.need(control.value == 'old', 'ordinary loader did not use stale bytecode')
            module = load_source(path, name)
            e.need(module.value == 'new', 'source loader did not use new bytes')
            e.need(sys.modules[name] is module and module.__spec__.origin == str(path) and
                   module.__file__ == str(path), 'source loader did not create a normal module')
            e.need(cache.read_bytes() == original_cache, 'source loader modified the cache')
        finally:
            sys.modules.pop(name, None)


TESTS = (real_pin_and_window, bad_pin, bad_windows, branch_offset, direct_call_target,
         memory_width_and_registers, pcrel_and_indirect, stale_timestamp_cache)


def main():
    expected = ('real_pin_and_window', 'bad_pin', 'bad_windows', 'branch_offset',
                'direct_call_target', 'memory_width_and_registers', 'pcrel_and_indirect',
                'stale_timestamp_cache')
    e.need(tuple(f.__name__ for f in TESTS) == expected, 'empty or incomplete test set')
    called = []
    for test in TESTS:
        test()
        called.append(test.__name__)
        print('PASS', test.__name__)
    e.need(tuple(called) == expected, 'not every test completed')
    print(f'{len(called)} tests passed; no skips')


if __name__ == '__main__':
    main()
