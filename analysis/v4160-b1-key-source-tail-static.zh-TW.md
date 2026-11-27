# B1 key 建立來源與提交尾跳：鏈表、保存與返回界線

接續[key producer／submit](v4160-b1-key-submit-static.zh-TW.md)，完整展開其上游來源與尾跳目標，新增 **712 bytes／228 條指令**。確認 key 來源請求配置488 bytes，實際回覆是稍後fresh讀取的U16 ID；提交尾跳的一條路徑會把原W指標交給既有record producer，條件性存入record+4。

[Python checker](check_v4160_b1_key_source_tail_static.py)與[固定 JSON ledger](v4160-b1-key-source-tail-static.json)保存完整原指令、hashes、CFG、所有store及邊／路徑證書。全程離線讀取APP／carrier／嚴格sparse HEX，檢查不可變圖與封閉host整數關係；沒有目標執行、模擬、可變registry／heap／clock模型、packet replay、硬體或目標網路分析。既有C重建覆蓋率不變。

## 完整範圍

| 函式 | V131 | V140 | 每版bytes／指令 |
|---|---|---|---|
| key source | `[0x57962,0x57a1e)` | `[0x57aa2,0x57b5e)` | 188／64 |
| submit tail | `[0x56716,0x567be)` | `[0x56856,0x568fe)` | 168／50 |

source首次RET後還有空鏈表、追加及候選ID遞增分支；tail首次RET後還有frameless分支與單次補償塊。完整範圍包含這些可達原指令。每版source有14個store sites、4個linked calls；tail有7個store sites、1個linked call、1個不改link的外部tail。

## 配置與清零在null檢查之前

source使用16-byte frame，保存RA／S0／S1，依序明示請求：

```text
P = RAM 0x20000040(A0=488,A1=611)
保存 P
RAM 0x2000039c(P,0,488)
然後才檢查保存的 P 是否為零
```

其餘未明示重設的參數保留then-live界線。完整208-byte allocation core、46-byte fill及212-byte release均重新核對逐指令／hash／strict HEX與startup first-copy來源涵蓋；這是reference綁定證據，不是實際installed provider或heap配置成功證明。

matching fill會先保存／清零固定控制word並FENCE.I，再檢查pointer／count；P=0時略過payload stores，但仍有控制word前後動作。非空且有效488-byte可寫範圍、正常完成、無不利alias／干擾及matching code等前提下，才可將這次fill解讀為488 bytes清零。source忽略fill回覆，持續使用S0保存的原P。

P=0時，source在fill正常返回後明示返回0，尚未讀registry head。配置請求大小與fill長度不替代真實extent／ownership／保存期證明。

## 候選ID：衝突後從捕獲的head重新掃描

令B為`0x200033b8／0x20003408`。P非空時只讀一次U32[B+156]作為head H。

H為零的分支：

1. U16[P+8]=1。
2. B+156=head與B+160=tail都寫P；U16[B+180]=1。
3. 呼叫`0x578a4／0x579e4`。這裡A0仍是先前設定的**0，不是P**；不能替未知helper假定物件參數。
4. 與追加分支會合，重新讀B+160，向fresh tail+0寫零，另清P+10與P+14 bytes。

H非零時，candidate從1開始：fresh讀目前node+8的U16，若不同就沿fresh node+0的next前進；相同則candidate加1、取低16位，並從**原先捕獲的H**重新掃描，不重新讀B+156，也不是從剛才node的next繼續。

候選遞增到`0x8000`時，SLLI16後signed檢查不再通過，改走耗盡分支。因而實際嘗試的candidate範圍為1..32767；最多32767次候選遞增即可跨越界線。這不是node visits或整個函式的返回bound：未知鏈表可能有環、無效node或持續變化的內容，某次候選掃描本身可能不結束。

找到未衝突的非零candidate時，先寫P+8，再把P寫到fresh B+160所指tail的next，更新B+160=P，並將fresh U16[B+180]加1後寫低16位。沒有tail null guard，count也可從65535回繞為零。這些本機stores不能獨立建立實際鏈表長度、無環、ID唯一性或原子發布。

會合處重新讀tail後清next；若空鏈表helper改了B+160，就不能直接把這個next-store等同於P+0。任何全物件初始化或鏈表一致性結論都需額外的callee／alias／保存條件。

## 耗盡後的讀取與真正回覆

耗盡分支先U16[P+8]=0，然後請求`RAM 0x20000110(P)`。**正常返回後仍fresh讀U16[P+8]，作為source回覆。**

這個讀取位於釋放請求之後。S0保存了P的數值，不代表P指向的物件仍有效；不能直接宣稱成功free、已確認的釋放後使用，或無條件返回零。仍需實際allocator／release綁定、ownership、release副作用、存取有效及保存條件。

成功追加／空鏈表分支最終也fresh讀P+8，因此回覆不是P，也不自動等於先前candidate。上層key producer捕獲這個回覆後還會lookup、配置另一塊buffer及可能清理；它的返回不能證明最初P仍存活或較後lookup得到同一node。

## Tail的flag非零分支：有frame，使用fresh slot

令D=`0x20003234／0x20003284`，SLOT=`0x200034ec／0x2000353c`。tail先讀U8[D+12]。

flag非零時才建立16-byte frame並保存RA。先捕獲SLOT word；若該值為零，將fresh U32[D+4]寫B+176，並向SLOT發布literal **`0x200013e8`**。然後不論先前slot是否為零，都重新讀SLOT作為A0，清U32[B+164]，呼叫`0x43ed2／0x43f5e`，其他參數仍是then-live值。

helper正常返回後，向數值位址`0xe000e204`寫word `0x02000000`，恢復16-byte frame並RET，沒有再定義A0。回覆是當時helper留下的A0，不是固定status。這些數值stores與literal publication沒有單獨證明實體排程、callback執行或SLOT當時內容的型別／有效性。

此分支本機不以入口W解參考；未知helper是否觀察其他暫存器、保存pointer或正常返回，仍未封閉。SLOT也不能僅因數值相似就與其他RF欄位混為一談。

## Tail的flag零分支：無frame與32-bit回繞

flag為零時不改SP／RA。原順序是先捕獲k=U16[D+8]，清B+164，再捕獲h=U16[W+134]並保存入口W，然後清SLOT。其後獨立讀取t=U32[W+144]及fresh byte c=`U8[0x20003203／0x20003253]`，形成：

```text
q = floor(low32(h*k + 999999) / 1000000)
deadline = q + c
若 unsigned t < deadline：adjusted = low32(t + fresh U32[D+4])
否則：adjusted = t
delay = low32(adjusted - deadline)
```

兩個U16的乘積雖可放入U32，**再加999999可能回繞**。product從4,293,967,297起發生此事，不能無條件改寫成數學ceil(product/1000000)。例如65535×65535的數學ceil是4295，原指令回繞後q卻為0。

q範圍0..4294，加byte後deadline在0..4549內，不會再因這次加法overflow。但原指令只在`t<deadline`時補加一次D+4，沒有重試／再次比較；補償後仍可能不足或回繞，delay可以成為很大的U32。沒有實際clock、時間單位、合理等待時間或進展保證。

本機對W的固定存取最少需148-byte範圍；這是存取需求，未證明真實物件大小或後續callee需求。

## 接入record producer後，W會被條件性保存

frameless分支最後準備五個明示實參，尾跳既有[完整268-byte record producer](v4160-record-producer-static.zh-TW.md)：

```text
A0 = 0x2000138e
A1 = 原入口 W
A2 = delay
A3 = W+41
A4 = fresh U32[W+140]
tail 0x43414／0x434a0 （不產生新link）
```

這個callback參數literal是**`0x2000138e`，不同於flag非零分支發布的`0x200013e8`**；兩者的實際RAM內容／來源／消費仍需追查。

matching producer若走到對應成功寫入路徑並正常返回status0，在所需arena／node／callee／extent／alias與保存前提下，會將callback、**W指標**、metadata分別寫至record+0、+4、+8；node+8保存entry A2 delay，並可透過A3將索引byte寫回W+41。producer也有控制word動作、配置／failure hook、fresh arena重讀與無界node鏈表路徑。

因此已有明確的條件性pointer保存來源，不能宣稱W只在這次呼叫期間借用或沒有escape。成功status亦不是callback已消費、event送達或安全釋放證明；record實際消費、移除、W ownership與完整保存期仍待串接。

## 重播與剩餘工作

```powershell
python analysis/check_v4160_b1_key_source_tail_static.py
python -O analysis/check_v4160_b1_key_source_tail_static.py
```

兩模式核對完整祖先證據鏈、strict HEX、固定ledger。每版source的69條CFG邊、tail的51條邊及各10條選定語法路徑均有證書；語法路徑不等於可行執行。228個逐指令變異與20個typed-load變異必須拒絕。

另核對32767個candidate transitions、65536個count increments，以及全部U16 h乘上k樣本0／1／65535的196608組封閉整數關係與全域界線；沒有遍歷或重播可變鏈表、heap、clock或全部U16×U16狀態。

後續需展開首節點helper`0x578a4／0x579e4`、RAM literals `0x2000138e／0x200013e8`、record消費／MEPC／scheduler路由，以及`0x5d006／0x5d14e`與其他巢狀服務，確認實際provider、來源／物件extent、釋放順序及完整保存期。
