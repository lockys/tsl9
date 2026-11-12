"""Offline static pins and independent abstract-model checks; never executes C."""
import hashlib
import itertools
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
IMAGE = ROOT / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
IMAGE_SHA = '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
C_SHA = 'c55545853f62fb5b53bffe205ba565c84561932a524424ea88ddcce322c7d88e'
WINDOW = bytes.fromhex('83c706006367b5026365a6029deb854741112380f60022c406c63a84ef40f05e9147631cf50022852244b24041016fe0005381cb238006008280b2402244410182808280')

def need(condition, message):
    if not condition:
        raise ValueError(message)

def verify_image(image):
    need(len(image) == 76800, 'image length')
    need(hashlib.sha256(image).hexdigest() == IMAGE_SHA, 'image sha256')
    verify_window(image)

def verify_window(image):
    need(image[0x248:0x28c] == WINDOW, 'target window')

def verify_c(source):
    need(hashlib.sha256(source).hexdigest() == C_SHA, 'candidate sha256')

def rejected(fn, value):
    try:
        fn(value)
    except ValueError:
        return
    raise ValueError('mutation accepted')

def model(x, lo, hi, old, arg, result):
    events = []
    if x < lo or hi < x:
        if old: events.append(('store', 0))
    elif not old:
        events.extend((('store', 1), ('call', 0xd052)))
        if result == 4: events.append(('tail', 0x167a6, arg))
    return events

def oracle(x, lo, hi, old, arg, result):
    inside = lo <= x <= hi
    if inside and old == 0:
        return [('store', 1), ('call', 0xd052)] + ([('tail', 0x167a6, arg)] if result == 4 else [])
    if not inside and old != 0:
        return [('store', 0)]
    return []

def main():
    image = IMAGE.read_bytes()
    source = (HERE / 'candidate.c').read_bytes()
    verify_image(image)
    verify_c(source)
    mutated = bytearray(image); mutated[0x248] ^= 1
    rejected(verify_image, mutated)
    rejected(verify_window, mutated)
    rejected(verify_image, image[:-1])
    rejected(verify_c, source + b'\n')
    # All weak orderings of three 32-bit unsigned values are represented,
    # including equalities, reversed bounds and the sign boundary.
    values = (0, 1, 2, 0x7fffffff, 0x80000000, 0xfffffffe, 0xffffffff)
    count = 0
    for x, lo, hi in itertools.product(values, repeat=3):
        for old in range(256):
            for result in (0, 3, 4, 5, 0x80000000, 0xffffffff):
                arg = 0xdeadbeef
                need(model(x, lo, hi, old, arg, result) == oracle(x, lo, hi, old, arg, result), 'model mismatch')
                count += 1
    # Explicit semantic negative controls target the Python event specification,
    # not the C implementation, which is not executed or parsed here.
    sx = lambda v: v if v < 0x80000000 else v - 0x100000000
    x, lo, hi = 0x80000000, 0x7fffffff, 0x80000001
    signed_wrong = model(sx(x), sx(lo), sx(hi), 0, 0x12345678, 4)
    need(signed_wrong != model(x, lo, hi, 0, 0x12345678, 4), 'signed comparison negative control')
    need([('store', 1), ('call', 0xd052)] != model(5, 5, 10, 2, 0, 4), 'old byte negative control')
    expected = model(5, 5, 10, 0, 0x12345678, 4)
    need([('store', 1), ('call', 0xd052), ('tail', 0x167a6, 0x78)] != expected, 'argument truncation negative control')
    need([('call', 0xd052), ('store', 1), ('tail', 0x167a6, 0x12345678)] != expected, 'event order negative control')
    need(expected != model(5, 5, 10, 0, 0x12345678, 3), 'callee return negative control')
    print('pins and abstract negative controls OK; abstract cases:', count)

if __name__ == '__main__':
    main()
