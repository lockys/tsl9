# V4.1.60 `0x131c2`：三組 table 的初始化來源

離線靜態證據；基準 main `d6e2391030eee86cc73426c206c47c7750e00c57`（不是要求目前工作樹 HEAD 等於該 commit）。固定原始映像 `firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin`：76,800 bytes，SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`。分析地址對應檔案 offset = address − `0x8000`；下述區間皆為半開。

## 三組不可混淆的指標與入口

| group | reset 初始 pointer word / RAM slot | 以初始 pointer 為條件的數值 base | `0x131c2` 外部來源、長度、call | marker／失敗時 default | `0x167a6` 中的外部 table 讀取入口 |
|---|---|---|---|---|---|
| A | `0x1abc0` → GP+`0x60` (`0x20004060`) | `0x2000c494` | `0x08077900`, 256, `0x13222` | `0x2000c593`；不等 `0x5a` → `0x13234` → `0x12e86` | `0x167ba` 起，讀 slot；offset `0,2,…,252`，比較成功才讀 offset+1，最大 `+253` |
| B | `0x1abc4` → GP+`0x64` (`0x20004064`) | `0x2000c594` | `0x08077700`, 256, `0x13282` | `0x2000c693`；不等 `0x5a` → `0x13294` → `0x12f7a` | `0x167ee` 起，offset `7,14,…,245`，讀取 offset 與 offset+1，最大 `+246` |
| C | `0x1abc8` → GP+`0x68` (`0x20004068`) | `0x2000c694` | `0x08077600`, 256, `0x132b2` | `0x2000c793`；不等 `0x5a` → `0x132c4` → `0x13084` | `0x16814` 起，offset `7,14,…,245`，讀取 offset 與 offset+1，最大 `+246` |

這裏的「外部來源」是指 initializer 傳入的數值來源參數，並非已證實的實體 Flash 映射；「外部讀取入口」是所列 consumer 函式內、透過指標取得 table bytes 的指令入口，不是全程式所有讀取者的完整清單。A 的讀取策略不同於 B/C；B/C 分別讀自己的 slot，且 B 的 dispatch 可以在 C 的 slot 讀取之前發生。不能把三者合併為同一指標、同一來源或同一迴圈。範圍只描述編碼中的條件性讀取，並不證明可達性、記憶體有效性或內容。

## 證據鏈與限制

* 原始 reset `[0x186aa,0x186de)` 建立 GP=`0x20004000`，從 `0x1ab60` 複製 128 bytes 至 GP；其中 `[0x1abc0,0x1abcc)` 是小端 words `94 c4 00 20 / 94 c5 00 20 / 94 c6 00 20`。僅在 reset copy 正常完成且槽未被更改的條件下，三個初始 pointer 如表。沒有證明後續指標不變、所有權、並行或 alias。
* initializer 的 A 窗口 `[0x13208,0x13238)`，B/C 窗口 `[0x13268,0x132c8)`：各自構造來源、目的和 256；各自 guard 自己目的的最後 byte，再以 `beq` 跳過各自 default；marker 不符落入相應 default call。A、B 之間另有 record `0x08077800 → 0x2000c30c`，不屬於這三個 consumer slots。guard 成功只跳過 default，**不證明完整內容、CRC 或有效資料**。
* 三個 default 函式完整原始指令窗口依序 `[0x12e86,0x12ee6)`、`[0x12f7a,0x13052)`、`[0x13084,0x130d6)`。各自先載入 `0x40048` slot，傳入對應 RAM、0、256 並間接呼叫，然後有各自的直接 stores、marker store 和尾跳 writer；這些窗口固定的是原始指令，不是已觀測的 RAM 狀態或成功持久化。不同 default 的 stores 不應相互替代。
* initializer 的 `lui a5,0x40; lw a5,76(a5); jalr a5` 證明的是從數值位址 **`0x0004004c` 載入 call target**，不是經由 `0x20004060/64/68` 任一 pointer base 作 ROM call。三個 default 所載入的是另一個數值 slot `0x00040048`。實際 target、語義和執行時 pointer base 若無獨立證據均為 **unknown**；不能因數值 destination 與初始 pointer 相同就認定 ROM call 是經該 pointer 執行或保證 copy 成功。若採既有 copy/fill 候選契約，表中只表示請求的參數及數值對應，並非實機觀測。
* consumer `[0x167a6,0x16846)` 與 reset、三份 default 和 initializer 視窗均直接以 bytes 固定；獨立語義解讀可對照 [table slot provenance](../v4160-167a6-table-slot-provenance/README.md)、[dual table](../v4160-167a6-dual-table-candidate/README.md) 及 [NVM record layout](../tsl9-NVM-record-layout/README.md)。這些歷史文獻是輔助解讀，不是本 verifier 的執行依賴；不繼承其中更強的 runtime 假設。

## 重現與負例

在 repository 根目錄，使用 Python 3：

```sh
python -I -S -B experiments/v4160-131c2-table-init-provenance/verify.py
python -O -I -S -B experiments/v4160-131c2-table-init-provenance/verify.py
```

檢查器驗證完整 image 長度及 SHA，將八段原始 code/data 的精確 bytes 固定在程式內並核對 pointer words。負例在記憶體內構造：截斷映像、改動視窗外一個 byte（測全檔 SHA）、逐視窗截斷、每個固定窗口每個 byte 單獨變異。失敗以顯式例外檢查，不依賴 `assert`，所以 `-O` 仍有效；負例不改磁碟檔案。這是 byte provenance 與手工指令解讀的審核，不是通用反組譯器、CFG 完整性證明或動態測試。沒有執行 target、模擬器、compiler、硬體、網路或更改 settings；不寫入既有檔案。
