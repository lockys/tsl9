# 放置空間與來源參照審查

本輪離線核對 ID2966 V4.1.60 原始位元組及既有 source-image carrier，不產生新 BIN，也不執行或模擬韌體。76800 位元組原始映像 SHA-256 是 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`。

## 精確範圍

| 用途 | 原始半開區間 | 位元組 |
|---|---|---:|
| 重設記憶體區段 | 0x186BA..0x186F8 | 62 |
| 時脈查詢 | 0x18834..0x188E2 | 174 |
| 衍生欄位 | 0x1973C..0x19764 | 40 |
| 中斷初始化 | 0x9A42..0x9AD2 | 144 |
| RCC helper | 0x19124..0x19142 | 30 |
| RCC helper | 0x19142..0x19160 | 30 |
| RCC helper | 0x19160..0x1917E | 30 |
| RCC helper | 0x1917E..0x1919C | 30 |

八個不重疊範圍合計 540 位元組。原始 IRQ 初始化是 **144**，不是 176；四個原始 helper 各 **30**，不是 22。錯誤拆分剛好抵銷了總數，卻把 32 位元組算在錯誤位置，不能拿合計大小當成放置證明。

記憶體區段只是 138 位元組 `.text.tsl9v4160.reset` 的一部分，從 0x186B6 設定 SP 後落入 0x186BA；0x186EA 可跳往 0x186F8，0x186F4 後也落入此延續，沒有 RET。不得直接刪除完整 reset owner；前綴、後續 CSR／時脈／ROM 序列仍需正確保留。

## 完整配置證據

`source-image-merged.o` 的 SHA-256 是 `646dbe43772be3858223dd6ec7f022c0252deba5879f3d3ab98da2940c9edb97`，有 691 個 allocated section、8280 筆 RELA；位址見證 ELF 的 SHA-256 是 `66fbf4cf1d9731f5fcd4f71c66ec1c67fc4fd2487f710125ed6488cbde2e8420`。檢查確認其中 690 個檔案 section 無缺口、無重疊地完整重現原始 76800 位元組；另有 0x20004000 起的 35160 位元組 RAM NOBITS，不能當成映像空間。

真正完整的 script 位於 `experiments/tsl9-v4160-startup/build/image-fidelity-999d8125159a4d80bd6df9153f267002/original-image-layout.ld`，126450 位元組，SHA-256 是 `651a8f14d09e373cb5523ec12f97d1fcce3ff26a51b3d835ae55d0239945507b`，含 691 個明確位址與 691 個 SIZEOF 斷言。`verify-image-fidelity.py` 第 139–141 行產生此檔；第 153 行以 `ld.lld --no-relax -T <full-layout> -T <numeric-ROM-script> <object> -o <witness>` 連結。本輪逐一核對實際 section 位址與大小。小型 `ADDRESS-WITNESS-ONLY.ld` 只指定 ROM=0x40000，不是完整 map，也沒有提供 ROM 實作；真正未定義符號仍是 `__tsl9v4160_rom_entry`。

這些 ELF section／符號屬於重建證據，不是原韌體 debug symbol。原位址對應由整份映像位元組相等支持，不代表實體執行或硬體相容。

## 已知靜態參照

已檢查全部 8280 筆 RELA 與 carrier executable section 中的 24585 個指令邊界。八個範圍收到 33 筆 RELA 參照及 34 個已納入的直接控制參照，其中 16 個跨範圍：

| 目標 | 來源 PC |
|---|---|
| 0x18834 | 0x9254 |
| 0x9A42 | 0x9258 |
| 0x1973C | 0x925C |
| 0x19124 | 0x9A6A、0x1986E |
| 0x19142 | 0x9A5E、0x19B68 |
| 0x19160 | 0x9A88、0x9A92、0x188F8、**0x18906**、0x1891C |
| 0x1917E | 0x99F2、0x99FC、0x9A74、0x9A7E |

0x18906 是 rd=x0 的 JAL 尾端轉移，不形成新 RA。每個 helper 都有 0x9A42 以外的呼叫端，因此將主函式的六次呼叫 inline，並不會讓 helper 入口變成可刪除空間。

其餘已納入直接參照是內部分支／跳躍，包含 reset 迴圈、query 區塊及各 helper 的入口+14 清除分支。另有兩筆 reset PC-relative low anchor RELA，不是 runtime 呼叫。29 個有名符號包含七個函式定義、局部標籤與 assembler mapping marker，不能全當成獨立函式入口；完整紀錄在 `reference-inventory.json`。

在已納入的指令邊界，未發現範圍外直接跳往內部的轉移；相鄰 LUI／AUIPC 加支援的低位指令，未形成指向這些範圍的位址。對所有 byte offset 掃描四位元組數值，含清除 JALR 最低位元，也沒有找到指向這些範圍的視窗。這些是有範圍的陰性觀察，**不能證明沒有計算型參照**。

另對原始映像每個 halfword 掃描，得到 39 個有效直接編碼候選：34 個已納入紀錄，加上五個從已知 32 位元指令後半段開始的候選，後五者不是已確認呼叫。也保留了 939 個已知間接轉移來源位址，其中 552 個是標準 RET 編碼，並保留完整紀錄的雜湊。多步運算、載入／callback 目標、外部 resident／ROM 及額外內部入口仍未知；靜態清單不能排除它們或證明可達性。

## 放置限制

有範圍的檢查拒絕 78 位元組 reset leaf 放入 62 位元組區段、80 位元組 fragment 放入同處、196 位元組 query 放入 174 位元組區段，以及錯誤的 IRQ 176 位元組原始範圍。另由相同的完整清單綁定 gate 拒絕八個紀錄修改，包含刪除其他／尾端呼叫及捏造 padding／計算目標不存在。這是四個 ownership 與八個 transcript 控制，**不是已編譯原生測試**。

38 位元組 fields 或舊 118 位元組 IRQ 雖在數值容量內，不代表符合原始暫存器、延續與參照要求。其他 ABI 審查已指出舊一般 C IRQ／helper 的暫存器契約問題，因此不能把舊尺寸當成可用餘量。新的正確元件仍需由實際 object 量測，計入入口、延續、所有參照、PC-relative、對齊、跳躍距離及 adapter／veneer 成本；本輪不宣告任何位元組可自由使用，也不接受候選放置。

```sh
python3 check-placement.py --firmware <exact-original> --object <pinned-carrier.o> --witness <pinned-witness.elf> --elf-parser <reviewed-elf32.py> --layout <full-original-image-layout.ld> --reference reference-inventory.json
python3 check-negative-gates.py
```

ELF parser 唯讀沿用 reset-memory compiler review 並固定雜湊；明確路徑可跨 shell／checkout 重播，但仍需提供原 object、witness 與完整 layout，不能以雜湊重建缺失檔案。Python 只檢查檔案及有限算術，不執行 RV32、不模擬指令集、不連網、不碰硬體、不作 OTA。
