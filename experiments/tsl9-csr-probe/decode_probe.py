"""Decode an exact 12-byte T9D record; never communicates with hardware."""
import argparse
import json
from pathlib import Path

def decode(data):
    if len(data) != 12 or data[:4] != b'T9D\x01':
        raise ValueError('expected exactly one 12-byte T9D version 1 record')
    arch = int.from_bytes(data[4:8], 'little')
    impl = int.from_bytes(data[8:12], 'little')
    return {'schema': 'T9D-v1', 'marchid': f'0x{arch:08x}', 'mimpid': f'0x{impl:08x}',
            'matches_wch_v4c_manual_pattern': arch == 0xdc68d883 and impl == 0xdc688001}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('record', type=Path, help='file containing exactly one binary record')
    args = parser.parse_args()
    try:
        data = args.record.read_bytes()
        print(json.dumps(decode(data), sort_keys=True))
    except (OSError, ValueError) as exc:
        parser.exit(2, f'{exc}\n')

if __name__ == '__main__':
    main()
