# B0 case18／case22：回覆轉換、槽位保存與 post-helper

接續 [完整B0 consumer](v4160-typeb0-consumer-static.zh-TW.md)，本次完整核對兩個case及共同post-helper。兩份參考候選合計 **860 bytes／358條指令**，全部由原始sparse HEX覆蓋，且與候選bytes一致。這是條件性靜態合約，沒有提高既有C重建覆蓋率；實際installed provider與完整payload保存期仍未證明。

| 完整範圍（右端不含） | V1.31 | V1.40 | 每版 |
| --- | --- | --- | --- |
| case18 | `4BDC6..4BE5E` | `4BE5E..4BEF6` | 152B／66i |
| case22 | `4BCD8..4BDC6` | `4BD70..4BE5E` | 238B／98i |
| post-helper | `49F54..49F7C` | `49FEC..4A014` | 40B／15i |

case18與post的函式內CFG為DAG；case22只有一條構成cycle的back edge，位於最多15筆的槽位探查。所有call／tail目標、完整operands與hash固定在[checker](check_v4160_typeb0_cases_static.py)及[ledger](v4160-typeb0-cases-static.json)。未執行目標ISA、provider或記憶體模型。

## case18：三種22必須區分

父handler傳入 `(M,&caller_SP10,&caller_SP9)`。case18建立48B frame，保存原M、halfword output address與release flag address。首先以 `U16[M+8]`、`&local_SP30`呼叫RAM `20000A48`；原A2 flag address仍在ambient register，且被另存於S2，不能宣稱lookup看不到它。

若lookup物件的fresh byte8 bit5有設，先以local SP30的halfword呼叫 `4B66C / 4B704`取得callback pointer，再以 `(fresh U16[M+2],lookup物件,18)`作indirect call。callback返回0才繼續ordinary流程；非零則寫出fresh U16[M+8]，再依fresh M+17決定返回值。**這裡callback回覆22本身不會直接清零release flag。**

ordinary流程呼叫 `4BB22 / 4BBBA`，明確準備的參數為：

```text
(fresh U16[M+2], fresh U16[M+8], fresh U32[M+12],
 fresh U16[M+10], 0,
 (82 if fresh U8[M+17] != 0 else fresh U8[M+4]))
```

此callee回覆恰好22，才會直接寫 `U8[原A2]=0`並強制返回0；這條直接清零路徑沒有本機halfword output store。其他非零回覆則先寫fresh U16[M+8]到原A1 output，再受fresh M+17影響。

ordinary callee回覆0時，fresh M+17非零就返回0；若為0，呼叫 `45104 / 45198(fresh U16[M+2])`，其非零回覆被映射成22、零映射成0。**這個本機合成的22也不直接清零flag。**

| 回覆來源 | 本機flag clear | halfword output／返回 |
| --- | --- | --- |
| 初次lookup空 | 無 | 寫fresh M8；fresh M17=0回1，非零回0 |
| callback pointer空 | 無 | 寫fresh M8；fresh M17=0回14，非零回0 |
| indirect callback非零，包括22 | 無 | 寫fresh M8；fresh M17非零改回0，否則保留完整callback回覆 |
| ordinary helper恰好22 | 寫0 | 無本機output store，回0 |
| ordinary helper其他非零 | 無 | 寫fresh M8；fresh M17非零改回0，否則保留回覆 |
| ordinary0後的follow-up非零 | 無 | 本機回22，沒有本機output store |

因此1、14、22或0都不能只看數字就推導flag或output結果。表格只描述直接原指令；未知callee仍可能修改、保存或透過alias影響欄位，caller初始化的halfword0也不代表所有nested paths後仍保持0。

## case22：先找物件，再探查15個槽位

case22保存M與原A1 halfword output address，沒有顯式release flag參數／store。它同樣先呼叫 `20000A48(U16[M+8],&local_SP18)`。lookup空回1；callback pointer空回14；若有indirect callback且回覆非零，原值傳回。這些路徑都寫fresh U16[M+8]到caller output。

ordinary部分先呼叫 `4B61E / 4B6B6(fresh U16[M+2])`。第一個lookup非空便跳過key store；只有第一次空、再以65535查找成功的fallback分支，才把先前捕捉的message ID寫到該物件的U16+0。兩次都空則返回9並寫fresh M8到output。這裡尚未展開lookup本體，不能假定物件唯一性、配置大小或lookup會自行配置。

取得物件O後，探查以下15個halfword head，找第一個0：

```text
U16[O+4+12*i], i = 0..14
```

每個非零head使index加1、pointer加12；index到15後離開，不在迴圈內呼叫外部服務。有效記憶體與保存條件成立時，最多15次probe。最後一個probe位於O+172..173；若最後一槽被選中，後續12B record實參區間到O+184（右端不含）。

全部15個head非零時返回9，並重新讀取fresh U16[M+8]寫到output，**不是把index15寫出**。這條路徑與初次lookup空路徑都跳到helper+0x4E的同一個M8讀取點。錯誤碼9還可來自兩次key lookup空；不能以9反推是哪個分支。

迴圈憑證包括first zero在index14與全部15槽佔用兩條完整原CFG見證，以及index／interval算式；沒有建立可變slot、heap或register模型，也不證明所有實際記憶體存取都會完成。

## 記錄複製早於後續request與report

選中槽位後，依次準備三個邊界：

| 動作 | 明確實參 |
| --- | --- |
| copy `20000332` | `(O+4+12*i, M+8, 12)` |
| 同一copy service | `(&local_SP20, M+8, 12)` |
| request `4A25A / 4A2F2` | `(fresh U16[M+2],23,fresh U16[M+12],0,16)` |

request回覆會寫入local SP+28。若先前copy採用預期byte語義，SP+28原本是從M+16複製來的word，現在被request返回pointer取代；這不會回頭改寫已傳給第一個copy的槽位。

request空時，返回17並寫fresh U16[M+8]到caller output。**此時兩次12B copy呼叫已先發生，函式沒有本機rollback動作。** 這是呼叫順序證據；不表示未知provider確實寫入、寫入具持久性、其他alias沒有改動，或後續consumer已讀到它。

request非空時，另呼叫：

```text
copy(request_reply, fresh U32[M+16], fresh U16[M+12])
report(fresh U16[M+2], &local_SP20)    // 45144 / 451D8
```

report回0則helper回0，非零則helper回22；這兩條末端沒有直接寫caller halfword output。沒有在此證明request的實際配置extent、copy長度可達範圍、source有效性或report消費／保存方式，也沒有看到對該request reply的直接release呼叫。

在前段固定byte-copy合約與欄位保存條件下，第一個槽位copy包含M+16的pointer值。這正是前一階段opcode22的pointer leaf選取來源；後續request失敗17或report失敗22時，父handler不走case22成功清零flag的直接分支，仍可能嘗試共同selected-word cleanup。保存、釋放與consumer的真正先後效果尚未閉合，不能宣稱安全ownership transfer或已發生實際錯誤。

## post-helper：opcode27不讀M+17

共同post-helper沒有store、frame或S-register改動。它首先測試的是 **U16[M+0]==0x00B0**，同時要求typeB0及byte1=0，並非只檢查type byte。

通過後，兩種本機tail條件不同：

- opcode18：必須另fresh讀取M+17，且值恰好為1。
- opcode27：跳到共用比較點，以opcode與27比較，**不讀M+17，也沒有M17==1的要求**。

匹配時準備 `(fresh U16[M+2],1)`，不建立新link地尾移交 `4D962 / 4D9FA`；其完整返回與副作用尚未證明。不匹配時普通RET，A0保持原M；父B0 handler未採用這個scalar回覆。

opcode27即使沒有專屬B0 case，也能從default路徑到post-helper。前段sender固定A2=0與byte1=0的對應仍需copy／provider／writer保存前提，不能把初始化值當作後續fresh讀值。

## 接回父handler與frame

父handler的SP+9是case18收到的flag位址；case18 ordinary helper回覆22所造成的直接清零，最後對應為helper返回0。case22沒有自己的flag store，父handler是在其正常回覆0之後才直接清零SP9。這兩種成功分支都需post-helper／其他writers保存flag，才會略過共同selected-word release呼叫；原訊息的public cleanup與event XOR仍在各自正常返回路徑上。

兩個case的48B frame保存words於SP+32..47。case18的lookup output SP+30..31、case22的lookup output SP+18..19與snapshot SP+20..31避開自己的保存槽；這只證明原指令offset，不證明callee只寫這些範圍或不保留stack pointer。

copy與request／report也可能觀察ambient registers。flag未直接傳入case22，不等於未知callee無法經alias或其他暫存器取得相關pointer。所有指標extent、輸出初始化、實際provider綁定、ordinary return、S/SP/RA及saved-frame保存、無IRQ/DMA/重入干擾，仍是明列前提。

## 離線重播與剩餘工作

```powershell
python -B analysis/check_v4160_typeb0_cases_static.py
python -O -B analysis/check_v4160_typeb0_cases_static.py
```

完整operands／hash、每條CFG edge到terminal見證、15槽迴圈邊界、case18多種22與M17 override、case22 fallback／copy／request順序及post18／27分支都有精確憑證。檢查另拒絕358條指令變異與2個typed-load變異，涵蓋全部65,536個post halfword及65,536個opcode/M17組合。

下一段需展開record lookup、callback pointer來源、ordinary helper `4BB22 / 4BBBA`、request／report／IDhelper及槽位後續consumer，才能繼續釐清pointer保存與清理的合約。全程只讀本機bytes、原始HEX、不可變CFG及host純量；沒有執行或模擬目標ISA、callback、provider、RAM／heap／queue、MMIO或硬體。GitHub僅新增本階段三份分析與驗證檔案。
