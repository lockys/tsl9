# 第二個 `sb a5,63(s0)` 是否寫到容量？

在 V1.31 參考 carrier（不是已確認的裝置 ROM）每兩 byte 掃描相同的 32-bit 指令編碼，命中 `0x5370c` 和 `0x58a1c`。前者的基址是已核對的 `0x200033b8`；**後者的基址是函式參數，不能因指令相同就把它算作容量的寫入。**

`0x5898c` 把傳入的 `a0` 存到 `s0`。在所查分支、被呼叫者保存 `s0` 的條件下，`0x58a1a/1c` 右移 `a5` 四位再把低 byte 存到該物件 `+63`。故要命中 `0x200033f7`，傳入的指標必須等於 `0x200033b8`。這是地址條件，不保證分支通過或寫入值非零。

查到的直接呼叫是 `0x58ca8 → 0x58988`；`0x58ca2` 傳入呼叫者當時的 `s0`。從 `0x58c52` 入口直落至該呼叫的路徑，`0x58c5a` 的 `s0` 來自 RAM word `0x2000344c`，不是固定基址。已知[第二角色登記此回呼](v4160-first-node-upstream-slots.zh-TW.md)晚於首次 `0x55bde` 讀取，因此靠**該次登記**才發生的呼叫太晚。沒有證據可由這個 store 推定首次讀取前容量已非零，也不能反推它必為零。

核對範圍：固定 carrier、相同 `sb` 指令與所述直接路徑；不是所有寬度、基址、間接呼叫與其他迴圈入口的完整分析。以 carrier 路徑為唯一參數：

```python
from hashlib import sha256
from pathlib import Path
import sys
b=Path(sys.argv[1]).read_bytes(); base=0x40000
def ck(v):
    if not v: raise ValueError('secondary store evidence mismatch')
def at(p,n):return b[p-base:p-base+n]
ck(sha256(b).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22')
ck([base+i for i in range(0,len(b)-3,2) if b[i:i+4]==bytes.fromhex('a30ff402')]==[0x5370c,0x58a1c])
for p,h in [(0x5898c,'2a84'),(0x58a1a,'9183a30ff402'),(0x58c54,'b737002022dc03a4c744'),(0x58ca2,'2285230a0950eff01fce')]:ck(at(p,len(bytes.fromhex(h)))==bytes.fromhex(h))
w=int.from_bytes(at(0x58ca8,4),'little');d=w>>31<<20|(w&0xff000)|(w>>20&1)<<11|(w>>21&1023)<<1;ck(w&4095==239 and 0x58ca8+(d^0x100000)-0x100000==0x58988)
ck(0x20003000+(int.from_bytes(at(0x58c5a,4),'little')>>20)==0x2000344c and 0x200033f7-63==0x200033b8);print('PASS: two identical stores; direct call and pointer source verified')
```
