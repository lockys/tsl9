# callback 的呼叫邊界與 ROM 條件

[English](readme.en.md)

本輪只讀取原始 ID2966、既有 624-byte C/C++ 元件與本機已保存的兩份官方 ROM 候選，追查 callback 的呼叫邊界。**沒有變更 C/C++ model、重編譯未變更的元件、執行韌體或產生 BIN。** 原有完整 TX 實驗映像維持不變，仍未證明可刷寫。

## 已確認的範圍

| 問題 | 靜態證據與結論 | 限制 |
| --- | --- | --- |
| GP+42 半字是否漏傳？ | 原 `0x8800` 的 LHU A5 只供 `0x8808` SH 使用，`0x880C` 已以目標 LW 覆寫 A5。新元件 `0x120A` LH A0 只供 `0x120E` SH 使用，`0x121A` 已覆寫 A0，再到 `0x1220` JALR。兩者資料均不存活到呼叫。 | 低 16 位寫入相同，不證明中間 fault／非同步中斷前綴相同。 |
| 是否需要新增 A4 引數？ | 此半字原本在 A5，並非 A4；新元件在對應窗口也沒有寫入 A3／A4／A6／A7。沒有發現這裡的 C 漏傳，不能因 LH 而自行加入 `a[4]` 賦值。 | 其他呼叫的引數與不透明殘值仍依各站契約。 |
| 可否把十五個呼叫依地址排序配對？ | 不可。核對依據是目標 slot、引數設定、事件分支與相鄰 memory／call 簽章。 | 新元件配置與原碼不同；數量相同不構成語義對應。 |
| S 暫存器角色是否相同？ | 不同。例如原 `0x86E0` 的 S4 是 context、S7 是 `0x40000`，新元件對應站的實體 S4／S7 是其他 C 區域值。 | 差異本身不證明 ABI 錯誤；需判斷 callee 是否觀察 caller 的這些值。普通「callee 會保存 S」尚不足以回答。 |
| 原返回地址數值是否必須相同？ | 新舊 RA 數值確實不同。對本輪候選 ROM `+0x13C` 的閉合小函式對，RA 只用於正常保存／還原／返回，未見數值檢查；caller S4／S7 不被讀取。 | 僅對已核對的兩份候選與指令 profile 成立，不是已安裝 ROM 的證明，也不能延伸至所有 callee。 |
| `+0xD4` 是否全部閉合？ | 已檢查局部函式及有限的直接小 helper。 | 三個更深的 flash callee 仍是不透明邊界；沒有據此宣稱完整 transitive ABI。 |

詳細來源、實際指令位置及未知項目分別見 [原碼局部證明](source-review/README.md)、[實際原生呼叫對照](native-review/README.md)及[候選 ROM](resident-review/README.md)。舊十五站原始引數契約維持原封存權威，沒有重製另一份工具或引數清單。

原生名義 slot 對應以一般 callee-saved preservation 為條件；另外保留「不透明呼叫可改寫所有暫存器」的 reaching-definition 前沿。十五站名義對應不是完整實體 prefix 等價證明，也沒有將未知返回值或暫存器補成零。

## 兩份候選的證據界線

本機官方 V1.40 的 `[0x4013C] = 0x4B4EE`、`[0x400D4] = 0x4C25C`；V1.31 分別是 `0x4B456`、`0x4C1C4`。`+0x13C` 的 22-byte wrapper 與 36-byte lookup helper 可作有界分析。非標準指令的解釋明確依賴已核對的 LLVM Xwchc profile，不能將未知 opcode 當作 NOP。

候選 header 將這兩個 slot 命名為 `GATTServApp_ReadCharCfg` 與 `GATT_Notification`。前者的實際小函式對在找不到 entry 時回傳 0，否則回傳 `entry+2` 的零延伸 byte（0..255）；**不是已證明僅回傳 0／1 的 Boolean**。所以原 callback 第一次 `==1` 與第二次 `&1` 的區別仍須保留。這支持「通知 CCC 設定 gate／通知送出」的候選解釋，可讓等待原因提案更具體，但不能宣稱實機已確認此命名或已實作診斷功能。

這些檔案並非實體 TSL9 的 ROM dump。沒有因版本字串、相同片段或原 App 的版本前綴檢查，就把候選當作已安裝版本。本輪不複製整份 vendor ROM 到 GitHub；實際候選核對需明示本機 reference root，metadata 檢查不等同讀取候選。

## 如何重跑

```sh
python3 -B analysis/v4160-callback-call-frontiers-2026-10-22/source-review/check-review.py --project-root /absolute/re-tsl9 --firmware /absolute/re-tsl9/firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin --component /absolute/re-tsl9/experiments/tsl9-v4160-callback-registers/build/EXISTING/ordered/c/COMPONENT-ONLY-NOT-FIRMWARE.elf
python3 -B analysis/v4160-callback-call-frontiers-2026-10-22/native-review/review.py --project-root /absolute/re-tsl9 --folder /absolute/re-tsl9/experiments/tsl9-v4160-callback-registers/build/EXISTING/ordered/c --receipt /absolute/re-tsl9/analysis/v4160-callback-call-frontiers-2026-10-22/build/new-c.json
```

實際 fresh-build 目錄通常還包含 `native/` 層；請使用自己正式 receipt 所記錄的 `ordered/c` 或 `ordered/cpp` 絕對路徑。此處讀取既有產物，不呼叫編譯器。新 receipt 只可新建，不能寫回舊產物目錄。候選核對指令與 metadata／actual flags 見 resident-review 說明。

下一步要將尚未透明的 callee 角色、實際 ROM 身分與必要的 RAM／中斷契約逐項收斂。完整 632-byte 範圍所有權、原位配置、BOOT／硬體／BLE OTA 仍未證實；不可填補剩餘 8 bytes 或用候選正常返回證據替代實機驗證。離線 OTA 預檢與等待原因顯示仍是新功能提案，未實作成硬體功能。
