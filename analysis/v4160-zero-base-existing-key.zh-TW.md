# 零基址 RAM：已有標頭時，何時原位更新？

承接[首筆新增](v4160-zero-base-first-header.zh-TW.md)。限 V1.31 參考映像、Xwchc、穩定且有效的 RAM 記錄。令 `o` 為目前偏移（首筆為 4），`H=B+(o & ~3)`。標記 H[2] 為 `0x5a` 時，寫入端讀取小端半字鍵及 `q=H[3]`，然後分三路：

|條件|本筆動作|
|---|---|
|鍵不同|`0x44570` 跳過寫入，取 `o=q` 繼續；下一筆位置相對 B，不是相對 H。|
|鍵相同且長度通過比較|`0x44574..0x44578` 計算 `q-o`，以 RV32 **有號**比較 `q-o >= len`；相等也進 `0x444c8`，請求複製至 H+4，保留原標頭。此比較不是從資料起點量出的長度。|
|鍵相同但比較不通過|`0x4457c` 按 Xwchc 為半字寫入，把 H 的鍵改成 `0x00ff`，不清標記，也不改 H[3]。再取 `o=q` 繼續掃描；這一步本身沒有新增記錄。|

以前輪正常建立的兩種首筆為例，16-byte 記錄的 q=24、64-byte 的 q=72；重新寫入相同鍵與相同長度都走原位更新。將 16-byte 記錄換成 64-byte 時則先改鍵再繼續。此處不據靜態控制流推論裝置資料、實際複製成功或後面一定找到空位。

離線核對（參數：V1.31 carrier）。由原分支解出比較種類、暫存器及目標，再以兩種既有記錄對照更新、改鍵、略過三條路徑：

```python
from pathlib import Path
import hashlib,sys
b=Path(sys.argv[1]).read_bytes()
def ck(x):
    if not x: raise ValueError('existing record mismatch')
ck(hashlib.sha256(b).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22')
def at(p,n): return int.from_bytes(b[p-0x40000:p-0x40000+n],'little')
def branch(p):
    w=at(p,4); ck(w&127==99)
    d=(w>>31<<12)|(w>>7&1)<<11|(w>>25&63)<<5|(w>>8&15)<<1
    return (w>>12&7,w>>15&31,w>>20&31,p+(d^4096)-4096)
ck(branch(0x44570)==(1,17,18,0x4457e) and branch(0x44578)==(5,13,9,0x444c8))
ck(at(0x44574,4)==0x40d606b3 and at(0x44556,4)==0x0ff00593)
h=at(0x4457c,2); ck((h&0xe003,8+(h>>7&7),8+(h>>2&7),8*(h>>10&7)+2*(h>>5&3))==(0xa002,14,11,0))
ck(b[0x457e:0x4586].hex()=='93160601c182d9bf')
for q,n,same,want in [(24,16,1,'copy'),(72,64,1,'copy'),(24,64,1,'rekey'),(72,16,0,'skip'),(24,20,1,'copy')]:
    ck(('skip' if not same else 'copy' if q-4>=n else 'rekey')==want)
print('PASS: two decoded branches, halfword store operands, next-offset path, five model decisions')
```
