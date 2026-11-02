# V4.1.60 候選映像來源建置

[English](readme.en.md)

執行 `python scripts/build-v4160-source-candidate.py --tool-dir <LLVM_BIN> --out <NEW_OUTPUT_DIR>`，從 `src/` 與專案建置工具分別編譯 C 和 C++，各生成 76,800 bytes 的候選映像，並檢查其 SHA-256 是否等於既有 TX-integrated 候選。建置過程不讀取既有候選 BIN。

`src/native/tx_candidate/full-image-payload.json` 中的 3,128 bytes 是既有候選映像的原始內容，由建置器產生 C 並編譯。它們是尚未恢復語意的原始資料，不是已逆向的 C 功能；其他來源也可能包含原始指令或資料載體。此結果證明映像位元組可重現，不代表完整原始碼還原、嚴格連結無依賴、實機啟動或功能經驗證。原有數值位址見證仍用於診斷布局。

**候選檔尚未驗證可安全燒錄。** 原機 ROM／ABI、RAM、IRQ、OTA 和實機功能仍須獨立確認。此建置不操作硬體。
