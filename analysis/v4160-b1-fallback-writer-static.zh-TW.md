# v4.1.60：ID66 RAM byte setter 與 ID11／count12 返回

接續 [所選 NV／status 至 writer 邊界](v4160-b1-fallback-nv-static.zh-TW.md)，本輪確認 `(66,1,SP+15)` 分支只讀一個借用來源 byte、寫入固定 RAM byte、正常回覆0，沒有下游呼叫。沿用先前保存條件後，已接回 save／outer，再到 ID11／count12，停在第六個 initializer 呼叫前。

檢查器：[check_v4160_b1_fallback_writer_static.py](check_v4160_b1_fallback_writer_static.py)；證據：[JSON ledger](v4160-b1-fallback-writer-static.json)。全程只核對原始 bytes、封閉 CFG、所選操作數、區間／frame／def-use 關係；沒有執行或模擬 target、NV、provider 或硬體，也沒有建立可變 RAM／heap／MMIO 模型。新增 C 重建 bytes 為0，原始 bin 不變。

## 完整函式邊界與所選分支

| 項目 | V1.31 候選 | V1.40 候選 |
|---|---|---|
| Writer 完整範圍 | `[0x494ee,0x49714)` | `[0x49586,0x497ac)` |
| 長度／指令數 | 550 bytes／187指令 | 550 bytes／187指令 |
| ID66 的單 byte RAM 目的地 | `0x20002edc` | `0x20002f2c` |

完整範圍包括 `+0x1a8` 分支抵達的 `+0x222` 錯誤尾段（`li A0,24; ret`）；不能在較早的 RET 截斷。封閉 CFG 有三個 RET、六個 linked call sites。完整 bytes、SHA-256、所有本地邊及 call／RET census 都有護欄，所選 ID66 分支另核對操作數；其他 option branches 的服務副作用並未在本輪串接。

入口 A0=66、A1=1 時，先跳過 ID5 特例，建立48-byte frame，保存 S0–S4 與 RA，再經 `5 < 66` 與 ID66 比較到 length guard。Length=1 才執行一次 `qk.c.lbu A4,0(A2)`，把讀到的 byte 以 SB 寫至 `G−292+δ`，回覆 A0=0。其他 length 在讀來源之前回覆24。

原始 `1822` bytes 解碼為 QK unsigned byte load；不把它當成一般 RISC-V 浮點 load。A2 是前輪仍存活的 save SP+15，該單 byte 已知為10，因此所選 RAM store 的值就是10。

六個下游 call sites 都不在這條所選路徑：`0x490f8／0x49190`、RAM release／allocator／fill，以及兩個 copy 呼叫。所選 ID66 分支沒有觸發它們，也沒有呼叫 `0x4435c／0x443f0` 等其他 NV wrapper。這裡證明的是一筆 RAM byte 更新，不能推論實體 NV 持久化。

## 借用來源的消費與返回

Writer 新 SP 比 save 的當前 SP 低48 bytes，因此借用來源在 writer SP+63：它位於 caller 的32-byte save frame，超出 writer 自己的48-byte frame，也不重疊 writer saved RA。所選分支只讀這一 byte，沒有把來源 pointer 發布為 global word；唯一非 frame store 的 source 是 byte 值。

Writer 還原 RA、S0–S4、SP 並 RET 到 save `+34`。Save 還原 RA、釋放32-byte frame，再 RET 回 outer entry+88。來源 dereference 發生在 save frame 仍有效時，但 writer／save 返回後 A2 仍暫存該借用位址；**這不會延長已釋放 frame 的有效期**，也不是完整 no-escape 證明。

本輪另外核對下一個 registrar 在讀取或解參考舊 A2 前，先以 `addi A2,A5,1` 覆寫 A2。所選返回鏈沒有在該空窗使用借用指標；不能因此保證任意 caller 或非所選分支的 pointer 保存期。

## RAM 目的地、既有配置與 frame

單 byte 目的地逐一排除於沿用的 fallback、config、flags、CB48、vectors、records0..2、ID／task metadata、NV pool／count／limit、ID8 pointers／hooks 等 protected intervals 之外。它也不位於第一段 copied code 的完整目標範圍。

對1024組舊來源家族與其 m=0..3 NV count，檢查器另核對所有舊 owners／headers、新 NV header／payload／remainder，以及完整第一張 table payload。此 setter 不更動那些區間；後續 entry11／task count 的發布則另行檢查。

這些是不可變位址與範圍運算。合法且實體不別名的 frames／RAM／code／metadata、matching ISA 與原始程式、required ABI／saved words 保留、沒有不利 IRQ／DMA／重入／外部寫入等前提仍須成立。

Writer 階段同時存活 outer16＋save32＋writer48=96 bytes。Writer 與 save 先後返回後，終點只剩 outer16-byte frame；並未執行任何目標 stack 或記憶體操作。

## ID11／count12 終點

Writer 所選路徑沒有重新定義 A1／A2，故回覆 A0=0、A1=1，A2 仍是借用來源位址。Save 亦不把 A1 改成其他值。Outer 隨後載入新的 handler，不測試這個 writer A0。

若 fresh count11、capacity至少14、table pointer仍為 T=`0x200047f4`，registrar 把 handler `0x4d1b0／0x4d248` 發布到 entry11=`0x20004820`，count 更新12，回覆 `(A0,A1,A2)=(11,1,12)`。Entry11 是第一張 table payload 內的預期更新，不覆蓋既有 entry0..10 或配置 owners。

終點為 V1.31 `0x6dd7a → 0x4d172`／V1.40 `0x6df6a → 0x4d20a`，fallback0、gate5、saved ID6、local ID7..10、ID66 byte=10、task count12。第六個 initializer 尚未串接。

這個結果仍沿用先前 m=0..3、正計數 read wrapper 的兩條回覆10路徑、FF status=0、兩個 optional flags 為零等所選條件；writer ID66 本身不需要那些 NV read 條件，但本輪返回鏈是從該既有 checkpoint 接入。

## 驗證與未完成項目

兩個候選各有5個 strict sparse HEX 範圍核對，包含 writer、save、outer、next-outer window 與 registrar。新增374個原指令位置變異拒絕，加上前輪2559組，合計2933組。正常與 `-O` 模式均須重算並逐 byte 比對 ledger：

```powershell
python analysis/check_v4160_b1_fallback_writer_static.py
python -O analysis/check_v4160_b1_fallback_writer_static.py
```

其他 writer option／NV 成功／cache／非零 flag 分支、實際 installed 綁定與 source writers、第六個 initializer／outer final tail、callbacks 的消費、完整跨事件保存／釋放期及實機功能仍未完成驗證。所選 byte store 與正常返回不等於 NV 持久化或整份韌體可用。
