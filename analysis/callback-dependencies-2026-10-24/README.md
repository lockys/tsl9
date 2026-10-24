# 回呼依賴：離線 C/C++ 重建

[English](readme.en.md)

本輪完整重建 `11356..11442`、`13CDC..13D48`、`16E88..16F00`，共464B／170指令，已納入 [src](../../src/native/receive/callback_dependencies.c)。全部原始bytes與29個具型別參照通過C11／C++17物件核對。[原始證據](evidence.json) · [位址契約](provider-contracts.json)。

- **已確認：** 11356最多掃描42筆、每筆6 bytes的記錄，比較32-bit key後轉交所選byte或255。13CDC配置長度+1空間、寫入byte長度前綴、複製原始完整長度，交給佇列入口並依結果呼叫清理。16E88保留原狀態回傳值，僅在值為零時設定所選通道。
- **推論：** 配置／複製／佇列等角色來自參數資料流與ROM槽位；installed ROM名稱、長度界限、ownership與實體暫存器效果未證。
- **未確認：** 新依賴155D0、16B50與回呼位址候選13EB4。接上三個舊入口，同時展開三個缺口；仍有115個真實未解析符號。[清單](next-providers.json)。

完整來源證明涵蓋120個C/H檔、188組比較／376物件；舊119個C/H檔及1105筆產物記錄保持不變。主元件為26,880B code＋714B data／1,755重定位，選定27,594B在名義原址逐byte吻合。診斷ELF入口為0且**沒有PT_LOAD**。靜態流程核對9,248指令、1,555直接轉移及611個呼叫返回位置，一般續行沒有缺口；474個間接轉移、10個MRET目標與原始EBREAK／向量邊界仍不構成執行證明。[摘要](summary.json)。

[新功能候選](feature-candidates.json)整理診斷報告與記錄變動解釋的用途及所需證據；目前只是提案，未實作或實機驗證。

本輪不執行韌體、HOST模型或ISA模擬，不接觸硬體、BLE／CAN／Flash或原廠網路，不產生BIN。實體MCU、installed ROM、RAM ownership、完整啟動／IRQ與OTA相容性未證。
