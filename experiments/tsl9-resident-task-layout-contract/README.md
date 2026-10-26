# Task 配置的條件式 RAM 邊界

[English](readme.en.md) · [既有 SDK C/C++](../tsl9-resident-message-queue/README.md) · [callback CPU 寫入合約](../tsl9-tscb-store-contract/README.md)

本輪核對既有 C/C++ 的配置數學與 ABI，**沒有新增目標 CODE 或可刷 BIN**。兩份實際 C11／C++17 型別斷言物件完全相同，均為0 runtime bytes；原有2264-byte SDK 候選與 APP 覆蓋95.54%保持不變。

## 可以確認的數值關係

- 原 APP `0x19A54 → 0x19A66 → 0x19A70` 把 `0x0E3F` 寫到 stack+36。設定指標為 stack+16；依 little-endian 與實際編譯的 `ConnectNumber` offset21，App 提供的連線 byte 是 `0x0E`。**尚未證明到 SDK task 初始化時仍未被修改。**
- SDK 在 `0x43B90..0x43BBA` 計算 `n=3*((c>>2)+(c&3))+14`，申請 `576+6*n` bytes。對 byte 型別的 c，可由整數界線證明 n介於14與212、申請量介於660與1848，不發生 capacity-byte 或 allocator16-bit 截斷。
- 若 task 初始化仍讀到 c=14，則 n=29、申請750 bytes、allocator 對齊至752 bytes。配置分成576-byte 記錄區、116-byte 回呼表與58-byte 事件陣列，最後保留2-byte 對齊餘量。

## 條件式原始位址範例

原 APP 宣告 arena 起點 `0x2000418C`、長度 `0x7000`。**若這是有效 RAM，且 heap metadata 在首次配置前仍為初始化狀態**，可由真實 heap 程式推出：

| 區域 | 半開位址範圍 | bytes |
| --- | --- | ---: |
| 48個12-byte 記錄 | `0x200045B4..0x200047F4` | 576 |
| 29個回呼 word | `0x200047F4..0x20004868` | 116 |
| 29個事件 halfword | `0x20004868..0x200048A2` | 58 |
| 對齊餘量 | `0x200048A2..0x200048A4` | 2 |

原始 large block 可用 payload 為27600 bytes；436-byte 佇列／事件新增本體不改變這項配置。首次752-byte 配置的 split free node 在 `0x200048A4`，其 payload 起於 `0x200048AC`、長26840 bytes，終點是 sentinel `0x2000B184`。這些是數值推導，**不是實體 RAM 容量或排他所有權證明**。

在註冊索引確為0／1／2、bit介於0..15的條件下，`12*(16*task+bit)` 的完整記錄欄位落在576-byte 區域內。三個註冊 word 也可容納；事件 halfword 的一般界線還要求 registered-count≤capacity。

## 未證明的前提

SNV 初始化會在三個回呼註冊前執行。雖然最早有清零40-byte 狀態區的指令，**本輪沒有證明 `0x43C06` 讀到的 task-count 仍是0**，也沒有證明途中 heap、指標或容量未被回呼、IRQ、DMA 或 alias 修改。RAM 所有權、完整 stack／IRQ、實機 ROM／ISA／Flash／OTA 仍未閉合。

[型別斷言](layout_assertions.c)僅確認原始官方 header 的 offset、RV32 指標寬度與觀察到的12-byte 記錄布局，沒有函式、runtime object 或替代 provider。可考慮新增容量／註冊數一致性診斷，目前尚未實作。

證據：[verification-v1.json](verification-v1.json)、[summary.json](summary.json)、[固定輸入](spec-v1.json)。

## 重跑

需先具備 spec 與既有 SDK audit 所列原始 APP、SDK／header／指令參考及先前建置產物。SDK 原始輸入與 native 產物未隨此次提交提供，不會自動下載。使用固定雜湊的 Windows NDK LLVM，從專案根目錄執行：

```sh
python experiments/tsl9-resident-task-layout-contract/verify-v1.py --tool-dir "$LLVM_BIN" --trial abi-v2
```

trial 必須尚不存在；已有產物時省略 `--trial abi-v2`。早先 abi-v1 的 include-scope 檢查失敗試次保留本機；abi-v2 僅允許精確來源、固定雜湊的官方 header 與編譯器資源。沒有執行目標／HOST 模型／ISA 模擬、存取硬體或廠商 API。
