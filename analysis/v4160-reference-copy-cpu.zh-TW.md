# V1.31 copy 參考原指令與 v4.1.60 TX 的條件性組合

2026-11-26。本批只分析既有本機 APP／SDK 檔案，不操作設備，不下載新資料。**SDK reference candidate 不等於設備已安裝的 resident provider**。

## 固定的原始檔身分

| 輸入 | bytes | SHA-256 |
|---|---:|---|
| v4.1.60 APP | 76800 | `0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667` |
| 既有 December 2023 SDK V1.31 carrier | 191078 | `133d37055626caa1ac0f0abd0b8ec4d8c5786a61d52e6a2ef24ae2705aa15a22` |
| carrier `0x405a2..0x405dc` helper | 58 | `558a82658cb54901945d4c2884f2e87e763f64d57c0cafa831307beb44ae0c36` |

這份 carrier 的 `0x4004c` word 為 `0x20000332`。依[既有條件性 loader 映射證據](resident-copy-reference-2026-10-21/source/README.md)，該 RAM 位址對應上述 58-byte carrier body。本次把這段原始 bytes 映射到合成解譯器的 RAM view，執行其相對分支；沒有把參考 bytes 注入 APP／BOOT 檔案，也沒有生成可刷入映像。

本次未執行 loader；初始化完成、設備槽位值與 resident 身分仍未證。既有證據記錄第二初始化來源缺最後四 bytes 的限制也仍保留。

## 原指令的保存與副作用

radare2 離線解碼與新解譯測試一致：

1. 讀取 `0x4002420c` word 至 A4，再寫零到同地址。
2. 遇到原始 `FENCE.I` 編碼 `0x0000100f`。測試只驗證並記錄此指令事件，沒有模擬真實 cache／硬體效果。
3. 才檢查 destination A0、source A1、count A2；零指標或零 count 跳過 byte 操作，仍走恢復路徑。
4. 非零者逐 byte 讀 `source+index`、寫 `destination+index`，向前處理，讀取是 live memory。重疊目的寫入可能改變後續 source，因此不能替換成 memmove。
5. 正常返回前寫回先前讀得的控制 word，之後沒有第二個 FENCE。

每次正常返回檢查除 A3/A4/A5/A6 外的所有暫存器都未改，包括 A0/A1/A2、RA、SP/GP、所有 S 暫存器。這是參考原指令的合約，不能提升為未知設備 provider 的保證。

96 個獨立 helper 案例為 count 0–15 × 六種 source／destination 關係：分離、相同、向前重疊、向後重疊、零 source、零 destination。比對完整記憶體結果與精確的 read/write/FENCE 事件順序，不用主機 memcpy 實作被測 helper。

第三個目的 byte-store 的合成中止案例確認：兩個已完成 bytes 保留、第三次未完成、控制 word 仍為零且沒有 restore 事件。沒有用 finally 補造原指令未執行的恢復。這不是實際硬體 fault 行為證據。

## 接回 v4.1.60 TX

先從 TX 真實入口執行到 copy 呼叫：slot fixture 明確選成該參考 RAM target，驗證 fresh load／參數，再執行上述 helper，接回 TX 尾段、query／send／update 與傳輸原指令。STATUS／DATA 仍是合成輸入。

720 個案例為 tag 1／2 × 長度 0–8 × 八種 selector 狀態 × 五種最終狀態。不同於前一批[無記憶體效果的 provider 假設](v4160-tx-entry-cpu.zh-TW.md)，本次參考 body 確實逐指令將 row 的非零 payload 複製到 frame；未使用的 payload bytes 保持本機 fill 的零值。

逐例檢查 helper 的所有事件與保存狀態、frame payload、TX 完整呼叫／傳輸輸入序列、最終返回值、caller RA/SP/S0–S3 與控制 word 恢復。這是**指定參考 binding 的組合結果**，不是已安裝 binding 的證明；返回 0 也不代表實際傳送或 ACK 成功。

## 重現與結果

```powershell
python analysis/test_v4160_reference_copy_cpu.py
python -O analysis/test_v4160_reference_copy_cpu.py
```

需要標準庫、原 APP、已發布的同目錄測試依賴，以及本機已保留的 carrier：
`analysis/wch-resident-candidate-2026-10-21/carrier-dec2023/REFERENCE-CANDIDATE-ONLY-00040000-0006EA66.bin`。可用 `--carrier <path>` 指定相同身分的檔案；不會自動下載或填補缺口。

```text
PASS: pinned SDK slot/body; 96 reference copy/null/overlap cases; 720 candidate-bound TX cases; interrupted prefix remains un-restored; LBU mutation detected; installed binding UNPROVED
```

一般與 `-O` 均通過。LBU source offset 從 0 改成 1 的記憶體複本必須被事件檢查抓出。既有 TX-entry 測試也重跑通過；共享 CPU 沒有更動。TX-entry 的 `probe` 只增加可選停止 target，預設保持原值，以便在候選 RAM 入口停下而不越過呼叫邊界。

## 舊封存重播失敗，未當作通過

本次另外執行舊 `source/inspect-source.py --check`，結果為：

```text
ValueError: seal member drift:README.md
```

因此沒有宣稱舊套件完整封存驗收通過，也沒有修改 README、seal 或歷史證據來消除錯誤。新腳本獨立固定整份 carrier／slot／body，以上原指令檢查的 PASS 不取代舊封存檢查，也不重新證明 loader 已完成。

本批新增參考原指令與 APP 的條件性驗證，沒有增加 APP C/C++ 重建 bytes 或重算覆蓋率。設備 resident 身分、實際 MMIO 用途、IRQ／非正常返回與硬體相容仍未證。
