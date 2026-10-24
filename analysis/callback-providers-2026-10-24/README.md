# Callback 提供者與常數資料整合

[English](readme.en.md)

已重建 D272、B0FC、12B24、13D48、10630，並保留真正被註冊的 B0D0 回呼，來源位於 [src/](../../src/native/receive/callback_providers.c)。新增 **558B／188 條指令與 62B 唯讀資料**；C11／C++17 均與原廠 BIN 的選定原碼、七項相對表及兩組常數相符。

整合後主元件為 **12782B code＋578B data、4464 條原始指令、860 RELA、81 UND**，兩種語言產物一致。所有既有 12224B code 與 516B data 保持相同；10 個新增入口別名均指向真實程式，未加入假回傳函式或 ABS 提供者。

[指令證據](evidence.json) · [結果與雜湊](summary.json) · [未解析入口](next-providers.json) · [整合檢查器](../../experiments/tsl9-callback-providers/integrate-v1.py)

| 原始入口 | 已確認的指令行為／限制 |
| --- | --- |
| D272 | 載入 resident 槽位 40048，保留長度 19 的清除參數；installed 身分未證 |
| B0FC／B0D0 | 初始化 GP+192 附近資料，傳入 B0D0 回呼位址；回呼依旗標更新三個 byte 計數。功能意義與 resident 身分未證 |
| 12B24 | 七項相對分派及堆疊資料組裝；共用 ret 後的 case 保留至 12BC8 |
| 13D48 | 保留狀態條件、GP+344 時間欄位與 100／35 通知參數；時間單位與實體效果未證 |
| 10630 | 兩組 17-byte 範本、GP+328 計數與資料組裝；未假設索引永遠有效 |

接通五個舊入口，並將新呼叫中的五個接到既有真實函式；其餘七個新入口繼續展開，所以未解析數 **79→81**。下一步追查 1070A、1299E、129C4、12AA0、13346、135E6、16DD4。

來源集現有 97 個 C/H、70 個 code units。含獨立指標資料共通過 142 組比較／284 個物件；舊 138 組結果及 829 筆產物記錄完全保留。新清單是精確的 96→97 檔延伸；凍結的舊檢查器未修改，不宣稱舊整份 manifest 的重播已適用新版。初次 native-v1 的換行跳脫編譯錯誤及原來源保留為 UNACCEPTED，僅 native-v2 計為通過。

在專案根目錄以本機 LLVM 目錄重查：

```sh
python3 experiments/tsl9-callback-providers/integrate-v1.py --tool-dir "$LLVM_BIN" --replay experiments/tsl9-callback-providers/build/component-v1
```

這仍是 VMA=0、保留 relocation 的 ET_REL 部分連結物件。原始程式／資料配置、RAM 擁有權、私有 ABI、實體 MCU／installed ROM／中斷與 OTA 相容性未證明，**不能燒錄**。未執行目標、模型或 ISA 模擬，未連線、接觸硬體或產生 BIN；歷史個資仍未清除，未 commit／push。

新功能候選是只讀的 callback／計數／通知診斷與韌體來源辨識。這次取得更多原始依據，尚未實作介面，也不以未知時間單位改動控制策略。
