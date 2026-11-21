# v4.1.60：TX 候選重跑與符號驗收

接續[重建基準與分析計畫](v4160-reconstruction-roadmap.zh-TW.md)。以下是現有本機工具與來源上的離線重跑，不代表 GitHub `main` 單獨即可重現。沒有修改正式來源或放寬正式檢查。

## 位元組：隔離候選通過

執行 `experiments/v4160-tx-symbolic-overlay-next/verify.py --tool-dir <NDK LLVM bin>`，以 Python `-I -B` 與 `-I -B -O` 各跑一次。每次 C11 與 C++17 都輸出 `PASS selected=73672/73672 BIN exact, baseline TX differences=93`。以真編的 TX 候選替換隔離建置中的舊複合區段後，原有 93 個差異全消失，非 TX 的選入位元組不變。這是重跑既有候選，不是本輪把它併入正式來源。

每組同時檢查 3 個符號及 8 筆既有入口重定位；改動重定位、符號歸屬、RAM 見證值和 4 條指令的負向控制均被拒。無見證值的嚴格連結仍有 7 個未定義符號；診斷 ELF 沒有 `PT_LOAD`，未產生可刷映像。此項未驗證未選入的 3,128 bytes。

## 符號：直接綁定尚未通過

另重跑 `experiments/v4160-dispatch-symbol-provenance-next/observe.py --tool-dir <NDK LLVM bin>`，查看 C/C++ 各自的 baseline 與 candidate 四路診斷連結。四路皆觀察到 dispatcher 的 `R_RISCV_JAL` 輸入仍引用未定義的 `tsl9_dispatch23_filter_8a56`；TX 輸入實際定義的是 `tsl9_filter_external_8a56`。兩名在輸出中同落 `0x8a56`、同一區段，不能證明輸入直接綁到 TX 定義。較大圖的父層結果仍為 `INFORMATIONAL_FAIL_CLOSED`，C/C++ 各有符號投影、別名投影及 owner 與 split+leaf 比較不符，共 6 項；不應因位元組相符而忽略。

下一項驗收：在隔離的連結中區分「真正由輸入物件提供」與「只靠連結時的別名或數值」；用移除實際提供者的負向測試判定是否仍能誤通過。不把這項觀察當成 ABI 或裝置行為證據。
