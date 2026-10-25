# 次要訊息與分派候選重建

[English](readme.en.md) · [C/C++ 原始碼](secondary_message_dispatch.c) · [驗證摘要](summary.json)

已從 ID2966 V4.1.60 重建九段原始上下文程式，共 **2,048 bytes／690 條指令**。C11、C++17 產生相同 RV32 物件；按原位址套回 229 個直接控制轉移及七組 HI/LO 位址參考後，全部程式 bytes 與官方 BIN 相同。兩個 ELF 讀取器核對通過；保守靜態 CFG 涵蓋全部指令。

| 原始範圍（尾端不含） | bytes | 目前確認的結構 |
|---|---:|---|
| `0x1264E..0x12660` | 18 | 狀態寫入與二擇一尾呼叫 |
| `0x12660..0x126A0` | 64 | ROM 間接尾呼叫輔助程式 |
| `0x126A0..0x128FE` | 606 | 七格事件分派，六個不同入口 |
| `0x1330A..0x1333C` | 50 | 六個既有入口及 ROM 尾呼叫 |
| `0x13F7E..0x13F88` | 10 | 參數轉接至既有 `0x13F66` |
| `0x13F88..0x1400C` | 132 | 條件呼叫、callback 位址及尾呼叫 |
| `0x1400C..0x14056` | 74 | 呼叫 0x1330A 及提供兩個 callback 位址；不包含後續私有函式 |
| `0x15584..0x155D0` | 76 | 計數、排程及 12-byte 複製來源 |
| `0x163AC..0x167A6` | 1,018 | 依 A2 比較分支並呼叫多個既有功能入口 |

事件入口的索引是 `(message[0] - 1) & 255`，原始無號 guard 限定到 `0..6` 才查 `0x1A58C`。這個 28-byte 表與 `0x19DD4` 的 12-byte 來源尚未作為 DATA 提供；54 個編譯器 UND 中，52 個可對應既有正式 CODE 入口，另外兩個是上述 DATA。尚未完成與既有 component 的部分連結及原位址放置。

另在**既有程式**發現 `0x1783A → 0x1AAE8` DATA 相依：`GP+370` 的 byte 索引於 `0x17844` 讀表後才取模。尚無全域界限證明；這不是新增來源的兩個 DATA UND，也未選入其內容。編譯器 UND 數量不代表全部執行相依。

## 本機重現

設定 `LLVM_BIN` 指向已安裝的 Android NDK 27.1.12297006 LLVM `bin`（工具雜湊列於 spec）；在 repo 根目錄執行：

```sh
python experiments/tsl9-secondary-message-dispatch/audit-v1.py
python experiments/tsl9-secondary-message-dispatch/build-v1.py --tool-dir "$LLVM_BIN" --trial local-v1
python experiments/tsl9-secondary-message-dispatch/build-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-secondary-message-dispatch/build/local-v1
```

`--trial` 只建立新的目錄。此 C/C++ 仍包含明確的原機暫存器、控制轉移、ROM 與 stack ports，必須保留原始上下文；不是一般可移植函式庫。

此候選尚未納入 `src/` 或正式覆蓋率；正式數字維持 **70,522／76,800 bytes＝91.83%**，這是位址 bytes 覆蓋率，並非功能完成比例。未產出 BIN，未執行目標、HOST model 或 ISA 模擬，未連接硬體或請求廠商 API。啟動、ROM ABI、RAM／IRQ 與 OTA 相容性尚待證明，不能宣稱可刷寫。可考慮新增離線事件／相依瀏覽器，目前僅為建議。
