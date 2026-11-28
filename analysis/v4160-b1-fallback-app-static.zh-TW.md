# v4.1.60：Fallback 保存延伸至 APP 返回與首次登記

接續 [post-config 至 initializer 返回](v4160-b1-fallback-post-static.zh-TW.md)，本輪將條件式 `D+52=0` 保存證書接過 APP builder 的正常返回，再經 setup 呼叫 wrapper，延伸至首次 callback 登記返回的 `0x19b30`。檢查器為 [check_v4160_b1_fallback_app_static.py](check_v4160_b1_fallback_app_static.py)，可重現證據為 [JSON ledger](v4160-b1-fallback-app-static.json)。

這是原始 bytes、完整函式／有界視窗 CFG、operand、固定區間與封閉整數運算的組合證明。保留前一階段所選 shortcut **或** mismatch 路徑的各自前提，並要求符合候選程式／provider、正常存取及返回、fresh metadata 與 frames 保存、無不良別名或其他寫入者。沒有執行韌體、模擬 target 狀態、操作硬體、重播資料或連線 target。

## APP 返回值與寫入範圍

Initializer 已發布路徑以 A0=`0` 返回，所以 `0x19aee` 選取零分支，跳過 `0x19af0` 自旋。`0x19af8` 呼叫完整 leaf `0x19106(A0=64,A1=1)`：

1. 讀 fresh `W=U32[0x40021014]`。
2. 寫回 `W | 0x40`，並以該值作為 A0 返回。
3. 不呼叫其他函式、不建立 frame、不定義 S／GP／SP／RA。

此 leaf 共 30 bytes／12 指令；所選路徑為其中的 OR 分支，另一分支仍由完整 body guard 覆蓋。對任何 32-bit W，bit 6 都會設為 1。因此 APP builder 的正常返回 **必定非零**；這個值是一次 register RMW 的結果，不能當成 initializer 的零回覆或錯誤狀態。

APP 後段不再定義 A0。它還原保存的 RA／S0，寫入以下兩個固定地址，將 SP 加回 96，於 `0x19b14` RET：

| 指令 | 目的 | 寬度 | 值 |
|---|---|---:|---|
| `0x19b08` | `0xe000e104` | 4 | `0x80000000` |
| `0x19b0e` | `0xe000e108` | 4 | `1` |

包括 `0x40021014` 在內的三個寫入區間，在數值上都不碰 V1.31 fallback `0x20003220` 或 V1.40 fallback `0x20003270`。數值分離不等於已證明物理映射或硬體副作用；存取完成、frame／保存字與受保護 RAM 不受干擾仍是必要前提。

## Setup、wrapper 與首次登記

有界 setup 原指令視窗顯示：`0x8ea8` 呼叫 builder；正常返回後，下一筆 `0x8eac` 直接呼叫 wrapper `0x19b16`，其間無指令解讀 builder 的非零 A0。這不證明整個 setup 或 boot 可達。

Wrapper 前綴配置 16-byte frame，在 then-live SP+4／+12／+8 保存 S1／RA／S0，從 fresh slot `0x40080` 取得服務，重新建立 A0=`0x1995c`，於 `0x19b2e` 登記 callback。這三筆 frame stores 要求有效、保存、不別名到 fallback 或其他受保護狀態。

兩版候選的完整登記 leaf 都是 48 bytes／16 指令。其原始 body、candidate slot 與 strict sparse HEX 一致；這項一致性不能證明實際 installed 綁定。

在前階段名義配置與 fresh `count=3`、`capacity=N0`、`table=T=0x200047f4` 保存的條件下：

| 效果 | V1.31 | V1.40 |
|---|---|---|
| Count byte 寫為 4 | `0x2000319d` | `0x200031ed` |
| Callback word 寫為 `0x1995c` | `0x20004800` | `0x20004800` |
| 返回的舊 count | `3` | `3` |
| 返回接點 | `0x19b30` | `0x19b30` |

對全部 67 個 N0（14..212、間隔 3），`3 < N0`，`T+16 <= T+4*N0`，該 word 落在前階段所選配置 payload 內，且兩筆登記 stores 都避開 fallback。Leaf 沒有巢狀呼叫或自身 frame，僅保存 callback 指標，沒有呼叫它。

因此在上述前提下，fallback 的零值保存可延伸至 builder RET，並進一步至首次登記正常返回 `0x19b30`。不把 `count/capacity/T` 的 fresh 值視為已取得的真實快照。

## 驗證與限制

使用原始 APP、兩版 resident candidate、SDK header 的既有 identity guards，以及 candidate sparse HEX 已捕捉區間；缺失 bytes 沒有補零。新證書重用完整 builder（308 bytes）、clock leaf、APP 尾段、wrapper（64 bytes）、有界 setup 視窗及兩版完整登記 leaf，沒有增加 C 重建 bytes 或提高靜態覆蓋百分比。

檢查包含 94 筆原指令 mutation 拒絕、每版 67 個配置區間，以及各 65,536 個 low／high 16-bit lane 的 OR 性質驗證。一般 Python 與 `-O` 都必須通過；ledger 採 exact-byte 比對。

```powershell
python analysis/check_v4160_b1_fallback_app_static.py
python -O analysis/check_v4160_b1_fallback_app_static.py
```

證書止於 `0x19b30`，尚未跨過 wrapper byte-save `0x19b34`、constructor `0x19b56`、fresh `0x40074`、後續 `0x40058` 尾跳／param774 與 RF。實際 provider／安裝來源、fresh fields、硬體／IRQ／DMA 副作用、其他 writers、跨事件消費及完整指標保存與釋放期仍未證明。
