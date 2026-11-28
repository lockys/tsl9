# v4.1.60：所選 NV 錯誤分支、FF status 與單 byte writer 邊界

接續 [ID10 的首次服務邊界](v4160-b1-fallback-id10-static.zh-TW.md)，本輪把兩條 NV read wrapper 的無子呼叫錯誤分支、loader 補值、兩次 status 與 save 前段接起來。在既有 m=0..3 等條件、且第二個 optional flag 為零時，停在 writer `(66,1,SP+15)` 呼叫前，stack source 的單 byte 為10。Task count 仍為11，尚未發布 ID11／count12。

檢查器：[check_v4160_b1_fallback_nv_static.py](check_v4160_b1_fallback_nv_static.py)；證據：[JSON ledger](v4160-b1-fallback-nv-static.json)。全程只核對原始 bytes、不可變 CFG、整數、區間與 frame 關係，沒有執行或模擬 target／NV／status／MMIO／硬體，也沒有建立可變 RAM／heap／provider 模型。本輪新增 C 重建 bytes 為0。

## 兩條不呼叫底層服務的 read wrapper 分支

完整590-byte read wrapper 位於 `0x440c2／0x44156`。令 F=`G+492+δ`、C=`F−80`，G=`0x20003000`，V1.31 δ=0、V1.40 δ=80。本輪正計數掃描額外限定下列其中一種保存條件：

| 分支 | 必要 fresh／retained 值 | 回覆與局部效果 |
|---|---|---|
| Configured missing callback | U32[F+8] 非零、U32[F+56] 為零 | 回覆10，只寫自身 frame |
| RAM null | U32[F+8] 為零、U32[C+32] 為零 | 回覆10，只寫自身 frame |

兩條原始 CFG 都不含 allocator、底層 callback、copy、release 子呼叫，亦不走 wrapper 的兩筆 context stores。輸出 pointer 只保存於 S2，沒有輸出寫入。這不是 NV read 成功、實體 NV 單位或資料已載入的證明；其他 wrapper 分支仍保留原有複雜合約。

Loader 在 m=1..3 時，數值請求為 `(512+6*i,16,P+16*i)`、i=0..m−1。Read wrapper 回覆10，故走非零回覆的 fallback：各筆前6 bytes 與接續6 bytes 補 `ff`，+12 半字清零。該 fallback 不寫 bytes14／15；所選兩條 wrapper 分支又沒有輸出寫入，因此 byte14 保留前輪初始化的零值，byte15 仍未被證明已初始化。完整16-byte record 的已知部分為：

| Record offsets | 所選結果 |
|---|---|
| 0..11 | `ff` |
| 12..14 | `00` |
| 15 | 未初始化／未知 |

這個較強結果只適用於本輪無輸出寫入分支；不能套用到可能部分寫入後失敗的其他 provider 路徑。m=0 沒有 read wrapper 或補值迴圈。

## Status 為何回覆0

Status helper 位於 `0x6af88／0x6b16c`，完整88 bytes／33指令。它有32-byte frame，五筆 stores 都在 frame。索引與累計值先設零，每次索引小於 fresh count 時，以 `(P+16*i,255,6)` 呼叫 `0x200004bc`，**只有 predicate 回覆0才累加**，最後回覆累計值。

完整62-byte／19指令 predicate 的 A1=255 是 full-word 比較值，不是 pointer，也不是任意值截成 byte。它將來源 byte 零擴展後逐一比較；P 非零、六 bytes 都為 `ff` 時回覆1。因此在所選 count／P／FF6 保存條件下，m=1..3 的每次比較都回覆1，累計保持0；m=0 不讀 pool、不呼叫 predicate，直接回覆0。

Predicate 雖不寫來源 RAM，也沒有 frame／子呼叫，卻會先擷取並清零 `0x4002420c`、執行 `FENCE.I`，在 RET 前寫回擷取值。本輪只驗證原指令、control 位址與 restore 順序；其物理效果不會破壞 protected RAM／frames、沒有不利 IRQ／DMA／重入等影響，仍是明列前提，並未執行這些指令。

Status 的33條原始指令、兩版完整 SHA-256、m=0..3 四條有限 CFG 路徑，以及 predicate 的六次 FF 比較路徑均收入 ledger。Status 回覆0不表示 NV read 成功或整筆 record 完全初始化。

## Optional flags 與第二次 status

第一次 status 返回 loader 後，仍有兩個獨立 fresh flag：

- G−71+δ：先前 setup 已清零，本輪所選 wrapper／fills／status 沒有對它的 RAM 寫入；在保存條件下跳過第一個 optional call。
- G−72+δ：先前 setup 沒有清零，本輪另需此 fresh byte 為零，才能跳過第二個 optional call。沒有把未知 optional callee 假設成無副作用。

跳過後，loader 還原並釋放32-byte frame，尾跳 save wrapper。Save 再呼叫同一個 status；count、P 與 records 的 FF6 保留時，再次回覆0。Save 的 unsigned 分支因此選 byte10，而非另一條一般路徑的 byte2。

## 單 byte stack source 與截止點

Save 使用32-byte frame，原 `qk.c.sbsp` 在 SP+15 寫 A5 的 byte10。只有這一 byte 被當作 writer 輸入；它與 saved RA 的 SP+28..31 不重疊。`SBSP` 解碼沿用前輪6個 LLVM 原向量與128個 field combinations，不把 byte store 誤認成半字或浮點 store。

| 項目 | V1.31 候選 | V1.40 候選 |
|---|---|---|
| Status helper | `0x6af88` | `0x6b16c` |
| Save wrapper | `0x6b25e` | `0x6b442` |
| 本輪截止點，writer 呼叫前 | `0x6b27c → 0x494ee` | `0x6b460 → 0x49586` |

截止時 A0=66、A1=1、A2=當前 save SP+15，來源單 byte 為10；fallback0、gate5、local ID10=10、task count11。Save frame 仍存活，尚未呼叫 writer，不能推定其同步消費、pointer 保留、回覆或持久化結果。

新增串接階段的最高同時存活 frame 為 outer16＋loader32＋read wrapper或status32=80 bytes；save32＋status32 也為同樣80 bytes。此前配置階段最高96 bytes 不變。Writer 截止時 outer16＋save32=48 bytes。所有 saved words／S／GP／SP／RA、實體不別名與有效存取仍是前提。

## 保存檢查與驗證範圍

Loader 的補值範圍逐一對1024組舊來源家族、m=1..3 的新 NV payload 核對，排除對所有舊 owners／headers、NV header／remainder、完整第一張 table payload、CB48、向量、records0..2、fallback、task metadata、NV count／pool／ID／limit 與兩個 flags 的覆蓋。任意位置的 frame 與 control 物理效果，仍由明列的 nonalias／有效存取／無不利介入寫入條件約束。

每個候選有6個 strict sparse HEX 範圍核對，包含完整 status、read wrapper、predicate、fill、loader 與 save。合計2559組原指令／typed-load 變異拒絕，組成為先前2003、read wrapper 404+48、status 66、predicate 38。正常與 `-O` 模式均須重算並逐 byte 比對 ledger：

```powershell
python analysis/check_v4160_b1_fallback_nv_static.py
python -O analysis/check_v4160_b1_fallback_nv_static.py
```

其他 read 成功／cache／provider 分支、非零 optional flags、實際 installed 綁定與 flags／source writers、writer 的消費與 borrowed buffer 保存期、完整 ID10 返回及 ID11 登記、第六個 initializer／outer tail、跨事件消費／釋放期與實機功能仍未完成驗證。
