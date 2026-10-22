# callback 實作與證據層級

[English](readme.en.md)

正式 HOST：model `verify_host.py --project-root ROOT --language both`；正式 native：`verify_native.py --project-root ROOT --tool-dir LLVM --language both`。兩者接受新 `--build-root`，輸出 `BUILD/{c,cpp}/verification.json` 及 stdout `results[{mode,receipt,sha256}]`。`--replay RECEIPT` 只讀實體 archives，拒絕 build-only 選項，不執行目標或重新編譯。

model `verify.py`／`verify.sh` 預設選 HOST，`--kind native` 選 native。`probe_native.py` 是正式工具釘選的生成子階段，也接受 owned build 中的 diagnostic source copy；正式入口只允許 canonical src。`compare_inline.py` 可從已採用來源重現唯一 native qualifier 比較：baseline 移除 `always_inline`，variant 保留它；不掃 flags/profile。

早期 `first-native` 是 A4 residue 修正前的 938+90=1,028-byte 診斷。修正後比較為 944+90=1,034，採用 inline 後 658。舊診斷完整保留，但不能作為當前四核心檔雜湊下的正式輸出。採用後原始 632-byte 原位 fit 仍為 false。

正式 native 綁定實際 5 條 LLVM command recipes、`-MD` canonical3＋resource `stdint.h` 閉包、來源/工具前後 pins、實際 generator/log 及完整 artifact inventory。獨立 native checker逐 byte覆蓋 658/241，核對 volatile width、15 個 A5/A6 call 與當前真實 frame/gaps，並拒絕實際 ELF byte 反例；passed 代表這個診斷子集，不代表原始 ABI。正式 HOST綁定正例與五個 copied-source 單一改動反例、exact compile recipes、log/exit、所有機器 guard 及真實產物。

合成 named state／frame／opaque provider 與 native compiler實體 GPR/SP/RA 是兩個證據層級。明示參數 mask 不代表完整 raw prefix。saved `return_address` 不跟蹤每次 JALR 的 RA，HOST 不執行還原地址。native 的 S10@SP0、save order、call RA offset、未知 resident preserve 行為均未確認，沒有 full image/BIN/hardware/OTA admission。

`check.py` 預設只驗封存 source/metadata，不假裝讀取未發佈的 build archives；明確 `--host-receipt`／`--native-receipt` 或 `--require-local-builds` 才讀實體產物。selected JSON metadata 隨來源發佈；objects/ELF/IR/PE/log/build copies 留本機，不上傳作為 source archive。
