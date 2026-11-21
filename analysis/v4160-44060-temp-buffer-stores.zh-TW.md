# `0x44060..0x440c2`：暫存緩衝區與失敗回呼槽

接續 [讀取比較](v4160-cfg-read-gate-44022.zh-TW.md)。本次只審 V1.31 參考 ROM 中「讀回值不相等」分支的 RAM 寫址；既有 [caller 契約](v4160-nv-call-contract-2026-10-22/caller-review/readme.zh-TW.md) 已分析回呼參數，不把那部分重算為新覆蓋。

| 機碼位置 | 寫入及條件 |
|---|---|
| `0x4406a`、`0x44076` | 要求配置 `u16(cfg+12)` bytes，把返回指標 **P** 寫入 `0x200031bc`。即使配置失敗也先寫零，然後返回 1，不進入填值或迴圈。 |
| `0x4407e..0x4408a` | 成功才重新讀取長度，以 `0xff` 要求填入 P 開始的範圍。長度是第二次載入；需設定未變才能沿用配置大小。 |
| `0x4408e..0x440c0` | 每次比較都重新讀取 `cfg+14` 的 byte 與 `0x200031bc` 的指標。繼續時，`0x440bc` 在**這次載入的指標 +0** 寫一個 word，再呼叫 `cfg+60`；迴圈沒有把 P 每輪加四。 |
| `0x44096..0x440aa` | 退出時把最後一次載入的指標交給釋放函式。正常返回並保留 s1 時，將 `0x200031bc` 和 `0x200031c0` 各清一個 word，返回 0。 |

依原 APP 設定及參考預設值，長度 256、次數 3。若配置返回有效的 256-byte arena 物件、後續長度不變、回呼未改寫指標或迴圈狀態，則填值及三次 word store 都在同一個物件內，不會碰到 `cfg+52`（`0x20003220`）。兩個固定全域 word 也不重疊該槽。這只排除本體直接寫入和指定長度的填值；不等於已證配置器、釋放函式、回呼及外設的所有副作用，也不假定實機一定執行三輪。

重現：以 V1.31 carrier 為唯一參數。核對這段的四個 store 指令位置（Xwchc 四條窄載入另行辨認）、間接 helper 位址及 RAM 範圍；不是執行 CPU。

```python
from hashlib import sha256
from pathlib import Path
import sys
b=Path(sys.argv[1]).read_bytes()
def need(x):
    if not x: raise ValueError('reference mismatch')
need(sha256(b).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22')
def rd(p,n): return int.from_bytes(b[p-0x40000:p-0x40000+n],'little')
p=0x44060; stores=[]; narrow=[]
while p<0x440c2:
    h=rd(p,2); q=h&3; f=h>>13
    if q==3:
        w=rd(p,4)
        if w&127==35:
            need(w>>12&7==2); stores.append((p,w>>15&31,(w>>25)*32+(w>>7&31),w>>20&31))
        p+=4
    else:
        if f==6 and q==0: stores.append((p,8+(h>>7&7),((h>>10&7)<<3)+((h>>5&1)<<6)+((h>>6&1)<<2),8+(h>>2&7)))
        elif f==1 and q in (0,2): narrow.append((p,h))
        else: need(not (q in (0,2) and f in (5,6,7)))
        p+=2
need(p==0x440c2 and stores==[(0x44076,14,32,10),(0x440a2,9,32,0),(0x440a6,9,36,0),(0x440bc,12,0,10)])
need(narrow==[(0x44060,0x244a),(0x4407e,0x2452),(0x4408e,0x247c),(0x440ac,0x244e)])
for pc,t in [(0x4406a,0x20000040),(0x44086,0x2000039c),(0x44098,0x20000110)]:
    u,j=rd(pc,4),rd(pc+4,4); need(u&4095==151 and j&0xfffff==0x80e7)
    need((pc+(u&~4095)+((j>>20^2048)-2048))&0xffffffff==t)
slot=0x20003220
def disjoint(a,n): return a+n<=slot or slot+4<=a
need(all(disjoint(0x2000319c+o,4) for o in (32,36)))
starts=range(0x200043b4,0x2000b184-256+1,4)
need(len(starts)>0 and all(disjoint(a,256) and disjoint(a,4) for a in starts))
print(f'PASS: 4 store sites, 3 helper targets, {len(starts)} aligned in-arena 256-byte placements disjoint from cfg+52')
```
