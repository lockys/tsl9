# v4.1.60：完整 attempt helper 與 request128 合約

延續 [request 配置與 RAM mode1](v4160-b1-request-config-static.zh-TW.md)，本階段完整展開 request 以 `(0,0,128)` 呼叫的 attempt helper。分析全程離線，僅核對原始位元組、operands、不可變 CFG、host scalar 與區間算術；沒有執行或模擬目標 ISA、provider、RAM、clock、sampler、queue、polling 或硬體。

[驗證程式](check_v4160_b1_attempt_static.py)及 [JSON ledger](v4160-b1-attempt-static.json)包含完整逐指令與串接證據。

| 完整函式 | 範圍 | bytes／指令數 |
|---|---|---|
| V131 resident 候選 | `[0x64794,0x6498a)` | 502／175 |
| V140 resident 候選 | `[0x6487e,0x64a74)` | 502／175 |

新增合計 **1,004 bytes、350 條指令**，兩份範圍均逐位元組符合原始 sparse HEX，不以補零填補來源缺口。重用 request caller 共 656 bytes、RAM callback setter 共 44 bytes，不重算新增覆蓋，也不提高既有 C 重建覆蓋率。

## 完整本機範圍

函式使用 64-byte frame，保存 RA 與 S0..S7 共九個 word，另有一次 SP+12 spill／reload 包住間接 clock 呼叫。共有 **38 個 store sites**：十個 SP-relative stores（九個保存與一次 spill）、28 個非 frame stores；只有一個普通 RET（+0x18a），沒有本機尾跳。

完整 CFG 有三個等待／重試區域。切除四條邊後為 DAG：+0x34／+0x3e 回 +0x2c、+0x11e 回 +0x11c、+0x1f2 回 +0x1ea。這是語法與路徑證據，不是終止證明。

| call offset | V131 目標 | V140 目標 | 本階段界線 |
|---|---|---|---|
| +0x30 | RAM `0x20002d4c` | RAM `0x20002d98` | 回覆參與 admission，內層語義待查 |
| +0x76 | `0x6434a` | `0x64434` | 明設 `(fresh F+1,0)`；其餘參數為當時值 |
| +0xf6 | RAM `0x20000332` | 相同 | header／copy 分支，request128 略過 |
| +0x12a | fresh `[0x200031e0]` | fresh `[0x20003230]` | 間接呼叫，沒有 null guard |
| +0x152／+0x1ae | `0x63b0e` | `0x63bf8` | 兩條互斥分支呼叫同一 helper |
| +0x1d2 | RAM `0x2000078a` | 相同 | 非128路徑發布 callback literal |

## request `(0,0,128)` 的 admission

令 V131 `F=0x20003540`、`S=0x20003514`、`C=0x20003560`、H slot=`0x2000353c`、R slot=`0x20003508`；V140 對應地址加 80。函式將完整入口 A0／A1／A2 保存到 S7／S1／S6。

只有完整 A2==128 進入 admission sampler：呼叫 RAM service，若 unsigned 回覆 t<=15，立即重試而不讀上限；t>15 才讀 fresh byte F+26，計算 `limit=low32(32*byte-16)`，t>limit 再重試。接受區間為 unsigned `[16,limit]`。

byte=0 時 limit 是 **`0xfffffff0`**，不是 signed 負數或空區間；byte=1 時只接受 16；byte=255 時上限為 8144。每次允許讀取時都重新取 fresh byte，沒有固定 limit、sampler 分布、timeout 或進展證據。接受後才將 160 寫至 fresh H+100。

## 共用配置與 payload 分支

其後共同路徑先把捕獲的 R 物件 word+44 低兩位清除後設 bit0，呼叫 `0x6434a/0x64434(fresh F+1,0,then-live A2)`。返回後重新捕獲 R，對兩次獨立讀取的 word+0 分別做 AND -385、再 AND -385 OR 256 的寫入；另一個 pointer slot 所指 word+8 OR `0x330000`。接著寫 fresh H+80=90、把 F+8／F+12 word 寫至 R+8／R+4、fresh H+4 OR 1、fresh C+14 byte OR 2。各個捕獲指標的相等性都沒有被假設。

payload header／copy 的 gate 是 **`low8(entry A2-1)<=1`**，不是完整 A2 只允許 1／2；257／258 等值也命中。命中時才捕獲 S+32 指標 P，寫 header bytes `low8(A2)` 與 `low8(entry A1)`，再請求 copy `(P+2,entry A0,entry A1)`。

完整128不符合這個 gate，會略過這些 header stores 與 copy，並將保存的 S1 改為 2。因此 request 的入口 A0=0 **不會在這個本機 copy 分支被解參考**；這不證明所有其他動態指標有效或 callees 不保留指標。

共同匯流後，重新讀取 S+32 word，將它發布到 fresh H+112；清 S+2、S+3，設 S+7=3。不能假設這次 S+32 與先前 payload 分支捕獲的是同一個指標。

## request128 的 held-pointer 等待與時間差封裝

完整128接著輪詢剛才捕獲並寫入 +112 的同一個 H 物件 word+100，直到零才離開。**這條迴圈內不重新讀取 H slot**。每次 word 讀取是 fresh，但沒有 timeout、硬體進展或必定歸零的證據。

其後呼叫 fresh clock slot 所指函式，沒有 null guard；A1=2 在 SP+12 保存並於返回後 reload，不能據此宣稱完整 clock ABI 或其他參數已知。令其完整 unsigned 回覆為 T，返回後 fresh C+8 為 B：

- T>=B：`D=T-B`。
- T<B：再讀 fresh word M（`0x20003238/0x20003288`），`D=low32(T+M-B)`。這裡沒有加 1，也未證明 M 是真實 clock modulus。

重新讀取 S+32 指標，向其 word+0 寫入：

```text
low32(((D >> 3) << 24) OR 0x008002ff)
```

也就是只保留 D 的 bits3..10 到最高 byte，與固定低位 OR 合併；不是飽和值，也沒有物理時間單位、monotonicity 或單次 wrap 的保證。

接著呼叫 `0x63b0e/0x63bf8(fresh F+0 bits4..5,A1=2,then-live A2)`。正常返回後，對 fresh R word+0 OR `0x00800000`、word+44 清低兩位，清 S+5／S+1，向 fresh H word+0 寫 2，恢復 frame 並 RET。這條路徑沒有再寫 A0，因此回傳**最後 helper 的當時 scalar**，不能宣稱固定返回 0。

## 其他完整 mode 與 callback 發布

完整 A2!=128 路徑略過 admission；它仍依低 byte gate 決定是否 copy。共同發布後呼叫 channel helper，更新 control，接著呼叫 RAM `0x2000078a`，A0 是 callback literal `0x65de6/0x65ed0`。

重用 first-copy 對應的完整 22-byte setter 證據：將此非零 literal 寫至 `0x20002ef8/0x20002f48`，並向 slot+4 byte 寫 1；setter 本身不修改 A0。這個發布位置不是 C+12。attempt 之後直接清 C+12、S+5／S+1、向 fresh H word+0 寫 2，再持續重新讀 C+12，直到非零才返回。該路徑需要外部 writer／callback 的進展；本階段沒有證明實際 callback 被呼叫。

RAM setter 的來源位元組與候選 first-copy affine mapping 已重新核對，但不代表實際 installed RAM 或開機 copy 已確認。callback 本體與 C+12 writer 仍是後續工作。

## 驗證與尚未證明事項

驗證涵蓋完整 operands、typed loads、QingKe 指令標記、所有七個 call sites、38 個 store sites、frame／spill／唯一 RET、CFG 每條邊及 request128／其他 mode witness。拒絕 **350 個逐指令 mutation、32 個 typed-load mutation**；host scalar 檢查包含 256 個 admission bytes 的 unsigned 邊界、65,536 個 copy gate 低16位值、65,536 個 delta 的 bit 投影與 modular subtraction 邊界。一般與 `-O` 模式精確重放同一 ledger。

完整函式範圍不等於已驗證全部執行效果。所有串接仍要求候選 ISA／API／mapping、有效 code／frame／global／dynamic object／payload extent、callee 對 S／SP／RA／spill 的遵守，以及沒有破壞性 alias、wrap、IRQ／DMA 或重入；fresh snapshots 的相等性須另證。sampler、clock、`0x6434a/0x64434`、`0x63b0e/0x63bf8`、callback 本體、實際 provider 綁定、所有輪詢進展與完整指標保存期仍未證明。

```powershell
python analysis/check_v4160_b1_attempt_static.py
python -O analysis/check_v4160_b1_attempt_static.py
```
