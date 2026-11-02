#!/usr/bin/env python3
"""Rebuild the integrated V4.1.60 candidate with opaque original spans."""
import argparse
import hashlib
import json
from pathlib import Path
import runpy
import subprocess
import sys

ROOT = Path(__file__).resolve().parent.parent
EXPECTED = '28697eab551bd9b3ca74a69c44db24fc02e07bedbb5bf02380e4bcb1a390ce89'
parser = argparse.ArgumentParser()
parser.add_argument('--tool-dir', type=Path, required=True)
parser.add_argument('--out', type=Path, required=True)
args = parser.parse_args()
out = args.out.resolve()
if out.exists() or out == ROOT or ROOT in out.parents:
    raise SystemExit('Output must be a new directory outside the project')
clang = args.tool_dir / ('clang.exe' if (args.tool_dir / 'clang.exe').is_file() else 'clang')
if not clang.is_file():
    raise SystemExit('LLVM clang missing')
payload = json.loads((ROOT / 'src/native/tx_candidate/full-image-payload.json').read_text(encoding='utf-8'))
if payload['schema'] != 'tsl9-v4160-opaque-payload-v1':
    raise ValueError('Unexpected payload schema')
ranges = payload['ranges']
if [(x['start'], x['end']) for x in ranges] != [(0x14056, 0x14c8a), (0x1a69c, 0x1a6a0)]:
    raise ValueError('Unexpected payload ranges')
raw = [bytes.fromhex(x['hex']) for x in ranges]
if any(len(data) != item['end'] - item['start'] or hashlib.sha256(data).hexdigest() != item['sha256']
       for item, data in zip(ranges, raw)):
    raise ValueError('Payload length or digest mismatch')
out.mkdir(parents=True)
spans_dir = out / 'selected'
p = subprocess.run([sys.executable, '-B', str(ROOT / 'scripts/build-source-spans.py'),
                    '--tool-dir', str(args.tool_dir), '--out', str(spans_dir)],
                   capture_output=True, text=True)
if p.returncode:
    raise ValueError('Selected source build failed: ' + p.stderr[:1000])
facts = json.loads(p.stdout)
if not facts['passed'] or facts['complete_firmware'] or facts['flashable']:
    raise ValueError('Unexpected selected source result')
manifest = json.loads((spans_dir / 'NOT-FLASHABLE-spans.json').read_text(encoding='utf-8'))
reader = runpy.run_path(str(ROOT / 'src/native/tx_candidate/postpass/elf32.py'))['ELF']
fragment_tools = runpy.run_path(str(ROOT / 'scripts/source-ota-epilogue.py'))
compile_epilogue, compile_entry = fragment_tools['compile_fragment'], fragment_tools['compile_entry']
results = []
for mode in ('c', 'cpp'):
    epilogue = compile_epilogue(args.tool_dir, out, mode, reader)
    entry = compile_entry(args.tool_dir, out, mode, reader)
    if entry != raw[0][:0x38]:
        raise ValueError('Compiled entry differs from original bytes')
    if epilogue != raw[0][0x42:0x50]:
        raise ValueError('Compiled epilogue differs from original bytes')
    selected = [entry + raw[0][0x38:0x42] + epilogue + raw[0][0x50:], raw[1]]
    source = '#ifdef __cplusplus\nextern "C" {\n#endif\n'
    for i, data in enumerate(selected):
        source += '__attribute__((used,section(".tsl9_payload_' + str(i) + '"))) extern const unsigned char payload_' + str(i) + '[] = {'
        source += ','.join(str(x) for x in data) + '};\n'
    source += '#ifdef __cplusplus\n}\n#endif\n'
    src = out / ('opaque-payload-' + mode + '.c')
    src.write_text(source, encoding='ascii')
    obj = out / ('opaque-' + mode + '.o')
    command = [str(clang), '--target=riscv32-unknown-elf', '-march=rv32imac', '-mabi=ilp32',
               '-ffreestanding', '-fno-common', '-x', 'c' if mode == 'c' else 'c++',
               '-c', str(src), '-o', str(obj)]
    p = subprocess.run(command, capture_output=True, text=True)
    if p.returncode:
        raise ValueError('Opaque source compilation failed: ' + p.stderr[:1000])
    elf = reader(obj)
    compiled = [elf.data(elf.byname['.tsl9_payload_' + str(i)]) for i in range(2)]
    if compiled != raw:
        raise ValueError('Compiled opaque bytes differ')
    item = next(x for x in manifest['outputs'] if x['mode'] == mode)
    data = (spans_dir / item['file']).read_bytes()
    spans = item['spans']
    if [(x['start'], x['end']) for x in spans] != [(0x8000, 0x14056), (0x14c8a, 0x1a69c), (0x1a6a0, 0x1ac00)]:
        raise ValueError('Unexpected source spans')
    image = bytearray()
    for i, span in enumerate(spans):
        part = data[span['file_offset']:span['file_offset'] + span['length']]
        if len(part) != span['end'] - span['start']:
            raise ValueError('Short source span')
        image.extend(part)
        if i < len(compiled):
            image.extend(compiled[i])
    digest = hashlib.sha256(image).hexdigest()
    if len(image) != 76800 or digest != EXPECTED:
        raise ValueError('Reconstructed candidate digest mismatch')
    dest = out / ('NOT-FLASH-VALIDATED-v4160-source-' + mode + '.bin')
    with dest.open('xb') as stream:
        stream.write(image)
    if dest.read_bytes() != image:
        raise ValueError('Output readback mismatch')
    results.append({'mode': mode, 'bytes': len(image), 'sha256': digest, 'file': dest.name})
print(json.dumps({'passed': True, 'outputs': results, 'opaque_original_bytes': 3128,
                  'compiled_epilogue_bytes_replacing_carrier': 14,
                  'compiled_entry_bytes_replacing_carrier': 56,
                  'historical_candidate_read_during_build': False,
                  'semantics_recovered': False, 'hardware_validated': False, 'flashable_proved': False}))
