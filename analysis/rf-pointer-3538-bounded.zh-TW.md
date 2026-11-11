# V1.31 candidate：0x20003538 pointer 的有界掃描

## 結果與限制

固定來源是 `analysis/resident-entry-reference-2026-10-21/reference-carrier/REFERENCE-CANDIDATE-ONLY-00040000-0006EA66.bin`，191078 bytes，SHA-256 `133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22`；檔案 offset 0 對應候選 flash 0x40000，掃描到 0x6EA66（不含）。候選不等於已證明設備上執行的 resident image。

`python scripts/scan-rf-pointer-direct.py` 在每個 halfword 起點匹配連續的 32-bit LUI、可選同一暫存器 ADDI，接著同一 base 的一般 load/store 或 C.LW/C.SW。檢查存取範圍是否與 `0x20003538..0x2000353B` 重疊；包含例如 `0x20003514+36` 的相鄰 alias。這是 encoding 掃描，資料或指令中間也可能是假陽性，並非控制流或可達性分析。結果：

| LUI PC | access PC | 原始 bytes（檔案順序） | 候選存取 |
|---|---|---|---|
| 0x40E7E | 0x40E82 | `3737002003278753` | `lui a4,0x20003; lw a4,0x538(a4)` |
| 0x59EF0 | 0x59EF4 | `b737002083a78753` | `lui a5,0x20003; lw a5,0x538(a5)` |
| 0x60928 | 0x6092C | `b737002083a78753` | 同上 |
| 0x64330 | 0x64334 | `3737002003278753` | 同第一列 |

此限定模式沒有 store 命中，因此**沒有找到寫入來源，不代表不存在 writer**；無法宣稱指標初始化值、allocator、物件大小或初始化時序。未掃描分離的指令序列、其他寄存器傳遞、GP/SP、間接 pointer、批次 copy/清零、ROM/RAM 執行碼、其他 image 或動態寫入。特別是 ACK 中 `s0=0x20003514` 與 `[s0+36]` 的指令不相鄰，本掃描不能涵蓋；已知候選 ACK 讀取詳見 [既有追查](rf-status-provenance-2026-10-24.md)。store 命中若日後出現，腳本記錄來源暫存器而非憑空推定其值。

## 有界 forward propagation（兩個已識別 RF windows）

`python scripts/scan-rf-pointer-identified.py` 固定上述完整影像 hash，僅選取 [既有 disassembly provenance](rf-status-provenance-2026-10-24.md) 的 ACK `645DC..646A8`、RF_Config `64BAE..64CEC`，不把其間或其餘資料視為 code；這是已識別 RF 範圍的子集，不是全部 RF code。每個 halfword 均作獨立候選起點，最多 32 條，非反組譯對齊或可達性證明。LUI/AUIPC、ADDI/ADD、部分 compressed 指令傳遞常數；load 目的寄存器變 unknown，其他不支援編碼或控制流立即終止並殺死 facts。

結果：261 個起點、471 次指令檢查、261 條路徑遇 unknown/control stop，涉及 149 個不同 stop PC；range-end 與 budget stop 均 0。候選 target-overlapping stores **0**（輸出 `hits: []`）；每個候選起點可重複計入同一 stop，因此 path count 不等於 distinct PC。此結果不排除間接、跨控制流、未實作指令及其他範圍的 writer；startup zero writer 的條件性證據仍見 [初始化分析](rf-3538-init-coverage.zh-TW.md)。

合成 bounded case 測試 `0x20003514 + 36` 的 C.SW：來源已知為 7 時報告 source value 7，改變 base 建立指令、插入 unknown 或截去 store 都不再命中。這只是測試掃描器，不是 firmware 的初始 pointer 值；實際非零 pointer writer 和初始值仍未知。hash、範圍內外 mutation 與截斷測試皆在 host 記憶體，未修改來源檔或操作硬體。重現：`python -m unittest discover -s tests -p test_rf_pointer_identified.py -v`。

## callback 容量條件

在候選 ACK path 的 `0x64650` 讀 then-live `[0x20003538]` 作 A2；若 callback 實際為 APP `0x174EE` 且 A0=2、A1=0，APP 讀 A2+1、+2、+3，所以需要這三個位址可讀；以有效 buffer 表述通常為至少 4 bytes。候選先前在部分路徑向重新讀取的指標 byte 0 寫入，另需該次指標 byte 0 可寫；多次讀取未證明相同。這些是條件性記憶體前提，不是已證明的分配容量或可達缺陷。helper 輸出 byte 不可當 allocation 大小；指標建立、寫入來源、實際可讀容量、callback 安裝與路徑可達性仍未知。

## 重現與 mutation

`python -m unittest discover -s tests -p test_rf_pointer_direct.py -v` 檢查固定影像命中、影像內外翻位與截斷拒絕，並以合成 direct store 和 `0x20003514+36` compressed alias store 驗證來源暫存器、破壞 alias 和截斷。合成 store 不是 firmware writer 證據。未連接或執行設備。
