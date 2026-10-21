# TX C/C++ HOST 效果獨立審查

[English](readme.en.md)

本份獨立審查 `experiments/tsl9-v4160-ota-tx/src` 的共用可讀演算法。參考為已封存的原始 `0x8A56..0x8B6E`、280 bytes／96條指令契約，透過旁邊的 `source-review-v2` 重查。一般 C 介面是否能重現原始每個機器暫存器或指令邊界，仍屬於其他證據層級。

獨立 oracle 實際編譯 C11、C++17 HOST 版本；每種語言選定結果均通過 **4組、31案例、78,283檢查，以及14個分別編譯的語意錯誤控制**。數值位址只是稀疏合成 byte map 的索引，沒有解參考裝置位址。預期有序效果由明列來源契約與 fixture 資料產生，獨立於實作 callback trace；記憶體會重新讀取，包含先前寫入與後續來源、保存堆疊字的別名。本份是具名演算法 oracle，沒有 CPU state、opcode step 或 ISA 解譯器。

| 組別 | 案例 | 證據 |
| --- | ---: | --- |
| 一般 lane0／lane1 |14|長度0、1、2、7、255、256、1039；header、payload、加總校驗、metadata、尾端參數與讀寫寬度|
| Guard 與選擇失敗 |7|1040／65536／UINT32_MAX 在效果前被拒絕、不匹配 handle、sentinel、gate2失敗仍A2=1、第一個結果殘留|
| 即時狀態與別名 |6|gate1改變GP／S0／S1／S2／S3；gate2取得gate1的A2／A3與新slot；初始guard後長度1041、65536有限前綴；向前來源重疊；SP移位及metadata／frame重疊；重新讀取frame改值|
| 未知與不透明控制 |4|payload讀取未知、拒絕返回的memory callback修改GPR、gate HALT、委派尾端TRANSFER|

記憶體 callback 可修改合成記憶體，但不能修改模型暫存器或 known mask；具名不透明 gate 可修改 GP／SP／S 暫存器與參數。這是明示 HOST 抽象，無法證明真實 ROM 被呼叫者行為或機器 fault／中斷前綴。長度 guard 只在不透明呼叫之前；模型沒有添加第二次 clamp。若 gate 將完整 S0 改成65536，low16 counter 不會遇到一般出口，fixture 因而明示以 budget 停在 UNKNOWN 前綴。budget 僅適用 HOST。零長度或 gate 後加長的案例都不能證明實體 buffer 容量安全。

Oracle 核對交錯的32／16／8位元保存、讀取與寫入，重新讀回的 RA／SP／S0、依路徑不同的 A0／A2、四個不透明呼叫參數、raw與清除bit0的目標／link，以及未正規化的委派結果；沒有宣稱完整所有機器暫存器前綴相同。尾端只是 provider 的不透明事件，沒有呼叫實際目標，也沒有傳送 wire／BLE 封包。

14個實際編譯、單一變更控制涵蓋：guard邊界與窄化、快取GP、遺失gate2參數殘留、錯誤lane、stride／magic、metadata改SW、尾端byte table偏移、快取restore SP、重複來源byte、checksum mask、正規化尾端結果、未清除目標bit0。每個負例皆成功編譯後由oracle斷言拒絕。最初草稿的快取SP變更曾觸發未使用區域變數的 `/WX` 編譯失敗；該次只保留在本機歷史 build，不列入語意負例。

最後的唯讀 replay 綁定實際編譯／執行 argv 與 exit、log／artifact hash、全部5份複製來源必須等於原始檔加上唯一指定變更、精確正例檢查數，以及全部15個執行檔 guard。10個記憶體內 receipt／來源視圖控制會拒絕錯誤recipe、計數、exit、缺少guard與錯誤mutant身分；包含額外修改第二份複製來源、並偽造相符artifact pin的情況。控制不修改任何封存檔案。另已回報 producer HOST runner 原先可略過guard讀回的問題；最終審查版本身分記於 `selected-verification.json`。

所有 HOST 啟動均使用固定的原生機器 guard：`experiments/tsl9-v4160-flash-register-prefix/verify_host.py`（`f1982360…713eb`）。選定實測為 Windows x64 PE；portable runner 支援其他平台，但本次沒有在其他平台執行。RISC-V目標產物從未啟動。實際C/C++來源執行、合成provider、native編譯、實體ROM ABI、固定位置、硬體及OTA接受度維持區分。目前native TX未准入為二進位相容替換；達到280 bytes不會解除入口guard、frame、restore與call前綴差異。

```sh
python3 -B apk-analysis/tsl9-v4160-ota-tx-2026-10-22/code-review/check-review.py --project-root . --firmware exports/TSL-firmware-options-22-BINs-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin
python3 -B apk-analysis/tsl9-v4160-ota-tx-2026-10-22/code-review/run-effects.py --project-root . --language both
```

`.sh` 包裝接受 `PYTHON`。預設 `check-review.py` 核對當下來源及已封存raw proof，但明確回報 `actual_archived_artifacts_replayed:false`：選定receipt metadata不代表本次讀回實際產物。可重複加上 `--receipt 實際獨立verification.json`，讀取本機真正封存；`run-effects.py --replay RECEIPT` 為唯讀，fresh run會在本份 `build/` 下建立新目錄。發布seal只含審查來源、文件及精簡選定metadata；執行檔、log、舊診斷嘗試與完整archive均留在本機。
