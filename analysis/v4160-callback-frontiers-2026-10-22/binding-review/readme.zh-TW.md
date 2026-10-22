# App 對 resident callback 的來源綁定

[English](readme.en.md) · [繁體中文](readme.zh-TW.md)

本次只讀 ID2966 原 FW 與舊封存來源，完整保留9個原始範圍 **682 bytes／248 列**：App199E2..19B16（308／106）、read1979A..197B8（30／13）、write197BE..197F0（50／20）、timer19764..1979A（54／22）、四個既有 Flash helpers（190／73）、MAC-source leaf18F56..18F88（50／14）。範圍右界不含，依實際入口 CFG／RET 得出。197B8 的另一個6-byte tail 不屬於 read callback。

`ledger.json` 保存全部 raw bytes／操作數，`r2-static.json` 提供全部248列獨立靜態操作數比對。沿用已封存解碼器，無新編碼格式、opcode 生成、CPU／ISA／ESIL／MMIO／native 執行、compiler／linker、網路或硬體操作，也不重跑 HOST suites。

| Record 欄位 | 實際 App 來源 | 結論 |
|---|---|---|
| +52 | 64-byte 清零覆蓋 record，沒有後續 explicit SP-relative store 寫此完整 word | 只在清零、copy、無別名／干擾與相關呼叫保存條件下為零 |
| +56 | 19A76 AUIPC + 19A7A ADDI−732；19A7E SW SP72，record base SP16 | 數值1979A |
| +60 | 19A80 AUIPC + 19A84 ADDI−706；19A88 SW SP76 | 數值197BE |
| +8 | 19A4A LUI08078000、19A4E ADDI−1024、19A52 SW SP24 | 數值08077C00；不是 Flash ownership 證明 |

清零呼叫19A38使用 nominal slot40048、目的 SP+16、A1=0、count64；候選 slot 指向2000039C。後續18F56只寫 caller SP+8..13 的六個 bytes，App loop只將六個 bytes 寫至 SP+40..45，因此在有效、無別名堆疊等條件下不修改 SP+68..71（record52）。本次不讀取任何實體 UID 值。原版本 guard 必須正常通過；沒有繞過它，也沒有假設兩份公開候選都能通過原 App 的版本檢查。

record+56 的1979A先 fresh READ32(4004C)，**早於 frame 分配與 RA store**；再 SP−16，A4=entryA2，保存 RA 到SP+12，令 A2=`u32(entryA1<<2)`、A1=entryA0、A0=A4，間接呼叫載入的完整 target（JALR 清 bit0），還原 RA，A0=0，SP+16，RET。slot/provider 效果未知時不能證明 generic ABI；native 提早保存 frame／改變 scratch 也不代表相同 fault prefix。

在精確候選 slot4004C→copied20000332 profile 下，完整58-byte／18-row forward-byte-copy leaf 不寫 SP／RA／S／GP／TP／T／A7，A0/A1/A2 也不被它改寫。其 MMIO word4002420C、FENCE.I、正常存取與返回仍是條件。因而 read callback 正常返回 A0=0、A1=entry source、A2=wordcount左移2，並在有效無別名 frame／正常 copy 下保存 S0。這是暫存器參數契約，不宣稱原始 C prototype 或已安裝 resident 身分。

第一個 resident read callback 的條件式實際參數為 source08077C00、wordcount1、destination=tableSP+12，故只複製4 bytes。其輸出在 parentSP+12..15，read wrapper RA 在 parentSP−4..−1，且 table 保存的 S2 從 parentSP+16 開始；有效、非零、無 wrap／別名的堆疊下三者不重疊。

此 **非零4-byte** copy 還能消除 native wrapper 在呼叫前新增的 A3 值：20000346 先令 A5=0，348 的非零 count 分支前往354；354 的 ADD 先定義 A3，358 的 LBU 才讀它；35C 再令 A3=destination+index。正常完成後 A3=destination+3。相反，null guard 或 count0 的 early return 不寫 A3，原 entry A3 會被保存；wordcount40000000左移2也會 wrap 成0。因此這是狹義 actual caller projection，**generic native full ABI 仍為 false**。

`post-read-liveness.json` 以純 CFG read/write 資料流內聯舊封存 allocator/fill/free，沒有模擬指令值。它明示 block256、tag78、count3、有效不 wrap heap／frame與穩定 config 等條件，保留 allocator 返回零／非零的來源路徑關聯。兩份候選結果一致：

| 邊界 | 仍可能帶入原 read-callback 出口值的 A/T registers |
|---|---|
| early table RET | A1、A2、A3、A6、A7、T0–T6 |
| 下一個 +60 callback | A7、T0–T6 |
| 若 +52 可非零的 allocator failure callback | A2、A6、A7、T0–T6 |

到這些邊界前沒有對上述原 A/T 值的自有 read-before-write，仍不代表允許任意 clobber：值可在 early return 逃逸，未知 callback 也可觀察它們。若 config52為零的保護條件成立，才移除 failure callback frontier。實際4-byte copy的 A3覆寫證明獨立於這份 caller 資料流；沒有依 PSABI 忽略 T 或 A7，normal-caller replacement／full ABI 均未在本 scope 宣稱完成。

record+60 的197BE保存32-byte frame、RA與S0，將 entryA2 保存為 source；entryA1未使用。它依序呼叫18E98 unlock、18EC4 erase、18EF2固定256-byte／64-word program、18EB6 lock，再以A0=1呼叫19764。後者讀 GP+382 的 byte 作縮放，操作E000F000系列暫存器並無限條件輪詢；Flash helpers亦有 busy polls。正常、存取有效且輪詢終止時還原 S0／RA／SP、回傳0；不檢查成功狀態，時間單位、GP有效性、IRQ排除、實體成功與 OTA 路由均未知。

第一個+56的S0保存如今可在上述 exact-copy 前提下閉合；但後續 allocator若透過非零 config52呼叫未知 target，仍須該 target 的保存條件。只有這些中間呼叫保存 live S0 時，後續 fresh READ32(live S0+60) 才能化為配置的+60並綁定197BE。

App record+12由清零得0，兩候選的 default令它為256；App record+14的 halfword0803令byte14=3，非零default不改它。若相關 fresh config／heap／callback／index 保存與無別名條件均成立，三次 write callback 的 source為同一新配置 buffer，A1=64、目的08077C00／08077D00／08077E00，數值範圍終點08077F00。這不是已驗寫入 extent、所有權或燒錄許可。

已有 `experiments/tsl9-v4160-contract-model/src/flash_contract.c:fc_write_registers` 的 HOST provider／語意模型（pin84f33520…），包含197BE及timer順序；本次沒有重建或執行它。四個 Flash leaf 的既有 native 工作與新 read callback native 審查屬其他封存範圍，不能把 HOST 模型稱為原 callback 的 native ABI 已閉合。

```sh
python -B check.py --project-root /absolute/project/root
python -B check.py --project-root /absolute/project/root --firmware /absolute/ID-2966-V4.1.60-decoded.bin
python -B check.py --project-root /absolute/project/root --firmware /absolute/ID-2966-V4.1.60-decoded.bin --candidate-root /absolute/wch-resident-candidate-2026-10-21
```

預設只讀中繼資料、actual counts皆為零。FW模式要求原檔76800 bytes及SHA0ee64183…fb667，重讀682B／248列並拒絕7個實際單一操作數反例。可選candidate模式另外查2份原始HEX、slot40048／4C與8個有界範圍（984B／370列），不補洞。checker唯讀，Python／sh可攜，沒有重試先前被拒絕的Shell。
