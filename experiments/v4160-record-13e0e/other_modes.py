"""Test additional bounded 0x13e0e modes with synthetic successful memory."""
import hashlib
from verify import BIN, SHA, FIRST, SECOND, run


def main():
    image = BIN.read_bytes()
    if len(image) != 76800 or hashlib.sha256(image).hexdigest() != SHA:
        raise ValueError('firmware identity mismatch')
    count = 0
    for value in range(65536):
        other = value ^ 1
        for mode in (0, 3, 0xffffffff):
            for handle, first, second, reads, writes in (
                (value, value, other, [FIRST], [(FIRST, 0xfffe), (FIRST+2, 0), (FIRST+3, 0)]),
                (value, other, value, [FIRST, SECOND], [(SECOND, 0xfffe), (SECOND+2, 0), (SECOND+3, 0)]),
                (value, value, value, [FIRST], [(FIRST, 0xfffe), (FIRST+2, 0), (FIRST+3, 0)]),
                (value, other, other, [FIRST, SECOND], []),
                (value | 0x10000, value, value, [FIRST, SECOND], []),
            ):
                if run(image, handle, first, second, mode=mode) != (reads, writes):
                    raise ValueError(f'mode {mode:#x}, handle {handle:#x}')
                count += 1
        for handle, first, second, reads, writes in (
            (value, 0xfffe, value, [FIRST], [(FIRST, value), (FIRST+2, 0), (FIRST+3, 0)]),
            (value | 0x10000, 0xfffe, 0xfffe, [FIRST], [(FIRST, value), (FIRST+2, 0), (FIRST+3, 0)]),
            (value, 0xffff, 0xfffe, [FIRST, SECOND], [(SECOND, value), (SECOND+2, 0), (SECOND+3, 0)]),
            (value, 0xffff, 0xffff, [FIRST, SECOND], []),
        ):
            if run(image, handle, first, second, mode=2) != (reads, writes):
                raise ValueError(f'mode 2, handle {handle:#x}')
            count += 1
    altered = bytearray(image)
    altered[0x13e40 - 0x8000] ^= 4
    try:
        result = run(altered, 7, 0xfffe, 0xffff, mode=2)
    except ValueError:
        pass
    else:
        if result == ([FIRST], [(FIRST, 7), (FIRST+2, 0), (FIRST+3, 0)]):
            raise ValueError('sentinel mutant survived')
    print(f'PASS: {count} synthetic mode 0/2/3/0xffffffff cases; ordered writes, sentinel priority, truncation and sentinel mutant')
    print('Projection only; no concurrency, hardware, real pointer validity or route reachability.')


if __name__ == '__main__': main()
