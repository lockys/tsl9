# 原生時脈證據

可讀實作位於 `experiments/tsl9-v4160-native-clock/`。
本輪沿用 ID2966 V4.1.60 已封存的原始來源證據：
`analysis/v4160-system-clock-query-2026-10-21/source/`
（調查工作區內為 `apk-analysis/tsl9-v4160-system-clock-query-2026-10-21/source/`）。
原始兩函式共 214 bytes／69 條指令，既有 50 個 raw 負例保持不變。

- [來源契約](source-review/readme.zh-TW.md)：來源效果與 ABI 限制。
- [獨立 C/C++ 審查](code-review/readme.zh-TW.md)：實際編譯的測試與反例。
- [原生結構審查](native-review/readme.zh-TW.md)：重新編譯、連結 RV32 並完整核對反組譯覆蓋範圍。

來源／主機證據與原生結構證據分開驗證，只執行自行重建的主機測試。
原始及重建的 RV32 都未執行或模擬。一般 C 的暫存器、堆疊、中斷 ABI、
完整映像整合及 OTA 相容性仍未證明。未操作硬體或廠商網路服務。
既有原始配置離線映像保持不變，本輪不產生新 BIN。

交付專案可能包含歷史本機編譯封存，但 Git 發佈會排除這些目錄。
主機與原生驗證器會自行建立新的忽略輸出目錄。已發佈封存雜湊若指向本機編譯檔，
只代表證據身分，不表示新的 clone 包含那些被排除的檔案。
