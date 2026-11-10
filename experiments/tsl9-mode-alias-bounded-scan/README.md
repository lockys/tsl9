# APP mode 直接 store／指標候選：有限 raw 掃描

離線對 ID-2966 V4.1.60 decoded APP 作可重播的**語法子集**盤點；這不是所有可能 writer 或 alias 的封閉證明。輸入 `firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin`，長度 `0x12c00`，SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`，名目基址 `0x8000`。整檔讀取用於 hash，包括下述排除區；語法掃描不進入排除區。

```sh
python -B experiments/tsl9-mode-alias-bounded-scan/scan.py
python -B experiments/tsl9-mode-alias-bounded-scan/test_scan.py
```

假設原始 PC 相對位址與記憶體環境，mode 名目地址 `0x2000bf39`；不等於已驗證實體 RAM 映射。掃描 `[0x8000,0x14056)`、`[0x14c8a,0x1a69c)`、`[0x1a6a0,0x1ac00)` 每個偶數位址的 LUI/AUIPC，配對同寄存器、16 bytes 內的 RV32 SB/SH/SW 或 C.SW，其計算區間涵蓋 mode；另容許緊鄰且同源同目的寄存器的 ADDI 形成 base，並列出 `bf36..bf39` 的 ADDI 指標。掃描器刻意不判斷中間寄存器覆寫、控制流或指令邊界；掃描範圍混合 code、data 和指令中間位元組，所有 raw 候選都必須另作分類。

| raw 形成者 → store | 分類 |
|---|---|
| `d000 → d010` | 假配對：`d004` 的 `lbu` 覆寫 a5，`d00c` 又形成新 a5；實際 `d010 sb a0,-199(a5)` 寫 `0x2000bf45`，不是 mode。見 `analysis/settings-state-inputs-2026-10-25/evidence.json`。 |
| `d05c/d060 → d06e` | 已知直接 byte setter，寫入 incoming A0 低 byte，沒有 182–184 檢查。 |
| `d0c4 → d0c8` | 已知 word store，涵蓋 `bf38..bf3b`，局部分支寫 mode 2、4 或 5。 |

ADDI 指標候選全為 `bf38`：`cefa/cefe`、`cfe0/cfe4`、`d05c/d060`、`d0fa/d0fe`。例如 `cfe8` 用第二個指標讀 offset 12；`d0fa` 則把指標作 A0 交由槽 `0x40048` 的間接尾轉移，A1=0、A2=16；callee 身分、寫入或清零效果未知。這些是生成候選，不代表指標完整傳播分析。既有較強的局部 CFG、原始 bytes 與 setter 呼叫證據見 [`tsl9-mode-state-writer-contract`](../tsl9-mode-state-writer-contract/README.md) 和 [`mode-direct-callers.zh-TW.md`](../tsl9-six-dependency-ledger/mode-direct-callers.zh-TW.md)。

**182–184：**已確認的局部 word writer 只給 2/4/5，既有 selected-CODE 五個直接 setter 呼叫的 A0 為 1、3、5；但 setter 本身允許任意 byte，未識別的 caller、指標傳遞、bulk copy、初始化、IRQ/DMA 或其他 writer 仍可能改變 mode。故不能證明 182–184 可達或不可達，也不能把掃描結果稱為全域 writer 清單。間接呼叫、跨函式與長距離 register propagation、不同目的寄存器的 ADDI、GP/SP 或載入的指標、其他 store 形式、排除區及其他韌體均未覆蓋；raw 候選數不能當作真實 writer 數。

測試驗證固定 hash、截斷與幾處 byte mutation 拒絕、兩個 raw 候選受 mutation 影響，及合成配對與排除邊界；不是對所有 mutation 或所有指令形式的證明。未執行目標、接觸硬體或產生韌體。
