"""Only encountered standard32 ORI/SLL/AND/SLTU operand fields; no CPU state."""
def decode(raw, pc, previous):
    try: return previous(raw, pc)
    except ValueError: pass
    if len(raw) < 4: raise ValueError('Whole standard word')
    w = int.from_bytes(raw[:4], 'little')
    rd, rs1, rs2 = (w >> 7) & 31, (w >> 15) & 31, (w >> 20) & 31
    op, f3, f7 = w & 127, (w >> 12) & 7, w >> 25
    row = dict(PC=pc, bytes=4, raw_hex=raw[:4].hex(), rd=rd, rs1=rs1,
               rs2=None, immediate=None, target=None, memory_width=None)
    if op == 0x13 and f3 == 6:
        imm = w >> 20
        row.update(op='ori', immediate=imm - 4096 if imm & 2048 else imm)
        return row
    if op == 0x33 and f7 == 0 and f3 in (1, 3, 7):
        row.update(op={1: 'sll', 3: 'sltu', 7: 'and'}[f3], rs2=rs2)
        return row
    raise ValueError('Unadmitted ADC field form '+hex(pc))
