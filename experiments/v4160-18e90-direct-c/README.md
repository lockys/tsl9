# V4.1.60 0x18e90 直接 C 候選

僅為離線靜態候選，非原始 C 的還原或硬體相容性證明。`candidate.c` 以純 ISO C 撰寫，不含 inline asm 或 callback：將 `value` 指派至 `(volatile uint32_t *)(uintptr_t)0x4002200c`，接著返回 `value`。**不得編譯或執行此 C、target 或模擬。**

## 靜態依據

沿用相鄰實驗 [`v4160-18e90-18eb6-candidate`](../v4160-18e90-18eb6-candidate/README.md) 的離線反組譯觀察。固定映像 `firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin` 長度 76800 bytes、SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`，映像基址 `0x8000`。精確半開位址視窗 `[0x18e90, 0x18e98)`（檔案偏移 `[0x10e90, 0x10e98)`）為 `b7270240c8c78280`。既有觀察為 `lui a5,0x40022; sw a0,12(a5); ret`：原始 leaf 使用並改寫 a5 作為位址暫存器，而 a0 不變，故正常返回時 a0 保留傳入值；這只是指令層觀察，非 ABI 證明。

## C 與環境限制

`uint32_t` 和 `uintptr_t` 都是可選型別；實作必須提供它們。整數轉指標的結果是 implementation-defined，可能未正確對齊、無法指向該類型的實體，甚至是 trap representation；不能只憑數字推論合法指標。需要相容架構與實作明確支援此地址映射、對齊、存取寬度及 volatile MMIO 語義，且該位址必須實際可寫。未對齊或無效指標解參照等可導致 C 未定義行為（UB）；不可存取的位址亦可能造成硬體 fault，C 不保證正常返回。其他違反 C 物件模型或執行環境要求的情況也可能是 UB。`volatile` 不保證原子性、執行緒同步、匯流排交易次數或硬體順序；並行存取須另外處理，避免資料競爭。

此候選未證明編譯器產生相同指令、保留原 leaf 的 a5 使用方式、符合任何 ABI、執行相同硬體交易或有相同 fault／時序；也未證明原始函式簽章。寫入正常完成後的返回是候選的 C 原始碼意圖，不是測得的 C 行為。

## 靜態驗證

`candidate_18e90_direct` 與 callback 候選使用不同符號名稱，但仍不能在未解決原址 owner 與 relocation 前一併整合。`candidate.c` SHA-256：`a2a291bc18c69ec4911de3e46149234e9d968ea2fac0f5df3180edb180aa0536`。在 repository 根目錄僅執行 Python 靜態檢查：

```text
python -B experiments/v4160-18e90-direct-c/verify.py
python -B -O experiments/v4160-18e90-direct-c/verify.py
```

腳本檢查映像長度、完整 SHA-256、精確視窗位元組及 source SHA-256，並以記憶體中的截斷與竄改資料測試各檢查的拒絕路徑；不使用 `assert`，因此 `-O` 不會移除檢查。此驗證不編譯或執行 C，不宣稱已測試 C 行為，也不使用網路、硬體或 target 模擬。
