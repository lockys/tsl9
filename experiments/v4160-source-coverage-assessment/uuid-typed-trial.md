# 0x1ab44 UUID 型別化試作：相容性界限

原 BIN 在 `[0x1ab44,0x1ab48)` 是 `f1 ff 00 00`；在 live 指標指向該位置的條件下，回呼以半字讀取前兩 bytes。後兩 bytes 用途未知。這不證明原始 C 宣告是 `uint16_t`，也不證明指標永遠不變。

`uuid_isolated_trial.py` 在暫存目錄試作將既有 `const uint8_t tsl9_opaque_gap_0001ab44[4]` 改成含 `uint16_t` 與兩個未知 bytes 的結構；不更改正式來源。它驗證原 BIN 雜湊，以 RV32 Clang 編譯 C/C++，比對試作與正式物件的唯讀 section 名稱、大小、旗標和全部內容，並用 LLD 部分連結一個以舊陣列宣告編譯的消費者。C/C++ 均有 32 個 section 相同，ELF relocation 解析至唯一 4-byte 定義。

```text
python -I -B experiments/v4160-source-coverage-assessment/uuid_isolated_trial.py --tool-dir <LLVM_BIN>
python -I -OB experiments/v4160-source-coverage-assessment/uuid_isolated_trial.py --tool-dir <LLVM_BIN>
```

**這只驗證指定工具鏈的 ELF 連結結果，不能證明跨編譯單元的 C/C++ 宣告型別相容。** 結構定義和陣列宣告型別不同；union、符號 alias 或指標轉型都不能憑連結成功消除該問題。未涵蓋 LTO、其他 linker、執行期及硬體。

因此不將試作當成與舊陣列介面完全相容的正式替代品。保守方案是保留原陣列、在需要時明確按 little-endian 解碼數值；這不建立位於原位址的 `uint16_t` 儲存物件，也不增加 bytes 覆蓋。正式變更如採用結構，必須先明確界定受影響 C 介面並遷移消費者，不能只憑 ELF 比對宣稱相容。
