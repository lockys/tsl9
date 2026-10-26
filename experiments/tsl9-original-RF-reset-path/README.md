# RF 初始化必要本體與輪詢

[English](readme.en.md) · [RF 傳送／重試](../tsl9-original-RF-tx-path/README.md) · [原始初始化銜接](../tsl9-original-RF-bridge/README.md)

補上原始候選執行層直接呼叫的 5 個缺失本體及其 2 個 helper：**4,090 bytes／1,298 指令、7 個完整本體**。C/C++ 保留原始暫存器情境與必要 assembly ports，不是一般 HOST 可呼叫 API。

| 候選本體 | 原始範圍，end exclusive | Bytes／自身 frame |
| --- | --- | ---: |
| Register initialization | 0x660CE..0x66242 | 372／16 |
| Register sequence／poll | 0x662DA..0x6636E | 148／0 |
| Register sequence | 0x6636E..0x663A6 | 56／0 |
| Large setup／calibration-like body | 0x6645C..0x67198 | 3388／80 |
| Register-bit setup | 0x67198..0x671AA | 18／0 |
| Register-write／software-loop helper | 0x66098..0x660CE | 54／0 |
| RAM polling helper | 0x20002DF2..0x20002E28 | 54／0 |

「校準」是根據設定／讀回形態的推論；尚未確認實體暫存器與晶片身分。

## 實際呼叫與條件

原始 initializer `0x64298` 在 `0x642FE` 呼叫本輪 `0x660CE`；此 call 在完整正常返回 CFG 中支配 initializer 的本地尾跳。

Common reset `0x641B0` 在 `0x64246／0x6424A／0x6424E／0x64252` 依序呼叫其餘 4 個本體，但**不是所有路徑都呼叫**。兩次獨立讀取 byte `0x2000351B`，各與 4 比較；另外比較 pointer word `0x20003504` 與 `0x40024300`。三個 guard 的 fallthrough 都是進入該 call 路徑的必要條件。這沒有證明非同步期間值穩定，或所有 callee 都能正常返回。

## 輪詢與晚置分支

- Helper `0x66098` 重新載入 pointer word `0x20003590`，對 pointed offset 12 寫入原始值 `0x1101 → 0 → 0x1101`，中間各有初值 20 的軟體迴圈；未證明物理 reset 意義或時長。
- `0x662DA` 對來自 pointer word `0x2000353C` 的 offset 100 寫入原始值 80，輪詢該 word 與另一 block 的 offset 156／bit 8。
- RAM helper 使用原始值 6000，輪詢 offset 100 與另一 block 的 offset 144。bit 26、bit 25 來自**不同次 volatile 讀取**，不可合併成同一次讀值的 mask。
- 大型本體的 `0x664D0` 比較 RAM word `0x20003588` 與 `0x12345678`。相符時走 return 後仍可達的 `0x67190`：清除該 word，跳到 `0x665B0`，略過先前 3 次 RAM polling-helper calls，然後繼續後段設定。未新增任何 runtime 控制或略過校準選項。

80／6000 是原碼數值，**不是已確認的時間單位或終止保證**。MMIO 容量、side effects、alias 與非同步作用未封閉；沒有在實體硬體上執行這些寫入。

## 驗證與限制

C11／C++17 物件完全相同；4,090 個原始情境 bytes、完整 CFG 自身 frame、52 個官方 Xwchc 正例與 4 個實際 ports、兩個 ELF readers 通過。25 個 FUNC 是編譯區段，不是邏輯函式數。保留所有輸入 bytes／symbols／relocations 及唯一原始 PC ownership。

累計唯一組合為 **18,526 CODE＋256 DATA bytes／6,330 指令**，1,194 個 FUNC 區段、894 個 relocation。實際補齊 5 個具名依賴，未提供依賴由 **19 降至 14**；沒有新增具名缺口。無具名缺口的單元仍可能依賴未證明的 RAM／MMIO／輪詢行為。

APP 仍為 159 個正式 C/H、95.54% 位元組覆蓋率，不是功能完成率。未整合進 APP、未產生新 BIN、未執行目標／模型或操作硬體。4-byte 啟動來源缺口、實體 ROM／RAM／ISA／IRQ、全程 stack／alias、Flash 與 OTA 相容性仍未確認；**尚未成功重建可用替代韌體**。初始化／輪詢來源診斷可列為後續觀測功能，尚未實作 UI。

[C/C++](original_RF_reset_path.c) · [原始指令](evidence-v1.json) · [完整收據](audit-result-v1.json) · [摘要](summary.json)

## 重現

需 spec 固定的本機輸入、先前 native artifacts、Windows NDK LLVM 與 trap 驗證的官方 header；不會下載缺少的輸入。

```sh
python experiments/tsl9-original-RF-reset-path/build-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-original-RF-reset-path/build/native-v1
python experiments/tsl9-original-RF-reset-path/audit-v1.py --tool-dir "$LLVM_BIN" --reference-root "$REFERENCE_ROOT"
```

建立新產物時，用 `--trial` 取代 `--replay`，第二行加 `--link-trial`；名稱均須未存在。跨平台編譯未驗證。
