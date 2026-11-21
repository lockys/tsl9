"""Check nominal fresh-arena first fit, not a device heap snapshot."""
from hashlib import sha256
from pathlib import Path
import sys


def check(b):
    def need(ok, label):
        if not ok:
            raise ValueError(label)

    need(sha256(b).hexdigest() == '133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22', 'carrier')
    def data(pc, size):
        i = pc-0x20000000+0x270 if pc >= 0x20000000 else pc-0x40000
        return b[i:i+size]

    for pc, h in [(0x4314c, '23a0e522e11656a223130600'), (0x200000ae, '7a2131ef5a21636cf704'), (0x200000bc, '3306f74021489386c6196375c802'), (0x200000d2, '138687001d8f2a9661175aa2232016012313060010c15ea1'), (0x200000f0, '6ea1ee222105'), (0x20000104, 'b240224441018280')]:
        need(data(pc,len(bytes.fromhex(h))) == bytes.fromhex(h), hex(pc))
    for pc, form, base, reg, off in [(0x43152,5,12,13,4),(0x200000ae,1,10,14,6),(0x200000b2,1,10,14,4),(0x200000dc,5,12,14,4),(0x200000e8,5,10,15,4),(0x200000f0,5,10,11,6)]:
        h = int.from_bytes(data(pc,2),'little')
        need((h&3,h>>13,8+(h>>7&7),8+(h>>2&7),((h>>10&7)<<3)|((h>>5&3)<<1)) == (2,form,base,reg,off), 'Xwchc field')
    header, successor, request = 0x200043ac, 0x200045ac, 16
    capacity = successor-header-8
    need(capacity == 504 and capacity-request > 8, 'fresh fit and split')
    node = header+8
    rest = node+request
    need((node,rest,successor-rest-8) == (0x200043b4,0x200043c4,480), 'layout')
    print('PASS: 6 instruction windows; 6 Xwchc operands; fresh header 504 -> payload 16 + header 8 + free 480')


if __name__ == '__main__':
    check(Path(sys.argv[1]).read_bytes())
