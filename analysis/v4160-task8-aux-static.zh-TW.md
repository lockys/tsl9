# typeA0 extended payload：兩個暫存區、計數 gate 與返回值

接續 [task8 typeA0 消費端](v4160-task8-typea0-static.zh-TW.md)，本次完整核對 decoder 的 auxiliary callee。兩份參考候選合計 **680 bytes／254 條指令**，全部由原始 sparse HEX 覆蓋，並與候選 bytes 一致。這是條件性的候選程式靜態合約；尚未證明實際 installed provider、演算法語義或執行時保存期，既有 C 重建覆蓋率沒有改動。

| 完整函式範圍（右端不含） | bytes | 指令 |
| --- | --- | --- |
| V1.31 `0x50160..0x502B4` | 340 | 127 |
| V1.40 `0x501FA..0x5034E` | 340 | 127 |

本機 CFG 是 DAG，只有一個普通 RET。以未知 callee 正常返回作為邊的前提，並不代表已證明 callee 終止、配置成功或釋放完成。V140 尾端緊接 task9 handler，不能把它算進本函式。

## 呼叫參數與兩層 gate

已驗證的 decoder 只在 first byte bit7=1 且 U16 長度 L>12 時呼叫：

```text
auxiliary(fresh U16[M+2], 1, P, N=L-12, tail=(P+N) mod 2^32)
```

P 是訊息的 payload pointer；tail 指向最後 12 bytes 的起點。一般函式入口檢查 P 與 tail 非零，否則回覆 2。它透過 RAM service `0x20000A94` 用 ID 取得物件 O；空物件回覆 20。然後以 tag=83 配置 16-byte 暫存區 T；空回覆 19，這些路徑沒有本機 release 呼叫。

取得 T 後，先從 tail 的 bytes 0..3 組成 little-endian U32 計數 C，再讀取 O+40 的 U32 值 U。完整的允許條件是：

```text
(C > U unsigned OR U == 0xFFFFFFFF)
AND
(mode == 0 OR (fresh U8[O+4] & 2) != 0)
```

第一層失敗回覆 2；第二層失敗回覆 1，兩者都經過 T 的 release 呼叫。**即使 C>U，mode 非零時仍須旗標 bit1。** 本次已知 decoder 固定傳 mode=1，所以 flag 檢查始終適用。checker 保留 `U=0,C=1,mode=1,flag=0` 的拒絕回歸案例，避免把遞增路徑誤接到 gate 之後。

## 暫存區內容與呼叫邊界

gate 通過後，以 fill service 清零本函式 SP+0 的 8 bytes；再以 tag=83 配置第二個暫存區 B，request=`low16(N+4)`。第二次配置空回覆 19，並經過 T 的 release。

配置成功路徑按此順序設定實參：

| 呼叫 | 實參／本機用途 |
| --- | --- |
| copy service `0x2000048A` | `(B+4, P, N)` |
| 同上 | `(B, tail, 4)` |
| 同上 | `(T, O+24, 16)` |
| core `0x521E0`／`0x52288` | `(T, B, low16(N+4), SP+0, 8)` |

這些是原指令的實參合約。copy/fill/compare 的實際綁定與全部副作用尚未閉合，core 的名稱或內容也不能僅憑這些參數推定為某種已知密碼演算法。尤其不能由 16-byte 來源直接認定特定 key、認證成功或安全性質。

本次完整涵蓋 L=13..65535 的 65,523 個純整數案例：N=1..65523，第二次 request=N+4=5..65527，故**在這個已知 caller 域不會發生 U16 request 回繞**。一般入口若接受 N=65532，`low16(N+4)` 則為 0；這個值不在本次 decoder 的來源域。

在有效 extent、無 adverse alias、來源保存及普通返回等前提下，B 的寫入區間 `[0,4)` 與 `[4,N+4)` 正好覆蓋 request；tail 的 12 bytes 位於原始長度的尾端。RV32 pointer 相加仍是模 2^32，這些等式本身不證明位址有效、配置範圍或線性區間沒有跨界。

## core、compare 與清理

core 的完整 scalar 回覆 R 保存在 saved register。R 非零時直接走清理並返回 R；不呼叫 compare 或 counter update。

R=0 時，以 copy service 把 SP+0 的 8 bytes 複製到 SP+8，再呼叫 `0x20000442(SP+8, tail+4, 8)`。**只有回覆恰好等於 1** 才呼叫 counter update `0x46308`／`0x463A0`，實參為 `(原 ID, 捕捉的 C)`；其他 compare 回覆改成 1。不能套用 C `memcmp()==0` 的成功慣例，也不能把任意非零都視為成功。

所有走到第二次配置成功之後的本機普通返回路徑，都依序呼叫：

```text
private_release(saved B)   // 0x20000110
private_release(saved T)   // 0x20000110
return saved R            // compare 不等於1時已改成1
```

本機傳入的是兩個配置結果的原值，沒有傳入 caller 的 P 或 tail 作為 release 實參。所有直接 store 都是自己的 frame save；但未知 provider 仍可能寫入、保存或透過別名影響來源，故不能把這段證據升格為「原 payload 不會被修改或保存」。

清理是控制流上的呼叫嘗試。若未知 core 不返回、release 不完成、call-clobber 或 alias 破壞了保存值，完整生命周期結論仍不成立。

## auxiliary 的 19 不等於 handler 的 19

父 decoder 在 auxiliary 返回後只取「零／非零」：

| auxiliary 回覆 | tuple status | decoder scalar 回覆 |
| --- | --- | --- |
| 0 | 1 | 0 |
| 非零（包含 19） | 2 | payload first byte 的 bit6，僅 0 或 1 |

因此 auxiliary 配置失敗 19 **不會直接成為 task8 handler 保存的 R=19**。handler 那條跳過訊息清理與事件 XOR 的分支，仍須從 callback 等其他來源追查。auxiliary 通過也不直接表示後續 delivery、ownership transfer 或原 payload 保存期已成立。

## frame 與仍未證明的保存條件

函式 frame 為 64 bytes，保存槽在 SP+20..63；SP+0..7 與 SP+8..15 是傳給 core、copy、compare 的借用空間，和保存槽不重疊。這只證明本機位移，不證明未知 callee 不保留 stack address。P、tail、O+24、T、B 的更深層保存行為也未完成驗證。

本次另行定位了 other callback `0x4B944`／`0x4B9DC`，但尚未在本階段納入完整可重播合約；接下來應核對其函式表與 release flag 寫入。其後仍需追查 core、物件取得與 counter update 的副作用、其他 writers，以及實際 installed provider。

## 離線重播

[checker](check_v4160_task8_aux_static.py) 與 [證據 ledger](v4160-task8-aux-static.json)：

```powershell
python -B analysis/check_v4160_task8_aux_static.py
python -O -B analysis/check_v4160_task8_aux_static.py
```

檢查涵蓋完整 operands、函式雜湊、每條本機 CFG edge 的到 RET 見證、全部 DAG 路徑中的清理位置、254 條指令變異、12 個 typed-load 變異、可達長度與 pointer 等式、計數／旗標／compare 邊界及父 decoder 串接。路徑見證是條件性的 CFG 資料，不宣稱每條 syntactic path 都可達。

全程只讀本機 bytes、原始 HEX 與 host 純量運算；沒有執行或模擬目標 ISA、crypto、callback、provider、RAM／heap／queue、MMIO 或硬體。GitHub 僅新增本階段的三份分析與驗證檔案。
