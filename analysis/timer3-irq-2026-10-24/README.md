# TIM3 中斷：離線 C/C++ 重建

[English](readme.en.md) · [結構化結果](summary.json) · [原始碼](../../src/native/irq/timer3_irq.c)

原 **979E–9958，442B／138 指令**已分成 32 個有明確相鄰順序的架構區域，分別編譯成 C11、C++17。376 個非控制 bytes 直接相同；24 個具型別控制轉移依原位址靜態編碼後，全部 442 bytes 相同。未執行目標或模擬 ISA。

來源使用 C unsigned 運算與 volatile 讀寫，加上必要的暫存器／控制埠。保留原 16B frame、S0／S1／S2 save／restore、AUIPC、signed DIV、MRET 與 compressed JALR。live-register 邊界防止 C 運算被移過實體 S-register 操作；這些區域不是一般可獨立呼叫的 C 函式。

既有 C/C++ 的四個完整 helper 共 60B 已選入：81B0 的時間包裝三區域、93EE 的停用葉函式；每個原廠 byte 相同。沒有假 provider 或替代實作。

真實向量 45 已綁定。部分啟動元件為 **1748B code＋456B data／181 RELA／2 UND**；原 1246B code 與所有資料未變。選定向量資料中 62 個非零槽位皆連到真實程式碼；不代表已證明實體 IRQ 數量、上下文或完整韌體。直接符號缺口剩主程式 9008 與 resident 40000；動態呼叫不包含於此數字內。

目前 `src/` 有 84 個 C/H、57 個程式單位與 1 個獨立資料單位。114 組函式來源比對／228 個物件，另有 2 組資料比對／4 個物件，合計 **116 組／232 物件**。先前 112 組結果與 673 筆 artifact 紀錄保持不變。

[指標與 SDK 邊界](pointer-boundaries.json)區分固定 word40068、當下 S2+12，以及時間包裝的 word4007C。S2 原始計算值是 2000BEBC，但不能假設所有未知 provider 都保留它。保存的 WCH 標頭對應 TIM3 autoreload／channel3 compare；這只支持軟體配置推論，不能確認實體晶片、pin 或輸出負載。

6-byte stride 的三個 halfword、phase／index 路徑與週期／比較值，支持「時序波形／序列」候選。值得加入離線序列時間表預覽，將來再評估自訂提示模式；實際是否蜂鳴器、燈或其他負載、時間單位與 live table 內容都未證明，尚未加入實機功能。

[下一個 main 候選](next-main-candidate.json)只選 **9008–901A，18B／8 指令**：16B frame、RA 保存、9250／8180 兩次呼叫、返回。較大的 [284B 解碼視窗](next-main-frontier.json)含多個函式返回，不能整段當成 main。

[五份公開收據](publication-provenance.json)與[本機重播說明](../../experiments/tsl9-timer3-irq/README.md)保留追溯性；完整整理收據留本機，凍結 checker 未修改，未重跑舊負例矩陣。

**此 VMA0 ET_REL 尚不可刷入原機。** 實體 MCU／ROM、動態 provider、IRQ ABI、原位址與 RAM、主程式／完整啟動及 BLE OTA 都未證明。未新增 BIN、連硬體／網路、commit／push；Git 歷史個資問題仍保留待處理。
