# `0xb0b0` return-value 候選的 RV32 原址差異

經使用者同意，離線編譯 `experiments/v4160-b0b0-return-value-candidate/leaf.c`，在新建的系統暫存目錄產生 object、link map 及 executable ELF；沒有執行或模擬目標程式，也沒有產生可刷寫映像。原始程式仍是隔離候選，未改正式來源。

本機 Android NDK Clang 18.0.2 的 SHA-256 為 `047dfde05acc6fcce5af669e25cd8d40b4f509b8842d151d6d8a43a1c6a35fd6`；LLD 18.0.2 的 SHA-256 為 `fe7f55c0c78b3d87f33b905a3874e10e872ca7beef53a8199d7ff9ac6641ec3f`，均符合既存紀錄，但這不證明整個工具鏈及依賴的可信性。編譯參數為 `--target=riscv32-unknown-elf -march=rv32imac_zicsr -mabi=ilp32 -mno-relax -fpic -ffreestanding -fno-stack-protector -Oz -std=c11 -c`；以 `ld.lld --no-relax --section-start=.text=0xb0b0 -e v4160_b0b0_return_value` 連結。這是一組工具及旗標的觀測，不代表所有純 C 寫法或工具鏈都無法匹配。

object SHA-256 `f89d0eaf4cfaaa1dfa7abf811b26188d62098305c3f2d5454997e910644485ae`，ELF SHA-256 `acd7229c96576eb5ab86fbcf516396654152a8a3553dd196955f71cdc346f399`；暫存產物未加入 Git。以 `rabin2 -s` 觀察 ELF symbol `v4160_b0b0_return_value` 位於 `0xb0b0`、長 10 bytes。`rabin2 -R` 對 object 與 executable 均未列出 relocation；這只是該工具的觀察結果。以固定 SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667` 的 76800-byte 參考 BIN 及 ELF .text 比對：

| 項目 | 10 bytes | 靜態解讀 |
|---|---|---|
| 參考 `[0xb0b0,0xb0ba)` | `97170020a38da7e28280` | `auipc a5,0x20001; sb a0,-453(a5); ret` |
| 本次 linked `.text` | `b7c50020a385a5ee8280` | `lui a1,0x2000c; sb a0,-277(a1); ret` |

**兩者不同，未通過原址 bytes 比對。** 在 PC `0xb0b0` 的靜態算術下，兩者 store 的目標皆為 `0x2000beeb`，且都以 `a0` 為 store 來源並以 `c.ret` 返回；中間覆寫的暫存器分別是 `a5` 和 `a1`。這些局部指令事實不證明 private ABI、所有 caller、可達性、記憶體存取成功或硬體效果等價；不應直接替換正式來源或修補 BIN。原始 AUIPC 結果依其 PC 位置計算，不能任意搬址。

另建立本機 `experiments/v4160-b0b0-rv32-direct/` 唯讀檢查器和合成負例；**此目錄尚未提交**，不能只靠 GitHub 重現。檢查器對上述 ELF 回報 `MISMATCH`、退出碼 1；Python normal 和 `-O` 各 7 項測試通過。獨立審查指出的重疊 PT_LOAD、RVC flags、window guard 負例與 PT_LOAD 對齊問題已修正並複審；這不證明 ELF parser 可安全處理所有敵意輸入，也不建立來源與 ELF 的來源鏈。
