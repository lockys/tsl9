# 記錄處理與真實提供者連結

[English](readme.en.md)

新增 [record_consumer.c](../../src/native/receive/record_consumer.c)：原 C776–C7E8 的114B／42指令／11架構區塊。C11／C++17 的94個非控制bytes及7筆具型別參照，經靜態原位址編碼後全部吻合。

| 已核對範圍 | 證據與限制 |
| --- | --- |
| C776／C798／C7AA | 分別保留16B frame複製、無frame清除尾跳、條件式32B frame回呼；GP+220暫存與2000C290 literal物件分開 |
| 82A8–82D2 | 重用既有C/C++實際物件的42B／16指令／4區塊；四個fall-through區塊全部保留 |
| 12A08–12A6E | 重用完整102B／35指令／9區塊分派器；四個下游依賴仍明示未解 |
| 主元件 | 4424B code＋456B data；371個有大小的FUNC區塊、18個真實入口別名、299RELA、22UND；C／C++產物雜湊相同 |

上一階段4166B程式碼與456B資料保持不變。舊C776缺口由真實程式碼接通；展開後新增C6A8、FAF8及四個分派器依賴，因此UND由17變22，未以空殼或絕對符號假裝完成。62個選定非零向量的真實綁定保留。

C7AA先寫status，再決定是否建立frame；保留呼叫後重新讀取pointer／byte與stack record。mask為4，不足以將欄位命名為座椅或免打擾功能。

~~~sh
python3 experiments/tsl9-record-consumer/build-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-record-consumer/build/trial-v1
python3 experiments/tsl9-record-consumer/verify-providers-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-record-consumer/build/providers-v1
python3 experiments/tsl9-record-consumer/integrate-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-record-consumer/build/component-v1
python3 scripts/check-record-consumer-publication.py
~~~

[摘要](summary.json) · [剩餘提供者](pending-providers.json) · [下一段反組譯](next-providers.json) · [匯出來源](publication-provenance.json)

下一輪優先重建C6A8的206B記錄解碼／分派與FAF8的6B狀態寫入。值得研究的新功能是離線7B記錄預覽及被動分派計數，目前尚未實作。

**這是VMA=0的未解析ET_REL靜態元件，不是可燒錄BIN。** 原機MCU、installed ROM／ABI、原位址配置、完整記憶體與IRQ／OTA尚未證明；未執行目標、HOST model或ISA，未接觸硬體。歷史個資問題仍在，未commit／push。
