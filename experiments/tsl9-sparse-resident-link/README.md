# 分段 resident 參考連結

本檢查以固定雜湊的 WCH V1.31 參考資料建立 **17 個分離區段**，保留原始位址與空洞；`0x40000` 入口由第一區段實際支撐。在現有資料別名及 RAM 條件下，C／C++ 的 `--no-undefined` 連結均完成，APP 區段與候選映像一致；診斷 ELF 沒有 `PT_LOAD`。

這只證明連結器處理目前被引用符號的結果：每個 ELF 的符號表仍有 44 個未定義項，不能宣稱所有依賴解除。候選啟動時的第二段複製來源 `[0x6EAA4,0x6EB30)`，參考檔僅覆蓋到 `0x6EB2C`，**缺最後 4 bytes**；分段缺口沒有填值。WCH 參考檔也不證明原機安裝同一 resident、RAM／ABI 正確或可燒錄。

先以 `scripts/build-v4160-source-candidate.py` 在專案外新目錄完成建置，再執行：

```sh
python scripts/verify-sparse-resident-link.py --project-root . --conditional-dir <BUILD_DIR>/conditional-link --reference-dir <WCH_REFERENCE_DIR> --tool-dir <LLVM_BIN> --out <NEW_OUTPUT_DIR>
```

需既有固定來源參考及其 `source-map.json`，不下載或讀取硬體；輸出僅供離線診斷，沒有實機驗證。

[後續符號檢查](../tsl9-diagnostic-discarded-symbols/README.md)將 44 項分為 43 個定義於丟棄區段的備選符號與一個原本未定義符號；相關 24 筆 relocation 的來源區段均被丟棄。

**連結器負例：**不提供 resident 時，C／C++ 的嚴格連結都因 `tsl9_boot_resident_40000` 未解析而失敗；只提供原參考入口的 4 bytes 時，兩者卻都成功連結。兩個四-byte 對照 ELF 沒有 `PT_LOAD`，也沒有其餘參考區段。此負例證明連結器成功本身無法確認 resident 完整或能啟動。
