# APP 自訂服務註冊之前：三個回呼位址的去向

從第三個角色入口正常返回的 `0x8ec4` 追到 `0x8fcc`。在這段原 APP 指令中，間接呼叫用到的服務偏移依序為 `80,174,174,174,154,154,[154],168,c4,80,80,138,130`（十六進位，方括號可略過）；另有 `0x8f30` 直接呼叫 `0x8b6e`，它使用 `0x174`。若 s0 保持或被重新設為 `0x40000`、服務表未變，這些呼叫點沒有直接選 `0x40134` 的固定四列入口。最後的 `0x40130` 是 APP 自己的註冊。動態列數的 `0x49b84` 尾跳在參考 resident 內，不能僅靠 APP 的偏移清單排除。

特別容易混淆的是 `0x8f7c` 經 `0x400c4` 進 V1.31 參考函式 `0x4b20a`。在完成逐列初始化的路徑上，有三個連續的直接呼叫：

| 呼叫點 | 傳入的函式位址 | 被呼叫者實際做的事 |
|---|---|---|
| `0x4b27e` | `0x4b030` | `0x4a1ec` 寫入 `0x20002f6c` 後返回 |
| `0x4b28a` | `0x4aaea` | `0x4468a` 寫入 `0x20002f00` 後返回 |
| `0x4b296` | `0x4abcc` | `0x4efe2` 在 `0x20003358` 的 12 個 word 中找第一個零，存入位址；全滿返回 19，不寫入 |

三個呼叫都不執行傳入的函式，不是三次服務 handle 分配。`0x4b29a` 另設返回值 0，並不傳回第三次登記結果。這只排除所列呼叫點；配置器、其他服務的內層路徑與非同步回呼不在排除範圍內。尚無實機 handle 值。

離線複核：以原 APP 和 V1.31 主 carrier 為參數。

```python
from hashlib import sha256
from pathlib import Path
import sys
a,r=map(lambda p:Path(p).read_bytes(),sys.argv[1:])
def check(ok):
    if not ok: raise ValueError('pre-registration evidence mismatch')
check([sha256(b).hexdigest() for b in (a,r)]==['0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667','133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22'])
def u(b,i,n=4): return int.from_bytes(b[i:i+n],'little')
i=0xec4; slot=None; calls=[]
while i<0xfce:
    n=4 if a[i]&3==3 else 2; w=u(a,i,n)
    if n==4 and w&0xfffff==0x42783: slot=w>>20
    if w==0x9782: calls.append((i+0x8000,slot)); slot=None
    i+=n
check(calls==list(zip([0x8ed0,0x8ef6,0x8f04,0x8f14,0x8f20,0x8f2c,0x8f5c,0x8f74,0x8f7c,0x8f8a,0x8fa0,0x8fb6,0x8fcc],[128,372,372,372,340,340,340,360,196,128,128,312,304])))
check(u(r,196)==0x4b20a and a[0xb74:0xb7c].hex()=='b707040083a74717')
for i,cb,dst in [(0xb27e,0x4b030,0x4a1ec),(0xb28a,0x4aaea,0x4468a),(0xb296,0x4abcc,0x4efe2)]:
    hi,lo,w=(u(r,i+k) for k in (-8,-4,0)); check(hi&4095==0x537 and lo&0xfffff==0x50513 and (hi&~4095)+(lo>>20)-(4096 if lo>>31 else 0)==cb)
    j=(w>>31<<20)|(w&0xff000)|((w>>20&1)<<11)|((w>>21&1023)<<1); check(w&4095==0xef and 0x40000+i+j-((j>>20)<<21)==dst)
check(r[0xa1ec:0xa1f6].hex()=='b737002023a6a7f68280' and r[0x468a:0x4694].hex()=='b737002023a0a7f08280' and r[0xb29a:0xb29c].hex()=='0145')
print('PASS: 13 APP call sites; 3 callback arguments and direct targets')
```
