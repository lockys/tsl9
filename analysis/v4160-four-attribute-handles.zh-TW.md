# 四列 handle 的分配順序

原 APP 註冊四列。V1.31 參考的 `0x4ce22` 先讀 `0x20002eec` 的半字，拒絕零或 `起點+列數 > 65536`；**等於 65536 可通過**。其後還有配置與清零呼叫，`0x4cec2` 才重新讀取用於寫列的起點 `F`。不能無條件把前後兩次讀值當成相同。

`0x4ceca` 算 `low16(F+i)`，`0x4cf08` 每次重讀描述中的陣列指標；先算 `16*i` 再遞增 i。依 Xwchc，`0x4cf12` 是 `SH a3,10(a2)`。因此陣列與計數穩定、寫入成功且後來沒有改列時，四列依序得到 F 至 F+3（模 65536），並非讀取前四個既有 handle。若起點跨呼叫保持一致，第四列不會繞回零：最後合法起點是 `0xfffc`，最後一列為 `0xffff`，下一分配游標才變成零。迴圈結束後 `0x4cede` 才更新游標，再建立服務串列連結。這並不證明回呼登記也成功。

所以給定分配後第一列的 handle，即可推得同次第四列的值；不能由 APP reset 表推出第一列的實際數字。後續寫入時仍逐列查找，並不以 handle 減法直接索引。參見[原列指標](v4160-write-attribute-identity.zh-TW.md)。

以下為固定參考位元組與邊界算術檢查，不是完整 CPU 模擬。以 Python 執行，唯一參數是該 V1.31 carrier：

```python
from hashlib import sha256
from pathlib import Path
import sys
b = Path(sys.argv[1]).read_bytes()
def need(x):
    if not x: raise ValueError('handle allocation evidence mismatch')
need(sha256(b).hexdigest() == '133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22')
for off, raw in [(0xce88,'8356c9ee85471309c9eef5d21a203697c166e3cee6fc'), (0xcec0,'1e208355090001460147b386e500c206c182636bf702ae97c207c18319c22310f900'), (0xcf08,'50401315470005072a9636a6054655bf')]:
    need(b[off:off+len(bytes.fromhex(raw))] == bytes.fromhex(raw))
accepted = 0
for f in range(65536):
    if f == 0 or f+4 > 65536: continue
    accepted += 1
    values = [(f+i)&65535 for i in range(4)]
    need(values[-1] == f+3 and len(set(values)) == 4)
    need((((f+4)&65535) == 0) == (f == 0xfffc))
need(accepted == 65532)
print('PASS: 65536 starts, 65532 admissible; final row at last start = 0xffff')
```
