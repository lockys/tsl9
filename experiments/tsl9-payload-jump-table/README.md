# 0x14056 分派器的五項相對跳轉表

[English](readme.en.md)

現已定位先前僅列為候選的資料表 consumer：`0x144C2..0x144C6` 在命令 `0xD0` 時分支至 `0x14512`；該處讀取 `s0` 指向的首 byte，對大於 4 的索引直接離開。索引 0–4 經 `0x1451C..0x1452C` 用 `0x1A6A4` 為基址，讀取五個 32-bit 相對位移後間接跳轉。

五個目的地依序為 `0x1452E`、`0x1453E`、`0x1454A`、`0x1473E`、`0x14748`，均是該原始區段的解碼指令起點。原先以 `0x1A6A0` 解讀的候選結果並非實際 consumer 基址；前面的 word 不屬於此五項表。此結論依正常控制流、`s0` 指標有效、記憶體未改寫及指令集解碼假設成立，不代表五個索引在實機都可達，也不推斷產品功能。

執行 `python scripts/verify-payload-jump-table.py --tool-dir <LLVM_BIN> --out <NEW_OUTPUT_DIR>`。C／C++ 皆核對 12 條關鍵指令、表的實際 section backing、五個目的地與 256 種 byte 的界限算術，並包含表格變更反向測試。沒有執行韌體；原機 ROM／RAM／OTA 相容性未證。
