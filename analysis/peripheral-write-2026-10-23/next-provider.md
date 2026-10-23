# 下一段：16B7C tagged 路徑
[English](next-provider.en.md) · [256B原始視窗](next-provider-window.json)

以原FW SHA與既有radare2 SHA核對後，唯讀取得[0x16B7C,0x16C7C)的256B／89條指令；未使用ESIL或執行目標。

候選函式範圍為[16B7C,16C72)（246B），涵蓋正常RET、16C62迴圈cold block與16C6C／16C6E早退。16C72開始另一段參數驗證；目前記為候選邊界，未主張已列出所有外部incoming references。

入口檢查record byte11是否為1／2；再讀取[GP+84] pointer+4 bit3。早退不建立frame；主要路徑建立64B frame並保存RA／S0..S3。原始呼叫包含8520、16994、168DE、1693E；16994已有可重用的獨立register-read重建，其他供應者仍須核對。不可把opaque呼叫當成符合一般C ABI。

下一輪需保留early-return／frame分離、迴圈次數與順序、每次opaque呼叫後then-live SP／S-register／A-register及post-RET路徑；先完成自身執行層，再接真實provider。tag值不證明外部CAN晶片型號、數量、座椅或免打擾語意。
