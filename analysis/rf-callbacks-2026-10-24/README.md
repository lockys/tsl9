# 更正後的 RF task／status 回呼

[English](readme.en.md)

新增 [C/C++ 原始碼](../../src/native/receive/rf_callbacks.c)：**17476–1753A，196B／65指令／23架構區塊**。C11／C++17的144個非控制bytes與16個具型別參照，經純資料原位址編碼後全部相同。[正式收據](evidence/standalone-trial.json)

## 位址更正

前輪人工換算把兩個callback各記早16B。現直接解析原AUIPC／ADDI編碼，得到task入口17476與RF status入口174EE。[更正記錄](literal-address-correction.json)／[原指令範圍](corrected-frontier.json)

舊212B投影保留，未當成有效函式：它起於17466，落在17464的4B LW中間，才產生兩列1B invalid解碼。這不是原韌體存在無效指令的證明。相關文件／工作索引已更正；原生父物件與原始收據未改寫。

## 靜態行為

- Task保留16B frame、低16-bit signed事件測試及共用還原出口。高位事件路徑呼叫訊息接收表項，必要時呼叫釋放表項。
- Event bit1依序呼叫fresh then-live S1+464／+460，傳入原state buffer／length及A2／A3=255；回傳then-live S0 XOR1。
- Event bit2將A0=1傳給173EE，再經共用出口回傳then-live S0 XOR2；未選中的事件路徑回傳0。
- Frameless status回呼保留A0==2、A1、A2+1／+2／+3三個原byte比對，以及往17442／173EE的原尾跳。未縮窄buffer存取、未移除比對；buffer界限與已安裝callback ABI仍未證明。

[SDK預設對照](rom-profile-correspondence.json)包含訊息接收／釋放與RF_Shut／RF_Tx。名稱僅為profile對應，不能代替installed ROM或實際RF傳送證據。

## 整合與限制

完整196B真實回呼本體已加入部分元件，**未新增假alias或宣稱原literal pointer已接通**。元件為 **4030B code＋456B data、340個非零FUNC、13個既有alias、278 RELA、19個直接UND**。新增173EE／17442，所以UND由17增為19；原3834B code／456B data與62個非零向量綁定皆保留。[原生證據](evidence/native-c.json) · [依賴清單](pending-providers.json)

`src/`現有92個C/H；code來源比對130組／260物件，指標資料另2組／4物件，共 **132組／264物件**。SDK配置資料核對重用前輪原件，[公開收據](evidence/rf-layout.json)僅CRLF→LF衍生，原件保留本機。

下一輪為[173EE–17476提供者家族](next-rf-providers.json)，136B／45指令。可探索被動RF結果診斷，區分raw status／接收狀態／header不符，需先證明ABI與memory ownership；目前未加入韌體。

VMA0 ET_REL不證明原位址、實機ROM／記憶體／完整啟動／IRQ或BLE OTA相容性。本輪無目標／HOST model／ISA／ESIL執行、硬體／網路操作、新BIN、commit或push。[建置收據](evidence/integration-build.json) · [匯出來源](publication-provenance.json)
