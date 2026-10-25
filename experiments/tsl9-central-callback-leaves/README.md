> 此頁保留先前實驗快照。最新正式來源與原位址證明見[整合結果](../../analysis/central-callback-integration-2026-10-26/README.md)。

# 三個中央角色候選回呼：C/C++ 實驗

從官方 ID2966 V4.1.60 BIN 重建三個完整原始函式：`0x10C36..0x10C7A`、`0x10D2E..0x10D30`、`0x10D30..0x10D60`，合計 **118 bytes／41 條指令**。C 與 C++ 各產生 11 個實際 FUNC，五筆具型別分支重定位；按原位址解析後全部指令與原 BIN 相同，兩種語言產生相同物件。使用兩套 ELF 讀取器交叉檢查。

- 已確認：第一個函式比對三筆 RAM 記錄的 16-bit 欄位，符合時寫入該筆的第一個 byte；第二個原始函式只有 RET；第三個呼叫 ROM 槽 `0x40038`，將結果取模 1,000,000，再經 `0x40170` 尾呼叫。
- SDK 候選對應：`gapCentralRoleCB_t.rssiCB`、`gapBondCBs_t.pairStateCB`、`gapBondCBs_t.passcodeCB`；SDK 的 `tmos_rand`／`GAPBondMgr_PasscodeRsp` 型別亦相符。這些是候選語義，**尚未證明實機安裝的 ROM ABI**。
- `0x11544..0x119C8` 另有 1,156 bytes／374 條指令。已核對事件值 0..16 的守衛、68-byte 相對跳轉表與七個內部目標；20 個直接呼叫中，四個目標 `0x10CE0`、`0x110F8`、`0x11266`、`0x114E2` 尚無正式 CODE owner。

本輪為實驗元件，尚未加入 `src/` 的正式來源證明與原位址整合，**正式覆蓋率維持 89.03%**。沒有新增 BIN、執行目標程式或存取硬體；不代表功能完成、原廠原始碼還原或可燒錄。

## 本機驗證

在專案根目錄執行 `python experiments/tsl9-central-callback-leaves/audit-v1.py` 及 `python experiments/tsl9-central-callback-leaves/build-v1.py`。需既有韌體、正式 layout-map 與相同雜湊的 NDK LLVM；腳本只做正向靜態檢查與交叉編譯。

下一步：重建事件回呼與四個輔助函式，為跳轉表建立有型別的 DATA／CODE 關係，再整合這三個已驗證函式。可研究的新增功能是 RSSI 連線診斷與事件追蹤；尚未實作。

[English](readme.en.md) · [實驗來源](src/central_callback_leaves.v1.c) · [驗證摘要](summary.json)
