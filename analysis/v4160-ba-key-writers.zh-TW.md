# 0xba 表的比對鍵：接收狀態，不是掃描函式的參數

`0x11356` 算得固定狀態基址 B=`0x2000bfc8`，先讀 `[B+4]`，為零就返回。入口 a0 留在 s1 作模式用，不是鍵。只有狀態 byte `[B+1]` 為零的這一支進入 42 筆掃描；`0x11396` 在每輪**重讀** `[B+4]` 作 32 位比較值，並非保存入口取樣。因此把它稱為接收端的當前比對鍵，比稱為 task ID 或某個固定事件號更貼近指令。

| 原 APP 寫入點 | 鍵的直接來源 | 寫入後在這條路徑上的動作 |
|---|---|---|
| `0x114f2` | `0x114e2` 的非零入口 a0 | 另存半字和 byte，改以 `a0=0` 呼叫 `0x11356`。這清楚區分了鍵與掃描模式。 |
| `0x11b54` | 從資料位元組組合出的非零 a5 | 在狀態條件成立時存鍵，接著 `0x11b6a` 直接呼叫掃描器。 |
| `0x11c86` | 另一條接收分支組合出的非零 a5 | 在此分支不是立即呼叫掃描器，而是向 `[0x40058]` 請求事件位 1。若其後派發至 `0x11442` 且選到位 1，才以模式 0 掃描；未證實際派發。 |

掃描整個原 BIN 的相鄰 `auipc` + 同基址 `sw` 編碼，恰有以上三處對準 `0x2000bfcc`。這不是所有寫入的證明；不涵蓋其他形式定址、間接服務與非同步改寫。五個標準直接 JAL 到 `0x11356` 中，`0x11454/0x11476` 是事件分支，`0x121a4` 是既有鍵相符後的條件重掃，不能把五個呼叫都計為新鍵寫入。這支持「按接收狀態的鍵查表並選動作」，仍不足以指定鍵代表哪種實體裝置或產品事件。

重播（參數為 decoded BIN；索引為半字對齊視窗，含資料區）：

```python
from pathlib import Path
import hashlib,sys
b=Path(sys.argv[1]).read_bytes()
if hashlib.sha256(b).hexdigest()!='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667': raise ValueError('APP')
def w(p): return int.from_bytes(b[p-32768:p-32768+4],'little')
def sx(x,n): return (x^(1<<(n-1)))-(1<<(n-1))
p=0x11356; u=w(p); i=w(p+4)
if u&4095!=0x797 or i&0xfffff!=0x78793: raise ValueError('base operands')
B=(p+(u&0xfffff000)+sx(i>>20,12))&0xffffffff
stores=[];calls=[]
for p in range(32768,32768+len(b)-3,2):
    v=w(p); r=v>>15&31
    if p>=32772 and v&0x707f==0x2023 and r:
        u=w(p-4); off=sx((v>>25<<5)|(v>>7&31),12)
        if u&4095==(r<<7|23) and (p-4+(u&0xfffff000)+off)&0xffffffff==B+4: stores.append((p,v>>20&31))
    if v&4095==0xef:
        d=(v>>31<<20)|(v>>12&255)<<12|(v>>20&1)<<11|(v>>21&1023)<<1
        if p+sx(d,21)==0x11356: calls.append(p)
if (B,w(0x11396),stores,calls)!=(0x2000bfc8,0x00492683,[(0x114f2,10),(0x11b54,15),(0x11c86,15)],[0x11454,0x11476,0x1150c,0x11b6a,0x121a4]): raise ValueError((B,stores,calls))
print('PASS: fixed key load, 3 adjacent word stores and 5 direct calls')
```
