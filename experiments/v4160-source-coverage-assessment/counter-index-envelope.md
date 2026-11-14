# Counter 查表位址的靜態範圍

`counter-index-envelope.py` 固定 v4.1.60 BIN SHA-256，檢查 `0xa146–0xa15c` 原始指令編碼，解析 byte 載入、左移和 PC-relative 表基，並核對 `0x1ab48` 的四個已知 halfword。以無號 byte 作為**語法上的**索引，256 個讀取中，4 個位於已還原資料，88 個落在映像中其他位置，164 個位於提供映像之外，共 328 個位元組；首個映像外索引為 92。原 BIN 的單 byte 變造會因完整雜湊被拒絕。

此分類不證明這些索引實際可達、映像外記憶體不可讀、原始資料表真正的宣告大小，也不提供尚未證實的 provider alias。已知 masked 寫入、啟動與條件性 resident fill 的限制，以及未知的非同步和間接寫入，仍見 `analysis/lookup-index-2026-10-25/readme.en.md` 與 `experiments/tsl9-input-counter-integration/readme.en.md`；這不是新增覆蓋或硬體測試。
