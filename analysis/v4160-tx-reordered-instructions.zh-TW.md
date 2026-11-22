# TX：前段四個差異 byte 與重排後的指令對照

輸入是[上一階段](v4160-tx-state-byte-delta.zh-TW.md)固定 SHA-256 的原 BIN 和 C、C++ 兩份實際連結輸出，不是由差異清單還原。以下位址均為 APP 位址。

- `0x8a7f/80` 落在 `0x8a7e` 的 BEQ：原版比較 `a4 == a5`，候選比較 `a5 == a0`，目的地同為 `0x8a96`。由共同前驅 `0x8a76` 正常順序執行到此，意味 `a4 == a0`；中間只設定 `a5 = 0xfffe`。所以接納判斷不變，但不能把兩條 BEQ 當作對任意入口狀態等價。每份候選各核對 196608 組；反轉前驅條件會使兩者可區分。
- `0x8ad3/d4` 落在 `0x8ad2` 的 MUL：目的同是 `a5`，僅把來源 `a2,a5` 換成 `a5,a2`。前一指令載入 1062；對相同輸入，RV32 低 32 位的 bank 偏移 `1062*a2` 不變。

將複製區和收尾區按功能重新配對後，兩版各 96 條指令中 **88 對編碼相同，8 對不同**。這是對應指令計數，與同位址 93 個差異 byte 是不同指標。

|原 → 候選（範圍末端不含）|指令數|編碼不同的原 PC|
|---|---:|---|
|8a56–8b14 → 同址|65|8a7e、8ad2、8b10|
|8b14–8b52 → 8b2e–8b6c|22|8b1e、8b3a、8b3e|
|8b52–8b6c → 8b14–8b2e|8|8b5a、8b6a|
|8b6c–8b6e → 同址|1|無|

另外六對：`0x8b10` 反轉無號比較並交換落入／跳轉區塊；`0x8b1e` 交換乘數；`0x8b5a` 交換加數；兩個迴圈尾跳都回 `0x8b0a`。最後兩對 `0x8b3a/3e` 不只是交換來源：原版先寫 `a5=gp+148` 再把它加進 `a2`；候選在 `a2` 內先加 gp 再加 148，**沒有更新 a5**。在相同輸入下最終 `a2` 相同，但中間暫存器狀態不必相同；兩條路都在後續 LUI 改寫 a5。此處沒有驗證異常、中斷、服務呼叫或整函式可觀測行為。

複核指令配對：依序傳入原 BIN、C selected-spans、C++ selected-spans。所有區間位於第一個連續 span。

```python
from hashlib import sha256
from pathlib import Path
import sys
b,c,cpp=[Path(p).read_bytes() for p in sys.argv[1:]]
def need(v):
    if not v: raise ValueError('TX pair mismatch')
need(sha256(b).hexdigest()=='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667')
need(c==cpp and sha256(c).hexdigest()=='ef9d3be753f02d5802a2c2feda99aa94b9b3c3acc2b55d32f8f480719d658a54')
def ops(d,l,r):
    while l<r:
        i=l-0x8000; n=4 if d[i]&3==3 else 2
        yield l,d[i:i+n]; l+=n
    need(l==r)
diff=[]; total=0
for lo,end,dst,count in [(0x8a56,0x8b14,0x8a56,65),(0x8b14,0x8b52,0x8b2e,22),(0x8b52,0x8b6c,0x8b14,8),(0x8b6c,0x8b6e,0x8b6c,1)]:
    x=list(ops(b,lo,end)); y=list(ops(c,dst,dst+end-lo)); need(len(x)==len(y)==count)
    total+=count; diff.extend(p for (p,v),(_,w) in zip(x,y) if v!=w)
need(diff==[0x8a7e,0x8ad2,0x8b10,0x8b1e,0x8b3a,0x8b3e,0x8b5a,0x8b6a]); print('PASS:',total,'pairs;',total-len(diff),'identical encodings')
```
