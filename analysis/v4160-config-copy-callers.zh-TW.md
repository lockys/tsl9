# 誰把設定傳給 64-byte 複製入口？

原 APP 有一條可辨識的啟動鏈：`0x8ea8` 直接呼叫 `0x199e2`；`0x19ae2` 設 `a5=0x40000`，`0x19ae6` 讀 `a5=[a5+164]`，`0x19aea` 設 `a0=sp+16`，`0x19aec` 間接呼叫 a5。在 V1.31 參考表中槽 `0x400a4` 的值為 `0x43c7e`。通過既有[入口檢查](v4160-cfg-source-stack-bound.zh-TW.md)且正常複製，才會將這份設定的 +52 複製到 `0x20003220`。此呼叫來源的該欄位[初值是零](v4160-allocator-failure-slot-origin.zh-TW.md)。

針對「初始化後是否又傳了另一份設定」做三項交叉檢查：

- 在原 APP、參考 ROM 及其啟動 RAM 映射，掃描 JAL、C.J、C.JAL 與相鄰 AUIPC/JALR；到 APP 包裝函式的命中只有 `0x8ea8`，到 resident 入口則均為零。
- 原 APP 每個半字位置掃標準 `LW rd,164(rs1)`，不限制暫存器。唯一命中是上述 `0x19ae6`；這不涵蓋先算出槽址再用不同位移載入。
- 三區逐 byte 找小端 32-bit 指標常數。`0x43c7e` 僅在參考表 `0x400a4` 出現，沒有 `0x199e2` 或 `0x400a4` 的常數。RAM 映射與 ROM 重疊，不是獨立證據。

因此目前沒有辨識出第二個設定來源。**單一呼叫位置不等於只執行一次**：這沒有排除呼叫者重入、間接呼叫、跳到函式中段或由其他複製途徑寫入。也未證實機安裝該 ROM。

重現：從 repository 根目錄以原 APP、V1.31 carrier 為參數執行下列 Python，使用同目錄已發表的直接轉移解碼器。

```python
from pathlib import Path
from hashlib import sha256
from runpy import run_path
import sys
edges=run_path('analysis/check_v131_descriptor_edges.py')['edges']
a,b=(Path(p).read_bytes() for p in sys.argv[1:])
def ck(v):
    if not v: raise ValueError('config copy caller mismatch')
ck(sha256(a).hexdigest()=='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667' and sha256(b).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22')
ck(a[0x11ae2:0x11aee].hex()=='b707040083a7470a08088297')
ck([i+0x8000 for i in range(0,len(a)-3,2) if int.from_bytes(a[i:i+4],'little')&0xfff0707f==0x0a402003]==[0x19ae6])
for base,data in [(0x8000,a),(0x40000,b),(0x20000000,b[0x270:0x2b0+2957*4])]:
    ck(edges(data,base,0x199e2)==([('0x8ea8','JAL',1)] if base==0x8000 else [])); ck(not edges(data,base,0x43c7e))
    for t in (0x199e2,0x43c7e,0x400a4):
        needle=t.to_bytes(4,'little'); hits=[base+i for i in range(len(data)-3) if data.startswith(needle,i)]
        ck(hits==([0x400a4] if (base,t)==(0x40000,0x43c7e) else []))
print('PASS: one wrapper edge, one APP LW +164, one reference table word; no second source identified')
```
