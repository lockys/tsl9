# B0B0 combined 物件的受限原址連結

## 範圍

這是離線、reference-only 的選定物件診斷，**不是完整純 C 重建、正式 provider 連結、ABI、執行行為或完整 BIN 驗收**。記錄中的 68 個區段包含既有的 assembly private regions；只有 B0B0 換成獨立純 C leaf 候選。沒有建立完整 BIN、執行或載入 ELF、模擬目標、使用硬體或燒錄。

## 方法與假設

- 固定參考 BIN：76,800 bytes，base `0x8000`，SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`。68 個原始窗口及其來源清單依已提交的 `experiments/v4160-record-helper-layout-map/` 檢查，合計 910 bytes。
- C11 和 C++17 分別編譯原 unit、移除 B0B0 的 unit 與 leaf，再執行部分連結和既有 selected-facts 比較。leaf 使用不同於原 unit 的特定 register/code-model flags；此比較不是跨單元 ABI 等價。
- Strict 原址連結不注入地址時先前因 19 個 named undefined symbols 失敗。本輪診斷注入 19 個明示的 **ABS reference witnesses**，不是提供者實作：18 個地址取自固定 spec 的 `target_PC`，僅作假設；尚未獨立解碼所有 51 個 control 與 11 個 PC-relative pair。第 19 個 `destination` 根據原 BIN 的 B0B0 AUIPC/SB 算出 `0x2000beeb`，不證明 RAM owner。
- 每個 `.text.<region>` 依 spec start 放置，使用 `--no-relax`。產出只保存在臨時目錄；檢查 entry 為零、無 PT_LOAD 後作靜態讀取，之後清除。即使如此也不可執行或部署。

## 本機實測

在固定 Clang 18.0.2（SHA-256 `047dfde05acc6fcce5af669e25cd8d40b4f509b8842d151d6d8a43a1c6a35fd6`）與 LLD 18.0.2（SHA-256 `fe7f55c0c78b3d87f33b905a3874e10e872ca7beef53a8199d7ff9ac6641ec3f`）下，C 與 C++ 兩種模式各自比較 68 個 section 的位置、長度及內容，得到：

```text
c: partial selected facts match; 18 spec target_PC values are pinned-spec assumptions, not independently decoded
c: final linker exit 0
TOTAL matched=910 mismatched=0 missing=0
c: all selected windows match; reference-only, not firmware equivalence
cpp: partial selected facts match; 18 spec target_PC values are pinned-spec assumptions, not independently decoded
cpp: final linker exit 0
TOTAL matched=910 mismatched=0 missing=0
cpp: all selected windows match; reference-only, not firmware equivalence
diagnostic exit: 0
```

Normal 與 Python `-O` 合成測試各 26 項通過；包含畸形 ELF、缺失符號、錯誤位置或內容等負例。這些測試不是目標韌體執行結果。hash pin 證明檔案身分，不能排除工具依賴或並發替換風險。

## 可重播性與後續

此筆是本機實驗記錄；`experiments/v4160-b0b0-combined-reference-link/` 及其 strict-link、partial-relink、unit-split 驗證器**尚未提交**，不能宣稱 clean `main` 可直接重播。當時 verifier SHA-256 依序為 `31dd22ea5252bdbc3b631a32a94a297cd0ef0d1cc77fb67a49f10f6be3fddf3c`、`b064147def4b10a016108c834174720572708a9ac11941863c32502827cfb1c1`、`06ab4325eedafdb07524d649e06fbe6a95297f2b78636b5f29b5502005f3f33f`、`f7675ad917980ed87cc69ba3c19e486d55698d23d4b86f854078803df8a4adb2`。臨時 ELF 已刪除，這些 hash 不是獨立留存的重播產物。

後續仍須審查並發布重播鏈、確立真實 symbol/data owner 與 private ABI、移除人工位址並以真正 provider 連結，最後重建並逐 byte 比較完整 BIN；窗口一致不代表上述目標已完成。
