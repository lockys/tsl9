# ECALL 上下文恢復：離線重建

[English](readme.en.md) · [結構化證據](summary.json) · [C/C++ 原始碼](../../src/native/irq/ecall_restore.c)

原 BIN 的 **8448–8496，78 bytes／35 條指令**已重建並分別編譯為 C11、C++17；兩者原位址碼皆逐 byte 相同。來源保留 CSR、實體 SP 與暫存器操作的內嵌組語，尚未建立一般 C trap ABI。

- 14-byte 入口以遮罩 32 執行 `CSRS 0x804`，從當下 `SP+0` 取得 MEPC；遮罩不是 CSR 的完整值。
- 64-byte 尾段載入 29 個暫存器、將 SP 加 128，再執行 MRET。入口消費既有 frame，沒有配置 frame，也沒有明確載入 GP。
- 後方兩個零 bytes 是獨立資料，未當作程式碼編譯。[與 LLE 的比較](frame-correspondence.json)證明兩個恢復尾段的 64 bytes 相同；不證明 frame 建立者或中斷 ABI。

部分連結元件為 **1168B code＋456B data、153 RELA、4 UND**；原 1090B code 與全部資料未變。向量 5、8 都連到真實 14-byte 入口，60 個非零槽位已連到真實程式碼，另 2 個向量槽位仍為外部符號。這不是整個韌體的完成率。

目前 `src/` 有 82 個 C/H、55 個程式單位與 1 個獨立指標資料單位；110 組函式來源比對／220 物件，另有 2 組資料比對／4 物件，合計 **112 組／224 物件**。先前 108 組結果及 649 筆 artifact 紀錄保持不變。

[四份公開收據](publication-provenance.json)保留原本可攜格式；完整整理收據仍保留本機。重播入口見[實驗說明](../../experiments/tsl9-ecall-restore/README.md)。本輪只重查正常靜態產物，未執行舊負例矩陣。

下一步追查向量 57 的 19BD4 入口與三個真實 provider。[RTC 候選契約](next-rtc-candidate.json)已分出 28B 入口與 10／16／20／4B 輔助區域，共 78B／23 指令；19296 是跳回 19282 的尾跳，19272 保留狀態輪詢。位址、半字寬度與遮罩符合保存的 WCH RTC 標頭，但尚未編譯這組候選，也不證明實體晶片身分。[現有向量前綴](remaining-vector-frontier.json)另指出 979E 的分支超出第一個 MRET，不能以第一個返回截斷完整函式。

值得後續加入的功能是唯讀 trap／frame 診斷；本輪只建立離線配置報告，實機功能須先證明 frame、CSR、RAM 與讀出通道安全性。

**未產生新的韌體 BIN，未執行目標或模擬 ISA，未連硬體／網路。** 主程式 9008、resident 40000、動態 callback、實體晶片／ROM、最終地址配置、完整啟動與 BLE OTA 仍未證明。Git 歷史個資尚未清理，本輪未 commit／push。
