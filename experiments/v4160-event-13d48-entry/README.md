# 0x13d48 入口與呼叫後重讀

`verify.py` 對原始 BIN `[0x13d48,0x13d68)` 使用有限 RV32I/C 解碼，從入口執行至第一個條件分支的兩個出口。將 `0x135e6` 替換成可正常返回、可改動合成半字的 stub；窮舉呼叫後 65,536 個值及兩個回傳值，共 131,072 組，檢查保存的返回位址、堆疊調整、呼叫目標、呼叫後重讀、暫存器與 `0xfffe` 分支。另檢查分支變造。

`model.c` 另提供 C 語意投影；`differential.py` 以 C11、C++17 各 131,072 個案例與原始指令解碼結果比對，再檢查六個 RV32 堆疊位址算術邊界，以及分支、位址兩個語意變造。部分邊界刻意使用未對齊的合成堆疊，只測數值環繞，不表示實際存取成功。

`paths.py` 接續第一個條件分支，以固定指令表解讀至 `0x13d8a`、`0x13da2` 或直接返回。524,288 個合成案例覆蓋兩個半字各為 sentinel／非 sentinel、兩個 byte 各 256 值及兩個回傳值；另有 262,144 個案例分別窮舉兩個半字的全部 65,536 值。測試檢查依路徑短路的讀取順序、返回位址和堆疊；15 個指令編碼變造均被拒絕。每次讀取的值作為獨立輸入，不假設同時取得快照。此固定表不是通用 RV32 解碼器。

`path_model.c` 提供分支的 C 語意投影，假定半字與 byte 輸入分別已限制為 16 位及 8 位；`path_differential.py` 的 C11、C++17 各 786,432 個案例與固定指令表逐軌跡比較，三種分支語意變造均被偵測。合成返回位址與堆疊僅檢查數值，不代表可在硬體上執行。

`tail.py` 以固定指令表執行 `0x13d88` 後的三條尾跳路徑：非零結果傳遞 100；零結果在假設 `0x81b0` 正常返回下，以 `T - [gp+344]` 的 32 位無號差比較 34，傳遞 35 或更新該欄位後跳至 `0x13346`。786,468 組合成軌跡涵蓋 34/35 與環繞邊界，23 個指令編碼變造均被拒絕。此處不執行外部函式，不推論數字的單位或實際效果；合成 `gp` 位址環繞也不代表真實有效記憶體。

`tail_model.c` 是尾跳行為的 C 語意投影；`tail_differential.py` 以 C11、C++17 各 786,468 組案例比對指令表軌跡，檢查跳躍目標、已確定的參數、讀寫與呼叫事件、還原的堆疊和返回位址；四個語意變造均被偵測。跳往 `0x13346` 時只有 a0 被視為已確定，其他參數不作聲稱。

重要邊界：此模型刻意令呼叫前後的半字不同，證明所檢查的指令**使用 stub 返回後的值**，並非認定真實 callee 一定會修改該欄位。未執行 `0x135e6`、後續分支、真實記憶體存取、競態或硬體，也不表示該路徑實際可達。

```text
python -I -B experiments/v4160-event-13d48-entry/verify.py
python -I -B experiments/v4160-event-13d48-entry/paths.py
python -I -B experiments/v4160-event-13d48-entry/tail.py
python -I -B experiments/v4160-event-13d48-entry/tail_differential.py --vcvars <vcvars64.bat>
python -I -B experiments/v4160-event-13d48-entry/path_differential.py --vcvars <vcvars64.bat>
python -I -B experiments/v4160-event-13d48-entry/differential.py --vcvars <vcvars64.bat>
```
