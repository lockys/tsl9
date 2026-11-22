# 774 廣播資料：複製成功後是否立即註冊 GATT？

原 APP 的 13-byte 呼叫已在前篇定位；以下只分析 V1.31 參考映像的非零長度分支，不假定裝置 ROM 相同。

`0x487ca` 要求 21 bytes。若配置失敗直接返回 2；成功時先按舊指標是否非零決定是否釋放，再設新物件首字為物件地址 +8、發布新指標到 `0x20002f48`，要求清零並複製 13 bytes。下表從這些服務正常返回後算起，不宣稱它們沒有副作用。

|依序取樣的條件|`0x48790` 的後續行為|
|---|---|
|`word[0x20002f14] == 0`|直接返回 0，連下一個旗標也不讀。|
|上述非零，且 `byte[0x200033b0] & 5 == 0`|直接返回 18。|
|上述非零，且 bit 0 或 bit 2 為 1|重新讀取 `word[0x20002f48]`；空指標時將 a3、a4 歸零，**不是**提早返回。兩路都以 `(a0,a1,a2)=(1,3,1)` 尾跳 `0x53414 → 0x677ae`。|

前兩條收尾不呼叫 GATT 註冊。第三條也不是跳到已知的兩個服務註冊入口：`0x677ae` 先呼叫 `0x68ee4`，若返回，再以 `(0x2037,1,sp+15)` 呼叫 `0x6a70c`。不能因此排除更深層的間接呼叫。下一個可判別問題是：第一個 gate 所讀 `0x20002f14` 在 APP 設定廣播資料**之前**是否已有寫入非零值；只找到某個寫入點並不證明它在此之前執行。

從 repo 根目錄執行以下 Python，唯一參數為 V1.31 參考主區檔。檢查解碼分支、實際載入位址、遮罩與轉移；有限列舉不是實機執行。

```python
from pathlib import Path
from hashlib import sha256
import sys
sys.path.insert(0,'analysis')
from check_v131_descriptor_edges import edges,sx
b=Path(sys.argv[1]).read_bytes()
def ck(v):
    if not v: raise ValueError('advertising dispatch mismatch')
ck(sha256(b).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22')
def raw(p,n): return b[p-0x40000:p-0x40000+n]
def val(p,n): return int.from_bytes(raw(p,n),'little')
def gate(p):
    h=val(p,2); ck(h&0xe383==0xc381)
    d=(h>>12&1)<<8|(h>>10&3)<<3|(h>>5&3)<<6|(h>>3&3)<<1|(h>>2&1)<<5
    return p+sx(d,9)
for p,op,addr in [(0x48818,2,0x20002f14),(0x48822,4,0x200033b0),(0x4882e,2,0x20002f48)]:
    u,w=val(p,4),val(p+4,4); ck(u&4095==0x7b7 and w&0xfffff==(15<<15|op<<12|15<<7|3)); ck((u&0xfffff000)+sx(w>>20,12)==addr)
g0,g1,g2=map(gate,(0x48820,0x4882c,0x48836)); ck((g0,g1,g2)==(0x48858,0x4885c,0x48852)); ck(val(0x4882a,2)==0x8b95)
for p,t,link in [(0x4884e,0x53414,0),(0x53414,0x677ae,0),(0x677b2,0x68ee4,1),(0x677c4,0x6a70c,1)]: ck(edges(raw(p,4),p,t)==[(hex(p),'JAL',link)])
counts=[0,0,0]; mask=(val(0x4882a,2)>>2)&31
for present in (0,1):
    for flag in range(256):
        for obj in (0,1):
            pc=g0 if not present else g1 if not flag&mask else g2 if not obj else 0x48838
            counts[{0x48858:0,0x4885c:1,0x48852:2,0x48838:2}[pc]]+=1
ck(counts==[512,128,384]); print('PASS: 3 gates, 4 transfers; return-0 / return-18 / tail:',counts)
```
