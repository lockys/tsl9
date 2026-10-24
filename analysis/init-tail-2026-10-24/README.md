# 初始化尾段、共用返回與排程器整合

[English](readme.en.md) · [結構化結果](summary.json) · [新增 C/C++](../../src/native/startup/init_tail.c) · [既有排程器](../../src/native/receive/scheduler.c)

原 **17B92–17BC4、17BF6–17C4E，共 138B／47 指令**已重建為 10 個架構區域。C11／C++17 的 120 個非控制 bytes 相同；5 個具型別轉移依原位址靜態編碼後，全部 138 bytes 相同。constructor 恢復 S0／RA／SP 後才尾跳至共用區域；保留 GP+378 的 fresh 讀取、條件式 frame、兩條返回路徑及三次 resident 間接呼叫。

既有 **9124–9250 排程器 300B／115i／28 區域**已完整接入，所有原位址編碼 bytes 相同，11 個直接控制參照均有真實來源，沒有直接 UND。只呼叫舊 checker 的正常物件檢查函式；未執行歷史負例矩陣。它的四個 resident 轉移與呼叫契約仍未證明。

實際部分元件為 **2350B code＋456B data／217 RELA／18 UND**。原 1912B code 與全部資料未變，17BF6 對應真實 constructor 入口，9124 對應完整原排程器。選定 62 個非零向量仍連到真實程式碼。這不是完整韌體完成率；[18 個直接依賴](pending-providers.json)之外，還有動態回呼與 ABI 缺口。

[ROM 標頭對應證據](rom-header-correspondence.json)列出已保存 WCH 標頭的預設表格與型別：

| 表項 word／slot | SDK 介面對應 | 原 BIN 證據 |
| --- | --- | --- |
| 40048 | tmos_memset | A1=0、A2=3／115 的兩次呼叫 |
| 40080 | TMOS_ProcessEventRegister | callback 位址參數、回覆低 byte 寫 GP+379 |
| 20000000 | TMOS_SystemProcess | 8180 應用迴圈的 RAM 回呼 |
| 4007C | TMOS_GetSystemClock | 既有時間包裝的讀取；標頭記載 0.625ms 單位 |
| 20000008 | LLE_IRQLibHandler | 既有 RAM+8→GP+384 初始化候選 |

以上是 **表項地址與介面配置對應**，不是已取得函式入口或證明裝置 ROM 的版本／內容。原先的暫存器埠與呼叫順序完全保留，沒有改成推測的標準函式庫呼叫。

目前 `src/` 有 86 個 C/H、59 個程式單位與 1 個獨立資料單位。118 組函式來源比對／236 物件，加上資料 2 組／4 物件，合計 **120 組／240 物件**；先前 116 組結果與 697 筆 artifact 紀錄未變。

[下一個 callback family](next-callback-family.json)涵蓋 901A–9124 的 266B／102 指令候選，包含目前缺少的 90B0。901A／9070 區域互有跨界控制路徑，不能以各自第一個 RET 截成獨立函式。

值得後續加入唯讀 BLE／TMOS task 與延後工作狀態診斷；需先追查 callback／旗標消費者，並證明 ROM、RAM、IRQ 與讀出契約。本輪未加入實機新功能。

[五份公開收據](publication-provenance.json)與[重播說明](../../experiments/tsl9-init-tail/README.md)保留追溯性；完整整理收據留本機，凍結 checker 未修改。

**VMA0 ET_REL 仍不可刷入原機。** 實體 MCU／ROM、原位址與 RAM、完整啟動／BLE OTA 未證明；未新增 BIN、連硬體／網路、commit／push。Git 歷史個資問題仍待處理。
