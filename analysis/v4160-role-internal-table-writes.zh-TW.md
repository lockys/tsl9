# 初始化函式表：排除失敗回呼槽，不需要先證明索引為零

v4.1.60 APP 搭配 V1.31 參考 resident；沿用[既有逐指令解讀](../experiments/tsl9-original-APP-task-binding/verify-v1.py)的 Xwchc 語義。`0x43be2` 從 `0x2000322c` 重讀配置指標 P；`0x43bf2` 將 `T=P+576` 存到 `0x200031c4`。這與 `0x43bfc` 寫入 `0x200031e4` 的另一張表不同。`0x4329a` 與 `0x44022` 返回後，`0x43c08` **重讀** T，並非直接沿用先前的暫存器。

若 s0/s1 仍為 `0x2000319c/0x20003000`，`n` 是 `0x43c06` 當下讀取的 `0x2000319d` 無號 byte。依執行順序，四筆寫入是：

| PC | 目的 | 寬度 | 值 |
|---|---|---:|---|
| `43c1a` | `T+4*n` | 4 | `0x432a4` |
| `43c30` | `T+4*((n+1)&255)` | 4 | `0x43326` |
| `43c3e` | `0x2000319d` | 1 | `(n+3)&255` |
| `43c42` | `T+4*((n+2)&255)` | 4 | `0x43326` |

若重讀的表基址仍為 `P+576`，P 來自名義 arena（取寬鬆界 `0x200043b4 <= P < 0x2000b184`），則三個 word 的每個 byte 均高於失敗回呼槽 `[0x20003220,0x20003224)`，且不會因 32-bit 加法回繞。計數 byte 亦不重疊。因此**不需要**假設初始化時 `n=0` 就能排除這四筆寫入。這不是陣列容量證明，更不是實機 ROM 或全程指標未變的證明；亦不表示裝置曾執行該路徑。

重現：以下檢查接受 V1.31 carrier 路徑；固定來源、核對原始指令窗，再用兩端點與所有 byte 索引檢查地址界（對 P 單調）。

```python
from hashlib import sha256
from pathlib import Path
import sys
b=Path(sys.argv[1]).read_bytes()
def need(v):
    if not v: raise ValueError('internal table check failed')
need(sha256(b).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22')
need(b[0x3be2:0x3c06].hex()=='83a7c4223820b7340020938707240a0723a2f41cba97373700202322f71eeff0afe93929')
need(b[0x3c06:0x3c44].hex()=='1c3083a6441c373604001397270036971306462a10c3138717001377f70f0a073736040036971306663210c313873700890793f7f70f8a0718b0b69790c3')
for p in (0x200043b4,0x2000b183):
    for n in range(256):
        ids=[(n+k)&255 for k in range(3)]
        need(len(set(ids))==3)
        for i in ids:
            w=p+576+4*i
            need(0x20003224<=w and w+3<2**32)
need(0x2000319d+1<=0x20003220)
print('PASS: 256 indices x 2 base endpoints; 3 word stores and 1 byte store exclude cfg+52')
```
