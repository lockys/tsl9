# v4.1.60：linked node 消費、事件寫入與釋放邊界

日期：2026-11-26。延續 [record 建立端](v4160-record-producer-static.zh-TW.md)，核對同一候選 metadata head 的完整遍歷函式、直接事件 helper，以及既有 private free 的原指令來源。[檢查器](check_v4160_linked_node_consumer_static.py) 與 [ledger](v4160-linked-node-consumer-static.json) 固定完整 bytes、operands、條件性 CFG、stores、來源映射及主機算術反例。

**本輪證明候選程式的條件性合約，沒有證明 v4.1.60 實際安裝這組 provider。** 全程讀取本機檔案與計算主機整數；沒有執行或模擬 target ISA、node list、allocator、clock、event buffer、provider、callback 或 MMIO。此靜態檢查點不增加既有 C 重建覆蓋率。

## 完整範圍與執行位址

以下 range 的終點不含在內；無 `0x` 的位址仍為十六進位。

| 候選 | consumer 的 flash source | 條件性 RAM 執行範圍 | event helper |
| --- | --- | --- | --- |
| V1.31 | `4076a..4088a` | `200004fa..2000061a` | `4354a..4358a` |
| V1.40 | `407aa..408ca` | `200004fa..2000061a` | `435d6..43616` |

每版 consumer 為 288 bytes、103 instructions、19 個靜態 store 位址；每版 helper 為 64 bytes、20 instructions、4 個 store 位址。合計 **704 bytes、246 instructions、46 個 store 位址**。consumer 的 10 個 frame stores 包含在 19 個中；helper 的互斥 restore branches 也分別計數，不是執行次數。

| body | SHA-256 |
| --- | --- |
| V1.31 consumer | `ba161fdee5b8033b76abc008a1f3c12c3187cd7394cc1ef567b91a94d9e0c06c` |
| V1.40 consumer | `d07007de1936346526ca0606cae4d7827ba41e93d0b848430a8ad021f60ab476` |
| V1.31 helper | `4ef50e4708a6b1c5ac912c80d17a95724f66d5a0cf7644327399725e928c16bd` |
| V1.40 helper | `ae751e4200fdbceed6610772cc6775a0863ee0a1d92169ff554ad6cda2802f3a` |

consumer 全部位於既有 first-copy 範圍。PC-relative 指令必須用 RAM PC 解讀：`20000550` 的 C.JAL 指向 **`20000110` private free**；`20000584/20000588` 的 AUIPC/JALR 則指向各版 flash event helper。以 flash load-image PC 解讀會算出不同目標。檢查器固定兩組映射與此反例；不能把 flash 反組譯顯示的 call target 當成執行目標。

first-copy 證據不等於完整啟動證據：既有 sparse copy 的末端來源缺口仍保留，不補零，也不推論實際 installed 綁定。

## 同一候選內的 globals

令 metadata base 為 M，config base 為 C=M+80；下列加數是十進位。

| operand 角色 | V1.31 | V1.40 |
| --- | --- | --- |
| M | `2000319c` | `200031ec` |
| C | `200031ec` | `2000323c` |
| head：M+76 | `200031e8` | `20003238` |
| 未知 time-like provider：M+68 | `200031e0` | `20003230` |
| hint：M+16 | `200031ac` | `200031fc` |
| event count：U8[M+1] | `2000319d` | `200031ed` |
| pending-table pointer：M+72 | `200031e4` | `20003234` |
| future-hint gate：C+40 | `20003214` | `20003264` |
| wrap/bound word：C+76 | `20003238` | `20003288` |

不同候選之間的位址巧合不代表共用狀態。clock、deadline、repeat、hint、wrap 等名稱只描述讀寫及算術用途；實際時間單位、硬體效果與物理 mapping 未證明。

## 遍歷、取消與 unlink

函式建立 48-byte frame，保存 RA、S0..S8，讀一次 head，current=head、predecessor=0。若初始 head 為零，直接 epilogue：**不正規化 hint，且 A0 保留入口 ambient 值**。

每筆先用 Xwchc LHU 讀 **U16[current+2] mask**。mask 為零時，此 node 不呼叫 time-like provider 或 event helper：

1. 讀 U32[node+12] 作為 splice next，更新 head 或 predecessor+12。
2. 在共用 release block **重新讀一次** U32[node+12]，存入 S8。
3. A0=current，呼叫 `20000110` private free；正常返回後 current=S8，predecessor 不變。

兩次 next 讀值不能無條件視為相同；unlink store 的 alias、外部 writer 等仍需排除。正常 caller/callee、有效記憶體與 nonalias 前提下，控制流先 unlink 才 release。既有 stop-task 路徑會把匹配 node 的 +2 halfword 清零，因此可串接到這條消費端移除路徑；實際取消時序仍未證明。

private free 的 212-byte 完整合約沿用 transitive checker。兩版 load-image source 分別為 `40380`、`403c0`，RAM 目標都是 `20000110`。它不是 SDK message-deallocate wrapper `431ba/43246`，不能套用 message 的 D−2 marker=255 wrapper 前提。這裡不檢查 free 的 scalar reply，也未證明實際 extent、ownership 或釋放效果。

## 非零 mask：到期判斷與 repeat

非零 mask 先讀 fresh U32[M+68]，於 `20000560` 間接呼叫。沒有本機 null guard，也沒有明確參數設定；ambient registers 可能被 callee 觀察。設正常返回 A0=N；**返回後才 fresh 讀** node+8 為 E1。

以下皆為 32-bit unsigned，算術結果取 mod 2^32，W0、W1、W2 表示不同位置的 fresh wrap-word 讀值：

```text
D = N-E1             if N >= E1
    W0-E1+N          otherwise
event path iff D <= 29999999
```

門檻包含等號：29999999 走 event，30000000 走 future 分支，沒有據此指定時間單位。

event 分支先把 hint 寫零，再 fresh 讀 U8[node+0]→A0、U16[node+2]→A1，呼叫直接 event helper。**helper 返回後不依 scalar reply 分支決定 retain/remove**；接著 fresh 讀 node+4 的 L 及 node+12 的 next：

- L=0：unlink，進共用 block 再讀 next、private free、advance。
- L≠0：fresh 讀 E2=node+8 與 W2；令 u=(L+E2) mod 2^32。若 u<E2（carry）或 u>=W2，newE=(u−W2) mod 2^32，否則 newE=u；寫回 node+8，再把 predecessor 設成 current，current 設為剛讀到的 next。

這是**至多一次條件減法**，不是通用 `% W2`，也不是補追多次事件的 catch-up loop。例如 E2=0、L=100、W2=30 得 70，不是 10。更新以 fresh E2 為基底，並非 N；L、E2、W2、next 皆不能直接沿用 producer 初始值或呼叫前 snapshot。

event reply 雖不直接控制本機 retain/remove，仍可作為 ambient A0 被後續 provider 觀察；不能擴大成「回覆在整條流程中無影響」。

## future 分支與 hint

D>29999999 時，fresh U32[C+40] 為零就不更新 hint；非零則算：

```text
remaining = E1-N         if E1 >= N
            E1+W1-N      otherwise
```

只有 remaining < fresh U32[M+16] 才寫入 hint。這裡沒有初始化 minimum；原 hint=0 時正值不會取代它，因此尚不能宣稱一定得到最早 deadline。這條路徑把 predecessor 設成 current，fresh 讀 node+12 推進。

非空遍歷走到 null 後，fresh h=U32[M+16]；h>1 寫 h−1，h<=1 寫零。初始空 head 會略過。最終 hint/epilogue 不設定 A0，正常返回值是當時仍 live 的 call/arithmetic 值，沒有統一 status/hint 回覆。

完整 consumer 有一個 59-node SCC。所有正常 call-return 邊都依 callee 返回前提建立；沒有任意 list 的終止證明或 cycle bound。consumer 本身沒有包住整個遍歷的控制 word save/clear/FENCE.I prologue，不能從子 helper 的控制讀寫推論遍歷 atomic。

## event helper：設定 pending bit，尚未到 APP callback

raw SDK header 的 `tmos_set_event` alias 是 JT7，slot `40050` 去除 bit0 後對上兩版 helper。helper 無 frame、nested call 或 cycle；先讀/保存控制 word `4002420c`、寫零、FENCE.I，**再**判斷完整 A0 task 與 fresh U8[M+1] count：

- task>=count：恢復控制 word，A0=3；不讀 pending pointer，不寫 event table。
- task<count：fresh 讀 M+72 作為 base，以 base+2*完整 task 計算位址，LHU 舊 pending，與完整 A1 OR，SH 寫 low16，恢復控制 word，A0=0。沒有 pending-base null guard。

consumer 傳入的是 U8 task 與 U16 mask，因此在此 caller 範圍內位寬有明確來源。控制 word 的實際 MMIO/中斷效果未證明。

此 helper 只寫 pending halfword，**沒有直接呼叫 APP 或 arena record callback**。重複 OR 同一 bit 是 idempotent，不是事件次數累加。即使 helper 回覆 3，consumer 的 L=0 node 仍走本機 unlink/free 流程；未看到本機 error retry。外層 event dispatcher 與成功 delivery 還需獨立證據。

## 與 record 建立端的條件性串接

既有 producer 使用同一 head slot，配置 16-byte Q，初始寫 Q+0=0、Q+2=low16(1<<i)、Q+4=入口 A4、Q+8=入口 A2、Q+12=0。若欄位與 globals 保存、實際綁定相符且 event count>0，消費端 task=0、one-hot mask 可落入 pending table。

producer 也把入口 A4 寫入 arena record+8，但那是**另一份 mutable copy**。本輪 repeat 判斷讀 Q+4；[既有 literal0 record handler](v4160-builtin-record-handlers-static.zh-TW.md) 的 callback 清除判斷則讀 fresh record flag。不能把兩份初始相同值當成日後永遠一致，也不能把 node、record、payload 的保存期合併成一個 ownership 結論。

## 可重播驗證與界線

本機依賴：原 APP、兩個 reference-only carrier、raw SDK header、既有 LLVM Xwchc 來源與 vectors。APP SHA-256 為 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`，其餘 identity 由 transitive guards 固定；候選來源位於 `analysis/wch-resident-candidate-2026-10-21/`，並未隨本輪上傳。檢查器 transitive import 另依賴 16 個已發布 Python 檔案。**只有 GitHub clone 而沒有本機候選來源，不能重播全部檢查**。

```powershell
& 'C:\Users\locky\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe' analysis/check_v4160_linked_node_consumer_static.py
& 'C:\Users\locky\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe' -O analysis/check_v4160_linked_node_consumer_static.py
```

兩種模式都應重播 ledger；主機驗證含 65536 wrap-distance cases、65536 bounded-repeat cases、262144 OR cases、65536 task/count pairs、12 個指定原指令單 bit 變異。這些是算術/operand guards，不是 target runtime、整個 list 或 allocator 模型。既有 JSON 不重新封存；本輪 ledger 的 `--write` 僅允許 exclusive-create。

剩餘工作：外層 event 派送到 APP callback 的真實 caller、provider/clock 的 installed 綁定與單位、node/record 的其他寫入者、取消及保存合約、物理 MMIO 效果。所有條件式控制流另需正常 callee-return、SP/S-register/frame 保存、有效指標、無不利 alias 及未建模 writer/interrupt 效果等前提；本輪不把這些前提當成已證明事實。
