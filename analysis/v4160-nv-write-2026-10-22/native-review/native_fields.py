"""Reuse retained ORI/CSR field definitions; add no instruction-state evaluator."""
import re


def attach(root, source, fields, llvm, ctx):
    # These forms already exist in the sealed flash source decoder. The newer
    # native reader's narrower callback does not route ORI or CSR to it.
    old = source.module(source.locate(root, 'analysis/v4160-flash-native-2026-10-22/source/inspect.py'))
    previous = ctx['extension']

    def extension(raw, pc, base):
        word = int.from_bytes(raw[:4], 'little')
        ori = word & 0x707f == 0x6013
        csr = word & 0x7f == 0x73 and (word >> 7) & 31 == 0 and (word >> 12) & 7 in (2, 3)
        if len(raw) >= 4 and (ori or csr):
            row = old.decode(raw, 0x8000)
            row.update(PC=pc, memory_width=None)
            return row
        return previous(raw, pc, base)

    ctx['extension'] = extension
    previous_parse = llvm['parse']

    def parse(text):
        result = []
        for line in text.splitlines():
            m = re.match(r'^\s*([0-9a-f]+):\s+((?:[0-9a-f]{2}\s+)+)\s*(ori|csrc|csrs)\s+([^#]+?)\s*$', line)
            if not m:
                result.extend(previous_parse(line))
                continue
            pc, raw, op = int(m[1], 16), bytes.fromhex(m[2]), m[3]
            args = [x.strip() for x in m[4].split(',')]
            source.need(len(raw) == 4 and len(args) == (3 if op == 'ori' else 2), 'Complete retained LLVM ORI/CSR operand form')
            row = dict(PC=pc, bytes=4, raw_hex=raw.hex(), op=op, rd=0,
                       rs1=None, rs2=None, immediate=None, target=None, memory_width=None)
            if op == 'ori':
                row.update(rd=llvm['reg'](args[0]), rs1=llvm['reg'](args[1]), immediate=int(args[2], 0))
            else:
                row.update(rs1=llvm['reg'](args[1]), immediate=int(args[0], 0))
            result.append(row)
        return result

    new_llvm = dict(llvm)
    new_llvm['parse'] = parse
    return fields, new_llvm, ctx
