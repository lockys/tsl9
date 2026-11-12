# V4.1.60 reset copy/clear 與 0x167a6 表來源：離線靜態證據

`verify.py` 只讀取固定映像 `firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin`；長度 76800，SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`，分析位址 base `0x8000`，檔案 offset = 位址減 base。所有記憶體區間以下為半開，表中端點則明示 inclusive。checker 直接比對原始 bytes，完整 pin reset 指令 `[0x186aa,0x186f8)`、128-byte source `[0x1ab60,0x1abe0)`、表函式視窗 `[0x167a6,0x16846)`；精確 hex 在 `verify.py`。既有獨立逐指令審核及 loop 解讀見 [slot provenance](../v4160-167a6-table-slot-provenance/README.md)、[first loop](../v4160-167a6-first-loop-candidate/README.md)、[second loop](../v4160-167a6-dual-table-candidate/README.md)。本 checker 固定 bytes 並計算常數，**不是自動反組譯或語義證明**。

## Reset 的條件推導

已審核指令：`0x186aa/ae` 形成 GP `0x20004000`；`0x186ba/be` 形成來源 `0x1ab60`；`0x186c2/c6` 形成目的及終點 GP+128；`0x186ca..da` 以 unsigned 比較控制逐 word load/store，游標加 4 並回跳。接著 `0x186de..f4` 由 GP+128 起以 unsigned 比較控制 word zero store，終點 `0x2000c958`，每次加 4 並回跳。以該固定 GP 和正常完成為條件，copy 32 words：`[0x1ab60,0x1abe0)` → `[0x20004000,0x20004080)`；clear 8758 words：`[0x20004080,0x2000c958)`。這是固定算術，不是執行 trace；不證明 GP 在其他路徑不變、指令可達、讀寫成功或其他 writer 不存在。

固定來源三個小端 word 對應如下：

| source | destination slot | 複製後的值 |
|---|---|---|
| `0x1abc0` | `0x20004060` | `0x2000c494` |
| `0x1abc4` | `0x20004064` | `0x2000c594` |
| `0x1abc8` | `0x20004068` | `0x2000c694` |

## 兩個 loop 的條件讀取範圍

以下假設各次讀 slot 時仍是上表值，並且程式到達相應 iteration、各次存取有效、呼叫正常返回且沒有其他狀態改變；不是 runtime 觀察或 buffer 大小證明。first loop 每次重讀 slot，key byte offsets 為 `0,2,...,252`（127 次），只在 key 與完整 event 相等時讀 offset+1。第二 loop index `1..35`，offset `7,14,...,245`，兩個表分別讀 offset 與 offset+1；第一個 dispatch 可以改變第二 slot，不能假定一次快照涵蓋兩表。

| slot 初始值 | loop 讀取，inclusive 位址 | 條件 |
|---|---|---|
| `0x2000c494` | key `0x2000c494..0x2000c590`，步長 2；value `0x2000c495..0x2000c591`，步長 2 | value 僅 key 相等時 |
| `0x2000c594` | low `0x2000c59b..0x2000c689`，步長 7；high `0x2000c59c..0x2000c68a`，步長 7 | 每次抵達該表讀取 |
| `0x2000c694` | low `0x2000c69b..0x2000c789`，步長 7；high `0x2000c69c..0x2000c78a`，步長 7 | 每次抵達該表讀取 |

這些潛在表讀取位址全部落在上述 reset clear 範圍內；若 clear 正常完成且其後無任何寫入，這些 byte 為零。這不排除後續初始化、dispatch、別名、非同步或其他寫入，因此不能推斷函式呼叫時的表內容或實際行為；槽自身在 copy 範圍，不在 clear 範圍。

## 重現

```text
python -I -S -B experiments/v4160-167a6-reset-clear-provenance/verify.py
python -I -S -B -O experiments/v4160-167a6-reset-clear-provenance/verify.py
```

可從任意工作目錄以腳本絕對路徑執行。自測含長度截斷與延長、視窗外 hash 變異、每個視窗逐 byte 變異、各視窗截斷、slot 損壞及截斷；無 `assert`，`-O` 仍生效。無 C/target/ISA 執行、模擬、編譯、硬體、網路或設定變更。
