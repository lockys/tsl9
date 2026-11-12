# 0x18ef2 callback 候選：host C 測試紀錄

使用者授權後，在 Windows host 執行隔離 callback 模型的測試程式，沒有執行、模擬、燒錄目標韌體或存取裝置。候選 `experiments/v4160-18ef2-candidate/candidate.c` 的 Git blob 為 `8d6279451c94285be66d1a478fc78f1887d34fe0`、SHA-256 為 `5db6dd08f40ee73470fd1475dbb2259dd747fae30450e01fd67b4e81d77c3e37`。

本機建立的精簡測試框架 `experiments/v4160-18ef2-compact-host/` **尚未提交**，本紀錄本身不足以從 GitHub 重現測試；不要把它當成已發布的測試程式。測試後該目錄的 `candidate.c`、`harness.c`、`fixtures.h`、`test_fixtures.py` Git blob 分別為 `8d6279451c94285be66d1a478fc78f1887d34fe0`、`4b6c0767ef30867437af51b7c21c94f06714f704`、`2472dc6e1dbb9377c23d0353767edbc8773afa2d`、`ef81301ddfcbb115cebdc46c2b3ad7a58f1c69e2`；事後雜湊不能排除編譯期間的暫時變動。

精簡 fixture 的 Python 展開結果與本機另一份尚未提交的固定 fixture 逐項比對，normal、wrap、alias、poll 共 812 事件一致；Python 正常及 `-O` 各通過一項測試。固定 fixture 不存在時只核對固定摘要和事件數，不能聲稱重新比對。獨立靜態審查未發現具體 P1/P2。

使用 `cl.exe` 19.44.35228.0 與 `link.exe` 14.44.35228.0，各自 SHA-256 `88c8344236a27a6e727e0a8edc49aaa2690bdc7a9464b9d18cc7abe70a9f1c0d`、`ca11e6c45debd34bf652dfe984c5360a531a005ed78bf72852330c9c2590cf0d`；MSVC 14.44.35207 與 Windows SDK 10.0.26100.0 標頭及 libraries 未逐一 pin。以 `/std:c11 /W4 /WX` 分別不加與加入 `/DNDEBUG` 編譯，均退出 0；執行兩個 host 程式均設 15 秒外部 timeout，各自輸出 `normal: pass`、`wrap: pass`、`alias: pass`、`poll: pass` 並退出 0。兩個 executable SHA-256 均為 `5c673e838b9aa8c56e952a8e72a9ba9e03d21476ce6a1d1c8d13cbd43e53fc69`，未加入 Git。

在另一新建暫存目錄複製測試檔，將 candidate 的第一次 control 寫入 OR mask 從 `0x10000` 改為 `0x20000`；該 mutant 編譯成功，執行時在 normal 事件 1 寫值不符、退出碼 1。這只是一個負例，不保證測試能偵測所有錯誤。

上述結果限於具體 callback 事件腳本；alias 中的後續讀值由腳本固定，不是完整記憶體模擬。不能據此證明 native ABI、RISC-V 原址 codegen、真實 bus／硬體、副作用、所有 alias、無限 polling、完整影像或可達性。
