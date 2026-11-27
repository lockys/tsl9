# task5 table0 與物件清理：重新入列、欄位寫入與保存界線

接續 [task5 parser／函式表](v4160-task5-parser-static.zh-TW.md)，本輪展開 type128 reason0 的 table0 callee，以及 type129 reason5 後續的物件處理函式。原始 APP 仍是 ID-2966 V4.1.60、76,800B；V1.31／V1.40 resident 是參考候選，未證明為原機 installed provider。

## 新增完整範圍

| 本體 | V1.31 | V1.40 | 各版本 bytes／指令 |
| --- | --- | --- | --- |
| table0 | `0x5E40E..0x5E4B0` | `0x5E556..0x5E5F8` | 162B／60i |
| cleanup | `0x5774E..0x5784A` | `0x5788E..0x5798A` | 252B／78i |
| V34 adapter | `0x6A722` | `0x6A906` | 4B／1i |

合計 **836B／278 指令**。每個 byte 都由原始 sparse HEX 完整提供，且與 candidate 相同；沒有把缺失 source 的補值算成證據。固定 operands、hashes、CFG、所有本機邊的語法見證，均納入 ledger。新增的是靜態合約，C 重建覆蓋率不變。

## table0：找物件、處理一個節點或重新送出訊息

入口 A0 為 parser 從四-byte message 讀出的 U16 ID。函式保存 control word `0x4002420C`、寫零並執行原始 `FENCE.I`，再呼叫既有 key lookup。lookup 返回 0 時，還原 control／frame，返回 **2**；沒有 object 寫入。若得到 O，先讀取 `U32[O+288]` 作為初始 head P，再清 byte O26、保存 O 至 S0。

| 本機分支 | 動作 |
| --- | --- |
| 初始 head=0 | SH0 到 O66，還原 control／frame，返回 0 |
| head!=0，fresh O15 bit0=0 | builder(fresh U16 O8,128,0) |
| head!=0，fresh O15 bit0=1 | 呼叫 V34，依回覆決定本機 pop，再查看 fresh head 是否仍非零 |

條件是 **O15 bit0**，不是節點 flags 或 O26。其他 O15 bits 不參與此分支。

builder 正常返回 0 時，本機將 O26 寫成 1；其他回覆沒有這個本機寫入。兩者都在還原 control 後返回 **0**，不轉送 builder status。若 callees 或其他 writers 會改 O26，最終欄位值仍需要額外保存條件。

### V34 的參數與後續 pop

V34 本身只是一條無新 link 的尾跳，實際 target 為 `0x530FE`／`0x531A6`。本輪固定原始參數：

```text
A0 = fresh U16[O+8]
A1 = fresh U8[initial P+8]
A2 = fresh U8[initial P+12]
A3 = (fresh U32[initial P+4] + 2) modulo 2^32
```

本體沒有解參考 A3 所指的 payload；其有效範圍、保存、產品功能及實際效果屬於尚未展開的 target 合約。初始 node 至少 13B 的有效範圍可涵蓋這裡的欄位讀取，並非真實配置大小證明。

V34 回覆 **0** 後，table0 **重新讀取 O288 得到 P'**，接著立刻讀取 P'+10，沒有新的 null guard。因此需要 post-call head 仍為有效 nonnull node；不能假定它與先前 P 相同。原指令隨後：

1. 先取樣 U16[P'+10]，再 SB0 到 P'+9。
2. 對剛才取樣的 halfword OR 上 sign-extended `-256` 後以 SH 寫回 P'+10：**byte10 保留，byte11=255**。
3. 將 U32[P'+0] 寫到 O288。
4. fresh U16[O66] 非零時減一並以 SH 寫回；零時略過減法。

V34 回覆非零時，略過這組本機 node mutation。兩條路徑最後都會再讀 fresh O288：非零時呼叫一次 builder(128,0)，零時 SH0 到 O66。正常返回均為 0，並不證明 V34 成功或失敗狀態的產品意義。

### 本機沒有迴圈，佇列可以形成條件性重複

table0 的完整本機 CFG 是 DAG，共 13 條語法路徑。每次呼叫最多一次 V34、一次 builder；向前面位址跳回 builder 區塊的邊，不會再回到 node-processing 區塊。

若 task／ID／table binding 保持相符、builder 配置並接受新的獨立 message，且之後確實經 receive／handler 再次派送，table0 可使下一筆 `(128,0)` 再進入自己。這是**跨訊息的條件性 recurrence**，不是直接遞迴或本機無窮迴圈。O15 bit0 持續為 0 時，本機沒有 pop，不能單憑再次入列宣稱工作有進展。

新的 message 可能在目前 handler 釋放原 message M **之前**就被建立並入列，所以需要兩者配置與保存期有效、互不混淆。builder0／O26=1 也不表示事件已送達：前輪 sender 會忽略 event helper 的 scalar 回覆。

parser 對 type128 reason0 會忽略 table0 的 scalar，接著固定返回 0。即使 table0 因 lookup0 返回 2，外層 parser 仍是 0，不能將它當作物件處理已成功的證據。

## cleanup：先走完 O280，再走 O288

cleanup 保存入口 O，從 O280 的 list 開始。每個 sampled node P：

1. 若 U32[P+4] 非零，直接呼叫 private release `0x20000110`，參數為該 payload pointer。
2. 重新讀 fresh head；讀 node+10 的 U16，令 byte11=255、byte10 保留。
3. 將該 fresh node 的 +0 next 寫回 O280，繼續迴圈。

O280 變為零後，以同樣方式處理 O288。這兩條是實際本機迴圈；沒有長度上限或 cycle detection。callee 前後 head／next 保持相同且有限、節點仍有效時，才能把它解釋成逐節點前進。

**本機沒有直接 free node P。** 它嘗試釋放的是 P+4 保存的 payload pointer，隨後仍讀取 head node；payload 與 node／object 的配置關係、callee 是否釋放或重配置節點、fresh head 是否有效，都需要另外證明。標記 byte11 並 pop，不等於完成 node 生命週期。

這裡的 node byte11 也不是前輪 message header 的 `M-2` marker。cleanup 直接呼叫 private release，沒有經 public deallocator 的 `U8[pointer-2]==255` guard；private release 自己仍有 heap 範圍／header／account 等合約。callee 返回不代表原配置區塊必定已成功釋放。

## 兩條 list 之後的欄位與全域處理

| 階段 | 原指令可證明的本機行為 |
| --- | --- |
| O272 | pointer 非零時 private release(pointer)；**沒有本機清零 O272** |
| O39、O38、O40、O41 | 每個 fresh byte 不等於 255 時，呼叫 `0x43A14`／`0x43AA0`(該 byte) |
| O41 | 上述 O41 helper 正常返回後，本機另寫 255；O38／O39／O40 沒有對應本機寫入 |
| object key | 呼叫 `0x57A4A`／`0x57B8A`(fresh U16 O8)；target 尚未展開，不能推定 O 被保留或釋放 |

`0x57A4A` 呼叫之後，本體不再解參考原 O。令固定全域 B=`0x200033B8`／`0x20003408`、C=`0x2000319C`／`0x200031EC`：

- fresh U16[B+180] 非零，直接進 epilogue。
- 否則，寫零到 B+308，再把 fresh U32[C+156] 複製到 B+176。
- fresh U32[C+88] 為零，進 epilogue；非零只是 gate，**沒有把它當 callback 呼叫**。
- gate 非零時，S0 改為 C；fresh C+32 pointer 非零，便 private release(pointer)，正常返回後將 C+32／C+36 兩個 words 寫零。C+32 為零時略過該 call 與兩個 stores；C+88 沒有本機清零。

cleanup 沒有固定的成功返回 0。A0 可能來自最後一個 callee，或 late C+32 的明確 load；該 load 為零的路徑才可就本機指令直接得到 0。reason5 parser 在 cleanup 正常返回後，自行設 A5=0 再返回，沒有再解參考 O，也沒有測試 cleanup scalar。

## 保存與驗證範圍

本輪需要 conditional Xwchc／RV32 解碼與原始程式／資料映射；O 至少 292B、table0 node 至少 13B、cleanup node 至少 12B 的有效對齊範圍，以及 nested calls 的 normal return、所需 S0／S1／S2／SP／RA／saved-frame 保存。payload 不得破壞仍要讀取的 node／object；跨 call 的 fresh heads 必須保持可存取。control word、全域、heap、message、object、node 與 frame 的 nonalias、IRQ／DMA／重入／其他 writers 仍屬明列前提。

table0 每條本機正常返回路徑都會還原保存的 control word；這不是實體 critical section 或硬體進展已證明。完整 node／payload／O ownership、原機 provider、實際派送及外部副作用仍未封閉。

[checker](check_v4160_task5_object_static.py) · [精確 ledger](v4160-task5-object-static.json)

```powershell
python -B analysis/check_v4160_task5_object_static.py
python -O -B analysis/check_v4160_task5_object_static.py
```

全部 278 條新指令各有單點變異拒絕，另有 12 個 unsigned→signed 變異。兩版本共核對 26 條 table0 完整語法路徑、4,608 條 cleanup 不可變 CFG 見證，涵蓋所有本機邊；不是可變 queue／list／heap 模擬，也不宣稱所有 syntactic paths 真實可達。純 scalar 算式涵蓋全部 U16 marker／count 值與 256 個 O15 flag bytes。

普通與 `-O` 須與同一 ledger 逐 byte 相符，核對固定 APP、兩候選、SDK raw header 及 Xwchc 來源向量。未執行原韌體、target ISA、provider、callback、MMIO 或硬體。GitHub 僅新增本輪三份分析檔；原 BIN 與既有工作保留。下一步仍需展開 V34 target、ID helper／object-key helper，以及 P4／O272／C32 的實際配置來源與保存條件。
