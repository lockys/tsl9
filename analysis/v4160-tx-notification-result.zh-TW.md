# TX 通知返回後：推進、重試與停止

接續 [bit 0 到複製](v4160-tx-bit0-to-copy.zh-TW.md)。下表只記 v4.1.60 APP `0x877a..0x884a` 的明示操作。D 是本 bank 的描述元，Q 是片段描述元。

|條件|APP 動作|下一個事件請求|
|---|---|---|
|入口讀到 `D[0]==0`|清除總長 `u16[D+2]`，不清游標、不配置|無|
|配置回傳零|不複製、不呼叫通知、不呼叫釋放；重新讀 `D[0]`，減一後寫低 byte|`[0x40058](task,2,2)`|
|複製後 CCC 回傳最低位是 0|不呼叫通知；以 `(Q,27)` 呼叫 `[0x4012c]`，再重新讀計數並減一|同上|
|CCC 最低位是 1，通知返回非零|將 `u16[gp+42]` 填入 Q 的首半字，以 `(handle,Q,0)` 呼叫 `[0x400d4]`；返回後走同一釋放及減一路徑|同上|
|通知返回零|在 `0x8816/0x881a` 重新讀游標和片段長度，`0x8824` 寫 `u16[D+4]=(游標+片段長度) mod 65536`；不走上述釋放或減一|`[0x40050](task,1)`，重新計算下一片段|

失敗路徑沒有 APP 游標寫入。只有在 bank、資料、游標和片段長度未被其他動作改動且重新派送成功時，才是重試「同一片段」。若從 10 開始且只有這條失敗路徑改計數，**第十次失敗仍請求事件 2**；是下一次事件讀到零才清總長。成功路徑也不等於對端已收到。`0x882e` 回傳原事件遮罩 XOR 2，不把服務回傳值當作事件遮罩（假設外部呼叫正常返回且保存所需暫存器）。

以下核對原 BIN 的四個壓縮條件跳躍及成功路徑的讀、加、寫指令；不模擬外部服務。以 BIN 路徑為參數執行：

```python
from pathlib import Path
from hashlib import sha256
import sys
b=Path(sys.argv[1]).read_bytes()
def check(ok):
    if not ok: raise ValueError('TX notification result mismatch')
check(sha256(b).hexdigest()=='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667')
def raw(pc,n): return b[pc-32768:pc-32768+n]
def branch(pc,x):
    w=int.from_bytes(raw(pc,2),'little'); op=w>>13
    check(w&3==1 and op in (6,7))
    k=(w>>12&1)*256+(w>>10&3)*8+(w>>5&3)*64+(w>>3&3)*2+(w>>2&1)*32
    return (8+(w>>7&7),pc+((k^256)-256) if (x!=0)==(op==7) else pc+2)
rows=[(0x877e,15,0x8844,0x8780),(0x87a6,10,0x8834,0x87a8),(0x87ca,10,0x87cc,0x87fc),(0x8814,10,0x8816,0x87cc)]
for pc,r,z,nz in rows:
    for x in range(256): check(branch(pc,x)==(r,nz if x else z))
check(raw(0x87c8,2).hex()=='0589')
check(raw(0x8816,18).hex()=='83574b0003d7240085455285ba972312fb00')
check(raw(0x8834,10).hex()=='83470b00fd172300fb00' and raw(0x8844,4).hex()=='23110b00')
print('PASS: 1024 branch cases, CCC mask, cursor update, allocation-failure decrement and zero-budget clear')
```
