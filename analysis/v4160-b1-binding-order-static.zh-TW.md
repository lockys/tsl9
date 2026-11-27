# v4.1.60：RF callback 發布來源與同輪初始化順序

本階段核對兩候選的完整 config、role 本體，以及原 APP 的完整 setup，合計 **1,152 個不重複 bytes／394 instructions**。共用 APP setup 只計一次。另重用已核對的 constructor、fill／copy 與 RF consumer；沒有增加 C 重建覆蓋率、執行目標或修改原始韌體。

| Body | V131／APP | V140 | 每份 bytes／instructions |
| --- | --- | --- | --- |
| config | `64bae..64cec` | `64c98..64dd6` | 318／112 |
| role | `66056..66098` | `66194..661d6` | 66／22 |
| APP setup | `8e88..9008` | 同一 APP，不重計 | 384／126 |

[檢查器](check_v4160_b1_binding_order_static.py)與[帳本](v4160-b1-binding-order-static.json)固定全部 operands、SHA-256、CFG、分支路徑與語法 edge 見證。候選 body 和 `401c0／401c4` table words 都逐 byte 比對原始 sparse HEX；APP 固定原始完整映像身分。這是 offline scalar／interval／CFG 驗證，沒有目標 ISA、callback、provider、heap 或硬體執行／模擬。

## 具體 callback 來源：APP stack record 中的 174ee

原 APP constructor `175e8..17666` 建立 48-byte frame，向 fill 請求清除 `[SP,SP+32)`，再寫入：

| 位置 | 原始 local store 值 |
| --- | --- |
| SP+0 halfword | `0x2501` |
| SP+8 word | `0x8e89bed6` |
| SP+12 word | `0x00555555` |
| SP+16 word | callback `0x174ee` |
| SP+25 byte | 4 |

`17654` 以 S0=`40000` 載入 +452，即 fresh slot `401c4`；`17658` 設 A0=SP，`1765a` 間接呼叫。此時 record 還在 frame 中；saved S1／S0／RA 位於 SP+36／40／44，與 32-byte record 分離。Constructor 不檢查這次 scalar reply，正常返回後會釋放自己的 frame。

兩份候選的 slot `401c4` 分別含 `64bae／64c98`。這連起數值 table 與完整候選 body，但不代表實機 slot、RAM helper 或 ABI 已與候選一致。

## Config 的兩個早期拒絕與發布次序

以 S 表示 caller record，F 表示 global config base：V131 `20003540`、V140 `20003590`。

1. 入口先讀 U32[S+16]。若為零，無 frame／child call 地返回 1；這不是對 S 本身的 null guard。
2. 建立 16-byte frame。若 fresh U8[S] 的 bit6 為1，且 fresh U32[S+4] 為零，返回 2，不進入 fill／copy。
3. 通過後請求 `fill(F,0,32)`，再請求 `copy(F,S,32)`；兩次 reply 都不檢查。

在實際 RAM helpers 匹配參考、存取有效、來源與目的不重疊且必要資料／frame 保存等前提下，callback word 的來源為：

```text
S+16..19  --forward byte copy-->  F+16..19
callback slot = 20003550 / 200035a0
APP 設定的值 = 000174ee
```

[先前 RF consumer](v4160-b1-inner-static.zh-TW.md)讀取的正是這個 slot。Fill 先清除這四個 bytes，接著 copy 依序寫入 `ee 74 01 00`；沒有證明這是一個原子 pointer 發布，也不能從控制字／FENCE 操作推得 concurrent callback 已被排除。

## 後段 defaults 不直接改 callback word，但晚期 callees 仍有義務

Config copy 之後有五個獨立 fresh byte-zero guards，分別對 F+25..29 補上 40、8、17、251、251。另一次 fresh U8[S] bit6 決定是否讀 fresh U32[F+4]、計算並寫 F+1；不能把兩次來源 flags 自動當成同一個 snapshot。

數值算式的完整 U32 partition 已固定：

| fresh U32[F+4] | 寫入 F+1 前的 scalar |
| --- | --- |
| 0..2,403,999 | 37 |
| 2,404,000..2,425,999 | `(x-2,402,000)/2000` 的 unsigned quotient，再減1 |
| 2,426,000 | 38 |
| 2,426,001..2,479,999 | 同 quotient，再減2 |
| 更高 | 39 |

這是原指令數值關係，不宣稱其物理單位。中間 75,999 個值及完整區間分割都由 host 代數核對。

令 C=F+32。之後順序為：

1. 讀 old U32[C+4]，非零就請求 private release `20000110(old)`，忽略返回。
2. fresh 讀 U8[F]，將 C+4 清零。
3. 若剛才 flags bit0 為1，請求 `allocate(2+fresh_U8[F+29],73)`，把返回值寫至 C+4，**沒有 null 檢查**。
4. fresh F+1 byte 寫 C+15，fresh F+8 word 寫 C+20，正常返回 0。

因此 allocation 返回零仍可得到 config scalar 0。直接 defaults／metadata stores 不重疊 F+16..19，但 private release、allocator、alias、IRQ／DMA／reentry 或其他 writers 是否保存該 word，不能從局部 store 清單推得。

對原 APP record，在 matching fill／copy、來源 frame 保持與無其他寫入等前提下，flags=1，bit6 guard 被略過；copy 後的 F+25 保留4，F+26..29 補為8、17、251、251，配置請求為 **253、tag73**。這裡的大小取自 **F+29**，不是 F+25；它只是條件性數值請求，不證明實際配置或綁定成功。

## 同一次 APP 初始化：role 先於 constructor

完整 setup 只有一個 local conditional branch：`8f40` 略過或包含 `8f5c` 的 optional call，之後在 `8f5e` 匯合。兩條以 callees 正常返回為條件的路徑，都有相同順序：

```text
8ec2：fresh [401c0] role call
8ef6：參數 A0=774 的間接 call
8fdc：直接呼叫 constructor 175e8
constructor 1765a：fresh [401c4](SP)
```

檢查器另以 CFG node-cut 證明前兩個 call 在正常返回圖中支配 constructor。S0 在本機先設 `40000`，之後重新設同值；跨未知 callee 仍需保存 S0。這不是 boot、未知 callee 必返回、task 排程或實際 slot 保持的觀察。

兩份候選的 `401c0` 指向 `66056／66194`。Role 本體先呼叫 `64298／64382` 的 pointer-publication parent，連同其 tail 正常返回後，才依序：

1. `fill(C,0,36)`。
2. SW `ffffffff` 至 C+0。
3. 以 `65920／65a0a` 作 callback 請求 task registration。
4. 將返回值 low8 寫 C+16，忽略 registration／fill scalar，正常返回0。

這個 36-byte context clear 從 **F+32** 開始，與 callback word F+16..19 分離，不能當作 callback slot 清零證據。Parent 的明確 pointer stores 已由前輪核對，但其所有 nested callee、其他 writer 或晚期時序不能因此一併視為封閉。

## 可以與不可以延伸的保存期結論

本次找到的是一條具體的 callback 發布來源及其局部順序：原 APP 用 stack record 傳入 code pointer，候選 config 請求 by-value 複製，RF 後續從對應 global word 取 pointer。

這份**較後** constructor 的 publication，不能倒過來供應同輪較早 role 初始化中的 callback。這也不代表較早 slot 必為零：前次初始化、其他 config caller、間接入口、bulk writes 或非同步寫入仍未普查封閉。

Config 的 post-copy local code 沒有將原始 S 寫成 global pointer；但 borrowed S 在 copy 請求與 ambient registers 中出現，後續未知 callees／alias 行為仍可能保存它。無法僅從 by-value copy 推得完整 source-pointer no-escape 或 callback lifetime。也沒有證明 B1 觸發時仍使用本次 publication、RF fresh state 保持某個值，或實際 installed API／RAM code 與候選相符。

## 重播

```powershell
& 'C:\Users\locky\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe' analysis/check_v4160_b1_binding_order_static.py
& 'C:\Users\locky\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe' -O analysis/check_v4160_b1_binding_order_static.py
```

拒絕 394 個不重複逐指令 mutations、22 個 typed-load mutations；驗證 75,999 個中段 scalar、512 組 flags／aux 條件、callback byte lanes、frame／global interval 及初始化順序。一般與 `-O` 逐 byte 重播同一 JSON。所有路徑是不可變 CFG 語法見證，沒有目標 ISA、callback、provider 或硬體執行。
