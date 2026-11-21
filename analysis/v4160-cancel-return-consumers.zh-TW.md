# 取消服務回傳 6，原 APP 會改走另一條路嗎？

區分兩種「未命中」：APP `0x90b0` 找不到匹配記錄時自行回 1；找到記錄時才清記錄並於 `0x910e` 尾跳服務。以下只分析**後者正常返回 6**時 a0 的用途，不把參考 ROM 的結果當成實機觀測。

|原 BIN 的呼叫點|返回後真正決定流程的值|
|---|---|
|`0x14100`、`0x14190`|隨即呼叫 `0x81aa`。其第一條指令是 `lbu a0,167(gp)`，完全覆蓋 6；接下來 `beqz` 測這個 byte，不是取消結果。它也不是存任務 ID 的 `gp+166`。|
|`0x13de0`|下一條 `li a0,0`，不測 6，改用 0 呼叫 `0x13d48`。|
|`0x9b12`|將 live s0 的低 byte 存至 `gp+168`，分支測完整的 s0，不測 a0。若 s0 在呼叫中保持，它是 `0x9b02` 的輸入。兩個正常出口皆不改 a0，因此**本層不測 6，但仍將 6 傳回上層**。|
|`0x17f72`|兩個前置 byte 判斷都通過才呼叫取消。呼叫後只還原暫存器與 SP、返回，故該路徑原樣傳回 6；若前置判斷跳過呼叫，不能把同一返回點當成取消結果。|

全 APP 半字對齊掃描發現 31 個 JAL-ra、8 個 JAL-x0 編碼直接指向 `0x90b0`。後者是尾跳，沒有本地的「呼叫後一條指令」可當作返回點。這是編碼盤點與上表五處的局部解讀，不是 39 條已執行的路徑，也不涵蓋間接呼叫；不表示服務的記憶體副作用被撤銷。

重現：傳入原 decoded APP。檢查 JAL 目的與 link register、重讀 byte 的位移及兩個分支使用的暫存器，另鎖定返回路徑。

```python
from pathlib import Path
from hashlib import sha256
from collections import Counter
import sys
b=Path(sys.argv[1]).read_bytes()
def ck(v):
    if not v: raise ValueError('cancel consumer evidence mismatch')
ck(sha256(b).hexdigest()=='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667')
def w(p):return int.from_bytes(b[p-32768:p-32764],'little')
def jal(p):
    x=w(p);d=x>>31<<20|(x&0xff000)|(x>>20&1)<<11|(x>>21&1023)<<1
    return (x>>7&31,p+(d^1048576)-1048576) if x&127==111 else (None,None)
def raw(p,h):
    v=bytes.fromhex(h);ck(b[p-32768:p-32768+len(v)]==v)
hits={p:r for p in range(32768,32768+len(b)-3,2) for r,t in [jal(p)] if t==0x90b0};ck(Counter(hits.values())=={1:31,0:8})
for p in (0x14100,0x14190,0x13de0,0x9b12,0x17f72):ck(hits[p]==1)
for p in (0x14100,0x14190):
    ck(jal(p+4)==(1,0x81aa));x=w(p+8)&65535;ck(x&0xe003==0xc001 and 8+(x>>7&7)==10)
x=w(0x81aa);ck((x&127,x>>12&7,x>>7&31,x>>15&31,x>>20)==(3,4,10,3,167));raw(0x81ae,'8280');raw(0x13de4,'0145');ck(jal(0x13de6)==(1,0x13d48))
raw(0x9b06,'2a84');raw(0x9b16,'2384810a11c8b2402244b7170140094723aae780410182802244b240410175bf');raw(0x9af0,'83c7810a91e7b7170140094723a8e7808280');raw(0x17f76,'f2406244d24405618280')
print('PASS: 31 direct call and 8 tail encodings; 5 selected caller paths; both getter branches test gp+167')
```
