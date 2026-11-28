# v4.1.60：Outer ID6 資源前段的 fallback 保存

接續 [retry 返回與 entry6](v4160-b1-fallback-retry-static.zh-TW.md)。本輪接入 `0x4da70／0x4db08`，入口為 ID=`6`、count=`7`、fallback=`0`，分開核對零資源與名義 heap 中的有效非零配置路徑，停在 parent 下一個 fill48 呼叫前。

檢查器：[check_v4160_b1_fallback_outer_static.py](check_v4160_b1_fallback_outer_static.py)；證據：[JSON ledger](v4160-b1-fallback-outer-static.json)。全程使用原始 bytes／CFG 與封閉整數、區間／frame 證書，沒有執行韌體、建立可變 target heap／RAM 模型、操作硬體、重播或連線 target。沒有增加 C 重建 bytes 或提高覆蓋百分比。

## 入口與零資源分支

Parent 的完整本體為 386 bytes／123 指令，第一個 resources callee 為 160 bytes／55 指令。Parent 先做九筆固定全域寫入，建立 48-byte frame，將入口 ID6 保存在自己的 SP+12，再呼叫 resources。

Resources 從 fresh config64+21 讀取 byte b，計算：

```text
r = b & 3
q = (b & 3) + (b >> 2)，範圍 0..66
```

它先將 r／q 寫入 D+9／D+8。只有 b=`0` 才有 q=`0`；此路直接還原 16-byte resource frame 並 RET，不配置、不 fill，也**不清除舊 pool pointer 或尾端資料區**。

Parent 之後從自己保存的 SP+12 重讀 ID6，將 byte `6` 寫入 `0x20003314／0x20003364`；這個 ID 不取自 resources 或 allocator 的 A0 回覆。零資源是獨立 fresh 值條件，不表示已從先前的名義 APP 設定證明可達。

## 非零資源：先略過已配置的 table block

q 非零時，resources 直接呼叫 core `0x20000040(60*q,0x9001)`。Request 範圍 60..3960，均為 4 的倍數且大於 52，因此選 large list。

本證書採用的名義幾何是前階段 table 配置後的結構，並額外要求它在目前 fresh 取樣時仍保持：

```text
N0 = 14 + 3*q
R0 = roundup4(576 + 6*N0)
B = 0x200045ac：已配置，tag=1，size=R0，next=M
M = 0x200045b4 + R0：free，tag=0，next=E
E = 0x2000b184
free_size(M) = E-M-8
```

Large head 仍是已配置的 B，不能直接當成 M。原指令 CFG 證書核對了先略過 B、沿 next 到 M，再 fit／split 的有限路徑；其中重複的 CFG 節點是靜態路徑證據，沒有執行 target 指令或維護可變 heap。

全部 66 個非零 q 都滿足 free_size−request>8，因此新配置為：

```text
P = M+8
N = P+60*q
配置 header M：size=60*q，tag=0x9001，next=N
新 free header N：size=free_size(M)-60*q-8，next=E，tag=0
accounting 依原 U16 更新規則扣除 60*q+8
```

Header／payload 範圍在名義 owned arena 內，且避開 fallback、timer／task、來源與 metadata。Table 的排除使用每一組實際 N0 範圍，不把小容量的 table 擴大成全域最大 212 entries。

這是目前 fresh header、來源／capacity 關係與 ownership 成立時的條件式幾何；沒有宣稱所有先前呼叫都已無條件保存這些 headers。

## Fill、重讀與 records

Resources 無條件將 allocator 回覆存入 pool word，再以另一次 fresh q 請求 fill。Fill 返回後，又重讀 pool pointer 與 count 才寫 records。因此非零成功證書要求：

- Allocator 確實回傳有效 owned P。
- 配置後與 fill 後的兩次 count 都仍等於 entry q。
- Fill 後重讀的 pool pointer 仍是同一個 P。
- Fill、headers、來源欄位、frames／保存字與必要暫存器均保持所需條件。

在這些條件下，fill 的長度為 `60*q`，每筆 record stride=`60`，初始化 `+2` 半字 `0xffff`、`+4` byte `0`、`+44` word `0`。所有 q 筆寫入均在同一個 `60*q` payload 內。Resource frame 釋放後，尾跳到固定 48-byte fill；該 fill 正常返回才接回 parent。

| 項目 | V1.31 | V1.40 |
|---|---|---|
| Pool pointer word | `0x20003354` | `0x200033a4` |
| Resource 尾端 fill48 | `0x20003358` | `0x200033a8` |
| Resources | `0x4edd2` | `0x4ee6a` |
| 本輪截止 call | `0x4daee` | `0x4db86` |
| 下一個 fill48 的 A0 | `0x20003320` | `0x20003370` |
| 下一個 fill48 的 A1／A2 | `0／48` | `0／48` |

本輪截止時 parent 的 48-byte frame 仍活躍；下一個 fill 尚未執行。

## APP byte14 的條件式例子

若 APP 來源 `0x0e3f` 的高 byte `14` 保持至此，q=`5`；在上述一致的名義來源／capacity／headers 條件下：

| 結果 | 值 |
|---|---|
| N0／R0 | `29／752` |
| Free header M | `0x200048a4` |
| Request／tag | `300／0x9001` |
| Payload P | `0x200048ac` |
| 新 remainder header N | `0x200049d8` |
| 新 remainder size | `26532` |
| Accounting 變化 | `−308` |

來源 literal 的存在不證明目前 fresh 設定值或 heap snapshot 就是這個例子。

## 不納入 null 配置失敗路徑

非零資源分支沒有 allocator-result null guard。即使 fallback=`0` 使 core 不呼叫失敗 callback，或 fill 的 null guard 跳過資料 stores，只要重讀 count 非零，之後 record loop 仍會使用重讀的 pool pointer。因此「fallback 保持零」不能代替「配置成功且 payload 有效」。本證書明確排除這種失敗情況，沒有將它與 q=`0` 的直接 RET 混用。

## 驗證與剩餘邊界

兩版各核對完整 initializer／resources／core／fill 的 strict sparse HEX 來源與既有 identity。356 筆原指令變異、全部 256 packed bytes、66 組非零 split／record 區間、有限 B-skip／M-fit CFG 證書及 exact-byte ledger 都必須通過：

```powershell
python analysis/check_v4160_b1_fallback_outer_static.py
python -O analysis/check_v4160_b1_fallback_outer_static.py
```

所選最深 frame 為 parent48＋resources16＋core16，共 80 bytes；parent 的 ID 保存位置與 resource 子 frame 不重疊。這只是相對 frame 位置證據，實際 owned／不回繞／不別名 placement、保存字與正常存取仍需成立。

所有前階段 source／retry／timer／metadata 條件仍保留，並要求匹配 core／fill／ISA／first-copy、所需 fresh headers／counts／pool 取樣、正常返回、無不利 MMIO／FENCE／IRQ／DMA／reentry／外部 writer 等影響。數值分離不證明物理副作用分離。

結論止於 parent 的下一個 fill48 呼叫前：fallback=`0`、保存的 ID byte=`6`、gate=`5`、task count=`7`。剩餘 parent allocators／getters／records／tail、後續登記 IDs、實際 provider／來源與 headers 保存，以及完整事件消費保留釋放期仍待釐清。
