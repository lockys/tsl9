# 記錄提供者與 SPI 靜態呼叫鏈

[English](readme.en.md)

接通81AA、821E、16B7C、18CA4四個入口及其填值／暫存器讀取／SPI必要依賴，重用8個既有C/C++單位的**1000B／349指令／67區塊**。C11／C++17全部原位址碼核對吻合；47筆新增具型別參照及函式內原生分支均保留。

| C/C++來源 | 選定範圍 |
| --- | --- |
| [queue-small-providers](../../src/native/receive/queue_small_providers.c) | 6B／2i／1 regions |
| [record-predicate](../../src/native/receive/record_predicate.c) | 42B／15i／1 regions |
| [fill-provider](../../src/native/receive/fill_provider.c) | 168B／55i／13 regions |
| [spi-transfer](../../src/native/receive/spi_transfer_ports.c) | 72B／25i／8 regions |
| [spi-write-providers](../../src/native/receive/spi_write_providers.c) | 182B／68i／20 regions |
| [register-read](../../src/native/receive/register_read.c) | 72B／26i／2 regions |
| [tagged-dispatch](../../src/native/receive/tagged_dispatch.c) | 246B／86i／15 regions |
| [peripheral-write](../../src/native/receive/peripheral_write.c) | 212B／72i／7 regions |

主元件為**5636B code＋456B data、455個有大小的FUNC、22個真實入口別名、356RELA、16UND**。C／C++產物雜湊相同。原4636B程式碼、456B資料與62個選定非零向量綁定保留，未加入stub或ABS假提供者。

95個C/H檔與manifest未改變。當前來源投影仍為136組code比對／272物件，另加2組指標資料比對／4物件，合計138組／276物件。本輪重用既有物件，不宣稱新增8個來源單位。81AA只選取完整6B leaf；其同來源的18B清除函式也通過原碼核對，但不加入本鏈。

原18730的JAL x0確實跳到APP映像外的40000（[證據](resident-tail.json)）。這是待證明的resident執行入口，不能以函式表配置或假位址取代。剩餘16項及可重用來源候選見[下一步](next-providers.json)；18834舊clock-query有196B／174B差異，尚未接入。

~~~sh
python3 experiments/tsl9-record-providers/verify-providers-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-record-providers/build/providers-v1
python3 experiments/tsl9-record-providers/integrate-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-record-providers/build/component-v1
python3 scripts/check-record-providers-publication.py
~~~

[摘要](summary.json) · [剩餘提供者](pending-providers.json) · [匯出來源](publication-provenance.json)

值得研究的新功能是被動busy／SPI等待與timeout診斷，搭配離線raw記錄預覽，目前未實作。**靜態鏈閉合不代表CAN／SPI傳輸成功；這仍是VMA=0的未解析ET_REL，不是可燒錄BIN。** 原機MCU、installed ROM／ABI、原位址配置、記憶體與IRQ／OTA未證明。未執行目標、HOST model或ISA、未接觸硬體、未commit／push；歷史個資問題仍在。
