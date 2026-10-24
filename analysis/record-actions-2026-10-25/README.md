# 記錄動作與共用修改器

[繁體中文](README.md) · [English](readme.en.md)

新增十九個完整函式，共 **1,506B／479 指令**。十九個舊匯入已有真實程式碼，同時新確認五個 helper／回呼依賴，剩餘數量由161降至147。本輪沒有產生韌體 BIN，也沒有存取硬體。

| 靜態證據 | 結果 |
| --- | --- |
| 獨立原生 C11／C++17 | 物件相同；97個程式區域、79 RELA、71個直接控制重定位、四組回呼位址引用 |
| 全部整理後來源 | 127個 C/H；200組函式比較＋2組獨立資料比較＝202組／404個物件 |
| 整合元件 | 36,462B code＋1,750B data；12,717指令；3,051 FUNC、71個零大小別名、2,395 RELA；147個真實匯入 |
| 原始位址 | 38,212個已選 bytes 全部與官方 BIN 相同；3,064個擁有者，107段僅合併相鄰區域的配置 |
| 跳轉位置 | 2,147個直接跳轉；754個呼叫返回位置；一般接續位置缺口為零 |
| 語意 | 171項明列指令見證與51項靜態位址解碼檢查 |

C 程式保留暫存器綁定運算、volatile 記憶體操作，以及私有 ABI 所需的明確架構操作。這還不能證明一般呼叫 ABI，也不代表完整還原原始碼。

已確認行為：

- `9508/954E/95BC/96A2` 分別以3／6／4／8呼叫9410，在判斷空指標前保存結果至2000BECC，再寫入合約記錄的 halfword 序列並交給93AA。這些參數的 byte 容量意義尚未證明。
- `BD0A` 將狀態 byte 與完整寬度輸入比較，只有不同才進入 D052／171DE 路徑。`BD5A/BD6E/CC78` 保留 byte 寫入與呼叫順序。
- `CC8C/D3C6/F672/F97C` 保留低 byte 儲存與完整寬度通知輸入的差別，以及條件清除和後續13D48呼叫。
- `F1C2` 是共用記錄修改器，保留旗標讀取順序、一次性清除、呼叫後重讀、記錄位元修改與強制提交。旗標 BF91 值為2時會呼叫 DE82(1000)，數字單位仍未知。
- 四個 wrapper 將原始 A0／A1、RAM 指標、旗標 byte 與回呼位址交給 F47E。F750／F796 先強制對記錄2000C1D0呼叫 F1C2，再依條件將完整原始輸入交給9792。

DE82、F058、F47E、F4D0、F578 尚未實作；後兩者只有回呼位址引用，沒有用位址取代其實作。剩餘依賴包含127個直接呼叫名稱與20個純位址名稱，已沒有同時被直接呼叫及取址的未實作提供者。

無法確認：座椅／免打擾等產品名稱、實體 MCU／板上元件、安裝中的 ROM、私有與非同步 ABI、RAM 保留區／容量／所有權，以及 IRQ／啟動／Flash／OTA 相容性。opaque 預設資料與17個靜態 pool 仍未提供；完整驗證函式保持私有且未解決。診斷 ELF 的 entry 為0，沒有 PT_LOAD；本輪沒有執行目標、host model 或 ISA 模擬。

[指令證據](evidence.json) · [語意合約](provider-contracts.json) · [量測摘要](summary.json) · [剩餘依賴](next-providers.json) · [功能候選](feature-candidates.json)

[整理後來源](../../src/native/receive/record_actions.c) · [原生配方](../../experiments/tsl9-record-actions/spec-v1.json) · [來源驗證](../../experiments/tsl9-record-actions/verify-source-v1.py) · [整合配方](../../experiments/tsl9-record-actions/integration-v1.json) · [位址配置](../../experiments/tsl9-original-layout/spec-v30.json) · [流程驗證](../../experiments/tsl9-original-layout/verify-flow-v33.py)

在 repo 根目錄，使用既有且符合雜湊的本機工具鏈與保留收據：

```sh
python3 -B experiments/tsl9-original-layout/verify-flow-v33.py --replay experiments/tsl9-original-layout/build/record-actions-flow-v1
python3 -B experiments/tsl9-record-actions/integrate-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-record-actions/build/component-v2
```

將 `LLVM_BIN` 設為本機 LLVM bin 目錄。公開配方記錄身分，原始建置收據與已被取代的試驗留在本機。以上檢查不執行韌體，也不燒錄。
