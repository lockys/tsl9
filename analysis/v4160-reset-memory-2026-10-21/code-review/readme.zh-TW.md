# 重設記憶體 C 元件：獨立審查

審查對象是 `experiments/tsl9-v4160-reset-memory/src/reset_memory.c` 及標頭；來源要求依據另外封存於 `source-review/` 的 `0x186BA..0x186F8`，共 62 位元組、17 條指令。原始映像及初始化內容只作為**資料**使用，不執行原始或重建 RV32 程式。

可讀 C 核心保留三次獨立 GP 觀察、先讀後寫的向前字組複製、無號比較、uint32 加法、重新形成清零起點與字組寫入，並透過 host 測試介面觀察延續時 A0／A1／A2 的值。在此有序數值記憶體介面範圍內，未發現來源語意不符；這不證明原生暫存器配置、SP／RA、T0 殘值、可選 fragment 轉移或原始進出 ABI。

## 獨立證據

`independent-tests.c` 使用獨立撰寫的事件預期及兩份位元組記憶體。預期端在每次寫入後更新 byte shadow，再決定下一次來源讀取；實際 callback 更新另一份 byte memory。因此可檢查即時重疊及數值未對齊 alias，不把來源當成固定快照。所有 callback 都先核對下一事件與邊界，額外迴圈、GP 或來源讀取會立即失敗；數值位址不會被轉成 host 指標。

C11 與 C++17 每個 host build 均通過 **5 組／538 案例／193964 斷言**：

- 複製數量 0..32 與清零數量 0..12 的所有配對。
- 正常複製 32 字組及清零 8758 字組、三次不同 GP、無號符號邊界與邊界回繞後的略過情形。
- 間距一至八字組、雙方向重疊，使用即時 byte memory。
- 數值未對齊的目的地／清零起點與部分位元組重疊；這只是 fake backend，不證明實體硬體支援未對齊。
- 精確邊界略過、未對齊終點殘值及 A0／A1／A2 輸出。

每種語言都**實際編譯並由斷言拒絕十一種修改**，共 22 個編譯後負向案例：快取複製邊界、快取清零 GP、有號複製比較、錯誤複製／清零增量、包含邊界的複製／清零比較、錯誤 A0／A1／A2 與提前讀取位址。編譯失敗不算行為拒絕。receipt 會核對實際編譯器、原始輸入、元件、獨立測試、runner、helper、執行檔及變異結果。

`receipts/` 保留兩份獨立 receipt 及主實作 C／C++ host receipt 的位元組相同副本；主實作每種語言均為 5 組／338 案例／133601 斷言。歷史編譯日誌、host 執行檔、object 與變異來源留在工作封存的排除目錄 `build/`，不要求隨發布內容提供；receipt 雜湊記錄當時真實本機產物，不代表發布 checkout 仍包含那些檔案。

正向案例也逐事件檢查先讀後寫順序與寬度；保留的 read-ahead 修改變更的是讀取位址，不是讀寫次序，不把它宣稱為另一個已編譯的 write-before-read 負向案例。

## 尚未證明的原生要求

Host macro 只替換 GP、數值記憶體及三個輸出觀察，不能驗證 production inline assembly 或硬體存取。C 本體是新 helper，編譯器可能加入自己的進出框架；原始區段沒有 RET 或形成 RA，只會落入後續指令。原始 T0 最後複製值不在三輸出介面內。雖然下一條原始指令在正常直線延續時設 T0=31，仍不能單憑此證明中間沒有實體陷阱／中斷觀察。

Native fragment 的延續符號、堆疊、未動暫存器、實際 A0／A1／A2 殘值與 GP 觀察點，仍需原生 object／link 檢查及來源綁定 adapter。一般 C 語意不等於架構上的二進位透明。固定來源位址 0x1AB60 也需在最終映像對應到正確初始化內容。本輪不證明硬體型號、RAM 存取、完整啟動、ROM／IRQ 相容性或可 OTA 燒錄。

```sh
python3 run-review.py --project-root /絕對路徑/project --firmware /絕對路徑/ID-2966-V4.1.60-decoded.bin --language c
python3 run-review.py --project-root /絕對路徑/project --firmware /絕對路徑/ID-2966-V4.1.60-decoded.bin --language cpp
```

Runner 需要 Python 3 與已安裝的 C／C++ 編譯器，沿用專案 portable compiler locator，只在本審查 `build/` 下產生新 receipt。本次在 Windows／MSVC 執行，不宣稱已在 Linux／macOS 執行；不連網、不存取實體記憶體、不執行目標或模擬指令集。

另可執行 `check-review.py --project-root /絕對路徑/project` 作唯讀身分／receipt 核對，檢查原始來源封存、目前元件及保留 receipt 的雜湊，不重跑編譯器或 host 執行檔。這只是證據綁定，不是額外行為測試或原生驗證。
