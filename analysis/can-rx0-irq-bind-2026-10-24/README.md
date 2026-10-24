# CAN RX0中斷與佇列整合

[English](readme.en.md) · [結果](summary.json)

已將三個既有C/C++單位接入啟動元件：IRQ12C24（52B／17指令）、接收資料整理18D78（164B／53指令）、ring12BC8（92B／32指令）。共308B／102指令，在純資料原位址重定位驗算後全部與原廠相同。

| 真實部分連結 | 結果 |
| --- | --- |
| 程式／資料 | 956B／335原指令＋456B資料；父元件648B程式與全部資料保持不變 |
| 架構區域／引用 | 116個非零FUNC區域、2個明示alias、153 RELA、6 UND |
| 向量 | 第36槽接到真實12C24入口；57個槽連到真實程式 |
| 提供者 | 18D78與12BC8直接呼叫均已接上；32B條件式frame與兩個MRET出口保留 |

靜態呼叫關係如下；這不是實機執行觀察：

~~~mermaid
flowchart LR
  IRQ["Vector36 /12C24"] --> RX["18D78 /20B record"]
  RX --> ADAPTER["12C3C /ID, DLC, payload"]
  ADAPTER --> RING["12BC8 /32 slots x12B"]
  RING --> ROM["word4004C /unknown provider"]
~~~

[SDK對照與記錄格式](hardware-sdk-match.json)確認原碼的CAN1地址40006400、FIFO0選擇／釋放、mailbox欄位及20B記錄格式與保存的CH32V20x CAN_Receive對應。這是暫存器／演算法的靜態對照，不是實體晶片識別。

同一份header的CH32V20x_D8W分支才有BB=63、LLE=64；原廠映像這兩槽分別指向1873E與8498，支持D8W軟體配置候選。[下一個LLE候選](static-frontier.json)選定8498–851E的134B／64指令，保留完整128B frame、29組save/load、GP+384間接callback及MRET；後面的2個零值bytes另記為資料，不編入code。這段尚未重建／編譯，且IRQ／callback契約未證。

**仍不能當作可刷BIN。** ring保留原12BD2的AUIPC，因此VMA0診斷元件不會自然得到原2000C038表格位址。4004C駐留callback身分未知；DLC<=8、擴充ID及caller/filter政策未證。剩餘8448、8498、979E、19BD4、main9008、resident40000，以及原機記憶體／IRQ／ROM／啟動／OTA相容性仍未閉合。

本輪沿用原C/H與manifest；當前108組來源比對／216物件證據通過。候選新功能是分通道IRQ／佇列滿診斷，目前只新增離線記錄格式報告，未改原機邏輯。

[三份原收據索引](publication-provenance.json) · [實驗與重播](../../experiments/tsl9-can-rx0-irq-bind/README.md)。未執行目標、HOST模型、ISA模擬或硬體／網路操作；commit／push因歷史個資持續暫停。
