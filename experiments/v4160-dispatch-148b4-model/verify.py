"""Check pinned firmware instructions and execute host C/C++ model smoke tests."""
import argparse
import hashlib
from pathlib import Path
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
IMAGE = ROOT / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
SHA = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
RAW = bytes.fromhex('050693151600a29583d50500636fb50013831600130e010a8606f2962398b6f89376f30f1376f60f4dbf')

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--vcvars', required=True, type=Path)
    args = parser.parse_args()
    data = IMAGE.read_bytes()
    if len(data) != 76800 or hashlib.sha256(data).hexdigest() != SHA:
        raise ValueError('firmware identity mismatch')
    if data[0x1488e-0x8000:0x14892-0x8000] != bytes.fromhex('63632603'):
        raise ValueError('loop-gate instruction bytes mismatch')
    if data[0x148b4-0x8000:0x148de-0x8000] != RAW:
        raise ValueError('instruction bytes mismatch')
    print('PASS: pinned firmware and 42-byte instruction window', flush=True)
    subprocess.run([sys.executable, '-I', '-B', str(HERE / 'predecessor.py')], check=True)
    subprocess.run([sys.executable, '-I', '-B', str(HERE / 'length_bound.py')], check=True)
    subprocess.run([sys.executable, '-I', '-B', str(HERE / 'ingress_bound.py')], check=True)
    subprocess.run([sys.executable, '-I', '-B', str(HERE / 'entry_provenance.py')], check=True)
    subprocess.run([sys.executable, '-I', '-B', str(HERE / 'entry_route.py')], check=True)
    subprocess.run([sys.executable, '-I', '-B', str(HERE / 'connection_gate.py')], check=True)
    subprocess.run([sys.executable, '-I', '-B', str(HERE / 'connection_state.py')], check=True)
    subprocess.run([sys.executable, '-I', '-B', str(HERE / 'command_gate.py')], check=True)
    subprocess.run([sys.executable, '-I', '-B', str(HERE / 'payload_gate.py')], check=True)
    subprocess.run([sys.executable, '-I', '-B', str(HERE / 'state_setter.py')], check=True)
    subprocess.run([sys.executable, '-I', '-B', str(HERE / 'callback_sequence.py')], check=True)
    subprocess.run([sys.executable, '-I', '-B', str(HERE / 'callback_table_scan.py')], check=True)
    subprocess.run([sys.executable, '-I', '-B', str(HERE / 'callback_table_match.py')], check=True)
    subprocess.run([sys.executable, '-I', '-B', str(HERE / 'callback_table_composition.py')], check=True)
    with tempfile.TemporaryDirectory(prefix='tsl9-dispatch-model-') as temp:
        for lang, flags in (('C', '/TC /std:c11'), ('C++', '/TP /std:c++17')):
            exe = Path(temp) / ('test-' + lang.replace('+', 'p') + '.exe')
            batch = Path(temp) / 'build.bat'
            batch.write_text(f'@call "{args.vcvars}" >nul\n@if errorlevel 1 exit /b 1\n'
                             f'@cl /nologo /W4 {flags} "{HERE / "model.c"}" "{HERE / "test.c"}" /Fe:"{exe}"\n'
                             '@exit /b %errorlevel%\n', encoding='utf-8')
            subprocess.run(['cmd.exe', '/d', '/c', str(batch)], cwd=temp, check=True)
            print(lang + ': ', end='', flush=True)
            subprocess.run([str(exe)], check=True)
            ingress = ROOT / 'experiments/tsl9-v4160-gatt-ingress-model/src'
            witness = Path(temp) / ('ingress-' + lang.replace('+', 'p') + '.exe')
            batch.write_text(f'@call "{args.vcvars}" >nul\n@if errorlevel 1 exit /b 1\n'
                             f'@cl /nologo /W4 {flags} /I"{ingress}" "{ingress / "gatt_ingress.c"}" "{HERE / "ingress_witness.c"}" /Fe:"{witness}"\n'
                             '@exit /b %errorlevel%\n', encoding='utf-8')
            subprocess.run(['cmd.exe', '/d', '/c', str(batch)], cwd=temp, check=True)
            print(lang + ' ingress witness: ', end='', flush=True)
            subprocess.run([str(witness)], check=True)
            dll = Path(temp) / ('model-' + lang.replace('+', 'p') + '.dll')
            batch.write_text(f'@call "{args.vcvars}" >nul\n@if errorlevel 1 exit /b 1\n'
                             f'@cl /nologo /W4 /LD {flags} "{HERE / "model.c"}" "{HERE / "bridge.c"}" /Fe:"{dll}"\n'
                             '@exit /b %errorlevel%\n', encoding='utf-8')
            subprocess.run(['cmd.exe', '/d', '/c', str(batch)], cwd=temp, check=True)
            print(lang + ' differential: ', end='', flush=True)
            subprocess.run([sys.executable, '-I', '-B', str(HERE / 'differential.py'), str(dll)], check=True)
            print(lang + ' classifier: ', end='', flush=True)
            subprocess.run([sys.executable, '-I', '-B', str(HERE / 'classification.py'), str(dll)], check=True)
            print(lang + ' composition: ', end='', flush=True)
            subprocess.run([sys.executable, '-I', '-B', str(HERE / 'composition.py'), str(dll)], check=True)
            source = (HERE / 'model.c').read_text(encoding='utf-8')
            mutants = (
                ('signed comparison', 'if (r.a0 < r.a1)', 'if ((r.a0 ^ UINT32_C(0x80000000)) < (r.a1 ^ UINT32_C(0x80000000)))'),
                ('early truncation', 'r.a2 += UINT32_C(1);', 'r.a2 += UINT32_C(1); r.a2 &= UINT32_C(255);'),
                ('new store index', '(r.a3 << 1)', '((r.a3 + UINT32_C(1)) << 1)'),
            )
            for index, (label, old, new) in enumerate(mutants):
                if source.count(old) != 1:
                    raise ValueError('mutation anchor mismatch: ' + label)
                mutant = Path(temp) / 'mutant.c'
                mutant.write_text(source.replace(old, new), encoding='utf-8')
                mdll = Path(temp) / f'mutant-{lang.replace("+", "p")}-{index}.dll'
                batch.write_text(f'@call "{args.vcvars}" >nul\n@if errorlevel 1 exit /b 1\n'
                                 f'@cl /nologo /W4 /LD {flags} /I"{HERE}" "{mutant}" "{HERE / "bridge.c"}" /Fe:"{mdll}"\n'
                                 '@exit /b %errorlevel%\n', encoding='utf-8')
                subprocess.run(['cmd.exe', '/d', '/c', str(batch)], cwd=temp, check=True, capture_output=True)
                check = subprocess.run([sys.executable, '-I', '-B', str(HERE / 'differential.py'), str(mdll)], capture_output=True, text=True)
                if check.returncode == 0 or 'case ' not in check.stderr:
                    raise ValueError('mutation not detected: ' + label)
            print(lang + ': PASS: three semantic mutants detected', flush=True)
            class_mutants = (
                ('first mask', 'r.t1 = r.a1 & r.a6;', 'r.t1 = r.a1 & r.a7;'),
                ('first store offset', 'r.sp + UINT32_C(24)', 'r.sp + UINT32_C(26)'),
                ('second store offset', 'r.sp + UINT32_C(36)', 'r.sp + UINT32_C(38)'),
                ('first counter', 'r.t1 = r.a4 + UINT32_C(1);', 'r.t1 = r.a4 + UINT32_C(2);'),
                ('second counter', 'r.t1 = r.a5 + UINT32_C(1);', 'r.t1 = r.a5 + UINT32_C(2);'),
            )
            for index, (label, old, new) in enumerate(class_mutants):
                if source.count(old) != 1:
                    raise ValueError('classification mutation anchor mismatch: ' + label)
                mutant = Path(temp) / 'class-mutant.c'
                mutant.write_text(source.replace(old, new), encoding='utf-8')
                mdll = Path(temp) / f'class-mutant-{lang.replace("+", "p")}-{index}.dll'
                batch.write_text(f'@call "{args.vcvars}" >nul\n@if errorlevel 1 exit /b 1\n'
                                 f'@cl /nologo /W4 /LD {flags} /I"{HERE}" "{mutant}" "{HERE / "bridge.c"}" /Fe:"{mdll}"\n'
                                 '@exit /b %errorlevel%\n', encoding='utf-8')
                subprocess.run(['cmd.exe', '/d', '/c', str(batch)], cwd=temp, check=True, capture_output=True)
                check = subprocess.run([sys.executable, '-I', '-B', str(HERE / 'classification.py'), str(mdll)], capture_output=True, text=True)
                if check.returncode == 0 or 'case ' not in check.stderr:
                    raise ValueError('classification mutation not detected: ' + label)
            print(lang + ': PASS: five classifier semantic mutants detected', flush=True)
    print('Host tests against manual and limited byte-decoding interpreters; no device execution.')

if __name__ == '__main__':
    main()
