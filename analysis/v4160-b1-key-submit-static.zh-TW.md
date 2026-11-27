# B1 key producer 與提交服務的完整靜態合約

接續[record parser](v4160-b1-record-parse-static.zh-TW.md)，本階段完整展開 key producer 與提交服務，共 **1,344 bytes／424 條指令**。確認 key producer 的回覆不是配置 pointer，也不是可靠成功旗標；提交服務會發布物件 pointer，最後恢復 frame 並尾跳，沒有自己的正常 RET。

[Python checker](check_v4160_b1_key_submit_static.py) 與[固定 JSON ledger](v4160-b1-key-submit-static.json) 記錄原始 hashes、完整 operands、CFG、所有 store、每條 CFG 邊及選定語法路徑。全程離線讀取原始 APP／carrier／嚴格 sparse HEX，只核對不可變圖與封閉 host 整數關係。沒有目標執行或模擬、可變 heap／list／callback 模型、packet replay、硬體或目標網路分析；C 重建覆蓋率不變。

## 完整範圍與邊界

| 函式 | V131 | V140 | 每版本 bytes／指令 |
|---|---|---|---|
| submit | `[0x59d3e,0x59e3e)` | `[0x59e86,0x59f86)` | 256／84 |
| key producer | `[0x59e64,0x5a004)` | `[0x59fac,0x5a14c)` | 416／128 |

key 的首次 RET 在 +0x8a，後面的成功分支及 +0x19c lookup-null 分支仍回到共同 epilogue。完整本體到 +0x19e；+0x1a0 已是下一函式的 16-byte frame prologue，另核對相鄰原 bytes 並排除。不能在首次 RET 截斷，也不能把下一函式算入。

兩函式 local CFG 無環；submit 每版有 15 個 store sites、8 個 linked call sites及1個無新 link 的 tail；key 每版有39個 store sites、6個 linked call sites及1個RET。無環僅屬本機圖，不保證 callees／lookup 鏈表／尾跳目標返回。

## Key 回覆：保留上游值，查找失敗時改成 1

key producer 使用32-byte frame，保存 RA、S0..S3。先呼叫 `0x57962／0x57aa2`，將完整 A0 回覆捕獲為 K：

- K=0：立即恢復 frame，返回0。
- K 非零：以完整 K 呼叫[24-byte lookup](v4160-constructor-consumer-tail-static.zh-TW.md)。lookup 沒有配置指令，沿 node+0 的 next 遍歷，以 U16[node+8] 比較完整入口 key。
- lookup 回覆為零：把保存的 K 改為1，再共同返回1。
- lookup 回覆為非零 W：進入後續配置／欄位流程，正常返回仍使用原 K。

所以原 K=1 與 lookup-miss 產生的1無法只靠回覆區分。來源服務 `0x57962／0x57aa2` 的完整語意仍未展開；其輸入為 then-live registers，不能因它返回 key 就反推固定 ABI。

## W+272 是另一塊配置的 pointer

W 非零後先寫 U16[W+10]=16、U8[W+14]=176、U8[W+16]=1。接著從固定 F+16 讀 U16 h，配置請求為：

```text
r = low16(h + 5)
size = clamp(r,64,260)
RAM 0x20000040(size,589)
```

F 為 `0x200031ec／0x2000323c`。配置呼叫明示設定A0／A1，其餘暫存器保留then-live界線，沒有假定為零。原指令先對 h+5 的低16位做上界比較，後面再取低16位；因此 h=65531..65535 時會回繞為0..4，最後請求64，不能把它寫成無回繞的 clamp(h+5)。所有65,536個 h 都已核對請求範圍64..260。

重用完整208-byte allocation core，逐指令及 strict HEX 核對 first-copy 來源。但它的實際 heap、fallback、物件大小與 installed binding 仍有條件；呼叫串接不是成功配置證明。

配置回覆 P **先寫入 W+272，再檢查 null**。P=0 時，fresh讀 U16[W+8]，呼叫[清理／移除服務](v4160-task5-removal-static.zh-TW.md) `0x57a4a／0x57b8a`，忽略其回覆，最後仍返回原 K。這個清理服務可能移除／請求釋放 matching node，不能把原 K 正常返回解讀為原 W 仍存活。

W 自身的明示存取最遠到 byte+398，需399-byte有效範圍；64..260是另一塊 P 的請求大小，不能用它證明 W 的 extent。

## 配置非零路徑的欄位來源與部分更新

令 B=`0x200033b8／0x20003408`。P 非零後可見下列 W 更新；完整寫入順序與 operands 在帳本中：

| W位置 | 本機來源／操作 |
|---|---|
| +276 word | fresh固定global word（G+1336／1416） |
| +252、+248 words | fresh B+220、B+216；fresh B+1=0時另清W+248的bits6/7 |
| +268、+264 words | 稍後重新讀W+252／W+248，再分別寫入 |
| +326 halfword | 0，同時涵蓋bytes326／327 |
| +324 halfword、+361 byte | fresh B+58、B+74 |
| +46 byte | fresh舊byte OR `0xc1` |
| +164 word | 先OR64；擷取B+208 bit25設置時，用較舊W+164觀察值OR80再寫；fresh B+82非零時再fresh讀、OR `0x00400000` |
| +64、+38 halfwords／+40 byte | `ffff`／`ffff`／`ff` |
| +74 halfword | 3000 |
| +322 byte | fresh F+20，亦為後續`0x63966／0x63a50`的明示A0 |
| +391／+389 bytes、+376 halfword、+378 byte、+380 halfword | 20／40／1776／127／`ceba`（最後一值為hex） |
| +323、+384..387 bytes | 上述`0x63966／0x63a50`同一次回覆的低8位 |
| +398 byte | fresh W+252 bit7設置時寫1；未設置不在此處清零 |

本機還呼叫 `0x560aa／0x561ea(W)`；最後清 U16[B+8]。未知 callees／alias／writers 可能影響欄位、pointer與frame，不能把此清單視為整個 W 初始化、完整 transactional 更新或持續 invariant。

## Submit：兩次獨立來源取樣與算術

submit 使用32-byte frame，保存 RA、S0..S4。入口 W 沒有本機 null／extent guard。Kslot 是固定 `0x2000323c／0x2000328c`，不是上面的 scalar key K。

依原指令順序：

1. fresh U8[B+3] 寫 W+47。
2. 捕獲第一組 U16[W+58]與U16[Kslot]，其乘積最大4,294,836,225，仍在U32內。W+140 word寫入 unsigned floor(product/800)，最大5,368,545。
3. 以 `(300*capturedU16Kslot,0,1000000,0)` 呼叫算術 helper `0x6df1a／0x6e10a`，實際 A0 回覆低16位寫 W+132。本階段僅固定此實參域，沒有將既有另一個config域的quotient證明直接套用。
4. 呼叫 `0x56326／0x56466(W)` 後，重新讀第二組 Kslot與W+58，不能沿用第一組值。
5. 第二組 product先REMU800，再乘1250，然後以 **signed DIV** 除以第二個U16 Kslot，低16位寫 W+32。numerator範圍0..998750，非零Kslot為正數。Kslot=0沒有guard；RV32 DIV語意返回−1，SH成為`ffff`，不自行宣稱fault或飽和處理。
6. fresh U16[W+132]乘2後寫低16位至W+130，可能截斷。

此後依序請求 `0x55d3c／0x55e7c(W)`、`0x5605c／0x5619c(W)`、`0x55d00／0x55e40(W,low16(16*freshU16[W+62]-2))`、`0x57b28／0x57c68(W)`。其餘未明示重設的參數保留then-live界線；沒有把回覆當成成功gate。

## Pointer發布、兩次callback與恢復frame後的尾跳

submit寫U8[W+309]=24，讀取fresh固定global word的bit1，並在分流前明示寫 **U32[B+168]=W**。這是pointer保存來源，不能宣稱沒有escape或submit返回後W可立即釋放。

當global bit1設置，且第一次fresh U32[F+52]非零時：

```text
callback1(A0=13,A1=fresh U32[W+152])
重新讀 F+52
callback2(A0=14,A1=fresh U32[W+156])
```

第二次讀出的pointer沒有再次null檢查；第一次callback正常返回不能證明兩次綁定相同、第二次非零或仍有效。兩個回覆均不作成功gate。callback可否保留參數、修改全域／W、重入或普通返回仍未封閉。

兩條路徑會合後，設A0為保存的W，清U16[B+14]與U32[B+16]，恢復全部保存暫存器與32-byte frame，再以**無新link的tail jump**進入`0x56716／0x56856`。submit沒有本機RET，也沒有固定scalar回覆；外層能否正常繼續取決於tail與整條callee鏈。

submit本機固定W存取至少需310 bytes，未知callees與tail的額外extent不包含在此界線。W的全域保存、callback、tail與更後續消費／釋放仍需追查。

## 接回 parser 時，不能合併兩次lookup

parser呼叫key producer之後，會以其完整回覆再做一次lookup。兩次lookup使用相同reference本體，卻是不同時點；key producer可能配置失敗並呼叫移除，lookup鏈表與物件內容也可能改變。因此尚不能證明兩次得到同一W、仍有效或完整保留欄位。

若另證明是同一物件且保存／順序成立，key producer先以SH0清W+326/327，parser稍後才以同一次N+128 byte寫這兩個位置。這只是一個條件性writer順序，不能將較早零值當成parser後續欄位值。

## 重播與剩餘工作

```powershell
python analysis/check_v4160_b1_key_submit_static.py
python -O analysis/check_v4160_b1_key_submit_static.py
```

兩模式都保留完整祖先證據鏈、strict HEX及固定帳本。host import鏈加深後，入口將Python recursion limit提高至至少3000，沒有跳過祖先檢查。每版本submit有85條CFG邊／3條選定語法路徑，key有136條邊／7條路徑；424個逐指令變異與44個typed-load變異必須拒絕。另有65,536個clamp來源、800個remainder、262,144組「四個H樣本×全部Kslot」整數檢查，並明示sample family，沒有冒稱遍歷全部U16×U16。

後續仍需展開上游key來源`0x57962／0x57aa2`、submit尾跳`0x56716／0x56856`、巢狀helpers、callback-slot writers及`0x5d006／0x5d14e`，釐清實際provider綁定、物件extent／ownership、訊息消費／釋放與完整指標保存期。
