# 原回覆位置的獨立 C/C++ 物件與設定入口生命週期

[English](readme.en.md)

本輪實際改進 OTA C/C++ 的位置契約，並縮小原 App 設定的未知寫入範圍。**沒有新BIN／原機執行；現有568元件與77,824-byte實驗映像保持不變，仍未驗證可刷寫。**

## 真實 C/C++ 改進

兩個有根據的source profile：先在range guard後具體化完整Flash base，防止常數與page兩值跨copycall占用額外S7；得到552B／8saves。再將native reply改為明示align4的4-byte volatile物件，不初始化額外bytes，取得**550B／186指令／48-byte frame**。

實際IR只有一個4-byte align4 alloca/lifetime4；整個物件SP12..15獨立，保存槽最低SP16。本地只寫S回覆的SP12/13及失敗時重寫SP12，傳送length2；空E回覆仍pointer0/length0，兩組phi沿同predecessor核對。相同入口SP時，指標SP12−48等於原entry−36。

原共同七個保存位置保留，新C仍多保存S6@16，保存順序與內部callRA也不同。未知provider可能觀察整個frame、其他register或超出2B的記憶體；不能因獨立4B object與數值pointer一致就宣稱完整ABI成功。原530-byte範圍也還差20 bytes。

[C/C++程式](../../experiments/tsl9-v4160-ota-reply-object/README.md) | [實際編譯／replay](implementation/README.md) | [獨立物件／IR／反例](object-review/README.md)

## 原 App 設定的局部範圍

- [MAC helper](mac-review/README.md)：18F56..18F88，50B／14指令；兩個工廠地址READ32後只寫入A0+0..5，不nestedcall、不改SP／S0／GP／RA。caller19AAC..19AEE的66B／24指令將六bytes複製至SP40..45，其他store亦避開staCB68..71。4個原始operand反例。
- [候選填值函式](memset-review/README.md)：兩份slot40048均指向RAM2000039C，完整46B／14指令，含MMIO save／zero／FENCE.I／restore，null／zero-length也有這些效果；正常回傳advanced A0。6個有效operand反例。
- 在設定分支已到達、選定參考leaf確為被呼叫者、SP+16非零且64B有效、不aliasMMIO/code、無非同步變更且正常存取等前提下，填值寫SP16..79包含staCB68..71；其後只剩已審MAC call、六byte copy與不重疊的明示stack stores。因此可推得**19AEC進入BLE_LibInit當下，App config+52為零**。

這是固定來源的欄位／區間論證，沒有CPU狀態執行。它不證明版本分支能到達、實機ROM或callback永久零值。BLE_LibInit在copy前的numeric200004BC與liveS1，仍可能改來源或register，是下一個實際邊界。

## 驗證、交付及尚缺條件

各checker預設metadata與明示實檔讀取分開；有原FW、candidate-root或ELF參數才讀相應實物。MAC的ELF檢查只驗50B子集，不能冒充完整映像provenance。C/C++由固定Windows LLVM實際編譯；Python／POSIX shell介面可攜，沒有Linux／macOS／CI native驗證。

沒有重跑未變的HOST演算法、重編原whole-image baseline、執行RV32／ISA模擬、BLE／UART／CAN／Flash、廠商API或裝置識別資料傳送。保留舊seal及所有BIN，僅在完成獨立驗證後提交此獨立元件／來源證據。

原機板型、已安裝ROM／BOOT、RAM／IRQ、Flash／NV所有權、未知callee／alias／async完整ABI、BLE OTA接受與失敗恢復仍未完成。新功能候選延續離線更新前的NV／ROM條件摘要：應顯示此類「前提成立才導出的值」與實測值的差別；尚未實作為原機功能。
