# V4.1.60：105c4 formal profile 的局部原址連結

這是本機靜態離線觀察，不是正式整合或完整 BIN 驗收。實驗重播程式與測試尚未隨本紀錄發布，不能稱為 clean-main 重播或 CI 通過；未執行、模擬或燒錄目標。

以 `experiments/v4160-new-leaf-turn/leaf.c` 為候選，依固定的 `src/source-build-manifest.json` 中 `queue-consumer-a0-a5` C11／C++17 完整有序 profile 編譯；另加實驗 symbol 映射和 `-nostdinc`。固定 NDK Clang／LLD 在 `0x105c4` 做局部連結，兩種語言所得 ET_EXEC 的 `.leaf` 均為 12 bytes：`034535007115133515008280`，與固定 76,800-byte reference BIN 在假設線性 base `0x8000` 時的 `[0x105c4,0x105d0)` 窗口一致（檔案 offset `0x85c4`）。此 ET_EXEC 不含 PT_LOAD，不是可載入韌體。

同次以相同 profile fresh 編譯完整 `src/native/receive/feature_state_records.c`，核對原 owner 的目標 section、symbol metadata 與 12 bytes；目標來源仍使用含 inline asm 的 macros。原 owner 有 255 symbols、115 relocations，候選 object 則有 6 symbols、無 relocation；這是整個 owner 與單 leaf 的不同範圍，並非 split 等價證明。原 owner 有兩筆 type 23 relocation 指向該 symbol，候選 `.llvm_addrsig` 只有一項；不可因此忽略原物件的其他依賴或 metadata。

每種語言的 `==5` 錯誤候選經真實編譯、連結後為 `034535006d15133515008280`，因與 reference bytes 不同被拒絕。另實測錯 placement、錯 symbol、object byte 變異、原 owner bytes 變異等有限負例。重播探針按設計輸出 `INCOMPLETE_FAIL_CLOSED`、`passed=false`，exit 1；本機 normal／Python `-O` 測試各 4 項通過。

上述結果不證明正式 split／重定位與 `.llvm_addrsig` remap、caller private ABI、原始 source owner、實際地址映射或完整映像。編譯器、OS 與未固定載入依賴的可信度和 TOCTOU 不由檔案 hash 保證；暫存 ELF 未隨本紀錄發布，不能對歷史產物另行解析。
