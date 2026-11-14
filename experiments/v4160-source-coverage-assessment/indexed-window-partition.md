# 0xcf5a 索引讀取的條件性位址分區

既有 `experiments/tsl9-APP-residual-access-audit/verify-v1.py` 對普通入口的靜態資料流得到 `0x1a078 + 16 * mode + nibble`，其中保守範圍為 8-bit mode、4-bit nibble；並未證明每個組合可達。`indexed_window_partition.py` 固定原 BIN SHA-256，重新解碼 `0xcf4e` 的 AUIPC/ADDI 基址並窮舉 4096 個組合。其餘算術與 mode 範圍採用前述稽核，不是獨立完整 CPU 執行。

- 16 個位址位於已知資料池尾端 `[0x1a078,0x1a088)`；2936 個位於其後、映像結束前；1144 個在映像 `[0x8000,0x1ac00)` 外。映像外不代表實機無映射或讀取會失敗。
- 全 `ff` 的 `[0x1abe0,0x1ac00)` 對應 mode 182 的 nibble 8–15、mode 183 的全部 nibble、mode 184 的 nibble 0–7；mode 184 的 nibble 8–15 已超出映像。基址低 nibble 是 8，不能把 32-byte carrier 誤認為兩個完整 mode。
- 這只是保守條件範圍的反向對照；既未證明實際能到這些模式與索引，也未證明 carrier 是 padding、執行時真的讀取、或硬體行為。

執行 `python -I -B experiments/v4160-source-coverage-assessment/indexed_window_partition.py`；也支援 `-I -OB`。
