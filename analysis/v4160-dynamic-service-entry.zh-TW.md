# 動態列數入口：可從服務表找到，但尚未找到啟動期呼叫者

V1.31 參考 SDK 的 `GGS_AddService(uint32_t services)` 是索引 71：`0x40034+71*4=0x40150`。該表項指向 `0x497f0`，不是最後分配 handle 的 `0x4cf22`。固定四列的 `GATTServApp_AddService` 是另一項（索引 64，`0x40134 → 0x4cf96`）。原 APP 在 `0x8fcc` 用的是第三個表項 `0x40130`。

動態入口的兩個早退條件：傳入 a0 為零，或按 Xwchc 解讀的 byte `[0x20002f5a]` 非零，都直接到 `0x49b8e` 返回 0，不進 `0x49b84`。否則 `0x49808` 先寫旗標 1，再組裝屬性列；`0x49b76..84` 以 a1 為列數、a2=16、a0=`a6+36` 尾跳 `0x4cf22`。旗標先寫，所以旗標為 1 不能證明 handle 已分配成功。

從入口反查：對原 APP 76,800 bytes、參考主區 191,078 bytes、按啟動搬移推得的 RAM 11,892 bytes，逐半字搜尋 `JAL`、`C.J`、`C.JAL`、相鄰同基底 `AUIPC/JALR`。兩個入口皆無這些直接轉移編碼；兩個入口的 32-bit 小端常數各只在對應的參考服務表項出現。原 APP 也未見標準 LW 立即數 0x150 或 0x134。這不是完整 caller 清單：分開取址、載入服務表後的間接呼叫、跳到函式內部、不同 resident 都不在排除範圍。不能據此把 APP 四列定為 1..4。

離線驗證：從 repo 根目錄執行以下 Python，參數依序為原 APP 與 V1.31 主區。`analysis/check_v131_descriptor_edges.py` 提供已測的編碼掃描器。

```python
from hashlib import sha256
from pathlib import Path
import sys
sys.path.insert(0,'analysis')
from check_v131_descriptor_edges import edges
a,r=[Path(p).read_bytes() for p in sys.argv[1:]]
def need(x):
    if not x: raise ValueError('dynamic entry evidence')
need([sha256(x).hexdigest() for x in (a,r)]==['0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667','133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22'])
need(r[0x97f0:0x980a].hex()=='630f0538b73700209387a7f598236318073885463738002094a3' and r[0x9b8e:0x9b92].hex()=='01458280')
need(edges(r[0x9b84:0x9b88],0x49b84,0x4cf22)==[('0x49b84','JAL',0)])
for base,b in [(0x8000,a),(0x40000,r),(0x20000000,r[0x270:0x2b0+2957*4])]:
    for t,s in [(0x497f0,71),(0x4cf96,64)]:
        need(not edges(b,base,t))
        hits=[base+i for i in range(0,len(b)-3,2) if b[i:i+4]==t.to_bytes(4,'little')]
        need(hits==([0x40034+4*s] if base==0x40000 else []))
need(not any((int.from_bytes(a[i:i+4],'little')&0xfff0707f) in (0x15002003,0x13402003) for i in range(0,len(a)-3,2)))
print('PASS: 2 service entries, 3 mapped ranges, tail control, APP LW census')
```
