# Resident入口參考模型

本C/C++模型僅對指定候選，涵蓋入口、初始化及RAM seed資料流，共230 bytes／66指令及4-byte header。來源證據拒絕35個原始運算元突變；每語言host suite為5組／121,496項。

```sh
sh ./verify.sh --language both
```

可攜入口先核對確切carrier、tail、Runtime、來源seal及依賴，再編譯自寫主機程式。嚴格main-only資料在來源6EAA4停止；主段加captured tail在6EB2C停止。不能略過缺失讀取先zero或MRET。合成未知記憶體只是有條件實驗，不修補原檔，也不證明實體fault。即時暫存器、helper身分條件及明示return／MRET邊界均保留。

指定參考不能辨識原機ROM或建立native ABI；不執行／模擬原始韌體、不存取實體硬體，也未驗證BLE OTA。[歷史封存說明](README.md)維持舊收據所需的原始內容。
