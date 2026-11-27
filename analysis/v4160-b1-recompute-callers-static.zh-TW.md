# B1 設定輸入來源、尾跳與兩個 caller gates

接續[設定巢狀服務](v4160-b1-config-child-static.zh-TW.md)，這次完整展開已定位的輸入解析函式與兩個直接 caller，共 **608 bytes、216 條指令**。已將四個外來 halfwords 串接到重算來源，確認 **27～251／328～17040** 的交錯限制，以及兩個 caller 對回覆 **2** 的不同判斷。

[Python checker](check_v4160_b1_recompute_callers_static.py) 與[固定 JSON ledger](v4160-b1-recompute-callers-static.json) 保存原始 operands、hashes、stores、完整 CFG、frame／返回定義及串接憑證。只分析本機 bytes、strict sparse HEX、不可變 CFG 和封閉 host 整數關係；沒有執行或模擬目標、建立可變物件／provider 模型、存取硬體、重播封包或進行目標網路分析。

## 完整原指令範圍

| 用途 | V131 FLASH | V140 FLASH | 每份 bytes／指令 |
|---|---|---|---|
| 輸入解析／尾跳 | `[0x5afba,0x5b03c)` | `[0x5b102,0x5b184)` | 130／43 |
| gate80 | `[0x5c74e,0x5c7ac)` | `[0x5c896,0x5c8f4)` | 94／35 |
| gateflag | `[0x5c7ac,0x5c7fc)` | `[0x5c8f4,0x5c944)` | 80／30 |

名稱 gate80／gateflag 只是本報告用來區分函式的標籤。完整範圍包含普通 RET 之後仍被分支進入的指令。gate 以 `JAL ra` 呼叫輸入解析函式；解析函式以 **`JAL x0`** 尾跳至已核對的 `0x55e44／0x55f84`，不能把它當成新增返回位址的普通 call。

本輪由指定原始來源中的直接跳轉編碼搜尋定位這些位置，再用完整函式／strict HEX 驗證正向串接；沒有將搜尋不到其他編碼當作「不存在其他 caller、函式指標或 runtime 路由」的證明。實際 installed resident provider 仍未確認。

## 來源 Q：四組 little-endian 值，先讀取再發布

解析入口為 P，先捕捉 **Q=U32[P+276]**，沒有 P／Q null guard、來源長度或配置 extent 檢查。接著依序讀取以下 bytes，前一組通過才讀下一組：

| held value | 實際讀取順序 | 組合 | 通過的無號範圍 | 發布 halfword |
|---|---|---|---:|---:|
| V1 | Q+4、Q+3 | `(Q4<<8) OR Q3` | 27～251 | P+472 |
| V2 | Q+6、Q+5 | `(Q6<<8) OR Q5` | 328～17040 | P+474 |
| V3 | Q+8、Q+7 | `(Q8<<8) OR Q7` | 27～251 | P+476 |
| V4 | Q+9、Q+10 | `(Q10<<8) OR Q9` | 328～17040 | P+478 |

Q offsets 3～10 是四組 **little-endian** U16，並非按照讀取先後一律將第一 byte 放低位。直接來源存取至少需要可讀到 Q+10，即 **11-byte extent**；這不是來源真的有 11 bytes 或資料已初始化的證明。

第一／三個 gate 是 `low16(V−27)<=224`；第二／四個是 `low16(V−328)<=16712`。checker 對全部 65536 個 U16 值核對，確認通過域正好是表列的閉區間，沒有額外 wrap 範圍。

任一 gate 失敗，直接 `A0=1; RET`，不走本函式的任何 store 或 child。全部通過後，四個 held values 才依序 SH 至 P+472、474、476、478，然後尾跳至重算函式。所有來源 byte reads 都在第一個 SH 之前；不是每寫一欄再重新讀取下一組。各 byte 仍是分別取樣，不能稱為原子快照。

解析函式沒有 frame、linked call 或 SP／RA／S 暫存器定義，通過路徑也不改 A0。因此尾跳時 **原 P 與原 RA 都保持**。對應的重算函式普通回覆 0／2 可沿原 RA 回到 gate；解析函式沒有在尾跳後強制覆寫 scalar 回覆。相符完整鏈的回覆域為：**拒絕 1、進入重算後 0 或 2**。

唯一直接 stores 是上述四個 scalar halfwords，沒有新增保存 Q 指標。P 的直接 extent 至少為 480 bytes，進入重算與 leaf 的鏈則仍需要先前定位的 488-byte 存取範圍；這都不證明物件配置或保存期。

## 範圍可以串接，但模式 2 的截斷次序仍不能省略

假設同一 P、接受的欄位值及所需模式，在後續 fresh loads 前沒有被其他 writers、alias 或非同步更新改變：

- `A=min(U16[P+464], accepted P+476)` 與 `C=min(U16[P+468], accepted P+472)` 均不超過 **251**。所以 P+480／P+484 雖經 low8 再以 halfword 寫入，這條路徑不會損失有效位元。
- `B=min(U16[P+466], accepted P+478)` 不超過 **17040**；2704 floor、2120 cap 都不會突破這個上限，因此重算寫入的 P+482 為 **0～17040**。
- 非 mode 2 的 D，來自與 accepted P+474 的 min，再保留或 cap，故寫入 P+486 為 **0～17040**。mode 2 仍是先 signed min、再 low16、最後套 2704 floor，只能保留 **2704～65535** 的界線，不能逕用輸入的 17040 上限。
- 若 leaf 重新讀取的 Z=U16[P+484] 仍在 0～251，則 `min(Z,low16(q))` 也在 **0～251**，最後 P+78 的 byte store 不再截掉有效位元。q 的有號除法／low16 次序仍須保留。

這些是有條件的 writer 合約，未證明實際可達資料。也不能推出欄位必為正：其他 min 的來源仍可能為零，讓 A 或 C 為零。模式與來源在不同函式內都是 fresh loads，沒有共同 snapshot 證明。

## gate80：只分零與非零，呼叫過後均返回 0

先讀 fresh byte P+22，必須恰為 **9**；再於 16-byte frame 中讀 P+16，必須恰為 **80**。任一不符時略過 child，普通返回 **1**。

條件通過後以原 P 呼叫解析函式，並檢查**完整 A0 回覆 R 是否非零**：

| 回覆 | 本機分支 effects |
|---|---|
| R=0 | 讀 fresh P+160 word，清 P+43 byte，寫 P+160 為 held word OR 256 |
| R≠0 | 讀 fresh P+42 byte，OR 1 後寫回 P+42 |

兩個 called arms 隨後共同讀 fresh P+17、將 bit 7 設定、寫 P+16=1，恢復 RA／S0／SP，並強制返回 **0**。`ORI -128` 接 byte store 的效果為低 byte OR 128，不能把符號擴展誤認成寫入整個 word。

在相符鏈的回覆域內，**R=2 與 R=1 走相同的非零分支**。但 2 是重算四欄位全部相等的回覆，1 才是解析拒絕，不能將 gate80 的所有非零回覆統稱為「輸入驗證失敗」。gate80 回覆 0 只表示其本機 called arm 的返回常數，不能單獨當作設定有改變的證據。

## gateflag：只攔截恰為 1，讓 0 與 2 繼續

先檢查 fresh P+22 byte 恰為 **9**，再讀 fresh U32[P+264] 的 **bit 5**。任一 gate 不符時返回 **1**。符合時以原 P 呼叫同一解析函式，只在完整回覆 **R==1** 時強制返回 1，略過此 gate 自己後續的物件 stores。

R 不等於 1 時，重新讀 fresh P+16 byte：

- 恰為 1：寫 P+16=81。
- 其他值：將 fresh P+168 word OR 128 後寫回。

兩路都強制返回 **0**，再恢復 RA／S0／SP。相符鏈中 **R=2 與 R=0 都能進入這段**，與 gate80 的分類不同。若只看某個通用「非零」標籤，就會遺失這個差異。

兩個 gates 都保存入口 P 於 S0；已核對的解析、重算及 leaf 沒有 S0 定義，支持匹配鏈中的 register 保存串接。這仍以合法 frame／物件範圍、非干擾 alias 和正常返回為前提，沒有建立實際 heap 或指標有效期模型。gate 的後續 stores 也都不直接寫 P+124；若其值由重算／leaf 保持，gate 不會因分支本身將它改掉。

## 驗證與尚未封閉的來源

```powershell
python analysis/check_v4160_b1_recompute_callers_static.py
python -O analysis/check_v4160_b1_recompute_callers_static.py
```

checker 重跑祖先驗證，核對原始 APP／SDK／兩份候選身份、完整 strict sparse HEX 與固定 ledger。三個本機 CFG 均無環，各有 **45／36／32 條 edges**，每條都有語法上的 entry→edge→某個 exit walk。尾跳是本機 exit，callee 效果由另外核對的完整重算／leaf 合約串接。

完整 DAG 語法路徑數為 **5／4／5**：解析有四條拒絕返回、一條尾跳；gate80 有三條到 frame epilogue、一條早退；gateflag 有四條到 frame epilogue、一條早退。這些是圖上計數，沒有假設每條路徑條件都能滿足，也不是實測機率或 target traces。

返回定義憑證追查 A0 最後的常數／A5 來源，確認 gates 普通返回只有 0／1，並檢查每個 child／tail edge 傳入原 P。frame 憑證檢查配置點支配所有 SP-relative 存取，且經過配置的每條本機 RET 路徑都必先解除 frame；沒有因此證明 stack 記憶體有效或不與 P／Q 干擾。

負向檢查修改 **216 個指令位置**及 **14 個 typed-load funct3**，全部必須被拒絕。純整數檢查包括所有 65536 個 U16 gate 值、65536 組 LE16 byte pairs、clamp 範圍與回覆分類；沒有可變目標記憶體、封包或 provider 的執行模型。

仍需追查 **P+276 的來源 writer／有效長度、兩個 gate 的實際外層派送**、`0x5d006／0x5d14e` 等巢狀服務、實際 clock／arena／record 綁定，以及 clear 後節點有效期、完整消費與釋放順序。本次未增加既有 C 重建分子或更新 **95.75%** 靜態重建快照，也未宣稱完整可用韌體已驗證。
