# 狀態控制與記錄傳輸

[繁體中文](README.md) · [English](readme.en.md)

新增十個完整函式，共 1,266B／452 指令；接上七個舊入口，沒有新增外部依賴。這是靜態重建里程碑，**本輪沒有產生韌體 BIN，也沒有存取硬體**。

| 證據 | 結果 |
| --- | --- |
| 原生 C11／C++17 | 獨立物件相同；89 個程式區域、59 RELA；12 個匯入皆由既有元件提供 |
| 整理後來源 | 126 個 C/H；198 組函式比較＋2 組獨立資料比較＝200 組／400 個物件 |
| 整合元件 | 34,956B code＋1,750B data；12,238 指令；2,954 FUNC、71 個零大小別名、2,316 RELA；仍缺 161 個提供者 |
| 原始位址 | 36,706 個已選 bytes 全部與官方 BIN 相同；2,967 個擁有者，101 段僅合併相鄰區域的配置 |
| 靜態跳轉位置 | 2,076 個直接跳轉；738 個呼叫返回位置；一般接續位置缺口為零 |
| 保存的 SDK 候選配置 | 另編譯兩個 48B 唯讀資料物件；無 FUNC、重定位或匯入，未連進韌體 |

已確認的指令行為：

- `960E` 在空指標判斷前保存配置結果，再寫七個 halfword 並提交。參數 3 不能視為已確認的 byte 容量。
- `AC0A` 保留完整寬度的輸入比較，呼叫後重新讀取 bit8，符合條件才排程 `AB02`；回呼直接送命令13，沒有再次檢查條件。
- `D2EE/D332` 保留低 byte 寫入後整個 halfword 重讀、狀態轉換命令102／103，以及兩次 `13D48` 呼叫。
- `10C7A` 建立兩 byte 負載與描述結構，保留配置、複製、送出及條件釋放的原始暫存器參數。
- `10D60/10E82/10EB2` 保留清理順序、指標重讀、三筆43B記錄、12B節點、逐 byte 進度，以及 return 後的其他分支。
- `167A6` 掃描127組鍵值與兩組35筆表格；保留所有匹配及每次表格指標重讀。

候選推論：本機保存的 WCH header 將預設槽位對應為 `GATT_bm_alloc`、`GATT_WriteCharValue`、`GATT_bm_free` 與 TMOS 函式；其 `tmos_memcmp` 在內容相同時回傳 TRUE。原生 `attWriteReq_t` 的大小12、對齊4、欄位位移0／2／4／8／9與原碼堆疊寫入相符。這些只證明**候選 header／profile 對照**，尚未證明裝置 ROM 身分與私有呼叫 ABI。該寫入槽位不是 `GATT_Notification`。

無法確認：實體 MCU／板上元件、ROM 內容、RAM 所有權與容量、中斷及非同步 ABI、時間單位與產品功能標籤，以及啟動／Flash／OTA 相容性。診斷 ELF 的 entry 為0，沒有 PT_LOAD。opaque 預設資料及17個 pool 資料目標仍未提供；完整驗證函式仍保持私有且未解決。本輪未執行 host model、ISA 模擬或目標程式。

[原始指令證據](evidence.json) · [語意合約](provider-contracts.json) · [量測摘要](summary.json) · [剩餘依賴](next-providers.json) · [功能候選](feature-candidates.json)

[整理後來源](../../src/native/receive/state_controls.c) · [原生編譯配方](../../experiments/tsl9-state-controls/spec-v1.json) · [來源驗證](../../experiments/tsl9-state-controls/verify-source-v1.py) · [整合配方](../../experiments/tsl9-state-controls/integration-v1.json) · [位址配置](../../experiments/tsl9-original-layout/spec-v29.json) · [靜態流程驗證](../../experiments/tsl9-original-layout/verify-flow-v32.py) · [SDK 唯讀配置驗證](../../experiments/tsl9-state-controls/sdk-write-layout-v1.json)

在 repo 根目錄，使用既有且雜湊符合的本機工具鏈與保留的產物：

```sh
python3 -B experiments/tsl9-original-layout/verify-flow-v32.py --replay experiments/tsl9-original-layout/build/state-controls-flow-v1
python3 -B experiments/tsl9-state-controls/verify-sdk-write-layout-v1.py --tool-dir "$LLVM_BIN" --sdk-header "$SDK_HEADER" --replay experiments/tsl9-state-controls/build/sdk-write-v1
```

`LLVM_BIN`、`SDK_HEADER` 由使用者指定本機路徑。原始建置收據與保存的 SDK header 留在本機，公開配方記錄其身分。以上指令只驗證靜態產物，不會燒錄。
