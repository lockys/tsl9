# Resident 記憶體函式獨立審查

[English](readme.en.md)

已獨立審查 compare／fill／forward-copy 的可讀 C，以及實際 C11、C++17 HOST 與 RV32 ET_REL 產物。沒有連結、執行 RV32、產生 BIN 或驗證硬體。

## 原始候選證據

兩份既有 resident 參考映像，在各自初始化映射後，三個完整函式的位元組相同。`source-ledger.json` 保留各自 RAM／Flash 位址、完整短函式、雜湊及契約；`review.py --candidate-refs` 實讀兩份 segment 的六個切片。這不證明 TSL9 已安裝其中任一版本。

| 候選 RAM 入口 | 原始大小／指令 | 已確認的正常效果 |
| --- | --- | --- |
| `200004BC` compare | 62B／19 | 初始空指標或零長度回傳 0；逐一 LBU 與完整 32 位 A1 比較，全部相等回傳 1 |
| `2000039C` fill | 46B／14 | 依序 SB 低 8 位；正常回傳前進後的目的位址，空／零長度保留原位址 |
| `20000332` copy | 58B／18 | 每次先 LBU 再 SB，向前重疊有回饋；A0 保留原目的位址 |

三者均先 READ32 `4002420C`、WRITE32 零、`FENCE.I`，之後才測初始指標與長度，正常出口恢復保存的 word。位址採 32 位模數運算，不在迴圈中新增空指標判斷。原始三函式合計 166B／51 指令，無自己的堆疊或巢狀呼叫。

## 獨立驗證

`independent_host.c` 使用合成 byte 記憶體與明列期望事件，不解譯機器碼。C11／C++17 各實際通過 **16 個敘事情境、940 項斷言**。情境含完整 A1、第一個 mismatch、下一次讀取前的記憶體變更、MMIO 別名、fill 結束位址、copy 向前重疊及跨 `FFFFFFFF→0`。HALT／TRANSFER／UNKNOWN 僅保留觀察到的事件前綴，不捏造恢復動作；HOST budget 只是診斷限制。

每語言另實際編譯三個單一語義錯誤，均由斷言拒絕：截短 compare 預期值、空指標提前跳過 guard、copy 重用首個來源位址。不可把這些 HOST 結果當成真實 MMIO 故障／中斷語義。

| 實際原生 C／C++ 函式 | 大小／指令 | 實測 frame |
| --- | --- | --- |
| compare | 146B／61 | 48B |
| fill | 138B／58 | 32B |
| copy | 160B／64 | 48B |
| 原始 C 中的 static `begin` 共用函式 | 86B／35 | 16B |

合計 **530B／218 指令、13 個 CALL_PLT**。`begin` 是來源明確宣告的函式，機器 outliner 已停用。獨立讀取所有指令欄位並與完整 LLVM 反組譯比對，檢查本地分支、save／restore、實際 AUIPC／JALR relocation、來源／工具／`-MD` resource header／IR 證據。三個公開函式使用真正的 struct-result 隱藏 sret 指標，加上明示 I/O context；這不是原始 A0/A1/A2 葉函式介面。

五個 `ml_port_*` 保持真 UND，沒有 ABS 或假 provider。此原生產物仍須外部 provider 才能執行讀寫與 `FENCE.I`，未證明原始 ABI、固定位置、已安裝 resident、非同步效果或 OTA 相容；530 只是本組函式的加總，不代表其他 530B 函式。

## 使用

預設只檢查封存成員、當前 C／來源契約及保留結果摘要，不需要被排除於發布的 build 產物：

```sh
python3 -B <case>/model-review/check.py --project-root <ROOT>
sh <case>/model-review/verify.sh --project-root <ROOT>
```

明確讀取既有候選 segment 或新原生產物（不執行目標）：

```sh
python3 -B <case>/model-review/review.py --project-root <ROOT> --candidate-refs <resident-reference-root>
python3 -B <case>/model-review/review.py --project-root <ROOT> --folder <native-mode-folder> --receipt <NEW-review.json>
python3 -B <case>/model-review/review.py --project-root <ROOT> --replay <review.json>
```

重新編譯並執行作者撰寫的本機測試，與唯讀驗收產物是不同模式：

```sh
python3 -B <case>/model-review/run-host.py --project-root <ROOT> --language both
python3 -B <case>/model-review/run-host.py --project-root <ROOT> --replay <HOST-verification.json>
```

`run-host.py` 使用既有不可變的 HOST 執行檔架構檢查，拒絕把 RV32 當本機測試執行。原生 mode folder 需包含 frozen producer 的 `verification.json`、`.o`、`.ll`、`.d` 與四個實際命令日誌。明確實物模式的 `actual_native_artifacts_read` 或 `actual_host_artifacts_replayed` 才為 true。`selected.json` 是已觀察結果的封存摘要，不能取代新實物驗收。
