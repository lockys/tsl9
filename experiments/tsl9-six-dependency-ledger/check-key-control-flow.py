"""Independently disassemble bounded windows, never execute target instructions."""
import argparse
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
IMAGE = ROOT / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
WINDOWS = {
    (0xae0e, 0x14e): 'f0178263a7827e6c63da36003011c01b1fd0141671f3abb1a0b7dfa9e587e6db',
    (0xcedc, 0xbc): 'e6dd2498940c6d477836f3411ad6e381fc9a485d0eb5d54f300f1c7809e9f27f',
    (0x12020, 0x90): '6f772d4580c8abb0313d8c1f038752bddb580148966c022a64d45ff101b796ea',
    (0xa0d4, 0x132): '1f19de347e3d329ee56aea9f42477d344355554b493d4c435a6aec8058a535c0',
    (0xa2ee, 0x8e): '1e3ba5cad99891ddf478123a9015736168e7bdad51c01abbed0cda7e4d043480',
    (0x172b6, 0x4a): '9567e295d85dee36d242e89c952adf091b12ab5e67486dea7d8c0b0597473ea7',
}
EXPECTED = {
    0xae54: 'bne a4, a5, 0xaf4c', 0xae5e: 'bne a4, a5, 0xaf4c',
    0xaf08: 'j 0xaf4c', 0xaf48: 'bnez s2, 0xaee0',
    0xcee4: 'beqz a5, 0xcf94', 0xcef6: 'bne a4, a3, 0xcf66',
    0xcf1c: 'beqz a3, 0xcf8a', 0xcf78: 'beqz a4, 0xcefa',
    0x12060: 'beqz a0, 0x1209c', 0x12076: 'bleu a5, a3, 0x1240c',
    0x120a4: 'bne s4, s7, 0x12046',
    0xa0ea: 'beq a5, a0, 0xa1f6', 0xa12e: 'bltu a4, a5, 0xa1e8',
    0xa13c: 'beq a0, a4, 0xa168', 0xa142: 'beq a0, a5, 0xa1fc',
    0xa2fe: 'bne a0, a5, 0xa364', 0xa314: 'beqz s1, 0xa372',
    0xa32e: 'beq a5, a4, 0xa372', 0x172de: 'bne a5, a4, 0x172fa',
    0x172fc: 'jal ra, 0xa2ee',
}

def disassemble(tool, base, data):
    command = f'wx {data.hex()} @ {base:#x};pDj {len(data)} @ {base:#x}'
    proc = subprocess.run([str(tool), '-N', '-q', '-a', 'riscv', '-b', '32',
                           '-m', hex(base), '-c', command, f'malloc://{len(data)}'],
                          capture_output=True, text=True, check=True, timeout=20)
    rows = json.loads(proc.stdout)
    return {row['addr']: row.get('opcode', '<invalid>') for row in rows}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--r2', type=Path, required=True, help='Existing radare2 executable')
    args = parser.parse_args()
    raw = {}
    with IMAGE.open('rb') as stream:
        for (base, size), expected_hash in WINDOWS.items():
            stream.seek(base - 0x8000)
            data = stream.read(size)
            if hashlib.sha256(data).hexdigest() != expected_hash:
                raise SystemExit(f'Original window changed: {base:#x}')
            raw[base] = data
    seen = {}
    for base, data in raw.items():
        seen.update(disassemble(args.r2, base, data))
    for address, expected in EXPECTED.items():
        if seen.get(address) != expected:
            raise SystemExit(f'Control-flow mismatch at {address:#x}')
    changed = bytearray(raw[0xa2ee])
    changed[0xa32e - 0xa2ee] ^= 0x10
    negative = disassemble(args.r2, 0xa2ee, changed)
    if negative.get(0xa32e) == EXPECTED[0xa32e]:
        raise SystemExit('Changed-branch negative check was not detected')
    print(f'{len(EXPECTED)} control-flow instructions verified; negative check passed; target not executed.')

if __name__ == '__main__':
    main()
