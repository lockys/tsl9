# BD5A／BD64：相鄰 byte 存取的隔離純 C 候選

本紀錄只涉及原始 BIN 的兩個 10-byte 窗口；不修改正式來源或執行目標。檔案 `experiments/v4160-bd5a-symbolic-c/candidate.c` 與 `experiments/v4160-bd64-symbolic-c/candidate.c` 是隔離的 `volatile unsigned char` 寫入與讀取候選。人工 ABS witness `0x2000bf13` 不配置 RAM，也不證實資料 owner、初始化或 native ABI。

參考 BIN 76,800 bytes、假設基址 `0x8000`、SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`：

| 位址 | 原始 10 bytes | 有界指令效果 |
|---|---|---|
| `0xbd5a` | `97070020a38ca71a8280` | `auipc a5,0x20000; sb a0,0x1b9(a5); ret`，store 位址 `0x2000bf13` |
| `0xbd64` | `170500200345f51a8280` | `auipc a0,0x20000; lbu a0,0x1af(a0); ret`，load 位址 `0x2000bf13` |

離線 C11／C++17 原址編譯與 `--no-relax` 非載入式連結：

- BD64 正例的 `.leaf` 各自匹配原始 10 bytes；將 data witness 改為 `0x2000cf13`，兩者都精確產生 `171500200345f51a8280`，不同於原址正例。
- BD5A 以一般 medany profile 產生 `97050020a38ca51a8280`，使用 `a1` 而非原始的 `a5`，**不匹配**；另加 `-ffixed-x11` 至 `-ffixed-x14` 時，兩種語言產生原始 10 bytes。將 witness 改為 `0x2000cf13` 時，該固定暫存器組合精確得到 `97170020a38ca71a8280`。這些額外旗標是局部 codegen 實驗，不證原始 compiler profile 或跨函式 ABI。

本輪對兩項觀察分別執行正常及 Python `-O` 的驗證和測試：BD64 每種模式 **11 項**、BD5A 每種模式 **12 項**通過，且在新暫存產物上檢查 relocation、ABI flags、symbol 0、section／FUNC、錯地址與拒絕案例。BD5A 的 `passed` 只表示包含預期 mismatch 的測量矩陣符合預期，並非全部 profile 相同。未驗證整個 firmware BIN、正式 source 整合或硬體行為。

這兩組完整重播器、測試與 README 目前只在本機相應實驗目錄，**不包含在本提交**。當次 BD64 `verify.py` SHA-256 `e25af93d63b184380949c108a7e9518c18ad05805693021a95cbc7b9d4282df7`，`test_verify.py` `e53330d24adeb6af0cedd40bc3d2f73895daad76892a6609025223e5c5d41e58`；BD5A 依次 `985ceff60184fc8683569cb39095a9b7ee7479c85e83d9eacc0849d4434f8f37`、`e0ad02013e5eb07e8ce2c9166568c5b2367c05087fdc25c8e6d3087212dfc1fa`。此紀錄不是 CI 或遠端 clean checkout 已重播的證明。工具、其動態依賴及所有中間檔在使用期間假設不被並行替換；暫存目錄不是安全 sandbox。
