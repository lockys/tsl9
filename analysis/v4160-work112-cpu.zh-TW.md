# v4.1.60：128FE 的 112-byte 工作區與 14 次記錄呼叫

2026-11-26。接續 [ready 固定資料複製](v4160-ready-copy-cpu.zh-TW.md)，本批展開原 `128FE..1299E`，並串接 selector 0 的 `1299E..129C4`。原 decoded APP 長 76800 bytes、基址 8000，SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`。

既有 `src/native/receive/filter_input.c` 與 `callback_flow.c` 已重建這些原區段。本批補原指令的參數、精確存取、資料重建及條件性返回驗證；不更改既有 C、共享 CPU、原 BIN、seal 或 C 覆蓋率。

全部使用有限解譯器與合成記憶體。fill／copy provider 及 `18BA2` 均在入口停止；目的寫入、正常返回與保存條件由測試明示。`18BA2` 的原始指令包含 MMIO 存取，本批沒有執行其本體，也沒有設備、CSR、實際傳輸或網路分析操作。

## 固定 112-byte 工作區與完整 word 長度判斷

令入口 SP=P、frame 起點 F=P−176，工作區 W=F+32，長度 112 bytes。原程式先讀 `[40048]`，依序保存 S0、S1、RA、S2、S3、S4，再呼叫該 target：

```text
A0=W, A1=0, A2=112, RA=12920
live S0=原輸入長度, S1=原來源指標, SP=F
```

只有在明示 fill 正常返回、保存 live S0/S1、其他 S、GP/SP 與 frame／指定以外記憶體的前提下，才能繼續以下合約。原 APP 自身沒有清零這 112 bytes。

返回後以 **完整無號 word** 比較輸入長度，得到 n=min(length,112)，再重新讀 `[4004c]` 並呼叫：

```text
A0=W, A1=原來源指標, A2=n, RA=1293C, SP=F
```

length=0 仍會呼叫。length=256、257、80000001、FFFFFFFF 均得 n=112；不能先截低 byte 再比較。本批在 fill 返回後改用新合成 slot target，確認後續重新載入 copy 指標。

1040 組案例為全部 256 個 byte 長度，加 256、257、80000001、FFFFFFFF，共 260 個完整 word × fill 有／無目的寫入 × copy 有／無目的寫入。直接入口的 176-byte frame 先預種可辨識的非零樣式；沒有將未寫入的洞位偷偷補零。

copy 的目的效果只按明示前提寫 n bytes；未執行 provider code。fill 無效果且 copy 不覆蓋的工作區部分會保留舊值，即使 count=0 也會流入後面的固定迴圈。

## 14 組讀取與 20-byte 記錄

在每次下游都正常返回並保存 live 迴圈狀態的前提下，原碼固定呼叫 14 次 `18BA2`，index=0..13，每次從 **當下** W+8×index 讀四個 little-endian U16；總讀取範圍是完整 112-byte 工作區，不以 n 縮短次數。

每個 U16 左移 5 位，A2..A5 中保留完整 32-bit 結果；寫入記錄時，SH 截斷至 low16。例：07FF→FFE0、0800→0000、FFFF→FFE0。不能把這當成飽和運算，也未據此命名實體欄位。

記錄 R=F+12，共 20 bytes：

| R 內偏移 | 原 APP 寫入結果 |
|---|---|
| 0..7 | 四個 `(U16 << 5) & FFFF` 的 little-endian halfwords。 |
| 8..9 | 0。 |
| 10 | index。 |
| 11 | 1。 |
| 12..15 | word 0。 |
| 16..19 | word 1。 |

精確順序是四個 LHU、R+8 的 zero-word、R+10 的 index byte、R+12 的 zero-word、R+11 的 byte 1、四個 halfword stores，最後 R+16 的 word 1。其後先將 live 工作指標推進 8 bytes，才呼叫 `18BA2`。

入口 A0=R、RA=1298A、SP=F；live S0=W+8×(index+1)、S1=index+1、S2=14、S3=S4=1。這裡核對 A0 所指記錄與 live 暫存器，不替未設定的其他暫存器發明函式參數。

9 組額外 shift 案例使用 0、1、07FF、0800、0801、1234、7FFF、8000、FFFF，各重複填入 56 個輸入 halfword，核對全部記錄的截斷結果。

## 呼叫間修改與保存條件

9 組 live-workspace 案例在第一次下游入口後，明示修改下一輪的 8-byte 工作區；後續 LHU 必須讀到新值。同時在前 13 次呼叫後把當前 R 的 20 bytes 改成 A5，確認下一輪完整重建記錄。這些是合成 hook 的變更，不是實測 MMIO 例程副作用。

所有一般返回 hook 保存 S、GP/SP、saved frame 與記憶體，並破壞 A/T。前 13 次提供不同 A0 reply，最後一次指定最終 reply。原 epilogue 恢復 RA、S0..S4、SP，**不重新設定 A0**，因此保留最後一次下游 reply，不能解讀成固定成功碼。

另有負向保存探針：第一次呼叫返回前明示把 live S1 改為 14，原迴圈就直接結束，只有一次下游入口。這說明「14 次」依賴服務保存 live 迴圈暫存器，不能從 caller 的 saved frame 推定未知服務一定保存它們。

每段原指令執行都比對精確資料存取順序及整個映射記憶體的寫入範圍。輸入指標、stack 與存取成功是合成 fixture 前提；不涵蓋任意 alias、例外、IRQ 或實機 stack 行為。

## selector 0 的原 96-byte caller

原 `1299E` 配置 112-byte frame Z，保存 RA 於 Z+108，呼叫真正 APP 軟體複製函式 `19BF0`，以 `(Z,19CA8,96)` 複製固定資料，RA=129B4。之後呼叫 `128FE(Z,96)`，RA=129BE。

本批補上 `[19CA8,19D08)` 的 literal 資料 trace，使用捕獲的 APP bytes 執行原軟體複製，沒有用合成值代替該固定資料。

24 組完整本機 caller 鏈為 selector={0,1,2} × fill 有／無效果 × copy 有／無效果 × 最終 reply={0,FFFFFFFF}：

```text
selector 0: 12AD0 → 1299E → 原96-byte軟體複製 → 128FE
selector 1: 12AD0 → 原94-byte軟體複製 → 128FE
selector 2: 12AD0 → 原106-byte軟體複製 → 128FE
             → fill入口／明示返回 → copy入口／明示返回
             → 14次18BA2入口／明示返回 → 原各層epilogue → caller
```

三條路徑各自預種內層 176-byte frame，避免無效果案例依賴前一案例的殘留值。各層 source/payload、RA/SP/S 保存及最終 A0 均核對。成功 fill 且 copy 完成時，三種長度的工作區尾端分別為 16、18、6 個零 bytes；這仍是 provider 目的寫入前提的結果。

以上「完整本機 caller 鏈」包含明示服務返回，並不代表完整設備／實際 MMIO 執行鏈已證明。

## 重現

[test_v4160_work112_cpu.py](test_v4160_work112_cpu.py) 使用原 APP、已發布的 ready_copy／source19 等同目錄測試依賴與標準庫，不需要 SDK carrier 或網路。

```text
python analysis/test_v4160_work112_cpu.py
python -O analysis/test_v4160_work112_cpu.py

PASS: 1040 full-word length/fill/copy cases, 14 records each; 9 shift/truncation cases; 9 live-workspace cases
PASS: 24 selector0/1/2 complete local chains; original96/94/106 literals; exact frames/records; negative S1 preservation probe
PASS: 5 specified mutations; provider writes/returns explicit; 18ba2 MMIO body and hardware NOT executed
```

一般與 `-O` 均通過，使用 `check()`。五個原 BIN 記憶體副本 mutation 改 fill count、clamp 上限、第一個 halfword shift、迴圈上限、selector 0 copy count；各自命中特定參數／存取／context 檢查，不接受任意 exception 作為攔截成功。原檔未修改。

原區段 SHA-256，右界不含：

| 範圍 | SHA-256 |
|---|---|
| 128FE..1299E | `0191afe9afa2ecad8b58295c50301bfac35115a1e33140f61c4678b5997dda4e` |
| 1299E..129C4 | `722428b52f60e85f2d3b40ab39a2be581def68ef8a795977b64b5f9edc3d18fe` |
| 19CA8..19D08 | `72c4511144ac0693fff827ccfaf986b85b93313446cdf43cced132148f19089a` |

後續需繼續以靜態方式核對 `18BA2` 的記錄消費與 MMIO 存取邊界，以及其他 caller、installed provider 身分與保存／寫入合約。本批沒有證明硬體相容性或將 MMIO 例程實際執行。
