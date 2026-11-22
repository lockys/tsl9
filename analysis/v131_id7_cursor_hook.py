"""Post-merge V1.31 projection: stop before the hook or at the next branch target."""
from collections import ChainMap

def bind(image):
    def pin(pc, text):
        raw = bytes.fromhex(text)
        off = pc - 0x20000000 + 0x270
        if image[off:off+len(raw)] != raw:
            raise ValueError('scheduler byte mismatch at %#x' % pc)
    pin(0x200007ea, '37390020')  # s2 base
    pin(0x20000832, '130ac419')  # s4 = s0 + 412
    pin(0x2000092a, '8347c419 81c7 8507 230ef418 8327891c 81c7 8297 2324091c 0347c419 83471a00 e371f7f0')
    def observe(ram, regs):
        mem = ChainMap({}, ram)
        cur = regs['s0'] + 412
        slot = regs['s2'] + 456
        if mem[cur]:
            mem[cur] = (mem[cur]+1) & 255
        missing = tuple(i for i in range(slot,slot+4) if i not in mem)
        if missing:
            return mem[cur], 'unknown-slot', missing
        hook = int.from_bytes(bytes(mem[i] for i in range(slot,slot+4)), 'little')
        if hook:
            return mem[cur], 'call', hook & 0xfffffffe
        target = 0x2000084c if mem[regs['s4']+1] <= mem[cur] else 0x2000094e
        return mem[cur], 'no-call', target
    return observe
