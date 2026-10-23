# 周邊寫入與實際 dispatch 整合
[English](readme.en.md) · [繁體中文](readme.zh-TW.md)

本輪將18CA4的212B／72指令重建選入src/native/receive/peripheral_write.c。C負責所有volatile讀寫與算術，七個私有架構區塊維持原始分支及cold paths。指定原始位址連結後，C／C++完整212B均與官方V4.1.60相同；不代表原機已執行。

實際部分連結既有950B與新provider成1162B／402指令／49 genuine FUNC；原呼叫offset888綁定真實provider offset950，原950B全部保持相同。仍有57 pending RELA及五個外部provider，VMA0不是原始整體實體配置。完整數據見[summary.json](summary.json)及[原始ELF獨立檢查](root-native-review.json)。

每語言通過197個native負例與33個join負例，完整上游收據實際重播通過。src共60個C/H／34個native TU，68組／136物件比對通過；舊66組與397個產物不變。兩語言strict firmware gate均在bounded PASS後exit1。

[本機封存SDK對應](hardware-sdk-match.md)支持CAN_Transmit／bxCAN類函式判讀及CH32V20x家族候選；尚未辨識實體板子、晶片料號、transceiver或觀察到CAN傳送。新功能候選是離線mailbox／拒絕原因／原始與masked DLC報表；未增加車輛控制，也未改原始guard。

[公開收據](publication-provenance.json)包含四份逐位元組原件與一份路徑匿名衍生版；原件與失敗輸出保留本機，另有73檔備份ZIP。v1 join checker漏列實際讀取的自身seal；已保留舊checker／seal／收據，v2補列輸入後用相同recipe重新連結，物件與結果不變。衍生收據不冒稱原件重播。

```sh
python scripts/check-peripheral-publication.py
python scripts/anonymize_public_evidence.py --check
```

下一段為[16B7C tagged provider](next-provider.md)：已取得256B原始視窗，候選函式246B、64B frame與四個外部callee。仍須逐項證明完整ABI／ROM／記憶體／IRQ／啟動及藍牙OTA；本輪不執行target／ISA／MMIO／硬體、不呼叫vendor API，也不產出可燒錄BIN。
