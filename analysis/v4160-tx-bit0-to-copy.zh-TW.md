# TX 待處理事件：遮罩 1 選擇片段，遮罩 2 才取資料

接續[兩版設位服務](v4160-dequeue-tx-event-leaf.zh-TW.md)。這次直接查 v4.1.60 APP，不從 SDK 的函式名稱推測。

- 若 `0x8614` 真收到事件，遮罩 `0x8000`、`8` 優先。其餘情況先比 task ID 與當下 `gp+148`，相同取 bank 0；否則再比 `gp+152`，相同取 bank 1。兩者都不符不走 TX。故生產端選用的 bank 只有在這些綁定一致且可區分時才等於消費端的 bank。
- 令 `D=0x2000b18c+1062*bank`、`Q=0x2000bdf8+8*bank`。遮罩 **1** 在 `0x86d4/0x86d8` 分別讀半字 `D+2`（總長）、`D+4`（游標），不是讀 frame 內容。查詢 `[0x4013c]` 必須恰回 1，且 `int16(uint16(總長−游標))>0`，否則清 `D+2` 並結束此位。通過時向 `[0x400b8]` 查詢，以 `min(剩餘長度,uint16(回傳值−3))` 寫 `Q+2`，設 `D[0]=10`，再呼叫 `[0x40050](taskID,2)`。不以這次設位的回傳值判定已送出。
- 遮罩 **2** 要等後續分派才會執行。若 `D[0]` 非零，`0x87a2` 以當下 `Q+2` 為長度請求配置。結果為零就不呼叫複製；非零時 `0x87a8..0x87ba` **重新讀** `D+4` 與 `Q+2`，以配置結果作目的、`D+6+游標` 作來源呼叫 `[0x4004c]`。因此 bank 0/1 在游標零時的來源依序是 `0x2000b192`、`0x2000b5b8`，皆從 frame 開頭而非略過封包 header。這是複製請求，不是已送達的證據。

假設相關暫存器在外部呼叫後正常保存、存取成功；不假設事件一定派送，也不把兩次取樣間 RAM 不變當成已證事實。以下以原 BIN 為唯一參數，重解四組 PC-relative 取址、查核欄位指令和成功路徑的複製參數；不執行 provider。

```python
from pathlib import Path
from hashlib import sha256
import sys
b=Path(sys.argv[1]).read_bytes()
def ck(x):
    if not x: raise ValueError('TX event consumer mismatch')
ck(sha256(b).hexdigest()=='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667')
def raw(p,n): return b[p-32768:p-32768+n]
def addr(p):
    u=int.from_bytes(raw(p,4),'little'); i=int.from_bytes(raw(p+4,4),'little'); r=u>>7&31
    ck(u&127==23 and i&0x707f==19 and i>>7&31==r and i>>15&31==r)
    return (p+(u&~4095)+((i>>20^2048)-2048))&0xffffffff
ck(addr(0x86c0)==addr(0x876c)==0x2000b18c and addr(0x870a)==addr(0x8784)==0x2000bdf8)
ck(raw(0x86d4,8).hex()=='83d9270003db4700' and raw(0x8732,12).hex()=='2380f400b7070400bc4b8297')
ck(raw(0x87a8,20).hex()=='83554b0083a7cb0403d624009909ce95e6958297')
ck([addr(0x876c)+1062*k+6 for k in (0,1)]==[0x2000b192,0x2000b5b8])
print('PASS: four PC-relative pairs; descriptor loads, post and copy operands; both frame bases')
```
