# BD50 純 C 候選的離線原址檢查

`experiments/v4160-bd50-symbolic-c/candidate.c` 回傳外部 byte 符號的位址，沒有 inline assembly；section/used 為 Clang 擴充。它是隔離候選，不是已整合的正式 provider。連結時的 `record_flag_bd50=0x2000bf10` 是人工 ABS 資料 witness，未配置 RAM，也未證明資料 owner。

在參考 BIN 長度 76800、base `0x8000`、SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667` 的前提下，`0xbd50` 的 10 bytes 為 `170500201305051c8280`；局部解碼為 `auipc a0,0x20000; addi a0,a0,0x1c0; c.jr ra`，算得 `0x2000bf10`。

本機離線實測 C11、C++17 各自原址編譯並以上述資料 witness 連結，兩者 10 bytes 均與 BIN 一致。將 witness 錯置為 `0x2000cf10` 的兩個負例均得到依重定位獨立推導的 `171500201305051c8280`，與參考不同。normal 和 Python `-O` 各 **13 項測試通過**；兩模式的 C11/C++17 正負例四案例均通過。ET_REL 檢查 HI20／LO12_I 及 anchor；final ELF 中目標是非 ABS GLOBAL FUNC、無 PT_LOAD，並檢查選定 section、資料 witness、符號及 bytes。這是受控產物的有限檢查，不是通用 ELF 認證。

本機工具為 NDK Clang／LLD 18.0.2，SHA-256 分別為 `047dfde05acc6fcce5af669e25cd8d40b4f509b8842d151d6d8a43a1c6a35fd6`、`fe7f55c0c78b3d87f33b905a3874e10e872ca7beef53a8199d7ff9ac6641ec3f`。主要編譯條件為 `--target=riscv32-unknown-elf -march=rv32imac_zicsr -mabi=ilp32 -mcmodel=medany -mno-relax -fno-pic -ffreestanding -Oz`；連結使用 `--no-relax` 和原址 linker script。

本輪僅提交候選及本紀錄；實測使用的 `experiments/v4160-bd50-symbolic-c/verify.py`、`test_verify.py`、`README.md` 尚未提交，因此乾淨 main 尚不能重播此實驗。本機這三個檔案 SHA-256 分別為 `1f1f9211a323741ffbf9b205511e11281efd75e6d54448ef4a835ca1adf34f66`、`2ad03dfc7e69d7591e3bba93c4d778fb2f1a5d0a7d5b40378b40a6d6c5fd0af9`、`c866d034b4bb032f190217baf3fe29c8e9cd7435b86bd2f91a5ece830cc063ee`。工具 hash 不證供應鏈；未 pin 的工具依賴及並行替換仍是限制。

另外，GitHub `main` commit `21a81b6627739ccae5642150351169f2ccd37d96` 的遞迴 tree 回覆 `truncated=false`。以下列出該 tree 與本機 `git hash-object --no-filters` 相符的 blob ID：

| 路徑 | Git blob ID |
| --- | --- |
| `experiments/v4160-b0b0-rela-order-guard/guard.py` | `4cbd6c2a0e11a10f833c1a400fc391551ffbe3f7` |
| `analysis/v4160-irq-native-2026-10-21/compiler-review/elf32.py` | `daf6f8603111b76a3f839c115d0db0ab6258cbaa` |
| `scripts/verify-curated-source.py` | `18687a6b9e9b1e39847b33eaae1690320587cf02` |
| `src/native/receive/record_helpers.c` | `e14b5ffde4056bd4c2059fffb7f892c6a2a2ae49` |
| `experiments/tsl9-record-helpers/src/record_helpers.v1.c` | `e14b5ffde4056bd4c2059fffb7f892c6a2a2ae49` |
| `src/source-manifest.json` | `66de11cd6310fb3e08cd1710a5a0f2aac84dc6e6` |

unit-split 的三個程式／測試／說明檔不在該 tree。這只核對列舉依賴的 bytes，不證其他 tree 內容或 clean main 已能重播。

本輪沒有執行、模擬或燒錄 target。局部 byte 一致不證實原機資料所有權、ABI、caller 行為、連結整合或完整 firmware 等價。
