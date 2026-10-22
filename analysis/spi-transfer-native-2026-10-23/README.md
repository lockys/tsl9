# SPI 原機碼重建里程碑

[English](readme.en.md)

完整 SPI 葉函式 `[0x16896,0x168DE)` 已由 C11／C++17 產生並連結為與官方相同的 **72 bytes／25 指令**。選用來源、明示組語埠及執行方式見[實驗說明](../../experiments/tsl9-spi-transfer-leaf/README.md)；[contract.json](contract.json)列出原始碼、寄存器與存取順序契約。

- 單體：每種語言 2 個實際 ELF、36 項負例；唯讀重播通過，strict firmware-ready gate 預期拒絕。
- 接收管線：已從 280B 擴為 **352B／16 個真實 FUNC**，六個 SPI 呼叫均綁到新定義；17 個 relocation 中 15 個指向已定義目標，packet provider 的兩個呼叫仍 UND。每種語言 32 項結構負例均拒絕，負例不靠整檔雜湊判斷。
- 部分連結保留全部零位移 JAL／RVC placeholder。原 280B 與 SPI 72B 投影不變，排除控制欄位的 294B 與官方相同；這不是已解析可執行檔或原機 Flash 配置。

[summary.json](summary.json)及[四份公開收據](receipts/)記錄精確雜湊與範圍。公開收據在產生時即使用路徑變數，與本機原始收據逐位元組相同；ELF、IR、MD、日誌及舊收據保留本機。舊 280B provider 收據是釘選的歷史輸入，本輪重讀其產物，沒有重播舊 checker 的全部依賴。

新查明的下一步限制見 [packet-next.json](packet-next.json)：packet 函式使用 `channel==1` 選擇 GPIO，與 register read/write 的兩個獨立 bit 判斷不同；還必須保留 48B frame、13-byte 接收、清理後驗證及 fresh slot 還原順序。這個函式尚未重建。

可考慮新增診斷：原成功出口 A4=1、A5>0，逾時出口 A4=A5=0，因此能區分有效的資料 0 與逾時。尚未實作；寫入診斷 RAM 前須先證明 ownership／IRQ 上下文，不能只看 A0=0 判斷。

本輪沒有修改既有 `src/` 清單；下一步先走來源整理與物件驗證，再加入選用 SPI 來源。未執行目標或 ISA 模擬，未操作硬體、未產 BIN。完整 packet／resident／啟動／IRQ／記憶體與 OTA 相容性尚未證實，**不能據此燒錄**。
