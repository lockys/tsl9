# v4.1.60：B1 selector 的直接子函式

本階段核對兩個 resident 候選中的完整 pool search、optional output、unlinked veneer 與三位元組檢查 wrapper，共 **500 bytes、198 instructions**。所有新增 body 的 bytes 均與原始 sparse HEX 一致，並接上[既有 selector](v4160-b1-selector-transform-static.zh-TW.md) 的直接呼叫。

| 函式 | V131 範圍，結尾不含 | V140 範圍，結尾不含 | 每份 bytes／instructions |
| --- | --- | --- | --- |
| pool search | `6b50c..6b55e` | `6b6f0..6b742` | 82／32 |
| optional output | `6b730..6b77a` | `6b914..6b95e` | 74／29 |
| unlinked veneer | `46018..4601c` | `460b0..460b4` | 4／1 |
| check wrapper | `50040..5009a` | `500da..50134` | 90／37 |

[檢查器](check_v4160_b1_selector_callees_static.py) 與[機器帳本](v4160-b1-selector-callees-static.json) 固定完整 operands、SHA-256、CFG、所有 local edges 的語法見證、分支路徑及 Xwchc 原始編碼。這是靜態合約驗證，沒有執行或模擬目標指令，也沒有建立 RAM／NV／worker／provider 狀態模型或呼叫硬體。

## Type 0／1：逐筆比較記錄開頭六個 bytes

`6b50c / 6b6f0(Q)` 保存 Q 至 S2，建立 32-byte frame，index 從 0 開始。每次 guard 都重新讀取 U8 count；未通過時返回該次 count。通過時才重新讀取 pool word，請求：

```text
20000442(pool + 16*index, Q, 6)
```

比對返回非零就返回 index；零則將 index 加一、取 low8，再重新取 count。此處比較的是 **row+0**，先前 selector type 2 比較的是 **row+6**；兩者不能混用。

在一般 callee 正常返回並保存 S registers、SP、RA、saved frame 的條件下，獲准的 index 最大為 254，不會在一次獲准的遞增中 wrap，最多 255 次探查。count=0 時仍會建立 frame，但不載入 pool word，也不解參考 Q。不同次 guard 與上層 selector 的 count 仍可能不同。

串接[既有 comparator](v4160-comparator-tail-static.zh-TW.md) 後，候選 leaf 的正常返回為：六個 fresh byte pair 全等則 1，第一個不等則 0；null pointer 也走返回 1。因而單憑非零結果不能證明記錄或 query 有效。實際 installed RAM binding、控制字及 FENCE 的物理效果仍未證明或執行。

## Optional output：先保留 NV 回覆，再有條件複製六個 bytes

`6b730 / 6b914(index,O)` 先讀一次 count，之後建立 32-byte frame。完整 unsigned index 大於或等於 count，或 O=null，都返回 2。其餘情況請求：

```text
440c2 / 44156(512 + 6*index, 16, SP)
```

完整 NV 返回值保存於 S0。非零時直接傳回；零時再請求 `20000332(O,SP,6)`，忽略 copy 返回，最後傳回保存的零。這個零本身不證明 copy 的目的範圍有效或 NV 實際輸出了資料。

已知的 local stores 只有 saved frame words：SP+20、24、28。傳出的 scratch pointer 為 SP，copy 局部來源為 SP+0..5；**數值參數 16 的單位、NV 寫入 extent、初始化條件與是否保存 pointer 都仍未知**，不能因 saved words 在較高 offset 就宣稱 provider 不會覆寫它們。

實際 B1 dispatch 傳入 selector 的 O=0；在 S2／frame 保存前提下，selector 不呼叫這個 optional output helper。本階段仍驗證其完整一般合約，供其他 caller 追查。

## Type 3：尾跳、三位元組 scratch 與完整返回值

`46018 / 460b0` 各只有一條 `JAL x0`，分別尾跳 `50040 / 500da`，沒有新建 link 或 frame。**V140 入口是 500da；500d8 屬於前一個 body 的最後跳轉**，未納入此 wrapper。

Wrapper 行為依序為：

1. P=null：在建立 frame 前返回 2。
2. 建立 32-byte frame；Q=null：恢復 frame 後返回 2。
3. 請求 `copy(SP+8,Q+3,3)`；fresh 讀取 SP+10，將其改為 `(byte & 63) | 64`，寫回 SP+10。
4. 請求未知 worker `51f78 / 52020(P,SP+8,SP+12)`；非零完整返回值直接傳回。
5. worker 返回零才請求 `comparator(SP+12,Q,3)`，之後返回 `reply != 1` 的 0／1。

第 3 步固定 byte 的 bits7:6 為 01，保留 bits5:0。這個 byte 位於 **本函式 SP+10**，不是直接改寫 caller 的 Q。Xwchc `1c85 / 5c85` 分別固定為此 offset 的 byte load／store，未誤讀為 SP+11。

最後兩條算術指令為 modulo-32 `reply-1` 與 unsigned `0 < result`。因此任意完整 U32 reply 都只有 **reply=1 才得到零**；不能將任意非零 comparator reply 視為成功。在匹配的 boolean comparator 前提下，wrapper 零返回還需要 worker 先返回零與最後三個 bytes 相等。

Copy 的 local scratch interval 為 `[SP+8,SP+11)`；傳給 worker 的輸出 pointer 是 SP+12，最後 comparator 要讀 `[SP+12,SP+15)`；saved words 位於 `[SP+20,SP+32)`。這些 local intervals 互不重疊，但 SP+12..14 **沒有本機初始化指令**。worker 的 output extent、實際輸出與保存條件未展開；不能從其零返回推得輸出已初始化。

上層 selector type 3 呼叫 veneer 的實參為 `(selector_SP,Q)`。所以 worker 的 P 是 selector 暫存區 pointer，不是原始 record base；wrapper 的 Q 才沿用 B1 record+6。wrapper 非零會讓 selector 跳過候選，零才進入下一次 fresh count 檢查。

## Pointer 保存與 NV 分析界線

這四個 bodies 沒有將原始 P／Q／O pointer 直接寫成 global pointer；它們會把 borrowed pointers 傳給子函式。這不足以推出子函式不保存 pointer，也不足以證明完整物件保存期、查詢來源穩定或中斷／DMA／reentry 不介入。

本階段另以唯讀原指令查看 NV wrappers 的入口：read `440c2 / 44156` 將入口 A0／A1／A2 保存至 S4／S1／S2，write `4435c / 443f0` 保存至 S2／S1／S3，之後透過設定物件與 callbacks 分派。入口保存動作本身不能證明長度單位或 callback binding。既有[zero-base cache 生命週期](v4160-zero-base-cache-lifecycle.zh-TW.md) 也不能替代尚未完成的完整 NV 分支驗證。

仍需展開未知 worker、NV read/write 完整 branches、實際 config callback／context writers，以及 provider 對傳入 stack、query、payload 的保存合約。本階段沒有增加 C 重建覆蓋率，也沒有宣稱完成可用韌體或實機功能。

## 可重播驗證

```powershell
& 'C:\Users\locky\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe' analysis/check_v4160_b1_selector_callees_static.py
& 'C:\Users\locky\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe' -O analysis/check_v4160_b1_selector_callees_static.py
```

檢查包含 198 個逐指令 mutations、6 個 typed-load mutations、65,536 組 index／fresh-count 整數條件、256 個 scratch byte 值，以及覆蓋完整 U32 的返回值區間代數。它們是 host 上的 scalar／interval 證書與不可變 CFG 路徑，沒有目標寄存器、記憶體、queue 或 provider 模型。`--write` 只建立新的確定性帳本；一般與 `-O` 模式均逐 byte 比對既有帳本。
