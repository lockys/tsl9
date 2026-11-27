# B1 兩個 RAM callbacks：查詢輸出、registry 選取與 record 清理

接續[key來源與提交尾跳](v4160-b1-key-source-tail-static.zh-TW.md)，完整展開兩個不同RAM literal所指的reference本體，共 **624 bytes／226條指令**。確認兩者都將SP+12交給同一查詢服務；本機沒有在query前初始化該word，實際輸出合約仍待展開。另將record callback接回既有handler：callback回覆不控制record清理，handler讀的是返回後fresh metadata。

[Python checker](check_v4160_b1_ram_record_callback_static.py)及[固定JSON ledger](v4160-b1-ram-record-callback-static.json)保存原始hashes、逐指令operands、完整CFG、全部stores與邊／路徑證書。全程離線、嚴格sparse HEX，不執行或模擬目標、query、registry、clock、RAM／frame或provider。沒有packet replay、硬體及目標網路分析；C重建覆蓋率不變。

## 來源與完整邊界

| callback | RAM完整範圍 | V131 FLASH | V140 FLASH | 每版bytes／指令 |
|---|---|---|---|---|
| record callback | `[0x2000138e,0x200013e8)` | `[0x415fe,0x41658)` | `[0x4163e,0x41698)` | 90／35 |
| registry selector | `[0x200013e8,0x200014c6)` | `[0x41658,0x41736)` | `[0x41698,0x41776)` | 222／78 |

解碼以RAM PC進行，並重新核對startup第一段copy的完整source／destination涵蓋；不能直接在FLASH PC解析C.JAL與AUIPC/JALR目標。完整範圍包含首次RET之後仍可達的分支，selector最後+0xdc跳回+b6。

這是候選載入映射，不證明實際啟動完成、RAM內容保存或installed callback身分。

## Record callback：三種完整query回覆

入口A0=P。P=0立即無frame返回0。非零建立32-byte frame，保存RA／S0，並請求：

```text
RAM 0x20001122(P, SP+12)
```

本機query前只保存暫存器到SP+24／28，**沒有SP+12初始化**。指標是當次frame內四-byte範圍；query是否寫入、保存指標、需要其他參數或正常返回，仍未證明。

令完整query回覆為R：

- R=0：以A0=0、其餘then-live參數呼叫RAM `0x20000d50`，恢復frame並傳回該child實際A0。
- R=`ffffffff`：略過後續調整，恢復frame並傳回同一`ffffffff`。
- 其他R：R不直接用作pointer或計算量；開始讀config及query輸出。

因此不能把「非零」當成統一成功，也不能由R不等於0／`ffffffff`單獨證明SP+12已初始化。

## Record callback的單次調整與後繼參數

F=`0x200031ec／0x2000323c`。依原指令先讀c=U8[F+23]，再獨立讀U32[F+40]，再讀T=U32[SP+12]。threshold A在word為零時等於c，非零時為c>>1。

```text
若 unsigned T < A：T′ = low32(T + fresh U32[0x20003238／0x20003288])
否則：T′ = T
V = low32(T′ - A)
```

只加一次，沒有再檢查T′是否已足夠，也未排除overflow／underflow；不指定物理時間單位或clock進展。

V先寫回SP+12，再重新載入A1；fresh U8[P+41]作A0，呼叫`0x436a8／0x43734`。其正常回覆直接通過epilogue，不轉成固定status。此本體對P的明示存取最少需42 bytes，但query／下游callee可能有額外需求；不能把42當成整條鏈的已證明extent。

目前只確定SP+12的借用／明示讀寫順序，沒有證明query／其他callee不保存frame pointer、P內容在返回後仍有效，或整條callback的完整生命期。

## Selector：早期statuses與optional前置服務

selector一律建立48-byte frame，保存RA／S0..S5。B=`0x200033b8／0x20003408`，I=`0x20003514／0x20003564`。

1. 捕獲U32[B+156]作head；為零返回2。
2. 非空時fresh U8[I+7]==5則返回3。
3. 否則保存原入口A0為Out。fresh U32[I+12]非零時，先呼叫`0x6430e／0x643f8`，其A0當時仍是Out；接著以第一個回覆作then-live A0呼叫`0x638ea／0x639d4`，之後清I+12 word。為零時略過兩個calls與clear。

Out沒有本機null guard。optional第一個未知callee可觀察Out，故即使本機沒有把Out當pointer發布至全域，也不能宣稱它沒有transitive escape。其餘未明示設定的參數不假定為零。

## Selector：strict unsigned最小回覆與SP+12

best初始化為`ffffffff`。每個node都請求同一query：

```text
RAM 0x20001122(current node, SP+12)
```

本機全函式沒有對SP+12的直接初始化store。query正常回覆R後：

- R=0立即走特殊路徑，略過min／next／Out stores。以`0x20000d50` literal呼叫既有22-byte setter `0x2000078a`，再寫U8[I+4]=8、向fresh U32[0x2000353c／0x2000358c]所指物件+100寫word2，返回3。最後的pointed store沒有null guard；不是實體狀態或callback已執行證明。
- R非零且unsigned R<best：捕獲U32[SP+12]為X，更新best=R。
- 其他非零R：不讀SP+12到X；相同回覆保留第一次擷取的X，`ffffffff`不會被選中。

然後才fresh讀current node+0的next，非零繼續。query可能改變node／list，保存node pointer的數值不證明返回後仍可讀。沒有cycle guard、visit count或整體終止bound。

若有限遍歷正常結束且全部非零回覆都是`ffffffff`，best仍是sentinel，返回255，不做本機Out stores。若有被選中的R，其數值在1..`fffffffe`；X卻是**相應query的SP+12輸出**，不是R本身。SP+12的初始化／有效內容與query保存合約仍需另證。

## Out與B+176可能不同

有選取結果時，使用擷取的X計算：

```text
X >= 5：Y = X - 5
X < 5 ：Y = low32(fresh U32[0x20003238／0x20003288] - 5 + X)
```

先透過保存的Out寫word Y，再寫U32[B+176]=Y，設status0。若**計算暫存器中的Y**為零，才重新讀一次上述global word，僅覆寫Out，沒有再寫B+176。即使X=5也會走這個fresh覆寫。

所以在非alias與所需保存條件下，Out最後可能是fresh global word，B+176仍是0；不能把它們當成一份原子／永遠相等的結果。B+176存的是scalar Y，不是Out pointer。Out至少需要四-byte可寫範圍；alias、外部writers與callee副作用仍可能影響真實最後值。

四種本機status為2、3、255、0，從A4搬入A0後恢復frame；status0僅表示到達對應本機輸出路徑，沒有替代query內容／Out有效性或後續完成證明。

## 接回record handler與清理條件

重驗[完整268-byte record producer](v4160-record-producer-static.zh-TW.md)及[完整130-byte kind0 handler](v4160-builtin-record-handlers-static.zh-TW.md)。若實際arena／index／物件／code binding與保存條件相符，producer可將literal`0x2000138e`及W分別寫入record+0／+4；handler之後從record+0載入callback，以fresh U32[record+4]作A0，便能條件性接到這個record callback。

handler不採用callback的scalar A0回覆。正常返回後，**fresh record+8 metadata為零**才清record+0／+4；record+8本身沒有在這裡一併清掉。這不是依callback成功／失敗做清理，也不能把清record words當成釋放W或非同步工作已結束。

候選producer、node consumer、event dispatch與handler仍需實際同一arena／node／slot及執行順序才能完整串接。其他callback、query、cleanup可能改變metadata或物件；本階段沒有建立整體ownership／消費／釋放生命期。

## 重播與後續界線

```powershell
python analysis/check_v4160_b1_ram_record_callback_static.py
python -O analysis/check_v4160_b1_ram_record_callback_static.py
```

兩模式均核對完整祖先證據鏈、strict HEX及固定ledger。每版本record有38條CFG邊／6條選定語法路徑，select有86條邊／8條路徑；226個逐指令變異、14個typed-load變異必須拒絕。

封閉整數檢查包含256 bytes×三個mode樣本、七個reply boundary值的49組strict-min predicates，以及所有X=0..65535×四個補償word樣本的262144組公式；沒有重播可變list、query、frame、clock或全部U32×U32狀態。

後續重點是RAM `0x20001122` 的完整query／SP+12輸出與保存合約、`0x436a8／0x43734`及兩個optional前置callee、實際MEPC／slot／record路由與釋放順序，另有`0x5d006／0x5d14e`及其餘巢狀服務尚待展開。
