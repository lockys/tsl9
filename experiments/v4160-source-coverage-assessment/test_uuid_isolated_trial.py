#!/usr/bin/env python3
"""Negative controls for the create-only UUID trial, without modifying the project."""
import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TRIAL = Path('experiments/v4160-source-coverage-assessment/uuid_isolated_trial.py')
BIN = Path('firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin')
SOURCE = Path('src/native/receive/opaque_allowed_gaps.c')
PARSER = Path('src/native/tx_candidate/postpass/elf32.py')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--tool-dir', type=Path, required=True)
    args = ap.parse_args()
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        for rel in (TRIAL, BIN, SOURCE, PARSER):
            dest = root / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / rel, dest)
        cmd = [sys.executable, '-I', '-B', str(root / TRIAL), '--tool-dir', str(args.tool_dir)]
        def rejected(label, message):
            p = subprocess.run(cmd, capture_output=True, text=True)
            if p.returncode == 0 or message not in p.stderr:
                raise RuntimeError(label + ' was not rejected as expected: ' + p.stderr)
            print('PASS: rejected ' + label)
        firmware = root / BIN
        pristine = firmware.read_bytes()
        damaged = bytearray(pristine)
        damaged[0x1ab44 - 0x8000] ^= 1
        firmware.write_bytes(damaged)
        rejected('mutated original BIN', 'original BIN mismatch')
        firmware.write_bytes(pristine)
        src = root / SOURCE
        original = src.read_text(encoding='utf-8')
        changed = original.replace('0xf1, 0xff, 0x00, 0x00', '0xf0, 0xff, 0x00, 0x00')
        if changed == original:
            raise RuntimeError('source negative control not applied')
        src.write_text(changed, encoding='utf-8')
        rejected('changed opaque source', 'expected exactly one original byte-array definition')
        src.write_text(original + '\n' + original, encoding='utf-8')
        rejected('duplicate original source definition', 'expected exactly one original byte-array definition')


if __name__ == '__main__':
    main()
