"""v4.1.60：0x107c0 的位址兩度出現：一次取消查找，一次請求登記。
若事件系統稍後呼叫它，入口會先把 a0 改為 0，再轉至 0x1074c。
這是指標流的候選來源，不證明登記成功或回呼曾執行。執行位置：repo 根目錄。
Scope: exact little-endian words at any byte, and adjacent RV32 LUI/AUIPC +
ADDI/JALR at any halfword. Excludes nonadjacent, compressed, relative-table,
RAM-computed and resident references. A data match alone is not a call.
"""
from hashlib import sha256
from pathlib import Path

BASE = 0x8000
IMAGE = Path('firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin')
TARGETS = {0x12b24, 0x1074c, 0x107c6, 0x9ad2, 0x107c0}


def scan(b, base, targets):
    hits = {t: [] for t in targets}
    for t in targets:
        needle = t.to_bytes(4, 'little')
        i = b.find(needle)
        while i >= 0:
            hits[t].append(('word', base+i)); i = b.find(needle, i+1)
    for i in range(0, len(b)-7, 2):
        w = int.from_bytes(b[i:i+4], 'little'); op = w & 127; rd = w >> 7 & 31
        if op not in (0x17, 0x37) or not rd: continue
        v = int.from_bytes(b[i+4:i+8], 'little'); low = v & 0x707f
        if low not in (0x13, 0x67) or (v >> 15 & 31) != rd: continue
        if low == 0x13 and not (v >> 7 & 31): continue
        t = ((base+i if op == 0x17 else 0)+(w & 0xfffff000)+((v >> 20 ^ 2048)-2048)) & 0xffffffff
        if low == 0x67: t &= ~1
        if t in hits: hits[t].append((('auipc' if op==0x17 else 'lui')+('addi' if low==0x13 else 'jalr'), base+i))
    return hits


def main():
    b = IMAGE.read_bytes()
    if sha256(b).hexdigest() != '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667': raise ValueError('wrong APP')
    actual = scan(b, BASE, TARGETS)
    if actual != {0x12b24: [], 0x1074c: [], 0x107c6: [], 0x9ad2: [('auipcaddi',0x9b08),('auipcaddi',0x9b6e)], 0x107c0: [('auipcaddi',0x1073e),('auipcaddi',0x1085a)]}: raise ValueError('unexpected census')
    for p, h in [(0x10852,'81461306007d8145'),(0x107c0,'0145')]:
        v = bytes.fromhex(h)
        if b[p-BASE:p-BASE+len(v)] != v: raise ValueError('unexpected arguments')
    for p, rd, dest in [(0x10748,0,0x90b0),(0x10862,1,0x9124),(0x107c2,0,0x1074c)]:
        w = int.from_bytes(b[p-BASE:p-BASE+4], 'little')
        d = (w>>31<<20)|(w>>12&255)<<12|(w>>20&1)<<11|(w>>21&1023)<<1
        if w&4095 != 111+(rd<<7) or p+(d^1048576)-1048576 != dest: raise ValueError('unexpected edge')
    # Positive controls for absent forms: word at odd byte; LUI x5 then JALR
    # with odd effective address rounded down. Mismatched base register must fail.
    toy = bytes.fromhex('b7220100e780522b')
    if scan(toy,0,{0x122b4})[0x122b4] != [('luijalr',0)]: raise ValueError('jalr control')
    if scan(toy[:4]+bytes.fromhex('e700532b'),0,{0x122b4})[0x122b4]: raise ValueError('register control')
    if scan(b'x'+(0x12b24).to_bytes(4,'little'),0,{0x12b24})[0x12b24] != [('word',1)]: raise ValueError('word control')
    for t, hits in sorted(actual.items()):
        print(hex(t), [(kind,hex(pc)) for kind,pc in hits])


if __name__ == '__main__': main()
