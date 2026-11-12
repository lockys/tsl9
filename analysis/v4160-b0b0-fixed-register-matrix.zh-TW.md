# `0xb0b0`：四個保留暫存器的 16 組原址比較

以 `experiments/v4160-b0b0-symbolic-c/leaf.c` 純 C 候選，在隔離暫存目錄離線編譯及連結：以 bit 0、1、2、3 分別表示 Clang 選項 `-ffixed-x11`、`-ffixed-x12`、`-ffixed-x13`、`-ffixed-x14`，窮舉 mask 0–15。未執行目標 ELF、未模擬、未修改正式來源或 BIN。

共同設定為 NDK Clang 18.0.2 的 `--target=riscv32-unknown-elf -march=rv32imac_zicsr -mabi=ilp32 -mno-relax -mcmodel=medany -fno-pic -ffreestanding -fno-stack-protector -Oz -std=c11`，連結用 LLD 18.0.2 `--no-relax --section-start=.text=0xb0b0 --defsym=destination=0x2000beeb -e candidate`。目的地址由 link-time 外部符號指定，是實驗定位而不是正式整合證據。執行前確認 Clang SHA-256 `047dfde05acc6fcce5af669e25cd8d40b4f509b8842d151d6d8a43a1c6a35fd6`、LLD SHA-256 `fe7f55c0c78b3d87f33b905a3874e10e872ca7beef53a8199d7ff9ac6641ec3f`、來源 SHA-256 `290336e8361500a563b725efed97714de0b293587fb79a3a2a762f2cc214d1ba`；參考 BIN 固定長度 76800 與 SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`。hash 檢查不防止執行前後的同機檔案替換或證明工具鏈依賴可信。

十進位 mask 與 linked executable section 的比較結果如下；每組皆為 10 bytes：

| mask | linked bytes | 結果 |
|---|---|---|
| 0、2、4、6、8、10、12、14 | `97150020a38da5e28280` | 不同 |
| 1、5、9、13 | `17160020a30da6e28280` | 不同 |
| 3、11 | `97160020a38da6e28280` | 不同 |
| 7 | `17170020a30da7e28280` | 不同 |
| 15 | `97170020a38da7e28280` | 相同 |

參考 BIN `[0xb0b0,0xb0ba)` 為 `97170020a38da7e28280`。本機唯讀 checker 在範圍、ELF32 RISC-V ET_EXEC、`e_flags`、entry 及可執行 PT_LOAD 檢查後再次執行 16 組矩陣，回報 `PASS: only mask 15 matches the 10-byte reference window`。故**在此有限的四旗標子集與固定工具鏈中**，只有同時保留四個暫存器的組合匹配；這不排除其他編譯旗標、C 表達方式或編譯器能匹配。

checker 本機目錄 `experiments/v4160-b0b0-fixed-register-matrix/` **尚未提交**，本文件本身不能讓讀者從 GitHub 重播其程式。其 Python 合成測試在正常及 `-O` 模式各執行 7 項、通過 6 項、跳過 1 項；symlink 負例因 Windows 權限不足（WinError 1314）跳過，不應宣稱該測試通過。測試中的 timeout 與相對工具路徑錯誤訊息是預期負例。獨立審查發現的主流程測試、ABI flags、虛擬／實體映射與重疊載入問題已修正並複審。

這是單一 leaf 的原址 bytes 證據，不是完整純 C 韌體或 full BIN 比對；特殊保留暫存器旗標、外部符號定義、正式 owner、caller 的 private ABI 和實際硬體行為仍須整合驗證。任何未測過的組合不可推論為失敗或成功。
