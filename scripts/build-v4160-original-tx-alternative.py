#!/usr/bin/env python3
"""Build an isolated offline alternative; NOT-FLASH-VALIDATED, never flash."""
import argparse
import hashlib
import json
from pathlib import Path
import runpy
import subprocess
import sys

ROOT = Path(__file__).resolve().parent.parent
BASE, START, END, SIZE = 0x8000, 0x8a56, 0x8b6e, 76800
REF_SHA = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'


def check(image, reference):
    if len(reference) != SIZE or hashlib.sha256(reference).hexdigest() != REF_SHA:
        raise ValueError('reference size or SHA-256 mismatch')
    if len(image) != SIZE or image != reference:
        raise ValueError('full image mismatch')


def run(*args):
    try:
        return subprocess.run([str(x) for x in args], check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as exc:
        raise ValueError(f'Command failed: {args[0]}\n{exc.stderr}') from exc


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tool-dir', type=Path, required=True)
    parser.add_argument('--reference', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    out = args.out.resolve()
    if out.exists() or out == ROOT or ROOT in out.parents:
        raise ValueError('output must be a new directory outside the project')
    reference = args.reference.read_bytes()
    check(reference, reference)
    def tool(name):
        p = args.tool_dir / name
        return p.with_suffix('.exe') if p.with_suffix('.exe').is_file() else p
    experiment = ROOT / 'experiments/tsl9-tx-whole-inline'
    # Includes branch decoding and four independent source mutations in each language.
    proof = run(sys.executable, experiment / 'verify.py', '--tool-dir', args.tool_dir,
                '--reference', args.reference).stdout
    out.mkdir(parents=True)
    run(sys.executable, ROOT / 'scripts/build-v4160-source-candidate.py',
        '--tool-dir', args.tool_dir, '--out', out / 'baseline')
    script = out / 'tx.ld'
    script.write_text('OUTPUT_ARCH(riscv)\nSECTIONS { .text 0x8a56 : { *(.text.tx) } }\n')
    branch = runpy.run_path(str(ROOT / 'scripts/verify-tx-branch-images.py'))
    results = []
    for mode, lang, standard in [('c', 'c', 'c11'), ('cpp', 'c++', 'c++17')]:
        obj, elf, raw = (out / ('tx-' + mode + ext) for ext in ('.o', '.elf', '.bin'))
        run(tool('clang'), '--target=riscv32-unknown-elf', '-march=rv32imac_zicsr',
            '-mabi=ilp32', '-mno-relax', '-ffreestanding', '-x', lang, '-std=' + standard,
            '-c', experiment / 'tx.c', '-o', obj)
        if 'There are no relocations in this file.' not in run(tool('llvm-readelf'), '-r', obj).stdout:
            raise ValueError('unexpected TX relocation')
        run(tool('ld.lld'), '--no-relax', '-T', script, obj, '-o', elf)
        run(tool('llvm-objcopy'), '-O', 'binary', '--only-section=.text', elf, raw)
        tx = raw.read_bytes()
        if len(tx) != END - START:
            raise ValueError('TX section length')
        baseline = (out / 'baseline' / ('NOT-FLASH-VALIDATED-v4160-source-' + mode + '.bin')).read_bytes()
        image = baseline[:START-BASE] + tx + baseline[END-BASE:]
        check(image, reference)
        branch['check_branches'](image[0x8b10-BASE:0x8b14-BASE], baseline[0x8b10-BASE:0x8b14-BASE])
        # Exercise the actual full-image guard inside and outside the TX replacement.
        for offset in (START-BASE, 0, SIZE-1):
            altered = bytearray(image)
            altered[offset] ^= 1
            try:
                check(altered, reference)
            except ValueError:
                pass
            else:
                raise ValueError('mutation accepted')
        dest = out / ('NOT-FLASH-VALIDATED-original-tx-' + mode + '.bin')
        with dest.open('xb') as f:
            f.write(image)
        check(dest.read_bytes(), reference)
        results.append({'mode': mode, 'file': str(dest), 'bytes': len(image),
                        'sha256': hashlib.sha256(image).hexdigest()})
    print(json.dumps({'passed': True, 'outputs': results, 'tx_experiment': proof,
                      'full_image_mutations_rejected_per_mode': 3,
                      'full_source': False, 'opaque_original_inputs_required': True,
                      'installed_rom_proved': False, 'hardware_validated': False,
                      'flashable_proved': False}, indent=2))


if __name__ == '__main__':
    main()
