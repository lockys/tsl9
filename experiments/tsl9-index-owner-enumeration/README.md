# 資料索引與來源物件的離線枚舉

[English](readme.en.md)

針對 `0x1AB48+2*index` 枚舉 byte 索引 0–255，以目前原位址布局的 DATA owner 判斷每次兩 byte 讀取是否完整位於單一物件。76 個索引符合此**位址**條件，但只有 0–3 屬於專用計數器窗口；4–7 對應另一個 record dispatch 資料物件，8–11 對應 service threshold 資料，12–75 對應 reset initializer。這些相鄰物件可佔用同一數值區域，並不證明它們是查表的有效資料或索引可達。

針對 `0x1A078+16*mode+column`，枚舉 256 列、每列 16 bytes：149 列完整落在單一 DATA owner；另外 107 列跨物件、未涵蓋或不在映像中。此前統計的 164 列是所有 bytes 均落於某個 DATA owner，包含跨多個 owner 的列；兩個數字的判準不同，均不代表表格語意有效。

在專案根目錄執行 `python experiments/tsl9-index-owner-enumeration/verify.py`。檢查器只讀取固定雜湊的既有 layout map，不讀取韌體 payload、不執行目標。此結果不建立全域索引界限，不解除六項未解析依賴，也不證明實機或 OTA 相容性。
