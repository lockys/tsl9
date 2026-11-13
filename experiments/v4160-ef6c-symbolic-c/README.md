# V4.1.60 `0xef6c`：符號式純 C getter 離線實驗

這是獨立實驗；**candidate 與測試只涵蓋這個 10-byte leaf**，不是正式 data owner、原始程式 ABI 證明、loader 規格或全 BIN 重建。`status_byte` 是人為 linker script ABS witness，不是實際 RAM 物件的擁有權或初始化證據；`int` 回傳與 C linkage 是實驗選擇，不證明原始宣告或呼叫 ABI。只做靜態編譯、連結及檢查，沒有執行、模擬或燒錄 target。

## 原始證據

`firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin`：76800 bytes、基址 `0x8000`、SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`。完整區間 `0xef6c..0xef76` 是 **`17d5ff1f 03450502 8280`**：

* `0xef6c`: `auipc a0, 0x1fffd`
* `0xef70`: `lbu a0, 32(a0)`
* `0xef74`: `c.jr ra`（ret）

計算 `(0xef6c + 0x1fffd000 + 0x20) mod 2^32 = 0x2000bf8c`。probe 先驗整個 BIN hash 和長度、完整 10 bytes、指令欄位及計算目標，才編譯。

## 重播

需 Python 3.7+、既有 NDK 27.1.12297006 clang/lld，及 repo 中 `experiments/tsl9-feature-dispatch-tree/elf_reader-v5.py`。從 repo 根目錄：

```sh
python -B experiments/v4160-ef6c-symbolic-c/probe.py
python -O -B experiments/v4160-ef6c-symbolic-c/probe.py
python -B experiments/v4160-ef6c-symbolic-c/test_probe.py
python -O -B experiments/v4160-ef6c-symbolic-c/test_probe.py
```

`probe.py --bin PATH --ndk-bin PATH` 可指定位置，內容仍須符合 pin。預設工具路徑為 Windows Android NDK。所有中間檔都在本實驗目錄下的臨時目錄，成功或例外後清理；輸出只寫 stdout。測試使用新建產物與定點突變，並以同一 Python 最佳化模式另跑完整 probe；不依賴歷史產物。直接執行 `test_probe.py` 的入口只要有 skipped 或執行零個測試即失敗；一般 unittest discovery／其他 runner 不套用此入口規則。另以子行程測試全跳過、部分跳過和零測試。測試以單次讀取的目前 `probe.py` bytes 編譯並執行，不讀取其 bytecode cache；隔離臨時目錄的負例建立有效舊 timestamp cache，再以同秒同長 source 變更兩次，確認一般載入會誤用舊 cache、測試入口則每次執行新 source。`-B` 避免一般 Python 載入寫入 bytecode；負例只在隔離臨時目錄明確建立 cache，不修改既有 `__pycache__`。

## 檢查範圍與結果

`leaf.c` 使用 `extern volatile unsigned char`，無內嵌組語或硬編碼地址；section/visibility 是 Clang 擴充。分別以 C11、C++17、RV32 `rv32imac_zicsr`/`ilp32`、`-Oz -mcmodel=medany -mno-relax -fno-pic` 編譯，LLD `--no-relax`。兩種語言均得到：

| 人工 ABS witness | 完整連結 bytes | 相等於 BIN |
|---|---|---|
| `0x2000bf8c` | `17d5ff1f034505028280` | 是 |
| `0x2000cf8c`（+`0x1000`） | `17e5ff1f034505028280` | 否，並精確比對此負例 |

實際新建的 C/C++ ET_REL 及兩地址 final 的 ELF `e_flags` 均為 `0x1`（RVC、soft-float ABI）；兩階段均精確檢查此值及 symbol 0 的完整 16 個零 bytes，並突變真實 ELF 測試。這是受控產物的檢查，並非原始韌體 ABI 的證明。ET_REL 檢查未重定位的 AUIPC、LBU、ret opcode 和暫存器、完整 leaf bytes/section、FUNC、唯一 undefined hidden data symbol、唯一 RELA section，以及 `PCREL_HI20` 對 data symbol、`PCREL_LO12_I` 對同 section 的 local anchor；含 offset、symbol index、addend，禁止多餘 relocation。final 檢查 `ET_EXEC`、無 PT_LOAD、leaf VMA/大小/flags/完整 bytes、FUNC 範圍、ABS witness、無 undefined 和 relocation section；其它非空 alloc section 不得與 leaf 的 VMA 或檔案 bytes 重疊（NOBITS 無檔案 bytes），且 VMA 不得溢出。刻意用 PT_NULL，不是可載入映像。測試含真實 ELF 的 ABI、null symbol、指令欄位和 overlap 原始突變，以及錯誤 data symbol、addend、relocation type/offset/symbol/anchor、section、目標、bytes、PT_LOAD、undefined、BIN pin、空資料及編譯/連結失敗；以顯式例外而非 Python `assert` fail closed。

執行前固定比對 SHA-256：clang `047dfde05acc6fcce5af669e25cd8d40b4f509b8842d151d6d8a43a1c6a35fd6`、lld `fe7f55c0c78b3d87f33b905a3874e10e872ca7beef53a8199d7ff9ac6641ec3f`、ELF reader `a56503572e8b65308ae1c8978ba5a6d44d0a20cd969315dc1b12103b59a9b43a`、source `4e50f5efd36b2e52597c74c6e2058732d5b0c8bff2e8dbd107be027af004457f`；reader 執行的是已驗 hash 的 bytes 快照。pin 是本機一致性檢查，非工具來源認證；Python、作業系統、工具依賴與檔案系統受信任。整次執行假設 compiler、linker、BIN、reader、原始與臨時 source、中間 object、linker script、final ELF 等均不被並行修改或替換；hash 或讀取快照並不能消除其餘路徑的 TOCTOU 風險。臨時目錄只用於整理與清理，**不是安全 sandbox**。reader 是受限本地檢查器，不是對抗性 ELF 安全解析器。
