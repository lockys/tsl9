# V4.1.60 0x102b2 value-event candidate

固定參考基準 `d6e2391030eee86cc73426c206c47c7750e00c57`；輸入為 `firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin`，長度 76800，SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`，位址基底 `0x8000`。這是輸入內容的固定基準，不依賴目前 HEAD 等於該 commit。

## 限定模型

輸入是已取出的 byte `p6`, `p7` 與舊的 `uint16_t old`，不是原函式指標或 RAM 模型。`raw = p6 | ((p7 & 1) << 8)`；`raw == 0x1ff` 時 value 為 0，否則為 raw。`out->value` 永遠為計算值，`out->store` 表示 `old != value` 時的條件 store 事件；store 為 0 時 value 仍是計算結果，並非宣稱有實際寫入。`out` 必須是有效可寫、非 volatile 的 struct 指標；C 僅寫該物件欄位，不讀輸入指標、不操作裝置記憶體或呼叫函式。模型不執行實際 GP store。

靜態視窗 `[0x10288,0x102b6)` 固定了完整指令 bytes：`0x1028c` / `0x10290` 載入 p[7]/p[6]，之後遮罩、移位及 OR；`0x102a4` 比較 0x1ff，`0x102a8` 為特殊值清零；`0x102aa` 讀取 GP+0x50 半字，`0x102ae` 相等則跳過 `0x102b2` 的半字 store。此解讀以進入該局部路徑、有效讀寫及原有控制流前提為條件；不是全函式，後續 `0x102b6` 起的行為、其他記憶體存取、呼叫、競態、可達性與所有其他 writer 均不在模型內。

## 離線驗證

```
python -I -S -B experiments/v4160-102b2-value-candidate/verify.py
python -I -S -B -O experiments/v4160-102b2-value-candidate/verify.py
```

先檢查整個固件長度及 SHA-256，另逐 byte 固定上述連續視窗。測試每個視窗 bit 的單一翻轉、截斷與窗外變動；模型測試所有 65536 組 byte，對每組測 old 的 0、1、0x1fe、0x1ff、0x200、0xffff、value 及其相鄰值（16-bit 環繞）。使用 unittest 而非 assert，因此 `-O` 仍執行檢查。

這是 Python 抽象模型相對於算術規格的自檢，以及實際固件 bytes 的靜態比對；不驗證 C 與 Python 一致、不編譯或執行 C，也不是 target differential、ISA 模擬或硬體證明。沒有使用 compiler、target、硬體、設定變更或網路。
