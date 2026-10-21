# 條件式執行層與 Flash 鏈

本輪使用 ID-2966 / V4.1.60 原始 76,800-byte 檔案，SHA256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`。版本標籤不能證明與實體 TSL9 的硬體相容性。

新增 `src/conditional_runtime_native.c` / `.h`，保存原始 6,318 bytes、2,169 個指令起點、14 個實際程式片段與 559 項 RELA。C11 / C++17 translation unit 承載原始 RV32 組語及指令編碼，並非已還原出原作者的高階 C/C++ 原始碼。新增 31 個標籤都是 GLOBAL NOTYPE、size 0 的儲存位置身分；header 只有 byte-array 宣告，沒有推定的 C 函式簽名。

內容包括 9 個條件入口的 3,992 bytes、21 個必要直接相依入口額外 2,196 bytes，以及新確認的條件 registry 回呼 `13EB4` 的 130 bytes。原入口為 `B0D0`、`11442`、`119C8`、`17476`、`174EE`、`1979A`、`197BE`、`197F0`、`1995C`。來源指標被交給未知 resident 或存入記錄，證明的是條件式執行片段；原 ROM 如何呼叫它們、暫存器與生命週期契約仍未證明。

完整整合實際通過：62,322 bytes code、3,676 bytes RO、614 個非空配置、7,238 項 RELA。原 600 個配置及 6,679 項 relocation 保留；RAM 仍是原 35,160-byte NOBITS、27 個 views，未增加 RAM 或唯讀 carrier。C/C++ 的實際 merged object 與原位數值見證 ELF 一致。新模組的 381 個直接控制 relocation、89 組 HI/own-LOW（含 store 型 LOW）均有原始指令證據；28 個實際負例均被拒絕。

原有 23 個未解決符號全部維持真 UND，包括與新增程式恰巧同址的 canonical；另有 8 個新地址義務 `1A608/1A614/1A61C/1A628/1A62C/1A638/1A668/1A674`，使 strict link 仍拒絕 31 個 UND。未因來源檔中看見位元組就猜出資料長度。其餘 9 個 RO 指標只沿用既有 `1A547..1A606` 的 191-byte OBJECT 地址，17 個 consumer 的完整讀取範圍都沒有閉合。

`1A638` 路徑首次以未遮罩 u8 形成指標，最大可能傳出 `1AC32`；後續名義迭代只有在未知呼叫正常返回並保留預期暫存器時，才得到最大 `1AC56`。這些是超過留存 BIN 範圍的指標值；不代表已證明讀取 6 bytes，也不代表實體硬體越界存取。16 處 GP-relative 存取保持原始編碼，GP 初始化與其 RAM 值仍需原機契約證據。

Flash 補充證據追到 `197BE → 18E98 / 18EC4 / 18EF2 / 18EB6 / 19764`。既有本體保存兩個 key 的 MMIO 寫入、頁面對齊、狀態輪詢，以及步進 4、上限 256 的 64-word 複製迴圈。模式符合已保存的 WCH CH32V20x SDK，支持家族候選；不證明實體晶片型號、寫入成功或它屬於藍牙 OTA 路徑。wrapper 回傳 0 也不能當成硬體成功回報。

可在本目錄執行：

```powershell
python -X utf8 -B verify-data-anchor-extension.py --spec evidence/conditional-runtime-integration.json
```

`re-tsl9` 使用專案內預設原始韌體路徑。分析工作區執行時需以 `--firmware` 指定原始檔絕對路徑。本輪 ROOT 收據為 `build/data-anchor-extension-ecb8f64d6d3640f2b8d2d6f6f6ad776e/verification.json`；獨立整合審查及目的地驗證另記在 `analysis/v4160-conditional-runtime-2026-10-21/`。

`ADDRESS-WITNESS-ONLY.elf` 只驗證原數值位置與位元組，不能用於 OTA。未執行或模擬目標程式，未連線廠商服務，未操作 BLE/UART/CAN 或 Flash。原硬體、ROM / IRQ ABI、啟動狀態、記憶體與 OTA 接受條件仍未通過，因此沒有可燒錄的重建 BIN。
