# V4.1.60 `0xbd50`：符號化純 C 候選

這是離線、局部實驗，不是正式 source 或完整 firmware。`candidate.c` 以 C 回傳外部 `volatile unsigned char` 的位址，沒有 asm；`section`/`used` 是 Clang 擴充，C++17 加 `extern "C"`。linker script 僅以 `record_flag_bd50 = 0x2000bf10` 提供獨立 ABS data witness，沒有配置資料，也不宣稱 RAM owner。

## 自行靜態觀察

完整讀取原 BIN：`firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin`，長度 76800、載入基址假設 `0x8000`、SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`。offset `0xbd50 - 0x8000 = 0x3d50` 開始的 10 bytes 是 `170500201305051c8280`，以 little-endian 解出：

- `0x20000517`：`auipc a0,0x20000`，以 `0xbd50` 為 PC。
- `0x1c050513`：`addi a0,a0,0x1c0`。
- `8280`：`c.jr ra`。

故靜態數值為 `0xbd50 + 0x20000000 + 0x1c0 = 0x2000bf10`；這是基於指令與載入基址的推導，不是實機 RAM owner 證明。驗證器另解碼完整 pinned BIN window，確認指令形狀和目標，再把連結的正例直接逐 byte 比較該 window。

負例獨立按 RISC-V PC-relative relocation 算：`P=0xbd50`、`S=0x2000cf10`（正確值 +`0x1000`）、`A=0`，`S+A-P=0x200011c0`，round HI20=`0x20001`，signed LO12=`0x1c0`。分別編碼 `auipc a0`、`addi a0,a0`、`c.jr ra` 得 `17150020 1305051c 8280`，故精確 10 bytes 為 `171500201305051c8280`。正例的 delta 是 `0x200001c0`，HI20=`0x20000`、LO12=`0x1c0`。負例要求精確這 10 bytes，不能只檢查不等於正例。

## 重播及本次驗證

在 repo 根目錄，以本機 Python 3 執行：

```text
python -B experiments/v4160-bd50-symbolic-c/verify.py
python -B -O experiments/v4160-bd50-symbolic-c/verify.py
python -B experiments/v4160-bd50-symbolic-c/test_verify.py
python -B -O experiments/v4160-bd50-symbolic-c/test_verify.py
```

本次上述四個命令均退出 0；正常和 `-O` 各 13 個測試通過，兩種 replay 的 C11/C++17 × 正例/負例共 4 cases 均通過。每次在全新 temporary directory 寫入 hash pin 的同一 source snapshot，使用 tool-index 指定原路徑 Clang/LLD 18.0.2 離線編譯與連結，不保留暫存產物。編譯使用 `--target=riscv32-unknown-elf -march=rv32imac_zicsr -mabi=ilp32 -mcmodel=medany -mno-relax -fno-pic -ffreestanding -Oz`；完整 flags、版本、產物 hash 與 linker script 見 JSON 輸出。兩種 Python 模式均只在所有檢查及完整 case matrix 成功後輸出 `passed: true`，錯誤則非零退出。

- 每個 ET_REL：檢查 `.leaf` 的可執行 PROGBITS shape 和 10-byte FUNC，唯一未定義 data 符號；HI20 type 23 在 offset 0 指向該符號、addend 0；LO12_I type 24 在 offset 4、addend 0 指向同 section value 0 的 local anchor，即 HI20 位置。
- 每個 ET_EXEC：entry 0、無 PT_LOAD、無未解析符號或殘餘 relocation；`.leaf` 精確 `0xbd50`/10 bytes；GLOBAL FUNC 非 ABS 且屬於 `.leaf`，data witness 為精確 ABS。`PT_NULL` 並非省略 no-PT_LOAD 檢查，亦不產生可載入映像。
- Pinned reader 檢查 ELF32/RISC-V、headers、section、symbol、RELA 及索引邊界；每個產物只接受一個可解析的常規 SHT_SYMTAB，禁止 SHT_REL、SHT_DYNSYM、SHT_RELR。這不是未知 ELF extensions 的全面分類，parser 僅用於受控產物，不是惡意 ELF 安全驗證。
- 測試包含合成 records 和完整 ELF32 bytes，後者實際經 parser 測 FUNC ABS、PT_LOAD、ELF bounds、未解析符號、錯誤 relocation、anchor、addend、重複符號與不支援 sections；另測完整 BIN 的截斷、附加與窗口外單 byte 篡改、pin 失敗、缺失 executable、命令失敗、錯誤 bytes 和不完整/重複 matrix。測試內也做一次真正全新 replay；不依賴 Python `assert`。

## 依賴及限制

本驗證器與測試由已提交的 bd46 snapshot `1472c432f415fb0e3b56877e763e652f7a5857bd` 改寫，原 `verify.py` SHA-256 `7ac1fbac0030863ce2114789816528eb33d8bc2b2c9f42a0273618b5fb3f6f88`、`test_verify.py` `01995ada33f66e3f5355edfcc451aba9220673407bd877856dbf4fa70a44da85`；不是在執行時 import 或錯用 bd46 的硬編地址/名稱檢查器。原檔未修改。本實驗的 candidate SHA-256 `9cb990b4e9a7a7c12abd604db978058c49ec8ed27348f9018ad3469f8e7fde23`。共用 `experiments/tsl9-feature-dispatch-tree/elf_reader-v4.py` 讀取一次、SHA-256 校驗 `2f7a5dc2d4eeb823e0e4c63f81b3c4fdcffe7cbb39262dc7f6731be675016b15`，執行同一份已驗 bytes，沒有第二次 import。

Clang SHA-256 `047dfde05acc6fcce5af669e25cd8d40b4f509b8842d151d6d8a43a1c6a35fd6`，LLD `fe7f55c0c78b3d87f33b905a3874e10e872ca7beef53a8199d7ff9ac6641ec3f`，執行前完整讀取比對；沒有下載或安裝。hash pin 不是供應鏈認證，亦未固定 Python、OS、DLL 或其他依賴；假設檔案不被並行替換。產物 hash 只是當次暫存收據。

未燒錄、執行或模擬 target，未接觸網路或硬體。10 bytes 相同不能證明實際 data owner、記憶體內容、runtime ABI 或原機 firmware 行為。
