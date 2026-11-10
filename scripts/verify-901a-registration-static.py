#!/usr/bin/env python3
"""Offline byte/opcode evidence checker; no execution or live binding inference."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INPUTS = {
    'app': ('firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin', '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'),
    'sdk': ('analysis/wch-resident-candidate-2026-10-21/carrier-dec2023/REFERENCE-CANDIDATE-ONLY-00040000-0006EA66.bin', '133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22'),
    'app_ops': ('analysis/resident-startup-2026-10-25/evidence.json', '9c9e418f16ec9b7231df2dc623ee90c39a0b1bba53f0a116271800d7ad8770f5'),
    'register_ops': ('experiments/tsl9-resident-task-registration/evidence-v1.json', 'bf782803e1633b0c830e87bea9ff4191ff3046b17138916b9bda8a79aac87dd7'),
    'scheduler_ops': ('experiments/tsl9-resident-scheduler/evidence-v1.json', '5947ac1c887e1ef8e9c7114c75a63f46814f36ebc0db5939b55fa723ad2b5c10'),
    'header': ('analysis/wch-resident-candidate-2026-10-21/original-dec2023/wchble_rom.h', '647a185941fedeb6ba16d544d9bca91a6f53219bb649a5513b59abeb21a9a94c'),
}
APP_907A = bytes.fromhex('411122c4370404003c4406c61306400b8145173500201305c5d782978327040817050000130505f88297b24022442383a10a41018280')
SLOTS = {0x40048: 0x2000039c, 0x40050: 0x4354a, 0x40058: 0x43728, 0x4005c: 0x439a8, 0x40080: 0x43c4e}


def check_opcode_windows(app, sdk, records):
    if app[0x907a-0x8000:0x90b0-0x8000] != APP_907A:
        raise ValueError('APP 907a opcode mismatch')
    # Pin the entire local scheduler, including both the set-event tail and
    # the occupied/full and timer branches; this is not a semantic decoder.
    if hashlib.sha256(app[0x9124-0x8000:0x9250-0x8000]).hexdigest() != '45dd01a76fedc4bd8d01fdb7ff005f410166a68f171d52420d19da2cbba2e992':
        raise ValueError('APP scheduler opcode mismatch')
    for slot, value in SLOTS.items():
        if sdk[slot-0x40000:slot-0x40000+4] != value.to_bytes(4, 'little'):
            raise ValueError(f'SDK slot {slot:#x} mismatch')
    for key, entry, image, base in [('app_ops', 0x19b16, app, 0x8000), ('register_ops', 0x43c4e, sdk, 0x40000), ('scheduler_ops', 0x200007d0, sdk, 0x40000)]:
        functions = json.loads(records[key])['selected_functions']
        f = next(x for x in functions if x['start'] == entry)
        pc = entry
        for op in f['operations']:
            raw = bytes.fromhex(op['bytes'])
            source = op.get('source_flash_PC', op['addr'])
            if op['addr'] != pc or len(raw) != op['size'] or source < base or image[source-base:source-base+len(raw)] != raw:
                raise ValueError(f'{key} opcode mismatch at {pc:#x}')
            pc += len(raw)
        if pc != f['end']:
            raise ValueError(f'{key} incomplete opcode coverage')


def verify(data):
    for key, (_, expected) in INPUTS.items():
        if hashlib.sha256(data[key]).hexdigest() != expected:
            raise ValueError(f'{key} SHA-256 mismatch')
    check_opcode_windows(data['app'], data['sdk'], data)


if __name__ == '__main__':
    verify({k: (ROOT / path).read_bytes() for k, (path, _) in INPUTS.items()})
    print('APP/SDK and recorded opcode evidence verified (static only)')
