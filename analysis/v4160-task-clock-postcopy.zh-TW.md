# 校準返回後：時鐘設定寫到哪裡？

針對首次排程前 `0x43f46` 的**非空 APP 設定成功路徑**。以下以 V1.31 參考映射、WCH 壓縮指令語意、正常堆疊、回呼槽和基址保持，以及複製器正常完成為條件；不是裝置 RAM 快照。

| 指令 | 寫入目的與條件 |
|---|---|
| `0x43f8c..43f9a` | 呼叫 `0x20000332(dst=0x20003234,src=重載的設定指標,n=16)`。預期複製範圍是 `[0x20003234,0x20003244)`；不是把資料寫回 APP stack。 |
| `0x43fa2..43faa` | 讀回第一個 word，再寫 `0x200031e0`。APP 設定未變時該 word 為 `0x191c6`。 |
| `0x43fae..43fd0` | 讀 **早期** 設定 `s0+23`；非零跳過寫入。零時取 **剛複製的** `+8` 半字 (16000)，乘 1400，再以 1000000 作除數。WCH byte store 只將結果低 byte 寫回 `0x20003203`，不是寫 `0x20003234+23`。名義整數商為 22。此除數與稍後時鐘回呼用的 16000 不同。 |
| `0x43fd2..43fdc` | [註冊並立即呼叫](v4160-role-nested-clock-registration.zh-TW.md) `0x43d62`。指標寫 `0x20003230`，回傳值寫 `0x200031b4`。內層有條件更新同一 `0x200031b4`，經 `0x191c6` 的時鐘讀取沒有 store；見[子呼叫寫入檢查](v4160-role-clock-write-sets.zh-TW.md)。這裡不是該報告另一呼叫者 `0x43520` 的路徑。 |

上述目的均不含 task byte `0x20004184`。若回呼返回後輸入為空，會改走 `0x43fe6`；欄位檢查失敗則可提前返回，兩者不能套用成功路徑的寫入順序。不據此推論所有堆疊、外設或中斷的實際影響。

重現：傳入 V1.31 carrier。解出兩個不同的基址、WCH load/store 寬度、複製目標，並驗算此特定除法的分支及兩個商位。另以 `analysis/check_v4160_clock_write_sets.py` 重跑共用除法尾段與註冊內層的無 store 視窗。

```python
from pathlib import Path
from hashlib import sha256
import sys
b=Path(sys.argv[1]).read_bytes()
def ck(x):
    if not x: raise ValueError('clock postcopy mismatch')
ck(sha256(b).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22')
def raw(p,n): return b[p-0x40000:p-0x40000+n]
def word(p): return int.from_bytes(raw(p,4),'little')
def imm(p): return int.from_bytes(raw(p,4),'little',signed=True)>>20
def wch(p):
    h=int.from_bytes(raw(p,2),'little'); q=h&3; ck(q in (0,2))
    off=8*((h>>10)&(7 if q==2 else 3))+2*((h>>5)&3)+(0 if q==2 else (h>>12)&1)
    return h>>13,q,8+((h>>7)&7),8+((h>>2)&7),off
ck(raw(0x43f8c,18).hex()=='3735002041461305452397c0fb1fe780c039')
dst=(word(0x43f8c)&0xfffff000)+imm(0x43f92)
ck(dst==0x20003234 and 0x43f96+(word(0x43f96)&0xfffff000)+imm(0x43f9a)==0x20000332)
ck([wch(p) for p in (0x43fae,0x43fb6,0x43fd0)]==[(1,0,8,14,23),(1,2,15,10,8),(5,0,8,10,23)])
ck(raw(0x43fb8,24).hex()=='9307805737460f003305f5021306062481468145ef90f274')
d=(word(0x43fbc)&0xfffff000)+imm(0x43fc4); n=16000*imm(0x43fb8)
ck(n==22400000 and 65536<=d==1000000<1<<24 and raw(0x6e274,8).hex()=='93560601c147d1b1')
lut=0x6df3e+4096+imm(0x6df42)+(d>>16); shift=32-16-raw(lut,1)[0]
ck(lut==0x6e96b and shift==12)
v=d<<shift; hi=v>>16; lo=v&65535; upper=(n<<shift)>>32; lower=(n<<shift)&0xffffffff
q,r=divmod(upper,hi); t=(r<<16)|(lower>>16); ck(q*lo<=t)
q2,r2=divmod(t-q*lo,hi); ck(q2*lo<=(r2<<16)+(lower&65535) and (q<<16|q2)==n//d==22)
ck(all(not x<=0x20004184<x+w for x,w in [(dst,16),(0x200031e0,4),(0x200031ec+23,1),(0x20003230,4),(0x200031b4,4)]))
print('PASS: 16-byte copy; separate cfg+23; 22400000 / 1000000 = 22; five fixed ranges exclude task ID')
```
