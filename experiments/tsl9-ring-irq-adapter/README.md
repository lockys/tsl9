# Ring 中斷轉接程式

[English](readme.en.md)

[irq_adapter.v2.c](src/irq_adapter.v2.c) 重建官方 ID2966 `[0x12C24,0x12C58)`，整理副本為 [src/native/irq/ring_irq_adapter.c](../../src/native/irq/ring_irq_adapter.c)。C 表達32-bit status讀取／mask與tag0；明示架構 ports 保留條件式frame、then-live SP讀取、真實JAL及兩個MRET。**不是一般C ABI，尚不可燒錄。**

v1把SP匯入C值，LLVM額外搬移A1並寫回SP，產生54B／19指令；partial linker依52B契約拒絕。原始失敗來源／本機收據保留。v2改用物理SP讀取埠，實測52B／17指令，42個非控制位元組相同；三處立即數仍待解析，不能宣稱完整52B相同。

```sh
python3 -B experiments/tsl9-ring-irq-adapter/probe.py --version 2 --llvm-bin "$LLVM_BIN" --out-dir experiments/tsl9-ring-irq-adapter/build/my-probe
```

使用全新輸出目錄及本機既有LLVM。此配方僅實測Windows NDK LLVM18，Windows可用`python`；未驗證其他OS／工具鏈。不下載工具、不搜尋旗標或執行target。`component.ld`僅產生partial ET_REL，保留3個RELA與2個真正UND：`18D78`及ring。

完整收據與限制見[本輪分析](../../analysis/ring-irq-adapter-2026-10-23/README.md)。下一個164B provider的[靜態邊界](../../analysis/ring-irq-adapter-2026-10-23/provider-next.md)不等於可讀C實作或晶片型號證明。
