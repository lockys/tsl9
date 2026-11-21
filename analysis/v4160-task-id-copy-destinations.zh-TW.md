# 任務 ID：六位元組連線列與 256-byte 表更新的複製目的

核對的是事件處理被呼叫時的三類目的，不宣稱這些事件曾在設備上發生。四個待保護 byte 是 reset gp 加 148、152、166、363。

|呼叫|實際作為目的的值|能排除什麼|
|---|---|---|
|`0x118ba`|第一個空連線列的 `R+4`，長度 6|三種合法索引的 18 個 byte 全不碰 ID；`event+4` 是來源。|
|`0x14b1a/0x14c20/0x14bf4`|從三個 RAM 槽重讀的表指標，長度 256|若仍是 reset 指標，三頁合計 `[0x2000c494,0x2000c794)` 不碰 ID；不是固定目的保證。|
|`0x12e6e/0x12f62/0x1306c`|包裝函式當下的 `sp`，長度 256|固定表位址在 **a1（來源）**。以包裝入口 SP 為 E，目的區間是 `[E−272,E−16)`，保存 ra 在 `[E−4,E)`。不重疊自己的 ra，與 ID 是否分離仍取決於 E。|

V1.31 參考服務入口 `0x20000332`：兩指標非零且長度非零才進迴圈。每輪先讀 `src+i`，以舊 i 計算 `dst+i`，才遞增 i、寫一個 byte，最後比較長度。另有兩次對 `0x4002420c` 的 word store，並非寫表或 ID。這是固定候選程式的正常存取語意，不是對實機的觀測。也不涵蓋快照完成後 `0x9c0a` 的副作用。

重現：先執行 `analysis/check_v4160_notify_replacements.py <APP>` 核對三個槽與對應包裝；[連線列來源](v4160-link-event-row-source.zh-TW.md)列出三個目的。下列檢查參數為 decoded APP、V1.31 carrier；堆疊例採明示的合成入口 E，而非假定真實呼叫深度。

```python
from hashlib import sha256
from pathlib import Path
import sys
a,b=[Path(f).read_bytes() for f in sys.argv[1:]]
def ck(x):
    if not x: raise ValueError('copy evidence differs')
ck(sha256(a).hexdigest()=='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667')
ck(sha256(b).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22')
def app(p,n): return a[p-0x8000:p-0x8000+n]
ck(b[76:80].hex()=='32030020' and b[0x5a2:0x5dc].hex()=='b747024003a7c72023a607200f10000001c599c1814711e6b747024023a6e7208280b386f50003c80600b306f500850723800601e317f6fec5b7')
ids={0x20004000+i for i in (148,152,166,363)}
for i,p in enumerate((0x12e54,0x12f48,0x13052)):
    ck(app(p,18).hex()=='b7070400fc476d71232611100a8513060010' and app(p+26,2).hex()=='8297')
    u=int.from_bytes(app(p+18,4),'little'); k=int.from_bytes(app(p+22,4),'little',signed=True)>>20
    src=p+18+(u&0xfffff000)+k; ck(src==0x2000c494+256*i)
    ck(not ids.intersection(range(src,src+256)))
    d=0x2000bff0+12*i; ck(not ids.intersection(range(d,d+6)))
for E in (0x2000f000,0x20010000):
    d=E-272; ck(d+256==E-16 and not ids.intersection(range(d,d+256)) and d+256<=E-4)
print('PASS: 3 link rows; 3 reset-bound pages; 3 stack copy prefixes; 2 illustrative stack placements')
```
