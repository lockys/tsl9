# 64-byte 重播記錄的產生端

與[讀取端](v4160-record-replay-page-source.zh-TW.md)對照。限 V1.31 參考映像與 Xwchc 解碼，不表示 v4.1.60 裝置採用此 ROM。

|呼叫位置|傳給 `0x4435c` 的鍵、長度與來源|
|---|---|
|`0x6b120`|`0x7000+s1`，64，`sp+48`|
|`0x6b632`|`0x7000+U8[s2]`，64，`sp`。先以 `(sp,255,64)` 要求填充，再讀索引。若正常填充且無干擾，重播端反相後 16 個半字皆零。|
|`0x6b8dc`|`s0`，64，`sp+16`。`0x6b884` 已將 `0x7000` 加入 s0，`0x6b88e` 先以此鍵呼叫讀取端；在通往寫入的分支上，`0x6b8d0` 再呼叫同一反相 helper `0x6af42`。依賴子呼叫保留 s0。|

**新建和更新不同。** 設定基址、讀寫回呼非零，鍵屬於 `0x7000..0x7ffe` 時，寫入端也減去 `0x7000` 並按頁長選頁。命中既有鍵且通過大小比較時，走 `0x444c8` 複製資料，不重寫標頭。若走到 `0x44516` 的新增分支並通過空間檢查，則依序寫標頭 +2 的 `0x5a`、+0 的 16-bit 鍵、+3 的下一偏移低 byte，再複製資料到標頭 +4。以預設頁長 256、首筆偏移 4、長度 64 為例：下一偏移 72，資料在頁內 `[8,72)`；這與讀取端相符。

這些是記憶體頁上的更新，不等同寫回裝置。第三條路徑在 `0x6b8e4` 重新載入一個 byte，再傳給 `0x44310`，不是依 `0x4435c` 的結果直接確認持久化。未證所有產生端、實際索引或頁面內容。

重現（參數為 V1.31 參考 BIN）：

```python
from pathlib import Path
import hashlib, sys
b=Path(sys.argv[1]).read_bytes()
def ck(x):
    if not x: raise ValueError('producer evidence mismatch')
ck(hashlib.sha256(b).hexdigest()=='133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22')
def raw(p,n): return b[p-0x40000:p-0x40000+n]
for p,t in [(0x6b120,0x4435c),(0x6b632,0x4435c),(0x6b88e,0x440c2),(0x6b8d0,0x6af42),(0x6b8dc,0x4435c),(0x6b8e8,0x44310)]:
    w=int.from_bytes(raw(p,4),'little'); d=(w>>31<<20)|(w>>12&255)<<12|(w>>20&1)<<11|(w>>21&1023)<<1
    ck(w&4095==0xef and p+(d^0x100000)-0x100000==t)
for p,h in [(0x6b116,'1d651018930500042695'),(0x6b624,'034509009d670a86930500043e95'),(0x6b8d4,'1008930500042285'),(0x44526,'13863400719a1106b296230107012310270134b379b7')]:
    ck(raw(p,len(h)//2)==bytes.fromhex(h))
print('PASS: six direct calls, three payload argument windows, new-header store sequence')
```
