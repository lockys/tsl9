# 配置與一般返回邊界 ABI 審查

舊原生 IRQ 初始化器 118 bytes 與四個 22-byte helper **不符合原始暫存器契約**。先前的記憶體／CSR 效果驗證，不能證明原始 ABI。此審查獨立解碼 C、C++ 實際連結 ELF，沒有執行 RV32。

| 函式 | 原始一般返回狀態 | 舊原生一般返回狀態 |
|---|---|---|
| `0x9A42` | 保留 A2/A3；A1=0；A4=128；A5=`0xE000E000` | A2=`0xE000E000`；A3=128；A1=136；A4=`0x101D`；A5 未改 |
| helper，啟用 | A4=`0x40021000`；A5=此次新讀取舊值；保留 A1 完整位元及 A2/A3 | A2=`0x40021000`；A3=此次舊值；A4/A5 未改 |
| helper，停用 | A4=此次舊值；A5=`0x40021000`；保留 A1 完整位元及 A2/A3 | 與啟用分支相同的原生殘留值 |

兩者 A0 都來自最後一次即時讀取後的 RMW，但不能抵銷其他差異。原生 main 寫 x10..x14，helpers 寫 x10/x12/x13；原始 helper 寫 x10/x14/x15。原始 main 會使用並重新載入 16-byte stack frame，原生 leaf 不會。因此一般返回邊界推理仍假設已儲存的 stack word 未遭外部改變；不宣稱非同步觀察等價。

既有 caller 證據顯示 clock query 產生的 A3，通過原始 IRQ、fields 與 `0x9F4C` 後，直到 `0x131E0` 的未知 callback 前都未覆寫。callback 是否使用它尚未知，不能假定可捨棄；這不是宣稱它必然是第四個 C 參數。

原始 IRQ 範圍是 `0x9A42..0x9AD2`，共 **144 bytes**，不是 176。與 118 的名義差為 26，不是 58。上述 ABI 不符，使這 26 bytes 不能當成已證明可用的空間；四個原始 helper 各 30 bytes，其名義 8-byte 差額同理。

## 配置與跳轉

八個限定範圍合計 540 bytes：reset memory 62、query 174、fields 40、IRQ 144、四個 helper 各 30。它們不連續；最大 174，無法直接放入目前 196-byte query。38-byte fields 放得進 40 也僅證明大小。實際完整配置檔 `original-image-layout.ld` 為 126450 bytes，具有 691 個明確位址及 691 個精確大小 assertion。小型 ROM script 僅是數字位址 witness。62-byte reset memory 是 138-byte reset section 的內部片段，不能丟掉前綴和 CSR／clock 後綴。

可呼叫入口可考慮明確四-byte **JAL x0**，保持既有 RA 及全部 GPR；`jal ra` 會覆寫呼叫者 RA。八個起點的 56 組有向配對均通過編碼與位移回解，只證明跳轉距離。它不證明入口可覆寫或目的地有空間；C.J 範圍也較小。helper 開頭是二-byte branch，接四-byte 指令；四-byte thunk 會只蓋到後一指令的一半，仍需處理完整六-byte 前綴、padding 和內部入口參照。

`0x186BA` 原本是順序落入，不是函式 call。直接導向 78-byte RET leaf 會造成錯誤續行。既有 80-byte fragment 最後以四-byte JAL x0 relocation 回 `0x186F8`；必須保留入場 RA、原始 CSR 順序、`0x18720 -> 0x1874A`／返回 `0x18724`、MEPC=`0x9008`，及跳至 ROM `0x40000`。數字 continuation witness 不等於完成整合，ROM 行為仍未確認。

query 目前在 offset 166 RET，offset 168 起有 28-byte cold tail。分割必須修正進入 tail 的 branch 與兩個短距離返回跳轉，不能直接裁切複製。此處沒有證明有效分割方案、可用 donor 或整合配置；不能弱化原始 section assertion，也不能假設空白或暫存器已不再使用。

incoming references 由 source-review 獨立負責；直接參照與 relocation 掃描不能排除計算式間接入口。本審查未宣稱完整 ABI、非同步 IRQ、硬體板、boot ROM、OTA 或可燒錄，沒有產生韌體 BIN。新 IRQ 暫存器版必須另行測試、解碼及量測，才可重新計算配置預算。

`verification.json` 綁定原始 `0ee64183...`、既有 source／caller 證據、完整配置與舊 C/C++ ELF／IR／disassembly／receipt。`audit.py` 核對 264 原始 bytes、十個原生函式的目的暫存器、八段範圍、691 assertion、56 跳轉編碼。沒有執行原始／重建 RV32 或硬體測試。
