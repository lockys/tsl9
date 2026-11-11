"""Three fixed RF_Tx data instructions only; synthetic state, no target execution.

The caller chooses each PC and supplies instruction bytes. Branches, instruction
fetch, helper, and all other instructions are outside this bounded model.
"""
import runpy
from pathlib import Path

_decoder = runpy.run_path(str(Path(__file__).with_name('check-rf-tx-header-window.py')))
SITES = {
    0x64e0e: (bytes.fromhex('0850'), _decoder['decode_load'], 'lw'),
    0x64e28: (bytes.fromhex('1c50'), _decoder['decode_load'], 'lw'),
    0x64e14: (bytes.fromhex('23007501'), _decoder['decode_sb'], 'sb'),
    0x64e18: (bytes.fromhex('04b1'), _decoder['decode_qk_sb'], 'sb'),
}
END = 1 << 32


def step(state, pc, instruction):
    """Return a fresh state; forbidden code or invalid access halts without writes.

    State has 32 u32 registers, an explicit address->byte map, and halted flag.
    x0 is required to be zero. There is no automatic PC advancement.
    """
    result = {'regs': list(state['regs']), 'memory': dict(state['memory']),
              'halted': state['halted']}
    if result['halted']:
        return result
    try:
        regs, mem = result['regs'], result['memory']
        if (len(regs) != 32 or any(type(v) is not int or not 0 <= v < END for v in regs)
                or regs[0] != 0):
            raise ValueError('invalid registers')
        expected, decode, op = SITES[pc]
        if instruction != expected:
            raise ValueError('forbidden instruction')
        reg, base, offset = decode(instruction)
        address = (regs[base] + offset) % END
        width = 4 if op == 'lw' else 1
        if address + width > END:
            raise ValueError('wrapping access')
        if any(a not in mem or type(mem[a]) is not int or not 0 <= mem[a] <= 255
               for a in range(address, address + width)):
            raise ValueError('unmapped or invalid byte')
        if op == 'lw':
            value = int.from_bytes(bytes(mem[a] for a in range(address, address + 4)), 'little')
            if reg:
                regs[reg] = value
        else:
            mem[address] = regs[reg] & 255
    except (KeyError, ValueError, TypeError):
        result['halted'] = True
    return result
