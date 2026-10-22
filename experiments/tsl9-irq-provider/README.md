# IRQ 接收資料 provider

[English](readme.en.md)

[irq_provider.v2.c](src/irq_provider.v2.c) 重建官方 ID2966 `[0x18D78,0x18E1C)`。C 表達每次 fresh volatile word 讀取、位移／mask、byte／word寫入；明示 ports 保留原始 cold edges、實體暫存器與兩個RET。六個區域為18／8／108／10／10／10B。**這些是private架構區域，不是一般C ABI函式，也不是完整韌體。**

v2的C11／C++17原位量測均為164B／53指令，完整程式區段與原廠相同，SHA256 `678a3cbf42bc02d5c730973675858a18e538af9fdc1cb74dd9296f220f487ae3`。Native有3筆指向真實定義的RVC relocation；單體原位連結後解析，無UND／RELA。

v1雖同為164B，兩個返回區塊的LW卻使用A1，再OR到A5，改變原廠A1保存效果；原位差異在offset134／138／154／158。v2在兩次word讀取後增加A5值埠。失敗來源與原始本機收據均保留，未把v1列為相同。

```sh
python3 -B experiments/tsl9-irq-provider/probe.py --version 2 --llvm-bin "$LLVM_BIN" --out-dir experiments/tsl9-irq-provider/build/my-probe
```

使用全新目錄與本機已有LLVM；Windows可用`python`。目前只實測記錄的Windows NDK LLVM18；其他OS／工具鏈未驗證。不下載工具、搜尋旗標或執行target。

原始資料流／未知見[先前靜態邊界](../../analysis/ring-irq-adapter-2026-10-23/provider-next.md)，正式驗證與整合結果見[本輪分析](../../analysis/irq-provider-2026-10-23/README.md)。MMIO身分、IRQ上下文、ring的動態resident呼叫、完整啟動／記憶體／硬體與OTA仍未證。未產生完整韌體BIN。
