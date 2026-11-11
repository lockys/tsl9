"""Host-only sparse startup-copy and RF composition, not hardware execution.

The copy model is conditional; interrupts and subsequent RAM writes are unknown.
The isolated diagnostic entry bypasses startup, never the helper identity gate.
"""
import hashlib
import runpy
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
window = runpy.run_path(str(ROOT / 'scripts/rf_tx_window_interpreter.py'))
helper = runpy.run_path(str(ROOT / 'experiments/tsl9-copy-instruction-interpreter/interpreter.py'))
startup = runpy.run_path(str(ROOT / 'scripts/v131_sparse_startup_copy.py'))
REFERENCE_MAP_SHA256 = 'd8109168b5bf20c86ca847e85caf173247e2dfc81beb775a68ad5d17ee275d69'


@dataclass(frozen=True)
class InjectedSecondCopyFixture:
    """Hypothetical missing word, never evidence or an output image."""
    word: bytes


def _reference_ok(source):
    try:
        if any(type(a) is not int or not 0 <= a <= 0xffffffff or
               type(v) is not int or not 0 <= v <= 255 for a, v in source.items()):
            return False
        encoded = b''.join(a.to_bytes(4, 'big') + bytes([v]) for a, v in sorted(source.items()))
        return hashlib.sha256(encoded).hexdigest() == REFERENCE_MAP_SHA256
    except (AttributeError, TypeError, ValueError, OverflowError):
        return False


def reload_pointer(s, code):
    """Execute only 64e28's C.LW on the existing synthetic state."""
    try:
        pc = s['pc']
        ins = bytes(code[pc + i] for i in range(2))
        t = window['steps']['step'](
            {'regs': s['regs'], 'memory': s['memory'], 'halted': False}, pc, ins)
        if pc != 0x64e28 or t['halted']:
            raise ValueError('reload')
        s['regs'], s['memory'] = t['regs'], t['memory']
        s['pc'] = pc + 2
        s['status'] = 'reloaded'
    except (KeyError, ValueError, TypeError, OverflowError):
        s['status'] = 'halted'
        s['reason'] = 'invalid reload instruction or memory'
    return s


def run(state, code, source, budget=1000):
    """Require both sparse startup copies before executing any RF instruction."""
    if not _reference_ok(source):
        return {'status': 'halted', 'reason': 'startup reference identity mismatch'}
    return _run_startup(state, code, source, budget)


def run_with_injected_fixture(state, code, source, fixture, budget=1000):
    """Host-only counterfactual; fixture bytes are not ROM or hardware evidence."""
    if not _reference_ok(source) or type(fixture) is not InjectedSecondCopyFixture or type(fixture.word) is not bytes or len(fixture.word) != 4:
        return {'status': 'halted', 'reason': 'invalid injected fixture or reference', 'hypothetical': True}
    injected = dict(source)
    injected.update((0x6eb2c + i, b) for i, b in enumerate(fixture.word))
    result = _run_startup(state, code, injected, budget)
    result['hypothetical'] = True
    return result


def _run_startup(state, code, source, budget):
    memory = {}
    for which in ('first', 'second'):
        result = startup['copy'](source, memory, which)
        memory = result['memory']
        if result['status'] != 'copied':
            return {'status': 'halted', 'reason': 'startup missing-source',
                    'copy': which, 'address': result['address'],
                    'words_copied': result['words_copied'], 'startup_memory': memory}
    return run_isolated_provenance(state, code, memory, budget)


def run_isolated_provenance(state, code, helper_mapping, budget=1000):
    """Diagnostic only: bypass startup completeness, retain helper identity gate."""
    s = window['run'](state, code)
    if s['status'] != 'boundary':
        return s
    try:
        target = s['target']
        body = helper['BODY']
        if target != helper['BASE'] or any(helper_mapping[target + i] != b for i, b in enumerate(body)):
            raise ValueError('unknown target or helper mapping')
        memory = s['memory']
        base = helper['RAM']
        # The helper's existing RAM provider is contiguous; represent holes as
        # explicitly unmapped, and bound allocation for untrusted input.
        if any(type(a) is not int or a < base or a >= base + 0x100000 or
               type(v) is not int or not 0 <= v <= 255 for a, v in memory.items()):
            raise ValueError('unsupported data mapping')
        size = max(memory, default=base - 1) - base + 1
        data = bytearray(size)
        for a, v in memory.items():
            data[a - base] = v
        holes = set(range(base, base + size)) - memory.keys()
        r = s['regs']
        machine = helper['Machine'](data, r[10], r[11], r[12], code=body,
                                    unmapped_reads=holes, unmapped_writes=holes)
        # JALR reads its target before writing rd. The fixed instruction links ra.
        ins = int.from_bytes(window['CODE'][-4:], 'little')
        rd = (ins >> 7) & 31
        link = s['pc'] + 4
        if rd:
            r[rd] = link
        machine.r = list(r)
        machine.return_link = link
        machine.pc = target
        try:
            machine.run(budget)
            s['status'] = 'returned'
        except helper['Halt'] as exc:
            s['status'] = 'halted'
            s['reason'] = str(exc)
        s['regs'] = machine.r
        s['pc'] = machine.pc
        s['memory'] = {a: machine.data[a - base] for a in memory}
        s['effects'] = machine.effects
        s['mmio'] = machine.mmio
        if s['status'] == 'returned':
            reload_pointer(s, code)
    except (KeyError, ValueError, TypeError, OverflowError):
        s['status'] = 'halted'
        s['reason'] = 'unknown target or unsupported mapping'
    return s
