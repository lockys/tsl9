# v4.1.60：完整 completion callback 與設定欄位來源

本階段完整展開 attempt 發布的 callback `0x65de6/0x65ed0`，串接 [channel helper](v4160-b1-channel-static.zh-TW.md) 與既有 RAM service 證據。全程離線，只核對原始位元組、operands、不可變 CFG、host bitstring／區間算術；沒有執行或模擬目標 ISA、provider、packet、RAM、timer 或硬體，也沒有資料重放。

[驗證程式](check_v4160_b1_completion_static.py)及 [JSON ledger](v4160-b1-completion-static.json)保存完整 callback、producer 與順序證據。

| 完整 callback | 原始範圍 | bytes／指令 |
|---|---|---|
| V131 resident 候選 | `[0x65de6,0x65f94)` | 430／156 |
| V140 resident 候選 | `[0x65ed0,0x6607e)` | 430／156 |

新增 **860 bytes、312 條指令**。每個位元組都符合原始 sparse HEX，不補零填缺口。重用完整 config、channel、cleanup、RAM service／request、comparator 與 copy 合約，不重算新增範圍，也不提高既有 C 重建覆蓋率。

## 完整本機範圍與 gates

令 V131 `S=0x20003514`、`F=0x20003540`、`C=0x20003560`；V140 對應地址加 80。callback 使用 32-byte frame，保存 RA／S0..S4 六個 word。共有 **24 個 store sites**（六個 frame saves、18 個非 frame stores）、十個 linked call sites、一個普通 RET 與一個恢復 frame 後的 timer 尾跳。本機唯一迴圈是固定 32 位 popcount；不因此宣稱含 callees 的整條鏈必定結束。

六個失敗 gate 共用 reset／failure 出口：

1. 初始 fresh S+2 bit0 必須設位；清 S+2，再請求 config `(fresh F+0 bits4..5,32,0)`，之後 RAM request `(1,另一個 fresh bits,255)`。
2. fresh S+3 bit0 必須設位；捕獲 fresh S+36，清 S+3／S+2，請求 RAM service `(captured S36,0,0,0)`。
3. 該 service 必須回覆完整 0。回覆先保存至 S4，作後續 popcount seed；成功路徑此時 seed=0。
4. **重新讀取 S+36** 為 P，要求 byte P+2==5。P 不假設等於前一個 service 入口的指標。
5. comparator `(P+9,0x20003204/0x20003254,6)` 必須回覆完整 1。
6. 向 fresh S+32 所指 word0 寫 6，呼叫 channel `(fresh bits,0)` 與 RAM request `(3,另一個 fresh bits,0)` 後，另一個 fresh S+2 bit0 必須設位。

任一 gate 失敗即呼叫 reset `0x63e58/0x63f42`，在其正常返回後向 C+12 寫 byte **255**，恢復 frame 並普通 RET。255 是記憶體中的 flag，並非強制 A0 回覆；RET 保留當時 reset 返回的 A0。先前已做的寫入沒有本機整體 rollback。

## 重用服務的精確界線

RAM `0x2000263a/0x20002686` 的完整 128-byte 合約已重新驗證；這次 A1／A2／A3 都為 0，會略過 packet A0 的解參考與兩個 optional output writes。它依 fresh R words 可回 0／1；回 0 的路徑會寫 status S+11。這個零回覆不能取代 callback 自己的 type／comparator gates，也不是 packet extent 或內容有效的證明。

72-byte comparator、58-byte copy、250-byte RAM request 均重新核對完整來源與 first-copy affine mapping。comparator 的既有 null-success 情況仍保留；若要從回覆 1 推得六 bytes 相同，須另有有效且非零 operands／無 wrap 等前提。RAM request 的輪詢與實際 provider 綁定亦未因重用而自動證明。

## 成功路徑的 clock、cleanup 與保存期

最後一個 gate 通過後，捕獲 fresh clock function word，清 S+2，間接呼叫並把返回 A0 寫至 C+8 baseline。接著呼叫完整 inner cleanup `0x656c6/0x657b0`。

**callback 在 cleanup 返回後才繼續讀保存的 P。** 已知 cleanup 可請求釋放 C+4 指標並清除該欄位；目前未證明 C+4 與 P 的物件關係。即使 callee 保存 S0 內的 P 數值，也不能據此推論 P 的內容／extent 在返回後仍有效。這是保存期條件，並非本階段確認了實際釋放後使用。

## 設定來源與 popcount producer

在有效 P、callee 正常返回及必要保存條件下，成功路徑直接產生：

| 目的欄位 | 來源／寫入 |
|---|---|
| F+1 | 0 |
| F+25 | fresh byte P+19 |
| F+26（sampler K） | fresh byte P+20 |
| F+27（selector step） | fresh byte P+21 |
| C+13（proposed index） | 0 |
| F+8 word | LE32(P+15..18)，實際讀取順序 16、15、17、18 |
| F+20 mask word | LE32(P+22..25)，實際讀取順序 23、22、24、25 |
| C+17（selector divisor） | 先清零，之後按同一 held mask 的 popcount 發布 |
| F+24 | fresh byte P+26 |

這些都是獨立 byte observations，不能稱為原子 packet snapshot。直接存取至少需要 P 的 27-byte extent，仍未證明真實來源具有此長度或生命期。

mask 先以同一個 held word W 寫入 F+20。S4 的 seed 來自先前已通過的 service==0 gate；接著恰好掃描 W 的 32 位，遇到 set bit 才遞增 S4，byte mask 不會在 0..32 內 wrap。若 mask 非零，將 count 寫入 C+17；若為零，保留先前的 C+17=0。

因此在完整 producer 已結束、store 未被 alias／其他 writer 改變等條件下，產生的配對滿足 **C+17=popcount(W)，範圍 0..32**。這補上先前 bit selector 的一個條件性來源，但不是所有路徑或所有後續 fresh reads 的 invariant：C+17 preclear、F+20 store、32-bit count、C+17 publication 之間有明確的非原子窗口。

另外，**P+20→F+26 沒有零值檢查**。這條 producer 不能證明 K>0，先前 sampler 的 K=0 不進展情況仍未排除。

## completion flag 與尾端工作

成功路徑在產生上述欄位後，先向 C+12 寫 **2**，才請求 copy `(C+28,P+3,6)`；之後重新讀 fresh C+16 task ID，恢復自身 frame，無新 link 尾跳 start_timer `(fresh task,4,40)`，目標 `0x43728/0x437b4`。

這個 flag store 在最後 copy 及 timer 請求之前。失敗值 255 也同樣非零，因此其他 waiter 看到 C+12 非零，不足以證明成功、copy 完成、timer 啟動或 callback 全部返回。

原始 attempt 的非128路徑會在發布 callback **之後**清 C+12=0，再等非零。callback 的兩種寫入現已定位，但尚未證明實際 dispatch、相對執行順序或 waiter 能觀察到它們；callback 若早於外層 clear，後者仍可能覆寫該值。未宣稱存在既定 happens-before、事件交付或 polling 進展。

## 驗證與剩餘工作

驗證固定完整 operands、typed loads、QingKe byte accesses、十個 linked calls／單一 timer tail、24 個 stores、frame／返回、全部 CFG 邊與六個 failure gates，以及 zero／full mask 的 32-iteration 不可變 witness。拒絕 **312 個逐指令 mutation、12 個 typed-load mutation**。

host scalar 檢查涵蓋全部 16-bit masks 及重複至高16位的 mask family，共 **131,072 個 popcount 案例**；另核對全部 K byte 與 byte packing。此 family 不是全部 32-bit masks 的窮舉；generic producer 合約另由原指令／CFG 支持。一般與 `-O` 模式精確重放同一 JSON，沒有 target packet／RAM 狀態模型。

實際 candidate ISA／mapping／provider／callback identity、有效 code／frame／global／packet／dynamic object extent、callee 保存與 P 的內容生命期、無破壞性 alias／IRQ／DMA／重入等仍是前提。後續需追查 S+36 的真正 producer、來源長度與保存期、設定欄位可達值，以及 callback dispatch 和外層 C+12 clear 的順序；整體 polling 與完整保存期尚未驗證。

```powershell
python analysis/check_v4160_b1_completion_static.py
python -O analysis/check_v4160_b1_completion_static.py
```
