# 初始化返回後，首次校時究竟從哪裡取得回呼？

**結論：**若初始化正常返回時 `[0x2000321c]` 仍為 `0x197b8`，下列名義路徑會在 `0x43f52` 重新讀到它。此值不是初始化回傳值，也不是 APP 直接呼叫校準時留下的暫存器。這是 v4.1.60 APP 配 V1.31 參考 resident 的條件結論。

|從哪裡到哪裡|可能寫入與條件|
|---|---|
|`0x43d4e → 0x19aee → 0x8eac`|[正常返回鏈](v4160-release-to-registration-returns.zh-TW.md)；APP 呼叫 `0x19106(64,1)` 寫 `0x40021014`，再寫 `0xe000e104/108`。不把外設間接效應算作已排除。|
|`0x8eac → 0x19b16` 首次登記|`0x43c4e` 若表滿，不寫表；成功時寫計數 byte `0x2000319d` 及重讀之表的第 n 個 word。若表基址仍是 `0x200047f4`，所有成功索引均與回呼槽分離。APP 把結果低 byte 寫 `gp+388`，名義上為 `0x20004184`；登記不是執行 handler。|
|`0x19b38 → 0x19b56`|[13 個直接呼叫](v4160-first-task-reload.zh-TW.md)涵蓋外設控制、四次輪詢、[兩個 RTC setter](v4160-clock-rtc-setters-task-fields.zh-TW.md)及[直接校準](v4160-calibration-store-footprint.zh-TW.md)。已列出的 RAM 寫入在名義堆疊；其餘為 MMIO。直接呼叫 `0x197b8` 不讀 cfg+48。輪詢不退出就到不了下一列。|
|`0x19bcc → [0x40074] → 0x43f52`|傳入的是 16-byte 時鐘設定指標 C，不是 resident 的全域設定基址。參考函式在讀槽之前只把 s0 存到 `C−8`；保存 ra 的 `0x43f54` 則在讀槽**之後**。以 LUI/ADDI 建立全域設定基址，再用 C.LW 讀 `0x200031ec+48`。|

前提：返回與堆疊正常、GP 和函式表符合上述配置、記憶體存取成功、無異步寫入或地址映射變化。若讀到零便跳過回呼；若讀到其他值，不可沿用 `0x197b8` 的分析。這不是設備記憶體快照或新的純 C 覆蓋。

重現：傳入 decoded APP、V1.31 carrier。從來源解出參考槽、讀址和之前的堆疊寫址；列舉所有 byte 計數及容量，驗登記的名義目的範圍。上表子函式另見各自的指令驗證。

```python
from hashlib import sha256
from pathlib import Path
import sys
def ck(v):
    if not v: raise ValueError('clock load bridge mismatch')
a,b=(Path(p).read_bytes() for p in sys.argv[1:]);ck([sha256(x).hexdigest() for x in (a,b)]==['0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667','133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22'])
def rd(buf,i,n):return int.from_bytes(buf[i:i+n],'little')
ck(a[0x11bc4:0x11bce].hex()=='b7070400fc5b0a858297' and rd(b,0x74,4)==0x43f46)
ck(b[0x3f46:0x3f4a].hex()=='011122cc');u,i,h=rd(b,0x3f4a,4),rd(b,0x3f4e,4),rd(b,0x3f52,2)
ck(u&4095==0x437 and i&0xfffff==0x40793 and h&0xe003==0x4000 and (8+(h>>7&7),8+(h>>2&7))==(15,15))
slot=(u&~4095)+(i>>20)+((h>>10&7)*8+(h>>6&1)*4+(h>>5&1)*64);ck(slot==0x2000321c)
C=0x2000ff90;save=rd(b,0x3f48,2);ck(save&0xe003==0xc002 and (save>>2&31)==8 and C-32+4*(save>>9&15)+64*(save>>7&3)==C-8)
ck(b[0x3c5a:0x3c5e].hex()=='63ffd700' and b[0x3c6a:0x3c74].hex()=='10b313972700369708c3');accepted=0
for n in range(256):
    for cap in range(256):
        writes=[(0x20004184,1),(C-8,4)]
        if n<cap:accepted+=1;writes.extend([(0x2000319d,1),(0x200047f4+4*n,4)])
        ck(all(p+w<=slot or slot+4<=p for p,w in writes))
ck(accepted==32640);print('PASS: 65536 registration pairs; pre-load save C-8; live load at 0x43f52 = cfg+48')
```
