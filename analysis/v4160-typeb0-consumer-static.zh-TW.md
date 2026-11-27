# ID11 的 typeB0 消費端與選定 word 釋放

接續 [B0 forward helper 與 pointer leaf](v4160-task8-forward-static.zh-TW.md)，本次從目的 task byte 的初始化來源，接到完整候選 B0 handler，再展開共同 payload cleanup wrapper。兩份參考候選合計 **1,616 bytes／576 條指令**，全部由原始 sparse HEX 覆蓋，且與候選 bytes 一致。這是條件性靜態合約，沒有證明實際 installed provider 或實機功能，既有 C 重建覆蓋率不變。

| 完整範圍（右端不含） | V1.31 | V1.40 | 每版 |
| --- | --- | --- | --- |
| registered B0 handler | `0x4D1B0..0x4D4BC` | `0x4D248..0x4D554` | 780B／277i |
| selected-word release wrapper | `0x4A7BA..0x4A7D6` | `0x4A852..0x4A86E` | 28B／11i |

兩者函式內 CFG 均為 DAG。handler 有兩個普通 RET；wrapper 有一個 RET及一個不建立新 link 的 private release 尾移交。未知 callee／private service 能否返回，仍是各條跨呼叫路徑的前提。

## ID11：送出與接收使用兩個不同 byte

重用 [ID11 initializer](v4160-id11-outer-tail-static.zh-TW.md) 及 outer registration 的既有完整原指令證據：在條件性 admitted chain 中，outer 將 handler位址交給 registration，再以返回的 ID進入 initializer。若既定 count／capacity／table、所需 frame保存及無干擾前提持續成立，這筆 ID為11。

initializer 以 saved S0 保存入口 ID，分別發布：

| 用途 | V131 | V140 |
| --- | --- | --- |
| handler 接收時 fresh讀取 | `0x20002EDF` | `0x20002F2F` |
| other callback／B0 sender 使用 | `0x20002EEE` | `0x20002F3E` |

兩者都寫入同一個保存 ID的 low8，但不是同一個儲存格，也不是原子配對。只有值一直保存到各自 fresh read時，才可把 sender與receiver串成 task11；這裡未證明所有 writers、實際 scheduler invocation 或 queue delivery。也不能把這條候選 resident 路徑與 APP其他 B0 consumer 混為同一個入口。

## Event入口與訊息處理的共同尾段

以 E表示完整入口 A1。handler首先 sign-extend E的low16，只有 bit15=1 才建立48-byte frame並接收訊息；沒有 bit15時，在 frame外直接返回0。

bit15路徑以 fresh saved task byte呼叫 `0x2000028C`。null時不清理訊息，直接返回完整 `E XOR 0x8000`；nonnull M保存在 S0：

- fresh byte0不是 `0xB0`：略過本體派送，以原 M呼叫 public message cleanup。
- typeB0：初始化自己的 release flag `U8[SP+9]=1` 及 `U16[SP+10]=0`，再處理 cached state／opcode。
- 本體派送正常返回後，fresh SP+9非零才嘗試 selected-word cleanup；最後以原 M呼叫 public cleanup，並返回完整 `E XOR 0x8000`。

完整 CFG路徑核對確認：所有走過非空訊息 type讀取的本機普通返回路徑，都包含原 M的 public cleanup 呼叫，且發生在 event XOR之前。**本 handler沒有前面 task8 的「R=19就略過 message cleanup與event XOR」分支。** 未知 callee若不返回或破壞保存條件，則無法由此推導清理已發生。

public cleanup仍是呼叫嘗試，不是實際配置釋放成功的證明。

## Cached state與24-byte共用 scratch

handler先讀取 cached state pointer `0x20002F84`／`0x20002FD4`。若為0，呼叫 `0x4D958`／`0x4D9F0` 取得 allocator的 A0實參，再以 A1=`0x4703`呼叫 `0x20000040`，將結果寫回 cached word。callee與allocator的完整副作用留待後續；不能把回覆當成已知有效物件。

若配置結果仍為0，直接回到 fresh flag cleanup；這條路徑仍可能嘗試釋放訊息內選定的 word，再 public cleanup原訊息。

cached pointer存在時，先要求 fill service `0x2000039C` 對共用 scratch `0x20003154`／`0x200031A4` 清零24 bytes，才 fresh讀取 M+4的 opcode進入分支。其後每個read／write的時間點保持分離；實際fill語義、scratch保存與其他 writer沒有被假定完成。

## 十個 case的呼叫邊界

完整 handler有33個 linked callsites，全部原始目標、operand、CFG與hash固定在ledger；以下只列各已辨認case的第一個專屬呼叫，並不宣稱callee本體的業務或硬體語義已知。

| M+4 opcode | V131／V140第一個case callee | 目前核對的本機邊界 |
| --- | --- | --- |
| 2 | `4D958 / 4D9F0` | 後續呼叫`44DDA / 44E6E`；依回覆分流，可能截小U16[M+8] |
| 6 | `4C7FA / 4C892` | 準備 `(M,&SP10)`，之後進共同回覆／report分支 |
| 8 | `4CC94 / 4CD2C` | 準備 `(M,&SP10)`，接同一個共同分支 |
| 10 | RAM `20000A48` | 使用U16[M+8]及SP+12輸出，另有配置／scratch流程 |
| 12 | RAM `20000A48` | 類似10但後續參數、欄位讀取與report路徑不同 |
| 14 | `4C6AA / 4C742` | 準備 `(M,&SP10)` |
| 16 | `4CAAA / 4CB42` | 準備 `(M,&SP10)` |
| 18 | `4BDC6 / 4BE5E` | 明確準備 `(M,&SP10,&SP9)`，可透過借用位址改變release flag |
| 22 | `4BCD8 / 4BD70` | 準備 `(M,&SP10)`；回覆0時本體直接寫`SP9=0` |
| 24 | `4BBC6 / 4BC5E` | 準備 `(M,&SP10)` |

其他 opcode不進上述case，但仍走共同post-helper與cleanup。表中的參數記法只列明確準備的registers；不證明未知ABI忽略ambient registers。

在原tuple opcode跨未知callee與fresh reads保持不變的額外前提下，前段other callback的表內opcode去掉先行返回的4，正好是此處十個case。opcode30另走null-source B0 forward路徑，抵達這個handler時屬此處的default，而非新增一個專屬case。

opcode2對捕捉的U16[M+8]與scratch halfword作unsigned比較，只有原值不小於scratch值才SH回後者，所以在對應存取、alias與保存前提下是截小到兩者minimum；不把兩次fresh load當成未變快照。

case6／8／14／16／18／24會匯入共同回覆處理；非零回覆還可能經report及其他sender，0與22分支的動作不同。case10／12另有SP+12、SP+14借用輸出、scratch+4 pointer及對 `0x20000110` 的直接呼叫。這些nestedcallee與pointer來源尚未閉合，不能把「完整handler原指令已固定」解讀為各case的所有效果都已證明。

共同post-helper `0x49F54`／`0x49FEC` 以原 M為明確A0，仍是未知呼叫邊界；它也可能影響記錄或flag所依賴的資料。

## 共同cleanup：傳遞選定的word，不是記錄起點

共同尾段fresh讀取 SP+9。非零時，準備：

```text
selected_word_cleanup(M+8, fresh U8[M+4])
```

28-byte wrapper先呼叫已驗證的 pointer leaf `0x49DCC`／`0x49E64`。leaf返回0時還原RA／SP並普通RET；非零時，同樣先還原RA／SP，再無新link尾移交 `0x20000110`，A0是**leaf選出的word原值**。callee之後的實際返回及釋放效果仍未知。

這與直接傳遞 M+8或原forwarder來源pointer不同。從前段B0的32-byte visible message布局可條件性串接：記錄起點是M+8，固定24-byte copy/fill覆蓋的目標實參範圍是 `[M+8,M+32)`；leaf所選word的最大相對offset12，在有效24-byte記錄前提下位於範圍內。

若opcode跨處理全程穩定，本段十個case中，只有以下四個會使leaf讀一個word：

| opcode | 相對記錄offset | 相對訊息M offset |
| --- | --- | --- |
| 6 | 12 | 20 |
| 14 | 0 | 8 |
| 18 | 4 | 12 |
| 22 | 8 | 16 |

word是否非零、是否仍是原內容、是否對應原payload或有效free base，都需要其他證據。未知case或post-helper若改變opcode，不能再套用這個縮小集合。

wrapper在handler+0x1C2還有一次對共用scratch record的呼叫；handler+0x28A另有對scratch+4所讀word的直接private release。這些與共同M+8記錄cleanup是不同來源，不能互相替代或合併成「原payload只被釋放一次」的結論。

## Release flag與訊息保存期

本體的直接flag動作是：初始化SP9=1，以及case22 helper回覆0之後寫SP9=0。case18另顯式把`&SP9`傳給callee；其他callee也可能經ambient registers或alias接觸資料，尚未證明無間接寫入。

因此case22清零後，若post-helper與其他寫入者保持它，才會略過共同 selected-word cleanup；原M的public cleanup仍會被呼叫。這個flag只控制一個呼叫嘗試，不代表原payload已安全交接或完整ownership transfer。

前段task8 callback的flag控制的是另一個frame裡的private cleanup；本handler的SP9是新的獨立flag。兩者不能視為同一個儲存格、同一段lifetime或同一個同步原語。

沒有證明下游已完成copy、深拷貝內含pointer、完成消息投遞、真正釋放所有區塊，或保留的pointer在frame／message返回後仍有效。

## Frame與離線重播

handler的48-byte frame保存8個words於SP+16..47，SP+9 flag、SP+10／12／14 halfwords位於保存區之前；wrapper另有16-byte child frame保存RA。這是原指令位移的區間證據，不是未知callee所有讀寫extent或no-escape合約的證明。

[checker](check_v4160_typeb0_consumer_static.py) 與 [精確ledger](v4160-typeb0-consumer-static.json)：

```powershell
python -B analysis/check_v4160_typeb0_consumer_static.py
python -O -B analysis/check_v4160_typeb0_consumer_static.py
```

檢查涵蓋完整operands／hash、每條函式內CFG edge的到terminal見證、全部DAG路徑的message cleanup與event XOR位置、576條指令變異、14個typed-load變異、65,536個event low16與196,608個U16 minimum樣本，以及ID11初始化／登錄／sender來源串接。語法路徑不等於每條都已證明執行時可達。

下一段優先展開case18、case22、共同post-helper與cached allocation來源，接續追查selected pointer的寫入與保存，並確認實際provider／其他writers。全程只讀本機bytes、原始HEX、不可變CFG與host純量；沒有執行或模擬目標ISA、callback、provider、RAM／heap／queue、MMIO或硬體。GitHub僅新增本階段三份分析與驗證檔案。
