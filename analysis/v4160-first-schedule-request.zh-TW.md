# 首次排程要求：哪些情況才會建立新節點？

接續[task ID 保存條件](v4160-task-clock-copy16.zh-TW.md)。若 APP 成功登記且沿用 ID 3，`0x19b54` 尾跳時的參數是 `(3,0x2000,192000)`。以下是 V1.31 參考槽 `[0x40058] → 0x43728` 的條件分析，不是裝置執行記錄。

1. `0x43754` 要求 **ID < 已登記數量**，`0x43760` 還要求時鐘回呼非零。任一失敗都恢復外設 word、返回 0，不查表。先前三個內部 handler 加上第一個 APP handler 給出數量 4；成功設定時時鐘槽為 `0x191c6`。這兩個值都必須保持到讀取時。
2. `0x4378a..437aa` 計算 `(16000 × 192000 + 800) // 1600 = 1920000`。名義上限是 `(0xffffffff - 30000000) mod 2^32 = 4264967295`，故通過。`0x437ca` 才讀時鐘；返回後**再讀一次**設定半字並重算，不能用第一次計算替代第二次。若設定不變，寫入期限為 `(tick + 1920000) mod 0xffffffff`，不是一般的 32-bit 截斷。例：`tick=0xffe2b3ff` 得 0，下一個 tick 得 1。這是計數值，未推定物理時間單位。
3. 查找 `0x20000314(3,0x2000)` 在所選映射內由 `[0x200031e8]` 起，按 **event 半字 +2、ID byte +0** 比對，以 `+12` 找下一筆。若命中，`0x43812` 只更新該節點 `+8` 的期限，返回 1，**沒有建立新節點**。
4. 未命中才要求 `0x20000040(16,0xff03)`。若配置返回零，可能呼叫錯誤回呼，正常返回後仍回 0；若成功，在空表設 head，非空表則走到尾端接上節點，再填 ID=3、旗標=1、event=8192、期限及清零欄位，返回 1。兩種成功共用返回點，**返回 1 本身不能區分更新或新增**。遍歷、外設讀取與回呼都不能預設一定結束。

核對方式：以下傳入 V1.31 carrier。核對固定指令、兩次相對呼叫、查找欄位與期限分支；以門檻兩側及均勻間隔的合成 tick 比較數學模型。不假設初始表為空，也不把測試當成完整 CPU 執行。

```python
from hashlib import sha256
from pathlib import Path
import sys
b=Path(sys.argv[1]).read_bytes(); M=0xffffffff
def ck(x):
    if not x: raise ValueError('first schedule evidence mismatch')
ck(sha256(b).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22')
def raw(p,n): return b[p-0x40000:p-0x40000+n]
def w(p): return int.from_bytes(raw(p,4),'little')
def imm(p): return int.from_bytes(raw(p,4),'little',signed=True)>>20
def pair(p): return (p+(w(p)&0xfffff000)+imm(p+4))&0xfffffffe
ck(int.from_bytes(b[88:92],'little')==0x43728 and raw(0x43750,8).hex()=='83c7d7196378f500')
ck(raw(0x4375c,8).hex()=='83ab071e63970b00' and raw(0x437ca,6).hex()=='829b83558900')
limit=(M+(w(0x43780)&0xfffff000)+imm(0x43784))&M
q=(16000*192000+imm(0x43798))//imm(0x437a0); ck(q==1920000<limit==4264967295)
ck(raw(0x437ee,22).hex()=='b3079500be840327490063e4a70063e4e700b384e740')
samples={0,M,M-q-1,M-q,M-q+1,M-q+2,*range(0,M,65537)}
for t in samples:
    u=(t+q)&M; due=(u-M)&M if u<q or u>=M else u
    ck(due==(t+q)%M)
ck(pair(0x43808)==0x20000314 and pair(0x4382a)==0x20000040)
ck(raw(0x40584,30).hex()=='b737002083a7871e99e33e858280ba236315b7009823e30aa7fedc47f5b7')
ck(raw(0x43810,16).hex()=='01c904c5b747024023a64721054559bf')
ck(raw(0x43850,26).hex()=='2324a71e85472326050004c52311550100a11cb12322050075b7')
ck(raw(0x4386c,8).hex()=='d84775ffc8c7cdb7' and (3|0xff00)==0xff03)
print(f'PASS: ID 3 < 4; delta {q}; {len(samples)} deadline checks; distinct update and allocate paths')
```
