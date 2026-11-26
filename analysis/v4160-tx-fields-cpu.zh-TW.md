# v4.1.60 TX bytes38..43 與有效記錄至 lookup 的串接

2026-11-26。76800-byte decoded APP，基址 `0x8000`，SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`。接續 [TX記錄選擇與byte23](v4160-tx-record-cpu.zh-TW.md)，本批補上A非零路徑的原getter、bytes38..43、後兩段config copy參數，並接到原8A56 lookup入口。

全部離線合成狀態。copy/fill資料與時鐘標量返回使用明示前提，沒有執行provider、讀取實機ROM/RAM來源、送出event或操作設備。沿用既有C來源，本批未改共享CPU、原BIN或C，不提高C覆蓋百分比。

## byte38：布林、完整byte與兩次讀取

F為144-byte TX frame基址；F+38初值來自前批原A968布林getter。本批直接執行下列原getter，核對它們只改A0、不建立frame或寫記憶體：

| getter | 原來源 | 返回值 |
|---|---|---|
| D314 | U16[2000bf5c] | 非零→1 |
| D3E8 | U8[2000bf5f] | 非零→1 |
| 181C4 | U8[2000c925] | 完整byte |
| B5B4 | U8[2000beef] | **≥2**→1，1不成立 |
| C35A | U8[2000bf12] | 完整byte |
| CD44 | U8[2000bf26] | 完整byte |

每個返回後重新讀F+38，再OR、SB。181C4是**兩次實際讀取**：第一次取 `(R1<<3)&8`，第二次取 `(R2<<3)&16`。32組fixture在兩次呼叫間改值，確認bit0/bit1來自各自當次byte，不能合成一次入口snapshot。

其餘新增成分為 `bool(D314)<<1`、`bool(D3E8)<<2`、`(B5B4結果)<<5`、`C35A<<6`、`CD44<<7`。後兩者沒有先遮成單bit，高位可重疊；SB只截低byte，不把A0的完整移位OR值一併截斷。

## byte39：完整byte逐次OR，最後bit7不是一般的 !ready

先由原8440讀 `U8[GP+364]`，完整byte直接SB至F+39。依序由下列getter讀完整byte，左移1..6後OR進舊stack byte：

| 左移 | getter／來源 |
|---|---|
| 1 | F6B0／2000bf9d |
| 2 | F714／2000bfa2 |
| 3 | F6E2／2000bf9f |
| 4 | F746／2000bfa4 |
| 5 | 8202／2000bee1 |
| 6 | F992／GP+277 |

這些輸入不是一律布林。每段重新讀F+39，使用OR，不能以加法代替，也不能假設欄位互不重疊。

最後先實際執行 `821e(0)`：它重新讀config指標/config4；bit3設定即返回0，否則讀GP+193，byte<3才返回1。

- getter非零：新增bit7為0，不再讀config4。
- getter=0：caller**重新讀config指標/config4**，新增值為 `((fresh_config4>>3)^1)&1`，再左移7。

因此config4 bit3設定雖使ready=0，新增bit7仍是0，不能簡化成 `!ready`。固定狀態下，新增bit7等於「config4 bit3清除且GP+193≥3」；4組明示跨返回flag變更另核對實際兩次讀取。最終仍是OR：前面完整byte已設的bit7不會被清掉。

24組stack hook另在各getter返回後改寫F+38或F+39，確認caller使用live byte。hook屬fixture外部變更，不是純getter的已證副作用。

## 171BA 與 bytes40..43

原171BA先讀 `[40060]`，再建frame16保存RA，讀GP+365作A0、設A1=1，呼叫未知target。A2/A3沒有被設定，不賦予其用途。1792組明示正常返回保存全部記憶體、S暫存器、GP/SP/frame，破壞A/T，提供raw word；**provider本體未執行**。

原續段計算：

```text
value = (((raw*10)&0xffffffff)>>4) + 50
```

caller只SH低16位至F+40。乘法先截32位，+50在右移之後；例如raw=0x19999999或0xffffffff時value=0x10000031，儲存halfword=0x0031。數值單位未證明。

接著：

- byte42=`low8((mode & 31) | (U8[GP+356]<<7))`。bits5/6為0，bit7只取GP+356最低位，非零偶數不會設bit7。
- byte43由三次原 `821e(0/1/2)` 結果組成bits0..2，各讀GP+193/194/195（config4 bit3設定時不讀對應RAM）。每次getter都重新讀config。

本批45組readiness案例涵蓋三個index、config4={0,8,255}、欄位值={0,1,2,3,255}，完整核對短路與stack stores。D314則另窮舉全部65536個halfword的零／非零布林。

## 兩段config copy分別重新載入

原1356E續段先讀舊byte43，**載入第一個config指標P1後才store新byte43**，再讀4004C並呼叫 `(F+44,P1,16)`，RA=13586。

第一段明示返回後，原碼重新讀config指標P2，再讀4004C，呼叫 `(F+79,P2+96,16)`，RA=13598。400組完整鏈分別測P1/P2及target保持或變更，來源資料均由fixture提供，沒有讀實際config來源或執行copy本體。

第二段明示返回後才重新讀記錄handle，傳 `(handle,160,F+20,76)` 至原8A56。原transport建立nested frame，再以匹配的合成第一個handle進入4013C lookup服務入口，A0=handle、A1=GP+128、RA=8a90；至此停止。

這400組從原TX建構入口、byte23、完整A非零getter鏈接續至lookup。每段資料與時鐘返回仍具上述前提；不證明transport admission、真正送出、事件投遞或完整回到記錄迴圈。合成變更P2/slot/handle是可重現的依賴探針，不是觀測到provider副作用。

## 驗證

[test_v4160_tx_fields_cpu.py](test_v4160_tx_fields_cpu.py) 使用 `check()`，一般與 `-O` 保留同樣檢查：

```text
python analysis/test_v4160_tx_fields_cpu.py
python -O analysis/test_v4160_tx_fields_cpu.py
```

```text
PASS: 14336 original byte38/39 chains; 65536 halfword booleans; 32 repeated-read pairs; 24 stack hooks
PASS: 45 readiness cases/4 fresh-flag pairs; 1792 declared clock returns; 400 active-record-to-lookup chains; 4 mutations
PASS: original getters/fields40..43 and fresh config/slot/handle loads; provider and transport posting bodies NOT executed
```

14336組為14個來源逐項256值 × 其他來源基值0/255 × 兩個記錄位置，不是所有來源的全組合。1792組為全部256個task byte × 7種raw邊界。400組完整鏈為兩位置 × mode={0,1,31,32,255} × GP356={0,1,2,3,255} × 四種raw × config/slot固定或變更。

四個記憶體副本mutation：第二次181C4的mask16改8、B5B4閾值2改1、171BA加50改51、第二段config偏移96改97。均由指定存取／getter結果／參數檢查拒絕，不將解碼或unmapped錯誤當作偵測。完整核對stores順序、原frame及入口／返回暫存器；copy後比對完整144-byte frame，包含未修改區域。

主區段SHA-256（右界不含；其他原getter亦受整檔hash固定）：

| 範圍 | SHA-256 |
|---|---|
| `13430..13598` | `7b17123131e59dd204b9e107a455cb7fb8092c2f030d9ce97711650009c0542b` |
| `171ba..171de` | `5b93f07a292d4126dda1d69831f6e78e30b4b1c3a921765329257fce214ebf6c` |
| `821e..8248` | `4af30f18b196e304a5b6d30bb167ee2a02c567c4ffcf4e36bb4f72e6204bcdcd` |

後續待接transport admission與傳輸frame、返回後的第二筆記錄，以及實際provider綁定、保存與payload生命週期。本批沒有執行未知provider、transport posting、IRQ或設備操作。
