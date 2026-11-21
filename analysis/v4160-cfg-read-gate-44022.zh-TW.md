# `0x44022`：三個欄位都非零才呼叫讀取函式

接續[第一次配置入口](v4160-role-first-allocation-prefix.zh-TW.md)。配置成功的路徑從 `0x43c04` 呼叫 `0x44022`。原 APP 以 `sp+16` 為設定起點；若正常複製至 V1.31 參考 ROM 使用的 `0x200031ec`，且這三個欄位到使用前未改變：

| 設定位移 | 原 APP 指定值 | 參考 ROM 的用途 |
|---|---:|---|
| +8 | `0x08077c00` | `0x4402e` 載入 a0；非零才繼續 |
| +56 | `0x1979a` | `0x4404a` 載入 a5；非零才繼續，也是實際呼叫目標 |
| +60 | `0x197be` | `0x4404e` 載入 a4；非零才繼續，**此處不呼叫它** |

任一為零即返回 1。三者非零時，`0x44056` 呼叫 `0x1979a(0x08077c00,1,frame_sp+12)`。原 APP `0x1979a..0x197b6` 將參數重新排列，把長度乘四，透過 `[0x4004c]` 請求將 **4 bytes 從 `0x08077c00` 複製到呼叫者堆疊**，正常返回後回傳 0。這不是要求寫入非揮發儲存。`0x44058..0x4405c` 比較的是重新載入的設定 +8 和堆疊取回的 word，不是回傳碼；相等才直接走返回 1 的路徑。若 provider 僅寫指定目的範圍且堆疊與設定分離，複製不會碰失敗回呼 `0x20003220`。APP BIN 沒有提供來源 word 的現場內容，故無法據此選定比較結果或證明實機抵達。

以下以原 APP、參考 carrier 路徑為兩個參數。從 APP 指令恢復三個輸入，從三條壓縮分支解出比較暫存器、方向及目的地，檢查八種零／非零組合；另以固定指令核對呼叫邊界，不模擬 provider。

```python
from pathlib import Path
from hashlib import sha256
from itertools import product
import sys
a,b=(Path(f).read_bytes() for f in sys.argv[1:])
def need(x):
    if not x: raise ValueError('evidence mismatch')
need(sha256(a).hexdigest()=='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667')
need(sha256(b).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22')
def word(p): return int.from_bytes(a[p-0x8000:p-0x8000+4],'little')
def half(p): return int.from_bytes(b[p-0x40000:p-0x40000+2],'little')
def sx(x,n): return (x^(1<<(n-1)))-(1<<(n-1))
vals=[]
for p,op,reg,off in [(0x19a4a,0x37,15,24),(0x19a76,0x17,14,72),(0x19a80,0x17,14,76)]:
    u,v,h=word(p),word(p+4),word(p+8)&65535
    need(u&4095==reg*128+op and v&0xfffff==(reg<<15)+(reg<<7)+19)
    need(h&0xe003==0xc002 and (h>>2&31)==reg and 4*(h>>9&15)+64*(h>>7&3)==off)
    vals.append(((u&~4095)+(p if op==0x17 else 0)+sx(v>>20,12))&0xffffffff)
need(vals==[0x08077c00,0x1979a,0x197be])
branches={}
for p,r in [(0x44036,10),(0x4404c,15),(0x44050,14)]:
    h=half(p); f=h>>13; need(h&3==1 and f in (6,7) and 8+(h>>7&7)==r)
    d=((h>>12&1)<<8)|((h>>10&3)<<3)|((h>>5&3)<<6)|((h>>3&3)<<1)|((h>>2&1)<<5)
    branches[p]=(f,p+sx(d,9))
for vs in product(*[(0,v) for v in vals]):
    pc=0x44036
    for p,v in zip(branches,vs):
        f,t=branches[p]; need(pc==p)
        pc=t if (v!=0)==(f==7) else p+2
        if pc==0x44038: break
        pc={0x44046:0x4404c,0x4404e:0x44050,0x44052:0x44056}[pc]
    need(pc==(0x44056 if all(vs) else 0x44038))
need(b[0x4052:0x4060].hex()=='7000854582971844b247e30ef7fc')
need(a[0x1179a:0x117b8].hex()=='b7070400fc474111328706c613962500aa853a858297b240014541018280')
print('PASS: 3 APP fields; 8 gate combinations; read wrapper and result comparison pinned')
```
