# RTC alarm 中斷：離線 C/C++ 重建

[English](readme.en.md) · [結構化結果](summary.json) · [原始碼](../../src/native/irq/rtc_alarm.c)

原 BIN 的五個區域共 **78B／23 指令**已重建為 C/C++ 加明確暫存器／控制轉移組語埠。C11、C++17 實際物件均通過：62 個非控制轉移 bytes 直接相同；四個 relocation 依原位址作靜態編碼後，全部 78 bytes 相同。沒有執行指令或模擬暫存器狀態。

| 原位址 | 範圍 | 已確認操作 |
| --- | --- | --- |
| 19BD4–19BF0 | 28B／8i | GP+392 寫 1、三次呼叫、MRET；未新增 frame |
| 18E86–18E90 | 10B／3i | 對 40010414 寫入 A0 word |
| 19272–19282 | 16B／5i | 重複讀取 40002804 halfword，測試位元 0x20 |
| 19282–19296 | 20B／6i | halfword 讀取、補數遮罩、halfword 寫回 |
| 19296–1929A | 4B／1i | 無 link 的尾跳至 19282 |

位址、寬度、向量 57 與遮罩符合先前保存的 WCH RTC／EXTI 標頭，屬於軟體配置對應，**不證明實體晶片或喚醒功能**。GP+392 是寫入常數 1 的旗標，不能描述成事件計數器；其消費端仍待追查。原始輪詢沒有 timeout，本輪完整保留；未證明其會結束。

真實向量 57 已接上 28B 入口。部分啟動元件為 **1246B code＋456B data／157 RELA／3 UND**；原 1168B code 與所有資料完全保留，沒有假 provider 或 ABS 替代。61 個非零向量槽位連到真實程式碼，剩餘向量入口是 979E。另有主程式 9008、resident 40000，以及未包含於 UND 數字內的動態 callback／IRQ 契約。

目前 `src/` 有 83 個 C/H、56 個程式單位與 1 個獨立指標資料單位。112 組函式來源比較／224 物件，加上資料 2 組／4 物件，合計 **114 組／228 物件**。先前 110 組結果與 661 筆 artifact 紀錄未變。

[四份公開收據](publication-provenance.json)與[實驗重播](../../experiments/tsl9-rtc-alarm-irq/README.md)保留可追溯性；完整整理收據仍留本機。未修改凍結 checker，未重跑舊負例矩陣。

[下一個計時器前沿](next-timer-frontier.json)在固定 512B 視窗中選出 979E–9958 的 442B／138 指令直接控制流候選，含六次直接呼叫與兩次間接呼叫。直接邊未超出視窗；callee 返回、完整函式範圍與 IRQ ABI 仍未證明。

值得加入的功能候選是唯讀 RTC alarm／pending 狀態診斷；需先追到 GP+392 消費者，證明 IRQ、RAM ownership 與安全讀出通道。本輪尚未加入實機新功能。

**這是 VMA0 的 ET_REL 部分元件，並非可刷入映像。** 未證明原硬體、ROM、最終地址與 RAM 配置、完整啟動／BLE OTA；未新增 BIN、連硬體或網路。Git 歷史個資尚未清理，未 commit／push。
