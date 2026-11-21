# `cfg+60` 返回後，暫存區指標與堆積區標頭是否還在？

接續[釋放函式的前提](v4160-44098-release-write-set.zh-TW.md)。以 v4.1.60 **原 APP**（非 C overlay）核對 `0x197be` 和其五個直接子函式。沿用[呼叫者契約](v4160-nv-call-contract-2026-10-22/caller-review/readme.zh-TW.md)的三次名義呼叫，只問 CPU 寫址是否落入受保護的 RAM；不操作裝置。

| 寫址類別 | 指令位置數 | 與 RAM 的關係 |
|---|---:|---|
| 回呼本體的 stack word | 3 | 相對回呼入口 SP 為 −4、−8、−20。這是唯一不能只靠 APP 常數排除重疊的一類。 |
| 四個儲存控制子函式的固定外設 word | 12 | 共四個不同地址，在 `0x40022000` 外設區，不是暫存區指標或堆積區。 |
| 固定長度迴圈的資料目的 | 1 | 同一條 store 多次執行。來源是暫存區，**寫址不是來源指標**；依未變的名義設定，三次呼叫的目的聯集為 `[0x08077c00,0x08077f00)`。 |
| `0x19764` 計時函式的固定外設 word | 6 | 共四個不同地址，在 `0xe000f000` 外設區。`gp+382` 是讀取，不是寫入。 |

因此，若回呼仍綁定 `0x197be`、三輪目的參數未變、stack 保存位置與受保護 RAM 分離，則這 22 個 store 位置不會直接改寫 `0x200031bc`、`0x20003220`、三個 heap cursor 或 `[0x200043ac,0x2000b184)` 內的標頭。這是維持既有有效串列的**一項必要查核**，不是證明串列本來有效。也不把邏輯地址不重疊擴大成實體映射、外設副作用、中斷或輪詢一定返回的證明。

重現：以 decoded APP 路徑為參數，依指令寬度走訪六個函式，解出 word store 的基底暫存器和位移。下列固定基址與目的參數沿用前述靜態呼叫者與 leaf 分析；不在測試內執行它們。

```python
from pathlib import Path
from hashlib import sha256
import sys
b=Path(sys.argv[1]).read_bytes()
def need(v):
    if not v: raise ValueError('APP evidence mismatch')
need(sha256(b).hexdigest()=='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667')
def stores(p,end):
    rows=[]
    while p<end:
        w=int.from_bytes(b[p-0x8000:p-0x8000+4],'little'); h=w&65535; q=h&3; f=h>>13
        if q==3 and w&127==35:
            need(w>>12&7==2); d=(w>>25)*32+(w>>7&31); rows.append((w>>15&31,(d^2048)-2048))
        elif q==0 and f==6: rows.append((8+(h>>7&7),8*(h>>10&7)+4*(h>>6&1)+64*(h>>5&1)))
        elif q==2 and f==6: rows.append((2,4*(h>>9&15)+64*(h>>7&3)))
        elif q in (0,2): need(f not in (5,7))
        p+=4 if q==3 else 2
    need(p==end); return rows
need(stores(0x197be,0x197f0)==[(2,28),(2,24),(2,12)])
need(stores(0x19764,0x1979a)==[(15,n) for n in (4,16,20,0,0,0)])
need(stores(0x18e98,0x18eb6)==[(15,n) for n in (4,4,36,36)])
need(stores(0x18eb6,0x18ec4)==[(14,16)])
need(stores(0x18ec4,0x18ef2)==[(15,n) for n in (16,20,16,16)])
need(stores(0x18ef2,0x18f56)==[(14,16),(13,0),(14,16),(15,16)])
protected=[(0x200031bc,4),(0x20003220,4),(0x2000318c,12),(0x200043ac,0x2000b184-0x200043ac)]
fixed=[(0x40022000+n,4) for n in (4,16,20,36)]+[(0xe000f000+n,4) for n in (0,4,16,20)]
words=[(0x08077c00+256*i+j,4) for i in range(3) for j in range(0,256,4)]
need(all(a+n<=c or c+m<=a for a,n in fixed+words for c,m in protected))
print('PASS: 6 functions; 22 store sites; 8 fixed MMIO words and 192 nominal destination words disjoint; stack conditional')
```
