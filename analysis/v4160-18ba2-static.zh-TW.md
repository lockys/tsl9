# v4.1.60：18BA2 靜態記錄合約、位址與返回指標

2026-11-26。接續 [112-byte 工作區與 14 次呼叫](v4160-work112-cpu.zh-TW.md)，本批只靜態核對完整 `[18BA2,18CA4)`，包括第一個 RET 後仍可達的分支區段。**沒有執行或以 ISA 解譯器模擬這段 MMIO 本體，也沒有讀寫任何設備位址。**

原 decoded APP 長 76800 bytes、基址 8000，SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`。既有 `src/native/receive/filter_program.c` 已重建本段；本批增加 operand／CFG guard 與記錄位址清單，不修改 C、共享 CPU、原 BIN 或 seal，不增加 C 覆蓋率。

成果：[靜態 checker](check_v4160_18ba2_static.py) · [完整 JSON ledger](v4160-18ba2-static.json)。只需標準庫與原 APP，沒有 SDK carrier、工具下載或網路依賴。

## 79 條指令與封閉 CFG

checker 對 258 bytes 解碼出 79 條 RV32IMC 指令，逐項保留 PC、原 bytes、operands、控制流 edges，並確認：

- 所有直接邊都落在本段的已解碼指令邊界。
- 36 條結構路徑均由入口到 `JR RA`，沒有迴圈、外部邊或額外呼叫；全段 bytes 都由結構可達指令覆蓋。
- 寫入的 GPR 集合恰為 x11..x16，即 A1..A6；沒有修改 A0、RA、SP、GP、T 或 S 暫存器。
- record load 的位址、寬度、destination register，以及 MMIO store 的 base、source register、offset 均由指定 operand guard 核對。

這是靜態結構及讀寫意圖，不是動態 trace、MMIO 成功、例外處理或實際路徑可達性的證明。record 欄位與 MMIO 讀值仍必須在相關存取時有效；並未為設備建立可執行模型。

## 指令要求的讀／改／寫位址

令 R=入口 A0、I=U8[R+10]、M=`1 << (I & 31)`，所有 word 位元運算採 32-bit。

| 位址 | 原指令要求的操作 |
|---|---|
| 40006600 | 入口新讀 word、OR 1、寫回；返回前另一次新讀、AND FFFFFFFE、寫回。 |
| 4000661C | 入口附近新讀、AND ~M、寫回；稍後只有 U32[R+16] **完整等於 1**，才再讀、OR M、寫回。 |
| 4000660C | U8[R+12]=0 時讀／清 M／寫；=1 時讀／設 M／寫；其他 byte 不存取此 word。 |
| 40006604 | U8[R+11]=0 時讀／清 M／寫；任意非零 byte 時讀／設 M／寫。 |
| 40006614 | U16[R+8]=0 時讀／清 M／寫；=1 時讀／設 M／寫；其他 halfword 不存取此 word。 |
| 40006640+8×I、再 +4 | U8[R+12]=0 或 1 才寫兩個資料 word，packing 如下表。 |

入口 4000661C 的 clear 在 record scale／mode／FIFO 分支之前；晚段 enable 另讀同位址。返回前對 40006600 的新讀與 clear 也不是把入口 snapshot 寫回，不能稱為恢復原 control word。

表內只記錄原指令的數值位址與意圖，沒有據此認定硬體型號、register 實體名稱、有效 bit、設備接受結果或中斷原子性。所有 MMIO read 都應視為各自當時的未知值，不能假設前後讀值相同或普通 RAM 的寫回語意。

## mask 與資料索引的範圍不同

RV32 `SLL` 的 shift count 使用低 5 bits，所以 mask 公式含 `I & 31`。資料位址則使用 **未遮罩的完整 I** 左移 3；本段沒有 I 上界判斷。

例如 I=0 和 32 的 mask 都為 1，但資料位址相差 100（十六進位）。I=255 時，兩個數值位址為 40006E38、40006E3C；這不表示硬體支援該索引或位址。

先前 `128FE` 已驗證的 caller 只產生 I=0..13，對應資料寫入的半開區間 `[40006640,400066B0)`，每筆兩個 word。此為 caller 有界範圍，不是從本段推得的設備容量或所有 caller 的索引保證。

## 兩種 halfword packing

令 H0=U16[R+0]、H1=U16[R+2]、H2=U16[R+4]、H3=U16[R+6]：

| U8[R+12] | 第一個資料 word | 第二個資料 word |
|---|---|---|
| 0 | H1 OR (H3 << 16) | H0 OR (H2 << 16) |
| 1 | H1 OR (H0 << 16) | H3 OR (H2 << 16) |
| 其他 | 無資料 word store | 無資料 word store |

scale=0 時的 record halfword 讀取順序是 R+2、+6、+4、+0；scale=1 是 R+2、+0、+4、+6。兩條分支的第一個資料 store 都先於最後一個 halfword load；ledger 保留每條 CFG 路徑的 memory-site 順序，沒有將它改成一次 record snapshot。

U8[R+12] 只讀一 byte，U32[R+16] 則比較完整 word；後者 257、80000001、FFFFFFFF 等雖低 byte 或 bit 含 1，仍不符合 enable 條件。R+13..15 沒有作為獨立欄位讀取。

## 三種已知 literal 的 42 筆靜態合約

checker 同時固定先前 `1293C..1298A` 產生器 bytes，依已驗證的記錄布局，以三個原 APP literal 建立 3×14 筆 record ledger：selector 0 的 96 bytes、selector 1 的 94 bytes、selector 2 的 106 bytes。

這些靜態樣本沿用**112-byte zero fill 與 exact n-byte copy 成功**的明示前提；不是本輪執行服務。每筆 ledger 含完整 record bytes、index、mask、資料位址、packing 值及分支類型。

42 筆均為 R+12=0、R+11=1、U16[R+8]=0、U32[R+16]=1。因此其原指令意圖是：scale bit clear、mode bit set、FIFO bit clear、入口 enable bit clear，晚段 enable bit set；不把這些意圖合併為已觀測的最終設備狀態。

## 正常返回時 A0 是記錄位址

本段所有結構路徑只寫 A1..A6，唯一終點為未改 RA 的 `JR RA`。所以在所有存取成功、正常返回且沒有外部改寫暫存器的前提下，A0 保留入口 R；本段沒有另外產生 scalar 狀態碼。

結合先前的 caller 原指令與固定 epilogue bytes，可收斂出下列條件性返回值：

| caller 入口 | 最後返回的 A0 |
|---|---|
| 直接進 128FE，入口 SP=P | P−164，即其 176-byte frame 的 +12。 |
| 12AD0 selector 1／2，入口 SP=P | P−292，即外層 128-byte frame 再扣內層 176，再 +12。 |
| 12AD0 selector 0，入口 SP=P | P−404，另包含 1299E 的 112-byte frame。 |

此推論還需要 fill／copy 正常返回、保存先前已列的 live context／frame，且 stack 與數值 MMIO stores 不重疊。前一輪採任意 A0 reply 的 hook 是一般條件測試；現在對這個已定位的直接 callee，可由完整 body 的靜態保存集合進一步收斂。

返回時 caller 已恢復 SP，因此該數值指向先前 frame 的舊記錄位置；不能把它當成功碼或仍有效的 record 指標。本批沒有執行 MMIO 來取得返回值，也不證明設備實際會完成這些存取。

## 重現與結果

預設及 `-O` 只讀重算 ledger，逐 byte 比對既有 JSON；`--write` 僅供初次建立，使用 exclusive-create，不覆寫既有 ledger。

```text
python analysis/check_v4160_18ba2_static.py
python -O analysis/check_v4160_18ba2_static.py

PASS: algebra probes: 256 index, 256 scale, 256 mode, 65536 FIFO, 8 full-word enable; 8 specified raw mutations
PASS: 79 complete-body instructions; 36 closed CFG paths; GPR writes only A1..A6; no calls
PASS: 42 producer-record contracts; 14 bounded indices; exact ledger replay; NO ISA/provider/MMIO execution
```

一般與 `-O` 均通過，使用 `check()`。algebra probes 測主機端欄位分類與數學公式，不執行目標指令：全部 byte index／scale／mode、全部 U16 FIFO，以及 8 個完整 enable word。

8 個記憶體副本 mutation 繞過 baseline 全檔／body hash 預檢，分別改 mask shift 的來源暫存器、table stride、scale 欄位 offset、mode branch polarity、halfword destination register、enable store source register、RET 的來源暫存器、caller 迴圈上限。每個必須命中特定 operand／CFG／producer guard，不接受任意解析例外作為成功。全檔 hash 仍保護其他原始 bytes。

原區段 SHA-256，右界不含：

| 範圍 | SHA-256 |
|---|---|
| 18BA2..18CA4，258 bytes | `a7740d7785b0ab0def54148e8d56242da4341de1d4041a0ee7fffceed37338cc` |
| 1293C..1298A，78 bytes | `ef3f4a2c364f1fcce5c826f7efe7fe6985d7d4ee06576b01aa677d39344eaa5a` |

後續仍需追查其他 `18BA2` caller 的記錄來源與索引限制、獨立 provider 的實際綁定／保存／目的寫入合約。實體 MMIO 語意、相容性、IRQ／例外與完整實機啟動仍未證。
