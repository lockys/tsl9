# B0B0 與 BD46 的隔離原址連結

本紀錄是本機離線 selected-window 診斷，不是完整 firmware 或正式來源整合。基於先前 B0B0 split + 純 C leaf 的 reference-link，額外將已提交的 `experiments/v4160-bd46-symbolic-c/candidate.c` 編譯成 ET_REL，連到 `0xbd46`，不再以 ABS 符號冒充該函式。資料符號 `record_flag_bd46=0x2000bf11` 仍是人工 ABS witness，未配置資料或證明 owner。

## 本次實測

- 正常及 Python `-O` 合成測試各 **12 項通過**；合成測試不是完整 ELF 格式驗證。另行執行的真實 replay 在兩種 Python 模式均完成 C11/C++17 離線編譯及連結，退出 0。
- 每個 C/C++ 模式均通過部分連結 selected-facts 比對，以及最後 **69 sections、920 bytes**：`matched=920 mismatched=0 missing=0`。其中原 68 sections／910 bytes 含既有組合語言來源和 10 bytes 的 B0B0 C 候選；新增 BD46 純 C 候選為另外 10 bytes。
- final BD46 符號核驗為指向指定 PROGBITS section、位於 `0xbd46`、大小 10 的 GLOBAL FUNC，而非 ABS；ET_REL 的 HI20、LO12_I 與同區段 anchor 均核對。原 `0xf034` JAL bytes `efc03fd1` 解碼為 `0xbd46`，並與原 BIN 對照。
- final ELF 的 entry 為 0、無 PT_LOAD；已檢查未定義符號與受限 REL／RELA／RELR、DYNSYM 情況。臨時 ELF 於離線比對後清理；沒有執行、模擬或燒錄目標。

## 限制與重播狀態

仍使用 **19 個人工 ABS witness**：17 個其餘外部目標、B0B0 的 `destination`，以及 BD46 的資料地址。17 個外部目標由 BIN 中規格列舉的 references 解碼並與 spec 交叉核對；部分起始指令邊界仍是未獨立證實的假設。此實驗不證實資料 owner、完整 CFG、runtime ABI、其他 provider、實際硬體行為或整機純 C；沒有將 920 bytes 誤認為整個 76800-byte BIN。

本機 `experiments/v4160-b0b0-bd46-combined-link/` 的三個檔案尚未提交，舊 reference／strict／partial／split 重播鏈也有依賴未提交，因此 **乾淨的 main 無法直接重播本紀錄**。這不是 CI 通過的證明。本機檔案 SHA-256：

- `verify.py`：`5cfacfb51d5b7d9ee9d1b0817be17be0ba49c33c51c82b5cc235bccf8bc7656e`
- `test_verify.py`：`1a4cee4c6b9be6460134e62aa72346cdedc58204d1abf0c1aa723b30777b794a`
- `README.md`：`a4a6d6cc8c462078714c2873be1d27295107e4b1a7551fe4748ddf8a26c764f6`

本次 receipt 由已驗證快照產生；工具 hash 不固定 resource headers、DLL、Python 或 OS，也不消除並行替換的 TOCTOU 風險。程式對 BIN 和直接讀取的 object／ELF 設定大小上限，但舊 replay 和其餘輸入／輸出並非完整資源沙箱。下一步是審查並發布完整重播鏈，研究 BD46 資料 owner 與正式 caller ABI，並持續取代其他 ABS witness。
