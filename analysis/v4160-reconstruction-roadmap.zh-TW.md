# v4.1.60 BIN：重建基準與下一批驗收

## 本輪重跑

以 76,800-byte decoded v4.1.60 BIN 為比對基準，SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`。在現有本機來源上，以 Android NDK 27.1.12297006 重跑 `scripts/build-source-spans.py`，輸出放在新暫存目錄；不表示只靠 GitHub main 即可重現。

- C／C++ 各選入 73,672 / 76,800 bytes；C 模式盤點有 6,266 個區段。排除 `[0x14056,0x14c8a)` 3,124 bytes 與 `[0x1a69c,0x1a6a0)` 4 bytes。排除不等於沒有反組譯成果。
- 目前選入的連結結果有 93 bytes 與原 BIN 不同，全部在 TX，首末差異位址為 `0x8a7f` 和 `0x8b6b`。因此選入的 73,672 bytes 中有 73,579 bytes 與原 BIN 相同。
- 選入範圍的 121 bytes 屬於明列的 opaque carrier；其餘含既有 C、組語、資料或組合產物，不能拿選入比例當純 C 或語意復原進度。`complete_firmware=false`、`flashable=false`。
- `experiments/v4160-current-coverage-fresh-next/map.py` 在一般與 Python `-O` 的輸出一致；`test_map.py` 各通過 8 項。以上是本機重跑結果，僅發布報告。

## 分析順序

1. **優先把 TX 的 93-byte 差異縮到零。** 以現有 TX 候選做隔離建置，逐項對照輸入物件、原本八個已盤點的外部呼叫關聯，以及 dispatcher 另有的一條 `0x14738 → 0x8a56`。驗收要分開記錄「位元組相符」與「實際符號提供者已確認」；地址相同不等於證實直接綁定。不得放寬現有建置檢查換取通過。
2. **再處理未納入正式檢查的 3,128 bytes。** 將 dispatcher 及 4-byte 資料分開驗收，區分既有來源、從原 BIN 取出的資料，以及仍靠數值假設的外部符號。用缺物件、錯位址及改動位元組等負向測試確認檢查真的能拒絕錯誤輸入。
3. **最後對完整映像結算。** 重新比對全部 76,800 bytes，列出剩餘來源、外部符號與正式檢查缺口；不可用局部片段或取自原 BIN 的資料把結果說成獨立重建。V1.30 resident 只能作為參考，除非能把觀察直接連回 v4.1.60，否則不計入上述成果。
