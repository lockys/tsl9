# V1.31 候選 resident 啟動 copy 順序（離線）

在 repo 根目錄執行 `python analysis/resident-copy-order-v131/check.py`。唯讀固定 SHA-256 的原 SDK HEX 和主 segment carrier，核對兩者 byte 對應、完整稀疏 HEX 及既有固定 hash 指令解碼器；測試六處指令變異、兩處輸入 hash 變異及未擷取 READ32 的拒絕。這些負測不修改原檔，也不是 CPU 模擬或實機測試。

## 控制流程與讀取順序

以下為固定 HEX 的靜態指令，RAM 位址的執行須以 seed 複製成功、指令可見且未遭改寫為前提。`0x40000` 跳到 `0x6DE7E`，seed 將 `0x40280..0x402B0` 搬到 `0x20000010..0x20000040`，再於 `0x6DEBA` 呼叫 initializer `0x6DE0C`。initializer 依序：

1. `0x6DE4A/4E` call RAM `0x20000010`，參數 source `0x402B0`、destination `0x20000040`、inclusive last destination `0x20002E70`；正常完成 2957 words，返回 `0x6DE52`。
2. `0x6DE6A/6E` 再 call 相同 helper，source `0x6EAA4`、destination `0x20002E70`、inclusive last `0x20002EF8`；要求 35 words，返回 `0x6DE72`。兩次目的區在 `0x20002E70..0x20002E74` 重疊。
3. `0x6DE72` 重新讀取 stack 上 RA，`0x6DE74` 恢復 SP，`0x6DE76/7A` 不設新 link tail jump 到 RAM `0x20000022` zero helper。zero 自行設定 `0x20002EF8..0x20003618`，包含最後 word `0x20003614`。

copy helper 的來源指令 `0x40280` 是 unsigned `a2 >= a1` 才執行的 inclusive guard；`0x40286` **先讀 source word**，`0x40288/8A` 遞增目的及來源，`0x4028C` 寫目的，`0x40290` 回 guard。第二次第 35 個 READ32 從 `0x6EB2C..0x6EB30` 讀取，目的為 `0x20002EF8..0x20002EFC`；HEX 僅提供前 34 words、到 `0x6EB2C` 為止。若該讀取及後續 store 正常完成，helper 返回後才可能進入 zero，zero 的首個 store 覆蓋同一目的 word。**後來覆蓋不會取消之前讀取。**

## 異常與可達性界線

嚴格擷取資料 provider 在缺口讀取停止；該前綴中沒有第 35 次 store、第二次正常返回、RA reload 或 zero。這只描述 provider 拒絕，不證明 CPU 對該物理位址必然 fault：HEX 缺失不是物理不可讀的證據。若真實存取發生 fault、陷阱、外部轉移或不返回，不能假定仍到 zero；是否經 trap handler 修復／恢復並最終到達，取決於未證實的硬體、handler 和 live context。若全部讀寫成功、正常返回且 RA/SP、RAM code 與控制流未被干擾，才有上述 zero 路徑；zero 返回是否抵達 `0x6DEBE` MRET 也取決於重新讀出的 RA。此處沒有宣稱所有異常路徑不可達或可達。

此 SDK V1.31 參考不能證明原機安裝 resident 相同、實際映射或啟動成功；未補字節、未放寬 gate、未刷機。未改其他工作區內容。
