# V4.1.60：BD5A／BD64 raw JAL pattern scan

這是離線、唯讀的 raw pattern 實驗，不是反組譯器或 caller 證明。輸入固定為 repository 中 `firmware-downloads/legacy-options-2026-10-20/BINs/ID-2966-V4.1.60-decoded.bin`；不附帶、修改或執行 BIN。必須是完整 **76800 bytes**、SHA-256 `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667`；檔案 offset 0 對應模型 PC `0x8000`。長度或雜湊不符即在掃描前失敗。

## 重現

Python 3 標準函式庫，從 repository 根目錄執行；`-B` 避免寫入 bytecode：

```text
python -B experiments/v4160-bf13-raw-direct-edge-scan/scan.py
python -B -O experiments/v4160-bf13-raw-direct-edge-scan/scan.py
python -B experiments/v4160-bf13-raw-direct-edge-scan/test_scan.py
python -B -O experiments/v4160-bf13-raw-direct-edge-scan/test_scan.py
python -B experiments/v4160-bf13-raw-direct-edge-scan/test_runner.py
python -B -O experiments/v4160-bf13-raw-direct-edge-scan/test_runner.py
```

掃描每個完整、little-endian 的 4-byte 視窗，起始 offset 為 0、2、4……76796，共 38399 視窗，包括彼此重疊的視窗；尾端不足 4 bytes 不解讀。僅檢查 32-bit RISC-V JAL opcode `word & 0x7f == 0x6f`，重組 J immediate（含最低位移 0）、對 21-bit 位移 sign-extend，再以 `(PC + displacement) mod 2^32` 計算 target。輸出全部 target 等於 `0xbd5a` 或 `0xbd64` 的 raw 命中，列出 offset、PC、指令字、rd 和位移。掃描器最後比對完整命中快照和視窗數；缺少、變更或新增命中，以及不完整掃描皆非零退出；即使不符，也先列出實際命中。無 `assert`，`-O` 不會移除檢查。

## 固定 BIN 的 raw 結果

| offset | PC | little-endian word | rd | 位移 | target |
|---:|---:|---:|---:|---:|---:|
| `0x06d74` | `0xed74` | `0xfe7fc0ef` | x1 | -12314 | `0xbd5a` |
| `0x0de5a` | `0x15e5a` | `0xf0bf50ef` | x1 | -41206 | `0xbd64` |
| `0x0de70` | `0x15e70` | `0xeebf506f` | x0 | -41238 | `0xbd5a` |
| `0x0de80` | `0x15e80` | `0xedbf506f` | x0 | -41254 | `0xbd5a` |
| `0x0de90` | `0x15e90` | `0xecbf506f` | x0 | -41270 | `0xbd5a` |

所要求四個 BD5A 位置和一個 BD64 位置均有對應 raw 命中；此次無其他命中。x0 是不保存返回位址的 JAL，不能自動稱為 call。

## 邊界

半字對齊掃描會把另一條指令的中間、embedded data 或其他非指令位元組誤解成 JAL；命中不證明指令邊界、可執行性、可達性或真實 caller，也不證明控制流程或函式語意。此實驗只涵蓋指定 BIN 中符合上述模式的直接 JAL，不涵蓋 compressed jump、JALR、其他間接轉移、其他映像、執行期改寫或資料寫入；不能據此宣稱全局／間接 writer 已封閉。

測試以獨立 J-type 編碼器及固定已知指令字檢查正反向、x1/x0、位移極限、模數回繞、半字對齊、重疊與截斷；另測錯誤 pin、缺失／額外／變更命中、不完整／零掃描，以及真 BIN 在正常和 `-O` 下的完整 stdout、stderr 與退出碼。測試直接讀取 `scan.py` 的 source bytes 並編譯成註冊於 `sys.modules` 的模組；隔離暫存目錄中的同時間戳、同長度 stale pyc 對照驗證一般載入讀到舊碼，但此 loader 讀到新碼且支援 monkeypatch，不修改既有 cache。測試入口要求載入及執行全部 10 個測試，並拒絕任何 skipped 或 expected failures，避免零測或部分測試被當作成功。`test_runner.py` 以直接編譯的新 source bytes 測試真正空 suite、全部跳過、部分跳過和 expected failure，避免 stale pyc；各負例均在正常及 `-O` 下執行。不使用網路、第三方套件、target 執行或模擬。
