# 記錄解碼與狀態寫入連結

[English](readme.en.md)

新增 [record_decode.c](../../src/native/receive/record_decode.c)：C6A8–C776的206B／75指令，加上FAF8–FAFE的6B／2指令。C11／C++17的184非控制bytes與10筆具型別參照，經靜態原位址編碼後，完整212B全部吻合。

主元件為**4636B code＋456B data**：388個有大小的FUNC區塊、21個真實入口別名、309RELA、20UND。C／C++產物雜湊相同；原4424B程式碼與456B資料保持不變，62個選定非零向量綁定保留。C6A8與FAF8缺口由真實程式碼接通，12A08重用主元件中既有的完整分派器。

| 靜態觀察 | 證據與限制 |
| --- | --- |
| C6A8記錄處理 | bit9 gate、條件三byte寫入、raw數值分支、target byte7高bit及byte8高6bits保留；最後可能尾跳12A08 |
| FAF8狀態寫入 | 無frame，將A0低byte寫到GP+284後返回；不代表已確認某種裝置狀態 |
| 記憶體 | source GP+224完整word包含先前7B複製外的一個byte；target寫到offset8。保留原始寬度，未證明bounds／ownership |
| 下一批 | 已找到81AA、821E、16B7C、18CA4的既有C/C++實際物件；尚未驗證本輪重用所需的完整原碼範圍 |

[欄位圖](static-field-map.json)區分指令事實與「來源不變」的snapshot推論；實際程式仍保留每次fresh讀取，不合併成單一快照。欄位尚不能命名為座椅、免打擾或溫度。可研究的新增功能是**離線raw記錄預覽**，目前未實作。

~~~sh
python3 experiments/tsl9-record-decode/build-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-record-decode/build/trial-v1
python3 experiments/tsl9-record-decode/integrate-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-record-decode/build/component-v1
python3 scripts/check-record-decode-publication.py
~~~

[摘要](summary.json) · [20個剩餘提供者](pending-providers.json) · [下一批物件](next-providers.json) · [匯出來源](publication-provenance.json)

**這是未解析、VMA=0的ET_REL，不是可燒錄BIN。** 原機MCU、installed ROM／ABI、原位址配置、記憶體與IRQ／OTA尚未證明。未執行目標、HOST model或ISA，未接觸硬體。歷史個資問題仍在，未commit／push。
