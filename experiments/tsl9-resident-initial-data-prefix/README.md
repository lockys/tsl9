# 候選 SDK 初始化資料：136-byte prefix

[English](readme.en.md) · [前輪時鐘／亂數證據](../tsl9-original-clock-random-idle-binding/README.md) · [先前 C/C++ 本體](../tsl9-resident-scheduled-record-callback/README.md)

[C/C++](resident_initial_data.c) 重建已擷取的 **34 個 word／136 bytes**，來源 `[0x6EAA4,0x6EB2C)`，條件式 RAM 目的範圍 `[0x20002E70,0x20002EF8)`。這是實際 readonly DATA，不是函式 stub、硬體模型或 Flash 映像；未新增 CODE。

C11／C++17 物件相同，單一正大小 OBJECT、alignment4、零 FUNC／relocation／UND；兩個 ELF 讀取器與原 segment 逐 byte 相符。與既有候選實際部分連結後，完整物件為 **35,324 CODE + 392 DATA bytes／12,195 指令**、2401 FUNC、1914 relocations、4174 sections、0 具名 UND。所有既有 CODE 與 typed relations 保留。[完整收據](audit-result-v1.json)

## 為何仍有 4-byte 缺口

原 HEX 有 **17 個不重疊 segment／191,244 個資料 bytes**。主 segment 的 191,078 bytes 不包含最後這份 136-byte 資料；它有獨立擷取檔。驗證器重新檢查全部 11,973 筆 HEX record 的長度、checksum、位址及所有 segment，沒有將 holes 補零或填 FF。

原啟動 helper 的 unsigned guard 會複製**包含上界的最後一個 word**：

| 操作 | 實際要求來源／目的範圍（end exclusive） | 大小 |
| --- | --- | ---: |
| 第一段 copy | `0x402B0..0x430E4` → `0x20000040..0x20002E74` | 11,828 bytes |
| 第二段 copy | `0x6EAA4..0x6EB30` → `0x20002E70..0x20002EFC` | 140 bytes |
| 已擷取第二段 prefix | `0x6EAA4..0x6EB2C` → `0x20002E70..0x20002EF8` | 136 bytes |
| 尚未擷取的最後 READ32 | `0x6EB2C..0x6EB30` → `0x20002EF8..0x20002EFC` | 4 bytes |

後續 zero helper 的範圍為 `[0x20002EF8,0x20003618)`。它必須等 copy 正常返回才執行，**不能因稍後清零就跳過先前 READ32**。擷取缺失不代表已證明原硬體會讀取失敗，也不能自行補造該 word。

## 可確認的條件式初值

prefix 的第 22 個 word（zero-based）在來源 `0x6EAFC`，值為 `0x012F81C3`，對應亂數狀態 `0x20002EC8`。若已知 prefix 確實依原指令複製、先前存取正常且沒有覆寫，該值會在缺口讀取之前寫入。

這仍未證明實際完成啟動、首個亂數呼叫看到的值、熵、MRET context 或原硬體 ROM 身分。先前「live 初始種子未證明」的限制保持有效。

APP 的 159 個 C/H 檔與 **95.54% 靜態 byte 覆蓋率**不變；本輪資料屬於候選 SDK，尚未納入原 APP。沒有原位址最終連結、硬體執行或新 BIN；ROM／RAM／ISA／IRQ／Flash／OTA 相容性仍未解決，**尚不可宣稱可燒錄**。

可將本輪的離線稀疏來源檢查納入未來產物檢查流程；目前只在驗證器中實作，未整合 App 或燒錄器。

需具備收據固定的原參考檔、既有 native 物件及 LLVM；不自動下載。在專案根目錄首次建立：

```sh
python experiments/tsl9-resident-initial-data-prefix/build-v1.py --tool-dir "$LLVM_BIN" --build
python experiments/tsl9-resident-initial-data-prefix/audit-v1.py --tool-dir "$LLVM_BIN" --link --write-receipt
```

已有產物時省略 `--build`、`--link`、`--write-receipt`，執行唯讀核對；建立流程不覆寫既有產物。
