#!/usr/bin/env python3
"""Exercise the complete pinned probe source in fresh Python processes, offline."""
import hashlib, json, os, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROBE = HERE / 'probe.py'
DIGEST = 'c5c8c18a296d858cb1fc7891fa0c6171ba563b1d7ca1b4599bfec86cb99342f9'
INPUTS = [
    'experiments/tsl9-v4160-startup/src/startup.c',
    'experiments/tsl9-v4160-startup/src/startup.h',
    'experiments/tsl9-v4160-startup/layout/component.ld',
    'experiments/v4160-bd5a-symbolic-c/candidate.c',
    'experiments/v4160-bd64-symbolic-c/candidate.c',
    'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin',
]
EXPECTED = {
    'wrong_base':'final RAM', 'wrong_offset':'final symbol record_flag_bf13',
    'missing':'__tsl9v4160_ram', 'duplicate':'duplicate symbol', 'extra':'final alloc',
    **{k:'final phdr: expected one PT_NULL' for k in ('pt_load','pt_interp','pt_dynamic','phdr_none','phdr_extra')},
    'ram_type':'final RAM', 'alias_abs':'final symbol record_flag_bf13',
    'leaf_byte':'final bytes bd5a', 'carrier_size':'carrier section',
    'symstr_type':'symbol string table type', 'shstr_type':'section name string table type',
    'duplicate_global':'final globals',
}
for artifact in ('full','gc','final'):
    for case in ('relr','unknown_type'):
        EXPECTED[artifact+'_'+case] = 'unsupported section type'
    for case in ('name','value','size','info','other','shndx'):
        EXPECTED[artifact+'_sym_zero_'+case] = 'symbol zero entry'
    for case in ('shinfo_zero','shinfo_large','shinfo_early','shinfo_late','local_binding','global_binding'):
        EXPECTED[artifact+'_'+case] = 'symbol local boundary'
for case in ('name','value','size','global_slot_binding','other','shndx_undef','shndx_abs'):
    EXPECTED['gc_section_'+case] = 'SECTION symbol metadata'
EXPECTED['gc_section_binding'] = 'symbol local boundary'
EXPECTED['gc_section_shndx_oob'] = 'symbol index'

def check(ok, msg):
    if not ok: raise RuntimeError(msg)

def execute(flags, mode='positive', input_name='', args=()):
    # Verify and execute the entire source, not a reconstructed function fragment.
    runner = '''
import hashlib
from pathlib import Path
p = Path(%r)
source = p.read_bytes()
if hashlib.sha256(source).hexdigest() != %r: raise RuntimeError('probe digest')
mode, target = %r, Path(%r)
original = Path.read_bytes
def read_bytes(self):
    if mode != 'positive' and self.resolve() == target:
        if mode == 'missing': raise FileNotFoundError('simulated missing input: ' + str(self))
        b = original(self)
        return b + b'\\0'
    return original(self)
Path.read_bytes = read_bytes
exec(compile(source, str(p), 'exec'), {'__name__': '__main__', '__file__': str(p)})
''' % (str(PROBE), DIGEST, mode, str((HERE.parents[1] / input_name).resolve()))
    env = {k:v for k,v in os.environ.items() if not k.upper().startswith('PYTHON')}
    return subprocess.run([sys.executable, *flags, '-c', runner, *args],
                          stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE, timeout=120, env=env)

def failure(p, text):
    check(p.returncode != 0 and not p.stdout and text in p.stderr.decode('utf8', 'replace'),
          'expected failure: ' + text + ' / ' + repr((p.returncode,p.stdout,p.stderr)))

def main():
    check(hashlib.sha256(PROBE.read_bytes()).hexdigest() == DIGEST, 'probe digest')
    for flags, optimize in [(['-I','-B'], 0), (['-I','-B','-O'], 1)]:
        p = execute(flags)
        check(p.returncode == 0 and not p.stderr, 'positive: ' + repr(p.stderr))
        result = json.loads(p.stdout)
        check(result['status'] == 'PASS' and result['python_optimize'] == optimize, 'positive status')
        cases = result['cases']
        check(len(cases) == 2 and {c['language'] for c in cases} == {'c11','c++17'}, 'languages')
        for case in cases:
            check(case['negative_reasons'] == EXPECTED, 'negative IDs/reasons')
            check(case['leaf_bytes'] == {'bd5a':'97070020a38ca71a8280','bd64':'170500200345f51a8280'}, 'leaf bytes')
        for name in INPUTS:
            failure(execute(flags, 'missing', name), 'simulated missing input:')
            failure(execute(flags, 'changed', name), 'pin:')
    for flags, args in [(['-I','-B','-OO'], ()), (['-I','-B'], ('extra',)),
                        (['-B'], ()), (['-I'], ())]:
        failure(execute(flags, args=args), 'use python -I -B with optional -O, no arguments')
    print('PASS: full source digest, both optimization modes, 68 negative IDs/reasons per language, '
          'all six inputs missing/changed, invalid CLI')

if __name__ == '__main__':
    main()
