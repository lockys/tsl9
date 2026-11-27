# 候選 task5 parser：四-byte 訊息、分派表與物件欄位

接續 [APP task 與 task5 登錄來源的區別](v4160-app-task-1995c-static.zh-TW.md)及 [receive／unlink／釋放合約](v4160-message-receive-static.zh-TW.md)，本輪展開候選 handler `0x5352C`／`0x535DA` 所呼叫的 parser。原始目標仍為 ID-2966 V4.1.60 APP、76,800B；兩版 resident 是參考候選，沒有證明是實機 installed provider。

## 完整範圍與原始來源

| 合約 | V1.31 | V1.40 | 合計 |
| --- | --- | --- | --- |
| parser 完整本體 | `0x5E230..0x5E3A8`，376B／130i | `0x5E378..0x5E4F0`，376B／130i | 752B／260i |
| type128 函式表 | `0x6E5EC` 起 45 words | `0x6E7DC` 起 45 words | 360B／90 words |
| 本 parser 使用的七個 veneer | `0x6A700` 相對 offsets 0、4、8、20、24、28、32 | 基底 `0x6A8E4`，相同 offsets | 52B／14i |

每個 veneer 只有一條指令：前六個為無新 link 的直接尾跳，最後一個為兩-byte RET。完整 parser／表格／veneer 的每個 byte，都由嚴格解析的原始 sparse HEX 提供，且與 candidate 完全相同；沒有為不存在的 source byte 指派補值。表格有完整 word operands 與 hashes，但未展開其 45 個 target 本體。

本輪是新增靜態合約範圍，不是 C 重建覆蓋增加量。原 APP、兩候選、SDK raw header 與 Xwchc 來源向量均固定；未執行 target、provider、callback、heap／queue 模型、MMIO 或硬體。

## handler 到 parser 的生命週期

重用 [完整 registered handler](v4160-list-setup-handler-static.zh-TW.md)：bit15 分支呼叫 receive，將 nonnull M 保存在 S1；只有 `(U8[M+0] XOR 128) <= 1` 才呼叫本 parser，精確選出 types 128／129。parser 正常返回後，handler 以保存的 **原始 M** 呼叫 public deallocator；其他 nonnull types 也會嘗試清理。parser scalar 返回值未被 handler 檢查。

前輪的 task5 結論仍需要 fresh gate=0、當時 count=5、matching registration／initializer prefix 和保存條件。靜態 literal handler 被寫入 entry5，不代表 scheduler 已經實際調用它。

parser 對原訊息的欄位讀取全部位於四個 bytes：M+0=type、M+1=reason、U16[M+2]=ID，與前面的 builder 佈局相符。4B 有效 readable message 是涵蓋這些欄位的充分範圍；函式沒有本機 null／length guard。下游 callee 另有自己的存取與保存需求。

## 正常返回碼

| 條件 | 正常返回 |
| --- | --- |
| type128、reason 0～44，表格 callee 正常返回 | 0 |
| type129、reason 5／8／12／19／26／48，lookup 找到物件且所需呼叫正常返回 | 0 |
| 上述六個 reason 的 lookup 返回 0 | 2 |
| type129、reason87 或 255 | 0 |
| 其他 type／reason | 1 |

這些值在共同 epilogue 以 A0=本機 A5 返回；callee scalar 結果除了物件 lookup 的 null 判斷外，沒有作成功狀態測試。返回 0 不表示物理動作、事件送達、callee 副作用或後續 free 成功，也不能證明所有等待都會終止。

## type128：45 項 callable 表

reason 是 unsigned byte，先檢查 <=44，再以 `table + 4*reason` 取 fresh function word；A0 改為 U16[M+2] 後，以 `word & ~1` linked-call。沒有 function-null guard。兩份被捕獲的表格項目都是非零偶數，但實際執行時仍需要正確映射與表格保存前提。

callee 正常返回後，parser 一律設 status0，不轉送其 scalar。前面 threshold 建立的 `(type128,reason0,ID)` 對應表格 index0：`0x5E40E`／`0x5E556`。本輪只固定其入口及參數，尚未展開該 callee；不能由 type 名稱推定產品功能。

## type129：key lookup 與 reason 分支

六個 object reasons 重用已完整驗證的 24B lookup `0x5784A`／`0x5798A`。它從全域 head `0x20003454`／`0x200034A4` 開始，沿 object+0 next，找第一個 fresh U16[object+8] 等於 requested ID 的物件 O；有限鏈表未命中時返回 0。沒有由 ID 自動推得唯一物件、鏈表有限或 O 就是原 threshold 物件。

以下 V0／V4／V8／V20／V24／V28／V32，表示前表 veneer base 的相對 offset。只有尾跳目標與明確重建的參數已證，下游實作及產品意義仍未證；未設定的其他 argument registers 仍可被觀察。

| reason | 找到 O 後的本機動作 |
| --- | --- |
| 5 | 見下段計數流程；之後 V0(fresh O43,fresh U16 O8,fresh O84)，再呼叫 `0x5774E`／`0x5788E`(O) |
| 8 | V4(fresh O43,fresh U16 O8,bool(fresh O76))；正常返回後 SB0 到 O43 |
| 12 | V8(fresh O43,fresh U16 O8,fresh U8 O79,fresh U16 O80,fresh U16 O82)；正常返回後 SB0 到 O43 |
| 19 | fresh U16 O68 非零時，V20(1,fresh U16 O8,取樣 O68)，正常返回後 SH0 到 O68；接著一律 SB0 到 O49 |
| 26 | V24(fresh O43)，沒有其他本機 object clear |
| 48 | V28(fresh O43,fresh U16 O8)；正常返回後 SB0 到 O43 |
| 87 | 不 lookup；將 U16[M+2] 傳給 V32，該 veneer 本身直接 RET，再固定 status0 |
| 255 | 不 lookup、不讀 ID、不呼叫 veneer，直接 status0 |

最大直接 object 存取是 O+280 的四-byte word，因此 284B 有效、適當對齊的 object 範圍是涵蓋本體 object 存取的充分界限，並非已證明的真實配置大小。

所有 fresh reads 都保持各自的時間點。lookup 當下 key 相等，不足以證明稍後 fresh O8 仍等於 message ID；O43／O68 等欄位也不能無條件視為穩定快照。

## reason5：鏈表計數與 U16 回繞

若 fresh `U32[O+280]` 為 0，本機分支跳過 O68 的讀取、加法及 stores，直接進入 V0 與後續 helper；這不限制 nested callees 可能造成的欄位變化。

若 head 非零，本體先令 count=`(old U16[O68]+1)&65535`，沿每個節點的 +0 next 走訪；每見到非零 next，就再加一並截成 U16。鏈表有限且長度 n>=1、欄位保持有效時，最終存入 O68 的值為：

```text
(old U16[O68] + n) modulo 65536
```

若此值非零，呼叫 V20(1,fresh U16 O8,count)，正常返回後才 SH0 到 O68；若回繞成 0，略過該 V20 呼叫。例如 old=65535、n=1 時值為 0。這只是精確的寬度／分支合約，沒有推定 V20 是哪一種實體功能，也沒有替原程式加上溢位處理。

parser 唯一的本機迴圈就是這條 list-next 掃描，沒有長度上限或 cycle detection。有效 finite list 的前提不能從本機 CFG 或回繞算式自行推出。

## 接回 threshold 訊息的條件

若先前 builder 的三種訊息在同 task、有效配置／queue／receive／handler 與欄位保存條件下到達此 parser：`(128,0)` 進 table0，`(129,19)` 進 reason19，`(129,5)` 進 reason5。builder 每次 key／task 都是 fresh read，且配置／送出回覆未被 threshold 檢查，因此不能假定三筆都已建立、送到同 task 或依序消費。

parser 不直接把 M 存入持久欄位；其 object stores 使用 lookup reply 保存於 S0。但 key-only lookup 仍需要 first-match identity／唯一性與保存條件，才能把這些 stores 歸到原 threshold 的同一個 O。table callees、veneer targets、後續 helper 也可能觀察 ambient registers 或保存指標，完整 retention／ownership 合約尚未封閉。

handler 在 parser 返回後才嘗試 free M；需要 parser 與所有 nested callees 保持 handler 的 S1、SP／RA／frame，以及 message／object／heap／global 的有效 nonalias。前輪 same-header release 證明仍只適用於明列的 retained nominal heap 前提；不能把 parser 的 status0 當成 release 已成功的證據。

## 重播

[checker](check_v4160_task5_parser_static.py) · [精確 ledger](v4160-task5-parser-static.json)

```powershell
python -B analysis/check_v4160_task5_parser_static.py
python -O -B analysis/check_v4160_task5_parser_static.py
```

全部 260 條 parser 與 14 條 veneer 指令各有單點變異拒絕；另有 24 個 unsigned→signed 編碼變異與 90 個表格 word 變異。固定的語法路徑見證涵蓋 parser 每一條本機 CFG 邊，包括一次額外 next-link 迴圈。純 scalar 算式核對全部 65,536 個 type／reason 組合、全部 U16 old-count 搭配五組正鏈長向量，沒有建立可變 message／heap／queue 或執行 ISA。

普通／`-O` 模式須與同一 ledger 逐 byte 相符。GitHub 僅發布本輪三份新分析檔；原 BIN、既有工作與 C 重建覆蓋率不變。後續仍需展開 table0 與其他 table callees、veneer targets／後續 helper、副作用與 writers，並確認實際 task5／provider 綁定及完整保存期。
