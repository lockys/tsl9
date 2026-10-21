# 從封包組裝追到實際傳送

[English](readme.en.md)

## 已確認的靜態邊界

`check.py --firmware <官方 BIN 絕對路徑>` 重新讀取官方 ID2966 V4.1.60，直接解析四組 AUIPC／ADDI 位元欄位：`0x86C0`、`0x876C`、`0x8AD6`、`0x8E9C` 均形成 `0x2000B18C`。另核對傳送函式的兩組 `0x4013C` pointer load 與最後的 `0x40050` pointer load。七項 operand 變異在相同的位元欄位檢查中被拒絕；沒有 CPU 狀態模型、ISA 模擬或網路操作。

在這份現有物件中，前三組相關 owner 為 `callback_8614`、`code_continuation_8a56`、`init_8e88`；`callback_8614` 有兩組上述引用。原本的 `0x8614..0x888C` 共 632 bytes 是後續追查候選：必須逐條確認其讀寫、事件與 ROM 呼叫，不能因為共用緩衝區地址就先宣稱它已完成藍牙傳送。四組選定引用也不是任意計算地址或整個映像的完整引用清單。

## 候選解釋，尚非原機 ROM 證明

本機先前保存的 WCH V1.30 與 V1.40 headers 都將 function table base 寫為 `0x40034`，JT7 為 `tmos_set_event`，JT66 為 `GATTServApp_ReadCharCfg`。對照本函式的數值 slot，**可能**是在通知設定通過後填入緩衝區，再提交 task event。`sdk-candidates.json` 保存精確的本機 header 雜湊、行號及候選型別；本輪未重新下載文件。

這不能證明原機安裝了任一版本，也不能用候選的兩參數函式型別消除原碼實際的 A2／A3 殘值。pointer word、callee bytes、返回型別、寄存器及 SP／GP 保存仍未確認。函式完成封包組裝或交接，不代表封包已被實際發送、收到或接受。

## 新功能候選

1. **離線封包預檢與預覽**：顯示命令、負載長度、標頭及校驗值，拒絕超過 1039 bytes 的原入口負載。此提案不需要 BLE 連線；主機測試資料仍不證明原 ROM 行為。
2. **更新等待原因顯示**：在 App 中區分通知未開啟、緩衝區等待和更新回覆等待。必須先確定原狀態與回覆語義，不能把本函式依路徑而異的 A0 一律改成成功／失敗碼。

以上是提案，不列入已完成的原硬體功能。後續重建仍需涵蓋事件消費者、GATT ingress、完整 OTA handler，以及原板／ROM／BOOT／記憶體／中斷與 OTA 接受和復原證據；目前沒有新增可燒錄性聲明。
