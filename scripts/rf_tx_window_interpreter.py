"""Fixed candidate window interpreter over synthetic state; no helper or hardware execution."""
import runpy
from pathlib import Path

steps = runpy.run_path(str(Path(__file__).with_name('rf_tx_header_steps.py')))
START = 0x64e0e
END = 1 << 32
# Identity gate as well as instruction boundaries. Fetch is always from caller's map.
CODE = bytes.fromhex('0850 63080c0c 23007501 04b1 2686 e285 0905 97b0f91f e7802051')
SIZES = {0x64e0e: 2, 0x64e10: 4, 0x64e14: 4, 0x64e18: 2,
         0x64e1a: 2, 0x64e1c: 2, 0x64e1e: 2, 0x64e20: 4, 0x64e24: 4}


def run(state, code):
    """Start at 64e0e; return boundary, or fail-closed halt. No external effects.

    code is an address->byte map. The taken branch leaves this subset and halts.
    State is copied; previously completed instructions remain visible on a halt.
    """
    s = {'regs': list(state['regs']), 'memory': dict(state['memory']),
         'pc': START, 'status': 'running'}
    while s['status'] == 'running':
        pc = s['pc']
        try:
            r = s['regs']
            if len(r) != 32 or r[0] != 0 or any(type(v) is not int or not 0 <= v < END for v in r):
                raise ValueError('registers')
            size = SIZES[pc]
            ins = bytes(code[pc + i] for i in range(size))
            if ins != CODE[pc - START:pc - START + size]:
                raise ValueError('mutated instruction')
            w = int.from_bytes(ins, 'little')
            next_pc = pc + size
            if pc in steps['SITES']:
                t = steps['step']({'regs': r, 'memory': s['memory'], 'halted': False}, pc, ins)
                if t['halted']:
                    raise ValueError('memory access')
                s['regs'], s['memory'] = t['regs'], t['memory']
            elif pc == 0x64e10:  # BEQ: decode rs1, rs2 and signed B immediate
                imm = ((w >> 31) << 12) | (((w >> 7) & 1) << 11) | (((w >> 25) & 63) << 5) | (((w >> 8) & 15) << 1)
                if imm & 0x1000:
                    imm -= 0x2000
                if r[(w >> 15) & 31] == r[(w >> 20) & 31]:
                    next_pc = pc + imm
            elif pc in (0x64e1a, 0x64e1c):  # C.MV
                r[(w >> 7) & 31] = r[(w >> 2) & 31]
            elif pc == 0x64e1e:  # C.ADDI, signed six-bit immediate
                imm = ((w >> 2) & 31) | (((w >> 12) & 1) << 5)
                if imm & 32:
                    imm -= 64
                rd = (w >> 7) & 31
                r[rd] = (r[rd] + imm) % END
            elif pc == 0x64e20:  # AUIPC
                r[(w >> 7) & 31] = (pc + (w & 0xfffff000)) % END
            else:  # JALR boundary: report target and arguments, do not call
                imm = w >> 20
                if imm & 0x800:
                    imm -= 0x1000
                s['target'] = ((r[(w >> 15) & 31] + imm) % END) & ~1
                s['status'] = 'boundary'
                continue
            s['pc'] = next_pc
        except (KeyError, ValueError, TypeError, OverflowError):
            s['status'] = 'halted'
    return s
