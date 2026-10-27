# 原 APP 的 task 註冊與事件派發

[English](readme.en.md) · [前輪初始化資料](../tsl9-resident-initial-data-prefix/README.md) · [前輪 callback 清單](../tsl9-original-clock-random-idle-binding/README.md)

本輪核對 **5 個完整 APP 函式／896 bytes** 與 **7 個完整 SDK 函式／1,536 bytes**，共 **2,432 bytes／827 指令**。串起原 APP 的 `0x1995C` handler、候選註冊 API `0x43C4E` 與主排程器的間接呼叫 `0x2000090A`。[完整收據](verification-v1.json) · [累計清單](ledger-v1.json)

## 註冊與表格來源

原 main 在 `0x8EA8` 呼叫 BLE 初始化，再於 `0x8EAC` 呼叫 `0x19B16`。原 `0x19B26` 產生 callback 位址 `0x1995C`，在 `0x19B2E` 經候選槽 `0x40080 → 0x43C4E` 註冊。

若候選內部初始化在 `0x43C06` 看到 count=0、有效配置正常完成、沒有中途註冊或覆寫，前四個 handler 為：

| Task ID | 表格值 | 來源 |
| ---: | --- | --- |
| 0 | `0x432A4` | 候選初始化 |
| 1、2 | `0x43326` | 候選初始化 |
| 3 | `0x1995C` | 原 APP 後續註冊 |

handler 表格指標槽為 `0x200031C4`，stride4；pending-event 表格槽為 `0x200031E4`，stride2。容量表達式 `n=3*((x>>2)+(x&3))+14` 對 unsigned byte x 得 n14..212。在穩定 n／p 與有效配置前提下，前四個 handler 的 16 bytes、event 的 8 bytes 都落在各自 suffix 範圍內；**未證明實際配置容量、所有權或所有後續寫入安全**。

註冊 API 在 capacity≤count 時回傳 255，不寫 handler；原 APP 仍會保存結果至 **live GP+388**，未檢查拒絕值就繼續排程。因此 task3 是上述條件下的結果，不是實機觀察或無條件保證。

主排程器以 `table+4*taskID` 載入 handler，傳入 taskID 與清除前的 16-bit event。返回後重新讀取 live task index、clear mask、pending events，寫回 `low16((returned & ~fresh_mask) | fresh_pending)`。不能假設 callback 若改變 index，回傳一定套用到原 task。

## 原 handler 的優先順序

每次只走一個優先分支；下表是原始指令語義，不是執行測試：

| 優先 | Event bit | 原行為 | 正常回傳 |
| ---: | --- | --- | --- |
| 1 | `0x8000` | 接收訊息；非 null 時釋放 | `events XOR 0x8000` |
| 2 | `0x0001` | 確認該 bit | `events XOR 1` |
| 3 | `0x2000` | 候選 `0x641B0`、校準 callback `0x197B8`、重新排同 bit | `events XOR 0x2000` |
| 4 | `0x4000` | 重新排同 bit | `events XOR 0x4000` |
| 其餘 | 未匹配 | 正常返回 | 0 |

初次排程與 bit13 的 delay 參數均為 `0x2EE00`；bit14 為 1600。**只確認 raw 值，未確認實體時間單位、校準效果或重排程成功**。原 handler 不檢查 schedule 結果。初次排程的 `0x19B54` 是釋放 frame 後的 `jr t1` 尾呼叫，沒有新增 link RA。

另外核對 7 個原 APP 間接 API 呼叫／尾呼叫點，其候選目標 `0x43C4E`、`0x2000028C`、`0x431BA`、`0x641B0`、`0x43728` 都已有真實 native 本體；不把這 7 點混入 SDK 的 51 點分母。SDK 累計現在為 **36／51 點**，仍有 15 點未串接，不代表缺失函式數。

## C/C++ 與限制

沿用 [原 APP C/C++](../../src/native/startup/resident_startup.c)，以兩個 ELF 讀取器核對原位址 native 診斷物件，並檢查候選 SDK 的實際 CODE 所有權。新增的 [ABI 斷言](task_handler_abi.c) 經 RV32 C11／C++17 編譯，確認官方候選 header 的 `uint16_t (*)(uint8_t, uint16_t)` 宣告；物件無 allocated CODE／DATA、函式或 provider。**這不是對 installed private ABI 的證明，也沒有新增可執行 adapter。**

要求相同 ROM profile、原 GP／stack／ABI、有效不重疊記憶體、正常返回、穩定表格且沒有 IRQ／重入覆寫。全域初始化必早於所有 dispatch、實體 ROM／RAM／ISA／IRQ／Flash／OTA 相容性、校準效果與既有 4-byte 啟動來源缺口仍未解決。候選維持 **35,324 CODE＋392 DATA bytes**；APP 靜態覆蓋率仍為 **95.54%**，**尚不可宣稱可燒錄**。

可考慮加入離線 task 註冊拒絕、事件優先順序及重排程狀態診斷；未實作 UI 或硬體控制。

首次建立 ABI 斷言，再執行完整離線驗證（需收據固定的參考檔與既有物件）：

```sh
python experiments/tsl9-original-APP-task-binding/build-v1.py --tool-dir "$LLVM_BIN" --build
python experiments/tsl9-original-APP-task-binding/verify-v1.py --tool-dir "$LLVM_BIN" --write-receipts
```

已有產物時省略 `--build` 與 `--write-receipts`，執行唯讀核對。
