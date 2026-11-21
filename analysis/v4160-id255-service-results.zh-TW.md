# 登記失敗後，四個服務如何處理 ID 255？

沿用 [APP 四處讀取](v4160-gp166-result-consumers.zh-TW.md)與[登記條件](v4160-registration-gp166.zh-TW.md)。以下是 V1.31 參考映射，不是裝置紀錄。`0x2000319d` 是一個 byte，因此 ID 255 不可能小於當前任務數，即使數量也是 255。

|服務槽 → 入口|收到 255、正常返回時的行為|APP 看見的結果|
|---|---|---|
|`40050 → 4354a`|`43562` 跳過 pending 表的讀改寫，恢復外設控制字後回傳 3。|快速路徑尾跳，傳回 3；APP 先前已填記錄。|
|`40058 → 43728`|`43754` 直接去 `43764`，不讀 clock 指標、不配置 timer；恢復控制字與 stack，回傳 0。|`9230` 的 `seqz` 把 0 轉為 1。|
|`4022c → 43932`|`43954` 呼叫上一列，但不以回傳值決策；重載原 ID 和遮罩，查找既有節點。未找到回傳 1；找到並完成運算則寫節點 +4，回傳 0。|非零模式尾跳，傳回 1 或 0。|
|`4005c → 439a8`|先查節點，命中時清節點 +2 的半字；內層 `4358a` 的數量檢查返回 3，但外層不傳回它。若目前任務 byte `0x2000319c` 等於 255，另將遮罩 OR 進 `0x200031dc` 半字。|尾跳；查找未命中回傳 6，命中回傳 0。APP 在進入服務前已清記錄的兩個 word。|

「直接拒絕」不等於無寫入：前兩個服務都先保存並暫清 `0x4002420c`，之後才恢復。後兩個服務的查找是同一 RAM 入口 `0x20000314`；在參考程式已複製且採 Xwchc 解讀時，以事件與 ID 配對。未證明曾有 ID 255 的節點，或當時任務 byte 就是 255。以上假設表與 stack 有效、子呼叫正常返回且保存需要的狀態。

重現（參數為 V1.31 carrier）：比對槽位、解出三個 unsigned branch 的目標與寄存器，測所有 byte count；另比對兩個 wrapper 的回傳處理與查找目的。非整機執行。

```python
from hashlib import sha256
from pathlib import Path
import sys
b=Path(sys.argv[1]).read_bytes()
def ck(v):
    if not v: raise ValueError('service evidence mismatch')
ck(sha256(b).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22')
def w(p):return int.from_bytes(b[p-0x40000:p-0x40000+4],'little')
def raw(p,h):
    v=bytes.fromhex(h);ck(b[p-0x40000:p-0x40000+len(v)]==v)
ck([w(p) for p in (0x40050,0x40058,0x4022c,0x4005c)]==[0x4354a,0x43728,0x43932,0x439a8])
for pc,target,r in [(0x43562,0x43582,14),(0x43754,0x43764,15),(0x435a2,0x435c6,14)]:
    x=w(pc);d=(x>>31<<12)|(x>>7&1)<<11|(x>>25&63)<<5|(x>>8&15)<<1
    ck(x&0x707f==0x7063 and pc+(d^4096)-4096==target);rs=x>>15&31;rt=x>>20&31
    for n in range(256):
        regs={10:255,r:n};ck(regs[rs]>=regs[rt] and (rs,rt)==(10,r))
for pc in (0x4395a,0x439c8):
    hi=w(pc);lo=w(pc+4);ck(hi&4095==0x97 and lo&0xfffff==0x80e7 and (pc+(hi&0xfffff000)+((lo>>20^2048)-2048))&0xfffffffe==0x20000314)
raw(0x43582,'23a6d7200d458280');raw(0x43768,'23a6472199a0');raw(0x437b2,'0145');raw(0x43954,'d13b2285ce85');raw(0x4398a,'48c013351400');raw(0x439d2,'19c123110500a2854a857d36');raw(0x439f2,'598c239e871c');raw(0x43a00,'014591e01945')
print('PASS: 4 slots; 3 x 256 invalid-ID comparisons; 2 lookup targets; selected return/write sites')
```
