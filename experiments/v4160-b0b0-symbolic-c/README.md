# V4.1.60 0xb0b0：外部符號 C 候選

`leaf.c` 是局部候選，透過外部 volatile byte 符號寫入參數低位元組並回傳原值；不是正式來源或 runtime ABI 的證據。

先前離線觀察的一份連結樣本使用 NDK clang/LLD 18.0.2：編譯選項 `--target=riscv32-unknown-elf -march=rv32imac_zicsr -mabi=ilp32 -mno-relax -mcmodel=medany -fno-pic -ffreestanding -fno-stack-protector -Oz -std=c11`；linker 選項 `--no-relax --section-start=.text=0xb0b0 --defsym=destination=0x2000beeb -e candidate`。rabin2 顯示 object relocation type 23 指向 `destination`、type 25 指向 `.Lpcrel_hi0`。relocation symbol resolved via linker definition 是外部定位，不能證明正式來源或 runtime ABI；此結果只是一份連結樣本。

BIN 在 0xb0b0 的 10 bytes 為 `97170020a38da7e28280`；該樣本觀察值為 `97150020a38da5e28280`，不同處僅 byte offsets 1、6。兩者 AUIPC/SB 基底分別使用 x15/a5 與 x11/a1，SB 來源皆為 x10/a0，位移皆為 -453，靜態計算目標皆為 `0x2000beeb`，後接 c.ret。a1 與 a5 不可直接替換：暫存器活躍性、呼叫慣例與上下文尚未證明。相同目標不證明可寫、執行效果或等價性，亦不可據此 patch。

`test_static.py` 固定 source SHA-256、完整 BIN SHA-256 與兩組 bytes，獨立解碼並檢查變異。觀察值為記錄資料，測試不讀取或驗證 ELF，不構成此次重新編譯的證據。從 repo 根目錄執行：

```
python -B experiments/v4160-b0b0-symbolic-c/test_static.py
python -B -O experiments/v4160-b0b0-symbolic-c/test_static.py
```

本次 object 與 ELF 產物未加入 Git；此候選與 BIN 不同，尚不能視為重建完成。
