# 兩個角色首次讀記錄前：登記本身會寫哪裡？

V1.31 參考段 `0x6d5b2`、`0x6aeb2` 直接呼叫同一個 `0x43c4e`，傳入的 handler 分別是 `0x6d26c`、`0x6abc6`。這兩處都是登記，不是執行 handler。接上[登記返回後的寫入](v4160-pre774-role-preread-writes.zh-TW.md)，可把原來的排除範圍向前延伸至這兩個呼叫點。

依[登記指令](v4160-registration-gp166.zh-TW.md)的 Xwchc 解讀，滿表分支不讀表基址、不寫 RAM；成功分支先寫計數 byte `0x2000319d`，再將 handler 存入 `T+4*n`，其中 `T` 是從 `0x200031c4` 載入的表基址。無須假設登記一定成功或預測角色 ID。若 `T` 保持[初始化配置](v4160-role-internal-table-writes.zh-TW.md)的 `P+576`，且 P 在名義 arena，這兩筆寫入都不碰 `cfg+52`。若容量 c 也仍對應原配置，`n<c` 更保證該 word 的結束界（不含）不超過 `T+4*c`，而非只證起點在表內。

重現：將以下程式以 V1.31 主段檔名作為參數執行。檢查原碼身分、兩個 JAL 目標與傳入值，再枚舉成功分支全部 32,640 個計數／容量組合（其餘 32,896 組滿表）；P 的地址算式單調，檢查兩端點。這不是裝置 ROM 鑑定，也不證明 `T` 在更早的初始化回呼之後仍有效。

```python
from hashlib import sha256
from pathlib import Path
import sys
b=Path(sys.argv[1]).read_bytes()
def ck(v):
    if not v: raise ValueError('role registration mismatch')
def w(p): return int.from_bytes(b[p-0x40000:p-0x40000+4],'little')
def sx(v,k): return (v^(1<<(k-1)))-(1<<(k-1))
ck(sha256(b).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22')
ck(b[0x3c4e:0x3c7e].hex()=='373700201307c7191c33342363ffd700b736002083a6461c1386170010b313972700369708c33e8582809307f00fe5bf')
for p,j,target in [(0x6d5aa,0x6d5b2,0x6d26c),(0x6aea6,0x6aeb2,0x6abc6)]:
    a,d,x=w(p),w(p+4),w(j)
    ck(a&4095==0x537 and d&0xfffff==0x50513 and (a&0xfffff000)+sx(d>>20,12)==target)
    if j!=p+8: ck(w(p+8)==0x20003437)
    off=(x>>31<<20)|(x>>12&255)<<12|(x>>20&1)<<11|(x>>21&1023)<<1
    ck(x&4095==0xef and j+sx(off,21)==0x43c4e)
success=0
for c in range(256):
    for n in range(c):
        for p in (0x200043b4,0x2000b183):
            t=p+576; a=t+4*n
            ck(0x20003224<=a and a+4<=t+4*c<2**32)
        success+=1
ck(success==32640 and 0x2000319d+1<=0x20003220)
print('PASS: two registration edges; 32640 successful pairs bounded, 32896 full pairs by complement')
```
