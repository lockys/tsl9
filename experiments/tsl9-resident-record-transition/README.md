# Record 轉換與 0x58988 雙尾跳

[English](readme.en.md) · [前輪配置鏈](../tsl9-resident-record-configuration/README.md) · [排程配置契約](../tsl9-scheduler-allocation-contract/README.md)

[C/C++](resident_record_transition.c) 新增 **2 個完整候選 SDK 本體／918 bytes／322 條指令**。保留原始暫存器 context，不能當作 HOST API，也不是原廠 C 原始碼。

| 原始半開範圍 | Bytes／指令 | 自身 frame |
| --- | --- | --- |
| `0x58988..0x58C52` | 714／251 | 32 bytes |
| `0x580A4..0x58170` | 204／71 | 32 bytes |

實際 C11／C++17 物件相同；51 個正尺寸 FUNC、47 筆重定位（39 個直接控制、4 組 far call）。17 個 Xwchc 指令埠按官方定義與既有 52 個正例核對。全部 bytes 在原位址正規化後相同；完整 CFG 可到達，自身 frame 在出口平衡。相鄰 `0x58170` 與 caller `0x58C52` 不混入這兩個本體。

## 重要證據

- 原 caller `0x58C52` 的實際 `0x58988` 呼叫位置保留於 [audit-result-v1.json](audit-result-v1.json) 的 `contract.actual_58988_call_sites`。
- `0x58B6C` 為 **JAL zero → 0x58788**；`0x58C2E` 為 **JAL zero → 0x58744**。兩條路徑皆先恢復原 record 參數與 RA，再釋放 32-byte frame；不是一般 C call。目標是前輪已完整重建的真實本體。
- 第一條路徑保留 `0x58B56` 的 bit0 zero 分支；第二條保留 `0x58C1A` 的「比較 helper 回傳值等於 1 才進入尾跳」條件。原數值極性未轉成實機成功／失敗標籤。
- `0x580A4` 從原指標槽 `0x2000353C`、`0x20003508` 取得基底；指令要求對第二基底+8 寫入 `0x8E89BED6`、+4 寫入 `0x00555555`。也將 record byte+6 寫成 `0xB3`，並正常呼叫真實既有 `0x63C54`（A1=255、A2=0）。只確認編碼存取，未推定實體暫存器名稱、射頻行為或硬體成功。

九個匯入皆有真實既有本體；沒有新增具名缺口或 stub。唯一 CODE 所有權與兩個獨立 ELF 讀取器核對後，組合為 **32,386 CODE + 256 DATA bytes／11,209 指令**，2187 FUNC、1754 relocations。具名缺口由 2 降至 **1**：`0x58498`；此入口還會牽出其他相依，不能據此推定執行鏈或韌體接近完成。

證據：[audit-result-v1.json](audit-result-v1.json)、[evidence-v1.json](evidence-v1.json)、[summary.json](summary.json)、[frames_abi.c](frames_abi.c)。原 APP 159 個 C/H 與 95.54% 靜態 byte 覆蓋不變。實機 ROM／RAM／ISA／IRQ、Flash／OTA、全域初始化與回呼效果仍未證明；啟動來源仍缺 4 bytes。**沒有新增 BIN，尚不可宣稱可刷。**

## 重驗

備妥 spec／evidence 所列的雜湊參考、前序產物與本機工具，不會自動下載。從專案根目錄執行：

```sh
python experiments/tsl9-resident-record-transition/build-v1.py --tool-dir "$LLVM_BIN" --trial native-v1
python experiments/tsl9-resident-record-transition/audit-v1.py --tool-dir "$LLVM_BIN" --reference-root "$REFERENCE_ROOT" --link-trial composition-v1 --output audit-result-v1.json
```

名稱須尚不存在。已有產物時，第一行改用 `--replay experiments/tsl9-resident-record-transition/build/native-v1`，第二行移除 `--link-trial` 與 `--output`。沒有執行目標、HOST 模型、ISA 模擬或硬體。

可新增方向：離線工具說明原始狀態分支及對應配置來源。尚未實作；未確認實機協定意義前，不顯示硬體成功或發送控制命令。
