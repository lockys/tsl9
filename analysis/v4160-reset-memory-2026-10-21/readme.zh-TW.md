# 啟動記憶體重建證據

目標是 ID2966 V4.1.60，SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`。原始記憶體初始化區段為 `[0x186BA,0x186F8)`，62 bytes／17 條指令，位於 138-byte reset 流程內；初始化來源 `[0x1AB60,0x1ABE0)` 共 128 bytes。未執行或模擬原始韌體。

可讀程式與自有主機測試位於 `experiments/tsl9-v4160-reset-memory/`。各項審查分開保存：

- [來源證據](source-review/readme.zh-TW.md)：確切 bytes、解碼欄位、初始化資料與 raw 負例。
- [呼叫邊界](caller-review/readme.zh-TW.md)：reset、時脈與未知 ROM 延續；正常 A0／A1 仍存活。
- [獨立 C/C++ 審查](code-review/readme.zh-TW.md)：有序的合成記憶體／GP／輸出 oracle 與實際編譯反例。
- [編譯器審查](compiler-review/readme.zh-TW.md)：實際 freestanding RV32 object、連結元件、結構覆蓋與拒絕的配置／缺少 provider 案例。

一般固定 GP 路徑複製 32 個 word、清除 8,758 個 word。測試另區分三次 GP 觀察、即時向前重疊複製、跳過路徑、無號比較及最終 A0／A1／A2。未對齊的數值 callback 是合成測試，不能證明硬體對齊行為；會使原始複製迴繞而不終止的輸入不在主機測試中執行。

原生 leaf 為 78 bytes，可選的延續 fragment 為 80 bytes，均放不進原始 62-byte 範圍。原始程式直接接續，C 編譯器產生的返回屬不同介面。數值 relocation 證據不會實作缺少的入口／延續 adapter，也不能確認原機 ROM。暫存器與迴圈結構檢查不能證明原始中斷或非同步中途狀態。既有完整映像 carrier 與原始 BIN 保持不變；未產生新 BIN。

交付與發佈包含選定的審查程式、文字及收據 metadata。歷史 object、執行檔與 probe 留在工作區編譯封存；目的地及發佈目錄驗證建立新的本機忽略產物。交付目錄的 `destination-verification.json` 記錄該處收據；儲存庫 manifest 核對原始 artifacts 及實際發佈檔案。Windows 本機通過不代表 Linux／macOS 或 shell 啟動已通過。
