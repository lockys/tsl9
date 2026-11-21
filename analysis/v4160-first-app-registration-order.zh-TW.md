# 從內部三槽到第一個 APP handler

接續[三筆內部登記](v4160-initial-registration-count.zh-TW.md)，只追正常返回後的同步指令路徑。`0x43b3e` 返回後，V1.31 候選 `0x43d4e..43d5a` 把 a0 設零後返回，沒有另一筆註冊。**這個零不是三槽登記成功的收據**：包裝函式不檢查內層結果。必須另外滿足前輪的配置和寫表條件。

1. APP `0x19aee` 在 a0 為零時續行；非零則在 `0x19af0` 原地跳轉。續行路徑還有一次呼叫，不能只看 main 的相鄰兩條 JAL。`0x19af8` 呼叫 `0x19106(64,1)`，走非零分支，把 `0x40021014` 的 word 與 `0x40` 做 OR 後寫回，直接返回。隨後兩個 word store 到 `0xe000e104/108`，都不直接寫 task 計數或表，也沒有同步呼叫 handler。這不排除外設副作用或非同步中斷。
2. 返回 main 的 `0x8eac` 後直接呼叫 `0x19b16`。此函式在第一次間接呼叫前只保存暫存器、讀 `[0x40080]`、以 PC-relative 方式算出 a0=`0x1995c`。`0x19b2e` 是這條續行路徑的**第一個 APP 登記呼叫**，不是執行 `0x1995c`。main 的 `0x8eb0` 是更晚的呼叫。
3. 若該槽仍是候選 `0x43c4e`、計數仍為 3、容量仍為 14..212、表基址仍為 `0x200047f4`，登記成功：計數先改為 4，`[0x20004800]` 寫 `0x1995c`，返回 3。APP `0x19b34` 將返回值低 byte 寫到 live `gp+388`。容量不足則返回 255 而不寫表，APP 仍會保存該值。未證裝置 ROM 或中斷時序。

重現（decoded APP、V1.31 carrier）：從三個直接呼叫的 JAL 解目的位址，核對中間 leaf 實際走的指令窗與回呼來源。這是靜態控制流檢查，不是裝置執行。

```python
from hashlib import sha256
from pathlib import Path
import sys
a,b=(Path(p).read_bytes() for p in sys.argv[1:])
def need(v):
    if not v: raise ValueError('registration order mismatch')
need(sha256(a).hexdigest()=='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667')
need(sha256(b).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22')
def app(p,n): return a[p-0x8000:p-0x8000+n]
def sx(v,n): return (v^(1<<(n-1)))-(1<<(n-1))
def jal(p):
    x=int.from_bytes(app(p,4),'little'); need(x&4095==0xef)
    return p+sx(((x>>31)<<20)|(x&0xff000)|((x>>20&1)<<11)|((x>>21&1023)<<1),21)
need([jal(p) for p in (0x8ea8,0x19af8,0x8eac)]==[0x199e2,0x19106,0x19b16])
need(b[0x3d4e:0x3d5c].hex()=='8147b240224492443e8541018280')
need(app(0x19aee,10).hex()=='11c101a0854513050004')
need(app(0x19106,14).hex()=='99c5371702405c4b5d8d48cb8280')
need(app(0x19afc,26).hex()=='b7e700e037070080f640664423a2e710054723a4e71025618280')
need(app(0x19b16,26).hex()=='411126c2b704040083a7040806c622c417050000130565e38297')
handler=0x19b26+sx(int.from_bytes(app(0x19b2a,4),'little')>>20,12)
need(handler==0x1995c and int.from_bytes(b[128:132],'little')==0x43c4e)
need(app(0x19b30,8).hex()=='138441182300a400' and 0x200047f4+4*3==0x20004800)
print('PASS: 3 direct calls; intervening MMIO leaf; first APP handler 0x1995c; conditional slot 3 at 0x20004800')
```
