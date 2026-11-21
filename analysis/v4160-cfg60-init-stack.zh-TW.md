# `cfg+60` 的三筆 stack store：從 `0x9008` 計算，而非直接沿用 reset SP

接續[回呼寫址清單](v4160-cfg60-heap-separation.zh-TW.md)。取 v4.1.60 APP 搭配 V1.31 參考 ROM，只分析初始化中抵達 `0x440be → 0x197be` 的那條路徑。令 `S` 為 **APP `0x9008` 入口的 SP**。下表是呼叫回呼時仍然存活的 frame，不是曾執行過的所有函式用量總和。先前已返回的函式須還原 SP；不把它們的 frame 疊加，也不假定中斷一定不存在。

| 所在函式 | 扣除 SP 的 PC | bytes | 此時 SP |
|---|---|---:|---|
| APP `9008` | `9008` | 16 | S−16 |
| APP `9250` | `9250` | 16 | S−32 |
| APP `8e88` | `8e88` | 32 | S−64 |
| APP `199e2` | `199e8` | 96 | S−160 |
| 參考 `43c7e` | `43c94` | 16 | S−176 |
| 參考 `43b3e` | `43b4e` | 16 | S−192 |
| 參考 `44022` | `44022` | 32 | S−224 |
| APP `197be` | `197be` | 32 | S−256 |

回呼本體三個 `swsp` 相對最後一列為 `+28/+24/+12`，即 `S−228 / S−232 / S−244`。**在既有條件式交接 `S=0x20010000` 下**，各寫 4 bytes 至 `0x2000ff1c / 0x2000ff18 / 0x2000ff0c`。它們全在名義堆積區上界 `0x2000b184` 以上，也不碰暫存指標 `0x200031bc` 或失敗回呼槽 `0x20003220`。因此在這條路徑及前輪其餘條件下，三筆 stack store 不再是未分類的寫址。

這不是最大 stack 深度或實機證明。APP reset 之後會跳入 resident，而非直接呼叫 `9008`；[既有交接研究](v4160-runtime-loop-2026-10-21/reuse/README.md)指出嚴格來源在缺少的 word 停止，指定額外 provider 才能演算到帶此 SP 的交接。此處也沒有證明先前的所有呼叫必定正常返回且不改 SP。

重現：以 decoded APP、V1.31 carrier 為參數。檢查兩檔身分，解碼八條 SP 調整與三筆 store，並核對選定的呼叫位置（不執行間接呼叫）。

```python
from pathlib import Path
from hashlib import sha256
import sys
a,b=(Path(x).read_bytes() for x in sys.argv[1:])
def need(ok):
    if not ok: raise ValueError('stack evidence mismatch')
need(sha256(a).hexdigest()=='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667')
need(sha256(b).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22')
def raw(p,n):
    image,base=(b,0x40000) if p>=0x40000 else (a,0x8000)
    return image[p-base:p-base+n]
def h(p): return int.from_bytes(raw(p,2),'little')
def sx(x,n): return (x^(1<<(n-1)))-(1<<(n-1))
def adjust(p):
    x=h(p); need(x&3==1 and (x>>7)&31==2); sign=x>>12&1
    if x>>13==0: return sx(sign*32+(x>>2&31),6)
    need(x>>13==3); return sx(sign*512+(x>>6&1)*16+(x>>5&1)*64+(x>>3&3)*128+(x>>2&1)*32,10)
d=[adjust(p) for p in (0x9008,0x9250,0x8e88,0x199e8,0x43c94,0x43b4e,0x44022,0x197be)]
need(d==[-16,-16,-32,-96,-16,-16,-32,-32])
for p,s in [(0x900c,'9124'),(0x9268,'0531'),(0x8ea8,'ef00b133'),(0x19aec,'8297'),(0x400a4,'7e3c0400'),(0x43d4c,'cd3b'),(0x43c04,'3929'),(0x440be,'0297')]: need(raw(p,len(s)//2).hex()==s)
slots=[]
for p in (0x197c0,0x197c2,0x197c4):
    x=h(p); need(x&0xe003==0xc002); slots.append(0x20010000+sum(d)+(x>>9&15)*4+(x>>7&3)*64)
need(slots==[0x2000ff1c,0x2000ff18,0x2000ff0c])
protected=[(0x2000318c,12),(0x200031bc,4),(0x20003220,4),(0x200043ac,0x2000b184-0x200043ac)]
need(all(w+4<=p or p+n<=w for w in slots for p,n in protected))
print('PASS: 8 live frames, 256 bytes; 3 conditional stack writes disjoint from protected RAM')
```
