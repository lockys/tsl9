# Record 配置與 0x58788 尾跳鏈

[English](readme.en.md) · [前輪比較 helper](../tsl9-resident-record-comparison/README.md) · [排程配置契約](../tsl9-scheduler-allocation-contract/README.md)

[C/C++](resident_record_configuration.c) 新增 **3 個完整候選 SDK 本體／1,028 bytes／355 條指令**。保留原始暫存器 context，不能當作 HOST API，也不是原廠 C 原始碼。

| 原始半開範圍 | Bytes／指令 | 自身 frame |
| --- | --- | --- |
| `0x58788..0x588B4` | 300／109 | 16 bytes |
| `0x58744..0x58788` | 68／25 | 16 bytes |
| `0x581CE..0x58462` | 660／221 | 32 bytes |

實際 C11／C++17 物件相同；69 個正尺寸 FUNC、59 筆重定位（45 個直接控制、7 組 far call）。45 個 Xwchc 指令埠按官方定義與既有 52 個正例核對。所有 bytes 在原位址正規化後相同；完整 CFG 可到達、frame 在出口平衡。`0x58462` 起的相鄰函式未選入。

## 重要證據

- 原 caller `0x58C52` 的實際 `0x58788` 呼叫位置保留於 [audit-result-v1.json](audit-result-v1.json) 的 `contract.actual_58788_call_sites`。
- `0x58890..0x5889A` 恢復原始 record 參數、S 暫存器、RA，並釋放 16-byte frame。`0x5889C` 是 **JAL zero → 0x58744**，保留為 no-link tail；`0x5874C` 再正常呼叫 `0x581CE`。
- `0x58744` 從 record+148 取 word，經指標槽 `0x2000353C` 寫到其基底+112；經指標槽 `0x20003508` 對 word+0 OR `0x08000000`，並清除 word+44 的低兩個 bit。這是編碼存取關係，沒有推定實體暫存器名稱、射頻效果或硬體成功。
- `0x581CE` 依 record byte+57 是否等於 8，將 byte+6 寫成 `0xB5` 或 `0xB4`；實際兩處呼叫既有 `0x63B0E`，A1=34。保留原 `DIVU`（`0x5840C`）及串列 next 讀取（`0x58442`）；尚未證明執行時除數非零、記憶體有效或巡訪必定終止，沒有改寫成帶入假設的 C 除法／有界模型。

六個匯入皆有真實既有本體，沒有新增具名缺口或 stub。唯一 CODE 所有權與兩個獨立 ELF 讀取器核對後，組合為 **31,468 CODE + 256 DATA bytes／10,887 指令**，2136 FUNC、1707 relocations。具名缺口由 3 降至 **2**：`0x58498`、`0x58988`；它們仍牽出其他相依，數量不代表執行鏈完成度。

證據：[audit-result-v1.json](audit-result-v1.json)、[evidence-v1.json](evidence-v1.json)、[summary.json](summary.json)、[frames_abi.c](frames_abi.c)。原 APP 159 個 C/H、95.54% 靜態 byte 覆蓋不變。實機 ROM／RAM／ISA／IRQ、Flash／OTA 與全域初始化順序尚未證明；啟動來源仍缺 4 bytes。**沒有新增 BIN，尚不可宣稱可刷。**

## 重驗

備妥 spec／evidence 所列的雜湊參考、前序產物與本機工具，不會自動下載。從專案根目錄執行：

```sh
python experiments/tsl9-resident-record-configuration/build-v1.py --tool-dir "$LLVM_BIN" --trial native-v1
python experiments/tsl9-resident-record-configuration/audit-v1.py --tool-dir "$LLVM_BIN" --reference-root "$REFERENCE_ROOT" --link-trial composition-v1 --output audit-result-v1.json
```

名稱須尚不存在。已有產物時，第一行改用 `--replay experiments/tsl9-resident-record-configuration/build/native-v1`，第二行移除 `--link-trial` 與 `--output`。沒有執行目標、HOST 模型、ISA 模擬或硬體。

可新增方向：離線比較 record 欄位與配置寫入的來源證據。尚未實作；未確認實體暫存器語意前不轉成硬體新功能。
