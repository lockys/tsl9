# `0xb0b0`：保留暫存器的隔離原址 C codegen

使用 `experiments/v4160-b0b0-symbolic-c/leaf.c` 的純 C 候選，在隔離暫存目錄離線編譯及連結；未執行或模擬目標程式、未修改正式來源或 BIN。固定原始檔 SHA-256 `290336e8361500a563b725efed97714de0b293587fb79a3a2a762f2cc214d1ba`。相同候選先前未保留暫存器時使用 a1，原址差兩個 bytes。

本次使用既存 NDK Clang 18.0.2 及 LLD 18.0.2，編譯工具 SHA-256 分別為 `047dfde05acc6fcce5af669e25cd8d40b4f509b8842d151d6d8a43a1c6a35fd6` 與 `fe7f55c0c78b3d87f33b905a3874e10e872ca7beef53a8199d7ff9ac6641ec3f`。編譯參數：`--target=riscv32-unknown-elf -march=rv32imac_zicsr -mabi=ilp32 -mno-relax -mcmodel=medany -fno-pic -ffreestanding -fno-stack-protector -Oz -std=c11 -ffixed-x11 -ffixed-x12 -ffixed-x13 -ffixed-x14`。以 `ld.lld --no-relax --section-start=.text=0xb0b0 --defsym=destination=0x2000beeb -e candidate` 連結。這些編譯旗標是特殊條件，**不是**已驗證的整體建置設定；連結器定義目的符號也是外部定位，不證正式來源已正確提供符號。

以 Python 匯入既有 `experiments/v4160-b3e4-pure-c/verify.py`，在記憶體設 `m.ADDR=0xb0b0; m.END=0xb0ba` 後，呼叫 `m.reference(m.BIN.read_bytes())` 與 `m.section(elf_bytes)`；前者驗證固定參考 BIN SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`，後者擷取指定地址、受可執行 PT_LOAD 對映的 section。該函式不檢查 section 名稱或函式 symbol：

```text
reference=97170020a38da7e28280
candidate=97170020a38da7e28280
candidate_identical=True
```

`rabin2 -s` 顯示 `candidate` 位於 `0xb0b0`，大小 10 bytes；object 的 relocation 觀察為 type 23 `destination` 與 type 25 `.Lpcrel_hi0`。object SHA-256 `14dbd4e8ef36e8522bed8b2d0ac8864a4018bb604e56eee9ec8f6aeeec06d600`，ELF SHA-256 `39b9917140ac346f9a91964b87e182073c3c3252cc0e1978f85566ae5227e4e1`；產物未加入 Git，來源雜湊於編譯後核對，不能排除編譯期間暫時變動。

負例：沿用同一 object，將連結器符號設為 `0x2000beec`，得到 `97170020238ea7e28280`，原址 bytes 檢查正確拒絕。此單一負例不證明檢查器能偵測所有錯誤。

**僅證明上述一次受限實驗中 10 bytes 一致。** `-ffixed-x11` 至 `-ffixed-x14` 改變編譯器可用暫存器集合，不能假設其他正式 translation unit、函式簽章、caller 或 private ABI 可直接套用；必須另核對與既有原址 owner、呼叫路徑、符號定義及正式連結腳本的相容性。這不證明執行時位址有效、所有 caller 的暫存器需求、韌體全圖為純 C、完整 BIN 一致或裝置效果，也不是可刷寫映像。
