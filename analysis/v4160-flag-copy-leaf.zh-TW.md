# 旗標服務：0x4004c 是否還會呼叫其他函式？

[APP 呼叫圖](v4160-flag-service-closure.zh-TW.md) 剩下的 `0x12c0c` 是 `jalr a5`，正常返回點是 `0x12c0e`。在 V1.31、V1.40 參考 ROM，槽內都是 `0x20000332`；按各自的啟動映射，兩個候選 RAM 函式的 58 bytes 完全一致。以 RAM 執行位址反組譯，共 18 條指令：

| 控制轉移 PC（低位） | 條件與目的地（同一 0x20000000 基址） |
|---|---|
| 0342、0344 | 目的或來源為零即跳 034a，略過迴圈 |
| 0348 | 長度非零跳 0354，否則落入 034a |
| 0366、036a | 計數尚未達長度跳 0354，結束則經 036a 跳 034a |
| 0352 | 唯一 `ret`；沒有 call、外部尾跳或其他間接跳轉 |

入口仍先讀取並清零外設 word `0x4002420c`，執行 `fence.i`；共同出口寫回先前讀值。不是無副作用的空操作。迴圈依升序逐 byte 先讀再寫。若該候選確實被複製到 RAM 且保持不變、取指與資料存取成功、正常返回，旗標入列的 1..8 bytes 複製本身不會呼叫設定初始化；同一槽的兩個 12-byte 出列呼叫亦然。這不涵蓋出列後的 APP 分派、外設副作用、中斷或實機 ROM 身分。

以下檢查只需標準 Python。依序傳入 V1.31、V1.40 主區 carrier，不使用實機資料。核對身分、槽、整段、指令邊界與分支編碼，拒絕未列的控制形式：

```python
from pathlib import Path
from hashlib import sha256
import sys

def require(ok):
    if not ok: raise ValueError('copy leaf evidence mismatch')

refs = [('133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22', 0x5a2),
        ('b02cf8ec6829425a558887bd6bc10d28ae1f0e2e9e1850333f0bab6088e9e941', 0x5e2)]
control = {0x342:'01c5', 0x344:'99c1', 0x348:'11e6', 0x352:'8280', 0x366:'e317f6fe', 0x36a:'c5b7'}
require(len(sys.argv)==3)
for path,(digest,off) in zip(sys.argv[1:],refs):
    b=Path(path).read_bytes(); require(sha256(b).hexdigest()==digest)
    require(int.from_bytes(b[76:80],'little')==0x20000332)
    body=b[off:off+58]; require(sha256(body).hexdigest()=='558a82658cb54901945d4c2884f2e87e763f64d57c0cafa831307beb44ae0c36')
    i=0; seen=set(); count=0
    while i<len(body):
        n=4 if body[i]&3==3 else 2; raw=body[i:i+n]; pc=0x332+i
        if pc in control: require(raw.hex()==control[pc]); seen.add(pc)
        elif n==2: require(raw.hex() in ('8147','8507'))  # li / addi
        else: require(raw[0]&127 in (0x37,3,0x23,0x0f,0x33))  # lui/load/store/fence/ALU
        i+=n; count+=1
    require(i==58 and count==18 and seen==set(control))
print('PASS: 2 reference slots, identical 58-byte leaf, 18 instructions, 5 internal branches/jumps and 1 return')
```
