# OTA 處理器縮減：568-byte 共享 C/C++

[English](readme.en.md)

本輪以真實 compiler IR 與原碼共用出口為依據，將 OTA 命令的原生 C11／C++17 元件由 776 bytes／285 指令／112-byte frame，縮為 **568 bytes／193 指令／48-byte frame**。八個暫存器 I/O、memory clobber、volatile 操作、U／S／W／R／E 行為與 W 回覆投影均保留。原本範圍仍是 530 bytes，新元件多 38 bytes；**未連結、未納入 BIN，也未驗證可刷寫。**

## 實際變更

原 native `oh_port` 把參數陣列與會傳往 opaque callee 的兩-byte 回覆陣列放在同一個物件。新的 C 將回覆陣列改為 wrapper 自有的 `volatile uint8_t[2]`，port 保存其指標，讓參數物件不因回覆指標而整體逃逸。這個單一生命週期變更的實測中間元件是 592 bytes／196 指令／48-byte frame。

再依原碼的 `0x9D7A`、`0x9DB4`、`0x9DF4` 三個共用回覆出口，使用明示 C 標籤合併 small／packet／page 回覆位置。參數 setter 的先後順序、各命令的 mask、來源 PC 與 callee 停止行為仍由共享來源及獨立 fixture 核對。最終物件有九個真 UND 與 20 筆 RELA：十二個 JAL、四組 HI／LO；另有一個 slot `0x4004C` 間接呼叫。沒有以 ABS 位址、stub、偽造 FUNC 或原始指令補缺。[靜態組語觀察](allocation-observations.json)記錄 SP 定址記憶體指令由 111 個降為 23 個；它包含保存／還原與回覆存取，不是動態成本或可刪 spill 數量。

程式：[共享 C/C++](../../experiments/tsl9-v4160-ota-handler-compact/README.md)。證據：[implementation](implementation/README.md)、[獨立 HOST／原生及來源差異核對](ABI-review/README.md)、[UID 與候選 copy callee](callee-review/README.md)。[計畫](plan.zh-TW.md)保留完整目標及停止條件。

## 否定結果與前輪更正

先前三份分析 README 誤把四次 quarter 執行寫成四個展開的靜態呼叫點。實際 776-byte 物件只有一個 quarter JAL 與 backedge；原有獨立 ABI metadata 亦記錄一個。新的「停用展開」探針仍為 776 bytes／285 指令，沒有增益。最終來源移除該無效 pragma，沒有採用 compiler flags 搜尋來湊大小。詳見[前輪更正](../v4160-ota-handler-2026-10-22/ERRATA.md)及本輪獨立證據；舊 sealed 檔案未改寫。

舊 parent seal 還綁定了前輪六份首頁／里程碑文件。這輪正常更新那些文件後，舊 parent checker 的「當時全域文件」檢查不能當成目前通過；其 seal 成員與程式來源仍保持不變，也未放寬舊 checker。六份文件可在前一提交 `ea92e46` 重現原 hash，見[歷史文件脈絡](baseline-context.json)。本輪 parent seal 改綁定版本化 scope 與程式證據，不把會持續更新的首頁當作不可變依賴。

## 證明範圍

HOST 驗證執行的是自有 C/C++ 與合成記憶體／callee provider，執行檔先經不可變 machine guard；沒有執行或模擬 RV32。原生核對讀取真正 ELF／IR／MD／完整指令與來源工具身分。中間探針的摘要與來源身分保留，不把沒有移交的 build 路徑當成可攜 replay。

UID App 函式先要求 14-byte 長度，經 builder 及 fresh slot `0x4004C` 產生數值，再比較並回傳 0／1。兩份官方 ROM 候選的 copy leaf 可提供有條件的參數／保存證據，但不等於已安裝 ROM。這輪沒有根據局部 callee 無讀取就刪除 ambient 暫存器。

新的兩-byte 回覆仍是 private C 配置，不等於原碼的 live SP+12。實際新回覆在 SP+6／7，保存 RA 與 S0..S8 共十個 slot；SP+12 已是 S7 的保存位置，不能盲目把回覆綁回該處。frame 同為 48 bytes 也不證明保存位置、scratch、S／SP／RA／GP、alias 或非同步契約相同。38-byte 差距、存活來向／continuation 與完整映像配置尚待處理。

完整 TX 實驗映像 SHA-256 `28697eab551bd9b3ca74a69c44db24fc02e07bedbb5bf02380e4bcb1a390ce89` 不變，仍只將十三個原始範圍共 930 bytes 以可讀 C/C++ 與明示 ABI 層提供。這不是功能完成率；新增獨立元件不計入完整 BIN 的覆蓋。完整目標與硬體／ROM／BOOT／IRQ／Flash／BLE OTA／復原缺口見[既有盤點](../v4160-ota-handler-2026-10-22/status.zh-TW.md)。離線封包預檢與等待原因顯示仍是提案。

## 重跑

```sh
python3 -B experiments/tsl9-v4160-ota-handler-compact/verify_host.py --project-root /absolute/re-tsl9 --language both --build-root /absolute/re-tsl9/experiments/tsl9-v4160-ota-handler-compact/build/new-host
python3 -B analysis/v4160-ota-handler-compact-2026-10-22/implementation/verify_native.py --project-root /absolute/re-tsl9 --tool-dir /absolute/llvm/bin --language both --build-root /absolute/re-tsl9/experiments/tsl9-v4160-ota-handler-compact/build/new-native
```

輸出目錄只可新建。各 scope 區分預設 metadata 與明示實際產物 replay。實測環境為 Windows；Python／POSIX shell 入口不代表 Linux／macOS 已實測。
