# OTA 頁面回覆：本輪證據入口

[English](readme.en.md)

本輪新增原始 `0x9B8E..0x9C0A` 的可讀 C/C++ 元件。獨立元件的
124 bytes／50 指令已在兩語言新編譯、明確 ABI 排序及固定地址連結後，
與原始函式完全相同。完整十一函式映像保持不變；第十二函式尚未納入。

**來源契約更正：** `0x9DF4` 的 `69 3b` 是 RV32 `C.JAL`，會設定
`RA=0x9DF6` 並呼叫 `0x9B8E`，不是無連結尾跳轉。原始封存
`source-review/contracts.json` 的 `recorded_RELA.external_incoming_role`
以及該封存三份語言說明中的「共用實體尾端路徑」文字，應由
[來向呼叫更正](entry-call-correction/README.md)取代。舊封存保留供追溯。
這不改變函式自身 `0x9BF8` 透過 T1、不更新 RA 的釋放尾端轉移。

| 問題 | 本輪證據 | 邊界 |
| --- | --- | --- |
| 原始函式的運算元與流程 | [原始解碼](source-review/README.md)及上述更正 | 靜態指令欄位，不是執行觀察 |
| 可讀 C/C++ 與主機模型 | [實作封存](implementation/README.md) | 每語言 87 案例、3,634 次檢查；六個編譯反例 |
| 獨立來源效果檢查 | [獨立檢查](code-review/README.md) | 每語言 90 案例、6,699 次檢查；十個編譯反例 |
| 原生呼叫、IR、固定地址 | [ABI 檢查](ABI-review/README.md) | TX 只有數值地址見證，未知服務實作未提供 |
| 額外 ABI 指令排序 | [排序工具](../../experiments/tsl9-v4160-reply-abi-order/README.md) | 兩段共 28 bytes；編譯器既有指令字，非編譯器單獨輸出 |
| 原始入口角色的可整合性 | [局部連結邊界](integration-plan/README.md) | 兩物件驗證，不是完整 691 區段映像 |

預設封存檢查、指定實際產物重播及新編譯測試是不同證據層級。發布內容
包含來源與選定收據中繼資料，排除生成的物件、ELF 及主機執行檔；要重播
實際產物，須先在自己的專案內新建測試結果。Windows LLVM／主機編譯證據
不代表 Linux、macOS、shell 或 CI 已實際執行。

原硬體及晶片身分、實際 ROM／BOOT、記憶體與中斷、未知服務的暫存器
保存、BLE OTA 接受與復原能力仍未完全證明。**目前不可宣稱可燒錄；
完整目標保持進行中。** [新增功能候選](integration-plan/README.md)與
已實作功能分開記錄。
