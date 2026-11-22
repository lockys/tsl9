"""V1.31 scheduler at handler return. Only the listed ten encodings, conditional Xwchc."""
from collections import ChainMap

START = 0x2000090c
WORDS = '83d7ca1d 0347c419 93c7f7ff 7d8d 93171700 03a7491e 3e97 1e23 5d8d 0aa3'.split()

def bind(image):
    encoded = bytes.fromhex(''.join(WORDS))
    off = 0x270 + START - 0x20000000
    if image[off:off+len(encoded)] != encoded:
        raise ValueError('scheduler return bytes differ')

    def merge(ram, regs, patches=()):
        m = ChainMap({}, ram)
        r = regs.copy()
        def load(addr, width):
            return int.from_bytes(bytes(m[addr+i] for i in range(width)), 'little')
        def store(addr, width, value):
            m.update({addr+i: (value >> (8*i)) & 255 for i in range(width)})
        for addr,width,value in patches: store(addr,width,value)
        r['a5'] = load(r['s5']+476,2)
        r['a4'] = load(r['s0']+412,1)
        r['a5'] ^= 0xffffffff
        r['a0'] &= r['a5']
        r['a5'] = r['a4'] << 1
        r['a4'] = load(r['s3']+484,4)
        r['a4'] = (r['a4']+r['a5']) & 0xffffffff
        r['a5'] = load(r['a4'],2)   # 1e23, conditional vendor halfword load
        r['a0'] |= r['a5']
        store(r['a4'],2,r['a0'])     # 0aa3, conditional vendor halfword store
        return r['a4'],load(r['a4'],2)
    return merge
