# 可讀原生時脈元件審查

本審查重用 `apk-analysis/tsl9-v4160-system-clock-query-2026-10-21/source/` 已封存的來源證據，seal SHA-256 為 `ebf0521f52c5142d1dc7969aaca17bb1c7567065165eba4c88fd4523e30b6a51`。原始 ID2966 runtime digest 為 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`；兩個函式共 214 位元組、69 條指令，範圍為 `0x18834..0x188E2`、`0x1973C..0x19764`。先前的來源限定 SF 主機模型可供參考，但不是原生 ABI 實作。

## 可讀 C 必須遵守的來源條件

兩個原始函式都是沒有堆疊操作、沒有呼叫的 leaf，不設定 A0、A1、GP、RA。新增的 `void` C 介面可表達記憶體效果，但其型別不保證保留原始 A0 或 caller-saved 暫存器。`void` 或一般編譯結果也不能證明可替代原入口位址、完全相同的堆疊／返回行為、中斷 ABI 或已安裝環境的 GP 慣例；整合原生替代品前仍需驗證 wrapper 或完整的新呼叫慣例。

查詢有四個獨立 GP 使用點：`0x18850` 初次 scalar store、`0x1885A` table base、`0x18868` 新 scalar 位址、`0x18872` 最後 store。派生函式分別在 `0x1973C`、`0x19752`、`0x1975E` 使用 GP。位址加法需先以 32 位元環繞，再轉成原生 pointer。若環境依既有來源契約改變 GP，只在函式入口讀取一次會改變行為。原生 `readGP` 組語 primitive 需 volatile 並維持所需的編譯器記憶體次序；這不是實體記憶體 fence。

查詢 selector 0、12 選擇 8,000,000，4 選擇 32,000,000，8 進入 multiplier 路徑。Multiplier 與 source sample 是兩次獨立讀取。倍率為 `((sample >> 18) & 15) + 2`，17 改為 18。內部分支讀取 `0x40023800`，以 bit 4 選擇 4,000,000 或 8,000,000。外部分支先重新讀取 `0x40021004`，檢查 `0x00C00000` 遮罩是否全相等；若不相等，再讀一次，以 bit 17 選擇 4,000,000 或 8,000,000。直接測 bit 17 是原始 32 位元環繞左移 14、再用 signed BGEZ 判斷的明確 unsigned-C 等價寫法。重用先前 config 讀值不等價。

查詢先儲存 provisional scalar，再重新讀 config 取得 table index、讀取 GP+64+index 的 live byte、重新讀取當時 scalar word，最後以 `(byte & 31)` 做邏輯右移。固定 reset table、快取 provisional scalar、限制 shift 最大值、算術右移或 C shift 超過 31 都會改變行為。Reset table 只提供有條件的初始化證據，不能取代 byte 讀取。

派生函式讀取 live word，執行 unsigned 除以 8,000,000、截為八位元、寫入 byte，再將保留的截斷值乘 1,000，寫入低 16 位元。寫完 byte 不會重新讀取它。也不能使用較早查詢的快取結果，因為兩者之間還有另一個原始初始化呼叫。

## 獨立實作結果

已審查實際共用的 `native_clock.c` 與公開標頭，沒有修改它們，也未發現阻擋性的來源差異。原生 primitive 使用 volatile word、unsigned-byte、byte-write、halfword-write 存取；`current_gp` 為附 compiler memory clobber 的 volatile `mv` 組語。主機選擇只切換 primitive，不改變分支與算術邏輯。

獨立 C11、C++17 各通過 **4 組、5,345 個案例、214,811 次 assertion**。Harness 由已封存來源契約建立依序的 primitive trace，涵蓋全部 16 倍率欄位、內外部分支與新的 fallback sample、16 個 index 乘上 256 種 shift-byte、獨立變動 GP 與 32 位元位址環繞、與 provisional scalar 不同的新 global、unsigned 邊界及全部 537 個 quotient 邊界。Byte、halfword store 分別取新的 GP，使用保留的 quotient，不重讀已寫入的 byte。

每種語言另實際編譯、執行五個錯誤來源版本：沿用倍率 sample 作 source selection、以 provisional scalar 取代新 global、查詢只快取一次 GP、shift 最大限制為 31、乘法前省略 quotient 截斷。合計 **10 個已編譯負例**全被獨立執行期 assertion 拒絕；編譯失敗不算行為拒絕通過。Receipt 綁定來源／標頭／harness／編譯 helper／來源證據、實際編譯器與執行檔、選項及編譯日誌，每次執行前後輸入均未改變。可用 `audit.py --language both` 重現此主機審查。

父層最終測試另於每種語言通過 6 組、269,618 次檢查，並重播既有 214 位元組、69 條指令、50 個 raw mutation 的來源證據。`check-review.py` 將兩份父層正式 receipt 與兩份獨立 receipt 對照目前輸入、實際執行檔與編譯器 digest；最終父層腳本、文件及 source map 經正式 receipt 綁定。此核對只讀取檔案，不執行測試或 firmware。

原生編譯、主機假記憶體行為、原生指令／IR 審查、實體硬體與 OTA 驗證是不同證據層級。本範圍不執行原始 RV32、不做 ISA 模擬、網路或裝置 I/O。
