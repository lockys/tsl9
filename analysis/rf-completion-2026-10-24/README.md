# RF 完成回呼、重試與整段相對佈局

[English](readme.en.md)

新增 [C/C++ 原始碼](../../src/native/receive/rf_completion.c)：173EE–17476，共 **136B／45指令／7架構區塊**。C11／C++17的126個非控制bytes與3個具型別參照，純資料原位址編碼後全部相同。[收據](evidence/standalone-trial.json)

原碼先以表項4005C處理event2，再清除原state bytes；保存的callback非零時，以then-live S0傳遞原參數，按原順序還原S0／RA、清除callback word、還原SP，最後透過已捕捉T1尾跳。空callback保留另一條原還原／返回路徑。

17442先讀byte、遞減並遮罩255、寫回，再決定以A0=1尾跳173EE或以event1／time參數2透過40058重排程。**沒有遞減前的零值guard**；保留原wrap行為，不宣稱硬體上有有界重試。[SDK配置對照](rom-profile-correspondence.json)只是profile，不是installed ROM／ABI證明。

## 主元件

兩個原待解析參照已綁到真實26B／24B入口，全部136B一起連入。主元件為 **4166B code＋456B data、347個非零FUNC、15個真實入口alias、281 RELA、17個直接UND**。原4030B code／456B data與62個非零向量綁定保留。[原生證據](evidence/native-c.json) · [依賴清單](pending-providers.json)

`src/`共93個C/H；code來源比對132組／264物件，指標資料另2組／4物件，共 **134組／268物件**。這是來源與原指令證據，不是整體行為或實機驗證。

## 六單位 RF 相對佈局

另把六個**現有實際curated物件**按原區塊順序連結，得到173EE–179FC對應的 **1550B／538指令、103真實FUNC區塊、5個入口alias、56 RELA**。所有區塊連續，53個內部直接參照與6組內部AUIPC／ADDI函式指標位址算式，都對應到實際原生symbol offset；整段純資料原位址編碼後與原BIN相同。[證據](evidence/rf-relative-c.json)／[完整收據](evidence/rf-relative-build.json)

隔離RF物件仍有3個外部provider：90B0、9124及C776；前兩者在主元件已有實作，此隔離配置沒有複製它們。1AAE8表格資料亦未包含。

**這不是原始絕對位址配置證明。** 第一次嘗試要求VMA173EE，LLD部分連結輸出的ET_REL仍為VMA0，該要求未通過；保留本機原輸出，沒有改寫ELF header或加入假provider。接受的核對明確只證明相對offset及內部位址對應。RAM的AUIPC、外部提供者位置、最終image、installed ROM／IRQ／硬體與BLE OTA均未證明。

下一步追查[有界C776候選](next-c776-candidate.json)，114B／42指令及四個外部目標；不把它當成已證明完整ABI。可探索被動重試／完成狀態診斷，但須先證明memory ownership與並行／callee契約，目前未加入韌體。

本輪無目標／HOST model／ISA／ESIL執行、硬體／網路操作、新BIN、commit或push。[主建置收據](evidence/integration-build.json) · [匯出來源](publication-provenance.json)
