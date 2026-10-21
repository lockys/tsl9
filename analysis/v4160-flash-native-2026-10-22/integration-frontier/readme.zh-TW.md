# Flash 完整映像整合的下一步

[English](readme.en.md)

這份報告讀取前一里程碑實際產生的 `source-integrated.o`，逐筆檢查全部 8,276 筆 RELA；不執行 RV32。六個 Flash 函式的原始載體仍有 262 bytes，與原廠 V4.1.60 的指定範圍完全一致。

在這個物件的已記錄重定位中，12 筆範圍外引用都進入六個函式的起點；其中八筆進入 quarter wrapper，四筆由 `0x197BE` 的呼叫端進入 helper。六個函式內另有五筆 helper 呼叫，以及六筆輪詢／迴圈分支。未來整合必須明確取代這 11 筆，並保留其餘 8,265 筆的完整角色與次數；本輪尚未建立新整合物件。

program 重建為 94 bytes，原區段是 100 bytes。因此 `0x18F50..0x18F55` 的六個 bytes 仍未建立新的儲存來源。本報告不填入 NOP、不借用鄰段，也不把「已記錄 RELA 沒有外部 interior target」擴大成原機 ROM、間接數值引用與執行期沒有其他進入點的證明。

`report.json` 保留確切物件 SHA-256、23 筆相關 RELA 及五個語義反例。若要重新讀取實際物件，需明確提供該雜湊的歷史編譯產物：

```sh
python analysis/v4160-flash-native-2026-10-22/integration-frontier/inspect_frontier.py --project-root . --merged-object /absolute/path/to/source-integrated.o --check
```

發佈文件封存報告與成員雜湊；未把歷史 build 目錄當成可攜輸入。只核對 seal 不能宣稱已在目的地重新讀取實際物件。原硬體、Flash 容量、非同步狀態與藍牙 OTA 相容性仍未知；此輪沒有新 BIN。
