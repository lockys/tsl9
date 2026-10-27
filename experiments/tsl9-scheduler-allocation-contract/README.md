# 排程表配置關係（候選 SDK）

[English](readme.en.md) · [前一輪 C/C++ 本體](../tsl9-resident-task-final-handlers/README.md) · [既有 BLE 初始化](../tsl9-resident-ble-initialization/README.md)

將前一輪 **48 筆 × 12 bytes = 576 bytes** 的索引證據，追溯到候選 SDK 的實際配置請求。這是條件式靜態證據，尚未確認實機 ROM／RAM／IRQ 相容性。

| 已核對的原始指令 | 結果 |
| --- | --- |
| `0x43B90`、`0x43B9A..0x43BB4` | 讀取 `x=byte[0x20003201]`，計算並儲存 `n=3*((x>>2)+(x&3))+14` 至 `0x2000319E`。位元寬度推導 `14≤n≤212`，此式不會遭低 8-bit 儲存截斷。 |
| `0x43BBE/0x43BC2` | 真正的 AUIPC/JALR 目標為候選 RAM `0x20000040`；A0 請求 `576+6*n` bytes、A1=1。代數範圍為 660..1848 bytes，不會繞回配置器的 16-bit 對齊運算。 |
| `0x43BC6`、`0x43BCA` | 回傳值存至 `0x2000322C`；null 分支直接前往恢復／返回，略過後續清除與區段指標設定。不能用外層正常返回單獨判定初始化成功。 |
| `0x43BCC..0x43BDE` | 重新讀取 `n_clear`，要求 memset 清除 `576+6*n_clear` bytes。 |
| `0x43BE2..0x43BFC` | 重新讀取 `p` 與 `n_partition`；`word[0x200031C4]=p+576`，`word[0x200031E4]=p+576+4*n_partition`。 |

只有在配置／清除／分區時的數量一致、回傳指標與後續指標一致，且記憶體有效、不重疊及 callee／IRQ 契約相容時，才能把整塊視為 **576-byte 表格前綴 + 4*n 區段 + 2*n 區段**。這些時間穩定性條件尚未閉合；未宣稱已證明配置容量、所有權、生命週期或全部後續 callback 寫入皆在界內。

## C/C++ 與驗證

[scheduler_layout.h](scheduler_layout.h) 只描述原始 32-bit 數值欄位與條件式配置關係；記錄的第三個 word 未賦予用途。[scheduler_layout_abi.c](scheduler_layout_abi.c) 僅有型別／offset／大小斷言，沒有函式、儲存空間或可呼叫模型。

重新核對六個既有完整本體 **1,104 bytes／386 條指令**、控制流程與當前 C/C++ 組合中的所有權，再實際編譯 C11／C++17。兩份斷言物件相同；獨立 ELF 讀取器確認 allocated bytes／provider／import／relocation 全為 0。未新增目標 CODE，也未執行目標、HOST 模型、ISA 模擬或硬體。

證據：[verification-v1.json](verification-v1.json)、[evidence-v1.json](evidence-v1.json)、[spec-v1.json](spec-v1.json)、[summary.json](summary.json)。候選組合仍為 **29,848 CODE + 256 DATA bytes／4 個具名缺口**；原 APP 靜態 byte 覆蓋仍為 **95.54%**，不代表功能完成度。沒有新增 BIN，也不是可刷韌體。

## 重驗

需先備妥 spec／evidence 雜湊所列的原始參考、前序建置產物、LLVM 及本機參考目錄。既有 native-v1 產物可唯讀重驗：

```sh
python experiments/tsl9-scheduler-allocation-contract/verify-v1.py \
  --tool-dir "$LLVM_BIN" --reference-root "$REFERENCE_ROOT"
```

首次建立數值斷言物件時，加上 `--build-trial native-v1 --output verification-v1.json`；名稱必須尚不存在。工具不下載依賴或寫入硬體。

可新增的功能方向：將配置失敗與 OTA 完成／重啟驗證分開呈現的啟動診斷。此處只列待評估方向，尚未實作或驗證實機診斷通道。
