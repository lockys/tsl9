# v4.1.60：record 與 node 的不同生命週期

本階段重用兩版完整 producer268B、consumer288B、event helper64B、kind0 handler130B 與 private release212B，新增配置／釋放及清除時序的條件性合約。**新增原指令 bytes=0，C 重建覆蓋率不變**；[ledger](v4160-record-node-lifecycle-static.json) 保留本體身分、selected walks、intervals 及前提。

全程離線讀取原 bytes、檢查圖、不可變區間與 scalar equations。沒有執行或模擬 target ISA、callback、synthetic heap／list／record memory、allocator、event scheduler、MMIO 或裝置。

## 先區分16-byte node與12-byte record

producer `43414/434a0` 使用兩個不同物件：

- Q：向 `20000040` 請求配置的16-byte鏈表節點。
- record：位於 fresh arena pointer 所指的 `P+12*i`，i∈0..15；不是 Q 本身。

在 saved inputs 保持下，producer 形成：

| 欄位 | 寫入值 |
|---|---|
| Q+0 byte | 0（event task ID） |
| Q+2 halfword | `1<<i` |
| Q+4 word | entry A4 |
| Q+8 word | entry A2 |
| Q+12 word | 0（next） |
| record+0 word | entry A0 callback |
| record+4 word | entry A1 argument |
| record+8 word | entry A4 |

Q+1 byte 沒有由此 producer 直接初始化。entry A0 在這裡是 callback word，只要求非零，不是 task ID，也沒有驗證 function pointer 身分。

list link 在 node／record fields 完整初始化前就發布。初次檢查 arena callback 是否為零與後續寫入使用不同的 P snapshots，沒有 reservation 或重新檢查 empty slot；因此同一 record 的串接仍需 P／P′、index、fields、heap及frame保持、無干擾 writers／reentry 等條件。

本次16條選定 producer walks 都假設先前 i 個 callback words 非零、第i個為零、配置成功、原 node list為空、optional index-output pointer A3=0。這些是圖與地址合約，不是實機可達性或原子配置證明。

## Small-block split／release 的選定還原

採用額外 fresh heap 前提：small-head 全域 word=A=`200043ac`、large-head 全域 word=B=`200045ac`、end／sentinel 全域 word=E=`2000b184`，A 的原 size504、tag0、next=B。三個全域值都須保持，沒有推定先前 timer／其他配置之後仍維持這個狀態。ledger 分別列出兩版的槽位地址及條件值。

matching core 的 request16、tag`ff00` 產生 Q=A+8=`200043b4`，remainder header R=A+24=`200043c4`，其 size480、tag0、next B。區間關係為：

```text
原 payload504 = 已配置16 + remainder header8 + free payload480
Q+[0,16) 結束於 R，沒有碰到 arena P=200045b4
```

若這些 owner／heap globals／links／tags／sizes 與 accounting 關係保持，並以 exact owned payload Q 呼叫 matching private release `20000110`，選定路徑會：

1. 把 A+6 的 tag 清零。`ff00 != 8001`，不走特殊 counter increment。
2. accounting 加回16。
3. 發現後繼 R 為free，合併為 A.size=16+8+480=504、A.next=B，accounting 再加8。

配置時 accounting 減24，釋放時加16+8，在16-bit accounting 範圍內還原。checker 分別核對65,511個可 split sizes、65,536個 accounting words；不是建立或執行 synthetic heap。

global 值也決定原 branch：配置時 A!=E，release 的 A<E bound 通過，下一個 R 不等於 E 或 large-head B，才會檢查 R.tag並進入這次 forward merge。只保留 A／R 的 header，無法替這些 global reads提供前提。

這條 release 的 heap stores 落在 A+0／4／6 及獨立 accounting word，**不清除 Q 的16-byte payload，也不清 arena record**。payload bytes 可能還在，但不能由此推論釋放後仍有所有權、指標有效或不會被下一次配置重用。

private release 的一般 range guard 並不是精確 ownership checker；這個還原只套在上述 exact-Q／header 前提。consumer 使用的是 `20000110`，不是帶 message marker 檢查的 SDK deallocate wrapper，不能隨意互換兩個 API。

## Consumer 先提出事件，再決定 node 留下或釋放

完整 RAM consumer `200004fa` 的三條選定路徑為：

- mask+2=0：直接 unlink，請求 private release，沒有 event helper 呼叫。
- 到期且 fresh Q+4=0：呼叫 event helper，然後 unlink／請求 private release。
- 到期且 fresh Q+4 非零：保留 Q，更新 deadline+8，繼續遍歷。

此處「到期」只指原整數比較條件成立，本次選定 nonwrap 路徑還要求 clock reply>=原 deadline、差值<=29999999；不指定物理時間單位。

consumer 在 release 前先更新 head／predecessor link，另 fresh 讀 Q+12 到 S8，再以 A0=Q 呼叫 private release。完整212-byte release 本體沒有 calls、frame 或 S／SP／RA writes，因此本機不改這個 S8。單節點退出路徑在返回後以 S8繼續，沒有再解參考原 Q。

兩次 next reads 的值不是無條件相等；必須保留 links／objects、frame、code與alias前提。self-loop、已釋放的 next、其他 writers 或無效 header 都不能由這個局部保存性質排除。

## Event helper 拒絕也不阻止 one-shot node 的 release

event helper 使用 task=`U8[Q+0]`、mask=`U16[Q+2]`。若 task<fresh task-count，OR mask 進 event halfword並返回0；拒絕時返回3。

consumer 沒有依這個 A0 回覆決定 retain／release，而是重新讀 Q+4。故在 Q+4=0、其餘存取及 release 前提成立時，**提出事件被拒絕也會走 unlink／release 路徑**。這個路徑不清 arena record，不能以「node已釋放」推論 callback已送達或record已空。

mask0 路徑也沒有 arena-clear store。即使沒有從此 node 新增 pending bit，仍可能有舊 pending bit 或其他 dispatch，因此也不能推論該 record callback 永不會再被呼叫。

這些是原控制流的條件性反例，沒有宣稱特定 task-count／取消時序已在裝置發生。

## 後續 kind0 handler 才處理 arena callback

kind0 handler 先找 event word 低16位的第一個 set bit。對 entry group0、single-bit event=`1<<i`，才會選到與 producer 的 `P+12*i` 相同位置；多個 pending bits、其他 group或不同 P snapshots 不直接套用此結論。

它先讀 selected record+0，非零時以 fresh record+4 作 A0 呼叫 callback，完整事件 word在A1，其他 ambient arguments仍可被觀察。callback 的 scalar A0 回覆不決定後續清除。

正常 callback 返回後，handler 以另一個 fresh arena base讀 `P′+12*i+8`。這個 flag address **沒有 group term**，所以非零group還需額外分析；本次只證 group0。

若 fresh flag=0，且 callback 保持必要 S／SP／frame／saved-event／record 身分，它清除原 selected record 的 word0和word4；word8沒有清除，也沒有 free Q、arena或argument payload的呼叫。非零flag時，record callback與argument可以保留，但事件bit仍按原XOR返回式處理。

因此 callback 正常返回、callback metadata保持0及arena保持等，都是「record後來被清掉」的必要條件；無法從consumer或producer的正常status替它們保證。

## One-shot 串接與不同生命週期

entry A4=0 會同時初始化 Q+4=0與record+8=0。若兩個欄位保持、相應selected paths正常完成、event實際被dispatch給kind0(group0)且callback遵守所需保存條件，才可串為：

```text
producer：建立 Q，寫入 arena record
consumer：提出 pending event，unlink／release Q
後續 handler：執行 record callback，再清 record+0／4
```

這些是分開的入口，不是同步的完整執行pipeline。consumer 不直接呼叫 arena record callback；handler 的實際時機、綁定與正常返回仍未知。

在此串接中，Q 可以早於 record callback 的執行被釋放；record 清除也不釋放 callback argument 所代表的記憶體。argument只是保存的word，其所有權、有效期、與Q／arena的關係必須另外證明。

entry A4非零的情況，node repeat 與handler record-retention各自重新讀取fullword，不是同一個原子判斷。取消node、改metadata、callback reentry 或arena改址，都可能讓兩個生命週期分離。

## 其他 fallback consumer 的零值分支

producer 與 core 使用同一個 `20003220/20003270` fallback word。core失敗的非零hook參數為 `(1,0010ff00,...)`，producer失敗後另 fresh 讀取並可呼叫 `(4,0,...)`，不能推論必定呼叫兩次或ABI相同。

沿用 [clock191c6／fallback0證據](v4160-timer-provider-closure-static.zh-TW.md)，在matching reader、retained zero、frame／control／heap／arena分離及無外部干擾前提下，兩個hook都不可達；producer failure11路徑沒有 node／record stores。producer0則代表本機初始化及record writes正常完成，不代表事件送達。

另一條 RAM threshold exit 使用 `(5,2)` 的 unlinked tail，前面還有其他callee；不能直接套用此零值保存結論。其 helper `568f6/56a36` 是後續待核對的具體範圍。

## 重播

[Checker](check_v4160_record_node_lifecycle_static.py) 核對102個指定 instruction mutations、65,511組 split sizes、65,536組 accounting words及16個 group0 single-bit cases；兩版共32條producer、32條handler、6條consumer、4條event walks。所有圖與區間為靜態證據，不是實際schedule或heap執行。

```powershell
& 'C:\Users\locky\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe' analysis/check_v4160_record_node_lifecycle_static.py
& 'C:\Users\locky\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe' -O analysis/check_v4160_record_node_lifecycle_static.py
```

一般／`-O` 均須精確重播ledger。仍需核對 threshold helper、實際 outer dispatch／APP callback、其他 global／arena／heap writers與生命週期；本次不是全binary writer清單或無條件ownership證明。
