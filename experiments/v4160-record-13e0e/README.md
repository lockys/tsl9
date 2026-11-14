# 0x13e0e 紀錄更新路徑

`verify.py` 對 SHA-256 固定的原始 BIN 使用有限 RV32I/C 解碼器，從 `0x13e0e` 執行到返回，僅涵蓋呼叫者傳入 `a1=1` 的路徑。在合成、成功的記憶體讀寫下，枚舉 65,536 個半字值，各測第一筆相符、第二筆相符、兩筆均相符、不相符及 32 位元 handle 高位非零，共 327,680 組；另檢查條件分支變造。

比較先讀 `0x2000c796` 的半字；相符則依序寫 `0x2000c798=1`、`0x2000c799=0`，不再讀第二筆。否則讀 `0x2000c79a`，相符則依序寫 `0x2000c79c=1`、`0x2000c79d=0`；都不符則不寫。兩筆都相符時第一筆優先。比較使用完整 32 位元 handle 與零延伸半字。

`model.c` 另以 C11/C++17 投影讀取與有序寫入事件；`differential.py` 各以 40,980 組資料與上述原始指令解碼器比較。另於每次比較檢查模擬返回時 `ra`、`sp`、`a0`、`a1` 與 callee-saved 暫存器未變；此 C 模型不執行實體記憶體操作。DLL 在獨立子程序中載入，子程序結束後再清除暫存編譯檔。測試另於暫存目錄編譯三種 C 語意變造（狀態值、sentinel、寫入寬度），確認均因預期的差分不符而被拒絕；不修改正式模型。`other_modes.py` 測試 `a1=2` 與 `a1=0、3、0xffffffff` 的合成路徑，共 1,245,184 組。`a1=2` 優先選第一個值為 `0xfffe` 的半字欄位，將 handle 低 16 位寫入，再依序清除相鄰兩個狀態 byte；沒有空項則不寫。測試的其他三種值依序比較兩個完整 handle，命中時寫入半字 `0xfffe` 並清除兩個狀態 byte。上述 sentinel 名稱僅描述程式條件，不代表已知其設備語意。新增的 `record_update_other` C 投影限定 `a1 != 1`，C11/C++17 各以 155,724 組案例與原始 bytes 解碼器比較，包含寫入順序、位址、寬度與數值；仍未窮舉所有 32-bit 參數。

`composition.py` 將四位元組比對與 `a1=1` 紀錄更新的兩個解碼投影條件式串接，涵蓋 6,000 組長度不符、比對失敗、第一筆／第二筆相符及無相符案例。呼叫邊界的狀態由測試重建，不是連續 CPU 執行；不執行 callback 或其他 provider。

解碼器與預期結果均為自製；測試不涵蓋所有其他 `a1` 值、存取例外、競態、別名、呼叫前狀態可達性或實機執行。

```text
python -I -B experiments/v4160-record-13e0e/verify.py
python -B experiments/v4160-record-13e0e/other_modes.py
python -B experiments/v4160-record-13e0e/composition.py
python -B experiments/v4160-record-13e0e/differential.py --vcvars <vcvars64.bat>
```
