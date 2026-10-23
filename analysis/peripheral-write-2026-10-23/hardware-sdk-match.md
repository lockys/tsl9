# CAN SDK 靜態對應
[English](hardware-sdk-match.en.md) · [雜湊與來源行號](hardware-sdk-match.json)

離線讀取先前已封存的CH32V20x SDK header／CAN source，並核對三個檔案雜湊；沒有重新下載或執行SDK。

| 原BIN觀察 | 本機SDK對應 |
| --- | --- |
| 呼叫端base40006400；status+8，bits26／27／28 | CAN1_BASE；CAN_TypeDef.TSTATR；TME0／1／2 |
| mailbox起點+384、stride16、三組 | 8個word加88個reserved words；sTxMailBox[3]，每組四個word |
| +384／388／392／396 | TXMIR／TXMDTR／TXMDLR／TXMDHR |
| record words0／4、bytes8／9／10、payload11..18 | CanTxMsg.StdId／ExtId／IDE／RTR／DLC／Data[8] |
| ID移位21／3、完整IDE／RTR byte、DLC&15、兩個payload word、最後OR1、未選中回4 | CAN_Transmit（cached source行399..451） |

這是對CAN_Transmit／bxCAN類SDK函式的強靜態對應，支持CH32V20x家族候選；共用周邊配置仍不能唯一辨識TSL9晶片、封裝、接腳或transceiver。SDK高階C運算式也不證明原BIN的存取求值順序；重建仍以72條原始指令為準。

未觀察到實際CAN傳送。16B7C的tag1／2路徑尚待重建，不能據此宣稱實體模組具有幾組外部CAN晶片。
