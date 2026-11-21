# 重新排程驗的是 ID 範圍，不是 handler 身分

**同一事件有三個不同的 ID 來源：**派送器以目前索引呼叫 handler；`0x199bc` 排下一次時用 `0x199b8` 從 `gp+388` 重讀的 byte；未來派送又依當時的表項取 handler。要說「仍是 `0x1995c`」，需知道 byte 仍為原登記 ID、該 ID 仍有效、未來表項仍指向原函式。單靠排程成功無法證明。

原 APP 的 `0x19b30` 建立 `s0=gp+388`，`0x19b34` 間接經 s0 把登記返回值的低 byte 存進去。對整個 decoded APP 逐半字搜尋**一般 32-bit、以 gp 為基址**的整數存取，與 byte +388 重疊者只有兩個 `lbu`：`0x199b8`（事件 `0x2000`）、`0x199d8`（`0x4000`）。另只找到一個完全相等的 `addi rd,gp,388`，即上述登記位置。這是指令編碼盤點，不是全域唯一 writer 證明：那個已知 store 就不以 gp 當直接基址；其他指標、初始化清零、參考 ROM 和非同步寫入亦不在此掃描的保證內。

V1.31 參考槽 `[0x40058]` 的 `0x43754` 比較 `U8[0x2000319d]` 和輸入 ID；若 count ≤ ID 就返回 0。**通過時沒有再比較 handler 地址**，而是以 live ID 與事件查找計時節點。例如 count=4，讀回 4 會被拒，讀回 2 卻能過第一關；若之後成功，要求是給 ID 2，不是自動轉回 3。這是分支例子，未觀察到 ID 被改寫。

其他正常返回 0 的路徑包括時鐘回呼為零、首次換算的延遲超出限制、查無節點且配置失敗（錯誤回呼如有須返回）。[期限與配置細節](v4160-first-schedule-request.zh-TW.md)。不返回與返回 0 不同。只要排程呼叫正常返回且保存暫存器未變，APP 隨即用 `0x2000` 覆寫 a0，回傳原事件遮罩 XOR `0x2000`；**拒絕也不會讓這一位自動留下待重試**。其他來源仍可再次設位。

離線重現：Python 參數依序為 decoded APP、V1.31 carrier；掃描列出候選指令，另對全部 byte ID/count 配對解譯第一個分支。

```python
from pathlib import Path
from hashlib import sha256
import sys
a,b=[Path(p).read_bytes() for p in sys.argv[1:]]
def ck(v):
    if not v: raise ValueError('rearm identity mismatch')
ck([sha256(x).hexdigest() for x in (a,b)]==['0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667','133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22'])
hits=[]; addrs=[]
for i in range(0,len(a)-3,2):
    x=int.from_bytes(a[i:i+4],'little'); op=x&127; f=x>>12&7
    if x&0xfffff07f==0x18418013: addrs.append(i+32768)
    if x>>15&31!=3 or op not in (3,35): continue
    n=({0:1,1:2,2:4,4:1,5:2} if op==3 else {0:1,1:2,2:4}).get(f,0)
    d=x>>20 if op==3 else (x>>25<<5)|(x>>7&31); d=(d^2048)-2048
    if d<=388<d+n: hits.append((i+32768,op,f,d))
ck(hits==[(0x199b8,3,4,388),(0x199d8,3,4,388)] and addrs==[0x19b30])
ck(a[0x11b30:0x11b38].hex()=='138441182300a400' and a[0x119b8:0x119c2].hex()=='03c5411882970965c1b7')
x=int.from_bytes(b[0x3754:0x3758],'little'); ck(x==0x00f57863 and b[0x3750:0x3754].hex()=='83c7d719')
rs1=x>>15&31; rs2=x>>20&31; ck(x>>12&7==7)
for ident in range(256):
    for count in range(256):
        r={10:ident,15:count}; ck((r[rs1]>=r[rs2])==(ident>=count))
print('PASS: 2 direct loads; 1 exact address formation; 65536 ID/count pairs')
```
