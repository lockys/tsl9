# V4.1.60 兩個 leaf 的抽象事件候選

僅離線靜態分析與候選，不是原始 C 或硬體實作。固定檔案 `firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin`，長度 76800，SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`；映像基址 `0x8000`，位址減基址為檔案偏移。以下是互不連續的精確半開視窗，中間的其他 leaf 不在範圍內。

| 位址視窗 | bytes | SHA-256 |
|---|---|---|
| `[0x18e90,0x18e98)` | `b7270240c8c78280` | `4937a9406887122dfa589dbe9fee75572e5cccd9ae20f52e7f9a59e140e2c466` |
| `[0x18eb6,0x18ec4)` | `372702401c4ba166d58f1ccb8280` | `20c1f57d6f8294aa24230996a9311f4a73ae3da72b0eed0acc4da3e2330ea7de` |

以索引工具 `C:\Users\locky\Tools\radare2\bin\r2.exe` 唯讀、RISC-V 32、映射基址 `0x8000` 的 `pD` 反組譯：前者依序 `lui a5,0x40022; sw a0,12(a5); ret`；後者 `lui a4,0x40022; lw a5,16(a4); lui a3,0x8; or a5,a5,a3; sw a5,16(a4); ret`。兩者均不改 `a0`，故在正常返回的指令層觀察中保留傳入值；這不是 ABI 證明。

`candidate.c` 是純 ISO C 的抽象介面：前者送一次 `(write32, 0x4002200c, input)`；後者每次呼叫都重新送一次 `(read32, 0x40022010)`，再以該次回傳值 OR `0x8000` 送一次 write，同時返回原 input。不快取讀取，也不設定 timeout。地址與輸入只是數值標籤：即使數值相同，也不推論指標或記憶體別名；read/write 可由同一個 callback 所持狀態處理。呼叫者須確保每次 callback 型別與函數指標有效、context 及其共享物件的生命週期有效，且不存在資料競爭或其他 C 未定義行為；假設 callback 正常返回。callback 可重入，包括同一候選，巢狀事件按實際呼叫順序交錯，各次後者保留自己的讀值，不能假設原子性。對無效 callback、未返回、fault 或外部並行行為不作保證。

`test.py` 固定完整映像長度及 hash、兩視窗 hash 和 `candidate.c` SHA-256 `212e26afc031097e43ea2a22f169f78d83c2d237353f4d43d4d920a2068ebeeb`；獨立解碼指令操作數、立即數並測試拒絕不支援及截斷輸入，另檢查 Python 抽象事件和重複讀取。在 repository 根目錄執行 `python -B experiments/v4160-18e90-18eb6-candidate/test.py` 及 `python -B -O experiments/v4160-18e90-18eb6-candidate/test.py`；測試不編譯、不執行 C，也不宣稱 C 已測試。無 target 執行或模擬。

不能由此推論原始 C、C ABI、實體暫存器語義、fault 行為、硬體相容性或時序；callback 事件並非硬體存取證據。
