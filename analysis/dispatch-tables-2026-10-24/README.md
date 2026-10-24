# 通道分流、功能分派與相對表

[English](readme.en.md)

接通12ABE與14D2E，重用8個既有C/C++單位的**2736B／956指令／269區塊**，以及兩張共**60B、15項**的相對表。C11／C++17的程式與表格原位址編碼均與原廠BIN吻合；每個表格目標都有真實程式區塊承接。

主元件為**9836B code＋516B data、783個有大小FUNC、26個真實入口別名、698RELA、82UND**，C／C++產物相同。原7100B code、456B data與62個選定非零向量綁定保持不變。12ABE／14D2E接通後展開69個外部符號；再將C6A8綁到既有解碼器，因此仍有82個符號待補，不代表所有功能實作完成。

| 核對範圍 | 證據與限制 |
| --- | --- |
| 通道分流 | 保留內建／SPI分流、filter輸入與program路徑；實體CAN／SPI結果未證明 |
| 14D2E主體 | 保留16B frame、模式guard、record-ID比較與尾跳；尚未命名為座椅或免打擾功能 |
| 兩張相對表 | 原1A6B8的28B與1A6D4的32B；15組ADD32／SUB32及兩組HI20／LO12參照皆有正確owner，[詳表](relative-tables.json) |
| 三個時鐘區塊 | 父元件已供應原26B；[C選取](../../experiments/tsl9-dispatch-tables/derive-selection-v1.py)只移除同一定義，保留其餘函式與參照 |

95個curated C/H檔與manifest未改變，來源copy投影仍合計138組／276物件，另有本輪2個C選取編譯物件。這項copy比對不等於所有來源都與原廠相同；本輪另做選定2736B程式及60B表格的原碼核對。

~~~sh
python3 experiments/tsl9-dispatch-tables/verify-providers-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-dispatch-tables/build/providers-v2
python3 experiments/tsl9-dispatch-tables/integrate-v2.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-dispatch-tables/build/component-v2
python3 scripts/check-dispatch-tables-publication.py
~~~

[摘要](summary.json) · [82個剩餘符號與來源候選](next-providers.json) · [匯出來源](publication-provenance.json)

可研究離線mode／record-ID到handler的檢視器與被動分派原因診斷，目前未實作。**這仍是VMA=0的未解析ET_REL，不是可燒錄BIN。** 原機、installed ROM／ABI、實際表格／RAM配置、完整IRQ與BLE OTA未證明。未執行目標、HOST model或ISA、未接觸硬體／網路、未commit／push；歷史個資問題仍在。
