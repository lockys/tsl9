# 在哪裡讀計數，哪些初始化寫入仍值得追？

V1.31 參考映射中，讀 `n` 的指令是 **`0x4daf6`** (`lbu a0,848(s4)`)，不是 `0x4db10`。`0x4db06` 在零值時跳過配置；`0x4db0e` 將非零值乘 16，`0x4db10/14` 才呼叫配置器。因果界線應畫在 `0x4daf6`。

| 讀取前的順序 | 對 `0x20003350` 的判斷 |
|---|---|
| `0x6dd1a → 0x61b1c → 0x55bde` | `[0x2000319f] != 0` 時跳過內層 `0x43c4e` 登記及 `0x5362e` 初始化。兩路會合後，`0x55c0c/16/20/2c` 在 `0x20003420..0x2000342f` 寫四個 word；`0x61b34/40/52` 分別寫 `0x20003470/3474/34fc`（後兩者同為 `0x2000` 高位）。這七筆都是存函式位址，不是此時呼叫它們。 |
| `0x6dd26 → 0x43c4e` | 另一次登記。先前的排除依賴正常 table 指標；不能把登記的 handler 當作同步執行。 |
| `0x6dd2a → 0x4da70`，至 `0x4dace` | 除 stack 外，直接寫 `0x20002fa2, 0x20002f9c, 0x2000331c, 0x20002fa5, 0x20002fa0, 0x20002fa1, 0x20002f9e` (halfword)、`0x20002f98` (word)、`0x20002fa3`；沒有重疊。 |
| `0x4dace → 0x4edd2` | 若內部計算量為零，`0x4edf6 → 0x4ee68` 還原並返回；非零才有 `0x4ee08` 配置、`0x4ee20` 清動態區與逐筆初始化、`0x4ee4e` 尾呼叫清固定區。正常 payload 界限能排除動態資料寫入，但不等於已證配置器自己的所有 metadata 寫入。 |
| `0x4dadc`、`0x4daea → 0x2000039c` | 先寫 byte `0x20003314`，再清 `[0x20003320,0x20003350)`；右端不包含在內。返回後即載入基址和計數，沒有第三個呼叫。 |

另以半字對齊滑窗掃描整份參考 carrier，檢查標準 SB/SH/SW 的 immediate 是否可在基址**恰為 `0x20003000`** 時覆蓋目標 byte；包含資料區與非指令邊界，不靠函式劃分。以下 Python 以 carrier 路徑為參數。陽性對照是上表 `0x4dadc` 的 byte store。

```python
from hashlib import sha256
from pathlib import Path
import sys
b = Path(sys.argv[1]).read_bytes()
if sha256(b).hexdigest() != '133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22': raise ValueError('reference')
def hits(target):
    out = []
    for i in range(0,len(b)-3,2):
        w = int.from_bytes(b[i:i+4],'little'); f = w>>12&7
        if w&127 != 35 or f>2: continue
        raw = (w>>25)*32+(w>>7&31); off = (raw^2048)-2048
        if off <= target < off+(1<<f): out.append(i+0x40000)
    return out
if 0x4dadc not in hits(0x314) or hits(0x350): raise ValueError('store census')
print('PASS: known +0x314 store found; zero standard store windows covering +0x350')
```

**仍待追查：** 優先檢查 `0x4ee08` 所用配置器的 metadata 基址與寫入範圍，再回查 `0x6dd16` 以前的初始化來源。零命中只排除一種編碼形式；不同基址、壓縮指令、間接指標、其他映像或中斷均不在此判據內，不能斷定 `n=0` 或此 ROM 已安裝。
