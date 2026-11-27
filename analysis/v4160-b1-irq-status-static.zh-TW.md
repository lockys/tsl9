# v4.1.60：JT2 非零路徑的完整旗標寫入函式

本次封閉先前 context callback 非零路徑直接呼叫的函式，接通 S+2／S+3 旗標的具體寫入者，以及 P+1 的讀取用途。它讀取該 byte 來選數值代碼，**沒有驗證 ingress 長度，也沒有直接將資料寫入 P 指向的 buffer**。

[驗證程式](check_v4160_b1_irq_status_static.py)與 [JSON ledger](v4160-b1-irq-status-static.json)固定完整原始 operands、SHA-256、typed loads、QingKe byte 存取、CFG 與全部 stores。全程離線，只解析原 bytes、不可變 CFG 路徑及 host 位元算術；未執行或模擬目標 ISA、RAM、packet、MMIO、trap、callback 或裝置。

| 候選 | FLASH 完整半開區間 | 條件性 RAM 座標 | bytes／指令 |
|---|---|---|---:|
| V131 | `[0x42dbc,0x42ec0)` | `[0x20002b4c,0x20002c50)` | 260／100 |
| V140 | `[0x42e48,0x42f4c)` | `[0x20002b98,0x20002c9c)` | 260／100 |

合計新增原指令驗證 **520 bytes、200 條指令**。兩份均逐 byte 核對 sparse HEX 實際捕獲內容，沒有補零缺口；FLASH 與 RAM 座標分別解碼，並核對 first-copy affine mapping。這是 resident 參考候選，未證明實際 installed provider；既有 C 重建覆蓋率不變。

## 八次 H+8 讀取，不能合併成同一快照

V131 令 S=`0x20003514`、C=`0x20003560`，V140 對應兩者各加 80。函式入口從 S+40 的 slot 擷取 **H** 到 A5，直到 RET 不再重新讀該 slot。需要 R 時則從 S−12 的 slot 讀取 **R** 到 A1。H／R 是動態指標，本機沒有 null 或 extent guard。

下表 offsets 相對各自 RAM 函式入口：

| H+8 讀取 offset | 本次觀察的用途 |
|---|---|
| +0x10 | 保存整個 fresh word 到 S+24 |
| +0x14 | bit3 設定時，對 fresh S+2 OR1；S+4=128；向 H+8 寫 8 |
| +0x2e | bit0 設定時，對 fresh S+1 OR1；向 H+8 寫 1 |
| +0x40 | bit2 設定則進入 S+5 清零及後續分類區段 |
| +0x48 | 僅當上一觀察 bit2=0 才讀；本次 bit1 設定也進入該區段 |
| +0x54 | 該區段重新觀察 bit2，決定 S+3 路徑或代碼分類路徑 |
| +0x9a | bit13 設定時檢查 S+4 的 signed byte，必要時改為1；向 H+8 寫 8192 |
| +0xb6 | bit15 設定時向 H+8 寫 32768 |

每個位置都是獨立 load。前面的 H+8 stores 不足以決定後面的讀值，不能把動態硬體存取當成普通 RAM 的固定 readback。S+4 曾寫128，也可能在後續 signed byte 路徑改為1。從位移後符號判斷反推出 bit13／bit15，是指令位元算術關係，不是硬體旗標名稱或清除語義。

## S+3 的 producer 與 P+1 分類

進入中段時先將 S+5 清零。若 **+0x54 這次 fresh H+8 的 bit2=0**，則：

1. 對 fresh S+3 OR1。
2. 向 H+8 寫2。
3. 讀 fresh U32[R+44]，將低2位改為1，再寫回。

這條分支不讀 P+1。較早 +0x40 或 +0x48 的進入條件不能取代 +0x54 的獨立觀察。

若 +0x54 觀察 bit2=1，則讀 fresh U32[R+0] 的 bits12..13。非零直接選代碼108；為零才讀 fresh H+80、fresh `P=U32[S+36]`，接著讀 `U8[P+1]`。該讀取沒有 P null guard，沒有對來源長度作比較。

| fresh R+0 bits12..13 | fresh H+80 bit5 | P+1 byte | 寫入 H+28 的代碼 |
|---|---|---|---:|
| 非零 | 不讀 | 不讀 | 108 |
| 零 | 1 | 0 | 93 |
| 零 | 1 | 1..255 | 107 |
| 零 | 0 | 0／1／2／3 | 93／97／101／105 |
| 零 | 0 | 4..255 | 107 |

選好代碼後，原指令依序寫 H+28、對 fresh S+0 OR1、寫 H+8=4，再更新 fresh R+44 的低2位為1。隨後還會進入最後兩次 H+8 讀取。這些數值代碼的物理／協定含義尚未證明，不據此命名成功、錯誤或 packet 長度。

函式共有 **15 個 store sites**，只定義 A0..A5；沒有 local call、frame、CSR 指令，沒有 SP／RA／GP／S registers 的本機定義，唯一普通 RET 位於 +0xc4。A4 在最後段被重新用作 H+8 的值與常數，所有以 A4 作 S 基址的存取都在重用前；不能把 A4 全程當成 S。

沒有以 P 作基址的本機 store。不過 H／R stores 的動態別名、裝置寫入、IRQ／DMA 或其他 writers 尚未封閉，因此這不是「buffer 從未被改寫」的全域證明。

## 接回 callback 與外層清零的界線

重用完整 context callback 的非零分支：先把當時 CSR 0x341 存到 caller frame+0，將 gateway operand 寫入 CSR 0x341，再 linked-call 本次完整 leaf，之後 MRET。Leaf 沒有直接寫 CSR／SP／保存 registers；若存取正常、動態 stores 不別名 caller frame 且沒有物理副作用／外部干擾，才可沿用 caller 的必要保存條件。這沒有證明實際 trap 來源或 MRET 到 gateway 的動態交付。

重用 gateway、hook setter／consumer、attempt 及 completion，得到下列靜態關係：

```text
attempt：setter(completion literal) → 返回後清 C+12=0 → 輪詢 fresh C+12
JT2 非零分支：清 hook flag → 設定 MEPC operand → 本次 leaf → MRET
gateway：consumer 擷取 hook slot → 非零時間接呼叫 → 正常返回後 ECALL
completion：成功路徑 C+12=2；失敗路徑 reset 返回後 C+12=255
```

V131 hook slot／flag=`0x20002ef8／0x20002efc`，C+12=`0x2000356c`；V140 分別為 `0x20002f48／0x20002f4c` 與 `0x200035bc`，是不同數值欄位。Setter 本身不呼叫 completion；consumer 使用先擷取的 pointer，完成後再依 fresh flag 決定是否清 slot，沒有重新比對當前 pointer。

實際 callback 必須在 slot／mapping／frame／code 保存等條件成立時才能接上 completion literal。本次 leaf 可產生 completion 檢查的 S+2／S+3 bit0，但兩者來自不同觀察與路徑，並未因此證明同一次 callback 能通過全部 gates。

**仍沒有 callback 相對外層 C+12 清零的 happens-before 證明。** completion 的2與255都非零；如果發生在外層清零之前，後續可能被清零覆蓋。實際順序與觀察結果未知，不能宣稱已發生 lost completion，也不能證明 polling 一定進展。成功旗標又早於 copy／timer 尾跳，非零本身也不表示全部工作已完成。

## 重播與後續工作

驗證器核對每版完整100條 operands、3個 typed loads、10個 QingKe byte encodings、15個 stores 及全部 GPR 定義。每版 **456 條不可變局部 CFG 路徑**皆到唯一 RET；這是語法路徑證書，不宣稱全部在實際裝置狀態下可達。

另核對65,536個低16位 bit 投影、256個 signed byte、512個 byte 分類 cases，拒絕 **200 個指令及6個 typed-load mutation**。一般與 `-O` 模式需逐 byte 重放同一份 JSON，並重新驗證完整上游證據鏈。

```powershell
python analysis/check_v4160_b1_irq_status_static.py
python -O analysis/check_v4160_b1_irq_status_static.py
```

接續仍需追查 P 的實際 byte 內容 producer、ingress 長度與初始化條件；JT2 零路徑的 callee、trap／callback 的實際派送與清零順序；以及 installed provider、物理副作用、fresh pointer 相等性、ownership 與完整保存期。
