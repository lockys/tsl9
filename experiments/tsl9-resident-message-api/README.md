# 訊息配置／釋放：公開 SDK 候選重建

[English](readme.en.md)

本輪重建的是 **公開 WCH SDK 的兩個候選入口**，不是從 TSL9 實機讀出的 ROM。原 APP 的三個配置呼叫與四個釋放尾呼叫，分別讀取 `0x40070`、`0x40068` 指標；保存的 header 將它們定義為 `tmos_msg_allocate`（slot15）與 `tmos_msg_deallocate`（slot13）。

來源保留原暫存器情境及明示組語埠，不能作一般 C API 直接替換。

| V1.31 候選入口 | 已確認的靜態行為 |
|---|---|
| `0x20000236`，86B | 條件式 RAM 映射的配置本體。非零輸入傳入 heap helper 的長度為 `(len+8)&65535`，另傳 `0xF000 | len`；寫入私有標頭，成功路徑回傳底層指標＋8。 |
| `0x431BA`，78B | Flash 釋放本體。NULL 路徑回5；`payload[-2] != 0xFF` 路徑回4；其他路徑呼叫另一 heap helper 後回0。這些數值不證明實際釋放成功。 |

配置標頭可見 word `+0` 清零、halfword `+4` 儲存長度、byte `+6` 寫入 `0xFF`；不推斷其他 byte 已初始化。原 APP 的12-byte請求，依此候選會傳長度20給 heap helper，**不是完整 heap 實體占用量證明**。

兩入口都讀取 `0x4002420C`、寫零並執行 `FENCE.I`，各局部正常回傳路徑都有還原儲存指令，包括 NULL 路徑。該 MMIO 含義、callee 暫存器保存、IRQ 原子性與實際還原效果仍未證，不能直接改成一般 `malloc/free`。

## 原生證據與版本限制

[`resident_message_api.c`](resident_message_api.c) 實際編成 C11、C++17 後，兩個物件完全相同：164B／62條指令、14個正長度區段、11個 relocation。原位址重編碼後逐 byte 等於候選來源；兩套獨立 ELF 解析器核對通過。[摘要](summary.json) · [稽核收據](audit-result-v1.json)

標準解碼器將兩個16-bit word標為浮點儲存；依保存的官方 LLVM Xwchc 格式，它們是 `qk.c.sh s0,4(a0)`、`qk.c.sb a5,6(a0)`。來源保留兩個明示原始編碼埠。編譯器的架構屬性**不證明**實體 CPU profile。

V1.31／V1.40 候選的86B配置碼在各自 RAM 映射下完全相同；78B釋放碼的原始 bytes 不同，僅在扣除一組 far-call 位移後吻合。實際 slot13 指標也不同：`0x431BA`／`0x43246`。沒有比較底層 heap helper 的實作，不能因此推論兩版 ROM 可互換。

兩個真實相依 `0x20000040`、`0x20000110` 仍未提供，未補假函式。候選未併入 APP；正式來源仍159個 C/H檔，APP位元組覆蓋率仍95.54%。沒有產出BIN、執行目標／模擬器、操作硬體或連線供應商服務。

## 本機唯讀重播

需要已保存且固定雜湊的 SDK、header、LLVM參考及原生輸出。`LLVM_BIN` 指向本機工具目錄；本收據使用 Windows Android NDK27.1／LLVM18。其他平台未驗證。

```sh
python3 experiments/tsl9-resident-message-api/build-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-resident-message-api/build/native-v1
python3 experiments/tsl9-resident-message-api/audit-v1.py --tool-dir "$LLVM_BIN"
```

Windows 可用 `py -3`。前置原生輸出與 SDK carrier 不隨本輪文字提交上傳。可考慮做離線訊息狀態解說工具；尚未實作，也不能把這裡的0／4／5與OTA字母E回覆混為一談。
