# v4.1.60：完整 callback、13-entry dispatch tables 與版本差異

本階段完成 callback `55480/5555e` 與兩份 dispatch table 的原始指令／資料證據。新增 **2,322 bytes**：兩個完整本體 2,218 bytes／743 條指令，加兩張 52-byte table／26 個 word；既有 common body、RAM tail、clear 與 C 重建工作不重複計入。

| resident 參考候選 | 完整 callback 範圍，不含尾端 | bytes／指令 | dispatch table |
|---|---|---|---|
| V1.31 | `55480..558a8` | 1064／356 | `6e50c..6e540`，52 bytes |
| V1.40 | `5555e..559e0` | 1154／387 | `6e6fc..6e730`，52 bytes |

完整 SHA-256、分版 literal operands、table words、calls／stores、展開後 CFG 與路徑見 [機器可讀證據](v4160-callback-dispatch-static.json)。以下 `+offset` 是各 callback 入口的相對十六進位位置。

全程離線讀取原始 APP、SDK、候選 bytes 與本機指令參考，未執行或模擬目標 ISA、callback、copy、provider、polling、MMIO、CSR 或裝置。參考候選不代表原裝置已安裝、實際登記或排程這些函式。

## 物件來源與 computed jump

B=`200033b8/20003408`。callback 用 fresh `U32[B+100]` 作 N，**沒有 N null guard**；incoming A0 不是本機物件來源。N 保存於 S0，進入重新派送時不會再次載入 B+100。frame48 保存 RA、S0～S6。

每次派送讀 fresh `U8[N+11]`，計算：

```text
index = (byte + 110) & 255
index > 12：fallback
其他：讀取 table[index]，由 +56 的 JR A5 進入本機 case
```

這個 JR 是內部 switch，不能當作函式返回或 external tail。13 個原始 entries 都不重複，且都落在完整 callback 的指令邊界；256 個 byte cases 中，恰有 `92..9e` 對應 index0..12，其餘 243 個值走 fallback。

| N+11 | index | V1.31 target | V1.40 target |
|---|---|---|---|
| `92` | 0 | `55552` | `55630` |
| `93` | 1 | `5557e` | `5565c` |
| `94` | 2 | `55688` | `5576e` |
| `95` | 3 | `554d8` | `555b6` |
| `96` | 4 | `55720` | `55800` |
| `97` | 5 | `55800` | `558e0` |
| `98` | 6 | `5579c` | `5587c` |
| `99` | 7 | `5583c` | `5591c` |
| `9a` | 8 | `5587c` | `559b4` |
| `9b` | 9 | `554ea` | `555c8` |
| `9c` | 10 | `5563a` | `55720` |
| `9d` | 11 | `555e4` | `556ca` |
| `9e` | 12 | `557e8` | `558c8` |

raw table entries 雖然沒有 target aliases，cases 仍共用 cleanup、fallback、epilogue 與 redispatch blocks，不能拆成 13 個互不相干的完整函式。index 的 unsigned bound 在 computed JR 前成立，table 讀取範圍局部限制為 52 bytes；實際 code／table 未被替換、S4 table base 在 callees 後保存，仍是 runtime 前提。

## 控制圖與等待界線

展開 table edges 後，兩版各有一個 243-node redispatch SCC，以及獨立的三指令 SCC `+3d2/+3d6/+3da`。後者是 **LBU B+124、AND 32、BEQZ back**，在等 byte 的 bit5 設置，不是 pointed word100 polling。

大型 redispatch SCC 內還有其他 local waits：

- case `95`：反覆讀 fresh `U8[B+124]`，直到等於 4，才呼叫 `54322/543ec(N)` 並重新派送。
- 另一個三指令 byte loop 在 `+2ba/+2be/+2c2`／`+2bc/+2c0/+2c4`，同樣等 B+124 bit5。它屬於大型 SCC，而非獨立 component。
- 多條路徑 fresh 載入全域 H pointer，再讀 H+100；非零就回 dispatch。重新進入該路徑時會重新讀 pointer，不能與先前 common body／RAM tail 的固定 snapshot 迴圈混同。

本機沒有能涵蓋這些等待的有限上限或 progress 保證。即使每個編碼 edge 都有語法上的出口 witness，也不代表可行輸入、callee 返回或真實事件一定能讓 callback 結束。

S1 起初是 B，但通知路徑會改成 `20003000`。checker 除了固定 operands，另以 encoded reaching definitions 核對上述 waits 的 S1 仍來自形成 B 的 `+28`，computed JR 的 S4 來自 `+2c` table definition；這些圖證據仍以 live callee GPR／frame 保存為前提，沒有執行暫存器模型。

## 接回 common body、RAM tail 與另一個服務

沿用 [完整 common body 證據](v4160-list-common-body-static.zh-TW.md)，其 code literal 指向本次 callback；本次 callback 也有 `54c08/54cd2(N)` 的直接 call。來源／請求相符不等同實際 callback invocation。

三個 callsites 請求已驗證的 [RAM tail](v4160-constructor-consumer-tail-static.zh-TW.md) `200026ba/20002706`：A0 均為 1、A1 均為 0；case `9b` 的 A2=37，cases `9c/9d` 的 A2=0。它們選中的是 generic **mode1**，不同於 common body 尾跳的 mode0；RAM 本體的 polling、pointed accesses 與 FENCE.I 原指令仍沒有執行。

另一組 RAM service `2000263a/20002686` 有三個 callsites，由 fresh C+3 bit0 gate 控制，C=`20003514/20003564`。先清 C+3，參數為 `(fresh U32[N+80],0,N+20,0)`；第三參數是 S6 保存的 **N+20 指標**，不是 byte 值。

該服務回覆 A0=0 時，才呼叫對應本機 helper，再用另一個 fresh N+11 值決定是否重派送。helper、回覆意義、借用指標與 RAM 服務本體仍未封閉。其候選 load-image 來源與完整合約列為下一階段，不把同一位址當作已證明 provider 語義。

## 通知 scratch 與重讀後的指標

通知 root slot 是 `20002fac/20002ffc`。原指令先檢查初次 root 及 `U32[root+4]` 非零，才建立 frame payload：

| frame 位置 | 本機形成的內容 |
|---|---|
| SP+4 | 2 |
| SP+5 | fresh `U8[N+69]` |
| SP+6..11 | 請求 `20000332(SP+6,N+70,6)` 的目的範圍 |
| SP+12 | fresh `U8[N+20]` |

copy 之後會 **fresh 重讀 root 及 root+4**，沒有再次 null guard 就間接呼叫，A0=SP+4。初次 guard 不能替代後來 pointer／function word 的有效性；copy 也可能改變 globals 或 N。

只有 matching exact-six-byte copy 完成且必要 frame／nonalias／callee 保存成立時，SP+4..12 才是連續九個已形成 bytes。沒有推定 callback 實際讀取 extent、不保存 stack 指標，或 SP+13..15 已初始化。

V1.31 有一個這類 scratch/copy/indirect-call 區段，V1.40 有兩個。通知服務 `6a7d0/6a9b4(U8[N+8],U8[N+69],N+70)` 另有依 case／版本不同的 N+103 gates，不能與間接 callback 或 copy 的保存合約合併。

## 實際版本差異

V1.40 多 90 bytes／31 條指令，並非整體 +222 重定位：

- case `93`：V1.31 在通知 scratch 之前呼叫 `53d98(N)`；V1.40 先做通知，再依另一個 fresh N+103 bit1，選擇 `53e94(N)` 或 `53e4a(N)` cleanup。N+103 的不同讀取不能合成快照。
- case `99`：V1.40 增加另一組通知 scratch、RAM copy、fresh callback reload 與 N+103 bit0 控制的服務；V1.31 使用不同的共用分支連接。
- calls 為 36／40 個 sites，其中一般 loaded-function calls 為 2／3；stores 為 31／34，包括固定 8 個 saved-register frame stores，以及 3／6 個 scratch byte stores。RAM AUIPC/JALR pairs 為 7／8。

因此 checker 分別固定 356／387-row templates 與兩份 table，不以單一位址差合併兩個函式。

## 其他 callback 與存取範圍

case `9e` 先寫 **N+124=3**，再載入 fresh `U32[B+120]` 間接呼叫 `(N)`，沒有本機 function null guard；之後 fresh N+11=`97` 才重派送。N+124 與 B+124 是不同位置，除非另有 alias。

本體還包含 `55330/553fa(N)` 的已驗證 clear 呼叫，以及多個未知 helpers；部分 `63e58/63f42` callsites 沒有重新設定 A0，不能一律標成 helper(N) 或無參數函式。RET 路徑會恢復 frame，但回覆依最後 callee／路徑而定，沒有通用 success status。

選定本機固定 accesses 需要 N 至少 125 bytes、B 至少 126 bytes、C 至少 11 bytes；H 與另一個 R pointer 的 word+100 accesses 需要至少 104 bytes；通知 root 的 word+4 需要至少 8 bytes。較早其他函式的 48-byte R 範圍，不能套用到這次 word+100。callees 可能需要更大範圍。

原指令另含 literal byte address `40022048` 的 AND253 RMW，以及 fresh R+100 的 AND-5；這裡只驗證編碼與局部參數，沒有執行存取、指定板卡／MMIO 身分或宣稱物理效果。table、N、frame、globals 的 nonalias、所有 live registers 保存、實際 provider 與物件／payload 保存期仍需證明。

## 重播與下一步

[靜態 checker](check_v4160_callback_dispatch_static.py) 驗證 743 次 instruction mutations、26 次 tableword mutations、256 個 dispatch byte cases、32 條選定 walks、875 條 edge witnesses、SCC、dominance、reaching definitions 與 exact ledger。正常重播不依賴 temporary inspection 檔。

```powershell
& 'C:\Users\locky\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe' analysis/check_v4160_callback_dispatch_static.py
& 'C:\Users\locky\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe' -O analysis/check_v4160_callback_dispatch_static.py
```

後續仍需展開較大 B+152 consumer `69a22/69b3a`、另一個 RAM service、通知 root／B+120 的 writers，以及 helper 副作用與 polling 進展。對較大 consumer 的入口 prefix 與 table helper 已有只讀定位，但未計入本次完整 callback/table 證據。C 重建覆蓋率沒有改變。
