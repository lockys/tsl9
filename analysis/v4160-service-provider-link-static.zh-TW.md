# v4.1.60：service pointer 的條件性設定來源與完整 APP reader

接續 [RAM callback prefix 與前兩次間接呼叫](v4160-ram-callback-prefix-static.zh-TW.md)，本輪追查 service pointer 的來源。APP 把 `0x191c6` 存入 stack 設定第一個 word；兩份 resident **候選**的設定片段在 copy 呼叫返回後，重新讀取複製結果的第一個 word，寫入該 service slot。

這是一條具體但條件性的來源鏈：實際 installed 身分、前置 gates、config pointer、copy 語意與值保存均尚未證明，不能把 service slot 直接標成已安裝的 `0x191c6`。另外完整核對 `0x191c6` 的 90-byte 本體，確認它是帶四個 retry edges 的配對 halfword reader。

分析只讀原 bytes、核對 operands／CFG 與主機端 bit packing；未執行或模擬目標 ISA、MMIO、copy、callback、resident、RAM／frame 或裝置。既有 C 重建 bytes 未增加。

## 178 bytes／53 指令的範圍

| 本體／片段 | 原地址，end-exclusive | bytes／指令 | 完整函式 |
|---|---|---:|---|
| APP stack 設定與呼叫 | `0x19bba..0x19bce` | 20／7 | 否 |
| APP reader | `0x191c6..0x19220` | 90／28 | 是 |
| V1.31 候選 copy／publication | `0x43f8c..0x43fae` | 34／9 | 否 |
| V1.40 候選 copy／publication | `0x44020..0x44042` | 34／9 | 否 |

每個範圍都核對全部 operands、CFG 與 SHA-256。APP 仍為 76,800 bytes、base `0x8000`、SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`；候選、SDK、sparse 與既有指令格式來源合約也遞迴重驗。

## APP 形成 reader pointer，並傳入 stack config

APP `0x19bba` 的 AUIPC／ADDI 以自身 PC 形成 `0x191c6`，接著：

```text
SW formed_pointer,0(SP)
A5=fresh U32[0x40074]
A0=SP
JALR A5                 // link 0x19bce，effective target=raw A5 & ~1
```

這個有界片段沒有 local null guard，也未驗證全部 config 欄位、完整 enclosing function 或 SP 的完整生命週期。

兩份候選的 `[0x40074]` raw word 分別是 V1.31 `0x43f46`、V1.40 `0x43fd2`。它們只建立候選 entry，不能證明原機槽位的實際內容，也不能由此跳過 entry 到 publication 之間的 gates／optional callback。

## 候選片段：copy 呼叫之後才 fresh reload

兩份 publication fragment 的 operands：

| 候選 | copy destination | copy target | publication source word | service slot |
|---|---|---|---|---|
| V1.31 | `0x20003234` | `0x20000332` | `U32[0x20003234]` | `0x200031e0` |
| V1.40 | `0x20003284` | `0x20000332` | `U32[0x20003284]` | `0x20003230` |

呼叫前 A0=destination、A2=16；A1 是 then-live config pointer，片段內沒有重新設定它。AUIPC／JALR 由各自 FLASH PC 精確形成上述 helper target。這是原指令的參數請求，尚未證明 helper 確實複製、正常返回或保存 config。

若該呼叫正常返回，本體重新形成 destination 地址，**fresh LW 第一個 word 到 A3，再 SW A3 到 service slot**。它沒有把 APP 的原 stack register 值直接傳遞成 service pointer。因此即使 entry config 曾指向 APP stack，也仍需確認 copy 行為、原 stack first word、copied first word 與後續 slot 沒被改寫。

兩個 service slot 與先前 callback prefix 的 nominal pointer word 精確相符。這縮小了候選來源，但未知 callee 的 S4／frame／register 保存條件及之後的 writers 仍保留。

V1.40 entry 與對應 publication 不是統一平移：entry 差 `0x8c`，本輪 fragment 差 `0x94`。檢查器分別釘住原 bytes 與目標，沒有用單一版本 offset 推測。

## 完整 `0x191c6` reader：四個 retry edges

原指令只做 halfword loads、整數 shift／compare／OR 與普通 RET；沒有 local store、call 或 stack allocation。其 address operands 為 `0x40002818` 與 `0x4000281c`。這裡只記錄存取地址，不推定硬體計數器語意或副作用。

將前一地址的一次配對讀值稱 H，後一地址的一次配對讀值稱 L：

1. 讀 H 兩次；不同便回到 `0x191ca`。相同的一對記為 H1。
2. 讀 L 兩次；不同便回到 `0x191de`。相同的一對記為 L1。
3. 再讀 H 兩次；不同便回到 `0x191f2`。相同的一對記為 H2。
4. 若 H1=H2，回傳 `(H2<<16)|L1`。
5. 若 H1≠H2，再讀 L 兩次；不同便回到 `0x1920a`。取得相同的一對 L2 後，回傳 `(H2<<16)|L2`。

四個 backward edges 分別是 `0x191d6→0x191ca`、`0x191ea→0x191de`、`0x191fe→0x191f2`、`0x19216→0x1920a`。所有八條 LHU 都另釘 unsigned encoding。

最後 L2 之後沒有再讀 H。本體沒有 retry counter 或 timeout；若某一配對持續不同，無法由這段指令證明終止。兩次連續讀到相同值，也不代表硬體資料永久穩定、兩個 halfwords 原子一致、回傳值單調或符合任意 counter 規格。

即使在額外前提下確認 service slot 指向此 reader，這些限制仍適用；本輪沒有用模擬讀值去替代硬體證據。

## 重播與尚未解除的邊界

[檢查器](check_v4160_service_provider_link_static.py) 與 [完整 ledger](v4160-service-provider-link-static.json)：

```text
python analysis/check_v4160_service_provider_link_static.py
python -O analysis/check_v4160_service_provider_link_static.py
```

一般與 `-O` 模式都逐 byte 重現 ledger，核對四個原範圍的全部 operands／hash、候選 `[0x40074]` words、copy target 與 callback service slot 的接點、reader 的四個精確 retry edges，以及 26 個指定 operand mutations。另檢查 131,072 個主機端高低 halfword bit-packing cases；這不是 MMIO 或 loop 執行測試。

三個較大 callback continuation 的勘查已定位後續更新段與真正的回跳；它們尚未納入本輪指令驗證範圍。接續可展開該段、完整 config gates／copy provider、其他 writers、實際登錄次序，以及硬體與物件／frame 保存合約。
