# Resident 缺失 word 的條件位址檢查

[English](readme.en.md)

已保存的 WCH V1.31 參考 HEX 對候選 loader 第二段複製來源 `[0x6EAA4, 0x6EB30)` 缺少最後 `[0x6EB2C, 0x6EB30)` 四個位元組。這是**檔案未記錄**，不是實機 Flash 缺少或空白的證據。完整的指令視窗、copy helper 與缺口證據見 [依賴帳本](../tsl9-six-dependency-ledger/README.md)。

[WCH CH32V208 資料手冊 V2.6](https://datasheet.lcsc.com/datasheet/pdf/036eca5d5805c8189aa2b0396c0860e1.pdf?productCode=C5187528) 的 §2.1 註 1–2 與 §2.5.2 說明 Code Flash 最大 480 KiB，區分零等待區和非零等待區，實際大小視型號而定。以連續最大範圍 `[0, 0x78000)` 為**條件數值模型**，缺口位於其中；只有額外假定程式 Flash 啟動映射及該 offset 實際有效，才對應到高位 `[0x0806EB2C, 0x0806EB30)`。缺口也不在候選 APP `[0x8000, 0x1AC00)` 內，因此不能只靠這個 APP BIN 補足。

本檢查固定參考來源 map 雜湊、驗證 17 段檔案並核算覆蓋及邊界。它不讀取裝置、不填補缺口、不執行目標指令，也不證明啟動模式、映射、可讀性、缺口內容或裝置實際 resident。嚴格連結仍缺 `tsl9_boot_resident_40000`；不能依此燒錄。

```sh
python experiments/tsl9-resident-missing-word-map/verify.py --reference-dir analysis/wch-resident-candidate-2026-10-21/carrier-dec2023
```
