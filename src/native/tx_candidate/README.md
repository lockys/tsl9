# V4.1.60 TX 候選來源元件

[English](readme.en.md)

這是已測試 TX 候選的入口、C 主體及返回葉節點的獨立 `src/` 副本；目前的 `../receive/transport_frame.c` 是原始 TX 路徑，**不可同時當成同一個位置的兩個 provider 連結**。來源以原實驗為根據，包含由組合語言入口改寫的等價 file-scope inline assembly；只改動 include 路徑。六個 C/H 檔已加入目前 `src/source-manifest.json` 的來源追溯清單；候選元件仍由本目錄的獨立檢查器建置，沒有加入舊 125 個 native units。原有 164 檔歷史收據維持原樣，由於當前 manifest 已擴充，固定舊 manifest 雜湊的歷史重播不能直接視為通過。

使用當初的 LLVM NDK 18，將工具目錄與全新輸出路徑傳入 `python src/native/tx_candidate/verify.py --tool-dir <LLVM_BIN> --out <NEW_OUTPUT_DIR>`。檢查器分別以 C11／C++17 fresh compile 三段，核對 **pre-pass** section bytes 與 relocation 欄位，並輸出 `NOT-FLASHABLE-unlinked-TX-*.bin`。這些 280-byte 檔案只是未連結片段，沒有套用 relocation、frame postpass、APP 其餘程式、BOOT 或 resident；**不得燒錄，也不是 4.1.60 候選 BIN**。不讀取原廠或候選韌體。

進一步執行 `python src/native/tx_candidate/verify-linked.py --tool-dir <LLVM_BIN> --candidate <CANDIDATE_BIN> --out <NEW_OUTPUT_DIR>`，會呼叫既有、雜湊固定的 `experiments/tsl9-v4160-tx-register-abi/postpass`，重新排序 frame 並在名目位址 `0x8A56` 連結。兩種語言的 280 bytes 皆與候選 BIN 的 TX 視窗逐 byte 一致；驗證僅讀候選位址 `[0x8A56,0x8B6E)`。嚴格缺 RAM provider 的連結應失敗，診斷連結的 `0x2000B18C` 只是數值地址見證，並沒有提供實體 RAM。輸出 `NOT-FLASHABLE-TX-ONLY-*.bin` 僅是已連結 TX 片段，**不能燒錄**；此流程仍依賴上述 `experiments/` postpass 與解碼器，並非完全由 `src/` 獨立建置。

`python src/native/tx_candidate/integrate-diagnostic.py --tool-dir <LLVM_BIN> --candidate <CANDIDATE_BIN> --out <NEW_OUTPUT_DIR>` 再將新編譯 TX bytes 插入既有、雜湊固定的 `src/` 來源編譯物件，停用舊 TX 區內 9 筆重定位並遮除 24 個過期內部符號；檢查 8 筆區外進入的 relocation 均指向 TX 入口。這是**物件層診斷整合**，不是完整重新編譯全部 `src/`；它依賴本機保留的歷史 `experiments/.../build` 物件與 layout。嚴格連結仍因六個 provider 失敗，另以數值地址見證連成零 `PT_LOAD` 的不可燒錄診斷 ELF。其 73,538 個已配置 bytes 與候選檔相同；比對跳過既定排除區，不證明完整檔案或硬體相容。舊中途入口的間接跳轉與 runtime ABI 也未封閉。

要從 `src/` 重建完整候選，仍須把此元件以正確符號及 postpass 整合到原位址圖，處理六個 provider、未選與既定排除區、RAM／resident／IRQ 及最終 OTA 條件；目前這些尚未完成，現有實機 OTA 的成功紀錄也不能套用至此未連結片段。

可另執行 `python scripts/verify-curated-data-objects.py --tool-dir <LLVM_BIN> --out <NEW_OUTPUT_DIR>`，以 C 與 C++ 重新編譯 13 個既有資料單元及其來源，檢查已配置區段、符號、重定位與包含檔來源。輸出為物件檔，不是韌體；通過不代表資料索引範圍、完整 provider 或硬體相容性已確認。

`python scripts/verify-conditional-data-link.py --tool-dir <LLVM_BIN> --out <NEW_OUTPUT_DIR>` 在兩種語言模式下，將新編譯消費者分別與 8-byte 計數器、48-byte 序列資料物件做局部連結：先確認未綁定的符號，再將條件性別名綁到實際物件。這只證明物件連結關係；全域索引界限未確認，不代表完整 provider 已解決。輸出物件不可燒錄。
