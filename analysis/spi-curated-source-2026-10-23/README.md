# SPI 選用來源已納入 src

[English](readme.en.md)

已將通過獨立單體驗證的 SPI 來源原樣加入 [src/native/receive/spi_transfer_ports.c](../../src/native/receive/spi_transfer_ports.c)，來源與副本 SHA-256 同為 `1f68851e9ae71d1ef56147e554fdaa53ae0918e2bfac73bad32a110549fe3182`。清單現在有 49 個 C/H 檔、23 個 native translation units。

完整 C11／C++17 來源整理檢查通過 **46 組／92 個物件**，唯讀重播亦通過。原有 44 組結果、88 個物件、88 份 MD 及依賴紀錄不變；舊編譯命令只差建置目錄。新增四個 SPI 物件都與獨立實驗的 native ELF 相同。

新 profile 僅針對 SPI 使用 `rv32imac_zicsr` 及 A0/A3/A4/A5 bank；其他 profile／gate 保留。專屬 gate 核對 8 個真實 FUNC、8 個 AX 區段、72B、5 個已定義 RVC relocation、零 UND／ABS provider。完整已解析的 72B 原碼、區域相鄰及 352B 部分連結仍由[獨立實驗](../../experiments/tsl9-spi-transfer-leaf/README.md)證明，來源副本比對不取代那些檢查。

[summary.json](summary.json)記錄精確雜湊與範圍。[公開收據](receipts/curated-source.json)只替換路徑，屬衍生副本；原始收據保留本機，SHA-256 `582f6d2aa8c3efb4e92c30b94cada79b106a3292377a4029659624ac6930b5fb`。反向代入路徑後，完整 JSON 與原件相同；不能直接把公開副本當原始重播收據。

本機重播：

```sh
python3 -B scripts/verify-curated-source.py --replay build/curated-source/spi-20261023-v1/verification.json
```

沒有執行 RV32／ISA 模擬／MMIO，沒有產生或燒錄 BIN，也沒有重跑舊 V4.1.00 HOST 測試。這是來源整理與原生物件一致性證據；packet／resident／啟動／IRQ／實體記憶體與 OTA 相容性仍未閉合。
