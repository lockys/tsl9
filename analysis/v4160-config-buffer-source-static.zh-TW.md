# v4.1.60：設定長度來源、三筆記錄與條件性 256-byte buffer

日期：2026-11-26。承接 [APP callbacks](v4160-app-nv-callbacks-static.zh-TW.md) 的固定 256-byte program 路徑，追查 APP 設定建構、resident 預設值及 fill 本體。[檢查器](check_v4160_config_buffer_source_static.py)／[ledger](v4160-config-buffer-source-static.json) 保存完整原指令、條件性 CFG、所有本機 stores 及來源關係。

**APP 沒有直接寫 C+12 長度：清零成功且該欄位未被其他路徑改動時，傳入值為 0；兩份參考 resident 均將零補為 256。APP 將 C+14 設為 3。** 這解釋了預設三筆、每筆 256-byte 的來源，仍不能直接認定配置、填值及各輪 fresh reads 始終相等。後續 C+44 callback 等 writer 的完整副作用與 installed provider 仍未知。

本輪只讀本機檔案、解碼指令並檢查主機整數關係；沒有執行或模擬 target ISA、heap、buffer、provider 或 MMIO。C 重建覆蓋率未增加，原 BIN 與既有分析均未改寫。

## 完整範圍

| 本體 | range（終點不含） | bytes／instructions | SHA-256 |
| --- | --- | --- | --- |
| APP config builder | `199e2..19b16` | 308／106 | `c4adfa47a73e8a89af8c8625961cd798292c7c478503a250a005f885bc3e64a0` |
| APP 六 byte source leaf | `18f56..18f88` | 50／14 | `5ea71cc5060b528919272111556388a084fe65e49474efa62683825e4df2eedf` |
| V1.31 fill | RAM `2000039c..200003ca`，flash `4060c..4063a` | 46／14 | `d67147a681aca68d4d082eebf74ab6214f61f43253be91e932eebd5c3e3d05a3` |
| V1.40 fill | 同 RAM，flash `4064c..4067a` | 46／14 | 同上 |

合計 **450 bytes／148 instructions／35 個靜態 store 位置**。另在兩版本已固定的完整 228-byte config 函式中，對各 18-byte 預設值區段補上明確 operand guards；這 36 bytes 不另算成完整本體或新增 C 覆蓋。

沿用固定 APP／carrier／SDK header hashes，及已保存 LLVM 四份來源、Git blob pins 與 28 筆 Xwchc vectors。完整 bytes/hash 與解碼邊界均核對，關鍵資料流、所有 store operands、呼叫、分支和 loop 有獨立 guards。仍使用條件性 ISA 解讀，不把一般 disassembler 的浮點顯示當成 Xwchc 語義。

## APP 建構設定

完整 APP 函式建立 96-byte frame，保存 S0 至 SP+88、RA 至 SP+92。以 C=當時 SP+16 投影：

| 欄位 | 來源 | 在保存與無介入改寫條件下的值 |
| --- | --- | --- |
| C+0 | `19a3a/19a3e` PC-relative，`19a42` SW | `2000418c` |
| C+4 | `19a44` LUI，`19a46` SH | heap length `7000`，即 28672 |
| C+8 | `19a4a/19a4e`，`19a52` SW | NV base `08077c00` |
| C+12..13 | 無直接 store | clear 成功後為 0 |
| C+14..15 | `19a56` 得 `1000-2045=0803`，`19a5a` SH | little-endian：count=3、neighbor byte=8 |
| C+44 | `19a92/19a96`，`19a9e` SW | callback `197f0` |
| C+52..55 | 無直接 store | clear 成功後為 0 |
| C+56 | `19a76/19a7a`，`19a7e` SW | read callback `1979a` |
| C+60 | `19a80/19a84`，`19a88` SW | write callback `197be` |

`19a38` 經當時 `[S0+72]` 呼叫，A0=live SP+16、A1=0、A2=64；若 S0 保持 `40000`，該處為 slot40048。**APP 不檢查回覆，正常返回本身也不證明清零完成。** 本輪把兩候選的完整 fill 解開，仍需其實際綁定、有效寫入及 context 保存，才能由清零請求推到零欄位。

clear 後的 14 個直接 config stack stores，不碰 SP+28..29（C+12）或 SP+68..71（C+52）。六 byte source leaf 只寫 entry A0+0..5；此處 A0=SP+8，所以落在 SP+8..13。它讀 `1ffff7e8` 的四個 byte 及 `1ffff7ec` 的低兩個 byte，並未讀出可由 APP 檔案確定的內容。

接著七節點 APP loop，把這六個 bytes 搬到 SP+40..45，即 C+24..29。指令先將 A4 遞增再以 +23 store，因此目的地起點是 SP+40，不能誤算為 SP+39。此 leaf 與 loop 都不直接碰 C+12／C+52；這是本機存取區間的結論，仍需 live SP、code、有效 accesses 與外部 writer 前提。

## APP 的五個 calls 與停留路徑

| call | 參數／回覆處理 |
| --- | --- |
| `19a04`，nominal slot4003c | A0=先前讀出的 `[S0+52]`、A1=`1ab1c`、A2=21；回覆非零才繼續，零進入 `19a08` 自旋 |
| `19a38`，nominal slot40048 | C、0、64；回覆未檢查 |
| `19ab4 → 18f56` | SP+8；完整六 byte leaf 已核對 |
| `19aec`，fresh slot400a4 | A0=當時 SP+16；回覆零才繼續，非零進入 `19af0` 自旋 |
| `19af8 → 19106` | A0=64、A1=1；callee 未展開、回覆未檢查 |

config call 之前另 fresh 讀取 `[SP+16]` 非零、U16[SP+20]≥4096；不符進入 `19ae0` 自旋。這不是 C+12 的驗證，也不是已證 heap 有效性。

本體 CFG 有三個單節點自旋及一個七節點搬移 loop。opaque call 的 fallthrough 全部只是「假設正常返回」邊。尾段固定 store 為 `E000E104←80000000`、`E000E108←1`，未執行硬體操作。最後 callee `19106` 返回後沒有再定義 A0，因此 APP 的正常回覆沿用該 callee；不能把 resident 返回零擴大成整個 APP 函式返回零。

## fill 的具體方向與回覆

兩份 slot40048 值均為 `2000039c`，完整 46-byte body 位於各自已檢查的 first-copy source 範圍。

它先讀並保存 `U32[4002420c]`、寫零、FENCE.I，再判斷 destination；非零時計算 end=`destination+count mod 2^32`。count 非零才進入三節點 loop：

```text
A0 += 1
SB low8(A1) to A0-1
A0 != end 時重複
```

非零 destination／count 在所需 accesses 全部完成的正常路徑，寫入 offsets 0..count−1，**回覆 A0 為 one-past end，並非原 destination**。destination=0 或 count=0 時不執行資料 loop，回覆 A0 保持原值。所有正常返回路徑都先恢復先前保存的控制 word。

fill 不明確寫 S0／S1／S2／SP／RA，沒有 nested calls；它寫 A0／A4／A5。但動態目的地可以 alias config、saved frame 或其他資料，因此 encoded nonwrites 仍不能單獨證明整體保存。

APP 的 clear request 若確實對 C 寫 64 個零，C+12 與 C+52 才有上述零來源。resident 的 fill request 若對 P 寫 256 個 FF，A0 回覆可為 P+256；[config-I/O](v4160-config-io-static.zh-TW.md) 使用 cache 重讀 Pcurrent，不應拿 fill 的 A0 當作同一來源指標。

## resident 預設值如何接上 256 bytes

兩版本相同的 guarded default 規則：

```text
fresh U16[C+12] 非零則保留，否則寫 256
fresh U8 [C+14] 非零則保留，否則寫 1
```

故在 APP 清零／欄位保存與 resident validation／64-byte copy 都完成的條件下，這次輸入的 length=0、count=3，經 defaults 後是 **length=256、count=3**。default 的 byte count 與 neighbor byte 分開，不能把 `0803` 整個 halfword 誤當成 2051 筆記錄。

defaults 後會呼叫 APP C+44 callback（來源為 `197f0`），再執行 post-config callee 等流程，最後才可抵達已核對的 config-I/O。因此這次來源證據沒有解除 L0／L1／Li 是不同 fresh reads 的限制。

只有再加上 ledger 所列的保存前提：所有相關呼叫／writer 保持必要欄位、L0=L1=各 Li=256、count 保持3、cache 指標相同、core 在合法非回繞 B≥256 區塊成功、fill 與 store 有效且不破壞其他資料、poll 與 callbacks 正常返回，才得到下列**條件性情境**：

| 項目 | 情境內的算式／值 |
| --- | --- |
| allocation | request256、tag78；R=256，選 large list |
| block 分割 | B>264 才分割；fit 且 B=256..264 不分割 |
| fill | P 的 256 bytes 寫 FF |
| 三輪 index | 0、1、2；S2 在每個 callback 之前遞增 |
| 目的地址 | `08077c00`、`08077d00`、`08077e00`；均已對齊256 |
| callback A1 | `Li>>2 = 64`，APP write callback 仍忽略它 |
| source | Pcurrent 起的 256 bytes；bytes0..3 是該輪地址的 little-endian word，其他 bytes 只有在填值與保存條件下仍為 FF |
| release | 最後重讀的 Pcurrent；與初次 P 相同仍需獨立保存前提 |

這是大小與來源關係的串接，不是實際 buffer 快照、所有權或合法 heap extent 的證明。header 的 B≥256 也不等於這段物理 RAM 一定可讀寫。未建立可執行程式、故障觸發輸入或硬體操作序列。

## 重播結果與限制

```text
python analysis/check_v4160_config_buffer_source_static.py
python -O analysis/check_v4160_config_buffer_source_static.py
```

兩模式均實際輸出：

```text
PASS: 65536 length defaults; 256 count defaults; 65536 split-gap identities; 768 fill-address identities; 10 specified raw mutations
PASS: 4 complete bodies, 450 bytes/148 instructions/35 store sites; 2 guarded resident default slices
PASS: exact ledger replay; conditional length256/count3/extent256; actual field stability UNPROVED; NO target execution
```

長度／count／split-gap／increment-before-store cases 都是主機寬度代數；部分 gap 算式不一定代表合法 U16 block。十個 raw mutations 改 clear count、config pointer、count 常數／store offset、六 byte loop bound／destination、config slot、source leaf extent、fill offset、resident default 常數，均要求命中指定 semantic guard，沒有以全檔 hash 不符或任意 exception 當成通過。

預設只讀重算並精確比對 JSON；`--write` 僅建立不存在的 ledger。重播需十個已發布 Python dependency 模組與本機固定 APP、兩份 carrier、SDK header、LLVM sources／vectors。candidate 輸入未隨本次發布，僅 clone repo 不足以重跑。

下一步為 `197f0` 與其他後續 writer 的完整副作用、實際 installed provider、初始 NV contents 與指標保存期。整個過程仍保留先前 sparse 初始化來源缺口及外部干擾未知。
