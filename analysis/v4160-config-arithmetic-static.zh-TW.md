# v4.1.60：config 專用算術路徑與 copy 保存合約串接

接續 [完整 config gates](v4160-config-gates-static.zh-TW.md)，本輪核對算術 helper `0x6df1a`／`0x6e10a` 對 config 實參的完整續行路徑。在相符程式碼／查表值、正常存取與無外部干擾前提下，返回 A0 精確為 `floor(7*h/5000)`，A1=0；h 是呼叫前 fresh load 的 U16。結果範圍 0..91，因此後續 byte store 不會截斷商。

同時把既有完整 copy leaf 驗證接回 config 呼叫點，解除僅靠一般 ABI 推測的部分暫存器保存疑點。實際 installed provider、MMIO 副作用與 frame／物件保存期仍未確認。

全程僅解碼原始 bytes、檢查 CFG 與主機整數等式，未執行或模擬 target ISA、copy、callback、RAM、MMIO、FENCE.I 或裝置。C 重建覆蓋率未增加。

## 證據範圍

程式：[check_v4160_config_arithmetic_static.py](check_v4160_config_arithmetic_static.py)。可重播證據：[v4160-config-arithmetic-static.json](v4160-config-arithmetic-static.json)。來源 APP、兩版 candidate、稀疏 HEX、SDK header 與 Xwchc 參考來源沿用固定雜湊的驗證鏈。

| 候選 | entry fragment | normalization side block | lookup prefix |
|---|---|---|---|
| V1.31 | `0x6df1a..0x6dfd6` | `0x6e274..0x6e27c` | `0x6e95c..0x6e96c` |
| V1.40 | `0x6e10a..0x6e1c6` | `0x6e464..0x6e46c` | `0x6eb4c..0x6eb5c` |

各版兩段 instruction fragments 合計 196 bytes／62 條，另釘住 16-byte 查表前綴。兩版相應 fragments bytes 完全相同：

```text
188-byte entry fragment SHA-256
fa6f59ae203928d3a374374ed27afdaafa0853df94a9a7951f92cdfa2c7c1868
8-byte side block SHA-256
d6f207480c5ba1e976090946008d93aaa3ab2335ba91924302b2eb77de4b2a1d
16-byte lookup prefix
00010202030303030404040404040404
```

這不是整個 general helper 的完整反組譯。未限制輸入的 fragments 有四個外部 cuts；它們與額外修正路徑都不在本輪 config 實參域的可達圖內。程式保留 general fragment CFG/cuts，另列出有代數依據的分支選擇，驗證選定圖恰為 49 節點、單一有限鏈、無外部 cuts，並以普通 RET 結束。

## 固定實參如何排除分支

由 config 原指令串接，入口 `(A0,A1,A2,A3)=(N,0,1000000,0)`，`N=1400*h`、`0<=h<=65535`。因此 `N<=91749000`，沒有 U32 乘法溢位。

1. A3 非零分支不走；A1≥A2 分支不走。
2. divisor<65536 分支不走；divisor<16777216 分支會走 normalization side block。
3. side block 設 lookup index=`1000000>>16=15`、初值16。唯一資料 load 是 QK.C.LBU：V1.31 `0x6e96b`／V1.40 `0x6eb5b` 的固定值4。
4. normalization bits=16+4=20，shift=32−20=12，因此「shift為零」分支不走。
5. 正規化 divisor 的 low digit 為0，所以兩個 quotient correction products 都是0，對應 unsigned 比較直接走不修正的匯流路徑。

stock r2 對 QK.C.LBU 的浮點別名不作為語意來源；驗證使用既有官方 Xwchc 格式、向量與固定 encoding。

## 商的代數證明

```text
D = 1000000
D << 12 = 0xf4240000
normalized divisor high digit = 62500
normalized divisor low digit = 0

normalized numerator high = N >> 20 <= 87
first quotient digit = (N >> 20) // 62500 = 0

merged partial numerator
  = ((N >> 20) << 16) | (((N << 12) mod 2^32) >> 16)
  = N >> 4

second quotient digit
  = (N >> 4) // 62500
  = N // 1000000
  = (7*h) // 5000
```

第一個商位為0，最後組合輸出就是第二個商位，且明設 A1=0。檢查對全部 65,536 個 h 驗證正規化、兩個修正 product 為0所需的非負比較、merge 等式與商範圍。這是封閉公式對照，不建立 register machine、不讀取 PC 來跑指令，也不模擬記憶體或分支執行。

若 default 欄位保留 `h=31250`，且 fresh state byte+23 為0而確實執行此 call，返回商為43。若該 state byte 非零，config 直接略過算術並保留既有值，不能由本輪宣稱它必在0..91內。

選定路徑只定義 T1、A0..A7，沒有 store、nested call 或 frame 配置；唯一資料讀取是上述固定 lookup byte。故在有效語意與無外部干擾前提下，RA、SP、S0 及其他未定義 GPR 在本機保持。這個保存結論限定於此實參族，不外推其他 divisor、upper word 或 callback 呼叫族。

## 重用 copy leaf，補上 config 連接

既有 [event payload 與 copy leaf](v4160-event-payload-chain-static.zh-TW.md) 已完整固定 `0x20000332` 的 58 bytes／18 指令。本輪直接重播其完整 body 驗證，並以 first-copy 映射核對來源 `0x405a2`／`0x405e2`，不重複計入新增 code bytes。

config 的 direct call target 與該 leaf 相等，要求 destination=`0x20003234`／`0x20003284`、then-live source=C、length=16。leaf 只定義 A3/A4/A5/A6；A0/A1/A2、RA、SP、S0 本機不改寫。當 source 非零、存取正常且程式碼保持時，forward loop index 依序0..15，每次先讀 source byte 再寫 destination byte，之後正常返回。

該 leaf 在 null/count guards 前仍先讀 `U32[0x4002420c]`、將該處寫0、執行 FENCE.I，返回前再把先前讀得 word 寫回。這些是已辨識的原指令，沒有實際執行，也不表示外設狀態已安全復原。

沒有把 source/destination 指標暫存器本身存成資料的本機指令；但被搬移的 bytes 可以含有指標值，外部／MMIO 行為也可能保留資訊，因此不能宣稱「所有指標都不被保存」。forward overlap 可讀到自己先前的寫入，不是 memmove 或 entry snapshot 保證。

在相符已映射 leaf、正常存取與無不利 alias／外部改寫等前提下，config 的 fresh publication load 可接回完成的16次 byte transfers。目的區寫入及 MMIO 效果仍須不破壞 caller frame、code、後續所需欄位；僅有 GPR 不改寫不能證明 stack 保存期。destination 與入口 source 內容相等還需要額外的來源／目的別名和 writer 條件。

## 重播與界線

```powershell
& 'C:\Users\locky\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe' analysis/check_v4160_config_arithmetic_static.py
& 'C:\Users\locky\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe' -O analysis/check_v4160_config_arithmetic_static.py
```

驗證涵蓋兩版原 operands、general fragment cuts、config 專用49節點閉合圖、lookup來源、caller／copy joins、全部 halfword 代數、82個 operand與2個lookup變異拒絕，以及逐 bytes JSON 重播。

仍需追查 general helper 的其他實參域、APP 完整 config 建構、實際 installed candidate／provider 來源、optional hook／registration 副作用、外部 writers 與 frame／物件保存期。
