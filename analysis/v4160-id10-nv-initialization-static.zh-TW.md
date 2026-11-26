# 第五個外層 ID10 初始化：配置、NV 載入與單 byte 保存

接續[ID9 vector 與派送邊界](v4160-id9-vector-dispatch-static.zh-TW.md)，本次完整核對 `6c300`／`6c4ec`、配置callee、逐筆載入tail、保存wrapper及下一筆task登記。resident映像仍是參考候選；原目標程式、allocator、fill、NV與硬體服務都沒有被執行或模擬。

| Body | V131 範圍（右端不含） | V140 範圍（右端不含） | 每版 bytes／指令 |
|---|---|---|---|
| initializer | `6c300..6c31c` | `6c4ec..6c508` | 28／10 |
| allocate/setup | `6b928..6bafe` | `6bb0c..6bce2` | 470／138 |
| record loader | `6b286..6b338` | `6b46a..6b51c` | 178／60 |
| save wrapper | `6b25e..6b286` | `6b442..6b46a` | 40／15 |
| next outer window | `6dd6e..6dd7e` | `6df5e..6df6e` | 16／4 |

合計1464個原始bytes、454條指令。[檢查器](check_v4160_id10_nv_initialization_static.py)固定所有operands、CFG及各body SHA256；完整值見 [JSON證據](v4160-id10-nv-initialization-static.json)。initializer的code增量為492 decimal，其三個callees為484 decimal，不能一律平移。

## Saved ID10 與暫時的 FF

initializer建立32-byte frame，保存RA@SP+28、入口A0@SP+12。沿用前階段條件性入口A0=10、A2=11，A1仍是不固定的callback登記結果。

allocate/setup先將ID byte `20002fc2`／`20003012`寫為`ff`。其正常返回後，initializer重讀自己的saved A0，將同一byte改為10，取回RA並釋放frame，再尾跳record loader。這裡的ID10來自入口保存值，不依賴callee的返回A0；也不能忽略中途曾存在的`ff`狀態。

## 配置來源、null guard 與 fresh count

配置讀取config F+14：`200031fa`／`2000324a`，向RAM `20000040`請求 `(16*n,66)`。n是fresh unsigned byte，因此request為0..4080 bytes；**n=0仍會呼叫allocator**。

pool word位於 `20002fbc`／`2000300c`；count byte位於 `20002fc1`／`20003011`。count先清零，allocator返回值存入pool word後有null guard：

- 返回零：跳過pool迴圈與F+8旗標更新；在所需保存前提下count維持0，但仍執行共同路徑的兩個16-byte fill。
- 返回非零：再次fresh讀F+14，將該值存為count，然後初始化逐筆16-byte記錄。兩次F+14讀取不能自動視為相等；有效非alias block及足夠extent仍須另證。

每筆本機要求fill兩段6 bytes為`ff`，分別位於slot+0及slot+6，接著SH0至+12、SB0至+14。**slot+15不在這些本機初始化範圍內**。fill的實際寫入、返回與保存合約仍未由此確定。

成功路徑掃描後fresh讀F+8：零時將 `200035a3`／`200035f3`寫為`80`，非零時寫0。allocation-null路徑不更新這個byte，不能推定所有路徑都給它相同初值。

共同路徑另要求將 `2000317c`／`200031cc`及 `2000316c`／`200031bc`各16 bytes清零，並寫入固定RAM defaults。全部33筆固定非frame store區間及兩個fill目的區間均避開task metadata、T及相關config/source/hook欄位；動態pool writes、provider副作用、實體alias與非同步writers仍保留前提。

## 兩個掃描迴圈的上界

配置與載入兩個迴圈都從index=0開始，每次只有在 `index < fresh_U8_count` 時進入body，返回後index加1並mask255。

這個上界不要求count固定：在任意fresh byte下，index=255都不能通過比較。因此在callee返回且index/live GPR保存、code及存取有效等條件下，最多255次body，不會走到已准入的wrap。檢查器涵蓋全部65536個index/count配對。

此終止界線不證明payload extent與fresh count一致，也不證明allocator、fill或NV服務會返回。

## NV 載入與非零返回的清理分支

loader對每個准入index i呼叫 `440c2`／`44156`，原始參數為：

```text
A0 = 512 + 6*i
A1 = 16
A2 = fresh_pool + 16*i
```

i可准入的最大值為254，因此A0最高2036。這只固定callee入口參數；NV地址單位、實際讀取／輸出、provider綁定與保存期仍未知。

若該call返回非零，caller要求將slot+0/+6兩段6 bytes填`ff`，並SH0至+12。**這個fallback沒有本機重設byte+14或+15**；不能假設失敗或部分寫入的provider會保存它們，也不能將先前+14=0當成必然仍成立。

掃描後必定呼叫 `6af88`／`6b16c`，再按fresh flags選擇是否呼叫 `6b16e`／`6b352`及 `6b1d4`／`6b3b8`。setup雖清了第一個flag，兩次fresh flag讀取都在狀態call之後，不能排除它或其他writer改值；另一個flag沒有被setup清除。

## 單 byte 保存與 Xwchc SBSP

loader釋放frame後尾跳save wrapper。wrapper重新建立32-byte frame，再次呼叫 `6af88`／`6b16c`；以這次unsigned返回值選擇：≤1則byte10，否則byte2。

選定值只寫至SP+15。實際窄指令bytes為 `dc87`，已依快取且雜湊固定的LLVM `RISCVInstrInfoXwch.td`與 `xwchc-valid.s`確認是：

```text
qk.c.sbsp a5, 15(sp)
```

這是單byte store，不是halfword或一般浮點store。新增解碼只適用於明示的條件性LLVM-Xwchc profile；檢查器另重播6個官方SBSP向量及全部128個compact-register／4-bit-offset欄位組合。

接著call `494ee`／`49586`，參數 `(66,1,SP+15)`。byte在32-byte frame內，與saved RA@28..31分離；但provider是否同步消費、是否保存此借用指標及延後讀取，尚未證明。call返回後wrapper恢復RA／SP並RET，沒有強制新的A0/A1/A2狀態。因此**count=0也不能宣稱整條鏈沒有NV或外部服務**。

## 條件性返回與 ID11 邊界

只有上述allocator、fill、NV、status及optional callees均正常返回並保存所需frame／code／live metadata／payload等條件成立，才可接到outer `6dd6e`／`6df5e`。

outer不測試save wrapper的返回值，直接形成handler `4d1b0`／`4d248`。若fresh count仍11、capacity仍≥14、table pointer仍T=`200047f4`，且extent／非alias／保存前提成立，下一筆登記寫entry11=`20004820`，回覆A0=11、A2=12，count變12。

A1沿用writer/callee返回後的opaque值，不能由呼叫前A1=1推定其仍為1。新的邊界停在 `6dd7a`／`6df6a`對最後一個outer initializer `4d172`／`4d20a`的呼叫前。

## 離線重播

```text
python analysis/check_v4160_id10_nv_initialization_static.py
python -O analysis/check_v4160_id10_nv_initialization_static.py
```

兩種模式要求454次逐指令operand變異拒絕、65536個index/count配對、6個LLVM SBSP向量、128個欄位案例及精確JSON重播。APP／candidate／SDK／快取來源與上游靜態證據身分一併核對。沒有執行或模擬目標ISA、provider、NV、callback、MMIO、CSR或trap；新增靜態合約不增加既有約88.09%的C重建基準。
