# 本輪新增的標準 RISC-V 靜態欄位來源

這是2026-10-22實際查閱的官方 riscv/riscv-opcodes 公開文字節錄，僅用來核對來源指令欄位，不產生 opcode、不執行 CPU，也不宣稱是完整 ISA decoder。

- [rv_i](https://raw.githubusercontent.com/riscv/riscv-opcodes/master/extensions/rv_i)：ori、sll、sltu、and 定義。
- [rv_m](https://raw.githubusercontent.com/riscv/riscv-opcodes/master/extensions/rv_m)：mul 定義。
- [arg_lut.csv](https://raw.githubusercontent.com/riscv/riscv-opcodes/master/arg_lut.csv)：選定暫存器、立即值與 opcode 欄位。

本機檔案為選定逐行節錄；摘要雜湊只對這些節錄負責，並非完整上游檔案的 hash。上游 master URL 可變；本輪已保存實際採用的行，後續驗證以本機封存為準。查詢 GitHub commits/master API 的網頁讀取不可用，因此不杜撰 immutable commit。
