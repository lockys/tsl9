# v4.1.60：直接連結的別名與 resident 引用盤點

延續[全 BIN 診斷連結](v4160-105c4-direct-full.zh-TW.md)。本次逐件讀取直接連結的 ET_REL 輸入，並將具名定義及重定位與保留的輸入區段對照，再驗證最終 ELF 符號表。

- 72 個既有別名的右側，在保留的 ET_REL 輸入中各有唯一具名的區段內定義。最終 ELF 的別名與右側符號位於同一區段、值相同。這 72 個別名涵蓋 83 筆保留重定位：RISC-V 類型 1、17、23、45 各 7、70、5、1 筆。這證明別名依附輸入定義，不等於已移除別名或驗證設備提供者。
- `tsl9_boot_resident_40000` 在這組保留輸入中沒有區段內定義；僅一筆保留引用，在 `.text.tsl9_boot_18724` 偏移 12（原位 0x18730），`R_RISCV_JAL`、addend 0。最終符號是 ABS 0x40000，不是實體 resident 區段。GP 數值設定仍另外存在。

一般 Python 與 `-O` 各四路（C／C++ 基準及 split/leaf 候選）結果一致，6,364 區段、76,800 bytes 仍與原 BIN 相同。未讀取實機、未確認 resident 來源；仍屬含 BIN 取樣資料、無 PT_LOAD 的診斷連結。下一步先用小批具名別名做直接符號替換對照，再確認其他別名可否沿用同一規則，避免把 resident 數值見證混入可移除清單。本提交僅發布報告。

重跑：`experiments/v4160-aggregate-no-ident-next/verify.py --baseline <saved baseline> --objcopy <llvm-objcopy.exe> --full`。
