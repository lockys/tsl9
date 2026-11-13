# V4.1.60 `0x105c4`：有限 caller 證據

離線靜態檢查，非完整 caller graph、ABI 還原或執行結果。在倉庫根目錄執行：

```text
python -I -B experiments/v4160-105c4-callers-bounded-next/scan.py
python -I -B -O experiments/v4160-105c4-callers-bounded-next/scan.py
python -I -B experiments/v4160-105c4-callers-bounded-next/test_scan.py
python -I -B -O experiments/v4160-105c4-callers-bounded-next/test_scan.py
```

工具使用標準函式庫；測試需實驗目錄可寫，會建立暫存目錄和 `.pyc`，異常中斷可能殘留。固定完整 76,800-byte BIN 與 manifest、owner、spec、candidate SHA-256；具體路徑和 pins 見 `scan.py`。假定 BIN offset 0 映射至 `0x8000`，並不因此證明原始載入映射。兩次 Python 模式重播，對每一 byte offset 解碼完整 JAL（76,797 個窗口）及 RV32C C.JAL（76,799 個窗口）；各自到 `0x105c4` 的 raw 命中均為 **0**。掃描包含奇數位址、重疊窗口和資料，不能推定指令邊界或可達性。未掃 JALR、C.JALR、C.J、其他控制流、非相鄰取址、其他映像或 runtime 修改；零命中不證明沒有直接或間接 caller。

`0x105c4` 的固定 12 bytes 是 `034535007115133515008280`：`lbu a0,3(a0); c.addi a0,-4; sltiu a0,a0,1; c.jr ra`。讀取成功時結果為 byte 是否等於 4。本段只明確寫 a0、讀一 byte，未寫記憶體；不能由此確立原始 C 原型、合法記憶體或 caller ABI。純 C candidate 的 `volatile` 和參數／返回型別是實驗選擇。

固定 owner 中有兩筆對目標的文字層 `R_RISCV_PCREL_HI20` 引用；spec 的配對 PC 是 `0x1094c`、`0x10be4`，實際 BIN 的 AUIPC/ADDI 分別將 `0x105c4` 置入 a0 和 a3。這些是**取址**而非直接 call，且並非全工程引用清單。受限窗口中：

- `0x10944` 將入口 a0 複製到 a1，取址後以 JAL 前往 `0x1083c`；若依該路徑連續進入，`0x1083c` 將指標移到 a0 並 `c.jalr a5`，目標為 `0x105c4`。
- `0x10bc2` 在先前呼叫 `0x107c6` 正常返回且 s0 保持時，後續取址至 a3、透過 a4 傳遞保存的入口值並尾跳；`0x107c6` 的窄窗口把 a4 移到 a0，然後 `c.jalr a3`。這些條件與有限窗口不證明路徑可達或所有外部呼叫副作用。

測試窮舉 C.JAL 的 2048 個位移，涵蓋 JAL 邊界、32-bit 回繞、短尾及奇數位址；另在完整 BIN 副本不同位置注入樣本並逐次核對 decoder 實際訪問、用固定的正負 C.JAL 向量與真實 BIN 中三條 JAL 作對照、測輸入變更和 stale pyc。獨立向量源自本機 rasm2 6.2.4 的**反匯編**：`0122` 於 PC `0x1000` 目標 `0x1100`，`7d3f` 於同 PC 目標 `0xfbe`；未使用 rasm2 執行 target，測試也不依賴它。

測試以固定 hash 的 `scan.py` source bytes 直接 compile/exec，避免舊 pyc；CLI 本身是一般 Python 腳本。這些資料是靜態、受限證據，不證正式 split／relocation 全圖、記憶體狀態或完整 BIN 等價。
