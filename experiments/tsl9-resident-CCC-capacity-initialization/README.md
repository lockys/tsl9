# CCC 容量初始化與 APP 呼叫順序

[English](readme.en.md) · [專案](../../README.md) · [C/C++ 本體](resident_CCC_capacity_initialization.c)

新增 **4 個完整 SDK 候選本體，598 CODE bytes／198 指令**。C11／C++17 原生物件與原指令及 36 筆重定位相符；2 個普通匯入由既有 allocator／memset 本體解析。仍有未選取的 callback `0x4D916`，不能把無具名 UND 解讀成完整執行環境。

|證據位置|已確認的靜態行為|
|---|---|
|APP `0x19A70`|SH 寫入 `0x0E3F` 至 SP+36；config 起點 SP+16、ConnectNumber offset21，因此名義值為 `0x0E`|
|SDK `0x43CE8`|複製 64B config 至 `0x200031EC`，offset21 對應 `0x20003201`|
|SDK `0x4EDD2..0x4EE72`|讀取此 byte；`c&3` 寫至 CCC 容量 `0x200033B5`，`(c&3)+(c>>2)` 寫至 total `0x200033B4`|
|APP `0x8EB6` → PeripheralInit `0x6DD2A` → `0x4DACE`|正常呼叫路徑先執行容量初始化，再到 APP `0x8FB6` 清除 CCC 記錄|
|CentralInit `0x6DDB0`|有條件呼叫共同初始化器；保留跳過分支，未宣稱所有角色路徑都會初始化|
|SDK `0x4EFE2..0x4F00C`|12-slot callback table 找首個空位；滿表回19。此 status 不代表一般 OTA 錯誤|

**條件式推論：**若 APP 的 `0x0E` 從寫入、複製至 helper 讀取皆未被改寫，CCC 為 **2 筆×4B＝8B**（`0x20004080..0x20004088`），total 為5，候選配置量為300B。已證明正常 CFG 的局部呼叫順序；未證明 live 值、全域唯一寫入者或實體 RAM 所有權。

容量寫入先於記憶體配置，helper **未檢查 allocator 是否回 NULL**。配置後重新讀取 total 的行為保留；total=0 跳過配置及48B callback table 清除。容量寫入成功不等於表格或 callback 已就緒。尚須正常 ABI、既有呼叫返回、設定保持及無 alias／IRQ／DMA／重入改寫等條件。

完整參考另核對 APP main 384B、config initializer 308B、既有 BLE_LibInit 228B，以及兩個 role wrapper 246B／66指令。role wrapper 是完整原始 CFG 參考，**本輪未把它們新增為 native provider**。

C/C++ 部分連結結果一致：**42,282 CODE＋412 DATA bytes／14,592 指令**、2,950正大小FUNC、2,353重定位、0具名UND；父輸入的 bytes、globals、typed roles 全部保留。修正一個沿用的「未提供 callback」旗標後，以 `native-v2` 保存新收據；舊 `native-v1` 留在本機。

APP 正式來源仍 **162 份、73,478／76,800B（95.67% 靜態 byte 覆蓋）**，不等於功能完成度。SDK 未連入 APP、未做最終原位址配置；既有4B啟動來源缺口保留。**沒有新 BIN，也未證明實體 ROM／RAM／IRQ／Flash／OTA 相容性**。未執行 target、HOST model、ISA 或硬體，未呼叫廠商 API。

[`verification-v1.json`](verification-v1.json) · [`summary.json`](summary.json) · [尚未實作的離線診斷候選](feature-candidates.json)

已有固定本機輸入與 LLVM 時，可唯讀重播：

```sh
python3 experiments/tsl9-resident-CCC-capacity-initialization/verify-v1.py --tool-dir "$LLVM_BIN"
```
