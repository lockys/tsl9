# 停止事件 4 的兩個 task ID 與連線的兩個 task ID

原 APP 正常同步初始化路徑的順序（不是用函式位址排序）：`0x9268` 先呼叫 `0x8e88`，其中 `0x8eb0` 呼叫 `0x907a`；等 `0x8e88` 返回並經過其他初始化，`0x9280` 才呼叫 `0x17040`。下表的 slot 綁定假設表基址保持 `0x40000`。

|順序|呼叫 `[0x40080]`|handler|回傳低 byte 存放|
|---|---|---|---|
|1|`0x90a2`|`0x901a`|`0x90a8`: gp+166|
|2|`0x8f8a`|`0x8614`|`0x8f8c`: gp+148|
|3|`0x8fa0`|`0x8614`|`0x8fa2`: gp+152|
|4|`0x1706a`|`0x16f00`|`0x17070`: `[s2]`，呼叫前 `0x17066` 設 s2=gp+363|

最後一筆不是直接的 gp-relative store。它前面的清零請求只涵蓋 gp+360..362，不含 gp+363。前兩個周邊記錄雖共用 handler，仍各呼叫一次註冊服務。

**判斷：** 若 V1.31 參考註冊實作 `0x43c4e` 適用、容量穩定、計數只由成功註冊遞增、表和四個結果未遭其他寫入，任兩次成功註冊不會領到相同 ID（不要求四次相鄰）。所以 `gp+166` 或 `gp+363` 不能以同一成功 ID 停止 `gp+148/+152` 的事件 4。滿表可使多個結果同為 255；這是共同失敗值，不是共同註冊的任務。此結論限四筆都已寫回後；不是所有 writer 或設備上時間順序的證明。

下列檢查接受原 decoded BIN 路徑，固定新發現的指令窗，並窮舉註冊計數規則的 byte 邊界；不執行韌體。其他三筆的原始指令見 `v4160-shared-role-handler-pa.zh-TW.md` 與 `v4160-registration-gp166.zh-TW.md`。

```python
from pathlib import Path
from hashlib import sha256
import sys
b=Path(sys.argv[1]).read_bytes()
def ck(x):
    if not x: raise ValueError('evidence mismatch')
ck(sha256(b).hexdigest()=='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667')
def win(p,s):
    raw=bytes.fromhex(s); ck(b[p-32768:p-32768+len(raw)]==raw)
win(0x9268,'0531'); win(0x9280,'efd0105c'); win(0x17050,'0d468145138581168297'); win(0x1705a,'83a7040817050000130525ea1389b1168297371401402300a900')
ck(0x1705e-350==0x16f00)
for c in range(256):
    for n in range(256):
        first=n if n<c else 255
        nxt=n+int(n<c); second=nxt if nxt<c else 255
        ck(first!=second or first==255)
        ck(first==255 or first<nxt<=255)
print('PASS: gp+363 registration window; 65536 count/capacity pairs')
```
