# main、應用迴圈與初始化：離線重建

[English](readme.en.md) · [結構化結果](summary.json) · [C/C++ 原始碼](../../src/native/startup/main_family.c)

三段原廠範圍已重建並以 C11、C++17 實際編譯核對：

| 範圍 | 大小 | 已確認結構 |
| --- | --- | --- |
| 9008–901A | 18B／8i | 16B frame、RA 保存、9250／8180 呼叫、RA 恢復與返回 |
| 8180–81AA | 42B／15i | 持續迴圈、當下 S2+0 回呼、17002／12C58、watchdog 寫入 |
| 9250–9290 | 64B／19i | 原順序 14 次呼叫、恢復 RA／SP、無 link 尾跳 17BF6 |

合計 **124B／42 指令、23 個架構區域**。52 個非控制 bytes 直接相同；20 個具型別控制轉移依原位址靜態編碼後，全部 124 bytes 相同。保留明確的 frame／S-register／RA 埠；不是可獨立呼叫的一般 C 函式，未建立 entry／callee ABI。

既有 9F4C 的 **40B／15i** 完整 C/C++ 葉函式已接入，保留五筆有序 word 寫入。[watchdog／callback 邊界](watchdog-boundaries.json)對應保存的 WCH IWDG 標頭；確切 timeout、實體晶片與實際服務情況未知。應用碼先設定 S2=20000000、S1=40003000、S0=AAAA，之後使用當下暫存器；不假設未知 provider／IRQ 保留這些值。

實際部分元件為 **1912B code＋456B data／201 RELA**，原 1748B code 與所有資料未變。main9008 已連到真實 18B 程式；選定 62 個非零向量仍全部有真實程式碼。真正呼叫鏈展開後，[17 個具體依賴](pending-providers.json)包含初始化／接收提供者及 resident40000；動態回呼另列未知，尚未閉合完整應用。

目前 `src/` 有 85 個 C/H、58 個程式單位與 1 個獨立資料單位。116 組函式來源比對／232 個物件，加上資料 2 組／4 個物件，合計 **118 組／236 個物件**。先前 114 組結果與 685 筆 artifact 紀錄未變。

[下一個尾段前沿](next-tail-frontier.json)顯示 17BF6 呼叫 resident 指標 word40048，另有 90B0／1798A 呼叫及到 17B92 的回跳。96B 解碼窗未涵蓋完整函式；不可用窗內第一個返回猜測範圍。初始化資料中可辨識的位址只是候選值，不能當成已確認的 runtime callback。

值得後續加入唯讀主迴圈／watchdog／重啟原因診斷；須先證明 RAM、IRQ、clock 與安全讀出契約。本輪未加入實機功能，也未改變原 watchdog 行為。

[五份公開收據](publication-provenance.json)及[重播方式](../../experiments/tsl9-main-family/README.md)保留追溯性；完整整理收據留本機，凍結 checker 未修改，未重跑舊負例矩陣。

**這仍是 VMA0 的 ET_REL 部分元件，尚不可刷入原機。** 實體 MCU／ROM、記憶體與原位址、完整啟動／BLE OTA 仍未證明；未新增 BIN、連硬體／網路、commit 或 push。Git 歷史個資問題仍未處理。
