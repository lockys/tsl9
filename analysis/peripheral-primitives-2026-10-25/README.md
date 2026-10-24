# 周邊原語與校正

[繁體中文](README.md) · [English](readme.en.md)

新增二十四個完整函式，共 **2,020B／677指令**，接上22個舊匯入，沒有新增外部依賴；剩餘數量由165降至143。本輪沒有新增資料、韌體 BIN 或實車控制。

| 靜態證據 | 結果 |
| --- | --- |
| 獨立 C11／C++17 | 物件相同；120個真實程式區域、64 RELA，皆為直接控制引用；外部19160由既有元件提供 |
| 整理後來源 | 130個 C/H；206組函式／程式單元比較＋2組獨立資料比較＝208組／416個物件 |
| 整合元件 | 40,474B code＋1,771B data；14,085指令；3,313 FUNC、71個零大小別名、14個唯讀物件、2,598 RELA |
| 原始位址 | 42,245個已選 bytes 全部與官方 BIN 相同；3,327個擁有者，106段僅合併相鄰區域的配置 |
| 跳轉位置 | 2314個直接跳轉；827個呼叫返回位置；一般接續位置缺口為零 |
| 語意見證 | 256項明列指令，保留16處原始 signed DIV |

已確認的指令行為：

- 188E2 依兩個編碼指標值，經既有19160切換512／1024遮罩。1892E 保留三個設定 word 的遮罩與存取順序。
- 189AE 保留完整寬度的 channel／rank 分支與原始可變位移。ADC 候選 helper 保留 word 讀取、位元門控與低16位結果，沒有新增範圍限制或截斷修補。
- 18F56 從1FFFF7E8／1FFFF7EC讀取兩個 word，擷取六個 bytes 寫入呼叫者緩衝區。這接上了啟動設定中候選 MAC 欄位的來源程式；沒有讀取實際識別值，實體記憶體屬性仍未確認。
- 時鐘 helper 保留 word／byte 的 RMW 寬度，包含1909E兩次獨立的零 byte 寫入。19220／19248 保留設定模式進出與先 high、後 low 的 halfword 寫入。
- 191C6 保留連續 high／low halfword 取樣、重讀 high、必要時再讀 low 的順序，不能據此宣稱實體計數器快照具原子性或單調性。
- 完整1929A..196C4校正函式保留 signed DIV／暫存器位移、狀態輪詢、依正負號取整、trim寫入、全部暫存器還原，以及 return 後的其他分支。S10從4開始，在退出檢查前減一並截成 byte；其他硬體等待仍保留原流程。
- 19764 保留GP+382縮放乘法、low／high比較值寫入、兩次獨立控制 RMW、狀態輪詢與最後清除；時間單位與干擾尚未證明。

C 程式仍含暫存器綁定與明確架構操作。本輪未執行目標、host model、ISA模擬或硬體。實體晶片、ROM／私有 ABI、時鐘輸入、校正收斂性、緩衝區／RAM／Flash容量、中斷及 OTA 相容性仍未證明。既有版本資料與14個唯讀物件保留；opaque預設資料及20個靜態內容引用尚未提供，完整驗證函式保持私有且未解決。診斷 ELF 的 entry 為0，沒有 PT_LOAD。

[原始證據](evidence.json) · [合約](provider-contracts.json) · [量測摘要](summary.json) · [剩餘依賴](next-providers.json) · [功能候選](feature-candidates.json)

[整理後來源](../../src/native/startup/peripheral_primitives.c) · [原生配方](../../experiments/tsl9-peripheral-primitives/spec-v1.json) · [來源驗證](../../experiments/tsl9-peripheral-primitives/verify-source-v1.py) · [整合配方](../../experiments/tsl9-peripheral-primitives/integration-v1.json) · [位址配置](../../experiments/tsl9-original-layout/spec-v33.json) · [流程驗證](../../experiments/tsl9-original-layout/verify-flow-v36.py)

在 repo 根目錄，使用既有且符合雜湊的本機工具與保留收據：

```sh
python3 -B experiments/tsl9-original-layout/verify-flow-v36.py --replay experiments/tsl9-original-layout/build/peripheral-primitives-flow-v1
python3 -B experiments/tsl9-peripheral-primitives/integrate-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-peripheral-primitives/build/component-v1
```

`LLVM_BIN` 為本機 LLVM bin 目錄；原始收據留在本機，以上指令不會燒錄。
