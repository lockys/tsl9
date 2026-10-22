# callback 的暫存器與 live GP 重建

[English](readme.en.md)

本輪以原始 `0x8614..0x888C` 的 632-byte callback 為依據，保留可讀 C/C++ 邏輯，修正原生暫存器橋接與保存順序。正式 C11、C++17 均編譯、連結成 **624-byte／223 條指令** 的元件，未執行 RISC-V、未連接硬體，也沒有新增完整 BIN。

## 已確認的進展

- 先明確保留 x26／x27（S10／S11），將舊 658-byte 診斷降為 656 bytes；原始直接指令沒有使用這兩個暫存器。這不證明不透明 callee 的保存契約。
- 原 656-byte 元件有十六次 GP 快照，共 32 bytes。新的窄橋接改在六個使用位置讀取當下的實體 GP，移除入口與十五次不透明呼叫後的冗餘快照，產出 624 bytes；沒有假設 ROM 保存 GP。
- 真實原生產物使用 48-byte frame、十一組來源 register／slot、十五個間接呼叫；沒有 S10／S11、直接 SP0 spill 或 GP 寫入。
- 明示 postpass 只交換開頭兩個既有 2-byte stack store，恢復 S0／RA 的相對保存順序。其他 ELF bytes、符號及 relocation metadata 完全不改寫。
- 來源審查及獨立 ABI 審查都重讀正式 C／C++ 的編譯前後產物、編譯命令、標頭依賴及唯讀重播。HOST accessor 與舊 mutable GP 欄位的對應已核對；**本輪沒有重跑 HOST 行為測試**。

來源位於 [C/C++ model](../../experiments/tsl9-v4160-callback-registers/README.md)。各項證據與限制分別見 [實作](implementation/README.md)、[獨立來源](source-review/README.md)、[獨立 ABI](ABI-review/README.md)、[live GP](gp-plan/README.md)、[保存順序](entry-plan/README.md)及[原始尾區](tail-plan/README.md)。

## 尚未證實的相容性

624 小於 632 只代表數值上放得下，不代表可整合。原最後 8 bytes 是三條可執行指令；完整尾區所有權尚未證明。原碼在首次保存前還有額外指令，新元件的十五個呼叫返回 offset 集合也不同。最後一個 halfword read 被編譯成 LH：後續 low16 store 可對應，但中間實體 GPR 的 sign-prefix 不同。完整入口 prefix、未知 scratch registers、ROM／返回 ABI、原位配置、BOOT／中斷及硬體 OTA 均未閉合。

原有十三個可讀函式範圍的完整 TX 實驗映像維持不變，SHA-256 `28697eab551bd9b3ca74a69c44db24fc02e07bedbb5bf02380e4bcb1a390ce89`；它仍使用舊 callback 承載。**本輪的 624-byte 元件尚未納入該 BIN，也尚無驗證可燒錄的重建 BIN。**

## 重跑證據

```sh
python3 -B analysis/v4160-callback-registers-2026-10-22/implementation/check.py --project-root /absolute/re-tsl9
python3 -B analysis/v4160-callback-registers-2026-10-22/implementation/verify_native.py --project-root /absolute/re-tsl9 --tool-dir /absolute/llvm/bin --language both --build-root /absolute/re-tsl9/experiments/tsl9-v4160-callback-registers/build/new-native
python3 -B analysis/v4160-callback-registers-2026-10-22/ABI-review/review-ordered.py --project-root /absolute/re-tsl9 --pre /absolute/re-tsl9/experiments/tsl9-v4160-callback-registers/build/new-native/pre/c --folder /absolute/re-tsl9/experiments/tsl9-v4160-callback-registers/build/new-native/ordered/c --receipt /absolute/re-tsl9/experiments/tsl9-v4160-callback-registers/build/new-review.json
```

`check.py` 是來源／中繼資料核對，不是新編譯。正式 runner 必須使用已核對身分的 LLVM；輸出路徑只可新建。實際來源審查另需官方本機 BIN 與 `--receipt .../ordered/c/verification.json`，C++ 使用 `cpp`；見各子目錄說明。已核對的環境為 Windows；本輪沒有取得 Linux／macOS 或實機結果。

後續值得研究的功能仍是離線 OTA 封包預檢與更新等待原因說明；它們是提案，尚未作為硬體功能實作。本輪優先補足原機執行契約，不以新功能取代必要相容性證據。
