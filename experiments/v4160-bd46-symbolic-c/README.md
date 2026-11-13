# V4.1.60 `0xbd46`：符號化純 C 候選

離線、局部實驗，**不是**正式 source、data owner 或完整 firmware。`candidate.c` 宣告外部 `volatile unsigned char`，回傳其位址；沒有 inline asm 或 opaque 機制。section/used 是 Clang 擴充，C++17 使用 `extern "C"`。linker 的單一 `record_flag_bd46 = 0x2000bf11` 是 ABS data witness，不配置資料，也不宣稱 RAM 擁有者。

## 重播

在 repo 根目錄，使用 Python 3（本機 tool-index 的 Python 路徑亦可）：

```text
python -B experiments/v4160-bd46-symbolic-c/verify.py
python -B -O experiments/v4160-bd46-symbolic-c/verify.py
python -B experiments/v4160-bd46-symbolic-c/test_verify.py
python -B -O experiments/v4160-bd46-symbolic-c/test_verify.py
```

需要原 BIN `firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin`，以及 tool-index 指定的本機 NDK 27.1.12297006 `clang.exe`、`ld.lld.exe`；路徑固定於 `verify.py`，不下載、不安裝。另依賴既有 `experiments/tsl9-feature-dispatch-tree/elf_reader-v4.py`，讀取一次、校驗 SHA-256 後直接執行同一份 bytes，而非重新 import。Python 標準庫以外無套件依賴。

每次於全新系統 temporary directory 寫入同一份經 hash pin 的 source snapshot，C11/C++17 分別編譯 ET_REL，使用兩個獨立 linker script 連結 ET_EXEC；結束後 temp 及物件均刪除。腳本只在全部檢查成功後印出帶 `passed: true` 的 JSON，錯誤、工具缺失及工具非零退出均返回非零。測試包含合成 parsed records，以及完整有界合成 ELF32 bytes 的正例和 section/symbol 變異；後者驗證唯一 target 必須可從常規 SYMTAB 獨立解析，且額外 DYNSYM（包含重複 target）、RELR、REL 均拒絕。也用截斷資料測試 pinned reader、以真實缺失 executable 測頂層 CLI，並執行全新真實重播；這不是完整 ELF 格式測試。測試 runner 要求至少一項測試實際執行，`-O` 下不依賴 Python `assert`。

## 本次結果

正常及 `-O` 測試各 9 項通過；兩種 Python 模式的 replay 均為 4 cases、退出碼 0。驗證器輸出的 JSON 含編譯／連結 flags、工具版本及暫存物件的 hash。`PT_NULL` program header 並非省略 PT_LOAD 檢查。

- BIN 長度 `76800`、基址 `0x8000`、SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`；區間 `0xbd46..0xbd50` 為 `170500201305b51c8280`。
- Source snapshot SHA-256 `39d194961f6aba4d503a3fe122a9b312e372d5e45273a4871ccaaf425d29949f`；reader SHA-256 `2f7a5dc2d4eeb823e0e4c63f81b3c4fdcffe7cbb39262dc7f6731be675016b15`。
- C11 及 C++17：`0x2000bf11` 均得到 `170500201305b51c8280`；錯誤值 `0x2000cf11`（+`0x1000`）必須精確得到 `171500201305b51c8280`，其他錯誤 bytes 也拒絕。獨立計算使用 `P=0xbd46`、addend 0：錯誤值的 `S+A-P=0x200011cb`，round HI20 為 `0x20001`、signed LO12 為 `0x1cb`；按 `auipc a0`、`addi a0,a0` 與 `c.jr ra` 編碼分別為 `17150020`、`1305b51c`、`8280`。正例相同公式得 HI20 `0x20000`、LO12 `0x1cb`，並核對 BIN。
- 每個 ET_REL 檢查 leaf 範圍及 C linkage，PCREL_HI20 type 23 的 offset 0 指向唯一未定義 `record_flag_bd46`、addend 0；PCREL_LO12_I type 24 offset 4 的 addend 0 指向同 section、value 0 的 local anchor，該位置正是 HI20。reader 同時驗證 RELA 的 symtab link、section info、索引與資料邊界。
- 每個 ET_EXEC 檢查 entry 0、無 PT_LOAD、無未解析符號或殘餘 relocation；`.leaf` 為可執行 PROGBITS 且恰好 `0xbd46`/10 bytes，FUNC 為 GLOBAL、非 ABS、指向此 section 且尺寸精確，witness 為精確 ABS，並比較整段 bytes。PT_NULL 使此 ELF 不代表可載入的 target image。

兩種產物均要求且僅接受一個可解析的常規 SHT_SYMTAB，該表連結 SHT_STRTAB，目標符號必須唯一；明確禁止 SHT_REL、SHT_RELR、SHT_DYNSYM。這不是所有未知 ELF extension 的拒絕政策：其他 section type 並未通盤分類或驗證；reader 及此檢查只適用這次受控產物，不可用來證明任意 ELF 安全或沒有其他形式的 relocation。

工具檔 SHA-256 固定為 clang `047dfde05acc6fcce5af669e25cd8d40b4f509b8842d151d6d8a43a1c6a35fd6`、LLD `fe7f55c0c78b3d87f33b905a3874e10e872ca7beef53a8199d7ff9ac6641ec3f`。hash pin 不是供應鏈或可信時間認證，亦未固定 Python、OS、DLL 或工具其他依賴。假設本機檔案在讀取和執行期間未被並行替換；reader 是供此 bounded 本機產物使用的 parser，不是對抗惡意 ELF 的完整驗證器。記錄的 object/ELF hashes 是本次臨時產物的收據，產物未留存，並非外部認證。

沒有操作硬體、網路、執行或模擬 target。10 bytes 相同不能推論 runtime ABI、真實資料地址/owner、記憶體內容或完整 firmware 正確性。
