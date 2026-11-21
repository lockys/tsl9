# v4.1.60：以直接符號取代第一個 boot 別名

依照[提供者盤點](v4160-direct-provider-inventory.zh-TW.md)，選擇只有一筆引用的 `tsl9_boot_main_9008`。只在暫存的 ET_REL 副本以 `llvm-objcopy --redefine-sym` 將未定義符號改成 `tsl9_main_family_entry_9008`。輸入比較確認這筆是 `R_RISCV_PCREL_HI20`（23）、addend 0，重定位的所有位置、類型、addend 以及配置區段投影均未改；比較的重定位名稱只有預期替換。這不是直接 JAL，也不是一般性的 ELF metadata 等價測試。

僅移除該別名而不改引用，嚴格連結會多出預期的未定義符號。改引用並移除別名後，C / C++ 基準與 split/leaf 候選在一般 Python 與 `-O` 下各通過四路：剩 71 個既有別名，6,364 個配置區段的內容、旗標、型別、大小和位址與原診斷連結一致，覆蓋的 76,800 bytes 均與原 BIN 相同。

只測了一筆 HI20，不可外推到 JAL、壓縮跳轉或資料重定位；下一步依重定位類型各選一筆驗證。resident 仍用數值見證，未修改正式來源、未連設備。本提交僅發布報告；重跑 `experiments/v4160-aggregate-no-ident-next/verify.py --baseline <saved baseline> --objcopy <llvm-objcopy.exe> --full`。
