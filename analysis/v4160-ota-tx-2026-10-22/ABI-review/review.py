#!/usr/bin/env python3
"""Read actual TX component objects/IR/link witness, without running target code."""
import argparse
import hashlib
import json
from pathlib import Path
import runpy
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
NATIVE = '24ade8f364d00cbc6c7afc2239f13d67fef4f6822647fc4525c05cd9e64bd5eb'


def need(value, message):
    if not value:
        raise ValueError(message)


def digest(payload):
    return hashlib.sha256(payload).hexdigest()


def module():
    path = HERE / 'native.py'
    need(digest(path.read_bytes()) == NATIVE, 'Pinned independent native subset/gap checker')
    return runpy.run_path(str(path))


def linked_contract(e, component, native, context):
    need(e.kind == 2 and e.flags == 1, 'Actual linked RVC soft-float ELF32 witness')
    symbol = native['one'](e.symbols, lambda s: s['name'] == native['NAME'], 'One linked TX function')
    need((symbol['value'], symbol['size'], symbol['info'], symbol['other']) ==
         (0x8a56, len(component), 18, 0), 'Linked original entry/actual component extent/FUNC role')
    owner = e.sections[symbol['index']]
    need((owner['type'], owner['flags'], owner['alignment'], owner['address'], owner['size']) ==
         (1, 6, 2, 0x8a56, len(component)), 'Single exact linked AX component owner')
    need([s['index'] for s in e.sections if s['flags'] & 2 and s['size']] == [owner['index']],
         'No additional allocated witness storage')
    need(not e.relocations and not [s for s in e.symbols if s['name'] and s['index'] == 0],
         'No unresolved linked relocation/provider')
    provider = native['one'](e.symbols, lambda s: s['name'] == '__tsl9v4160_data_2000b18c',
                             'One numeric original RAM alias witness')
    need(provider['index'] == 0xfff1 and provider['value'] == 0x2000b18c and provider['size'] == 0,
         'RAM provider is numeric ABS witness only')
    body = e.function_bytes(symbol)
    original_rows = native['rows'](component, context)
    pair = native['kernel'](original_rows)['RAM_PCREL_pair']
    hi, lo = pair[0]['offset'], pair[1]['offset']
    raw_hi = int.from_bytes(body[hi:hi + 4], 'little')
    raw_lo = int.from_bytes(body[lo:lo + 4], 'little')
    need(raw_hi & 0xfff == 0x697 and raw_lo & 0xfffff == 0x68693,
         'Linked PCREL instructions retain AUIPC A3 / ADDI A3,A3 fields')
    displacement = raw_hi & 0xfffff000
    if displacement & 0x80000000:
        displacement -= 1 << 32
    low = raw_lo >> 20
    if low & 0x800:
        low -= 1 << 12
    resolved = (0x8a56 + hi + displacement + low) & 0xffffffff
    need(resolved == 0x2000b18c, 'Actual encoded PCREL target equals numeric RAM witness')
    restored = bytearray(body)
    restored[hi:hi + 4] = component[hi:hi + 4]
    restored[lo:lo + 4] = component[lo:lo + 4]
    need(bytes(restored) == component, 'All linked bytes outside two actual PCREL words equal compiler object')
    return dict(actual_linked_artifact_read=True, entry=0x8a56, bytes=len(body),
                body_sha256=digest(body), RAM_PCREL_target=resolved,
                numeric_provider_is_installed_RAM_proof=False,
                only_two_PCREL_words_may_change=True, original_ABI_admitted=False)


def inspect(root, firmware, folder):
    native = module()
    checked = native['inspect_native'](root, folder, firmware)
    context = native['context'](root, firmware)
    obj = context['ELF'](folder / 'tx_native.o')
    symbol, _ = native['object_contract'](obj)
    component = obj.function_bytes(symbol)
    linked = folder / 'ADDRESS-WITNESS-ONLY.elf'
    if not linked.is_file():
        linked = folder / 'COMPONENT-ONLY-NOT-FIRMWARE.elf'
    need(linked.is_file(), 'Explicit actual linked component witness required')
    actual = context['ELF'](linked)
    link = linked_contract(actual, component, native, context)
    controls = []
    symbol = next(s for s in actual.symbols if s['name'] == native['NAME'])
    owner = actual.sections[symbol['index']]
    hi = checked['checked_subset']['RAM_PCREL_pair'][0]['offset']
    for name, offset, mask in [('changed_compiler_byte', owner['offset'], 4),
                               ('wrong_encoded_RAM_target', owner['offset'] + hi + 2, 16)]:
        raw = bytearray(actual.raw)
        raw[offset] ^= mask
        try:
            changed = context['ELF'](context['helper']['BytesInput'](bytes(raw)))
            linked_contract(changed, component, native, context)
        except ValueError as error:
            controls.append(dict(name=name, actual_ELF_bytes_mutated=True, rejected=True, reason=str(error)))
        else:
            raise ValueError('Linked artifact mutation was admitted: ' + name)
    files = ['tx_native.o', 'tx_native.ll', linked.name]
    if (folder / 'verification.json').is_file():
        files.append('verification.json')
    return dict(schema='TSL9-TX-actual-native-ABI-review-v1', review_completed=True,
                actual_build_artifact_replay=True, checked_subset_passed=True,
                original_ABI_admitted=False, target_execution=False, ISA_emulation=False,
                hardware_OTA_proved=False, native=checked, linked=link,
                linked_artifact_controls=controls,
                actual_files={name: digest((folder / name).read_bytes()) for name in files})


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--project-root', type=Path, required=True)
    parser.add_argument('--firmware', type=Path, required=True)
    parser.add_argument('--folder', type=Path)
    parser.add_argument('--receipt', type=Path)
    parser.add_argument('--replay', type=Path)
    args = parser.parse_args()
    root, firmware = args.project_root.resolve(), args.firmware.resolve()
    if args.replay:
        need(not args.folder and not args.receipt, 'Replay has no creation arguments')
        saved = json.loads(args.replay.read_bytes())
        folder = root / saved['folder']
        result = inspect(root, firmware, folder)
        need(result == saved['result'], 'Actual artifact replay matches recorded full static results')
    else:
        need(args.folder and args.receipt, 'Actual folder and create-only receipt required')
        folder = args.folder.resolve()
        result = inspect(root, firmware, folder)
        need(not args.receipt.exists(), 'Create-only review receipt')
        args.receipt.parent.mkdir(parents=True, exist_ok=True)
        value = dict(folder=folder.relative_to(root).as_posix(), result=result)
        args.receipt.write_bytes((json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf8'))
    print(json.dumps(dict(review_completed=True, actual_build_artifact_replay=True,
                         checked_subset_passed=True, original_ABI_admitted=False,
                         bytes=result['native']['bytes'], linked_controls=len(result['linked_artifact_controls']))))


if __name__ == '__main__':
    main()
