# ADC 特定 caller 的完整暫存器 bank 實驗

[English](readme.en.md) · [繁體中文](readme.zh-TW.md)

此輪以新 C 檔普通 include 已封存的 ADC native.c；C core、真實 volatile IO、A0/A1 bridge 全部不變。只在原固定 NDK/-Oz/rv32imac_zicsr_zifencei 配方加入一個由實際 caller 證據推導的完整 bank，實際編譯 C11/C++17，沒有 HOST matrix 重跑或 native 執行。

來源為上一輪 source-review 的 post_config_register_liveness：這個 caller 在讀取前會覆寫 A0..A6；A7 與 T0/T2/T3/T4/T5/T6 保留到正常出口，T1 出口值固定 15。因此唯一可配置集合為 **x10..x16**，從 x5..x31 的全集保留其餘所有暫存器。x0/RA/SP/GP/TP 另外檢查，其專用角色不代表可以任意改寫。完整 clang --help 在編譯前實際確認每個 -ffixed-xN 適用於 RISC-V。

## 實際結果

C 與 C++ 均成功編譯，所有五個函式的機器碼各自相同；兩份真實 artifacts 的唯讀 replay 通過。

| 真正 global FUNC | bytes / 指令 | 狀態 |
| --- | ---: | --- |
| tsl9_adc_config_1892e | 110 / 42 | 選定入口，沒有 call |
| tsl9_adc_config_io | 132 / 50 | 未選定的真實 context/sret core |
| ml_port_read32 | 8 / 4 | 未選定的真實 volatile port |
| ml_port_write32 | 6 / 3 | 未選定的真實 volatile port |
| ml_port_read8 | 10 / 4 | 未選定的真實 volatile port |

完整 ET_REL 為 **266B／103 指令／5 globals、UND=0、RELA=0、ABS provider=0**；沒有假設其餘四個函式已被 linker 移除。所有函式都沒有寫入 fixed bank 中的暫存器。

選定入口自行寫入 **RA/SP/A2/A3/A4/A5/A6**，不再寫 A7 或任何 T 暫存器，但新產生 **16-byte frame**。入口先把 SP 減16，再把 RA 存到 entrySP-4；RA 暫作第一個 WORD 讀取的 scratch，正常返回前從相同位置還原 RA，再把 SP 加16。A0/A1 沒有自行寫入，沒有 S/GP/TP 寫入。這些新增 stack/RA 效果不能被省略成「原始 frameless ABI 相符」。

公開 LLVM IR 保留原本依序 **10 個 volatile WORD read、1 個 BYTE read、3 個 WORD write**。完整反組譯另外顯示 stack 的 RA store/load；14 個 target 效果不是整個機器函式的所有記憶體效果。

原始 callee 是 88B／37 指令；新入口多22B。原始 callee 只寫 A3/A4/A5，新入口仍有額外 RA/SP/A2/A6，scratch liveout 也不同。本 producer 不自行核准特定 caller 的正常投影；獨立 ABI review 必須另證正常返回、私有且與 config/目標分離的 stack 空間、entrySP-4 不被觀察，以及原 caller 的覆寫鏈。即使該有限投影成立，也不是原始 callee 完整 ABI、fault/IRQ/async 等價、固定配置或 installed provider 證明。

## 操作與證據

```sh
sh experiments/tsl9-adc-caller-bank/verify.sh --project-root "$PWD" --tool-dir LLVM --build-root NEW
python3 CASE/implementation/check.py --project-root ROOT
python3 CASE/implementation/probe.py --project-root ROOT --replay MODE/verification.json
python3 CASE/implementation/check.py --project-root ROOT --receipt C/verification.json --receipt CPP/verification.json
```

CASE 支援 workspace 的 apk-analysis/tsl9-v4160-adc-caller-2026-10-22 與交付樹的 analysis/v4160-adc-caller-2026-10-22。NEW 必須是 model/build 下尚不存在的目錄；省略時建立 UUID 路徑。正式 W artifacts 在 build/caller-bank-v1/{c,cpp}，含實際 tool/resource/header hash、完整 MD 七項輸入、IR、完整 disassembly、help、原始日誌及 receipts。預設 check 只讀來源及 metadata；顯式 receipt 才重讀真實 artifacts，並不重新編譯或執行。

只有一個 bank、同一份 source、一次配方；無 mask/flag sweep、手工 opcode、stub、假 provider、數值 ABS、native link、BIN 或刷寫。真實 volatile MMIO 程式不得在 HOST 執行；本輪也沒有 RV32、ISA、MMIO、實體硬體或第三方網路操作。Python/sh 原始碼可跨平台；native 結果限定固定 Windows NDK 工具 hash。先前 Git Bash 啟動拒絕後不重試，sh runtime 未驗證。新增來源與文件以 LF、單一 EOF newline 寫入並執行 Git 式空白檢查；實際 raw compiler log 保留原樣。
