"""Static pins and independent Python event examples, not tests of C execution."""
from pathlib import Path
import hashlib

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
BIN = ROOT / 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
WINDOW = bytes.fromhex('13950501418163618504a297a382e70093076042b307f60219040a06f240d2444249b2498545b6972391870023920700938741093e966244b707040003a3070503450600056102833385b400034505003388b70085052a97a302a8001377f70f45b7')
SOURCE_SHA = 'f6bf999820c98a10bb6c1fa2789335d93e427c2f9d116d4c325e6f6e6c4260c6'
# Independently transcribed from r2: address, exact bytes, operand-bearing instruction.
OPS = ((0x8b0a,'13950501','slli a0,a1,16'), (0x8b0e,'4181','srli a0,a0,16'),
       (0x8b10,'63618504','bltu a0,s0,0x8b52'), (0x8b52,'3385b400','add a0,s1,a1'),
       (0x8b56,'03450500','lbu a0,0(a0)'), (0x8b5a,'3388b700','add a6,a5,a1'),
       (0x8b5e,'8505','addi a1,a1,1'), (0x8b60,'2a97','add a4,a4,a0'),
       (0x8b62,'a302a800','sb a0,5(a6)'), (0x8b66,'1377f70f','andi a4,a4,255'),
       (0x8b6a,'45b7','j 0x8b0a'))

def require(ok, message):
    if not ok:
        raise ValueError(message)

def pin(window, source):
    require(window == WINDOW, 'BIN window pin failed')
    for addr, code, text in OPS:
        raw = bytes.fromhex(code)
        require(window[addr-0x8b0a:addr-0x8b0a+len(raw)] == raw, text)
    require(hashlib.sha256(source).hexdigest() == SOURCE_SHA, 'source pin failed')

def model(mem, s0, s1, a5, a1, a4, a6, step_limit=None):
    events = []
    while (a1 & 65535) < s0:
        if step_limit is not None and len(events) // 2 == step_limit:
            return None, events
        src = s1 + a1
        value = mem[src]
        events.append(('load', src, value))
        a6 = a5 + a1
        a1 += 1
        a4 = (a4 + value) & 0xffffffff
        dst = a6 + 5
        mem[dst] = value
        events.append(('store', dst, value))
        a4 &= 255
    return (a1 & 65535, a1, a4, a6), events

def run():
    with BIN.open('rb') as f:
        f.seek(0x8b0a - 0x8000)
        window = f.read(len(WINDOW))
    source = (HERE / 'candidate.c').read_bytes()
    pin(window, source)
    # Mutations must fail even when Python runs with -O; no assert statements.
    for i in range(len(window)):
        bad = bytearray(window)
        bad[i] ^= 1
        try:
            pin(bytes(bad), source)
        except ValueError:
            continue
        raise ValueError('mutated BIN bypassed pin')
    try:
        pin(window, source + b' ')
    except ValueError:
        pass
    else:
        raise ValueError('mutated source bypassed pin')
    mem = bytearray(32)
    mem[10:13] = bytes((250, 7, 9))
    regs, events = model(mem, 3, 10, 6, 0, 0xfffffffe, 123)
    require(events == [('load',10,250),('store',11,250),('load',11,250),('store',12,250),('load',12,250),('store',13,250)], 'alias events')
    require(regs == (3,3,236,8), 'carry/truncation or registers')
    mem = bytearray(65550)
    mem[65538] = 17
    regs, events = model(mem, 3, 0, 0, 65538, 255, 99)
    require(events == [('load',65538,17),('store',65543,17)] and regs == (3,65539,16,65538), 'full index boundary')
    mem = bytearray(65550)
    mem[65535:65537] = bytes((3, 4))
    regs, events = model(mem, 65536, 0, 0, 65535, 0, 0, 2)
    require(regs is None and events == [('load',65535,3),('store',65540,3),('load',65536,4),('store',65541,4)], 'low16 wrap prefix')
    regs, events = model(mem, 0, 0, 0, 0x12340000, 0xffffffff, 99)
    require(not events and regs == (0,0x12340000,0xffffffff,99), 'zero iteration')
    print('Pins, mutation negatives, and independent Python event examples passed; C was not executed.')

if __name__ == '__main__':
    run()
