# v4.1.60：4005C／40068 的兩份 SDK 候選靜態合約

2026-11-26。接續 [命中列清理鏈](v4160-cleanup-hits-cpu.zh-TW.md) 與 [provider 槽位映射](v4160-provider-binding-ledger.zh-TW.md)，本批固定 `[4005c]`、`[40068]` 在既有 V1.31／V1.40 參考 carrier 中的完整外層函式、內部呼叫目標與來源映射。

**這兩份 SDK reference candidate 都不是設備 installed resident 的證據。** 本輪不執行候選指令、loader、provider、私有 helper 或 MMIO，不連接設備、不下載輸入，也不產生可刷入映像。既有 C 與共享 CPU 未修改，C 覆蓋率未增加。

成果：[靜態 checker](check_v4160_cancel_provider_static.py) · [JSON ledger](v4160-cancel-provider-static.json)。原 APP 仍是 76800-byte decoded BIN、基址 8000，SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`。

## 本機輸入與 SDK 名稱對照

沿用既有 carrier 的固定來源，本批沒有重新取得 SDK：

| 本機輸入 | bytes | SHA-256 |
|---|---:|---|
| carrier-dec2023，V1.31 連續 segment | 191078 | `133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22` |
| carrier，V1.40 連續 segment | 191574 | `b02cf8ec6829425a558887bd6bc10d28ae1f0e2e9e1850333f0bab6088e9e941` |
| original-dec2023/wchble_rom.h | 243435 | `647a185941fedeb6ba16d544d9bca91a6f53219bb649a5513b59abeb21a9a94c` |

header 並非完整 UTF-8；checker 直接從原始 bytes 解析 ASCII 程式宣告，不轉碼或改寫輸入。固定的宣告為 flash base=40000、JT base=flash+34、stride=4：

| SDK 宣告名稱 | JT index | 數值槽位 |
|---|---:|---|
| tmos_clear_event | 8 | 40054 |
| tmos_stop_task | 10 | 4005C |
| tmos_msg_deallocate | 13 | 40068 |

同時核對函式 cast 與 typedef：bStatus_t、tmosTaskID 為 8 bits，tmosEvents 為 16 bits。這是 **original-dec2023 header** 的參考名稱／型別；沒有把它當成 V1.40 專用 header 或 installed ABI 證明。

原 APP 在 90D8／90DC 讀 40068，在 90FA／9106 組出 4005C；其 task 來自 U8[GP+166]，event mask 來自 index=0..14 的 `1<<index`，所以這些已驗證參數形狀符合上述名義寬度。非零 payload 本身不證明符合 deallocate 的資料前提。

## 固定四個完整外層本體

| 候選 | 40068 target／範圍右界不含 | 4005C target／範圍右界不含 |
|---|---|---|
| V1.31 | 431BA..43208，78 bytes | 439A8..43A14，108 bytes |
| V1.40 | 43246..43294，78 bytes | 43A34..43AA0，108 bytes |

合計 372 bytes。free 本體包含第一個 RET 後仍可達的 null／標記／私有 call 返回區段，沒有以第一個 RET 截斷函式。

checker 固定四份完整 body hash；另僅遮去已獨立驗算的 profile 差異 operand，核對兩份 free 與兩份 stop-task 的完整標準化 bytes。私有 call 的 AUIPC/JALR、clear-event 的 C.JAL、RAM 欄位、return LI、control-word load/store 及 FENCE.I 均另有 operand guard。這是 bytes 與數學公式核對，沒有執行候選本體。

## 共同的控制 word 前置動作

兩個外層函式都先保存當時的 U32[4002420C]、寫零到該地址、遇到編碼 `0000100f` 的 FENCE.I，之後才做下述條件判斷。靜態編碼出的正常返回路徑會寫回保存值；不模擬其硬體／cache 效果。

返回推論都要求存取有效、路徑上的被呼叫函式正常返回並保留外層仍 live 的 S 暫存器、GP/SP 與 saved frame。沒有因為看到保存／恢復指令，就推定例外、中止或私有 helper 一定完成 restore。

## 40068：非零指標還有前置標記條件

參考外層使用 16-byte frame，保存 RA、S0、S1；S0 保存 control base，S1 保存 control word。從原 C.LI operands 解出的正常返回值：

| 參考入口條件 | 本體要求及條件性 A0 |
|---|---|
| pointer=0 | 已做 control／FENCE 前置，不讀 pointer−2，restore 後返回 5。 |
| pointer 非零，U8[pointer−2]≠255 | 讀標記，restore 後返回 4。 |
| pointer 非零，標記=255 | 呼叫私有 RAM helper；正常返回後設 A0=0、restore。 |

私有 helper 的返回值沒有在這層被當成最終狀態碼；但它的完成、記憶體效果與保存合約仍未證。外層自己保存／恢復的 S0/S1，不取代 nested helper 必須保存其 live 值及其他 caller context 的要求。

這收斂了前批通用 free-return fixture 的適用前提：原 APP 只判斷 payload 是否為零，並未先驗證 pointer−2 可讀或標記為 255。本輪沒有讀取任何實機 payload，也不能由這份候選把 callback payload 直接認定為合法 message allocation。

## 4005C：兩個呼叫與 0／6 返回條件

參考 stop-task 外層配置 32-byte frame，保存 RA、S0..S3；S0 保留輸入 event，S2 保留輸入 task，S3 保存 control word。

1. 呼叫私有 RAM 查找 helper，輸入 task／event，將結果保存於 S1。
2. 若結果非零，向結果+2 寫 zero-halfword；這需要該地址有效。
3. 恢復 task／event 參數，呼叫另一個 flash helper。checker 另外確認它也正是此候選 `[40054]` 的 tmos_clear_event target。
4. 讀 profile 的 current-task byte，與完整 S2 比較；相等時讀 pending-event halfword，OR 原 event，再以 SH 寫回 low16。
5. restore control word；S1 非零返回 0，S1=0 返回 6，最後恢復 frame。

查找結果為零也不會跳過第二個 call。clear-event helper 的 reply 不決定這層最終 0／6；不代表任意任務／事件狀態都可用，也不證明真實 timer 或 event 被取消。

| RAM 欄位 | V1.31 | V1.40 |
|---|---|---|
| current-task byte | 2000319C | 200031EC |
| pending-event halfword | 200031DC | 2000322C |

外層沒有先把輸入完整 task word 截成 U8 再比較；本輪的 APP caller 已透過 LBU 提供 0..255，不能把這點外推成任意 32-bit 呼叫輸入皆符合 SDK 型別。

## 六個 call targets 與四個 RAM 來源

沿用既有 startup 操作數／首段 copy 的靜態映射，不執行 loader：

| 角色 | target | V1.31 source | V1.40 source |
|---|---|---|---|
| deallocate 私有 helper | 20000110 | 40380 | 403C0 |
| timer 查找私有 helper | 20000314 | 40584 | 405C4 |
| clear-event flash helper | 4358A／43616 | 4358A | 43616 |

兩份 profile 合計六個 call targets、四個 RAM-source 映射。私有 helper 只固定映射後的 16-byte prefix hash，不宣稱完整函式邊界或 ABI；first-copy 來源也不等於已證最後執行時 RAM bytes。

RAM 查找 helper 的 bytes 含可能需要 WCH compressed profile 的編碼；本輪不把一般 RV32 disassembler 顯示的浮點名稱當成已證實際語意，也不執行或重建這些私有 body。完整 startup、後續覆寫、指令 profile、RAM coherence 與 installed 身分均保留未知。

## 重現與結果

checker 依賴已發布的 `check_v4160_provider_binding_ledger.py` 與本機三份 SDK 輸入。主線目前沒有 `wch-resident-candidate-2026-10-21` 輸入目錄，因此只 clone 倉庫不足以重跑這批候選檢查。輸入需保留在上表對應的既有本機路徑；腳本不自動下載、補資料或執行服務。

預設只讀重算、逐 byte 比對 JSON；`--write` 僅供首次建立新 ledger，使用 exclusive-create。

```text
python analysis/check_v4160_cancel_provider_static.py
python -O analysis/check_v4160_cancel_provider_static.py

PASS: 257 free-path/4 lookup-result algebra cases; 3840 APP typed argument shapes; 6 specified raw mutations; odd-slot distinction
PASS: 4 complete candidate bodies, 372 bytes; 6 call targets; 4 conditional RAM-source mappings; header JT8/JT10/JT13 slots
PASS: ledger exact replay; installed binding/private ABI UNPROVED; NO candidate ISA/provider/MMIO execution
```

一般與 `-O` 均通過，使用 `check()`。主機代數依原 return LI 與型別 operands 核對 257 個 free 分類、四個 lookup 結果形狀與 256×15 個 APP task／event 參數形狀；不會將這些數值用作真實指標去讀取記憶體。

六組 raw mutation 繞過 baseline 全檔 hash 預檢，分別改兩槽 entry pointer、pointer−2 offset、current-task 欄位地址、私有 call target、header JT index；均命中特定 guard，不接受任意解析失敗作為通過。另把 slot pointer bit0 設為 1，確認 raw word 改變而 JALR 正規化 target 可相同；這不構成 installed 綁定證明。

四個完整 body SHA-256：

| 候選／函式 | SHA-256 |
|---|---|
| V1.31 deallocate 78B | `45e504a67ace2215263cfbaddc9d99a0cc0c1714f8289f19889a9573e7c520b5` |
| V1.40 deallocate 78B | `3db0d77ac9e5b56d1b327b3c3576a91acd4895f9d752b337e06b44b07758dfa7` |
| V1.31 stop-task 108B | `b7039b31b68bfe6aeae2e453d4b159efab81edade95c9f3079a56898444ff098` |
| V1.40 stop-task 108B | `ef68aa1e9331e08e48880f35aa3b1d0ec25d2f781fa60289d78a07330beec866` |

後續仍需釐清私有 callee、payload 真實來源／標記與保存合約，及 installed resident 身分。這批縮小參考候選的條件性合約，不把 SDK 名稱或版本相似性提升為設備執行證據。
