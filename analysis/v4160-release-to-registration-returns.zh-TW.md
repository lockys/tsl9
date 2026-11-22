# 釋放返回到首次 APP 登記：四個返回位址

以 `0x199e2` 入口 SP 為 E。將[配置釋放的寫址](v4160-release-header-footprint.zh-TW.md)接上[既有 frame 大小](v4160-cfg60-init-stack.zh-TW.md)和[首次 APP 登記](v4160-first-app-registration-order.zh-TW.md)。若釋放正常返回到 `0x440a0`、保存區未變且各層恢復 SP，四個仍存活的呼叫依下列順序返回。這裡比對的是每一對真正的 `swsp ra` / `lwsp ra`，不是只看反組譯中出現 `ret`。

|函式|保存 / 取回 PC|同一個 word|預期續行 PC|
|---|---|---|---|
|參考 `44022`|44030 / 4403a|E−132|43c06|
|參考 `43b3e`|43b60 / 43c44|E−116|43d4e|
|參考 `43c7e`|43ca2 / 43d50|E−100|19aee|
|APP `199e2`|199f8 / 19b04|E−4|8eac|

前三次返回之間不需再呼叫 provider：`440a2/440a6` 清兩個 word；`43c06` 起重讀計數與表指標，依序寫三個內部 handler；`43d4e` 起直接返回零。第四次返回前還有 `19af8 → 19106(64,1)`，這條分支是直接 MMIO 讀改寫，不是未知 handler。接著 `8eac → 19b16`，到 `19b2e` 才經表槽 `40080` 呼叫，這是登記而非執行 APP handler。

尚未由此證實：設備安裝的 resident 是否同 V1.31、上游間接呼叫是否正常返回、保存區或表是否被中斷改寫、MMIO 是否成功。下列檢查不模擬整機；四個續行 PC 由呼叫位置及指令寬度取得，間接目標沿用先前的條件綁定。

```python
from hashlib import sha256
from pathlib import Path
import sys
a,b=(Path(x).read_bytes() for x in sys.argv[1:])
def ck(v):
    if not v: raise ValueError('return chain mismatch')
ck(sha256(a).hexdigest()=='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667' and sha256(b).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22')
def h(p):
    x,k=(b,0x40000) if p>=0x40000 else (a,0x8000)
    return int.from_bytes(x[p-k:p-k+2],'little')
for save,load,depth,slot,call,ret,opcode in [(0x44030,0x4403a,160,132,0x43c04,0x43c06,0x2939),(0x43b60,0x43c44,128,116,0x43d4c,0x43d4e,0x3bcd),(0x43ca2,0x43d50,112,100,0x19aec,0x19aee,0x9782),(0x199f8,0x19b04,96,4,0x8ea8,0x8eac,0x00ef)]:
    s,l=h(save),h(load); ck(s&0xe07f==0xc006 and l&0xef83==0x4082)
    so=((s>>9&15)<<2)|((s>>7&3)<<6); lo=((l>>4&7)<<2)|((l>>12&1)<<5)|((l>>2&3)<<6)
    ck(so==lo==depth-slot and h(call)==opcode and call+(4 if opcode&3==3 else 2)==ret)
print('PASS: four paired RA slots and four return PCs')
```
