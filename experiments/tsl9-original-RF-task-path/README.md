# RF task、取樣比較與跳頻關閉

[English](readme.en.md) · [初始化／輪詢](../tsl9-original-RF-reset-path/README.md) · [傳送／重試](../tsl9-original-RF-tx-path/README.md)

新增 **1,586 bytes／576 指令、7 個完整候選本體**，補上 RF task 的 3 個實際具名缺口及必要 helper／註冊 callback。C/C++ 保留原始暫存器情境與必要 assembly ports，不是一般 HOST 可呼叫 API。

| 本體 | 原始範圍，end exclusive | Bytes／自身 frame |
| --- | --- | ---: |
| Sampling monitor | 0x43EDC..0x43F46 | 106／16 |
| RF_FrequencyHoppingShut | 0x6575A..0x657D8 | 126／16 |
| RF task state handler | 0x657D8..0x65920 | 328／48 |
| Internal RF helper | 0x64794..0x6498A | 502／64 |
| Indexed word setter | 0x43B28..0x43B3E | 22／0 |
| Registered callback | 0x65DE6..0x65F94 | 430／32 |
| RAM byte-compare helper | 0x20000442..0x2000048A | 72／0 |

## 原始行為與限制

RF task `0x65920` 的 event 4／8／16 分支分別呼叫 `0x657D8`／`0x6575A`／`0x43EDC`；event 8 另檢查 context byte `0x2000356C & 4`。較高優先序事件可先返回，不能說有該 bit 就必然呼叫。取樣路徑之後，state byte `0x2000351B == 8` 才以 event 16、原始時間值 1600 排程；時基與活性未證明。

`0x43EDC` 從候選 library config `0x200031EC` 的 +44／+48 讀取 callback，與官方 header 的 `tsCB`／`rcCB` 對應。tsCB 為空時不配置 frame 即返回；舊 halfword `0x200031A4` 為 0 時略過比較動作。其餘路徑保留原式：

```text
hi = low16(max_u32(sample, old))
lo = low16(min_u32(old, sample))
delta32 = hi - lo
action iff int32(delta32) > 20
```

僅在 callback 遵守官方 `uint16_t` 回傳 ABI 時，可將它解讀為絕對差值 >20。不是已確認的攝氏溫差。動作依序為可選 rcCB、common reset、寫回 sample 低 16 bits，依賴 callee 正常返回、保存暫存器及有效記憶體。實機 callback 值與效果未觀測。

官方 header／candidate table 的 index 116、slot `0x40204` 指向 `RF_FrequencyHoppingShut`。它停止 task events 8／4，依 flags 以原始 status 34，或次順位 status 36 呼叫 `0x20003550` 的 callback，再清除 context flags。釋放自身 16-byte frame 後，以 A0=0、A1=2 尾跳 `0x43B28`，寫入 indexed word `0x200031D0`；不改作保留 frame 的一般 call。Indexed setter 僅在 unsigned index<=4 時寫入，array 實體容量／所有權未證明。

內部 helper 準備的 callback literal `0x65DE6` 有本輪完整實體本體。仍保留 **5 個 opaque callback calls**，包括兩次讀取 clock-like word `0x200031E0`。RAM helper 比較 bytes，null／零長度或相同比較路徑回傳 1、不同比較路徑回傳 0；同時保留 hardware word `0x4002420C` 的 save／clear／FENCE.I／restore。這沒有證明 IRQ mask、原子性或 caller bounds。

## 驗證

C11／C++17 CODE 與 ABI 物件完全相同。全部原始情境 bytes、完整 CFG 自身 frame、9 個 far call pairs、52 個官方 Xwchc 正例與 38 個實際 ports 通過；16 個明確匯入都有既有實體 provider。104 個 FUNC 是編譯區段，不是邏輯函式數。

累計唯一組合 **20,112 CODE＋256 DATA bytes／6,906 指令**，1,298 個 FUNC 區段、977 個 relocation；具名缺口由 **14 降至 11**，沒有新增具名缺口。逐輸入 bytes／symbols／relocations 與原始 PC 唯一性通過。

完整組合有 2,218 sections，超過舊 reader 的 <2,048 上限。本輪另存有界 v6 reader（<4,096），只改 section ceiling 與說明，其他結構／file extent 檢查維持。獨立 parser 比對全部 fields／bytes／symbols／relocations；原有 2,040-section 物件與 v5 完全一致。以實際大物件重現舊上限失敗，沒有合成測試輸入。原 v5 reader 保留。

先前 ABI trial 因缺少型別宣告而失敗；目前 native-v2 直接包含固定官方 header，驗證 RF config 32B、library config 64B、tsCB+44／rcCB+48 及 uint16_t／void callback 型別。失敗 native-v1／部分 composition-v1 保留本機；目前依據為 native-v2／audit-v2／composition-v2。

APP 仍為 159 個正式 C/H、95.54% 位元組覆蓋率，不是功能完成率。未整合進 APP、未產生 BIN、未執行目標／模型或操作硬體。4-byte 啟動來源缺口、ROM／RAM／ISA／IRQ、全程 stack／alias、callback、Flash／OTA 相容性仍未確認；**尚未成功重建可用替代韌體**。取樣／校準來源與跳頻狀態診斷可列為後續觀測功能，尚未實作 UI。

[C/C++](original_RF_task_path.c) · [原始指令](evidence-v1.json) · [完整收據](audit-result-v2.json) · [摘要](summary.json)

## 重現

需 spec 固定的本機輸入、先前 native artifacts、Windows NDK LLVM 與 trap 驗證的官方 header；不會下載缺少的輸入。

```sh
python experiments/tsl9-original-RF-task-path/build-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-original-RF-task-path/build/native-v2
python experiments/tsl9-original-RF-task-path/audit-v2.py --tool-dir "$LLVM_BIN" --reference-root "$REFERENCE_ROOT"
```

建立新產物時，用 `--trial` 取代 `--replay`，第二行加 `--link-trial`；名稱須未存在。跨平台編譯未驗證。
