# 原 APP 的 SNV／Flash callback

[English](readme.en.md) · [前輪 callback 清單](../tsl9-resident-callback-binding-ledger/README.md) · [候選 SNV C/C++](../tsl9-resident-snv-initialization/README.md)

本輪核對原 APP 的 8 個完整函式（632 bytes）與候選 SDK 的 4 個完整函式（718 bytes），共 **1,350 bytes／492 指令**，串接兩個額外間接呼叫點。[驗證收據](verification-v1.json) 保留完整範圍、CFG、條件與既有 native 物件證據；沒有新增目標程式碼或 BIN。

| 項目 | 原始靜態證據與條件式結果 |
| --- | --- |
| 設定來源 | `0x199E2` 的 64-byte BLE 設定，於 `0x19AEC` 傳入候選 SDK |
| SNV 設定 | 起址 `0x08077C00`；原 block=0，由 SDK 設為 256；SNVNum=3 |
| 讀取 callback | `0x19A7E` 寫入 `0x1979A`；SDK `0x44056` 經槽 `0x20003224` 呼叫 |
| 寫入 callback | `0x19A88` 寫入 `0x197BE`；SDK `0x440BE` 經槽 `0x20003228` 呼叫 |
| 初始化入口 | BLE `0x43C7E` → `0x43B3E` → SNV `0x44022`，受原分支與正常返回條件限制 |

若第一頁 marker 不符、取得有效 256-byte buffer，且原迴圈正常完成，三個寫入參數位址為 `0x08077C00`、`0x08077D00`、`0x08077E00`。邏輯窗口為 `[0x08077C00, 0x08077F00)`；**不是已確認的實體 Flash 容量、分區或 MCU 型號**。

### 與 APP 設定頁的數值區間對照

既有 [APP 六筆設定記錄](../tsl9-NVM-record-layout/README.md)的 writer 以 256-byte 數值粒度使用 `[0x08077500,0x08077B00)`；上述條件式 SNV 三頁位於 `[0x08077C00,0x08077F00)`。兩個窗口不重疊，中間是 `[0x08077B00,0x08077C00)` 的 256-byte 數值間隔。此間隔**用途未知**，不能據此視為空白或可用。

將兩組目的地址依 256 bytes 分段，六個設定頁與三個條件式 SNV 頁數值上互不相同，但九頁都在同一個 4 KB 對齊區間 `[0x08077000,0x08078000)`。本機 WCH 候選驅動區分 256-byte 快速頁擦除與 4 KB 一般頁擦除，原 APP 擦除指令與前者的對齊和控制位相符，見[擦除交叉對照](../tsl9-NVM-record-layout/README.md)。因此若錯將涉及此區的操作換成 4 KB 擦除，數值涵蓋範圍將包含兩組頁；這是有條件的區間與候選介面比較，不證明實機實際擦除、實體映射或損毀，也不代表其餘七個 256-byte 區間可用。既有區間檢查器已加入九頁共區驗算。

如果兩組高位數值都映射為以 `0x08000000` 起算的同一連續區域，涵蓋至 SNV 窗口結尾需要偏移 `0x77F00`（491,264 bytes）；這是該假設下的算術需求，不是已確認的晶片容量、物理位址或可寫分區。兩組路徑的 slot、記憶體、初始化及執行條件仍各自適用，SNV 頁也可能因 marker 相符而不寫入。未讀取裝置或推定任何頁面內容。[離線檢查器](check-snv-settings-ranges.py)固定兩份既有收據並交叉驗算區間。

讀取 callback 把 num=1 轉為 copy 長度 4 bytes，透過候選槽 `0x4004C` 呼叫 `0x20000332`，輸出至 SDK 自身 SP+12。此 copy 還會存取 `0x4002420C` 並執行 FENCE.I；不是只靠一般 RAM memcpy 就能保證相同硬體效果。callback 正常返回 A0=0，不會驗證 copy 是否成功。

寫入前 buffer 填 `0xFF`，每輪將第一個 word 改成該頁邏輯位址。SDK 傳 num=64 words；原 `0x197BE` 忽略此參數，保存來源指標後依序呼叫 unlock、erase、program、lock、delay。原 program 固定讀寫 64 words＝256 bytes，erase／program 都將目的位址向下對齊 256。沒有證明實際配置容量、Flash 成功或 polling 必定結束；delay 還依賴 live GP+382 與 MMIO。

**返回值不能作為持久化成功證明：**

- 只比較第一頁第一個 word；marker 相同就略過寫入，沒有逐頁驗證三頁內容。
- 讀寫 callback 正常返回都設 A0=0，未檢查硬體操作結果。
- SNV 的 marker 相同或配置失敗路徑均可返回 1；外層 BLE 在 `0x43D4E`／`0x43D56` 仍將結果覆蓋為 0。

### 配置失敗與 APP gate 的條件式串接

若第一頁 marker 不相符而候選 `0x44022` 的 256-byte heap 配置回傳空指標，`0x4407C` 轉至返回 1 的路徑；它沒有走該次三頁寫入迴圈。若之後中間 task initializer 正常返回，候選 BLE initializer 在 `0x43D4E` 設 0，並由 `0x43D56` 將該值返回。原 APP `0x19AEE` 對這個返回值只檢查是否為零：零則繼續 `0x19AF2` 之後的初始化，非零才進入自迴圈。

因此，在 installed ROM 符合候選、上述控制流實際走到且記憶體／呼叫正常的條件下，**SNV 配置失敗與該外層零返回可以同時成立**；APP 這個 gate 不能單獨證明 SNV 已初始化或持久化。這不證明實機曾發生配置失敗、排除其他錯誤訊號，或保證後續初始化成功。[靜態檢查器](check-snv-failure-ble-gate.py)固定相關 APP／候選指令及既有收據，未執行目標或讀取排除區。

累計條件式串接為 **21／51 點**（16 個目標、5 個零值略過）；其餘 30 點未納入累計清單，不代表缺失函式。前輪 19 點的假設全部保留。所有結論仍依賴相同 ROM profile、有效不重疊記憶體、穩定設定、原 private ABI、正常返回及無 IRQ／重入覆寫；不是 live 綁定證據。

現有 C/C++ 本體：原 APP [callback](../../src/native/startup/resident_startup.c)、[Flash helpers](../../src/native/receive/ota_runtime.c)、[delay](../../src/native/startup/peripheral_primitives.c)。重新透過兩個 ELF 讀取器核對原位址 native 診斷物件，並驗證現有候選 SDK 所有權。沿用既有 ABI 收據，沒有新增編譯。靜態 APP 覆蓋率維持 **95.54%**；ROM／RAM／ISA／IRQ／Flash／OTA 相容性與既有 4-byte 啟動來源缺口仍未解決，**尚不可宣稱可燒錄**。

可考慮新增「離線 NVM dump 的逐頁 marker／內容一致性診斷」；目前未實作，也未讀取硬體或推定現有頁面內容。

在專案根目錄離線重跑：

```sh
python experiments/tsl9-original-SNV-Flash-binding/verify-v1.py --tool-dir "$LLVM_BIN"
```
