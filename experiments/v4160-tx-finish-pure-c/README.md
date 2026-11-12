# V4.1.60 post-loop：隔離的純 ISO C fragments

**不是完整函式、ABI、硬體模型或可燒錄實作。** 對照固定 BIN `[0x8b14,0x8b52)`、`analysis/transport-frame-2026-10-23/original-contract.md` 和 `src/native/receive/transport_frame.c`。`candidate.c` 無 asm、callback 或 tail call；它刻意拆成獨立序列。不得將其普通 C 呼叫連接直接宣稱與原機器碼等價：參數、回傳 struct、C ABI 與呼叫邊界不是原始 register/frame。尤其不可在所有片段之前預取記憶體或 tail slot。要捕捉時須在相應片段執行時才取值；片段之間任何外部行為均屬額外 unknown。

## 範圍與資料流

- `finish_checksum`：`8b14..8b1a`，對當時 D+s0+5 執行一次 volatile byte store。
- `finish_restore`：`8b26..8b2e`，依序 fresh LW RA/S1/S2/S3。
- `finish_metadata`：`8b32..8b3a`，依序兩次 volatile uint16_t store，length+6 取低16位。這是兩個 **C halfword 存取**，不是四個 byte 存取；ISO C 不保證其 bus transaction 或等同原 SH 硬體行為。
- `finish_tail`：`8b3a..8b50` 的值與記憶體片段，依序 fresh 讀 S0、`0x00040050` 的 T1、GP 選擇 byte，回傳 S0/T1/A0/A1/A2/A5/SP，不跳轉。A2=GP+148+4*bank，A5=0x40000，A1=1，SP=entry SP+32，運算皆模 2^32。T1 為讀出之值而非函式指標。GP 為此區間 then-live 值，不是 GP 指向的 slot 快照。
- `finish_bank_base`：模 2^32 的 A3+1062*bank。checksum 前的 A5=D；A3/A4 在本區間不變；RA/S1/S2/S3 用 restore 結果，S0 等用 tail 結果。其他未更動 register 使用入口值；這是值級出口描述，不是物理 register 捕捉。`jr t1` 不寫 RA；實際跳轉及其後效應未知。

原本順序是 checksum store → 四個 restore read → metadata SH/SH → S0 read → tail slot read → GP byte read；相同 byte address 可 alias word 或 halfword，故每次皆重新存取。特別是 checksum 可能修改 stack，metadata 可能修改 GP byte，GP byte 亦可指向 tail slot；不得先讀後重用。每段以完整 expression 排序 volatile 存取。此處沒有 `restrict`。

## C 邊界和不能表示的部分

實作必須提供可選型別 `uint16_t`、`uint32_t`、`uint64_t`、`uintptr_t`；每個轉換的 RV32 數值均須能由 `uintptr_t` 表示，並在 integer-to-pointer 轉換後正確映射到該原始地址。只在各次存取指向**有效、存活、對齊、具相容有效型別的 volatile 單一物件**時才有 C 意義；integer-to-pointer、byte order、volatile 實際效果由實作決定。地址是 RV32 實體數值，並非 host 陣列 index；例如 BIN 的 `0x8b14` 對應檔案 index `0xb14`（mapping base `0x8000`），不表示 C 物件可用此映射。無效位址、未對齊、fault、並行/中斷與 MMIO 副作用均未知。

unsigned char 可合法存取其他物件的 representation；但重疊的 uint32_t LW 與 uint16_t SH 不可一般性假裝為同一個有效 C 物件（有效型別／對齊問題）。因此未把四段合成可支援任意 word/halfword alias 的單一模型，亦未用兩個 byte 模擬 SH。這類 alias、跨片段調用時序與實際物件建立仍 unknown；各片段僅在其自身前提下有意義。全序是 BIN 證據，不是 ISO C 對所有 alias 的完整實作證明。64-bit unsigned 中間運算避免 16-bit 型別提升造成 signed overflow；截斷實現 RV32 wrap。無編譯、連結、執行 C 的證據。

## 離線檢查

於 repo root：

```
python experiments/v4160-tx-finish-pure-c/check.py
python -O experiments/v4160-tx-finish-pure-c/check.py
```

腳本以明確例外而非 `assert` 檢查完整 BIN SHA256、62-byte window、22 個連續 row 的位址／長度／opcode／bytes 與 candidate source SHA256。row 解碼來自既有 JSON；不是獨立反彙編證明。窗口變異、截短和 row 位址／長度／opcode／bytes 變異均直接交給檢查器作負例；Python 手列有序事件只示意 length=0、0xffff 的 metadata wrap、32-bit 位址 wrap、GP 對 metadata 和 tail slot 的 byte alias，並不測試 C 或實際 alias 行為。它**沒有執行、編譯或證明 C**，沒有執行 ISA、模擬目標或硬體。未設定網路或硬體；`firmware_ready=false`。
