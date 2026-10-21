# 9DF4 入口呼叫更正

[English](readme.en.md)

**`0x9DF4` 的原始 bytes `69 3B` 是 RV32 `C.JAL`，寫入 `RA=0x9DF6`，目標是 `0x9B8E`。它不是無連結尾端跳轉。** 半字 `0x3B69` 的 quadrant=1、funct3=1，位移為−614。重定位 type45（`R_RISCV_RVC_JUMP`）名稱不能單獨決定指令是否寫入 RA；funct3=5 的 `C.J` 才是相同格式的無連結形式。

本補充**僅取代**舊 `source-review/contracts.json` 的 `/recorded_RELA/external_incoming_role`，以及該目錄 README、繁中與英文文件中將 **9DF4** 稱作「W/R 共用的實體尾端路徑／shared physical W/R tail edge」的敘述。精確舊檔案雜湊、原句及更正內容見 [correction.json](correction.json)。所有舊封存檔保留原樣。`0x9BF8` 透過 T1 的無連結釋放尾端跳轉仍然正確，並未被這次更正取代。

已實際讀取 SHA256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667` 的原始韌體，以及既有 C/C++ 邊界探針的 `carrier.o`、`partial.o`。兩種語言的原始與合併物件皆保留同一個 `693b`；呼叫端 section 的 offset426、type45、local entry offset0 也符合紀錄。這些是兩物件邊界證據，不能當成完整映像已連結或硬體可燒錄的證明。

`check.py` 直接拆解指令欄位，沒有執行或模擬 CPU。它拒絕改成同目標 `C.J`、改變目標、錯誤指令寬度等3個原始指令變異；每種語言另拒絕3個實際 ELF bytes 變異（呼叫改成無連結、重定位型別改變、local entry 偏移改變）。

```sh
python -B check.py
python -B check.py --project-root ROOT --firmware ORIGINAL_FW --report NEW_RAW_REPORT.json
python -B check.py --project-root ROOT --firmware ORIGINAL_FW --folder ACTUAL_BOUNDARY_FOLDER --report NEW_BOUNDARY_REPORT.json
```

預設及 `check.sh` 無參數模式只驗證補充封存的來源／中繼資料，**不讀取韌體或建置物件**。明確提供 `--firmware` 才重讀原始韌體，`--folder` 還會重讀實際邊界物件；報告必須是新路徑。唯讀 parser 支援工作區 `apk-analysis/` 與發布版 `analysis/` 路徑。封存不包含 `.o`、`.elf` 或產生的 build 目錄。本補充未編譯、執行目標、使用模擬器、連網或操作硬體。
