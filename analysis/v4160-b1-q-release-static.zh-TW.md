# v4.1.60：Config private release 的返回、合併與 Q 保存

接續 [RF config allocator](v4160-b1-q-allocator-static.zh-TW.md)。本輪接通 **fresh 舊 C+4 非零**時的直接 private release，核對完整 212-byte／73 指令本體、四種合併寫入足跡，以及返回後的 caller 流程。

結論：private A0 不是固定狀態碼；config 不以它判斷成功。Q 可在明確的 tag／區間／ordinary memory／frame／實體映射與無外部干擾等前提下保存，但實際 matched header、所有權與完整釋放生命週期仍未證明。

## Caller 與完整 helper

Config 的 +0x9e 讀取舊 C+4，+0xa4 的零值分支略過呼叫，+0xaa 直接呼叫 `0x20000110`。正常返回後：

```text
+0xae：fresh 讀 F+0
+0xb2：C+4 = 0
+0xb6／+0xb8：依 fresh flag 的 bit0 決定後續 allocator
+0xca：若有配置，將其回覆重新存入 C+4
+0xce：config 自己的 A0 = 0
```

所以 **清 C+4 不是成功 release 的證據，也不代表函式最後 C+4 一定為零**。後續 allocator 仍可能替換它；判斷配置分支使用 fresh flag，不使用 private A0。

| 項目 | V1.31 | V1.40 |
|---|---|---|
| Private 原始來源 | `0x40380` | `0x403c0` |
| 名義 runtime 入口 | `0x20000110` | `0x20000110` |
| Small-head pointer 槽 | `0x20003194` | `0x200031e4` |
| Limit／sentinel pointer 槽 | `0x2000318c` | `0x200031dc` |
| Large-head boundary 槽 | `0x20003190` | `0x200031e0` |
| Accounting 半字 | `0x200031a2` | `0x200031f2` |

這些 slots 也逐一接回前輪 core 的 small／large／sentinel／account 身分。特別是 private 本體用來限制跨區合併的 boundary 是 **large-head 槽**，不能與 limit sentinel 混同。

完整 helper 沒有 local frame 或 nested call。其 encoded GPR 定義不含 S／SP／RA／GP，但 header stores 是否碰到 caller frame／code／context，仍須單獨排除。控制字保存與唯一正常 RET 前的恢復也有原指令與 dominance 核對；硬體副作用、存取成功或中斷時序不在本輪執行驗證範圍。

## 指標比對不是精確 payload／ownership 驗證

令 P 為入口參數、H 為本次 current、K 為該次讀得的 next。通往 matched 路徑的編碼條件為 unsigned 比較：

```text
H < limit
H <= P <= K
P >= (H+8) mod 2^32
```

這個條件可接受 interior pointer，且包含 P=K 的邊界。不能只因舊 C+4 非零，就把它當成先前 allocation 的精確 P=H+8，或推定 matched H 是預期的原 header。

若要接回前輪配置，還需要同一 H／links／size／tag 的保存、有效遍歷，以及沒有較早節點先符合比對等條件。Search SCC 本身沒有編碼 store 或 nested call；有限終止、節點有效性與 fresh pointer 身分仍未證明。

## 四種 matched 合併足跡

令 J 為 previous header，B 為清 tag 前讀得的 `U16[H+4]`，U 為前合併後的 active header：有前合併時 U=J，否則 U=H。

共同寫入是 `U16[H+6]=0`，以及 accounting 加回原 B。之後的額外 stores 為：

| Previous merge | Next merge | 額外 header 寫入 | 額外 accounting |
|---|---|---|---|
| 無 | 無 | 無 | 無 |
| 有 | 無 | J+0 word、J+4 半字 | +8 |
| 無 | 有 | H+4 半字、H+0 word | +8 |
| 有 | 有 | J+0／J+4 先後更新兩次 | +8、+8 |

前合併另受 H 是否等於 small head、fresh large-head boundary，以及 previous tag 是否為零控制；後合併另受 fresh next 是否為 limit／boundary 與 next tag 是否為零控制。

指令沒有以 fresh next-pointer 暫存器作 store base，使用它的相關操作是讀取；這**不等於 next header 的實際地址從未被寫入**，因為 H／J／next 或實體映射仍可能別名。有效且分離的節點關係須另證，亦不能推定被移出的 header 被清零或 payload 還可安全使用。

從 tag read 起至正常 RET 的局部 CFG 有 32 條語法路徑。Fresh tag=73 排除 counter 分支後剩 16 條，四個合併組各有 9／3／3／1 條。這是 CFG 分類，不是實際可達情形或執行次數。完整本體共 11 個 store 編碼位置，包含固定 control／counter／accounting 寫入。

Counter 僅在 fresh tag **恰為 `0x8001`** 時加一，按 U8 回繞。若同一先前 RF allocation 的 fresh matched tag 仍為 73，就不觸發該 counter；但 tag73 本身不證明 pointer／所有權或成功釋放。

## Private A0 的完整返回來源

在唯一 RET 的逆向定義證書中，A0 可能來自入口值，或本體 +0x60／+0x80／+0x88 的定義：

| 正常返回路徑 | 留下的 A0 |
|---|---|
| Null／未進入 matched 修改的路徑 | 入口 P |
| Matched H 等於 captured small head | Accounting base |
| 不是 small head，但 H 等於 fresh large boundary | 該 boundary 值，即 H |
| 其他 matched 路徑 | Fresh `U16[J+6]`；為零時進入 previous merge |

Next-merge 部分不再定義 A0。零與非零都可能是中間值，不能套用外層 free wrapper 的強制零回覆合約，或當成這個 private 函式的成功／失敗狀態。

## Q 保存的兩類充分條件

第一類是 **未合併、fresh tag73** 的值保存引理。若入口 Q=`0x40025000` 與 tag read 來自同一個一致的 ordinary little-endian byte 映像：

```text
Q 的 bytes：00 50 02 40
原 tag73： 49 00
清 tag：   00 00
```

兩 byte tag 若碰到 Q，起點只能在 Q−1..Q+3。與原 tag73 相容的唯一重疊是起點 Q−1，此時相交的 Q+0 對應 tag 的高 byte，原本與清除後均為零。其他起點與 Q 的已知 byte 不一致。因此，在必要存取正常完成、固定 control／accounting 與其他效應排除不良別名時，這個未合併情形可保存 Q 值；不需要先證 tag store 的數值區間完全不碰 Q。它仍不證明未對齊存取一定成功、H 屬於真正配置或 P 的保存期。

第二類是合併路徑的區間證書：實際被寫入的 H／J header 區間有效、不回繞，且與 Q／caller frame／code 無不良別名，固定 counter／account／control 效應也分離。若這些 written headers 還維持在既有名義 arena `[0x200043ac,0x2000b184)` 內，可同時排除 F 的 32 bytes、C 的 36 bytes 與 Q 四 bytes。

後者能在普通記憶體、mapping、無 IRQ／DMA／重入／其他 writer 等前提下保存 private call 前的 F+0／F+29 等資料，讓後續 **fresh** 分支與前輪 allocator 證書繼續串接；**名義 arena 圖本身不證明當下 H／J 的 ownership 或 snapshots**。如果只證 Q 的值保存，仍不能自動沿用較早的 size／flag 值。

## 加回量與配置／釋放合約

在穩定且不別名的 header／accounting reads 下，private release 的加回量為：

```text
B + 8*previous_merge + 8*next_merge   (mod 2^16)
```

若 matched header 確實來自前輪 R=256 allocation，而且其 size 保持：未分割 allocation 留下 B=256..264，配置扣256；分割 allocation 留下 size256，配置扣264。排除其他 accounting 更新後，配置再釋放的淨變化為：

| 配置來源 | 淨變化，mod 2^16 |
|---|---|
| 未分割 | `B−256+8*(previous_merge+next_merge)` |
| 分割 | `8*(previous_merge+next_merge−1)` |

不能把 release 加回量一律寫成256，也不能僅因完成一次呼叫就推定 accounting 回到原值。這些原指令的封閉數值關係尚未證明實機記帳快照或所有權。

## 驗證與未完成部分

[檢查器](check_v4160_b1_q_release_static.py)與[固定 ledger](v4160-b1-q-release-static.json)保留完整來源／strict HEX／conditional first-copy 接點、返回定義、四組寫入足跡及 tag-lane 證書。檢查包含全部 U16 account 值、四個 merge 組合、九種未分割 size 與分割 size256，共 **2,621,440 個封閉等式**；另核對 65,536 個 tag、256 個 counter 值，以及 60 個 private 原指令與 14 個 caller 接點突變。

```powershell
python analysis/check_v4160_b1_q_release_static.py
python -O analysis/check_v4160_b1_q_release_static.py
```

新增原始 byte 覆蓋為 **0**，APP C 重建覆蓋率不變。仍需追查 fresh H／J／next／tag／size 與真正所有權、非零 fallback、實際 provider／mapping／中間 callees、IRQ／poll 進展，以及完整保留／消費／釋放／通知保存期。

全程離線，僅核對原 bytes／CFG／定義與封閉 scalar、byte-lane、區間關係；沒有目標執行、模擬、mutable target model、硬體存取、封包重放或 target network。
