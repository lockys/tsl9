# v4.1.60：APP callback 表的取消、登記與兩個 callback 合約

日期：2026-11-26。接續 [初始化尾跳與硬體 leaf](v4160-init-tail-hardware-static.zh-TW.md)，展開其 `90b0`／`9124` 呼叫，並固定 `176a0`、`178f8` 的完整原指令。[檢查器](check_v4160_app_callback_records_static.py)／[ledger](v4160-app-callback-records-static.json) 保存每條操作數、完整 hashes、條件性 CFG、direct stores、indirect tail exits 與實參串接。

**APP 服務會先修改本機記錄，再向 provider 提出事件／計時請求；本體沒有失敗後回滾。delay 換算先截32位乘積再除625；retry byte 也會回繞，不能宣稱無條件最多重試四次。** Provider 自己是否改寫同一區域、實際成功與保存期仍需另外證據。

全程離線讀本機 bytes、解碼及主機整數算術，沒有執行或模擬 target ISA、callback table、provider、timer、payload 或 MMIO。原 BIN、舊 ledger、C 原始碼不改寫，C 重建覆蓋率不增加。

## 四個完整本體

位址為十六進位，range 終點不含。

| 本體 | range | bytes／instructions／stores | SHA-256 |
| --- | --- | --- | --- |
| cancel | `90b0..9124` | 116／45／5 | `6ae3c32faae25ccd27fea46de4a04b6246489daafb5f1fa0d9ede512e65f2b31` |
| register/schedule | `9124..9250` | 300／115／14 | `45dd01a76fedc4bd8d01fdb7ff005f410166a68f171d52420d19da2cbba2e992` |
| retry callback | `176a0..176f8` | 88／30／3 | `8411c1a832677e340569a880397508fbe62ff7016d7d17b52856dfe3b856cd6d` |
| packet callback | `178f8..17948` | 80／29／4 | `ee37bb82ebc75f0273397af864811a63fc953c51f06cc26d57a76156e2e78077` |

合計 **584 bytes、219 instructions、26個靜態 memory-store 位址**，含 frame stores，不是執行次數。每條 boundary／opcode／operand／target 固定並另核對全 body hash；新增 DIVU、SLTIU 的欄位解碼，仍以明示條件性 RV32M／既有 ISA profile 解讀，未證實體支援。

`910e`、`917e`、`91fc` 的 `JR T1` 均列為**外部間接 tail**，不是本機 `JR RA`。其餘正常 call fallthrough 也只是假設 callee 正常返回，不推定副作用或成功。

## APP 的15筆表與欄位

三組 PC-relative operands 共同得到 base=`2000be08`，stride=12，掃描 index=0..14，end-exclusive=`2000bebc`。只有必要的 register／frame／table 保存與有效存取前提下，才能把 scan index 對上後續寫入地址。

| offset（十進位） | 原指令用途 |
| --- | --- |
| +0 | mode byte；本輪 stores 不初始化 +1..3 |
| +4 | 完整 callback/key word；零作為可選空位 |
| +8 | 保存入口 A3 的 word；舊值非零時可能傳給 `[40068]` |

這是 **APP 的15筆表**，不是前輪候選 resident 的16筆 arena。相同步距12不代表同一物件、同一任務或相同 ownership。記錄 callback/key 為零沒有本機拒絕 guard；不能額外假設每次傳入非零函式指標。

## `90b0`：先處理舊 word，清欄位，再尾跳 stop

以完整入口 A0 比對，取第一筆 U32[R+4]==A0。找不到時，恢復 frame 後本地返回1。命中時：

1. fresh 讀 R+8，非零才呼叫 fresh `[40068](A0=該word)`；不檢查 scalar reply。
2. 重建 index offset／one-hot；fresh 讀 U8[GP+166] 作 task。
3. 依序 SW0 至 R+4、R+8；**保留 R+0**。
4. 恢復 S0／S1／RA／SP，`910e JR T1` 尾跳 fresh `[4005c](task,low16(1<<i))`。

header 對應 `tmos_msg_deallocate`／`tmos_stop_task`；候選槽位 word 重新核對，但不因此證明實機 provider、舊 word 的合法 payload/marker、deallocate 或 stop 成功。命中回覆是 tail 的 raw A0，本機不轉成固定布林。清表發生在 stop 回覆之前，本機沒有回滾；provider 自身仍可能改表。

只處理第一筆相等記錄，未證明沒有相同 callback 的其他記錄，也不應說取消必然清除所有相同 key。

## `9124`：零 delay 快路與一般路徑

入口 A2=0 時，先掃第一筆 R+4=0，**不先搜尋相同 callback**。找到空位就依序寫 R+4=入口A0、U8[R+0]=0、R+8=入口A3，形成 one-hot，fresh 讀 GP+166，恢復 frame 後由 `917e` 尾跳 fresh `[40050](task,mask)`。此路沒有 provider 回覆轉換。若15筆都非零，仍會落入一般流程，不立即返回。

一般流程保存入口 A1／A2／A3，先找第一筆 R+4==入口A0：

- 命中：若 old R+8 非零，先呼叫 fresh `[40068]`，不測回覆；其後只寫 U8[R+0]=low8(入口A1)、R+8=入口A3，**不重寫 callback word**。
- 無匹配：重掃第一筆空位，依序寫 callback、mode byte、A3 word。
- 仍無空位：本地返回1。

空位是表項選擇，這裡沒有 heap allocation。mode／R+8 與 callback word 的寫入先後也沒有構成 atomic publication 證明。舊 R+8 的 ownership、各 provider 是否改動 table/frame、指標有效性與外部 writer 都保留前提。

### provider operands 與回覆差異

兩條一般命中路徑都形成：

```text
task     = fresh U8[GP+166]
mask     = low16(1<<index)              # index0..14，需 scan/context 前提
duration = uint32(entry A2 * 1000) / 625 # unsigned DIVU；先截乘積
```

完整入口 A1 非零時，退框後由 `91fc` 尾跳 fresh `[4022c]`（header JT126 `tmos_start_reload_task`），raw A0 直接回到外層。完整 A1 為零時，在 `922e` call fresh `[40058]`（JT9 `tmos_start_task`），再 SLTIU：

```text
wrapper A0 = (provider A0 == 0) ? 1 : 0
```

不是「provider回零，所以wrapper也回零」。另一條零-delay event tail、reload tail、找不到空位的返回又不同，因此不能替整個函式套統一 status 語義。

mode 分支使用**完整入口 A1**，表中卻只保存 low8。例如 A1=256 會寫 mode byte0，仍選非零 reload 路徑；不能由 mode byte0倒推一定走 one-shot。duration 也不是無界算術：A2=4294968 時，乘積截32位後為704，除625得1。本文未指定物理時間單位。

## 初始化與 retry 的實際 caller

前輪 `17bb0` 明確呼叫 `9124(176a0,0,100,0)`。若找到相同 callback 或可用表項，請求參數才是 fresh `[40058](fresh U8[GP+166],one-hot,160)`；outer `17b92` 不使用 wrapper 的布林回覆，而是重讀 GP+378。

這裡的 task byte **GP+166** 與 `17bf6` 登記 `176f8` 後保存 task 的 **GP+379** 不同。沒有兩者 runtime 值相等的證據，也不能把同一 callback literal 或 provider 名稱當作 delivery 證明。

## `176a0`：兩 byte stack payload 與回繞的 retry counter

callback 建32-byte frame、SH `62b5` 至 SP+12，明示初始化兩 bytes `b5 62`。`176c4` 直接呼叫 `1753a`，設定的 register operands 為：

```text
A0=b562, A1=21 decimal, A2=15 decimal,
A3=SP+12, A4=2, A5=17666
```

這是將本機 stack pointer 與 callback literal 傳給未知 callee。`1753a` 是否複製 payload、保留 pointer、何時呼叫 `17666`，以及 frame 退回後的保存期尚未閉合，不能把2-byte初始化當作傳送完成或 ownership 移交。

只有 `1753a` 的 scalar A0=0 才繼續：fresh 讀 U8[GP+377]，u=(byte+1)&255，寫回該 byte；u<=4 才要求 `9124(176a0,0,500,0)`。若表項條件成立，後者的 provider duration operand 為800。

符合重排條件的舊 byte 值是 **0、1、2、3、255**；255回繞成0仍重排。其他 writers／重新初始化也未知，因此不能概括為無條件最多重試四次。非零 transmission reply 原樣離開；零而不重排時保持0；重排時則留下 `9124` 的 then-live A0，沒有統一 callback status。

## `178f8`：7-byte stack payload 的 fresh RMW

建立32-byte frame，呼叫 fresh `[40048](SP+8,0,7)`，沒有本機 null guard。正常返回後依序 fresh 讀值並寫回：

```text
SW ((U32[SP+8]  & 3ff)  | ff000c00) -> SP+8
SH ((U16[SP+12] & e000) | 1f00)     -> SP+12
SB ( U8[SP+14]          | 80)       -> SP+14
```

然後 `1793e` call `1787c(A0=SP+8)`，不測 scalar reply，正常返回後退框。三筆 payload stores 合計覆蓋7 bytes；未知 fill 回覆後各次讀值不能先當成零。`1787c` 的 copy／pointer retention／ownership 與 callback 保存期仍需展開，本輪沒有執行或建立 payload memory model。

## 可重播與界線

```powershell
& 'C:\Users\locky\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe' analysis/check_v4160_app_callback_records_static.py
& 'C:\Users\locky\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe' -O analysis/check_v4160_app_callback_records_static.py
```

兩模式精確重播同一 JSON；guards 使用 RuntimeError，不依賴 `-O` 會關閉的 assert。主機驗證含65536組 bounded duration／halfword算式、全部256個 retry bytes、overflow／full-mode／reply邊界，以及17個指定原指令單 bit 變異須在預期 guard 失敗。這些不是 callback-table、timer、register machine 或 target memory 模型。

發布前核對22個 transitive Python dependencies 與 GitHub main blob 身分。完整重播仍需要固定 APP、本機候選 carriers／HEX、34個 sidecars、saved reader、raw SDK header 及 LLVM Xwchc sources/vectors；只有 clone repo 不足以完整重播。沒有下載、安裝、啟動服務或上傳候選來源。

本輪只發布新 checker、ledger、本文，保留原 BIN、舊分析與本機 Git index。`176f8` 雖已定位為登記的 event consumer，本輪不把它算入完整解碼範圍；後續還需展開它、`1753a`／`1787c`／`17666`，以及實際 task ID、provider words、其他 writers 與 record/payload 保存合約。
