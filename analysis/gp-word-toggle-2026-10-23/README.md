# GP guard／word XOR 葉函式

[English](readme.en.md)

已以可讀 C 重建原廠 `0x9B36–0x9B4E`：24B／7 指令；C11 與 C++17 的機器碼逐位元組相同。選用來源在 [`src/native/receive/gp_word_toggle.c`](../../src/native/receive/gp_word_toggle.c)。這是局部架構契約，尚非可刷韌體。

| 已確認行為 | 證據 |
| --- | --- |
| 讀取當下 GP+168 的 unsigned byte；非零就返回，A4 保留入口值 | `9B36 LBU`、`9B3A BNEZ → 9B4C` |
| 零值時，讀取 `0x4001080C` 的 word、XOR 2、寫回同位址 | `9B3C LUI`、`9B40 LW`、`9B44 XORI`、`9B48 SW` |
| 只改寫 A4／A5；返回使用 RA 清除 bit0 | `9B4C RET`；無 frame、call、CSR 或 IRQ masking |
| 原廠佇列在 `0x12D1C` 呼叫此函式，返回位址為 `0x12D20` | 原始 JAL 與正式收據 typed edge |

實體周邊用途、GP／記憶體有效性與 IRQ 交錯仍未知，不能稱為 LED 或蜂鳴器控制。讀改寫不是原子操作；不保證 fault 復原。

完整部分連結實際為 **1926B／669 指令／108 strong FUNC／97 pending RELA／3 UND**，新增函式使用真正的 C 物件定義，沒有 ABS 替代。三個缺口為 `9454`、`12ABE`、`14D2E`。97 個原廠轉移的目的地及非 relocation 位元均已核對；診斷 ET_REL 內的控制位移仍待解析。既有 1588B 原位圖保持原樣，未把這個獨立葉函式冒算成更大的閉合圖。

新版檢查器每個語言通過 1991 個靜態負例。獨立審查曾找到 v1／v2 的 UND／IR 漏檢；v3 對同六項變異各重測兩語言，12／12 拒絕。完整 IR body 雜湊只證明固定產物一致，並非泛用 SSA 證明。舊來源、失敗的 26B early-return 試作及舊收據均保留。

來源整理共65個 C/H、39個 native units；78組來源前後比對／156物件已通過，先前76組結果及既有編譯物件均未改變。整合證明直接核對當前13個來源單位、其編譯依賴與真實物件；不把舊全域 manifest 收據冒稱為新版來源的完整重播。

[證據來源／雜湊](publication-provenance.json) 包含四份逐位元組保留的可攜原收據，以及一份只匿名化路徑的來源整理收據。原始資料另保留於本機 ZIP，公開衍生副本不冒充原始收據。原始 BIN／APK 未改動。

尚未證明原機晶片、installed ROM、完整啟動／記憶體 ownership／中斷或 BLE OTA；本輪不產出韌體 BIN、不執行目標或硬體。未來值得考慮的是依既有授權日誌區分「guard 跳過」與「實際寫入」的診斷狀態；目前沒有實機觀察來源，也尚未實作此功能。

[重跑方式](../../experiments/tsl9-gp-word-toggle/README.md) · [獨立審查](independent-review.json) · [結果](summary.json)
