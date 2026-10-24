# Resident 提供者與 RF 組態證據

[English](readme.en.md)

新增 [C/C++ 原始碼](../../src/native/receive/resident_providers.c)：1753A–17666，共 **300B／103指令／12架構區塊**。C11／C++17的298個非控制bytes與1個具型別分支，經純資料原位址編碼後全部相同。[正式收據](evidence/standalone-trial.json)

1753A保留A6／A7用途、frame前flag條件及16B frame。原AUIPC表達式指向flag2000C7A9；非零時回傳1。正常路徑處理GP366序號欄位、封裝參數，再以fresh then-live S0+76／512／88／80間接呼叫，最後回傳0；這不是實際RF傳送成功證明。

175E8保留48B frame，以原2000C7A0、長度268等參數呼叫，傳入原17476 task callback並保存回傳byte；之後以長度32等參數處理stack組態，保留所有寫入次序與174EE literal callback。

## SDK／原生資料配置對照

已保存SDK的預設表項對應memcpy、RF_SetChannel、start-task、set-event、memset、task registration及RF_Config。[來源行與表項](rom-rf-profile-correspondence.json) 表項位址不是函式入口；實際使用then-live S0，不能假設未知callee不改變它。

把SDK的原始callback typedef與rfConfig_t宣告擷取後，以相同ILP32 C11／C++17配方編譯為**僅64B資料、零函式**的物件；兩語言皆核對size32、alignment4及欄位offset。[公開收據](evidence/rf-layout.json)僅正規化CRLF為LF；原Windows收據保留本機，JSON內容核對相同，雜湊關係見匯出來源。

| 原碼stack寫入 | 所選SDK配置欄位 |
| --- | --- |
| +0 halfword2501 | LLEMode=1、Channel=37 |
| +8 word8E89BED6 | accessAddress |
| +12 word00555555 | CRCInit |
| +16 word174EE | rfStatusCB原literal位址 |
| +25 byte4 | HeartPeriod；未證明裝置實際時間 |

這支持RF軟體組態的對應推論，**不證明實機MCU／無線電拓撲、installed ROM版本、callee身分或ABI**。資料配置物件僅供核對，未連入韌體；未執行SDK函式或模組。

## 整合結果與後續

1753A已綁到真實12B入口，完整300B接入。元件為 **3834B code＋456B data、317個非零FUNC、13個入口alias、262 RELA、17個直接UND**；原3534B code／456B data與62個非零向量綁定保留。[原生證據](evidence/native-c.json) · [依賴清單](pending-providers.json)

`src/`現有91個C/H；code來源比對128組／256物件，指標資料另2組／4物件，合計 **130組／260物件**。SDK配置的兩個資料物件另計，不混入來源比對。仍為VMA0 ET_REL；literal回呼、原位址配置、ROM／記憶體／完整啟動／IRQ與BLE OTA尚未證明。

下一輪重建[17476–1753A RF回呼候選](../rf-callbacks-2026-10-24/corrected-frontier.json)，196B／65指令；[C776有界片段](c776-bounded-backlog.json)另保留，未把256B範圍當成完整函式。可探索被動RF狀態／逾時診斷，需先證明資料ownership及ABI；目前未實作。

本輪無目標／HOST model／ISA／ESIL執行、硬體／網路操作、新BIN、commit或push。[建置收據](evidence/integration-build.json) · [匯出來源](publication-provenance.json)

更正：先前人工換算把兩個callback各記早16B。現依AUIPC／ADDI原編碼確認為17476／174EE；保留原212B候選投影與原生收據，詳見[更正記錄](../rf-callbacks-2026-10-24/literal-address-correction.json)。
