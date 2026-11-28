# v4.1.60：ID7 初始化的預期更新與 ID8 返回串接

接續 [第三池與 parent 返回](v4160-b1-fallback-third-static.zh-TW.md)，本輪把 ID7／count8／fallback0 的所選終點接過第二個 initializer、四個直接 callee、六 byte fill、selector 尾跳與下一次 task 登記。條件成立時，終點為 ID8／count9，停在第三個 outer initializer 呼叫前。

檢查器：[check_v4160_b1_fallback_id7_static.py](check_v4160_b1_fallback_id7_static.py)；證據：[JSON ledger](v4160-b1-fallback-id7-static.json)。全程核對原始 bytes、不可變 CFG、固定區間與整數／frame 關係；沒有執行或模擬目標、建立可變 target RAM／heap／provider／MMIO／IRQ 模型，也沒有操作硬體或 target network。本輪新增 C 重建 bytes 為0，這是保存條件與返回鏈的驗證進展。

## 接通的原函式

| 項目 | V1.31 候選 | V1.40 候選 |
|---|---|---|
| ID7 initializer | `0x46570` | `0x46608` |
| Defaults | `0x45220` | `0x452b4` |
| Vectors A | `0x48c56` | `0x48cee` |
| Vectors B | `0x47eac` | `0x47f44` |
| State | `0x6d682` | `0x6d86e` |
| Selector 尾跳 | `0x4d9ec` | `0x4da84` |

完整 initializer 為68 bytes；四個直接 callee 和44-byte selector 都有原指令、操作數、CFG、store census 與 SHA-256 護欄。Defaults 在 V1.31／V1.40 分別為352／356 bytes、75／76個 stores，各自核對，不能把差異視為單純位址平移。

這些直接 callees 沒有 source loads、linked 巢狀呼叫或 frame，也沒有定義 RA、SP、GP、S registers。Vectors A／B 的 code-pointer stores 只發布指標，沒有呼叫那些 callback。唯一額外服務邊界是 State 尾跳到 `0x2000039c`，以 `(A0,A1,A2)=(G+1456+δ,0,6)` 清零六 bytes；本輪沿用並核對匹配的46-byte 軟體 fill 合約。實際 installed 綁定仍是前提。

## F96 與 record1 有預期變更

令 G=`0x20003000`，V1.31 的 δ=0、V1.40 的 δ=80，F=`G+492+δ`。不能把整段 `[F,F+96)` 宣稱為原值保存：initializer 在 F+94 寫入半字 `0xff00`，little-endian bytes 為 `00 ff`，並在 F+96 寫零；後者已位於 F96 範圍外。

檢查器保護 `[F,F+94)`，另外逐一列出預期寫入。完整固定 store／fill envelope 與 F96 的唯一交集，必須恰為 initializer `+34` 的兩 byte store。

| 預期更新 | V1.31 | V1.40 | 值 |
|---|---|---|---|
| F+94 半字 | `0x2000324a` | `0x2000329a` | `0xff00` |
| F+96 byte | `0x2000324c` | `0x2000329c` | `0` |
| Record1 selector 半字 | `0x2000332c` | `0x2000337c` | `5` |
| Record1 ID byte | `0x2000332e` | `0x2000337e` | `7` |
| Local ID7 byte | `0x200033ac` | `0x200033fc` | `7` |

Selector 將 A1 固定為5後選 record index1，依原指令順序先寫 ID byte7，再寫 selector 半字5。這兩筆是先前 parent 48-byte 區塊中的唯一交集；其餘固定 stores 另列於 ledger，並非只有上表五筆副作用。Local ID7 的位置也不同於先前 saved ID6=`0x20003314／0x20003364`，後者仍在保護範圍內。

通用 selector guard 只檢查 `(A1-4)&65535 <= 3`，但位址計算使用完整32-bit A1。65536個 U16 值中的接受集合為4..7，這不能替任意 upper16 值證明48-byte record 範圍；本輪只串接原 caller 明確載入的 A1=5。

## Pool、callback table 與其他欄位的保存

每個候選有119／120筆固定 store 加 fill envelopes。檢查器逐一排除它們對 fallback F+52、F 前94 bytes、first／second／third pool pointers、saved ID6、resource q／lowbits、resource pool pointer、CB48、role object、task metadata、timer、既有 entry0..7 與 header 的覆蓋。六 byte fill 也使用相同區間檢查。

另對先前264組正配置幾何逐列交叉核對 resource、first／second pool、third pool 的 headers／payload、第三池 free remainder header，以及完整第一張 table payload。q=0 的三組已配置 first small pool 也另行檢查；未配置 first pool 的零案例沒有新增 owner。全部是不可變區間運算，沒有 heap 內容或指令重播。

因此，在原有 fresh metadata、實際匹配程式、合法且不別名的配置與 frame、沒有不利外部寫入等前提下，先前選定的 fallback0、q 來源與 pool／CB48 結果可保留到下一個登記邊界。q>0 先前發布的 callback pointer 保留；q=0 仍承接先前未限定 table 的插入／全滿結果，沒有把那些 fresh reads 變成一致快照或跨事件生命週期保證。

## Frame 與 ID8／count9 終點

Initializer 建立32-byte frame，把入口 ID7、RA 保存於 entry SP−20／−4。Defaults 會改寫 A0，因此 initializer 從 SP+12 重新載入 ID7；不能把 callee 的最後 A0 當成輸入 ID。State 的 fill 尾跳必須沿 carried RA 正常回到 initializer `+22`，並保存 required frame／ABI state。

Initializer 還原 RA、釋放 frame，再以 A0=7、A1=5 尾跳 selector；selector 回覆 A0=0、A1=5，普通 RET 回 outer entry+40。先前 q=0 table 全滿路徑帶來的入口 A1，在此固定 caller 路徑沒有被用來選 record。此階段 outer16＋initializer32 的同時存活 frame 為48 bytes；物理不別名與 saved words 有效仍是前提。

Outer 隨後載入 handler `0x4a808／0x4a8a0`。若 fresh count8、capacity至少14、table pointer仍為 T=`0x200047f4`，registrar 將 handler 寫至 entry8=`0x20004814`，count 更新9，回覆 `(A0,A1,A2)=(8,5,9)`；這筆 entry8 store 是 table payload 內的預期發布。既有 entries0..7 與配置 owners 不受其覆蓋。

終點為 V1.31 `0x6dd4a → 0x4a7d6`／V1.40 `0x6df3a → 0x4a86e`，fallback0、gate5、saved ID6、local ID7、task count9。第三個 initializer 尚未納入本輪串接。

## 驗證與未完成範圍

兩個候選各有10個 strict sparse HEX 範圍核對。檢查器重核先前證據與264組配置區間、1756 bytes／511個本輪原指令護欄、1059組合計變異拒絕，以及65536個 selector 值。正常與 `-O` 模式均須重算，逐 byte 比對 ledger：

```powershell
python analysis/check_v4160_b1_fallback_id7_static.py
python -O analysis/check_v4160_b1_fallback_id7_static.py
```

實際 installed provider／source writers、其他 allocation／失敗路徑、第三個 initializer 及後續 callbacks、IRQ／DMA／重入與硬體副作用、完整跨事件消費／保存／釋放期仍未完成驗證。固定 code-pointer 寫入與條件性普通返回，不代表 callback 已執行或實際啟動順序已證明。
