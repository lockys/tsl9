# 資料索引與來源物件的離線枚舉

[English](readme.en.md)

針對 `0x1AB48+2*index` 枚舉 byte 索引 0–255，以目前原位址布局的 DATA owner 判斷每次兩 byte 讀取是否完整位於單一物件。76 個索引符合此**位址**條件，但只有 0–3 屬於專用計數器窗口；4–7 對應另一個 record dispatch 資料物件，8–11 對應 service threshold 資料，12–75 對應 reset initializer。這些相鄰物件可佔用同一數值區域，並不證明它們是查表的有效資料或索引可達。

針對 `0x1A078+16*mode+column`，枚舉 256 列、每列 16 bytes：149 列完整落在單一 DATA owner；另外 107 列跨物件、未涵蓋或不在映像中。此前統計的 164 列是所有 bytes 均落於某個 DATA owner，包含跨多個 owner 的列；兩個數字的判準不同，均不代表表格語意有效。

以 byte mode 0–255 和 column 0–15 計算原始位址：mode 0–183 的列完整落在 APP 數值區間內，但 mode 98 的 column 4–7 落在排除的 `[0x1A69C,0x1A6A0)`；mode 184 的 column 0–7 在 APP 內、8–15 在 APP 外；mode 185–255 的整列均在 APP 外，共 1,144 個 APP 外位址。這些分類不讀取任何 payload，也不代表特定 mode 或 column 可達。

現有 layout 的另一個限制是：mode 92–94 的三列正好對應 `0x1A638` 的 48-byte sequence 資料物件；mode 173 的 column 0–7 對應 `0x1AB48` 的 8-byte counter 資料物件。位址重合只證明物件覆蓋關係，不代表這些資料是該 mode 查表的有效項目。要提供完整 `0x1A078` 依賴，仍須獨立建立 mode 的實際範圍及資料用途，不能把相鄰 object 自動當成查表內容。

針對序列讀取 `0x1A638+6*(2*channel+state)`，枚舉 channel 0–3 與 byte state 0–255，共 1,024 組：20 組完整位於 48-byte 專用窗口、872 組落在其他單一 DATA owner、72 組跨物件或無完整 owner、8 組碰到既有排除資料、52 組部分或全部位於 APP 外。分類先排除不可讀範圍，再檢查映像及 owner；未讀取資料值。20 組包含不同 channel/state 指向同一位址，並非 20 筆獨立表項，也不證明這些狀態可達或有效。

精確的位址界線可由公式直接推得；下表的 state 為 0–255，讀取長度均為 6 bytes，範圍端點皆包含。排除資料的交疊僅以位址計算，沒有讀取其內容。

| channel | 完整位於 48-byte 窗口 | 與排除的 4 bytes 交疊 | 部分或全部在 APP 外 |
| --- | --- | --- | --- |
| 0 | 0–7 | 16–17 | 246–255 |
| 1 | 0–5 | 14–15 | 244–255 |
| 2 | 0–3 | 12–13 | 242–255 |
| 3 | 0–1 | 10–11 | 240–255 |

這些只是 address ownership 的必要幾何條件，不代表超過 1 的 state 是有效表項：例如 `(channel,state)=(0,2)` 與 `(1,0)` 指向同一位置。也未證明任一排除或超界組合在實機可達。

在專案根目錄執行 `python experiments/tsl9-index-owner-enumeration/verify.py`。檢查器只讀取固定雜湊的既有 layout map，不讀取韌體 payload、不執行目標。此結果不建立全域索引界限，不解除六項未解析依賴，也不證明實機或 OTA 相容性。
