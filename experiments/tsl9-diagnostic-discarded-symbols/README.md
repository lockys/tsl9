# 稀疏 resident 診斷 ELF 的未定義符號

C／C++ 診斷 ELF 各有 44 個未定義符號表項：其中 43 個在來源 aggregate 中有定義，但位於 linker script 丟棄的備選 `.text`／`.bss` 區段；另一個 `tsl9_runtime_reset_stack_top` 在 aggregate 中已未定義。來源 aggregate 中指向這 44 個名稱的 24 筆 relocation，分布於 10 個區段；這 10 個 relocation 來源區段均由 linker script 丟棄。最終 ELF 沒有保留 relocation。

這解釋了為何在此診斷布局下 `--no-undefined` 可成功，卻仍有未定義符號表項；它**不代表**原始功能已重建、被丟棄的備選程式可運作，或 resident／RAM／資料索引已確認。數值與分類依賴此固定布局；間接呼叫和執行期行為不在檢查範圍。

先執行[分段參考連結](../tsl9-sparse-resident-link/README.md)，再以 `python scripts/verify-discarded-symbols.py --project-root . --conditional-dir <BUILD_DIR>/conditional-link --sparse-dir <SPARSE_OUTPUT_DIR>` 核對 C 與 C++ 實際 ELF、輸入 relocation 與 `/DISCARD/` 規則。檢查有合成負例，不執行目標。
