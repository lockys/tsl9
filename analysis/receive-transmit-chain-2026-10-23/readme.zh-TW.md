# 原位接收／分派／傳送鏈

[English](readme.en.md) · [繁體中文](readme.zh-TW.md)

本輪把既有來源實際接起來。可閉合部分有 **1588B／555 指令／97 個真實函式**，九段程式位元組全部與原廠 V4.1.60 相同。來源仍是 `src/native/receive/`；[建置配方](../../experiments/tsl9-receive-transmit-chain/README.md)未使用假提供者或原始 opcode carrier。

| 原位址 | Bytes | 內容 |
|---|---:|---|
| 81AA | 6 | GP 狀態讀取 |
| 820C | 60 | 清除 helper 與 predicate |
| 82D2 | 188 | 接收 filter |
| 8520 | 168 | fill |
| 8A56 | 280 | framing 與 resident 交接 |
| 12A08 | 102 | record dispatch |
| 16896 | 326 | SPI 與讀寫提供者 |
| 16B7C | 246 | tagged transmit |
| 18CA4 | 212 | peripheral write |

完整 **1902B／662 指令**的另一份部分連結仍包含 queue consumer，保留 107 FUNC／97 RELA／4 UND：`9454`、`9B36`、`12ABE`、`14D2E`。五個缺失呼叫點為 `12D16/12D1C/12D2C/12D46/12D8C`，沒有省略該缺口來宣稱完整重建。

[間接轉移清單](runtime-boundaries.json)列出六個未知目的地：8356、8A8E、8AB4、12A4E、16BF8，以及無 link 的 8B50。filter 使用 then-live S9；不能把呼叫前的40000永遠套用。resident 身分、GP／stack／IRQ／MMIO／fault 行為仍開放。RX LOAD 共68558B，內含66970B未證間隙，未產生可刷 BIN。

[C 收據](evidence/native-c.json)與 [C++ 收據](evidence/native-cpp.json)各通過1538個負向控制，涵蓋所有1217筆完整 LLVM 位址／位元組列。來源群組包括139個直接輸入、145個 tagged chain 輸入、83個 peripheral 輸入、5份上游收據及3個當前 proof 檔案；群組可重疊，不冒稱為相加的唯一檔數。[獨立檢查](independent-review.json)拒絕24／24變異。

保留失敗v1：兩個小函式的公開名稱與舊整合名稱不同，導致nominal-link失敗；v2僅用兩個明列C名稱對應解決，沒有ABS占位。先前proof對額外／擴張RX LOAD的結構檢查不足，上游來源亦未完整列入；新增verify-v2核對完整PHDR與上游閉包，舊收據不改寫。

可新增的診斷功能：[離線錯誤分類](feature-opportunities.json)。tagged回傳4有多條路徑；SPI timeout的0與真正收到0也可能混淆。未取得足夠觀測時，應回報無法分類，不能僅憑回傳值推定原因。這是待實作建議，不是已新增硬體功能。

[公開來源對照](publication-provenance.json)保留四份可攜原始JSON的完整位元組；含個人路徑的原始編譯日誌保留本機。此輪未呼叫廠商API、執行HOST／ISA模型或操作硬體；GitHub發布另依既有授權執行。
