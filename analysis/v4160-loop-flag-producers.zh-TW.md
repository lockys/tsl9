# 下一輪掃描前：誰能重設 APP 旗標的低兩位？

在原 v4.1.60 APP（SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`）逐半字檢查 32-bit RV32 SB/SH/SW 編碼，限定基底暫存器為 gp，且寫入範圍含 gp+360。四處命中，都是 `sb a5,360(gp)`。名義 gp=0x20004000，目標是 `0x20004168`。

| 寫入 PC | 條件與值 |
|---|---|
| 0x16fd6 | 0x16fba 讀 `0x40010414`，若 bit 6 為 1，先向同址寫 64；再重新讀旗標，OR 1 後寫回。 |
| 0x16ffa | 0x16fde **另讀一次** `0x40010414`，若 bit 7 為 1，先向同址寫 128；再重新讀旗標，OR 2 後寫回。 |
| 0x17014 | 主迴圈第一次取樣命中 bit 0，清該位後呼叫 `0x16b0a(1)`。 |
| 0x1702e | 主迴圈第二次取樣命中 bit 1，清該位後呼叫 `0x16b0a(2)`。 |

前兩處同屬 `0x16fb6..0x17002`，最後為 `mret`；映像 `0x80d4` 的小端 word 正好是入口 `0x16fb6`。這支持中斷處理程式的解讀，但不證明該中斷啟用、外設寫入確實清除狀態，或本輪曾進入該入口。另有[初始化的三位元組清零請求](v4160-event4-init-bulk.zh-TW.md)，不属于上述直接 store 編碼。

裁決：即使初始化成功清零，也不能把 `0x17004` 的輸入定為零；兩次外設採樣及兩次軟體旗標採樣都不能合併。掃描不涵蓋以其他暫存器為基底、間接 fill、裝置或 resident 寫入。下一個判別點是 APP 初始化是否設定相應中斷來源，而不是先假定某個事件已發生。

重現直接寫入盤點（`python -` 傳入 decoded BIN 路徑作第一參數；PC = file offset + 0x8000）：

```python
import hashlib, sys
from pathlib import Path
b = Path(sys.argv[1]).read_bytes()
if hashlib.sha256(b).hexdigest() != '0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667': raise ValueError('image')
hits = []
for i in range(0, len(b)-3, 2):
    w = int.from_bytes(b[i:i+4], 'little'); k = w >> 12 & 7
    if w & 0xf807f != 0x18023 or k > 2: continue
    d = ((w >> 25 << 5 | (w >> 7 & 31)) ^ 2048) - 2048
    if d <= 360 < d + (1 << k): hits.append((i+0x8000,k,w>>20&31))
if hits != [(p,0,15) for p in (0x16fd6,0x16ffa,0x17014,0x1702e)]: raise ValueError(hits)
if int.from_bytes(b[0xd4:0xd8],'little') != 0x16fb6: raise ValueError('entry word')
print('PASS: four GP-relative stores and one entry word checked')
```
