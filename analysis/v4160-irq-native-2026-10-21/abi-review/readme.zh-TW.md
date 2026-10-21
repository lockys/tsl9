# 原生 IRQ 一般返回邊界獨立審查

實際 C、C++ ELF 都包含四個 30-byte helper 與 180-byte 初始化器。四個 helper 的 **120 bytes 完整符合原始 runtime** `0x19124`、`0x19142`、`0x19160`、`0x1917E`：相對分支、兩條 RET、讀寫 offset 與暫存器均相同。原始 SHA 為 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`。

每種語言的 300 executable bytes 均由五個 symbol 無缺口／重疊覆蓋，共 113 條解碼指令；沒有額外 outlined function、UND、relocation 或可寫 allocation。實際 profile 為 `-Oz`、RV32IMAC_Zicsr、ILP32，停用 machine outliner，僅 A0/A1/A4/A5 可配置。本審查重用輸出檔，沒有重複編譯或執行目標指令。

| 邊界 | 靜態確認契約 |
|---|---|
| helper 啟用 | A0=before OR mask；完整保留 A1；A4=`0x40021000`；A5=此次 before |
| helper 停用 | A0=before AND NOT mask；A1=0；A4=此次 before；A5=`0x40021000` |
| helper 保留 | 實際目的暫存器只有 A0/A4/A5；A1、A2/A3/SP/RA 及其他 GPR 未寫入 |
| main 一般返回 | A0=最後新讀取 READ32(`0x4002100C`) AND `0xFFFFEFE2`；A1=0；A4=128；A5=`0xE000E000` |
| main 保留 | 實際只寫 A0/A1/A4/A5；未寫 A2/A3/SP/RA 或其他 GPR；沒有 call／frame |

限定 main transcript 的二十個有序效果為：CSR800 clear88、六次新讀取 32-bit RMW、六次後續寫入（三個 byte／三個 word）、CSR800 set88。`verification.json` 列出每個原生位址、raw instruction、記憶體位址、寬度與運算。候選 mapping 中最後 A0 讀取為 `0x10E2`、NOT `0x10E4`、AND `0x10E8`、寫回 `0x10EA`，之後不再寫 A0。`0x1120` 設 A4=128，`0x1124` 設 A5 基底，`0x1128` 設 A1=0，`0x112A` RET；均綁定實際 bytes。

既有 callback 證據顯示 query 的 A3 通過原始 IRQ／fields／`0x9F4C`，直到 `0x131E0` 第一個未知 callback 前未覆寫。callback 是否使用尚未知。新 main 沒有 A3 寫入，符合這項一般返回保留要求；不代表已知 callback 介面或行為。

## 限制與配置不通過

這不是原始 IRQ 逐點等價。main 在候選 `0x10EE` 暫將 A1 當 `0xE000E000` 位址 scratch；原始 main 具有 stack frame、helper calls 與保存值重載，新版則是 leaf。CSR 時序、暫態暫存器、stack 存取、指令位址、中斷投遞及非同步記憶體變化均未證明等價。helper bytes 相同也不代表已證明硬體／板級行為或任意搬移相容。

原始 main `0x9A42..0x9AD2` 僅 144 bytes，新版 180 bytes，**超出 36 bytes**。四個 helper 各占完整 30 bytes，沒有空間差額。本審查未做原址連結、選 donor 或產生 BIN；配置、boot ROM、OTA 與可燒錄皆未通過。compiler-review 可能另有數字配置 witness；映像外診斷位址不等於可用儲存空間。

十一個實際記憶體 transcript 變異皆被拒絕：helper 改 byte、A2／SP 寫入、錯誤返回暫存器、末端 A1 非零、錯誤 A4／A5、錯 CSR mask、最後新讀取 offset 錯誤、A0 末端被覆寫、尾端寫入寬度錯誤。它們是 **靜態 transcript controls**，不是編譯後 source mutants、ISA 執行或一般化等價證明。checker 僅接受這份限定 main transcript，遇到不熟悉編碼即失敗，沒有模擬執行。

`verification.json` 保存完整函式 bytes／rows、symbol 位址、profile、source／ELF／IR／log 雜湊。重新驗證需有被綁定的本機輸入；保存 ledger 本身可獨立閱讀。未修改 parent／model／舊封存範圍，沒有網路、硬體、目標執行或新韌體 BIN。
