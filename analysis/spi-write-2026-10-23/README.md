# SPI 寫入路徑里程碑

[English](readme.en.md) · [C/C++來源](../../src/native/receive/spi_write_providers.c) · [詳細驗證與限制](../../experiments/tsl9-spi-write-providers/README.md)

新重建兩個提供者：`0x168DE` 的區塊寫入請求與 `0x1693E` 的位元修改請求。C/C++實際編譯後，與既有SPI底層連到原PC；**254 bytes／93指令完整等於原BIN，沒有未解析符號或待處理重定位**。v3收據也核對入口、AX權限、配置映射、LLVM欄位與實際連結輸入；每語言97項nominal負向檢查通過。

`src/` 為62個C/H、36個原生單元、72組比較、144個物件；原70組結果與421個產物雜湊不變。仍屬局部靜態證據，**未產出可刷寫BIN，尚未完成逆向、硬體或OTA相容性驗證**。

[摘要](summary.json) 區分事實／推論／未確認事項；[硬體對應](hardware-correspondence.json) 只證明與快取WCH位址表相符，未確認晶片或外接控制器數量。可研究新增明確SPI timeout診斷，本輪未改變功能。

[公開收據對應](publication-provenance.json) 包含四份完整可攜原始收據及一份僅路徑匿名化的衍生檔。原始收據、修正前checker及歷史失敗紀錄保留本機；不改寫Git歷史。既有1162B整合與246B標記候選保持原樣，後續將追查真正的`0x8520`提供者。
