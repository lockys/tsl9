# v4.1.60：constructor 消費端與映射 RAM tail

本階段完成較小 B+132 consumer、其直接 caller、lookup，以及前一輪 RAM tail 的完整原始指令證據。新增 **1,080 bytes／402 條指令**；未重算既有 constructor、publisher、startup、common body 或 C 重建覆蓋率。

| 完整本體 | V1.31 entry | V1.40 entry | 每版 bytes／指令數 |
|---|---|---|---|
| B+132 consumer | `6a2a8` | `6a3c0` | 222／80 |
| 直接 caller | `679a2` | `67ae0` | 44／19 |
| lookup | `5784a` | `5798a` | 24／9 |
| 映射 RAM tail | `200026ba` | `20002706` | 250／93 |

範圍尾端、完整 SHA-256、逐條欄位、CFG、stores／calls 與路徑見 [機器可讀證據](v4160-constructor-consumer-tail-static.json)。全程離線讀取原始檔、解碼、檢查控制圖與整數域；沒有執行或模擬目標 ISA、allocator、copy、provider、polling、FENCE.I、MMIO 或裝置。resident 參考候選及 startup 映射不代表實際 installed RAM 身分。

## 消費端保留舊 outer-pointer 快照

B=`200033b8/20003408`。consumer 的 frame32 保存 RA、S0～S6；先保存 entry A1～A4，再以原 A0 呼叫 lookup。lookup 返回後，**先讀 fresh `U32[B+128]` 到 S0**，才檢查 lookup 回覆是否為零；零時本機返回 2。

lookup 非零回覆保存成 R=S2，接著讀 B+132 的 constructor function word：

1. 初次 function word 為零時，呼叫已驗證 publisher `60856/60940`；它可能執行 handler registration 與完整 setup。
2. 之後仍以先前 S0 的 **舊 outer-pointer snapshot** 決定是否配置，沒有重新讀 B+128。
3. 舊 snapshot 非零：跳過 constructor 與新物件 copy 區段，使用保存的舊 N。
4. 舊 snapshot 為零：fresh 重讀 B+132，**沒有再次 null guard** 就 JALR；回覆保存為 N=S0。回覆為零時本機返回 3。

沿用 [outer／publisher 證據](v4160-list-outer-objects-static.zh-TW.md)，若匹配的 publication 值保存到這次 fresh read，目標才是 `5e8bc/5e9a6`。早先的非零檢查不保證後來重讀仍有效，setup 也可能改變實際 outer slot；舊 snapshot 的分支與實際全域值必須分開。

間接呼叫時 A0 在跳過 publisher 的路徑仍是 lookup 回覆；執行 publisher 的路徑則繼承它的回覆。沒有為 A1～A7 建立固定 constructor 參數組；已知 reference constructor 自行重設 allocation 請求參數，不能反向推定所有被載入的函式都採相同合約。

## 新物件 copy 與共同寫入

只對新配置的非零 N 執行 copy 分支：fresh `U8[N+77]` bit0 清除時，來源為 B+232；設置時則檢查 fresh **`U8[B+2]`**，為零返回 18，非零選 B+238。兩條請求都是 RAM `20000332(N+78,來源,6)`。

若另有 matching zero-fill232、有效且不重疊的 N／frame／globals／table、必要 callee 保存與無干擾前提，既有 constructor 的 explicit stores 都不碰 N+77，可條件性推出其返回時 N+77=0，選 B+232 分支。這仍不是實際 provider 或真實可達狀態證明。

舊 N 路徑跳過上述 copy，直接與新 N 路徑在 word N+28 的分支會合。共同區段的本機 stores 是：

| 位置 | 寫入值 |
|---|---|
| N+125 byte | `ff` |
| N+132 halfword | entry A2 低16位 |
| N+134 halfword | entry A3 低16位 |
| N+131 byte | entry A4 低8位 |
| lookup record R+334 byte | entry A1 低8位 |

接著呼叫 `63578/63662`，其 A0 沒有重新設成 N，而是繼承前序值／callee 回覆；正常返回後本機明確把 A0 設為 0。這不是 callee 成功判定。N 的固定存取至少需要 136 bytes，R 至少需要 335 bytes；最後 callee 是否保存剛寫的欄位及物件存活期仍未知。

## 編碼存在，但入口條件無解的取消區段

完整 raw CFG 保留所有原始指令；另外用 16 個 low4 patterns 證明下列兩個條件無共同解：

```text
x = 同一次 fresh U32[N+28]
先要求 (x & 2) != 0
再要求 (x & 14) == 8
```

兩次 AND 使用相同 A5，期間沒有 call 或 A5 重新定義。bit1 已設置時，`x&14` 必定仍含 bit1，無法等於 8。因此在普通 decoded GPR 語義、由本函式入口進入的條件下，`6a328..6a340`／`6a440..6a458` 的取消區段不可達。

這個區段包含 N+28 mask clear、N+124 清零與 `43a14/43aa0` 呼叫。它們仍存在於完整位元組與語法控制圖，不能當作入口路徑的可行副作用。分析沒有排除其他外部 mid-function entry、故障或 runtime patch。

可行的本機入口分流是 word bit1 清除就直接共同 stores；設置就先呼叫 `5f96c/5fa56` 再共同 stores。該 helper 的 A0 同樣沒有固定重設為 N。語法 walks 不等同可行執行，pruned-edge 與排除節點清單另存於 ledger。

## Lookup 與 caller 返回合約

lookup 從 B+156 取 head，依 node+0 的 next word 遍歷，以 **unsigned halfword node+8** 比較完整 entry A0。它沒有截斷 entry key；high16 非零時不可能匹配 U16，但返回零仍需實際走到 null。沒有 frame、store 或 nested call；node 有效範圍至少 10 bytes，鏈表界限、無環與有限返回尚未證明。

直接 caller 保留原 entry A0，呼叫 consumer 後建立三個 frame bytes：SP+12=consumer 回覆低8位、SP+13=原 entry A0 低8位、SP+14=原 entry A0 的 bits8..15。然後請求：

```text
6a70c / 6a8f0 (A0=205c hex, A1=3, A2=SP+12)
```

V1.40 此服務目標差 484，不能套用 caller 的 +318 或 consumer 的 +280 位址差。caller 最後返回 **callee 之後重新讀取的 `U8[SP+12]`**；只有 callee 保存該 byte，才等於先前 consumer status。沒有假定 callee 不保留 SP 指標。

consumer 本機 status 值為 0／2／3／18，不能無條件把 caller 的返回值或真實作業成功與之畫上等號。

## RAM tail 的來源是 startup 映射

本階段重播既有 `binding.profile()` 的候選 startup operands 與 copy-helper 合約，核對整個 tail 都在 first-copy 區間中：

| 候選 | first-copy 來源→目的 | inclusive last | RAM tail 對應 FLASH 範圍 |
|---|---|---|---|
| V1.31 | `402b0 → 20000040` | `20002e70` | `4292a..42a24` |
| V1.40 | `402f0 → 20000040` | `20002ebc` | `429b6..42ab0` |

250 bytes 在 **RAM entry PC** 解碼；其中 AUIPC／JALR 正確解析為 FLASH `63b0e/63bf8`。不能直接用 FLASH source PC 來推導這個 mapped call target。實際 startup 是否執行、RAM 是否保持原 bytes、installed provider 身分仍未證明。

沿用 [common body 證據](v4160-list-common-body-static.zh-TW.md)，這條尾跳收到 A0=0、A1=OR flags、A2=fresh N+17。RAM body frame16 保存 RA、S0、S1，先從 `2000353c/2000358c` 讀 pointer snapshot H0，再分流 entry mode。

### Common body 選到的 mode0

先以雙指令迴圈反覆讀 H0+100，直到該 word 為零。本機沒有上限或進展動作；全域 pointer slot 不在迴圈內重讀。

退出後令 C=`20003514/20003564`，C+2 清零，以 A0=entry A1 flags、A1=entry A2 N+17 呼叫 FLASH `63b0e/63bf8`；A2 本機仍保留 N+17，但沒有從中推定函式 prototype。

callee 返回後 fresh 取 R pointer，將 R+0 設 bit23、清 R+44 低兩位；再 fresh 取 H1，清 C+5、C+1，寫 H1+0=2。共同後段**再次**從全域讀 H2，進入最終 polling。H0／H1／H2 不預設相同。

### 所有 entry modes 共用的最終 polling

每輪依序觀察 fresh C+2 bit0、C+3 bit0、H2+100 word：任一 byte bit 被觀察為 1，或最後 word 被觀察為 0，就離開；否則回到第一個 byte read。這不是單純「等 H 清零」，三個觀察也不是原子快照。H2 在 loop 外取得，loop 內不重新讀 pointer slot；沒有 call、counter、backoff 或有限上限。

body 另含 generic mode3、mode1 與其他非零 modes；common body 的 A0=0 並不選到它們。mode1 的原指令包含 FENCE.I，以及對兩次 fresh R word bits12..13 的分別判斷；對應 duration literals 為 406／1086／446，不能合成單一穩定讀值。所有 generic 指令仍完整守衛，FENCE.I 僅作 bytes／opcode 檢查，未執行。

mode0 若兩個 polls 與 FLASH callee 都返回，本機保留該 callee A0；非零 modes 沒有 nested call，保留 entry A0。沒有固定 success status。選定固定 H 存取需要至少 104 bytes、R 至少 48 bytes、C 至少 6 bytes；物理 MMIO 身分、nonalias、callee 副作用與保存期仍未知。

## Callback 與後續範圍

只讀探索另定位 callback `55480/5555e` 與 13-entry dispatch tables `6e50c/6e6fc`。兩版 callback 分別為 1064／1154 bytes，存在實際版本差異，不能只平移 +222；其 computed jump、table edges 與回圈將另立完整驗證，沒有計入本次 1080 bytes／402 guards。

後續也需處理較大 B+152 consumer `69a22/69b3a`、lookup head／node writers、FLASH helpers、caller 服務，以及 polling 外部進展與實際 provider 綁定。沒有宣稱完整 call graph、所有 writers、物件釋放或保存期已封閉。

## 重播

[靜態 checker](check_v4160_constructor_consumer_tail_static.py) 核對 402 次 operand／encoding 變異拒絕、44 條選定 CFG walks、434 條 edge witnesses、16 個 bitmask patterns、65536 個 payload low16 cases、RAM source mapping 與 exact ledger。

```powershell
& 'C:\Users\locky\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe' analysis/check_v4160_constructor_consumer_tail_static.py
& 'C:\Users\locky\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe' -O analysis/check_v4160_constructor_consumer_tail_static.py
```

consumer／caller 的局部 CFG 無環，lookup 有鏈表循環，RAM tail 有兩個 polling SCC。這些圖證據都不代表未知 callee、poll 或完整呼叫鏈必然返回。
