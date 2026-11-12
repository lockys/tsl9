# TX composed C11 host harness

`harness.c` 直接 include 相鄰 `../v4160-tx-composed-ram-c/candidate.c`，使用單一有限 RAM 陣列及固定預期值；不使用 `assert`，定義 `NDEBUG` 亦不會移除檢查。測試 zero bank 0/1 的 entry_a6 保留、header 別名來源、逐次前向重疊傳播、非重疊 checksum，以及 65535 bytes（兩側明確 sentinel、來源和目的分離）。每例比較整個陣列及所有回傳欄位；`origin=0x2000b128`、`base_index=100`，兩者相加為 `0x2000b18c`。索引均位於同一陣列且不回捲，遵守候選 README 的呼叫者契約。

固定 candidate SHA-256：`de88c0b5677d5d036443e022c6ac71b41e7b7de347c184908cc9fc1039d957cf`。可用 `python experiments/v4160-tx-composed-c-harness/check_source.py` 離線核對本地 bytes；此檢查**不測 C**，也不自行驗證遠端一致性。

日後需先確認 host 支援 C11、`CHAR_BIT == 8`、`uint32_t`，且 `int` 能表示 135536、`size_t` 與物件大小可容納兩個該長度陣列。先選定受控隔離目錄中**不存在**的輸出路徑；編譯器的 `-o` 可能覆寫既有檔案，不要直接輸出到工作樹。使用者允許且工具身分確認後，編譯 `harness.c` 時可選 `-std=c11 -Wall -Wextra -Wpedantic -DNDEBUG`。執行產物必須使用該平台可用的**外部程序逾時**，逾時視為失敗；最大長度測例遇到錯誤迴圈可能無限執行。上述是未重播的操作指引，並非本次成功編譯或測試。

本次未編譯或執行 C，未執行 target、模擬器、網路或硬體設定。此 harness 僅針對抽象 C 物件與具體例子，不測硬體、bus、原址存取，也不證明韌體等價或所有輸入正確。
