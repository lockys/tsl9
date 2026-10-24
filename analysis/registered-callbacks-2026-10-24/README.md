# 已註冊回呼：離線 C/C++ 重建

[English](readme.en.md)

本輪完整重建 `11442..114E2`、`119C8..12506`、`16F00..16FB6` 三個函式，共3,220 bytes／1,032指令，已納入 [src](../../src/native/receive/registered_callbacks.c)，通過 C11／C++17 物件核對。相鄰 helper 與16FB6開始的IRQ不混入本輪範圍。

- **已確認：** 11442依2、1、16、8、4順序處理旗標；16F00依2、4、1處理，兩個byte計數器先模256遞增再與2比較。[位址契約](provider-contracts.json)與[原始指令](evidence.json)可追溯。
- **推論：** 119C8透過ROM槽4006C／4012C／40068呈現類似訊息接收、分派、釋放的路徑。原廠API名稱、旗標用途與時間單位未證；不假設完整A1回傳遮罩被截成uint16。
- **未確認：** 17個靜態資料位址尚未提供內容，9508用途未分類。接上3個舊回呼，同時展開28個依賴；仍有115個真實缺口。[清單](next-providers.json)。

完整來源檢查涵蓋119個C/H檔、186組比較與372個物件；保留舊118個C/H檔及1093筆產物記錄。單體物件有613個ELF section；新版 [reader v4](../../experiments/tsl9-feature-dispatch-tree/elf_reader-v4.py)僅將section上限從512提高到1024，另以獨立解析器核對兩種語言物件。舊reader與來源檢查器保持不變。

主元件為26,416B code＋714B data、1,726重定位、115真實匯入。診斷ELF配置回名義原始位址後，選定27,130B逐byte吻合；產物**沒有PT_LOAD**。靜態流程核對9,078指令、1,528個直接轉移與594個呼叫返回位置，一般續行沒有缺口。465個間接轉移與10個MRET的執行期目標仍未證，原始EBREAK／向量邊界保留。[機器摘要](summary.json)。

本輪不執行韌體、HOST模型或ISA模擬，不接觸硬體、BLE／CAN／Flash或原廠網路，不產生BIN。實體MCU、installed ROM、記憶體ownership、完整啟動／IRQ與OTA相容性未證，尚不能宣稱可刷入。
