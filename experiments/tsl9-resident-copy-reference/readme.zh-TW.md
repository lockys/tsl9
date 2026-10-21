# Resident byte-copy參考模型

本C/C++模型僅適用指定候選，涵蓋58 bytes／18條原始指令。可攜raw證據拒絕23個運算元突變；每語言host suite執行5組／772項。

```sh
sh ./verify.sh --language both
```

入口核對確切carrier、BOOT橋接檔、來源seal與已宣告依賴。保留guard前MMIO保存／清除／FENCE、即時向前byte讀取及store前遞增；只有正常路徑才restore／RET，HALT、TRANSFER及觀察次數限制均保留前綴。RAM helper綁定是明示的主機身分條件。

此參考未辨識原機resident，也未證明原ABI、實體Flash或BLE OTA；僅執行自寫合成host測試。[歷史封存說明](README.md)維持舊收據所需的原始bytes。
