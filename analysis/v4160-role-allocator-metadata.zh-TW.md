# `0x4ee08`：配置器自己的管理資料會寫到計數嗎？

接續[讀取前的初始化順序](v4160-role-before-count.zh-TW.md)。V1.31 參考 carrier 在既定 RAM 複製映射與 Xwchc 解碼下，`0x4ee08/0c` 呼叫 `0x20000040`。輸入 byte `c` 來自 `0x20003201`，`k=(c&3)+(c>>2)`；`k=0` 不呼叫，否則要求 `R=60*k`（60..3960，已對齊），tag `0x9001`。均走大區塊游標 `[0x20003190]`。這裡查的是配置器，不是返回後的 payload fill。

設 `H` 為命中的空閒 header，`C` 為其容量，`G=0x2000319c`。遍歷從 `H+0` 讀下一個 header；僅在 tag 為零且 `C>=R` 時進入成功路徑。

| 路徑 | 管理資料的直接寫入（不含 stack、MMIO） |
|---|---|
| `C-R > 8` 分割 | `N=H+8+R`；在 `N+4` 寫剩餘容量 `C-R-8`、`N+0` 寫原 successor、`N+6` 清 tag；在 `H+0` 寫 `N`、`H+4` 寫 `R`；在 `G+6` 將原 halfword 減 8。 |
| `0 <= C-R <= 8` 不分割 | 跳過以上寫入，沿用原容量，不產生第二個 header。 |
| 成功路徑會合 | 在 `H+6` 寫 tag，在 `G+6` 將當時的 halfword 減 `R`；返回 `H+8`。 |

若 `H` 確為名義 arena 中的有效 header（`0x200043ac <= H`、區塊不越 sentinel `0x2000b184`），兩個 header 的欄位都高於 `0x20003350`；固定統計欄位佔 `0x200031a2..0x200031a3`，低於計數。故在這些條件下，**成功分割及不分割都不會直接改計數**。另有 stack 保存與固定 `0x4002420c` 的 store，假設 stack 獨立，不推論外設副作用。

**未解路徑：** 游標抵達 `[0x2000318c]` 的 sentinel 時，`0x20000094` 讀 `[0x20003220]`；非零才在 `0x200000a0` 呼叫它。配置器本體隨後走失敗返回，但不能把未知回呼的寫入當成空集合。也沒有證明實機使用此 ROM、heap 完整或配置一定成功。

下列檢查用 carrier 路徑作參數；核對呼叫目標、`0x200000d2..0x200000fb` 的連續 bytes，另解碼五個 Xwchc halfword store，避免以標準浮點助記符判斷目的地。

```python
from pathlib import Path
from hashlib import sha256
import sys
b=Path(sys.argv[1]).read_bytes()
def need(p):
    if not p: raise ValueError('reference mismatch')
need(sha256(b).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22')
u,i=(int.from_bytes(b[p:p+4],'little') for p in (0xee08,0xee0c))
need((u&4095,i&0xfffff,(0x4ee08+(u&~4095)+((i>>20^2048)-2048))&0xfffffffe)==(0x97,0x80e7,0x20000040))
r=b[0x270:]; need(r[0xd2:0xfc].hex()=='138687001d8f2a9661175aa2232016012313060010c15ea1130788fffaa26ea1ee222105b387f540fea2')
for p,base,src,offset in [(0xdc,12,14,4),(0xe8,10,15,4),(0xee,13,14,6),(0xf0,10,11,6),(0xfa,13,15,6)]:
    h=int.from_bytes(r[p:p+2],'little')
    need((h&3,h>>13,8+(h>>7&7),8+(h>>2&7),8*(h>>10&7)+2*(h>>5&3))==(2,5,base,src,offset))
for c in range(1,256):
    size=60*((c&3)+(c>>2)); need(52<size<=3960 and size%4==0)
print('PASS: call target; split/join bytes; 5 Xwchc stores; 255 nonzero request inputs')
```
