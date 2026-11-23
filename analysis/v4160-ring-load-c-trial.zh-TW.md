# v4.1.60 ring producer：以 C 取代單一 halfword load 的實驗

## 目的與方法

已知 `src/native/receive/ring_insert.c` 的混合 C/assembly 在既有原位收據中比對成功。本次在暫存目錄複製來源，只測試將掃描位置的 `lhu a6, 0(s0)` 改寫成 C `volatile uint16_t` 讀取，同時保留地址計算的 assembly、實體 s0/a6 ports、其他程式碼與既有的 RV32 編譯設定。未修改正式來源或 BIN。

```c
register uintptr_t slot __asm__("s0");
__asm__ volatile("add s0, a7, a4\n"
                 : "=r"(slot), "+r"(offset), "+r"(base) : : "memory");
register uint32_t occupied __asm__("a6") = *(volatile uint16_t *)slot;
```

## 實際結果

以既有 `experiments/tsl9-ring-insert/probe.py` 的設定（RV32IMAC、`-Oz`、`-mno-relax` 與固定暫存器）編譯；C11 與 C++17 均在 object 產生階段失敗，錯誤為 `error: Stack pointer required, but has been reserved.`。在另一個全新暫存目錄重新執行，結果相同。兩種語言的 LLVM IR 輸出均成功，但 IR 成功不等於機器碼成功；IR 中的 `align 2` 另引入 C 對齊假設。

因此沒有候選 object、原位連結 bytes 或候選 relocation 可比對。原指令在 `0x12be8`，bytes 為 `03 58 04 00`；不得將原先正式物件的 relocation 當作候選的結果。此負面結果僅涵蓋上述這一種寫法和既定設定，不能推論其他 C 寫法均不可行，也不證實機行為。下一步可在隔離副本分析 register pressure 與其他可驗證寫法；正式來源的原位 bytes、實體暫存器、relocation、IR 和來源 pin 仍須全部滿足。
