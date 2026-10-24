# 事件消費、重試回呼與色盤線索

[English](readme.en.md)

新增 [C/C++ 原始碼](../../src/native/receive/event_consumer.c)：原廠17666–1787C，共 **534B／187指令／35架構區塊**。C11／C++17的472個非控制bytes與23個具型別參照，經純資料原位址編碼後全534B吻合。[正式收據](evidence/standalone-trial.json)

## 靜態觀察

- 17666保留16B frame；以GP379、event1、time參數2呼叫表項40058。then-live S0與fresh GP378共同決定是否以原176A0位址呼叫90B0，再設GP378=1。
- 176A0保留32B frame，建立halfword62B5並呼叫1753A；A5為原17666位址。零結果時遞增8-bit GP377；值<=4才以time參數500排入9124。未將結果值或時間參數等同實際成功／毫秒。
- 176F8保留48B frame。event bit1處理佇列；只有1753A回傳零的路徑才以fresh then-live S1讀取更新索引／計數，透過共用出口回傳then-live S0 XOR1。
- event bit2使用fresh GP376與word[GP104]的7B記錄，保留兩次copy可能性、條件式GP變更、原生signed REM及C776呼叫。未將未知GP欄位命名為座椅或免打擾。

## 七項色盤候選

1783A的原AUIPC表達式指向1AAE8；程式先用GP370 byte查表，再遞增並做signed REM7。[所選28B資料](selected-1aae8-data.json)的七個little-endian words為：

`000000FF, 00007DFF, 0000FFFF, 0000FF00, 00FFFF00, 00FF0000, 00FF00FF`

這些24-bit常數支持「色盤輪播」推論，尚未確認RGB／BGR、通道順序或實體燈效用途。可探索自訂七段色盤與離線預覽；目前未實作。**後面的REM7不能證明先前查表索引有界**。所選28B也尚未連入元件，不宣稱完整表格extent或ownership。

## 整合與限制

真實17666參照已綁到24B入口，完整534B連入；90B0與9124重用父元件真實定義。新增1753A／C776，故直接UND由17增為18。元件為 **3534B code＋456B data、305個非零FUNC、12個入口alias、261 RELA**；原3000B code／456B data與62個非零向量綁定皆保留。[原生證據](evidence/native-c.json) · [依賴清單](pending-providers.json)

採trial-v2；trial-v1因原4B ADDI編為2B未通過，舊輸出保留本機且未宣稱成功。SDK預設memcpy／start-task表項僅為[配置對照](rom-profile-correspondence.json)，不是installed ROM／ABI證明。literal callback仍需要原始PC配置。

`src/`共90個C/H；code來源比對126組／252物件，指標資料另2組／4物件，合計 **128組／256物件**。VMA0 ET_REL不是可燒錄BIN；實機ROM、記憶體、完整啟動／IRQ與BLE OTA仍未證明。

下一步為[1753A–17666候選家族](next-1753a-frontier.json)，300B／103指令，含兩個入口候選及八個間接呼叫。本輪無目標／HOST model／ISA／ESIL執行、硬體／網路操作、新BIN、commit或push。[建置收據](evidence/integration-build.json) · [匯出來源](publication-provenance.json)
