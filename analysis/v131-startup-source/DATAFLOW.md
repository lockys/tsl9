# V1.31 缺失末 word：有限靜態資料流

以本目錄固定 SHA-256 `11d849ac3333535b31dae1941afd8d59fa99ad7760de5c1e64bdfcc8c0024bb5` 的完整 HEX 為輸入；不是實機 resident。`dataflow.py` 重用入口與 helper 指令解碼 gate，並核對下述完整 setter／runner 指令視窗及關鍵讀寫欄位。RAM 指令位址依第一段 copy 的 `0x402b0 → 0x20000040` 換算；須假設 copy、取指、控制流和記憶體均正常，且指令未被改寫。

- 第二段 inclusive copy 最後從 `0x6eb2c` 讀 word，再寫 `[0x20002ef8,0x20002efc)`；來源四 bytes 在完整 HEX 無紀錄。缺失不等於零、FF 或實體 fault。嚴格捕獲來源模型在讀取處停止，尚未寫入，也未進 zero。
- **若**該讀寫和返回均正常，後續 zero helper 的首個 store（來源 PC `0x402a8`，條件 RAM PC `0x20000038`）將 `0x20002ef8` 寫零。此覆寫不能消除先前讀取或其失敗風險，也不能保證無中斷、別名或其他觀察者在兩者之間讀取。
- 後續選定視窗：setter 來源 `[0x409fa,0x40a10)`／RAM `[0x2000078a,0x200007a0)`，`0x2000078e` 將 A0 寫入該 word；非零時設 `0x20002efc` byte，零值不清 flag。runner 來源 `[0x40a10,0x40a40)`／RAM `[0x200007a0,0x200007d0)`，`0x200007a4` 讀該 word，非零時透過它呼叫；返回後重新讀 flag，若為零則 `0x200007c4` 清除 word。呼叫、返回及這些函式的實際可達性均未證實，callback 可能有副作用。

## 清零前的條件式指標傳播

在最後 READ32 成功、store 完成，且 zero 首次 store **之前**有控制流進入 runner、又無其他寫入該 slot 的條件下，固定的資料流是：來源 `0x40286`（RAM `0x20000016`）讀到的 word → `0x4028c`（RAM `0x2000001c`）寫入 `0x20002ef8` → 來源 `0x40a14`（RAM `0x200007a4`）載入 a4 → `0x40a22`（RAM `0x200007b2`）非零分支 → `0x40a24`（RAM `0x200007b4`）`c.jalr a4`，目標為 a4 清除最低 bit。runner 實際在這個時間窗可達、控制如何轉移、讀取成功與 callback 安全性都**未證明**；正常固定順序則先進 zero，不能把上述條件當成已發生。

對每一個 byte，純符號比較全零 word 和只改該 byte 的另一個 word：低 byte 選 bit 1，其餘各選 bit 0，均可改變非零判斷及 jalr 目標。這些是假設反例，不是缺失內容、記憶體供應或原機值；因此即使僅一 byte 未知，也不能普遍排除指標敏感性。但並非每個變化都改變目標（jalr 清 bit 0），也未建立該值作為**容量**使用的固定路徑，不能宣稱容量敏感性已證明。

這是**選定視窗**審計，不是全程式掃描或無其他讀者證明；間接指標、IRQ、DMA、別名、其他程式碼與實際執行順序均未閉合。不得據此補值、放寬 strict link／startup gate 或視為可刷機。未接觸硬體。

重跑（負測刻意繞過輸入 hash 以測試指令 gate；另測 hash 拒絕）：

```sh
python -B analysis/v131-startup-source/dataflow.py
python -B analysis/v131-startup-source/test_dataflow.py
```
