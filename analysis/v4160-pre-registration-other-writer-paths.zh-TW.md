# 清零後，還有哪條路能先設定 0x2000319f？

接續[前置登記](v4160-pre-registration-gate.zh-TW.md)。在 V1.31 參考檔中找到第二個同樣讀取該 byte 的入口 `0x60856`：`0x60862` 遇非零就略過；若為零，依序以 `0x5352c` 呼叫登記函式 `0x43c4e`、以返回值呼叫 `0x5362e`。因此它和 `0x55bde` 共用 `0x53668` 這個寫入點。如果先有一條路以非零 ID 寫回，後一次檢查才會略過。不能因為寫入指令只有一處，就推斷第一次讀到零。

| 候選 API 槽 | 在入口找到的呼叫鏈 |
|---|---|
| `0x40188` | `0x6dca6 → 0x55bde` |
| `0x40190` | `0x6dc36 → 0x60856` |
| `0x401a0` | `0x6dd16 → 0x61b1c → 0x55bde`（本次追查的讀取） |

APP `0x8eb2` 在這裡載入的是 `s0+416`（名義 `0x401a0`），不是前兩個槽；槽的排列並非呼叫順序。另有兩個通往 `0x60856` 的 JAL 編碼位置 `0x5a008 / 0x6a2e0`，不能只檢查三個 API 槽。現有證據只增加**可能的先行寫入途徑**，沒有證明它們在清零與 `0x55bde` 之間被執行，亦沒有推翻清零後保持零的可能性。

重現（參數依序為 decoded APP、V1.31 carrier）。對兩份資料每兩個 bytes 掃描一次；這是編碼候選，不是可達性分析。固定目的寫入搜尋僅辨識緊鄰的 LUI 與一般 SB/SH/SW，涵蓋跨越目標的寬寫，不涵蓋壓縮指令、指標別名、間接呼叫或其他基址建構。

```python
from pathlib import Path
from hashlib import sha256
import sys
a,b=(Path(s).read_bytes() for s in sys.argv[1:])
def need(ok):
    if not ok: raise ValueError('gate origin mismatch')
def sx(v,n): return (v^(1<<(n-1)))-(1<<(n-1))
need([sha256(v).hexdigest() for v in (a,b)]==['0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667','133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22'])
refs={t:[] for t in (0x5362e,0x55bde,0x60856)}; stores=[]
for buf,base in ((a,0x8000),(b,0x40000)):
    for i in range(0,len(buf)-3,2):
        w=int.from_bytes(buf[i:i+4],'little'); pc=base+i
        if w&127==111:
            t=pc+sx(w>>31<<20|(w&0xff000)|(w>>20&1)<<11|(w>>21&1023)<<1,21)
            if t in refs: refs[t].append(pc)
        if w&0xfffff07f!=0x20003037 or i+8>len(buf): continue
        x=int.from_bytes(buf[i+4:i+8],'little'); f=x>>12&7
        if x&127==35 and x>>15&31==w>>7&31 and f<=2:
            d=0x20003000+sx((x>>25)*32+(x>>7&31),12)
            if d<=0x2000319f<d+(1<<f): stores.append((pc+4,d,1<<f))
need(list(refs.values())==[[0x55bf8,0x60870],[0x61b20,0x6dcaa],[0x5a008,0x6a2e0,0x6dc3a]])
need(stores==[(0x53668,0x2000319f,1)])
need([int.from_bytes(b[i:i+4],'little') for i in (0x188,0x190,0x1a0)]==[0x6dca6,0x6dc36,0x6dd16])
need(a[0xeb2:0xeb8].hex()=='8327041a8297' and b[0x20856:0x20874].hex()=='b737002083c7f719411106c689eb373505001305c552ef302ebeef20ffdb')
print('PASS: 2 images; 7 direct-JAL encodings; 1 adjacent fixed store; 3 distinct slots')
```
