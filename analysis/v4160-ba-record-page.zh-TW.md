# 0xba：延後回送六 byte 記錄表，而非單筆命中通知

`0x136d0` 把 `[gp+88]` 放進描述項，長度固定 256。reset 於 `0x186ba..0x186da` 把 `0x1ab60` 起的 32 個 word 複製到 gp=`0x20004000`；第 22 個（索引從零起）將 `0x1abb8` 的 `0x2000c30c` 寫入 `0x20004058`。初始化的是**指標**，不是頁內容。

APP 中找到兩個直達 `0x136d0` 的 JAL，皆以當下 s1 作 a0。`0x14474` 在 `0xba` 的短分支、`0x1264e` 正常返回後要求回送整頁；相鄰的 `0x14b3a` 分支則直接以長度 1 呼叫 `0x13e98`，不建立此描述項。`0x14b86` 位於整頁更新之後：先以即時 `[gp+88]` 為目的要求複製 256 bytes，再呼叫 `0x12ee6`、`0x1264e`。`0x12ee6` 的快照來源是固定 `0x2000c30c`；描述項建立時則重新讀取指標槽。只有綁定仍在，兩者才是同一頁。

頁用途另有讀取端佐證：`0x10de8` 將每筆 +4、+2 的兩個半字合為 `(hi<<16)|lo`，每次前進 6，到偏移 252 為止。`0x11392` 迴圈同樣遍歷至多 42 筆，將組合值與輸入記錄 +4 的 word 比對；在特定命中分支以該筆 +1 的 byte 呼叫 `0x155d0`。因此可區分 **0xba 整頁回送** 與 **記錄命中後的動作**。目前未給 32 位鍵指定業務名稱，亦未證實頁的即時內容、間接呼叫結果或實機可達性。

重播：對 decoded BIN 執行下段（第一個參數為路徑）。掃描半字對齊的標準 JAL 編碼，不視為完整呼叫圖。

```python
from pathlib import Path
import hashlib,sys
b=Path(sys.argv[1]).read_bytes()
if hashlib.sha256(b).hexdigest()!='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667': raise ValueError('APP')
def w(p): return int.from_bytes(b[p-32768:p-32768+4],'little')
def sx(x,n): return (x^(1<<(n-1)))-(1<<(n-1))
def pair(p): return (p+(w(p)&0xfffff000)+sx(w(p+4)>>20,12))&0xffffffff
hits=[]
for p in range(32768,32768+len(b)-3,2):
    v=w(p); d=(v>>31<<20)|(v>>12&255)<<12|(v>>20&1)<<11|(v>>21&1023)<<1
    if v&127==111 and p+sx(d,21)==0x136d0: hits.append((p,v>>7&31))
if hits!=[(0x14474,1),(0x14b86,1)]: raise ValueError(hits)
if (pair(0x186aa),pair(0x186ba),w(pair(0x186ba)+88),pair(0x12ef8))!=(0x20004000,0x1ab60,0x2000c30c,0x2000c30c): raise ValueError('bindings')
for p,h in ((0x10de8,'03d7470003d627004207518f'),(0x1139c,'03d7470003d627004207518f'),(0x113d6,'1904e31d34fb'),(0x136ee,'938781059c43'),(0x14472,'2685'),(0x14b84,'2685')):
    if not b.startswith(bytes.fromhex(h),p-32768): raise ValueError(hex(p))
print('PASS: 2 direct JALs, reset slot 22, fixed snapshot source, both record-key readers')
```
