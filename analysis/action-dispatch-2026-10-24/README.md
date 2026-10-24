# 動作分派器：完整離線 C/C++ 重建

[English](readme.en.md)

完整10DCC、13EB4、155D0、16B50共3,904B／1,571指令與1,012B唯讀相對跳轉表，已納入 [action_dispatch.c](../../src/native/receive/action_dispatch.c)。原有record_dispatch.c另行保留、不覆寫。C11／C++17核對全部原始程式／表bytes及252個重定位。[證據](evidence.json) · [契約](provider-contracts.json)。

- **已確認：** 155D0使用253個有號相對表項，指向174個真實指令入口；39項進入還原／返回區塊。表之前還有狀態門檻與pending-byte分支，被表排除的數值不代表完全不執行動作。[數值對照](case-map.json)。
- **已確認：** 13EB4檢查兩個描述子slot，符合條件才傳送含長度前綴的資料，最後轉入原清理槽。16B50對已證呼叫索引選出0x20／0x24，轉交FF E0 00 00 payload。ROM與實體用途未證。
- **新增證據：** 9508同時出現位址引用與直接控制呼叫；函式內容仍未提供。
- **未確認：** 接上四個舊入口並展開74個依賴，仍有185個真實匯入缺口。[清單](next-providers.json)。不以數值猜產品功能名稱。

完整來源證明涵蓋121個C/H檔、190組比較／380物件；舊120個C/H檔及1117筆產物記錄不變。主元件30,784B code＋1,726B data／2,007重定位；選定32,510B在名義原址逐byte吻合，診斷ELF入口0且**沒有PT_LOAD**。靜態核對10,819指令、1,801直接轉移及654個呼叫返回位置，一般續行沒有缺口；表guard與253個候選對照實際連結bytes，但執行期目標、482個間接轉移、10個MRET與trap恢復仍未證。[摘要](summary.json)。

[新功能候選](feature-candidates.json)包含離線數值動作清單與雙slot資料診斷，尚不構成硬體功能成功。本輪不執行韌體、HOST模型或ISA模擬，不操作硬體、BLE／CAN／Flash或原廠網路，不產生BIN。MCU、installed ROM、RAM／IRQ／啟動與OTA相容性未證。
