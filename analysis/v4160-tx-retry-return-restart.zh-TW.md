# 重試未排入時：本輪不補送，新 TX 可重新啟動

[通知失敗路徑](v4160-tx-notification-result.zh-TW.md)的兩個入口匯合到 `0x87f2`，參數是 `(task,2,2)`。若 `[0x40058]` 正常返回，`0x87fa` 無條件跳至 `0x882e`；`xori a0,s0,2` 直接覆寫排程服務的回傳值，再跳至還原暫存器的尾段。不論服務返回零或非零，APP 都不據此再次呼叫排程，亦不把事件 2 留在這次返回遮罩中。前提是所需暫存器及 stack 正常保存。這不同於另一個 APP 呼叫者 `0x9230` 對同一槽的結果做 `seqz`。V1.31 參考例子：若 ID 不小於任務數，服務可正常返回零而不建 timer；不代表此分支實際發生。

仍有獨立的啟動入口：若後來另一筆 TX 通過 `0x8a56` 的接納條件、選到同一 bank 且完成組框，`0x8b32` 寫入新總長、`0x8b36` 將游標歸零，再向該 bank 當下的 task ID 請求事件 1。它不接續先前失敗的游標，[事件 1](v4160-tx-bit0-to-copy.zh-TW.md)重新讀長度並準備片段。這是新提交流程，不是保證舊片段自動重送。如果已有其他事件 2 待處理，這次返回也不能證明那一份已取消。此分析不宣稱枚舉所有投遞來源或證實實機傳送。

重現（參數為 v4.1.60 APP）：從原碼解出三條無條件跳躍與 XORI，枚舉 16-bit 事件遮罩中匹配本處優先序者，另固定新 TX 游標清零與投遞指令。不是排程器模擬。

```python
import sys
from pathlib import Path
from hashlib import sha256
b=Path(sys.argv[1]).read_bytes()
def ck(ok):
    if not ok: raise ValueError('TX retry evidence mismatch')
ck(sha256(b).hexdigest()=='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667')
def raw(pc,n): return b[pc-32768:pc-32768+n]
def jump(pc):
    w=int.from_bytes(raw(pc,2),'little'); ck(w&0xe003==0xa001)
    d=sum(((w>>s)&1)<<t for s,t in [(12,11),(11,4),(10,9),(9,8),(8,10),(7,6),(6,7),(5,3),(4,2),(3,1),(2,5)])
    return pc+(d^2048)-2048
ck([jump(p) for p in (0x8842,0x87fa,0x8832)]==[0x87f2,0x882e,0x866c])
ck(raw(0x87f2,8).hex()=='0946894552858297')
w=int.from_bytes(raw(0x882e,4),'little'); ck(w&0x707f==0x4013 and (w>>7&31,w>>15&31,w>>20)==(10,8,2))
masks=[m for m in range(65536) if m&0x800b==2]; ck(len(masks)==4096 and all((m^(w>>20))==m-2 for m in masks))
ck(raw(0x8b2e,12).hex()=='8545b6972391870023920700' and raw(0x8b42,16).hex()=='b707040003a307050345060005610283')
print('PASS: 3 jumps; scheduler result overwritten; 4096 eligible masks; new TX resets cursor and requests event 1')
```
