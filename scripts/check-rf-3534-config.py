#!/usr/bin/env python3
"""Offline identity and bounded instruction-window checks, not execution."""
import hashlib
import json
import runpy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
base = runpy.run_path(str(ROOT / 'scripts/check-rf-3538-api-alias.py'))
WINDOWS = {
    (0x401c4, 0x401c8): 'dc55dfbb2d2cbe1162d1469abf1e87506fc55a4b1b2cfb005508cdfd23fe64b0',
    (0x64bae, 0x64cec): '0e73a5cebf069a716f6967b386c8cc9de529e25608933422eda98997a0ec9bf4',
    (0x64cec, 0x64f04): 'ceaf41c2ab3fe78e13a20a79e19480c367c767395dc8f11ed6f02b7dce23a871',
}

def verify_windows(image):
    for (start, end), digest in WINDOWS.items():
        window = image[start - 0x40000:end - 0x40000]
        if len(window) != end - start or hashlib.sha256(window).hexdigest() != digest:
            raise ValueError(f'window mismatch {start:#x}..{end:#x}')
    return True

def verify(image, header):
    base['verify'](image, header)
    verify_windows(image)
    if int.from_bytes(image[0x1c4:0x1c8], 'little') != 0x64bae:
        raise ValueError('RF_Config slot mismatch')
    return {'rf_config': '0x64bae', 'rf_tx': '0x64cec',
            'pointer_word': '0x20003534', 'config_allocator_word': '0x20003564',
            'conditional_alias_not_initialization': True}

if __name__ == '__main__':
    print(json.dumps(verify(base['IMAGE'].read_bytes(), base['HEADER'].read_bytes()), indent=2))
