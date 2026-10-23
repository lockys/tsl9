# 功能分派的完整邊界

[English](readme.en.md)

原廠 `14D2E–154A6` 是1912B／666指令的候選完整分派函式。第一個也是唯一RET在`14DA8`，後面仍有可達的分派區塊；舊36B入口片段不是整個函式。

- `1A6B8`主表有7個signed-relative目的地；mode>6走default。
- `1A6D4`第二表有8個entry，以`(byte[S0+5]>>2)&7`選擇；兩個JR都不寫RA。
- 21個直接呼叫點、59個直接尾跳，合計71個不同外部目標。
- 725條含重複table-entry的內部邊，去重後723條。全部666個指令起點可由「正常call回傳、兩個條件結果皆保留」的靜態過度近似涵蓋；不代表每條路徑實際可達。
- 所有尾跳依S0→RA→SP順序恢復；共用RET則RA→S0→SP。opaque呼叫後不假設普通callee-saved ABI。

[summary.json](summary.json)列出原始位元組／資料表雜湊、每個call/tail及restore位置。所有解碼位元組都與本機原始BIN核對；腳本只處理資料，沒有執行指令。

「2250B整合元件剩兩個直接提供者」只描述該元件的目前邊界。展開`12ABE`後有兩個不同backend，展開`14D2E`又有上述71個目標；不能把兩個UND當作整個韌體只剩兩個未知函式。完整C重建、原機身份、installed ROM、啟動／記憶體／IRQ及OTA仍未證。

從專案根目錄唯讀復核：

```sh
python3 scripts/analyze-feature-dispatch.py --replay analysis/feature-dispatch-frontier-2026-10-23/summary.json
```

需已安裝雜湊相同的radare2及原始BIN；使用`--r2`指定工具，不會下載或安裝。
