# 中斷暫存器 C 核心：獨立行為審查

凍結的審查對象為 `experiments/tsl9-v4160-interrupt-registers/src/interrupt_registers.c`、`interrupt_registers.h`、`irq_io.h`，重建原始 0x9A42 及 0x19124／0x19142／0x19160／0x1917E 的正常邊界輸出要求。沿用的原始來源證據涵蓋 264 位元組、94 條指令並拒絕 94 個原始控制。本輪只執行自行撰寫的 C／C++ host 程式，明確使用 `TSL9_IRQ_REGISTERS_HOST_TEST=1` 替換 I/O，不執行原始或重建 RV32 韌體。

## 獨立檢查的輸出

各 helper 對正確 RCC 位址作新的 READ32，再 WRITE32。enabled 任意非零值選 OR，零值選 AND 配合 32 位元反遮罩。正常輸出為：

| 分支 | A0 | A1 | A4 | A5 |
|---|---|---|---|---|
| enabled 非零 | before OR mask | 完整 enabled 位元 | 0x40021000 | before |
| enabled 零 | before AND NOT mask | 完整 enabled 位元 | before | 0x40021000 |

基址是 **0x40021000**，不是個別暫存器的完整位址。測試包含 2、3、0x100、0x7FFFFFFF、0x80000000、0xFFFFFFFF 等非標準非零 enabled，A1 不能只保留真假值。

主初始化 oracle 明列二十個有序外部效果：CSR clear、六組獨立 READ32／WRITE32、保留原始寬度的六次 PFIC 寫入、最後 CSR set；另核對六次 helper 與最終初始化輸出觀察。重複 RCC 讀取刻意給不同取樣。最終 A0 必須來自**最後一次** 0x4002100C 清除讀取；A1=0、A4=128、A5=0xE000E000。Fake 環境還在操作間改變 CSR 其他位元，確認最後是設定當時狀態，而非恢復入口快照。

C11 與 C++17 各通過 **4 組／3820 案例／138312 斷言**：3168 種 helper 輸入／遮罩／enabled 組合、256 個主初始化新取樣情境、384 個單位元 helper 案例及 12 個 CSR／邊界情境。Callback 精確核對型別、順序、數值位址、值與四個正常輸出欄位，先確認邊界才存取 host 資料；周邊數值位址不會被轉成 host 指標。

每種語言實際編譯並由斷言拒絕十八種修改，合計 **36 個已編譯負向案例**，涵蓋 enabled 正規化、只認 enabled=1、A4／A5 誤用完整位址、以改寫值取代取樣輸出、錯誤 helper 位址、快取讀取、先寫後讀、錯誤寬度、主輸出 A0／A1／A4／A5 或回傳值錯誤、CSR 遮罩／順序及漏掉最後 PFIC 寫入。編譯失敗不計為行為拒絕。

在本 host 數值 I/O／正常輸出介面內，未發現來源語意不符。`receipts/` 核對實際編譯器、三份凍結來源、測試邊界、獨立 oracle、runner、helper 與執行檔／變異結果。歷史 host EXE、object、日誌及變異來源留在工作封存排除的 `build/`；發布 receipt 不表示同時提供那些二進位檔。

## 原生與放置限制

A0／A1／A4／A5 在此是 **host 輸出觀察欄位**，不是實體暫存器擷取。測試不能證明 production inline assembly 或配置 profile 保存 A2／A3、正確產生原生 A1、沒有堆疊改變、保存其他暫存器或符合 IRQ／入口 ABI；這些需要獨立原生 object／CFG／編碼檢查，不能從 host 通過、void callback 或 C 回傳值推得。

先前放置來源審查列出八段、合計 540 位元組及 helper 呼叫端與未知間接目標。舊一般 C 的 118 位元組初始化與 22 位元組 helper 已有暫存器 ABI 不符證據，不能當成可用空間；新核心也仍需證明實際原生暫存器、大小、入口／延續／參照與最終放置，才可整合。本輪不證明 BIN、硬體型號、IRQ／ROM 或 OTA 相容。

```sh
python3 run-review.py --project-root /絕對路徑/project --language c
python3 run-review.py --project-root /絕對路徑/project --language cpp
```

Python runner 沿用 portable compiler locator，每次產生獨立 build，並在 `build/` 外保存位元組相同的 selected receipt。本次實際使用 Windows／MSVC，不宣稱 Linux／macOS 已執行；不連網、不存取硬體、不模擬指令集、不執行韌體。

`receipts/parent-c.json` 與 `parent-cpp.json` 另保留主實作完整來源加 ABI 反證的 host 執行，每種語言 4 組／9184 案例／246384 斷言，與本獨立套件分開計算。原生編譯審查的四個有限候選配置均需要堆疊狀態，未通過預定原生限制，native verification 仍為 false。唯讀 `check-review.py --project-root <project>` 核對目前凍結輸入、三個不可變 peer seal 及四份 receipt，不重跑測試；綁定成功不會將 host 結果提升成原生證明。
