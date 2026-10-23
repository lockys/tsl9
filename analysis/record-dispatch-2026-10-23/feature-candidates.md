# 新功能候選：離線診斷與拒絕原因
[English](feature-candidates.en.md)

已確認：821E會因pointer+4的bit3、unsigned index>2或state byte>=3而回傳0；12A08還有status／ID／tag分支。18CA4靜態流程在三個bank均不符合時回傳4並略過其寫入。證據分別見 `next-821e-contract.json`、`root-native-review.json`、`next-peripheral-contract.json`；不可把這些數值命名成免打擾、座椅錯誤或CAN壅塞。

值得新增：先在離線分析器提供「原始分支條件／未解析provider／寫入頁雜湊」報表，協助辨識資料被哪道條件拒絕；待證明可用RAM、IRQ並行、resident ABI與BLE回覆格式後，再評估原硬體上只讀的版本／拒絕原因／診斷計數查詢。

本輪未實作新的硬體功能，也不增加車輛控制、自動重試、Flash操作或未知記憶體寫入。先完成18CA4原始執行層與其provider邊界；不得為診斷而改動現有判斷或更新相容性。
