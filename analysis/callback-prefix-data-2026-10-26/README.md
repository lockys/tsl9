# 回呼路徑固定長度資料（實驗）

[English](readme.en.md)

新增 [C/C++ 唯讀資料](../../experiments/tsl9-callback-prefix-data/src/callback_prefix_data.v1.c)：**14 個實際配置，共 109 bytes**。範圍來自原始 A0 指標及 A2 長度參數，沒有補 NUL 或依相鄰位址猜陣列大小。

- 104 條新擷取指令／16 個視窗均與原廠 BIN 相同；全部已選取 CODE 為 64,544 bytes／21,938 指令。
- C11 與 C++17 的 DATA 及實驗性 ET_REL 元件相同，兩套 ELF 讀取器一致。
- 既有 CODE／DATA、六個真實 DATA 標籤與 4,861 筆重定位完整保留；實驗元件未解參照 **22→8**。
- 尚未納入正式 `src/`、完整來源證明或原位址配置。正式狀態仍為 **88.89%／22 個未解參照**。

## 契約與限制

名義槽位 `0x4003C` 對應封存 SDK 的 `tmos_memcmp` 候選：SDK 宣告 BOOL，註解表示 TRUE 為相同。實作保留原始呼叫與分支，沒有代換標準 C `memcmp` 語義。原機 ROM／ABI 與實際讀取契約仍未證明。14 個視窗中有一個在指定長度之後仍不是 NUL，因此本輪只提供精確的固定長度資料。

## 新發現的回呼缺口

`0x1236A..0x12384` 的原始呼叫使用槽位 `0x401B0`，與封存 SDK 的 CentralStartDevice 候選公式吻合。其兩個資料參數位於 `0x1A668`／`0x1A674`，符合 RV32 三指標、12-byte 回呼結構的候選布局；原機 SDK 布局尚未確認。

五個非零指標中，`0x10C34` 已有 CODE 支撐，**`0x10C36`／`0x10D2E`／`0x10D30`／`0x11544` 尚未被目前選取的 CODE 覆蓋**。本輪沒有提供這兩張表或假函式。這四個間接目標也不在目前的編譯器未解參照計數中，因此「8 個未解參照」不代表只剩八個執行期缺口。

沒有產生 BIN、執行韌體／HOST 模型／ISA、操作硬體或呼叫後端。實機與 OTA 相容性仍未證明。

[摘要](summary.json) · [原始證據](evidence.json) · [編譯證據](native-proof.json) · [參照契約](provider-contracts.json) · [下一步](next-providers.json) · [功能提案](feature-candidates.json)
