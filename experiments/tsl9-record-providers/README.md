# 記錄提供者與SPI鏈的實際物件整合

[English](readme.en.md)

從既有C/C++來源重用1000B／349i／67架構區塊，補齊81AA、821E、16B7C、18CA4及其必要子呼叫。完整來源皆先做正常原碼核對，只從24B queue-small-providers物件選取完整6B81AA leaf。其餘七單位保留全部必要區塊，按原PC排序連結。

[分析與限制](../../analysis/record-providers-2026-10-24/README.md)

~~~sh
python3 experiments/tsl9-record-providers/verify-providers-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-record-providers/build/providers-v1
python3 experiments/tsl9-record-providers/integrate-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-record-providers/build/component-v1
python3 scripts/check-record-providers-publication.py
~~~

5636B code＋456B data／356RELA／16UND；C／C++產物相同。當前95個C/H檔、68個code單位與獨立指標資料來源未改變；來源比對合計138組／276物件。這是VMA=0的靜態ET_REL，未證明原機、ROM／ABI／記憶體／IRQ／OTA，不是可燒錄BIN。無目標／HOST model／ISA執行、硬體或網路操作，未重跑舊負例矩陣。
