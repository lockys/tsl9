"""Abstract trace checks and static pins; does not execute or validate C."""
from pathlib import Path
import hashlib

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
IMAGE = ROOT / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'

def require(ok, what):
    if not ok:
        raise ValueError(what)

def pin(data, digest):
    require(hashlib.sha256(data).hexdigest() == digest, 'pin mismatch')

def trace(gp, words, callback):
    # Independent abstract specification. Memory is consulted on each read.
    events = []
    def read(pc, addr):
        value = words[addr]; events.append(('read', pc, addr, value)); return value
    def call(pc, target, a0, a1, a2):
        events.append(('call', pc, target & 0xfffffffe, a0, a1, a2))
        return callback(pc, words)
    t = read(0x13172, 0x40048)
    if not call(0x13188, t, 0x2000c29c, 0, 112): return events
    events.extend([('store', 0x1318e, 0x2000c29e, 2, 0xfff),
                   ('store', 0x13194, 0x2000c2a0, 1, 1),
                   ('store', 0x1319c, 0x2000c2a4, 2, 257)])
    p = read(0x131a4, (gp + 84) & 0xffffffff)
    t = read(0x131a6, 0x4004c)
    if not call(0x131b4, t, (p + 12) & 0xffffffff, 0x1a69c, 4): return events
    events.append(('tail', 0x131be, 0x13138))
    return events

def main():
    image = IMAGE.read_bytes()
    window = image[0x1316a-0x8000:0x131c2-0x8000]
    c = (HERE / 'model.c').read_bytes()
    pin(image, '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667')
    pin(window, '0eee723b584b06b7f4addfd45403bbfd17b9f0b09cb29aadaedfbf9f346a5514')
    pin(c, '91fa452ed5c321cb857c42c4ec1d9a3927e66e91d3525f1a9c088405167c694d')
    for data, digest in [(image, '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'), (window, '0eee723b584b06b7f4addfd45403bbfd17b9f0b09cb29aadaedfbf9f346a5514'), (c, '91fa452ed5c321cb857c42c4ec1d9a3927e66e91d3525f1a9c088405167c694d')]:
        try: pin(bytes([data[0] ^ 1]) + data[1:], digest)
        except ValueError: pass
        else: raise RuntimeError('negative pin accepted')
    def change(pc, words):
        if pc == 0x13188:
            words[0x1054] = 0xfffffffc
            words[0x4004c] = 0x3333
        return True
    got = trace(0x1000, {0x40048: 0x1111, 0x4004c: 0x2222, 0x1054: 0x8888}, change)
    want = [('read',0x13172,0x40048,0x1111),('call',0x13188,0x1110,0x2000c29c,0,112),('store',0x1318e,0x2000c29e,2,0xfff),('store',0x13194,0x2000c2a0,1,1),('store',0x1319c,0x2000c2a4,2,257),('read',0x131a4,0x1054,0xfffffffc),('read',0x131a6,0x4004c,0x3333),('call',0x131b4,0x3332,8,0x1a69c,4),('tail',0x131be,0x13138)]
    require(got == want, 'abstract trace')
    for stop, count in [(0x13188,2), (0x131b4,8)]:
        result = trace(0x1000, {0x40048:1,0x4004c:2,0x1054:3}, lambda pc, words: pc != stop)
        require(len(result) == count and result[-1][0] == 'call', 'nonreturn boundary')
    require(got != want[:-1], 'missing tail accepted')
    require(got != [want[0], want[1], *want[5:7], *want[2:5], *want[7:]], 'reordered reads accepted')
    print('pins and abstract model tests passed (C not executed)')

if __name__ == '__main__': main()
