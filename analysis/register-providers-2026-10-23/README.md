# Register providers 重建

[English](readme.en.md) · [C/C++與驗證](../../experiments/tsl9-register-providers/README.md) · [原始frame契約](frame-contracts.json)

read72B與write76B已重建；三次SPI呼叫之外60B／64B與原廠相同。GPIO條件、參數槽位、RA讀回及最後A0殘值的順序保留，沒有新增frame或spill。

兩個channel條件各自判斷，不能改成if/else。參數必須在SPI呼叫後重新32-bit讀取；RA必須在GPIO清理寫入前讀回。`frame-contracts.json`列出條件式alias影響，未宣稱實際硬體發生該alias。

280B部分連結包含consumer／receiver／read／write八個真實FUNC。四筆呼叫指向內部定義，八筆呼叫仍依賴SPI／packet兩個UND；十二筆relocations全部保留。**尚非已解析執行碼或可燒錄韌體。**

公開收據保留本機原件；curation公開檔是具原始SHA的路徑匿名化衍生檔。仍缺SPI／packet／resident、完整IRQ／main與實體OTA證據；未執行RV32、MMIO或硬體操作。
