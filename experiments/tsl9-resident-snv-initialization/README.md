# SNV 與訊息初始化候選 C/C++

[English](readme.en.md) · [前一輪 BLE 啟動](../tsl9-resident-ble-initialization/README.md)

重建公開 WCH SDK V1.31 的三個完整函式，補上前一輪的三個具名相依。**實機 ROM／ISA 尚未確認，沒有新增可刷 BIN。**

| 本體 | 候選位址範圍 | bytes |
| --- | --- | ---: |
| `tmos_isbufset` | 條件式 RAM `0x200004BC..0x200004FA` | 62 |
| 訊息初始化 | Flash `0x4329A..0x432A4` | 10 |
| SNV 初始化 | Flash `0x44022..0x440C2` | 160 |

[C/C++ 來源](resident_snv_initialization.c)共 **232 bytes／83 條指令**，22 個正尺寸 FUNC、18 筆重定位。C11／C++17 物件完全相同，還原原始位址編碼後全部 bytes 吻合；4 條條件式 Xwchc 指令埠依官方定義及 28 個向量核對。相鄰函式不在選取範圍內。

## 可確認的行為

- `tmos_isbufset` 在空指標或長度0時返回0；逐 byte 與完整 A1 暫存器值比較，全部相同返回1。函式保存、清零並還原 `0x4002420C`，但該 MMIO 的實體語意尚未確認。
- `0x4329A` 只把 `0x20003198` 的 word 清零後返回。
- `0x44022` 讀取 64-byte 設定內的 SNVAddr／SNVBlock／SNVNum（offset8／12／14），經 readFlashCB（offset56）讀取一個本地 word，與 SNVAddr 比較。**呼叫端未使用讀取回呼的回傳值，不能假設輸出有效。**
- 未跳過的路徑以 SNVBlock 配置真實 heap buffer、填入 `0xFF`，按 SNVNum 迴圈，寫入位址為 `SNVAddr + SNVBlock × index`。A1 為 `SNVBlock >> 2`、A2 為 buffer；每次回呼前把 buffer 第一個 word 改成該位址。writeFlashCB 的回傳值亦未使用。位址、容量、至少4-byte buffer、計數單位與回呼效果仍需契約；沒有實際讀寫 Flash。
- 數值1涵蓋停用 SNV、缺少回呼、首 word 已相同及配置失敗等不同路徑；迴圈結束、heap 釋放正常返回並清零兩個狀態 word 後為0。這些是條件式指令路徑，**不是持久化成功證明**。

`tsl9_candidate_system_task_initialize_44022` 保留舊匯入名稱以便連結；本輪證據支持 SNV／Flash 初始化行為，不把「system task」當成已確認功能。

## 部分連結與限制

與既有 1336-byte 候選做實際非載入式 ET_REL 部分連結後，C／C++ 均為 **1568 bytes／550 條指令**、138 個正尺寸 FUNC、104 筆重定位。六個跨輸入匯入均由真實既有函式解析，每個輸入 byte、符號與重定位皆保留。

**具名 UND 為0，不等於執行層閉合。** 原始 RAM、Flash／其他回呼，以及 CODE 指標 `0x432A4`／`0x43326` 仍有相依；沒有連入 APP 或進行原位址執行連結。實體 RAM／IRQ／stack／Flash／ROM／OTA 相容性仍未確認。APP 正式 byte 覆蓋維持 **95.54%**，不是功能完成度。

證據：[audit-result-v3.json](audit-result-v3.json)、[summary.json](summary.json)、[原始指令與向量](evidence-v1.json)、[官方標頭 ABI 斷言](config_abi.c)。可考慮新增 SNV 初始化階段及持久化診斷；目前僅列候選，尚未實作。

## 重跑

需先備妥 [spec-v1.json](spec-v1.json)／[evidence-v1.json](evidence-v1.json)列出的原始 APP、SDK carrier、官方標頭與指令參考，以及前一輪候選的既有建置產物。SDK 原始參考輸入與 native 產物未隨此次提交提供；指令不會自動下載。使用固定雜湊的 Windows NDK LLVM，從專案根目錄執行：

```sh
python experiments/tsl9-resident-snv-initialization/build-v1.py --tool-dir "$LLVM_BIN" --trial native-v1
python experiments/tsl9-resident-snv-initialization/audit-v1.py --tool-dir "$LLVM_BIN" --link-trial composition-v1
```

trial 必須尚不存在；有產物時，第一個指令改用 `--replay experiments/tsl9-resident-snv-initialization/build/native-v1`，第二個省略 `--link-trial`。未執行目標／HOST 模型／ISA 模擬，也未連接硬體或廠商 API。
