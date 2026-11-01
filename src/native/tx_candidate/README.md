# V4.1.60 TX 候選來源元件

[English](readme.en.md)

這是已測試 TX 候選的入口、C 主體及返回葉節點的獨立 `src/` 副本；目前的 `../receive/transport_frame.c` 是原始 TX 路徑，**不可同時當成同一個位置的兩個 provider 連結**。來源以原實驗為根據，包含由組合語言入口改寫的等價 file-scope inline assembly；只改動 include 路徑。它是獨立來源包，不修改既有封存的 `src/source-manifest.json` 和舊收據。

使用當初的 LLVM NDK 18，將工具目錄與全新輸出路徑傳入 `python src/native/tx_candidate/verify.py --tool-dir <LLVM_BIN> --out <NEW_OUTPUT_DIR>`。檢查器分別以 C11／C++17 fresh compile 三段，核對 **pre-pass** section bytes 與 relocation 欄位，並輸出 `NOT-FLASHABLE-unlinked-TX-*.bin`。這些 280-byte 檔案只是未連結片段，沒有套用 relocation、frame postpass、APP 其餘程式、BOOT 或 resident；**不得燒錄，也不是 4.1.60 候選 BIN**。不讀取原廠或候選韌體。

要從 `src/` 重建完整候選，仍須把此元件以正確符號及 postpass 整合到原位址圖，處理六個 provider、未選與既定排除區、RAM／resident／IRQ 及最終 OTA 條件；目前這些尚未完成，現有實機 OTA 的成功紀錄也不能套用至此未連結片段。
