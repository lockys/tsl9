# 從設定初始化到函式表重讀：哪些返回路徑保留 `0x200031c4`？

[上一輪](v4160-role-internal-table-writes.zh-TW.md)的 T 是 `0x43c08` **從 RAM 重讀**的表基址。本輪查的是保存 T 的四個 bytes，不是 T 指向的表內容。沿用 V1.31 參考 ROM 與[初始化堆疊](v4160-cfg60-init-stack.zh-TW.md)條件：APP `0x9008` 入口 SP 為 `0x20010000`、呼叫按預期返回並還原 SP，無外部干擾。

| 分支 | 對表基址的結論 |
|---|---|
| `0x4329a` | 整個 leaf 只將 `0x20003198..319b` 清零後返回，不依賴堆疊。 |
| `0x44022` 的三個設定欄位有任一為零 | 返回 1 之前只有四個保存用的 word store，皆在 `0x2000ff30..ff3f`；不呼叫 provider。此路徑保留 T。 |
| 三欄非零，讀回 word 與重新載入的 `cfg+8` 相等 | 若 `cfg+56` 仍是 APP `0x1979a`，其保存 ra 寫 `0x2000ff1c`，要求 copy 的目的為 `0x2000ff2c..ff2f`；在 copy 僅寫指定四個 bytes 且正常返回時，T 不變。 |
| 不相等，配置失敗 | `0x44076` 將配置結果寫到 `0x200031bc`，不是 T；不能單靠返回零排除配置器或其失敗回呼的其他寫入。 |
| 不相等，配置成功 | 本體兩個結尾清零各為 4 bytes，第二個恰在表基址**前一個 byte**結束。動態寫入仍須[有效暫存物件](v4160-44060-temp-buffer-stores.zh-TW.md)、[正常回呼](v4160-cfg60-heap-separation.zh-TW.md)及[有效釋放串列](v4160-44098-release-write-set.zh-TW.md)；不把固定寫址結果當成整支函式的無條件保證。 |

可重跑檢查（參數：decoded APP、V1.31 carrier）。從固定映像解碼 S-type/C.SWSP 的位移，檢查涵蓋整個 word 的半開區間。這是靜態寫址計算，不是裝置或 provider 的執行紀錄。

```python
from pathlib import Path
from hashlib import sha256
import sys
a,b=(Path(p).read_bytes() for p in sys.argv[1:])
def need(v):
    if not v: raise ValueError('handler-base evidence mismatch')
need(sha256(a).hexdigest()=='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667')
need(sha256(b).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22')
def sw(raw,reg):
    x=int.from_bytes(raw,'little'); need(x&0x707f==0x2023 and (x>>15)&31==reg and (x>>20)&31==0)
    i=(x>>25)*32+((x>>7)&31); return (i^2048)-2048
def spoff(raw):
    x=int.from_bytes(raw,'little'); need(x&0xe003==0xc002); return (x>>9&15)*4+(x>>7&3)*64
need(b[0x329a:0x329e].hex()=='b7370020' and b[0x32a2:0x32a4].hex()=='8280')
f=0x20010000-224
writes=[0x20003000+sw(b[0x329e:0x32a2],15)]
writes += [f+spoff(b[i:i+2]) for i in (0x4024,0x4030,0x4032,0x4034)]
need(a[0x117a0:0x117a2].hex()=='4111' and b[0x4052:0x4056].hex()=='70008545')
writes += [f-16+spoff(a[0x117a4:0x117a6]),f+12]
writes += [0x2000319c+sw(b[i:i+4],9) for i in (0x40a2,0x40a6)]
need(writes==[0x20003198,0x2000ff38,0x2000ff3c,0x2000ff34,0x2000ff30,0x2000ff1c,0x2000ff2c,0x200031bc,0x200031c0])
t=0x200031c4
need(all(w+4<=t or t+4<=w for w in writes) and writes[-1]+4==t)
print('PASS: 9 word destinations disjoint; final clear ends exactly at handler-base slot')
```
