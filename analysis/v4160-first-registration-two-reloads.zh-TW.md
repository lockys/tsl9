# 首次 APP 登記：舊計數相同，不代表寫入同一張表

V1.31 參考映像中，`43be2` 重讀配置指標 P，`43bec` 加 576，`43bf2` 將結果寫至 `0x200031c4`。內部三槽在 `43c08` 從 s1 相對位址重讀這個 word；首次 APP 登記成功分支在 `43c5e/43c62` **重新建立基址並再讀一次**，沒有直接沿用前三槽的指標。以下從三條 load/store 的立即數與基底暫存器交叉核對位址。

[初始化計數](v4160-initial-registration-count.zh-TW.md)在清零、正常配置且無干擾下由 0 變 3；[首次 APP 登記](v4160-first-app-registration-order.zh-TW.md)則獨立比較當時的計數與容量。若 P 仍是首次 payload `0x200045b4`、兩次載入間沒有其他寫入，第四個 word 才是 `[0x20004800] ← 0x1995c`，返回舊計數 3。**返回 3 本身只辨識索引，不辨識表位址**。例如合成測試只在兩次載入之間換成另一個測試表，返回值不變，寫入目的卻改變；反之保持指標而將容量設為 3，滿表分支不讀第二次指標，返回 255。這兩個對照都不是實機事件。

重現：參數為 V1.31 主段。依既有 Xwchc 計數解讀，這裡只解標準 RV32 的指標產生與重讀，分支以局部模型表示；不假設設備已安裝此版本。

```python
from hashlib import sha256
from pathlib import Path
import sys
b=Path(sys.argv[1]).read_bytes()
def ck(v):
    if not v: raise ValueError('table provenance mismatch')
ck(sha256(b).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22')
def w(p): return int.from_bytes(b[p-0x40000:p-0x40000+4],'little')
def sx(x): return (x^2048)-2048
def lui(p,r):
    x=w(p); ck(x&4095==r*128+55); return x&0xfffff000
def imm(p,low):
    x=w(p); ck(x&0xfffff==low); return sx(x>>20)
x=w(0x43bf2); ck(x&0x1fff07f==0xf4a023); dst=lui(0x43be8,9)+sx((x>>25<<5)|(x>>7&31))
first=lui(0x43be8,9)+imm(0x43c08,0x4a683); second=lui(0x43c5e,13)+imm(0x43c62,0x6a683)
ck(dst==first==second==0x200031c4); t=0x200045b4+imm(0x43bec,0x78793)
def register(mem,n,c):
    if n>=c: return 255,None
    return n,mem[second]+4*n
for i in range(256):
    c=14+3*((i>>2)+(i&3)); m={dst:t}; ck(m[first]==0x200047f4 and register(m,3,c)==(3,0x20004800))
    m[dst]=t+0x100; ck(register(m,3,c)==(3,0x20004900))
ck(register({},3,3)==(255,None))
print('PASS: one pointer store, two independent loads; 256 nominal and 256 substituted-table cases; full branch skips load')
```
