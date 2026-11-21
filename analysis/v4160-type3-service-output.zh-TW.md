# 類型 3：RAM 服務的輸出範圍與周邊基址

承接 [0x51f78 的 48-byte 工作區 P](v4160-link-type3-workspace.zh-TW.md)。這次只核對 V1.31 參考 carrier 的兩筆基址初始化、`0x63890` 的間接寫入，以及它呼叫的 RAM 服務；不假設已安裝此 ROM。

| 寫入者 | 目的地如何得到 | 初始化仍有效時 |
|---|---|---|
| `0x638ac` | `0x642c0` 存入 `0x2000353c` 的值為 `0x40024200`；呼叫時重新載入，對基址 +80 的 word 做 OR 128 | `0x40024250`，不是事件欄位 |
| `0x200022be` 的 13 處 word store | `0x642b4` 存入 `0x20003504` 的值為 `0x40024300`；此服務用它作為周邊基址 | 只寫基址 +0、4、24、28、32、36、40、44、48、52；部分位置寫多次 |
| 同服務的 16 處 byte store | Xwchc 的 `qk.c.sb`，目的基底皆為第三參數 a2，偏移依次為 0 至 15 | 呼叫 `0x63890(P,P+16,P+32)` 且參數正常傳遞時，恰為 `P+32..P+47` |

輸出不是無條件產生。`0x200023ac` 重新載入周邊指標並取基址 +4 的 bit 0；為 1 時重試，尚未寫任何輸出 byte。為 0 且後續存取成功時才寫滿 16 bytes，再返回。輸出階段多次讀周邊 word，不保證是同一瞬間的快照。上層倒序取最後三個 byte，因此最終送入比較的順序是 `P[47],P[46],P[45]`。

若兩個周邊槽保有初值、P 是與事件分離的有效 48-byte 配置，以上指令不會改到事件位址。這不是關於 `0x63890` 另一個子呼叫 `0x63eda`、非同步寫入、硬體輪詢必定結束或實機 ROM 的結論。

以下為可重跑的 store 盤點（Python 3，命令列參數是候選 carrier 路徑）。來源 RAM 映射以第一段啟動複製成功且未被改寫為前提；不能用標準浮點壓縮指令的寬度解釋 vendor byte store。

```python
import sys, hashlib
from pathlib import Path
b = Path(sys.argv[1]).read_bytes()
assert hashlib.sha256(b).hexdigest() == '133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22'
assert b[0x242a8:0x242c4].hex() == 'b747024093860730373700202322d7509386072037370020232ed752'
p, end = 0x252e, 0x2696  # RAM [0x200022be, 0x20002426)
words, output = [], []
while p < end:
    h = int.from_bytes(b[p:p+2], 'little'); n = 4 if h & 3 == 3 else 2
    if n == 2 and h & 3 == 0 and h >> 13 in (5, 6):
        base = 8 + (h >> 7 & 7)
        if h >> 13 == 5:
            assert base == 12
            output.append((h >> 12 & 1) | ((h >> 10 & 3) << 3) | ((h >> 5 & 3) << 1))
        else:
            assert base == 15
            words.append(((h >> 10 & 7) << 3) | ((h >> 6 & 1) << 2) | ((h >> 5 & 1) << 6))
    elif n == 4:
        w = int.from_bytes(b[p:p+4], 'little')
        if w & 127 == 35:
            assert w == 0x0007a023
            words.append(0)
    p += n
assert p == end and words == [0,0,40,44,48,52,24,28,32,36,4,4,0]
assert output == list(range(16))
print('PASS: 2 initializer bindings; 13 peripheral word stores; 16 ordered output bytes')
```
