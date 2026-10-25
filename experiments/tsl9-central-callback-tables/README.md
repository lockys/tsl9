> 此頁保留先前實驗快照。最新正式來源與原位址證明見[整合結果](../../analysis/central-callback-integration-2026-10-26/README.md)。

# 中央角色表格與原位址診斷

用 C/C++ 重建三段已觀察到的唯讀表格，共 **92 bytes**：`0x1A548` 的 17 格相對事件表，以及 `0x1A668`、`0x1A674` 的回呼表。五個非空回呼採真正的 `R_RISCV_32` 函式參考，另保留一格原始空指標。這些是選定的表格範圍；原始宣告邊界與實機 ROM 讀取慣例尚未證明。

驗證結果：

- C 與 C++ 產生相同 DATA 物件；三個正大小 OBJECT、92 bytes、五筆重定位全部符合原 BIN。
- 部分連結保留全部 **66,600 CODE bytes、3,922 DATA bytes、4,972 筆重定位**。三個 DATA 相依已補上，剩六個未解析符號；此數字不代表完整執行期缺口清單。
- 原位址診斷 ELF 的 **70,522 bytes** 與原 BIN 相同；17 格事件目標及五個非空回呼都落在實際正大小 FUNC。三組 HI／LO 指標與 DATA 位址也完全一致。
- 既有 71 個 CODE 別名與六個 DATA 標籤保留。一般延續位置無缺口；保守分類器保留原始 `0x8034` 的 `EBREAK` 陷阱例外。

診斷 ELF 為 **entry=0、PT_LOAD=0**，未輸出 BIN、未執行韌體或接觸硬體。六個未提供項目僅作明示的參考常數，沒有以 ABS FUNC 或替代函式充數。實機 MCU／ROM／RAM／IRQ／BLE OTA 與全域狀態邊界仍未證明。

**尚未正式整理進 `src/`；正式覆蓋率仍為 89.03%。** 下一步是把上一輪兩個 CODE 來源及本輪 DATA 來源納入正式來源證明、manifest 與原位址流程。沒有宣稱完整還原原廠原始碼或可燒錄。

## 本機驗證

先依[事件與輔助函式](../tsl9-central-event-callbacks/README.md)建立既有實驗元件。`LLVM_BIN` 指向 spec 雜湊相符的 NDK LLVM 目錄；試驗目錄採只建立模式。

```sh
python experiments/tsl9-central-callback-tables/build-v1.py --tool-dir "$LLVM_BIN" --trial native-v1
python experiments/tsl9-central-callback-tables/integrate-v1.py --tool-dir "$LLVM_BIN" --trial component-v1
python experiments/tsl9-original-layout/build-v61.py --tool-dir "$LLVM_BIN" --trial central-callback-tables-v1
python experiments/tsl9-central-callback-tables/audit-layout-v1.py
```

已存在的 DATA／原位址試驗可用各自 build 的 `--replay` 搭配完整試驗目錄重驗；部分連結採新的試驗名稱，原收據保留。本輪沒有新增產品功能；RSSI 診斷、事件追蹤與欄位解析診斷仍為後續候選。

[English](readme.en.md) · [C 來源](src/central_callback_tables.v1.c) · [證據摘要](summary.json)
