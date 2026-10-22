# 16B0A 接收入口重建

[English](readme.en.md) · [C/C++與驗證方式](../../experiments/tsl9-receive-wrapper/README.md) · [下游契約](downstream-contracts.json)

**已確認：**70B／26指令的入口14B、主體56B緊鄰；四個呼叫／尾跳視窗外54B與原廠一致。原16B frame、先檢查A0 bit0再存S0、呼叫後使用當下S0／S1、fresh saved-slot reads及尾跳順序保留。

S0／S1的架構埠避免LLVM額外建立callee-save frame；其中mask0x02判斷與分支明示為組語埠，不宣稱pure C實作。其他條件、參數與呼叫流程以C重建。

實際132B ET_REL區段包含62B消費函式與70B接收函式。兩個caller relocations指向真實receiver FUNC定義；四個下游relocations仍指向三個UND providers。所有relocations都保留，這是連結結構證據，**不是已解析執行碼或可燒錄韌體**。

**新發現：**`16A7C→12BC8→[4004C]`可到未知resident provider，已知也會使用A6／A7／T1／T3；不能把clobber清單解讀為完整ABI。SPI逾時回傳0亦無法與有效byte0區別，值得另加診斷計數；尚未實作，需先證明RAM與IRQ契約。

正式收據採可攜路徑且保留本機原件；curation公開檔是具原始SHA的路徑匿名化衍生檔。實體晶片、完整resident／IRQ／main與OTA相容性仍未證明；沒有執行RV32、MMIO或操作硬體。
