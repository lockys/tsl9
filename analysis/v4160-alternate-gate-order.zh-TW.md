# 哪一次 0x60856 呼叫可能在第一角色之前？

接續[候選寫入來源](v4160-pre-registration-other-writer-paths.zh-TW.md)。以下只討論 APP 同步正常返回、槽仍綁定 V1.31 參考實作的路徑。

* **`0x5a008`：從第二角色入口來的這一次太晚。** APP `0x8eb6` 先經 `[0x401a0]` 進 `0x6dd16 → 0x61b1c → 0x55bde`；返回後 `0x8ebc` 才經 `[0x401ac]` 進 `0x6dd86 → 0x5a004 → 0x60856`。所以這次呼叫不能影響前一次讀值。它在第二角色自身的 `0x6dda0` 判斷之前，不能因後者略過一組初始化而把這次呼叫也刪掉。沒有排除同一入口的其他間接來源。
* **`0x6a2e0`：不是無條件的第二初始化。** `0x679a2` 包裝函式在 `0x679aa` 呼叫 `0x6a2a8`。其 `0x6a2c6` 先呼叫 `0x5784a`；若返回零，`0x6a2d2` 跳過候選呼叫。若返回非零，還要 `U32[0x2000343c]==0` 才會執行 `0x6a2e0`。`0x6a2ce` 讀的相鄰 word `0x20003438` 不是此處條件，它到 `0x6a2e4` 才被測試。`0x5784a` 的入口讀 `0x20003454`；若為零，直接返回零，不需要推測任何串列內容。尚未證明清零到首次角色入口間此 word 持續為零，或包裝函式在此期間被呼叫。

重現：以 decoded APP、V1.31 carrier 為參數。從映像讀指令、解析 JAL 和兩個壓縮分支的目標，比對兩次槽呼叫的順序與查表前綴。這不是設備或整條初始化執行證明。

```python
from hashlib import sha256
from pathlib import Path
import sys
a,b=(Path(p).read_bytes() for p in sys.argv[1:])
def ck(x):
    if not x: raise ValueError('alternate registration origin mismatch')
ck(sha256(a).hexdigest()=='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667' and sha256(b).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22')
def u(p,n=4):return int.from_bytes(b[p-0x40000:p-0x40000+n],'little')
def sx(v,n):return (v^(1<<(n-1)))-(1<<(n-1))
def jal(p):
    x=u(p);ck(x&4095==239);return p+sx(x>>31<<20|(x&0xff000)|(x>>20&1)<<11|(x>>21&1023)<<1,21)
def branch(p,opcode,reg):
    h=u(p,2);ck(h&0xe003==opcode and (h>>7&7)+8==reg)
    return p+sx((h>>12&1)<<8|(h>>10&3)<<3|(h>>5&3)<<6|(h>>3&3)<<1|(h>>2&1)<<5,9)
ck(a[0xeb2:0xebe].hex()=='8327041a82978327c41a8297' and [u(p) for p in (0x401a0,0x401ac)]==[0x6dd16,0x6dd86])
ck([jal(p) for p in (0x6dd1a,0x61b20,0x6dd8a,0x5a008,0x679aa,0x6a2c6,0x6a2e0)]==[0x61b1c,0x55bde,0x5a004,0x60856,0x6a2a8,0x5784a,0x60856])
ck(branch(0x6a2d2,0xc001,10)==0x6a382 and branch(0x6a2de,0xe001,15)==0x6a2e4)
ck(u(0x6a2c2)==0x200034b7 and u(0x6a2d4)==0x3b848493 and u(0x6a2d8)==0x0844a783)
ck(0x20003000+(u(0x6a2d4)>>20)+(u(0x6a2d8)>>20)==0x2000343c)
ck(u(0x5784a)==0x200037b7 and u(0x5784e)==0x4547a783 and branch(0x57852,0xe001,15)==0x57858 and u(0x57854)==0x8082853e)
print('PASS: ordered APP slots; 7 call edges; 3 branch targets; empty lookup head returns zero')
```
