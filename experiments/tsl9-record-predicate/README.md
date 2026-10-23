# Record predicate 821E
[English](readme.en.md) · [繁體中文](readme.zh-TW.md)

以 C 算術重建官方 `[0x821E,0x8248)` 的42B／15指令 leaf；只使用空字串的暫存器／GP asm 埠。C11／C++17 完整函式 bytes 均與原始 BIN 相同，無 frame／store／call／UND／relocation。選用 `src/predicate.v2.c`；專案副本為 `src/native/receive/record_predicate.c`。

先從 [GP+84] 讀 pointer，再讀 pointer+4 的 bit3，即使 index 不合法也先讀；bit3為零且 unsigned index<=2 時，再從 fresh GP+193+index 讀 byte，判斷 unsigned byte<3。保留 A4／A5 輸出殘值。GP、pointer 有效性及 flag 真正功能未知，不把它命名成免打擾。

正式 `build/verified-v3/{c,cpp}/verification.json` 各通過65負例：46個 raw ELF typed/metadata、2個 whole-file padding、13個 IR、4個 source；63個不使用全檔 hash 判定。完整 IR、15 typed operands、原始42B、兩個 MD 來源及五個實際 recipes 均受檢查。

[source-history.json](source-history.json) 記錄有限兩版來源、失敗輸出與驗證器修正。最初失敗驗證器未封存，不能補稱原件已保留；已知修正前驗證器另存 `history/verify.pre-root-path-fix.py`。v3僅正規化 Python 執行檔路徑；原始碼／flags 不變。兩種 Python 執行檔雜湊確實不同，必須使用原收據所記錄的同一個 interpreter；另一個 interpreter 的重播失敗是預期限制。v1/v2原始收據與輸出仍保留本機，不改寫成v3。

```sh
python experiments/tsl9-record-predicate/verify.py --language c --out-dir experiments/tsl9-record-predicate/build/verified-NEW/c --llvm-bin "$LLVM"
python experiments/tsl9-record-predicate/verify.py --replay experiments/tsl9-record-predicate/build/verified-v3/c/verification.json --llvm-bin "$LLVM"
```

不執行 target／ISA／MMIO／硬體；nominal821E link 不等於實體安裝。`--require-firmware-ready` 必須拒絕。完整 IRQ／ROM／記憶體／藍牙 OTA 與新功能仍未證明。
