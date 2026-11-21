# 首次排程有兩次 head 讀取

V1.31 參考映像中，`0x43b42` 明確把 `0x200031e8` 整個 word 清零。若此值保持到首次排程查找，RAM helper `0x20000314`（carrier `0x40584`）只讀 head，走 `0x4058e` 將零移入 a0 並返回，不讀任何節點。`0x43810` 因而進入配置分支，而不是更新節點。這仍以[首次排程的前置檢查](v4160-first-schedule-request.zh-TW.md)通過為前提。

**配置成功後還要重新判斷表是否為空。** `0x4384a` 再讀同一個 word，沒有使用查找時的快照。若仍為零，`0x43850` 才將新指標寫進 head；若已非零，從重讀的 head 走到尾節點、寫其 `+12`，並非覆寫 head。不空也可能查無符合的 ID/event，因此「進入配置」「查找時為空」「安裝時為空」是三個不同命題。這裡沒有證明發生穿插寫入，也沒有用參考 ROM 代替實機。

核對：傳入 V1.31 carrier。從四條 load/store 的編碼獨立還原地址、寬度和暫存器；另核對零返回、分支及尾端寫入。負對照把第二次讀取的位移改為相鄰 word，必須不再等於 head。

```python
from pathlib import Path
from hashlib import sha256
import sys
b=Path(sys.argv[1]).read_bytes()
def ck(v):
    if not v: raise ValueError('timer head mismatch')
ck(sha256(b).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22')
def raw(p,n): return b[p-0x40000:p-0x40000+n]
def w(p): return int.from_bytes(raw(p,4),'little')
def access(l,x,store,reg):
    ck(l&127==55 and (l>>7&31)==(x>>15&31)); ck(x&0x707f==(0x2023 if store else 0x2003))
    ck((x>>(20 if store else 7)&31)==reg)
    i=(x>>25)*32+(x>>7&31) if store else x>>20
    return ((l&~4095)+(i^2048)-2048)&0xffffffff
head=0x200031e8
for l,p,s,r in [(0x43b3e,0x43b42,1,0),(0x40584,0x40588,0,15),(0x43846,0x4384a,0,15),(0x43846,0x43850,1,10)]:
    ck(access(w(l),w(p),s,r)==head)
ck(access(w(0x43846),w(0x4384a)+(4<<20),0,15)==head+4)
ck(raw(0x4058c,6).hex()=='99e33e858280' and raw(0x43810,4).hex()=='01c904c5')
ck(raw(0x4384e,2).hex()=='99ef' and raw(0x4386c,8).hex()=='d84775ffc8c7cdb7')
print('PASS: clear / lookup / reload / install use same word; adjacent-word control distinguished')
```
