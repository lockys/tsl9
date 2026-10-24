# 記錄 helper 與週期回呼

[繁體中文](README.md) · [English](readme.en.md)

新增十二個完整函式，共 **910B／306指令**。接上十二個舊匯入，同時暴露十個新依賴，其中三個是靜態資料位址；剩餘145個。本輪沒有產生新韌體 BIN 或加入實車控制。

| 靜態證據 | 結果 |
| --- | --- |
| 獨立 C11／C++17 | 物件相同；68個程式區域、73 RELA、51個直接控制重定位、11組型別化位址引用 |
| 整理後來源 | 128個 C/H；202組函式比較＋2組獨立資料比較＝204組／408個物件 |
| 整合元件 | 37,372B code＋1,750B data；13,023指令；3,119 FUNC、71個零大小別名、2,468 RELA；145個真實匯入 |
| 原始位址 | 39,122個已選 bytes 全部與官方 BIN 相同；3,132個擁有者，112段僅合併相鄰區域的配置 |
| 跳轉 | 2,198個直接跳轉；771個呼叫返回位置；一般接續位置缺口為零 |
| 語意檢查 | 140項明列指令見證、29項 RAM 位址解碼 |

已確認行為：

- F47E 儲存請求 byte，保留完整寬度的請求／通知輸入，並在 F1C2 呼叫前後保留入口的另一旗標快照。回呼／取消依據該快照，沒有重新讀取狀態 byte。
- F4D0 以零判斷切換 BFA1，並以數值50排程自身。F578 先將 BFA6 加一截成 byte，再做無號門檻3比較，選135或1500。兩者都修改本機記錄位元並強制交給 F1C2。
- EF76 更新模式 byte，選取尚未提供的1A430／1A454／1A478位址及17／17／53計數。F016 保留 EE9A 前後的寫入，包含不使用該呼叫的結果。
- F058 依設定選25／40／32，或取消後直接呼叫 EDF2。DE82 將完整輸入傳為排程參數。A6AA、B0B0、B572、B594、18218 保留各自的清除／寫入／正規化／遮罩順序。

C 程式仍包含暫存器綁定與明確的私有架構操作，尚未完整還原原始碼或證明一般／非同步 ABI。排程數值的時間單位，以及座椅／免打擾等功能名稱仍未知。

七個新 helper／回呼實作與三份表格內容仍未提供。剩餘引用分為121個直接提供者名稱、24個純位址名稱，以及1個混合名稱 EDF2（已計入直接名稱）。原有 opaque 預設資料與17個靜態 pool 仍未提供。

實體 MCU／板上元件、安裝中的 ROM、RAM 所有權／容量、中斷／啟動／Flash／OTA 相容性仍未證明。診斷 ELF 的 entry 為0，沒有 PT_LOAD；本輪未執行目標、host model、ISA 模擬或硬體。完整驗證函式保持私有且未解決。

[指令證據](evidence.json) · [合約](provider-contracts.json) · [量測摘要](summary.json) · [剩餘依賴](next-providers.json) · [功能候選](feature-candidates.json)

[整理後來源](../../src/native/receive/record_helpers.c) · [原生配方](../../experiments/tsl9-record-helpers/spec-v1.json) · [來源驗證](../../experiments/tsl9-record-helpers/verify-source-v1.py) · [整合配方](../../experiments/tsl9-record-helpers/integration-v1.json) · [位址配置](../../experiments/tsl9-original-layout/spec-v31.json) · [流程驗證](../../experiments/tsl9-original-layout/verify-flow-v34.py)

在 repo 根目錄，使用符合雜湊的本機工具與保留收據：

```sh
python3 -B experiments/tsl9-original-layout/verify-flow-v34.py --replay experiments/tsl9-original-layout/build/record-helpers-flow-v1
python3 -B experiments/tsl9-record-helpers/integrate-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-record-helpers/build/component-v2
```

`LLVM_BIN` 為使用者的本機 LLVM bin 目錄。原始收據與已取代試驗留在本機；以上指令不會燒錄。
