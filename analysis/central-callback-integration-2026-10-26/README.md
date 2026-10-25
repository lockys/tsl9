# 中央角色回呼：正式來源與原位址整合

已把三個通過驗證的來源整理進 `src/`：三個回呼、五個輔助函式及一個事件回呼，共新增 **2,056 CODE bytes／686 條指令**；三個唯讀表格新增 **92 DATA bytes**。

- 完整來源：**156 個 C/H 檔、123 個 CODE 單元、七個 DATA 單元；260 組比較／520 個物件**。舊有 242 組 CODE 結果與 1,453 筆產物紀錄全部保留。
- 原位址：**70,522／76,800 bytes（91.83%）**，包含 66,600B CODE 與 3,922B DATA。4,972 筆重定位、71 個 CODE 別名與六個 DATA 標籤均保留。
- 靜態流程：22,624 條指令、4,347 個直接轉移、1,336 個呼叫返回位置、12 個守衛跳轉表；一般延續位置無缺口。886 個暫存器間接轉移包含返回指令，其整體執行期目標仍未證明。
- 回呼表：17 格事件目標與五個非空回呼均有實際正大小 CODE；三組 HI／LO 指標對應實際 DATA。原本四個候選回呼 CODE 缺口已補上。

仍有六個編譯器未解析符號，包括兩個未提供 CODE 與四個 DATA 位址。這個數字不等於全部執行期缺口。事件／回呼 ROM ABI、原始宣告邊界、全域 RAM／索引／非同步條件與實機相容性仍未證明。

產物仍為 **entry=0、PT_LOAD=0 的診斷 ELF**，保留原始 EBREAK 邊界與十個特權返回。沒有生成 BIN、執行韌體、接觸硬體或呼叫廠商 API。91.83% 是原位址位元組覆蓋，不是功能完成率、完整原始碼還原或可燒錄比例。

## 來源與重驗

[回呼來源](../../src/native/receive/central_callback_leaves.c) · [事件／輔助來源](../../src/native/receive/central_event_callbacks.c) · [表格來源](../../src/native/receive/central_callback_tables.c)

工具與既有產物齊備時，以專案根目錄及 `LLVM_BIN` 執行：

```sh
python experiments/tsl9-central-callback-tables/integrate-v2.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-central-callback-tables/build/component-v2
python experiments/tsl9-original-layout/build-v62.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-original-layout/build/central-callbacks-v2
python experiments/tsl9-original-layout/verify-flow-v62.py --replay experiments/tsl9-original-layout/build/central-callbacks-flow-v2
```

來源證明的 `build/source-proof-v2.json` 採只建立模式；既有收據可由 `integrate-v2.py --replay` 一併重驗。原生物件整理流程見 [src 說明](../../src/README.md)。目前只驗證 Windows／指定 NDK LLVM，其他平台需重新取得同等證據。

下一步持續追查剩餘依賴及原機執行條件。RSSI 診斷、事件追蹤與欄位解析診斷為可研究的新功能，尚未實作。

[English](readme.en.md) · [摘要](summary.json) · [證據索引](evidence.json) · [提供者契約](provider-contracts.json)
