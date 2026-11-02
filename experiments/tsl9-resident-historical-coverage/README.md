# WCH 歷史參考檔覆蓋

WCH 官方 GitHub 對 `EVT/EXAM/BLE/LIB/wchble_rom.hex` 的公開歷史查詢，在每頁 30 筆的第一頁回傳四個提交；其中 2023-12-01 的 `ec059e0` 是既有 V1.31 參考，2024-02-26 的 `9596a13` 是另一版本。其餘兩份公開檔案經記錄語法、長度、checksum、重疊與 EOF 檢查，結果如下：

| 官方提交 | HEX SHA-256 | 有 V1.31 完整標記 | `0x6EB2C..0x6EB30` 有記錄的 bytes |
| --- | --- | ---: | ---: |
| [`64be955`](https://github.com/openwch/ch32v20x/blob/64be9554615df522899579633530fd234d685682/EVT/EXAM/BLE/LIB/wchble_rom.hex) | `42766be9b9aea7a819b61ee6bdb6c49c47838b2177947a460364888c4b621c57` | 0 | 0 |
| [`b79c6ac`](https://github.com/openwch/ch32v20x/blob/b79c6ac80df7b75753498c0742a1f0e4502a0b44/EVT/EXAM/BLE/LIB/wchble_rom.hex) | `e18c0a5cdfb8c1b46d2961fe2e28ffe81ec36d96f971f529e9fde5ee810c5f0b` | 0 | 0 |

兩份檔案均無該完整標記，也沒有同一數值位置的四 bytes；這不能排除其他版本或不同位址的等價內容，亦不能識別實機 resident。沒有用其他版本填補缺口。

`python experiments/tsl9-resident-historical-coverage/test_inspect.py` 執行一個合成正例及四個拒絕案例，不連網。`inspect.py` 從 stdin 讀取 GitHub contents API 的 base64 文字，僅輸出雜湊、計數與位置覆蓋，不輸出原始內容；重播上述真實檔案需要使用者提供公開檔案的對應 API 內容。沒有讀取或傳送裝置資料。
