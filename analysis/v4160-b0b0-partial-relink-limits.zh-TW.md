# V4.1.60 `0xb0b0`：部分連結的失敗紀錄

## 隔離實驗

預定在暫存目錄分別以 C11 和 C++17 profile 編譯完整 `record_helpers` unit、移除唯一 `0xb0b0` 定義的 unit 及同名純 C leaf；leaf 單獨增加 `-mcmodel=medany -fno-pic -ffixed-x11 -ffixed-x12 -ffixed-x13 -ffixed-x14`。使用固定 Clang 18.0.2 離線編譯，再分別以固定 LLD 18.0.2 的 `-r --no-relax` 處理完整 unit、拆分 unit 加 leaf、以及單獨的 leaf。實際僅執行至 C11 比對失敗；這不是正式 build，不執行產生的目標程式。

本機驗證器位於 `experiments/v4160-b0b0-partial-relink/`，依賴尚未提交的 `experiments/v4160-b0b0-record-unit-split/verify.py`；兩者**未包含在本次提交**。摘要所記錄的暫存 object 均已清除，因此本紀錄不是自包含或可獨立查驗的驗證套件。

## 實際結果

本機合成測試在 Python 一般和 `-O` 模式各 20 項通過；這不保證真實 linker 輸出會通過。實際 C11 replay 在比較保留 facts 時拒絕：

```text
FAIL: retained function/allocated-section/relocation/symbol facts differ
```

另一次診斷的 C11 完整 unit baseline 與 split + leaf combined 物件，顯示保留函式 67 個、allocated sections 68 個、RELA 73 筆、relocation symbol facts 73 筆及 globals 85 個均在指定投影下相同；locals 的數量分別為 79 和 80。combined 多出一筆 `('mapping', 'd', '.comment', 0, 0, 0)`。這是受限靜態檢查的診斷，不證全部 ELF metadata、符號來源或語義一致。程式在 C11 比對處停止，**未進入本次 C++ replay 和最後的 leaf 原址連結階段**。

先前 partial link 的診斷還觀察到 LLD 將部分未引用 `$d.N` mapping symbols 表示成 `SHN_ABS`、value 0；一組 leaf 的 `.riscv.attributes` bytes 在 link 前後相同。比較器僅對特定 shape、未引用的 mapping labels 作受限多重集合對照；數量一致不證個別符號來源。當 `.comment` 多出一筆時沒有忽略該差異，保持 fail-closed。

## 邊界

本實驗不證跨單元 caller、實際 placement、private ABI、動態可達性、硬體或完整 BIN 等價。額外 leaf 編譯旗標不是正式 unit 的 profile。linker 的 `destination` 符號、LO12_S 正式 guard 及其他整合條件仍需核對；編譯器及 linker 的 hash 不證依賴可信，也不能消除 TOCTOU。
