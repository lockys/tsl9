# V4.1.60 TX：共同 RAM 的受限 C 切片

`candidate.c` 是獨立 C11 抽象候選，不是 ABI 入口、韌體補丁或等價證明。入口為選定 bank 後 `0x8ace`，出口為未進入 loop 分支、執行 `0x8b14` 前；不包括 admission、完成路徑或 tail。沒有 callback、asm、memcpy 或 tail 寫入。尚未編譯或執行 C。

## 呼叫者契約

`ram` 指向單一仍存活、有限大小的 `volatile unsigned char` 陣列，`CHAR_BIT == 8`；所有索引均相對該同一物件，包含 `base_index` 與 `source_index`，即使長度為零也要求來源索引有效。`origin` 是此陣列 index 0 對應的原始 RV32 地址 R；要求可逆映射 `R + base_index = 0x2000b18c`，`R + source_index` 是 then-live 原始 s1。`bank` 為 then-live a2（0 或 1），`length`、`command` 為 admission 返回後的完整 then-live s0、s3，`length <= 65535`，不能用此前 guard 代替此條件。`entry_a6` 是未知原始地址或原始寄存器值，不必可映射。

呼叫者須保證 header 的 D 索引至 D+4，以及每次實際來源與目的索引，均在同一陣列內；所有相關索引、原始地址、D+i、source+i、D+i+5 與 i 遞增的數學結果不回捲且可表示為 RV32 地址／索引，映射可逆，物件大小為該 C 實作可表示。無故障或非同步干擾；不涵蓋 MMIO。沒有動態檢查。checksum 則刻意模 2^32，再取低 8 位；以 `uintmax_t` 加法避免特殊實作中有號整數提升溢位。

## 精確範圍

D 的原址為 `0x2000b18c + 1062*bank + 6`。按 little-endian 最終 RAM 及順序 byte 事件模型，header 依次寫 D=55、D+1=7f、D+4=length 低位元組、D+3=length 高位元組、D+2=command 低位元組。原始的 D 半字 SH 在此拆成兩次 byte 寫入：**不等價於原 bus 寬度、原子性或中斷/DMA 可見的中間狀態**；volatile 也不提供同步。之後逐次讀來源、再寫 D+5+i；不快照，故 header 或前次目的寫入可以影響之後讀取。低 16 位比較、完整 i、實際讀值 checksum 均保留。

輸出欄位對照 `0x8b14` 前：a0 為最後低 16 位比較值，a1 完整索引，a2=bank、a3=原始 B、a4=checksum、a5=原始地址 D；a6 零次時原樣保留入口值，非零時為原址 D+最後一次遞增前索引。s0=length、s1=R+source_index、s3=command；這些是原切點未變的寄存器值。其他暫存器未列入介面，不聲稱全暫存器狀態。

## 離線檢查

執行 `python experiments/v4160-tx-composed-ram-c/test_offline.py` 與 `python -O experiments/v4160-tx-composed-ram-c/test_offline.py`。只讀 BIN 的 `[0x8ace,0x8b0a)`、`[0x8b0a,0x8b6c)` 完整固定 bytes 和 candidate source SHA-256；逐 byte BIN 變異及 source 末尾變異必須失敗（不用 assert，-O 仍有效）。第二窗口也含非執行路徑，不表示那些指令屬於切片；固定 bytes 並非反組譯或語義證明。Python 獨立事件例子涵蓋非重疊、header/逐次寫入別名、零長、最大長及循環界限；**Python 不測試 C**，也不驗證呼叫者的地址映射、物件邊界或 no-wrap 契約，亦不證明 C 或完整 BIN 等價。沒有執行 target、模擬器、網路或硬體設定。
