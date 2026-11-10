# 原廠 TX 替代候選：NOT-FLASH-VALIDATED

離線研究，不得刷寫。既有候選及其建置路徑不變。新路徑先在專案外全新目錄重建原候選，再分別用 C11/C++17 在原位址編譯 `experiments/tsl9-tx-whole-inline/tx.c`，檢查無 relocation，以編譯所得 280 bytes 替換 `[0x8a56,0x8b6e)`；其餘沿用基底建置。不是完整原始碼重建：基底含 opaque 載體及機器指令資料。

```powershell
$llvm = "$env:LOCALAPPDATA/Android/Sdk/ndk/27.1.12297006/toolchains/llvm/prebuilt/windows-x86_64/bin"
$ref = 'firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin'
$out = "$env:TEMP/tsl9-original-tx-alt-unique"
python scripts/build-v4160-original-tx-alternative.py --tool-dir $llvm --reference $ref --out $out
python -m unittest discover -s tests -p test_original_tx_alternative.py
```

本機實測兩語言完整 76800 bytes 均與本機標示原廠解碼參考逐 byte 相同，SHA-256 均為 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`。此雜湊不是原廠簽章認證。產物位於 `%TEMP%/tsl9-original-tx-alt-20261209-unique`，檔名均有 NOT-FLASH-VALIDATED。

實際產物的 `0x8b10` 分支解碼對照基底；TX 實驗分別重編兩語言並檢查八個 B 目標與 C.J，四種來源 mutation 均造成差異，兩種目標 mutation 另行解碼。完整映像檢查對 TX 內及首末 bytes mutation 均拒絕，非窮舉，亦非目標執行或行為等價證明。

## 隔離與依賴檢查

設定 `$env:TSL9_LLVM_DIR = $llvm` 後執行上述 unittest，會複製 `src`（排除 `.bin`、`.elf`、`.o`）、Python scripts 及 TX 實驗的兩個文字檔到臨時樹，參考映像只作樹外明確輸入。兩語言實際產物分別驗證為基底前段 + 新編譯 TX + 基底後段；TX 與基底原區段不同，完整產物則等於參考。刪除參考、刪除 `full-image-payload.json`、或變更 TX 指令均拒絕產生替代映像。此隔離不排除文字檔內編碼的原始機器碼，亦不是無原廠目標資料建置的證明。

### 全映像 OTA 形狀的隔離重播

隔離測試也直接對兩種新鮮產物套用 `tests/test_ota_full_image_contract.py` 的固定本機 SHA、首 byte、合成分頁與 W envelope 檢查：各為 76,800 bytes、首 byte `6f`、75 頁（每頁 BE16 索引加 1,024 bytes），合成 BytesCount 76,950、CheckCode 31,872；逐頁驗證 `55 7f 57 04 02 | page | sum8` 並重組全映像。測試拒絕錯誤 count/bytes/checksum、缺頁、增頁、換序與截斷或損毀 envelope。這些 metadata 和 envelope 是合成的相容性形狀，不是實際伺服器回應或 APK／BOOT 執行結果；已知 APK 並無固定 1026-byte 全映像格式檢查，實際相容條件及限制見 [離線契約](ota-full-image-offline-contract.md)。

缺失參考與同長但內容變更的參考均在建立輸出目錄前拒絕；後者即使樹外存在正確參考也不會回退。這只檢查此建置入口，未證明其他工具不存在 stale reference fallback。來源固定為本機 SHA，不是原廠簽章。此次以 NDK 27.1 執行隔離測試及既有 OTA 合約測試皆通過；未接觸設備。

基底依賴 `src/native/tx_candidate/full-image-payload.json` 中兩段原始 bytes（`[0x14056,0x14c8a)`、`[0x1a69c,0x1a6a0)`）；前段重新編譯的片段仍與 carrier 逐段比較，後段四 bytes 直接攜帶。其他來源亦包含以指令或資料形式攜帶的機器碼，不能因其為文字而稱為完整語意重建。替代建置還強制讀取指定完整參考並檢查其雜湊及全映像相等；需要 Python、外部 LLVM clang、ld.lld、llvm-readelf、llvm-objcopy，以及基底建置所需工具。建置 JSON 明示 `full_source: false` 和 `opaque_original_inputs_required: true`。

嚴格連結仍缺 `tsl9_boot_resident_40000`；安裝 ROM、RAM 所有權及全域索引界限未知。無硬體、OTA 或刷寫測試，byte 相同不證明可開機或安全刷寫。
