"""Project each original jump-table case to its first direct call boundary.

Successful table/input reads assumed; the callee is not executed.  Not an ABI,
full instruction emulator, reachability, or hardware proof.
"""
import hashlib
import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('dispatch', HERE / 'table_dispatch.py')
dispatch = importlib.util.module_from_spec(spec)
spec.loader.exec_module(dispatch)
CASES = {
    0x1452e: bytes.fromhex('26858145eff04fe7'),
    0x1453e: bytes.fromhex('26858d45eff04fe6'),
    0x1454a: bytes.fromhex('8d452685eff08fe5'),
    0x1473e: bytes.fromhex('91452685eff04fc6'),
    0x14748: bytes.fromhex('8d452685eff0afc5'),
}


def entry(pc, code, handle):
    if pc not in CASES or code != CASES[pc] or not 0 <= handle <= 0xffffffff:
        raise ValueError('unexpected case entry')
    # Pinned c.mv/c.li pair selects a0=s1 and a1=0,3,3,4,3.
    mode = {0x1452e: 0, 0x1453e: 3, 0x1454a: 3, 0x1473e: 4, 0x14748: 3}[pc]
    callpc = pc + 4
    word = int.from_bytes(code[4:8], 'little')
    if word & 0xfff != 0x0ef: raise ValueError('expected JAL ra')
    imm = ((word >> 31 & 1) << 20) | ((word >> 12 & 255) << 12) | ((word >> 20 & 1) << 11) | ((word >> 21 & 1023) << 1)
    imm -= (imm & (1 << 20)) * 2
    return ((callpc + imm) & 0xffffffff, handle, mode, callpc + 4)


def main():
    image = dispatch.IMAGE.read_bytes()
    if len(image) != 76800 or hashlib.sha256(image).hexdigest() != dispatch.SHA: raise ValueError('APP identity mismatch')
    code = image[dispatch.START-0x8000:dispatch.START-0x8000+len(dispatch.EXPECTED)]
    table = image[0x1a6a4-0x8000:0x1a6b8-0x8000]
    cases = {pc: image[pc-0x8000:pc-0x8000+len(raw)] for pc,raw in CASES.items()}
    for index, pc in enumerate(dispatch.TARGETS):
        if dispatch.dispatch(code,table,index) != pc: raise ValueError('dispatch mismatch')
        for handle in range(65536):
            if entry(pc,cases[pc],handle) != (0x13ba6,handle,(0,3,3,4,3)[index],pc+8): raise ValueError('call projection mismatch')
        for handle in (0x10000,0x80000000,0xffffffff):
            if entry(pc,cases[pc],handle)[1] != handle: raise ValueError('full handle lost')
        for offset in range(8):
            bad=bytearray(cases[pc]); bad[offset]^=1
            try: entry(pc,bytes(bad),0)
            except ValueError: continue
            raise ValueError('instruction mutation accepted')
    print('PASS: five cases x 65536 handles, 15 full-width boundaries, 40 instruction mutations')
    print('First calls target 0x13ba6 with a0=s1 and a1=0,3,3,4,3; stop before call.')
    print('Bounded pinned-code projection, not continuous CPU, callee or hardware execution.')

if __name__ == '__main__': main()
