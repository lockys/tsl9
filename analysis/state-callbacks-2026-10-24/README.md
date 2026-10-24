# 狀態讀取函式重建

本頁保留先前來源階段快照；目前已整合，請見[狀態事件與 callback 整合證據](../state-callback-integration-2026-10-24/README.md)。

[English](readme.en.md)

新增 [C/C++ 來源](../../src/native/receive/state_leaf_reads.c)：27 個事件讀取入口加上 2 個實際輔助函式，共 **472 bytes／153 條指令**。C11 與 C++17 皆通過逐指令檢查：438 bytes 非控制指令直接相符，10 個分支／呼叫以靜態原位址編碼後，全部原始 bytes 相符。這不是執行或模擬結果。

[指令證據](leaf-evidence.json) · [編譯規格](../../experiments/tsl9-state-callbacks/spec-v1.json) · [結果與雜湊](summary.json) · [重查程式](../../experiments/tsl9-state-callbacks/verify-source-v1.py)

| 已確認範圍 | 證據位置 |
| --- | --- |
| A976、A9BC、E058 的條件位元組合與原讀取寬度 | 原始 BIN 同名位址；來源內 45 個完整基本區塊 |
| B082 的兩個輔助呼叫、16-byte 堆疊及 RA 保存／還原 | B086→A968、B08E→8202、B0A8 共用返回 |
| GP 相對位址回傳與 byte／halfword 讀取 | D190／D754 回傳位址；10402／10408 分別讀 GP+80／GP+82 |
| 來源整理與主元件保留 | 96 個 C/H、69 個 code units；含獨立指標資料共 140 組比較／280 物件；舊 136 組結果及 817 筆產物記錄完全保留 |

這批來源**尚未併入啟動主元件**。現有主元件仍是 9836B code＋516B data、698 RELA、82 UND，雜湊與既有版本相同。新清單是精確的 95→96 檔延伸；舊檢查器未修改，不宣稱舊的整份 95 檔 manifest 重播已適用新清單。

接續整合前，已對既有 state-access 336B、feature-callback 314B、state-events **v2** 1308B 做完整原始碼原位址 byte 稽核，兩種語言均通過。整合時 state-access 的 82A8–82D2 共 42B 已由主元件持有，必須核對兩個原始轉移後避免重複加入；state-events 的 13C4E 不可只保留 24B 入口而捨去後續流程。

有價值的新功能候選：只讀狀態診斷，讓欄位顯示其來源位址、原始值與已確認／推測標記，並以韌體 SHA-256 區分 App 顯示相同版本的不同檔案。這是設計候選，尚未實作；欄位意義、記憶體映射及安全讀取條件仍須證明。

MCU、installed ROM、RAM 擁有權、私有 ABI、原址配置、中斷與 OTA 相容性仍未證明。未執行目標、模型或 ISA 模擬，未連線、未接觸硬體、未產生或燒錄 BIN。歷史隱私問題尚存，未 commit／push；完整目標保持進行中。
