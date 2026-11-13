# V4.1.60 F030 → BD46：真實 provider 選區連結

## 問題與輸入

在不以人工 ABS 定義取代 provider 的前提下，測試重建的 F030 直接邊能否連到重建的 BD46。這是離線、選區實驗，不是整機建置或純 C 替換。

參考 `firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin` 為 76,800 bytes，SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`；假設映像 base 為 `0x8000`。以完整 `src/native/receive/record_helpers.c` 編譯 caller，以完整 `src/native/receive/record_continuations.c` 編譯 provider。兩個來源仍含 inline assembly，不是純 C。

依 `src/source-build-manifest.json` 的 `queue-consumer-a0-a5` profile，分別以 Windows NDK Clang 18.0.2 編譯 C11 與 C++17。實驗另加 `--no-default-config -nostdinc -isystem <temporary include> -H`，不是宣稱這些旗標屬於原 manifest profile。兩物件交給 LLD，以 F030 作 GC root、固定 `.caller` 在 `0xf030`、`.provider` 在 `0xbd46`，並使用 `--gc-sections --no-relax --discard-all`。未使用 `--defsym` 或人工 ABS provider；其他未選中的 sections 可以被 GC 丟棄。

## 局部結果

| 選中區段 | 參考／連結 bytes | 長度 |
|---|---|---:|
| F030 caller | `23059400efc03fd1` | 8 |
| BD46 provider | `170500201305b51c8280` | 10 |

兩語言的所選 18 bytes 均與參考窗口一致。caller ET_REL 在 F030+4 的 `R_RISCV_JAL` 指向 undefined BD46；provider ET_REL 的 BD46 為所編譯 provider section 中的 GLOBAL FUNC 定義。最終 JAL 解碼指向 `0xbd46`，provider 的位址形成結果為 `0x2000bf11`。從 caller object 省略 provider 的嚴格連結非零退出並診斷該 undefined。final ELF 無 PT_LOAD，不是可載入韌體。

檢查僅對兩個 alloc sections 的 type、flags、address、size 做精確比較，另外限制 final section 名稱 inventory、動態及 relocation sections，並拒絕具名 undefined 與非 FILE ABS；未命名 undefined 未列入這項拒絕範圍。實際 ET_REL relocation、final symtab、final `.comment` 的 `SHT_DYNAMIC` type、BIN byte 和錯誤 placement 均有負例；FILE ABS 是明示允許的正例。這些測試不代表所有可能的 ELF 變異均被涵蓋。

## 重播範圍與未閉合項

本機 `experiments/v4160-f030-bd46-real-provider-release/{verify.py,test_verify.py,README.md}` 尚未隨本報告發布。使用 GitHub `main` commit `14cd3e4bc1042d19b70b56b4f309f5dfc9e8d70c` 所取得並核對 Git blob 與 SHA-256 的六項輸入，搭配本機上述三個實驗檔，於臨時目錄執行 `test_verify.py`，normal 和 Python `-O` 各 7 tests 通過。其後修正相對工具路徑並增加測試，本機目前版本在兩模式各 8 tests 通過；新的版本尚未以遠端輸入子集重新測試。測試確實重新編譯及連結，但這不是由本報告單獨可重播的公開鏈；工具 executable/header pin、測試程式和其他限制記錄於尚未發布的本機實驗。

此結果只涉及 linker GC 留下的子圖，不證明其他 sections、完整 CFG、資料 owner、原始 private ABI、caller register/stack 語意或硬體行為。也不證明 formal owner 能被標準 C 取代，更不是完整 76,800-byte BIN 逐 byte 驗收。未執行、模擬或燒錄 target。
