# `0xb0b0` 純 C 候選：目標機器碼觀察

`target_codegen.py` 驗證原 BIN 與 `leaf.c` 的 SHA-256，以指定 Clang 編譯 RV32IMAC/ILP32 的 C11 與 C++17，檢查 `-O2`、`-Oz` 輸出。從 ELF 提取唯一函式，要求無 relocation，以小型指令欄位解碼器分別檢查原始與編譯結果的 base、`sb` 操作數及 `c.jr ra`。

在本機 Android NDK 27.1.12297006 Clang 的四個組態中：原始與候選都是 10 bytes，均將 a0 低 byte 寫至 `0x2000beeb`，但 **bytes 不同**。原始 `auipc` 改寫 a5；候選 `lui` 改寫 a1。兩者都不直接寫 a0，因此這四份實際輸出保留 a0；這不是 `void` C 介面的通用承諾。不同 scratch register 也意味著不能僅因記憶體結果相同，就認定直接替換對所有 caller 安全。

執行：`python -I -B experiments/v4160-b0b0-pure-c-candidate/target_codegen.py --tool-dir <LLVM_BIN>`。測試刻意固定這次觀察到的形式；其他編譯器或版本產生其他正確實作時，會報錯而不是自動宣稱錯誤或等價。

這是對物件位元組的有限解碼，不執行機器碼、不證明載入位址映射、例外、中斷、完整 ABI 或實機行為；不是 byte-exact 替代或新增覆蓋。
