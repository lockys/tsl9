# 0x1316a 有限別名事件模型

純 Python 標準函式庫；從 repository 根目錄執行：

```sh
python -B experiments/v4160-1316a-alias-events/test_model.py
python -B -O experiments/v4160-1316a-alias-events/test_model.py
```

模型只描述假設前一個間接呼叫正常返回後的有限記憶體事件：先前呼叫載入 `word[0x40048]` 並清除目標最低 bit；其 callback 可改記憶體，包括下一個 slot 與 GP+84 所在的四個 bytes。接著依序執行 `sh 0x0fff,[0x2000c29e]`、`sb 1,[0x2000c2a0]`、`sh 0x0101,[0x2000c2a4]`，然後讀 `word[(gp+84) mod 2^32]`、讀 `word[0x4004c]` 並清目標最低 bit，最後計算指標加 12。第二個外部呼叫的內容、返回及後續尾跳不在模型內。

假設第一個 callee 正常返回，依 ABI 保留 s0、s1、gp、sp，堆疊有效且未破壞必要保存值；s0 為 `0x2000c29c`、s1 為 `0x40000`，無中斷或並行寫入。呼叫目標、其行為及可達性並未證實。模型中 byte 位址按 32-bit 回捲，little-endian；byte/halfword/word 分別須對齊 1/2/4 bytes，所有存取均假設一般可讀寫 RAM 且已初始化，未初始化讀取報錯；未模擬 MMIO、fault、未對齊硬體行為。可選 GP 必須讓 word 讀取對齊；回捲僅為數值模型，不代表實機可存取。

測例令第一個 callee 將設定區設為 `10 20 30 40 50 60 70 80 90 a0 b0 c0 d0 e0 f0 00`，並更改第二 slot。GP+84 恰為下列 word 位址時，直接 stores 後的小端結果為：

| 讀取位址 | bytes | word |
|---|---|---|
| `0x2000c29c` | `10 20 ff 0f` | `0x0fff2010` |
| `0x2000c2a0` | `01 60 70 80` | `0x80706001` |
| `0x2000c2a4` | `01 01 b0 c0` | `0xc0b00101` |
| `0x2000c2a8` | `d0 e0 f0 00` | `0x00f0e0d0`（不重疊） |

另測 callee 修改非重疊指標 bytes、byte load 與相疊 halfword store 的先後順序、GP 加法及指標加法回捲、錯誤對齊，以及省略 store/錯誤 endian mutants。固定原始 BIN 全長及 SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`，核對 `[0x1316a,0x131b6)` 指令 bytes；變異測試分別檢查 window 與整檔 digest。位址以分析 base `0x8000` 換算檔案 offset。

這些只是條件式 Python 事件模型與靜態 bytes pin，不是 C 語義、完整 binary、實際 callee、真實記憶體配置或硬體執行的驗證；沒有使用 compiler、target、simulator、network、外部設定或硬體。
