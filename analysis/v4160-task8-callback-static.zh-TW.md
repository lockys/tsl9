# typeA0 other callback：函式表、release flag 與 status19

接續 [task8 typeA0 消費端](v4160-task8-typea0-static.zh-TW.md) 與 [extended auxiliary](v4160-task8-aux-static.zh-TW.md)，本次完整核對 other callback 及其唯讀函式表。兩份參考候選合計 **876 bytes／320 條指令，另有 192 bytes 原始表資料**；全部由原始 sparse HEX 覆蓋，並與候選 bytes 一致。實際 installed provider、未知 callee 的效果及保存期仍未證明，既有 C 重建覆蓋率沒有更新。

| 範圍（右端不含） | V1.31 | V1.40 | 每版 |
| --- | --- | --- | --- |
| 完整 callback | `0x4B944..0x4BAFA` | `0x4B9DC..0x4BB92` | 438B／160i |
| 原始 pointer table | `0x6E3B0..0x6E410` | `0x6E5A0..0x6E600` | 96B／12 對指標 |

函式內 CFG 是 DAG，共一個普通 RET。CFG 的 call fallthrough 以 callee 正常返回及所需保存條件成立為前提，不代表已執行 callee 或證明其終止。

## 登錄來源與 caller 範圍

已驗證的 ID8 resources tail 形成 callback 位址，經 setter A 寫入 `0x20002F70`／`0x20002FC0`。task8 的 other callback 分支重讀同一個 word，再傳入：

```text
(fresh U16[M+2], &tuple_at_parent_SP20, &release_flag_at_parent_SP11)
```

這是候選 source 與 consumer 的匹配，不是執行時 installed binding 或所有 writer 的閉合證明。初始 release flag=1 也不能取代 callback 後的 fresh flag 讀取。

對全部 64 個 decoded low6 opcode 逐一套用已驗證的 task8 mask／奇偶分支，在 decoder 成功、tuple 保持不變、相應 callback word 非零等條件下：

- other callback：`2,4,6,8,10,12,14,16,18,22,24,30`。
- odd callback：`1,3,5,7,9,11,13,15,17,19,23,25,27,29`，本階段不展開。
- 特殊 report／bypass 分支：`0,20,21,26,28` 與 `31..63`；這些 opcode 不會從該初始分派進入本 callback。

callback 再把 opcode30 分開，所以本次來源域只有其餘 11 個 opcode 能進入表派送。code4 transport routing 與這裡的 payload opcode 是不同欄位，不能混為一談。

## opcode30 與 connection 路徑

opcode30 先呼叫 RAM service `0x20000A1C`，明確準備的參數為 `(ID,30)`。若取得 connection，且 `low8(connection[2]+2)>1`，便呼叫 helper `0x49E4A`／`0x49EE2`，明確實參為 `(connection[3],ID,0,30,0)`，之後呼叫 connection helper `0x4B88C`／`0x4B924`。

這條路徑最終固定返回 0，忽略上述 helper 的 scalar 回覆；即使未知 helper 回覆 19，也不能由這個返回鏈直接推成 callback 的 19。此路徑沒有直接清零 release flag。

非30路徑先捕捉 tuple word0，並把原始 A2（release flag address）存入 saved register。若 `(word0 & 0x00FFFF00)==0x00120100`，略過 connection lookup；否則明確準備 `(ID,初次讀取的 opcode)` 呼叫同一 RAM service。

若 lookup 非空且 connection byte4 非零，最後固定返回 0。若該 byte 的 sign bit 未設，會先呼叫 `0x49ED0`／`0x49F68`，再 fresh 讀取 byte4、設 bit7 並寫回；sign bit 已設時略過這個動作。

**兩個初次 lookup callsite 的 A2 都仍保有原始 release flag address。** 上面的二參數記法只列明確準備的 A0/A1，沒有證明 lookup 的真正 prototype、其他 argument register 不被讀取，或它不保存 A2。因此「沒有直接發布 flag pointer」不能推成「下游收不到或不會保存 pointer」。

## 函式表的條件與內容

共同 table path 依序要求：fresh task byte `0x20002EEE`／`0x20002F3E` 不等於255、初次 opcode<=24、兩個 row pointer 非零，以及捕捉的 word0 low16 為0（opcode18例外）。任一 gate 失敗固定回覆6。

index=`(unsigned opcode >> 1)-1`，row stride8。一般 callback 入口沒有先驗證 opcode>=2；opcode0/1 的模32位移為 `0xFFFFFFF8`。本次已知 caller 的11個 opcode，才足以證明 row 在96-byte表內；不可把這個來源條件升格為一般入口已做好下界檢查。兩個 pointer 分別讀取，也不是原子配對快照。

| opcode | V131 decoder／handler | V140 decoder／handler |
| --- | --- | --- |
| 2 | `44DC4 / 4B2E0` | `44E58 / 4B378` |
| 4 | `44DF6 / 4C048` | `44E8A / 4C0E0` |
| 6 | `44E64 / 4C01A` | `44EF8 / 4C0B2` |
| 8 | `44F0E / 4BFEC` | `44FA2 / 4C084` |
| 10 | `44F9C / 4CA7C` | `45030 / 4CB14` |
| 12 | `44FE8 / 4CA7C` | `4507C / 4CB14` |
| 14 | `4503A / 4C9E2` | `450CE / 4CA7A` |
| 16 | `44F0E / 4BF98` | `44FA2 / 4C030` |
| 18 | `450D2 / 4C2A0` | `45166 / 4C338` |
| 20 | `0 / 0` | `0 / 0` |
| 22 | `45110 / 4C32A` | `451A4 / 4C3C2` |
| 24 | `45178 / 4B35A` | `4520C / 4B3F2` |

opcode20 的零 row 是已捕捉的原始資料，沒有被當作已知 caller 域中的一次派送。各 row target 的內部效果尚未在本階段展開。

## row 回覆與 report

table gates 通過後，先呼叫 captured row decoder：

```text
(fresh U8[tuple+0], fresh U8[tuple+1], fresh U32[tuple+8],
 fresh U16[tuple+4], &local_SP24)
```

其回覆非零便原值返回。零才呼叫 captured row handler，明確參數 `(原 ID,&local_SP24)`。

row handler 非零時，如果 fresh tuple byte1 非零，原值返回；否則建立 local SP+16 的 report。byte16= fresh opcode，halfword18取決於 opcode，byte20=low8(row handler 回覆)。opcode14 的 halfword 由 SP+24 word 所指向的兩個 bytes 組成 little-endian 值；其餘取 SP+24 的 low16。

report helper `0x448CC`／`0x44960` 返回0時，callback 改成返回0；非零則呼叫 `0x4A0B4`／`0x4A14C`，明確參數 `(ID,22,1,&report_at_SP16)`，並傳回該 helper 的完整 scalar。因此 row handler 的非零回覆不是每條路徑都能原值穿透。

report construction 只寫 offsets16、18、19、20，沒有在此寫入17、21..23。借用輸出 SP+24 的全部初始化範圍仍由未知 row decoder 決定。

## 唯一的 release flag 直接清零

row handler 返回0時，fresh opcode4 直接返回0；其餘呼叫 `0x49E4A`／`0x49EE2`，明確參數：

```text
(fresh task byte, 原 ID, 0, fresh opcode, &local_SP24)
```

回覆非零便原值返回，**不會走到唯一的 flag clear**。只有此 helper 返回0，才呼叫 `0x49DCC`／`0x49E64`，明確參數 `(&local_SP24,fresh opcode)`；且這個 leaf 回覆非零時，才執行 callback+0x18E：

```text
U8[原始 A2] = 0
```

之後依 fresh tuple word0 mask 與 cached connection 是否非空，可能把 fresh opcode 寫入 connection byte4，然後返回0。helper 與 leaf 的內部合約留待下一段驗證，這裡只固定呼叫與分支邊界。

函式共16個直接 store：9個 frame save、4個自己的 scratch/report store、2個 connection byte4 store，以及這1個 flag clear。沒有直接寫 tuple 或直接呼叫 payload release；未知 callee、connection alias 或其他 writer 的間接影響仍不能排除。

flag 清零抑制的是父 handler 後續的 private payload release 嘗試；它不能單獨證明深拷貝、exclusive ownership、成功投遞或完整保存期。

## callback 的19與父 handler 串接

本函式沒有固定產生19的本機常數路徑。19可能來自未知 row decoder、某些 row handler 路徑、report 後的 sender 或 forward helper；前提是相應 callee 真的回覆19且保存條件成立。所有這些直接返回19的路徑都繞過唯一 flag clear。

父 handler 的 other callback 返回非零時會替換保存的 R。若這個 R=19 一直保存到共同尾段，則 fresh flag非零且 original M+8非空時，**仍先嘗試 private payload release**，再呼叫 ID helper；之後才因 R=19 略過 public message cleanup 與 event XOR。這不是「訊息保留時 payload 也安全保留」的證明，也沒有證明 requeue 或已完成釋放。

這與 [extended auxiliary 的19](v4160-task8-aux-static.zh-TW.md) 不同：後者先被 decoder 轉成 tuple status2與 scalar bit6，不能直接當作 handler R=19。

## frame、重播與剩餘工作

callback frame 為96 bytes，保存槽在SP+60..95；report 在SP+16，output pointer在SP+24。若額外假定 output使用24 bytes，兩者避開保存槽；但傳入 pointer 不代表已證明 callee 只寫24 bytes、不保留 stack address或遵守所有保存要求。

[checker](check_v4160_task8_callback_static.py) 與 [證據 ledger](v4160-task8-callback-static.json)：

```powershell
python -B analysis/check_v4160_task8_callback_static.py
python -O -B analysis/check_v4160_task8_callback_static.py
```

檢查涵蓋完整 operands／雜湊、每條 CFG edge 的普通返回見證、全部 syntactic DAG 路徑的返回來源與 flag clear 條件、320條指令變異、12個 typed-load 變異、48個表指標變異及128組 QK.C.SHSP operand vectors。SHSP 來自已保存且驗證雜湊的官方 Xwchc 定義，原 halfword `0x81FC` 為 `SHSP a5,18(sp)`；沒有執行該指令。

下一段應展開134B forward helper、126B pointer leaf、表內的 decoder／handler，以及其餘呼叫邊界。實際 provider 綁定、所有 writers、pointer 的傳遞與保存合約仍未閉合。

全程只讀本機 bytes、原始 HEX 與 host 純量／CFG資料；沒有執行或模擬目標 ISA、callback、provider、RAM／heap／queue、MMIO 或硬體。GitHub 僅新增本階段三份分析與驗證檔案。
