# v4.1.60：admission sampler 與 clock 來源

延續 [完整 attempt helper](v4160-b1-attempt-static.zh-TW.md)，本階段展開它所呼叫的完整 RAM sampler，並串接既有 APP constructor、config writer 與 reader 證據。全程離線，只核對原始位元組、operands、不可變 CFG、host scalar／區間算術；沒有執行或模擬目標 ISA、clock、provider、timer、RAM、polling 或硬體。

[驗證程式](check_v4160_b1_sampler_static.py)及 [JSON ledger](v4160-b1-sampler-static.json)保存逐指令、分支與跨函式證據。

| resident 候選 | 原始 FLASH 範圍 | first-copy 對應 RAM 範圍 | bytes／指令 |
|---|---|---|---|
| V131 | `[0x42fbc,0x43062)` | `[0x20002d4c,0x20002df2)` | 166／56 |
| V140 | `[0x43048,0x430ee)` | `[0x20002d98,0x20002e3e)` | 166／56 |

新增 **332 bytes、112 條指令**。每個範圍均在原始 sparse HEX 捕獲且與 carrier 完全一致，不填補來源缺口。重用 attempt 共 1,004 bytes、完整 config writer 共 448 bytes、APP constructor／reader 共 216 bytes，不算新增範圍，也不提高既有 C 重建覆蓋率。first-copy 對應僅是候選靜態 mapping，沒有證明實際 RAM 或開機 copy 相同。

## sampler 的差值與出口

令 V131 `C=0x20003560`、`F=0x20003540`、clock slot=`0x200031e0`、M word=`0x20003238`；V140 對應地址加 80。

sampler 先讀取 fresh clock function word，配置 32-byte frame，保存 RA 與 S0..S4 共六個 word，再作間接呼叫。沒有本機 null guard，亦沒有明設 A0／A1／A2，因此不能宣稱它已證明為零參數 ABI。clock 正常返回的完整 unsigned 值記為 T，**其後**才讀 fresh C+8 baseline B。

- T==B：直接回傳 0，不讀 threshold byte 或 M。
- unsigned T>B：`D=T-B`。
- unsigned T<B：讀 fresh M，`D=low32(T+M-B)`；沒有加 1，也未證明 M 是硬體 modulus。

令 `q=D>>5`、`r=D&31`。讀第一個 fresh byte `k0=[F+26]`，若 q<k0，略過迴圈並回傳原 D；否則進入以下狀態更新。這個輸出合約沒有提供亂數或分布證據。

## 迴圈內的獨立 snapshots

每輪先 linked call RAM `0x20002c50/0x20002c9c`，其副作用仍待展開。正常返回後，依序重新讀取：

1. fresh byte `K=[F+26]`；
2. fresh word `old=[C+8]`；
3. fresh word M。

計算 `v=low32(old+32*K)`，若 unsigned v<old 或 v>=M，向 C+8 寫入 `low32(v-M)`，否則寫入 v。這是**一次條件性減法**，不能泛稱為任意輸入的 modulo M。

另外將 q 更新為 `low32(q-K)`。若 unsigned 新 q>=本輪剛讀到的 K，回到迴圈；否則回傳 `low32((q<<5)|原始 r)`。完整函式只有這一個非 frame store site（C+8），唯一 RET 在 +0x94；切除 +0x7a→+0x54 後 CFG 為 DAG。

初始 k0 與每一輪 K 都可能不同。若 fresh K 比當時 q 大，減法可以 underflow；K=0 不會降低 q。沒有無條件的單調性、迭代上限、輸出範圍或進展保證。

## 僅在穩定正數 K 下成立的算術

若**初始與每次迴圈讀取均為同一 K>0**，且每個 callee 正常返回並保存 q／r／frame 等必要條件成立，則由 `D=32*q+r` 與 quotient／remainder 身分可得：

```text
迴圈 callee 次數 = floor((D >> 5) / K)
普通返回值       = D % (32*K)
次數上限         <= 134217727
```

這個上限只計算穩定正數 K 下的本機迭代次數，不代表 callee 時間、硬體進展或整個 attempt 有限時完成。

若 K 持續為 0，非相等 clock 路徑會進入迴圈，q 不變且 unsigned backedge 總成立；在相同 callee／保存條件下無法普通返回。T==B 仍先回傳 0。先前 attempt 的外層 admission 在 byte=0 時計算出 `0xfffffff0` 的寬區間，但那是**sampler 返回後另一次 fresh read**；不能把它與內部 K=0 的不進展情況合併成已知實際可達輸出。

若外層 admission 也另有證據讀到同一正數 K，則它只接受 sampler 回覆 `[16,32*K-16]`。本階段沒有假設這種跨呼叫／跨讀取穩定性。

## clock slot 的條件性發布來源

重用的完整 writer 是 candidate API `0x40074`：V131 `[0x43f46,0x44022)` 共 220 bytes／76 指令；V140 `[0x43fd2,0x440b6)` 共 228 bytes／78 指令。

APP constructor `0x19b56` 在自身 frame word0 形成 reader code address **`0x191c6`**，再以 A0=frame 呼叫 fresh `[0x40074]`。candidate writer 的接受路徑經過 optional hook 與 config gates，請求 copy 16 bytes 至 `0x20003234/0x20003284`，正常返回後**重新讀 copied word0**，才寫入 clock slot `0x200031e0/0x20003230`。

因此不是直接把入口 A0 存入 clock slot。只有在來源、copy、optional hook、保存與返回等條件成立時，該次發布 word 才可對應 `0x191c6`。完整 null-config/default 路徑有不同來源，其他未知非零 hooks 也未閉合。

attempt 與 sampler 確實讀取同一個 nominal clock slot，但兩者各作 fresh read；沒有證明 installer 曾執行、發布先於使用、slot 之後沒被改寫，或實際 installed provider 等於候選。

## 對應 APP reader 的既有界線

完整 APP reader `[0x191c6,0x19220)` 共 90 bytes／28 指令已重新核對，沒有本機 calls、stores 或 frame。它對 nominal high halfword 地址 `0x40002818` 與 low 地址 `0x4000281c` 作 pairwise reads：

- 先重讀 H1，直到一對 high 相等；再重讀 L1，直到一對 low 相等；再取得相同方式的 H2。
- H1==H2 時回傳 `(H2<<16)|L1`；否則再取得一對相等的 L2，回傳 `(H2<<16)|L2`。

L2 後沒有最後一次 high recheck。四條精確 retry edges 已固定，但沒有 coherent／atomic／monotonic counter、半字硬體語義、時間單位或必定終止的證據。這裡只串接既有原指令合約，未採集或合成目標 bus 讀取序列。

## 驗證與剩餘工作

驗證包含完整函式 operands、typed loads、QingKe byte load、六個 frame saves／唯一非 frame store、兩個 call sites、全部 CFG 邊與選定分支 witness。拒絕 **112 個逐指令 mutation、10 個 typed-load mutation**。host scalar 驗證涵蓋 K=1..255、D=0..65535，共 **16,711,680 組 quotient／remainder 算術**，另核對 zero-K 與條件性單次減法邊界；沒有迭代目標狀態模型。一般與 `-O` 模式精確重放相同 JSON。

所有串接仍要求候選 ISA／mapping／API、有效 code／frame／global extent、一般 callee 對 S／SP／RA／frame 的保存，以及沒有破壞性 alias、wrap、IRQ／DMA 或重入。fresh reads 的相等性須另證。下一步仍需展開 loop callee `0x20002c50/0x20002c9c`、baseline writers、`0x6434a/0x64434`、`0x63b0e/0x63bf8` 與 callback 本體，確認實際 provider 綁定、順序、輪詢進展與完整指標保存期。

```powershell
python analysis/check_v4160_b1_sampler_static.py
python -O analysis/check_v4160_b1_sampler_static.py
```
