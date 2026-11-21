# 第二個 APP 登記：`gp+166` 是 4 還是 255？

原 APP 的 `0x90a2` 用 `0x901a` 作參數呼叫 `[0x40080]`。若槽綁定 V1.31 的 `0x43c4e`，並按 Xwchc 解讀，`0x43c56/58` 依序讀 `0x2000319d` 的計數 n 與 `0x2000319e` 的容量 c。若 **n < c**，先存 `n+1` 到計數，再把 handler 寫到 `T+4*n`，回傳舊 n；否則不讀表基址、不改表與計數，回傳 255。APP 正常續行時一律將結果低 byte 存 `gp+166`，沒有替 255 提供預設值。成功 ID 最大 254。

名義初始化先完成三筆內部登記，第一個 APP handler `0x1995c` 得到 3，計數才成為 4。若到本次讀取前沒有其他登記或改寫，沿用設定 byte 14 所得容量 `14+3*((14>>2)+(14&3))=29`，且 `T=0x200047f4`、表可寫，則得到 **ID 4**：計數變 5，`[0x20004804]` 寫 `0x901a`。這不依賴前一個排程回傳 1，只要求執行到此且相關狀態保持。容量若正好是 4 也算滿；即使先前有其他登記，也要用本次 n 比較，不能沿用 4。未確認裝置 resident 或實際執行。

重現：以 decoded APP、V1.31 carrier 為參數。固定 APP 呼叫/寫回及候選函式 bytes，從分支解出條件、寄存器、目的 PC，再對全部 byte 配對測比較方向和臨界值；不是完整指令模擬。

```python
from hashlib import sha256
from pathlib import Path
import sys
a,b=(Path(s).read_bytes() for s in sys.argv[1:])
def ck(v):
    if not v: raise ValueError('registration evidence mismatch')
ck([sha256(v).hexdigest() for v in (a,b)]==['0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667','133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22'])
ck(a[0x1096:0x10ac].hex()=='8327040817050000130505f88297b24022442383a10a' and int.from_bytes(b[128:132],'little')==0x43c4e)
ck(b[0x3c4e:0x3c7e].hex()=='373700201307c7191c33342363ffd700b736002083a6461c1386170010b313972700369708c33e8582809307f00fe5bf')
x=int.from_bytes(b[0x3c5a:0x3c5e],'little'); f=x>>12&7; r1=x>>15&31; r2=x>>20&31
imm=(x>>31<<12)|(x>>7&1)<<11|(x>>25&63)<<5|(x>>8&15)<<1
ck(x&127==99 and f==7 and 0x43c5a+(imm^4096)-4096==0x43c78)
passed=0
for n in range(256):
    for c in range(256):
        regs={13:c,15:n}; full=regs[r1]>=regs[r2]; result=255 if full else n
        ck((result!=255)==(n<c)); passed+=not full
ck(passed==32640 and 0x200047f4+4*4==0x20004804)
print('PASS: 65536 count/capacity pairs; 32640 success, 32896 full; nominal ID 4, slot 0x20004804')
```
