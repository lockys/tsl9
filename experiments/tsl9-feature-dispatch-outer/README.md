# 外層功能分派：有限靜態重建

已實際以固定 LLVM 編譯 C11 / C++17，兩語言物件相同。這是給主分派樹接合的私有架構區域來源，沒有執行 target、HOST 模型、ISA、硬體或網路，也未產生韌體 BIN。

覆蓋原廠 `14D2E–14D5E`（48B，入口及 mode0）、`153BA–154A6`（236B，mode2–6 與 default），以及完整 `829E–82A8` getter（10B）。合計 **294B / 101 指令 / 21 FUNC**，另有原位址 `1A6B8` 的 28B / 7 entry 相對表。mode1 與 `14DA2` 共用返回區域由其他來源負責，這份來源不將外層片段冒稱整個 1912B 函式。

正式試作來源是 [src/outer.v2.c](src/outer.v2.c)。`build.py` 固定並重用 `scripts/verify-curated-source.py` 的 `queue-consumer-a0-a5` profile，僅讓 A0–A5 作為自由暫存器，沒有猜測 normal ABI，也沒有借用 A6。完整旗標、實際命令、exit、dependency、原始編譯及 LLVM IR / objdump 日誌保存在 `build/trial-v2/{c,cpp}/`。

`verify.py` 已實際通過 C 與 C++ 各 **549** 個記憶體中的畸形物件負例；收據是 [verification-v1.json](verification-v1.json)。核對包含每個 294B 程式及 28B 表 placeholder、FUNC owner/extent/type/visibility、所有 RELA 的位置/型別/目標/addend、移除 RELA 後還原原始指令的案例。這是 byte/relocation 與結構證據，不是通用 C 語義或執行證明。

## 介面與控制

- 主入口：`tsl9_queue_external_14d2e`。保存 frame 後，真實 `jal` 呼叫 `tsl9_feature_mode_getter_829e`。
- getter 保留 `AUIPC` 的原始 PC 依賴，在名義 VA 829E 讀取 `byte[2000BFB5]` 至 A0，再 `ret`。欄位的實際記憶體所有權、有效性與裝置配置身分未證。
- `A0 > 6` 走 `tsl9_feature_outer_1549a`，恢復 S0/RA，設定 A0=0，再尾跳 `tsl9_feature_external_1074c`。
- 主表有真實 `R_RISCV_ADD32/SUB32` target-minus-table-base 資料 relocation。主程式用真實 `PCREL_HI20/LO12_I` 引用該 OBJECT，不用 ABS target provider，也沒有把表值塞入程式位元組。
- 原始 `JR` 在 `14D50`，不寫 RA。表依序指向 `14D52,14D5E,153BA,153DA,153FA,1543A,1547A`。mode1 符號是 `tsl9_feature_mode1_14d5e`。

| mode | then-live `u16[S0]` | 尾跳目的地 |
| --- | --- | --- |
| 0 | 不讀此欄位 | 10B60 |
| 2 | 169 / 540 | 10870 / 108D8 |
| 3 | 169 / 540 | 10870 / 10944 |
| 4 | 393 / 1676 / 169 | 109C4 / 10A00 / 10870 |
| 5 | 929 / 1002 / 890 | 10A16 / 10B0A / 10AC6 |
| 6 | 169 / 1176 | 10870 / 10936 |

mode2–6 不符合表列值時分支至真實 `tsl9_feature_return_14da2`。所有表列尾跳都先以 then-live S0 設 A0，再依原始 S0→RA→SP 順序恢復，最後 `jal zero`；不能把這些請求路由稱為車輛已完成的行為。

21 個 FUNC 的 VA / extent 在 [spec.json](spec.json)，25 個直接控制點的 owner/offset/型別/真實目的地在兩份 `receipt.json` 的 `facts.direct_controls`。另有 2 筆 table-PC relocation 與 14 筆資料 relocation，合計 **41 RELA**。

## 原廠證據與來源界線

原始 bin SHA256 是 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`，VA=8000。原始外層指令重用 `build/feature-dispatch-frontier-20261023-v1/reader-output.json`，SHA256 `60520b4156dd2c7f391f716135b141fb26504334eaa60839f74bb8b03b2db4b7`；其 98 筆外層記錄與 bin 逐 byte 核對。getter 的三筆原始 r2 記錄另保存在 [original-getter.json](original-getter.json)，完整 10B 亦直接與原始 bin 核對。

C 擁有 free-bank table/getter 記憶體讀取、unsigned shift/add 與比較常數。frame / S0 / RA / SP、呼叫/尾跳/分支與 PC-relative base 是明示架構 port。**五個 `lhu a5,0(s0)` 亦保留為 then-live S0 架構 memory port**：v1 嘗試用 C 的固定 S0 output 讀取，固定 LLVM 會要求 callee-save stack，實際報錯 `Stack pointer required, but has been reserved`。另一個唯讀 builtin probe 報 unknown builtin。兩份失敗來源、命令、snapshot、C/C++ 原始 log 全保留在 `trial-v1` 與 `register-probe-v1`。沒有用未初始化 C register、虛構保存值或額外 mv 冒充原始指令。

頂層 `.word` 僅定義獨立 `.rodata` 的 7 筆符號差，不包含原廠程式 opcode stream；沒有 incbin / insn / code-byte carrier。這個特殊架構 memory port 範圍與一般 C 記憶體邏輯已明確區分。

## 尚未閉合

原始 unresolved ET_REL 有 **13 UND**：mode1、common return，及 11 個 `tsl9_feature_external_<va>` 尾跳提供者（1074C、10870、108D8、10936、10944、109C4、10A00、10A16、10AC6、10B0A、10B60）。它們都是實際符號依賴，未以 ABS 名義地址或原廠 bytes 假充 provider。

這份試作沒有原位連結結果；checker 對符號的原始 VA 做靜態 relocation 核對，不宣稱已提供或執行那些目的地。ET_REL 中的 PC-sensitive code 必須在真實 provider 接合及名義位址核對後才有後續證據。memory / IRQ / startup / installed ROM / hardware / 車輛效果 / OTA 仍未證。

## 固定雜湊

| 檔案 | SHA256 |
| --- | --- |
| src/outer.v2.c | bc94efda3e290fd63b65b1df058e5af59065529e9d3e19d79b6a929b96fc29f3 |
| build.py | d8058bf49e092c9e7e8f9e29b25b167e885ce6422b510da5f7e71a03be37204d |
| spec.json | 68bccb73e2e38672b8171e58ffc512a0a90b0c6f6f9f2bc068179ba5e4436392 |
| verify.py | 5cc2766139756997f3661245146be95d082d05dc6e23bd85133df4d5ceea3077 |
| verification-v1.json | 13d88b05ff8196820fac54a9a6b448d4329e34834d2f2e73b023b035a3f25215 |
| C/C++ unit.o | 626c4030b98de7e23fe1e4f0a770889bdde87e75884130a443973c0c79a36c7e |
| C receipt.json | eeef5a5918195bae650ab1a9bab3e77df81309f85980c96331a3a9c700b62653 |
| C++ receipt.json | de8b8020a3af940d2b96605e6a84535b42c1b43be0d207c2ba1bcaa022fbbb33 |

唯讀復核：`python experiments/tsl9-feature-dispatch-outer/verify.py`。
實際重編譯必須選擇全新的 `--output`，例如：

```text
python experiments/tsl9-feature-dispatch-outer/build.py --source experiments/tsl9-feature-dispatch-outer/src/outer.v2.c --output experiments/tsl9-feature-dispatch-outer/build/trial-v3
```

builder 以 USERPROFILE 組合本機固定 LLVM 路徑，先核對 tool / stdint / profile / 原始 bin / listing / ELF reader 雜湊，沒有安裝或下載動作。
