# 設定 774 前：先排查直達派送器與兩個 handler 的呼叫

逐半字檢查原 APP（76,800 bytes）、V1.31 參考主區（191,078 bytes），以及將首段搬移內容按 RAM 位址解讀的區間（11,828 bytes）。目的端是派送器 `0x200007d0` 與兩個包含 12-byte 廣播物件配置呼叫的 handler 入口 `0x6a7e4`、`0x6d26c`。九組檢查都沒有 JAL、C.J/C.JAL 或相鄰 AUIPC/JALR 直達目的端的編碼。對應的小端 32-bit 位址常數只找到一筆：主區 `0x40078` 存放 `0x200007d0`。資料表有指標，不代表初始化執行過它。

正控制是兩個 handler 內呼叫 `0x482f4` 的真實 JAL。此法不涵蓋透過暫存器、函式表、分開構造位址或中斷抵達的路徑；例如已知 APP `0x819c` 本來就是透過 RAM 槽間接呼叫。因此不能由九組零命中斷言 774 前沒有派送。下一個有區別力的檢查是追初始化內哪些間接呼叫實際載入派送器，而不是再掃直達跳轉。

在 repo 根目錄執行下列 Python，依序傳入原 APP 與 V1.31 主區檔：

```python
from hashlib import sha256
from pathlib import Path
import sys
sys.path.insert(0,'analysis')
from check_v131_descriptor_edges import edges
a,r=(Path(p).read_bytes() for p in sys.argv[1:])
def ck(x):
    if not x: raise ValueError('dispatch census mismatch')
ck(sha256(a).hexdigest()=='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667')
ck(sha256(r).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22')
ck(edges(r,0x40000,0x482f4)==[('0x6aa42','JAL',1),('0x6d3b2','JAL',1)])
for t in (0x200007d0,0x6a7e4,0x6d26c):
    for base,b in [(0x8000,a),(0x40000,r),(0x20000040,r[0x2b0:0x2b0+2957*4])]:
        ck(not edges(b,base,t))
        words=[base+i for i in range(0,len(b)-3,2) if b[i:i+4]==t.to_bytes(4,'little')]
        ck(words==([0x40078] if (t,base)==(0x200007d0,0x40000) else []))
print('PASS: 9 target/range pairs; 1 literal; 2 positive control edges')
```
