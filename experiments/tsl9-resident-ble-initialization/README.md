# BLE 啟動與 heap 候選 C/C++

[English](readme.en.md) · [heap 初始化](../tsl9-resident-heap-initialization/README.md) · [配置／釋放](../tsl9-resident-heap-core/README.md)

本輪重建公開 WCH SDK V1.31 的三個完整候選本體。**實機 ROM／ISA 尚未確認，不是可刷韌體。**

| 本體 | 位址域與範圍 | bytes |
| --- | --- | ---: |
| task 初始化 | Flash `0x43B3E..0x43C4E` | 272 |
| `BLE_LibInit` | Flash `0x43C7E..0x43D62` | 228 |
| `tmos_memset` | 條件式 RAM `0x2000039C..0x200003CA` | 46 |

[來源](resident_ble_initialization.c)共 **546 bytes／193 條指令**，49 個正尺寸 FUNC 區域、39 筆重定位。C11／C++17 物件完全相同，還原原始位址編碼後全部 bytes 吻合；23 條條件式 Xwchc byte／halfword 指令埠已依官方定義及 28 個向量核對。相鄰的獨立函式 `0x43C4E..0x43C7E` 未選入。

## 本輪證據

- 原 APP 在 `0x19A3A` 編碼設定起點 `0x2000418C`、長度 `0x7000`（28 KiB），數值終點為 `0x2000B18C`。這是宣告範圍，不是實體 RAM 容量或所有權證明。
- 原 APP 呼叫 `0x19AEC` 經指標槽 `0x400A4`，該 SDK 候選槽指向 `0x43C7E`；候選內的直接鏈為 `0x43D4C → 0x43B3E`、`0x43B88 → 0x43104`。此為條件式候選流程，未量測裝置 ROM。
- 64-byte 設定的 `staCB` 位於 offset52（stack+68..72）。14 個明確欄位寫入、MAC helper 的 6-byte 寫入與後續 MAC 複製皆避開此欄位；但 `0x43D38` 會呼叫 `tsCB`，其副作用及 IRQ／alias 契約尚未閉合，不能斷言 heap 呼叫時 `staCB` 為零。未讀取硬體 MAC／UID 值。
- task 初始化有配置回傳 null 後直接恢復並返回的指令路徑；外層在 task 正常返回後強制回傳數值0。未執行或證明該路徑在有效設定下可達；**數值0不能單獨證明完整啟動成功**。

## 實際部分連結

加入既有的配置／釋放、訊息 API、heap 初始化及複製函式後，C／C++ 非載入式 ET_REL 均為 **1336 bytes／467 條指令**，116 個正尺寸 FUNC、86 筆重定位；每個輸入 byte、符號與重定位皆保留。

三個新匯入由真實既有函式解析：複製、heap 配置、heap 初始化。仍有三個具名未解析函式（`0x200004BC`、`0x4329A`、`0x44022`），以及原始 RAM、callback 與回呼表 CODE 位址相依。未連入 APP，也未進行原位址執行連結。

證據：[audit-result-v2.json](audit-result-v2.json)、[summary.json](summary.json)、[原始指令與向量](evidence-v1.json)、[官方標頭 ABI 斷言](config_abi.c)。APP 正式 byte 覆蓋維持 **95.54%**，不是功能完成度。

## 重跑

需先備妥 [spec-v1.json](spec-v1.json)／[evidence-v1.json](evidence-v1.json)列出的原始 APP、SDK carrier、官方標頭與指令參考。SDK 原始參考輸入未隨本次提交提供；audit 也需要前述候選與 curation 的既有建置產物，不會自動下載或重新產生。使用固定雜湊的 Windows NDK LLVM，從專案根目錄執行；`LLVM_BIN` 為工具目錄，trial 名稱須尚不存在：

```sh
python experiments/tsl9-resident-ble-initialization/build-v1.py --tool-dir "$LLVM_BIN" --trial native-v1
python experiments/tsl9-resident-ble-initialization/audit-v1.py --tool-dir "$LLVM_BIN" --link-trial composition-v1
```

已有產物時，第一個指令改用 `--replay experiments/tsl9-resident-ble-initialization/build/native-v1`，第二個省略 `--link-trial`。沒有執行目標／HOST 模型／ISA 模擬、連接硬體或新增 BIN。

值得新增的功能：啟動配置完整度與 heap 診斷。目前僅列候選，需先確認實機 RAM、callback／IRQ 所有權及真正的完成條件。
