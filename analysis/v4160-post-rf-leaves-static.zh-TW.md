# v4.1.60：大型 magic 路徑、後續 leaves 與無界等待

接續 [RF 返回與尾段保存驗證](v4160-rf-tail-return-static.zh-TW.md)，本輪核對大型 `6645c／6659a` 的完整本機結構，封閉額外 magic 前提下的保存與返回合約，並展開後續三個完整 leaves。新增證據包含一個真正的 MMIO 等待迴圈；不能從先前的固定 NOP 計數推定它會結束。

程式：[check_v4160_post_rf_leaves_static.py](check_v4160_post_rf_leaves_static.py)。證據：[v4160-post-rf-leaves-static.json](v4160-post-rf-leaves-static.json)。只解碼原 bytes，檢查 operands／CFG／定義與讀寫集合、frame 及區間等式；沒有執行或模擬 ISA、MMIO、服務、callback 或裝置。resident 仍是兩份候選映像，實際 installed provider 未證明，C 重建覆蓋率不變。

## 完整範圍與證據粒度

| 項目 | V131 起點 | V140 起點 | bytes／指令 | stores／loads |
|---|---|---|---:|---:|
| large | `6645c` | `6659a` | 3388／1032 | 145／159 |
| enable | `67198` | `672d6` | 18／6 | 1／2 |
| wait | `662da` | `66418` | 148／60 | 10／16 |
| final | `6636e` | `664ac` | 56／24 | 6／7 |

large 核對完整 bytes 身分、指令邊界、opcode／load／store census、完整 decode／store operands及本機 CFG，另核對 SP／GP／A5／關鍵S0定義與magic所選stores分類。入口、pointer 定義、控制與 epilogue 共80個指令另有 operand guards；共同組裝段的數值算式由完整 bytes 固定，本輪沒有獨立還原99個 signed DIV 與其餘 packing 的數值公式。三個 leaves 共222 bytes／90指令，全部逐指令核對 operands。

## large：magic 分支接回共同組裝段

large 先配置80-byte frame，保存 RA 與全部12個 S registers。fresh 取 Q=`U32[20003590／200035e0]`，在其保持 `40025000` 的前提下，先做五個有序 fresh RMW，offsets依序 `4,40,44,8,4`。這些寫入發生在 magic 判斷之前。

large+102 fresh 讀 `U32[20003588／200035d8]`，與 `12345678` 比較：

| fresh 值 | 路徑 |
|---|---|
| `12345678` | 跳到+3380，將同一 magic word 寫0，再由+3384跳到+340 |
| 其他 | 從+120續行，在+156開始形成第一個服務呼叫 |

magic 分支**不是直接返回**。它略過+156／+160、+222／+226、+298／+302三組 AUIPC／JALR，三者在 V131 都指向 `20002df2`，V140 都指向 `20002e3e`。這些地址僅是原指令的靜態目標，未證明服務綁定或行為。

共同段先讀既有來源 bytes；+348只將一個 byte-derived 資料存入自己的 SP+8 word。+352重新 fresh 讀 Q到A5；直到 RET 都沒有其他 A5 定義。共同段109個非 frame stores 全是使用A5的word stores，offset集合為 `4,40,44,56,160,164,...,208`。

因此，在額外 fresh magic 前提、所需 Q mapping、正常指令／存取、有效非別名 frame，以及無不利 MMIO／非同步干擾條件下，所選 large 路徑只有：

* 自己的 frame stores；scratch words位於SP+8與+12，與SP+28..79的保存字分離。
* 一次固定 RAM word清零：消費 magic。
* 114個條件式 MMIO store位置：入口5個，加共同段109個。

magic 清零另與前輪 B296、ctx metadata、table／node／task及所需 pointer slots核對區間分離。common 的數值 payload 未還原，不妨礙上述寫入地址及 frame 保存界線；它也不證明校準值有效或硬體動作成功。

完整本機 CFG只有+116的BEQ、三個條件式服務返回邊、+3378的RET與+3384回到+340的跳轉；無本機環。magic 所選路徑沒有callee。+3350..3374還原13個保存字，SP加80後RET。GP從未定義，A0回覆仍為opaque，不能指定成功碼。

若 magic 不相等，本輪只將語意推到第一個 AUIPC之前；尚未封閉服務及其後副作用。magic 寫入者、初始化值、實際可達分支仍是缺口。

## 三個 leaves 的保存合約

三者沒有 frame、callee，亦不定義 RA／SP／GP／S registers或A0／A1，只定義 A2..A5（enable只A4／A5）。總共17個 stores均為條件式 MMIO word stores，沒有直接 RAM 欄位寫入。

enable 只 fresh 取 Q，對Q+4寫 `fresh OR00000100` 後RET。final只取一次fresh Q，依序寫：

| offset | 資料 |
|---:|---|
| 88 | `fresh & fffeffff` |
| 8 | `fresh OR00010000` |
| 12 | `fresh & fffffeff` |
| 4 | `fresh & fffeffff` |
| 12 | `fresh OR00000100` |
| 4 | `fresh OR00010000` |

此處 `ffff0000-1=fffeffff`，清的是bit16。clear／set之間各有fresh read，不能代數相消成硬體還原。

## wait：短路讀取與無界迴圈

wait 有三次獨立 Q loads：+4取Q0、+50取Q1、+106取Q2；+74另取R0=`U32[2000353c／2000358c]`。各次 Q需保持 `40025000`、R需保持 `40024200`，才能沿用下列地址。

前段對Q0／Q1做有序 fresh RMW，包含對Q0+12置bit4、清bit4、四個NOP、對Q1+12再置bit4及對Q1+4置bit12。+82對R0+100寫 **80十進位，即50十六進位**。

唯一循環 SCC是六個offset：`84,86,88,92,94,96`。

1. +84 fresh讀R0+100；為0時直接離開，本次不讀Q1狀態。
2. 否則+88 fresh讀Q1+156；bit8為1便離開。
3. R值非零且Q bit8為0時，回到+84。

loop內只有A5資料定義，沒有pointer槽重載、stores、軟體計數器或timeout。如果每輪R非零且Q bit8為0，CFG容許無限循環；本輪以明確的循環邊集合檢查這個可能性，沒有模擬 MMIO。初始SW80不證明硬體會遞減或清零。八個NOP也不構成有界等待。

離開後再經四個NOP，+106重新取Q2，+112重新讀Q2+156。該值不保證等於loop中的最後一次Q1取樣。後段對Q2+80置bit16，以這個新狀態的低5位更新Q2+80低5位，最後對Q2+8清bit21（`ffe00000-1=ffdfffff`），再RET。

## 尾段可返回的額外條件

前輪條件式 RF 返回後，若本輪large fresh magic相等、所有所需fresh mappings及frame保存前提成立，三個leaves也正常完成，而且wait在某次取樣遇到上述短路退出條件，則四個callees的本機保存合約可接回外層tail。

在相同無干擾條件下，外層tail才會繼續清state、將自己S4中保存的snapshot SW回`4002420c`，還原32-byte frame並RET。這是增加明確前提後的條件式CPU返回鏈；尚未證明 magic 實際可達、硬體事件終會出現、control實際恢復，或整個initializer已返回。

## 可重現檢查與後續

```powershell
& 'C:\Users\locky\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe' analysis/check_v4160_post_rf_leaves_static.py
& 'C:\Users\locky\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe' -O analysis/check_v4160_post_rf_leaves_static.py
```

核對APP／SDK／兩份候選身分及既有證據鏈，一般與`-O`均要求ledger逐bytes相同。兩版合計拒絕324個operand mutations及16個非本輪支援的NOP編碼變體，另檢查完整CFG可達性、large無環、wait精確SCC／繼續等待的循環、frame與pointer保存及mask等式。非支援編碼不等同架構上非法。

下一步追查magic來源及不相等路徑的`20002df2／20002e3e`服務，接續其後組裝／保存合約；實際provider、硬體效果與物件保存期仍未釐清。
