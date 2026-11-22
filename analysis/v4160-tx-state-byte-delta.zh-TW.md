# 把 TX 的 93 個差異位元組對回狀態轉移

直接比較原 decoded BIN 與既存 C、C++ selected-spans 輸出，沒有用差異清單反造候選。兩份候選是包含 TX composite 的連結產物，不是純 C。三段已選範圍共 73,672 bytes；93 處全部在組框函式 `0x8a56` 內，後續事件 1/2 的 handler 沒有同位址差異。這不增加覆蓋，不涵蓋未選的 3,128 bytes。

|原 BIN 位址（末端不含）|原指令的作用|同位址不同 bytes|
|---|---|---:|
|8a56–8ace|長度、handle、CCC、選 bank 或返回|2|
|8ace–8b0a|準備 frame header、checksum 初值|2|
|8b0a–8b14|比較游標與長度|2|
|8b14–8b1a|寫最後 checksum|6|
|8b1a–8b3a|還原部分暫存器、寫總長與零游標|32|
|8b3a–8b52|載入 task ID 與服務槽，尾跳請求事件 1|24|
|8b52–8b6c|複製一個 byte、累加 checksum、回迴圈|25|
|8b6c–8b6e|早退 ret|0|

**不能把 32 個差異解讀成 32 個描述元錯誤。** 原版在 `0x8b10` 滿足無號 `<` 才跳去 `0x8b52` 複製；候選改為滿足 `>=` 才跳去 `0x8b2e` 結算，複製本體在 `0x8b14` 順序執行。原版寫總長、清游標在 `0x8b32/36`，候選相同兩條半字 store 在 `0x8b4c/50`；事件尾跳則從 `0x8b50` 移至 `0x8b6a`。這說明為何按原位址分桶有 87 bytes 落在結算與迴圈本體；不是全函式等價證明。狀態語意見[TX 狀態轉移表](v4160-tx-state-map.zh-TW.md)。

複核：依序傳入原 BIN、C 與 C++ 的 `NOT-FLASHABLE-selected-spans-*.bin`。不修改輸入，不需要裝置。

```python
from hashlib import sha256
from pathlib import Path
import sys
b,c,cpp=map(lambda p:Path(p).read_bytes(),sys.argv[1:])
def check(ok):
    if not ok: raise ValueError('TX state delta mismatch')
check(sha256(b).hexdigest()=='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667')
check(c==cpp and sha256(c).hexdigest()=='ef9d3be753f02d5802a2c2feda99aa94b9b3c3acc2b55d32f8f480719d658a54')
pcs=[i for lo,hi in [(0x8000,0x14056),(0x14c8a,0x1a69c),(0x1a6a0,0x1ac00)] for i in range(lo,hi)]
check(len(pcs)==len(c)==73672)
d=[pc for pc,v in zip(pcs,c) if b[pc-0x8000]!=v]
edges=[0x8a56,0x8ace,0x8b0a,0x8b14,0x8b1a,0x8b3a,0x8b52,0x8b6c,0x8b6e]
n=[sum(lo<=pc<hi for pc in d) for lo,hi in zip(edges,edges[1:])]
check(sum(n)==len(d)==93 and n==[2,2,2,6,32,24,25,0])
check(b[0xb32:0xb3a]==c[0xb4c:0xb54]==bytes.fromhex('2391870023920700'))
print('PASS: 73672 selected bytes per mode; 93 differences:',n)
```
