"""Bounded static byte anchors for one CF96 caller and its frame; not an ABI proof."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BIN = ROOT / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
SHA = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
BASE = 0x8000
# Byte fingerprints are independently checked against the pinned image, not decoded here.
ANCHORS = {
    'entry_frame': (0xcf96, '411122c42a840345550006c6'),
    'mode_store_then_gp_load': (0xcfb4, '238aa7f883c7410e'),
    'e220_argument_setup': (0xcfd4, '014685451305e503'),
    'mode_reload_then_gp_store': (0xcfe0, '97f7ff1f938787f583c7c7002382f10e'),
    'before_provider_reload': (0xcff4, '03457400'),
    'after_provider_reload': (0xcffc, '03457400'),
    'tail_restore': (0xd026, '2244b2404101'),
    'return_restore': (0xd040, 'b240224441018280'),
    'caller_move_restore': (0x14dc2, '22852244b2404101'),
}
JALS = {'caller_tail': (0x14dca, 0xcf96, 0),
        'first_provider': (0xcff8, 0xa00c, 1),
        'normal_state_call': (0xcff0, 0x13c4e, 1),
        'e220_call': (0xcfdc, 0xe220, 1),
        'f9ec_call': (0xd022, 0xf9ec, 1),
        'cc54_call': (0xd036, 0xcc54, 1),
        'bce0_call': (0xd03a, 0xbce0, 1),
        'final_state_tail': (0xd02c, 0x13c4e, 0)}


def decode_jal(pc, data):
    if len(data) != 4:
        raise ValueError('JAL width')
    word = int.from_bytes(data, 'little')
    if word & 0x7f != 0x6f:
        raise ValueError('JAL opcode')
    immediate = (((word >> 31) & 1) << 20 | ((word >> 12) & 0xff) << 12 |
                 ((word >> 20) & 1) << 11 | ((word >> 21) & 0x3ff) << 1)
    if immediate & (1 << 20):
        immediate -= 1 << 21
    return ((pc + immediate) & 0xffffffff, (word >> 7) & 31)


def raw_jal_sites(image, base, target):
    """Inspect windows in a non-wrapping RV32 image with an even base."""
    if not (0 <= base <= 0xffffffff and base % 2 == 0 and
            0 <= target <= 0xffffffff and base + len(image) <= 0x100000000):
        raise ValueError('scan requires an even base and non-wrapping RV32 range')
    hits = []
    for offset in range(0, len(image) - 3, 2):
        chunk = image[offset:offset + 4]
        if chunk[0] & 0x7f == 0x6f:
            destination, rd = decode_jal(base + offset, chunk)
            if destination == target:
                hits.append((base + offset, rd))
    return hits


def verify(image, check_identity=True):
    if len(image) != 76800:
        raise ValueError('BIN length')
    if check_identity and hashlib.sha256(image).hexdigest() != SHA:
        raise ValueError('BIN identity')
    for name, (address, hex_bytes) in ANCHORS.items():
        expected = bytes.fromhex(hex_bytes)
        if image[address-BASE:address-BASE+len(expected)] != expected:
            raise ValueError('anchor mismatch: ' + name)
    for name, (address, destination, rd) in JALS.items():
        actual = decode_jal(address, image[address-BASE:address-BASE+4])
        if actual != (destination, rd):
            raise ValueError('edge mismatch: ' + name)
    hits = raw_jal_sites(image, BASE, 0xcf96)
    return {'anchors': list(ANCHORS), 'jal_edges': list(JALS),
            'raw_jal_cf96': [{'pc': hex(pc), 'rd': rd} for pc, rd in hits],
            'status': 'INCOMPLETE_FAIL_CLOSED', 'passed': False,
            'scope': 'selected static bytes and raw halfword-aligned JAL scan only; not instruction boundaries, complete callers, reachability, ABI or pure-C equivalence'}


def main():
    with BIN.open('rb') as stream:
        image = stream.read(76801)
    print(json.dumps(verify(image), indent=2))
    return 2


if __name__ == '__main__':
    raise SystemExit(main())
