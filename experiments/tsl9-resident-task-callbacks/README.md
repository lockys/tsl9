# 已註冊 task 回呼候選 C/C++

[English](readme.en.md) · [前一輪 SNV 初始化](../tsl9-resident-snv-initialization/README.md)

重建公開 WCH SDK V1.31 的兩個完整回呼，並核對既有原 APP 的 Flash 參數流程。**實機相容性尚未確認，沒有新增可刷 BIN。**

| 本體 | 候選 Flash 範圍 | bytes |
| --- | --- | ---: |
| 已註冊回呼1 | `0x432A4..0x43326` | 130 |
| 已註冊回呼2 | `0x43326..0x433A8` | 130 |

[C/C++ 來源](resident_task_callbacks.c)共 **260 bytes／104 條指令**、26 個正尺寸 FUNC、16 筆重定位。C11／C++17 物件完全相同，還原原始位址編碼後每個 byte 均吻合；本輪未選入 custom 指令。它們需要原始暫存器與私有執行環境，不是一般可直接呼叫的 C API。

## 已確認的指令行為

- 初始化的三個表格寫入 `0x43C1A`／`0x43C30`／`0x43C42` 分別存入 `0x432A4`／`0x43326`／`0x43326`。本輪為這些數值 CODE 指標提供真實本體，尚未做原位址執行連結。
- 兩個回呼以 bit index 與入口 A0 計算記錄位址：`record_array + 12 × (16 × A0 + bit)`，每次返回最多處理一個事件。`0x432EA` 呼叫前有 null 檢查，`0x43390` 沒有；callback 的 A0 來自所選記錄的第二個 word。
- 回呼1的第三 word 測試來自 `record_array + 12 × bit + 8`，與所選記錄的索引公式不同。程式保留此差異，不推斷它是錯誤或擅自修正。回呼2在 bit15 設定時呼叫訊息接收，非空結果交給真實釋放函式；其回傳值未使用。

## Flash 參數核對

四個既有完整 APP 本體共 **226 bytes／90 條指令**；本節沒有新增 APP CODE。

- `0x1979A` 將讀取參數變為 `copy(buffer, address, num << 2)`，經指標儲存位址 `0x4004C` 呼叫；SDK 候選在該處指向已重建的 `0x20000332`。正常返回後回覆數值0，並未驗證讀取內容。
- `0x197BE → 0x18EF2` 將保存的 buffer 指標放入 A1／A2；helper 在資料迴圈前把 A2 改為常數256。因此不能僅因指標重用就判定 ABI 錯誤，入口的 num 也不是該 helper 的搬移計數。
- 若輪詢正常結束、暫存器／記憶體契約成立，helper 從 A1 指向的連續256 bytes 讀取64個 word，向 `(A0 & 0xFFFFFF00)` 起的256-byte 區域做64次 CPU word store。erase helper 亦將地址低8位清零。**這不是實體 Flash 成功提交、容量或可安全刷寫的證明。**
- 256-byte SNVBlock 與該固定搬移大小數值一致；其他 block 大小、回呼附帶 helper、實體位址、輪詢終止、IRQ／stack／alias 仍待驗證。沒有執行讀寫 Flash。

## 部分連結與限制

與既有1568-byte 候選做實際非載入式 ET_REL 部分連結後，C／C++ 均為 **1828 bytes／654 條指令**、164個正尺寸 FUNC、120筆重定位。真實訊息釋放函式解析一個匯入；**訊息接收 `0x2000028C` 仍是具名未解析相依**，沒有用 stub 補齊。每個輸入 byte、符號與重定位皆保留。

原始 RAM、記錄 callback 與實機 ROM／ISA／IRQ／OTA 相容性仍未閉合，未連入 APP。正式 APP byte 覆蓋維持 **95.54%**，不是功能完成度。可考慮新增 callback 生命週期與持久化診斷，目前尚未實作。

證據：[audit-result-v1.json](audit-result-v1.json)、[summary.json](summary.json)、[原始 SDK 指令](evidence-v1.json)。

## 重跑

需先具備 [spec-v1.json](spec-v1.json)／[evidence-v1.json](evidence-v1.json)與 audit 所列的原始 APP、SDK carrier、標頭／指令參考及前述候選的既有建置產物。SDK 原始輸入與 native 產物未隨此次提交提供，指令不會自動下載。使用固定雜湊的 Windows NDK LLVM，從專案根目錄執行：

```sh
python experiments/tsl9-resident-task-callbacks/build-v1.py --tool-dir "$LLVM_BIN" --trial native-v1
python experiments/tsl9-resident-task-callbacks/audit-v1.py --tool-dir "$LLVM_BIN" --link-trial composition-v1
```

trial 必須尚不存在；已有產物時，第一個改用 `--replay experiments/tsl9-resident-task-callbacks/build/native-v1`，第二個省略 `--link-trial`。未執行目標／HOST 模型／ISA 模擬，未連接硬體或廠商 API。
