# 從取樣返回到第一次配置：失敗回呼槽是否被寫入？

對象是與 v4.1.60 APP 比對使用的 **V1.31 參考 ROM**，不是裝置 ROM 快照。接續 [APP 取樣函式](v4160-cfg44-callback-write-set.zh-TW.md)，這次把終點設在 `0x43bbe` 發起第一次配置之前，不預設配置成功。

| 路段 | 對 RAM 的作用 |
|---|---|
| `0x43d3a..0x43d4c` | 把取樣返回值低半字寫到 `0x200031a4`，把 `0xff` 寫到 `0x200035f5`，再呼叫 `0x43b3e`。後者不是失敗回呼。 |
| `0x43b3e..0x43b88` | 三個 word 清零位置依序為 `0x200031e8`、`0x20003230`、`0x200031e0`；另保存三個暫存器到 stack。兩次呼叫同一個 `0x2000039c`，要求清零 `[0x200031c8,0x200031dc)` 與 `[0x2000319c,0x200031c4)`。`0x20003230` 與失敗回呼 `0x20003220` 是不同 word。 |
| `0x43104` 子呼叫 | 在 APP 提供基址 `0x2000418c`、長度 `0x7000` 時，兩個 heap header 位於 `0x200043ac`、`0x200045ac`。三個固定 cursor word 在 `0x2000318c..0x20003197`；`0x4316c` 寫半字到 `0x200031a2`。`0x430e0` 走訪串列，只讀。 |
| `0x43b8c..0x43bbe` | 讀 `0x20003201` 的 byte `c`，計算 `k=(14+3*((c>>2)+(c&3)))&255`。在 Xwchc 解讀下 `0x43bb4` 將 `k` 寫回以 `0x2000319c` 為基址的 byte 欄位；其後請求 `576+6*k` bytes，不把 `k` 寫入設定 +52。 |

因此，若入口時 `[0x20003220]` 為零、stack 分離、參考填值函式按指定長度返回、heap 初始化使用上述設定，且沒有非同步寫入，這個 word **到第一次配置入口仍為零**。這不涵蓋配置器返回後的 `0x44022` 或真正的裝置行為。

下列檢查以 carrier 路徑為參數，從指令解出固定 store 和兩次填值呼叫的實參。它不執行被呼叫函式。

```python
from hashlib import sha256
from pathlib import Path
import sys
b=Path(sys.argv[1]).read_bytes()
def need(ok):
    if not ok: raise ValueError('reference mismatch')
need(sha256(b).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22')
def ins(p,n=4): return int.from_bytes(b[p-0x40000:p-0x40000+n],'little')
def sx(v,n): return (v^(1<<(n-1)))-(1<<(n-1))
base=0x20003000; slot=base+0x220
rows=[]
for p in (0x43d3e,0x43d48,0x43b42,0x43b50,0x43b62):
    w=ins(p); need(w&127==35 and (w>>15)&31==15)
    rows.append((base+sx((w>>25)*32+(w>>7&31),12),1<<(w>>12&7)))
need(rows==[(base+420,2),(base+1525,1),(base+488,4),(base+560,4),(base+480,4)])
for p in (0x43b6e,0x43b80):
    u,j=ins(p),ins(p+4); need(u&4095==151 and j&0xfffff==0x80e7 and (p+(u&~4095)+sx(j>>20,12))&0xffffffff==0x2000039c)
need(ins(0x43b54,2)==0x4651 and ins(0x43b7a)==0x02800613)
ranges=[(base+(ins(p)>>20),n) for p,n in [(0x43b5c,20),(0x43b76,40)]]
need(ranges==[(base+456,20),(base+412,40)])
need(all(a+n<=slot or slot+4<=a for a,n in rows+ranges))
print('PASS: 5 fixed stores; 2 zero-fill requests to the same helper; all 7 ranges exclude cfg+52')
```
