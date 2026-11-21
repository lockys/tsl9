# v4.1.60：APP 事件表座標與參數來源

接續[前一輪](v4160-resident-slot-index-boundary.zh-TW.md)：其中 `0xf844`／`0x12ae8` 是 BIN **檔案偏移**，不是執行位址。以 APP 基址 `0x8000` 換算，正確位址是 `0x17844`／`0x1aae8`。後者已在 `src/native/receive/event_word_table_data.c` 保存七個 32-bit word；這一輪不新增來源覆蓋，也不把七筆條件視窗宣稱為完整表長。

`0x17832` 的索引為 `uint8[gp+370]`，先用它讀表，再寫回 `(i+1)%7`；正常 reset 與已知寫入的限制見[既有核對](v4160-code-continuation-2026-10-20/index-writer-review/README.md)。本輪只驗證七筆已知資料及其下游用途：`0x17854` 保留原 `a4` 低 16 位並把表 word 低 16 位放入堆疊 `sp+8` word 的高半；`0x17860` 將表 word 的 bits 16..23 寫入 `sp+12`。

`0x1786c` 從 `sp+12` 重讀 32-bit little-endian word，再擷取 bits 18..22。這五位來自 **`sp+14` 的 bits 2..6**，不是剛寫入 `sp+12` 的表 byte。在堆疊與 gp 索引欄不別名、存取成功且沒有其他改寫的條件下，`0x1782e` 所見的 `a2` 是 `800 * (1 + ((byte[sp+14] >> 2) & 31))`，`a1=2`、`a0=s1`，目標來自 `[0x40058]`。表值與此參數來源應分開追蹤；不據此命名參數的物理單位或 provider。

以固定 SHA-256 的 BIN 核對原指令窗、七個 C 常數，並以 Python `-O` 通過 3,584 組合成 byte 封裝與參數向量。這是受限的靜態推導與數值驗證，不是 CPU 或硬體測試。下一步先追 APP 內 `sp+14` 在這條路徑上的寫入者，再決定能否把參數域縮小。
