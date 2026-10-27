# Record 比較 helper 與 0x588B4 handler

[English](readme.en.md) · [前輪本體](../tsl9-resident-task-final-handlers/README.md) · [排程配置契約](../tsl9-scheduler-allocation-contract/README.md)

[C/C++](resident_record_comparison.c) 重建兩個完整候選 SDK 本體，共 **592 bytes／211 條指令**。保留原始暫存器與執行 context，不能當作 HOST API 呼叫，也不是還原出的原廠 C 原始碼。

| 原始半開範圍 | Bytes／指令 | 自身 stack frame |
| --- | --- | --- |
| `0x588B4..0x58988` | 212／77 | 32 bytes |
| `0x585C8..0x58744` | 380／134 | 32 bytes |

實際 C11／C++17 物件相同；59 個正尺寸 FUNC、62 筆重定位（46 個直接控制、7 組 far call、1 組 far tail）。15 個 Xwchc 指令埠按官方定義與既有 52 個正例核對；原位址正規化後全部 bytes 相同。所有 CFG 指令可到達，自身 frame 在出口平衡，早期 RET 後可達分支完整保留。

## 關鍵證據

- 完整 caller `0x58C52` 的實際編碼呼叫指向 `0x588B4`，位置保留於 [audit-result-v2.json](audit-result-v2.json) 的 `contract.actual_588B4_call_sites`。
- `0x58956` 呼叫 `0x585C8`。其後 `0x5895A` 對 A0 做 zero 判斷：zero 略過 `0x58498`；非 zero 才呼叫。這是原始分支極性，不代表任何實機成功／失敗語意。
- helper 依序讀取 halfwords `+2/+4/+6/+8`，用高半部左移 16 組成 A0／A1。`0x586F4` 恢復 RA、`0x586FC` 釋放 32-byte frame；`0x586FE/0x58702` 為 **AUIPC t1／JALR zero**，直接跳往既有 RAM `0x20002276`。原始 no-link tail 沒有改成普通 C call。
- 五個匯入已有真實既有本體；`0x58498` 保留為真正未解析相依，沒有補 stub。相鄰 `0x58744` 等函式不屬於這兩個完整本體，未宣稱已供應其行為。

唯一 CODE 所有權與兩個獨立 ELF 讀取器核對後，組合為 **30,440 CODE + 256 DATA bytes／10,532 指令**；2067 FUNC、1648 relocations。具名缺口由 4 降至 **3**：`0x58498`、`0x58788`、`0x58988`。這三個入口還會牽出其他相依；具名缺口數不是整條執行鏈完成度。

證據：[audit-result-v2.json](audit-result-v2.json)、[evidence-v1.json](evidence-v1.json)、[summary.json](summary.json)、[frames_abi.c](frames_abi.c)。原 APP 159 個 C/H 與 95.54% 靜態 byte 覆蓋不變。候選 SDK 身分、實體 ROM／RAM／ISA／IRQ、Flash／OTA 相容性仍未證明；啟動來源仍缺 4 bytes。**沒有新增 BIN，尚不可宣稱可刷。**

## 重驗

需備妥 spec／evidence 所列的雜湊參考與前序產物，不會自動下載。由專案根目錄執行；`LLVM_BIN` 與 `REFERENCE_ROOT` 指向本機工具與既有參考目錄：

```sh
python experiments/tsl9-resident-record-comparison/build-v1.py --tool-dir "$LLVM_BIN" --trial native-v1
python experiments/tsl9-resident-record-comparison/audit-v1.py --tool-dir "$LLVM_BIN" --reference-root "$REFERENCE_ROOT" --link-trial composition-v1 --output audit-result-v2.json
```

建立名稱須尚不存在。已有產物時，第一行改用 `--replay experiments/tsl9-resident-record-comparison/build/native-v1`，第二行移除 `--link-trial` 與 `--output`。沒有執行目標／HOST 模型／ISA 模擬或硬體。

可新增的方向：離線工具將回覆碼連到原始分支與 PC 證據。尚未實作，不能在未確認實機語意時顯示硬體成功。
