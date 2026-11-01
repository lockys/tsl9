# 來源建置的已選區段資料

[English](readme.en.md)

`python scripts/build-source-spans.py --tool-dir <LLVM_BIN> --out <NEW_OUTPUT_DIR>` 從來源重編 C／C++ 診斷版面，將已選位元組依原位址排序串接，輸出 `NOT-FLASHABLE-selected-spans-*.bin` 與 `NOT-FLASHABLE-spans.json`。建置不讀候選檔或排除區，兩種語言各輸出 73,672 bytes，並核對固定摘要。

| 原位址半開範圍 | 輸出檔 offset 半開範圍 | Bytes |
| --- | --- | ---: |
| `[0x8000,0x14056)` | `[0,49238)` | 49,238 |
| `[0x14C8A,0x1A69C)` | `[49238,72296)` | 23,058 |
| `[0x1A6A0,0x1AC00)` | `[72296,73672)` | 1,376 |

輸出是**三段資料的串接**，不是原始位址的連續映像；沒有填入既定排除的 3,128 bytes。已選區段含 121 bytes 未知語意的原始資料。嚴格連結仍有 7 個依賴；數值見證、ROM／RAM、啟動、執行與硬體相容均未解決。**不得燒錄此資料檔**。

可另以 `python scripts/verify-allowed-source-layout.py --tool-dir <LLVM_BIN> --candidate <CANDIDATE_BIN> --out <NEW_OUTPUT_DIR>` 在不讀取排除區的條件下逐區段比對候選檔。

`python scripts/compare-allowed-reference.py --tool-dir <LLVM_BIN> --reference <REFERENCE_BIN> --out <NEW_OUTPUT_DIR>` 可將來源建置結果與另一份 76,800-byte 參考檔比對，只讀上述三個允許區段。對 `legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin` 的 C／C++ 測試均比較 73,672 bytes，發現 93 個不同 bytes，全部位於 `[0x8A56,0x8B6E)` TX 區段；其餘允許範圍相同。這不比較排除區，也不證明 TX 行為相同或不同；目前來源對應整合候選，不是已證實的官方原映像完整重建。
