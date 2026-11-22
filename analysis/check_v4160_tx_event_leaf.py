"""Usage: python check_v4160_tx_event_leaf.py APP V131-carrier V140-carrier"""
from hashlib import sha256
from pathlib import Path
import sys


def check(ok):
    if not ok:
        raise ValueError('unexpected TX/event evidence')


def load(path, digest):
    data = Path(path).read_bytes()
    check(sha256(data).hexdigest() == digest)
    return data


def main(paths):
    app, old, new = paths
    b = load(app, '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667')
    check(b[0xb24:0xb3a].hex() == '0a06f240d2444249b2498545b6972391870023920700')
    check(b[0xb3a:0xb52].hex() == '938741093e966244b707040003a307050345060005610283')
    specs = [(old, '133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22', 0x4354a, 413, 484),
             (new, 'b02cf8ec6829425a558887bd6bc10d28ae1f0e2e9e1850333f0bab6088e9e941', 0x435d6, 493, 564)]
    for path, digest, entry, count, table in specs:
        image = load(path, digest)
        check(int.from_bytes(image[80:84], 'little') == entry)
        p = entry - 0x40000
        body = image[p:p+64]
        for off, imm, op in [(20, count, 0x74703), (36, table, 0x62503)]:
            check(int.from_bytes(body[off:off+4], 'little') == (imm << 20 | op))
        check((body[:20]+body[24:36]+body[40:]).hex() == 'b747024083a6c72023a607200f100000373700206370e50237360020131715003a951a21d98d0ea123a6d7200145828023a6d7200d458280')
        print(f'PASS {entry:#x}: 64 bytes; count={0x20003000+count:#x}, table pointer={0x20003000+table:#x}')


if __name__ == '__main__':
    main(sys.argv[1:])
