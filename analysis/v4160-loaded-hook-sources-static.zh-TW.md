# v4.1.60：loaded hook 的兩個來源與另一個登錄表

接續 [setter callers 與 flag writer](v4160-hook-callers-flag-static.zh-TW.md)。本輪把先前第五個 loaded-argument caller 展開成兩個來源，並完整核對四個來源 publisher 與兩個 table registrar。所有 resident 身分仍為**候選**，不據此認定實際 installed provider。

主要結論：A0 不是只有一個來源。fresh byte `[S0+11]` 選擇兩個 pointer slot；接著另一個 fresh byte `[S1+12]` 決定走 hook setter 或另一個 table registrar。這個 gate 不是 A0 的 null guard。來源 publisher 只能在前置 callees 正常返回、存取成立後建立固定值，不能單憑它們的存在保證 consumer 已讀到該值。

全程只解碼原 bytes、核對 operands／條件 CFG，以及做主機端地址與 predicate 算術。未執行或模擬目標 ISA、callback、RAM、stack、resident、CSR、ECALL 或硬體；既有 C 重建 bytes 未增加。

## 範圍：六個有界片段與六個完整函式

| 範圍 | V1.31 FLASH，end-exclusive | V1.40 FLASH，end-exclusive | 每份 bytes／指令 |
|---|---|---|---:|
| 選擇與 primary source | `0x412ae..0x412d0` | `0x412ee..0x41310` | 34／11 |
| alternative source | `0x41326..0x41336` | `0x41366..0x41376` | 16／5 |
| byte-zero bypass | `0x41336..0x41342` | `0x41376..0x41382` | 12／4 |
| 完整 table registrar | `0x43b28..0x43b3e` | `0x43bb4..0x43bca` | 22／8 |
| 完整 alternative publisher | `0x5a004..0x5a026` | `0x5a14c..0x5a16e` | 34／11 |
| 完整 primary publisher | `0x61b1c..0x61b5a` | `0x61c06..0x61c44` | 62／18 |

合計 360 bytes／114 指令。前三項共六個有界片段、124 bytes／40 指令；後三項共六個完整函式、236 bytes／74 指令。不能把前三項當成完整 enclosing callback。

前三個片段依已核對的 first-copy 映射搬至 RAM；其 branch、JAL 與 AUIPC／JALR targets 同時在 FLASH 與 RAM 座標核對。source publishers 與 registrar 使用 FLASH 座標。每個視窗的 bytes SHA-256、完整指令 operands 與 CFG 都保存在 ledger。

APP 仍為 76,800 bytes、base `0x8000`，SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`；候選、SDK、sparse 與既有來源指令格式合約也遞迴重驗。

## 兩個 slot 由 selector 選擇

片段開頭先將 then-live S0 寫到 `[then-live S3+164]`，再讀 `[S0+11]`。S0／S3 物件身分與 alias 關係仍是前提。

| selector | 寫入 `[S0+14]` 的 byte | A0 fresh word 來源，V1.31 | A0 fresh word 來源，V1.40 |
|---|---:|---|---|
| 等於 1 | `208`，即 low8(-48) | `0x200034fc` | `0x2000354c` |
| 其他 byte | `193`，即 low8(-63) | `0x200034f4` | `0x20003544` |

alternative 片段載入 A0 後直接跳到 primary 片段的共同 gate，沒有先呼叫其他函式。共同指令 raw halfword `0x24dc` 經已保存的官方 LLVM Xwchc 格式來源確認為 **QK.C.LBU A5,12(S1)**，並非 stock r2 顯示的浮點 load。它只改 A5，保留剛載入的 A0。

同時核對 `0x3438` 為 QK.C.LBU A4,11(S0)、`0xa47c` 為 QK.C.SB A5,14(S0)。這些語意仍依明列的條件性 Xwchc ISA profile。

- gate 非零：JAL 到候選 hook setter，mapped target=`0x2000078a`。沒有檢查 A0 是否非零，因此來源 slot 為零時也可能把零交給 setter。
- gate 為零：設 A1=0，走下述另一個 registrar。A0 在呼叫前保留選出的 raw pointer。

兩條 call 在正常返回與保存條件成立時，匯入同一個外部 continuation cut：FLASH `0x412d0`／`0x41310`，兩者 mapped RAM 均為 `0x20001060`。後續中段未在本輪驗證。

## primary source 的完整 publisher

V1.31 `0x61b1c`／V1.40 `0x61c06` 各先配置 16-byte frame、保存 RA，直接呼叫 `0x55bde`／`0x55d1e`。只有該呼叫正常返回且 SP／保存字等前提成立，才有後續三個 pointer stores：

| 候選 | 第一個額外 store | 第二個額外 store | 本輪 primary source store |
|---|---|---|---|
| V1.31 | `[0x20003470]=0x6089a` | `[0x20003474]=0x609de` | `[0x200034fc]=0x61234` |
| V1.40 | `[0x200034c0]=0x60984` | `[0x200034c4]=0x60ac8` | `[0x2000354c]=0x6131e` |

本體之後 SP+=16、普通 RET。前置 callee 的副作用、這些 callback 本體及 publisher 的實際可達順序未解除。

## alternative source 的完整 publisher

V1.31 `0x5a004`／V1.40 `0x5a14c` 各配置 16-byte frame、保存 RA，依序直接呼叫：

| 候選 | 第一個 callee | 第二個 callee | 兩者返回後的 store |
|---|---|---|---|
| V1.31 | `0x60856` | `0x58ef2` | `[0x200034f4]=0x595b8` |
| V1.40 | `0x60940` | `0x5903a` | `[0x20003544]=0x59700` |

接著 SP+=16、普通 RET。這證明候選本體有具體 publication 指令；要把後續 A0 認成這個固定 callback，還需要該 store 確實先發生且直到載入時都沒有被其他 writer 改寫。

## gate 為零時的另一個 table registrar

mapped bypass 的 AUIPC／JALR target 是 `0x43b28`／`0x43bb4`，並不是 hook setter。完整 registrar 的 local contract 是：

```text
if unsigned A1 > 4:
    RET
SW A0, table_base + 4*A1
RET
```

table base 分別為 `0x200031c8`／`0x20003218`。本輪 bypass 明確設 A1=0，因而條件性寫入第一個 word；它們與 hook slot `0x20002ef8`／`0x20002f48` 不同。registrar 沒有本機 hook-slot store、flag store、call 或 stack allocation。

所以 gate-zero 也是保存 raw pointer 的一條路徑，但寫到另一個 table。這不證明 table 的 consumer 曾呼叫它，也沒有建立 referent 的配置、保存期、copy 或 payload ownership。不能把兩種登錄寫成同一個 provider 合約。

## 重播與界線

[檢查器](check_v4160_loaded_hook_sources_static.py) 與 [完整 ledger](v4160-loaded-hook-sources-static.json)：

```text
python analysis/check_v4160_loaded_hook_sources_static.py
python -O analysis/check_v4160_loaded_hook_sources_static.py
```

兩種模式都逐 byte 重現 ledger，核對所有原 operands／hash、雙來源 CFG 的唯一 continuation cut、三個關鍵 WCH encodings、65,536 組 byte selector／gate 的主機端分支分類、五個 registrar word positions，以及 52 個指定 operand mutations。分支分類不是實際值可達性的證明；物件 alias 或 writer 可能使 byte 值相依。

本輪尚未完整驗證 RAM callback `0x20000d50`；此次定位顯示它含更多分支、間接呼叫、迴圈與不同出口，不能以早期 RET 當作整體結尾。接續可追查它的入口算術與後段、四個 source callback 本體、publisher 的實際 callers／先後及其他 slot writers。實際 installed provider、ECALL 路由與物件／frame 保存期仍待釐清。
