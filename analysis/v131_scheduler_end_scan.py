"""V1.31 end of scan. Stop at the first service call, missing input or epilogue."""
from collections import ChainMap


def bind(image):
    def pin(pc, hexes):
        raw = bytes.fromhex(hexes)
        i = pc - 0x20000000 + 0x270
        if image[i:i + len(raw)] != raw:
            raise ValueError(f'end-scan instruction mismatch at {pc:#x}')
    pin(0x2000084c, '230e0418 37340020 93074451 9c37 13044451 63910710 b7370020 83a7071e f5c3 dc40 2328fa00 6131')
    pin(0x20000960, '7c30 93f7f70f e39e07ee a3040400 973006e0 e7802046')
    pin(0x2000094e, 'f240 6244 d244 4249 b249 224a 924a 0561 8280')

    def run(ram, regs):
        m = ChainMap({}, ram)
        def load(a, n):
            return int.from_bytes(bytes(m[a+i] for i in range(n)), 'little')
        m[regs['s0'] + 412] = 0
        base = 0x20003514
        try:
            if load(base+9, 1) and not load(base+7, 1):  # conditional Xwchc byte loads
                m[base+9] = 0
                return 'call', 0x63dd0, m
            if not load(0x200031e0, 4):
                return 'epilogue', 0x2000094e, m
            sample = load(regs['s1']+4, 4)
            for i in range(4):
                m[regs['s4']+16+i] = (sample >> (8*i)) & 255
            return 'call', 0x200004fa, m
        except KeyError as err:
            return 'missing', err.args[0], m
    return run
