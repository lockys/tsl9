# Callback 暫存器與即時 GP 原生實驗

[English](readme.en.md)

本實驗以可讀 C11／C++17 重建事件 callback 的原生元件，保留原版 0x8614 起始的 632-byte 函式作為驗證依據。候選實際為 **624 bytes、223 條指令**，並不是可直接替換原韌體的 BIN。

| 層次 | 函式 bytes／指令數 | GP 使用站點 | frame／保存暫存器 |
| --- | --- | --- | --- |
| 先前封存的原生元件 | 658／241 | 16 個快照 | 48 bytes／12，含 S10、SP+0 |
| 僅保留 S10、S11 不供配置的診斷 | 656／240 | 16 個快照 | 48 bytes／11，不碰 SP+0 |
| 本次即時 GP 候選 | 624／223 | 6 個實際即時使用 | 48 bytes／11，不碰 SP+0 |
| 本次明示保存排序後 | 624／223 | 同前 | 僅交換兩個已編譯 C.SWSP words |

原生編譯旗標沿用已封存設定，唯一新增 `-ffixed-x26 -ffixed-x27`。程式只把原本六個 `s->gp` 使用改為 `CB_GP(h)`，並移除 native 入口與 opaque call 後的 GP 快照。HOST 展開仍為原來的 `values.gp`，來源比對已確認沒有改變共享演算法，因此沒有重跑未變更的 HOST suites。

`postpass/frame.py` 是獨立、明示的來源擁有 ABI 排序步驟：只把已編譯的 RA@44／S0@40 兩個 2-byte 保存指令交換為 S0、RA。它不產生 opcode、不讀原始 BIN，也不修改其餘 ELF bytes。最終管線是 **C/C++ 編譯＋明示保存排序＋標準 linker**；排序後 ELF 不應被描述為純編譯器輸出。

## 執行

需 Python 3 與符合記錄 SHA-256 的本機 LLVM 工具目錄。實測環境是 Windows NDK LLVM；Python／shell 介面可攜，但未宣稱已在 Linux 或 macOS 實跑相同工具。其他平台編譯器若不符合工具 pin，會明確拒絕，不能視為跨平台工具身份已驗證。

```sh
python3 -B experiments/tsl9-v4160-callback-registers/verify.py --tool-dir /path/to/pinned/llvm/bin --language both
sh experiments/tsl9-v4160-callback-registers/verify.sh --tool-dir /path/to/pinned/llvm/bin --language both
python3 -B experiments/tsl9-v4160-callback-registers/verify.py --replay /absolute/path/to/ordered/c/verification.json
```

Windows 可直接使用 `python -B`。使用 `--project-root ROOT` 指定 checkout；`--build-root NEW` 必須是此 model 的新建 build 子目錄，拒絕覆寫。預設產生 UUID 目錄。Replay 不呼叫編譯器或執行元件，且拒絕混用 fresh-build 參數。

輸出位於 `build/NEW/pre/{c,cpp}` 與 `build/NEW/ordered/{c,cpp}`。前者保留原始編譯 object、LLVM IR、MD、ELF、完整 disassembly 與 probe receipt；後者保留排序 object／receipt、標準 link 與正式 verification receipt。所有 object、ELF、IR、日誌只保存在本機 build；版本控制只保留來源、文字與選定的 receipt metadata。

## 證據與限制

逐指令 raw-field／LLVM 檢查確認：x26/x27 完全無編碼使用、GP 無寫入、六個即時 GP operand、15 個 opaque JALR、11 對 32-bit stack 保存／讀回、無 SP+0／替代 spill／UND／額外配置資料。實際 MD 包含三個專案來源與一個 Clang `stdint.h` resource header。正式 receipt 檢查來源、工具前後身份、8 個明示工具步驟、完整產物、原始與排序後 machine/IR、5 個原生產物反例、4 個排序反例、3 個 disassembly 反例與4個 recipe／MD 反例。

只修復了 **11 個 stack store 的相對順序**。原版入口 SLLI 相對 stores 的時序、15 個 opaque call RA、實體 scratch/S 暫存器映射與未知 ROM 的 preservation 均未完整證明。624 bytes 小於 632 的數學尺寸成立，但仍有 **8-byte 原區段尾端未建立所有權**；沒有填補、借用舊 bytes、宣稱原址放置或更新完整 image。

未執行 RV32、ISA 模擬或硬體 I/O；沒有產生 BIN。現有完整韌體實驗 image 保持不變。完整 ABI、板子適用性、實體燒錄、BLE/OTA 與安全相容性仍未通過。
